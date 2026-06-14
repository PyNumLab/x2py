"""
Module containing the `Codegen` class which handles the generation of code
for a Python program or module. It takes the X2py semantic parser, which
contains the X2py AST annotated through the semantic stage as well as the
scoping information, and uses the appropriate `CodePrinter` to generate code
in the target language.
See developer_docs/codegen_stage.md for more details on the codegen stage.
"""

from .ccode import CCodePrinter
from .cppcode import CppCodePrinter
from .fcode import FCodePrinter
from .pycode import PythonCodePrinter

_extension_registry = {"fortran": "f90", "c": "c", "c++": "cpp", "python": "py"}
_header_extension_registry = {"fortran": None, "c": "h", "c++": "hpp", "python": None}
printer_registry = {
    "fortran": FCodePrinter,
    "c": CCodePrinter,
    "c++": CppCodePrinter,
    "python": PythonCodePrinter,
}
