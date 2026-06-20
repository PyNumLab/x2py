"""Small container passed from semantic lowering to wrapper generation."""

from __future__ import annotations


class Codegen:
    """Hold the generated module and scope used by `BindingPipeline`."""

    def __init__(self, name, ast, scope):
        self._name = name
        self._scope = scope
        self._ast = ast

    @property
    def name(self):
        """Return the Python extension module name."""
        return self._name

    @property
    def scope(self):
        """Return the root codegen scope."""
        return self._scope

    @property
    def ast(self):
        """Return the lowered codegen module AST."""
        return self._ast
