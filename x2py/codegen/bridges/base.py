"""
Module describing the base bridge generator class : BridgeGenerator.
"""

from ..scope import Scope

__all__ = ["BridgeGenerator"]


class BridgeGenerator:
    """
    The base class for bridge generator subclasses.

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

    def __init__(self, verbose):
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
                try:
                    obj = getattr(self, visit_method)(expr)
                except:
                    raise NotImplementedError(visit_method)
                return obj

        return self._visit_not_supported(expr)

    def _visit_not_supported(self, expr):
        """Print an error message if the generate function for the type
        is not implemented"""
        msg = f"_visit_{type(expr).__name__} is not yet implemented for generator : {type(self)}\n"
        raise ValueError(msg)
