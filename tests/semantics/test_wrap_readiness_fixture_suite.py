import json

from tests._shared.fixture_outputs import (
    SEMANTIC_READINESS_FIXTURE_PATH,
    iter_wrap_readiness_fortran_fixtures,
    readiness_fixture_key,
    wrap_readiness_message_payload_for_corpus,
)


def test_wrap_readiness_fixture_suite_has_corpus_files():
    files = iter_wrap_readiness_fortran_fixtures()
    assert files, "No Fortran corpus files found for semantic readiness fixtures"
    keys = {readiness_fixture_key(path) for path in files}
    assert any(key.startswith("blas/") for key in keys)
    assert any(key.startswith("lapack/") for key in keys)
    assert any(key.startswith("scifortran/") for key in keys)


def test_wrap_readiness_fixture_matches_fortran_corpus():
    expected = json.loads(SEMANTIC_READINESS_FIXTURE_PATH.read_text(encoding="utf-8"))
    assert wrap_readiness_message_payload_for_corpus() == expected
