from pathlib import Path

import pytest

from x2py.semantics.fortran2ir import fortran_module_to_semantic_module
from x2py.codegen.printers.pyi_printer import emit_module

from _fixture_conversion_utils import FORTRAN_FIXTURES, TESTS_DIR, parse_fixture


def test_pyi_printer_fixture_suite_has_fixtures():
    assert FORTRAN_FIXTURES, "No Fortran fixtures found in tests/data/fortran/general"


@pytest.mark.parametrize(
    "fixture",
    FORTRAN_FIXTURES,
    ids=lambda p: str(p.relative_to(TESTS_DIR)),
)
def test_pyi_printer_conversion_smoke(fixture: Path):
    parsed = parse_fixture(fixture)

    for module in parsed.modules:
        semantic_module = fortran_module_to_semantic_module(module)
        emit_module(semantic_module)
