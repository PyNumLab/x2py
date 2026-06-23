"""Structural checks for the wrapper guide and subject-oriented test layout."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tests.wrapper.fortran._support import REPO_ROOT, WRAPPER_FORTRAN_DATA, WRAPPER_TEST_ROOT

WRAPPER_ROOT = WRAPPER_TEST_ROOT
WRAPPER_SUITE_ROOT = WRAPPER_ROOT.parent
DOCS_ROOT = REPO_ROOT / "docs"
CHECKLIST_COVERAGE = WRAPPER_SUITE_ROOT / "CHECKLIST_COVERAGE.md"
FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".for"}
ROOT_FILES = {"README.md", "_support.py", "conftest.py", "fmath_cases.py", "valgrind.supp"}
SUBJECT_TEST_MODULES = {
    "contract_generation": (
        "test_contract_package_namespaces.py",
        "test_pyi_wrapper_builds.py",
    ),
    "native_build": (
        "test_build_modes.py",
        "test_compiler_verbose.py",
        "test_runtime_abi.py",
    ),
    "multi_source": ("test_multi_source_builds.py",),
    "standalone": (),
    "feature_parity": (
        "test_allocatable_replacement.py",
        "test_allocatable_views.py",
        "test_array_callbacks.py",
        "test_array_contracts.py",
        "test_array_results.py",
        "test_assumed_rank_arrays.py",
        "test_bind_c_array_type.py",
        "test_borrowed_finalizers.py",
        "test_character_arguments.py",
        "test_character_edge_cases.py",
        "test_common_blocks.py",
        "test_constructors_and_finalizers.py",
        "test_defined_operators.py",
        "test_derived_callbacks.py",
        "test_derived_layout.py",
        "test_derived_type_boundaries.py",
        "test_derived_type_methods.py",
        "test_fortran_enums.py",
        "test_generic_interfaces.py",
        "test_inheritance.py",
        "test_module_state.py",
        "test_multidimensional_arrays.py",
        "test_openmp_runtime.py",
        "test_optional_arguments.py",
        "test_output_arguments.py",
        "test_pointers.py",
        "test_runtime_policies.py",
        "test_runtime_recursion.py",
        "test_scalar_callbacks.py",
        "test_scalar_kinds.py",
        "test_value_and_bind_c.py",
        "test_verified_baseline.py",
        "test_visibility_naming.py",
    ),
    "editable_contracts": (),
    "parity_policy": (
        "test_codegen_structure.py",
        "test_wrapper_guide_layout.py",
    ),
    "library_scale": (),
}
ALLOWED_SUBJECTS = tuple(SUBJECT_TEST_MODULES)
SUBJECT_TEST_PATHS = tuple(
    f"{subject}/{filename}" for subject, filenames in SUBJECT_TEST_MODULES.items() for filename in filenames
)


def _is_meaningful(path: Path) -> bool:
    return "__pycache__" not in path.parts and path.suffix != ".pyc"


def _meaningful_files(path: Path) -> list[Path]:
    return [child for child in path.rglob("*") if child.is_file() and _is_meaningful(child)]


def _wrapper_fixture_paths() -> list[Path]:
    return sorted(
        path for path in WRAPPER_FORTRAN_DATA.rglob("*") if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
    )


def _subject_test_text() -> str:
    return "\n".join((WRAPPER_ROOT / relative_path).read_text(encoding="utf-8") for relative_path in SUBJECT_TEST_PATHS)


def _docs_and_test_text_paths() -> list[Path]:
    roots = (DOCS_ROOT, WRAPPER_SUITE_ROOT, REPO_ROOT / "README.md")
    return sorted(
        path
        for root in roots
        for path in ([root] if root.is_file() else root.rglob("*"))
        if path.is_file() and path.suffix in {".md", ".py"} and path != Path(__file__)
    )


def test_fortran_wrapper_tree_uses_only_allowed_subjects():
    missing_subjects = [subject for subject in ALLOWED_SUBJECTS if not (WRAPPER_ROOT / subject).is_dir()]
    assert missing_subjects == []

    unexpected_root_files = sorted(
        path.name
        for path in WRAPPER_ROOT.iterdir()
        if path.is_file() and _is_meaningful(path) and path.name not in ROOT_FILES
    )
    assert unexpected_root_files == []

    unexpected_directories = sorted(
        path.name
        for path in WRAPPER_ROOT.iterdir()
        if path.is_dir()
        and path.name not in ALLOWED_SUBJECTS
        and path.name != "__pycache__"
        and _meaningful_files(path)
    )
    assert unexpected_directories == []


def test_subject_test_modules_match_the_layout_contract():
    expected = set(SUBJECT_TEST_PATHS)
    actual = {
        path.relative_to(WRAPPER_ROOT).as_posix() for path in WRAPPER_ROOT.rglob("test_*.py") if _is_meaningful(path)
    }

    assert actual == expected
    assert not list(WRAPPER_ROOT.glob("test_*.py"))
    assert not any(WRAPPER_ROOT.glob("section_*"))


def test_native_wrapper_sources_live_only_in_the_shared_corpus():
    in_wrapper_tree = sorted(
        path.relative_to(WRAPPER_ROOT).as_posix()
        for path in WRAPPER_ROOT.rglob("*")
        if path.is_file() and _is_meaningful(path) and path.suffix.lower() in FORTRAN_SUFFIXES
    )
    assert in_wrapper_tree == []

    fixture_paths = _wrapper_fixture_paths()
    assert len(fixture_paths) >= 40

    fixture_name_counts = Counter(path.name for path in fixture_paths)
    duplicate_names = sorted(name for name, count in fixture_name_counts.items() if count > 1)
    assert duplicate_names == []

    test_text = _subject_test_text()
    unreferenced = sorted(path.name for path in fixture_paths if path.name not in test_text)
    assert unreferenced == []


def test_runtime_contract_fixtures_stay_under_consuming_subjects():
    contract_files = sorted(
        path.relative_to(WRAPPER_ROOT).as_posix()
        for path in WRAPPER_ROOT.glob("*/contracts/**/*")
        if path.is_file() and _is_meaningful(path)
    )
    assert contract_files
    assert all(path.endswith(".pyi") for path in contract_files)

    bad_locations = []
    for relative_path in contract_files:
        parts = relative_path.split("/")
        if len(parts) < 5 or parts[0] not in ALLOWED_SUBJECTS or parts[1] != "contracts":
            bad_locations.append(relative_path)
            continue
        if parts[3] not in {"generated", "modified", "handwritten", "invalid"}:
            bad_locations.append(relative_path)
    assert bad_locations == []

    undocumented_modified = [
        relative_path
        for relative_path in contract_files
        if "/modified/" in relative_path
        and not (WRAPPER_ROOT / relative_path).read_text(encoding="utf-8").startswith("# Intentional difference:")
    ]
    assert undocumented_modified == []


def test_subject_readmes_and_checklist_coverage_index_the_layout():
    for subject, test_modules in SUBJECT_TEST_MODULES.items():
        readme = WRAPPER_ROOT / subject / "README.md"
        assert readme.is_file(), subject
        text = readme.read_text(encoding="utf-8")
        for required in ("Focused pytest command:", "Native data path:", "Contract fixtures:", "Roadmap items:"):
            assert required in text, f"{subject} README missing {required}"
        for test_module in test_modules:
            assert test_module in text, f"{subject} README missing {test_module}"

    coverage_text = CHECKLIST_COVERAGE.read_text(encoding="utf-8")
    missing_subjects = [f"fortran/{subject}/README.md" for subject in ALLOWED_SUBJECTS if subject not in coverage_text]
    missing_tests = [test_path for test_path in SUBJECT_TEST_PATHS if test_path not in coverage_text]
    assert missing_subjects == []
    assert missing_tests == []


def test_wrapper_language_suite_and_user_guide_link_current_subject_paths():
    root_test_modules = sorted(path.name for path in WRAPPER_SUITE_ROOT.glob("test_*.py"))
    assert root_test_modules == []
    assert (WRAPPER_SUITE_ROOT / "README.md").is_file()
    assert "fortran/README.md" in (WRAPPER_SUITE_ROOT / "README.md").read_text(encoding="utf-8")

    guide = (DOCS_ROOT / "user-guide/fortran-wrapper.md").read_text(encoding="utf-8")
    runtime_paths = [
        test_path
        for test_path in SUBJECT_TEST_PATHS
        if not test_path.startswith("parity_policy/")
        and test_path
        not in {
            "contract_generation/test_contract_package_namespaces.py",
            "feature_parity/test_bind_c_array_type.py",
        }
    ]
    missing = [test_path for test_path in runtime_paths if test_path not in guide]
    assert missing == []
    assert "- [x]" not in guide
    assert "- [ ]" not in guide


def test_stale_wrapper_paths_are_rejected_after_stage_one_moves():
    fixture_names = [path.name for path in _wrapper_fixture_paths()]
    stale_fragments = [
        "tests/wrapper/fortran/" + "test_",
        "tests/wrapper/fortran/" + "multi_source" + "_builds",
        "tests/wrapper/fortran/" + "pyi/",
        *(f"tests/wrapper/fortran/{fixture_name}" for fixture_name in fixture_names),
    ]
    offenders = []
    for path in _docs_and_test_text_paths():
        text = path.read_text(encoding="utf-8")
        for fragment in stale_fragments:
            if fragment in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {fragment}")
    assert offenders == []


def test_obsolete_policy_files_and_monolithic_wrapper_test_are_removed():
    obsolete_docs = (
        "fortran_wrapper_checklist.md",
        "fortran_wrapper_ownership_policy.md",
        "fortran_wrapper_naming_policy.md",
    )

    assert not any((DOCS_ROOT / filename).exists() for filename in obsolete_docs)
    assert not (WRAPPER_ROOT / "test_wrapper.py").exists()
    assert not any(WRAPPER_ROOT.glob("section_*"))
