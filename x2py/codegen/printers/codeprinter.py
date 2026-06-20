"""
Module containing the base class `CodePrinter` from which all code printers
inherit. The sub-classes should define a language and `_visit_X` functions.
The `CodePrinter` class also contains some general functionality which may be
used by all code printers, such as the management of imports and the current
scope.
"""

from ..models.core import Module, ModuleHeader, Program

# TODO: add examples

__all__ = ["CodePrinter"]


class CodePrinter:
    """
    The base class for code-printing subclasses.

    The base class from which code printers inherit. The sub-classes should define a language
    and `_visit_X` functions.

    Parameters
    ----------
    verbose : int
        The level of verbosity.
    """

    language = None

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, verbose):
        """Initialize the state used for one generation run."""
        self._scope = None
        self._additional_imports = {}
        self._verbose = verbose

    def doprint(self, expr):
        """
        Print the expression as code.

        Print the expression as code.

        Parameters
        ----------
        expr : Expression
            The expression to be printed.

        Returns
        -------
        str
            The generated code.
        """
        assert isinstance(expr, Module | ModuleHeader | Program)

        # Do the actual printing
        lines = self._visit(expr).splitlines(True)

        # Format the output
        return "".join(self._format_code(lines))

    def get_additional_imports(self):
        """
        Get any additional imports collected during the printing stage.

        Get any additional imports collected during the printing stage.
        This is necessary to correctly compile the files.

        Returns
        -------
        dict[str, Import]
            A dictionary mapping the include strings to the import module.
        """
        return self._additional_imports

    def add_import(self, import_obj):
        """
        Add a new import to the current context.

        Add a new import to the current context. This allows the import to be recognised
        at the compiling/linking stage. If the source of the import is not new then any
        new targets are added to the Import object.

        Parameters
        ----------
        import_obj : Import
            The AST node describing the import.
        """
        source = str(import_obj.source)
        if source not in self._additional_imports:
            self._additional_imports[source] = import_obj
        elif import_obj.target:
            self._additional_imports[source].define_target(import_obj.target)

    @property
    def scope(self):
        """Return the scope associated with the object being printed"""
        return self._scope

    def set_scope(self, scope):
        """Change the current scope"""
        assert scope is not None
        self._scope = scope

    def exit_scope(self):
        """Exit the current scope and return to the enclosing scope"""
        self._scope = self._scope.parent_scope

    # ------------------------------------------------------------------
    # Model dispatch
    # ------------------------------------------------------------------

    def _visit(self, expr):
        """
        Print the AST node in the printer language.

        The printing is done by finding the appropriate function _visit_X
        for the object expr. X is the type of the object expr. If this function
        does not exist then the method resolution order is used to search for
        other compatible _visit_X functions. If none are found then an error is
        raised.

        Parameters
        ----------
        expr : model object
            The expression that should be printed.

        Returns
        -------
        str
            A string containing code in the printer language which is equivalent
            to the expression.
        """

        classes = type(expr).__mro__
        for cls in classes:
            visitor_method = "_visit_" + cls.__name__
            if hasattr(self, visitor_method):
                if self._verbose > 2:
                    print(f">>>> Calling {type(self).__name__}.{visitor_method}")
                return getattr(self, visitor_method)(expr)
        return self._visit_not_supported(expr)

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    def _visit_NumberSymbol(self, expr):
        """Print sympy symbols used for constants"""
        return str(expr)

    def _visit_str(self, expr):
        """Basic print functionality for strings"""
        return expr

    def _visit_not_supported(self, expr):
        """Raise an error when no visitor supports the model type."""
        msg = f"_visit_{type(expr).__name__} is not yet implemented for language : {self.language}\n"
        raise NotImplementedError(msg)

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _declare_number_const(self, name, value):
        """Declare a numeric constant at the top of a function"""
        raise NotImplementedError("This function must be implemented by subclass of CodePrinter.")

    def _format_code(self, lines):
        """Take in a list of lines of code, and format them accordingly.

        This may include indenting, wrapping long lines, etc..."""
        raise NotImplementedError("This function must be implemented by subclass of CodePrinter.")

    # Number constants
    _visit_Catalan = _visit_NumberSymbol
    _visit_EulerGamma = _visit_NumberSymbol
    _visit_GoldenRatio = _visit_NumberSymbol
    _visit_Exp1 = _visit_NumberSymbol
    _visit_Pi = _visit_NumberSymbol
