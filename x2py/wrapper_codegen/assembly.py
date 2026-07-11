"""In-memory source assembly for isolated wrapper backend modules."""

from __future__ import annotations

from dataclasses import dataclass

from x2py.wrapper_codegen.nodes import CHeader, CModule, FortranModule
from x2py.wrapper_codegen.source_printers import CSourcePrinter, FortranSourcePrinter


@dataclass(frozen=True)
class RenderedBackendSources:
    """Rendered in-memory source strings for one wrapper module."""

    c_source: str
    c_header: str
    fortran_source: str


@dataclass(frozen=True)
class BackendSourceAssembly:
    """Complete isolated backend module set before file writing."""

    module_name: str
    c_module: CModule
    c_header: CHeader
    fortran_module: FortranModule

    def rendered_sources(self) -> RenderedBackendSources:
        """Render complete C source, C header, and Fortran source strings."""
        c_printer = CSourcePrinter()
        fortran_printer = FortranSourcePrinter()
        return RenderedBackendSources(
            c_source=c_printer.doprint(self.c_module),
            c_header=c_printer.doprint(self.c_header),
            fortran_source=fortran_printer.doprint(self.fortran_module),
        )
