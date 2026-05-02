from __future__ import annotations

import argparse
import json
from dataclasses import fields, is_dataclass
from pathlib import Path

from .parser import assess_wrap_readiness, parse_fortran_modules, parse_fortran_signatures, parse_fortran_types


def _to_dict_no_parent(obj):
    if is_dataclass(obj):
        out = {}
        for f in fields(obj):
            if f.name == "parent":
                continue
            out[f.name] = _to_dict_no_parent(getattr(obj, f.name))
        return out
    if isinstance(obj, list):
        return [_to_dict_no_parent(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _to_dict_no_parent(v) for k, v in obj.items()}
    return obj


def _collect_extensions(path: Path) -> list[Path]:
    exts = {".f", ".for", ".ftn", ".f90", ".f95", ".f03", ".f08"}
    return sorted(p for p in path.rglob("*") if p.suffix.lower() in exts)


def _parse_paths(paths: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    expanded: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            expanded.extend(_collect_extensions(p))
        else:
            expanded.append(p)

    for p in sorted(set(expanded)):
        code = p.read_text(encoding="utf-8")
        out[str(p)] = {
            "signatures": [_to_dict_no_parent(s) for s in parse_fortran_signatures(code, filename=str(p))],
            "types": [_to_dict_no_parent(t) for t in parse_fortran_types(code, filename=str(p))],
            "modules": [_to_dict_no_parent(m) for m in parse_fortran_modules(code, filename=str(p))],
            "wrap_readiness": assess_wrap_readiness(code, filename=str(p)),
        }
    return out


def _format_report(report: dict[str, dict]) -> str:
    lines: list[str] = []
    for fname, parsed in report.items():
        lines.append(f"File: {fname}")
        lines.append(
            "  Summary: "
            f"procedures={len(parsed['signatures'])}, "
            f"types={len(parsed['types'])}, "
            f"modules={len(parsed['modules'])}"
        )
        lines.append("  Tree:")
        for mod in parsed["modules"]:
            lines.append(
                f"    ├─ module {mod['name']} (vars={len(mod['variables'])}, uses={len(mod['uses'])}, "
                f"procs={len(mod.get('procedures', []))}, types={len(mod.get('derived_types', []))}, "
                f"ifaces={len(mod.get('interfaces', []))})"
            )
            for v in mod["variables"]:
                lines.append(f"    │  ├─ var {v['name']}:{v['base_type']}[{v['rank']}]")
            for t in mod.get("derived_types", []):
                lines.append(f"    │  ├─ type {t['name']} (fields={len(t['fields'])}, methods={len(t['methods'])})")
            for s in mod.get("procedures", []):
                args = ", ".join(f"{a['name']}:{a['base_type']}[{a['rank']}]" for a in s["arguments"])
                lines.append(f"    │  └─ {s['kind']} {s['name']}({args})")
            for iface in mod.get("interfaces", []):
                iface_name = iface["name"] if iface.get("name") else "<anonymous>"
                lines.append(f"    │  ├─ interface {iface_name} (procs={len(iface.get('procedures', []))})")

        module_names = {m["name"].lower() for m in parsed["modules"]}
        orphan_types = [t for t in parsed["types"] if not t.get("module") or t["module"].lower() not in module_names]
        orphan_sigs = [s for s in parsed["signatures"] if not s.get("module") or s["module"].lower() not in module_names]
        for t in orphan_types:
            lines.append(f"    ├─ type {t['name']} (fields={len(t['fields'])}, methods={len(t['methods'])})")
        for s in orphan_sigs:
            args = ", ".join(f"{a['name']}:{a['base_type']}[{a['rank']}]" for a in s["arguments"])
            lines.append(f"    └─ {s['kind']} {s['name']}({args})")

        readiness = parsed["wrap_readiness"]
        lines.append(f"  Wrappable: {readiness['wrappable']}")
        if readiness["unsupported_constructs"]:
            lines.append("  Unsupported constructs:")
            for c in readiness["unsupported_constructs"]:
                lines.append(f"    - line {c['line']}: {c['text']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse Fortran files and print a human-readable report or JSON.")
    parser.add_argument("paths", nargs="+", help="Fortran file(s) or directory path(s)")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    parser.add_argument("--json-out", type=Path, help="Write JSON report to this file")
    args = parser.parse_args()

    report = _parse_paths(args.paths)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(_format_report(report))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
