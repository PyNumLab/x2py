"""Functions for printing C++ code."""

from itertools import chain

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
    PythonNativeFloat,
    StringType,
)
from ..models.datatypes import LiteralString, LiteralTrue, Nil
from ..models.datatypes import NumpyFloat
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
# Used in CppCodePrinter._print_MathFunctionBase(self, expr)
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
    As for all printers the navigation of this file is done via _print_X
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

    _default_settings = {
        "tabwidth": 4,
    }

    def __init__(self, filename, *, verbose):

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
        else:
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

    def function_signature(self, expr, print_arg_names=True):
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

        args = ", ".join(self._print(a) for a in expr.arguments)

        result = "void" if result_var is Nil() else self._print(result_var.class_type)

        return f"{result} {name}({args})"

    def get_declare_type(self, var):
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
        class_type_str = self._print(class_type)
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
            return f"static_cast<{self._print(dtype)}>" + "({})"
        return "{}"

    # -----------------------------------------------------------------------
    #                              Print methods
    # -----------------------------------------------------------------------

    def _print_ModuleHeader(self, expr):
        name = expr.module.name
        self.set_scope(expr.module.scope)
        self._in_header = True

        decls = [
            Declare(v, external=True, module_variable=True)
            for v in expr.module.variables
            if not v.is_private
        ]
        global_variables = "".join(self._print(d) for d in decls)

        classes = "\n".join(self._print(classDef) for classDef in expr.module.classes)

        funcs = "\n".join(
            f"{self.function_signature(f)};"
            for f in expr.module.funcs
            if not f.is_inline
        )

        # Print imports last to be sure that all additional_imports have been collected
        imports = [
            i
            for i in chain(expr.module.imports, self._additional_imports.values())
            if not i.ignore
        ]
        # imports = self.sort_imports(imports)
        imports = "".join(self._print(i) for i in imports)

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

    def _print_Module(self, expr):
        self.set_scope(expr.scope)
        name = expr.name

        global_variables = "".join([self._print(d) for d in expr.declarations])
        body = "".join(self._print(i) for i in expr.body)

        # Print imports last to be sure that all additional_imports have been collected
        imports = Import(
            self.scope.get_python_name(expr.name), Module(expr.name, (), ())
        )
        imports_code = self._print(imports)
        if "complex" in self._additional_imports:
            imports_code += "using namespace std::complex_literals;\n"

        self.exit_scope()

        return "".join(
            (imports_code, f"namespace {name} {{\n\n", global_variables, body, "\n}\n")
        )

    def _print_Program(self, expr):
        mod = get_direct_module(expr)
        assert mod is not None
        name = mod.name
        self.set_scope(expr.scope)
        body = self._print(expr.body)
        variables = self.scope.variables.values()
        decs = "".join(
            self._print(Declare(v))
            for v in variables
            if v not in self._declared_vars[-1]
        )

        imports = [
            i
            for i in chain(expr.imports, self._additional_imports.values())
            if not i.ignore
        ]
        imports = "".join(self._print(i) for i in imports)
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

    def _print_FunctionDef(self, expr):
        if expr.is_inline:
            return ""

        self.set_scope(expr.scope)

        body = self._print(expr.body)

        self.exit_scope()

        return "".join(
            (
                self.function_signature(expr),
                " {\n",
                self._indent_codestring(body),
                "}\n",
            )
        )

    def _print_CodeBlock(self, expr):
        body_exprs = expr.body
        body_code = ""
        for b in body_exprs:
            code = self._print(b)
            code = self._additional_code + code
            self._additional_code = ""
            body_code += code
        return body_code

    def _print_Assign(self, expr):
        lhs = expr.lhs

        prefix = ""
        if lhs in self.scope.variables.values() and lhs not in self._declared_vars[-1]:
            prefix = self.get_declare_type(lhs) + " "
            self._declared_vars[-1].add(lhs)

        lhs_code = self._print(lhs)
        rhs_code = self._print(expr.rhs)
        return f"{prefix}{lhs_code} = {rhs_code};\n"

    # ------------------------------
    #  Ternary operator
    # ------------------------------

    def _print_IfTernaryOperator(self, expr):
        """
        Python: a if cond else b
        C++:    (cond ? a : b)
        """
        c = self._print(expr.cond)
        a = self._print(expr.value_true)
        b = self._print(expr.value_false)
        return f"({c} ? {a} : {b})"

    # ------------------------------
    #  Arithmetic operators
    # ------------------------------

    def _print_Add(self, expr):
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._print(a))
        b_code = self._cast_to(b, target_dtype).format(self._print(b))
        return f"{a_code} + {b_code}"

    def _print_Minus(self, expr):
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._print(a))
        b_code = self._cast_to(b, target_dtype).format(self._print(b))
        return f"{a_code} - {b_code}"

    def _print_Mul(self, expr):
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._print(a))
        b_code = self._cast_to(b, target_dtype).format(self._print(b))
        return f"{a_code} * {b_code}"

    def _print_Div(self, expr):
        target_dtype = expr.dtype
        a, b = expr.args
        a_code = self._cast_to(a, target_dtype).format(self._print(a))
        b_code = self._cast_to(b, target_dtype).format(self._print(b))
        return f"{a_code} / {b_code}"

    def _print_FloorDiv(self, expr):
        # the result type of the floor division is dependent on the arguments
        # type, if all arguments are integers or booleans the result is integer
        # otherwise the result type is float
        need_to_cast = all(
            a.dtype.primitive_type in (PrimitiveIntegerType(), PrimitiveBooleanType())
            for a in expr.args
        )
        if need_to_cast:
            self.add_import(cpp_imports["pyc_math_cpp"])
            return f"py_floor_div({self._print(expr.args[0])}, {self._print(expr.args[1])})"

        self.add_import(cpp_imports["cmath"])
        code = " / ".join(
            self._print(
                a
                if a.dtype.primitive_type is PrimitiveFloatingPointType()
                else NumpyFloat(a)
            )
            for a in expr.args
        )
        return f"std::floor({code})"

    def _print_Mod(self, expr):
        self.add_import(cpp_imports["pyc_math_cpp"])
        target_dtype = expr.dtype
        n, base = expr.args
        n_code = self._cast_to(n, target_dtype).format(self._print(n))
        base_code = self._cast_to(base, target_dtype).format(self._print(base))
        return f"pyc_modulo({n_code}, {base_code})"

    def _print_Pow(self, expr):
        self.add_import(cpp_imports["cmath"])
        base, exponent = expr.args
        base_code = self._print(base)
        exponent_code = self._print(exponent)

        dtype = expr.dtype

        try:
            exponent_is_pos_int = (
                exponent.dtype.primitive_type is PrimitiveIntegerType() and exponent > 0
            )
        except TypeError:
            exponent_is_pos_int = False

        if base == 2 and exponent_is_pos_int:
            code = f"2 << {exponent_code}"
            current_dtype = exponent.dtype
        else:
            code = f"std::pow({base_code}, {exponent_code})"
            current_dtype = (
                dtype
                if dtype.primitive_type
                not in (PrimitiveIntegerType(), PrimitiveBooleanType())
                else PythonNativeFloat()
            )

        if current_dtype != dtype:
            return f"({self._print(dtype)})({code})"
        else:
            return code

    # ------------------------------
    #  Unary operators
    # ------------------------------

    def _print_UnaryPlus(self, expr):
        return f"+{self._print(expr.args[0])}"

    def _print_UnarySub(self, expr):
        return f"-{self._print(expr.args[0])}"

    def _print_Not(self, expr):
        return f"!({self._print(expr.args[0])})"

    def _print_Invert(self, expr):
        # Bitwise invert (~)
        return f"~({self._print(expr.args[0])})"

    # ------------------------------
    #  Logical operators
    # ------------------------------

    def _print_And(self, expr):
        return " && ".join(self._print(a) for a in expr.args)

    def _print_Or(self, expr):
        return " || ".join(self._print(a) for a in expr.args)

    # ------------------------------
    #  Comparison operators
    # ------------------------------

    def _print_Eq(self, expr):
        a, b = expr.args
        return f"{self._print(a)} == {self._print(b)}"

    def _print_Ne(self, expr):
        a, b = expr.args
        return f"{self._print(a)} != {self._print(b)}"

    def _print_Gt(self, expr):
        a, b = expr.args
        return f"{self._print(a)} > {self._print(b)}"

    def _print_Ge(self, expr):
        a, b = expr.args
        return f"{self._print(a)} >= {self._print(b)}"

    def _print_Lt(self, expr):
        a, b = expr.args
        return f"{self._print(a)} < {self._print(b)}"

    def _print_Le(self, expr):
        a, b = expr.args
        return f"{self._print(a)} <= {self._print(b)}"

    # ------------------------------
    #  Bitwise operators
    # ------------------------------

    def _print_BitAnd(self, expr):
        a, b = expr.args
        return f"{self._print(a)} & {self._print(b)}"

    def _print_BitOr(self, expr):
        a, b = expr.args
        return f"{self._print(a)} | {self._print(b)}"

    def _print_BitXor(self, expr):
        a, b = expr.args
        return f"{self._print(a)} ^ {self._print(b)}"

    # ------------------------------
    #  Bit shifts
    # ------------------------------

    def _print_LShift(self, expr):
        a, b = expr.args
        return f"{self._print(a)} << {self._print(b)}"

    def _print_RShift(self, expr):
        a, b = expr.args
        return f"{self._print(a)} >> {self._print(b)}"

    # ------------------------------
    #  Parentheses
    # ------------------------------

    def _print_AssociativeParenthesis(self, expr):
        return f"({self._print(expr.args[0])})"

    # ------------------------------
    #  Casts
    # ------------------------------

    def _print_PythonFloat(self, expr):
        value = self._print(expr.arg)
        type_name = self._print(expr.dtype)
        return f"static_cast<{type_name}>({value})"

    # ------------------------------
    #  Types
    # ------------------------------

    def _print_PythonNativeBool(self, expr):
        return "bool"

    def _print_PythonNativeInt(self, expr):
        # TODO: Improve, wrong precision
        return "int"

    def _print_PythonNativeFloat(self, expr):
        return "double"

    def _print_PythonNativeComplex(self, expr):
        self.add_import(cpp_imports["complex"])
        return "std::complex<double>"

    def _print_StringType(self, expr):
        self.add_import(cpp_imports["string"])
        return "std::string"

    def _print_NumpyFloat32Type(self, expr):
        return "float"

    def _print_NumpyFloat64Type(self, expr):
        return "double"

    # ------------------------------
    #  Mathematical functions
    # ------------------------------

    # ------------------------------
    #  Literals
    # ------------------------------

    def _print_Literal(self, expr):
        # TODO: Ensure correct precision
        return repr(expr.python_value)

    def _print_LiteralTrue(self, expr):
        return "true"

    def _print_LiteralFalse(self, expr):
        return "false"

    def _print_LiteralImaginaryUnit(self, expr):
        self.add_import(cpp_imports["complex"])
        return "1i"

    def _print_LiteralComplex(self, expr):
        if self._in_header:
            return f"{self._print(expr.dtype)}{{{self._print(expr.real)}, {self._print(expr.imag)}}}"
        else:
            if expr.real == 0:
                return self._print(expr.imag) + "i"
            else:
                return f"({self._print(expr.real)} + {self._print(expr.imag)}i)"

    def _print_LiteralString(self, expr):
        escaped_str = expr.python_value
        escaped_str = (
            escaped_str.replace("\\", "\\\\")
            .replace("\a", "\\a")
            .replace("\b", "\\b")
            .replace("\f", "\\f")
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
            .replace("\v", "\\v")
            .replace('"', '\\"')
        )
        return f'"{escaped_str}"'

    # ------------------------------
    #  Miscellaneous
    # ------------------------------

    def _print_Variable(self, expr):
        name = expr.name
        if expr.is_alias:
            return f"(*{name})"
        else:
            return name

    def _print_Declare(self, expr):
        var = expr.variable

        name = var.name
        class_type = var.class_type
        class_type_str = self._print(class_type)
        const = " const" if isinstance(class_type, FinalType) else ""

        external = "extern " if expr.external else ""
        static = "static " if expr.static else ""

        return f"{static}{external}{class_type_str}{const} {name};\n"

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

    def _print_Comment(self, expr):
        comments = self._print(expr.text)

        return f"//{comments}\n"

    def _print_Import(self, expr):
        if expr.ignore:
            return ""
        if isinstance(expr.source, AsName):
            source = expr.source.name
        else:
            source = expr.source
        source = self._print(source)

        if source == "omp_lib":
            source = "omp"

        if source is None:
            return ""
        if expr.source in cpp_library_headers:
            return f"#include <{source}>\n"
        else:
            return f'#include "{source}.hpp"\n'

    def _print_FunctionCall(self, expr):
        func = expr.funcdef
        # Ensure the correct syntax is used for pointers
        args = [a.value for a in expr.args]

        if func.arguments and func.arguments[0].bound_argument:
            raise NotImplementedError("Classes not yet implemented for C++")

        args = ", ".join(self._print(a) for a in args)

        call_code = f"{func.name}({args})"
        if func.is_imported:
            mod = get_direct_module(func)
            assert mod is not None
            call_code = f"{mod.name}::{call_code}"
        if func.results.var is not Nil():
            return call_code
        else:
            return f"{call_code};\n"

    def _print_Allocate(self, expr):
        variable = expr.variable
        if isinstance(variable.class_type, StringType):
            return ""
        else:
            raise NotImplementedError(
                f"Allocate not implemented for {variable.class_type}"
            )

    def _print_Deallocate(self, expr):
        return ""

    def _print_PythonType(self, expr):
        return self._print(expr.print_string)
