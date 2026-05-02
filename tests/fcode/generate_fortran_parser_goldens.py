"""Generate/update golden files for Fortran parser fixtures."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from fortran_parser.parser import parse_fortran_signatures, parse_fortran_types

_TESTS_DIR = Path(__file__).parent


def _serialize_fixture(fixture: Path) -> dict | list:
    source = fixture.read_text(encoding="utf-8")
    signatures = [asdict(s) for s in parse_fortran_signatures(source, filename=fixture.name)]
    types = [asdict(t) for t in parse_fortran_types(source, filename=fixture.name)]
    if types:
        return {"signatures": signatures, "types": types}
    return signatures


def main() -> None:
    _TESTS_DIR.mkdir(parents=True, exist_ok=True)
    requested = sys.argv[1:]
    if requested:
        fixtures = []
        for item in requested:
            p = Path(item)
            if not p.is_absolute():
                p = _TESTS_DIR / p
            if p.suffix.lower() not in (".f", ".for", ".ftn", ".f90", ".f95", ".f03", ".f08"):
                p = p.with_suffix(".f90")
            fixtures.append(p)
    else:
        fixtures = sorted(_TESTS_DIR.glob("*.f*"))
    if not fixtures:
        raise SystemExit("No Fortran fixtures found")

    for fixture in fixtures:
        if not fixture.exists():
            raise SystemExit(f"Fixture does not exist: {fixture}")
        payload = _serialize_fixture(fixture)
        out = _TESTS_DIR / f"{fixture.stem}.json"
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"updated {out}")


if __name__ == "__main__":
    main()
