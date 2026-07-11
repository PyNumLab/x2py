"""Phase 0B boundary tests for the isolated wrapper-codegen package."""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path

from tests.wrapper.fortran._support import REPO_ROOT
from x2py.pipeline.wrapper_artifacts import GeneratedWrapperArtifacts
from x2py.wrapper_codegen.checks import (
    WrapperCodegenCheckConfig,
    check_wrapper_codegen_package,
    check_wrapper_codegen_paths,
)

SOURCE_ROOT = REPO_ROOT / "x2py"
WRAPPER_CODEGEN_ROOT = SOURCE_ROOT / "wrapper_codegen"
LEGACY_CODEGEN_ROOT = SOURCE_ROOT / "codegen"


def _python_modules(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _imports_under(imports: set[str], package: str) -> bool:
    return any(name == package or name.startswith(f"{package}.") for name in imports)


def _write_module(root: Path, relative_path: str, source: str) -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def _check_source(tmp_path: Path, source: str, *, filename: str = "bad.py") -> set[str]:
    path = _write_module(tmp_path, filename, source)
    violations = check_wrapper_codegen_paths(
        [path],
        package_root=tmp_path,
        config=WrapperCodegenCheckConfig(max_complexity=3, max_statements=4, max_nesting=2),
    )
    return {violation.code for violation in violations}


def test_wrapper_codegen_and_legacy_codegen_do_not_import_each_other():
    wrapper_codegen_imports = {path: _imported_modules(path) for path in _python_modules(WRAPPER_CODEGEN_ROOT)}
    wrapper_codegen_violations = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path, imports in wrapper_codegen_imports.items()
        if _imports_under(imports, "x2py.codegen")
    )
    assert wrapper_codegen_violations == []

    legacy_codegen_imports = {path: _imported_modules(path) for path in _python_modules(LEGACY_CODEGEN_ROOT)}
    legacy_codegen_violations = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path, imports in legacy_codegen_imports.items()
        if _imports_under(imports, "x2py.wrapper_codegen")
    )
    assert legacy_codegen_violations == []


def test_only_pipeline_modules_may_import_both_wrapper_routes():
    modules_importing_both = []
    for path in _python_modules(SOURCE_ROOT):
        imports = _imported_modules(path)
        if _imports_under(imports, "x2py.codegen") and _imports_under(imports, "x2py.wrapper_codegen"):
            modules_importing_both.append(path.relative_to(SOURCE_ROOT).as_posix())

    outside_pipeline = sorted(path for path in modules_importing_both if not path.startswith("pipeline/"))
    assert outside_pipeline == []


def test_wrapper_codegen_package_static_contracts_pass():
    assert check_wrapper_codegen_package(WRAPPER_CODEGEN_ROOT) == ()


def test_checker_rejects_legacy_codegen_imports(tmp_path: Path):
    codes = _check_source(tmp_path, "import x2py.codegen\n")

    assert "legacy-codegen-import" in codes


def test_checker_rejects_module_level_production_functions(tmp_path: Path):
    codes = _check_source(tmp_path, "def build_plan():\n    return None\n")

    assert "module-function" in codes


def test_checker_requires_visitor_based_production_classes(tmp_path: Path):
    codes = _check_source(tmp_path, "class WrapperPlanner:\n    pass\n")

    assert "visitor-class" in codes


def test_checker_enforces_complexity_statement_and_nesting_limits(tmp_path: Path):
    codes = _check_source(
        tmp_path,
        """
def oversized(value):
    first = value + 1
    second = first + 1
    third = second + 1
    fourth = third + 1
    if value:
        if first:
            if second:
                return third
    if value == 1:
        return first
    if value == 2:
        return second
    if value == 3:
        return third
    return fourth
""",
    )

    assert {"complexity", "statement-count", "nesting-depth"} <= codes


def test_checker_rejects_missing_primary_and_secondary_registry_handlers(tmp_path: Path):
    codes = _check_source(
        tmp_path,
        """
from x2py.wrapper_codegen import ClassVisitor

class DemoEmitter(ClassVisitor):
    PRIMARY_REGISTRY = {"scalar": "_emit_scalar"}
    SECONDARY_DISPATCHER = {"scalar": {"value": "_emit_scalar_value"}}
""",
    )

    assert "registry-missing-handler" in codes


def test_checker_rejects_printer_calls_from_handlers(tmp_path: Path):
    codes = _check_source(
        tmp_path,
        """
from x2py.wrapper_codegen import ClassVisitor

class DemoEmitter(ClassVisitor):
    HANDLER_REGISTRY = {"scalar": "_emit_scalar"}

    def _emit_scalar(self, node):
        return self.printer.doprint(node)
""",
    )

    assert "handler-printer-call" in codes


def test_generated_wrapper_artifacts_keep_compile_and_link_ownership_out_of_the_handoff():
    artifacts = GeneratedWrapperArtifacts(
        module_name="demo",
        bridge_sources=(Path("bind_c_demo.f90"),),
        binding_sources=(Path("demo.c"),),
        header_files=(Path("demo.h"),),
        runtime_support_keys=("python_runtime",),
    )

    assert artifacts.source_files == (Path("bind_c_demo.f90"), Path("demo.c"))
    assert artifacts.generated_files == (Path("bind_c_demo.f90"), Path("demo.c"), Path("demo.h"))
    assert {field.name for field in fields(GeneratedWrapperArtifacts)} == {
        "module_name",
        "bridge_sources",
        "binding_sources",
        "header_files",
        "runtime_support_keys",
    }
