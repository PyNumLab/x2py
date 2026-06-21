"""Structural checks for the wrapper guide and subject-oriented test layout."""

from pathlib import Path


WRAPPER_ROOT = Path(__file__).parent
WRAPPER_SUITE_ROOT = WRAPPER_ROOT.parent
DOCS_ROOT = WRAPPER_ROOT.parents[2] / "docs"
SUBJECT_TEST_MODULES = (
    "test_verified_baseline.py",
    "test_generic_interfaces.py",
    "test_defined_operators.py",
    "test_output_arguments.py",
    "test_optional_arguments.py",
    "test_value_and_bind_c.py",
    "test_allocatable_views.py",
    "test_allocatable_replacement.py",
    "test_pointers.py",
    "test_array_results.py",
    "test_array_contracts.py",
    "test_assumed_rank_arrays.py",
    "test_multidimensional_arrays.py",
    "test_bind_c_array_type.py",
    "test_derived_type_boundaries.py",
    "test_derived_type_methods.py",
    "test_inheritance.py",
    "test_constructors_and_finalizers.py",
    "test_borrowed_finalizers.py",
    "test_module_state.py",
    "test_common_blocks.py",
    "test_fortran_enums.py",
    "test_character_arguments.py",
    "test_character_edge_cases.py",
    "test_scalar_kinds.py",
    "test_derived_layout.py",
    "multi_source_builds/test_multi_source_builds.py",
    "test_build_modes.py",
    "test_compiler_verbose.py",
    "test_visibility_naming.py",
    "test_scalar_callbacks.py",
    "test_array_callbacks.py",
    "test_derived_callbacks.py",
    "test_runtime_policies.py",
    "test_runtime_recursion.py",
    "test_openmp_runtime.py",
    "test_runtime_abi.py",
    "test_pyi_wrapper_builds.py",
)
FORTRAN_SUFFIXES = {".f", ".f90", ".f95", ".for"}


def test_subject_tests_are_flat_except_for_true_multi_source_builds():
    missing = [relative_path for relative_path in SUBJECT_TEST_MODULES if not (WRAPPER_ROOT / relative_path).is_file()]
    assert missing == []

    section_directories = sorted(path.name for path in WRAPPER_ROOT.glob("section_*") if path.is_dir())
    assert section_directories == []

    multi_source_directory = WRAPPER_ROOT / "multi_source_builds"
    multi_source_fixtures = [
        path for path in multi_source_directory.rglob("*") if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES
    ]
    assert len(multi_source_fixtures) >= 2


def test_wrapper_language_suites_do_not_mix_test_modules():
    root_test_modules = sorted(path.name for path in WRAPPER_SUITE_ROOT.glob("test_*.py"))

    assert root_test_modules == []
    assert (WRAPPER_SUITE_ROOT / "README.md").is_file()
    assert "fortran/README.md" in (WRAPPER_SUITE_ROOT / "README.md").read_text(encoding="utf-8")


def test_every_fortran_fixture_is_named_by_a_python_test():
    test_text = "\n".join(
        (WRAPPER_ROOT / relative_path).read_text(encoding="utf-8") for relative_path in SUBJECT_TEST_MODULES
    )
    fixture_names = {
        path.name
        for path in WRAPPER_ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in FORTRAN_SUFFIXES and "__x2py__" not in path.parts
    }

    unreferenced = sorted(name for name in fixture_names if name not in test_text)
    assert unreferenced == []


def test_wrapper_index_lists_every_subject_test_module():
    index = (WRAPPER_ROOT / "README.md").read_text(encoding="utf-8")

    missing = [relative_path for relative_path in SUBJECT_TEST_MODULES if relative_path not in index]
    assert missing == []
    assert "section_" not in index


def test_wrapper_guide_links_runtime_subject_tests_without_checklist_boxes():
    guide = (DOCS_ROOT / "user-guide/fortran-wrapper.md").read_text(encoding="utf-8")
    guide_subjects = [path for path in SUBJECT_TEST_MODULES if path != "test_bind_c_array_type.py"]

    missing = [relative_path for relative_path in guide_subjects if relative_path not in guide]
    assert missing == []
    assert "- [x]" not in guide
    assert "- [ ]" not in guide


def test_obsolete_checklist_policy_files_section_layout_and_monolithic_test_are_removed():
    obsolete_docs = (
        "fortran_wrapper_checklist.md",
        "fortran_wrapper_ownership_policy.md",
        "fortran_wrapper_naming_policy.md",
    )

    assert not any((DOCS_ROOT / filename).exists() for filename in obsolete_docs)
    assert not (WRAPPER_ROOT / "CHECKLIST_COVERAGE.md").exists()
    assert not (WRAPPER_ROOT / "test_wrapper.py").exists()
    assert not any(WRAPPER_ROOT.glob("section_*"))
