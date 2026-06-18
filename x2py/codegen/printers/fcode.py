"""Print to F90 standard. Trying to follow the information provided at
www.fortran90.org as much as possible."""

import re
import string
from collections import OrderedDict
from itertools import chain
from typing import ClassVar


from ..bind_c import (
    BindCClassDef,
    BindCFunctionDef,
    BindCModule,
    BindCPointer,
    BindCVariable,
    FortranTransfer,
)

from ..models.datatypes import cast_to
from ..models.core import (
    AliasAssign,
    Assign,
    Declare,
    FunctionAddress,
    FunctionCall,
    FunctionCallArgument,
    FunctionDef,
    get_direct_assignment,
    get_direct_function_argument,
    Import,
    Module,
    SeparatorComment,
    Slice,
)
from ..models.datatypes import (
    CustomDataType,
    FinalType,
    FixedSizeNumericType,
    FixedSizeType,
    PrimitiveBooleanType,
    PrimitiveCharacterType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    Type,
    NumpyBoolType,
    StringType,
    SymbolicType,
    TupleType,
)
from ..models.datatypes import (
    Literal,
    NIL,
    convert_to_literal,
)

from ..models.datatypes import (
    NumpyFloat64Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from ..models.core import (
    Add,
    Minus,
)

from ..models.core import Variable
from .codeprinter import CodePrinter

# TODO: add examples

__all__ = ["FCodePrinter"]


# ==============================================================================
iso_c_binding = {
    PrimitiveIntegerType(): {
        1: "C_INT8_T",
        2: "C_INT16_T",
        4: "C_INT32_T",
        8: "C_INT64_T",
        16: "C_INT128_T",
    },  # not supported yet
    PrimitiveFloatingPointType(): {
        4: "C_FLOAT",
        8: "C_DOUBLE",
        16: "C_LONG_DOUBLE",
    },  # not supported yet
    PrimitiveComplexType(): {
        4: "C_FLOAT_COMPLEX",
        8: "C_DOUBLE_COMPLEX",
        16: "C_LONG_DOUBLE_COMPLEX",
    },  # not supported yet
    PrimitiveBooleanType(): {-1: "C_BOOL"},
    PrimitiveCharacterType(): {-1: "C_CHAR"},
}

iso_c_binding_shortcut_mapping = {
    "C_INT8_T": "i8",
    "C_INT16_T": "i16",
    "C_INT32_T": "i32",
    "C_INT64_T": "i64",
    "C_INT128_T": "i128",
    "C_FLOAT": "f32",
    "C_DOUBLE": "f64",
    "C_LONG_DOUBLE": "f128",
    "C_FLOAT_COMPLEX": "c32",
    "C_DOUBLE_COMPLEX": "c64",
    "C_LONG_DOUBLE_COMPLEX": "c128",
    "C_BOOL": "b1",
}

inc_keyword = (
    r"do\b",
    r"if \(.*?\) then$",
    r"else\b",
    r"type\b\s*[^\(]",
    r"(elemental )?(pure )?(recursive )?((subroutine)|(function))\b",
    r"interface\b",
    r"module\b(?! *procedure)",
    r"program\b",
)
inc_regex = re.compile("|".join(f"({i})" for i in inc_keyword))

end_keyword = (
    "do",
    "if",
    "type",
    "function",
    "subroutine",
    "interface",
    "module",
    "program",
)
end_regex_str = "(end ?({}))|(else)".format("|".join(f"({k})" for k in end_keyword))
dec_regex = re.compile(end_regex_str)


class FCodePrinter(CodePrinter):
    """
    A printer for printing code in Fortran.

    A printer to convert X2py's AST to strings of Fortran code.
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

    printmethod = "_fcode"
    language = "Fortran"

    _default_settings: ClassVar = {
        "tabwidth": 2,
    }

    def __init__(self, filename, *, verbose, prefix_module=None):
        super().__init__(verbose)
        self._constantImports = []

        self._additional_code = ""

        self.prefix_module = prefix_module

    def print_constant_imports(self):
        """
        Print the import of constant intrinsics.

        Print the import of constants such as `C_INT` from an intrinsic module (i.e. a
        module provided by Fortran) such as `iso_c_binding`.

        Returns
        -------
        str
            The code describing the import of the intrinsics.
        """
        macros = []
        for name, imports in self._constantImports[-1].items():
            macro = f"use, intrinsic :: {name}, only : "
            rename = [c if isinstance(c, str) else c[0] + " => " + c[1] for c in imports]
            if len(rename) == 0:
                continue
            rename.sort()
            macro += " , ".join(rename)
            macro += "\n"
            macros.append(macro)
        return "".join(macros)

    def _bind_c_external_optional_interfaces(self, expr):
        original_module = getattr(expr, "original_module", None)
        if original_module is None:
            return ""
        interfaces = [
            self._external_optional_interface(func)
            for func in original_module.funcs
            if func.is_external and any(getattr(arg.var, "is_optional", False) for arg in func.arguments)
        ]
        return "".join(interfaces)

    def _external_optional_interface(self, func):
        args = ", ".join(self._print(arg.name) for arg in func.arguments)
        result_vars = [var for var in func.scope.collect_all_tuple_elements(func.results.var) if var]
        is_function = len(result_vars) == 1
        func_type = "function" if is_function else "subroutine"
        lines = [f"{func_type} {self._print(func.name)}({args})", "import"]
        if is_function:
            lines.append(self._print(Declare(result_vars[0])).rstrip())
        for arg in func.arguments:
            var = arg.var
            declare_intent = (
                getattr(var, "intent", None) if var.rank > 0 or isinstance(var.class_type, StringType) else None
            )
            lines.append(self._print(Declare(var, intent=declare_intent)).rstrip())
        lines.append(f"end {func_type} {self._print(func.name)}")
        return "\n".join(lines) + "\n"

    def _format_code(self, lines):
        """
        Format code in order to match readable Fortran practices.

        Format code in order to match readable Fortran practices.
        In particular this function indents the code.

        Parameters
        ----------
        lines : list[str]
            The lines of code.

        Returns
        -------
        list[str]
            The formatted lines of code.
        """
        return self._wrap_fortran(self.indent_code(lines))

    def print_kind(self, expr):
        """
        Print the kind(precision) of a literal value or its shortcut if possible.

        Print the kind(precision) of a literal value or its shortcut if possible.

        Parameters
        ----------
        expr : model object | Type
            The object whose precision should be investigated.

        Returns
        -------
        str
            The code for the kind parameter.
        """
        dtype = expr if isinstance(expr, Type) else expr.dtype

        constant_name = iso_c_binding[dtype.primitive_type][dtype.precision]

        constant_shortcut = iso_c_binding_shortcut_mapping[constant_name]
        if constant_shortcut not in self.scope.all_used_symbols and constant_name != constant_shortcut:
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add((constant_shortcut, constant_name))
            constant_name = constant_shortcut
        else:
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add(constant_name)
        return constant_name

    def _get_external_declarations(self, decs):
        """
        Find external functions and declare their result type.

        Look for any external functions in the local imports from
        the scope and use their definitions to create declarations
        from the results. These declarations are stored in the list
        passed as argument.

        Parameters
        ----------
        decs : list
            The list where the declarations necessary to use the external
            functions will be stored.
        """
        for key, f in self.scope.imports["functions"].items():
            if isinstance(f, FunctionDef) and f.is_external and f.results.var:
                v = f.results.var.clone(str(key))
                decs.append(Declare(v, external=True))

    def _calculate_class_names(self, expr):
        """
        Calculate the class names of the functions in a class.

        Calculate the names that will be referenced from the class
        for each function in a class. Also rename magic methods.

        Parameters
        ----------
        expr : ClassDef
            The class whose functions should be renamed.
        """
        scope = expr.scope
        name = expr.name.lower()
        for method in expr.methods:
            if method.is_semantic:
                method.cls_name = scope.get_new_name(f"{name}_{method.name}")
        for i in expr.overload_sets:
            for f in i.functions:
                if f.is_semantic:
                    f.cls_name = scope.get_new_name(f"{name}_{f.name}")

    def _apply_cast(self, target_type, *args):
        """
        Cast the arguments to the specified target type.

        Cast the arguments to the specified target type. For literal containers this
        function applies the cast to the elements.

        Parameters
        ----------
        target_type : Type
            The type which we should cast to.
        *args : model object
            A node that should be cast to the target type.

        Returns
        -------
        model object | iterable[model object]
            A model object for each argument. The new nodes will have the target type.
        """
        new_args = []
        for a in args:
            if target_type != a.class_type:
                a = cast_to(a, target_type)
            new_args.append(a)

        if len(args) == 1:
            return new_args[0]
        return new_args

    # ============ Elements ============ #
    def _print_Symbol(self, expr):
        return expr

    def _print_Module(self, expr):
        self.set_scope(expr.scope)
        self._constantImports.append({})
        name = self._print(expr.name)
        name = name.replace(".", "_")
        if not name.startswith("mod_") and self.prefix_module:
            name = f"{self.prefix_module}_{name}"

        imports = "".join(self._print(i) for i in expr.imports)

        # Define declarations
        decs = ""
        # ...
        for c in expr.classes:
            if not isinstance(c, BindCClassDef):
                self._calculate_class_names(c)

        class_decs_and_methods = [self._print(i) for i in expr.classes]
        decs += "\n".join(c[0] for c in class_decs_and_methods)
        # ...

        declarations = list(expr.declarations)
        # look for external functions and declare their result type
        self._get_external_declarations(declarations)
        decs += "".join(self._print(d) for d in declarations)

        funcs_to_print = list(expr.funcs) + [f for i in expr.overload_sets for f in i.functions]

        # ...
        public_decs = "".join(
            f"public :: {n}\n"
            for n in chain(
                (c.name for c in expr.classes),
                (f.name for f in funcs_to_print if not f.is_private and f.is_semantic),
                (v.name for v in expr.variables if not v.is_private),
            )
        )

        # ...
        sep = self._print(SeparatorComment(40))
        if isinstance(expr, BindCModule):
            external_optional_interfaces = self._bind_c_external_optional_interfaces(expr)
            interfaces = (
                "interface\n"
                'function c_malloc(size) bind(C,name="x2py_malloc") result(ptr)\n'
                "use iso_c_binding\n"
                "integer(c_size_t), value, intent(in) :: size\n"
                "type(c_ptr) :: ptr\n"
                "end function c_malloc\n"
                f"{external_optional_interfaces}"
                "end interface\n"
            )
        else:
            interfaces = "\n".join(self._print(i) for i in expr.overload_sets)
            public_decs += "".join(
                f"public :: {i.name}\n" for i in expr.overload_sets if i.is_semantic and not i.is_private
            )

        func_strings = []
        # Get class functions
        func_strings += [c[1] for c in class_decs_and_methods]
        if funcs_to_print:
            func_strings += ["".join([sep, self._print(i), sep]) for i in funcs_to_print]
        if isinstance(expr, BindCModule):
            func_strings += ["".join([sep, self._print(i), sep]) for i in expr.variable_wrappers]
        body = "\n".join(func_strings)
        # ...

        private = "private\n" if (funcs_to_print or expr.classes or expr.overload_sets) else ""
        contains = "contains\n" if (funcs_to_print or expr.classes or expr.overload_sets) else ""
        imports += "".join(self._print(i) for i in self._additional_imports.values())
        imports = self.print_constant_imports() + imports
        implicit_none = "" if expr.is_external else "implicit none\n"

        parts = [
            f"module {name}\n",
            imports,
            implicit_none,
            public_decs,
            private,
            decs,
            interfaces,
            contains,
            body,
            f"end module {name}\n",
        ]

        self.exit_scope()
        self._constantImports.pop()

        return "\n".join([a for a in parts if a])

    def _print_Program(self, expr):
        self.set_scope(expr.scope)
        self._constantImports.append({})

        name = f"prog_{self._print(expr.name)}".replace(".", "_")
        imports = "".join(self._print(i) for i in expr.imports)
        body = self._print(expr.body)

        # Print the declarations of all variables in the scope, which include:
        #  - user-defined variables (available in Program.variables)
        #  - x2py-generated variables added to Scope when printing 'expr.body'
        variables = self.scope.variables.values()
        decs = "".join(self._print(Declare(v)) for v in variables)

        # Detect if we are using mpi4py
        # TODO should we find a better way to do this?
        mpi = any(str(getattr(i.source, "name", i.source)) == "mpi4py" for i in expr.imports)

        # Additional code and variable declarations for MPI usage
        # TODO: check if we should really add them like this
        if mpi:
            body = (
                "call mpi_init(ierr)\n"
                + "\nallocate(status(0:-1 + mpi_status_size)) "
                + "\nstatus = 0\n"
                + body
                + "\ncall mpi_finalize(ierr)"
            )

            decs += "\ninteger :: ierr = -1" + "\ninteger, allocatable :: status (:)"
        imports += "".join(self._print(i) for i in self._additional_imports.values())
        imports += "\n" + self.print_constant_imports()
        parts = [
            f"program {name}\n",
            imports,
            "implicit none\n",
            decs,
            body,
            f"end program {name}\n",
        ]

        self.exit_scope()
        self._constantImports.pop()

        return "\n".join(a for a in parts if a)

    def _print_Import(self, expr):
        source = ""
        if expr.ignore:
            return ""

        source = expr.source
        if isinstance(source, Literal) and isinstance(source.dtype, StringType):
            source = source.python_value
        else:
            source = self._print(source)

        if source.endswith(".inc"):
            return f"#include <{source}>\n"

        if expr.source_module:
            source = expr.source_module.name

        if str(getattr(expr.source, "name", expr.source)) == "mpi4py":
            return "use mpi\n" + "use mpiext\n"

        targets = [t for t in expr.target if not isinstance(t.object, Module)]

        if len(targets) == 0:
            if isinstance(expr.source_module, FunctionDef) and expr.source_module.is_external:
                if expr.source_module.results:
                    out_args = list(expr.source_module.scope.collect_all_tuple_elements(expr.source_module.results.var))
                    return self._print(Declare(out_args[0].clone(source), external=True))
                return f"external :: {source}\n"

            return f"use {source}\n"

        targets = [t for t in targets if not getattr(t.object, "is_inline", False)]
        if len(targets) == 0:
            return ""

        prefix = f"use {source}, only:"

        code = ""
        for i in targets:
            old_name = i.name
            new_name = i.local_alias
            if old_name != new_name:
                target = f"{new_name} => {old_name}"
                line = f"{prefix} {target}"

            if isinstance(new_name, str):
                line = f"{prefix} {new_name}"

            else:
                raise TypeError(f"Expecting str, Symbol or AsName, given {type(i)}")

            code = (code + "\n" + line) if code else line

        # in some cases, the source is given as a string (when using metavar)
        code = code.replace("'", "")
        return code + "\n"

    def _print_Comment(self, expr):
        comments = self._print(expr.text)
        return "!" + comments + "\n"

    def _print_CommentBlock(self, expr):
        txts = expr.comments
        header = expr.header
        header_size = len(expr.header)

        ln = max(len(i) for i in txts)
        if ln < max(20, header_size + 2):
            ln = 20
        top = "!" + "_" * int((ln - header_size) / 2) + header + "_" * int((ln - header_size) / 2) + "!"
        ln = len(top) - 2
        bottom = "!" + "_" * ln + "!"

        txts = ["!" + txt + " " * (ln - len(txt)) + "!" for txt in txts]

        body = "\n".join(i for i in txts)

        return f"{top}\n{body}\n{bottom}\n"

    def _print_EmptyNode(self, expr):
        return ""

    def _print_AnnotatedComment(self, expr):
        accel = self._print(expr.accel)
        txt = str(expr.txt)
        return f"!${accel} {txt}\n"

    def _print_tuple(self, expr):
        if expr[0].rank > 0:
            raise NotImplementedError(" tuple with elements of rank > 0 is not implemented")
        fs = ", ".join(self._print(f) for f in expr)
        return f"[{fs}]"

    def _print_InhomogeneousTupleVariable(self, expr):
        fs = ", ".join(self._print(f) for f in expr)
        return f"[{fs}]"

    def _print_Variable(self, expr):
        return self._print(expr.name)

    def _print_FunctionDefArgument(self, expr):
        var = expr.var
        return ", ".join(self._print(v) for v in self.scope.collect_all_tuple_elements(var))

    def _print_FunctionCallArgument(self, expr):
        if expr.keyword and expr.keyword != "*args":
            keyword = expr.keyword.lstrip("*")
            return f"{keyword} = {self._print(expr.value)}"
        return self._print(expr.value)

    def _print_DottedVariable(self, expr):
        if isinstance(expr.lhs, FunctionCall):
            base = expr.lhs.funcdef.results.var
            var_name = self.scope.get_new_name()
            var = base.clone(var_name)

            self.scope.insert_variable(var)

            self._additional_code += self._print(Assign(var, expr.lhs)) + "\n"
            return self._print(var) + "%" + self._print(expr.name)
        return self._print(expr.lhs) + "%" + self._print(expr.name)

    def _print_DottedName(self, expr):
        return " % ".join(self._print(n) for n in expr.name)

    def _print_Lambda(self, expr):
        return f'"{expr.variables} -> {expr.expr}"'

    def _print_ComplexPart(self, expr):
        function = "real" if expr.part == "real" else "aimag"
        return f"{function}({self._print(expr.arg)})"

    def _print_Cast(self, expr):
        value = self._print(expr.arg)
        dtype = expr.dtype

        if isinstance(dtype, StringType):
            return value
        primitive_type = dtype.primitive_type
        if isinstance(primitive_type, PrimitiveBooleanType):
            return value if isinstance(expr.arg.dtype.primitive_type, PrimitiveBooleanType) else f"({value} /= 0)"

        kind = self.print_kind(dtype)
        if isinstance(primitive_type, PrimitiveIntegerType):
            return f"int({value}, kind={kind})"
        if isinstance(primitive_type, PrimitiveFloatingPointType):
            return f"real({value}, kind={kind})"
        if isinstance(primitive_type, PrimitiveComplexType):
            return f"cmplx({value}, kind={kind})"
        raise TypeError(f"Unsupported Fortran cast datatype {dtype}")

    # ======================================================================= #
    def _print_ArraySize(self, expr):
        init_value = self._print(expr.arg)
        prec = self.print_kind(expr)
        if isinstance(expr.arg.class_type, StringType):
            return f"len({init_value}, kind={prec})"
        return f"size({init_value}, kind={prec})"

    def _print_ArrayShapeElement(self, expr):
        arg = expr.arg
        arg_code = self._print(arg)
        prec = self.print_kind(expr)

        if isinstance(arg.class_type, NumpyNDArrayType):
            if arg.rank == 1:
                return f"size({arg_code}, kind={prec})"

            if arg.order == "C":
                index = Minus(convert_to_literal(arg.rank), expr.index)
                index = self._print(index)
            else:
                index = Add(expr.index, convert_to_literal(1))
                index = self._print(index)

            return f"size({arg_code}, {index}, {prec})"

        if isinstance(arg.class_type, StringType):
            return f"len({arg_code})"
        raise NotImplementedError(f"Don't know how to represent shape of object of type {arg.class_type}")

    def _print_ArrayAllocated(self, expr):
        return f"allocated({self._print(expr.arg)})"

    def _print_ArrayAssociated(self, expr):
        return f"associated({self._print(expr.arg)})"

    def _print_Declare(self, expr):
        # ... ignored declarations
        var = expr.variable
        expr_type = var.class_type
        if isinstance(expr_type, SymbolicType):
            return ""

        # meta-variables
        if isinstance(expr.variable, Variable) and expr.variable.name.startswith("__"):
            return ""
        # ...

        # ... TODO improve
        # Group the variables by intent
        dtype = var.dtype
        rank = var.rank
        shape = var.alloc_shape
        is_const = isinstance(expr_type, FinalType)
        is_optional = var.is_optional
        is_private = var.is_private
        is_alias = var.is_alias and not isinstance(dtype, BindCPointer)
        on_heap = var.on_heap
        on_stack = var.on_stack
        is_static = expr.static
        is_external = expr.external
        is_target = var.is_target and not var.is_alias
        intent = expr.intent
        intent_in = intent and intent != "out"
        deferred_string = isinstance(dtype, StringType) and not intent_in and (not shape or shape[0] is None)
        # ...

        dtype_str = ""
        rankstr = ""

        # ... print datatype
        if isinstance(expr_type, CustomDataType):
            name = self._print(expr_type)

            sig = "type"
            if var.is_argument:
                # When inheritance is supported we must also check if inheritance is possible
                arg = get_direct_function_argument(var)
                assert arg is not None
                if arg.bound_argument:
                    sig = "class"
            dtype_str = f"{sig}({name})"
        elif isinstance(dtype, BindCPointer):
            dtype_str = "type(c_ptr)"
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_ptr")
        elif isinstance(dtype, FixedSizeType) and isinstance(expr_type, NumpyNDArrayType | FixedSizeType):
            dtype_str = self._print(dtype.primitive_type)
            if isinstance(dtype, FixedSizeNumericType):
                dtype_str += f"({self.print_kind(var)})"

            if rank > 0:
                # arrays are 0-based in x2py, to avoid ambiguity with range
                start_val = self._print(convert_to_literal(0))

                if is_alias or on_heap:
                    rankstr = ", ".join(":" * rank)
                elif intent_in:
                    rankstr = ", ".join([f"{start_val}:"] * rank)
                elif is_static or on_stack:
                    ordered_shape = shape[::-1] if var.order == "C" else shape
                    ubounds = [Minus(s, convert_to_literal(1)) for s in ordered_shape]
                    rankstr = ", ".join(f"{start_val}:{self._print(u)}" for u in ubounds)
                else:
                    raise NotImplementedError("Fortran rank string undetermined")
                rankstr = f"({rankstr})"

        elif isinstance(dtype, StringType):
            dtype_str = self._print(dtype)

            if shape and shape[0] is not None:
                dtype_str += f"(len = {self._print(shape[0])})"
            elif intent_in:
                dtype_str += "(len = *)"
            else:
                dtype_str += "(len = :)"
        else:
            raise TypeError(f"Don't know how to print type {expr_type} in Fortran")

        code_value = ""
        if expr.value:
            code_value = f" = {self._print(expr.value)}"

        vstr = self._print(expr.variable.name)

        # Default empty strings
        intentstr = ""
        allocatablestr = ""
        optionalstr = ""
        privatestr = ""
        externalstr = ""

        # Compute intent string
        if intent:
            if intent == "in" and rank == 0 and not is_optional and not isinstance(expr_type, CustomDataType):
                intentstr = ", value"
                if is_const:
                    intentstr += ", intent(in)"
            else:
                intentstr = f", intent({intent})"

        # Compute allocatable string
        if not is_static:
            if is_alias:
                allocatablestr = ", pointer"

            elif (on_heap and isinstance(expr_type, NumpyNDArrayType)) or deferred_string:
                allocatablestr = ", allocatable"

            # ISSUES #177: var is allocatable and target
            if is_target:
                allocatablestr = f"{allocatablestr}, target"

        # Compute optional string
        if is_optional:
            optionalstr = ", optional"

        # Compute private string
        if is_private:
            privatestr = ", private"

        # Compute external string
        if is_external:
            externalstr = ", external"

        mod_str = ""
        if expr.module_variable and not is_private and isinstance(expr.variable.class_type, FixedSizeNumericType):
            mod_str = ", bind(c)"

        # Construct declaration
        left = dtype_str + allocatablestr + optionalstr + privatestr + externalstr + mod_str + intentstr
        right = vstr + rankstr + code_value
        return f"{left} :: {right}\n"

    def _print_AliasAssign(self, expr):
        code = ""
        lhs = expr.lhs
        rhs = expr.rhs

        if isinstance(rhs, FunctionCall):
            return self._print(rhs)

        # TODO improve
        op = "=>"
        shape_code = ""
        if isinstance(lhs.class_type, (NumpyNDArrayType)):
            shape_code = ", ".join("0:" for i in range(lhs.rank))
            shape_code = f"({shape_code})"

        code += f"{self._print(expr.lhs)}{shape_code} {op} {self._print(expr.rhs)}"

        return code + "\n"

    def _print_CodeBlock(self, expr):
        body_exprs = expr.body
        body_stmts = []
        for b in body_exprs:
            line = self._print(b)
            if self._additional_code:
                body_stmts.append(self._additional_code)
                self._additional_code = ""
            body_stmts.append(line)
        return "".join(body_stmts)

    def _print_Assign(self, expr):
        lhs = expr.lhs
        rhs = expr.rhs

        if isinstance(rhs, FunctionCall):
            return self._print(rhs)

        lhs_code = self._print(lhs)

        # Right-hand side code
        rhs_code = self._print(rhs)

        code = ""
        code += f"{lhs_code} = {rhs_code}"

        return code + "\n"

    # ------------------------------------------------------------------------------
    def _print_Allocate(self, expr):
        class_type = expr.variable.class_type
        if expr.alloc_type == "function" and isinstance(class_type, NumpyNDArrayType | CustomDataType):
            if expr.status == "unallocated":
                return ""
            if expr.status == "unknown":
                var_code = self._print(expr.variable)
                return f"if (allocated({var_code})) then\n  deallocate({var_code})\nend if\n"

            if expr.status == "allocated":
                var_code = self._print(expr.variable)
                return f"deallocate({var_code})\n"

        if isinstance(class_type, NumpyNDArrayType | CustomDataType):
            # Transpose indices because of Fortran column-major ordering
            shape = () if expr.variable.rank == 0 else expr.shape if expr.order == "F" else expr.shape[::-1]

            var_code = self._print(expr.variable)
            size_code = ", ".join(self._print(i) for i in shape)
            shape_code = ", ".join("0:" + self._print(Minus(i, convert_to_literal(1))) for i in shape)
            if shape:
                shape_code = f"({shape_code})"
            code = ""

            if expr.status == "unallocated":
                code += f"allocate({var_code}{shape_code})\n"

            elif expr.status == "unknown":
                code += f"if (allocated({var_code})) then\n"
                code += f"  if (any(size({var_code}) /= [{size_code}])) then\n"
                code += f"    deallocate({var_code})\n"
                code += f"    allocate({var_code}{shape_code})\n"
                code += "  end if\n"
                code += "else\n"
                code += f"  allocate({var_code}{shape_code})\n"
                code += "end if\n"

            elif expr.status == "allocated":
                code += f"if (any(size({var_code}) /= [{size_code}])) then\n"
                code += f"  deallocate({var_code})\n"
                code += f"  allocate({var_code}{shape_code})\n"
                code += "end if\n"

            return code

        if isinstance(class_type, NumpyNDArrayType | StringType):
            return ""

        return self._print_not_supported(expr)

    # -----------------------------------------------------------------------------
    def _print_Deallocate(self, expr):
        var = expr.variable
        class_type = var.class_type

        if isinstance(class_type, CustomDataType):
            x2py__del = expr.variable.cls_base.scope.find("__del__")
            if x2py__del:
                x2py_del_args = [FunctionCallArgument(var)]
                return self._print(FunctionCall(x2py__del, x2py_del_args))
            return ""

        if var.is_alias:
            return ""
        if isinstance(class_type, NumpyNDArrayType | StringType):
            var_code = self._print(var)
            return f"if (allocated({var_code})) deallocate({var_code})\n"
        raise NotImplementedError(f"Deallocate not implemented for {class_type}")

    def _print_DeallocatePointer(self, expr):
        var_code = self._print(expr.variable)
        return f"deallocate({var_code})\n"

    # ------------------------------------------------------------------------------

    def _print_PrimitiveBooleanType(self, expr):
        return "logical"

    def _print_PrimitiveIntegerType(self, expr):
        return "integer"

    def _print_PrimitiveFloatingPointType(self, expr):
        return "real"

    def _print_PrimitiveComplexType(self, expr):
        return "complex"

    def _print_PrimitiveCharacterType(self, expr):
        return "character"

    def _print_StringType(self, expr):
        return "character"

    def _print_FixedSizeNumericType(self, expr):
        return f"{self._print(expr.primitive_type)}{expr.precision}"

    def _print_NumpyBoolType(self, expr):
        return "logical"

    def _print_CustomDataType(self, expr):
        while hasattr(expr, "underlying_type"):
            expr = expr.underlying_type
        try:
            name = self.scope.get_import_alias(expr, "cls_constructs")
        except RuntimeError:
            name = expr.low_level_name
        return name

    def _print_DataType(self, expr):
        return self._print(expr.name)

    def _print_FunctionOverloadSet(self, expr):
        dispatcher_funcs = expr.functions

        example_func = dispatcher_funcs[0]

        # ... we don't print 'hidden' functions
        if not example_func.is_semantic:
            return ""

        if example_func.results and len({f.results.var.rank == 0 for f in dispatcher_funcs}) != 1:
            message = (
                "Fortran cannot yet handle a templated function returning either a scalar or an array. "
                "If you are using the terminal interface, please pass --language c, "
                "if you are using the interactive interfaces ex2py or lambdify, please pass language='c'. "
                "See https://github.com/x2py/x2py/issues/1339 to monitor the advancement of this issue."
            )
            raise NotImplementedError(message)

        name = self._print(expr.native_name)
        if all(isinstance(f, FunctionAddress) for f in dispatcher_funcs):
            funcs = dispatcher_funcs
        else:
            funcs = [
                f
                for f in dispatcher_funcs
                if f
                is expr.point([FunctionCallArgument(a.var.clone("arg_" + str(i))) for i, a in enumerate(f.arguments)])
            ]

        if expr.is_argument:
            funcs_sigs = []
            for f in funcs:
                self._constantImports.append({})
                parts = self.function_signature(f, f.name)
                parts = [
                    "{}({}) {}\n".format(parts["sig"], parts["arg_code"], parts["func_end"]),
                    self.print_constant_imports() + "\n",
                    parts["arg_decs"],
                    "end {} {}\n".format(parts["func_type"], f.name),
                ]
                funcs_sigs.append("".join(a for a in parts))
                self._constantImports.pop()
            return "interface\n" + "\n".join(a for a in funcs_sigs) + "end interface\n"

        if funcs[0].cls_name:
            cls_name = expr.cls_name
            if cls_name != "__UNDEFINED__":
                name = f"{cls_name}_{name}"
        interface = "interface " + name + "\n"
        for f in funcs:
            interface += "module procedure " + str(f.name) + "\n"
        interface += "end interface\n"
        return interface

    def _print_FunctionAddress(self, expr):
        return expr.name

    def function_signature(self, expr, name):
        """
        Get the different parts of the signature of the function `expr`.

        A helper function to print just the signature of the function
        including the declarations of the arguments and results.

        Parameters
        ----------
        expr : FunctionDef
            The function whose signature should be printed.
        name : str
            The name which should be printed as the name of the function.
            (May be different from expr.name in the case of interfaces).

        Returns
        -------
        dict
            A dictionary with the keys :
                sig - The declaration of the function/subroutine with any necessary keywords.
                arg_code - A string containing a list of the arguments.
                func_end - Any code to be added to the signature after the arguments (ie result).
                arg_decs - The code necessary to declare the arguments of the function/subroutine.
                func_type - Subroutine or function.
        """
        is_pure = expr.is_pure
        is_elemental = expr.is_elemental
        out_args = [v for v in expr.scope.collect_all_tuple_elements(expr.results.var) if v and not v.is_argument]
        args_decs = OrderedDict()
        arguments = expr.arguments
        class_arg = next((a for a in arguments if a.bound_argument), None)

        func_end = ""
        rec = "recursive " if expr.is_recursive else ""
        string_result = isinstance(expr.results.var.class_type, StringType)
        if len(out_args) != 1 or (expr.results.var.rank > 0 and not string_result):
            func_type = "subroutine"
            for result in out_args:
                args_decs[result] = Declare(result, intent="out")

        else:
            # todo: if return is a function
            func_type = "function"
            result = out_args[0]
            func_end = f"result({result.name})"

            args_decs[result] = Declare(result)
            out_args = []
        # ...

        for arg in arguments:
            arg_var = arg.var
            if isinstance(arg_var, Variable):
                inout = arg.inout and not isinstance(arg_var, BindCVariable)
                for v in self.scope.collect_all_tuple_elements(arg_var):
                    dec = Declare(v, intent="inout") if inout else Declare(v, intent="in")
                    args_decs[v] = dec

        # treat case of pure function
        sig = f"{rec}{func_type} {name}"
        if is_pure:
            sig = f"pure {sig}"

        # treat case of elemental function
        if is_elemental:
            sig = f"elemental {sig}"

        arg_iter = chain((class_arg,), out_args, arguments[1:]) if class_arg else chain(out_args, arguments)
        arg_code = ", ".join(self._print(i) for i in arg_iter)

        arg_decs = "".join(self._print(i) for i in args_decs.values())

        return {
            "sig": sig,
            "arg_code": arg_code,
            "func_end": func_end,
            "arg_decs": arg_decs,
            "func_type": func_type,
        }

    def _print_FunctionDef(self, expr):
        if not expr.is_semantic:
            return ""
        self.set_scope(expr.scope)

        for r in expr.scope.collect_all_tuple_elements(expr.results.var):
            if r.rank and r.memory_handling == "stack" and any(not isinstance(s, Literal) for s in r.alloc_shape):
                raise ValueError("Can't return a stack array of unknown size")

        name = expr.cls_name or expr.name

        sig_parts = self.function_signature(expr, name)
        bind_c = " bind(c)" if isinstance(expr, BindCFunctionDef) else ""
        prelude = sig_parts.pop("arg_decs")
        functions = [f for f in expr.functions if f.is_semantic]
        func_interfaces = "\n".join(self._print(i) for i in expr.overload_sets)
        body_code = self._print(expr.body)
        docstring = self._print(expr.docstring) if expr.docstring else ""

        decs = [Declare(v) for v in expr.local_vars if not v.is_argument]
        self._get_external_declarations(decs)

        prelude += "".join(self._print(i) for i in decs)
        if len(functions) > 0:
            functions_code = "\n".join(self._print(i) for i in functions)
            body_code = body_code + "\ncontains\n" + functions_code

        external_imports = [
            i for i in expr.imports if isinstance(i.source_module, FunctionDef) and i.source_module.is_external
        ]
        imports = [i for i in expr.imports if i not in external_imports]
        imports = "".join(self._print(i) for i in imports)
        external_imports = "".join(self._print(i) for i in external_imports)

        parts = [
            docstring,
            f"{sig_parts['sig']}({sig_parts['arg_code']}){bind_c} {sig_parts['func_end']}\n",
            imports,
            "implicit none\n",
            external_imports,
            prelude,
            func_interfaces,
            body_code,
            "end {} {}\n".format(sig_parts["func_type"], name),
        ]

        self.exit_scope()

        return "\n".join(a for a in parts if a)

    def _print_Return(self, expr):
        code = ""
        if expr.stmt:
            code += self._print(expr.stmt)
        code += "return\n"
        return code

    def _print_Del(self, expr):
        return "".join(self._print(var) for var in expr.variables)

    def _print_ClassDef(self, expr):
        # ... we don't print 'hidden' classes
        if expr.hide:
            return "", ""
        # ...
        self.set_scope(expr.scope)

        name = self._print(expr.name)
        base = None  # TODO: add base in ClassDef

        decs = "".join(self._print(Declare(i)) for i in expr.attributes)

        names = []
        methods = "".join(
            f"procedure :: {method.name} => {method.cls_name}\n" for method in expr.methods if method.is_semantic
        )
        for i in expr.overload_sets:
            names = ",".join(f.cls_name for f in i.functions if f.is_semantic)
            if names:
                methods += f"generic, public :: {i.native_name} => {names}\n"
                methods += f"procedure :: {names}\n"

        self.exit_scope()

        sig = "type"
        if base is not None:
            sig = f"{sig}, extends({base})"

        docstring = self._print(expr.docstring) if expr.docstring else ""
        code = f"{sig} :: {name}\n{decs}\n"
        code = code + "contains\n" + methods
        decs = "".join([docstring, code, f"end type {name}\n"])

        sep = self._print(SeparatorComment(40))
        cls_methods = [i for i in expr.methods if i.is_semantic]
        for i in expr.overload_sets:
            cls_methods += [j for j in i.functions if j.is_semantic]

        methods = "".join("\n".join(["", sep, self._print(i), sep, ""]) for i in cls_methods)

        return decs, methods

    def _print_AugAssign(self, expr):
        new_expr = expr.to_basic_assign()
        return self._print(new_expr)

    def _handle_not_none(self, lhs, lhs_var):
        """
        Print code for `x is not None` statement.

        Print the code which checks if x is not None. This means different
        things depending on the type of `x`. If `x` is optional it checks
        if it is present, if `x` is a C pointer it checks if it points at
        anything.

        Parameters
        ----------
        lhs : str
            The code representing `x`.
        lhs_var : Variable
            The Variable `x`.

        Returns
        -------
        str
            The code which checks if `x is not None`.
        """
        if isinstance(lhs_var.dtype, BindCPointer):
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_associated")
            return f"c_associated({lhs})"
        return f"present({lhs})"

    def _print_IsNot(self, expr):
        lhs, rhs = expr.args
        if rhs is NIL:
            return self._handle_not_none(self._print(lhs), lhs)
        if lhs is NIL:
            return self._handle_not_none(self._print(rhs), rhs)
        raise NotImplementedError(f"Fortran is-not printing is not implemented for {expr}")

    def _print_Is(self, expr):
        lhs, rhs = expr.args
        if rhs is NIL:
            return f".not. {self._handle_not_none(self._print(lhs), lhs)}"
        if lhs is NIL:
            return f".not. {self._handle_not_none(self._print(rhs), rhs)}"
        raise NotImplementedError(f"Fortran is printing is not implemented for {expr}")

    def _print_If(self, expr):
        # ...

        lines = []

        for i, (c, e) in enumerate(expr.blocks):
            if i == len(expr.blocks) - 1 and isinstance(c, Literal) and c.python_value is True:
                lines.append("else\n")
            elif i == 0:
                lines.append(f"if ({self._print(c)}) then\n")
            else:
                lines.append(f"else if ({self._print(c)}) then\n")

            if isinstance(e, list | tuple):
                lines.extend(self._print(ee) for ee in e)
            else:
                lines.append(self._print(e))

        if len(lines) == 0:
            return ""
        if lines[0] == "else\n":
            lines = lines[1:]
        else:
            lines.append("end if\n")

        return "".join(lines)

    def _print_IfTernaryOperator(self, expr):
        cond = (
            cast_to(expr.cond, NumpyBoolType())
            if not isinstance(expr.cond.dtype.primitive_type, PrimitiveBooleanType)
            else expr.cond
        )
        value_true, value_false = self._apply_cast(expr.dtype, expr.value_true, expr.value_false)

        cond = self._print(cond)
        value_true = self._print(value_true)
        value_false = self._print(value_false)
        return f"merge({value_true}, {value_false}, {cond})"

    def _print_Pow(self, expr):
        base = expr.args[0]
        e = expr.args[1]

        base_c = self._print(base)
        e_c = self._print(e)
        return f"{base_c} ** {e_c}"

    def _print_Add(self, expr):
        if isinstance(expr.dtype, StringType):
            return " // ".join(self._print(a) for a in expr.args)
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        return " + ".join(self._print(a) for a in args)

    def _print_Minus(self, expr):
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        args_code = [self._print(a) for a in args]

        return " - ".join(args_code)

    def _print_Mul(self, expr):
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        args_code = [self._print(a) for a in args]
        return " * ".join(a for a in args_code)

    def _print_Div(self, expr):
        if all(isinstance(a.dtype.primitive_type, PrimitiveBooleanType | PrimitiveIntegerType) for a in expr.args):
            args = [cast_to(a, NumpyFloat64Type()) for a in expr.args]
        else:
            args = expr.args
        return " / ".join(self._print(a) for a in args)

    def _print_Mod(self, expr):
        is_float = isinstance(expr.dtype.primitive_type, PrimitiveFloatingPointType)

        def correct_type_arg(a):
            if is_float and isinstance(a.dtype.primitive_type, PrimitiveIntegerType):
                return cast_to(a, NumpyFloat64Type())
            return a

        args = [self._print(correct_type_arg(a)) for a in expr.args]

        code = args[0]
        for c in args[1:]:
            code = f"MODULO({code},{c})"
        return code

    def _print_FloorDiv(self, expr):
        new_args = [self._apply_cast(expr.dtype, arg) for arg in expr.args]
        args = [self._print(arg) for arg in new_args]
        if all(
            isinstance(
                arg.dtype.primitive_type,
                PrimitiveBooleanType | PrimitiveIntegerType,
            )
            for arg in expr.args
        ):
            self.add_import(Import("pyc_math_f90", Module("pyc_math_f90", (), ())))
            return f"pyc_floor_div({args[0]}, {args[1]})"
        return f"real(FLOOR({args[0]} / {args[1]}, {self.print_kind(expr)}), {self.print_kind(expr)})"

    def _print_And(self, expr):
        args = [
            (a if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else cast_to(a, NumpyBoolType()))
            for a in expr.args
        ]
        return " .and. ".join(self._print(a) for a in args)

    def _print_Or(self, expr):
        args = [
            (a if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else cast_to(a, NumpyBoolType()))
            for a in expr.args
        ]
        return " .or. ".join(self._print(a) for a in args)

    def _print_Eq(self, expr):
        lhs, rhs = expr.args
        lhs_code = self._print(lhs)
        rhs_code = self._print(rhs)
        a = lhs.dtype.primitive_type
        b = rhs.dtype.primitive_type

        if all(isinstance(var, PrimitiveBooleanType) for var in (a, b)):
            return f"{lhs_code} .eqv. {rhs_code}"
        if lhs.class_type is rhs.class_type or (
            isinstance(lhs.class_type, FixedSizeNumericType) and isinstance(rhs.class_type, FixedSizeNumericType)
        ):
            return f"{lhs_code} == {rhs_code}"
        raise NotImplementedError(f"Fortran equality printing is not implemented for {expr}")

    def _print_Ne(self, expr):
        lhs, rhs = expr.args
        lhs_code = self._print(lhs)
        rhs_code = self._print(rhs)
        a = lhs.dtype.primitive_type
        b = rhs.dtype.primitive_type

        if all(isinstance(var, PrimitiveBooleanType) for var in (a, b)):
            return f"{lhs_code} .neqv. {rhs_code}"
        if lhs.class_type is rhs.class_type or (
            isinstance(lhs.class_type, FixedSizeNumericType) and isinstance(rhs.class_type, FixedSizeNumericType)
        ):
            return f"{lhs_code} /= {rhs_code}"
        raise NotImplementedError(f"Fortran inequality printing is not implemented for {expr}")

    def _print_Lt(self, expr):
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return f"{lhs} < {rhs}"

    def _print_Le(self, expr):
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return f"{lhs} <= {rhs}"

    def _print_Gt(self, expr):
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return f"{lhs} > {rhs}"

    def _print_Ge(self, expr):
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return f"{lhs} >= {rhs}"

    def _print_Not(self, expr):
        a = self._print(expr.args[0])
        if not isinstance(expr.args[0].dtype.primitive_type, PrimitiveBooleanType):
            return f"{a} == 0"
        return f".not. {a}"

    def _print_Header(self, expr):
        return ""

    def _print_int(self, expr):
        return str(expr)

    def _print_Literal(self, expr):
        value = expr.python_value
        dtype = expr.dtype

        if expr is NIL:
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_null_ptr")
            return "c_null_ptr"
        if isinstance(dtype, StringType):
            if value == "":
                return "''"
            special_characters = {"\a", "\b", "\f", "\r", "\t", "\v", "'", "\n"}
            substring = ""
            parts = []
            for character in value:
                if character in special_characters:
                    if substring:
                        parts.append(f"'{substring}'")
                        substring = ""
                    parts.append(f"ACHAR({ord(character)})")
                else:
                    substring += character
            if substring:
                parts.append(f"'{substring}'")
            return " // ".join(parts)

        primitive_type = dtype.primitive_type
        if isinstance(primitive_type, PrimitiveBooleanType):
            value_code = ".True." if value else ".False."
            return f"{value_code}_{self.print_kind(expr)}"
        if isinstance(primitive_type, PrimitiveComplexType):
            real = self._print(Literal(value.real, dtype.element_type))
            imag = self._print(Literal(value.imag, dtype.element_type))
            return f"({real}, {imag})"
        return f"{value!r}_{self.print_kind(expr)}"

    def _print_IndexedElement(self, expr):
        base = expr.base
        if isinstance(base.class_type, TupleType):
            return self._print(self.scope.collect_tuple_element(expr))
        if isinstance(base.class_type, StringType):
            if len(expr.indices) != 1 or isinstance(expr.indices[0], Slice):
                raise NotImplementedError("Fortran string indexing requires one index")
            index = self._print(expr.indices[0])
            return f"{self._print(base)}({index}:{index})"
        if not isinstance(base.class_type, NumpyNDArrayType):
            raise NotImplementedError(f"Fortran indexing is not implemented for {base.class_type}")

        indices = list(expr.indices)
        if base.order != "F":
            indices.reverse()

        indices = [
            Slice(index.start, Minus(index.stop, convert_to_literal(1)), index.step)
            if isinstance(index, Slice) and index.stop is not None and index.stop is not NIL
            else index
            for index in indices
        ]
        return f"{self._print(base)}({', '.join(self._print(i) for i in indices)})"

    def _print_Slice(self, expr):
        start = "" if expr.start is None or expr.start is NIL else self._print(expr.start)
        stop = "" if expr.stop is None or expr.stop is NIL else self._print(expr.stop)
        if expr.step is not None:
            return f"{start}:{stop}:{self._print(expr.step)}"
        return f"{start}:{stop}"

    # =======================================================================================

    def _print_FunctionCall(self, expr):
        func = expr.funcdef

        native_name = expr.overload_set.native_name_for(func) if expr.overload_set else ""
        if expr.overload_set and self._is_defined_operator(native_name):
            args = expr.overload_set.native_arguments(func, expr.args)
            values = [self._print(argument.value) for argument in args]
            token = self._defined_operator_token(native_name)
            if len(values) == 1:
                code = f".not. {values[0]}" if token == ".not." else f"{token}{values[0]}"
            else:
                code = f"{values[0]} {token} {values[1]}"
            parent_assign = get_direct_assignment(expr)
            if parent_assign:
                assignment = "=>" if isinstance(parent_assign, AliasAssign) else "="
                return f"{self._print(parent_assign.lhs)} {assignment} {code}\n"
            return code

        f_name = self._print(expr.func_name if not expr.overload_set else expr.overload_set_name)

        if func.is_imported:
            f_name = self.scope.get_import_alias(func, "functions")
        elif expr.overload_set and expr.overload_set.is_imported:
            f_name = self.scope.get_import_alias(expr.overload_set, "functions")

        args = expr.args
        func_result_variables = (
            func.scope.collect_all_tuple_elements(func.results.var) if func.scope else [func.results.var]
        )
        out_results = [v for v in func_result_variables if v and not v.is_argument]
        parent_assign = get_direct_assignment(expr)
        is_function = len(out_results) == 1 and (
            func.results.var.rank == 0 or isinstance(func.results.var.class_type, StringType)
        )
        if len(out_results) == 1 and isinstance(func.results.var.class_type, NumpyNDArrayType):
            is_function = func.results.var.memory_handling in {"alias", "heap"}

        if func.arguments and func.arguments[0].bound_argument:
            bound_name = expr.overload_set_name if expr.overload_set else func.scope.get_python_name(func.name)
            f_name = self._print(bound_name)
            class_variable = args[0].value
            args = args[1:]
            if isinstance(class_variable, FunctionCall):
                base = class_variable.funcdef.results.var
                var = self.scope.get_temporary_variable(base)

                self._additional_code += self._print(Assign(var, class_variable)) + "\n"
                f_name = f"{self._print(var)} % {f_name}"
            else:
                f_name = f"{self._print(class_variable)} % {f_name}"

        if parent_assign:
            lhs = parent_assign.lhs
            lhs_vars = {out_results[0]: lhs} if len(out_results) == 1 else dict(zip(out_results, lhs, strict=False))
            assign_args = []
            for a in args:
                key = a.keyword
                arg = a.value
                if arg in lhs_vars.values():
                    var = arg.clone(self.scope.get_new_name())
                    self.scope.insert_variable(var)
                    self._additional_code += self._print(Assign(var, arg))
                    newarg = var
                else:
                    newarg = arg
                assign_args.append(FunctionCallArgument(newarg, key))
            args = assign_args
            results = list(lhs_vars.values())
            results_strs = [] if is_function else [self._print(r) for r in lhs_vars.values()]

        else:
            results_strs = []
            results = None

        args_strs = [self._print(a) for a in args if a.value is not NIL]
        args_code = ", ".join(results_strs + args_strs)
        code = f"{f_name}({args_code})"
        if not is_function:
            code = f"call {code}\n"

        if not parent_assign:
            if is_function or len(out_results) == 0:
                return code
            self._additional_code += code
            if len(out_results) == 1:
                return self._print(results[0])
            return self._print(tuple(results))
        if is_function:
            result_code = self._print(results[0])
            if isinstance(parent_assign, AliasAssign):
                return f"{result_code} => {code}\n"
            return f"{result_code} = {code}\n"
        return code

    @staticmethod
    def _is_defined_operator(name):
        return re.fullmatch(r"operator\(.+\)", re.sub(r"\s+", "", str(name)), re.IGNORECASE) is not None

    @staticmethod
    def _defined_operator_token(name):
        compact = re.sub(r"\s+", "", str(name))
        return compact[compact.index("(") + 1 : -1]

    # =======================================================================================

    def _print_CLocFunc(self, expr):
        lhs = self._print(expr.result)
        rhs = self._print(expr.arg)
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_loc")
        return f"{lhs} = c_loc({rhs})\n"

    def _print_C_NULL_CHAR(self, expr):
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("C_NULL_CHAR")
        return "C_NULL_CHAR"

    def _print_C_F_Pointer(self, expr):
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("C_F_Pointer")
        shape_tuple = expr.shape or ()
        shape = ", ".join(self._print(s) for s in shape_tuple)
        if shape:
            return f"call C_F_Pointer({self._print(expr.c_pointer)}, {self._print(expr.f_array)}, [{shape}])\n"
        return f"call C_F_Pointer({self._print(expr.c_pointer)}, {self._print(expr.f_array)})\n"

    # =======================================================================================

    def _print_PythonConjugate(self, expr):
        return f"conjg( {self._print(expr.internal_var)} )"

    # =======================================================================================

    def _wrap_fortran(self, lines):
        """
        Wrap long Fortran lines.

        A comment line is split at white space. Code lines are split with a more
        complex rule to give nice results.

        Parameters
        ----------
        lines : list[str]
            A list of lines (ending with a \\n character).

        Returns
        -------
        list[str]
            A list of the new lines.
        """
        # routine to find split point in a code line
        my_alnum = set("_+-." + string.digits + string.ascii_letters)
        my_white = set(" \t()")

        def split_pos_code(line, endpos):
            if len(line) <= endpos:
                return len(line)
            pos = endpos

            def split(pos):
                return (
                    (line[pos] in my_alnum and line[pos - 1] not in my_alnum)
                    or (line[pos] not in my_alnum and line[pos - 1] in my_alnum)
                    or (line[pos] in my_white and line[pos - 1] not in my_white)
                    or (line[pos] not in my_white and line[pos - 1] in my_white)
                )

            while not split(pos):
                pos -= 1
                if pos == 0:
                    return endpos
            return pos

        # split line by line and add the split lines to result
        result = []
        trailing = " &"
        # trailing with no added space characters in case splitting is within quotes
        quote_trailing = "&"

        for line in lines:
            if len(line) > 72:
                cline = line[:72].lstrip()
                if cline.startswith("!") and not cline.startswith("!$"):
                    result.append(line)
                    continue

                tab_len = line.index(cline[0])
                # code line
                # set containing positions inside quotes
                inside_quotes_positions = set()
                inside_quotes_intervals = [
                    (match.start(), match.end()) for match in re.compile("(\"[^\"]*\")|('[^']*')").finditer(line)
                ]
                for lidx, ridx in inside_quotes_intervals:
                    for idx in range(lidx, ridx):
                        inside_quotes_positions.add(idx)
                initial_len = len(line)
                pos = split_pos_code(line, 72)

                startswith_omp = cline.startswith("!$omp")
                startswith_acc = cline.startswith("!$acc")

                if startswith_acc or startswith_omp:
                    assert pos >= 5

                if pos not in inside_quotes_positions:
                    hunk = line[:pos].rstrip()
                    line = line[pos:].lstrip()
                else:
                    hunk = line[:pos]
                    line = line[pos:]

                if line:
                    hunk += quote_trailing if pos in inside_quotes_positions else trailing

                last_cut_was_inside_quotes = pos in inside_quotes_positions
                result.append(hunk)
                while len(line) > 0:
                    removed = initial_len - len(line)
                    pos = split_pos_code(line, 65 - tab_len)
                    if pos + removed not in inside_quotes_positions:
                        hunk = line[:pos].rstrip()
                        line = line[pos:].lstrip()
                    else:
                        hunk = line[:pos]
                        line = line[pos:]
                    if line:
                        hunk += quote_trailing if (pos + removed) in inside_quotes_positions else trailing

                    if last_cut_was_inside_quotes:
                        hunk_start = tab_len * " " + "&"
                    elif startswith_omp:
                        hunk_start = tab_len * " " + "!$omp &"
                    elif startswith_acc:
                        hunk_start = tab_len * " " + "!$acc &"
                    else:
                        hunk_start = tab_len * " " + "      "

                    result.append(hunk_start + hunk)
                    last_cut_was_inside_quotes = (pos + removed) in inside_quotes_positions
            else:
                result.append(line)

        # make sure that all lines end with a carriage return
        return [line if line.endswith("\n") else line + "\n" for line in result]

    def indent_code(self, code):
        """
        Add the correct indentation to the code.

        Analyse the code to calculate when indentation is needed.
        Add the necessary spaces at the start of each line.

        Parameters
        ----------
        code : str | iterable[str]
            A string of code or a list of code lines.

        Returns
        -------
        list[str]
            A list of indented code lines.
        """
        if isinstance(code, str):
            code_lines = self.indent_code(code.splitlines(True))
            return "".join(code_lines)

        code = [line.lstrip(" \t") for line in code]

        increase = [int(inc_regex.match(line) is not None) for line in code]
        decrease = [int(dec_regex.match(line) is not None) for line in code]

        level = 0
        tabwidth = self._default_settings["tabwidth"]
        new_code = []
        for i, line in enumerate(code):
            if line in ("", "\n") or line.startswith("#"):
                new_code.append(line)
                continue
            level -= decrease[i]

            padding = " " * (level * tabwidth)

            line = f"{padding}{line}"

            new_code.append(line)
            level += increase[i]

        return new_code

    def _print_BindCArrayVariable(self, expr):
        return self._print(expr.wrapper_function)

    def _print_BindCClassDef(self, expr):
        funcs = [
            expr.new_func,
            *expr.methods,
            *[f for i in expr.overload_sets for f in i.functions],
            *[a.getter for a in expr.attributes],
            *[a.setter for a in expr.attributes if a.setter],
        ]
        sep = f"\n{self._print(SeparatorComment(40))}\n"
        return "", sep.join(self._print(f) for f in funcs)

    def _print_BindCSizeOf(self, expr):
        elem = self._print(expr.args[0])
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_size_t")
        return f"storage_size({elem}, kind = c_size_t)"

    def _print_FortranTransfer(self, expr: FortranTransfer):
        source = self._print(expr.source)
        mold = self._print(expr.mold)
        if expr.size is None:
            return f"transfer({source}, {mold})"
        size = self._print(expr.size)
        return f"transfer({source}, {mold}, {size})"

    def _print_AllDeclaration(self, expr):
        return ""

    def _print_KindSpecification(self, expr):
        return f"(kind = {self.print_kind(expr.type_specifier)})"
