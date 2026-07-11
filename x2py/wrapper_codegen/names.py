"""Minimal naming and emission contexts for isolated wrapper backends."""

from __future__ import annotations

from dataclasses import dataclass, field


class NameAllocator:
    """Allocate deterministic unique generated identifiers."""

    _KEYWORDS = frozenset(
        {
            "auto",
            "break",
            "case",
            "char",
            "const",
            "continue",
            "default",
            "do",
            "double",
            "else",
            "enum",
            "extern",
            "float",
            "for",
            "goto",
            "if",
            "int",
            "long",
            "return",
            "short",
            "signed",
            "sizeof",
            "static",
            "struct",
            "switch",
            "typedef",
            "union",
            "unsigned",
            "void",
            "volatile",
            "while",
        }
    )

    def __init__(self, reserved: tuple[str, ...] = ()):
        """Create an allocator with optional reserved names."""
        self._used = {self._sanitize(name) for name in reserved}

    def reserve(self, name: str) -> str:
        """Reserve an exact generated identifier."""
        sanitized = self._sanitize(name)
        self._used.add(sanitized)
        return sanitized

    def allocate(self, preferred: str, *, prefix: str = "x") -> str:
        """Return a unique identifier derived from ``preferred``."""
        base = self._sanitize(preferred, prefix=prefix)
        candidate = base
        index = 1
        while candidate in self._used:
            candidate = f"{base}_{index}"
            index += 1
        self._used.add(candidate)
        return candidate

    @property
    def used_names(self) -> tuple[str, ...]:
        """Return allocated and reserved names in deterministic order."""
        return tuple(sorted(self._used))

    def _sanitize(self, value: str, *, prefix: str = "x") -> str:
        """Return a valid C-like identifier."""
        raw = value.strip() or prefix
        chars = [char if self._is_identifier_char(char) else "_" for char in raw]
        name = "".join(chars)
        if not self._is_identifier_start(name[0]):
            name = f"{prefix}_{name}"
        if name in self._KEYWORDS:
            name = f"{name}_"
        return name

    def _is_identifier_start(self, char: str) -> bool:
        """Return whether ``char`` may start an identifier."""
        return char == "_" or char.isalpha()

    def _is_identifier_char(self, char: str) -> bool:
        """Return whether ``char`` may appear in an identifier."""
        return char == "_" or char.isalnum()


@dataclass
class ModuleEmissionContext:
    """Backend-local state for one generated module."""

    module_name: str
    name_allocator: NameAllocator = field(default_factory=NameAllocator)

    def function_context(self, owner_path: str) -> FunctionEmissionContext:
        """Return a function-local context sharing module names."""
        return FunctionEmissionContext(
            module_name=self.module_name,
            owner_path=owner_path,
            name_allocator=self.name_allocator,
        )


@dataclass
class FunctionEmissionContext:
    """Backend-local state for one generated function."""

    module_name: str
    owner_path: str
    name_allocator: NameAllocator

    def local_name(self, preferred: str) -> str:
        """Allocate one function-local generated name."""
        return self.name_allocator.allocate(preferred)
