"""Shared visitor base for bridge and binding generators."""

from x2py.utilities.visitor import ClassVisitor

from .scope import Scope

__all__ = ("BindingGenerator", "BridgeGenerator")


class _Generator(ClassVisitor):
    """Dispatch codegen model nodes to `_visit_<Model>` methods."""

    start_language = None
    target_language = None
    generator_kind = "generator"

    def __init__(self, verbose):
        self._scope = None
        self._verbose = verbose

    @property
    def scope(self):
        """Return the current generation scope."""
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Set the current generation scope."""
        assert isinstance(scope, Scope)
        self._scope = scope

    def exit_scope(self):
        """Return to the enclosing generation scope."""
        self._scope = self._scope.parent_scope

    def generate(self, expr):
        """Generate a bridge or binding model for `expr`."""
        return self._visit(expr)

    def _visit_not_supported(self, expr):
        """Raise an error when no visitor supports the model type."""
        msg = f"_visit_{type(expr).__name__} is not yet implemented for {self.generator_kind} : {type(self)}\n"
        raise NotImplementedError(msg)


class BindingGenerator(_Generator):
    """Base class for generators that create target-language bindings."""

    generator_kind = "binding generator"


class BridgeGenerator(_Generator):
    """Base class for generators that create language bridges."""

    generator_kind = "bridge generator"
