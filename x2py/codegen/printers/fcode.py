"""Print to F90 standard. Trying to follow the information provided at
www.fortran90.org as much as possible."""

import re
import string
from collections import OrderedDict
from itertools import chain
from typing import ClassVar


from ..bind_c import (
    BindCNativeArrayHandleProperty,
    BindCFunctionDef,
    BindCModule,
    BindCModuleConstant,
    BindCPointer,
    BindCVariable,
    FortranTransfer,
)

from ..models.datatypes import cast_to, is_model_object
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
    Module,
    SeparatorComment,
    Slice,
)
from ..models.datatypes import (
    CustomDataType,
    FixedSizeNumericType,
    FixedSizeType,
    PrimitiveBooleanType,
    PrimitiveCharacterType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    Type,
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
    NumpyInt64Type,
    NumpyNDArrayType,
)
from ..models.core import (
    Add,
    Minus,
)

from ..models.core import Variable
from .codeprinter import CodePrinter
from x2py.semantics.ownership import CodegenAction, ownership_decision_for_codegen_variable

# TODO: add examples

__all__ = ["FCodePrinter"]


_FORTRAN_ACCESS_BY_CODEGEN_ACTION = {
    CodegenAction.DIRECT_VALUE: "read",
    CodegenAction.CALL_LOCAL_INPUT: "read",
    CodegenAction.IN_PLACE_ARGUMENT: "readwrite",
    CodegenAction.IDENTITY_OUTPUT: "write",
    CodegenAction.COPY_IN_OUT: "readwrite",
    CodegenAction.COPY_OUT: "write",
    CodegenAction.SNAPSHOT_COPY: "read",
    CodegenAction.BORROWED_VIEW: "read",
    CodegenAction.WRAPPER_INSTANCE: "write",
}


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
    "C_BOOL": "x2py_b1",
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

    printmethod = "_fcode"
    language = "Fortran"

    _default_settings: ClassVar = {
        "tabwidth": 2,
    }

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, filename, *, verbose, prefix_module=None):
        """Initialize the state used for one generation run."""
        super().__init__(verbose)
        self._constantImports = []

        self._additional_code = ""

        self.prefix_module = prefix_module

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    def _visit_Symbol(self, expr):
        """Render the ``Symbol`` model node."""
        return expr

    def _visit_Module(self, expr):
        """Render the ``Module`` model node."""
        self.set_scope(expr.scope)
        self._constantImports.append({})
        name = self._fortran_module_name(expr.name)

        imports = "".join(self._visit(i) for i in expr.imports)

        # Define declarations
        decs, class_decs_and_methods = self._module_declarations(expr)
        funcs_to_visit = self._module_functions(expr)

        # ...
        public_decs = self._module_public_declarations(expr, funcs_to_visit)

        # ...
        sep = self._visit(SeparatorComment(40))
        interfaces, interface_public_decs = self._module_interfaces(expr)
        public_decs += interface_public_decs

        body = self._module_body(expr, class_decs_and_methods, funcs_to_visit, sep)
        # ...

        has_routines = bool(funcs_to_visit or expr.classes or expr.overload_sets)
        private = "" if isinstance(expr, BindCModule) else "private\n" if has_routines else ""
        contains = "contains\n" if has_routines else ""
        imports += "".join(self._visit(i) for i in self._additional_imports.values())
        imports = self._constant_imports() + imports
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

    def _fortran_module_name(self, name):
        """Return the emitted Fortran module name."""
        name = self._visit(name).replace(".", "_")
        if not name.startswith("mod_") and self.prefix_module:
            return f"{self.prefix_module}_{name}"
        return name

    def _module_declarations(self, module):
        """Render module declarations and collect class method bodies."""
        class_parts = [self._visit(class_def) for class_def in module.classes]
        declarations = [
            declaration
            for declaration in module.declarations
            if not isinstance(declaration.variable, BindCModuleConstant)
        ]
        self._get_external_declarations(declarations)
        code = "\n".join(part[0] for part in class_parts)
        code += "".join(self._visit(declaration) for declaration in declarations)
        return code, class_parts

    @staticmethod
    def _module_functions(module):
        """Collect non-header procedures emitted in a module body."""
        candidates = [
            *module.funcs,
            *(function for interface in module.overload_sets for function in interface.functions),
        ]
        return [function for function in candidates if not function.is_header]

    @staticmethod
    def _module_public_declarations(module, functions):
        """Render public declarations for module-visible symbols."""
        if isinstance(module, BindCModule):
            return "private :: c_malloc\n"
        names = chain(
            (class_def.name for class_def in module.classes),
            (function.name for function in functions if not function.is_private and function.is_semantic),
            (
                variable.name
                for variable in module.variables
                if not variable.is_private and not isinstance(variable, BindCModuleConstant)
            ),
        )
        return "".join(f"public :: {name}\n" for name in names)

    def _module_interfaces(self, module):
        """Render module interfaces and their public declarations."""
        if isinstance(module, BindCModule):
            external_interfaces = self._bind_c_external_interfaces(module)
            code = (
                "interface\n"
                'function c_malloc(size) bind(C,name="x2py_malloc") result(ptr)\n'
                "use iso_c_binding\n"
                "integer(c_size_t), value :: size\n"
                "type(c_ptr) :: ptr\n"
                "end function c_malloc\n"
                f"{external_interfaces}"
                "end interface\n"
            )
            return code, ""
        code = "\n".join(self._visit(interface) for interface in module.overload_sets)
        public = "".join(
            f"public :: {interface.name}\n"
            for interface in module.overload_sets
            if interface.is_semantic and not interface.is_private
        )
        return code, public

    def _module_body(self, module, class_parts, functions, separator):
        """Render class, procedure, and variable-wrapper bodies."""
        blocks = [part[1] for part in class_parts]
        blocks.extend("".join((separator, self._visit(function), separator)) for function in functions)
        if isinstance(module, BindCModule):
            blocks.extend("".join((separator, self._visit(wrapper), separator)) for wrapper in module.variable_wrappers)
        return "\n".join(blocks)

    def _visit_BindCNativeArrayHandleVariable(self, expr):
        """Render generated native-array-handle operation functions."""
        return "\n".join(self._visit(function) for _name, function in expr.operation_function_items)

    def _visit_Import(self, expr):
        """Render the ``Import`` model node."""
        source = ""
        if expr.ignore:
            return ""

        source = expr.source
        if isinstance(source, Literal) and isinstance(source.dtype, StringType):
            source = source.python_value
        else:
            source = self._visit(source)

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
                    return self._visit(Declare(out_args[0].clone(source), external=True))
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
            elif isinstance(new_name, str):
                line = f"{prefix} {new_name}"

            else:
                raise TypeError(f"Expecting str, Symbol or AsName, given {type(i)}")

            code = (code + "\n" + line) if code else line

        # in some cases, the source is given as a string (when using metavar)
        code = code.replace("'", "")
        return code + "\n"

    def _visit_Comment(self, expr):
        """Render the ``Comment`` model node."""
        comments = self._visit(expr.text)
        return "!" + comments + "\n"

    def _visit_EmptyNode(self, expr):
        """Render the ``EmptyNode`` model node."""
        return ""

    def _visit_Variable(self, expr):
        """Render the ``Variable`` model node."""
        return self._visit(expr.name)

    def _visit_FunctionDefArgument(self, expr):
        """Render the ``FunctionDefArgument`` model node."""
        var = expr.var
        return ", ".join(self._visit(v) for v in self.scope.collect_all_tuple_elements(var))

    def _visit_FunctionCallArgument(self, expr):
        """Render the ``FunctionCallArgument`` model node."""
        if expr.keyword and expr.keyword != "*args":
            keyword = expr.keyword.lstrip("*")
            return f"{keyword} = {self._visit(expr.value)}"
        return self._visit(expr.value)

    def _visit_DottedVariable(self, expr):
        """Render the ``DottedVariable`` model node."""
        if isinstance(expr.lhs, FunctionCall):
            base = expr.lhs.funcdef.results.var
            var_name = self.scope.get_new_name()
            var = base.clone(var_name)

            self.scope.insert_variable(var)

            self._additional_code += self._visit(Assign(var, expr.lhs)) + "\n"
            return self._visit(var) + "%" + self._visit(expr.name)
        return self._visit(expr.lhs) + "%" + self._visit(expr.name)

    def _visit_Cast(self, expr):
        """Render the ``Cast`` model node."""
        value = self._visit(expr.arg)
        dtype = expr.dtype

        if isinstance(dtype, StringType):
            return value
        primitive_type = dtype.primitive_type
        if isinstance(primitive_type, PrimitiveBooleanType):
            return value if isinstance(expr.arg.dtype.primitive_type, PrimitiveBooleanType) else f"({value} /= 0)"

        kind = self._kind(dtype)
        if isinstance(primitive_type, PrimitiveIntegerType):
            return f"int({value}, kind={kind})"
        if isinstance(primitive_type, PrimitiveFloatingPointType):
            return f"real({value}, kind={kind})"
        if isinstance(primitive_type, PrimitiveComplexType):
            return f"cmplx({value}, kind={kind})"
        raise TypeError(f"Unsupported Fortran cast datatype {dtype}")

    # ======================================================================= #
    def _visit_ArraySize(self, expr):
        """Render the ``ArraySize`` model node."""
        init_value = self._visit(expr.arg)
        prec = self._kind(expr)
        if isinstance(expr.arg.class_type, StringType):
            return f"len({init_value}, kind={prec})"
        return f"size({init_value}, kind={prec})"

    def _visit_ArrayShapeElement(self, expr):
        """Render the ``ArrayShapeElement`` model node."""
        arg = expr.arg
        arg_code = self._visit(arg)
        prec = self._kind(expr)

        if isinstance(arg.class_type, NumpyNDArrayType):
            if arg.rank == 1:
                return f"size({arg_code}, kind={prec})"

            if arg.order == "C":
                index = Minus(convert_to_literal(arg.rank), expr.index)
                index = self._visit(index)
            else:
                index = Add(expr.index, convert_to_literal(1))
                index = self._visit(index)

            return f"size({arg_code}, {index}, {prec})"

        if isinstance(arg.class_type, StringType):
            return f"len({arg_code})"
        raise NotImplementedError(f"Don't know how to represent shape of object of type {arg.class_type}")

    def _visit_ArrayLowerBound(self, expr):
        """Render the ``ArrayLowerBound`` model node."""
        arg = expr.arg
        if not isinstance(arg.class_type, NumpyNDArrayType):
            raise NotImplementedError(f"Don't know how to represent lower bound of object of type {arg.class_type}")
        index = (
            Minus(convert_to_literal(arg.rank), expr.index)
            if arg.order == "C"
            else Add(expr.index, convert_to_literal(1))
        )
        return f"lbound({self._visit(arg)}, {self._visit(index)}, kind={self._kind(expr)})"

    def _visit_ArrayAllocated(self, expr):
        """Render the ``ArrayAllocated`` model node."""
        return f"allocated({self._visit(expr.arg)})"

    def _visit_ArrayAssociated(self, expr):
        """Render the ``ArrayAssociated`` model node."""
        return f"associated({self._visit(expr.arg)})"

    def _visit_ArrayContiguous(self, expr):
        """Render the ``ArrayContiguous`` model node."""
        return f"is_contiguous({self._visit(expr.arg)})"

    def _visit_Declare(self, expr):
        # ... ignored declarations
        """Render the ``Declare`` model node."""
        var = expr.variable
        expr_type = var.class_type
        if isinstance(expr_type, SymbolicType):
            return ""

        # meta-variables
        if isinstance(expr.variable, Variable) and expr.variable.name.startswith("__"):
            return ""
        # ...

        dtype = var.dtype
        rank = var.rank
        shape = var.alloc_shape
        is_optional = var.is_optional
        is_private = var.is_private
        is_alias = var.is_alias and not isinstance(dtype, BindCPointer)
        on_heap = var.on_heap
        on_stack = var.on_stack
        is_static = expr.static
        is_external = expr.external
        is_target = var.is_target and not var.is_alias
        by_value = expr.by_value
        accepts_assumed_length = var.is_argument and not getattr(var, "projected_output", False)
        deferred_string = (
            isinstance(dtype, StringType) and not accepts_assumed_length and (not shape or shape[0] is None)
        ) or self._is_deferred_character_array(var)
        # ...

        dtype_str, rankstr = self._fortran_declaration_type(
            var,
            expr_type,
            dtype,
            rank,
            shape,
            is_alias=is_alias,
            on_heap=on_heap,
            on_stack=on_stack,
            is_static=is_static,
            accepts_assumed_length=accepts_assumed_length,
        )

        code_value = ""
        if expr.value:
            code_value = f" = {self._visit(expr.value)}"

        vstr = self._visit(expr.variable.name)

        # Default empty strings
        intentstr = self._fortran_intent_attribute(expr.access, by_value)
        valuestr = self._fortran_value_attribute(by_value, rank, is_optional, expr_type)
        allocatablestr = self._fortran_allocation_attributes(
            is_static,
            is_alias,
            on_heap,
            expr_type,
            deferred_string,
            is_target,
        )
        optionalstr = ""
        privatestr = ""
        externalstr = ""

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
        left = dtype_str + allocatablestr + optionalstr + intentstr + privatestr + externalstr + mod_str + valuestr
        right = vstr + rankstr + code_value
        return f"{left} :: {right}\n"

    def _fortran_declaration_type(
        self,
        var,
        expr_type,
        dtype,
        rank,
        shape,
        *,
        is_alias,
        on_heap,
        on_stack,
        is_static,
        accepts_assumed_length,
    ):
        """Render a variable datatype and rank declaration."""
        if isinstance(expr_type, CustomDataType):
            return self._custom_declaration_type(var, expr_type), ""
        if isinstance(dtype, BindCPointer):
            self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_ptr")
            return "type(c_ptr)", ""
        if isinstance(dtype, FixedSizeType) and isinstance(expr_type, NumpyNDArrayType | FixedSizeType):
            if self._is_character_array(var):
                type_code = self._fortran_character_array_type(var, dtype, accepts_assumed_length)
            else:
                type_code = self._visit(dtype.primitive_type)
            if isinstance(dtype, FixedSizeNumericType):
                type_code += f"({self._kind(var)})"
            rank_code = self._fortran_rank_code(
                var,
                rank,
                shape,
                is_alias=is_alias,
                on_heap=on_heap,
                on_stack=on_stack,
                is_static=is_static,
                accepts_assumed_length=accepts_assumed_length,
            )
            return type_code, rank_code
        if isinstance(dtype, StringType):
            return self._fortran_string_type(dtype, shape, accepts_assumed_length), ""
        raise TypeError(f"Don't know how to print type {expr_type} in Fortran")

    def _custom_declaration_type(self, var, expr_type):
        """Render a derived-type declaration, including bound receivers."""
        signature = "type"
        if var.is_argument:
            argument = get_direct_function_argument(var)
            assert argument is not None
            if argument.bound_argument:
                signature = "class"
        return f"{signature}({self._visit(expr_type)})"

    def _fortran_rank_code(
        self,
        var,
        rank,
        shape,
        *,
        is_alias,
        on_heap,
        on_stack,
        is_static,
        accepts_assumed_length,
    ):
        """Render Fortran bounds for an array declaration."""
        if rank == 0:
            return ""
        start = self._visit(convert_to_literal(0))
        if is_alias or on_heap:
            dimensions = [":"] * rank
        elif accepts_assumed_length:
            dimensions = [f"{start}:"] * rank
        elif is_static or on_stack:
            ordered_shape = shape[::-1] if var.order == "C" else shape
            upper_bounds = [Minus(item, convert_to_literal(1)) for item in ordered_shape]
            dimensions = [f"{start}:{self._visit(bound)}" for bound in upper_bounds]
        else:
            raise NotImplementedError("Fortran rank string undetermined")
        return f"({', '.join(dimensions)})"

    def _fortran_string_type(self, dtype, shape, accepts_assumed_length):
        """Render a Fortran character type and length contract."""
        type_code = self._visit(dtype)
        if shape and shape[0] is not None:
            return f"{type_code}(len = {self._visit(shape[0])})"
        if accepts_assumed_length:
            return f"{type_code}(len = *)"
        return f"{type_code}(len = :)"

    @staticmethod
    def _is_character_array(var):
        """Return whether ``var`` stores fixed-width Fortran character elements."""
        return isinstance(var.class_type, NumpyNDArrayType) and isinstance(
            var.dtype.primitive_type, PrimitiveCharacterType
        )

    def _is_deferred_character_array(self, var):
        """Return whether ``var`` needs an allocatable deferred character length."""
        return self._is_character_array(var) and var.fortran_character_length == ":"

    def _fortran_character_array_type(self, var, dtype, accepts_assumed_length):
        """Render a Fortran character array element type and length contract."""
        type_code = self._visit(dtype.primitive_type)
        length = var.fortran_character_length
        if length == ":":
            return f"{type_code}(len = :)"
        if length is None:
            return f"{type_code}(len = *)" if accepts_assumed_length else type_code
        length_code = self._visit(length) if is_model_object(length) else self._visit(convert_to_literal(length))
        return f"{type_code}(len = {length_code})"

    @staticmethod
    def _fortran_value_attribute(by_value, rank, is_optional, expr_type):
        """Render the Fortran value ABI attribute for a declaration."""
        if by_value and rank == 0 and not is_optional and not isinstance(expr_type, CustomDataType):
            return ", value"
        return ""

    @staticmethod
    def _fortran_intent_attribute(access, by_value):
        """Render a Fortran INTENT attribute from declaration access metadata."""
        if by_value or access in (None, "unspecified"):
            return ""
        return {
            "read": ", intent(in)",
            "write": ", intent(out)",
            "readwrite": ", intent(inout)",
        }[access]

    @staticmethod
    def _fortran_allocation_attributes(is_static, is_alias, on_heap, expr_type, deferred_string, is_target):
        """Render pointer, allocatable, and target attributes."""
        if is_static:
            return ""
        if is_alias:
            attributes = ", pointer"
        elif (on_heap and isinstance(expr_type, NumpyNDArrayType | FixedSizeNumericType)) or deferred_string:
            attributes = ", allocatable"
        else:
            attributes = ""
        return f"{attributes}, target" if is_target else attributes

    def _visit_AliasAssign(self, expr):
        """Render the ``AliasAssign`` model node."""
        code = ""
        lhs = expr.lhs
        rhs = expr.rhs

        if isinstance(rhs, FunctionCall):
            return self._visit(rhs)

        # TODO improve
        op = "=>"
        shape_code = ""
        if isinstance(lhs.class_type, (NumpyNDArrayType)):
            shape_code = ", ".join("0:" for i in range(lhs.rank))
            shape_code = f"({shape_code})"

        code += f"{self._visit(expr.lhs)}{shape_code} {op} {self._visit(expr.rhs)}"

        return code + "\n"

    def _visit_CodeBlock(self, expr):
        """Render the ``CodeBlock`` model node."""
        body_exprs = expr.body
        body_stmts = []
        for b in body_exprs:
            line = self._visit(b)
            if self._additional_code:
                body_stmts.append(self._additional_code)
                self._additional_code = ""
            body_stmts.append(line)
        return "".join(body_stmts)

    def _visit_Assign(self, expr):
        """Render the ``Assign`` model node."""
        lhs = expr.lhs
        rhs = expr.rhs

        if isinstance(rhs, FunctionCall):
            return self._visit(rhs)

        lhs_code = self._visit(lhs)

        # Right-hand side code
        rhs_code = self._visit(rhs)

        code = ""
        code += f"{lhs_code} = {rhs_code}"

        return code + "\n"

    # ------------------------------------------------------------------------------
    def _visit_Allocate(self, expr):
        """Render the ``Allocate`` model node."""
        class_type = expr.variable.class_type
        if expr.alloc_type == "function" and isinstance(class_type, NumpyNDArrayType | CustomDataType):
            if expr.status == "unallocated":
                return ""
            if expr.status == "unknown":
                var_code = self._visit(expr.variable)
                return f"if (allocated({var_code})) then\n  deallocate({var_code})\nend if\n"

            if expr.status == "allocated":
                var_code = self._visit(expr.variable)
                return f"deallocate({var_code})\n"

        if isinstance(class_type, NumpyNDArrayType | CustomDataType):
            # Transpose indices because of Fortran column-major ordering
            shape = () if expr.variable.rank == 0 else expr.shape if expr.order == "F" else expr.shape[::-1]

            var_code = self._visit(expr.variable)
            size_code = ", ".join(self._visit(i) for i in shape)
            shape_code = ", ".join("0:" + self._visit(Minus(i, convert_to_literal(1))) for i in shape)
            if shape:
                shape_code = f"({shape_code})"
            type_spec = self._allocate_type_spec(expr.variable)
            code = ""

            if expr.status == "unallocated":
                code += f"allocate({type_spec}{var_code}{shape_code})\n"

            elif expr.status == "unknown":
                code += f"if (allocated({var_code})) then\n"
                code += f"  if (any(size({var_code}) /= [{size_code}])) then\n"
                code += f"    deallocate({var_code})\n"
                code += f"    allocate({type_spec}{var_code}{shape_code})\n"
                code += "  end if\n"
                code += "else\n"
                code += f"  allocate({type_spec}{var_code}{shape_code})\n"
                code += "end if\n"

            elif expr.status == "allocated":
                code += f"if (any(size({var_code}) /= [{size_code}])) then\n"
                code += f"  deallocate({var_code})\n"
                code += f"  allocate({type_spec}{var_code}{shape_code})\n"
                code += "end if\n"

            return code

        if isinstance(class_type, NumpyNDArrayType | StringType):
            return ""

        return self._visit_not_supported(expr)

    def _allocate_type_spec(self, var):
        """Render an allocation type spec for fixed-length character arrays."""
        if not self._is_character_array(var):
            return ""
        length = var.fortran_character_length
        if length in (None, ":"):
            return ""
        length_code = self._visit(length) if is_model_object(length) else self._visit(convert_to_literal(length))
        return f"character(len = {length_code}) :: "

    # -----------------------------------------------------------------------------
    def _visit_Deallocate(self, expr):
        """Render the ``Deallocate`` model node."""
        var = expr.variable
        class_type = var.class_type

        if isinstance(class_type, CustomDataType):
            x2py__del = expr.variable.cls_base.scope.find("__del__")
            if x2py__del:
                x2py_del_args = [FunctionCallArgument(var)]
                return self._visit(FunctionCall(x2py__del, x2py_del_args))
            return ""

        if var.is_alias:
            return ""
        if isinstance(class_type, NumpyNDArrayType | StringType):
            var_code = self._visit(var)
            return f"if (allocated({var_code})) deallocate({var_code})\n"
        raise NotImplementedError(f"Deallocate not implemented for {class_type}")

    def _visit_DeallocatePointer(self, expr):
        """Render the ``DeallocatePointer`` model node."""
        var_code = self._visit(expr.variable)
        return f"deallocate({var_code})\n"

    def _visit_Nullify(self, expr):
        """Render the ``Nullify`` model node."""
        return f"nullify({self._visit(expr.variable)})\n"

    # ------------------------------------------------------------------------------

    def _visit_PrimitiveBooleanType(self, expr):
        """Render the ``PrimitiveBooleanType`` model node."""
        return "logical"

    def _visit_PrimitiveIntegerType(self, expr):
        """Render the ``PrimitiveIntegerType`` model node."""
        return "integer"

    def _visit_PrimitiveFloatingPointType(self, expr):
        """Render the ``PrimitiveFloatingPointType`` model node."""
        return "real"

    def _visit_PrimitiveComplexType(self, expr):
        """Render the ``PrimitiveComplexType`` model node."""
        return "complex"

    def _visit_PrimitiveCharacterType(self, expr):
        """Render the ``PrimitiveCharacterType`` model node."""
        return "character"

    def _visit_StringType(self, expr):
        """Render the ``StringType`` model node."""
        return "character"

    def _visit_FortranCharacterLength(self, expr):
        """Render the Fortran element length intrinsic."""
        return f"len({self._visit(expr.arg)})"

    def _visit_CustomDataType(self, expr):
        """Render the ``CustomDataType`` model node."""
        while hasattr(expr, "underlying_type"):
            expr = expr.underlying_type
        try:
            name = self.scope.get_import_alias(expr, "cls_constructs")
        except RuntimeError:
            name = expr.low_level_name
        return name

    def _visit_FunctionAddress(self, expr):
        """Render the ``FunctionAddress`` model node."""
        return expr.name

    def _visit_FunctionDef(self, expr):
        """Render the ``FunctionDef`` model node."""
        if not expr.is_semantic:
            return ""
        self.set_scope(expr.scope)

        self._validate_fortran_function_results(expr)

        name = expr.cls_name or expr.name

        sig_parts = self._function_signature(expr, name)
        bind_c = " bind(c)" if isinstance(expr, BindCFunctionDef) else ""
        prelude = sig_parts.pop("arg_decs")
        functions = [f for f in expr.functions if f.is_semantic]
        func_interfaces = "\n".join(self._visit(i) for i in expr.overload_sets)
        body_code = self._visit(expr.body)
        docstring = self._visit(expr.docstring) if expr.docstring else ""

        decs = [Declare(v) for v in expr.local_vars if not v.is_argument]
        self._get_external_declarations(decs)

        prelude += "".join(self._visit(i) for i in decs)
        body_code = self._function_body_with_nested(body_code, functions)
        imports, external_imports = self._split_function_imports(expr.imports)

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

    @staticmethod
    def _validate_fortran_function_results(function) -> None:
        """Reject unknown-size stack arrays returned from Fortran."""
        if function.decorators.get("x2py_callback_adapter"):
            return
        for result in function.scope.collect_all_tuple_elements(function.results.var):
            unknown_stack_array = (
                result.rank
                and result.memory_handling == "stack"
                and any(not isinstance(shape, Literal) for shape in result.alloc_shape)
            )
            if unknown_stack_array:
                raise ValueError("Can't return a stack array of unknown size")

    def _function_body_with_nested(self, body_code, functions):
        """Append nested procedures to a function body."""
        if not functions:
            return body_code
        functions_code = "\n".join(self._visit(function) for function in functions)
        return body_code + "\ncontains\n" + functions_code

    def _split_function_imports(self, imports):
        """Render regular and external procedure imports separately."""
        external = [
            item for item in imports if isinstance(item.source_module, FunctionDef) and item.source_module.is_external
        ]
        regular = [item for item in imports if item not in external]
        return "".join(self._visit(item) for item in regular), "".join(self._visit(item) for item in external)

    def _visit_Return(self, expr):
        """Render the ``Return`` model node."""
        code = ""
        if expr.stmt:
            code += self._visit(expr.stmt)
        code += "return\n"
        return code

    def _visit_IsNot(self, expr):
        """Render the ``IsNot`` model node."""
        lhs, rhs = expr.args
        if rhs is NIL:
            return self._handle_not_none(self._visit(lhs), lhs)
        if lhs is NIL:
            return self._handle_not_none(self._visit(rhs), rhs)
        raise NotImplementedError(f"Fortran is-not printing is not implemented for {expr}")

    def _visit_If(self, expr):
        # ...

        """Render the ``If`` model node."""
        lines = []

        for i, (c, e) in enumerate(expr.blocks):
            if i == len(expr.blocks) - 1 and isinstance(c, Literal) and c.python_value is True:
                lines.append("else\n")
            elif i == 0:
                lines.append(f"if ({self._visit(c)}) then\n")
            else:
                lines.append(f"else if ({self._visit(c)}) then\n")

            if isinstance(e, list | tuple):
                lines.extend(self._visit(ee) for ee in e)
            else:
                lines.append(self._visit(e))

        if len(lines) == 0:
            return ""
        if lines[0] == "else\n":
            lines = lines[1:]
        else:
            lines.append("end if\n")

        return "".join(lines)

    def _visit_SelectCase(self, expr):
        """Render the ``SelectCase`` model node."""
        lines = [f"select case ({self._visit(expr.expr)})\n"]
        for section in expr.sections:
            if section.label is None:
                lines.append("case default\n")
            else:
                lines.append(f"case ({self._visit(section.label)})\n")
            lines.append(self._visit(section.body))
        lines.append("end select\n")
        return "".join(lines)

    def _visit_Add(self, expr):
        """Render the ``Add`` model node."""
        if isinstance(expr.dtype, StringType):
            return " // ".join(self._visit(a) for a in expr.args)
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        return " + ".join(self._visit(a) for a in args)

    def _visit_Minus(self, expr):
        """Render the ``Minus`` model node."""
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        args_code = [self._visit(a) for a in args]

        return " - ".join(args_code)

    def _visit_Mul(self, expr):
        """Render the ``Mul`` model node."""
        args = [
            (cast_to(a, NumpyInt64Type()) if isinstance(a.dtype.primitive_type, PrimitiveBooleanType) else a)
            for a in expr.args
        ]
        args_code = [self._visit(a) for a in args]
        return " * ".join(a for a in args_code)

    def _visit_Literal(self, expr):
        """Render the ``Literal`` model node."""
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
            return f"{value_code}_{self._kind(expr)}"
        if isinstance(primitive_type, PrimitiveComplexType):
            real = self._visit(Literal(value.real, dtype.element_type))
            imag = self._visit(Literal(value.imag, dtype.element_type))
            return f"({real}, {imag})"
        return f"{value!r}_{self._kind(expr)}"

    def _visit_IndexedElement(self, expr):
        """Render the ``IndexedElement`` model node."""
        base = expr.base
        if isinstance(base.class_type, TupleType):
            return self._visit(self.scope.collect_tuple_element(expr))
        if isinstance(base.class_type, StringType):
            if len(expr.indices) != 1 or isinstance(expr.indices[0], Slice):
                raise NotImplementedError("Fortran string indexing requires one index")
            index = self._visit(expr.indices[0])
            return f"{self._visit(base)}({index}:{index})"
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
        return f"{self._visit(base)}({', '.join(self._visit(i) for i in indices)})"

    def _visit_Slice(self, expr):
        """Render the ``Slice`` model node."""
        start = "" if expr.start is None or expr.start is NIL else self._visit(expr.start)
        stop = "" if expr.stop is None or expr.stop is NIL else self._visit(expr.stop)
        if expr.step is not None:
            return f"{start}:{stop}:{self._visit(expr.step)}"
        return f"{start}:{stop}"

    # =======================================================================================

    def _visit_FunctionCall(self, expr):
        """Render the ``FunctionCall`` model node."""
        func = expr.funcdef

        native_name = expr.overload_set.native_name_for(func) if expr.overload_set else ""
        if expr.overload_set and self._is_defined_operator(native_name):
            return self._defined_operator_call(expr, func, native_name)

        f_name = self._fortran_call_name(expr, func)

        args = expr.args
        func_result_variables = (
            func.scope.collect_all_tuple_elements(func.results.var) if func.scope else [func.results.var]
        )
        out_results = [v for v in func_result_variables if v and not v.is_argument]
        parent_assign = get_direct_assignment(expr)
        is_function = self._call_is_fortran_function(func, out_results, parent_assign)

        if func.arguments and func.arguments[0].bound_argument:
            f_name, args = self._bound_fortran_call(expr, func, args)

        if parent_assign:
            args, results, results_strs = self._assigned_fortran_call_arguments(
                args, out_results, parent_assign, is_function
            )

        else:
            results_strs = []
            results = None

        args_strs = [self._visit(a) for a in args if a.value is not NIL]
        args_code = ", ".join(results_strs + args_strs)
        code = f"{f_name}({args_code})"
        if not is_function:
            code = f"call {code}\n"

        return self._finalize_fortran_call(code, parent_assign, is_function, out_results, results)

    def _defined_operator_call(self, expr, function, native_name):
        """Render a defined operator call or its assignment."""
        arguments = expr.overload_set.native_arguments(function, expr.args)
        values = [self._visit(argument.value) for argument in arguments]
        token = self._defined_operator_token(native_name)
        if len(values) == 1:
            code = f".not. {values[0]}" if token == ".not." else f"{token}{values[0]}"
        else:
            code = f"{values[0]} {token} {values[1]}"
        parent_assign = get_direct_assignment(expr)
        if not parent_assign:
            return code
        assignment = "=>" if isinstance(parent_assign, AliasAssign) else "="
        return f"{self._visit(parent_assign.lhs)} {assignment} {code}\n"

    def _fortran_call_name(self, expr, function):
        """Resolve the emitted name for a Fortran call."""
        name = self._visit(expr.func_name if not expr.overload_set else expr.overload_set_name)
        if function.is_imported:
            return self.scope.get_import_alias(function, "functions")
        if expr.overload_set and expr.overload_set.is_imported:
            return self.scope.get_import_alias(expr.overload_set, "functions")
        return name

    @staticmethod
    def _call_is_fortran_function(function, out_results, parent_assign):
        """Return whether a call is emitted as a function expression."""
        is_function = len(out_results) == 1 and (
            function.results.var.rank == 0 or isinstance(function.results.var.class_type, StringType)
        )
        if len(out_results) == 1 and isinstance(function.results.var.class_type, NumpyNDArrayType):
            return parent_assign is not None or function.results.var.memory_handling in {"alias", "heap"}
        return is_function

    def _bound_fortran_call(self, expr, function, arguments):
        """Render a type-bound call receiver and remaining arguments."""
        bound_name = (
            expr.overload_set_name
            if expr.overload_set
            else (function.type_bound_name or function.scope.get_python_name(function.name))
        )
        function_name = self._visit(bound_name)
        class_variable = arguments[0].value
        remaining_arguments = arguments[1:]
        if not isinstance(class_variable, FunctionCall):
            return f"{self._visit(class_variable)} % {function_name}", remaining_arguments
        base = class_variable.funcdef.results.var
        variable = self.scope.get_temporary_variable(base)
        self._additional_code += self._visit(Assign(variable, class_variable)) + "\n"
        return f"{self._visit(variable)} % {function_name}", remaining_arguments

    def _assigned_fortran_call_arguments(self, arguments, out_results, parent_assign, is_function):
        """Prepare call arguments and result targets under assignment."""
        lhs = parent_assign.lhs
        lhs_vars = {out_results[0]: lhs} if len(out_results) == 1 else dict(zip(out_results, lhs, strict=False))
        assigned_arguments = []
        for argument in arguments:
            value = argument.value
            if value in lhs_vars.values():
                replacement = value.clone(self.scope.get_new_name())
                self.scope.insert_variable(replacement)
                self._additional_code += self._visit(Assign(replacement, value))
                value = replacement
            assigned_arguments.append(FunctionCallArgument(value, argument.keyword))
        results = list(lhs_vars.values())
        result_strings = [] if is_function else [self._visit(result) for result in results]
        return assigned_arguments, results, result_strings

    def _finalize_fortran_call(self, code, parent_assign, is_function, out_results, results):
        """Render final call or assignment syntax for a Fortran procedure."""
        if not parent_assign:
            if is_function or not out_results:
                return code
            self._additional_code += code
            if len(out_results) == 1:
                return self._visit(results[0])
            return self._visit(tuple(results))
        if not is_function:
            return code
        result_code = self._visit(results[0])
        assignment = "=>" if isinstance(parent_assign, AliasAssign) else "="
        return f"{result_code} {assignment} {code}\n"

    def _visit_CLocFunc(self, expr):
        """Render the ``CLocFunc`` model node."""
        lhs = self._visit(expr.result)
        rhs = self._visit(expr.arg)
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_loc")
        return f"{lhs} = c_loc({rhs})\n"

    def _visit_C_NULL_CHAR(self, expr):
        """Render the ``C_NULL_CHAR`` model node."""
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("C_NULL_CHAR")
        return "C_NULL_CHAR"

    def _visit_C_F_Pointer(self, expr):
        """Render the ``C_F_Pointer`` model node."""
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("C_F_Pointer")
        shape_tuple = expr.shape or ()
        shape = ", ".join(self._visit(s) for s in shape_tuple)
        if shape:
            return f"call C_F_Pointer({self._visit(expr.c_pointer)}, {self._visit(expr.f_array)}, [{shape}])\n"
        return f"call C_F_Pointer({self._visit(expr.c_pointer)}, {self._visit(expr.f_array)})\n"

    # =======================================================================================

    def _visit_BindCArrayVariable(self, expr):
        """Render the ``BindCArrayVariable`` model node."""
        return self._visit(expr.wrapper_function)

    def _visit_BindCClassDef(self, expr):
        """Render the ``BindCClassDef`` model node."""
        handle_operations = [
            function
            for attribute in expr.attributes
            if isinstance(attribute, BindCNativeArrayHandleProperty)
            for _name, function in attribute.operation_function_items
        ]
        funcs = [
            expr.new_func,
            *expr.methods,
            *[f for i in expr.overload_sets for f in i.functions],
            *[a.getter for a in expr.attributes if not isinstance(a, BindCNativeArrayHandleProperty)],
            *[a.setter for a in expr.attributes if not isinstance(a, BindCNativeArrayHandleProperty) and a.setter],
            *handle_operations,
        ]
        sep = f"\n{self._visit(SeparatorComment(40))}\n"
        return "", sep.join(self._visit(f) for f in funcs)

    def _visit_BindCSizeOf(self, expr):
        """Render the ``BindCSizeOf`` model node."""
        elem = self._visit(expr.args[0])
        self._constantImports[-1].setdefault("ISO_C_Binding", set()).add("c_size_t")
        return f"storage_size({elem}, kind = c_size_t)"

    def _visit_FortranTransfer(self, expr: FortranTransfer):
        """Render the ``FortranTransfer`` model node."""
        source = self._visit(expr.source)
        mold = self._visit(expr.mold)
        if expr.size is None:
            return f"transfer({source}, {mold})"
        size = self._visit(expr.size)
        return f"transfer({source}, {mold}, {size})"

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _constant_imports(self):
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

    def _bind_c_external_interfaces(self, expr):
        """Handle explicit external interfaces for the current generation context."""
        original_module = getattr(expr, "original_module", None)
        if original_module is None:
            return ""
        interfaces = [
            self._external_interface(func)
            for func in original_module.funcs
            if func.is_external and func.is_semantic and not func.is_private
        ]
        return "".join(interfaces)

    def _external_interface(self, func):
        """Emit an explicit interface for one external native procedure."""
        args = ", ".join(self._visit(arg.name) for arg in func.arguments)
        result_vars = [var for var in func.scope.collect_all_tuple_elements(func.results.var) if var]
        is_function = len(result_vars) == 1
        func_type = "function" if is_function else "subroutine"
        lines = [f"{func_type} {self._visit(func.name)}({args})", "import", "implicit none"]
        if is_function:
            lines.append(self._visit(Declare(result_vars[0].clone(str(func.name)))).rstrip())
        for arg in func.arguments:
            lines.append(self._external_interface_argument_declaration(arg.var))
        lines.append(f"end {func_type} {self._visit(func.name)}")
        return "\n".join(lines) + "\n"

    def _external_interface_argument_declaration(self, var):
        """Declare an external native argument without changing its call ABI."""
        if isinstance(var.class_type, StringType):
            return self._visit(Declare(var)).rstrip()
        if isinstance(var.class_type, CustomDataType):
            type_code = f"type({self._visit(var.class_type)})"
        elif isinstance(var.class_type, NumpyNDArrayType | FixedSizeType):
            type_code = self._visit(var.dtype.primitive_type)
            if isinstance(var.dtype, FixedSizeNumericType):
                type_code += f"({self._kind(var)})"
        else:
            raise TypeError(f"Unsupported external native argument type {var.class_type}")

        attributes = []
        if getattr(var, "is_optional", False):
            attributes.append("optional")
        attribute_code = f", {', '.join(attributes)}" if attributes else ""
        shape_code = ""
        if var.rank:
            dimensions = self._external_interface_argument_dimensions(var)
            shape_code = f"({', '.join(dimensions)})"
        return f"{type_code}{attribute_code} :: {var.name}{shape_code}"

    def _external_interface_argument_dimensions(self, var):
        """Return dimensions for an external interface without changing native ABI."""
        source_shape = tuple(getattr(var, "fortran_source_shape", ()) or ())
        if source_shape:
            if var.rank > 1 and str(source_shape[0]).strip() == "*":
                return ["*"]
            dimensions = []
            for index, item in enumerate(var.alloc_shape):
                source_dim = str(source_shape[index]).strip() if index < len(source_shape) else ""
                if source_dim:
                    dimensions.append(source_dim)
                elif item is None:
                    dimensions.append("*" if index == var.rank - 1 else ":")
                else:
                    dimensions.append(self._visit(item))
            return dimensions
        return [":" if item is None else self._visit(item) for item in var.alloc_shape]

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
        return self._wrap_fortran(self._indent_code(lines))

    def _kind(self, expr):
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

    def _function_signature(self, expr, name):
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
        out_args = [v for v in expr.scope.collect_all_tuple_elements(expr.results.var) if v and not v.is_argument]
        arguments = expr.arguments
        class_arg = next((a for a in arguments if a.bound_argument), None)
        callback_adapter = bool(expr.decorators.get("x2py_callback_adapter"))
        out_args, args_decs, func_type, func_end, callback_result = self._fortran_result_signature(
            expr, out_args, callback_adapter
        )
        callback_interfaces = self._fortran_argument_declarations(expr, arguments, callback_adapter, args_decs)
        if callback_result is not None:
            result, declaration = callback_result
            args_decs[result] = declaration

        sig = self._fortran_signature_prefix(expr, func_type, name)

        arg_iter = chain((class_arg,), out_args, arguments[1:]) if class_arg else chain(out_args, arguments)
        arg_code = ", ".join(self._visit(i) for i in arg_iter)

        arg_decs = "".join(self._visit(i) if isinstance(i, Declare) else i for i in args_decs.values())
        arg_decs = "".join(callback_interfaces) + arg_decs

        return {
            "sig": sig,
            "arg_code": arg_code,
            "func_end": func_end,
            "arg_decs": arg_decs,
            "func_type": func_type,
        }

    @staticmethod
    def _fortran_result_signature(function, out_args, callback_adapter):
        """Classify results and build their signature declarations."""
        declarations = OrderedDict()
        string_result = isinstance(function.results.var.class_type, StringType)
        uses_output_arguments = len(out_args) != 1 or (
            function.results.var.rank > 0 and not string_result and not callback_adapter
        )
        if uses_output_arguments:
            for result in out_args:
                declarations[result] = Declare(result, access="write")
            return out_args, declarations, "subroutine", "", None
        result = out_args[0]
        declaration = Declare(result)
        callback_result = (result, declaration) if callback_adapter else None
        if callback_result is None:
            declarations[result] = declaration
        return [], declarations, "function", f"result({result.name})", callback_result

    def _fortran_argument_declarations(self, function, arguments, callback_adapter, declarations):
        """Populate argument declarations and callback interfaces."""
        callback_interfaces = []
        bind_c_function = isinstance(function, BindCFunctionDef)
        callback_c_abi_function = bool(function.decorators.get("x2py_callback_abi"))
        for argument in arguments:
            variable = argument.var
            if isinstance(variable, Variable):
                if callback_adapter:
                    declarations[variable] = self._callback_native_argument_declaration(variable)
                    continue
                is_c_abi_argument = isinstance(variable, BindCVariable) or callback_c_abi_function
                for element in self.scope.collect_all_tuple_elements(variable):
                    by_value = self._fortran_argument_passes_by_value(
                        element,
                        bind_c_function=bind_c_function,
                        c_abi_argument=is_c_abi_argument,
                    )
                    declarations[element] = Declare(
                        element,
                        access=self._fortran_argument_access(element) if bind_c_function else None,
                        by_value=by_value,
                    )
            elif isinstance(variable, FunctionAddress) and variable.decorators.get("x2py_callback_abi"):
                callback_interfaces.append(self._callback_c_interface(variable))
        return callback_interfaces

    @staticmethod
    def _fortran_argument_passes_by_value(var, *, bind_c_function, c_abi_argument):
        """Return whether a Fortran declaration needs the C ``value`` ABI attribute."""
        if var.rank != 0 or var.is_optional or isinstance(var.class_type, CustomDataType):
            return False
        if c_abi_argument or getattr(var, "passes_by_value", False):
            return True
        return (
            bind_c_function
            and var.memory_handling == "stack"
            and isinstance(
                var.class_type,
                FixedSizeType | BindCPointer,
            )
        )

    @staticmethod
    def _fortran_argument_access(var):
        """Derive bridge declaration access from completed ownership policy."""
        try:
            action = ownership_decision_for_codegen_variable(var).codegen_action
        except ValueError:
            return None
        return _FORTRAN_ACCESS_BY_CODEGEN_ACTION.get(action)

    @staticmethod
    def _fortran_callback_intent_attribute(access, by_value):
        """Render callback adapter INTENT without hiding value input intent."""
        if by_value:
            if access in {"write", "readwrite"}:
                raise ValueError("Fortran VALUE callback arguments cannot have output or readwrite access")
            return ", intent(in)"
        if access in (None, "unspecified"):
            return ""
        return {
            "read": ", intent(in)",
            "write": ", intent(out)",
            "readwrite": ", intent(inout)",
        }[access]

    @staticmethod
    def _fortran_signature_prefix(function, func_type, name):
        """Render recursive, pure, and elemental signature prefixes."""
        signature = f"{'recursive ' if function.is_recursive else ''}{func_type} {name}"
        if function.is_pure:
            signature = f"pure {signature}"
        if function.is_elemental:
            signature = f"elemental {signature}"
        return signature

    def _callback_native_argument_declaration(self, var):
        """Declare an internal callback adapter argument with its native Fortran ABI."""
        if isinstance(var.class_type, StringType):
            type_code = self._callback_character_type(var)
        elif isinstance(var.class_type, CustomDataType):
            type_code = f"type({self._visit(var.class_type)})"
        elif isinstance(var.class_type, NumpyNDArrayType | FixedSizeType):
            type_code = self._visit(var.dtype.primitive_type)
            if isinstance(var.dtype, FixedSizeNumericType):
                type_code += f"({self._kind(var)})"
        else:
            raise TypeError(f"Unsupported native callback argument type {var.class_type}")

        shape_code = ""
        if var.rank and not isinstance(var.class_type, StringType):
            dimensions = [":" if item is None else self._visit(item) for item in var.alloc_shape]
            shape_code = f"({', '.join(dimensions)})"
        access = getattr(var, "fortran_callback_access", None) or "read"
        by_value = getattr(var, "passes_by_value", False)
        intent_code = self._fortran_callback_intent_attribute(access, by_value=by_value)
        value_code = self._fortran_value_attribute(by_value, var.rank, var.is_optional, var.class_type)
        return f"{type_code}{intent_code}{value_code} :: {var.name}{shape_code}\n"

    def _callback_character_type(self, var):
        """Render the character type for a callback adapter dummy."""
        length = var.fortran_character_length
        if length in (None, "*", ":") and var.alloc_shape and var.alloc_shape[0] is not None:
            length = var.alloc_shape[0]
        if length in (None, "*", ":"):
            return "character(len = *)"
        length_code = self._visit(length) if is_model_object(length) else self._visit(convert_to_literal(length))
        return f"character(len = {length_code})"

    def _callback_c_interface(self, callback):
        """Emit the interoperable interface for a C callback dummy procedure."""
        parts = self._function_signature(callback, callback.name)
        signature = f"{parts['sig']}({parts['arg_code']}) bind(c) {parts['func_end']}".rstrip()
        return (
            "interface\n"
            f"{signature}\n"
            "import\n"
            f"{parts['arg_decs']}"
            f"end {parts['func_type']} {callback.name}\n"
            "end interface\n"
        )

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

    @staticmethod
    def _is_defined_operator(name):
        """Return whether is defined operator."""
        return re.fullmatch(r"operator\(.+\)", re.sub(r"\s+", "", str(name)), re.IGNORECASE) is not None

    @staticmethod
    def _defined_operator_token(name):
        """Handle defined operator token for the current generation context."""
        compact = re.sub(r"\s+", "", str(name))
        return compact[compact.index("(") + 1 : -1]

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

    def _indent_code(self, code):
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
            code_lines = self._indent_code(code.splitlines(True))
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
