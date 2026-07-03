"""Shared class-based visitor dispatch for parser, semantics, and codegen models."""

from __future__ import annotations

__all__ = ("ClassVisitor",)


class ClassVisitor:
    """Dispatch model nodes through the ``_visit_<ClassName>`` protocol.

    Subclasses implement one handler per supported model class. Dispatch follows
    the model class MRO so a handler for a base model remains a deliberate
    fallback for its subclasses.
    """

    def _visit(self, node, *args, **kwargs):
        """Call the most specific ``_visit_<ClassName>`` handler for ``node``."""
        for node_type in type(node).__mro__:
            method_name = f"_visit_{node_type.__name__}"
            method = getattr(self, method_name, None)
            if method is None:
                continue
            if getattr(self, "_verbose", 0) > 2:
                print(f">>>> Calling {type(self).__name__}.{method_name}")
            return method(node, *args, **kwargs)
        return self._visit_not_supported(node)

    @staticmethod
    def _visit_not_supported(node):
        """Raise when no class visitor handles ``node``."""
        raise TypeError(f"Unsupported model for class visitor: {type(node)!r}")
