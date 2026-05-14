# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import ast
from pathlib     import Path
from dataclasses import replace

from .lexer         import preprocess_lines
from .models        import FortranArgument, FortranBlockData, FortranDerivedType, FortranFile, FortranInterface, FortranModule, FortranParseError, FortranProcedureSignature, FortranProgram, FortranProject, FortranSubmodule, FortranVariable
from .type_resolver import extract_kind_from_type_spec
from .utils         import split_csv

_TYPE_RE = re.compile(r"^(integer|real|complex|logical|character|double\s+precision)\s*(\([^)]*\))?\s*(.*)$", re.IGNORECASE)
_CHAR_STAR_RE = re.compile(r"^character\s*\*\s*(?P<len>\([^)]*\)|\*|[A-Za-z_]\w*|\d+)\s*(?P<rest>.*)$", re.IGNORECASE)
_PROC_RE = re.compile(r"^(?P<prefix>(?:\w+\s+)*)subroutine\s+(?P<name>\w+)\s*\((?P<args>[^)]*)\)\s*(?P<tail>.*)$", re.IGNORECASE)
_FUNC_RE = re.compile(r"^(?P<prefix>(?:\w+\s+)*)function\s+(?P<name>\w+)\s*\((?P<args>[^)]*)\)\s*(?P<tail>.*)$", re.IGNORECASE)
_RESULT_RE = re.compile(r"results?\s*\(\s*(?P<name>\w+)\s*\)", re.IGNORECASE)
_ATTR_PREFIX_WORDS = {"pure", "elemental", "recursive"}

_BINDC_RE = re.compile(r"bind\s*\(\s*c\s*(?:,\s*name\s*=\s*['\"][^'\"]*['\"])?\s*\)", re.IGNORECASE)
_USE_RE = re.compile(r"^use\s+(?P<module>\w+)\s*(?:,\s*only\s*:\s*(?P<symbols>.*))?$", re.IGNORECASE)
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
_SUBMODULE_RE = re.compile(r"^submodule\s*\(\s*(?P<parent>[^)]+?)\s*\)\s*(?P<name>\w+)\s*$", re.IGNORECASE)
_MOD_PROC_IMPL_RE = re.compile(r"^module\s+procedure\s+(?P<name>\w+)\s*$", re.IGNORECASE)
_PROGRAM_RE = re.compile(r"^program\s+(?P<name>\w+)\s*$", re.IGNORECASE)
_BLOCK_DATA_RE = re.compile(r"^block\s+data(?:\s+(?P<name>\w+))?\s*$", re.IGNORECASE)
_INTRINSIC_KIND_SYMBOLS = {
    "int8", "int16", "int32", "int64",
    "real32", "real64", "real128",
    "c_signed_char", "c_short", "c_int", "c_long", "c_long_long",
    "c_size_t", "c_int8_t", "c_int16_t", "c_int32_t", "c_int64_t",
    "c_int_least8_t", "c_int_least16_t", "c_int_least32_t", "c_int_least64_t",
    "c_int_fast8_t", "c_int_fast16_t", "c_int_fast32_t", "c_int_fast64_t",
    "c_float", "c_double", "c_long_double",
    "c_float_complex", "c_double_complex", "c_long_double_complex",
    "c_bool", "c_char",
}

_UNSUPPORTED_PATTERNS = (
    re.compile(r"\bclass\s*\(\s*\*\s*\)", re.IGNORECASE),
    re.compile(r"\bselect\s+type\b", re.IGNORECASE),
    re.compile(r"\bcoarray\b|\[[^\]]*\]", re.IGNORECASE),
    re.compile(r"\bprocedure\s*,\s*pointer\b", re.IGNORECASE),
    re.compile(r"\btype\s*\(\s*c_ptr\s*\)", re.IGNORECASE),
)


_PreprocessedLines = list[tuple[str, int | None, str | None]]
_SourceOrLines = str | _PreprocessedLines


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


def _parse_derived_type_start(line: str) -> tuple[str, list[str]] | None:
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


def _preprocessed_lines(source: _SourceOrLines, filename: str | None) -> _PreprocessedLines:
    """Return preprocessed source lines, reusing file-level preprocessing when supplied."""
    if isinstance(source, list):
        return source
    return preprocess_lines(source, filename)



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
        return base, extract_kind_from_type_spec(base, type_spec)
    derived = _TYPE_FIELD_RE.match(txt)
    if derived:
        return "derived", derived.group("dtype")
    class_derived = _CLASS_FIELD_RE.match(txt)
    if class_derived:
        return "derived", class_derived.group("dtype")
    return None


def _enforce_source_form_compatibility(line: str, filename: str | None, lineno: int | None = None, source_line: str | None = None) -> None:
    """Raise `FortranParseError` if a file's dialect/source-form is violated.

    This guard enforces a strict contract used throughout the parser:

    - Files recognized as **Fortran 77** (by suffix) must not contain modern-only
      constructs such as `module`, `contains`, or `interface`.

    The goal is to fail fast on mixed-standard inputs that would otherwise
    produce ambiguous metadata.
    """
    if not filename or Path(filename).suffix.lower() != ".f77":
        return
    forbidden = (
        r"\bmodule\b",
        r"\bsubmodule\b",
        r"\bcontains\b",
        r"\binterface\b",
        r"\bclass\s*\(",
    )
    for pat in forbidden:
        if re.search(pat, line, re.IGNORECASE):
            raise FortranParseError(
                f"Unsupported syntax for Fortran 77 source '{filename}': {line.strip()}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )


def _parse_fortran_signatures(
    code: _SourceOrLines,
    filename: str | None = None,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
) -> list[FortranProcedureSignature]:
    """Parse procedure signatures from a single Fortran source string.

    Produces `FortranProcedureSignature` objects for top-level procedures and
    module-contained procedures. Internal procedures in a `contains` block are
    intentionally ignored for the host routine signature.

    Notes
    -----
    - Raw source input is normalized by `preprocess_lines`; file/project
      callers pass already-normalized lines so preprocessing happens once.
    - Declarations are only applied while the parser is in the specification
      part; once an executable statement start is detected, later lines are
      ignored for declaration purposes.
    - Procedures declared inside `interface ... end interface` are included and
      flagged with `in_interface=True`.
    """
    lines = _preprocessed_lines(code, filename)
    macro_selection_enabled = macro_defines is not None
    signatures: list[FortranProcedureSignature] = []
    interface_memberships: dict[str, set[str]] = {}
    declared_procedures: dict[tuple[str | None, bool], dict[str, list[frozenset[str]]]] = {}
    current_module = None
    current_module_uses: dict[str, list[str]] = {}
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

        if s.startswith("#"):
            directive = s[1:].strip()
            directive_low = directive.lower()
            if directive_low.startswith("ifdef "):
                pp_group_counter += 1
                pp_condition_stack.append((pp_group_counter, 0))
                expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
                pp_active_stack.append((bool(expr) and expr.lower() in macro_names) if macro_selection_enabled else True)
                continue
            if directive_low.startswith("ifndef "):
                pp_group_counter += 1
                pp_condition_stack.append((pp_group_counter, 0))
                expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
                pp_active_stack.append(((not expr) or expr.lower() not in macro_names) if macro_selection_enabled else True)
                continue
            if directive_low.startswith("if "):
                pp_group_counter += 1
                pp_condition_stack.append((pp_group_counter, 0))
                expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
                pp_active_stack.append(_eval_cpp_expr(expr, macro_names) if macro_selection_enabled else True)
                continue
            if directive_low.startswith("else"):
                if pp_condition_stack:
                    group_id, branch_id = pp_condition_stack.pop()
                    pp_condition_stack.append((group_id, branch_id + 1))
                if pp_active_stack:
                    prev = pp_active_stack.pop()
                    pp_active_stack.append((not prev) if macro_selection_enabled else True)
                continue
            if directive_low.startswith("elif "):
                if pp_condition_stack:
                    group_id, branch_id = pp_condition_stack.pop()
                    pp_condition_stack.append((group_id, branch_id + 1))
                if pp_active_stack:
                    pp_active_stack.pop()
                    expr = directive.split(None, 1)[1].strip() if len(directive.split(None, 1)) > 1 else ""
                    pp_active_stack.append(_eval_cpp_expr(expr, macro_names) if macro_selection_enabled else True)
                continue
            if directive_low.startswith("endif"):
                if pp_condition_stack:
                    pp_condition_stack.pop()
                if pp_active_stack:
                    pp_active_stack.pop()
                continue

        if macro_selection_enabled and pp_active_stack and not all(pp_active_stack):
            continue

        l = s.lower()

        _enforce_source_form_compatibility(s, filename, lineno, source_line)

        if l.startswith("interface"):
            interface_depth += 1
            parts = s.split(maxsplit=1)
            iface_name = parts[1].strip() if len(parts) > 1 else None
            interface_name_stack.append(iface_name)
            continue
        if l.startswith("end interface"):
            interface_depth = max(0, interface_depth - 1)
            if interface_name_stack:
                interface_name_stack.pop()
            continue

        submodule_match = _SUBMODULE_RE.match(s)
        if submodule_match:
            current_module = submodule_match.group("name")
            current_module_uses = {}
            continue
        if l.startswith("end submodule"):
            current_module = None
            current_module_uses = {}
            continue

        if _PROGRAM_RE.match(s):
            program_depth += 1
            continue
        if l.startswith("end program"):
            program_depth = max(0, program_depth - 1)
            continue
        if program_depth > 0:
            continue

        if l.startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", l):
            current_module = s.split()[1]
            current_module_uses = {}
            continue
        if l.startswith("end module"):
            current_module = None
            current_module_uses = {}
            continue

        if current_proc is None:
            m = _USE_RE.match(s)
            if m and current_module is not None:
                current_module_uses[m.group("module")] = split_csv(m.group("symbols")) if m.group("symbols") else []
                continue

        if current_proc is None:
            current_proc = _parse_header(s, current_module, interface_depth > 0)
            if current_proc:
                scope_key = (current_module.lower() if current_module else None, interface_depth > 0)
                seen_in_scope = declared_procedures.setdefault(scope_key, {})
                proc_name = current_proc["signature"].name.lower()
                condition_set = frozenset(
                    f"g{group_id}:b{branch_id}" for group_id, branch_id in pp_condition_stack
                )
                existing_conditions = seen_in_scope.setdefault(proc_name, [])
                if any(_preprocessor_conditions_overlap(existing, condition_set) for existing in existing_conditions):
                    scope_label = (
                        f"module '{current_module}'" if current_module is not None else "global scope"
                    )
                    raise FortranParseError(
                        f"Duplicate procedure name '{current_proc['signature'].name}' in {scope_label}.",
                        filename=filename,
                        line_number=lineno,
                        source_line=source_line,
                    )
                existing_conditions.append(condition_set)
                current_proc["uses"].update(current_module_uses)
                current_proc["filename"] = filename
                current_proc["header_lineno"] = lineno
                current_proc["header_source_line"] = source_line
                current_proc["in_exec_part"] = False
            continue

        if current_proc is not None and current_proc.get("in_contains"):
            if l.startswith("end subroutine") or l.startswith("end function") or l.startswith("end procedure"):
                end_parts = l.split()
                end_name = end_parts[2] if len(end_parts) > 2 else None
                if end_name == current_proc["signature"].name.lower():
                    signatures.append(_finalize_proc(current_proc))
                    current_proc = None
            continue
        if current_proc is not None and interface_depth > 0:
            if l.startswith("function ") or l.startswith("subroutine "):
                iface_proc = _parse_header(s, current_module, True)
                if iface_proc:
                    iface_name = iface_proc["signature"].name.lower()
                    current_proc["typed_symbols"].add(iface_name)
                    arg = current_proc["symbols"].get(iface_name)
                    if arg is not None:
                        arg.base_type = "procedure"
                        arg.kind = None
            continue

        if l.startswith("end subroutine") or l.startswith("end function") or l.startswith("end procedure") or l == "end":
            signatures.append(_finalize_proc(current_proc))
            current_proc = None
            continue
        if l == "contains":
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

        m = _USE_RE.match(s)
        if m:
            symbols = split_csv(m.group("symbols")) if m.group("symbols") else []
            current_proc["uses"][m.group("module")] = symbols
            continue

        if current_proc.get("in_exec_part"):
            continue

        if _is_executable_statement_start(s):
            current_proc["in_exec_part"] = True
            continue

        _parse_declaration(s, current_proc, filename=filename, lineno=lineno, source_line=source_line)

    if current_proc is not None:
        signatures.append(_finalize_proc(current_proc))
    for sig in signatures:
        for iface_name in sorted(interface_memberships.get(sig.name.lower(), set())):
            iface_attr = f"interface({iface_name})"
            if iface_attr not in sig.attributes:
                sig.attributes.append(iface_attr)

    return signatures


def _parse_fortran_project_signatures(files: dict[str, str]) -> list[FortranProcedureSignature]:
    """Parse signatures for multiple files and resolve cross-file kinds/shapes.

    This is a two-pass routine:
    - pass 1: parse each file and collect module-scope `parameter` constants
    - pass 2: for each signature, resolve kind/shape expressions using imported
      module parameters (honoring `use, only:` restrictions when present)
    """
    module_params: dict[str, dict[str, str]] = {}
    parsed_files: list[tuple[str, list[FortranProcedureSignature]]] = []
    preprocessed_files = {fname: preprocess_lines(code, fname) for fname, code in files.items()}
    for fname, lines in preprocessed_files.items():
        module_params.update(_collect_module_parameters(lines, fname))
        parsed_files.append((fname, _parse_fortran_signatures(lines, filename=fname)))

    for _, signatures in parsed_files:
        for sig in signatures:
            _resolve_signature_kinds(sig, module_params)

    out: list[FortranProcedureSignature] = []
    for _, signatures in parsed_files:
        out.extend(signatures)
    return out


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
    if not txt:
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


def _looks_like_existing_source_path(source: str | Path) -> bool:
    """Return True when ``source`` names a readable source file path."""
    if not isinstance(source, (str, Path)):
        return False
    text = str(source)
    if "\n" in text or "\r" in text:
        return False
    return Path(text).is_file()


def _parse_fortran_file(
    source: str | Path,
    filename: str | None = None,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    encoding: str = "utf-8",
) -> FortranFile:
    """Parse one Fortran source unit and return a structured ``FortranFile``.

    ``source`` is treated as source text by default. When ``filename`` is not
    supplied and ``source`` is an existing filesystem path, the file is read and
    that path becomes the filename. This keeps string parsing filename-free while
    preserving a convenient path-based entrypoint.
    """
    if filename is None and _looks_like_existing_source_path(source):
        path = Path(source)
        filename = str(path)
        code = path.read_text(encoding=encoding)
    else:
        code = str(source)

    lines = preprocess_lines(code, filename)

    signatures = _parse_fortran_signatures(lines, filename=filename, macro_defines=macro_defines)
    derived_types = _parse_fortran_types(lines, filename=filename)
    interfaces = _parse_fortran_interfaces(lines, filename=filename)
    modules = _parse_fortran_modules_impl(
        lines,
        filename=filename,
        require_present=False,
        signatures=signatures,
        types=derived_types,
        interfaces=interfaces,
    )
    submodules = _parse_fortran_submodules(
        lines,
        filename=filename,
        signatures=signatures,
        types=derived_types,
        interfaces=interfaces,
    )
    programs = _parse_fortran_programs(lines, filename=filename)
    block_data_units = _parse_fortran_block_data(lines, filename=filename)

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
    def _add_file_symbol(name: str, symbol: object) -> None:
        key = name.lower()
        if key in file.symbols:
            raise FortranParseError(
                f"Duplicate symbol '{name}' in file scope.",
                filename=filename,
            )
        file.symbols[key] = symbol

    for m in modules:
        _add_file_symbol(m.name, m)
    for sm in submodules:
        _add_file_symbol(sm.name, sm)
    for p in standalone_procedures:
        _add_file_symbol(p.name, p)
    return file


def _parse_fortran_signature(
    code: _SourceOrLines,
    filename: str | None = None,
    macro_defines: set[str] | dict[str, int | bool | str] | None = None,
) -> FortranProcedureSignature:
    return _DEFAULT_PARSER.parse_signature(code, filename=filename, macro_defines=macro_defines)


def _parse_fortran_project(
    files: dict[str, str] | list[str | Path] | tuple[str | Path, ...],
    *,
    encoding: str = "utf-8",
) -> FortranProject:
    """Parse multiple Fortran files and return a ``FortranProject`` aggregate."""
    if isinstance(files, dict):
        parsed_files = [parse_fortran_file(code, filename=fname, encoding=encoding) for fname, code in files.items()]
    else:
        parsed_files = [parse_fortran_file(path, encoding=encoding) for path in files]

    project = FortranProject(files=parsed_files)

    def _add_scoped_symbol(scope: dict[str, object], key: str, value: object, *, label: str) -> None:
        if key in scope:
            raise FortranParseError(f"Duplicate symbol '{key}' in {label}.")
        scope[key] = value

    for f in parsed_files:
        for module in f.modules:
            module_key = module.name.lower()
            _add_scoped_symbol(project.modules, module_key, module, label="project module scope")
            project.dependencies[module_key] = {name.lower() for name in module.uses}
            for proc in module.procedures:
                proc_key = f"{module_key}.{proc.name.lower()}"
                _add_scoped_symbol(project.procedures, proc_key, proc, label="project procedure scope")
                project.procedures.setdefault(proc.name.lower(), proc)
            for dtype in module.derived_types:
                dtype_key = f"{module_key}.{dtype.name.lower()}"
                _add_scoped_symbol(project.derived_types, dtype_key, dtype, label="project derived-type scope")
                project.derived_types.setdefault(dtype.name.lower(), dtype)
            for iface in module.interfaces:
                if iface.name:
                    iface_key = f"{module_key}.{iface.name.lower()}"
                    _add_scoped_symbol(project.interfaces, iface_key, iface, label="project interface scope")
                    project.interfaces.setdefault(iface.name.lower(), iface)
        for submodule in f.submodules:
            submodule_key = submodule.name.lower()
            _add_scoped_symbol(project.submodules, submodule_key, submodule, label="project submodule scope")
            deps = {submodule.parent.lower(), *(name.lower() for name in submodule.uses)}
            if submodule.ancestor:
                deps.add(submodule.ancestor.lower())
            project.dependencies[submodule_key] = deps
            for proc in submodule.procedures:
                proc_key = f"{submodule_key}.{proc.name.lower()}"
                _add_scoped_symbol(project.procedures, proc_key, proc, label="project procedure scope")
                project.procedures.setdefault(proc.name.lower(), proc)
        for program in f.programs:
            if program.name:
                _add_scoped_symbol(project.programs, program.name.lower(), program, label="project program scope")
                project.dependencies[program.name.lower()] = {name.lower() for name in program.uses}
        for proc in f.procedures:
            _add_scoped_symbol(project.procedures, proc.name.lower(), proc, label="project procedure scope")
        for dtype in f.derived_types:
            _add_scoped_symbol(project.derived_types, dtype.name.lower(), dtype, label="project derived-type scope")
        for iface in f.interfaces:
            if iface.name:
                _add_scoped_symbol(project.interfaces, iface.name.lower(), iface, label="project interface scope")
    return project


def _parse_fortran_types(code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:
    """Parse `type ... end type` derived type blocks from a source string.

    Captures:
    - fields (including rank/shape, pointer/allocatable)
    - `extends(parent)` relationships (linked to same-file parent objects)
    - type-bound procedures and generic bindings inside the type `contains` part
    """
    lines = _preprocessed_lines(code, filename)
    current_module = None
    current_type: FortranDerivedType | None = None
    in_type_contains = False
    types: list[FortranDerivedType] = []
    for line, lineno, source_line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename, lineno, source_line)
        submodule_match = _SUBMODULE_RE.match(s)
        if submodule_match:
            current_module = submodule_match.group("name")
            continue
        if l.startswith("end submodule"):
            current_module = None
            continue
        if l.startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", l):
            current_module = s.split()[1]
            continue
        if l.startswith("end module"):
            current_module = None
            continue
        if current_type is None:
            parsed_type = _parse_derived_type_start(s)
            if parsed_type:
                type_name, attrs = parsed_type
                extends = None
                normalized_attrs: list[str] = []
                for a in attrs:
                    la = a.lower()
                    if la.startswith("extends(") and la.endswith(")"):
                        extends = a[a.find("(") + 1 : -1].strip()
                    else:
                        normalized_attrs.append(la)
                current_type = FortranDerivedType(
                    name=type_name,
                    module=current_module,
                    extends=extends,
                    attributes=normalized_attrs,
                )
                in_type_contains = False
            continue
        if l == "contains":
            in_type_contains = True
            continue
        if l.startswith("end type"):
            _validate_derived_type_fields(current_type, filename)
            types.append(current_type)
            current_type = None
            in_type_contains = False
            continue
        if in_type_contains:
            pm = _PROC_BIND_RE.match(s)
            if pm:
                binding_names = split_csv(pm.group("names"))
                current_type.methods.extend(binding_names)
                left = s.split("::", 1)[0]
                attrs = [a.strip().lower() for a in split_csv(left.split(",", 1)[1] if "," in left else "")]
                for n in binding_names:
                    current_type.procedure_bindings.append({"name": n, "attrs": attrs})
                continue
            if s.lower().startswith("generic") and "::" in s and "=>" in s:
                left, right = [x.strip() for x in s.split("::", 1)]
                attr_txt = left[len("generic") :].strip().lstrip(",").strip()
                attrs = [a.strip().lower() for a in split_csv(attr_txt)] if attr_txt else []
                lhs, rhs_txt = [x.strip() for x in right.split("=>", 1)]
                rhs = [r.strip() for r in split_csv(rhs_txt)]
                current_type.generic_bindings.append({"name": lhs, "targets": rhs, "attrs": attrs})
            continue
        _parse_type_field_line(s, current_type, filename, lineno=lineno, source_line=source_line)
    by_name = {t.name.lower(): t for t in types}
    for t in types:
        if isinstance(t.extends, str):
            parent = by_name.get(t.extends.lower())
            if parent is not None:
                t.extends = parent
    return types


def _parse_fortran_derived_type(code: _SourceOrLines, filename: str | None = None) -> FortranDerivedType:
    return _DEFAULT_PARSER.parse_derived_type(code, filename=filename)


def _parse_fortran_modules_impl(
    code: _SourceOrLines,
    filename: str | None = None,
    *,
    require_present: bool = False,
    signatures: list[FortranProcedureSignature] | None = None,
    types: list[FortranDerivedType] | None = None,
    interfaces: list[FortranInterface] | None = None,
) -> list[FortranModule]:
    """Parse module blocks and attach child entities (procedures/types/interfaces).

    The module object includes:
    - `uses` map from `use` statements in the module specification part
    - module variables declared in the specification part
    - procedures/types/interfaces discovered in the same source and associated
      back to the owning module
    """
    lines = _preprocessed_lines(code, filename)
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
        _enforce_source_form_compatibility(s, filename, lineno, source_line)
        if l.startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", l):
            current = FortranModule(name=s.split()[1], filename=filename)
            in_contains = False
            interface_depth = 0
            type_depth = 0
            continue
        if l.startswith("end module"):
            if current:
                _validate_module_variables(current, filename)
                _apply_module_visibility(current)
                modules.append(current)
            current = None
            in_contains = False
            interface_depth = 0
            type_depth = 0
            continue
        if current is None:
            continue
        if l.startswith("contains"):
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
        if l.startswith("interface"):
            interface_depth += 1
            continue
        if l.startswith("end interface"):
            interface_depth = max(0, interface_depth - 1)
            continue
        if interface_depth > 0 or type_depth > 0:
            continue
        if l == "private":
            current.default_visibility = "private"
            continue
        if l == "public":
            current.default_visibility = "public"
            continue
        m = _USE_RE.match(s)
        if m:
            current.uses[m.group("module")] = split_csv(m.group("symbols")) if m.group("symbols") else []
            continue
        _parse_module_variable_line(s, current, filename, lineno=lineno, source_line=source_line)

    # Attach parsed procedures/types/interfaces to their owning modules.
    signatures = signatures if signatures is not None else _parse_fortran_signatures(code, filename)
    types = types if types is not None else _parse_fortran_types(code, filename)
    interfaces = interfaces if interfaces is not None else _parse_fortran_interfaces(code, filename)
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
    if require_present and not modules and signatures:
        raise FortranParseError(
            "_parse_fortran_modules() expected a module program unit, but only standalone procedures were found",
            filename=filename,
            code="PARSE_WRONG_ENTRYPOINT",
        )
    return modules


def _parse_fortran_modules(code: _SourceOrLines, filename: str | None = None) -> list[FortranModule]:
    """Parse module blocks; raise when the source only contains standalone procedures."""
    return _parse_fortran_modules_impl(code, filename=filename, require_present=True)


def _parse_fortran_module(code: _SourceOrLines, filename: str | None = None) -> FortranModule:
    return _DEFAULT_PARSER.parse_module(code, filename=filename)


def _parse_fortran_interfaces(code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:
    return _DEFAULT_PARSER._parse_fortran_interfaces(code, filename=filename)


def _parse_fortran_interface(code: _SourceOrLines, filename: str | None = None) -> FortranInterface:
    return _DEFAULT_PARSER.parse_interface(code, filename=filename)



def _split_submodule_parent(parent_spec: str) -> tuple[str, str | None]:
    parts = [p.strip() for p in parent_spec.split(":", 1)]
    if len(parts) == 2:
        ancestor, parent = parts
        return parent, ancestor
    return parts[0], None


def _parse_fortran_submodules(
    code: _SourceOrLines,
    filename: str | None = None,
    *,
    signatures: list[FortranProcedureSignature] | None = None,
    types: list[FortranDerivedType] | None = None,
    interfaces: list[FortranInterface] | None = None,
) -> list[FortranSubmodule]:
    """Parse Fortran 2008 ``submodule`` blocks and their owned entities.

    Submodules are returned separately from modules because their header points
    back to an ancestor module (and optionally a parent submodule) instead of
    defining a standalone module namespace. Procedures implemented with either
    ``module subroutine/function`` or ``module procedure`` are attached to the
    submodule object.
    """
    lines = _preprocessed_lines(code, filename)
    submodules: list[FortranSubmodule] = []
    current: FortranSubmodule | None = None
    in_contains = False
    for line, lineno, source_line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename, lineno, source_line)
        sm = _SUBMODULE_RE.match(s)
        if sm:
            parent, ancestor = _split_submodule_parent(sm.group("parent"))
            current = FortranSubmodule(
                name=sm.group("name"),
                parent=parent,
                ancestor=ancestor,
                filename=filename,
            )
            in_contains = False
            continue
        if l.startswith("end submodule"):
            if current is not None:
                _validate_module_variables(current, filename)
                submodules.append(current)
            current = None
            in_contains = False
            continue
        if current is None:
            continue
        if l.startswith("contains"):
            in_contains = True
            continue
        if in_contains:
            continue
        m = _USE_RE.match(s)
        if m:
            current.uses[m.group("module")] = split_csv(m.group("symbols")) if m.group("symbols") else []
            continue
        _parse_module_variable_line(s, current, filename, lineno=lineno, source_line=source_line)

    signatures = signatures if signatures is not None else _parse_fortran_signatures(code, filename)
    types = types if types is not None else _parse_fortran_types(code, filename)
    interfaces = interfaces if interfaces is not None else _parse_fortran_interfaces(code, filename)
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
    return submodules


def _parse_fortran_submodule(code: _SourceOrLines, filename: str | None = None) -> FortranSubmodule:
    return _DEFAULT_PARSER.parse_submodule(code, filename=filename)


def _parse_fortran_programs(code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:
    return _DEFAULT_PARSER._parse_fortran_programs(code, filename=filename)


def _parse_fortran_program(code: _SourceOrLines, filename: str | None = None) -> FortranProgram:
    return _DEFAULT_PARSER.parse_program(code, filename=filename)


def _parse_fortran_block_data(code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:
    return _DEFAULT_PARSER._parse_fortran_block_data(code, filename=filename)


def _parse_fortran_block_data_unit(code: _SourceOrLines, filename: str | None = None) -> FortranBlockData:
    return _DEFAULT_PARSER.parse_block_data_unit(code, filename=filename)


def _visible_import_modules(symbol: str, uses: dict[str, list[str]]) -> list[str]:
    """Return imported modules that could provide ``symbol`` under Fortran USE rules."""
    wanted = symbol.lower()
    providers: list[str] = []
    for module_name, only_symbols in uses.items():
        normalized_only = [str(sym).lower() for sym in only_symbols]
        if not normalized_only or wanted in normalized_only:
            providers.append(module_name)
    return providers


def _is_plain_symbol_reference(expr: str | None) -> bool:
    """Return True for simple kind symbols, excluding literals and expressions."""
    if expr is None:
        return False
    text = expr.strip()
    if not text or text == "*":
        return False
    return bool(re.fullmatch(r"[A-Za-z_]\w*", text))


def _kind_symbol_is_known(
    symbol: str,
    *,
    owning_module: str | None,
    uses: dict[str, list[str]],
    local_symbols: set[str],
    module_params: dict[str, dict[str, str]],
) -> bool:
    """Check whether a symbolic kind is declared locally or in parsed imports."""
    lowered = symbol.lower()
    if lowered in _INTRINSIC_KIND_SYMBOLS:
        return True
    if lowered in local_symbols:
        return True
    if owning_module and lowered in module_params.get(owning_module.lower(), {}):
        return True
    for provider in _visible_import_modules(symbol, uses):
        if lowered in module_params.get(provider.lower(), {}):
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
        for arg in sig.arguments:
            if arg.base_type != "derived" and _is_plain_symbol_reference(arg.kind) and not _kind_symbol_is_known(
                arg.kind or "",
                owning_module=sig.module,
                uses=sig.uses,
                local_symbols=local_symbols,
                module_params=module_params,
            ):
                unresolved_args.append({
                    "procedure": sig.name,
                    "module": sig.module,
                    "argument": arg.name,
                    "kind": arg.kind,
                    "import_modules": _visible_import_modules(arg.kind or "", sig.uses),
                })
        if sig.result and sig.result.base_type != "derived" and _is_plain_symbol_reference(sig.result.kind) and not _kind_symbol_is_known(
            sig.result.kind or "",
            owning_module=sig.module,
            uses=sig.uses,
            local_symbols=local_symbols,
            module_params=module_params,
        ):
            unresolved_args.append({
                "procedure": sig.name,
                "module": sig.module,
                "argument": sig.result.name,
                "kind": sig.result.kind,
                "import_modules": _visible_import_modules(sig.result.kind or "", sig.uses),
            })

    for dtype in types:
        uses = module_uses.get(dtype.module.lower(), {}) if dtype.module else {}
        local_symbols: set[str] = set()
        for field in dtype.fields:
            if field.base_type != "derived" and _is_plain_symbol_reference(field.kind) and not _kind_symbol_is_known(
                field.kind or "",
                owning_module=dtype.module,
                uses=uses,
                local_symbols=local_symbols,
                module_params=module_params,
            ):
                unresolved_fields.append({
                    "type_owner": dtype.name,
                    "module": dtype.module,
                    "field": field.name,
                    "kind": field.kind,
                    "import_modules": _visible_import_modules(field.kind or "", uses),
                })

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
    if missing_decl_args:
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

def _assess_wrap_readiness(code: str, filename: str | None = None) -> dict:
    """Heuristically assess whether a source is "wrap-ready".

    This is a diagnostic API: it does not try to be a complete static analysis,
    but instead surfaces common wrapper blockers:
    - known unsupported constructs (pattern-based scan)
    - signature arguments that remain undeclared (`base_type == "unknown"`)
    - derived-type and symbolic-kind references that require missing imports
    - basic counts (n_signatures, n_types, n_modules)
    """
    lines = _preprocessed_lines(code, filename)
    signatures = _parse_fortran_signatures(lines, filename)
    types = _parse_fortran_types(lines, filename)
    interfaces = _parse_fortran_interfaces(lines, filename)
    modules = _parse_fortran_modules_impl(
        lines,
        filename,
        require_present=False,
        signatures=signatures,
        types=types,
        interfaces=interfaces,
    )
    submodules = _parse_fortran_submodules(
        lines,
        filename,
        signatures=signatures,
        types=types,
        interfaces=interfaces,
    )
    programs = _parse_fortran_programs(lines, filename)
    block_data = _parse_fortran_block_data(lines, filename)
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

    module_params = _collect_module_parameters(code, filename)
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


def _parse_fortran_namespace(root: str | Path, extensions: tuple[str, ...] = (".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08")) -> dict:
    """Parse a directory tree as a Fortran namespace with dependency ordering.

    The namespace parse:
    - discovers sources under `root` with the provided suffixes
    - builds a file dependency graph from module `use` statements
    - topologically orders files (best-effort; cycles are appended deterministically)
    - parses signatures with cross-file kind/shape resolution
    - returns aggregate modules/types/signatures plus dependency metadata
    """
    root_path = Path(root)
    files = sorted([p for p in root_path.rglob("*") if p.suffix.lower() in extensions])
    sources = {str(p): p.read_text(encoding="utf-8") for p in files}
    file_lines = {fname: preprocess_lines(code, fname) for fname, code in sources.items()}

    module_to_file: dict[str, str] = {}
    submodule_to_file: dict[str, str] = {}
    file_to_uses: dict[str, set[str]] = {fname: set() for fname in sources}
    modules_by_file: dict[str, list[str]] = {}
    submodules_by_file: dict[str, list[str]] = {}
    for fname, code in sources.items():
        lines = file_lines[fname]
        modules = _parse_fortran_modules_impl(lines, filename=fname, require_present=False, signatures=[], types=[], interfaces=[])
        submodules = _parse_fortran_submodules(lines, filename=fname, signatures=[], types=[], interfaces=[])
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
    signatures = _parse_fortran_project_signatures({f: sources[f] for f in ordered_files})
    types = []
    modules = []
    submodules = []
    programs = []
    block_data = []
    for f in ordered_files:
        lines = file_lines[f]
        file_types = _parse_fortran_types(lines, filename=f)
        file_interfaces = _parse_fortran_interfaces(lines, filename=f)
        file_signatures = _parse_fortran_signatures(lines, filename=f)
        types.extend(file_types)
        modules.extend(_parse_fortran_modules_impl(
            lines,
            filename=f,
            require_present=False,
            signatures=file_signatures,
            types=file_types,
            interfaces=file_interfaces,
        ))
        submodules.extend(_parse_fortran_submodules(
            lines,
            filename=f,
            signatures=file_signatures,
            types=file_types,
            interfaces=file_interfaces,
        ))
        programs.extend(_parse_fortran_programs(lines, filename=f))
        block_data.extend(_parse_fortran_block_data(lines, filename=f))

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

# -----------------------------------------------------------------------------
# Helper APIs (used by tests / wrapper generators)
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


def _parse_header(line: str, module: str | None, in_interface: bool):
    module_proc = _MOD_PROC_IMPL_RE.match(line)
    if module_proc and not in_interface:
        name = module_proc.group("name")
        return {
            "signature": FortranProcedureSignature(name=name, kind="module procedure", module=module, attributes=["module procedure"], in_interface=in_interface),
            "symbols": {},
            "typed_symbols": set(),
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

    m = _PROC_RE.match(line)
    if m:
        args = [FortranArgument(name=a, procedure=m.group("name")) for a in split_csv(m.group("args"))]
        return {
            "signature": FortranProcedureSignature(name=m.group("name"), kind="subroutine", module=module, arguments=args, attributes=_attrs(m.group("prefix"), m.group("tail")), in_interface=in_interface),
            "symbols": {a.name.lower(): a for a in args},
            "typed_symbols": set(),
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
    m = _FUNC_RE.match(line)
    if not m:
        return None
    args = [FortranArgument(name=a, procedure=m.group("name")) for a in split_csv(m.group("args"))]
    result_match = _RESULT_RE.search(m.group("tail"))
    explicit_result = result_match is not None
    result_name = result_match.group("name") if result_match else m.group("name")
    result = FortranArgument(name=result_name, procedure=m.group("name"))

    prefix = (m.group("prefix") or "").strip()
    type_tokens = [t for t in prefix.split() if t.lower() not in _ATTR_PREFIX_WORDS]
    type_prefix = " ".join(type_tokens)
    parsed_prefix = _parse_type_prefix(type_prefix)
    if parsed_prefix:
        result.base_type, result.kind = parsed_prefix

    return {
        "signature": FortranProcedureSignature(name=m.group("name"), kind="function", module=module, arguments=args, result=result, attributes=_attrs(m.group("prefix"), m.group("tail")), in_interface=in_interface),
        "symbols": {**{a.name.lower(): a for a in args}, result_name.lower(): result},
        "typed_symbols": {result_name.lower()} if parsed_prefix else set(),
        "explicit_result": explicit_result,
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
    }


def _attrs(prefix: str, tail: str) -> list[str]:
    attrs = [t.lower() for t in prefix.split() if t.lower() in ("pure", "elemental", "recursive")]
    if _BINDC_RE.search(tail):
        attrs.append("bind(c)")
    return attrs


def _parse_declaration(line: str, proc_state: dict, filename: str | None = None, lineno: int | None = None, source_line: str | None = None) -> None:
    stripped = line.strip()
    # This parser is a subset parser focused on wrapper-relevant metadata.
    # Many Fortran statements are intentionally ignored here because they do not
    # affect signature typing/shapes (or because we only support them at the
    # module/project resolution layer).
    if re.match(r"^implicit\b", stripped, flags=re.IGNORECASE):
        if re.match(r"^implicit\s+none\b", stripped, flags=re.IGNORECASE):
            proc_state["implicit_none"] = True
        return

    external_match = re.match(r"^external\b\s*(?:::)?\s*(?P<names>.*)$", stripped, flags=re.IGNORECASE)
    if external_match:
        names = [n.strip().lower() for n in split_csv(external_match.group("names") or "") if n.strip()]
        for name in names:
            proc_state.setdefault("external_symbols", set()).add(name)
            arg = proc_state["symbols"].get(name)
            if arg is not None and arg.base_type == "unknown":
                arg.base_type = "procedure"
        return
    if re.match(r"^(function|subroutine)\b", stripped, flags=re.IGNORECASE):
        # Legacy callback declarations often appear as bare:
        #   function f(x)
        # inside a procedure declaration section.
        return
    if re.match(r"^intrinsic\b", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^data\b", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^equivalence\b", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^format\s*\(", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^go\s*to\b", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^use\b", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^save\b", stripped, flags=re.IGNORECASE):
        return
    if re.match(r"^common\b", stripped, flags=re.IGNORECASE):
        return
    include_match = _INCLUDE_RE.match(stripped)
    if include_match:
        proc_state.setdefault("includes", []).append(include_match.group("path"))
        return
    import_match = _IMPORT_RE.match(stripped)
    if import_match:
        symbols = [s.strip().lower() for s in split_csv(import_match.group("symbols") or "") if s.strip()]
        proc_state.setdefault("imports", set()).update(symbols)
        return

    pm = _PARAM_RE.match(stripped)
    if pm:
        for assign in split_csv(pm.group("body")):
            if "=" not in assign:
                continue
            k, v = [x.strip() for x in assign.split("=", 1)]
            if k.lower() in proc_state["local_params"]:
                raise FortranParseError(
                    f"Duplicate PARAMETER declaration of symbol '{k}' in procedure '{proc_state['signature'].name}'.",
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
            proc_state["local_params"][k.lower()] = v
        return
    legacy_pm = _LEGACY_PARAM_STMT_RE.match(stripped)
    if legacy_pm:
        for assign in split_csv(legacy_pm.group("body")):
            if "=" not in assign:
                continue
            k, v = [x.strip() for x in assign.split("=", 1)]
            if k.lower() not in proc_state["typed_symbols"] and proc_state.get("implicit_none", False):
                raise FortranParseError(
                    f"Unknown datatype for PARAMETER symbol '{k}' in procedure '{proc_state['signature'].name}'.",
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
            if k.lower() not in proc_state["typed_symbols"]:
                proc_state["local_params"][k.lower()] = v
                proc_state["implicit_typed_symbols"][k.lower()] = _infer_implicit_base_type(k)
                continue
            if k.lower() in proc_state["local_params"]:
                raise FortranParseError(
                    f"Duplicate PARAMETER declaration of symbol '{k}' in procedure '{proc_state['signature'].name}'.",
                    filename=filename,
                    line_number=lineno,
                    source_line=source_line,
                )
            proc_state["local_params"][k.lower()] = v
            proc_state["legacy_local_params"].add(k.lower())
        return
    if "::" in line:
        left, right = [x.strip() for x in line.split("::", 1)]
    else:
        left = line.strip()
        right = ""
    star_kind = _find_legacy_star_kind(left)
    source_form = _source_form(proc_state.get("filename"))
    if star_kind and source_form == "modern" and star_kind[0] != "character":
        base, kind = star_kind
        raise FortranParseError(
            f"Unsupported Fortran 77 star-kind declaration '{base}*{kind}' in modern source '{proc_state.get('filename')}'.",
            filename=filename,
            line_number=lineno,
            source_line=source_line,
        )

    char_star = _CHAR_STAR_RE.match(left)
    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
    class_derived = _CLASS_FIELD_RE.match(left)
    if char_star:
        base = "character"
        kind = char_star.group("len").strip()
        if kind.startswith("(") and kind.endswith(")"):
            kind = kind[1:-1].strip()
        trailing = (char_star.group("rest") or "").strip().lstrip(", ")
        if "::" in line:
            attrs = split_csv(trailing)
        else:
            attrs = []
            right = trailing
    elif tm:
        base = tm.group(1).lower()
        if base == "double precision":
            base = "real"
        type_spec = (tm.group(2) or "").strip()
        trailing = tm.group(3).strip().lstrip(", ")
        kind = extract_kind_from_type_spec(base, type_spec)
        if "::" in line:
            attrs = split_csv(trailing)
        else:
            attrs = []
            right = trailing
    elif derived or class_derived:
        base = "derived"
        kind = (derived or class_derived).group("dtype")
        decl = derived or class_derived
        attrs = split_csv((decl.group("attrs") or "").strip().lstrip(", "))
    elif re.match(r"^procedure\s*\(", left, flags=re.IGNORECASE):
        # Support procedure dummy declarations, e.g.
        #   procedure(my_iface) :: f
        #   procedure(my_iface), pointer :: f
        procm = _PROC_DUMMY_RE.match(left)
        iface = procm.group("iface").lower() if procm else None
        base = "procedure"
        imported = proc_state.get("imports", set())
        kind = None if iface in imported else iface
        attrs = split_csv((procm.group("attrs") if procm else "").strip().lstrip(", "))
    else:
        m_first = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)", line.strip())
        first_word = m_first.group(1).lower() if m_first else ""
        non_decl_starts = {"do", "if", "where", "call", "select", "case", "allocate", "deallocate", "print", "write", "read", "return", "stop", "cycle", "exit", "continue", "end", "else", "elseif", "contains", "goto", "go", "data", "format", "use", "save", "common"}
        if "=" in line and "::" not in line:
            return
        looks_like_decl = bool(re.match(r"^[A-Za-z]", line.strip())) and first_word not in non_decl_starts and ("::" in line or "," in line or " " in line.strip())
        if looks_like_decl:
            if any(p.search(line) for p in _UNSUPPORTED_PATTERNS):
                return
            raise FortranParseError(
                f"Unknown or unsupported datatype declaration for procedure '{proc_state['signature'].name}': {line.strip()}",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        return
    meta = {
        "base_type": base,
        "kind": kind,
        "rank": 0,
        "shape": [],
        "intent": "unknown",
        "optional": False,
        "value": False,
        "allocatable": False,
        "pointer": False,
        "external": False,
    }
    for a in attrs:
        la = a.lower()
        if la.startswith("intent") and "(" in la and ")" in la:
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
        elif la.startswith("dimension") and "(" in a and ")" in a:
            shape = split_csv(a[a.find("(")+1:a.rfind(")")])
            meta["shape"] = shape
            meta["rank"] = len(shape)

    for v in split_csv(right):
        raw_name, shape = _var(v)
        if not raw_name:
            continue
        normalized_name = re.sub(r"^\*\s*[0-9]+\s*", "", raw_name).strip()
        if meta["base_type"] == "character" and "*" in normalized_name:
            # Legacy CHARACTER declarations may carry entity-local length
            # specifiers (e.g. NAME*(*) or SUBNAM*6). Strip the `*len`
            # suffix so symbol lookup matches procedure arguments.
            normalized_name = normalized_name.split("*", 1)[0].strip()
        if not normalized_name:
            continue
        declared = proc_state["typed_symbols"]
        lowered_name = normalized_name.lower()
        if lowered_name in declared:
            raise FortranParseError(
                f"Duplicate declaration of symbol '{normalized_name}' in procedure '{proc_state['signature'].name}'.",
                filename=filename,
                line_number=lineno,
                source_line=source_line,
            )
        declared.add(lowered_name)
        if meta.get("external"):
            proc_state.setdefault("external_symbols", set()).add(lowered_name)
        symbols = proc_state["symbols"]
        # Legacy star-kind declarations can appear as:
        #   COMPLEX*16 AP(*), X(*)
        # In this case the first parsed entity may carry the `*16` token
        # in `raw_name`; always resolve symbols using the normalized name so
        # all listed variables receive the declaration metadata.
        lookup_name = lowered_name
        arg = symbols.get(lookup_name)
        if arg is None:
            proc_state["declared_local_types"][lookup_name] = {
                "base_type": meta["base_type"],
                "kind": meta["kind"],
            }
            continue
        _apply(arg, meta, shape)


def _is_executable_statement_start(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    lowered = stripped.lower()
    first = lowered.split(None, 1)[0]
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
    if re.match(r"^go\s*to\b", lowered):
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
    if not e:
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
    if not part:
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
    if shape:
        arg.shape = shape
        arg.rank = len(shape)
    else:
        arg.shape = list(meta["shape"])
        arg.rank = meta["rank"]
    arg.lbound, arg.ubound = _extract_bounds(arg.shape)

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
    if sig.result is None:
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


def _validate_module_variables(module: FortranModule, filename: str | None) -> None:
    seen: dict[str, FortranArgument] = {}
    for var in module.variables:
        key = var.name.lower()
        if not re.match(r"^[a-z_]\w*$", key, re.IGNORECASE):
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
                    f"Duplicate variable '{var.name}' in module '{module.name}'.",
                    filename=filename,
                )
            continue
        seen[key] = var


def _apply_module_visibility(module: FortranModule) -> None:
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
        if var.base_type == "unknown":
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
        if f.base_type == "unknown":
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
        if arg.name.lower() in declared_symbols and arg.base_type == "unknown":
            raise FortranParseError(
                f"Failed to resolve declared argument '{arg.name}' in procedure '{sig.name}'.",
                filename=filename,
            )
    for arg in sig.arguments:
        if arg.kind:
            arg.kind = _resolve_symbol_reference(arg.kind, local_params)
        if arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, local_params) for dim in arg.shape]
        if arg.base_type == "unknown" and not implicit_none:
            arg.base_type = _infer_implicit_base_type(arg.name)
    if sig.result and sig.result.kind:
        sig.result.kind = _resolve_symbol_reference(sig.result.kind, local_params)
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

    if implicit_none:
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
        if sig.result.base_type == "unknown":
            raise FortranParseError(
                f"Unknown datatype for function result '{sig.result.name}' in procedure '{sig.name}'.",
                filename=filename,
            )
    if sig.kind == "function":
        _validate_function_result(sig, filename)
    sig.uses = dict(state["uses"])
    return replace(sig)


def _collect_module_parameters(code: _SourceOrLines, filename: str | None) -> dict[str, dict[str, str]]:
    lines = _preprocessed_lines(code, filename)
    current_module = None
    in_module_spec_part = False
    output: dict[str, dict[str, str]] = {}
    in_module_spec_part = False
    for line, lineno, source_line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename, lineno, source_line)
        if l.startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", l):
            current_module = s.split()[1].lower()
            in_module_spec_part = True
            output.setdefault(current_module, {})
            in_module_spec_part = True
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

# -----------------------------------------------------------------------------
# Cross-file resolution helpers
# -----------------------------------------------------------------------------


def _resolve_signature_kinds(sig: FortranProcedureSignature, module_params: dict[str, dict[str, str]]) -> None:
    use_map = {k.lower(): [s.lower() for s in v] for k, v in sig.uses.items()}
    symbol_to_value: dict[str, str] = {}
    if sig.module:
        symbol_to_value.update(module_params.get(sig.module.lower(), {}))
    for mod, only_symbols in use_map.items():
        params = module_params.get(mod.lower(), {})
        if only_symbols:
            for sym in only_symbols:
                if sym in params:
                    symbol_to_value[sym] = params[sym]
        else:
            symbol_to_value.update(params)
    for name, var in sig.variables.items():
        if var.value is not None:
            symbol_to_value.setdefault(name.lower(), var.value)
    sig.variables.update(_resolve_variables(symbol_to_value))
    for arg in sig.arguments:
        if arg.kind:
            arg.kind = _resolve_symbol_reference(arg.kind, symbol_to_value)
        if arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, symbol_to_value) for dim in arg.shape]
    if sig.result and sig.result.kind:
        sig.result.kind = _resolve_symbol_reference(sig.result.kind, symbol_to_value)


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
# Derived type and module declaration parsing
# -----------------------------------------------------------------------------


def _parse_type_field_line(line: str, dtype: FortranDerivedType, filename: str | None, lineno: int | None = None, source_line: str | None = None) -> None:
    if "::" not in line:
        return
    if re.match(r"^type\s*::\s*\w+$", line.strip(), re.IGNORECASE):
        return
    left, right = [x.strip() for x in line.split("::", 1)]
    star_kind = _find_legacy_star_kind(left)
    source_form = _source_form(filename)
    if star_kind and source_form == "modern" and star_kind[0] != "character":
        base, kind = star_kind
        raise FortranParseError(
            f"Unsupported Fortran 77 star-kind declaration '{base}*{kind}' in modern source '{filename}'.",
            filename=filename,
            line_number=lineno,
            source_line=source_line,
        )

    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
    class_derived = _CLASS_FIELD_RE.match(left)
    if tm:
        base = tm.group(1).lower()
        type_spec = (tm.group(2) or "").strip()
        attrs = split_csv(tm.group(3).strip().lstrip(", "))
        meta = {
            "base_type": base,
            "kind": extract_kind_from_type_spec(base, type_spec),
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    elif derived or class_derived:
        decl = derived or class_derived
        attrs = split_csv((decl.group("attrs") or "").strip().lstrip(", "))
        meta = {
            "base_type": "derived",
            "kind": decl.group("dtype"),
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    elif re.match(r"^procedure\s*\(", left, re.IGNORECASE):
        procm = _PROC_DUMMY_RE.match(left)
        iface = procm.group("iface").lower() if procm else None
        attrs = split_csv((procm.group("attrs") if procm else "").strip().lstrip(", "))
        meta = {
            "base_type": "procedure",
            "kind": iface,
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    else:
        raise FortranParseError(
            f"Unknown or unsupported datatype declaration in type '{dtype.name}': {line.strip()}",
            filename=filename,
            line_number=lineno,
            source_line=source_line,
        )

    for a in attrs:
        la = a.lower()
        if la == "allocatable":
            meta["allocatable"] = True
        elif la == "pointer":
            meta["pointer"] = True
        elif la == "external":
            meta["external"] = True
        elif la.startswith("dimension") and "(" in a and ")" in a:
            shape = split_csv(a[a.find("(") + 1 : a.rfind(")")])
            meta["shape"] = shape
            meta["rank"] = len(shape)

    for v in split_csv(right):
        name, shape = _var(v)
        if not name:
            continue
        field = FortranArgument(name=name)
        _apply(field, meta, shape)
        dtype.fields.append(field)


def _parse_module_variable_line(line: str, module: FortranModule, filename: str | None, lineno: int | None = None, source_line: str | None = None) -> None:
    if "::" not in line:
        return
    if _DERIVED_TYPE_RE.match(line.strip()):
        return
    left, right = [x.strip() for x in line.split("::", 1)]
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
    star_kind = _find_legacy_star_kind(left)
    source_form = _source_form(filename)
    if star_kind and source_form == "modern" and star_kind[0] != "character":
        base, kind = star_kind
        raise FortranParseError(
            f"Unsupported Fortran 77 star-kind declaration '{base}*{kind}' in modern source '{filename}'.",
            filename=filename,
            line_number=lineno,
            source_line=source_line,
        )

    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
    class_derived = _CLASS_FIELD_RE.match(left)
    if tm:
        base = tm.group(1).lower()
        type_spec = (tm.group(2) or "").strip()
        attrs = split_csv(tm.group(3).strip().lstrip(", "))
        meta = {
            "base_type": base,
            "kind": extract_kind_from_type_spec(base, type_spec),
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    elif derived or class_derived:
        decl = derived or class_derived
        attrs = split_csv((decl.group("attrs") or "").strip().lstrip(", "))
        meta = {
            "base_type": "derived",
            "kind": decl.group("dtype"),
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    elif re.match(r"^procedure\s*\(", left, re.IGNORECASE):
        procm = _PROC_DUMMY_RE.match(left)
        iface = procm.group("iface").lower() if procm else None
        attrs = split_csv((procm.group("attrs") if procm else "").strip().lstrip(", "))
        meta = {
            "base_type": "procedure",
            "kind": iface,
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    elif star_kind:
        base, kind = star_kind
        attrs = []
        meta = {
            "base_type": base.lower(),
            "kind": kind,
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    else:
        raise FortranParseError(
            f"Unknown or unsupported datatype declaration in module '{module.name}': {line.strip()}",
            filename=filename,
            line_number=lineno,
            source_line=source_line,
        )

    for a in attrs:
        la = a.lower()
        if la == "allocatable":
            meta["allocatable"] = True
        elif la == "pointer":
            meta["pointer"] = True
        elif la == "external":
            meta["external"] = True
        elif la.startswith("dimension") and "(" in a and ")" in a:
            shape = split_csv(a[a.find("(") + 1 : a.rfind(")")])
            meta["shape"] = shape
            meta["rank"] = len(shape)

    for v in split_csv(right):
        name, shape = _var(v)
        if not name:
            continue
        var = FortranArgument(name=name)
        _apply(var, meta, shape)
        module.variables.append(var)


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
    def _parse_fortran_signatures(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    ) -> list[FortranProcedureSignature]:
        return _parse_fortran_signatures(code, filename=filename, macro_defines=macro_defines)

    def _parse_fortran_signature(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    ) -> FortranProcedureSignature:
        return _expect_single_parse_result(
            self._parse_fortran_signatures(code, filename=filename, macro_defines=macro_defines),
            parser_name="parse_fortran_signature",
            entity_name="procedure signature",
            filename=filename,
        )

    def _parse_fortran_project_signatures(self, files: dict[str, str]) -> list[FortranProcedureSignature]:
        project = self._parse_fortran_project(files)
        return list(project.procedures.values())

    """Object-oriented public API for the Fortran parser entrypoints.

    New code should prefer this class so parser configuration, such as
    preprocessor macro selections, lives on one instance instead of being
    threaded through separate public functions.
    """

    def _parse_fortran_file(
        self,
        source: str | Path,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        encoding: str = "utf-8",
    ) -> FortranFile:
        if filename is None and _looks_like_existing_source_path(source):
            path = Path(source)
            filename = str(path)
            code = path.read_text(encoding=encoding)
        else:
            code = str(source)

        lines = preprocess_lines(code, filename)
        signatures = _parse_fortran_signatures(lines, filename=filename, macro_defines=macro_defines)
        derived_types = _parse_fortran_types(lines, filename=filename)
        interfaces = _parse_fortran_interfaces(lines, filename=filename)
        modules = _parse_fortran_modules_impl(
            lines,
            filename=filename,
            require_present=False,
            signatures=signatures,
            types=derived_types,
            interfaces=interfaces,
        )
        submodules = _parse_fortran_submodules(
            lines,
            filename=filename,
            signatures=signatures,
            types=derived_types,
            interfaces=interfaces,
        )
        programs = _parse_fortran_programs(lines, filename=filename)
        block_data_units = _parse_fortran_block_data(lines, filename=filename)

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

        def _add_file_symbol(name: str, symbol: object) -> None:
            key = name.lower()
            if key in file.symbols:
                raise FortranParseError(
                    f"Duplicate symbol '{name}' in file scope.",
                    filename=filename,
                )
            file.symbols[key] = symbol

        for m in modules:
            _add_file_symbol(m.name, m)
        for sm in submodules:
            _add_file_symbol(sm.name, sm)
        for p in standalone_procedures:
            _add_file_symbol(p.name, p)
        return file

    def _parse_fortran_project(
        self,
        files: dict[str, str] | list[str | Path] | tuple[str | Path, ...],
        *,
        encoding: str = "utf-8",
    ) -> FortranProject:
        if isinstance(files, dict):
            parsed_files = [self.parse_file(code, filename=fname, encoding=encoding) for fname, code in files.items()]
        else:
            parsed_files = [self.parse_file(path, encoding=encoding) for path in files]

        project = FortranProject(files=parsed_files)

        def _add_scoped_symbol(scope: dict[str, object], key: str, value: object, *, label: str) -> None:
            if key in scope:
                raise FortranParseError(f"Duplicate symbol '{key}' in {label}.")
            scope[key] = value

        for f in parsed_files:
            for module in f.modules:
                module_key = module.name.lower()
                _add_scoped_symbol(project.modules, module_key, module, label="project module scope")
                project.dependencies[module_key] = {name.lower() for name in module.uses}
                for proc in module.procedures:
                    proc_key = f"{module_key}.{proc.name.lower()}"
                    _add_scoped_symbol(project.procedures, proc_key, proc, label="project procedure scope")
                    project.procedures.setdefault(proc.name.lower(), proc)
                for dtype in module.derived_types:
                    dtype_key = f"{module_key}.{dtype.name.lower()}"
                    _add_scoped_symbol(project.derived_types, dtype_key, dtype, label="project derived-type scope")
                    project.derived_types.setdefault(dtype.name.lower(), dtype)
                for iface in module.interfaces:
                    if iface.name:
                        iface_key = f"{module_key}.{iface.name.lower()}"
                        _add_scoped_symbol(project.interfaces, iface_key, iface, label="project interface scope")
                        project.interfaces.setdefault(iface.name.lower(), iface)
            for submodule in f.submodules:
                submodule_key = submodule.name.lower()
                _add_scoped_symbol(project.submodules, submodule_key, submodule, label="project submodule scope")
                deps = {submodule.parent.lower(), *(name.lower() for name in submodule.uses)}
                if submodule.ancestor:
                    deps.add(submodule.ancestor.lower())
                project.dependencies[submodule_key] = deps
                for proc in submodule.procedures:
                    proc_key = f"{submodule_key}.{proc.name.lower()}"
                    _add_scoped_symbol(project.procedures, proc_key, proc, label="project procedure scope")
                    project.procedures.setdefault(proc.name.lower(), proc)
            for program in f.programs:
                if program.name:
                    _add_scoped_symbol(project.programs, program.name.lower(), program, label="project program scope")
                    project.dependencies[program.name.lower()] = {name.lower() for name in program.uses}
            for proc in f.procedures:
                _add_scoped_symbol(project.procedures, proc.name.lower(), proc, label="project procedure scope")
            for dtype in f.derived_types:
                _add_scoped_symbol(project.derived_types, dtype.name.lower(), dtype, label="project derived-type scope")
            for iface in f.interfaces:
                if iface.name:
                    _add_scoped_symbol(project.interfaces, iface.name.lower(), iface, label="project interface scope")
        return project

    def _parse_fortran_types(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:
        return _parse_fortran_types(code, filename=filename)

    def _parse_fortran_derived_type(self, code: _SourceOrLines, filename: str | None = None) -> FortranDerivedType:
        return _expect_single_parse_result(
            self._parse_fortran_types(code, filename=filename),
            parser_name="parse_fortran_derived_type",
            entity_name="derived type",
            filename=filename,
        )

    def _parse_fortran_modules(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranModule]:
        return _parse_fortran_modules(code, filename=filename)

    def _parse_fortran_module(self, code: _SourceOrLines, filename: str | None = None) -> FortranModule:
        return _expect_single_parse_result(
            self._parse_fortran_modules(code, filename=filename),
            parser_name="parse_fortran_module",
            entity_name="module",
            filename=filename,
        )

    def _parse_fortran_interfaces(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:
        lines = _preprocessed_lines(code, filename)
        current_module = None
        current_interface: FortranInterface | None = None
        current_proc = None
        interfaces: list[FortranInterface] = []
        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()
            _enforce_source_form_compatibility(s, filename, lineno, source_line)
            submodule_match = _SUBMODULE_RE.match(s)
            if submodule_match:
                current_module = submodule_match.group("name")
                continue
            if l.startswith("end submodule"):
                current_module = None
                continue
            if l.startswith("module ") and not re.match(r"^module\s+(procedure|subroutine|function)\b", l):
                current_module = s.split()[1]
                continue
            if l.startswith("end module"):
                current_module = None
                continue
            if l.startswith("interface"):
                parts = s.split(maxsplit=1)
                name = parts[1].strip() if len(parts) > 1 else None
                current_interface = FortranInterface(name=name, module=current_module)
                current_proc = None
                continue
            if l.startswith("end interface"):
                if current_proc is not None and current_interface is not None:
                    sig = _finalize_proc(current_proc)
                    if current_interface.name:
                        iface_attr = f"interface({current_interface.name})"
                        if iface_attr not in sig.attributes:
                            sig.attributes.append(iface_attr)
                    current_interface.procedures.append(sig)
                    current_proc = None
                if current_interface is not None:
                    interfaces.append(current_interface)
                current_interface = None
                continue
            if current_interface is None:
                continue

            if current_proc is None:
                parsed = _parse_header(s, current_module, True)
                if parsed:
                    current_proc = parsed
                    current_proc["filename"] = filename
                    current_proc["header_lineno"] = lineno
                    current_proc["header_source_line"] = source_line
                continue

            if l.startswith("end subroutine") or l.startswith("end function") or l == "end":
                sig = _finalize_proc(current_proc)
                if current_interface.name:
                    iface_attr = f"interface({current_interface.name})"
                    if iface_attr not in sig.attributes:
                        sig.attributes.append(iface_attr)
                current_interface.procedures.append(sig)
                current_proc = None
                continue

            _parse_declaration(s, current_proc, filename=filename, lineno=lineno, source_line=source_line)

        return interfaces

    def _parse_fortran_interface(self, code: _SourceOrLines, filename: str | None = None) -> FortranInterface:
        return _expect_single_parse_result(
            self._parse_fortran_interfaces(code, filename=filename),
            parser_name="parse_fortran_interface",
            entity_name="interface",
            filename=filename,
        )

    def _parse_fortran_submodules(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranSubmodule]:
        return _parse_fortran_submodules(code, filename=filename)

    def _parse_fortran_submodule(self, code: _SourceOrLines, filename: str | None = None) -> FortranSubmodule:
        return _expect_single_parse_result(
            self._parse_fortran_submodules(code, filename=filename),
            parser_name="parse_fortran_submodule",
            entity_name="submodule",
            filename=filename,
        )

    def _parse_fortran_programs(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:
        lines = _preprocessed_lines(code, filename)
        programs: list[FortranProgram] = []
        current: FortranProgram | None = None
        in_contains = False
        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()
            _enforce_source_form_compatibility(s, filename, lineno, source_line)
            pm = _PROGRAM_RE.match(s)
            if pm:
                current = FortranProgram(name=pm.group("name"), filename=filename)
                in_contains = False
                continue
            if l.startswith("end program"):
                if current is not None:
                    programs.append(current)
                current = None
                in_contains = False
                continue
            if current is None:
                continue
            if l.startswith("contains"):
                in_contains = True
                continue
            if in_contains:
                continue
            m = _USE_RE.match(s)
            if m:
                current.uses[m.group("module")] = split_csv(m.group("symbols")) if m.group("symbols") else []
                continue
            _parse_module_variable_line(s, current, filename, lineno=lineno, source_line=source_line)
        return programs

    def _parse_fortran_program(self, code: _SourceOrLines, filename: str | None = None) -> FortranProgram:
        return _expect_single_parse_result(
            self._parse_fortran_programs(code, filename=filename),
            parser_name="parse_fortran_program",
            entity_name="program",
            filename=filename,
        )

    def _parse_fortran_block_data(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:
        lines = _preprocessed_lines(code, filename)
        blocks: list[FortranBlockData] = []
        current: FortranBlockData | None = None
        for line, lineno, source_line in lines:
            s = line.strip()
            if not s:
                continue
            l = s.lower()
            _enforce_source_form_compatibility(s, filename, lineno, source_line)
            bm = _BLOCK_DATA_RE.match(s)
            if bm:
                current = FortranBlockData(name=bm.group("name"), filename=filename)
                continue
            if l.startswith("end block data") or (current is not None and l == "end"):
                blocks.append(current)
                current = None
                continue
            if current is None:
                continue
            _parse_module_variable_line(s, current, filename, lineno=lineno, source_line=source_line)
        return blocks

    def _parse_fortran_block_data_unit(self, code: _SourceOrLines, filename: str | None = None) -> FortranBlockData:
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
        return _parse_fortran_namespace(root, extensions=extensions)

    def _assess_wrap_readiness(self, code: str, filename: str | None = None) -> dict:
        return _assess_wrap_readiness(code, filename=filename)
    def __init__(self, macro_defines: set[str] | dict[str, int | bool | str] | None = None):
        self.macro_defines = macro_defines

    def parse_signatures(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    ) -> list[FortranProcedureSignature]:
        if macro_defines is None:
            macro_defines = self.macro_defines
        return self._parse_fortran_signatures(code, filename=filename, macro_defines=macro_defines)

    def parse_signature(
        self,
        code: _SourceOrLines,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
    ) -> FortranProcedureSignature:
        if macro_defines is None:
            macro_defines = self.macro_defines
        return self._parse_fortran_signature(code, filename=filename, macro_defines=macro_defines)

    def parse_project_signatures(self, files: dict[str, str]) -> list[FortranProcedureSignature]:
        return self._parse_fortran_project_signatures(files)

    def parse_file(
        self,
        source_or_path: str | Path,
        filename: str | None = None,
        macro_defines: set[str] | dict[str, int | bool | str] | None = None,
        encoding: str = "utf-8",
    ) -> FortranFile:
        return self._parse_fortran_file(
            source_or_path,
            filename=filename,
            macro_defines=macro_defines,
            encoding=encoding,
        )

    def parse_project(self, files, *, encoding: str = "utf-8") -> FortranProject:
        return self._parse_fortran_project(files, encoding=encoding)

    def parse_types(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranDerivedType]:
        return self._parse_fortran_types(code, filename=filename)

    def parse_derived_type(self, code: _SourceOrLines, filename: str | None = None) -> FortranDerivedType:
        return self._parse_fortran_derived_type(code, filename=filename)

    def parse_modules(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranModule]:
        return self._parse_fortran_modules(code, filename=filename)

    def parse_module(self, code: _SourceOrLines, filename: str | None = None) -> FortranModule:
        return self._parse_fortran_module(code, filename=filename)

    def parse_interfaces(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranInterface]:
        return self._parse_fortran_interfaces(code, filename=filename)

    def parse_interface(self, code: _SourceOrLines, filename: str | None = None) -> FortranInterface:
        return self._parse_fortran_interface(code, filename=filename)

    def parse_submodules(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranSubmodule]:
        return self._parse_fortran_submodules(code, filename=filename)

    def parse_submodule(self, code: _SourceOrLines, filename: str | None = None) -> FortranSubmodule:
        return self._parse_fortran_submodule(code, filename=filename)

    def parse_programs(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranProgram]:
        return self._parse_fortran_programs(code, filename=filename)

    def parse_program(self, code: _SourceOrLines, filename: str | None = None) -> FortranProgram:
        return self._parse_fortran_program(code, filename=filename)

    def parse_block_data(self, code: _SourceOrLines, filename: str | None = None) -> list[FortranBlockData]:
        return self._parse_fortran_block_data(code, filename=filename)

    def parse_block_data_unit(self, code: _SourceOrLines, filename: str | None = None) -> FortranBlockData:
        return self._parse_fortran_block_data_unit(code, filename=filename)

    def parse_namespace(
        self,
        root: str | Path,
        extensions: tuple[str, ...] = (".f", ".for", ".ftn", ".f77", ".f90", ".f95", ".f03", ".f08"),
    ) -> dict:
        return self._parse_fortran_namespace(root, extensions=extensions)

    def assess_wrap_readiness(self, code: str, filename: str | None = None) -> dict:
        return self._assess_wrap_readiness(code, filename=filename)

    # Backwards-compatible method spellings that mirror the historical function names.
    parse_fortran_signatures = parse_signatures
    parse_fortran_project_signatures = parse_project_signatures
    parse_fortran_signature = parse_signature
    parse_fortran_file = parse_file
    parse_fortran_project = parse_project
    parse_fortran_types = parse_types
    parse_fortran_derived_type = parse_derived_type
    parse_fortran_modules = parse_modules
    parse_fortran_module = parse_module
    parse_fortran_interfaces = parse_interfaces
    parse_fortran_interface = parse_interface
    parse_fortran_submodules = parse_submodules
    parse_fortran_submodule = parse_submodule
    parse_fortran_programs = parse_programs
    parse_fortran_program = parse_program
    parse_fortran_block_data = parse_block_data
    parse_fortran_block_data_unit = parse_block_data_unit
    parse_fortran_namespace = parse_namespace


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
