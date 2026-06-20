"""Functions for printing C++ code."""

from itertools import chain
from typing import ClassVar

from ..models.core import (
    AsName,
    Declare,
    Import,
    Module,
    get_direct_module,
)
from ..models.datatypes import (
    FinalType,
    PrimitiveBooleanType,
    PrimitiveComplexType,
    PrimitiveFloatingPointType,
    PrimitiveIntegerType,
    StringType,
    Literal,
    NIL,
)
from ..models.datatypes import NumpyFloat64Type, cast_to
from ..models.core import Variable
from .codeprinter import CodePrinter

cpp_imports = {
    n: Import(n, Module(n, (), ()))
    for n in [
        "cassert",
        "complex",
        "cmath",
        "iostream",
        "pyc_math_cpp",
        "cstdint",
        "string",
    ]
}

# dictionary mapping Math function to (argument_conditions, C_function).
# Used in CppCodePrinter._visit_MathFunctionBase(self, expr)
# Math function ref https://docs.python.org/3/library/math.html
math_function_to_cpp = {
    # ---------- Number-theoretic and representation functions ------------
    "MathCeil": "ceil",
    # 'MathComb'   : TODO
    "MathCopysign": "copysign",
    "MathFabs": "fabs",
    "MathFloor": "floor",
    # 'MathFmod'   : TODO
    # 'MathRexp'   : TODO
    # 'MathFsum'   : TODO
    # 'MathIsclose' : TODO
    "MathIsfinite": "isfinite",
    "MathIsinf": "isinf",
    "MathIsnan": "isnan",
    # 'MathIsqrt'  : TODO
    "MathLdexp": "ldexp",
    # 'MathModf'  : TODO
    # 'MathPerm'  : TODO
    # 'MathProd'  : TODO
    "MathRemainder": "remainder",
    "MathTrunc": "trunc",
    # ----------------- Power and logarithmic functions -----------------------
    "MathExp": "exp",
    "MathExpm1": "expm1",
    "MathLog": "log",  # take also an option arg [base]
    "MathLog1p": "log1p",
    "MathLog2": "log2",
    "MathLog10": "log10",
    "MathPow": "pow",
    "MathSqrt": "sqrt",
    # --------------------- Trigonometric functions ---------------------------
    "MathAcos": "acos",
    "MathAsin": "asin",
    "MathAtan": "atan",
    "MathAtan2": "atan2",
    "MathCos": "cos",
    # 'MathDist'  : '???'
    "MathHypot": "hypot",
    "MathSin": "sin",
    "MathTan": "tan",
    # -------------------------- Hyperbolic functions -------------------------
    "MathAcosh": "acosh",
    "MathAsinh": "asinh",
    "MathAtanh": "atanh",
    "MathCosh": "cosh",
    "MathSinh": "sinh",
    "MathTanh": "tanh",
    # --------------------------- Special functions ---------------------------
    "MathErf": "erf",
    "MathErfc": "erfc",
    "MathGamma": "tgamma",
    "MathLgamma": "lgamma",
    # --------------------------- internal functions --------------------------
    "MathFactorial": "pyc_factorial",
    "MathGcd": "pyc_gcd",
    "MathDegrees": "pyc_degrees",
    "MathRadians": "pyc_radians",
    "MathLcm": "pyc_lcm",
    # --------------------------- cmath functions --------------------------
    "CmathAcos": "cacos",
    "CmathAcosh": "cacosh",
    "CmathAsin": "casin",
    "CmathAsinh": "casinh",
    "CmathAtan": "catan",
    "CmathAtanh": "catanh",
    "CmathCos": "ccos",
    "CmathCosh": "ccosh",
    "CmathExp": "cexp",
    "CmathSin": "csin",
    "CmathSinh": "csinh",
    "CmathSqrt": "csqrt",
    "CmathTan": "ctan",
    "CmathTanh": "ctanh",
}

cpp_library_headers = {
    "complex",
    "cmath",
    "inttypes",
    "iostream",
    "string",
}


class CppCodePrinter(CodePrinter):
    """
    A printer for printing code in C++.

    A printer to convert X2py's AST to strings of C++ code.
    As for all printers the navigation of this file is done via _visit_X
    functions.

    Parameters
    ----------
    filename : str
            The name of the file being converted.
    verbose : int
        The level of verbosity.
    """

    printmethod = "_cppcode"
    language = "C++"

    _default_settings: ClassVar = {
        "tabwidth": 4,
    }

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, filename, *, verbose):
        """Initialize the state used for one generation run."""
        super().__init__(verbose)

        self._additional_imports = {}
        self._additional_code = ""
        self._in_header = False

        # A set describing the variables that have been declared
        # in the scope.
        self._declared_vars: list[set[Variable]] = []

    def set_scope(self, scope):
        """
        Set the current scope.

        Set the current scope and create a new set of all variables that
        have been declared in this scope. This allows variables to be
        declared at their first usage.

        Parameters
        ----------
        scope : Scope
            The current scope.
        """
        self._declared_vars.append(set())
        super().set_scope(scope)

    def exit_scope(self):
        """
        Exit the current scope and return to the enclosing scope.

        Exit the current scope and return to the enclosing scope.
        """
        super().exit_scope()
        self._declared_vars.pop()

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    def _visit_ModuleHeader(self, expr):
        """Render the ``ModuleHeader`` model node."""
        name = expr.module.name
        self.set_scope(expr.module.scope)
        self._in_header = True

        decls = [Declare(v, external=True, module_variable=True) for v in expr.module.variables if not v.is_private]
        global_variables = "".join(self._visit(d) for d in decls)

        classes = "\n".join(self._visit(classDef) for classDef in expr.module.classes)

        funcs = "\n".join(f"{self._function_signature(f)};" for f in expr.module.funcs if not f.is_inline)

        # Print imports last to be sure that all additional_imports have been collected
        imports = [i for i in chain(expr.module.imports, self._additional_imports.values()) if not i.ignore]
        # imports = self.sort_imports(imports)
        imports = "".join(self._visit(i) for i in imports)

        self.exit_scope()
        self._in_header = False

        sections = (
            "#pragma once\n",
            imports,
            f"namespace {name} {{\n",
            global_variables,
            classes,
            funcs,
            "}\n",
        )

        return "\n".join(s for s in sections if s)

    def _visit_Module(self, expr):
        """Render the ``Module`` model node."""
        self.set_scope(expr.scope)
        name = expr.name

        global_variables = "".join([self._visit(d) for d in expr.declarations])
        body = "".join(self._visit(i) for i in expr.body)

        # Print imports last to be sure that all additional_imports have been collected
        imports = Import(self.scope.get_python_name(expr.name), Module(expr.name, (), ()))
        imports_code = self._visit(imports)
        if "complex" in self._additional_imports:
            imports_code += "using namespace std::complex_literals;\n"

        self.exit_scope()

        return "".join((imports_code, f"namespace {name} {{\n\n", global_variables, body, "\n}\n"))

    def _visit_Program(self, expr):
        """Render the ``Program`` model node."""
        mod = get_direct_module(expr)
        assert mod is not None
        name = mod.name
        self.set_scope(expr.scope)
        body = self._visit(expr.body)
        variables = self.scope.variables.values()
        decs = "".join(self._visit(Declare(v)) for v in variables if v not in self._declared_vars[-1])

        imports = [i for i in chain(expr.imports, self._additional_imports.values()) if not i.ignore]
        imports = "".join(self._visit(i) for i in imports)
        if "complex" in self._additional_imports:
            imports += "using namespace std::complex_literals;\n"
        self.exit_scope()
        return "".join(
            (
                imports,
                f"using namespace {name};\n\n",
                "int main()\n{\n",
                decs,
                body,
                "return 0;\n}",
            )
        )

    def _visit_FunctionDef(self, expr):
        """Render the ``FunctionDef`` model node."""
        if expr.is_inline:
            return ""

        self.set_scope(expr.scope)

        body = self._visit(expr.body)

        self.exit_scope()

        return "".join(
            (
                self._function_signature(expr),
                " {\n",
                self._indent_codestring(body),
                "}\n",
            )
        )

    def _visit_CodeBlock(self, expr):
        """Render the ``CodeBlock`` model node."""
        body_exprs = expr.body
        body_code = ""
        for b in body_exprs:
            code = self._visit(b)
            code = self._additional_code + code
            self._additional_code = ""
            body_code += code
        return body_code

    def _visit_Assign(self, expr):
        """Render the ``Assign`` model node."""
        lhs = expr.lhs

        prefix = ""
        if lhs in self.scope.variables.values() and lhs not in self._declared_vars[-1]:
            prefix = self._get_declare_type(lhs) + " "
            self._declared_vars[-1].add(lhs)

        lhs_code = self._visit(lhs)
        rhs_code = self._visit(expr.rhs)
        return f"{prefix}{lhs_code} = {rhs_code};\n"

    # ------------------------------
    #  Ternary operator
    # ------------------------------

    def _visit_IfTernaryOperator(self, expr):
        """
        Python: a if cond else b
        C++:    (cond ? a : b)
        """
        c = self._visit(expr.cond)
        a = self._visit(expr.value_true)
        b = self._visit(expr.value_false)
        return f"({c} ? {a} : {b})"

    # ------------------------------
    #  Arithmetic operators
    # ------------------------------

    def _visit_Add(self, expr):
        """Render the ``Add`` model node."""
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._visit(a))
        b_code = self._cast_to(b, target_dtype).format(self._visit(b))
        return f"{a_code} + {b_code}"

    def _visit_Minus(self, expr):
        """Render the ``Minus`` model node."""
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._visit(a))
        b_code = self._cast_to(b, target_dtype).format(self._visit(b))
        return f"{a_code} - {b_code}"

    def _visit_Mul(self, expr):
        """Render the ``Mul`` model node."""
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._visit(a))
        b_code = self._cast_to(b, target_dtype).format(self._visit(b))
        return f"{a_code} * {b_code}"

    def _visit_Div(self, expr):
        """Render the ``Div`` model node."""
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._visit(a))
        b_code = self._cast_to(b, target_dtype).format(self._visit(b))
        return f"{a_code} / {b_code}"

    def _visit_FloorDiv(self, expr):
        # the result type of the floor division is dependent on the arguments
        # type, if all arguments are integers or booleans the result is integer
        # otherwise the result type is float
        """Render the ``FloorDiv`` model node."""
        need_to_cast = all(
            a.dtype.primitive_type in (PrimitiveIntegerType(), PrimitiveBooleanType()) for a in expr.args
        )
        if need_to_cast:
            self.add_import(cpp_imports["pyc_math_cpp"])
            return f"py_floor_div({self._visit(expr.args[0])}, {self._visit(expr.args[1])})"

        self.add_import(cpp_imports["cmath"])
        code = " / ".join(
            self._visit(a if a.dtype.primitive_type is PrimitiveFloatingPointType() else cast_to(a, NumpyFloat64Type()))
            for a in expr.args
        )
        return f"std::floor({code})"

    def _visit_Mod(self, expr):
        """Render the ``Mod`` model node."""
        self.add_import(cpp_imports["pyc_math_cpp"])
        target_dtype = expr.dtype
        n, base = expr.args
        n_code = self._cast_to(n, target_dtype).format(self._visit(n))
        base_code = self._cast_to(base, target_dtype).format(self._visit(base))
        return f"pyc_modulo({n_code}, {base_code})"

    def _visit_Pow(self, expr):
        """Render the ``Pow`` model node."""
        self.add_import(cpp_imports["cmath"])
        base, exponent = expr.args
        base_code = self._visit(base)
        exponent_code = self._visit(exponent)

        dtype = expr.dtype

        try:
            exponent_is_pos_int = exponent.dtype.primitive_type is PrimitiveIntegerType() and exponent > 0
        except TypeError:
            exponent_is_pos_int = False

        if base == 2 and exponent_is_pos_int:
            code = f"2 << {exponent_code}"
            current_dtype = exponent.dtype
        else:
            code = f"std::pow({base_code}, {exponent_code})"
            current_dtype = (
                dtype
                if dtype.primitive_type not in (PrimitiveIntegerType(), PrimitiveBooleanType())
                else NumpyFloat64Type()
            )

        if current_dtype != dtype:
            return f"({self._visit(dtype)})({code})"
        return code

    # ------------------------------
    #  Unary operators
    # ------------------------------

    def _visit_UnaryPlus(self, expr):
        """Render the ``UnaryPlus`` model node."""
        return f"+{self._visit(expr.args[0])}"

    def _visit_UnarySub(self, expr):
        """Render the ``UnarySub`` model node."""
        return f"-{self._visit(expr.args[0])}"

    def _visit_Not(self, expr):
        """Render the ``Not`` model node."""
        return f"!({self._visit(expr.args[0])})"

    def _visit_Invert(self, expr):
        # Bitwise invert (~)
        """Render the ``Invert`` model node."""
        return f"~({self._visit(expr.args[0])})"

    # ------------------------------
    #  Logical operators
    # ------------------------------

    def _visit_And(self, expr):
        """Render the ``And`` model node."""
        return " && ".join(self._visit(a) for a in expr.args)

    def _visit_Or(self, expr):
        """Render the ``Or`` model node."""
        return " || ".join(self._visit(a) for a in expr.args)

    # ------------------------------
    #  Comparison operators
    # ------------------------------

    def _visit_Eq(self, expr):
        """Render the ``Eq`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} == {self._visit(b)}"

    def _visit_Ne(self, expr):
        """Render the ``Ne`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} != {self._visit(b)}"

    def _visit_Gt(self, expr):
        """Render the ``Gt`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} > {self._visit(b)}"

    def _visit_Ge(self, expr):
        """Render the ``Ge`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} >= {self._visit(b)}"

    def _visit_Lt(self, expr):
        """Render the ``Lt`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} < {self._visit(b)}"

    def _visit_Le(self, expr):
        """Render the ``Le`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} <= {self._visit(b)}"

    # ------------------------------
    #  Bitwise operators
    # ------------------------------

    def _visit_BitAnd(self, expr):
        """Render the ``BitAnd`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} & {self._visit(b)}"

    def _visit_BitOr(self, expr):
        """Render the ``BitOr`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} | {self._visit(b)}"

    def _visit_BitXor(self, expr):
        """Render the ``BitXor`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} ^ {self._visit(b)}"

    # ------------------------------
    #  Bit shifts
    # ------------------------------

    def _visit_LShift(self, expr):
        """Render the ``LShift`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} << {self._visit(b)}"

    def _visit_RShift(self, expr):
        """Render the ``RShift`` model node."""
        a, b = expr.args
        return f"{self._visit(a)} >> {self._visit(b)}"

    # ------------------------------
    #  Parentheses
    # ------------------------------

    def _visit_AssociativeParenthesis(self, expr):
        """Render the ``AssociativeParenthesis`` model node."""
        return f"({self._visit(expr.args[0])})"

    # ------------------------------
    #  Casts
    # ------------------------------

    def _visit_Cast(self, expr):
        """Render the ``Cast`` model node."""
        value = self._visit(expr.arg)
        type_name = self._visit(expr.dtype)
        return f"static_cast<{type_name}>({value})"

    # ------------------------------
    #  Types
    # ------------------------------

    def _visit_NumpyBoolType(self, expr):
        """Render the ``NumpyBoolType`` model node."""
        return "bool"

    def _visit_NumpyInt64Type(self, expr):
        """Render the ``NumpyInt64Type`` model node."""
        self.add_import(cpp_imports["cstdint"])
        return "int64_t"

    def _visit_NumpyFloat64Type(self, expr):
        """Render the ``NumpyFloat64Type`` model node."""
        return "double"

    def _visit_NumpyComplex128Type(self, expr):
        """Render the ``NumpyComplex128Type`` model node."""
        self.add_import(cpp_imports["complex"])
        return "std::complex<double>"

    def _visit_StringType(self, expr):
        """Render the ``StringType`` model node."""
        self.add_import(cpp_imports["string"])
        return "std::string"

    def _visit_NumpyFloat32Type(self, expr):
        """Render the ``NumpyFloat32Type`` model node."""
        return "float"

    # ------------------------------
    #  Mathematical functions
    # ------------------------------

    # ------------------------------
    #  Literals
    # ------------------------------

    def _visit_Literal(self, expr):
        """Render the ``Literal`` model node."""
        value = expr.python_value
        dtype = expr.dtype

        if expr is NIL:
            return "nullptr"
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
            )
            return f'"{escaped}"'

        primitive_type = dtype.primitive_type
        if isinstance(primitive_type, PrimitiveBooleanType):
            return "true" if value else "false"
        if isinstance(primitive_type, PrimitiveFloatingPointType):
            suffix = "f" if dtype.precision == 4 else ""
            return f"{value!r}{suffix}"
        if isinstance(primitive_type, PrimitiveComplexType):
            self.add_import(cpp_imports["complex"])
            real = self._visit(Literal(value.real, dtype.element_type))
            imag = self._visit(Literal(value.imag, dtype.element_type))
            return f"{self._visit(dtype)}{{{real}, {imag}}}"
        return repr(value)

    # ------------------------------
    #  Miscellaneous
    # ------------------------------

    def _visit_Variable(self, expr):
        """Render the ``Variable`` model node."""
        name = expr.name
        if expr.is_alias:
            return f"(*{name})"
        return name

    def _visit_Declare(self, expr):
        """Render the ``Declare`` model node."""
        var = expr.variable

        name = var.name
        class_type = var.class_type
        class_type_str = self._visit(class_type)
        const = " const" if isinstance(class_type, FinalType) else ""

        external = "extern " if expr.external else ""
        static = "static " if expr.static else ""

        return f"{static}{external}{class_type_str}{const} {name};\n"

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

    def _visit_Comment(self, expr):
        """Render the ``Comment`` model node."""
        comments = self._visit(expr.text)

        return f"//{comments}\n"

    def _visit_Import(self, expr):
        """Render the ``Import`` model node."""
        if expr.ignore:
            return ""
        source = expr.source.name if isinstance(expr.source, AsName) else expr.source
        source = self._visit(source)

        if source == "omp_lib":
            source = "omp"

        if source is None:
            return ""
        if expr.source in cpp_library_headers:
            return f"#include <{source}>\n"
        return f'#include "{source}.hpp"\n'

    def _visit_FunctionCall(self, expr):
        """Render the ``FunctionCall`` model node."""
        func = expr.funcdef
        # Ensure the correct syntax is used for pointers
        args = [a.value for a in expr.args]

        if func.arguments and func.arguments[0].bound_argument:
            raise NotImplementedError("Classes not yet implemented for C++")

        args = ", ".join(self._visit(a) for a in args)

        call_code = f"{func.name}({args})"
        if func.is_imported:
            mod = get_direct_module(func)
            assert mod is not None
            call_code = f"{mod.name}::{call_code}"
        if func.results.var is not NIL:
            return call_code
        return f"{call_code};\n"

    def _visit_Allocate(self, expr):
        """Render the ``Allocate`` model node."""
        variable = expr.variable
        if isinstance(variable.class_type, StringType):
            return ""
        raise NotImplementedError(f"Allocate not implemented for {variable.class_type}")

    def _visit_Deallocate(self, expr):
        """Render the ``Deallocate`` model node."""
        return ""

    def _visit_PythonType(self, expr):
        """Render the ``PythonType`` model node."""
        return self._visit(expr.print_string)

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _indent_codestring(self, code):
        """
        Indent code to the expected indentation.

        Indent code to the expected indentation.

        Parameters
        ----------
        code : str
            The code to be printed.

        Returns
        -------
        str
            The indented code to be printed.
        """
        tab = " " * self._default_settings["tabwidth"]
        if code == "":
            return code
        # code ends with \n
        return tab + code.replace("\n", "\n" + tab).rstrip(" ")

    def _format_code(self, lines):
        """
        Format the lines of code.

        Format the lines of code.

        Parameters
        ----------
        lines : str
            The unformatted lines of code.

        Returns
        -------
        str
            The formatted lines of code.
        """
        return lines

    def _function_signature(self, expr, print_arg_names=True):
        """
        Get the C++ representation of the function signature.

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
        name = expr.name
        result_var = expr.results.var

        args = ", ".join(self._visit(a) for a in expr.arguments)

        result = "void" if result_var is NIL else self._visit(result_var.class_type)

        return f"{result} {name}({args})"

    def _get_declare_type(self, var):
        """
        Get the type of a variable for its declaration.

        Get the type of a variable for its declaration.

        Parameters
        ----------
        var : Variable
            The variable to be declared.

        Returns
        -------
        str
            The code describing the type of the variable.
        """
        class_type = var.class_type
        class_type_str = self._visit(class_type)
        const = " const" if isinstance(class_type, FinalType) else ""

        return f"{class_type_str}{const}"

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
            return f"static_cast<{self._visit(dtype)}>" + "({})"
        return "{}"

    # -----------------------------------------------------------------------
    #                              Print methods
    # -----------------------------------------------------------------------
