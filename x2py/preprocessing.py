# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import shlex
import subprocess
from collections.abc import Sequence


class PreprocessingError(ValueError):
    """Raised when compiler-assisted preprocessing cannot produce source text."""


@dataclass(frozen=True)
class PreprocessingConfig:
    """User-selected preprocessing settings shared by language frontends.

    `compiler` is intentionally the exact executable supplied by the user or a
    build database. x2py does not guess compiler versions when compiler mode is
    requested.
    """

    mode: str = "internal"
    compiler: str | None = None
    compile_commands: str | None = None
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    undefs: list[str] = field(default_factory=list)
    std: str | None = None
    compiler_args: list[str] = field(default_factory=list)

    @property
    def uses_compiler(self) -> bool:
        """Return whether this configuration asks x2py to run a compiler."""
        return self.mode == "compiler"

    def fortran_macro_defines(self) -> dict[str, int | str]:
        """Return macro selections for the Fortran internal preprocessor."""
        macros: dict[str, int | str] = {}
        for define in self.defines:
            name, value = _split_define(define)
            macros[name] = 1 if value is None else value
        for name in self.undefs:
            macros[name] = 0
        return macros

    def fortran_internal_recipe(self, source_path: str | Path) -> dict[str, object] | None:
        """Return JSON provenance when internal Fortran macro selection is active."""
        if not (self.defines or self.undefs):
            return None
        return PreprocessingRecipe(
            mode=self.mode,
            language="fortran",
            source_path=str(source_path),
            include_dirs=list(self.include_dirs),
            defines=list(self.defines),
            undefs=list(self.undefs),
            standard=self.std,
            compiler_args=list(self.compiler_args),
        ).to_dict()


@dataclass(frozen=True)
class PreprocessingRecipe:
    """JSON-stable recipe for reproducing parser input preprocessing."""

    mode: str
    language: str
    source_path: str
    compiler: str | None = None
    argv: list[str] = field(default_factory=list)
    cwd: str | None = None
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    undefs: list[str] = field(default_factory=list)
    standard: str | None = None
    compiler_args: list[str] = field(default_factory=list)
    compile_commands: str | None = None
    compile_commands_entry: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        """Return JSON-compatible recipe metadata."""
        return asdict(self)


@dataclass(frozen=True)
class CompilerInvocation:
    """Concrete compiler-preprocessor command and working directory."""

    argv: list[str]
    cwd: str | None = None
    compile_commands_entry: dict[str, object] | None = None


_COMPILE_ONLY_FLAGS = {"-c", "/c"}
_SKIP_VALUE_FLAGS = {"-o", "/Fo", "-MF", "-MT", "-MQ"}
_SKIP_PREFIX_FLAGS = ("-o", "/Fo")
_SOURCE_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".f",
    ".for",
    ".ftn",
    ".f77",
    ".f90",
    ".f95",
    ".f03",
    ".f08",
}


def _split_define(define: str) -> tuple[str, str | None]:
    """Split a `-D` style value into macro name and optional value."""
    if "=" in define:
        name, value = define.split("=", 1)
        return name, value
    return define, None


def validate_macro_name(value: str, option: str) -> None:
    """Validate that a macro flag has a non-empty name."""
    name = value.split("=", 1)[0]
    if not name:
        raise PreprocessingError(f"{option} requires a macro name")


def _std_arg(language: str, standard: str | None) -> list[str]:
    """Return compiler standard arguments for the active frontend."""
    if not standard:
        return []
    return [f"-std={standard}"]


def _common_compiler_flags(config: PreprocessingConfig, language: str) -> list[str]:
    """Build flags shared by direct and compile-database preprocessing."""
    flags: list[str] = []
    for include_dir in config.include_dirs:
        flags.append(f"-I{include_dir}")
    for define in config.defines:
        flags.append(f"-D{define}")
    for undef in config.undefs:
        flags.append(f"-U{undef}")
    flags.extend(_std_arg(language, config.std))
    flags.extend(config.compiler_args)
    return flags


def build_direct_preprocess_invocation(
    source_path: str | Path,
    *,
    language: str,
    config: PreprocessingConfig,
) -> CompilerInvocation:
    """Build a direct compiler-preprocessor invocation for one source path."""
    if not config.compiler:
        raise PreprocessingError("--preprocess compiler requires --compiler with an exact executable")

    source = Path(source_path)
    argv = [config.compiler, "-E"]
    if language == "fortran":
        argv.append("-cpp")
    elif language == "c":
        argv.extend(["-x", "c"])
    else:
        raise PreprocessingError(f"compiler preprocessing is not supported for language {language!r}")
    argv.extend(_common_compiler_flags(config, language))
    argv.append(str(source))
    return CompilerInvocation(argv=argv)


def _compile_command_arguments(entry: dict) -> list[str]:
    """Return argv from a compile_commands.json entry."""
    if isinstance(entry.get("arguments"), list):
        return [str(arg) for arg in entry["arguments"]]
    command = entry.get("command")
    if isinstance(command, str):
        return shlex.split(command)
    raise PreprocessingError("compile_commands entry must contain 'arguments' or 'command'")


def _entry_file_path(entry: dict) -> Path:
    """Return the absolute source path for a compile database entry."""
    directory = Path(str(entry.get("directory") or "."))
    file_path = Path(str(entry.get("file") or ""))
    if not file_path:
        raise PreprocessingError("compile_commands entry is missing 'file'")
    return file_path if file_path.is_absolute() else directory / file_path


def _matches_compile_entry(entry: dict, source_path: Path) -> bool:
    """Return whether a compile database entry describes `source_path`."""
    entry_path = _entry_file_path(entry)
    try:
        return entry_path.resolve() == source_path.resolve()
    except OSError:
        return entry_path == source_path or entry_path.name == source_path.name


def _load_compile_command_entry(compile_commands: str | Path, source_path: str | Path) -> dict:
    """Load the compile database entry for one source path."""
    database_path = Path(compile_commands)
    source = Path(source_path)
    try:
        entries = json.loads(database_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PreprocessingError(f"cannot read compile commands file {database_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PreprocessingError(f"invalid compile commands JSON {database_path}: {exc}") from exc
    if not isinstance(entries, list):
        raise PreprocessingError("compile_commands JSON must contain a list of entries")

    matches = [entry for entry in entries if isinstance(entry, dict) and _matches_compile_entry(entry, source)]
    if not matches:
        raise PreprocessingError(f"no compile_commands entry found for {source}")
    if len(matches) > 1:
        raise PreprocessingError(f"multiple compile_commands entries found for {source}; pass --compiler explicitly")
    return matches[0]


def _is_source_arg(arg: str, entry_source: Path) -> bool:
    """Return whether an argv item is the compiled source path."""
    path = Path(arg)
    if path.suffix.lower() not in _SOURCE_SUFFIXES:
        return False
    if path == entry_source or path.name == entry_source.name:
        return True
    try:
        return path.resolve() == entry_source.resolve()
    except OSError:
        return False


def _filter_compile_args(args: Sequence[str], entry_source: Path) -> list[str]:
    """Remove compile-only/output/source args while preserving API flags."""
    filtered: list[str] = []
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in _COMPILE_ONLY_FLAGS:
            index += 1
            continue
        if arg in _SKIP_VALUE_FLAGS:
            index += 2
            continue
        if any(arg.startswith(prefix) and arg != prefix for prefix in _SKIP_PREFIX_FLAGS):
            index += 1
            continue
        if _is_source_arg(arg, entry_source):
            index += 1
            continue
        filtered.append(arg)
        index += 1
    return filtered


def build_compile_commands_invocation(
    source_path: str | Path,
    *,
    config: PreprocessingConfig,
) -> CompilerInvocation:
    """Build a C preprocessing command from `compile_commands.json`."""
    if not config.compile_commands:
        raise PreprocessingError("compile command database path is missing")
    entry = _load_compile_command_entry(config.compile_commands, source_path)
    argv = _compile_command_arguments(entry)
    if not argv:
        raise PreprocessingError("compile_commands entry has an empty command")

    directory = str(entry.get("directory") or ".")
    entry_source = _entry_file_path(entry)
    compiler = config.compiler or argv[0]
    filtered_args = _filter_compile_args(argv[1:], entry_source)
    command = [compiler, "-E", *_common_compiler_flags(config, "c"), *filtered_args, str(entry_source)]
    return CompilerInvocation(argv=command, cwd=directory, compile_commands_entry=entry)


def build_preprocess_invocation(
    source_path: str | Path,
    *,
    language: str,
    config: PreprocessingConfig,
) -> CompilerInvocation:
    """Build the compiler-preprocessor invocation for one source path."""
    if config.compile_commands:
        if language != "c":
            raise PreprocessingError("--compile-commands is only supported for --language c")
        return build_compile_commands_invocation(source_path, config=config)
    return build_direct_preprocess_invocation(source_path, language=language, config=config)


def run_compiler_preprocessor_with_recipe(
    source_path: str | Path,
    *,
    language: str,
    config: PreprocessingConfig,
) -> tuple[str, PreprocessingRecipe]:
    """Run compiler preprocessing and return source text plus its exact recipe."""
    invocation = build_preprocess_invocation(source_path, language=language, config=config)
    try:
        completed = subprocess.run(
            invocation.argv,
            cwd=invocation.cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise PreprocessingError(
            f"failed to run compiler preprocessor {invocation.argv[0]!r}: {exc}"
        ) from exc

    if completed.returncode != 0:
        command = " ".join(shlex.quote(arg) for arg in invocation.argv)
        stderr = completed.stderr.strip()
        detail = f": {stderr}" if stderr else ""
        raise PreprocessingError(f"compiler preprocessing failed for {source_path} with `{command}`{detail}")
    recipe = PreprocessingRecipe(
        mode=config.mode,
        language=language,
        source_path=str(source_path),
        compiler=invocation.argv[0],
        argv=list(invocation.argv),
        cwd=invocation.cwd,
        include_dirs=list(config.include_dirs),
        defines=list(config.defines),
        undefs=list(config.undefs),
        standard=config.std,
        compiler_args=list(config.compiler_args),
        compile_commands=config.compile_commands,
        compile_commands_entry=invocation.compile_commands_entry,
    )
    return completed.stdout, recipe


def run_compiler_preprocessor(
    source_path: str | Path,
    *,
    language: str,
    config: PreprocessingConfig,
) -> str:
    """Run the configured compiler preprocessor and return stdout source text."""
    source, _recipe = run_compiler_preprocessor_with_recipe(
        source_path,
        language=language,
        config=config,
    )
    return source


__all__ = (
    "CompilerInvocation",
    "PreprocessingConfig",
    "PreprocessingError",
    "PreprocessingRecipe",
    "build_compile_commands_invocation",
    "build_direct_preprocess_invocation",
    "build_preprocess_invocation",
    "run_compiler_preprocessor",
    "run_compiler_preprocessor_with_recipe",
    "validate_macro_name",
)
