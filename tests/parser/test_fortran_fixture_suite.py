import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path

import pytest

from x2py import parse_fortran_file


def parse_fortran_modules(source, filename=None):
    return parse_fortran_file(source, filename=filename).modules


_TESTS_DIR = Path(__file__).resolve().parents[1] / "data" / "fortran"
_FIXTURES_DIR = Path(__file__).parent / "fortran" / "fixtures"
_SOURCE_SUFFIXES = {".f", ".f90", ".f95", ".f03", ".f08", ".for", ".f77", ".ftn"}
_UPDATE_GOLDENS = os.getenv("FORTRAN_PARSER_UPDATE_GOLDENS", "0") == "1"


def _requires_compiler_preprocessing(fixture: Path) -> bool:
    return any(line.lstrip().startswith("#") for line in fixture.read_text(encoding="utf-8").splitlines())


def _has_direct_expected_json(fixture: Path) -> bool:
    return (_FIXTURES_DIR / fixture.relative_to(_TESTS_DIR)).with_suffix(".json").exists()


def _source_json_relpaths(root: Path) -> set[Path]:
    return {
        path.relative_to(root).with_suffix(".json")
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in _SOURCE_SUFFIXES
    }


def _fixture_json_relpaths(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.rglob("*.json") if path.is_file()}


_GOLDEN_FIXTURES = sorted(
    f
    for f in (_TESTS_DIR / "general").glob("*")
    if f.is_file() and f.suffix.lower() in _SOURCE_SUFFIXES and (_UPDATE_GOLDENS or _has_direct_expected_json(f))
)
_BLAS_FIXTURES = sorted(
    f for f in (_TESTS_DIR / "blas").rglob("*") if f.is_file() and f.suffix.lower() in _SOURCE_SUFFIXES
)
_LAPACK_FIXTURES = sorted(
    f for f in (_TESTS_DIR / "lapack").rglob("*") if f.is_file() and f.suffix.lower() in _SOURCE_SUFFIXES
)
_SCIFORTRAN_FIXTURES = sorted(
    f
    for f in (_TESTS_DIR / "scifortran").glob("*")
    if f.is_file() and f.suffix.lower() in _SOURCE_SUFFIXES and _has_direct_expected_json(f)
)
_CPP_FIXTURES = [
    fixture for fixture in [*_LAPACK_FIXTURES, *_SCIFORTRAN_FIXTURES] if _requires_compiler_preprocessing(fixture)
]
_DIRECT_LAPACK_FIXTURES = [fixture for fixture in _LAPACK_FIXTURES if not _requires_compiler_preprocessing(fixture)]
_DIRECT_SCIFORTRAN_FIXTURES = [
    fixture for fixture in _SCIFORTRAN_FIXTURES if not _requires_compiler_preprocessing(fixture)
]


def _expected_json_for_fixture(fixture: Path) -> Path:
    rel = fixture.relative_to(_TESTS_DIR)
    direct = (_FIXTURES_DIR / rel).with_suffix(".json")
    if direct.exists():
        return direct
    return _FIXTURES_DIR / "general" / (fixture.stem + ".json")


def _parser_filename_for_fixture(fixture: Path) -> str:
    relpath = str(fixture.relative_to(_TESTS_DIR))
    if relpath.startswith("scifortran/"):
        direct = (_FIXTURES_DIR / Path(relpath)).with_suffix(".json")
        if direct.exists():
            return relpath.replace("scifortran/", "SciFortran/", 1)
        return fixture.name
    return relpath if "/" in relpath else fixture.name


def _load_expected(expected_path: Path):
    with expected_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _strip_parent_fields(value):
    if isinstance(value, dict):
        return {k: _strip_parent_fields(v) for k, v in value.items() if k != "parent"}
    if isinstance(value, list):
        return [_strip_parent_fields(v) for v in value]
    return value


def _to_dict(value):
    return _strip_parent_fields(asdict(value))


def _dump_expected(path: Path, parsed: dict) -> None:
    payload = parsed
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _run_fixture_comparison(fixture: Path, *, filename_for_parser: str, expected_path: Path) -> None:
    source = fixture.read_text(encoding="utf-8")
    assert source.strip(), f"Fixture is empty: {filename_for_parser}"

    parsed = _to_dict(parse_fortran_file(source, filename=filename_for_parser))

    if _UPDATE_GOLDENS:
        _dump_expected(expected_path, parsed)
        return

    expected = _load_expected(expected_path)
    assert parsed == expected, f"FortranFile mismatch for {fixture.name}"


def test_fortran_fixture_golden_suite_has_fixtures():
    assert _GOLDEN_FIXTURES, "No fixtures found in tests/data/fortran"


@pytest.mark.parametrize(
    ("data_subdir", "fixture_subdir"),
    [
        ("general", "general"),
        ("blas", "blas"),
        ("lapack", "lapack"),
        ("scifortran", "scifortran"),
        ("errors/parser", "errors"),
    ],
)
def test_fortran_parser_fixtures_match_data_files_one_to_one(data_subdir, fixture_subdir):
    data_root = _TESTS_DIR / data_subdir
    fixture_root = _FIXTURES_DIR / fixture_subdir

    expected = _source_json_relpaths(data_root)
    actual = _fixture_json_relpaths(fixture_root)

    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    if not _UPDATE_GOLDENS:
        assert not missing, f"Missing parser JSON fixtures for {data_subdir}: {missing[:20]}"
    assert not extra, f"Parser JSON fixtures without matching data files in {fixture_subdir}: {extra[:20]}"


@pytest.mark.parametrize("fixture", _GOLDEN_FIXTURES, ids=lambda f: f.name)
def test_fortran_fixture_golden_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=fixture.name,
        expected_path=_expected_json_for_fixture(fixture),
    )


def test_fortran_blas_parse_suite_has_fixtures():
    assert _BLAS_FIXTURES, "No BLAS fixtures found in tests/data/fortran/blas"


@pytest.mark.parametrize("fixture", _BLAS_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_blas_parse_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=_parser_filename_for_fixture(fixture),
        expected_path=_expected_json_for_fixture(fixture),
    )


def test_fortran_lapack_parse_suite_has_fixtures():
    assert _LAPACK_FIXTURES, "No LAPACK fixtures found in tests/data/fortran/lapack"


@pytest.mark.parametrize("fixture", _DIRECT_LAPACK_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_lapack_parse_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=_parser_filename_for_fixture(fixture),
        expected_path=_expected_json_for_fixture(fixture),
    )


def test_fortran_scifortran_parse_suite_has_fixtures():
    assert _SCIFORTRAN_FIXTURES, "No scifortran fixtures found in tests/data/fortran/scifortran"


@pytest.mark.parametrize("fixture", _DIRECT_SCIFORTRAN_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_scifortran_parse_suite(fixture):
    _run_fixture_comparison(
        fixture,
        filename_for_parser=_parser_filename_for_fixture(fixture),
        expected_path=_expected_json_for_fixture(fixture),
    )


@pytest.mark.parametrize("fixture", _CPP_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_cpp_corpus_fixtures_require_compiler_preprocessing(fixture):
    from x2py import FortranParseError

    with pytest.raises(FortranParseError, match="require compiler preprocessing") as exc_info:
        parse_fortran_file(
            fixture.read_text(encoding="utf-8"),
            filename=_parser_filename_for_fixture(fixture),
        )

    assert exc_info.value.code == "PARSE_PREPROCESSING_REQUIRED"


@pytest.mark.parametrize("fixture", _CPP_FIXTURES, ids=lambda f: str(f.relative_to(_TESTS_DIR)))
def test_fortran_cpp_corpus_fixtures_parse_after_compiler_preprocessing(fixture, tmp_path):
    from x2py.preprocessing import PreprocessingConfig, preprocess_source

    compiler = shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is not available")
    (tmp_path / "arpackdef.h").write_text("", encoding="utf-8")
    (tmp_path / "error_msg_arpack.h90").write_text("", encoding="utf-8")
    (tmp_path / "info_msg_arpack.h90").write_text("", encoding="utf-8")
    preprocessed = preprocess_source(
        fixture,
        language="fortran",
        config=PreprocessingConfig(
            mode="compiler",
            compiler=compiler,
            include_dirs=[str(fixture.parent), str(tmp_path)],
        ),
    )

    parsed = parse_fortran_file(
        preprocessed.source,
        filename=_parser_filename_for_fixture(fixture),
    )

    assert parsed.modules or parsed.procedures
