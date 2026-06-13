from .cppcode import CppCodePrinter

class PyBindCodePrinter(CppCodePrinter):
    """
    A printer for printing the C++-Python interface.

    A printer to convert Pyccel's AST describing a translated module,
    to strings of PyBind11 code which provide an interface between the module
    and Python code.
    As for all printers the navigation of this file is done via _print_X
    functions.

    Parameters
    ----------
    filename : str
            The name of the file being pyccelised.
    **settings : dict
            Any additional arguments which are necessary for CppCodePrinter.
    """
