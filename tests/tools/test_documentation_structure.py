"""Verify the documentation architecture contract."""

from __future__ import annotations

from functools import cache
from pathlib import Path
import re
import subprocess
import sys

import pytest
import x2py


ROOT = Path(__file__).parents[2]
DOCS_ROOT = ROOT / "docs"
FEATURE_MATRIX_PATH = DOCS_ROOT / "language-support/feature-matrix.md"
CLI_REFERENCE_PATH = DOCS_ROOT / "reference/cli-commands.md"
PYTHON_API_REFERENCE_PATH = DOCS_ROOT / "reference/python-api.md"
DOCUMENTATION_CHECKLIST_PATH = DOCS_ROOT / "roadmap/documentation-content-checklist.md"
DOC_PATHS = sorted(path for path in DOCS_ROOT.rglob("*.md") if "old_docs" not in path.parts)
PUBLIC_DOCUMENTATION_PATHS = [ROOT / "README.md", *DOC_PATHS]
DEFERRED_C_PAGE_PATHS = [
    ROOT / "docs/design/cpython-integration.md",
    ROOT / "docs/developer-guide/c-parser-reference.md",
    ROOT / "docs/examples-gallery/recipes/inspect-c-api.md",
]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)#]+)(?:#[^)]+)?\)")
C_DOCS_START = "<!-- X2PY_C_DOCS_START"
C_DOCS_END = "X2PY_C_DOCS_END -->"
C_DOCS_DISABLED = "<!-- X2PY_C_DOCS_DISABLED:"
VISIBLE_C_DOCUMENTATION_EXCEPTIONS = {
    "docs/user-guide/enumerations.md": ("bind(C)",),
}
VISIBLE_C_DOCUMENTATION = re.compile(
    r"(?:"
    r"(?<![A-Za-z0-9_])C(?:\+\+)?(?![A-Za-z0-9_])"
    r"|CPython"
    r"|Cython"
    r"|C-input"
    r"|bind\s*\(\s*c\s*\)"
    r"|```c(?:\s|$)"
    r"|\b(?:c_parser|c2ir|fortran_to_c|c_to_python|cpython_api|cpythoncode)\b"
    r"|\b(?:ccode|cpreprocessor)\.py\b"
    r"|\btest_c(?:2ir|_(?:semantic|parser|declarations|functions|structs|project|compiler|corpus|fixture|json|error|public))[A-Za-z0-9_]*\b"
    r"|\b(?:bind_c|iso_c_binding)\b"
    r"|\b[A-Za-z][A-Za-z0-9_]*_c\b"
    r"|\bc_[A-Za-z0-9_]+\b"
    r"|\b(?:ORDER_C|REQUIRE_C_CONTIGUOUS|NPY_C_CONTIGUOUS)\b"
    r"|\b(?:CToIR|CFile|CProject|CParse|CDiagnostic)[A-Za-z0-9_]*\b"
    r"|\b(?:parse_c|c_file|c_project|c_function|c_parameter|c_struct|c_type)_[A-Za-z0-9_]+\b"
    r"|(?:tests/data/c|tests/parser/c|x2py/c_parser|/c/general/)"
    r"|(?:c-parser|inspect-c-api|c-api)"
    r"|\b(?:structs?|unions?|typedefs?|declarators?|bitfields?|K&R)\b"
    r"|--language\s+c\b"
    r"|(?:fortran\|c|\{fortran,c\}|\bc11\b|\bc17\b|\bc23\b)"
    r"|\"language\"\s*:\s*\"c\""
    r"|\.(?:c|h)(?:\b|`)"
    r"|\b(?:CFLAGS|CC|gcc(?:-\d+)?|clang(?:-\d+)?|cJSON)\b"
    r"|\bc-type(?:s|\b)"
    r")"
)
REQUIRED_METADATA = {"title", "audience", "prerequisites", "related", "status"}
ALLOWED_STATUSES = {
    "active-roadmap",
    "design",
    "draft",
    "maintained",
    "not-yet-implemented",
    "planned-documentation",
}
TODO_STATUSES = {"draft", "not-yet-implemented", "planned-documentation"}
REQUIRED_AREA_INDEXES = [
    "getting-started/index.md",
    "user-guide/index.md",
    "tutorials/index.md",
    "examples-gallery/index.md",
    "reference/index.md",
    "language-support/index.md",
    "design/index.md",
    "developer-guide/index.md",
    "internal-architecture/index.md",
    "roadmap/index.md",
    "faq/index.md",
    "troubleshooting/index.md",
    "changelog/index.md",
    "contributing/index.md",
]
REQUIRED_REFERENCE_PAGES = [
    "reference/index.md",
    "reference/cli-commands.md",
    "reference/python-api.md",
    "reference/semantic-ir.md",
    "reference/semantic-pyi-format.md",
    "reference/diagnostic-codes.md",
]
REQUIRED_ROADMAP_PAGES = [
    "roadmap/index.md",
    "roadmap/semantic-pyi-wrapper-checklist.md",
    "roadmap/documentation-content-checklist.md",
]
REQUIRED_GETTING_STARTED_PAGES = [
    "getting-started/index.md",
    "getting-started/installation.md",
    "getting-started/verification.md",
    "getting-started/first-wrapped-function.md",
    "getting-started/first-wrapped-module.md",
    "getting-started/beginner-workflow.md",
]
REQUIRED_USER_GUIDE_PAGES = [
    "user-guide/index.md",
    "user-guide/data-types.md",
    "user-guide/wrapping-functions.md",
    "user-guide/wrapping-subroutines.md",
    "user-guide/wrapping-modules.md",
    "user-guide/arrays.md",
    "user-guide/optional-arguments.md",
    "user-guide/generic-interfaces.md",
    "user-guide/allocatable-arrays.md",
    "user-guide/pointer-arguments.md",
    "user-guide/wrapping-derived-types.md",
    "user-guide/memory-management.md",
    "user-guide/callbacks.md",
    "user-guide/enumerations.md",
    "user-guide/error-handling.md",
    "user-guide/packaging.md",
    "user-guide/distribution.md",
    "user-guide/fortran-wrapper.md",
    "user-guide/editing-semantic-pyi-contracts.md",
]
CLI_HELP_GROUP_HEADINGS = [
    "input selection:",
    "inspection stages:",
    "compiler preprocessing:",
    "target type probes:",
    "C include exposure:",
    "parse report controls:",
    "wrapper builds:",
    "output and diagnostics:",
]
CLI_REFERENCE_OPTIONS = [
    "paths",
    "--language",
    "--parse",
    "--semantics",
    "--pyi",
    "--wrap-readiness",
    "--preprocessor-adapter",
    "--compiler",
    "--preprocess-template",
    "-I",
    "--include-dir",
    "-D",
    "--define",
    "-U",
    "--undef",
    "--std",
    "--compiler-arg",
    "--fortran-type-report",
    "--fortran-type-probe-runner",
    "--fortran-type-probe-cache-dir",
    "--refresh-fortran-type-probe",
    "--show-vars",
    "--print-limit",
    "--vars-limit",
    "--wrap",
    "--makefile",
    "--strict-wrapper-names",
    "--build-manifest",
    "--native-fortran-sources",
    "--native-fortran-flags",
    "--native-objects",
    "--native-library",
    "--native-link-item",
    "--native-library-dir",
    "--library-dir",
    "--native-include-dir",
    "--json",
    "--out",
    "--out-dir",
    "--verbose",
    "--no-color",
    "--debug",
    "--debug-traceback",
]
CLI_VISIBLE_HELP_OPTIONS = [option for option in CLI_REFERENCE_OPTIONS if option != "--vars-limit"]
REQUIRED_SOURCE_NAVIGATION_PAGES = [
    "developer-guide/source-map.md",
    "developer-guide/feature-to-code-map.md",
    "developer-guide/repository-structure.md",
    "internal-architecture/pipeline-map.md",
]
SOURCE_NAVIGATION_CORPUS = [
    "docs/developer-guide/source-map.md",
    "docs/developer-guide/feature-to-code-map.md",
    "docs/developer-guide/repository-structure.md",
    "docs/internal-architecture/pipeline-map.md",
    "x2py/README.md",
    "x2py/c_parser/README.md",
    "x2py/fortran_parser/README.md",
    "x2py/semantics/README.md",
    "x2py/codegen/README.md",
    "x2py/compiling/README.md",
]
SOURCE_NAVIGATION_HOTSPOTS = [
    "x2py/__init__.py",
    "x2py/cli.py",
    "x2py/wrapping.py",
    "x2py/preprocessing.py",
    "x2py/c_type_probe.py",
    "x2py/fortran_type_probe.py",
    "x2py/ownership_policy.py",
    "x2py/c_parser/parser.py",
    "x2py/c_parser/cli.py",
    "x2py/fortran_parser/parser.py",
    "x2py/fortran_parser/cli.py",
    "x2py/semantics/models.py",
    "x2py/semantics/fortran2ir.py",
    "x2py/semantics/c2ir.py",
    "x2py/semantics/pyi_parser.py",
    "x2py/semantics/pyi2ir.py",
    "x2py/semantics/policy_completion.py",
    "x2py/semantics/readiness.py",
    "x2py/semantics/ir2ast.py",
    "x2py/codegen/binding_pipeline.py",
    "x2py/codegen/bridges/fortran_to_c.py",
    "x2py/codegen/bindings/c_to_python.py",
    "x2py/codegen/bindings/cpython_api.py",
    "x2py/codegen/bindings/numpy_cpython_api.py",
    "x2py/codegen/printers/fcode.py",
    "x2py/codegen/printers/ccode.py",
    "x2py/codegen/printers/cpythoncode.py",
    "x2py/codegen/printers/pyi_printer.py",
    "x2py/compiling/basic.py",
    "x2py/compiling/compilers.py",
    "x2py/compiling/python_wrapper.py",
    "x2py/compiling/runtime_support.py",
    "x2py/naming/policy.py",
    "x2py/stdlib/",
]
SOURCE_NAVIGATION_PUBLIC_DOCS = [
    "README.md",
    "docs/documentation-architecture.md",
    "docs/tutorials/basic-wrapper.md",
    "docs/examples-gallery/verified-cookbook.md",
    "docs/examples-gallery/recipes/build-and-import-cli.md",
    "docs/examples-gallery/recipes/build-multiple-fortran-sources.md",
    "docs/examples-gallery/recipes/compiler-preprocessing.md",
    "docs/examples-gallery/recipes/generate-editable-makefile.md",
    "docs/examples-gallery/recipes/inspect-c-api.md",
    "docs/examples-gallery/recipes/inspect-fortran-api.md",
    "docs/examples-gallery/recipes/semantic-pyi-contracts.md",
    "docs/user-guide/fortran-wrapper.md",
    "docs/user-guide/editing-semantic-pyi-contracts.md",
    "docs/reference/cli-commands.md",
    "docs/reference/diagnostic-codes.md",
    "docs/reference/python-api.md",
    "docs/reference/semantic-ir.md",
    "docs/reference/semantic-pyi-format.md",
    "docs/developer-guide/build-system.md",
    "docs/developer-guide/c-parser-reference.md",
    "docs/developer-guide/fortran-parser-reference.md",
    "docs/developer-guide/quality-assurance.md",
    "docs/design/memory-ownership-model.md",
    "docs/internal-architecture/wrapper-generation-pipeline.md",
    "docs/language-support/feature-matrix.md",
    "docs/roadmap/semantic-pyi-wrapper-checklist.md",
]
SOURCE_NAVIGATION_TEST_TARGETS = [
    "tests/parser/",
    "tests/parser/c/",
    "tests/parser/test_cli.py",
    "tests/parser/test_fortran_fixture_suite.py",
    "tests/parser/test_parser_public_entrypoints.py",
    "tests/parser/test_preprocessing_cli.py",
    "tests/parser/test_preprocessor_and_execution_boundaries.py",
    "tests/pyi/",
    "tests/pyi/test_contract_package_generation.py",
    "tests/pyi/test_pyi_fixture_suite.py",
    "tests/pyi/test_pyi_to_ir.py",
    "tests/semantics/",
    "tests/semantics/test_c2ir.py",
    "tests/semantics/test_c_semantic_readiness.py",
    "tests/semantics/test_fortran2ir.py",
    "tests/semantics/test_ir2ast.py",
    "tests/semantics/test_pyi_printer.py",
    "tests/semantics/test_pyi_printer_modern_example.py",
    "tests/semantics/test_semantic_wrap_readiness.py",
    "tests/tools/test_documentation_examples.py",
    "tests/tools/test_documentation_structure.py",
    "tests/wrapper/fortran/",
    "tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py",
    "tests/wrapper/fortran/multiple_files/test_multi_source_builds.py",
    "tests/wrapper/fortran/build_from_source/test_build_modes.py",
    "tests/wrapper/fortran/build_from_source/test_runtime_abi.py",
]
PACKAGE_README_NAVIGATION_REFERENCES = [
    "docs/developer-guide/source-map.md",
    "docs/developer-guide/feature-to-code-map.md",
]
LEGACY_ACTIVE_DOC_REFERENCES = [
    "docs/c_parser.md",
    "docs/fortran_parser.md",
    "docs/fortran_wrapper.md",
    "docs/pyi_format.md",
    "docs/pyi_wrapper_checklist.md",
    "docs/quality.md",
    "docs/semantics.md",
]
FEATURE_MATRIX_STATUSES = {
    "Supported",
    "Partially supported",
    "Unsupported",
    "Planned",
    "Not implemented",
}
FEATURE_MATRIX_REQUIRED_FEATURES = [
    "Fortran source wrapper builds",
    "Scalar functions, subroutines, and baseline arrays",
    "Generic procedure interfaces",
    "Defined operators and assignment overloads",
    "Output arguments and multiple results",
    "Optional arguments",
    "Allocatable outputs, results, replacements, and borrowed module/component views",
    "Pointer call-local inputs and snapshot results",
    "Array-valued function results",
    "NumPy array argument contracts",
    "Derived-type scalar boundaries and methods",
    "Default and keyword constructors with finalizers",
    "Module variables, constants, saved state, and common-block procedure state",
    "Fortran enum constants",
    "Scalar character arguments, results, and fields",
    "Scalar kind coverage",
    "Caller-ordered multi-source builds, Makefiles, verbose mode, and output placement",
    "Visibility, naming, keyword escaping, and collision policy",
    "Immediate call-scoped Python callbacks",
    "Runtime error projection, GIL policy, recursion, OpenMP path, and GNU ABI checks",
    "Fortran parse, semantic IR, `.pyi`, and readiness inspection",
    "Semantic `.pyi` wrapper builds from explicit native artifacts",
    "Assumed-size, assumed-rank, and lower-bound array contracts",
    "Scalar inheritance and polymorphic dispatch",
    "General borrowed pointer views and pointer reassociation",
    "Persistent callbacks and procedure pointers",
    "Advanced multi-source dependency discovery and external-library integration",
    "Blocked array forms",
    "Unsupported polymorphic forms",
    "Generic constructor interfaces and overloaded runtime initialization",
    "Character arrays and mutable deferred-length character storage",
    "Wider-than-supported real, complex, and logical storage",
    "Full semantic `.pyi` parity across all wrapper scenarios",
    "MPI examples and distribution constraints",
    "Generated reference pages for modules, functions, and classes",
]
REQUIRED_EXAMPLE_RECIPE_PAGES = [
    "examples-gallery/verified-cookbook.md",
    "examples-gallery/recipes/build-and-import-cli.md",
    "examples-gallery/recipes/build-and-import-python-api.md",
    "examples-gallery/recipes/generate-editable-makefile.md",
    "examples-gallery/recipes/build-multiple-fortran-sources.md",
    "examples-gallery/recipes/inspect-fortran-api.md",
    "examples-gallery/recipes/inspect-c-api.md",
    "examples-gallery/recipes/semantic-pyi-contracts.md",
    "examples-gallery/recipes/control-cli-output.md",
    "examples-gallery/recipes/use-python-inspection-apis.md",
    "examples-gallery/recipes/compiler-preprocessing.md",
]
MAJOR_SOURCE_PACKAGES = [
    "x2py/c_parser/",
    "x2py/fortran_parser/",
    "x2py/semantics/",
    "x2py/codegen/",
    "x2py/compiling/",
]
PACKAGE_READMES = [
    "x2py/README.md",
    "x2py/c_parser/README.md",
    "x2py/fortran_parser/README.md",
    "x2py/semantics/README.md",
    "x2py/codegen/README.md",
    "x2py/compiling/README.md",
]
ARCHIVED_OLD_DOCS = [
    "old_docs/tutorial.md",
    "old_docs/examples.md",
    "old_docs/fortran_wrapper.md",
    "old_docs/semantics.md",
    "old_docs/pyi_format.md",
    "old_docs/diagnostic_codes.md",
    "old_docs/pyi_wrapper_checklist.md",
    "old_docs/developper_guide.md",
    "old_docs/quality.md",
    "old_docs/c_parser.md",
    "old_docs/fortran_parser.md",
    "old_docs/wrapper_design_notes.md",
    "old_docs/architecture/semantic_multilanguage_wrapper_runtime_architecture.md",
]
OLD_TOP_LEVEL_DOCS = [
    "tutorial.md",
    "examples.md",
    "fortran_wrapper.md",
    "semantics.md",
    "pyi_format.md",
    "diagnostic_codes.md",
    "pyi_wrapper_checklist.md",
    "developper_guide.md",
    "quality.md",
    "c_parser.md",
    "fortran_parser.md",
    "wrapper_design_notes.md",
]


def _front_matter(path: Path) -> tuple[dict[str, str], str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0] == "---", f"{path.relative_to(ROOT)}: missing front matter"

    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise AssertionError(f"{path.relative_to(ROOT)}: unclosed front matter") from error

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        assert separator, f"{path.relative_to(ROOT)}: invalid front matter line: {line!r}"
        metadata[key.strip()] = value.strip()

    return metadata, "\n".join(lines[end + 1 :])


def _visible_documentation_source(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if path != ROOT / "README.md" and lines and lines[0] == "---":
        lines = lines[lines.index("---", 1) + 1 :]

    visible: list[str] = []
    hidden = False
    for line in lines:
        stripped = line.strip()
        if stripped == C_DOCS_START:
            assert not hidden, f"{path.relative_to(ROOT)}: nested deferred documentation comment"
            hidden = True
        elif stripped == C_DOCS_END:
            assert hidden, f"{path.relative_to(ROOT)}: unmatched deferred documentation comment end"
            hidden = False
        elif hidden:
            assert "--" not in line, f"{path.relative_to(ROOT)}: invalid double hyphen in deferred comment"
        elif not line.lstrip().startswith(C_DOCS_DISABLED):
            visible.append(line)
    assert not hidden, f"{path.relative_to(ROOT)}: unclosed deferred documentation comment"
    return "\n".join(visible)


def _combined_text(relative_paths: list[str]) -> str:
    return "\n".join((ROOT / relative_path).read_text(encoding="utf-8") for relative_path in relative_paths)


@cache
def _x2py_cli_help() -> str:
    result = subprocess.run(
        [sys.executable, "-m", "x2py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _feature_matrix_rows() -> list[dict[str, str]]:
    header = "| Feature | Status | User docs | Source owner | Evidence | Limitations |"
    columns = ["Feature", "Status", "User docs", "Source owner", "Evidence", "Limitations"]
    rows: list[dict[str, str]] = []
    in_table = False

    for line in FEATURE_MATRIX_PATH.read_text(encoding="utf-8").splitlines():
        if line == header:
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("| ---"):
            continue
        if not line.startswith("|"):
            in_table = False
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == len(columns), f"invalid feature matrix row: {line!r}"
        rows.append(dict(zip(columns, cells, strict=True)))

    return rows


FEATURE_MATRIX_ROWS = _feature_matrix_rows()


@pytest.mark.parametrize("path", DOC_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_documentation_page_metadata(path: Path) -> None:
    metadata, body = _front_matter(path)
    missing = REQUIRED_METADATA - metadata.keys()
    assert not missing, f"{path.relative_to(ROOT)}: missing metadata fields: {sorted(missing)}"

    for key in REQUIRED_METADATA:
        assert metadata[key], f"{path.relative_to(ROOT)}: metadata field {key!r} is empty"

    assert metadata["status"] in ALLOWED_STATUSES, f"{path.relative_to(ROOT)}: unknown status {metadata['status']!r}"
    if metadata["status"] in TODO_STATUSES:
        assert "## TODO" in body, f"{path.relative_to(ROOT)}: unfinished pages must include a TODO section"
        assert "TODO:" in body, f"{path.relative_to(ROOT)}: TODO section must contain explicit TODO markers"


@pytest.mark.parametrize("path", PUBLIC_DOCUMENTATION_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_deferred_c_documentation_is_not_visible(path: Path) -> None:
    visible = _visible_documentation_source(path)
    for allowed_text in VISIBLE_C_DOCUMENTATION_EXCEPTIONS.get(str(path.relative_to(ROOT)), ()):
        visible = visible.replace(allowed_text, "")
    match = VISIBLE_C_DOCUMENTATION.search(visible)
    assert match is None, f"{path.relative_to(ROOT)}: visible deferred documentation: {match.group(0)!r}"


@pytest.mark.parametrize("path", DEFERRED_C_PAGE_PATHS, ids=lambda path: str(path.relative_to(ROOT)))
def test_dedicated_deferred_c_pages_have_no_visible_body(path: Path) -> None:
    assert _visible_documentation_source(path).strip() == ""


def test_deferred_c_pages_are_not_in_site_navigation() -> None:
    lines = (ROOT / "mkdocs.yml").read_text(encoding="utf-8").splitlines()
    active_navigation = "\n".join(line for line in lines if not line.lstrip().startswith("#"))
    assert "Inspect a C API" not in active_navigation
    assert "C Parser Reference" not in active_navigation
    assert any("X2PY_C_DOCS" in line and "inspect-c-api.md" in line for line in lines)
    assert any("X2PY_C_DOCS" in line and "c-parser-reference.md" in line for line in lines)


def test_readme_quick_start_shows_input_source_before_wrapper_build() -> None:
    readme = _visible_documentation_source(ROOT / "README.md")
    quick_start = readme.split("## Quick Start", maxsplit=1)[1].split(
        "The runtime wrapper mechanism is:",
        maxsplit=1,
    )[0]

    source_index = quick_start.index("<!-- x2py-doc-source: tests/data/fortran/wrapper/scale.f90 -->")
    fortran_block_index = quick_start.index("```fortran", source_index)
    source_build_command_index = quick_start.index(
        "python3 -m x2py scale.f90",
        fortran_block_index,
    )
    default_source_build_tree_index = quick_start.index(
        ".\n  scale.f90\n  scale.so\n  __x2py__/", source_build_command_index
    )
    named_source_build_command_index = quick_start.index(
        "python3 -m x2py scale.f90 --out SCALE",
        default_source_build_tree_index,
    )
    named_source_build_tree_index = quick_start.index(
        ".\n  scale.f90\n  SCALE.so\n  __x2py__/",
        named_source_build_command_index,
    )
    explicit_source_build_command_index = quick_start.index(
        "python3 -m x2py scale.f90 \\\n  --out SCALE \\\n  --out-dir build/SCALE",
        named_source_build_tree_index,
    )
    explicit_source_build_tree_index = quick_start.index("build/SCALE/", explicit_source_build_command_index)
    pyi_generation_command_index = quick_start.index(
        "python3 -m x2py scale.f90 \\\n  --pyi",
        explicit_source_build_tree_index,
    )
    pyi_contract_tree_index = quick_start.index("contracts/\n  __init__.pyi", pyi_generation_command_index)
    pyi_contract_body_index = quick_start.index(
        "@external\ndef scale(\n    value: Ptr(Const(Float64)),\n    factor: Ptr(Const(Float64))\n) -> Float64: ...",
        pyi_contract_tree_index,
    )
    pyi_build_command_index = quick_start.index(
        "python3 -m x2py contracts/__init__.pyi",
        pyi_contract_body_index,
    )
    native_source_argument_index = quick_start.index("--native-fortran-sources scale.f90", pyi_build_command_index)
    output_name_index = quick_start.index("--out SCALE", native_source_argument_index)
    pyi_build_tree_index = quick_start.index("build/SCALE_from_pyi/", output_name_index)
    direct_import_index = quick_start.index("SCALE.scale(", pyi_build_tree_index)
    package_entry_import_section_index = quick_start.index("The package-entry `.pyi` build", direct_import_index)
    pyi_import_index = quick_start.index("SCALE.scale(", package_entry_import_section_index)
    module_lesson_index = quick_start.index("first wrapped module", pyi_import_index)
    runtime_output_index = quick_start.index("7.5", pyi_import_index)

    assert source_index < fortran_block_index < source_build_command_index
    assert source_build_command_index < default_source_build_tree_index < named_source_build_command_index
    assert named_source_build_command_index < named_source_build_tree_index < explicit_source_build_command_index
    assert explicit_source_build_command_index < explicit_source_build_tree_index < pyi_generation_command_index
    assert pyi_generation_command_index < pyi_contract_tree_index < pyi_contract_body_index
    assert pyi_contract_body_index < pyi_build_command_index < native_source_argument_index < output_name_index
    assert output_name_index < pyi_build_tree_index < direct_import_index < package_entry_import_section_index
    assert package_entry_import_section_index < pyi_import_index
    assert pyi_import_index < runtime_output_index < module_lesson_index
    assert "tests/data/fortran/wrapper/scale.f90" in quick_start
    assert "scale.f90 --json" not in quick_start
    assert "python3 -m x2py solver.f90" not in quick_start
    assert "python3 -m x2py tests/data/fortran/wrapper/scale.f90" not in quick_start
    assert "fruntime_abi_f90" not in readme
    assert "solver.f90" not in readme
    assert "add1" not in readme
    assert "tests/data/fortran/general/basic_subroutine.f90" not in readme
    assert "contracts/basic_subroutine/basic_subroutine.pyi" not in readme


@pytest.mark.parametrize("relative_path", REQUIRED_AREA_INDEXES)
def test_required_documentation_area_exists(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", REQUIRED_REFERENCE_PAGES)
def test_required_reference_page_exists(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", REQUIRED_REFERENCE_PAGES)
def test_reference_page_is_in_site_navigation(relative_path: str) -> None:
    site_configuration = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert relative_path in site_configuration


@pytest.mark.parametrize("relative_path", REQUIRED_ROADMAP_PAGES)
def test_required_roadmap_page_exists(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", REQUIRED_ROADMAP_PAGES)
def test_roadmap_page_is_in_site_navigation(relative_path: str) -> None:
    site_configuration = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert relative_path in site_configuration


@pytest.mark.parametrize("relative_path", REQUIRED_GETTING_STARTED_PAGES)
def test_required_getting_started_page_is_maintained_and_navigable(relative_path: str) -> None:
    path = DOCS_ROOT / relative_path
    assert path.is_file()
    metadata, body = _front_matter(path)
    assert metadata["status"] == "maintained"
    assert relative_path in (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    for target in MARKDOWN_LINK.findall(body):
        if target.startswith(("http://", "https://")):
            continue
        assert (path.parent / target).resolve().exists(), f"{relative_path}: missing link target {target}"


@pytest.mark.parametrize("relative_path", REQUIRED_GETTING_STARTED_PAGES)
def test_getting_started_page_is_completed_in_documentation_checklist(relative_path: str) -> None:
    checklist = DOCUMENTATION_CHECKLIST_PATH.read_text(encoding="utf-8")
    assert f"- [x] `docs/{relative_path}`" in checklist


@pytest.mark.parametrize("relative_path", REQUIRED_USER_GUIDE_PAGES)
def test_required_user_guide_page_is_maintained_and_navigable(relative_path: str) -> None:
    path = DOCS_ROOT / relative_path
    assert path.is_file()
    metadata, body = _front_matter(path)
    assert metadata["status"] == "maintained"
    assert relative_path in (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    for target in MARKDOWN_LINK.findall(body):
        if target.startswith(("http://", "https://")):
            continue
        assert (path.parent / target).resolve().exists(), f"{relative_path}: missing link target {target}"


@pytest.mark.parametrize("relative_path", REQUIRED_USER_GUIDE_PAGES)
def test_user_guide_page_is_completed_in_documentation_checklist(relative_path: str) -> None:
    checklist = DOCUMENTATION_CHECKLIST_PATH.read_text(encoding="utf-8")
    assert f"- [x] `docs/{relative_path}`" in checklist


@pytest.mark.parametrize("relative_path", REQUIRED_USER_GUIDE_PAGES[:-2])
def test_user_guide_commands_do_not_expose_fixture_paths(relative_path: str) -> None:
    page = (DOCS_ROOT / relative_path).read_text(encoding="utf-8")
    assert "python3 -m x2py tests/" not in page


def test_getting_started_overview_uses_standalone_example_and_current_evidence() -> None:
    overview = (DOCS_ROOT / "getting-started/index.md").read_text(encoding="utf-8")

    assert "scale.scale(np.float64(3.0), np.float64(2.5))" in overview
    assert "build_from_source/test_build_modes.py" in overview


def test_first_wrapped_function_shows_contract_and_routes_support_boundaries_centrally() -> None:
    page = (DOCS_ROOT / "getting-started/first-wrapped-function.md").read_text(encoding="utf-8")
    source_index = page.index("[README Quick Start](../../README.md#quick-start)")
    build_index = page.index("python3 -m x2py scale.f90 \\")
    command_index = page.index("python3 -m x2py scale.f90 --pyi")
    contract_index = page.index(
        "@external\ndef scale(\n    value: Ptr(Const(Float64)),\n    factor: Ptr(Const(Float64))\n) -> Float64: ..."
    )

    assert source_index < build_index < command_index < contract_index
    assert "<!-- x2py-doc-source: tests/data/fortran/wrapper/scale.f90 -->" not in page
    assert "## Current Limitations" not in page
    assert "[language feature matrix](../language-support/feature-matrix.md)" in page


def test_first_wrapped_module_shows_local_input_and_generated_contract() -> None:
    page = (DOCS_ROOT / "getting-started/first-wrapped-module.md").read_text(encoding="utf-8")
    source_index = page.index("Create `module_state.f90` with this module:")
    build_index = page.index("python3 -m x2py module_state.f90 \\")
    inspect_index = page.index("python3 -m x2py module_state.f90 --pyi")
    contract_index = page.index("nmax: Final[Int32] = 12")

    assert source_index < build_index < inspect_index < contract_index
    assert "fmodule_vars_f90" not in page
    assert "## Current Limitations" not in page
    assert "[language feature matrix](../language-support/feature-matrix.md)" in page


def test_beginner_workflow_reuses_scale_example_without_renaming_it() -> None:
    page = (DOCS_ROOT / "getting-started/beginner-workflow.md").read_text(encoding="utf-8")
    source_reference_index = page.index("[README Quick Start](../../README.md#quick-start)")
    layout_index = page.index("src/\n    scale.f90")
    inspect_index = page.index("python3 -m x2py src/scale.f90 --wrap-readiness")
    build_index = page.index("python3 -m x2py src/scale.f90 \\\n  --wrap \\\n  --out-dir build/scale")
    smoke_index = page.index("result = scale.scale(np.float64(3.0), np.float64(2.5))")
    advanced_index = page.index("## Advanced Next Step: Edit The Semantic Contract")

    assert source_reference_index < layout_index < inspect_index < build_index < smoke_index < advanced_index
    assert "scale_api" not in page


@pytest.mark.parametrize("heading", CLI_HELP_GROUP_HEADINGS)
def test_cli_help_uses_documented_option_groups(heading: str) -> None:
    assert heading in _x2py_cli_help()


@pytest.mark.parametrize("option", CLI_REFERENCE_OPTIONS)
def test_cli_reference_documents_public_option(option: str) -> None:
    content = CLI_REFERENCE_PATH.read_text(encoding="utf-8")
    assert option in content


@pytest.mark.parametrize("option", CLI_VISIBLE_HELP_OPTIONS)
def test_cli_help_exposes_documented_public_option(option: str) -> None:
    assert option in _x2py_cli_help()


@pytest.mark.parametrize("name", sorted(x2py.__all__))
def test_python_api_reference_documents_public_export(name: str) -> None:
    content = PYTHON_API_REFERENCE_PATH.read_text(encoding="utf-8")
    assert f"`{name}`" in content


@pytest.mark.parametrize("relative_path", REQUIRED_SOURCE_NAVIGATION_PAGES)
def test_required_source_navigation_page_exists(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", REQUIRED_SOURCE_NAVIGATION_PAGES)
def test_source_navigation_page_is_in_site_navigation(relative_path: str) -> None:
    site_configuration = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert relative_path in site_configuration


@pytest.mark.parametrize("relative_path", REQUIRED_EXAMPLE_RECIPE_PAGES)
def test_required_example_recipe_exists(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", REQUIRED_EXAMPLE_RECIPE_PAGES)
def test_example_recipe_is_in_site_navigation(relative_path: str) -> None:
    site_configuration = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert relative_path in site_configuration


@pytest.mark.parametrize("relative_path", SOURCE_NAVIGATION_HOTSPOTS)
def test_source_navigation_hotspot_exists(relative_path: str) -> None:
    assert (ROOT / relative_path).exists()


@pytest.mark.parametrize("relative_path", SOURCE_NAVIGATION_HOTSPOTS)
def test_source_navigation_mentions_hotspot(relative_path: str) -> None:
    assert relative_path in _combined_text(SOURCE_NAVIGATION_CORPUS)


@pytest.mark.parametrize("relative_path", SOURCE_NAVIGATION_PUBLIC_DOCS)
def test_source_navigation_public_doc_exists(relative_path: str) -> None:
    assert (ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", SOURCE_NAVIGATION_PUBLIC_DOCS)
def test_source_navigation_mentions_public_doc(relative_path: str) -> None:
    assert relative_path in _combined_text(SOURCE_NAVIGATION_CORPUS)


@pytest.mark.parametrize("relative_path", SOURCE_NAVIGATION_TEST_TARGETS)
def test_source_navigation_test_target_exists(relative_path: str) -> None:
    assert (ROOT / relative_path).exists()


@pytest.mark.parametrize("relative_path", SOURCE_NAVIGATION_TEST_TARGETS)
def test_source_navigation_mentions_test_target(relative_path: str) -> None:
    assert relative_path in _combined_text(SOURCE_NAVIGATION_CORPUS)


@pytest.mark.parametrize("relative_path", PACKAGE_READMES)
def test_package_readme_links_to_source_navigation(relative_path: str) -> None:
    content = (ROOT / relative_path).read_text(encoding="utf-8")
    for reference in PACKAGE_README_NAVIGATION_REFERENCES:
        assert reference in content


@pytest.mark.parametrize("relative_path", PACKAGE_READMES)
def test_package_readme_does_not_use_legacy_active_doc_paths(relative_path: str) -> None:
    content = (ROOT / relative_path).read_text(encoding="utf-8")
    for reference in LEGACY_ACTIVE_DOC_REFERENCES:
        assert reference not in content


def test_feature_matrix_has_rows_and_status_groups() -> None:
    assert FEATURE_MATRIX_ROWS
    statuses = {row["Status"] for row in FEATURE_MATRIX_ROWS}
    assert {"Supported", "Partially supported", "Unsupported", "Planned", "Not implemented"} <= statuses


@pytest.mark.parametrize("feature", FEATURE_MATRIX_REQUIRED_FEATURES)
def test_feature_matrix_includes_required_feature(feature: str) -> None:
    matrix_features = {row["Feature"] for row in FEATURE_MATRIX_ROWS}
    assert feature in matrix_features


@pytest.mark.parametrize("row", FEATURE_MATRIX_ROWS, ids=lambda row: row["Feature"])
def test_feature_matrix_row_is_complete(row: dict[str, str]) -> None:
    assert row["Status"] in FEATURE_MATRIX_STATUSES
    assert "TODO" not in " ".join(row.values())
    for column in ["Feature", "Status", "User docs", "Source owner", "Evidence", "Limitations"]:
        assert row[column]
    for column in ["User docs", "Source owner", "Evidence"]:
        assert MARKDOWN_LINK.search(row[column]), f"{row['Feature']}: {column} must contain a Markdown link"
    if row["Status"] in {"Supported", "Partially supported"}:
        assert "](../../tests/" in row["Evidence"], f"{row['Feature']}: support claims need direct test evidence"


@pytest.mark.parametrize("row", FEATURE_MATRIX_ROWS, ids=lambda row: row["Feature"])
def test_feature_matrix_links_point_to_existing_files(row: dict[str, str]) -> None:
    for column in ["User docs", "Source owner", "Evidence"]:
        for target in MARKDOWN_LINK.findall(row[column]):
            if target.startswith(("http://", "https://")):
                continue
            resolved_target = (FEATURE_MATRIX_PATH.parent / target).resolve()
            assert resolved_target.exists(), f"{row['Feature']}: {column} link target does not exist: {target}"


@pytest.mark.parametrize("package", MAJOR_SOURCE_PACKAGES)
def test_source_map_covers_major_source_packages(package: str) -> None:
    source_map = (DOCS_ROOT / "developer-guide/source-map.md").read_text(encoding="utf-8")
    assert package in source_map


@pytest.mark.parametrize("relative_path", PACKAGE_READMES)
def test_major_source_package_has_local_readme(relative_path: str) -> None:
    assert (ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", ARCHIVED_OLD_DOCS)
def test_old_documentation_is_archived(relative_path: str) -> None:
    assert (DOCS_ROOT / relative_path).is_file()


@pytest.mark.parametrize("relative_path", OLD_TOP_LEVEL_DOCS)
def test_old_top_level_documentation_was_moved(relative_path: str) -> None:
    assert not (DOCS_ROOT / relative_path).exists()


def test_static_site_seed_configuration_exists() -> None:
    assert (ROOT / "mkdocs.yml").is_file()
