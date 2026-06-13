"""
Module containing the `CCodePrinter` class which converts X2py's AST to
strings of C code.
"""

import ast
import functools
import sys
from itertools import chain, product

import numpy as np

from ..bind_c import BindCPointer
from ..models.datatypes import PythonComplex
from ..bindings.c_concepts import (
    CMacro,
    CStackArray,
    CStringExpression,
    CStrStr,
    ObjectAddress,
    PointerCast,
)
from ..models.core import (
    AliasAssign,
    AsName,
    Assign,
    AugAssign,
    CodeBlock,
    Deallocate,
    Declare,
    For,
    FunctionAddress,
    FunctionCall,
    FunctionCallArgument,
    FunctionDef,
    get_direct_module,
    get_enclosing_function,
    If,
    IfSection,
    Import,
    Module,
    SeparatorComment,
)
from ..models.datatypes import (
    CharType,
    CustomDataType,
    FinalType,
    FixedSizeNumericType,
    FixedSizeType,
    HomogeneousContainerType,
    PrimitiveBooleanType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    PythonNativeBool,
    PythonNativeInt,
    StringType,
    TupleType,
    VoidType,
)
from ..models.core import Function, Slice
from ..models.datatypes import (
    Literal,
    LiteralFalse,
    LiteralFloat,
    LiteralImaginaryUnit,
    LiteralInteger,
    LiteralString,
    LiteralTrue,
    Nil,
    convert_to_literal,
)
from ..models.datatypes import (
    NumpyFloat32Type,
    NumpyFloat64Type,
    NumpyFloat128Type,
    NumpyNDArrayType,
    numpy_precision_map,
)
from ..models.core import (
    IfTernaryOperator,
    Add,
    AssociativeParenthesis,
    Div,
    Gt,
    Lt,
    Minus,
    Mod,
    Mul,
    Ne,
    Operator,
    Pow,
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
    "stc/hmap": "_TOOLS_DICT",
    "stc/hset": "_TOOLS_SET",
    "stc/vec": "_TOOLS_LIST",
}

stc_extension_mapping = {
    "stc/common": "STC_Extensions/Common_extensions",
    "stc/hmap": "STC_Extensions/Dict_extensions",
    "stc/hset": "STC_Extensions/Set_extensions",
    "stc/vec": "STC_Extensions/List_extensions",
}

class CCodePrinter(CodePrinter):
    """
    A printer for printing code in C.

    A printer to convert X2py's AST to strings of c code.
    As for all printers the navigation of this file is done via _print_X
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

    _default_settings = {
        "tabwidth": 4,
    }

    dtype_registry = {
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

    type_to_format = {
        (PrimitiveFloatingPointType(), 8): "%.15lf",
        (PrimitiveFloatingPointType(), 4): "%.6f",
        (PrimitiveIntegerType(), 4): "%d",
        (PrimitiveIntegerType(), 8): LiteralString("%") + CMacro("PRId64"),
        (PrimitiveIntegerType(), 2): LiteralString("%") + CMacro("PRId16"),
        (PrimitiveIntegerType(), 1): LiteralString("%") + CMacro("PRId8"),
    }

    def __init__(self, filename, *, verbose, prefix_module=None):

        super().__init__(verbose)
        self.prefix_module = prefix_module
        self._additional_imports = {"stdlib": c_imports["stdlib"]}
        self._additional_code = ""
        self._additional_args = []
        self._temporary_args = []
        self._in_header = False

    def sort_imports(self, imports):
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
        stc_imports = [
            i for i in imports if str(i.source) in import_header_guard_prefix
        ]
        split_stc_imports = [Import(i.source, t) for i in stc_imports for t in i.target]
        split_stc_imports.sort(
            key=lambda i:
            # Sort by rank to avoid elements printed after classes
            (
                next(iter(i.target)).object.class_type.rank,
                # Additionally sort by the source file
                str(i.source),
                # Finally sort by type name for reproducibility
                next(iter(i.target)).local_alias,
            )
        )

        non_stc_imports = [i for i in imports if i not in stc_imports]
        non_stc_imports.sort(key=lambda i: str(i.source))

        return non_stc_imports + split_stc_imports

    def _format_code(self, lines):
        return self.indent_code(lines)

    def is_c_pointer(self, a):
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
        if isinstance(a, (Nil, ObjectAddress, PointerCast, CStrStr)):
            return True
        if isinstance(a, FunctionCall):
            a = a.funcdef.results.var
        # STC _at and _at_mut functions return pointers
        if (
            isinstance(a, IndexedElement)
            and not isinstance(a.base.class_type, CStackArray)
            and a.rank == 0
        ):
            return True
        if not isinstance(a, Variable):
            return False
        if isinstance(a.class_type, NumpyNDArrayType):
            return a.is_optional or any(
                a is bi for b in self._additional_args for bi in b
            )

        if (
            isinstance(
                a.class_type, (CustomDataType, HomogeneousContainerType)
            )
            and a.is_argument
            and not isinstance(a.class_type, FinalType)
        ):
            return True

        return (
            a.is_alias
            or a.is_optional
            or any(a is bi for b in self._additional_args for bi in b)
        )

    # ============ Elements ============ #

    def _print_PythonAbs(self, expr):
        if expr.arg.dtype.primitive_type is PrimitiveFloatingPointType():
            self.add_import(c_imports["math"])
            func = "fabs"
        elif expr.arg.dtype.primitive_type is PrimitiveComplexType():
            self.add_import(c_imports["complex"])
            func = "cabs"
        else:
            func = "labs"
        return "{}({})".format(func, self._print(expr.arg))

    def _print_PythonRound(self, expr):
        self.add_import(c_imports["pyc_math_c"])
        arg = self._print(expr.arg)
        ndigits = self._print(expr.ndigits or LiteralInteger(0))
        if isinstance(
            expr.arg.class_type.primitive_type,
            (PrimitiveBooleanType, PrimitiveIntegerType),
        ):
            return f"ipyc_bankers_round({arg}, {ndigits})"
        else:
            return f"fpyc_bankers_round({arg}, {ndigits})"

    def _print_PythonFloat(self, expr):
        value = self._print(expr.arg)
        type_name = self.get_c_type(expr.dtype)
        return "({0})({1})".format(type_name, value)

    def _print_PythonInt(self, expr):
        self.add_import(c_imports["stdint"])
        value = self._print(expr.arg)
        type_name = self.get_c_type(expr.dtype)
        return "({0})({1})".format(type_name, value)

    def _print_PythonBool(self, expr):
        value = self._print(expr.arg)
        return "({} != 0)".format(value)

    def _print_Literal(self, expr):
        return repr(expr.python_value)

    def _print_LiteralInteger(self, expr):
        if (
            isinstance(expr, LiteralInteger)
            and getattr(expr.dtype, "precision", -1) == 8
        ):
            self.add_import(c_imports["stdint"])
            return f"INT64_C({repr(expr.python_value)})"
        return repr(expr.python_value)

    def _print_LiteralFloat(self, expr):
        if isinstance(expr, LiteralFloat) and expr.dtype.precision == 4:
            return f"{repr(expr.python_value)}f"
        return repr(expr.python_value)

    def _print_LiteralComplex(self, expr):
        if expr.real == LiteralFloat(0):
            return self._print(
                AssociativeParenthesis(
                    Mul(expr.imag, LiteralImaginaryUnit())
                )
            )
        else:
            return self._print(
                AssociativeParenthesis(
                    Add(expr.real, Mul(expr.imag, LiteralImaginaryUnit()))
                )
            )

    def _print_PythonComplex(self, expr):
        if expr.is_cast:
            value = self._print(expr.internal_var)
        else:
            value = self._print(
                AssociativeParenthesis(
                    Add(expr.real, Mul(expr.imag, LiteralImaginaryUnit()))
                )
            )
        type_name = self.get_c_type(expr.dtype)
        return "({0})({1})".format(type_name, value)

    def _print_LiteralImaginaryUnit(self, expr):
        self.add_import(c_imports["complex"])
        return "_Complex_I"

    def _print_Header(self, expr):
        return ""

    def _print_ModuleHeader(self, expr):
        self.set_scope(expr.module.scope)
        self._in_header = True
        name = expr.module.name
        if isinstance(name, AsName):
            name = name.name
        classes = ""
        func_blocks = []
        for classDef in expr.module.classes:
            if classDef.docstring is not None:
                classes += self._print(classDef.docstring)
            classes += f"struct {classDef.name} {{\n"
            # Is external is required to avoid the default initialisation of containers
            attrib_decl = [
                self._print(Declare(var, external=True)) for var in classDef.attributes
            ]
            classes += "".join(d.removeprefix("extern ") for d in attrib_decl)
            func_blocks.append("")
            for method in classDef.methods:
                if method.is_semantic:
                    func_blocks[-1] += f"{self.function_signature(method)};\n"
            for interface in classDef.interfaces:
                for func in interface.functions:
                    func_blocks[-1] += f"{self.function_signature(func)};\n"
            classes += "};\n"
        func_blocks.append(
            "".join(
                f"{self.function_signature(f)};\n"
                for f in expr.module.funcs
                if f.is_semantic
            )
        )

        func_blocks.extend(
            "".join(
                f"{self.function_signature(f)};\n" for f in i.functions if f.is_semantic
            )
            for i in expr.module.interfaces
        )

        funcs = "\n".join(f for f in func_blocks if f)

        decls = [
            Declare(v, external=True, module_variable=True)
            for v in expr.module.variables
            if not v.is_private
        ]
        global_variables = "".join(self._print(d) for d in decls)

        # Print imports last to be sure that all additional_imports have been collected
        imports = [
            i
            for i in chain(expr.module.imports, self._additional_imports.values())
            if not i.ignore
        ]
        imports = self.sort_imports(imports)
        imports = "".join(self._print(i) for i in imports)

        self._in_header = False
        self.exit_scope()
        body = "\n".join(
            info_block
            for info_block in (imports, global_variables, classes, funcs)
            if info_block
        )
        return f"#ifndef {name.upper()}_H\n \
                #define {name.upper()}_H\n\n \
                {body}\n \
                #endif // {name}_H\n"

    def _print_Module(self, expr):
        self.set_scope(expr.scope)
        body = "\n".join(self._print(i) for i in expr.body)

        global_variables = "".join([self._print(d) for d in expr.declarations])

        # Print imports last to be sure that all additional_imports have been collected
        imports = Import(
            self.scope.get_python_name(expr.name), Module(expr.name, (), ())
        )
        imports = self._print(imports)

        code = "\n".join((imports, global_variables, body))

        self.exit_scope()
        return code

    def _print_Break(self, expr):
        return "break;\n"

    def _print_Continue(self, expr):
        return "continue;\n"

    def _print_While(self, expr):
        self.set_scope(expr.scope)
        body = self._print(expr.body)
        self.exit_scope()
        cond = self._print(expr.test)
        return "while({condi})\n{{\n{body}}}\n".format(condi=cond, body=body)

    def _print_If(self, expr):
        lines = []
        condition_setup = []
        for i, (c, b) in enumerate(expr.blocks):
            body = self._print(b)
            if i == len(expr.blocks) - 1 and isinstance(c, LiteralTrue):
                if i == 0:
                    lines.append(body)
                    break
                lines.append("else\n")
            else:
                # Print condition
                condition = self._print(c)
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

    def _print_IfTernaryOperator(self, expr):
        cond = self._print(expr.cond)
        value_true = self._print(expr.value_true)
        value_false = self._print(expr.value_false)
        return f"({cond} ? {value_true} : {value_false})"

    def _print_LiteralTrue(self, expr):
        return "1"

    def _print_LiteralFalse(self, expr):
        return "0"

    def _print_And(self, expr):
        args = [
            (
                f"({self._print(a)})"
                if isinstance(a, Operator)
                and not isinstance(a, AssociativeParenthesis)
                else self._print(a)
            )
            for a in expr.args
        ]
        return " && ".join(args)

    def _print_Or(self, expr):
        args = [
            (
                f"({self._print(a)})"
                if isinstance(a, Operator)
                and not isinstance(a, AssociativeParenthesis)
                else self._print(a)
            )
            for a in expr.args
        ]
        return " || ".join(args)

    def _print_Eq(self, expr):
        lhs, rhs = expr.args
        if isinstance(lhs.class_type, StringType) and isinstance(
            rhs.class_type, StringType
        ):
            lhs_code = self._print(CStrStr(lhs))
            rhs_code = self._print(CStrStr(rhs))
            return f"!strcmp({lhs_code}, {rhs_code})"
        elif isinstance(lhs.class_type, FixedSizeNumericType):
            lhs_code = self._print(lhs)
            rhs_code = self._print(rhs)
            return f"{lhs_code} == {rhs_code}"
        else:
            raise
            errors.report(X2PY_RESTRICTION_TODO, symbol=expr, severity="error")
            return ""

    def _print_Ne(self, expr):
        lhs, rhs = expr.args
        if isinstance(lhs.class_type, StringType) and isinstance(
            rhs.class_type, StringType
        ):
            lhs_code = self._print(CStrStr(lhs))
            rhs_code = self._print(CStrStr(rhs))
            return f"strcmp({lhs_code}, {rhs_code})"
        elif isinstance(lhs.class_type, FixedSizeNumericType):
            lhs_code = self._print(lhs)
            rhs_code = self._print(rhs)
            return f"{lhs_code} != {rhs_code}"
        else:
            raise
            errors.report(X2PY_RESTRICTION_TODO, symbol=expr, severity="error")
            return ""

    def _print_Lt(self, expr):
        lhs = self._print(expr.args[0])
        rhs = self._print(expr.args[1])
        return "{0} < {1}".format(lhs, rhs)

    def _print_Le(self, expr):
        lhs = self._print(expr.args[0])
        rhs = self._print(expr.args[1])
        return "{0} <= {1}".format(lhs, rhs)

    def _print_Gt(self, expr):
        lhs = self._print(expr.args[0])
        rhs = self._print(expr.args[1])
        return "{0} > {1}".format(lhs, rhs)

    def _print_Ge(self, expr):
        lhs = self._print(expr.args[0])
        rhs = self._print(expr.args[1])
        return "{0} >= {1}".format(lhs, rhs)

    def _print_Not(self, expr):
        arg = expr.args[0]
        a = self._print(arg)
        if isinstance(arg, Operator) and not isinstance(
            arg, AssociativeParenthesis
        ):
            a = f"({a})"
        return f"!{a}"


    def _print_Mod(self, expr):
        self.add_import(c_imports["math"])
        self.add_import(c_imports["pyc_math_c"])

        first = self._print(expr.args[0])
        second = self._print(expr.args[1])

        if expr.dtype.primitive_type is PrimitiveIntegerType():
            return "pyc_modulo({n}, {base})".format(n=first, base=second)

        if expr.args[0].dtype.primitive_type is PrimitiveIntegerType():
            first = self._print(NumpyFloat(expr.args[0]))
        if expr.args[1].dtype.primitive_type is PrimitiveIntegerType():
            second = self._print(NumpyFloat(expr.args[1]))
        return "pyc_fmodulo({n}, {base})".format(n=first, base=second)

    def _print_Pow(self, expr):
        b = expr.args[0]
        e = expr.args[1]

        if expr.dtype.primitive_type is PrimitiveComplexType():
            b = self._print(
                b
                if b.dtype.primitive_type is PrimitiveComplexType()
                else PythonComplex(b)
            )
            e = self._print(
                e
                if e.dtype.primitive_type is PrimitiveComplexType()
                else PythonComplex(e)
            )
            self.add_import(c_imports["complex"])
            return "cpow({}, {})".format(b, e)

        self.add_import(c_imports["math"])
        b = self._print(
            b
            if b.dtype.primitive_type is PrimitiveFloatingPointType()
            else NumpyFloat(b)
        )
        e = self._print(
            e
            if e.dtype.primitive_type is PrimitiveFloatingPointType()
            else NumpyFloat(e)
        )
        code = "pow({}, {})".format(b, e)
        return self._cast_to(expr, expr.dtype).format(code)

    def _print_Import(self, expr):
        if expr.ignore:
            return ""
        if isinstance(expr.source, AsName):
            source = expr.source.name
        else:
            source = expr.source

        source = self._print(source)

        # Get with a default value is not used here as it is
        # slower and on most occasions the import will not be in the
        # dictionary
        if source in import_dict:  # pylint: disable=consider-using-get
            source = import_dict[source]

        if source is None:
            return ""
        if expr.source in c_library_headers:
            return "#include <{0}.h>\n".format(source)
        else:
            return '#include "{0}.h"\n'.format(source)

    def _print_LiteralString(self, expr):
        format_str = format(expr.python_value)
        format_str = (
            format_str.replace("\\", "\\\\")
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
        return f'cstr_lit("{format_str}")'

    def get_print_format_and_arg(self, var):
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
                _, real_part = self.get_print_format_and_arg(NumpyReal(var))
                float_format, imag_part = self.get_print_format_and_arg(NumpyImag(var))
                return (
                    f"({float_format} + {float_format}j)",
                    f"{real_part}, {imag_part}",
                )
            elif isinstance(primitive_type, PrimitiveBooleanType):
                return self.get_print_format_and_arg(
                    IfTernaryOperator(
                        var,
                        CStrStr(LiteralString("True")),
                        CStrStr(LiteralString("False")),
                    )
                )
            else:
                try:
                    arg_format = self.type_to_format[
                        (primitive_type, var.dtype.precision)
                    ]
                except KeyError:
                    raise
                    errors.report(
                        f"Printing {var.dtype} type is not supported currently",
                        severity="fatal",
                    )
                arg = self._print(var)
        elif isinstance(var.dtype, StringType):
            arg = self._print(CStrStr(var))
            arg_format = "%s"
        elif isinstance(var.dtype, CharType):
            arg = self._print(var)
            arg_format = "%s"
        else:
            try:
                arg_format = self.type_to_format[var.dtype]
            except KeyError:
                raise
                errors.report(
                    f"Printing {var.dtype} type is not supported currently",
                    severity="fatal",
                )

            arg = self._print(var)

        return arg_format, arg

    def _print_CStringExpression(self, expr):
        return "".join(self._print(CStrStr(e)) for e in expr.get_flat_expression_list())

    def _print_CMacro(self, expr):
        return str(expr.macro)

    def get_c_type(self, dtype):
        """
        Find the corresponding C type of the Type.

        For scalar types, this function searches for the corresponding C data type
        in the `dtype_registry`.  If the provided type is a container (like
        `HomogeneousSetType` or `HomogeneousListType`),  it recursively identifies
        the type of an element of the container and uses it to calculate the
        appropriate type for the `STC` container.
        A `X2PY_RESTRICTION_TODO` error is raised if the dtype is not found in the registry.

        Parameters
        ----------
        dtype : Type
            The data type of the expression. This can be a fixed-size numeric type,
            a primitive type, or a container type.

        Returns
        -------
        str
            The code which declares the data type in C or the corresponding `STC` container
            type.

        Raises
        ------
        X2pyCodegenError
            If the dtype is not found in the dtype_registry.
        """
        if isinstance(dtype, FixedSizeNumericType):
            primitive_type = dtype.primitive_type
            if isinstance(primitive_type, PrimitiveComplexType):
                self.add_import(c_imports["complex"])
                return f"{self.get_c_type(dtype.element_type)} complex"
            elif isinstance(primitive_type, PrimitiveIntegerType):
                self.add_import(c_imports["stdint"])
            elif isinstance(dtype, PythonNativeBool):
                self.add_import(c_imports["stdbool"])
                return "bool"

            key = (primitive_type, dtype.precision)

        elif isinstance(dtype, StringType):
            self.add_import(c_imports["stc/cstr"])
            return "cstr"

        elif isinstance(dtype, CustomDataType):
            return self._print(dtype)

        else:
            key = dtype

        try:
            return self.dtype_registry[key]
        except KeyError:
            raise
            raise errors.report(
                X2PY_RESTRICTION_TODO,  # pylint: disable=raise-missing-from
                symbol=dtype,
                severity="fatal",
            )

    def get_declare_type(self, expr):
        """
        Get the string which describes the type in a declaration.

        This function returns the code which describes the type
        of the `expr` object such that the declaration can be written as:
        `f"{self.get_declare_type(expr)} {expr.name}"`
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
        >>> v = Variable(PythonNativeInt(), 'x')
        >>> self.get_declare_type(v)
        'int64_t'

        For an object accessed via a pointer:
        >>> v = Variable(NumpyNDArrayType.get_new(PythonNativeInt(), 1, None), 'x', is_optional=True)
        >>> self.get_declare_type(v)
        'array_int64_1d*'
        """
        class_type = expr.class_type

        if isinstance(class_type, CStackArray):
            dtype = self.get_c_type(class_type.element_type)
        elif isinstance(class_type, (HomogeneousContainerType)):
            dtype = self.get_c_type(class_type)
        else:
            dtype = self.get_c_type(expr.class_type)

        if self.is_c_pointer(expr) and not isinstance(class_type, CStackArray):
            return f"{dtype}*"
        else:
            return dtype

    def _print_Declare(self, expr):
        var = expr.variable
        declaration_type = self.get_declare_type(var)

        init = f" = {self._print(expr.value)}" if expr.value is not None else ""

        if isinstance(var.class_type, CStackArray):
            assert init == ""
            preface = ""
            if isinstance(var.alloc_shape[0], (int, LiteralInteger)):
                init = f"[{var.alloc_shape[0]}]"
            else:
                declaration_type += "*"
                init = ""
        elif var.is_stack_array:
            preface, init = self._init_stack_array(var)
        else:
            preface = ""
            if (
                isinstance(var.class_type, (HomogeneousContainerType))
                and not expr.external
                and not var.is_alias
            ):
                init = " = {0}"

        external = "extern " if expr.external else ""
        static = "static " if expr.static else ""
        const = (
            "const "
            if isinstance(var.class_type, FinalType) and self.is_c_pointer(var)
            else ""
        )

        return (
            f"{preface}{static}{external}{const}{declaration_type} {var.name}{init};\n"
        )

    def function_signature(self, expr, print_arg_names=True):
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
        result_vars = [
            v
            for v in expr.scope.collect_all_tuple_elements(expr.results.var)
            if v and not v.is_argument
        ]

        n_results = len(result_vars)

        if n_results > 1:
            ret_type = self.get_c_type(PythonNativeInt())
            if expr.arguments and expr.arguments[0].bound_argument:
                # Place the first arg_var (the bound class object) first
                arg_vars = arg_vars[:1] + result_vars + arg_vars[1:]
            else:
                arg_vars = result_vars + arg_vars
            self._additional_args.append(
                result_vars
            )  # Ensure correct result for is_c_pointer
        elif n_results == 1:
            ret_type = self.get_declare_type(result_vars[0])
            self._additional_args.append([])
        else:
            ret_type = self.get_c_type(VoidType())
            self._additional_args.append([])

        for v in expr.global_vars:
            if get_direct_module(v) is None:
                self._additional_args[-1].append(v)
                arg_vars.append(v)
        arg_vars = [
            ai for a in arg_vars for ai in expr.scope.collect_all_tuple_elements(a)
        ]

        name = expr.name
        if not arg_vars:
            arg_code = "void"
        else:

            def get_arg_declaration(var):
                """Get the code which declares the argument variable."""
                const = "const " if isinstance(var.class_type, FinalType) else ""
                code = const + self.get_declare_type(var)
                if print_arg_names:
                    code += " " + var.name
                return code

            arg_code_list = [
                (
                    self.function_signature(var, False)
                    if isinstance(var, FunctionAddress)
                    else get_arg_declaration(var)
                )
                for var in arg_vars
            ]
            arg_code = ", ".join(arg_code_list)

        self._additional_args.pop()

        static = "static " if expr.is_static else ""

        if isinstance(expr, FunctionAddress):
            return f"{static}{ret_type} (*{name})({arg_code})"
        else:
            return f"{static}{ret_type} {name}({arg_code})"

    def _print_IndexedElement(self, expr):
        base = expr.base

        inds = list(expr.indices)
        raise NotImplementedError(f"Indexing not implemented for {base}")

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
            cast = self.get_c_type(dtype)
            return "({}){{}}".format(cast)
        return "{}"

    def _print_DottedVariable(self, expr):
        """convert dotted Variable to their C equivalent"""

        name_code = self._print(expr.name)
        if self.is_c_pointer(expr.lhs):
            code = f"{self._print(ObjectAddress(expr.lhs))}->{name_code}"
        else:
            lhs_code = self._print(expr.lhs)
            code = f"{lhs_code}.{name_code}"
        if self.is_c_pointer(expr):
            return f"(*{code})"
        else:
            return code

    def _print_ArraySize(self, expr):
        arg = self._print(ObjectAddress(expr.arg))
        return f"cspan_size({arg})"

    def _print_ArrayShapeElement(self, expr):
        arg = expr.arg
        if isinstance(arg.class_type, NumpyNDArrayType):
            idx = self._print(expr.index)
            cast_code = f"({self.get_c_type(PythonNativeInt())})"
            if self.is_c_pointer(arg):
                arg_code = self._print(ObjectAddress(arg))
                return f"{cast_code}{arg_code}->shape[{idx}]"
            arg_code = self._print(arg)
            return f"{cast_code}{arg_code}.shape[{idx}]"
        elif isinstance(arg.class_type, StringType):
            arg_code = self._print(ObjectAddress(arg))
            return f"cstr_size({arg_code})"
        else:
            raise NotImplementedError(
                f"Don't know how to represent shape of object of type {arg.class_type}"
            )

    def _print_Allocate(self, expr):
        free_code = ""
        variable = expr.variable
        if isinstance(variable.class_type, StringType):
            if expr.status in ("allocated", "unknown"):
                free_code = f"{self._print(Deallocate(variable))}"
            if expr.shape[0] is None:
                return free_code
            if expr.alloc_type == "function":
                return free_code
            size = self._print(expr.shape[0])
            variable_address = self._print(ObjectAddress(expr.variable))
            container_type = self.get_c_type(expr.variable.class_type)
            if expr.alloc_type == "reserve":
                if expr.status != "unallocated":
                    return (
                        f"{container_type}_clear({variable_address});\n"
                        f"{container_type}_reserve({variable_address}, {size});\n"
                    )
                return f"{container_type}_reserve({variable_address}, {size});\n"
            elif expr.alloc_type == "resize":
                return f"{container_type}_resize({variable_address}, {size}, {0});\n"
            return free_code
        elif isinstance(variable.class_type, (NumpyNDArrayType)):
            # free the array if its already allocated and checking if its not null if the status is unknown
            if expr.status == "unknown":
                data_ptr = ObjectAddress(
                    DottedVariable(
                        VoidType(), "data", lhs=variable, memory_handling="alias"
                    )
                )
                free_code = f"if ({self._print(data_ptr)} != NULL)\n"
                free_code += "".join(("{\n", self._print(Deallocate(variable)), "}\n"))
            elif expr.status == "allocated":
                free_code += self._print(Deallocate(variable))
            if expr.alloc_type == "function":
                return free_code

            tot_shape = self._print(
                functools.reduce(Mul.make_simplified, expr.shape)
            )
            c_type = self.get_c_type(variable.class_type)
            element_type = self.get_c_type(variable.class_type.element_type)

            if expr.like:
                buffer_array = ""
                if isinstance(expr.like.class_type, VoidType):
                    dummy_array_name = self._print(ObjectAddress(expr.like))
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
            shape = ", ".join(self._print(i) for i in expr.shape)

            return (
                free_code
                + buffer_array
                + f"{self._print(variable)} = ({c_type})cspan_md_layout({order}, {dummy_array_name}, {shape});\n"
            )
        elif variable.is_alias:
            var_code = self._print(ObjectAddress(variable))
            if expr.like:
                declaration_type = self.get_declare_type(expr.like)
                malloc_size = f"sizeof({declaration_type})"
                if variable.rank:
                    tot_shape = self._print(
                        functools.reduce(Mul.make_simplified, expr.shape)
                    )
                    malloc_size = f"{malloc_size} * ({tot_shape})"
                return f"{var_code} = malloc({malloc_size});\n"
            else:
                raise NotImplementedError(
                    f"Allocate not implemented for {variable.class_type}"
                )
        else:
            raise NotImplementedError(
                f"Allocate not implemented for {variable.class_type}"
            )

    def _print_Deallocate(self, expr):
        var = expr.variable
        if isinstance(var.class_type, StringType):
            if var.is_alias:
                return ""

            variable_address = self._print(ObjectAddress(var))
            container_type = self.get_c_type(var.class_type)
            return f"{container_type}_drop({variable_address});\n"
        if isinstance(var.dtype, CustomDataType):
            variable_address = self._print(ObjectAddress(var))
            x2py__del = var.cls_base.scope.find("__del__")
            if x2py__del:
                return f"{x2py__del.name}({variable_address});\n"
            else:
                return ""
        elif isinstance(var.class_type, NumpyNDArrayType):
            if var.is_alias:
                return ""
            else:
                data_ptr = DottedVariable(
                    VoidType(), "data", lhs=var, memory_handling="alias"
                )
                data_ptr_code = self._print(ObjectAddress(data_ptr))
                return f"free({data_ptr_code});\n{data_ptr_code} = NULL;\n"
        else:
            variable_address = self._print(ObjectAddress(var))
            return f"free({variable_address});\n"

    def _print_FunctionAddress(self, expr):
        return expr.name

    def _print_Interface(self, expr):
        return "".join(self._print(f) for f in expr.functions)

    def _print_FunctionDef(self, expr):
        if not expr.is_semantic:
            return ""

        for r in expr.scope.collect_all_tuple_elements(expr.results.var):
            if r.rank and r.memory_handling == "stack":
                raise
                errors.report(
                    "Can't return a stack array from C code", symbol=r, severity="error"
                )

        sep = self._print(SeparatorComment(40))

        inner_funcs = "".join(
            self._print(f).removeprefix(sep).removesuffix(sep) + "\n"
            for f in expr.functions
        )

        self.set_scope(expr.scope)

        # Collect results filtering out Nil()
        results = [
            r
            for r in self.scope.collect_all_tuple_elements(expr.results.var)
            if isinstance(r, Variable)
        ]
        returning_tuple = False
        if len(results) > 1 or returning_tuple:
            self._additional_args.append(results)
        else:
            self._additional_args.append([])
        for v in expr.global_vars:
            if get_direct_module(v) is None:
                self._additional_args[-1].append(v)

        body = self._print(expr.body)
        decs = [
            Declare(
                i,
                value=(
                    Nil()
                    if i.is_alias and isinstance(i.class_type, (VoidType, BindCPointer))
                    else None
                ),
            )
            for i in expr.local_vars
        ]

        if len(results) == 1 and not returning_tuple:
            res = results[0]
            if isinstance(res, Variable) and (not res.is_temp or res.rank):
                decs += [Declare(res)]
            elif not isinstance(res, Variable):
                raise NotImplementedError(f"Can't return {type(res)} from a function")
        decs = "".join(self._print(i) for i in decs)

        self._additional_args.pop()
        for i in expr.imports:
            self.add_import(i)
        docstring = self._print(expr.docstring) if expr.docstring else ""

        parts = [
            sep,
            inner_funcs,
            docstring,
            "{signature}\n{{\n".format(signature=self.function_signature(expr)),
            decs,
            body,
            "}\n",
            sep,
        ]

        self.exit_scope()

        return "".join(p for p in parts if p)

    def _print_FunctionCall(self, expr):
        func = expr.funcdef
        # Ensure the correct syntax is used for pointers
        args = []
        for a, f in zip(expr.args, func.arguments):
            arg_val = a.value
            f = f.var
            if self.is_c_pointer(f):
                if isinstance(arg_val, Variable):
                    args.append(ObjectAddress(arg_val))
                elif not self.is_c_pointer(arg_val):
                    tmp_var = self.scope.get_temporary_variable(f.dtype)
                    assign = Assign(tmp_var, arg_val)
                    code = self._print(assign)
                    self._additional_code += code
                    args.append(ObjectAddress(tmp_var))
                else:
                    args.append(arg_val)
            else:
                args.append(arg_val)

        if func.arguments and func.arguments[0].bound_argument:
            # Place the first arg_var (the bound class object) first
            args = args[:1] + self._temporary_args + args[1:]
        else:
            args = self._temporary_args + args

        for v in func.global_vars:
            if get_direct_module(v) is None:
                args.append(ObjectAddress(v))

        self._temporary_args = []
        args = ", ".join(
            self._print(ai)
            for a in args
            for ai in self.scope.collect_all_tuple_elements(a)
        )

        call_code = f"{func.name}({args})"
        if func.results.var is not Nil():
            return call_code
        else:
            return f"{call_code};\n"

    def _print_Return(self, expr):
        func = get_enclosing_function(expr)
        assert func is not None
        code = ""

        return_obj = expr.expr
        if return_obj is None:
            args = []
        else:
            args = [
                (
                    ObjectAddress(return_obj)
                    if self.is_c_pointer(return_obj)
                    else return_obj
                )
            ]

        if len(args) == 0:
            return code + "return;\n"

        returned_value = self.scope.collect_tuple_element(args[0])

        return code + f"return {self._print(returned_value)};\n"

    def _print_Pass(self, expr):
        return "// pass\n"

    def _print_Nil(self, expr):
        return "NULL"

    def _print_NilArgument(self, expr):
        raise
        raise errors.report(
            "Trying to use optional argument in inline function without providing a variable",
            symbol=expr,
            severity="fatal",
        )

    def _print_Add(self, expr):
        return " + ".join(self._print(a) for a in expr.args)

    def _print_Minus(self, expr):
        args = [self._print(a) for a in expr.args]
        if len(args) == 1:
            return "-{}".format(args[0])
        return " - ".join(args)

    def _print_Mul(self, expr):
        return " * ".join(self._print(a) for a in expr.args)

    def _print_Div(self, expr):
        if all(a.dtype.primitive_type is PrimitiveIntegerType() for a in expr.args):
            args = [NumpyFloat(a) for a in expr.args]
        else:
            args = expr.args
        return " / ".join(self._print(a) for a in args)

    def _print_FloorDiv(self, expr):
        # the result type of the floor division is dependent on the arguments
        # type, if all arguments are integers or booleans the result is integer
        # otherwise the result type is float
        need_to_cast = all(
            a.dtype.primitive_type in (PrimitiveIntegerType(), PrimitiveBooleanType())
            for a in expr.args
        )
        if need_to_cast:
            self.add_import(c_imports["pyc_math_c"])
            cast_type = self.get_c_type(expr.dtype)
            return f"py_floor_div_{cast_type}({self._print(expr.args[0])}, {self._print(expr.args[1])})"

        self.add_import(c_imports["math"])
        code = " / ".join(
            self._print(
                a
                if a.dtype.primitive_type is PrimitiveFloatingPointType()
                else NumpyFloat(a)
            )
            for a in expr.args
        )
        return f"floor({code})"

    def _print_RShift(self, expr):
        return " >> ".join(self._print(a) for a in expr.args)

    def _print_LShift(self, expr):
        return " << ".join(self._print(a) for a in expr.args)

    def _print_BitXor(self, expr):
        if expr.dtype is PythonNativeBool():
            return "{0} != {1}".format(
                self._print(expr.args[0]), self._print(expr.args[1])
            )
        return " ^ ".join(self._print(a) for a in expr.args)

    def _print_BitOr(self, expr):
        args = [
            (
                f"({self._print(a)})"
                if isinstance(a, Operator)
                and not isinstance(a, AssociativeParenthesis)
                else self._print(a)
            )
            for a in expr.args
        ]
        if expr.dtype is PythonNativeBool():
            return " || ".join(args)
        return " | ".join(args)

    def _print_BitAnd(self, expr):
        args = [
            (
                f"({self._print(a)})"
                if isinstance(a, Operator)
                and not isinstance(a, AssociativeParenthesis)
                else self._print(a)
            )
            for a in expr.args
        ]
        if expr.dtype is PythonNativeBool():
            return " && ".join(args)
        return " & ".join(args)

    def _print_Invert(self, expr):
        arg = self._print(expr.args[0])
        if expr.dtype is PythonNativeBool():
            return f"!{arg}"
        else:
            return f"~{arg}"

    def _print_AssociativeParenthesis(self, expr):
        return "({})".format(self._print(expr.args[0]))

    def _print_UnaryPlus(self, expr):
        return "+{}".format(self._print(expr.args[0]))

    def _print_UnarySub(self, expr):
        return "-{}".format(self._print(expr.args[0]))

    def _print_AugAssign(self, expr):
        op = expr.op
        lhs = expr.lhs
        rhs = expr.rhs

        if op == "//" or (
            op == "%"
            and isinstance(lhs.dtype.primitive_type, PrimitiveFloatingPointType)
        ):
            _expr = expr.to_basic_assign()
            return self._print(_expr)

        lhs_code = self._print(lhs)
        rhs_code = self._print(rhs)
        return f"{lhs_code} {op}= {rhs_code};\n"

    def _print_Assign(self, expr):
        lhs = expr.lhs
        rhs = expr.rhs

        lhs_code = self._print(lhs)
        rhs_code = self._print(rhs)
        return f"{lhs_code} = {rhs_code};\n"

    def _print_AliasAssign(self, expr):
        lhs_var = expr.lhs
        rhs_var = expr.rhs

        lhs_address = ObjectAddress(lhs_var)
        rhs_address = ObjectAddress(rhs_var)

        # The condition below handles the case of reassigning a pointer to an array view.
        if (
            isinstance(lhs_var, Variable)
            and lhs_var.is_ndarray
            and not lhs_var.is_optional
        ):
            lhs = self._print(lhs_var)

            if isinstance(rhs_var, Variable) and rhs_var.is_ndarray:
                lhs_ptr = self._print(lhs_address)
                rhs = self._print(rhs_address)
                rhs_type = self.get_c_type(rhs_var.class_type)
                slicing = ", ".join(["{c_ALL}"] * lhs_var.rank)
                code = f"{lhs} = cspan_slice({rhs}, {rhs_type}, {slicing});\n"
                if lhs_var.order != rhs_var.order:
                    code += f"cspan_transpose({lhs_ptr});\n"
                return code
            else:
                rhs = self._print(rhs_var)
                return f"{lhs} = {rhs};\n"
        else:
            lhs = self._print(lhs_address)
            rhs = self._print(rhs_address)

            return f"{lhs} = {rhs};\n"

    def _print_For(self, expr):
        self.set_scope(expr.scope)

        iterable = expr.iterable
        indices = iterable.loop_counters

        range_iterable = iterable.get_range()
        if indices:
            index = indices[0]
            if iterable.num_loop_counters_required and index.is_temp:
                self.scope.insert_variable(index)
        else:
            index = expr.target[0]

        targets = iterable.get_assign_targets()
        additional_assign = CodeBlock(
            [
                AliasAssign(i, t) if i.is_alias else Assign(i, t)
                for i, t in zip(expr.target[-len(targets) :], targets)
            ]
        )

        index_code = self._print(index)
        step = range_iterable.step
        start_code = self._print(range_iterable.start)
        stop_code = self._print(range_iterable.stop)
        step_code = self._print(range_iterable.step)

        # testing if the step is a value or an expression
        stop_condition = f"({step_code} > 0) ? ({index_code} < {stop_code}) : ({index_code} > {stop_code})"
        for_code = f"for ({index_code} = {start_code}; {stop_condition}; {index_code} += {step_code})\n"

        if self._additional_code:
            for_code = self._additional_code + for_code
            self._additional_code = ""

        body = self._print(additional_assign) + self._print(expr.body)

        self.exit_scope()
        return for_code + "{\n" + body + "}\n"

    def _print_CodeBlock(self, expr):
        body_exprs = expr.body
        body_stmts = []
        for b in body_exprs:
            code = self._print(b)
            code = self._additional_code + code
            self._additional_code = ""
            body_stmts.append(code)
        return "".join(self._print(b) for b in body_stmts)

    def _print_Idx(self, expr):
        return self._print(expr.label)

    def _print_PythonReal(self, expr):
        return "creal({})".format(self._print(expr.internal_var))

    def _print_PythonImag(self, expr):
        return "cimag({})".format(self._print(expr.internal_var))

    def _print_PythonConjugate(self, expr):
        return "conj({})".format(self._print(expr.internal_var))

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

        lhs = self._print(expr.args[0])
        rhs = self._print(expr.args[1])
        a = expr.args[0]
        b = expr.args[1]

        if Nil() in expr.args:
            lhs = (
                ObjectAddress(expr.args[0]) if isinstance(expr.args[0], Variable) else expr.args[0]
            )
            rhs = (
                ObjectAddress(expr.args[1]) if isinstance(expr.args[1], Variable) else expr.args[1]
            )

            lhs = self._print(lhs)
            rhs = self._print(rhs)
            return "{} {} {}".format(lhs, Op, rhs)

        if a.dtype is PythonNativeBool() and b.dtype is PythonNativeBool():
            return "{} {} {}".format(lhs, Op, rhs)
        else:
            raise
            errors.report(X2PY_RESTRICTION_IS_ISNOT, symbol=expr, severity="fatal")

    def _print_IsNot(self, expr):
        return self._handle_is_operator("!=", expr)

    def _print_Is(self, expr):
        return self._handle_is_operator("==", expr)

    def _print_Piecewise(self, expr):
        if expr.args[-1].cond is not True:
            # We need the last conditional to be a True, otherwise the resulting
            # function may not return a result.
            raise ValueError(
                "All Piecewise expressions must contain an "
                "(expr, True) statement to be used as a default "
                "condition. Without one, the generated "
                "expression may not evaluate to anything under "
                "some condition."
            )
        lines = []
        if expr.has(Assign):
            for i, (e, c) in enumerate(expr.args):
                if i == 0:
                    lines.append("if (%s) {\n" % self._print(c))
                elif i == len(expr.args) - 1 and c is True:
                    lines.append("else {\n")
                else:
                    lines.append("else if (%s) {\n" % self._print(c))
                code0 = self._print(e)
                lines.append(code0)
                lines.append("}\n")
            return "".join(lines)
        else:
            # The piecewise was used in an expression, need to do inline
            # operators. This has the downside that inline operators will
            # not work for statements that span multiple lines (Matrix or
            # Indexed expressions).
            ecpairs = [
                "((%s) ? (\n%s\n)\n" % (self._print(c), self._print(e))
                for e, c in expr.args[:-1]
            ]
            last_line = ": (\n%s\n)" % self._print(expr.args[-1].expr)
            return ": ".join(ecpairs) + last_line + " ".join([")" * len(ecpairs)])

    def _print_Variable(self, expr):
        if self.is_c_pointer(expr):
            return "(*{0})".format(expr.name)
        else:
            return expr.name

    def _print_FunctionDefArgument(self, expr):
        return self._print(expr.name)

    def _print_FunctionCallArgument(self, expr):
        return self._print(expr.value)

    def _print_ObjectAddress(self, expr):
        obj_code = self._print(expr.obj)
        if isinstance(expr.obj, ObjectAddress):
            return f"&{obj_code}"
        elif obj_code.startswith("(*") and obj_code.endswith(")"):
            return f"{obj_code[2:-1]}"
        elif not self.is_c_pointer(expr.obj):
            return f"&{obj_code}"
        else:
            return obj_code

    def _print_PointerCast(self, expr):
        declare_type = self.get_declare_type(expr.cast_type)
        if not self.is_c_pointer(expr.cast_type):
            declare_type += "*"
        obj = expr.obj
        if not isinstance(obj, ObjectAddress):
            obj = ObjectAddress(expr.obj)
        var_code = self._print(obj)
        return f"(*({declare_type})({var_code}))"

    def _print_Comment(self, expr):
        comments = self._print(expr.text)

        return "/*" + comments + "*/\n"

    def _print_Assert(self, expr):
        if isinstance(expr.test, LiteralTrue):
            return ""
        condition = self._print(expr.test)
        self.add_import(c_imports["assert"])
        return f"assert({condition});\n"

    def _print_Symbol(self, expr):
        return expr

    def _print_CommentBlock(self, expr):
        txts = expr.comments
        header = expr.header
        header_size = len(expr.header)

        ln = max(len(i) for i in txts)
        if ln < max(20, header_size + 4):
            ln = 20
        top = (
            "/*"
            + "_" * int((ln - header_size) / 2)
            + header
            + "_" * int((ln - header_size) / 2)
            + "*/\n"
        )
        ln = len(top) - 4
        bottom = "/*" + "_" * ln + "*/\n"

        txts = ["/*" + t + " " * (ln - len(t)) + "*/\n" for t in txts]

        body = "".join(i for i in txts)

        return "".join([top, body, bottom])

    def _print_EmptyNode(self, expr):
        return ""

    # =================== OMP ==================

    def _print_OmpAnnotatedComment(self, expr):
        clauses = ""
        if expr.combined:
            clauses = " " + expr.combined
        clauses += str(expr.txt)
        if expr.has_nowait:
            clauses = clauses + " nowait"
        omp_expr = "#pragma omp {}{}\n".format(expr.name, clauses)

        if expr.is_multiline:
            if expr.combined is None:
                omp_expr += "{\n"
            elif expr.combined and "for" not in expr.combined:
                if ("masked taskloop" not in expr.combined) and (
                    "distribute" not in expr.combined
                ):
                    omp_expr += "{\n"

        return omp_expr

    def _print_Omp_End_Clause(self, expr):
        return "}\n"

    # =====================================

    def _print_Program(self, expr):
        self.set_scope(expr.scope)
        body = self._print(expr.body)
        variables = self.scope.variables.values()
        decs = "".join(self._print(Declare(v)) for v in variables)

        imports = [
            i
            for i in chain(expr.imports, self._additional_imports.values())
            if not i.ignore
        ]
        imports = self.sort_imports(imports)
        imports = "".join(self._print(i) for i in imports)

        self.exit_scope()
        return f"{imports}int main()\n{{\n{decs}{body}return 0;\n}}"

    # ================== CLASSES ==================

    def _print_CustomDataType(self, expr):
        return "struct " + expr.low_level_name

    def _print_Del(self, expr):
        return "".join(self._print(var) for var in expr.variables)

    def _print_ClassDef(self, expr):
        methods = "".join(self._print(method) for method in expr.methods)
        interfaces = "".join(
            self._print(function)
            for interface in expr.interfaces
            for function in interface.functions
        )

        return methods + interfaces

    # ================== String methods ==================

    def _print_CStrStr(self, expr):
        arg = expr.args[0]
        code = self._print(ObjectAddress(arg))
        if code.startswith("&cstr_lit("):
            return code[10:-1]
        else:
            return f"cstr_str({code})"

    def _print_PythonStr(self, expr):
        arg = expr.args[0]
        arg_code = self._print(arg)
        if isinstance(arg.class_type, StringType):
            return f"cstr_clone({arg_code})"
        else:
            assert isinstance(arg.class_type, CharType) and getattr(
                arg, "is_alias", True
            )
            return f"cstr_from({arg_code})"

    def _print_AllDeclaration(self, expr):
        return ""

    def indent_code(self, code):
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
            code_lines = self.indent_code(code.splitlines(True))
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
