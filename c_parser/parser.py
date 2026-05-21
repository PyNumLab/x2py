# -*- coding: utf-8 -*-
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from .models import CFile, CProject


_C_SOURCE_SUFFIXES = {".c", ".h"}


def _looks_like_existing_source_path(value: object) -> bool:
    if isinstance(value, Path):
        return value.is_file()
    if not isinstance(value, str) or not value or "\n" in value:
        return False
    try:
        return Path(value).is_file()
    except OSError:
        return False


def _collect_c_paths(path: Path) -> list[Path]:
    return sorted(
        p
        for p in path.rglob("*")
        if p.is_file() and p.suffix.lower() in _C_SOURCE_SUFFIXES
    )


class CParser:
    """C parser skeleton entrypoint.

    This class intentionally returns typed empty models. Grammar parsing lands
    in later phases after the public API, CLI, and serialization contracts are
    stable.
    """

    def visit_file(
        self,
        source_or_path: str | Path,
        filename: str | None = None,
        *,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        include_dirs: Sequence[str | Path] | None = None,
        preprocessing: str = "raw",
        encoding: str = "utf-8",
    ) -> CFile:
        del macro_defines, include_dirs
        if _looks_like_existing_source_path(source_or_path):
            path = Path(source_or_path)
            if filename is None:
                filename = str(path)
            path.read_text(encoding=encoding)
        else:
            str(source_or_path)

        return CFile(filename=filename, preprocessing=preprocessing)

    def visit_project(
        self,
        files: Mapping[str, str] | Sequence[str | Path] | str | Path,
        *,
        include_dirs: Sequence[str | Path] | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        preprocessing: str = "raw",
        encoding: str = "utf-8",
    ) -> CProject:
        if isinstance(files, Mapping):
            parsed_files = {
                name: self.visit_file(
                    source,
                    filename=name,
                    include_dirs=include_dirs,
                    macro_defines=macro_defines,
                    preprocessing=preprocessing,
                    encoding=encoding,
                )
                for name, source in files.items()
            }
            return CProject(files=parsed_files)

        paths: list[Path] = []
        root: Path | None = None
        if isinstance(files, (str, Path)):
            path = Path(files)
            if path.is_dir():
                root = path
                paths = _collect_c_paths(path)
            else:
                paths = [path]
        else:
            paths = [Path(p) for p in files]

        parsed_files: dict[str, CFile] = {}
        for path in sorted(paths):
            key = path.name if root is not None else str(path)
            if root is not None:
                key = str(path.relative_to(root))
            parsed_files[key] = self.visit_file(
                path,
                filename=key,
                include_dirs=include_dirs,
                macro_defines=macro_defines,
                preprocessing=preprocessing,
                encoding=encoding,
            )
        return CProject(files=parsed_files)


_DEFAULT_PARSER = CParser()


def parse_c_file(
    source_or_path: str | Path,
    filename: str | None = None,
    *,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    include_dirs: Sequence[str | Path] | None = None,
    preprocessing: str = "raw",
    encoding: str = "utf-8",
) -> CFile:
    return _DEFAULT_PARSER.visit_file(
        source_or_path,
        filename=filename,
        macro_defines=macro_defines,
        include_dirs=include_dirs,
        preprocessing=preprocessing,
        encoding=encoding,
    )


def parse_c_project(
    files: Mapping[str, str] | Sequence[str | Path] | str | Path,
    *,
    include_dirs: Sequence[str | Path] | None = None,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    preprocessing: str = "raw",
    encoding: str = "utf-8",
) -> CProject:
    return _DEFAULT_PARSER.visit_project(
        files,
        include_dirs=include_dirs,
        macro_defines=macro_defines,
        preprocessing=preprocessing,
        encoding=encoding,
    )
