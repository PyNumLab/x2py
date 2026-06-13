# coding: utf-8
"""Print to F90 standard. Trying to follow the information provided at
www.fortran90.org as much as possible."""

import ast
import re
import string
import sys
from collections import OrderedDict
from itertools import chain

import numpy as np

from ..bind_c import (
    BindCClassDef,
    BindCFunctionDef,
    BindCModule,
    BindCPointer,
    BindCVariable,
)

from ..models.datatypes import (
    DtypePrecisionToCastFunction,
    PythonBool,
    PythonInt,
)
from ..models.core import (
    AliasAssign,
    Assign,
    CodeBlock,
    Deallocate,
    Declare,
    For,
    FunctionAddress,
    FunctionCall,
    FunctionCallArgument,
    FunctionDef,
    FunctionDefResult,
    get_direct_assignment,
    get_direct_function_argument,
    If,
    IfSection,
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
    HomogeneousContainerType,
    PrimitiveBooleanType,
    PrimitiveCharacterType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    Type,
    PythonNativeBool,
    PythonNativeInt,
    StringType,
    SymbolicType,
    TupleType,
    x2py_type_to_original_type,
)
from ..models.datatypes import (
    Literal,
    LiteralEllipsis,
    LiteralFalse,
    LiteralFloat,
    LiteralInteger,
    LiteralString,
    LiteralTrue,
    Nil,
    convert_to_literal,
)

from ..models.datatypes import (
    NumpyComplex128Type,
    NumpyFloat64Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from ..models.core import (
    Add,
    Eq,
    Gt,
    Lt,
    Minus,
    Mod,
    Mul,
    Not,
    UnarySub,
)

from ..models.core import IndexedElement, Variable
from .codeprinter import CodePrinter
from ..scope import Scope

# TODO: add examples

__all__ = ["FCodePrinter", "fcode"]


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
end_regex_str = "(end ?({}))|(else)".format(
    "|".join("({})".format(k) for k in end_keyword)
)
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

    _default_settings = {
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
            rename = [
                c if isinstance(c, str) else c[0] + " => " + c[1] for c in imports
            ]
            if len(rename) == 0:
                continue
            rename.sort()
            macro += " , ".join(rename)
            macro += "\n"
            macros.append(macro)
        return "".join(macros)

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
        if (
            constant_shortcut not in self.scope.all_used_symbols
            and constant_name != constant_shortcut
        ):
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add(
                (constant_shortcut, constant_name)
            )
            constant_name = constant_shortcut
        else:
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add(
                constant_name
            )
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
                m_name = method.name
                method.cls_name = scope.get_new_name(f"{name}_{method.name}")
        for i in expr.interfaces:
            for f in i.functions:
                if f.is_semantic:
                    i_name = f.name
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
        try:
            cast_func = DtypePrecisionToCastFunction[target_type]
        except KeyError:
            raise
            errors.report(X2PY_RESTRICTION_TODO, severity="fatal")

        new_args = []
        for a in args:
            if target_type != a.class_type:
                a = cast_func(a)
            new_args.append(a)

        if len(args) == 1:
            return new_args[0]
        else:
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

        funcs_to_print = list(expr.funcs) + [
            f for i in expr.interfaces for f in i.functions
        ]

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
            interfaces = (
                "interface\n"
                'function c_malloc(size) bind(C,name="malloc") result(ptr)\n'
                "use iso_c_binding\n"
                "integer(c_size_t), value, intent(in) :: size\n"
                "type(c_ptr) :: ptr\n"
                "end function c_malloc\n"
                "end interface\n"
            )
        else:
            interfaces = "\n".join(self._print(i) for i in expr.interfaces)
            public_decs += "".join(
                f"public :: {i.name}\n"
                for i in expr.interfaces
                if i.is_semantic and not i.is_private
            )

        func_strings = []
        # Get class functions
        func_strings += [c[1] for c in class_decs_and_methods]
        if funcs_to_print:
            func_strings += [
                "".join([sep, self._print(i), sep]) for i in funcs_to_print
            ]
        if isinstance(expr, BindCModule):
            func_strings += [
                "".join([sep, self._print(i), sep]) for i in expr.variable_wrappers
            ]
        body = "\n".join(func_strings)
        # ...

        private = (
            "private\n" if (funcs_to_print or expr.classes or expr.interfaces) else ""
        )
        contains = (
            "contains\n" if (funcs_to_print or expr.classes or expr.interfaces) else ""
        )
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

        name = "prog_{0}".format(self._print(expr.name)).replace(".", "_")
        imports = "".join(self._print(i) for i in expr.imports)
        body = self._print(expr.body)

        # Print the declarations of all variables in the scope, which include:
        #  - user-defined variables (available in Program.variables)
        #  - x2py-generated variables added to Scope when printing 'expr.body'
        variables = self.scope.variables.values()
        decs = "".join(self._print(Declare(v)) for v in variables)

        # Detect if we are using mpi4py
        # TODO should we find a better way to do this?
        mpi = any(
            "mpi4py" == str(getattr(i.source, "name", i.source)) for i in expr.imports
        )

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
            "program {}\n".format(name),
            imports,
            "implicit none\n",
            decs,
            body,
            "end program {}\n".format(name),
        ]

        self.exit_scope()
        self._constantImports.pop()

        return "\n".join(a for a in parts if a)

    def _print_Import(self, expr):

        source = ""
        if expr.ignore:
            return ""

        source = expr.source
        if isinstance(source, LiteralString):
            source = source.python_value
        else:
            source = self._print(source)

        if source.endswith(".inc"):
            return f"#include <{source}>\n"

        if expr.source_module:
            source = expr.source_module.name

        if "mpi4py" == str(getattr(expr.source, "name", expr.source)):
            return "use mpi\n" + "use mpiext\n"

        targets = [t for t in expr.target if not isinstance(t.object, Module)]

        if len(targets) == 0:
            if isinstance(expr.source_module, FunctionDef) and expr.source_module.is_external:
                if expr.source_module.results:
                    out_args = [v for v in expr.source_module.scope.collect_all_tuple_elements(expr.source_module.results.var)]
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
                target = "{target} => {name}".format(target=new_name, name=old_name)
                line = "{prefix} {target}".format(prefix=prefix, target=target)

            if isinstance(new_name, str):
                line = "{prefix} {target}".format(prefix=prefix, target=new_name)

            else:
                raise TypeError(
                    "Expecting str, Symbol or AsName, "
                    "given {}".format(type(i))
                )

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
        top = (
            "!"
            + "_" * int((ln - header_size) / 2)
            + header
            + "_" * int((ln - header_size) / 2)
            + "!"
        )
        ln = len(top) - 2
        bottom = "!" + "_" * ln + "!"

        txts = ["!" + txt + " " * (ln - len(txt)) + "!" for txt in txts]

        body = "\n".join(i for i in txts)

        return ("{0}\n" "{1}\n" "{2}\n").format(top, body, bottom)

    def _print_EmptyNode(self, expr):
        return ""

    def _print_AnnotatedComment(self, expr):
        accel = self._print(expr.accel)
        txt = str(expr.txt)
        return "!${0} {1}\n".format(accel, txt)

    def _print_tuple(self, expr):
        if expr[0].rank > 0:
            raise NotImplementedError(
                " tuple with elements of rank > 0 is not implemented"
            )
        fs = ", ".join(self._print(f) for f in expr)
        return "[{0}]".format(fs)

    def _print_InhomogeneousTupleVariable(self, expr):
        fs = ", ".join(self._print(f) for f in expr)
        return "[{0}]".format(fs)

    def _print_Variable(self, expr):
        return self._print(expr.name)

    def _print_FunctionDefArgument(self, expr):
        var = expr.var
        return ", ".join(
            self._print(v) for v in self.scope.collect_all_tuple_elements(var)
        )

    def _print_FunctionCallArgument(self, expr):
        if expr.keyword and expr.keyword != "*args":
            keyword = expr.keyword.lstrip("*")
            return f"{keyword} = {self._print(expr.value)}"
        else:
            return self._print(expr.value)

    def _print_DottedVariable(self, expr):
        if isinstance(expr.lhs, FunctionCall):
            base = expr.lhs.funcdef.results.var
            var_name = self.scope.get_new_name()
            var = base.clone(var_name)

            self.scope.insert_variable(var)

            self._additional_code += self._print(Assign(var, expr.lhs)) + "\n"
            return self._print(var) + "%" + self._print(expr.name)
        else:
            return self._print(expr.lhs) + "%" + self._print(expr.name)

    def _print_DottedName(self, expr):
        return " % ".join(self._print(n) for n in expr.name)

    def _print_Lambda(self, expr):
        return '"{args} -> {expr}"'.format(args=expr.variables, expr=expr.expr)

    def _print_PythonReal(self, expr):
        value = self._print(expr.internal_var)
        return f"real({value})"

    def _print_PythonImag(self, expr):
        value = self._print(expr.internal_var)
        return f"aimag({value})"

    # ========================== String Methods ===============================#

    def _print_PythonStr(self, expr):
        return self._print(expr.args[0])

    # ======================================================================= #
    def _print_ArraySize(self, expr):
        init_value = self._print(expr.arg)
        prec = self.print_kind(expr)
        return f"size({init_value}, kind={prec})"

    def _print_ArrayShapeElement(self, expr):
        arg = expr.arg
        arg_code = self._print(arg)
        prec = self.print_kind(expr)

        if isinstance(arg.class_type, NumpyNDArrayType):
            if arg.rank == 1:
                return f"size({arg_code}, kind={prec})"

            if arg.order == "C":
                index = Minus(LiteralInteger(arg.rank), expr.index)
                index = self._print(index)
            else:
                index = Add(expr.index, LiteralInteger(1))
                index = self._print(index)

            return f"size({arg_code}, {index}, {prec})"

        elif isinstance(arg.class_type, StringType):
            return f"len({arg_code})"
        else:
            raise NotImplementedError(
                f"Don't know how to represent shape of object of type {arg.class_type}"
            )

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
        elif isinstance(dtype, FixedSizeType) and isinstance(
            expr_type, (NumpyNDArrayType, FixedSizeType)
        ):
            dtype_str = self._print(dtype.primitive_type)
            if isinstance(dtype, FixedSizeNumericType):
                dtype_str += f"({self.print_kind(var)})"

            if rank > 0:
                # arrays are 0-based in x2py, to avoid ambiguity with range
                start_val = self._print(LiteralInteger(0))

                if intent_in:
                    rankstr = ", ".join([f"{start_val}:"] * rank)
                elif is_static or on_stack:
                    ordered_shape = shape[::-1] if var.order == "C" else shape
                    ubounds = [
                        Minus(s, LiteralInteger(1))
                        for s in ordered_shape
                    ]
                    rankstr = ", ".join(
                        f"{start_val}:{self._print(u)}" for u in ubounds
                    )
                elif is_alias or on_heap:
                    rankstr = ", ".join(":" * rank)
                else:
                    raise NotImplementedError("Fortran rank string undetermined")
                rankstr = f"({rankstr})"

        elif isinstance(dtype, StringType):
            dtype_str = self._print(dtype)

            if intent_in:
                dtype_str += "(len = *)"
            else:
                dtype_str += "(len = :)"
        else:
            raise
            errors.report(
                f"Don't know how to print type {expr_type} in Fortran",
                symbol=expr,
                severity="fatal",
            )

        code_value = ""
        if expr.value:
            code_value = " = {0}".format(self._print(expr.value))

        vstr = self._print(expr.variable.name)

        # Default empty strings
        intentstr = ""
        allocatablestr = ""
        optionalstr = ""
        privatestr = ""
        externalstr = ""

        # Compute intent string
        if intent:
            if (
                intent == "in"
                and rank == 0
                and not is_optional
                and not isinstance(expr_type, CustomDataType)
            ):
                intentstr = ", value"
                if is_const:
                    intentstr += ", intent(in)"
            else:
                intentstr = f", intent({intent})"

        # Compute allocatable string
        if not is_static:
            if is_alias:
                allocatablestr = ", pointer"

            elif (
                on_heap
                and not intent_in
                and isinstance(
                    var.class_type, (NumpyNDArrayType, StringType)
                )
            ):
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
        if (
            expr.module_variable
            and not is_private
            and isinstance(expr.variable.class_type, FixedSizeNumericType)
        ):
            mod_str = ", bind(c)"

        # Construct declaration
        left = (
            dtype_str
            + allocatablestr
            + optionalstr
            + privatestr
            + externalstr
            + mod_str
            + intentstr
        )
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
            shape_code = "({s_c})".format(s_c=shape_code)

        code += "{lhs}{s_c} {op} {rhs}".format(
            lhs=self._print(expr.lhs), s_c=shape_code, op=op, rhs=self._print(expr.rhs)
        )

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
        code += "{0} = {1}".format(lhs_code, rhs_code)

        return code + "\n"

    # ------------------------------------------------------------------------------
    def _print_Allocate(self, expr):
        class_type = expr.variable.class_type
        if expr.alloc_type == "function":
            if isinstance(
                class_type, (NumpyNDArrayType, CustomDataType)
            ):
                if expr.status == "unallocated":
                    return ""
                elif expr.status == "unknown":
                    var_code = self._print(expr.variable)
                    return (
                        f"if (allocated({var_code})) then\n"
                        f"  deallocate({var_code})\n"
                        "end if\n"
                    )

                elif expr.status == "allocated":
                    var_code = self._print(expr.variable)
                    return f"deallocate({var_code})\n"

        if isinstance(
            class_type, (NumpyNDArrayType, CustomDataType)
        ):
            # Transpose indices because of Fortran column-major ordering
            if expr.variable.rank == 0:
                shape = ()
            else:
                shape = expr.shape if expr.order == "F" else expr.shape[::-1]

            var_code = self._print(expr.variable)
            size_code = ", ".join(self._print(i) for i in shape)
            shape_code = ", ".join(
                "0:" + self._print(Minus(i, LiteralInteger(1)))
                for i in shape
            )
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

        elif isinstance(class_type, (HomogeneousContainerType, StringType)):
            return ""

        else:
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
            else:
                return ""

        if var.is_alias:
            return ""
        elif isinstance(
            class_type, (NumpyNDArrayType, StringType)
        ):
            var_code = self._print(var)
            code = f"if (allocated({var_code})) deallocate({var_code})\n"
            return code
        else:
            raise
            errors.report(
                f"Deallocate not implemented for {class_type}",
                severity="error",
                symbol=expr,
            )
            return ""

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

    def _print_PythonNativeBool(self, expr):
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

    def _print_LiteralString(self, expr):
        if expr.python_value == "":
            return "''"
        sp_chars = ["\a", "\b", "\f", "\r", "\t", "\v", "'", "\n"]
        sub_str = ""
        formatted_str = []
        for c in expr.python_value:
            if c in sp_chars:
                if sub_str != "":
                    formatted_str.append(f"'{sub_str}'")
                    sub_str = ""
                formatted_str.append(f"ACHAR({ord(c)})")
            else:
                sub_str += c
        if sub_str != "":
            formatted_str.append(f"'{sub_str}'")
        return " // ".join(formatted_str)

    def _print_Interface(self, expr):
        interface_funcs = expr.functions

        example_func = interface_funcs[0]

        # ... we don't print 'hidden' functions
        if not example_func.is_semantic:
            return ""

        if example_func.results:
            if len(set(f.results.var.rank == 0 for f in interface_funcs)) != 1:
                message = (
                    "Fortran cannot yet handle a templated function returning either a scalar or an array. "
                    "If you are using the terminal interface, please pass --language c, "
                    "if you are using the interactive interfaces ex2py or lambdify, please pass language='c'. "
                    "See https://github.com/x2py/x2py/issues/1339 to monitor the advancement of this issue."
                )
                raise
                errors.report(message, severity="error", symbol=expr)

        name = self._print(expr.name)
        if all(isinstance(f, FunctionAddress) for f in interface_funcs):
            funcs = interface_funcs
        else:
            funcs = [
                f
                for f in interface_funcs
                if f
                is expr.point(
                    [
                        FunctionCallArgument(a.var.clone("arg_" + str(i)))
                        for i, a in enumerate(f.arguments)
                    ]
                )
            ]

        if expr.is_argument:
            funcs_sigs = []
            for f in funcs:
                self._constantImports.append({})
                parts = self.function_signature(f, f.name)
                parts = [
                    "{}({}) {}\n".format(
                        parts["sig"], parts["arg_code"], parts["func_end"]
                    ),
                    self.print_constant_imports() + "\n",
                    parts["arg_decs"],
                    "end {} {}\n".format(parts["func_type"], f.name),
                ]
                funcs_sigs.append("".join(a for a in parts))
                self._constantImports.pop()
            interface = (
                "interface\n" + "\n".join(a for a in funcs_sigs) + "end interface\n"
            )
            return interface

        if funcs[0].cls_name:
            cls_name = expr.cls_name
            if not (cls_name == "__UNDEFINED__"):
                name = "{0}_{1}".format(cls_name, name)
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
        out_args = [
            v
            for v in expr.scope.collect_all_tuple_elements(expr.results.var)
            if v and not v.is_argument
        ]
        args_decs = OrderedDict()
        arguments = expr.arguments
        class_arg = next((a for a in arguments if a.bound_argument), None)

        func_end = ""
        rec = "recursive " if expr.is_recursive else ""
        if len(out_args) != 1 or expr.results.var.rank > 0:
            func_type = "subroutine"
            for result in out_args:
                args_decs[result] = Declare(result, intent="out")

            functions = expr.functions

        else:
            # todo: if return is a function
            func_type = "function"
            result = out_args[0]
            functions = expr.functions

            func_end = "result({0})".format(result.name)

            args_decs[result] = Declare(result)
            out_args = []
        # ...

        for i, arg in enumerate(arguments):
            arg_var = arg.var
            if isinstance(arg_var, Variable):
                inout = arg.inout and not isinstance(arg_var, BindCVariable)
                for v in self.scope.collect_all_tuple_elements(arg_var):
                    if inout:
                        dec = Declare(v, intent="inout")
                    else:
                        dec = Declare(v, intent="in")
                    args_decs[v] = dec

        # treat case of pure function
        sig = "{0}{1} {2}".format(rec, func_type, name)
        if is_pure:
            sig = "pure {}".format(sig)

        # treat case of elemental function
        if is_elemental:
            sig = "elemental {}".format(sig)

        if class_arg:
            arg_iter = chain((class_arg,), out_args, arguments[1:])
        else:
            arg_iter = chain(out_args, arguments)
        arg_code = ", ".join(self._print(i) for i in arg_iter)

        arg_decs = "".join(self._print(i) for i in args_decs.values())

        parts = {
            "sig": sig,
            "arg_code": arg_code,
            "func_end": func_end,
            "arg_decs": arg_decs,
            "func_type": func_type,
        }
        return parts

    def _print_FunctionDef(self, expr):
        if not expr.is_semantic:
            return ""
        self.set_scope(expr.scope)

        for r in expr.scope.collect_all_tuple_elements(expr.results.var):
            if (
                r.rank
                and r.memory_handling == "stack"
                and any(not isinstance(s, LiteralInteger) for s in r.alloc_shape)
            ):
                raise
                errors.report(
                    "Can't return a stack array of unknown size",
                    symbol=r,
                    severity="error",
                )

        name = expr.cls_name or expr.name

        sig_parts = self.function_signature(expr, name)
        bind_c = " bind(c)" if isinstance(expr, BindCFunctionDef) else ""
        prelude = sig_parts.pop("arg_decs")
        functions = [f for f in expr.functions if f.is_semantic]
        func_interfaces = "\n".join(self._print(i) for i in expr.interfaces)
        body_code = self._print(expr.body)
        docstring = self._print(expr.docstring) if expr.docstring else ""

        decs = [Declare(v) for v in expr.local_vars if not v.is_argument]
        self._get_external_declarations(decs)

        prelude += "".join(self._print(i) for i in decs)
        if len(functions) > 0:
            functions_code = "\n".join(self._print(i) for i in functions)
            body_code = body_code + "\ncontains\n" + functions_code

        external_imports = [i for i in expr.imports if isinstance(i.source_module, FunctionDef) and i.source_module.is_external]
        imports          = [i for i in expr.imports if not i in external_imports]
        imports          = ''.join(self._print(i) for i in imports)
        external_imports = ''.join(self._print(i) for i in external_imports)

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

        aliases = []
        names = []
        methods = "".join(
            f"procedure :: {method.name} => {method.cls_name}\n"
            for method in expr.methods
            if method.is_semantic
        )
        for i in expr.interfaces:
            names = ",".join(f.cls_name for f in i.functions if f.is_semantic)
            if names:
                methods += f"generic, public :: {i.name} => {names}\n"
                methods += f"procedure :: {names}\n"

        self.exit_scope()

        sig = "type"
        if not (base is None):
            sig = "{0}, extends({1})".format(sig, base)

        docstring = self._print(expr.docstring) if expr.docstring else ""
        code = f"{sig} :: {name}\n{decs}\n"
        code = code + "contains\n" + methods
        decs = "".join([docstring, code, f"end type {name}\n"])

        sep = self._print(SeparatorComment(40))
        cls_methods = [i for i in expr.methods if i.is_semantic]
        for i in expr.interfaces:
            cls_methods += [j for j in i.functions if j.is_semantic]

        methods = "".join(
            "\n".join(["", sep, self._print(i), sep, ""]) for i in cls_methods
        )

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
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add(
                "c_associated"
            )
            return f"c_associated({lhs})"
        else:
            return f"present({lhs})"

    def _print_If(self, expr):
        # ...

        lines = []

        for i, (c, e) in enumerate(expr.blocks):

            if i == len(expr.blocks) - 1 and isinstance(c, LiteralTrue):
                lines.append("else\n")
            elif i == 0:
                lines.append(f"if ({self._print(c)}) then\n")
            else:
                lines.append("else if (%s) then\n" % self._print(c))

            if isinstance(e, (list, tuple)):
                lines.extend(self._print(ee) for ee in e)
            else:
                lines.append(self._print(e))

        if len(lines) == 0:
            return ""
        elif lines[0] == "else\n":
            lines = lines[1:]
        else:
            lines.append("end if\n")

        return "".join(lines)

    def _print_IfTernaryOperator(self, expr):

        cond = (
            PythonBool(expr.cond)
            if not isinstance(expr.cond.dtype.primitive_type, PrimitiveBooleanType)
            else expr.cond
        )
        value_true, value_false = self._apply_cast(
            expr.dtype, expr.value_true, expr.value_false
        )

        cond = self._print(cond)
        value_true = self._print(value_true)
        value_false = self._print(value_false)
        return "merge({true}, {false}, {cond})".format(
            cond=cond, true=value_true, false=value_false
        )

    def _print_Pow(self, expr):
        base = expr.args[0]
        e = expr.args[1]

        base_c = self._print(base)
        e_c = self._print(e)
        return "{} ** {}".format(base_c, e_c)

    def _print_Add(self, expr):
        if isinstance(expr.dtype, StringType):
            return " // ".join(self._print(a) for a in expr.args)
        else:
            args = [
                (
                    PythonInt(a)
                    if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                    else a
                )
                for a in expr.args
            ]
            return " + ".join(self._print(a) for a in args)

    def _print_Minus(self, expr):
        args = [
            (
                PythonInt(a)
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else a
            )
            for a in expr.args
        ]
        args_code = [self._print(a) for a in args]

        return " - ".join(args_code)

    def _print_Mul(self, expr):
        args = [
            (
                PythonInt(a)
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else a
            )
            for a in expr.args
        ]
        args_code = [self._print(a) for a in args]
        return " * ".join(a for a in args_code)

    def _print_Div(self, expr):
        if all(
            isinstance(
                a.dtype.primitive_type, (PrimitiveBooleanType, PrimitiveIntegerType)
            )
            for a in expr.args
        ):
            args = [NumpyFloat(a) for a in expr.args]
        else:
            args = expr.args
        return " / ".join(self._print(a) for a in args)

    def _print_Mod(self, expr):
        is_float = isinstance(expr.dtype.primitive_type, PrimitiveFloatingPointType)

        def correct_type_arg(a):
            if is_float and isinstance(a.dtype.primitive_type, PrimitiveIntegerType):
                return NumpyFloat(a)
            else:
                return a

        args = [self._print(correct_type_arg(a)) for a in expr.args]

        code = args[0]
        for c in args[1:]:
            code = "MODULO({},{})".format(code, c)
        return code

    def _print_FloorDiv(self, expr):
        new_args = [self._apply_cast(expr.dtype, arg) for arg in expr.args]
        args = [self._print(arg) for arg in new_args]
        if all(
            isinstance(
                arg.dtype.primitive_type, (PrimitiveBooleanType, PrimitiveIntegerType)
            )
            for arg in expr.args
        ):
            self.add_import(Import("pyc_math_f90", Module("pyc_math_f90", (), ())))
            return f"pyc_floor_div({args[0]}, {args[1]})"
        code = f"real(FLOOR({args[0]} / {args[1]}, {self.print_kind(expr)}), {self.print_kind(expr)})"
        return code

    def _print_And(self, expr):
        args = [
            (
                a
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else PythonBool(a)
            )
            for a in expr.args
        ]
        return " .and. ".join(self._print(a) for a in args)

    def _print_Or(self, expr):
        args = [
            (
                a
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else PythonBool(a)
            )
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
        elif lhs.class_type is rhs.class_type or (
            isinstance(lhs.class_type, FixedSizeNumericType)
            and isinstance(rhs.class_type, FixedSizeNumericType)
        ):
            return f"{lhs_code} == {rhs_code}"
        else:
            raise
            errors.report(X2PY_RESTRICTION_TODO, symbol=expr, severity="error")
            return ""

    def _print_Ne(self, expr):
        lhs, rhs = expr.args
        lhs_code = self._print(lhs)
        rhs_code = self._print(rhs)
        a = lhs.dtype.primitive_type
        b = rhs.dtype.primitive_type

        if all(isinstance(var, PrimitiveBooleanType) for var in (a, b)):
            return f"{lhs_code} .neqv. {rhs_code}"
        elif lhs.class_type is rhs.class_type or (
            isinstance(lhs.class_type, FixedSizeNumericType)
            and isinstance(rhs.class_type, FixedSizeNumericType)
        ):
            return f"{lhs_code} /= {rhs_code}"
        else:
            raise
            errors.report(X2PY_RESTRICTION_TODO, symbol=expr, severity="error")
            return ""

    def _print_Lt(self, expr):
        args = [
            (
                PythonInt(a)
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else a
            )
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return "{0} < {1}".format(lhs, rhs)

    def _print_Le(self, expr):
        args = [
            (
                PythonInt(a)
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else a
            )
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return "{0} <= {1}".format(lhs, rhs)

    def _print_Gt(self, expr):
        args = [
            (
                PythonInt(a)
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else a
            )
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return "{0} > {1}".format(lhs, rhs)

    def _print_Ge(self, expr):
        args = [
            (
                PythonInt(a)
                if isinstance(a.dtype.primitive_type, PrimitiveBooleanType)
                else a
            )
            for a in expr.args
        ]
        lhs = self._print(args[0])
        rhs = self._print(args[1])
        return "{0} >= {1}".format(lhs, rhs)

    def _print_Not(self, expr):
        a = self._print(expr.args[0])
        if not isinstance(expr.args[0].dtype.primitive_type, PrimitiveBooleanType):
            return "{} == 0".format(a)
        return ".not. {}".format(a)

    def _print_Header(self, expr):
        return ""

    def _print_LiteralImaginaryUnit(self, expr):
        """purpose: print complex numbers nicely in Fortran."""
        return "cmplx(0,1, kind = {})".format(self.print_kind(expr))

    def _print_int(self, expr):
        return str(expr)

    def _print_Literal(self, expr):
        printed = repr(expr.python_value)
        return "{}_{}".format(printed, self.print_kind(expr))

    def _print_LiteralTrue(self, expr):
        return ".True._{}".format(self.print_kind(expr))

    def _print_LiteralFalse(self, expr):
        return ".False._{}".format(self.print_kind(expr))

    def _print_LiteralComplex(self, expr):
        real_str = self._print(expr.real)
        imag_str = self._print(expr.imag)
        return "({}, {})".format(real_str, imag_str)

    def _print_IndexedElement(self, expr):
        base = expr.base
        if isinstance(base.class_type, TupleType):
            return self._print(self.scope.collect_tuple_element(expr))
        if not isinstance(base.class_type, NumpyNDArrayType):
            raise NotImplementedError(
                f"Fortran indexing is not implemented for {base.class_type}"
            )

        indices = list(expr.indices)
        if base.order != "F":
            indices.reverse()

        indices = [
            Slice(index.start, Minus(index.stop, LiteralInteger(1)), index.step)
            if isinstance(index, Slice)
            and index.stop is not None
            and not isinstance(index.stop, Nil)
            else index
            for index in indices
        ]
        return f"{self._print(base)}({', '.join(self._print(i) for i in indices)})"

    def _print_Slice(self, expr):
        if expr.start is None or isinstance(expr.start, Nil):
            start = ""
        else:
            start = self._print(expr.start)
        if (expr.stop is None) or isinstance(expr.stop, Nil):
            stop = ""
        else:
            stop = self._print(expr.stop)
        if expr.step is not None:
            return "{0}:{1}:{2}".format(start, stop, self._print(expr.step))
        return "{0}:{1}".format(start, stop)

    # =======================================================================================

    def _print_FunctionCall(self, expr):
        func = expr.funcdef

        f_name = self._print(
            expr.func_name if not expr.interface else expr.interface_name
        )

        if func.is_imported:
            f_name = self.scope.get_import_alias(func, "functions")
        elif expr.interface and expr.interface.is_imported:
            f_name = self.scope.get_import_alias(expr.interface, "functions")

        args = expr.args
        func_result_variables = (
            func.scope.collect_all_tuple_elements(func.results.var)
            if func.scope
            else [func.results.var]
        )
        out_results = [v for v in func_result_variables if v and not v.is_argument]
        parent_assign = get_direct_assignment(expr)
        is_function = len(out_results) == 1 and func.results.var.rank == 0

        if func.arguments and func.arguments[0].bound_argument:
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
            if len(out_results) == 1:
                lhs_vars = {out_results[0]: lhs}
            else:
                lhs_vars = dict(zip(out_results, lhs))
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
            if is_function:
                results_strs = []
            else:
                results_strs = [self._print(r) for r in lhs_vars.values()]

        else:
            results_strs = []
            results = None

        args_strs = [self._print(a) for a in args if not isinstance(a.value, Nil)]
        args_code = ", ".join(results_strs + args_strs)
        code = f"{f_name}({args_code})"
        if not is_function:
            code = f"call {code}\n"

        if not parent_assign:
            if is_function or len(out_results) == 0:
                return code
            else:
                self._additional_code += code
                if len(out_results) == 1:
                    return self._print(results[0])
                else:
                    return self._print(tuple(results))
        elif is_function:
            result_code = self._print(results[0])
            if isinstance(parent_assign, AliasAssign):
                return f"{result_code} => {code}\n"
            else:
                return f"{result_code} = {code}\n"
        else:
            return code

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
        else:
            return f"call C_F_Pointer({self._print(expr.c_pointer)}, {self._print(expr.f_array)})\n"

    # =======================================================================================

    def _print_PythonConjugate(self, expr):
        return "conjg( {} )".format(self._print(expr.internal_var))

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
            split = (
                lambda pos: (line[pos] in my_alnum and line[pos - 1] not in my_alnum)
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
                    (match.start(), match.end())
                    for match in re.compile("(\"[^\"]*\")|('[^']*')").finditer(line)
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
                    hunk += (
                        quote_trailing if pos in inside_quotes_positions else trailing
                    )

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
                        hunk += (
                            quote_trailing
                            if (pos + removed) in inside_quotes_positions
                            else trailing
                        )

                    if last_cut_was_inside_quotes:
                        hunk_start = tab_len * " " + "&"
                    elif startswith_omp:
                        hunk_start = tab_len * " " + "!$omp &"
                    elif startswith_acc:
                        hunk_start = tab_len * " " + "!$acc &"
                    else:
                        hunk_start = tab_len * " " + "      "

                    result.append(hunk_start + hunk)
                    last_cut_was_inside_quotes = (
                        pos + removed
                    ) in inside_quotes_positions
            else:
                result.append(line)

        # make sure that all lines end with a carriage return
        return [l if l.endswith("\n") else l + "\n" for l in result]

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

            line = "%s%s" % (padding, line)

            new_code.append(line)
            level += increase[i]

        return new_code

    def _print_BindCArrayVariable(self, expr):
        return self._print(expr.wrapper_function)

    def _print_BindCClassDef(self, expr):
        funcs = [
            expr.new_func,
            *expr.methods,
            *[f for i in expr.interfaces for f in i.functions],
            *[a.getter for a in expr.attributes],
            *[a.setter for a in expr.attributes if a.setter],
        ]
        sep = f"\n{self._print(SeparatorComment(40))}\n"
        return "", sep.join(self._print(f) for f in funcs)

    def _print_BindCSizeOf(self, expr):
        elem = self._print(expr.args[0])
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_size_t")
        return f"storage_size({elem}, kind = c_size_t)"

    def _print_AllDeclaration(self, expr):
        return ""

    def _print_KindSpecification(self, expr):
        return f"(kind = {self.print_kind(expr.type_specifier)})"
