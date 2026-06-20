from .codeprinter import CodePrinter


class PythonCodePrinter(CodePrinter):
    """
    A printer for printing code in Python.

    A printer to convert X2py's AST to strings of Python code.
    As for all printers the navigation of this file is done via _visit_X
    functions.

    Parameters
    ----------
    filename : str
        The name of the file being converted.
    verbose : int
        The level of verbosity.
    """
