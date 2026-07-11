"""Generated-wrapper artifact handoff shared by wrapper build routes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ("GeneratedWrapperArtifacts",)


@dataclass(frozen=True)
class GeneratedWrapperArtifacts:
    """Generated wrapper files produced before compile/link orchestration."""

    module_name: str
    bridge_sources: tuple[Path, ...] = ()
    binding_sources: tuple[Path, ...] = ()
    header_files: tuple[Path, ...] = ()
    runtime_support_keys: tuple[str, ...] = ()

    @property
    def source_files(self) -> tuple[Path, ...]:
        """Return all generated wrapper sources in compile order."""
        return (*self.bridge_sources, *self.binding_sources)

    @property
    def generated_files(self) -> tuple[Path, ...]:
        """Return all generated wrapper files, including headers."""
        return (*self.source_files, *self.header_files)
