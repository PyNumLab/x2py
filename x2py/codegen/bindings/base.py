"""
Module describing the base code-wrapping class : BindingGenerator.
"""

from ..scope import Scope

__all__ = ["BindingGenerator"]


class BindingGenerator:
    """
    The base class for code-wrapping subclasses.

    The base class for any classes designed to create a wrapper around code.
    Such wrappers are necessary to create an interface between two different
    languages.

    Parameters
    ----------
    verbose : int
        The level of verbosity.
    """

    start_language = None
    target_language = None

    # ------------------------------------------------------------------
    # Public entrypoints and state
    # ------------------------------------------------------------------

    def __init__(self, verbose):
        """Initialize the state used for one generation run."""
        self._scope = None
        self._verbose = verbose

    @property
    def scope(self):
        """
        Get the current scope.

        Get the scope for the current context.

        See Also
        --------
        x2py.parser.scope.Scope
            The type of the returned object.
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Handle scope for the current generation context."""
        assert isinstance(scope, Scope)
        self._scope = scope

    def exit_scope(self):
        """
        Exit the current scope and return to the enclosing scope.

        Exit the current scope and set the scope back to the value
        of the enclosing scope.
        """
        self._scope = self._scope.parent_scope

    def generate(self, expr):
        """
        Get the wrapped version of the AST object.

        Return the AST object which allows the object `expr` printed
        in the start language to be accessed from the target language.

        Parameters
        ----------
        expr : codegen model object
            The expression that should be wrapped.

        Returns
        -------
        codegen model object
            The AST which describes the object that lets you
            access the expression.
        """
        return self._visit(expr)

    # ------------------------------------------------------------------
    # Model dispatch
    # ------------------------------------------------------------------

    def _visit(self, expr):
        """
        Get the wrapped version of the AST object.

        Private function returning the AST object which is used to access
        the object `expr` from the target language.

        Parameters
        ----------
        expr : codegen model object
            The expression that should be wrapped.

        Returns
        -------
        codegen model object
            The AST which describes the object that lets you
            access the expression.
        """

        classes = type(expr).mro()
        for cls in classes:
            visit_method = "_visit_" + cls.__name__
            if hasattr(self, visit_method):
                if self._verbose > 2:
                    print(f">>>> Calling {type(self).__name__}.{visit_method}")
                return getattr(self, visit_method)(expr)

        return self._visit_not_supported(expr)

    # ------------------------------------------------------------------
    # Model visitors
    # ------------------------------------------------------------------

    def _visit_not_supported(self, expr):
        """Raise an error when no binding visitor supports the model type."""
        msg = f"_visit_{type(expr).__name__} is not yet implemented for generator : {type(self)}\n"
        raise NotImplementedError(msg)
