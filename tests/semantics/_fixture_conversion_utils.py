from pathlib import Path

from fortran_parser import parse_fortran_file


TESTS_DIR = Path(__file__).resolve().parents[1] / "parser" / "fcode"
FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".f03", ".f08"}


def iter_fortran_fixtures():
    for path in TESTS_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in FORTRAN_SUFFIXES:
            continue

        relpath = path.relative_to(TESTS_DIR).as_posix()
        if relpath.startswith("errors/") or relpath.startswith("SciFortran/errors/"):
            continue

        if not path.with_suffix(".json").exists():
            continue

        yield path


FORTRAN_FIXTURES = sorted(iter_fortran_fixtures())


def parse_fixture(path: Path):
    source = path.read_text(encoding="utf-8")
    relpath = str(path.relative_to(TESTS_DIR))
    return parse_fortran_file(source, filename=relpath)
