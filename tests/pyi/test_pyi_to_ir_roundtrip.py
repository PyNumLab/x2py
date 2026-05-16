from pathlib import Path

from semantics.fortran2ir import fortran_file_to_semantic_modules
from semantics.pyi_parser import load_pyi_file, parse_pyi_text
from semantics.pyi_printer import emit_module
from tests._shared.fixture_outputs import FORTRAN_DATA_DIR, FORTRAN_SUFFIXES
from x2py import parse_fortran_file


ROUNDTRIP_DIRS = ("general", "blas", "lapack", "scifortran")
FORTRAN_ROUNDTRIP_FIXTURES = sorted(
    path
    for dirname in ROUNDTRIP_DIRS
    for path in (FORTRAN_DATA_DIR / dirname).rglob("*")
    if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
)


def _semantic_modules_for_source(path: Path):
    parsed = parse_fortran_file(
        path.read_text(encoding="utf-8"),
        filename=str(path.relative_to(FORTRAN_DATA_DIR)),
    )
    return fortran_file_to_semantic_modules(parsed, standalone_module_name=path.stem)


def test_parse_pyi_text_allows_user_modified_stub():
    pyi = """
import iso_c_binding

class particle:
    id: Int32

scale: private[Float64]

def touch(
    p: particle
) -> Returns["p", particle]: ...
"""

    module = parse_pyi_text(pyi, module_name="edited")

    assert module.name == "edited"
    assert module.imports == ["iso_c_binding"]
    assert module.classes[0].name == "particle"
    assert module.variables[0].name == "scale"
    assert module.variables[0].visibility == "private"
    assert module.functions[0].arguments[0].intent == "inout"


def test_parse_pyi_text_accepts_plain_return_type():
    pyi = """
def make_value(
    x: Float64
) -> Float64: ...
"""

    module = parse_pyi_text(pyi, module_name="edited")

    func = module.functions[0]
    assert func.return_type is not None
    assert func.return_type.name == "Float64"
    assert func.arguments[0].intent == "in"


def test_generated_pyi_roundtrips_to_original_ir_for_all_fortran_fixtures(tmp_path: Path):
    assert FORTRAN_ROUNDTRIP_FIXTURES

    checked_modules = 0
    for fixture in FORTRAN_ROUNDTRIP_FIXTURES:
        for module in _semantic_modules_for_source(fixture):
            pyi_path = tmp_path / f"{module.name}.pyi"
            pyi_path.write_text(emit_module(module, roundtrip=True) + "\n", encoding="utf-8")

            try:
                assert load_pyi_file(pyi_path) == module
            finally:
                pyi_path.unlink(missing_ok=True)

            checked_modules += 1

    assert checked_modules > 0
    assert not list(tmp_path.glob("*.pyi"))
