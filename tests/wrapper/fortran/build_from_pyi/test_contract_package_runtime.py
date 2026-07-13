"""Source-free `.pyi` contract package runtime tests."""

from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from x2py import build_fortran_extension, build_pyi_extension

from tests._shared.fixture_outputs import PYI_WRAPPER_CONTRACT_FIXTURE_DIR
from tests._shared.pyi_fixture_packages import assert_generated_pyi_package_matches_fixture
from tests.wrapper.fortran._support import REPO_ROOT

GENERAL_FORTRAN_DATA = REPO_ROOT / "tests" / "data" / "fortran" / "general"
SOURCE_NAMESPACE = GENERAL_FORTRAN_DATA / "contract_mixed_module_external.f90"
STANDALONE_ONLY = GENERAL_FORTRAN_DATA / "contract_standalone_only.f90"
SAME_NAME_MIXED = GENERAL_FORTRAN_DATA / "contract_same_name.f90"
TRANSITIVE_NATIVE = GENERAL_FORTRAN_DATA / "contract_import_graph.f90"
MULTI_MODULE = GENERAL_FORTRAN_DATA / "contract_multi_module.f90"


def _compiler() -> str:
    compiler = shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is required for contract package runtime tests")
    return compiler


def _copy_source(source_template: Path, workdir: Path) -> Path:
    source = workdir / source_template.name
    source.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_template, source)
    return source


def _compile_native(source: Path, workdir: Path) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    native_object = workdir / f"{source.stem}.o"
    subprocess.run(
        [
            _compiler(),
            "-fPIC",
            "-c",
            str(source),
            "-o",
            str(native_object),
            "-J",
            str(workdir),
        ],
        check=True,
    )
    return native_object


def _generate_contract_package(source: Path, output_parent: Path) -> Path:
    package = output_parent / source.stem
    subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--pyi",
            "--out",
            str(package),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert_generated_pyi_package_matches_fixture(
        package,
        PYI_WRAPPER_CONTRACT_FIXTURE_DIR / source.stem / "generated",
    )
    return package / "__init__.pyi"


def _run_json(command: list[str], *, cwd: Path | None = None) -> dict[str, object]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def _import_extension(module_name: str, build_dir: Path):
    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(build_dir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(build_dir))


def _build_contract(
    entry: Path | str,
    native_object: Path,
    build_dir: Path,
    *,
    cwd: Path | None = None,
    output_name: str | None = None,
):
    command = [
        sys.executable,
        "-m",
        "x2py",
        str(entry),
        "--wrap",
        "--native-objects",
        str(native_object),
        "--native-include-dir",
        str(native_object.parent),
        "--out-dir",
        str(build_dir),
        "--json",
    ]
    if output_name is not None:
        command.extend(("--out", output_name))
    payload = _run_json(command, cwd=cwd)
    module = _import_extension(str(payload["module_name"]), build_dir)
    return module, payload


def _assert_general_source_surface(source: Path, module) -> None:
    """Assert the public hierarchy and calls of one complete general fixture."""
    if source == SOURCE_NAMESPACE:
        assert not hasattr(module, "module_increment")
        assert module.contract_math_mod.module_increment(np.int32(4)) == np.int32(5)
        assert module.external_double(np.int32(4)) == np.int32(8)
    elif source == TRANSITIVE_NATIVE:
        assert not hasattr(module, "func")
        assert not hasattr(module, "deep_func")
        assert module.m1.func(np.int32(2)) == np.int32(3)
        assert module.deep.deep_func(np.int32(3)) == np.int32(6)
    elif source == MULTI_MODULE:
        assert not hasattr(module, "shared_value")
        assert module.contract_left_mod.shared_value(np.int32(3)) == np.int32(4)
        assert module.contract_right_mod.shared_value(np.int32(3)) == np.int32(6)
    elif source == STANDALONE_ONLY:
        assert module.standalone_ping() is None
        assert module.standalone_double(np.int32(4)) == np.int32(8)
    else:
        assert source == SAME_NAME_MIXED
        assert not hasattr(module, "module_ping")
        assert module.external_ping() is None
        assert module.contract_same_name.module_ping() is None


@pytest.mark.parametrize(
    ("route", "route_options"),
    [
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ],
)
@pytest.mark.parametrize(
    "source",
    [SOURCE_NAMESPACE, TRANSITIVE_NATIVE, MULTI_MODULE, STANDALONE_ONLY, SAME_NAME_MIXED],
    ids=lambda path: path.stem,
)
def test_complete_general_source_preserves_namespaces_through_both_routes(
    tmp_path: Path,
    source: Path,
    route: str,
    route_options: dict[str, bool],
):
    result = build_fortran_extension(source, output_dir=tmp_path / route, **route_options)
    module = _import_extension(result.module_name, result.output_dir)

    _assert_general_source_surface(source, module)


def test_source_build_preserves_modules_and_root_externals(tmp_path: Path):
    source = _copy_source(SOURCE_NAMESPACE, tmp_path)
    build_dir = tmp_path / "source_build"
    payload = _run_json(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--wrap",
            "--out-dir",
            str(build_dir),
            "--json",
        ]
    )
    module = _import_extension("contract_mixed_module_external", build_dir)

    assert payload["module_name"] == "contract_mixed_module_external"
    assert not hasattr(module, "module_increment")
    assert module.contract_math_mod.module_increment(np.int32(4)) == np.int32(5)
    assert module.external_double(np.int32(4)) == np.int32(8)


def test_init_entry_uses_resolved_parent_name_from_inside_package(tmp_path: Path):
    source = _copy_source(SAME_NAME_MIXED, tmp_path)
    entry = _generate_contract_package(source, tmp_path / "contracts")
    native_object = _compile_native(source, tmp_path / "native")
    build_dir = tmp_path / "build"

    module, payload = _build_contract(
        "__init__.pyi",
        native_object,
        build_dir,
        cwd=entry.parent,
    )

    assert payload["module_name"] == "contract_same_name"
    assert Path(str(payload["shared_library"])).name.startswith("contract_same_name.")
    assert module.external_ping() is None
    assert module.contract_same_name.module_ping() is None


def test_output_name_override_replaces_entry_inference(tmp_path: Path):
    source = _copy_source(STANDALONE_ONLY, tmp_path)
    entry = _generate_contract_package(source, tmp_path / "contracts")
    native_object = _compile_native(source, tmp_path / "native")

    module, payload = _build_contract(
        entry,
        native_object,
        tmp_path / "build",
        output_name="custom_api",
    )

    assert payload["module_name"] == "custom_api"
    assert Path(str(payload["shared_library"])).name.startswith("custom_api.")
    assert module.standalone_ping() is None


def test_recursive_graph_preserves_module_and_symbol_aliases_and_ignores_support_imports(tmp_path: Path):
    source = _copy_source(TRANSITIVE_NATIVE, tmp_path)
    native_object = _compile_native(source, tmp_path / "native")
    entry = _generate_contract_package(source, tmp_path / "contracts")
    package = entry.parent
    nested = package / "nested"
    nested.mkdir(parents=True)
    entry.write_text(
        "from types import SimpleNamespace\n"
        "from x2py.contracts import Callable\n"
        "from . import facade as m2\n"
        "from .m1 import func as f\n",
        encoding="utf-8",
    )
    (package / "facade.pyi").write_text("from .nested import deep as branch\n", encoding="utf-8")
    (nested / "__init__.pyi").write_text("from . import deep\n", encoding="utf-8")
    deep_leaf = package / "deep.pyi"
    (nested / "deep.pyi").write_text(deep_leaf.read_text(encoding="utf-8"), encoding="utf-8")
    deep_leaf.unlink()

    module, payload = _build_contract(entry, native_object, tmp_path / "build")

    assert payload["sources"] == [
        str(entry),
        str(package / "facade.pyi"),
        str(package / "m1.pyi"),
        str(nested / "__init__.pyi"),
        str(nested / "deep.pyi"),
    ]
    assert not hasattr(module, "facade")
    assert not hasattr(module, "m1")
    assert not hasattr(module, "func")
    assert not hasattr(module, "SimpleNamespace")
    assert not hasattr(module, "Callable")
    assert module.f(np.int32(2)) == np.int32(3)
    assert module.m2.branch.deep_func(np.int32(3)) == np.int32(6)

    plan_result = build_pyi_extension(
        entry,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "plan_build",
        _force_wrapper_plan_route=True,
    )
    plan_module = _import_extension(plan_result.module_name, plan_result.output_dir)
    assert not hasattr(plan_module, "facade")
    assert not hasattr(plan_module, "m1")
    assert not hasattr(plan_module, "func")
    assert plan_module.f(np.int32(2)) == np.int32(3)
    assert plan_module.m2.branch.deep_func(np.int32(3)) == np.int32(6)


def test_recursive_graph_reports_missing_relative_contract_before_native_validation(tmp_path: Path):
    entry = tmp_path / "api.pyi"
    entry.write_text("from . import missing\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match=r"missing\.pyi"):
        build_pyi_extension(entry, native_objects=[tmp_path / "unused.o"])


def test_recursive_graph_reports_cycles_before_codegen(tmp_path: Path):
    entry = tmp_path / "api.pyi"
    dependency = tmp_path / "dependency.pyi"
    entry.write_text("from . import dependency\n", encoding="utf-8")
    dependency.write_text("from . import api\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Cyclic relative \.pyi export imports"):
        build_pyi_extension(entry, native_objects=[tmp_path / "unused.o"])
