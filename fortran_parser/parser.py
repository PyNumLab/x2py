# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import ast
from pathlib     import Path
from dataclasses import replace

from .lexer         import preprocess_lines
from .models        import FortranArgument, FortranBlockData, FortranDerivedType, FortranFile, FortranInterface, FortranModule, FortranParseError, FortranProcedureSignature, FortranProgram, FortranProject, FortranSubmodule, FortranUseMapping, FortranVariable
from .type_resolver import extract_kind_from_type_spec
from .utils         import split_csv

"""
Parser architecture quick guide
===============================

This module is intentionally split into two layers:

1) Module-level helper functions
   - Pure helpers for lexical checks, declaration parsing utilities,
     shape/kind resolution, diagnostics, and dependency ordering.

2) `FortranParser`
   - Stateful orchestration layer that runs block parsers and aggregates
     file/project models.

Recommended reading order for maintainers:
- Start from `FortranParser.parse_file` / `parse_project`
- Then read the high-level unit parsers at the top of the class
- Then drill into `*_impl` implementations and low-level helpers

`FortranParser` class layout (top -> bottom):
- Public API: `__init__`, `parse_file`, `parse_project`, `assess_wrap_readiness`
- High-level unit dispatchers: programs/modules/submodules/interfaces/types/signatures
- Core implementations (`*_impl`) that perform scoped parsing
- Shared declaration/header helpers
- File/project assembly and readiness/report helpers
- Final module-level convenience wrappers using `_DEFAULT_PARSER`

Scoping model used throughout parsing:
- Module/submodule scope is tracked by current block headers (`module`,
  `submodule`) and closed on matching `end ...`.
- Procedure scope opens on `subroutine/function` headers and is finalized at
  matching `end subroutine/end function/end`.
- Interface scope is tracked with explicit depth counters, allowing nested
  procedure declarations to be marked as interface members.
- Type scope opens on derived-type start and splits into specification-part vs
  `contains` member-binding region until `end type`.
- Program/block-data scopes collect declaration sections and stop at block end.
- `contains` transitions each scope from declaration/spec-part into internal
  procedure/member regions, changing what is collected.
- Optional preprocessor scope (`#if/#ifdef/...`) controls active/inactive
  branches while collecting procedure signatures when macro selection is provided.
"""

_TYPE_RE = re.compile(r"^(integer|real|complex|logical|character|double\s+precision)\s*(\([^)]*\))?\s*(.*)$", re.IGNORECASE)
_CHAR_STAR_RE = re.compile(r"^character\s*\*\s*(?P<len>\([^)]*\)|\*|[A-Za-z_]\w*|\d+)\s*(?P<rest>.*)$", re.IGNORECASE)
_PROC_RE = re.compile(r"^(?P<prefix>(?:\w+\s+)*)subroutine\s+(?P<name>\w+)(?:\s*\((?P<args>[^)]*)\))?\s*(?P<tail>.*)$", re.IGNORECASE)
_FUNC_RE = re.compile(
    r"^(?P<prefix>.*?)\b"
    r"function\s+(?P<name>\w+)(?:\s*\((?P<args>[^)]*)\))?\s*(?P<tail>.*)$",
    re.IGNORECASE,
)
_RESULT_RE = re.compile(r"results?\s*\(\s*(?P<name>\w+)\s*\)", re.IGNORECASE)
_ATTR_PREFIX_WORDS = {"pure", "elemental", "recursive", "impure", "module"}

_BINDC_RE = re.compile(r"bind\s*\(\s*c\s*(?:,\s*name\s*=\s*['\"][^'\"]*['x\"])?\s*\)", re.IGNORECASE)
_USE_RE = re.compile(
    r"^use\s*(?:,\s*(?:intrinsic|non_intrinsic)\s*)?(?:::)?\s*(?P<module>\w+)\s*(?P<rest>,\s*.*)?$",
    re.IGNORECASE,
)
_INCLUDE_RE = re.compile(r"^(?:#\s*)?include\s*(?P<path>['\"][^'\"]+['\"])", re.IGNORECASE)
_IMPORT_RE = re.compile(r"^import\s*(?:::)?\s*(?P<symbols>.*)$", re.IGNORECASE)
_PARAM_RE = re.compile(
    r"^(integer|real|logical|character|complex)\s*(?:\([^)]*\))?\s*,\s*parameter\s*::\s*(?P<body>.*)$",
    re.IGNORECASE,
)
_LEGACY_PARAM_STMT_RE = re.compile(r"^parameter\s*\(\s*(?P<body>.*)\s*\)$", re.IGNORECASE)
_DERIVED_TYPE_RE = re.compile(r"^type\s*(?P<attrs>(?:,\s*[^:]+)?)::\s*(?P<name>\w+)$", re.IGNORECASE)
_TYPE_FIELD_RE = re.compile(r"^type\s*\(\s*(?P<dtype>\w+)\s*\)\s*(?P<attrs>.*)$", re.IGNORECASE)
_CLASS_FIELD_RE = re.compile(r"^class\s*\(\s*(?P<dtype>\w+)\s*\)\s*(?P<attrs>.*)$", re.IGNORECASE)
_PROC_BIND_RE = re.compile(r"^procedure\s*(?:,\s*[^:]*)?::\s*(?P<names>.*)$", re.IGNORECASE)
_PROC_DUMMY_RE = re.compile(r"^procedure\s*\(\s*(?P<iface>\w+)\s*\)\s*(?P<attrs>.*)$", re.IGNORECASE)
_MODULE_RE = re.compile(r"^module\s+(?P<name>\w+)\s*$", re.IGNORECASE)
_SUBMODULE_RE = re.compile(r"^submodule\s*\(\s*(?P<parent>[^)]+?)\s*\)\s*(?P<name>\w+)\s*$", re.IGNORECASE)
_MOD_PROC_IMPL_RE = re.compile(r"^module\s+procedure\s+(?P<name>\w+)\s*$", re.IGNORECASE)
_PROGRAM_RE = re.compile(r"^program\s+(?P<name>\w+)\s*$", re.IGNORECASE)
_BLOCK_DATA_RE = re.compile(r"^block\s+data(?:\s+(?P<name>\w+))?\s*$", re.IGNORECASE)
_INTRINSIC_KIND_MODULES = {"iso_c_binding", "iso_fortran_env"}
_KIND_EXPRESSION_INTRINSICS = {
    "kind",
    "len",
    "selected_char_kind",
    "selected_int_kind",
    "selected_real_kind",
}
_KIND_EXPRESSION_KEYWORDS = {"and", "or", "not", "true", "false"}

_UNSUPPORTED_PATTERNS = (
    re.compile(r"\bclass\s*\(\s*\*\s*\)", re.IGNORECASE),
    re.compile(r"\bselect\s+type\b", re.IGNORECASE),
    re.compile(r"\bcoarray\b|\[[^\]]*\]", re.IGNORECASE),
    re.compile(r"\bprocedure\s*,\s*pointer\b", re.IGNORECASE),
    re.compile(r"\btype\s*\(\s*c_ptr\s*\)", re.IGNORECASE),
)


_PreprocessedLines = list[tuple[str, int | None, str | None]]
_SourceOrLines = str | _PreprocessedLines


# -----------------------------------------------------------------------------
# Low-level syntax and declaration helpers
# -----------------------------------------------------------------------------

def _is_derived_type_block_start(line: str) -> bool:
    stripped = line.strip()
    lower = stripped.lower()
    if not lower.startswith("type"):
        return False
    if lower.startswith("type("):
        return False
    if _DERIVED_TYPE_RE.match(stripped):
        return True
    return bool(re.match(r"^type\s+\w+\s*$", stripped, re.IGNORECASE))



def _expect_single_parse_result(
    items: list,
    *,
    parser_name: str,
    entity_name: str,
    filename: str | None,
):
    """Return one parsed entity or raise when a singular parser contract is broken."""
    if len(items) == 1:
        return items[0]
    if not items:
        raise FortranParseError(
            f"{parser_name}() expected exactly one {entity_name}, but none were found",
            filename=filename,
            code="PARSE_WRONG_ENTRYPOINT",
        )
    raise FortranParseError(
        f"{parser_name}() expected exactly one {entity_name}, but found {len(items)}",
        filename=filename,
        code="PARSE_AMBIGUOUS_ENTRYPOINT",
    )

# -----------------------------------------------------------------------------
# Public entrypoints
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Source-form and implicit typing helpers
# -----------------------------------------------------------------------------

def _source_form(filename: str | None) -> str:
    if not filename:
        return "unknown"
    ext = Path(filename).suffix.lower()
    if ext in {".f", ".for", ".ftn", ".f77"}:
        return "f77"
    if ext in {".f90", ".f95", ".f03", ".f08"}:
        return "modern"
    return "unknown"


def _infer_implicit_base_type(symbol_name: str) -> str:
    first = symbol_name.strip()[:1].lower()
    if "i" <= first <= "n":
        return "integer"
    return "real"


def _find_legacy_star_kind(type_left: str) -> tuple[str, str] | None:
    m = re.match(r"^(integer|real|complex|logical|character)\s*\*\s*([0-9]+)\b", type_left, re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower(), m.group(2)


def _parse_type_prefix(prefix: str) -> tuple[str, str | None] | None:
    txt = prefix.strip()
    if not txt:
        return None
    star_kind = _find_legacy_star_kind(txt)
    if star_kind:
        base, kind = star_kind
        return base, kind
    cm = _CHAR_STAR_RE.match(txt)
    if cm:
        raw_len = cm.group("len").strip()
        char_kind = raw_len[1:-1].strip() if raw_len.startswith("(") and raw_len.endswith(")") else raw_len
        return "character", char_kind
    tm = _TYPE_RE.match(txt)
    if tm:
        base = tm.group(1).lower()
        if base == "double precision":
            base = "real"
        type_spec = (tm.group(2) or "").strip()
        kind = extract_kind_from_type_spec(base, type_spec)
        if kind is None and type_spec and base != "character":
            kind = type_spec[1:-1].strip()
        return base, kind
    derived = _TYPE_FIELD_RE.match(txt)
    if derived:
        return "derived", derived.group("dtype")
    class_derived = _CLASS_FIELD_RE.match(txt)
    if class_derived:
        return "derived", class_derived.group("dtype")
    return None  # pragma: no cover - unsupported prefixes are rejected by public grammar.


# -----------------------------------------------------------------------------
# Preprocessor and conditional-compilation helpers
# -----------------------------------------------------------------------------

def _preprocessor_conditions_overlap(c1: frozenset[str], c2: frozenset[str]) -> bool:
    """Return True when two preprocessor condition sets may both be active."""
    if not c1 or not c2:
        return True
    values: dict[str, str] = {}
    for token in c1 | c2:
        group, _, branch = token.partition(":")
        if group in values and values[group] != branch:
            return False
        values[group] = branch
    return True


def _normalize_macro_defines(macro_defines: set[str] | dict[str, int | bool | str] | None) -> set[str]:
    if not macro_defines:
        return set()
    if isinstance(macro_defines, dict):
        out = set()
        for k, v in macro_defines.items():
            if str(v).strip() not in {"", "0", "false", "False"}:
                out.add(str(k).lower())
        return out
    return {str(x).lower() for x in macro_defines}


def _eval_cpp_expr(expr: str, macro_names: set[str]) -> bool:
    """Evaluate a small C-preprocessor boolean expression."""
    txt = expr.strip()
    if not txt:  # pragma: no cover - bare #if is not valid Fortran preprocessing input.
        return False
    txt = re.sub(r"defined\s*\(\s*([A-Za-z_]\w*)\s*\)", lambda m: str(m.group(1).lower() in macro_names), txt)
    txt = re.sub(r"\bdefined\s+([A-Za-z_]\w*)\b", lambda m: str(m.group(1).lower() in macro_names), txt)
    def _ident_to_bool(m: re.Match[str]) -> str:
        token = m.group(1)
        if token in {"True", "False", "and", "or", "not"}:
            return token
        return "True" if token.lower() in macro_names else "False"
    txt = re.sub(r"\b([A-Za-z_]\w*)\b", _ident_to_bool, txt)
    txt = txt.replace("&&", " and ").replace("||", " or ")
    txt = re.sub(r"(?<![=!<>])!(?!=)", " not ", txt)
    txt = re.sub(r"\b0\b", "False", txt)
    txt = re.sub(r"\b1\b", "True", txt)
    try:
        node = ast.parse(txt, mode="eval")
        return bool(eval(compile(node, "<cpp-expr>", "eval"), {"__builtins__": {}}, {}))
    except Exception:
        return False


# -----------------------------------------------------------------------------
# Symbol, import, and diagnostic utilities
# -----------------------------------------------------------------------------

def _looks_like_existing_source_path(source: str | Path) -> bool:
    """Return True when ``source`` names a readable source file path."""
    if not isinstance(source, (str, Path)):
        return False
    text = str(source)
    if "\n" in text or "\r" in text:
        return False
    return Path(text).is_file()


def _split_submodule_parent(parent_spec: str) -> tuple[str, str | None]:
    parts = [p.strip() for p in parent_spec.split(":", 1)]
    if len(parts) == 2:
        ancestor, parent = parts
        return parent, ancestor
    return parts[0], None


def _visible_import_modules(symbol: str, uses: dict[str, list[FortranUseMapping]]) -> list[str]:
    """Return imported modules that could provide ``symbol`` under Fortran USE rules."""
    wanted = symbol.lower()
    providers: list[str] = []
    for module_name, only_symbols in uses.items():
        normalized_only = [sym.local_name.lower() for sym in only_symbols]
        if not normalized_only or wanted in normalized_only:
            providers.append(module_name)
    return providers


def _kind_expression_symbols(expr: str | None) -> set[str]:
    """Return identifier symbols referenced by a kind/len expression."""
    if expr is None:
        return set()
    text = expr.strip()
    if not text or text == "*":
        return set()
    parts: list[str] = []
    for item in split_csv(text):
        token = item.strip()
        if not token:
            continue
        key, sep, value = token.partition("=")
        if sep and key.strip().lower() in {"kind", "len"}:
            parts.append(value.strip())
        else:
            parts.append(token)
    normalized = " ".join(parts)
    normalized = re.sub(
        r"(?<![A-Za-z_])(?:\d+(?:\.\d*)?|\.\d+)(?:[deDE][+-]?\d+)?",
        " ",
        normalized,
    )
    ignored = _KIND_EXPRESSION_INTRINSICS | _KIND_EXPRESSION_KEYWORDS
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", normalized)
        if token.lower() not in ignored
    }


def _kind_symbol_visible_from_intrinsic_use(symbol: str, uses: dict[str, list[FortranUseMapping]]) -> bool:
    lowered = symbol.lower()
    for module_name, mappings in uses.items():
        if module_name.lower() not in _INTRINSIC_KIND_MODULES:
            continue
        if not mappings or lowered in {mapping.local_name.lower() for mapping in mappings}:
            return True
    return False


def _kind_symbol_visible_from_module_params(
    symbol: str,
    uses: dict[str, list[FortranUseMapping]],
    module_params: dict[str, dict[str, str]],
) -> bool:
    lowered = symbol.lower()
    for module_name, mappings in uses.items():
        params = module_params.get(module_name.lower(), {})
        if not params:
            continue
        if not mappings and lowered in params:
            return True
        for mapping in mappings:
            if mapping.local_name.lower() != lowered:
                continue
            if mapping.source.lower() in params:
                return True
    return False


def _kind_symbol_is_known(
    symbol: str,
    *,
    owning_module: str | None,
    uses: dict[str, list[FortranUseMapping]],
    local_symbols: set[str],
    module_params: dict[str, dict[str, str]],
) -> bool:
    """Check whether a symbolic kind is declared locally or in parsed imports."""
    lowered = symbol.lower()
    if lowered in local_symbols:
        return True
    if owning_module and lowered in module_params.get(owning_module.lower(), {}):
        return True
    if _kind_symbol_visible_from_module_params(symbol, uses, module_params):
        return True
    if _kind_symbol_visible_from_intrinsic_use(symbol, uses):
        return True
    return False


def _collect_unresolved_derived_type_diagnostics(
    signatures: list[FortranProcedureSignature],
    types: list[FortranDerivedType],
    modules: list[FortranModule],
) -> tuple[list[dict], list[dict]]:
    """Find derived-type references that are not defined in the parsed source."""
    defined_types = {dtype.name.lower() for dtype in types}
    module_uses = {mod.name.lower(): mod.uses for mod in modules}
    unresolved_args: list[dict] = []
    unresolved_fields: list[dict] = []

    def _missing_type(kind: str | None) -> bool:
        return bool(kind) and kind.lower() not in defined_types

    for sig in signatures:
        for arg in sig.arguments:
            if arg.base_type == "derived" and _missing_type(arg.kind):
                unresolved_args.append({
                    "procedure": sig.name,
                    "module": sig.module,
                    "argument": arg.name,
                    "type": arg.kind,
                    "import_modules": _visible_import_modules(arg.kind or "", sig.uses),
                })
        if sig.result and sig.result.base_type == "derived" and _missing_type(sig.result.kind):
            unresolved_args.append({
                "procedure": sig.name,
                "module": sig.module,
                "argument": sig.result.name,
                "type": sig.result.kind,
                "import_modules": _visible_import_modules(sig.result.kind or "", sig.uses),
            })

    for dtype in types:
        uses = module_uses.get(dtype.module.lower(), {}) if dtype.module else {}
        for field in dtype.fields:
            if field.base_type == "derived" and _missing_type(field.kind):
                unresolved_fields.append({
                    "type_owner": dtype.name,
                    "module": dtype.module,
                    "field": field.name,
                    "type": field.kind,
                    "import_modules": _visible_import_modules(field.kind or "", uses),
                })

    return unresolved_args, unresolved_fields


def _collect_unresolved_kind_diagnostics(
    signatures: list[FortranProcedureSignature],
    types: list[FortranDerivedType],
    modules: list[FortranModule],
    module_params: dict[str, dict[str, str]],
) -> tuple[list[dict], list[dict]]:
    """Find symbolic intrinsic kind references not declared in parsed source/imports."""
    module_uses = {mod.name.lower(): mod.uses for mod in modules}
    unresolved_args: list[dict] = []
    unresolved_fields: list[dict] = []

    for sig in signatures:
        local_symbols = {name.lower() for name, var in sig.variables.items() if var.value is not None}

        def _append_unresolved_arg(arg: FortranArgument) -> None:
            for symbol in sorted(_kind_expression_symbols(arg.kind)):
                if _kind_symbol_is_known(
                    symbol,
                    owning_module=sig.module,
                    uses=sig.uses,
                    local_symbols=local_symbols,
                    module_params=module_params,
                ):
                    continue
                item = {
                    "procedure": sig.name,
                    "module": sig.module,
                    "argument": arg.name,
                    "kind": symbol,
                    "import_modules": _visible_import_modules(symbol, sig.uses),
                }
                if (arg.kind or "").strip().lower() != symbol:
                    item["kind_expression"] = arg.kind
                unresolved_args.append(item)

        for arg in sig.arguments:
            if arg.base_type != "derived":
                _append_unresolved_arg(arg)
        if sig.result and sig.result.base_type != "derived":
            _append_unresolved_arg(sig.result)

    for dtype in types:
        uses = module_uses.get(dtype.module.lower(), {}) if dtype.module else {}
        local_symbols: set[str] = set()
        for field in dtype.fields:
            if field.base_type == "derived":
                continue
            for symbol in sorted(_kind_expression_symbols(field.kind)):
                if _kind_symbol_is_known(
                    symbol,
                    owning_module=dtype.module,
                    uses=uses,
                    local_symbols=local_symbols,
                    module_params=module_params,
                ):
                    continue
                item = {
                    "type_owner": dtype.name,
                    "module": dtype.module,
                    "field": field.name,
                    "kind": symbol,
                    "import_modules": _visible_import_modules(symbol, uses),
                }
                if (field.kind or "").strip().lower() != symbol:
                    item["kind_expression"] = field.kind
                unresolved_fields.append(item)

    return unresolved_args, unresolved_fields


def _build_wrap_blockers(
    *,
    signatures: list[FortranProcedureSignature],
    unsupported: list[dict],
    missing_decl_args: list[str],
    unresolved_derived_args: list[dict],
    unresolved_derived_fields: list[dict],
    unresolved_kind_args: list[dict],
    unresolved_kind_fields: list[dict],
) -> list[dict]:
    """Create explicit, user-facing reasons why a source is not wrap-ready."""
    blockers: list[dict] = []
    if not signatures:
        blockers.append({
            "code": "no_signatures",
            "message": "No procedure signatures were found to wrap.",
            "items": [],
        })
    if unsupported:
        blockers.append({
            "code": "unsupported_constructs",
            "message": "Unsupported Fortran constructs were found.",
            "items": unsupported,
        })
    if missing_decl_args:  # pragma: no cover - public parsing resolves or rejects declarations before readiness.
        blockers.append({
            "code": "unknown_argument_types",
            "message": "Some procedure arguments have no resolved declaration/type.",
            "items": missing_decl_args,
        })
    if unresolved_derived_args:
        blockers.append({
            "code": "unresolved_derived_type_arguments",
            "message": "Some derived-type procedure arguments refer to types missing from the parsed source.",
            "items": unresolved_derived_args,
        })
    if unresolved_derived_fields:
        blockers.append({
            "code": "unresolved_derived_type_fields",
            "message": "Some derived-type fields refer to types missing from the parsed source.",
            "items": unresolved_derived_fields,
        })
    if unresolved_kind_args:
        blockers.append({
            "code": "unresolved_kind_arguments",
            "message": "Some procedure arguments use kind symbols missing from the parsed source/imports.",
            "items": unresolved_kind_args,
        })
    if unresolved_kind_fields:
        blockers.append({
            "code": "unresolved_kind_fields",
            "message": "Some derived-type fields use kind symbols missing from the parsed source/imports.",
            "items": unresolved_kind_fields,
        })
    return blockers

# -----------------------------------------------------------------------------
# Signature/shape evaluation and validation utilities
# -----------------------------------------------------------------------------

def collect_signature_shape_symbols(sig: FortranProcedureSignature) -> set[str]:
    """Collect identifier tokens referenced by argument shape expressions.

    Useful for callers that want to provide a dictionary of concrete sizes to
    `evaluate_signature_shapes`.
    """
    symbols: set[str] = set()
    for arg in sig.arguments:
        for dim in arg.shape:
            symbols.update(re.findall(r"\b[a-zA-Z_]\w*\b", dim))
    return {s.lower() for s in symbols}


def evaluate_signature_shapes(
    sig: FortranProcedureSignature,
    symbol_values: dict[str, int | str],
) -> FortranProcedureSignature:
    """Return a copy of `sig` with shapes rewritten using `symbol_values`.

    This does not mutate the input signature. Values are coerced to strings and
    applied case-insensitively. This is intended for consumers that know array
    extents at wrapper-generation time and want concrete dimension expressions.
    """
    normalized = {k.lower(): str(v) for k, v in symbol_values.items()}
    out = replace(sig)
    out.arguments = [replace(a) for a in sig.arguments]
    for arg in out.arguments:
        if arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, normalized) for dim in arg.shape]
    return out

# -----------------------------------------------------------------------------
# Procedure parsing helpers
# -----------------------------------------------------------------------------

def _validate_no_duplicate_arg_names(
    args: list[FortranArgument],
    proc_name: str,
    filename: str | None,
    line_number: int | None = None,
    source_line: str | None = None,
) -> None:
    seen: set[str] = set()
    for arg in args:
        key = arg.name.lower()
        if key in seen:
            raise FortranParseError(
                f"Duplicate argument name '{arg.name}' in procedure '{proc_name}'.",
                filename=filename,
                line_number=line_number,
                source_line=source_line,
            )
        seen.add(key)

def _attrs(prefix: str, tail: str) -> list[str]:
    attrs = [t.lower() for t in prefix.split() if t.lower() in _ATTR_PREFIX_WORDS]
    if _BINDC_RE.search(tail):
        attrs.append("bind(c)")
    return attrs


def _looks_like_procedure_header(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    if lowered.startswith(("end ", "call ")):
        return False
    return bool(re.search(r"(?:^|[\s,])(?:subroutine|function)\s+[A-Za-z_]\w*", stripped, re.IGNORECASE))


def _is_openmp_directive(line: str) -> bool:
    return line.lstrip().lower().startswith("!$omp")


def _is_openmp_declarative_directive(line: str) -> bool:
    directive = line.lstrip()[5:].strip().lower() if _is_openmp_directive(line) else ""
    return directive.startswith(
        (
            "threadprivate",
            "declare simd",
            "declare target",
            "declare reduction",
            "requires",
            "declare mapper",
        )
    )


def _looks_like_declaration_or_spec(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    if _is_openmp_directive(stripped):
        return _is_openmp_declarative_directive(stripped)
    first_match = re.match(r"([a-z_][a-z0-9_]*)", lowered)
    first = first_match.group(1) if first_match else lowered.split(None, 1)[0].rstrip(",")
    non_decl_starts = {
        "do", "if", "where", "call", "select", "case", "allocate", "deallocate",
        "print", "write", "read", "return", "stop", "cycle", "exit", "continue",
        "end", "else", "elseif", "contains", "goto", "go", "format",
    }
    if first in non_decl_starts:
        return False
    if "::" in stripped or "," in stripped:
        return True
    return bool(re.match(r"^[A-Za-z_]\w+\s+[A-Za-z_]\w*", stripped))


def _is_ignored_spec_statement(line: str) -> bool:
    return bool(
        _INCLUDE_RE.match(line)
        or re.match(
            r"^(implicit|save|common|data|equivalence|external|intrinsic|parameter|namelist|entry)\b",
            line,
            flags=re.IGNORECASE,
        )
    )


def _parse_use_statement(line: str) -> tuple[str, list[FortranUseMapping]] | None:
    match = _USE_RE.match(line)
    if not match:
        return None
    rest = (match.group("rest") or "").strip()
    if not rest:
        return match.group("module"), []
    payload = rest.lstrip(",").strip()
    only_match = re.match(r"^only\s*:\s*(?P<symbols>.*)$", payload, re.IGNORECASE)
    if only_match:
        payload = only_match.group("symbols")
    mappings: list[FortranUseMapping] = []
    for item in split_csv(payload):
        token = item.strip()
        if not token:
            continue
        if "=>" in token:
            target, source = [part.strip() for part in token.split("=>", 1)]
        else:
            source = token
            target = None
        mappings.append(FortranUseMapping(source=source, target=target))
    return match.group("module"), mappings

def _is_executable_statement_start(line: str) -> bool:
    stripped = line.strip()
    if not stripped:  # pragma: no cover - callers skip blank lines before executable checks.
        return False
    lowered = stripped.lower()
    if _is_openmp_directive(stripped):
        return not _is_openmp_declarative_directive(stripped)
    first_match = re.match(r"([a-z_][a-z0-9_]*)", lowered)
    first = first_match.group(1) if first_match else lowered.split(None, 1)[0]
    if first.isdigit():
        return False
    executable_starts = {
        "do", "if", "where", "call", "select", "case", "allocate", "deallocate",
        "print", "write", "read", "return", "stop", "cycle", "exit", "continue",
        "goto", "go", "open", "close", "rewind", "backspace", "inquire", "flush",
        "wait", "nullify", "associate", "block", "forall", "error", "pause",
    }
    if first in executable_starts:
        return True
    if _LEGACY_PARAM_STMT_RE.match(stripped):
        return False
    if "=" in stripped and "::" not in stripped:
        # Distinguish assignment/statements from declaration lines carrying
        # type specs with named arguments, e.g.:
        #   integer ( kind = 4 ) i
        #   character ( len = * ) s
        if _CHAR_STAR_RE.match(stripped) or _TYPE_RE.match(stripped) or _TYPE_FIELD_RE.match(stripped) or _CLASS_FIELD_RE.match(stripped):
            return False
        # Covers assignment and statement functions in execution part.
        return True
    return False


def _var(entry: str):
    e = entry.strip()
    if not e:  # pragma: no cover - split_csv omits empty declaration entities for valid declarations.
        return "", []
    if "=" in e:
        # Keep only the declared entity name/shape; drop initializer text.
        e = e.split("=", 1)[0].strip()
    if "(" in e and e.endswith(")"):
        name = e[:e.find("(")].strip()
        return name, split_csv(e[e.find("(")+1:-1])
    return e, []


def _split_dim_bounds(dim: str) -> tuple[str | None, str | None]:
    part = dim.strip()
    if not part:  # pragma: no cover - empty dimensions are invalid Fortran and not emitted by split_csv.
        return None, None
    if ':' not in part:
        return "1", part
    lo, hi = part.split(':', 1)
    lo = lo.strip() or None
    hi = hi.strip() or None
    return lo, hi


def _extract_bounds(shape: list[str]) -> tuple[list[str | None], list[str | None]]:
    lbounds: list[str | None] = []
    ubounds: list[str | None] = []
    for dim in shape:
        lo, hi = _split_dim_bounds(dim)
        lbounds.append(lo)
        ubounds.append(hi)
    return lbounds, ubounds


def _apply(arg: FortranArgument, meta: dict, shape: list[str]):
    arg.base_type = meta["base_type"]
    arg.kind = meta["kind"]
    arg.intent = meta["intent"]
    arg.optional = meta["optional"]
    arg.pass_by_value = meta["value"]
    arg.allocatable = meta["allocatable"]
    arg.pointer = meta["pointer"]
    arg.is_parameter = meta["parameter"]
    if shape:
        arg.shape = shape
        arg.rank = len(shape)
    else:
        arg.shape = list(meta["shape"])
        arg.rank = meta["rank"]
    arg.lbound, arg.ubound = _extract_bounds(arg.shape)


def _new_decl_meta(base_type: str, kind: str | None) -> dict:
    return {
        "base_type": base_type,
        "kind": kind,
        "rank": 0,
        "shape": [],
        "intent": "unknown",
        "optional": False,
        "value": False,
        "allocatable": False,
        "pointer": False,
        "external": False,
        "parameter": False,
    }


def _apply_decl_attrs(meta: dict, attrs: list[str], *, include_intent: bool = False) -> None:
    for a in attrs:
        la = a.lower()
        if include_intent and la.startswith("intent") and "(" in la and ")" in la:
            meta["intent"] = la.split("(", 1)[1].rsplit(")", 1)[0].strip()
        elif la == "optional":
            meta["optional"] = True
        elif la == "value":
            meta["value"] = True
        elif la == "allocatable":
            meta["allocatable"] = True
        elif la == "pointer":
            meta["pointer"] = True
        elif la == "external":
            meta["external"] = True
        elif la == "parameter":
            meta["parameter"] = True
        elif la.startswith("dimension") and "(" in a and ")" in a:
            shape = split_csv(a[a.find("(") + 1 : a.rfind(")")])
            meta["shape"] = shape
            meta["rank"] = len(shape)


def _normalize_declared_name(name: str, meta: dict) -> str:
    normalized_name = re.sub(r"^\*\s*[0-9]+\s*", "", name).strip()
    if meta["base_type"] == "character" and "*" in normalized_name:
        # Legacy CHARACTER declarations may carry entity-local length
        # specifiers (e.g. NAME*(*) or SUBNAM*6). Strip the `*len`
        # suffix so symbol lookup matches procedure arguments.
        normalized_name = normalized_name.split("*", 1)[0].strip()
    return normalized_name


def _strip_legacy_star_kind_prefix(left: str) -> str:
    return re.sub(
        r"^(integer|real|complex|logical)\s*\*\s*[0-9]+\s*",
        "",
        left,
        flags=re.IGNORECASE,
    ).strip()


def _legacy_declaration_entities(left: str, meta: dict) -> str | None:
    """Return the entity-list tail from a declaration without `::`."""
    char_star = _CHAR_STAR_RE.match(left)
    if char_star:
        return (char_star.group("rest") or "").strip().lstrip(", ")

    star_kind = _find_legacy_star_kind(left)
    if star_kind and meta["base_type"] != "character":
        return _strip_legacy_star_kind_prefix(left).lstrip(", ")

    tm = _TYPE_RE.match(left)
    if tm:
        return tm.group(3).strip().lstrip(", ")

    derived = _TYPE_FIELD_RE.match(left) or _CLASS_FIELD_RE.match(left)
    if derived:
        return (derived.group("attrs") or "").strip().lstrip(", ")

    procm = _PROC_DUMMY_RE.match(left)
    if procm:
        tail = (procm.group("attrs") or "").strip()
        if tail and not tail.startswith(","):
            return tail
    return None  # pragma: no cover - invalid legacy declaration tails are ignored.


def _parse_common_declaration_left(
    left: str,
    *,
    filename: str | None,
    line_number: int | None = None,
    source_line: str | None = None,
    parse_character_star: bool = True,
) -> tuple[dict, list[str]] | None:
    star_kind = _find_legacy_star_kind(left)
    char_star = _CHAR_STAR_RE.match(left) if parse_character_star else None
    if char_star:
        kind = char_star.group("len").strip()
        if kind.startswith("(") and kind.endswith(")"):
            kind = kind[1:-1].strip()
        trailing = (char_star.group("rest") or "").strip().lstrip(", ")
        return _new_decl_meta("character", kind), split_csv(trailing)
    if star_kind:
        base, kind = star_kind
        tail = _strip_legacy_star_kind_prefix(left)
        attrs = split_csv(tail.lstrip(", ")) if tail.startswith(",") else []
        return _new_decl_meta(base.lower(), kind), attrs

    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
    class_derived = _CLASS_FIELD_RE.match(left)
    if tm:
        base = tm.group(1).lower()
        if base == "double precision":
            base = "real"
        type_spec = (tm.group(2) or "").strip()
        return _new_decl_meta(base, extract_kind_from_type_spec(base, type_spec)), split_csv(tm.group(3).strip().lstrip(", "))
    if derived or class_derived:
        decl = derived or class_derived
        return _new_decl_meta("derived", decl.group("dtype")), split_csv((decl.group("attrs") or "").strip().lstrip(", "))
    if re.match(r"^procedure\s*\(", left, re.IGNORECASE):
        procm = _PROC_DUMMY_RE.match(left)
        iface = procm.group("iface").lower() if procm else None
        return _new_decl_meta("procedure", iface), split_csv((procm.group("attrs") if procm else "").strip().lstrip(", "))
    return None


def _parse_common_declaration_line(
    line: str,
    *,
    filename: str | None,
    line_number: int | None = None,
    source_line: str | None = None,
    include_intent: bool = False,
    parse_character_star: bool = True,
) -> tuple[dict, str] | None:
    if "::" in line:
        left, right = [x.strip() for x in line.split("::", 1)]
        has_separator = True
    else:
        left = line.strip()
        right = ""
        has_separator = False

    parsed_decl = _parse_common_declaration_left(
        left,
        filename=filename,
        line_number=line_number,
        source_line=source_line,
        parse_character_star=parse_character_star,
    )
    if parsed_decl is None:
        return None

    meta, attrs = parsed_decl
    if not has_separator:
        legacy_right = _legacy_declaration_entities(left, meta)
        if legacy_right is not None:
            right = legacy_right
            attrs = []

    _apply_decl_attrs(meta, attrs, include_intent=include_intent)
    return meta, right

# -----------------------------------------------------------------------------
# Validation and finalization
# -----------------------------------------------------------------------------


def _validate_all_args_declared(sig: FortranProcedureSignature, filename: str | None, *, explicit_result: bool) -> None:
    for arg in sig.arguments:
        if arg.base_type == "unknown":
            raise FortranParseError(
                f"Argument '{arg.name}' in procedure '{sig.name}' has no type declaration (implicit none is active).",
                filename=filename,
            )
    if sig.kind == "function" and sig.result and sig.result.base_type == "unknown":
        if explicit_result:
            raise FortranParseError(
                f"Unknown datatype for function result '{sig.result.name}' in procedure '{sig.name}'.",
                filename=filename,
            )
        raise FortranParseError(
            f"Function result '{sig.result.name}' in procedure '{sig.name}' has no type declaration (implicit none is active).",
            filename=filename,
        )


def _validate_function_result(sig: FortranProcedureSignature, filename: str | None) -> None:
    if sig.result is None:  # pragma: no cover - function signatures are constructed with result objects.
        raise FortranParseError(
            f"Function '{sig.name}' has no result variable.",
            filename=filename,
        )
    result_name = sig.result.name.lower()
    func_name = sig.name.lower()
    for arg in sig.arguments:
        if arg.name.lower() == result_name and result_name != func_name:
            raise FortranParseError(
                f"Function result variable '{sig.result.name}' in function '{sig.name}' shadows an argument name.",
                filename=filename,
            )


def _validate_variable_declarations(
    variables: list[FortranVariable],
    *,
    owner_kind: str,
    owner_name: str | None,
    filename: str | None,
) -> None:
    seen: dict[str, FortranArgument] = {}
    display_name = owner_name or "<unnamed>"
    for var in variables:
        key = var.name.lower()
        if not re.match(r"^[a-z_]\w*$", key, re.IGNORECASE):  # pragma: no cover - parser normalizes valid Fortran identifiers.
            continue
        prev = seen.get(key)
        if prev is not None:
            if (
                prev.base_type != var.base_type
                or prev.kind != var.kind
                or prev.rank != var.rank
                or tuple(prev.shape) != tuple(var.shape)
            ):
                raise FortranParseError(
                    f"Duplicate variable '{var.name}' in {owner_kind} '{display_name}'.",
                    filename=filename,
                )
            continue  # pragma: no cover - exact duplicate declarations are invalid Fortran and tolerated defensively.
        seen[key] = var


def _variable_scope_label(scope) -> tuple[str, str | None]:
    if isinstance(scope, FortranSubmodule):
        return "submodule", scope.name
    if isinstance(scope, FortranProgram):
        return "program", scope.name
    if isinstance(scope, FortranBlockData):
        return "block data", scope.name
    return "module", scope.name


def _validate_module_variables(module: FortranModule | FortranSubmodule, filename: str | None) -> None:
    owner_kind, owner_name = _variable_scope_label(module)
    _validate_variable_declarations(
        module.variables,
        owner_kind=owner_kind,
        owner_name=owner_name,
        filename=filename,
    )


def _apply_module_visibility(module: FortranModule, filename: str | None) -> None:
    public_set = {s.lower() for s in module.public_symbols}
    private_set = {s.lower() for s in module.private_symbols}
    for var in module.variables:
        name = var.name.lower()
        if name in private_set:
            var.visibility = "private"
        elif name in public_set:
            var.visibility = "public"
        else:
            var.visibility = module.default_visibility
        if var.base_type == "unknown":  # pragma: no cover - unknown module declarations raise before finalization.
            raise FortranParseError(
                f"Unknown type for variable '{var.name}' in module '{module.name}'.",
                filename=filename,
            )


def _validate_derived_type_fields(dtype: FortranDerivedType, filename: str | None) -> None:
    seen: set[str] = set()
    for f in dtype.fields:
        if f.name.lower() in seen:
            raise FortranParseError(
                f"Duplicate field '{f.name}' in derived type '{dtype.name}'.",
                filename=filename,
            )
        seen.add(f.name.lower())
        if f.base_type == "unknown":  # pragma: no cover - unknown type fields raise before finalization.
            raise FortranParseError(
                f"Unknown type for field '{f.name}' in derived type '{dtype.name}'.",
                filename=filename,
            )


def _finalize_proc(state: dict) -> FortranProcedureSignature:
    sig = state["signature"]
    symbols = state["symbols"]
    local_params = state.get("local_params", {})
    legacy_local_params = state.get("legacy_local_params", set())
    implicit_typed_symbols = state.get("implicit_typed_symbols", {})
    filename = state.get("filename")
    implicit_none = state.get("implicit_none", False)
    sig.variables = {}
    sig.arguments = [symbols.get(a.name.lower(), a) for a in sig.arguments]
    if sig.result:
        sig.result = symbols.get(sig.result.name.lower(), sig.result)

    _validate_no_duplicate_arg_names(
        sig.arguments,
        sig.name,
        filename,
        state.get("header_lineno"),
        state.get("header_source_line"),
    )

    # Safety check: if an argument has been explicitly declared in this
    # procedure, it must not remain unknown after declaration parsing.
    # This catches declaration-application regressions (e.g. legacy
    # star-kind list handling) while still allowing truly undeclared
    # arguments to be reported via readiness diagnostics.
    declared_symbols = state.get("typed_symbols", set())
    for arg in sig.arguments:
        if arg.name.lower() in declared_symbols and arg.base_type == "unknown":  # pragma: no cover - defensive parser invariant.
            raise FortranParseError(
                f"Failed to resolve declared argument '{arg.name}' in procedure '{sig.name}'.",
                filename=filename,
            )
    for arg in sig.arguments:
        if arg.kind:
            arg.kind = _resolve_kind_expression(arg.kind, local_params)
        if arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, local_params) for dim in arg.shape]
        if arg.base_type == "unknown" and not implicit_none:
            arg.base_type = _infer_implicit_base_type(arg.name)
    if sig.result and sig.result.kind:
        sig.result.kind = _resolve_kind_expression(sig.result.kind, local_params)
    relevant_params = _collect_relevant_local_params(sig, local_params)
    declared_local_types = state.get("declared_local_types", {})
    # Defensive reconciliation: some legacy declaration forms can be parsed into
    # `declared_local_types` before being matched back to argument symbols.
    # If an argument is still unknown but we have an exact-name local type
    # record, apply it before implicit-none validation to avoid false positives.
    for arg in sig.arguments:
        if arg.base_type != "unknown":
            continue
        inferred = declared_local_types.get(arg.name.lower())
        if not inferred:
            continue
        arg.base_type = inferred.get("base_type", arg.base_type)
        arg.kind = inferred.get("kind", arg.kind)

    if implicit_none and not sig.in_interface:
        _validate_all_args_declared(sig, filename, explicit_result=bool(state.get("explicit_result", False)))

    for name, value in relevant_params.items():
        if name.lower() in legacy_local_params:
            # Legacy PARAMETER (...) constants are declaration artifacts in
            # fixed-form sources; keep them available for compile-time
            # resolution but do not expose them as parsed procedure variables.
            continue
        local_decl = declared_local_types.get(name.lower(), {})
        sig.variables[name.lower()] = FortranVariable(
            name=name.lower(),
            base_type=local_decl.get("base_type", implicit_typed_symbols.get(name.lower(), "unknown")),
            kind=local_decl.get("kind"),
            value=_normalize_parameter_value(value),
            value_type="expression",
            is_parameter=True,
        )
    if sig.kind == "function" and sig.result and sig.result.base_type == "unknown":
        if not implicit_none:
            sig.result.base_type = _infer_implicit_base_type(sig.result.name)
        if sig.result.base_type == "unknown":  # pragma: no cover - implicit-none result validation handles public cases first.
            raise FortranParseError(
                f"Unknown datatype for function result '{sig.result.name}' in procedure '{sig.name}'.",
                filename=filename,
            )
    if sig.kind == "function":
        _validate_function_result(sig, filename)
    for symbol in sorted(state.get("imports", set())):
        attr = f"import({symbol})"
        if attr not in sig.attributes:
            sig.attributes.append(attr)
    sig.uses = dict(state["uses"])
    return replace(sig)

# -----------------------------------------------------------------------------
# Cross-file resolution helpers
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Compile-time expression and symbol resolution
# -----------------------------------------------------------------------------

def _resolve_module_parameter_values(module_params: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    resolved: dict[str, dict[str, str]] = {}
    for module_name, params in module_params.items():
        resolved[module_name.lower()] = {
            name.lower(): _resolve_compile_time_expression(value, params)
            for name, value in params.items()
        }
    return resolved


def _resolve_signature_kinds(
    sig: FortranProcedureSignature,
    module_params: dict[str, dict[str, str]],
    *,
    resolve_shapes: bool = True,
) -> None:
    module_params = _resolve_module_parameter_values(module_params)
    symbol_to_value: dict[str, str] = {}
    if sig.module:
        symbol_to_value.update(module_params.get(sig.module.lower(), {}))
    for mod, mappings in sig.uses.items():
        params = module_params.get(mod.lower(), {})
        if not params:
            continue
        if not mappings:
            symbol_to_value.update(params)
            continue
        for mapping in mappings:
            source = mapping.source.lower()
            local = mapping.local_name.lower()
            if source in params:
                symbol_to_value[local] = params[source]
    for name, var in sig.variables.items():
        if var.value is not None:
            symbol_to_value.setdefault(name.lower(), var.value)
    sig.variables.update(_resolve_variables(symbol_to_value))
    for arg in sig.arguments:
        if arg.kind:
            arg.kind = _resolve_kind_expression(arg.kind, symbol_to_value)
        if resolve_shapes and arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, symbol_to_value) for dim in arg.shape]
    if sig.result and sig.result.kind:
        sig.result.kind = _resolve_kind_expression(sig.result.kind, symbol_to_value)


def _resolve_kind_expression(expr: str, symbols: dict[str, str]) -> str:
    resolved = _resolve_symbol_reference(expr, symbols)
    return _resolve_compile_time_expression(resolved, symbols)


def _resolve_symbol_reference(expr: str, symbols: dict[str, str]) -> str:
    out = expr.strip()
    seen: set[str] = set()
    while out.lower() in symbols and out.lower() not in seen:
        seen.add(out.lower())
        out = symbols[out.lower()].strip()
    return out


def _collect_relevant_local_params(sig: FortranProcedureSignature, local_params: dict[str, str]) -> dict[str, str]:
    if not local_params:
        return {}
    if not sig.arguments and sig.result is None:
        return dict(local_params)
    pending = set()
    for arg in sig.arguments:
        if arg.kind:
            pending.update(_extract_symbol_names(arg.kind))
        for dim in arg.shape:
            pending.update(_extract_symbol_names(dim))
    if sig.result and sig.result.kind:
        pending.update(_extract_symbol_names(sig.result.kind))
    relevant: dict[str, str] = {}
    while pending:
        sym = pending.pop().lower()
        if sym in relevant or sym not in local_params:
            continue
        value = local_params[sym]
        relevant[sym] = value
        pending.update(_extract_symbol_names(value))
    return relevant


def _extract_symbol_names(expr: str) -> set[str]:
    keywords = {"and", "or", "not"}
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr or "")
        if not token.isdigit() and token.lower() not in keywords
    }


def _normalize_parameter_value(value: str) -> str:
    parsed_int = _safe_eval_int_expr(value)
    if parsed_int is not None:
        return str(parsed_int)
    text = value.strip()
    if re.fullmatch(r"[+-]?\d+(?:\.\d*)?(?:[deDE][+-]?\d+)?", text):
        try:
            as_float = float(text.replace("d", "e").replace("D", "E"))
            if as_float.is_integer():
                return str(int(as_float))
        except ValueError:
            pass
    return text

def _resolve_variables(symbols: dict[str, str], base_types: dict[str, str] | None = None) -> dict[str, FortranVariable]:
    base_types = base_types or {}
    valued: dict[str, FortranVariable] = {}
    for name, value in symbols.items():
        valued[name] = FortranVariable(
            name=name,
            base_type=base_types.get(name.lower(), "unknown"),
            value=_resolve_compile_time_expression(value, symbols, prefer_symbolic=False),
            value_type="expression",
            is_parameter=True,
        )
    return valued


def _is_evaluable_symbol(name: str, symbols: dict[str, str]) -> bool:
    if name.lower() not in symbols:
        return False
    resolved = _resolve_compile_time_expression(symbols[name.lower()], symbols, prefer_symbolic=False)
    return _safe_eval_int_expr(resolved) is not None

def _resolve_compile_time_expression(expr: str, symbols: dict[str, str], prefer_symbolic: bool = True) -> str:
    """Resolve a kind/shape expression using a dictionary of compile-time symbols.

    The resolver performs repeated, whole-token substitutions (using word
    boundaries) and then tries to fold the result to an integer when safe.

    Parameters
    ----------
    expr:
        Expression text to resolve (e.g. ``"dp"`` or ``"n+1"`` or ``"1:n"``).
    symbols:
        Mapping of symbol -> expression text. Resolution is case-insensitive.
    prefer_symbolic:
        If True, keep non-evaluable symbols in symbolic form rather than
        inlining their definitions. This improves readability for wrappers.
    """
    text = expr.strip()
    if not text:
        return expr
    if ":" in text:
        parts = text.split(":")
        return ":".join(_resolve_compile_time_expression(p, symbols) if p.strip() else p for p in parts)

    replaced = text
    max_passes = max(8, len(symbols) * 2)
    for _ in range(max_passes):
        updated = replaced
        for name, value in sorted(symbols.items(), key=lambda kv: len(kv[0]), reverse=True):
            replacement = name if (prefer_symbolic and not _is_evaluable_symbol(name, symbols)) else f"({value})"
            updated = re.sub(rf"\b{re.escape(name)}\b", replacement, updated, flags=re.IGNORECASE)
        if updated == replaced:
            break
        replaced = updated

    evaluated = _safe_eval_int_expr(replaced)
    # Keep a resolved symbolic expression when integer folding is not possible
    # (e.g. selected_*_kind intrinsics), rather than the original unresolved token.
    if evaluated is not None:
        return str(evaluated)
    return replaced if replaced != text else text


def _safe_eval_int_expr(expr: str) -> int | None:
    """Safely evaluate a restricted integer-only Python expression.

    Used to fold simple arithmetic after symbol substitution. Only numeric
    constants and basic arithmetic operators are allowed. Any other syntax
    returns None rather than raising.
    """
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None

    allowed_binops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
    allowed_unary = (ast.UAdd, ast.USub)

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and isinstance(n.op, allowed_binops):
            left = _eval(n.left)
            right = _eval(n.right)
            if left is None or right is None:
                return None
            if isinstance(n.op, ast.Add):
                return left + right
            if isinstance(n.op, ast.Sub):
                return left - right
            if isinstance(n.op, ast.Mult):
                return left * right
            if isinstance(n.op, ast.Div):
                return left / right
            if isinstance(n.op, ast.FloorDiv):
                return left // right
            if isinstance(n.op, ast.Mod):
                return left % right
            if isinstance(n.op, ast.Pow):
                return left ** right
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, allowed_unary):
            v = _eval(n.operand)
            if v is None:
                return None
            return +v if isinstance(n.op, ast.UAdd) else -v
        return None

    val = _eval(node)
    if val is None:
        return None
    if isinstance(val, float) and val.is_integer():
        return int(val)
    return val if isinstance(val, int) else None


# -----------------------------------------------------------------------------
# Project dependency ordering
# -----------------------------------------------------------------------------

def _topological_files(file_deps: dict[str, set[str]]) -> list[str]:
    in_degree = {f: 0 for f in file_deps}
    for f, deps in file_deps.items():
        for d in deps:
            if d in in_degree:
                in_degree[f] += 1
    ready = sorted([f for f, deg in in_degree.items() if deg == 0])
    ordered: list[str] = []
    deps_copy = {k: set(v) for k, v in file_deps.items()}
    while ready:
        cur = ready.pop(0)
        ordered.append(cur)
        for f, deps in deps_copy.items():
            if cur in deps:
                deps.remove(cur)
                if len(deps) == 0 and f not in ordered and f not in ready:
                    ready.append(f)
                    ready.sort()
    remaining = [f for f in file_deps if f not in ordered]
    ordered.extend(sorted(remaining))
    return ordered

class FortranParser:
    """Stateful parser entrypoint and orchestration object.

    State carried on the instance:
    - `macro_defines`: optional macro-selection configuration used while
      collecting procedures when conditional branches are present.

    Parsing pipeline used by `parse_file`:
    1. Preprocess source into normalized lines (`_preprocessed_lines`).
    2. Parse signatures/types/interfaces/program units.
    3. Attach parsed members to owning module/submodule scopes.
    4. Build `FortranFile` symbol table and standalone entity lists.

    Class section map:
    - Public API methods first (developer discovery).
    - High-level unit parsing methods next (top-down by Fortran block size).
    - Internal `*_impl` methods after that (full scoped parsing logic).
    - Lower-level declaration/header helpers and assembly utilities last.

    Scope behavior summary:
    - `current_module` tracks ownership for procedures/types/interfaces.
    - `interface_depth`/stacks track when declarations belong to interface blocks.
    - Per-procedure state tracks declaration-part vs executable-part boundaries.
    - Type parsing tracks `contains` sub-region for bindings/generics vs fields.
    - Program/module/submodule parsers collect specification-part declarations
      and stop collecting variable declarations after `contains`.

    `parse_project` composes multiple `FortranFile` objects into one
    `FortranProject` registry and validates duplicate symbols by scope.
    """
    # ------------------------------------------------------------------
    # Public API (kept first for discoverability)
    # ------------------------------------------------------------------

    def __init__(self, macro_defines: set[str] | dict[str, int | bool | str] | None = None):
        self.macro_defines = macro_defines

    def visit_file(
        self,
        source_or_path: str | Path,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        encoding: str = "utf-8",
    ) -> FortranFile:
        return self.visit_fortran_file(
            source_or_path,
            filename=filename,
            macro_defines=macro_defines,
            encoding=encoding,
        )

    def visit_project(self, files, *, encoding: str = "utf-8") -> FortranProject:
        return self.visit_fortran_project(files, encoding=encoding)

    def visit_wrap_readiness(self, code: str, filename: str | None = None) -> dict:
        return self.visit_fortran_wrap_readiness(code, filename=filename)

    def parse_file(
        self,
        source_or_path: str | Path,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        encoding: str = "utf-8",
    ) -> FortranFile:
        return self.visit_file(
            source_or_path,
            filename=filename,
            macro_defines=macro_defines,
            encoding=encoding,
        )

    def parse_project(self, files, *, encoding: str = "utf-8") -> FortranProject:
        return self.visit_project(files, encoding=encoding)

    def assess_wrap_readiness(self, code: str, filename: str | None = None) -> dict:
        return self.visit_wrap_readiness(code, filename=filename)

    # ------------------------------------------------------------------
    # Scope symbol-table helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _scope_key(name: str) -> str:
        return name.lower()

    def _new_procedure_scope_state(
        self,
        signature: FortranProcedureSignature,
        *,
        symbols: dict[str, FortranArgument],
        typed_symbols: set[str] | None = None,
        explicit_result: bool = False,
    ) -> dict:
        state = {
            "signature": signature,
            "symbols": symbols,
            "typed_symbols": typed_symbols or set(),
            "uses": {},
            "in_contains": False,
            "local_params": {},
            "legacy_local_params": set(),
            "implicit_typed_symbols": {},
            "declared_local_types": {},
            "implicit_none": False,
            "imports": set(),
            "external_symbols": set(),
            "includes": [],
            "filename": None,
            "local_type_depth": 0,
        }
        if explicit_result:
            state["explicit_result"] = True
        return state

    def _proc_scope_get_symbol(self, proc_state: dict, name: str) -> FortranArgument | None:
        return proc_state["symbols"].get(self._scope_key(name))

    def _proc_scope_symbol_is_declared(self, proc_state: dict, name: str) -> bool:
        return self._scope_key(name) in proc_state["typed_symbols"]

    def _proc_scope_mark_declared_symbol(
        self,
        proc_state: dict,
        name: str,
        *,
        filename: str | None = None,
        line_number: int | None = None,
        source_line: str | None = None,
    ) -> str:
        key = self._scope_key(name)
        if key in proc_state["typed_symbols"]:
            raise FortranParseError(
                f"Duplicate declaration of symbol '{name}' in procedure '{proc_state['signature'].name}'.",
                filename=filename,
                line_number=line_number,
                source_line=source_line,
            )
        proc_state["typed_symbols"].add(key)
        return key

    def _proc_scope_add_external_symbol(self, proc_state: dict, name: str) -> str:
        key = self._scope_key(name)
        proc_state.setdefault("external_symbols", set()).add(key)
        arg = self._proc_scope_get_symbol(proc_state, key)
        if arg is not None and arg.base_type == "unknown":
            arg.base_type = "procedure"
        return key

    def _proc_scope_add_include(self, proc_state: dict, include_path: str) -> None:
        proc_state.setdefault("includes", []).append(include_path)

    def _proc_scope_add_imports(self, proc_state: dict, names: list[str]) -> None:
        proc_state.setdefault("imports", set()).update(self._scope_key(n) for n in names if n.strip())

    def _proc_scope_set_declared_local_type(self, proc_state: dict, name: str, meta: dict) -> None:
        key = self._scope_key(name)
        proc_state["declared_local_types"][key] = {
            "base_type": meta["base_type"],
            "kind": meta["kind"],
        }

    def _proc_scope_add_local_parameter(
        self,
        proc_state: dict,
        name: str,
        value: str,
        *,
        filename: str | None = None,
        line_number: int | None = None,
        source_line: str | None = None,
        require_declared: bool = False,
        register_implicit_if_missing: bool = False,
        legacy: bool = False,
    ) -> None:
        key = self._scope_key(name)
        if require_declared and not self._proc_scope_symbol_is_declared(proc_state, key):
            raise FortranParseError(
                f"Unknown datatype for PARAMETER symbol '{name}' in procedure '{proc_state['signature'].name}'.",
                filename=filename,
                line_number=line_number,
                source_line=source_line,
            )
        if key in proc_state["local_params"]:
            raise FortranParseError(
                f"Duplicate PARAMETER declaration of symbol '{name}' in procedure '{proc_state['signature'].name}'.",
                filename=filename,
                line_number=line_number,
                source_line=source_line,
            )
        proc_state["local_params"][key] = value
        if register_implicit_if_missing and not self._proc_scope_symbol_is_declared(proc_state, key):
            proc_state["implicit_typed_symbols"][key] = _infer_implicit_base_type(name)
        if legacy:
            proc_state["legacy_local_params"].add(key)

    @staticmethod
    def _insert_unique_scope_symbol(
        scope: dict[str, object],
        key: str,
        value: object,
        *,
        label: str,
        filename: str | None = None,
    ) -> None:
        if key in scope:
            raise FortranParseError(f"Duplicate symbol '{key}' in {label}.", filename=filename)
        scope[key] = value

    @staticmethod
    def _is_module_program_unit_start(line: str) -> bool:
        lower = line.lower()
        return _MODULE_RE.match(line) is not None

    @staticmethod
    def _is_contains_transition(line: str) -> bool:
        return line.lower() == "contains"

    def _track_containing_module_scope(self, current_module: str | None, line: str) -> tuple[str | None, bool]:
        """Track module/submodule ownership for nested type/interface passes."""
        lower = line.lower()
        submodule_match = _SUBMODULE_RE.match(line)
        if submodule_match:
            return submodule_match.group("name"), True
        if lower.startswith("end submodule"):
            return None, True
        if self._is_module_program_unit_start(line):
            return line.split()[1], True
        if lower.startswith("end module"):
            return None, True
        return current_module, False

    def _parse_module_header(
        self,
        line: str,
        filename: str | None,
        lineno: int | None = None,
        source_line: str | None = None,
    ) -> FortranModule | None:
        module_match = _MODULE_RE.match(line)
        if not module_match:
            if line.lower().startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", line, re.IGNORECASE):
                raise FortranParseError(
                    f"Unsupported or malformed module header: {line.strip()}",
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
            return None
        return FortranModule(name=module_match.group("name"), filename=filename)

    def _collect_module_spec_line(
        self,
        module: FortranModule,
        line: str,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        lower = line.lower()
        if lower == "private":
            module.default_visibility = "private"
            return
        if lower == "public":
            module.default_visibility = "public"
            return
        parsed_use = _parse_use_statement(line)
        if parsed_use:
            module_name, mappings = parsed_use
            module.uses[module_name] = mappings
            return
        self._parse_module_variable_line(line, module, filename, lineno=lineno, source_line=source_line)

    def _finalize_module(self, module: FortranModule, modules: list[FortranModule], filename: str | None) -> None:
        _validate_module_variables(module, filename)
        _apply_module_visibility(module, filename)
        modules.append(module)

    def _attach_module_children(
        self,
        modules: list[FortranModule],
        *,
        signatures: list[FortranProcedureSignature],
        types: list[FortranDerivedType],
        interfaces: list[FortranInterface],
    ) -> None:
        modules_by_name = {m.name.lower(): m for m in modules}
        for sig in signatures:
            if sig.module and not sig.in_interface:
                mod = modules_by_name.get(sig.module.lower())
                if mod is not None:
                    mod.procedures.append(sig)
        for dtype in types:
            if dtype.module:
                mod = modules_by_name.get(dtype.module.lower())
                if mod is not None:
                    mod.derived_types.append(dtype)
        for iface in interfaces:
            if iface.module:
                mod = modules_by_name.get(iface.module.lower())
                if mod is not None:
                    mod.interfaces.append(iface)

    def _parse_submodule_header(self, line: str, filename: str | None) -> FortranSubmodule | None:
        match = _SUBMODULE_RE.match(line)
        if not match:
            return None
        parent, ancestor = _split_submodule_parent(match.group("parent"))
        return FortranSubmodule(
            name=match.group("name"),
            parent=parent,
            ancestor=ancestor,
            filename=filename,
        )

    def _collect_submodule_spec_line(
        self,
        submodule: FortranSubmodule,
        line: str,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        parsed_use = _parse_use_statement(line)
        if parsed_use:
            module_name, mappings = parsed_use
            submodule.uses[module_name] = mappings
            return
        self._parse_module_variable_line(line, submodule, filename, lineno=lineno, source_line=source_line)

    def _finalize_submodule(
        self,
        submodule: FortranSubmodule,
        submodules: list[FortranSubmodule],
        filename: str | None,
    ) -> None:
        _validate_module_variables(submodule, filename)
        submodules.append(submodule)

    def _attach_submodule_children(
        self,
        submodules: list[FortranSubmodule],
        *,
        signatures: list[FortranProcedureSignature],
        types: list[FortranDerivedType],
        interfaces: list[FortranInterface],
    ) -> None:
        submodules_by_name = {m.name.lower(): m for m in submodules}
        for sig in signatures:
            if sig.module:
                submod = submodules_by_name.get(sig.module.lower())
                if submod is not None and not sig.in_interface:
                    submod.procedures.append(sig)
        for dtype in types:
            if dtype.module:
                submod = submodules_by_name.get(dtype.module.lower())
                if submod is not None:
                    submod.derived_types.append(dtype)
        for iface in interfaces:
            if iface.module:
                submod = submodules_by_name.get(iface.module.lower())
                if submod is not None:
                    submod.interfaces.append(iface)

    def _parse_program_header(self, line: str, filename: str | None) -> FortranProgram | None:
        match = _PROGRAM_RE.match(line)
        if not match:
            return None
        return FortranProgram(name=match.group("name"), filename=filename)

    def _collect_program_spec_line(
        self,
        program: FortranProgram,
        line: str,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        parsed_use = _parse_use_statement(line)
        if parsed_use:
            module_name, mappings = parsed_use
            program.uses[module_name] = mappings
            return
        self._parse_module_variable_line(line, program, filename, lineno=lineno, source_line=source_line)

    def _finalize_program(self, program: FortranProgram, programs: list[FortranProgram], filename: str | None) -> None:
        _validate_variable_declarations(
            program.variables,
            owner_kind="program",
            owner_name=program.name,
            filename=filename,
        )
        programs.append(program)

    def _parse_block_data_header(self, line: str, filename: str | None) -> FortranBlockData | None:
        match = _BLOCK_DATA_RE.match(line)
        if not match:
            return None
        return FortranBlockData(name=match.group("name"), filename=filename)

    def _collect_block_data_line(
        self,
        block_data: FortranBlockData,
        line: str,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        self._parse_module_variable_line(line, block_data, filename, lineno=lineno, source_line=source_line)

    def _finalize_block_data(
        self,
        block_data: FortranBlockData,
        blocks: list[FortranBlockData],
        filename: str | None,
    ) -> None:
        _validate_variable_declarations(
            block_data.variables,
            owner_kind="block data",
            owner_name=block_data.name,
            filename=filename,
        )
        blocks.append(block_data)

    # ------------------------------------------------------------------
    # High-level unit parsing (largest scopes first)
    # ------------------------------------------------------------------

    def visit_fortran_modules(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        require_present: bool = True,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranModule]:
        return self._visit_fortran_modules_impl(
            code,
            filename=filename,
            require_present=require_present,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )

    def visit_fortran_submodules(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranSubmodule]:
        return self._visit_fortran_submodules_impl(
            code,
            filename=filename,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )

    def visit_fortran_interfaces(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:
        return self._visit_fortran_interfaces_impl(code, filename=filename)

    def visit_fortran_types(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:
        return self._visit_fortran_types_impl(code, filename=filename)

    def visit_fortran_module(self, code: _SourceOrLines, filename: str | None = None) -> FortranModule:
        return _expect_single_parse_result(
            self.visit_fortran_modules(code, filename=filename, require_present=True),
            parser_name="visit_fortran_module",
            entity_name="module",
            filename=filename,
        )

    def visit_fortran_submodule(self, code: _SourceOrLines, filename: str | None = None) -> FortranSubmodule:
        return _expect_single_parse_result(
            self.visit_fortran_submodules(code, filename=filename),
            parser_name="visit_fortran_submodule",
            entity_name="submodule",
            filename=filename,
        )

    def visit_fortran_interface(self, code: _SourceOrLines, filename: str | None = None) -> FortranInterface:
        return _expect_single_parse_result(
            self.visit_fortran_interfaces(code, filename=filename),
            parser_name="visit_fortran_interface",
            entity_name="interface",
            filename=filename,
        )

    def visit_fortran_derived_type(self, code: _SourceOrLines, filename: str | None = None) -> FortranDerivedType:
        return _expect_single_parse_result(
            self.visit_fortran_types(code, filename=filename),
            parser_name="visit_fortran_derived_type",
            entity_name="derived type",
            filename=filename,
        )

    def visit_fortran_programs(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:
        return self._visit_fortran_programs_impl(code, filename=filename)

    def visit_fortran_program(self, code: _SourceOrLines, filename: str | None = None) -> FortranProgram:
        return _expect_single_parse_result(
            self.visit_fortran_programs(code, filename=filename),
            parser_name="visit_fortran_program",
            entity_name="program",
            filename=filename,
        )

    def visit_fortran_block_data(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:
        return self._visit_fortran_block_data(code, filename=filename)

    def visit_fortran_block_data_unit(self, code: _SourceOrLines, filename: str | None = None) -> FortranBlockData:
        return _expect_single_parse_result(
            self.visit_fortran_block_data(code, filename=filename),
            parser_name="visit_fortran_block_data_unit",
            entity_name="block data unit",
            filename=filename,
        )

    def _parse_fortran_types(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:  # pragma: no cover - private compatibility shim.
        return self.visit_fortran_types(code, filename=filename)

    def _parse_fortran_modules(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        require_present: bool = True,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranModule]:  # pragma: no cover - private compatibility shim.
        return self.visit_fortran_modules(
            code,
            filename=filename,
            require_present=require_present,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )

    def _parse_fortran_submodules(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranSubmodule]:  # pragma: no cover - private compatibility shim.
        return self.visit_fortran_submodules(
            code,
            filename=filename,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )

    def _parse_fortran_interfaces(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:  # pragma: no cover - private compatibility shim.
        return self.visit_fortran_interfaces(code, filename=filename)

    def _parse_fortran_programs(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:  # pragma: no cover - private compatibility shim.
        return self.visit_fortran_programs(code, filename=filename)

    def _parse_fortran_block_data(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:  # pragma: no cover - private compatibility shim.
        return self.visit_fortran_block_data(code, filename=filename)

    def _visit_fortran_types_impl(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:  # pragma: no cover - private compatibility shim.
        return self._parse_fortran_types_impl(code, filename=filename)

    def _visit_fortran_modules_impl(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        require_present: bool = True,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranModule]:  # pragma: no cover - private compatibility shim.
        return self._parse_fortran_modules_impl(
            code,
            filename=filename,
            require_present=require_present,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )

    def _visit_fortran_submodules_impl(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranSubmodule]:  # pragma: no cover - private compatibility shim.
        return self._parse_fortran_submodules_impl(
            code,
            filename=filename,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )

    def _visit_fortran_interfaces_impl(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:  # pragma: no cover - private compatibility shim.
        return self._parse_fortran_interfaces_impl(code, filename=filename)

    def _visit_fortran_programs_impl(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:  # pragma: no cover - private compatibility shim.
        return self._parse_fortran_programs_impl(code, filename=filename)

    def _visit_fortran_block_data(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:  # pragma: no cover - private compatibility shim.
        return self._parse_fortran_block_data(code, filename=filename)

    # ------------------------------------------------------------------
    # Procedure collection lifecycle helpers
    # ------------------------------------------------------------------

    def _handle_procedure_preprocessor_line(
        self,
        line: str,
        *,
        macro_selection_enabled: bool,
        macro_names: set[str],
        pp_condition_stack: list[tuple[int, int]],
        pp_active_stack: list[bool],
        pp_group_counter: int,
    ) -> tuple[bool, int]:
        """Update conditional-compilation state while collecting procedures."""
        if not line.startswith("#"):
            return False, pp_group_counter

        directive = line[1:].strip()
        directive_low = directive.lower()
        if directive_low.startswith("ifdef "):
            pp_group_counter += 1
            pp_condition_stack.append((pp_group_counter, 0))
            expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
            pp_active_stack.append((bool(expr) and expr.lower() in macro_names) if macro_selection_enabled else True)
            return True, pp_group_counter
        if directive_low.startswith("ifndef "):
            pp_group_counter += 1
            pp_condition_stack.append((pp_group_counter, 0))
            expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
            pp_active_stack.append(((not expr) or expr.lower() not in macro_names) if macro_selection_enabled else True)
            return True, pp_group_counter
        if directive_low.startswith("if "):
            pp_group_counter += 1
            pp_condition_stack.append((pp_group_counter, 0))
            expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
            pp_active_stack.append(_eval_cpp_expr(expr, macro_names) if macro_selection_enabled else True)
            return True, pp_group_counter
        if directive_low.startswith("else"):
            if pp_condition_stack:
                group_id, branch_id = pp_condition_stack.pop()
                pp_condition_stack.append((group_id, branch_id + 1))
            if pp_active_stack:
                prev = pp_active_stack.pop()
                pp_active_stack.append((not prev) if macro_selection_enabled else True)
            return True, pp_group_counter
        if directive_low.startswith("elif "):
            if pp_condition_stack:
                group_id, branch_id = pp_condition_stack.pop()
                pp_condition_stack.append((group_id, branch_id + 1))
            if pp_active_stack:
                pp_active_stack.pop()
                expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
                pp_active_stack.append(_eval_cpp_expr(expr, macro_names) if macro_selection_enabled else True)
            return True, pp_group_counter
        if directive_low.startswith("endif"):
            if pp_condition_stack:
                pp_condition_stack.pop()
            if pp_active_stack:
                pp_active_stack.pop()
            return True, pp_group_counter
        return False, pp_group_counter

    @staticmethod
    def _procedure_preprocessor_condition_set(pp_condition_stack: list[tuple[int, int]]) -> frozenset[str]:
        return frozenset(f"g{group_id}:b{branch_id}" for group_id, branch_id in pp_condition_stack)

    def _handle_procedure_interface_boundary(
        self,
        line: str,
        *,
        interface_depth: int,
        interface_name_stack: list[str | None],
    ) -> tuple[int, bool]:
        lower = line.lower()
        if lower.startswith("interface") or lower.startswith("abstract interface"):
            parts = line.split(maxsplit=1)
            iface_name = parts[1].strip() if len(parts) > 1 and not lower.startswith("abstract interface") else None
            interface_name_stack.append(iface_name)
            return interface_depth + 1, True
        if lower.startswith("end interface"):
            if interface_name_stack:
                interface_name_stack.pop()
            return max(0, interface_depth - 1), True
        return interface_depth, False

    def _handle_procedure_owner_boundary(
        self,
        line: str,
        *,
        current_module: str | None,
        current_module_uses: dict[str, list[FortranUseMapping]],
        program_depth: int,
    ) -> tuple[str | None, dict[str, list[FortranUseMapping]], int, bool]:
        lower = line.lower()
        submodule_match = _SUBMODULE_RE.match(line)
        if submodule_match:
            return submodule_match.group("name"), {}, program_depth, True
        if lower.startswith("end submodule"):
            return None, {}, program_depth, True
        if _PROGRAM_RE.match(line):
            return current_module, current_module_uses, program_depth + 1, True
        if lower.startswith("end program"):
            return current_module, current_module_uses, max(0, program_depth - 1), True
        if self._is_module_program_unit_start(line):
            return line.split()[1], {}, program_depth, True
        if lower.startswith("end module"):
            return None, {}, program_depth, True
        return current_module, current_module_uses, program_depth, False

    def _register_procedure_block_name(
        self,
        proc_state: dict,
        *,
        current_module: str | None,
        interface_depth: int,
        declared_procedures: dict[tuple[str | None, bool], dict[str, list[frozenset[str]]]],
        pp_condition_stack: list[tuple[int, int]],
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        scope_key = (current_module.lower() if current_module else None, interface_depth > 0)
        seen_in_scope = declared_procedures.setdefault(scope_key, {})
        proc_name = proc_state["signature"].name.lower()
        condition_set = self._procedure_preprocessor_condition_set(pp_condition_stack)
        existing_conditions = seen_in_scope.setdefault(proc_name, [])
        if (
            not interface_depth
            and any(_preprocessor_conditions_overlap(existing, condition_set) for existing in existing_conditions)
        ):
            scope_label = f"module '{current_module}'" if current_module is not None else "global scope"
            raise FortranParseError(
                f"Duplicate procedure name '{proc_state['signature'].name}' in {scope_label}.",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        existing_conditions.append(condition_set)

    def _start_procedure_block(
        self,
        line: str,
        *,
        current_module: str | None,
        current_module_uses: dict[str, list[FortranUseMapping]],
        interface_depth: int,
        declared_procedures: dict[tuple[str | None, bool], dict[str, list[frozenset[str]]]],
        pp_condition_stack: list[tuple[int, int]],
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> dict | None:
        proc_state = self._parse_procedure_header(
            line,
            current_module,
            interface_depth > 0,
            filename=filename,
            lineno=lineno,
            source_line=source_line,
        )
        if proc_state is None:
            self._raise_if_unparsed_procedure_header(
                line,
                in_interface=interface_depth > 0,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )
            return None
        self._register_procedure_block_name(
            proc_state,
            current_module=current_module,
            interface_depth=interface_depth,
            declared_procedures=declared_procedures,
            pp_condition_stack=pp_condition_stack,
            filename=filename,
            lineno=lineno,
            source_line=source_line,
        )
        proc_state["uses"].update(current_module_uses)
        proc_state["filename"] = filename
        proc_state["header_lineno"] = lineno
        proc_state["header_source_line"] = source_line
        proc_state["in_exec_part"] = False
        return proc_state

    def _finalize_procedure_block(
        self,
        proc_state: dict,
        signatures: list[FortranProcedureSignature],
    ) -> None:
        signatures.append(_finalize_proc(proc_state))

    def _handle_procedure_contains_line(
        self,
        line: str,
        *,
        current_proc: dict,
        signatures: list[FortranProcedureSignature],
    ) -> dict | None:
        lower = line.lower()
        if lower.startswith("end subroutine") or lower.startswith("end function") or lower.startswith("end procedure"):
            end_parts = lower.split()
            end_name = end_parts[2] if len(end_parts) > 2 else None
            if end_name == current_proc["signature"].name.lower():
                self._finalize_procedure_block(current_proc, signatures)
                return None
        return current_proc

    def _handle_interface_procedure_declaration_line(
        self,
        line: str,
        *,
        current_proc: dict,
        current_module: str | None,
        signatures: list[FortranProcedureSignature],
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> dict | None:
        lower = line.lower()
        if (
            current_proc["signature"].in_interface
            and (
                lower.startswith("end subroutine")
                or lower.startswith("end function")
                or lower.startswith("end procedure")
            )
        ):
            self._finalize_procedure_block(current_proc, signatures)
            return None
        if _looks_like_procedure_header(line):
            iface_proc = self._parse_procedure_header(
                line,
                current_module,
                True,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )
            if iface_proc:
                iface_name = iface_proc["signature"].name.lower()
                self._proc_scope_mark_declared_symbol(
                    current_proc,
                    iface_name,
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
                arg = self._proc_scope_get_symbol(current_proc, iface_name)
                if arg is not None:
                    arg.base_type = "procedure"
                    arg.kind = None
            return current_proc
        return current_proc

    @staticmethod
    def _raise_if_unparsed_procedure_header(
        line: str,
        *,
        in_interface: bool,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        stripped = line.strip()
        if not stripped:
            return
        lowered = stripped.lower()
        if lowered.startswith("module procedure"):
            if in_interface or _MOD_PROC_IMPL_RE.match(stripped):
                return
            raise FortranParseError(
                f"Unsupported or malformed module procedure header: {stripped}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        if _looks_like_procedure_header(stripped):
            raise FortranParseError(
                f"Unsupported or malformed procedure header: {stripped}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )

    # ------------------------------------------------------------------
    # Procedure declaration parsing helpers
    # ------------------------------------------------------------------

    def _handle_proc_implicit_line(self, line: str, proc_state: dict) -> bool:
        if not re.match(r"^implicit\b", line, flags=re.IGNORECASE):
            return False
        if re.match(r"^implicit\s+none\b", line, flags=re.IGNORECASE):
            proc_state["implicit_none"] = True
        return True

    def _handle_proc_external_line(self, line: str, proc_state: dict) -> bool:
        external_match = re.match(r"^external\b\s*(?:::)?\s*(?P<names>.*)$", line, flags=re.IGNORECASE)
        if not external_match:
            return False
        names = [n.strip().lower() for n in split_csv(external_match.group("names") or "") if n.strip()]
        for name in names:
            self._proc_scope_add_external_symbol(proc_state, name)
        return True

    @staticmethod
    def _is_ignored_proc_spec_line(line: str) -> bool:
        ignored_patterns = (
            r"^(function|subroutine)\b",
            r"^intrinsic\b",
            r"^data\b",
            r"^equivalence\b",
            r"^format\s*\(",
            r"^go\s*to\b",
            r"^use\b",
            r"^save\b",
            r"^common\b",
        )
        return any(re.match(pattern, line, flags=re.IGNORECASE) for pattern in ignored_patterns)

    def _handle_proc_include_or_import_line(self, line: str, proc_state: dict) -> bool:
        include_match = _INCLUDE_RE.match(line)
        if include_match:
            self._proc_scope_add_include(proc_state, include_match.group("path"))
            return True
        import_match = _IMPORT_RE.match(line)
        if import_match:
            symbols = [s.strip().lower() for s in split_csv(import_match.group("symbols") or "") if s.strip()]
            self._proc_scope_add_imports(proc_state, symbols)
            return True
        return False

    def _handle_proc_parameter_line(
        self,
        line: str,
        proc_state: dict,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> bool:
        param_match = _PARAM_RE.match(line)
        if param_match:
            for assign in split_csv(param_match.group("body")):
                if "=" not in assign:
                    continue
                name, value = [x.strip() for x in assign.split("=", 1)]
                self._proc_scope_add_local_parameter(
                    proc_state,
                    name,
                    value,
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
            return True

        legacy_param_match = _LEGACY_PARAM_STMT_RE.match(line)
        if legacy_param_match:
            for assign in split_csv(legacy_param_match.group("body")):
                if "=" not in assign:
                    continue
                name, value = [x.strip() for x in assign.split("=", 1)]
                declared = self._proc_scope_symbol_is_declared(proc_state, name)
                self._proc_scope_add_local_parameter(
                    proc_state,
                    name,
                    value,
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                    require_declared=proc_state.get("implicit_none", False),
                    register_implicit_if_missing=not declared,
                    legacy=declared,
                )
            return True

        return False

    @staticmethod
    def _looks_like_unknown_proc_declaration(line: str) -> bool:
        m_first = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)", line.strip())
        first_word = m_first.group(1).lower() if m_first else ""
        non_decl_starts = {
            "do", "if", "where", "call", "select", "case", "allocate", "deallocate",
            "print", "write", "read", "return", "stop", "cycle", "exit", "continue",
            "end", "else", "elseif", "contains", "goto", "go", "data", "format",
            "use", "save", "common",
        }
        if "=" in line and "::" not in line:
            return False
        return (
            bool(re.match(r"^[A-Za-z]", line.strip()))
            and first_word not in non_decl_starts
            and ("::" in line or "," in line or " " in line.strip())
        )

    def _handle_unknown_proc_declaration(
        self,
        line: str,
        proc_state: dict,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        if not self._looks_like_unknown_proc_declaration(line):
            return
        if any(pattern.search(line) for pattern in _UNSUPPORTED_PATTERNS):
            return
        raise FortranParseError(
            f"Unknown or unsupported datatype declaration for procedure '{proc_state['signature'].name}': {line.strip()}",
            filename=filename,
            line_number=lineno,
            source_line=source_line,
        )

    def _apply_declaration_to_procedure_state(
        self,
        meta: dict,
        right: str,
        proc_state: dict,
        *,
        filename: str | None,
        lineno: int | None,
        source_line: str | None,
    ) -> None:
        if meta["base_type"] == "procedure" and meta["kind"] in proc_state.get("imports", set()):
            meta["kind"] = None

        for entity in split_csv(right):
            raw_name, shape = _var(entity)
            if not raw_name:
                continue
            normalized_name = _normalize_declared_name(raw_name, meta)
            if not normalized_name:
                continue
            lowered_name = self._proc_scope_mark_declared_symbol(
                proc_state,
                normalized_name,
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
            if meta.get("external"):
                self._proc_scope_add_external_symbol(proc_state, lowered_name)
            # Legacy star-kind declarations can appear as:
            #   COMPLEX*16 AP(*), X(*)
            # In this case the first parsed entity may carry the `*16` token
            # in `raw_name`; always resolve symbols using the normalized name so
            # all listed variables receive the declaration metadata.
            arg = self._proc_scope_get_symbol(proc_state, lowered_name)
            if arg is None:
                self._proc_scope_set_declared_local_type(proc_state, lowered_name, meta)
                continue
            _apply(arg, meta, shape)

    def _collect_procedure_signatures(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    ) -> list[FortranProcedureSignature]:
        """Scan source lines for procedure blocks and collect finalized signatures.

        Scope model:
        - Tracks module/submodule scope (`current_module`).
        - Tracks interface nesting (`interface_depth`) to mark interface members.
        - Tracks preprocessor branches and suppresses inactive blocks when macro
          selection is enabled.
        - Identifies procedure block boundaries from `subroutine/function` headers
          to matching `end ...` statements, then finalizes symbols/types/shapes.
        """
        lines = self._preprocessed_lines(code, filename)
        macro_selection_enabled = macro_defines is not None
        signatures: list[FortranProcedureSignature] = []
        declared_procedures: dict[tuple[str | None, bool], dict[str, list[frozenset[str]]]] = {}
        current_module = None
        current_module_uses: dict[str, list[FortranUseMapping]] = {}
        current_proc = None
        interface_depth = 0
        interface_name_stack: list[str | None] = []
        program_depth = 0
        macro_names = _normalize_macro_defines(macro_defines)
        pp_condition_stack: list[tuple[int, int]] = []
        pp_active_stack: list[bool] = []
        pp_group_counter = 0

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue

            handled_pp, pp_group_counter = self._handle_procedure_preprocessor_line(
                s,
                macro_selection_enabled=macro_selection_enabled,
                macro_names=macro_names,
                pp_condition_stack=pp_condition_stack,
                pp_active_stack=pp_active_stack,
                pp_group_counter=pp_group_counter,
            )
            if handled_pp:
                continue

            if macro_selection_enabled and pp_active_stack and not all(pp_active_stack):
                continue

            l = s.lower()

            interface_depth, handled_interface = self._handle_procedure_interface_boundary(
                s,
                interface_depth=interface_depth,
                interface_name_stack=interface_name_stack,
            )
            if handled_interface:
                continue

            current_module, current_module_uses, program_depth, handled_owner = self._handle_procedure_owner_boundary(
                s,
                current_module=current_module,
                current_module_uses=current_module_uses,
                program_depth=program_depth,
            )
            if handled_owner:
                continue
            if program_depth > 0:
                continue

            if current_proc is None:
                parsed_use = _parse_use_statement(s)
                if parsed_use and current_module is not None:
                    module_name, mappings = parsed_use
                    current_module_uses[module_name] = mappings
                    continue

            if current_proc is None:
                current_proc = self._start_procedure_block(
                    s,
                    current_module=current_module,
                    current_module_uses=current_module_uses,
                    interface_depth=interface_depth,
                    declared_procedures=declared_procedures,
                    pp_condition_stack=pp_condition_stack,
                    filename=filename,
                    lineno=lineno,
                    source_line=source_line,
                )
                continue

            if current_proc is not None and current_proc.get("in_contains"):
                current_proc = self._handle_procedure_contains_line(
                    s,
                    current_proc=current_proc,
                    signatures=signatures,
                )
                continue
            if current_proc is not None and interface_depth > 0:
                current_proc = self._handle_interface_procedure_declaration_line(
                    s,
                    current_proc=current_proc,
                    current_module=current_module,
                    signatures=signatures,
                    filename=filename,
                    lineno=lineno,
                    source_line=source_line,
                )
                continue

            if l.startswith("end subroutine") or l.startswith("end function") or l.startswith("end procedure") or l == "end":
                self._finalize_procedure_block(current_proc, signatures)
                current_proc = None
                continue
            if self._is_contains_transition(s):
                current_proc["in_contains"] = True
                continue
            if current_proc.get("in_contains"):
                continue

            if re.match(r"^type\s+\w+$", s, flags=re.IGNORECASE):
                current_proc["local_type_depth"] = current_proc.get("local_type_depth", 0) + 1
                continue
            if current_proc.get("local_type_depth", 0) > 0:
                if re.match(r"^end\s+type\b", s, flags=re.IGNORECASE):
                    current_proc["local_type_depth"] -= 1
                continue

            parsed_use = _parse_use_statement(s)
            if parsed_use:
                module_name, mappings = parsed_use
                current_proc["uses"][module_name] = mappings
                continue

            if current_proc.get("in_exec_part"):
                continue

            if _is_executable_statement_start(s):
                current_proc["in_exec_part"] = True
                continue

            self._parse_procedure_declaration_line(s, current_proc, filename=filename, lineno=lineno, source_line=source_line)

        if current_proc is not None:
            self._finalize_procedure_block(current_proc, signatures)

        return signatures

    def _parse_procedure_declaration_line(self, line: str, proc_state: dict, filename: str | None = None, lineno: int | None = None, source_line: str | None = None) -> None:
        """Parse one declaration/specification line inside a procedure scope.

        The method mutates `proc_state` in-place by:
        - registering typed symbols and parameter constants,
        - annotating argument metadata (type/kind/intent/rank/shape),
        - recording imports/includes/external callbacks,
        - transitioning unsupported/unknown declarations into explicit errors.
        """
        stripped = line.strip()
        if _is_openmp_declarative_directive(stripped):
            raise FortranParseError(
                f"Unsupported OpenMP declarative directive in procedure '{proc_state['signature'].name}': {stripped}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        if self._handle_proc_implicit_line(stripped, proc_state):
            return
        if self._handle_proc_external_line(stripped, proc_state):
            return
        # This parser is a subset parser focused on wrapper-relevant metadata.
        # These statements do not affect extracted signature typing/shapes.
        if self._is_ignored_proc_spec_line(stripped):
            return
        if self._handle_proc_include_or_import_line(stripped, proc_state):
            return
        if self._handle_proc_parameter_line(
            stripped,
            proc_state,
            filename=filename,
            lineno=lineno,
            source_line=source_line,
        ):
            return

        parsed_decl = _parse_common_declaration_line(
            stripped,
            filename=proc_state.get("filename") or filename,
            line_number=lineno,
            source_line=source_line,
            include_intent=True,
        )
        if parsed_decl is None:
            self._handle_unknown_proc_declaration(
                line,
                proc_state,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )
            return

        meta, right = parsed_decl
        self._apply_declaration_to_procedure_state(
            meta,
            right,
            proc_state,
            filename=filename,
            lineno=lineno,
            source_line=source_line,
        )


    # ------------------------------------------------------------------
    # Module/submodule/program/block-data variable declarations
    # ------------------------------------------------------------------

    def _parse_module_variable_line(self, line: str, module: FortranModule | FortranSubmodule | FortranProgram | FortranBlockData, filename: str | None, lineno: int | None = None, source_line: str | None = None) -> None:
        """Parse one specification-part declaration line for a module-like scope.

        Applies to modules/submodules/programs/block-data units that share
        declaration grammar. Only declaration lines are consumed; executable
        or contained-procedure sections are handled by caller scope logic.
        """
        stripped = line.strip()
        if not stripped:
            return
        if _is_openmp_declarative_directive(stripped):
            owner_kind, owner_name = _variable_scope_label(module)
            raise FortranParseError(
                f"Unsupported OpenMP declarative directive in {owner_kind} '{owner_name or '<unnamed>'}': {stripped}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        if _DERIVED_TYPE_RE.match(stripped):
            return
        if "::" in stripped:
            left, right = [x.strip() for x in stripped.split("::", 1)]
            lower_left = left.lower()
            if lower_left == "public":
                names = [n.strip() for n in split_csv(right) if n.strip()]
                if names:
                    module.public_symbols.extend(names)
                else:
                    module.default_visibility = "public"
                return
            if lower_left == "private":
                names = [n.strip() for n in split_csv(right) if n.strip()]
                if names:
                    module.private_symbols.extend(names)
                else:
                    module.default_visibility = "private"
                return
            if lower_left == "module procedure":
                return
            if lower_left == "import":
                return
        elif _is_executable_statement_start(stripped) or _is_ignored_spec_statement(stripped):
            if _is_executable_statement_start(stripped) and not isinstance(module, FortranProgram):
                owner_kind, owner_name = _variable_scope_label(module)
                raise FortranParseError(
                    f"Executable statement is not allowed in {owner_kind} specification part '{owner_name or '<unnamed>'}': {line.strip()}",
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
            return

        parsed_decl = _parse_common_declaration_line(
            stripped,
            filename=filename,
            line_number=lineno,
            source_line=source_line,
            parse_character_star=not isinstance(module, (FortranModule, FortranSubmodule)),
        )
        if parsed_decl is None:
            if "::" not in stripped and not _looks_like_declaration_or_spec(stripped):
                return
            owner_kind, owner_name = _variable_scope_label(module)
            raise FortranParseError(
                f"Unknown or unsupported datatype declaration in {owner_kind} '{owner_name or '<unnamed>'}': {line.strip()}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        meta, right = parsed_decl

        for v in split_csv(right):
            name, shape = _var(v)
            if not name:
                continue
            var = FortranArgument(name=_normalize_declared_name(name, meta))
            _apply(var, meta, shape)
            module.variables.append(var)
    def _parse_single_procedure_signature(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    ) -> FortranProcedureSignature:
        return _expect_single_parse_result(
            self._collect_procedure_signatures(code, filename=filename, macro_defines=macro_defines),
            parser_name="parse_single_procedure_signature",
            entity_name="procedure signature",
            filename=filename,
        )

    def _collect_project_procedure_signatures(self, files: dict[str, str]) -> list[FortranProcedureSignature]:
        module_params: dict[str, dict[str, str]] = {}
        parsed_files: list[tuple[str, list[FortranProcedureSignature]]] = []
        preprocessed_files = {fname: preprocess_lines(code, fname) for fname, code in files.items()}
        for fname, lines in preprocessed_files.items():
            module_params.update(self._collect_module_parameters(lines, fname))
            parsed_files.append((fname, self._collect_procedure_signatures(lines, filename=fname)))

        for _, signatures in parsed_files:
            for sig in signatures:
                _resolve_signature_kinds(sig, module_params)

        out: list[FortranProcedureSignature] = []
        for _, signatures in parsed_files:
            out.extend(signatures)
        return out

    def _collect_module_parameters(self, code: _SourceOrLines, filename: str | None) -> dict[str, dict[str, str]]:
        lines = self._preprocessed_lines(code, filename)
        current_module = None
        in_module_spec_part = False
        output: dict[str, dict[str, str]] = {}
        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()
            if l.startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", l):
                current_module = s.split()[1].lower()
                in_module_spec_part = True
                output.setdefault(current_module, {})
                continue
            if l.startswith("contains") and current_module is not None:
                in_module_spec_part = False
                continue
            if l.startswith("end module"):
                current_module = None
                in_module_spec_part = False
                continue
            if current_module is None or not in_module_spec_part:
                continue
            if l == "contains":
                in_module_spec_part = False
                continue
            if not in_module_spec_part:
                continue
            pm = _PARAM_RE.match(s)
            if not pm:
                continue
            for assign in split_csv(pm.group("body")):
                if "=" not in assign:
                    continue
                k, v = [x.strip() for x in assign.split("=", 1)]
                output[current_module][k.lower()] = v
        return output
    # ------------------------------------------------------------------
    # File/project orchestration and cross-file resolution
    # ------------------------------------------------------------------

    def visit_fortran_file(
        self,
        source: str | Path,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        encoding: str = "utf-8",
    ) -> FortranFile:
        """Parse one source string/path into a `FortranFile` aggregate model."""
        if filename is None and _looks_like_existing_source_path(source):
            path = Path(source)
            filename = str(path)
            code = path.read_text(encoding=encoding)
        else:
            code = str(source)

        effective_macro_defines = self.macro_defines if macro_defines is None else macro_defines
        lines = preprocess_lines(code, filename)
        signatures = self._collect_procedure_signatures(lines, filename=filename, macro_defines=effective_macro_defines)
        derived_types = self.visit_fortran_types(lines, filename=filename)
        interfaces = self.visit_fortran_interfaces(lines, filename=filename)
        modules = self.visit_fortran_modules(
            lines,
            filename=filename,
            require_present=False,
            signatures=signatures,
            types=derived_types,
            interfaces=interfaces,
        )
        submodules = self.visit_fortran_submodules(
            lines,
            filename=filename,
            signatures=signatures,
            types=derived_types,
            interfaces=interfaces,
        )
        programs = self.visit_fortran_programs(lines, filename=filename)
        block_data_units = self.visit_fortran_block_data(lines, filename=filename)

        owned_proc_ids = {id(proc) for mod in modules for proc in mod.procedures}
        owned_proc_ids.update(id(proc) for submod in submodules for proc in submod.procedures)
        standalone_procedures = [
            sig for sig in signatures
            if sig.module is None and not sig.in_interface and id(sig) not in owned_proc_ids
        ]

        file = FortranFile(
            filename=filename,
            source=code,
            encoding=encoding,
            format=_source_form(filename),
            modules=modules,
            submodules=submodules,
            programs=programs,
            block_data_units=block_data_units,
            procedures=standalone_procedures,
            interfaces=[iface for iface in interfaces if iface.module is None],
            derived_types=[dtype for dtype in derived_types if dtype.module is None],
        )

        for m in modules:
            self._insert_unique_scope_symbol(file.symbols, m.name.lower(), m, label="file scope", filename=filename)
        for sm in submodules:
            self._insert_unique_scope_symbol(file.symbols, sm.name.lower(), sm, label="file scope", filename=filename)
        for p in standalone_procedures:
            self._insert_unique_scope_symbol(file.symbols, p.name.lower(), p, label="file scope", filename=filename)
        return file

    def parse_fortran_file(
        self,
        source: str | Path,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        encoding: str = "utf-8",
    ) -> FortranFile:
        return self.visit_fortran_file(
            source,
            filename=filename,
            macro_defines=macro_defines,
            encoding=encoding,
        )

    def visit_fortran_project(
        self,
        files: dict[str, str] | list[str | Path] | tuple[str | Path, ...] | str | Path,
        *,
        encoding: str = "utf-8",
    ) -> FortranProject:
        """Parse many sources and merge them into one dependency-aware project model."""
        if isinstance(files, dict):
            parsed_files = [self.visit_file(code, filename=fname, encoding=encoding) for fname, code in files.items()]
        elif isinstance(files, (str, Path)):
            namespace = self._parse_fortran_namespace(files)
            parsed_files = [self.visit_file(path, encoding=encoding) for path in namespace["files"]]
        else:
            parsed_files = [self.visit_file(path, encoding=encoding) for path in files]

        module_params: dict[str, dict[str, str]] = {}
        for parsed_file in parsed_files:
            if parsed_file.source is not None:
                module_params.update(self._collect_module_parameters(parsed_file.source, parsed_file.filename))

        seen_procedures: set[int] = set()
        for parsed_file in parsed_files:
            for proc in parsed_file.procedures:
                if id(proc) not in seen_procedures:
                    _resolve_signature_kinds(proc, module_params, resolve_shapes=False)
                    seen_procedures.add(id(proc))
            for module in parsed_file.modules:
                for proc in module.procedures:
                    if id(proc) not in seen_procedures:
                        _resolve_signature_kinds(proc, module_params, resolve_shapes=False)
                        seen_procedures.add(id(proc))
            for submodule in parsed_file.submodules:
                for proc in submodule.procedures:
                    if id(proc) not in seen_procedures:
                        _resolve_signature_kinds(proc, module_params, resolve_shapes=False)
                        seen_procedures.add(id(proc))

        project = FortranProject(files=parsed_files)

        for f in parsed_files:
            for module in f.modules:
                module_key = module.name.lower()
                self._insert_unique_scope_symbol(project.modules, module_key, module, label="project module scope")
                project.dependencies[module_key] = {name.lower() for name in module.uses}
                for proc in module.procedures:
                    proc_key = f"{module_key}.{proc.name.lower()}"
                    self._insert_unique_scope_symbol(project.procedures, proc_key, proc, label="project procedure scope")
                    project.procedures.setdefault(proc.name.lower(), proc)
                for dtype in module.derived_types:
                    dtype_key = f"{module_key}.{dtype.name.lower()}"
                    self._insert_unique_scope_symbol(project.derived_types, dtype_key, dtype, label="project derived-type scope")
                    project.derived_types.setdefault(dtype.name.lower(), dtype)
                for iface in module.interfaces:
                    if iface.name:
                        iface_key = f"{module_key}.{iface.name.lower()}"
                        self._insert_unique_scope_symbol(project.interfaces, iface_key, iface, label="project interface scope")
                        project.interfaces.setdefault(iface.name.lower(), iface)
            for submodule in f.submodules:
                submodule_key = submodule.name.lower()
                self._insert_unique_scope_symbol(project.submodules, submodule_key, submodule, label="project submodule scope")
                deps = {submodule.parent.lower(), *(name.lower() for name in submodule.uses)}
                if submodule.ancestor:
                    deps.add(submodule.ancestor.lower())
                project.dependencies[submodule_key] = deps
                for proc in submodule.procedures:
                    proc_key = f"{submodule_key}.{proc.name.lower()}"
                    self._insert_unique_scope_symbol(project.procedures, proc_key, proc, label="project procedure scope")
                    project.procedures.setdefault(proc.name.lower(), proc)
            for program in f.programs:
                if program.name:
                    self._insert_unique_scope_symbol(project.programs, program.name.lower(), program, label="project program scope")
                    project.dependencies[program.name.lower()] = {name.lower() for name in program.uses}
            for proc in f.procedures:
                self._insert_unique_scope_symbol(project.procedures, proc.name.lower(), proc, label="project procedure scope")
            for dtype in f.derived_types:
                self._insert_unique_scope_symbol(project.derived_types, dtype.name.lower(), dtype, label="project derived-type scope")
            for iface in f.interfaces:
                if iface.name:
                    self._insert_unique_scope_symbol(project.interfaces, iface.name.lower(), iface, label="project interface scope")
        return project

    def parse_fortran_project(self, files, *, encoding: str = "utf-8") -> FortranProject:
        return self.visit_fortran_project(files, encoding=encoding)

    # ------------------------------------------------------------------
    # Derived types, modules, interfaces, and other program units
    # ------------------------------------------------------------------

    def _init_derived_type(
        self,
        line: str,
        *,
        current_module: str | None,
    ) -> FortranDerivedType | None:
        parsed_type = self._parse_derived_type_start(line)
        if not parsed_type:
            return None

        type_name, attrs = parsed_type
        extends = None
        normalized_attrs: list[str] = []
        for attr in attrs:
            lowered = attr.lower()
            if lowered.startswith("extends(") and lowered.endswith(")"):
                extends = attr[attr.find("(") + 1 : -1].strip()
            else:
                normalized_attrs.append(lowered)

        return FortranDerivedType(
            name=type_name,
            module=current_module,
            extends=extends,
            attributes=normalized_attrs,
        )

    def _parse_derived_type_contains_line(
        self,
        line: str,
        dtype: FortranDerivedType,
        *,
        filename: str | None = None,
        lineno: int | None = None,
        source_line: str | None = None,
    ) -> None:
        proc_binding = _PROC_BIND_RE.match(line)
        if proc_binding:
            binding_names = split_csv(proc_binding.group("names"))
            dtype.methods.extend(binding_names)
            left = line.split("::", 1)[0]
            attrs = [a.strip().lower() for a in split_csv(left.split(",", 1)[1] if "," in left else "")]
            for name in binding_names:
                dtype.procedure_bindings.append({"name": name, "attrs": attrs})
            return

        if line.lower().startswith("generic") and "::" in line and "=>" in line:
            left, right = [x.strip() for x in line.split("::", 1)]
            attr_txt = left[len("generic") :].strip().lstrip(",").strip()
            attrs = [a.strip().lower() for a in split_csv(attr_txt)] if attr_txt else []
            lhs, rhs_txt = [x.strip() for x in right.split("=>", 1)]
            rhs = [r.strip() for r in split_csv(rhs_txt)]
            dtype.generic_bindings.append({"name": lhs, "targets": rhs, "attrs": attrs})
            return

        if _looks_like_declaration_or_spec(line):
            raise FortranParseError(
                f"Unsupported or malformed type-bound declaration in type '{dtype.name}': {line.strip()}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )

    def _finalize_derived_type(
        self,
        dtype: FortranDerivedType,
        types: list[FortranDerivedType],
        filename: str | None,
    ) -> None:
        _validate_derived_type_fields(dtype, filename)
        types.append(dtype)

    @staticmethod
    def _resolve_derived_type_extensions(types: list[FortranDerivedType]) -> None:
        by_name = {t.name.lower(): t for t in types}
        for dtype in types:
            if isinstance(dtype.extends, str):
                parent = by_name.get(dtype.extends.lower())
                if parent is not None:
                    dtype.extends = parent

    def _parse_fortran_types_impl(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:
        """Parse derived-type blocks (`type ... end type`) and their members.

        Scope model:
        - Tracks containing module/submodule name for type ownership.
        - Opens a type block when a type-start declaration is found.
        - Splits specification-part fields from `contains` type-bound procedure
          bindings and generic bindings until `end type`.
        """
        lines = self._preprocessed_lines(code, filename)
        current_module = None
        current_type: FortranDerivedType | None = None
        in_type_contains = False
        types: list[FortranDerivedType] = []

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()

            current_module, handled_scope = self._track_containing_module_scope(current_module, s)
            if handled_scope:
                continue

            if current_type is None:
                current_type = self._init_derived_type(s, current_module=current_module)
                if current_type is not None:
                    in_type_contains = False
                continue

            if self._is_contains_transition(s):
                in_type_contains = True
                continue

            if l.startswith("end type"):
                self._finalize_derived_type(current_type, types, filename)
                current_type = None
                in_type_contains = False
                continue

            if in_type_contains:
                self._parse_derived_type_contains_line(
                    s,
                    current_type,
                    filename=filename,
                    lineno=lineno,
                    source_line=source_line,
                )
                continue

            self._parse_type_field_line(s, current_type, filename, lineno=lineno, source_line=source_line)

        self._resolve_derived_type_extensions(types)
        return types


    def _parse_type_field_line(self, line: str, dtype: FortranDerivedType, filename: str | None, lineno: int | None = None, source_line: str | None = None) -> None:
        stripped = line.strip()
        if re.match(r"^type\s*::\s*\w+$", stripped, re.IGNORECASE):
            return
        if stripped.lower() in {"sequence", "private"}:
            return
        if _is_openmp_declarative_directive(stripped):
            raise FortranParseError(
                f"Unsupported OpenMP declarative directive in type '{dtype.name}': {stripped}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        parsed_decl = _parse_common_declaration_line(
            stripped,
            filename=filename,
            line_number=lineno,
            source_line=source_line,
            parse_character_star=False,
        )
        if parsed_decl is None:
            if "::" not in stripped and not _looks_like_declaration_or_spec(stripped):
                return
            raise FortranParseError(
                f"Unknown or unsupported datatype declaration in type '{dtype.name}': {line.strip()}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        meta, right = parsed_decl

        for v in split_csv(right):
            name, shape = _var(v)
            if not name:
                continue
            field = FortranArgument(name=_normalize_declared_name(name, meta))
            _apply(field, meta, shape)
            dtype.fields.append(field)

    def _parse_derived_type_start(self, line: str) -> tuple[str, list[str]] | None:
        stripped = line.strip()
        tm = _DERIVED_TYPE_RE.match(stripped)
        if tm:
            attr_txt = (tm.group("attrs") or "").strip().lstrip(",").strip()
            attrs = [a.strip() for a in split_csv(attr_txt)] if attr_txt else []
            return tm.group("name"), attrs
        legacy = re.match(r"^type\s+(?P<name>\w+)\s*$", stripped, re.IGNORECASE)
        if legacy:
            return legacy.group("name"), []
        return None

    def _parse_fortran_derived_type(self, code: _SourceOrLines, filename: str | None = None) -> FortranDerivedType:  # pragma: no cover - private compatibility shim.
        return _expect_single_parse_result(
            self._parse_fortran_types(code, filename=filename),
            parser_name="parse_fortran_derived_type",
            entity_name="derived type",
            filename=filename,
        )

    def _parse_fortran_modules_impl(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        require_present: bool = True,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranModule]:
        """Parse `module ... end module` blocks and collect module scope state.

        Scope model:
        - Opens module scope at `module <name>` and closes on `end module`.
        - Reads only specification-part declarations into module variables; once
          `contains` starts, variable collection stops for that module block.
        - Attaches already parsed procedures/types/interfaces by matching module
          names, preserving ownership and visibility rules.
        """
        lines = self._preprocessed_lines(code, filename)
        modules: list[FortranModule] = []
        current: FortranModule | None = None
        in_contains = False
        interface_depth = 0
        type_depth = 0

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()

            module = self._parse_module_header(s, filename, lineno=lineno, source_line=source_line)
            if module is not None:
                current = module
                in_contains = False
                interface_depth = 0
                type_depth = 0
                continue

            if l.startswith("end module"):
                if current is not None:
                    self._finalize_module(current, modules, filename)
                current = None
                in_contains = False
                interface_depth = 0
                type_depth = 0
                continue

            if current is None:
                continue

            if self._is_contains_transition(s):
                in_contains = True
                continue
            if in_contains:
                continue

            if _is_derived_type_block_start(s):
                type_depth += 1
                continue
            if l.startswith("end type"):
                type_depth = max(0, type_depth - 1)
                continue
            if l.startswith("interface") or l.startswith("abstract interface"):
                interface_depth += 1
                continue
            if l.startswith("end interface"):
                interface_depth = max(0, interface_depth - 1)
                continue
            if interface_depth > 0 or type_depth > 0:
                continue

            self._collect_module_spec_line(
                current,
                s,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )

        signatures = self._collect_procedure_signatures(code, filename) if signatures is None else signatures
        types = self._parse_fortran_types(code, filename) if types is None else types
        interfaces = self._parse_fortran_interfaces(code, filename) if interfaces is None else interfaces
        self._attach_module_children(
            modules,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )
        if require_present and not modules and signatures:
            raise FortranParseError(
                "_parse_fortran_modules() expected a module program unit, but only standalone procedures were found",
                filename=filename,
                code="PARSE_WRONG_ENTRYPOINT",
            )
        return modules

    def _parse_fortran_module(self, code: _SourceOrLines, filename: str | None = None) -> FortranModule:  # pragma: no cover - private compatibility shim.
        return _expect_single_parse_result(
            self._parse_fortran_modules(code, filename=filename, require_present=True),
            parser_name="parse_fortran_module",
            entity_name="module",
            filename=filename,
        )

    @staticmethod
    def _parse_interface_header(line: str) -> tuple[bool, str | None]:
        lower = line.lower()
        if not (lower.startswith("interface") or lower.startswith("abstract interface")):
            return False, None
        parts = line.split(maxsplit=1)
        name = parts[1].strip() if len(parts) > 1 and not lower.startswith("abstract interface") else None
        return True, name

    @staticmethod
    def _add_interface_attribute(sig: FortranProcedureSignature, interface_name: str | None) -> None:
        if not interface_name:
            return
        iface_attr = f"interface({interface_name})"
        if iface_attr not in sig.attributes:
            sig.attributes.append(iface_attr)

    def _finalize_interface_procedure(
        self,
        proc_state: dict,
        interface: FortranInterface,
    ) -> None:
        sig = _finalize_proc(proc_state)
        self._add_interface_attribute(sig, interface.name)
        interface.procedures.append(sig)

    @staticmethod
    def _finalize_interface(interface: FortranInterface, interfaces: list[FortranInterface]) -> None:
        interfaces.append(interface)

    def _parse_fortran_interfaces_impl(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:
        """Parse `interface ... end interface` blocks and their procedure members.

        Scope model:
        - Tracks containing module/submodule for interface ownership.
        - Opens interface scope at `interface [name]` and closes at
          `end interface`.
        - Parses contained procedure declarations with signature rules and
          annotates them as interface members.
        """
        lines = self._preprocessed_lines(code, filename)
        current_module = None
        current_interface: FortranInterface | None = None
        current_proc = None
        interfaces: list[FortranInterface] = []

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()

            current_module, handled_scope = self._track_containing_module_scope(current_module, s)
            if handled_scope:
                continue

            starts_interface, interface_name = self._parse_interface_header(s)
            if starts_interface:
                current_interface = FortranInterface(name=interface_name, module=current_module)
                current_proc = None
                continue

            if l.startswith("end interface"):
                if current_proc is not None and current_interface is not None:
                    self._finalize_interface_procedure(current_proc, current_interface)
                    current_proc = None
                if current_interface is not None:
                    self._finalize_interface(current_interface, interfaces)
                current_interface = None
                continue

            if current_interface is None:
                continue

            if current_proc is None:
                parsed = self._parse_interface_procedure_header(
                    s,
                    current_module,
                    filename=filename,
                    lineno=lineno,
                    source_line=source_line,
                )
                if parsed:
                    current_proc = parsed
                    current_proc["filename"] = filename
                    current_proc["header_lineno"] = lineno
                    current_proc["header_source_line"] = source_line
                else:
                    self._raise_if_unparsed_procedure_header(
                        s,
                        in_interface=True,
                        filename=filename,
                        lineno=lineno,
                        source_line=source_line,
                    )
                continue

            if l.startswith("end subroutine") or l.startswith("end function") or l == "end":
                self._finalize_interface_procedure(current_proc, current_interface)
                current_proc = None
                continue

            self._parse_procedure_declaration_line(s, current_proc, filename=filename, lineno=lineno, source_line=source_line)

        return interfaces

    def _parse_interface_procedure_header(
        self,
        line: str,
        module: str | None,
        filename: str | None = None,
        lineno: int | None = None,
        source_line: str | None = None,
    ):
        return self._parse_procedure_header(
            line,
            module,
            True,
            filename=filename,
            lineno=lineno,
            source_line=source_line,
        )

    def _parse_procedure_header(
        self,
        line: str,
        module: str | None,
        in_interface: bool,
        filename: str | None = None,
        lineno: int | None = None,
        source_line: str | None = None,
    ):
        module_proc = _MOD_PROC_IMPL_RE.match(line)
        if module_proc and not in_interface:
            name = module_proc.group("name")
            sig = FortranProcedureSignature(
                name=name,
                kind="module procedure",
                module=module,
                attributes=["module procedure"],
                in_interface=in_interface,
            )
            return self._new_procedure_scope_state(sig, symbols={})

        m = _PROC_RE.match(line)
        if m:
            args = [FortranArgument(name=a, procedure=m.group("name")) for a in split_csv(m.group("args") or "")]
            sig = FortranProcedureSignature(
                name=m.group("name"),
                kind="subroutine",
                module=module,
                arguments=args,
                attributes=_attrs(m.group("prefix"), m.group("tail")),
                in_interface=in_interface,
            )
            return self._new_procedure_scope_state(
                sig,
                symbols={a.name.lower(): a for a in args},
            )
        m = _FUNC_RE.match(line)
        if not m:
            return None
        prefix = (m.group("prefix") or "").strip()
        args = [FortranArgument(name=a, procedure=m.group("name")) for a in split_csv(m.group("args") or "")]
        result_match = _RESULT_RE.search(m.group("tail"))
        explicit_result = result_match is not None
        result_name = result_match.group("name") if result_match else m.group("name")
        result = FortranArgument(name=result_name, procedure=m.group("name"))

        type_tokens = [t for t in prefix.split() if t.lower() not in _ATTR_PREFIX_WORDS]
        type_prefix = " ".join(type_tokens)
        parsed_prefix = _parse_type_prefix(type_prefix)
        if type_prefix and parsed_prefix is None:
            raise FortranParseError(
                f"Unsupported function result type prefix '{type_prefix}' in procedure header.",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        if parsed_prefix:
            result.base_type, result.kind = parsed_prefix

        sig = FortranProcedureSignature(
            name=m.group("name"),
            kind="function",
            module=module,
            arguments=args,
            result=result,
            attributes=_attrs(m.group("prefix"), m.group("tail")),
            in_interface=in_interface,
        )
        return self._new_procedure_scope_state(
            sig,
            symbols={**{a.name.lower(): a for a in args}, result_name.lower(): result},
            typed_symbols={result_name.lower()} if parsed_prefix else set(),
            explicit_result=explicit_result,
        )

    def _parse_fortran_interface(self, code: _SourceOrLines, filename: str | None = None) -> FortranInterface:  # pragma: no cover - private compatibility shim.
        return _expect_single_parse_result(
            self._parse_fortran_interfaces(code, filename=filename),
            parser_name="parse_fortran_interface",
            entity_name="interface",
            filename=filename,
        )

    def _parse_fortran_submodules_impl(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        *,
        signatures: list[FortranProcedureSignature] | None = None,
        types: list[FortranDerivedType] | None = None,
        interfaces: list[FortranInterface] | None = None,
    ) -> list[FortranSubmodule]:
        """Parse `submodule(parent) name ... end submodule` units.

        Scope model:
        - Resolves parent/ancestor from submodule header.
        - Collects specification-part `use` and declarations before `contains`.
        - Attaches procedures/types/interfaces whose parsed owner matches the
          submodule name.
        """
        lines = self._preprocessed_lines(code, filename)
        submodules: list[FortranSubmodule] = []
        current: FortranSubmodule | None = None
        in_contains = False
        interface_depth = 0
        type_depth = 0

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()

            submodule = self._parse_submodule_header(s, filename)
            if submodule is not None:
                current = submodule
                in_contains = False
                interface_depth = 0
                type_depth = 0
                continue

            if l.startswith("end submodule"):
                if current is not None:
                    self._finalize_submodule(current, submodules, filename)
                current = None
                in_contains = False
                interface_depth = 0
                type_depth = 0
                continue

            if current is None:
                continue

            if self._is_contains_transition(s):
                in_contains = True
                continue
            if in_contains:
                continue

            if _is_derived_type_block_start(s):
                type_depth += 1
                continue
            if l.startswith("end type"):
                type_depth = max(0, type_depth - 1)
                continue
            if l.startswith("interface") or l.startswith("abstract interface"):
                interface_depth += 1
                continue
            if l.startswith("end interface"):
                interface_depth = max(0, interface_depth - 1)
                continue
            if interface_depth > 0 or type_depth > 0:
                continue

            self._collect_submodule_spec_line(
                current,
                s,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )

        signatures = self._collect_procedure_signatures(code, filename) if signatures is None else signatures
        types = self._parse_fortran_types(code, filename) if types is None else types
        interfaces = self._parse_fortran_interfaces(code, filename) if interfaces is None else interfaces
        self._attach_submodule_children(
            submodules,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )
        return submodules

    def _parse_fortran_submodule(self, code: _SourceOrLines, filename: str | None = None) -> FortranSubmodule:  # pragma: no cover - private compatibility shim.
        return _expect_single_parse_result(
            self._parse_fortran_submodules(code, filename=filename),
            parser_name="parse_fortran_submodule",
            entity_name="submodule",
            filename=filename,
        )

    def _parse_fortran_programs_impl(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:
        """Parse `program ... end program` blocks.

        Scope model:
        - Opens a program unit at `program <name>` and closes at `end program`.
        - Collects specification-part `use` and declarations until `contains`.
        - Ignores internal procedures in `contains` for program-variable scope.
        """
        lines = self._preprocessed_lines(code, filename)
        programs: list[FortranProgram] = []
        current: FortranProgram | None = None
        in_contains = False
        in_exec_part = False

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()

            program = self._parse_program_header(s, filename)
            if program is not None:
                current = program
                in_contains = False
                in_exec_part = False
                continue

            if l.startswith("end program"):
                if current is not None:
                    self._finalize_program(current, programs, filename)
                current = None
                in_contains = False
                in_exec_part = False
                continue

            if current is None:
                continue

            if self._is_contains_transition(s):
                in_contains = True
                in_exec_part = False
                continue
            if in_contains:
                continue
            if in_exec_part:
                continue
            if _is_executable_statement_start(s):
                in_exec_part = True
                continue

            self._collect_program_spec_line(
                current,
                s,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )
        return programs

    def _parse_fortran_program(self, code: _SourceOrLines, filename: str | None = None) -> FortranProgram:  # pragma: no cover - private compatibility shim.
        return _expect_single_parse_result(
            self._parse_fortran_programs(code, filename=filename),
            parser_name="parse_fortran_program",
            entity_name="program",
            filename=filename,
        )

    def _parse_fortran_block_data(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:
        """Parse `block data` units and their declaration sections."""
        lines = self._preprocessed_lines(code, filename)
        blocks: list[FortranBlockData] = []
        current: FortranBlockData | None = None

        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()

            block_data = self._parse_block_data_header(s, filename)
            if block_data is not None:
                current = block_data
                continue

            if current is not None and (l.startswith("end block data") or l == "end"):
                self._finalize_block_data(current, blocks, filename)
                current = None
                continue
            if current is None:
                continue
            self._collect_block_data_line(
                current,
                s,
                filename=filename,
                lineno=lineno,
                source_line=source_line,
            )
        return blocks

    def _parse_fortran_block_data_unit(self, code: _SourceOrLines, filename: str | None = None) -> FortranBlockData:  # pragma: no cover - private compatibility shim.
        return _expect_single_parse_result(
            self._parse_fortran_block_data(code, filename=filename),
            parser_name="parse_fortran_block_data_unit",
            entity_name="block data unit",
            filename=filename,
        )

    def _parse_fortran_namespace(
        self,
        root: str | Path,
        extensions: tuple[str, ...] = (".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"),
    ) -> dict:
        root_path = Path(root)
        files = sorted([p for p in root_path.rglob("*") if p.suffix.lower() in extensions])
        sources = {str(p): p.read_text(encoding="utf-8") for p in files}
        file_lines = {fname: preprocess_lines(code, fname) for fname, code in sources.items()}

        module_to_file: dict[str, str] = {}
        submodule_to_file: dict[str, str] = {}
        file_to_uses: dict[str, set[str]] = {fname: set() for fname in sources}
        modules_by_file: dict[str, list[str]] = {}
        submodules_by_file: dict[str, list[str]] = {}
        for fname, _code in sources.items():
            lines = file_lines[fname]
            modules = self._parse_fortran_modules(lines, filename=fname, require_present=False, signatures=[], types=[], interfaces=[])
            submodules = self._parse_fortran_submodules(lines, filename=fname, signatures=[], types=[], interfaces=[])
            modules_by_file[fname] = [m.name for m in modules]
            submodules_by_file[fname] = [m.name for m in submodules]
            for m in modules:
                module_to_file[m.name.lower()] = fname
                file_to_uses[fname].update(u.lower() for u in m.uses)
            for sm in submodules:
                submodule_to_file[sm.name.lower()] = fname
                file_to_uses[fname].add(sm.parent.lower())
                if sm.ancestor:
                    file_to_uses[fname].add(sm.ancestor.lower())
                file_to_uses[fname].update(u.lower() for u in sm.uses)

        file_dependencies: dict[str, set[str]] = {}
        for fname, used_modules in file_to_uses.items():
            deps = set()
            for mod in used_modules:
                dep_file = module_to_file.get(mod) or submodule_to_file.get(mod)
                if dep_file and dep_file != fname:
                    deps.add(dep_file)
            file_dependencies[fname] = deps

        ordered_files = _topological_files(file_dependencies)
        signatures = self._collect_project_procedure_signatures({f: sources[f] for f in ordered_files})
        types = []
        modules = []
        submodules = []
        programs = []
        block_data = []
        for f in ordered_files:
            lines = file_lines[f]
            file_types = self._parse_fortran_types(lines, filename=f)
            file_interfaces = self._parse_fortran_interfaces(lines, filename=f)
            file_signatures = self._collect_procedure_signatures(lines, filename=f)
            types.extend(file_types)
            modules.extend(self._parse_fortran_modules(
                lines,
                filename=f,
                require_present=False,
                signatures=file_signatures,
                types=file_types,
                interfaces=file_interfaces,
            ))
            submodules.extend(self._parse_fortran_submodules(
                lines,
                filename=f,
                signatures=file_signatures,
                types=file_types,
                interfaces=file_interfaces,
            ))
            programs.extend(self._parse_fortran_programs(lines, filename=f))
            block_data.extend(self._parse_fortran_block_data(lines, filename=f))

        return {
            "files": ordered_files,
            "file_dependencies": {k: sorted(v) for k, v in file_dependencies.items()},
            "module_to_file": module_to_file,
            "submodule_to_file": submodule_to_file,
            "modules": modules,
            "submodules": submodules,
            "programs": programs,
            "block_data": block_data,
            "types": types,
            "signatures": signatures,
        }

    def visit_fortran_wrap_readiness(self, code: str, filename: str | None = None) -> dict:
        lines = self._preprocessed_lines(code, filename)
        signatures = self._collect_procedure_signatures(lines, filename)
        types = self.visit_fortran_types(lines, filename)
        interfaces = self.visit_fortran_interfaces(lines, filename)
        modules = self.visit_fortran_modules(
            lines,
            filename,
            require_present=False,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )
        submodules = self.visit_fortran_submodules(
            lines,
            filename,
            signatures=signatures,
            types=types,
            interfaces=interfaces,
        )
        programs = self.visit_fortran_programs(lines, filename)
        block_data = self.visit_fortran_block_data(lines, filename)
        unsupported: list[dict] = []
        for line, lineno, source_line in lines:
            for p in _UNSUPPORTED_PATTERNS:
                if p.search(line):
                    unsupported.append({"line": lineno, "text": line.strip(), "pattern": p.pattern})
                    break

        missing_decl_args: list[str] = []
        for sig in signatures:
            for a in sig.arguments:
                if a.base_type == "unknown":
                    missing_decl_args.append(f"{sig.name}:{a.name}")

        module_params = self._collect_module_parameters(code, filename)
        unresolved_derived_args, unresolved_derived_fields = _collect_unresolved_derived_type_diagnostics(
            signatures,
            types,
            modules,
        )
        unresolved_kind_args, unresolved_kind_fields = _collect_unresolved_kind_diagnostics(
            signatures,
            types,
            modules,
            module_params,
        )
        blockers = _build_wrap_blockers(
            signatures=signatures,
            unsupported=unsupported,
            missing_decl_args=missing_decl_args,
            unresolved_derived_args=unresolved_derived_args,
            unresolved_derived_fields=unresolved_derived_fields,
            unresolved_kind_args=unresolved_kind_args,
            unresolved_kind_fields=unresolved_kind_fields,
        )

        return {
            "n_signatures": len(signatures),
            "n_types": len(types),
            "n_modules": len(modules),
            "n_submodules": len(submodules),
            "n_programs": len(programs),
            "n_block_data": len(block_data),
            "unsupported_constructs": unsupported,
            "unknown_argument_types": missing_decl_args,
            "unresolved_derived_type_arguments": unresolved_derived_args,
            "unresolved_derived_type_fields": unresolved_derived_fields,
            "unresolved_kind_arguments": unresolved_kind_args,
            "unresolved_kind_fields": unresolved_kind_fields,
            "wrappability_blockers": blockers,
            "why_not_wrappable": [b["message"] for b in blockers],
            "wrappable": not blockers,
        }

    def assess_wrap_readiness(self, code: str, filename: str | None = None) -> dict:
        return self.visit_fortran_wrap_readiness(code, filename=filename)

    def _preprocessed_lines(self, source: _SourceOrLines, filename: str | None) -> _PreprocessedLines:
        """Return preprocessed source lines, reusing file-level preprocessing when supplied."""
        if isinstance(source, list):
            return source
        return preprocess_lines(source, filename)


# -----------------------------------------------------------------------------
# Module-level convenience wrappers
# -----------------------------------------------------------------------------

_DEFAULT_PARSER = FortranParser()

# Module-level parser entrypoints are intentionally limited.

def parse_fortran_file(
    source_or_path: str | Path,
    filename: str | None = None,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    encoding: str = "utf-8",
) -> FortranFile:
    return _DEFAULT_PARSER.parse_file(
        source_or_path,
        filename=filename,
        macro_defines=macro_defines,
        encoding=encoding,
    )


def parse_fortran_project(files, *, encoding: str = "utf-8") -> FortranProject:
    return _DEFAULT_PARSER.parse_project(files, encoding=encoding)


def assess_wrap_readiness(code: str, filename: str | None = None) -> dict:
    return _DEFAULT_PARSER.assess_wrap_readiness(code, filename=filename)
