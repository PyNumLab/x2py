"""
Module containing all classes which handle name collision rules
for different languages.
"""

from .cnameclashchecker import CNameClashChecker
from .fortrannameclashchecker import FortranNameClashChecker
from .pythonnameclashchecker import PythonNameClashChecker

name_clash_checkers = {
    "fortran": FortranNameClashChecker(),
    "c": CNameClashChecker(),
    "python": PythonNameClashChecker(),
}
