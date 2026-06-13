# ------------------------------------------------------------------------- #
# This file is part of Pyccel which is released under MIT License. See the  #
# LICENSE file or go to https://github.com/pyccel/pyccel/blob/devel/LICENSE #
# for full license details.                                                 #
# ------------------------------------------------------------------------- #
"""
Module containing the `Codegen` class which handles the generation of code
for a Python program or module. It takes the Pyccel semantic parser, which
contains the Pyccel AST annotated through the semantic stage as well as the
scoping information, and uses the appropriate `CodePrinter` to generate code
in the target language.
See developer_docs/codegen_stage.md for more details on the codegen stage.
"""

import os

from ..models.core import ModuleHeader
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
