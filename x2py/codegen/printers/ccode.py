"""
Module containing the `CCodePrinter` class which converts X2py's AST to
strings of C code.
"""

import functools
from itertools import chain
from typing import ClassVar


from ..bind_c import BindCPointer
from ..bindings.c_concepts import (
    CMacro,
    CStrStr,
    ObjectAddress,
    PointerCast,
)
from ..models.core import (
    AsName,
    Assign,
    Deallocate,
    Declare,
    FunctionAddress,
    FunctionCall,
    get_direct_assignment,
    get_direct_module,
    get_enclosing_function,
    Import,
    Module,
    PythonTuple,
    SeparatorComment,
)
from ..models.datatypes import (
    CharType,
    CustomDataType,
    FinalType,
    FixedSizeNumericType,
    PrimitiveBooleanType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    NumpyBoolType,
    NumpyComplex128Type,
    NumpyInt64Type,
    ComplexPart,
    StringType,
    VoidType,
)
from ..models.datatypes import (
    Literal,
    NIL,
    cast_to,
    convert_to_literal,
)
from ..models.datatypes import (
    NumpyFloat64Type,
    NumpyNDArrayType,
)
from ..models.core import (
    IfTernaryOperator,
    AssociativeParenthesis,
    Mul,
    Operator,
)
from ..models.core import DottedVariable, IndexedElement, Variable
from .codeprinter import CodePrinter

# TODO: add examples

__all__ = ["CCodePrinter"]

c_library_headers = (
    "complex",
    "ctype",
    "float",
    "inttypes",
    "math",
    "stdarg",
    "stdbool",
    "stddef",
    "stdint",
    "stdio",
    "stdlib",
    "string",
)

import_dict = {"omp_lib": "omp"}

c_imports = {
    n: Import(n, Module(n, (), ()))
    for n in [
        "assert",
        "complex",
        "float",
        "inttypes",
        "math",
        "pyc_math_c",
        "stdbool",
        "stdint",
        "stdio",
        "stdlib",
        "string",
        "stc/cstr",
        "CSpan_extensions",
    ]
}

import_header_guard_prefix = {
    "stc/common": "_TOOLS_COMMON",
    "stc/cspan": "",  # Included for import sorting
}

stc_extension_mapping = {
    "stc/common": "STC_Extensions/Common_extensions",
}


class CCodePrinter(CodePrinter):
    """
    A printer for printing code in C.

    A printer to convert X2py's AST to strings of c code.
    As for all printers the navigation of this file is done via _visit_X
    functions.

    Parameters
    ----------
    filename : str
            The name of the file being converted.
    verbose : int
        The level of verbosity.
    prefix_module : str
            A prefix to be added to the name of the module.
    """

    printmethod = "_ccode"
    language = "C"

    _default_settings: ClassVar = {
        "tabwidth": 4,
    }

    dtype_registry: ClassVar = {
        VoidType(): "void",
        CharType(): "char",
        (PrimitiveIntegerType(), None): "int",
        (PrimitiveComplexType(), 8): "double complex",
        (PrimitiveComplexType(), 4): "float complex",
        (PrimitiveFloatingPointType(), 8): "double",
        (PrimitiveFloatingPointType(), 4): "float",
        (PrimitiveIntegerType(), 4): "int32_t",
        (PrimitiveIntegerType(), 8): "int64_t",
        (PrimitiveIntegerType(), 2): "int16_t",
        (PrimitiveIntegerType(), 1): "int8_t",
        (PrimitiveBooleanType(), -1): "bool",
    }

    type_to_format: ClassVar = {
        (PrimitiveFloatingPointType(), 8): "%.15lf",
        (PrimitiveFloatingPointType(), 4): "%.6f",
        (PrimitiveIntegerType(), 4): "%d",
        (PrimitiveIntegerType(), 8): convert_to_literal("%") + CMacro("PRId64"),
        (PrimitiveIntegerType(), 2): convert_to_literal("%") + CMacro("PRId16"),
        (PrimitiveIntegerType(), 1): convert_to_literal("%") + CMacro("PRId8"),
    }

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, filename, *, verbose, prefix_module=None):
        """Initialize the state used for one generation run."""
        super().__init__(verbose)
        self.prefix_module = prefix_module
        self._additional_imports = {"stdlib": c_imports["stdlib"]}
        self._additional_code = ""
        self._additional_args = []
        self._temporary_args = []
        self._in_header = False

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    def _visit_Cast(self, expr):
        """Render the ``Cast`` model node."""
        value = self._visit(expr.arg)
        dtype = expr.dtype

        if isinstance(dtype, StringType):
            if isinstance(expr.arg.class_type, StringType):
                return f"cstr_clone({value})"
            assert isinstance(expr.arg.class_type, CharType) and getattr(expr.arg, "is_alias", True)
            return f"cstr_from({value})"
        if isinstance(dtype.primitive_type, PrimitiveBooleanType):
            return f"({value} != 0)"
        if isinstance(dtype.primitive_type, PrimitiveIntegerType):
            self.add_import(c_imports["stdint"])
        return f"({self._c_type(dtype)})({value})"

    def _visit_Literal(self, expr):
        """Render the ``Literal`` model node."""
        value = expr.python_value
        dtype = expr.dtype

        if expr is NIL:
            return "NULL"
        if isinstance(dtype, StringType):
            escaped = (
                value.replace("\\", "\\\\")
                .replace("\a", "\\a")
                .replace("\b", "\\b")
                .replace("\f", "\\f")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
                .replace("\v", "\\v")
                .replace('"', '\\"')
                .replace("'", "\\'")
            )
            return f'cstr_lit("{escaped}")'

        primitive_type = dtype.primitive_type
        if isinstance(primitive_type, PrimitiveBooleanType):
            return "1" if value else "0"
        if isinstance(primitive_type, PrimitiveIntegerType) and dtype.precision == 8:
            self.add_import(c_imports["stdint"])
            sign = "-" if value < 0 else ""
            return f"{sign}INT64_C({abs(value)})"
        if isinstance(primitive_type, PrimitiveFloatingPointType):
            suffix = "f" if dtype.precision == 4 else ""
            return f"{value!r}{suffix}"
        if isinstance(primitive_type, PrimitiveComplexType):
            self.add_import(c_imports["complex"])
            real = self._visit(Literal(value.real, dtype.element_type))
            imag = self._visit(Literal(abs(value.imag), dtype.element_type))
            if value.real == 0:
                sign = "-" if value.imag < 0 else ""
                return f"({sign}{imag} * _Complex_I)"
            sign = "-" if value.imag < 0 else "+"
            return f"({real} {sign} {imag} * _Complex_I)"
        return repr(value)

    def _visit_ModuleHeader(self, expr):
        """Render the ``ModuleHeader`` model node."""
        self.set_scope(expr.module.scope)
        self._in_header = True
        name = expr.module.name
        if isinstance(name, AsName):
            name = name.name
        classes, func_blocks = self._class_header_blocks(expr.module.classes)
        func_blocks.append("".join(f"{self._function_signature(f)};\n" for f in expr.module.funcs if f.is_semantic))

        func_blocks.extend(
            "".join(f"{self._function_signature(f)};\n" for f in i.functions if f.is_semantic)
            for i in expr.module.overload_sets
        )

        funcs = "\n".join(f for f in func_blocks if f)

        decls = [Declare(v, external=True, module_variable=True) for v in expr.module.variables if not v.is_private]
        global_variables = "".join(self._visit(d) for d in decls)

        # Print imports last to be sure that all additional_imports have been collected
        imports = [i for i in chain(expr.module.imports, self._additional_imports.values()) if not i.ignore]
        imports = self._sort_imports(imports)
        imports = "".join(self._visit(i) for i in imports)

        self._in_header = False
        self.exit_scope()
        body = "\n".join(info_block for info_block in (imports, global_variables, classes, funcs) if info_block)
        return f"#ifndef {name.upper()}_H\n \
                #define {name.upper()}_H\n\n \
                {body}\n \
                #endif // {name}_H\n"

    def _class_header_blocks(self, classes):
        """Render class declarations and their function prototype blocks."""
        definitions = []
        function_blocks = []
        for class_def in classes:
            class_parts = []
            if class_def.docstring is not None:
                class_parts.append(self._visit(class_def.docstring))
            class_parts.append(f"struct {class_def.name} {{\n")
            declarations = [self._visit(Declare(var, external=True)) for var in class_def.attributes]
            class_parts.extend(declaration.removeprefix("extern ") for declaration in declarations)
            class_parts.append("};\n")
            definitions.extend(class_parts)
            function_blocks.append(self._class_function_prototypes(class_def))
        return "".join(definitions), function_blocks

    def _class_function_prototypes(self, class_def):
        """Render method and overload prototypes for one class."""
        functions = [method for method in class_def.methods if method.is_semantic]
        functions.extend(function for interface in class_def.overload_sets for function in interface.functions)
        return "".join(f"{self._function_signature(function)};\n" for function in functions)

    def _visit_Module(self, expr):
        """Render the ``Module`` model node."""
        self.set_scope(expr.scope)
        body = "\n".join(self._visit(i) for i in expr.body)

        global_variables = "".join([self._visit(d) for d in expr.declarations])

        # Print imports last to be sure that all additional_imports have been collected
        imports = Import(self.scope.get_python_name(expr.name), Module(expr.name, (), ()))
        imports = self._visit(imports)

        code = "\n".join((imports, self._x2py_malloc_helper(), global_variables, body))

        self.exit_scope()
        return code

    def _visit_If(self, expr):
        """Render the ``If`` model node."""
        lines = []
        condition_setup = []
        for i, (c, b) in enumerate(expr.blocks):
            body = self._visit(b)
            if i == len(expr.blocks) - 1 and isinstance(c, Literal) and c.python_value is True:
                if i == 0:
                    lines.append(body)
                    break
                lines.append("else\n")
            else:
                # Print condition
                condition = self._visit(c)
                # Retrieve any additional code which cannot be executed in the line containing the condition
                condition_setup.append(self._additional_code)
                self._additional_code = ""
                # Add the condition to the lines of code
                line = f"if ({condition})\n"
                if i == 0:
                    lines.append(line)
                else:
                    lines.append("else " + line)
            lines.append("{\n")
            lines.append(body + "}\n")
        return "".join(chain(condition_setup, lines))

    def _visit_IfTernaryOperator(self, expr):
        """Render the ``IfTernaryOperator`` model node."""
        cond = self._visit(expr.cond)
        value_true = self._visit(expr.value_true)
        value_false = self._visit(expr.value_false)
        return f"({cond} ? {value_true} : {value_false})"

    def _visit_And(self, expr):
        """Render the ``And`` model node."""
        args = [
            (
                f"({self._visit(a)})"
                if isinstance(a, Operator) and not isinstance(a, AssociativeParenthesis)
                else self._visit(a)
            )
            for a in expr.args
        ]
        return " && ".join(args)

    def _visit_Or(self, expr):
        """Render the ``Or`` model node."""
        args = [
            (
                f"({self._visit(a)})"
                if isinstance(a, Operator) and not isinstance(a, AssociativeParenthesis)
                else self._visit(a)
            )
            for a in expr.args
        ]
        return " || ".join(args)

    def _visit_Eq(self, expr):
        """Render the ``Eq`` model node."""
        lhs, rhs = expr.args
        if isinstance(lhs.class_type, StringType) and isinstance(rhs.class_type, StringType):
            lhs_code = self._visit(CStrStr(lhs))
            rhs_code = self._visit(CStrStr(rhs))
            return f"!strcmp({lhs_code}, {rhs_code})"
        if isinstance(lhs.class_type, FixedSizeNumericType):
            lhs_code = self._visit(lhs)
            rhs_code = self._visit(rhs)
            return f"{lhs_code} == {rhs_code}"
        raise NotImplementedError(f"C equality printing is not implemented for {expr}")

    def _visit_Ne(self, expr):
        """Render the ``Ne`` model node."""
        lhs, rhs = expr.args
        if isinstance(lhs.class_type, StringType) and isinstance(rhs.class_type, StringType):
            lhs_code = self._visit(CStrStr(lhs))
            rhs_code = self._visit(CStrStr(rhs))
            return f"strcmp({lhs_code}, {rhs_code})"
        if isinstance(lhs.class_type, FixedSizeNumericType):
            lhs_code = self._visit(lhs)
            rhs_code = self._visit(rhs)
            return f"{lhs_code} != {rhs_code}"
        raise NotImplementedError(f"C inequality printing is not implemented for {expr}")

    def _visit_Lt(self, expr):
        """Render the ``Lt`` model node."""
        lhs = self._visit(expr.args[0])
        rhs = self._visit(expr.args[1])
        return f"{lhs} < {rhs}"

    def _visit_Le(self, expr):
        """Render the ``Le`` model node."""
        lhs = self._visit(expr.args[0])
        rhs = self._visit(expr.args[1])
        return f"{lhs} <= {rhs}"

    def _visit_Gt(self, expr):
        """Render the ``Gt`` model node."""
        lhs = self._visit(expr.args[0])
        rhs = self._visit(expr.args[1])
        return f"{lhs} > {rhs}"

    def _visit_Ge(self, expr):
        """Render the ``Ge`` model node."""
        lhs = self._visit(expr.args[0])
        rhs = self._visit(expr.args[1])
        return f"{lhs} >= {rhs}"

    def _visit_Not(self, expr):
        """Render the ``Not`` model node."""
        arg = expr.args[0]
        a = self._visit(arg)
        if isinstance(arg, Operator) and not isinstance(arg, AssociativeParenthesis):
            a = f"({a})"
        return f"!{a}"

    def _visit_Mod(self, expr):
        """Render the ``Mod`` model node."""
        self.add_import(c_imports["math"])
        self.add_import(c_imports["pyc_math_c"])

        first = self._visit(expr.args[0])
        second = self._visit(expr.args[1])

        if expr.dtype.primitive_type is PrimitiveIntegerType():
            return f"pyc_modulo({first}, {second})"

        if expr.args[0].dtype.primitive_type is PrimitiveIntegerType():
            first = self._visit(cast_to(expr.args[0], NumpyFloat64Type()))
        if expr.args[1].dtype.primitive_type is PrimitiveIntegerType():
            second = self._visit(cast_to(expr.args[1], NumpyFloat64Type()))
        return f"pyc_fmodulo({first}, {second})"

    def _visit_Pow(self, expr):
        """Render the ``Pow`` model node."""
        b = expr.args[0]
        e = expr.args[1]

        if expr.dtype.primitive_type is PrimitiveComplexType():
            b = self._visit(
                b if b.dtype.primitive_type is PrimitiveComplexType() else cast_to(b, NumpyComplex128Type())
            )
            e = self._visit(
                e if e.dtype.primitive_type is PrimitiveComplexType() else cast_to(e, NumpyComplex128Type())
            )
            self.add_import(c_imports["complex"])
            return f"cpow({b}, {e})"

        self.add_import(c_imports["math"])
        b = self._visit(b if b.dtype.primitive_type is PrimitiveFloatingPointType() else cast_to(b, NumpyFloat64Type()))
        e = self._visit(e if e.dtype.primitive_type is PrimitiveFloatingPointType() else cast_to(e, NumpyFloat64Type()))
        code = f"pow({b}, {e})"
        return self._cast_to(expr, expr.dtype).format(code)

    def _visit_Import(self, expr):
        """Render the ``Import`` model node."""
        if expr.ignore:
            return ""
        source = expr.source.name if isinstance(expr.source, AsName) else expr.source

        source = self._visit(source)

        # Get with a default value is not used here as it is
        # slower and on most occasions the import will not be in the
        # dictionary
        if source in import_dict:  # pylint: disable=consider-using-get
            source = import_dict[source]

        if source is None:
            return ""
        if expr.source in c_library_headers:
            return f"#include <{source}.h>\n"
        return f'#include "{source}.h"\n'

    def _format_and_arg(self, var):
        """
        Get the C print format string for the object var.

        Get the C print format string which will allow the generated code
        to print the variable passed as argument.

        Parameters
        ----------
        var : model object
            The object which will be printed.

        Returns
        -------
        arg_format : str
            The format which should be printed in the format string of the
            generated print expression.
        arg : str
            The code which should be printed in the arguments of the generated
            print expression to print the object.
        """
        if isinstance(var.dtype, FixedSizeNumericType):
            primitive_type = var.dtype.primitive_type
            if isinstance(primitive_type, PrimitiveComplexType):
                _, real_part = self._format_and_arg(ComplexPart(var, "real"))
                float_format, imag_part = self._format_and_arg(ComplexPart(var, "imag"))
                return (
                    f"({float_format} + {float_format}j)",
                    f"{real_part}, {imag_part}",
                )
            if isinstance(primitive_type, PrimitiveBooleanType):
                return self._format_and_arg(
                    IfTernaryOperator(
                        var,
                        CStrStr(convert_to_literal("True")),
                        CStrStr(convert_to_literal("False")),
                    )
                )
            try:
                arg_format = self.type_to_format[(primitive_type, var.dtype.precision)]
            except KeyError as error:
                raise TypeError(
                    f"Printing {var.dtype} type is not supported currently",
                ) from error
            arg = self._visit(var)
        elif isinstance(var.dtype, StringType):
            arg = self._visit(CStrStr(var))
            arg_format = "%s"
        elif isinstance(var.dtype, CharType):
            arg = self._visit(var)
            arg_format = "%s"
        else:
            try:
                arg_format = self.type_to_format[var.dtype]
            except KeyError as error:
                raise TypeError(
                    f"Printing {var.dtype} type is not supported currently",
                ) from error

            arg = self._visit(var)

        return arg_format, arg

    def _visit_CStringExpression(self, expr):
        """Render the ``CStringExpression`` model node."""
        return "".join(self._visit(CStrStr(e)) for e in expr.get_flat_expression_list())

    def _visit_CMacro(self, expr):
        """Render the ``CMacro`` model node."""
        return str(expr.macro)

    def _visit_Declare(self, expr):
        """Render the ``Declare`` model node."""
        var = expr.variable
        declaration_type = self._get_declare_type(var)

        init = f" = {self._visit(expr.value)}" if expr.value is not None else ""

        if isinstance(var.class_type, NumpyNDArrayType) and var.class_type.raw:
            assert init == ""
            preface = ""
            if isinstance(var.alloc_shape[0], int | Literal):
                init = f"[{var.alloc_shape[0]}]"
            else:
                declaration_type += "*"
                init = ""
        elif var.is_stack_array:
            preface, init = self._init_stack_array(var)
        else:
            preface = ""
            if isinstance(var.class_type, NumpyNDArrayType) and not expr.external and not var.is_alias:
                init = " = {0}"

        external = "extern " if expr.external else ""
        static = "static " if expr.static else ""
        const = "const " if isinstance(var.class_type, FinalType) and self._is_c_pointer(var) else ""

        return f"{preface}{static}{external}{const}{declaration_type} {var.name}{init};\n"

    def _visit_IndexedElement(self, expr):
        """Render the ``IndexedElement`` model node."""
        base = expr.base

        list(expr.indices)
        raise NotImplementedError(f"Indexing not implemented for {base}")

    def _visit_DottedVariable(self, expr):
        """convert dotted Variable to their C equivalent"""

        name_code = self._visit(expr.name)
        if self._is_c_pointer(expr.lhs):
            code = f"{self._visit(ObjectAddress(expr.lhs))}->{name_code}"
        else:
            lhs_code = self._visit(expr.lhs)
            code = f"{lhs_code}.{name_code}"
        if self._is_c_pointer(expr):
            return f"(*{code})"
        return code

    def _visit_ArraySize(self, expr):
        """Render the ``ArraySize`` model node."""
        arg = self._visit(ObjectAddress(expr.arg))
        return f"cspan_size({arg})"

    def _visit_ArrayShapeElement(self, expr):
        """Render the ``ArrayShapeElement`` model node."""
        arg = expr.arg
        if isinstance(arg.class_type, NumpyNDArrayType):
            idx = self._visit(expr.index)
            cast_code = f"({self._c_type(NumpyInt64Type())})"
            if self._is_c_pointer(arg):
                arg_code = self._visit(ObjectAddress(arg))
                return f"{cast_code}{arg_code}->shape[{idx}]"
            arg_code = self._visit(arg)
            return f"{cast_code}{arg_code}.shape[{idx}]"
        if isinstance(arg.class_type, StringType):
            arg_code = self._visit(ObjectAddress(arg))
            return f"cstr_size({arg_code})"
        raise NotImplementedError(f"Don't know how to represent shape of object of type {arg.class_type}")

    def _visit_Allocate(self, expr):
        """Render the ``Allocate`` model node."""
        free_code = ""
        variable = expr.variable
        if isinstance(variable.class_type, StringType):
            if expr.status in ("allocated", "unknown"):
                free_code = f"{self._visit(Deallocate(variable))}"
            if expr.shape[0] is None:
                return free_code
            if expr.alloc_type == "function":
                return free_code
            size = self._visit(expr.shape[0])
            variable_address = self._visit(ObjectAddress(expr.variable))
            container_type = self._c_type(expr.variable.class_type)
            if expr.alloc_type == "reserve":
                if expr.status != "unallocated":
                    return (
                        f"{container_type}_clear({variable_address});\n"
                        f"{container_type}_reserve({variable_address}, {size});\n"
                    )
                return f"{container_type}_reserve({variable_address}, {size});\n"
            if expr.alloc_type == "resize":
                return f"{container_type}_resize({variable_address}, {size}, {0});\n"
            return free_code
        if isinstance(variable.class_type, (NumpyNDArrayType)):
            # free the array if its already allocated and checking if its not null if the status is unknown
            if expr.status == "unknown":
                data_ptr = ObjectAddress(DottedVariable(VoidType(), "data", lhs=variable, memory_handling="alias"))
                free_code = f"if ({self._visit(data_ptr)} != NULL)\n"
                free_code += "".join(("{\n", self._visit(Deallocate(variable)), "}\n"))
            elif expr.status == "allocated":
                free_code += self._visit(Deallocate(variable))
            if expr.alloc_type == "function":
                return free_code

            tot_shape = self._visit(functools.reduce(Mul.make_simplified, expr.shape))
            c_type = self._c_type(variable.class_type)
            element_type = self._c_type(variable.class_type.element_type)

            if expr.like:
                buffer_array = ""
                if isinstance(expr.like.class_type, VoidType):
                    dummy_array_name = self._visit(ObjectAddress(expr.like))
                else:
                    raise NotImplementedError("Unexpected type passed to like argument")
            else:
                dummy_array_name = self.scope.get_new_name(f"{variable.name}_ptr")
                buffer_array_var = Variable(
                    variable.class_type.datatype,
                    dummy_array_name,
                    memory_handling="alias",
                )
                self.scope.insert_variable(buffer_array_var)
                buffer_array = f"{dummy_array_name} = malloc(sizeof({element_type}) * ({tot_shape}));\n"

            order = "c_COLMAJOR" if variable.order == "F" else "c_ROWMAJOR"
            shape = ", ".join(self._visit(i) for i in expr.shape)

            return (
                free_code
                + buffer_array
                + f"{self._visit(variable)} = ({c_type})cspan_md_layout({order}, {dummy_array_name}, {shape});\n"
            )
        if variable.is_alias:
            var_code = self._visit(ObjectAddress(variable))
            if expr.like:
                declaration_type = self._get_declare_type(expr.like)
                malloc_size = f"sizeof({declaration_type})"
                if variable.rank:
                    tot_shape = self._visit(functools.reduce(Mul.make_simplified, expr.shape))
                    malloc_size = f"{malloc_size} * ({tot_shape})"
                return f"{var_code} = malloc({malloc_size});\n"
            raise NotImplementedError(f"Allocate not implemented for {variable.class_type}")
        raise NotImplementedError(f"Allocate not implemented for {variable.class_type}")

    def _visit_Deallocate(self, expr):
        """Render the ``Deallocate`` model node."""
        var = expr.variable
        if isinstance(var.class_type, StringType):
            if var.is_alias:
                return ""

            variable_address = self._visit(ObjectAddress(var))
            container_type = self._c_type(var.class_type)
            return f"{container_type}_drop({variable_address});\n"
        if isinstance(var.dtype, CustomDataType):
            variable_address = self._visit(ObjectAddress(var))
            x2py__del = var.cls_base.scope.find("__del__")
            if x2py__del:
                return f"{x2py__del.name}({variable_address});\n"
            return ""
        if isinstance(var.class_type, NumpyNDArrayType):
            if var.is_alias:
                return ""
            data_ptr = DottedVariable(VoidType(), "data", lhs=var, memory_handling="alias")
            data_ptr_code = self._visit(ObjectAddress(data_ptr))
            return f"free({data_ptr_code});\n{data_ptr_code} = NULL;\n"
        variable_address = self._visit(ObjectAddress(var))
        return f"free({variable_address});\n"

    def _visit_FunctionAddress(self, expr):
        """Render the ``FunctionAddress`` model node."""
        return expr.name

    def _visit_FunctionOverloadSet(self, expr):
        """Render the ``FunctionOverloadSet`` model node."""
        return "".join(self._visit(f) for f in expr.functions)

    def _visit_FunctionDef(self, expr):
        """Render the ``FunctionDef`` model node."""
        if not expr.is_semantic:
            return ""

        self._validate_c_function_results(expr)

        sep = self._visit(SeparatorComment(40))

        inner_funcs = "".join(self._visit(f).removeprefix(sep).removesuffix(sep) + "\n" for f in expr.functions)

        self.set_scope(expr.scope)

        # Collect results filtering out NIL
        results = [r for r in self.scope.collect_all_tuple_elements(expr.results.var) if isinstance(r, Variable)]
        returning_tuple = False
        self._push_additional_function_args(expr, results, returning_tuple)

        body = self._visit(expr.body)
        decs = self._function_declarations(expr, results, returning_tuple)

        self._additional_args.pop()
        for i in expr.imports:
            self.add_import(i)
        docstring = self._visit(expr.docstring) if expr.docstring else ""

        parts = [
            sep,
            inner_funcs,
            docstring,
            f"{self._function_signature(expr)}\n{{\n",
            decs,
            body,
            "}\n",
            sep,
        ]

        self.exit_scope()

        return "".join(p for p in parts if p)

    @staticmethod
    def _validate_c_function_results(function) -> None:
        """Reject stack arrays that cannot be returned from C."""
        for result in function.scope.collect_all_tuple_elements(function.results.var):
            if result.rank and result.memory_handling == "stack":
                raise ValueError("Can't return a stack array from C code")

    def _push_additional_function_args(self, function, results, returning_tuple) -> None:
        """Track output and global variables passed as hidden arguments."""
        self._additional_args.append(results if len(results) > 1 or returning_tuple else [])
        self._additional_args[-1].extend(
            variable for variable in function.global_vars if get_direct_module(variable) is None
        )

    def _function_declarations(self, function, results, returning_tuple):
        """Render local and result declarations for a C function."""
        declarations = [
            Declare(
                variable,
                value=(NIL if variable.is_alias and isinstance(variable.class_type, VoidType | BindCPointer) else None),
            )
            for variable in function.local_vars
        ]
        if len(results) == 1 and not returning_tuple:
            result = results[0]
            if not result.is_temp or result.rank:
                declarations.append(Declare(result))
        return "".join(self._visit(declaration) for declaration in declarations)

    def _visit_FunctionCall(self, expr):
        """Render the ``FunctionCall`` model node."""
        func = expr.funcdef
        if func.name in {"memcpy", "memset", "strlen"}:
            self.add_import(c_imports["string"])
        parent_assign = get_direct_assignment(expr)
        returns_via_output_args = self._returns_via_output_args(func)
        # Ensure the correct syntax is used for pointers
        args = [
            self._prepare_call_argument(argument.value, formal.var)
            for argument, formal in zip(expr.args, func.arguments, strict=False)
        ]
        args = self._insert_after_bound_argument(func, args, self._temporary_args)

        for v in func.global_vars:
            if get_direct_module(v) is None:
                args.append(ObjectAddress(v))

        if parent_assign is not None and returns_via_output_args:
            output_args = self._output_call_arguments(parent_assign)
            args = self._insert_after_bound_argument(func, args, output_args)

        self._temporary_args = []
        args = ", ".join(self._visit(ai) for a in args for ai in self.scope.collect_all_tuple_elements(a))

        call_code = f"{func.name}({args})"
        if parent_assign is not None and returns_via_output_args:
            return f"{call_code};\n"
        if func.results.var is not NIL:
            return call_code
        return f"{call_code};\n"

    def _prepare_call_argument(self, argument, formal):
        """Adapt one call argument to the formal C pointer contract."""
        if not self._is_c_pointer(formal):
            return argument
        if isinstance(argument, Variable):
            return ObjectAddress(argument)
        if self._is_c_pointer(argument):
            return argument
        temporary = self.scope.get_temporary_variable(formal.dtype)
        self._additional_code += self._visit(Assign(temporary, argument))
        return ObjectAddress(temporary)

    @staticmethod
    def _insert_after_bound_argument(function, arguments, inserted):
        """Insert hidden arguments after a bound receiver when present."""
        if function.arguments and function.arguments[0].bound_argument:
            return arguments[:1] + inserted + arguments[1:]
        return inserted + arguments

    def _output_call_arguments(self, parent_assign):
        """Build address arguments for results returned through outputs."""
        if isinstance(parent_assign.lhs, PythonTuple):
            result_args = parent_assign.lhs.args
        else:
            result_args = self.scope.collect_all_tuple_elements(parent_assign.lhs)
        output_args = []
        for argument in result_args:
            output_arg = ObjectAddress(argument)
            if not isinstance(argument, ObjectAddress) and self._is_c_pointer(argument):
                output_arg = ObjectAddress(output_arg)
            output_args.append(output_arg)
        return output_args

    def _visit_Return(self, expr):
        """Render the ``Return`` model node."""
        func = get_enclosing_function(expr)
        assert func is not None
        code = ""

        return_obj = expr.expr
        if return_obj is None:
            args = []
        else:
            args = [(ObjectAddress(return_obj) if self._is_c_pointer(return_obj) else return_obj)]

        if len(args) == 0:
            return code + "return;\n"

        returned_value = self.scope.collect_tuple_element(args[0])

        return code + f"return {self._visit(returned_value)};\n"

    def _visit_Pass(self, expr):
        """Render the ``Pass`` model node."""
        return "// pass\n"

    def _visit_Add(self, expr):
        """Render the ``Add`` model node."""
        return " + ".join(self._visit(a) for a in expr.args)

    def _visit_Minus(self, expr):
        """Render the ``Minus`` model node."""
        args = [self._visit(a) for a in expr.args]
        if len(args) == 1:
            return f"-{args[0]}"
        return " - ".join(args)

    def _visit_Mul(self, expr):
        """Render the ``Mul`` model node."""
        return " * ".join(self._visit(a) for a in expr.args)

    def _visit_Div(self, expr):
        """Render the ``Div`` model node."""
        if all(a.dtype.primitive_type is PrimitiveIntegerType() for a in expr.args):
            args = [cast_to(a, NumpyFloat64Type()) for a in expr.args]
        else:
            args = expr.args
        return " / ".join(self._visit(a) for a in args)

    def _visit_FloorDiv(self, expr):
        # the result type of the floor division is dependent on the arguments
        # type, if all arguments are integers or booleans the result is integer
        # otherwise the result type is float
        """Render the ``FloorDiv`` model node."""
        need_to_cast = all(
            a.dtype.primitive_type in (PrimitiveIntegerType(), PrimitiveBooleanType()) for a in expr.args
        )
        if need_to_cast:
            self.add_import(c_imports["pyc_math_c"])
            cast_type = self._c_type(expr.dtype)
            return f"py_floor_div_{cast_type}({self._visit(expr.args[0])}, {self._visit(expr.args[1])})"

        self.add_import(c_imports["math"])
        code = " / ".join(
            self._visit(a if a.dtype.primitive_type is PrimitiveFloatingPointType() else cast_to(a, NumpyFloat64Type()))
            for a in expr.args
        )
        return f"floor({code})"

    def _visit_RShift(self, expr):
        """Render the ``RShift`` model node."""
        return " >> ".join(self._visit(a) for a in expr.args)

    def _visit_LShift(self, expr):
        """Render the ``LShift`` model node."""
        return " << ".join(self._visit(a) for a in expr.args)

    def _visit_BitXor(self, expr):
        """Render the ``BitXor`` model node."""
        if expr.dtype is NumpyBoolType():
            return f"{self._visit(expr.args[0])} != {self._visit(expr.args[1])}"
        return " ^ ".join(self._visit(a) for a in expr.args)

    def _visit_BitOr(self, expr):
        """Render the ``BitOr`` model node."""
        args = [
            (
                f"({self._visit(a)})"
                if isinstance(a, Operator) and not isinstance(a, AssociativeParenthesis)
                else self._visit(a)
            )
            for a in expr.args
        ]
        if expr.dtype is NumpyBoolType():
            return " || ".join(args)
        return " | ".join(args)

    def _visit_BitAnd(self, expr):
        """Render the ``BitAnd`` model node."""
        args = [
            (
                f"({self._visit(a)})"
                if isinstance(a, Operator) and not isinstance(a, AssociativeParenthesis)
                else self._visit(a)
            )
            for a in expr.args
        ]
        if expr.dtype is NumpyBoolType():
            return " && ".join(args)
        return " & ".join(args)

    def _visit_Invert(self, expr):
        """Render the ``Invert`` model node."""
        arg = self._visit(expr.args[0])
        if expr.dtype is NumpyBoolType():
            return f"!{arg}"
        return f"~{arg}"

    def _visit_AssociativeParenthesis(self, expr):
        """Render the ``AssociativeParenthesis`` model node."""
        return f"({self._visit(expr.args[0])})"

    def _visit_UnaryPlus(self, expr):
        """Render the ``UnaryPlus`` model node."""
        return f"+{self._visit(expr.args[0])}"

    def _visit_UnarySub(self, expr):
        """Render the ``UnarySub`` model node."""
        return f"-{self._visit(expr.args[0])}"

    def _visit_AugAssign(self, expr):
        """Render the ``AugAssign`` model node."""
        op = expr.op
        lhs = expr.lhs
        rhs = expr.rhs

        if op == "//" or (op == "%" and isinstance(lhs.dtype.primitive_type, PrimitiveFloatingPointType)):
            _expr = expr.to_basic_assign()
            return self._visit(_expr)

        lhs_code = self._visit(lhs)
        rhs_code = self._visit(rhs)
        return f"{lhs_code} {op}= {rhs_code};\n"

    def _visit_Assign(self, expr):
        """Render the ``Assign`` model node."""
        lhs = expr.lhs
        rhs = expr.rhs

        if isinstance(rhs, FunctionCall) and self._returns_via_output_args(rhs.funcdef):
            return self._visit(rhs)

        lhs_code = self._visit(lhs)
        rhs_code = self._visit(rhs)
        return f"{lhs_code} = {rhs_code};\n"

    def _visit_AliasAssign(self, expr):
        """Render the ``AliasAssign`` model node."""
        lhs_var = expr.lhs
        rhs_var = expr.rhs

        lhs_address = ObjectAddress(lhs_var)
        rhs_address = ObjectAddress(rhs_var)

        # The condition below handles the case of reassigning a pointer to an array view.
        if isinstance(lhs_var, Variable) and lhs_var.is_ndarray and not lhs_var.is_optional:
            lhs = self._visit(lhs_var)

            if isinstance(rhs_var, Variable) and rhs_var.is_ndarray:
                lhs_ptr = self._visit(lhs_address)
                rhs = self._visit(rhs_address)
                rhs_type = self._c_type(rhs_var.class_type)
                slicing = ", ".join(["{c_ALL}"] * lhs_var.rank)
                code = f"{lhs} = cspan_slice({rhs}, {rhs_type}, {slicing});\n"
                if lhs_var.order != rhs_var.order:
                    code += f"cspan_transpose({lhs_ptr});\n"
                return code
            rhs = self._visit(rhs_var)
            return f"{lhs} = {rhs};\n"
        lhs = self._visit(lhs_address)
        rhs = self._visit(rhs_address)

        return f"{lhs} = {rhs};\n"

    def _visit_CodeBlock(self, expr):
        """Render the ``CodeBlock`` model node."""
        body_exprs = expr.body
        body_stmts = []
        for b in body_exprs:
            code = self._visit(b)
            code = self._additional_code + code
            self._additional_code = ""
            body_stmts.append(code)
        return "".join(self._visit(b) for b in body_stmts)

    def _visit_ComplexPart(self, expr):
        """Render the ``ComplexPart`` model node."""
        function = "creal" if expr.part == "real" else "cimag"
        return f"{function}({self._visit(expr.arg)})"

    def _visit_IsNot(self, expr):
        """Render the ``IsNot`` model node."""
        return self._handle_is_operator("!=", expr)

    def _visit_Is(self, expr):
        """Render the ``Is`` model node."""
        return self._handle_is_operator("==", expr)

    def _visit_Variable(self, expr):
        """Render the ``Variable`` model node."""
        if self._is_c_pointer(expr):
            return f"(*{expr.name})"
        return expr.name

    def _visit_FunctionDefArgument(self, expr):
        """Render the ``FunctionDefArgument`` model node."""
        return self._visit(expr.name)

    def _visit_FunctionCallArgument(self, expr):
        """Render the ``FunctionCallArgument`` model node."""
        return self._visit(expr.value)

    def _visit_ObjectAddress(self, expr):
        """Render the ``ObjectAddress`` model node."""
        obj_code = self._visit(expr.obj)
        if isinstance(expr.obj, ObjectAddress):
            return f"&{obj_code}"
        if obj_code.startswith("(*") and obj_code.endswith(")"):
            return f"{obj_code[2:-1]}"
        if not self._is_c_pointer(expr.obj):
            return f"&{obj_code}"
        return obj_code

    def _visit_PointerCast(self, expr):
        """Render the ``PointerCast`` model node."""
        declare_type = self._get_declare_type(expr.cast_type)
        if not self._is_c_pointer(expr.cast_type):
            declare_type += "*"
        obj = expr.obj
        if not isinstance(obj, ObjectAddress):
            obj = ObjectAddress(expr.obj)
        var_code = self._visit(obj)
        return f"(*({declare_type})({var_code}))"

    def _visit_Comment(self, expr):
        """Render the ``Comment`` model node."""
        comments = self._visit(expr.text)

        return "/*" + comments + "*/\n"

    def _visit_Symbol(self, expr):
        """Render the ``Symbol`` model node."""
        return expr

    def _visit_CommentBlock(self, expr):
        """Render the ``CommentBlock`` model node."""
        txts = expr.comments
        header = expr.header
        header_size = len(expr.header)

        ln = max(len(i) for i in txts)
        if ln < max(20, header_size + 4):
            ln = 20
        top = "/*" + "_" * int((ln - header_size) / 2) + header + "_" * int((ln - header_size) / 2) + "*/\n"
        ln = len(top) - 4
        bottom = "/*" + "_" * ln + "*/\n"

        txts = ["/*" + t + " " * (ln - len(t)) + "*/\n" for t in txts]

        body = "".join(i for i in txts)

        return "".join([top, body, bottom])

    def _visit_EmptyNode(self, expr):
        """Render the ``EmptyNode`` model node."""
        return ""

    def _visit_CustomDataType(self, expr):
        """Render the ``CustomDataType`` model node."""
        return "struct " + expr.low_level_name

    def _visit_ClassDef(self, expr):
        """Render the ``ClassDef`` model node."""
        methods = "".join(self._visit(method) for method in expr.methods)
        interfaces = "".join(
            self._visit(function) for interface in expr.overload_sets for function in interface.functions
        )

        return methods + interfaces

    # ================== String methods ==================

    def _visit_CStrStr(self, expr):
        """Render the ``CStrStr`` model node."""
        arg = expr.args[0]
        code = self._visit(ObjectAddress(arg))
        if code.startswith("&cstr_lit("):
            return code[10:-1]
        return f"cstr_str({code})"

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _sort_imports(self, imports):
        """
        Sort imports to avoid any errors due to bad ordering.

        Sort imports. This is important so that types exist before they are used to create
        container types. E.g. it is important that complex or inttypes be imported before
        vec_int or vec_double_complex is declared.

        Parameters
        ----------
        imports : list[Import]
            A list of the imports.

        Returns
        -------
        list[Import]
            A sorted list of the imports.
        """
        stc_imports = [i for i in imports if str(i.source) in import_header_guard_prefix]
        split_stc_imports = [Import(i.source, t) for i in stc_imports for t in i.target]
        split_stc_imports.sort(
            key=lambda i: (
                # Sort by rank to avoid elements printed after classes
                (
                    next(iter(i.target)).object.class_type.rank,
                    # Additionally sort by the source file
                    str(i.source),
                    # Finally sort by type name for reproducibility
                    next(iter(i.target)).local_alias,
                )
            )
        )

        non_stc_imports = [i for i in imports if i not in stc_imports]
        non_stc_imports.sort(key=lambda i: str(i.source))

        return non_stc_imports + split_stc_imports

    def _format_code(self, lines):
        """Format code."""
        return self._indent_code(lines)

    def _is_c_pointer(self, a):
        """
        Indicate whether the object is a pointer in C code.

        Some objects are accessed via a C pointer so that they can be modified in
        their scope and that modification can be retrieved elsewhere. This
        information cannot be found trivially so this function provides that
        information while avoiding easily outdated code to be repeated.

        The main reasons for this treatment are:
        1. It is the actual memory address of an object
        2. It is a reference to another object (e.g. an alias, an optional argument, or one of multiple return arguments)

        See codegen_stage.md in the developer docs for more details.

        Parameters
        ----------
        a : model object
            The object whose storage we are enquiring about.

        Returns
        -------
        bool
            True if a C pointer, False otherwise.
        """
        if a is NIL or isinstance(a, ObjectAddress | PointerCast | CStrStr):
            return True
        if isinstance(a, FunctionCall):
            a = a.funcdef.results.var
        # STC _at and _at_mut functions return pointers
        if isinstance(a, IndexedElement):
            return self._indexed_element_is_c_pointer(a)
        if not isinstance(a, Variable):
            return False
        additional_argument = self._is_additional_c_argument(a)
        if isinstance(a.class_type, NumpyNDArrayType):
            return a.is_optional or additional_argument or (a.class_type.raw and a.is_alias)

        if isinstance(a.class_type, CustomDataType) and a.is_argument and not isinstance(a.class_type, FinalType):
            return True

        return a.is_alias or a.is_optional or additional_argument

    @staticmethod
    def _indexed_element_is_c_pointer(element):
        """Return whether an indexed element is represented as a C pointer."""
        raw_array = isinstance(element.base.class_type, NumpyNDArrayType) and element.base.class_type.raw
        return not raw_array and element.rank == 0

    def _is_additional_c_argument(self, variable):
        """Return whether a variable is tracked as a hidden C argument."""
        return any(variable is item for arguments in self._additional_args for item in arguments)

    # ============ Elements ============ #

    @staticmethod
    def _x2py_malloc_helper():
        """Handle x2py malloc helper for the current generation context."""
        return (
            "void* x2py_malloc(size_t size)\n"
            "{\n"
            '    const char* fail_alloc = getenv("X2PY_WRAPPER_FAIL_ALLOC");\n'
            "    if (fail_alloc != NULL && fail_alloc[0] != '\\0' && fail_alloc[0] != '0') {\n"
            "        return NULL;\n"
            "    }\n"
            "    return malloc(size == 0 ? 1 : size);\n"
            "}\n"
        )

    def _c_type(self, dtype):
        """
        Find the corresponding C type of the Type.

        For scalar types, this function searches for the corresponding C data type
        in the `dtype_registry`.

        Parameters
        ----------
        dtype : Type
            The data type of the expression.

        Returns
        -------
        str
            The code which declares the data type in C.

        Raises
        ------
        TypeError
            If the dtype is not found in the dtype_registry.
        """
        if isinstance(dtype, FixedSizeNumericType):
            primitive_type = dtype.primitive_type
            if isinstance(primitive_type, PrimitiveComplexType):
                self.add_import(c_imports["complex"])
                return f"{self._c_type(dtype.element_type)} complex"
            if isinstance(primitive_type, PrimitiveIntegerType):
                self.add_import(c_imports["stdint"])
            elif isinstance(dtype, NumpyBoolType):
                self.add_import(c_imports["stdbool"])
                return "bool"

            key = (primitive_type, dtype.precision)

        elif isinstance(dtype, StringType):
            self.add_import(c_imports["stc/cstr"])
            return "cstr"

        elif isinstance(dtype, CustomDataType):
            return self._visit(dtype)

        else:
            key = dtype

        try:
            return self.dtype_registry[key]
        except KeyError:
            raise TypeError(f"Unsupported C dtype: {dtype}") from None

    def _get_declare_type(self, expr):
        """
        Get the string which describes the type in a declaration.

        This function returns the code which describes the type
        of the `expr` object such that the declaration can be written as:
        `f"{self._get_declare_type(expr)} {expr.name}"`
        The function takes care of reporting errors for unknown types and
        importing any necessary additional imports (e.g. stdint/ndarrays).

        Parameters
        ----------
        expr : Variable
            The variable whose type should be described.

        Returns
        -------
        str
            The code describing the type.

        Raises
        ------
        X2pyCodegenError
            If the type is not supported in the C code.

        Examples
        --------
        >>> v = Variable(NumpyInt64Type(), 'x')
        >>> self._get_declare_type(v)
        'int64_t'

        For an object accessed via a pointer:
        >>> v = Variable(NumpyNDArrayType.get_new(NumpyInt64Type(), 1, None), 'x', is_optional=True)
        >>> self._get_declare_type(v)
        'array_int64_1d*'
        """
        class_type = expr.class_type

        if isinstance(class_type, NumpyNDArrayType) and class_type.raw:
            dtype = self._c_type(class_type.element_type)
        elif isinstance(class_type, NumpyNDArrayType):
            dtype = self._c_type(class_type)
        else:
            dtype = self._c_type(expr.class_type)

        if self._is_c_pointer(expr) and not (isinstance(class_type, NumpyNDArrayType) and class_type.raw):
            return f"{dtype}*"
        return dtype

    def _function_signature(self, expr, print_arg_names=True):
        """
        Get the C representation of the function signature.

        Extract from the function definition `expr` all the
        information (name, input, output) needed to create the
        function signature and return a string describing the
        function.

        This is not a declaration as the signature does not end
        with a semi-colon.

        Parameters
        ----------
        expr : FunctionDef
            The function definition for which a signature is needed.

        print_arg_names : bool, default : True
            Indicates whether argument names should be printed.

        Returns
        -------
        str
            Signature of the function.
        """
        arg_vars = [a.var for a in expr.arguments]
        result_vars = [v for v in expr.scope.collect_all_tuple_elements(expr.results.var) if v and not v.is_argument]

        n_results = len(result_vars)

        if n_results > 1:
            ret_type = self._c_type(VoidType())
            if expr.arguments and expr.arguments[0].bound_argument:
                # Place the first arg_var (the bound class object) first
                arg_vars = arg_vars[:1] + result_vars + arg_vars[1:]
            else:
                arg_vars = result_vars + arg_vars
            self._additional_args.append(result_vars)  # Ensure correct result for _is_c_pointer
        elif n_results == 1:
            ret_type = self._get_declare_type(result_vars[0])
            self._additional_args.append([])
        else:
            ret_type = self._c_type(VoidType())
            self._additional_args.append([])

        for v in expr.global_vars:
            if get_direct_module(v) is None:
                self._additional_args[-1].append(v)
                arg_vars.append(v)
        arg_vars = [ai for a in arg_vars for ai in expr.scope.collect_all_tuple_elements(a)]

        name = expr.name
        if not arg_vars:
            arg_code = "void"
        else:

            def get_arg_declaration(var):
                """Get the code which declares the argument variable."""
                const = "const " if isinstance(var.class_type, FinalType) else ""
                code = const + self._get_declare_type(var)
                if print_arg_names:
                    code += " " + var.name
                return code

            arg_code_list = [
                (self._function_signature(var, False) if isinstance(var, FunctionAddress) else get_arg_declaration(var))
                for var in arg_vars
            ]
            arg_code = ", ".join(arg_code_list)

        self._additional_args.pop()

        static = "static " if expr.is_static else ""

        if isinstance(expr, FunctionAddress):
            return f"{static}{ret_type} (*{name})({arg_code})"
        return f"{static}{ret_type} {name}({arg_code})"

    def _cast_to(self, expr, dtype):
        """
        Add a cast to an expression when needed.

        Get a format string which provides the code to cast the object `expr`
        to the specified dtype. If the dtypes already
        match then the format string will simply print the expression.

        Parameters
        ----------
        expr : model object
            The expression to be cast.
        dtype : Type
            The target type of the cast.

        Returns
        -------
        str
            A format string that contains the desired cast type.
            NB: You should insert the expression to be cast in the string
            after using this function.
        """
        if expr.dtype != dtype:
            cast = self._c_type(dtype)
            return f"({cast}){{}}"
        return "{}"

    @staticmethod
    def _result_vars(func):
        """Handle result vars for the current generation context."""
        if func.scope is None:
            return [func.results.var] if func.results.var is not NIL else []
        return [v for v in func.scope.collect_all_tuple_elements(func.results.var) if isinstance(v, Variable)]

    def _returns_via_output_args(self, func):
        """Handle returns via output args for the current generation context."""
        return len(self._result_vars(func)) > 1

    def _handle_is_operator(self, Op, expr):
        """
        Get the code to print an `is` or `is not` expression.

        Get the code to print an `is` or `is not` expression. These two operators
        function similarly so this helper function reduces code duplication.

        Parameters
        ----------
        Op : str
            The C operator representing "is" or "is not".

        expr : Is/IsNot
            The expression being printed.

        Returns
        -------
        str
            The code describing the expression.

        Raises
        ------
        X2pyError : Raised if the comparison is poorly defined.
        """

        lhs = self._visit(expr.args[0])
        rhs = self._visit(expr.args[1])
        a = expr.args[0]
        b = expr.args[1]

        if NIL in expr.args:
            lhs = ObjectAddress(expr.args[0]) if isinstance(expr.args[0], Variable) else expr.args[0]
            rhs = ObjectAddress(expr.args[1]) if isinstance(expr.args[1], Variable) else expr.args[1]

            lhs = self._visit(lhs)
            rhs = self._visit(rhs)
            return f"{lhs} {Op} {rhs}"

        if a.dtype is NumpyBoolType() and b.dtype is NumpyBoolType():
            return f"{lhs} {Op} {rhs}"
        raise TypeError("C is/is not printing is only supported for booleans and nil checks")

    def _indent_code(self, code):
        """
        Add the necessary indentation to a string of code or a list of code lines.

        Add the necessary indentation to a string of code or a list of code lines.

        Parameters
        ----------
        code : str | iterable[str]
            The code which needs indenting.

        Returns
        -------
        str | list[str]
            The indented code. The type matches the type of the argument.
        """

        if isinstance(code, str):
            code_lines = self._indent_code(code.splitlines(True))
            return "".join(code_lines)

        tab = " " * self._default_settings["tabwidth"]

        code = [line.lstrip(" \t") for line in code]

        increase = [int(line.endswith("{\n")) for line in code]
        decrease = [int(any(map(line.startswith, "}\n"))) for line in code]

        pretty = []
        level = 0
        for n, line in enumerate(code):
            if line == "" or line == "\n":
                pretty.append(line)
                continue
            level -= decrease[n]
            indent = tab * level
            pretty.append(f"{indent}{line}")
            level += increase[n]
        return pretty
