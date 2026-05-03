from __future__ import annotations

import re
import ast
from pathlib import Path
from dataclasses import replace

from .lexer import preprocess_lines
from .models import FortranArgument, FortranDerivedType, FortranInterface, FortranModule, FortranProcedureSignature, FortranVariable
from .type_resolver import extract_kind_from_type_spec
from .utils import split_csv

_TYPE_RE = re.compile(r"^(integer|real|complex|logical|character|double\s+precision)\s*(\([^)]*\))?\s*(.*)$", re.IGNORECASE)
_CHAR_STAR_RE = re.compile(r"^character\s*\*\s*(?P<len>\([^)]*\)|\*|[A-Za-z_]\w*|\d+)\s*(?P<rest>.*)$", re.IGNORECASE)
_PROC_RE = re.compile(r"^(?P<prefix>(?:\w+\s+)*)subroutine\s+(?P<name>\w+)\s*\((?P<args>[^)]*)\)\s*(?P<tail>.*)$", re.IGNORECASE)
_FUNC_RE = re.compile(r"^(?P<prefix>(?:\w+\s+)*)function\s+(?P<name>\w+)\s*\((?P<args>[^)]*)\)\s*(?P<tail>.*)$", re.IGNORECASE)
_RESULT_RE = re.compile(r"results?\s*\(\s*(?P<name>\w+)\s*\)", re.IGNORECASE)
_ATTR_PREFIX_WORDS = {"pure", "elemental", "recursive"}

_BINDC_RE = re.compile(r"bind\s*\(\s*c\s*(?:,\s*name\s*=\s*['\"][^'\"]*['\"])?\s*\)", re.IGNORECASE)
_USE_RE = re.compile(r"^use\s+(?P<module>\w+)\s*(?:,\s*only\s*:\s*(?P<symbols>.*))?$", re.IGNORECASE)
_PARAM_RE = re.compile(
    r"^(integer|real|logical|character|complex)\s*(?:\([^)]*\))?\s*,\s*parameter\s*::\s*(?P<body>.*)$",
    re.IGNORECASE,
)
_LEGACY_PARAM_STMT_RE = re.compile(r"^parameter\s*\(\s*(?P<body>.*)\s*\)$", re.IGNORECASE)
_DERIVED_TYPE_RE = re.compile(r"^type\s*(?P<attrs>(?:,\s*[^:]+)?)::\s*(?P<name>\w+)$", re.IGNORECASE)
_TYPE_FIELD_RE = re.compile(r"^type\s*\(\s*(?P<dtype>\w+)\s*\)\s*(?P<attrs>.*)$", re.IGNORECASE)
_PROC_BIND_RE = re.compile(r"^procedure\s*(?:,\s*[^:]*)?::\s*(?P<names>.*)$", re.IGNORECASE)
_UNSUPPORTED_PATTERNS = (
    re.compile(r"\bclass\s*\(", re.IGNORECASE),
    re.compile(r"\bselect\s+type\b", re.IGNORECASE),
    re.compile(r"\bcoarray\b|\[[^\]]*\]", re.IGNORECASE),
    re.compile(r"\bprocedure\s*,\s*pointer\b", re.IGNORECASE),
    re.compile(r"\btype\s*\(\s*c_ptr\s*\)", re.IGNORECASE),
)


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
    return None


def _enforce_source_form_compatibility(line: str, filename: str | None) -> None:
    # Keep strict legacy checks only for files explicitly marked as .f77.
    # Many .f sources in real-world projects (e.g. LAPACK) are fixed-form but
    # still use modern declaration attributes.
    if not filename or Path(filename).suffix.lower() != ".f77":
        return
    forbidden = (
        r"\bmodule\b",
        r"\bcontains\b",
        r"\binterface\b",
        # Some codebases (e.g. LAPACK) keep modern attribute declarations
        # in fixed-form .f sources. Permit declaration-level modern syntax,
        # but keep rejecting larger unsupported structural features.
        r"\bclass\s*\(",
    )
    for pat in forbidden:
        if re.search(pat, line, re.IGNORECASE):
            raise ValueError(f"Unsupported syntax for Fortran 77 source '{filename}': {line.strip()}")


def parse_fortran_signatures(code: str, filename: str | None = None) -> list[FortranProcedureSignature]:
    lines = preprocess_lines(code, filename)
    signatures: list[FortranProcedureSignature] = []
    declared_procedures: dict[tuple[str | None, bool], set[str]] = {}
    current_module = None
    current_module_uses: dict[str, list[str]] = {}
    current_proc = None
    interface_depth = 0

    for line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()

        _enforce_source_form_compatibility(s, filename)

        if l.startswith("interface"):
            interface_depth += 1
            continue
        if l.startswith("end interface"):
            interface_depth = max(0, interface_depth - 1)
            continue

        if l.startswith("module ") and not l.startswith("module procedure"):
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
                seen_in_scope = declared_procedures.setdefault(scope_key, set())
                proc_name = current_proc["signature"].name.lower()
                if proc_name in seen_in_scope:
                    scope_label = (
                        f"module '{current_module}'" if current_module is not None else "global scope"
                    )
                    raise ValueError(
                        f"Duplicate procedure name '{current_proc['signature'].name}' in {scope_label}."
                    )
                seen_in_scope.add(proc_name)
                current_proc["uses"].update(current_module_uses)
                current_proc["filename"] = filename
                current_proc["in_exec_part"] = False
            continue

        if l.startswith("end subroutine") or l.startswith("end function") or l == "end":
            signatures.append(_finalize_proc(current_proc))
            current_proc = None
            continue
        if l == "contains":
            current_proc["in_contains"] = True
            continue
        if current_proc.get("in_contains"):
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

        _parse_declaration(s, current_proc)

    if current_proc is not None:
        signatures.append(_finalize_proc(current_proc))
    return signatures


def parse_fortran_project_signatures(files: dict[str, str]) -> list[FortranProcedureSignature]:
    module_params: dict[str, dict[str, str]] = {}
    parsed_files: list[tuple[str, list[FortranProcedureSignature]]] = []
    for fname, code in files.items():
        module_params.update(_collect_module_parameters(code, fname))
        parsed_files.append((fname, parse_fortran_signatures(code, filename=fname)))

    for _, signatures in parsed_files:
        for sig in signatures:
            _resolve_signature_kinds(sig, module_params)

    out: list[FortranProcedureSignature] = []
    for _, signatures in parsed_files:
        out.extend(signatures)
    return out


def parse_fortran_file(path: str) -> list[FortranProcedureSignature]:
    with open(path, "r", encoding="utf-8") as f:
        return parse_fortran_signatures(f.read(), filename=path)


def parse_fortran_types(code: str, filename: str | None = None) -> list[FortranDerivedType]:
    lines = preprocess_lines(code, filename)
    current_module = None
    current_type: FortranDerivedType | None = None
    in_type_contains = False
    types: list[FortranDerivedType] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename)
        if l.startswith("module ") and not l.startswith("module procedure"):
            current_module = s.split()[1]
            continue
        if l.startswith("end module"):
            current_module = None
            continue
        if current_type is None:
            tm = _DERIVED_TYPE_RE.match(s)
            if tm:
                attr_txt = (tm.group("attrs") or "").strip().lstrip(",").strip()
                attrs = [a.strip() for a in split_csv(attr_txt)] if attr_txt else []
                extends = None
                normalized_attrs: list[str] = []
                for a in attrs:
                    la = a.lower()
                    if la.startswith("extends(") and la.endswith(")"):
                        extends = a[a.find("(") + 1 : -1].strip()
                    else:
                        normalized_attrs.append(la)
                current_type = FortranDerivedType(
                    name=tm.group("name"),
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
        _parse_type_field_line(s, current_type, filename)
    # Resolve extends references for parent types declared in the same parsed file.
    # Keep cross-file parents as strings.
    by_name = {t.name.lower(): t for t in types}
    for t in types:
        if isinstance(t.extends, str):
            parent = by_name.get(t.extends.lower())
            if parent is not None:
                t.extends = parent
    return types


def parse_fortran_modules(code: str, filename: str | None = None) -> list[FortranModule]:
    lines = preprocess_lines(code, filename)
    modules: list[FortranModule] = []
    current: FortranModule | None = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename)
        if l.startswith("module ") and not l.startswith("module procedure"):
            current = FortranModule(name=s.split()[1], filename=filename)
            continue
        if l.startswith("end module"):
            if current:
                modules.append(current)
            current = None
            continue
        if current is None:
            continue
        if l.startswith("contains"):
            continue
        m = _USE_RE.match(s)
        if m:
            current.uses[m.group("module")] = split_csv(m.group("symbols")) if m.group("symbols") else []
            continue
        _parse_module_variable_line(s, current, filename)

    # Attach parsed procedures/types/interfaces to their owning modules.
    signatures = parse_fortran_signatures(code, filename)
    types = parse_fortran_types(code, filename)
    interfaces = parse_fortran_interfaces(code, filename)
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
    return modules


def parse_fortran_interfaces(code: str, filename: str | None = None) -> list[FortranInterface]:
    lines = preprocess_lines(code, filename)
    current_module = None
    current_interface: FortranInterface | None = None
    current_proc = None
    interfaces: list[FortranInterface] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename)
        if l.startswith("module ") and not l.startswith("module procedure"):
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
            continue

        if l.startswith("end subroutine") or l.startswith("end function") or l == "end":
            sig = _finalize_proc(current_proc)
            current_interface.procedures.append(sig)
            current_proc = None
            continue

        _parse_declaration(s, current_proc)

    return interfaces


def assess_wrap_readiness(code: str, filename: str | None = None) -> dict:
    lines = preprocess_lines(code, filename)
    signatures = parse_fortran_signatures(code, filename)
    types = parse_fortran_types(code, filename)
    modules = parse_fortran_modules(code, filename)
    unsupported: list[dict] = []
    for lineno, line in enumerate(lines, start=1):
        for p in _UNSUPPORTED_PATTERNS:
            if p.search(line):
                unsupported.append({"line": lineno, "text": line.strip(), "pattern": p.pattern})
                break

    missing_decl_args: list[str] = []
    for sig in signatures:
        for a in sig.arguments:
            if a.base_type == "unknown":
                missing_decl_args.append(f"{sig.name}:{a.name}")

    return {
        "n_signatures": len(signatures),
        "n_types": len(types),
        "n_modules": len(modules),
        "unsupported_constructs": unsupported,
        "unknown_argument_types": missing_decl_args,
        "wrappable": len(unsupported) == 0 and len(missing_decl_args) == 0 and len(signatures) > 0,
    }


def parse_fortran_namespace(root: str | Path, extensions: tuple[str, ...] = (".f", ".for", ".ftn", ".f90", ".f95", ".f03", ".f08")) -> dict:
    root_path = Path(root)
    files = sorted([p for p in root_path.rglob("*") if p.suffix.lower() in extensions])
    sources = {str(p): p.read_text(encoding="utf-8") for p in files}

    module_to_file: dict[str, str] = {}
    file_to_uses: dict[str, set[str]] = {}
    modules_by_file: dict[str, list[str]] = {}
    for fname, code in sources.items():
        modules = parse_fortran_modules(code, filename=fname)
        modules_by_file[fname] = [m.name for m in modules]
        for m in modules:
            module_to_file[m.name.lower()] = fname
            uses = file_to_uses.setdefault(fname, set())
            uses.update(u.lower() for u in m.uses)

    file_dependencies: dict[str, set[str]] = {}
    for fname, used_modules in file_to_uses.items():
        deps = set()
        for mod in used_modules:
            dep_file = module_to_file.get(mod)
            if dep_file and dep_file != fname:
                deps.add(dep_file)
        file_dependencies[fname] = deps

    ordered_files = _topological_files(file_dependencies)
    signatures = parse_fortran_project_signatures({f: sources[f] for f in ordered_files})
    types = []
    modules = []
    for f in ordered_files:
        code = sources[f]
        types.extend(parse_fortran_types(code, filename=f))
        modules.extend(parse_fortran_modules(code, filename=f))

    return {
        "files": ordered_files,
        "file_dependencies": {k: sorted(v) for k, v in file_dependencies.items()},
        "module_to_file": module_to_file,
        "modules": modules,
        "types": types,
        "signatures": signatures,
    }


def collect_signature_shape_symbols(sig: FortranProcedureSignature) -> set[str]:
    symbols: set[str] = set()
    for arg in sig.arguments:
        for dim in arg.shape:
            symbols.update(re.findall(r"\b[a-zA-Z_]\w*\b", dim))
    return {s.lower() for s in symbols}


def evaluate_signature_shapes(
    sig: FortranProcedureSignature,
    symbol_values: dict[str, int | str],
) -> FortranProcedureSignature:
    normalized = {k.lower(): str(v) for k, v in symbol_values.items()}
    out = replace(sig)
    out.arguments = [replace(a) for a in sig.arguments]
    for arg in out.arguments:
        if arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, normalized) for dim in arg.shape]
    return out


def _parse_header(line: str, module: str | None, in_interface: bool):
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
            "filename": None,
        }
    m = _FUNC_RE.match(line)
    if not m:
        return None
    args = [FortranArgument(name=a, procedure=m.group("name")) for a in split_csv(m.group("args"))]
    result_match = _RESULT_RE.search(m.group("tail"))
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
        "uses": {},
        "in_contains": False,
        "local_params": {},
        "legacy_local_params": set(),
        "implicit_typed_symbols": {},
        "declared_local_types": {},
        "implicit_none": False,
        "filename": None,
    }


def _attrs(prefix: str, tail: str) -> list[str]:
    attrs = [t.lower() for t in prefix.split() if t.lower() in ("pure", "elemental", "recursive")]
    if _BINDC_RE.search(tail):
        attrs.append("bind(c)")
    return attrs


def _parse_declaration(line: str, proc_state: dict) -> None:
    stripped = line.strip()
    if re.match(r"^implicit\b", stripped, flags=re.IGNORECASE):
        # IMPLICIT statements configure typing rules and are not variable declarations.
        if re.match(r"^implicit\s+none\b", stripped, flags=re.IGNORECASE):
            proc_state["implicit_none"] = True
        return

    if re.match(r"^external\b", stripped, flags=re.IGNORECASE):
        # EXTERNAL declares procedure names (not data objects); keep parsing without treating as datatype declarations.
        return
    if re.match(r"^intrinsic\b", stripped, flags=re.IGNORECASE):
        # INTRINSIC lists intrinsic procedures that may appear as bare statements in legacy fixed-form code.
        return
    if re.match(r"^data\b", stripped, flags=re.IGNORECASE):
        # DATA initializes variables in legacy fixed-form code.
        return
    if re.match(r"^equivalence\b", stripped, flags=re.IGNORECASE):
        # EQUIVALENCE overlays storage in legacy code; it is not a datatype declaration.
        return
    if re.match(r"^format\s*\(", stripped, flags=re.IGNORECASE):
        # FORMAT labels are executable I/O formatting statements, not declarations.
        return
    if re.match(r"^go\s*to\b", stripped, flags=re.IGNORECASE):
        # GO TO is an executable statement.
        return
    if re.match(r"^use\b", stripped, flags=re.IGNORECASE):
        # USE statements can appear in free-form and preprocessed fixed-form sources.
        return

    pm = _PARAM_RE.match(stripped)
    if pm:
        for assign in split_csv(pm.group("body")):
            if "=" not in assign:
                continue
            k, v = [x.strip() for x in assign.split("=", 1)]
            if k.lower() in proc_state["local_params"]:
                raise ValueError(
                    f"Duplicate PARAMETER declaration of symbol '{k}' in procedure '{proc_state['signature'].name}'."
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
                raise ValueError(
                    f"Unknown datatype for PARAMETER symbol '{k}' in procedure '{proc_state['signature'].name}'."
                )
            if k.lower() not in proc_state["typed_symbols"]:
                # In legacy fixed-form code with implicit typing, keep compatibility
                # with implicit typing rules: infer type from symbol name.
                proc_state["local_params"][k.lower()] = v
                proc_state["implicit_typed_symbols"][k.lower()] = _infer_implicit_base_type(k)
                continue
            if k.lower() in proc_state["local_params"]:
                raise ValueError(
                    f"Duplicate PARAMETER declaration of symbol '{k}' in procedure '{proc_state['signature'].name}'."
                )
            proc_state["local_params"][k.lower()] = v
            proc_state["legacy_local_params"].add(k.lower())
        return
    if "::" in line:
        left, right = [x.strip() for x in line.split("::", 1)]
    else:
        # Fortran 77 fixed-form declarations commonly omit "::"
        # (e.g., "INTEGER N", "COMPLEX CX(*), CY(*)").
        left = line.strip()
        right = ""
    star_kind = _find_legacy_star_kind(left)
    source_form = _source_form(proc_state.get("filename"))
    if star_kind and source_form == "modern":
        base, kind = star_kind
        raise ValueError(f"Unsupported Fortran 77 star-kind declaration '{base}*{kind}' in modern source '{proc_state.get('filename')}'.")

    char_star = _CHAR_STAR_RE.match(left)
    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
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
            # Legacy Fortran alias for double-precision real.
            base = "real"
        type_spec = (tm.group(2) or "").strip()
        trailing = tm.group(3).strip().lstrip(", ")
        kind = extract_kind_from_type_spec(base, type_spec)
        if "::" in line:
            attrs = split_csv(trailing)
        else:
            attrs = []
            right = trailing
    elif derived:
        base = "derived"
        kind = derived.group("dtype")
        attrs = split_csv((derived.group("attrs") or "").strip().lstrip(", "))
    else:
        m_first = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)", line.strip())
        first_word = m_first.group(1).lower() if m_first else ""
        non_decl_starts = {"do", "if", "where", "call", "select", "case", "allocate", "deallocate", "print", "write", "read", "return", "stop", "cycle", "exit", "continue", "end", "else", "elseif", "contains", "goto", "go", "data", "format", "use"}
        if "=" in line and "::" not in line:
            # Assignment statement, not a declaration.
            return
        looks_like_decl = bool(re.match(r"^[A-Za-z]", line.strip())) and first_word not in non_decl_starts and ("::" in line or "," in line or " " in line.strip())
        if looks_like_decl:
            if any(p.search(line) for p in _UNSUPPORTED_PATTERNS):
                return
            raise ValueError(f"Unknown or unsupported datatype declaration for procedure '{proc_state['signature'].name}': {line.strip()}")
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
            raise ValueError(
                f"Duplicate declaration of symbol '{normalized_name}' in procedure '{proc_state['signature'].name}'."
            )
        declared.add(lowered_name)
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


def _finalize_proc(state: dict) -> FortranProcedureSignature:
    sig = state["signature"]
    symbols = state["symbols"]
    local_params = state.get("local_params", {})
    legacy_local_params = state.get("legacy_local_params", set())
    implicit_typed_symbols = state.get("implicit_typed_symbols", {})
    sig.variables = {}
    sig.arguments = [symbols.get(a.name.lower(), a) for a in sig.arguments]
    if sig.result:
        sig.result = symbols.get(sig.result.name.lower(), sig.result)
    # Safety check: if an argument has been explicitly declared in this
    # procedure, it must not remain unknown after declaration parsing.
    # This catches declaration-application regressions (e.g. legacy
    # star-kind list handling) while still allowing truly undeclared
    # arguments to be reported via readiness diagnostics.
    declared_symbols = state.get("typed_symbols", set())
    for arg in sig.arguments:
        if arg.name.lower() in declared_symbols and arg.base_type == "unknown":
            raise ValueError(
                f"Failed to resolve declared argument '{arg.name}' in procedure '{sig.name}'."
            )
    for arg in sig.arguments:
        if arg.kind:
            arg.kind = _resolve_symbol_reference(arg.kind, local_params)
        if arg.shape:
            arg.shape = [_resolve_compile_time_expression(dim, local_params) for dim in arg.shape]
    if sig.result and sig.result.kind:
        sig.result.kind = _resolve_symbol_reference(sig.result.kind, local_params)
    relevant_params = _collect_relevant_local_params(sig, local_params)
    declared_local_types = state.get("declared_local_types", {})
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
        if not state.get("implicit_none", False):
            sig.result.base_type = _infer_implicit_base_type(sig.result.name)
        if sig.result.base_type == "unknown":
            raise ValueError(f"Unknown datatype for function result '{sig.result.name}' in procedure '{sig.name}'.")
    sig.uses = dict(state["uses"])
    return replace(sig)


def _collect_module_parameters(code: str, filename: str | None) -> dict[str, dict[str, str]]:
    lines = preprocess_lines(code, filename)
    current_module = None
    in_module_spec_part = False
    output: dict[str, dict[str, str]] = {}
    in_module_spec_part = False
    for line in lines:
        s = line.strip()
        if not s:
            continue
        l = s.lower()
        _enforce_source_form_compatibility(s, filename)
        if l.startswith("module ") and not l.startswith("module procedure"):
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


def _parse_type_field_line(line: str, dtype: FortranDerivedType, filename: str | None) -> None:
    if "::" not in line:
        return
    if re.match(r"^type\s*::\s*\w+$", line.strip(), re.IGNORECASE):
        return
    left, right = [x.strip() for x in line.split("::", 1)]
    star_kind = _find_legacy_star_kind(left)
    source_form = _source_form(filename)
    if star_kind and source_form == "modern":
        base, kind = star_kind
        raise ValueError(f"Unsupported Fortran 77 star-kind declaration '{base}*{kind}' in modern source '{filename}'.")

    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
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
    elif derived:
        attrs = split_csv((derived.group("attrs") or "").strip().lstrip(", "))
        meta = {
            "base_type": "derived",
            "kind": derived.group("dtype"),
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    else:
        raise ValueError(f"Unknown or unsupported datatype declaration: {line.strip()}")

    for a in attrs:
        la = a.lower()
        if la == "allocatable":
            meta["allocatable"] = True
        elif la == "pointer":
            meta["pointer"] = True
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


def _parse_module_variable_line(line: str, module: FortranModule, filename: str | None) -> None:
    if "::" not in line:
        return
    if re.match(r"^type\s*::\s*\w+$", line.strip(), re.IGNORECASE):
        return
    left, right = [x.strip() for x in line.split("::", 1)]
    star_kind = _find_legacy_star_kind(left)
    source_form = _source_form(filename)
    if star_kind and source_form == "modern":
        base, kind = star_kind
        raise ValueError(f"Unsupported Fortran 77 star-kind declaration '{base}*{kind}' in modern source '{filename}'.")

    tm = _TYPE_RE.match(left)
    derived = _TYPE_FIELD_RE.match(left)
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
    elif derived:
        attrs = split_csv((derived.group("attrs") or "").strip().lstrip(", "))
        meta = {
            "base_type": "derived",
            "kind": derived.group("dtype"),
            "rank": 0,
            "shape": [],
            "intent": "unknown",
            "optional": False,
            "value": False,
            "allocatable": False,
            "pointer": False,
        }
    else:
        raise ValueError(f"Unknown or unsupported datatype declaration: {line.strip()}")

    for a in attrs:
        la = a.lower()
        if la == "allocatable":
            meta["allocatable"] = True
        elif la == "pointer":
            meta["pointer"] = True
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
