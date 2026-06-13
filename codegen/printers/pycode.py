from .codeprinter import CodePrinter


class PythonCodePrinter(CodePrinter):
    """
    A printer for printing code in Python.

    A printer to convert Pyccel's AST to strings of Python code.
    As for all printers the navigation of this file is done via _print_X
    functions.

    Parameters
    ----------
    filename : str
        The name of the file being pyccelised.
    verbose : int
        The level of verbosity.
    """
    


