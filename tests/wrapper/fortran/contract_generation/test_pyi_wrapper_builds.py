"""Semantic .pyi driven wrapper build tests."""

import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest

from x2py import build_pyi_extension
from x2py.wrapping import build_fortran_extension
from tests.wrapper.fortran._support import REPO_ROOT, wrapper_source

SOURCE = wrapper_source("fruntime_abi_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"
PYI_FIXTURE = CONTRACT_FIXTURES / "runtime_abi" / "generated" / "fruntime_abi_f90.pyi"
INVALID_NATIVE_CALL_PYI = CONTRACT_FIXTURES / "projection_metadata" / "invalid" / "incomplete_native_call.pyi"
MODIFIED_BASIC_CONTRACTS = CONTRACT_FIXTURES / "basic_subroutine" / "modified"
BASIC_SOURCE = REPO_ROOT / "tests" / "data" / "fortran" / "general" / "basic_subroutine.f90"
MODULE_VARIABLE_SOURCE = wrapper_source("fmodule_vars_f90.f90")
MIXED_SOURCE = """\
module m1
contains
subroutine add1(n, x)
  integer, intent(in) :: n
  real(kind=8), intent(inout), dimension(n) :: x
  x = x + 1.0d0
end subroutine add1
end module m1

subroutine func()
end subroutine func
"""
MULTI_MODULE_SOURCE = """\
module first_mod
contains
subroutine shared_call()
end subroutine shared_call
end module first_mod

module second_mod
contains
subroutine shared_call()
end subroutine shared_call
end module second_mod
"""


def _compile_native_object(source: Path, workdir: Path) -> Path:
    compiler = shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is required to compile native .pyi wrapper test artifacts")

    workdir.mkdir(parents=True, exist_ok=True)
    native_source = workdir / source.name
    shutil.copyfile(source, native_source)
    native_object = workdir / f"{source.stem}.o"
    subprocess.run(
        [
            compiler,
            "-fPIC",
            "-c",
            str(native_source),
            "-o",
            str(native_object),
            "-J",
            str(workdir),
        ],
        check=True,
    )
    return native_object


def _import_from_build_dir(module_name: str, build_dir: Path):
    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(build_dir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(build_dir))


def _build_pyi_cli(pyi_path: Path, native_object: Path, build_dir: Path):
    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(pyi_path),
        "--wrap",
        "--native-object",
        str(native_object),
        "--native-include-dir",
        str(native_object.parent),
        "--out-dir",
        str(build_dir),
        "--json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    return _import_from_build_dir(payload["module_name"], build_dir), payload


def _generate_pyi(source: Path, output_parent: Path) -> Path:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--pyi",
            "--out",
            str(output_parent),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    package = output_parent / source.stem
    init_entry = package / "__init__.pyi"
    return init_entry if init_entry.is_file() else package / f"{source.stem}.pyi"


def _sole_native_module(module):
    children = [
        value
        for value in vars(module).values()
        if isinstance(value, ModuleType) and value.__name__.startswith(f"{module.__name__}.")
    ]
    return children[0] if len(children) == 1 else module


def _assert_scale_runtime_contract(module) -> None:
    assert module.scale(np.float64(2.0), np.float64(4.0)) == np.float64(8.0)


def _assert_module_variable_runtime_contract(module) -> None:
    assert module.counter == np.int32(3)
    module.counter = np.int32(9)
    assert module.counter == np.int32(9)
    assert module.summarize() == np.int32(21)
    assert not hasattr(module, "get_counter")
    assert not hasattr(module, "set_counter")


def _copy_modified_entry(generated_entry: Path, fixture_name: str) -> None:
    fixture = MODIFIED_BASIC_CONTRACTS / fixture_name
    text = fixture.read_text(encoding="utf-8")
    assert text.startswith("# Intentional difference:")
    generated_entry.write_text(text, encoding="utf-8")


@pytest.fixture
def scale_runtime_module(pyi_parity_build_mode: str, tmp_path: Path):
    if pyi_parity_build_mode == "source":
        result = build_fortran_extension(SOURCE, output_dir=tmp_path / "source_build")
        return _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    generated_pyi = _generate_pyi(SOURCE, tmp_path / "contracts")
    native_object = _compile_native_object(SOURCE, tmp_path / "native")
    module, _payload = _build_pyi_cli(generated_pyi, native_object, tmp_path / "pyi_build")
    return _sole_native_module(module)


@pytest.fixture
def module_variable_runtime_module(pyi_parity_build_mode: str, tmp_path: Path):
    if pyi_parity_build_mode == "source":
        result = build_fortran_extension(MODULE_VARIABLE_SOURCE, output_dir=tmp_path / "source_build")
        return _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    generated_pyi = _generate_pyi(MODULE_VARIABLE_SOURCE, tmp_path / "contracts")
    native_object = _compile_native_object(MODULE_VARIABLE_SOURCE, tmp_path / "native")
    module, _payload = _build_pyi_cli(generated_pyi, native_object, tmp_path / "pyi_build")
    return _sole_native_module(module)


def test_pyi_cli_requires_a_native_link_input(tmp_path: Path):
    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(PYI_FIXTURE), "--wrap", "--out-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "--wrap from .pyi requires --native-object or --native-library" in result.stderr


def test_pyi_cli_accepts_exactly_one_entry_contract(tmp_path: Path):
    other = tmp_path / "other.pyi"
    other.write_text("", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(PYI_FIXTURE),
            str(other),
            "--wrap",
            "--native-object",
            str(tmp_path / "unused.o"),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "--wrap from .pyi accepts exactly one entry contract" in result.stderr


def test_pyi_python_api_rejects_a_missing_native_artifact(tmp_path: Path):
    missing_object = tmp_path / "missing.o"

    with pytest.raises(FileNotFoundError, match=f"Native artifact not found: {missing_object}"):
        build_pyi_extension(PYI_FIXTURE, native_objects=[missing_object], output_dir=tmp_path / "build")


def test_pyi_python_api_rejects_python_suffix_as_semantic_contract(tmp_path: Path):
    contract = tmp_path / "modified_contract.py"
    contract.write_text("def scale(value: Float64) -> Float64: ...\n", encoding="utf-8")
    native_object = tmp_path / "native.o"
    native_object.touch()

    with pytest.raises(ValueError, match=r"\.pyi wrapper build expects one semantic contract file"):
        build_pyi_extension(contract, native_objects=[native_object], output_dir=tmp_path / "build")


def test_pyi_python_api_accepts_exactly_one_entry_contract(tmp_path: Path):
    with pytest.raises(TypeError, match="exactly one entry contract"):
        build_pyi_extension([PYI_FIXTURE], native_objects=[tmp_path / "unused.o"])


def test_pyi_python_api_rejects_invalid_projection_before_codegen(tmp_path: Path):
    native_object = tmp_path / "native.o"
    native_object.touch()

    with pytest.raises(ValueError, match="native_call argument position is out of range"):
        build_pyi_extension(INVALID_NATIVE_CALL_PYI, native_objects=[native_object], output_dir=tmp_path / "build")

    assert not list((tmp_path / "build").glob("*_wrapper.*"))


def test_generated_pyi_fixture_builds_from_native_object_without_source_reparse(tmp_path: Path):
    native_object = _compile_native_object(SOURCE, tmp_path / "native")
    module, payload = _build_pyi_cli(PYI_FIXTURE, native_object, tmp_path / "pyi_build")

    assert Path(payload["shared_library"]).is_file()
    assert payload["sources"] == [str(PYI_FIXTURE)]
    assert str(native_object) in payload["native_inputs"]
    assert module.scale(np.float64(2.0), np.float64(4.0)) == np.float64(8.0)


def test_generated_pyi_matches_checked_in_fixture(tmp_path: Path):
    entry = _generate_pyi(SOURCE, tmp_path / "contracts")
    generated_pyi = entry.parent / PYI_FIXTURE.name

    assert generated_pyi.read_text(encoding="utf-8") == PYI_FIXTURE.read_text(encoding="utf-8")


def test_source_named_root_discovers_and_builds_module_leaf(tmp_path: Path):
    root = _generate_pyi(BASIC_SOURCE, tmp_path / "contracts")
    leaf = root.parent / "m1.pyi"
    native_object = _compile_native_object(BASIC_SOURCE, tmp_path / "native")

    module, payload = _build_pyi_cli(root, native_object, tmp_path / "pyi_build")

    assert root.read_text(encoding="utf-8") == "from . import m1\n"
    assert leaf.is_file()
    assert payload["module_name"] == "basic_subroutine"
    assert payload["sources"] == [str(root), str(leaf)]
    assert not hasattr(module, "add1")
    values = np.array([1.0, 2.0], dtype=np.float64)
    module.m1.add1(np.int32(values.size), values)
    np.testing.assert_array_equal(values, np.array([1.0, 2.0], dtype=np.float64))


def test_entry_wildcard_import_explicitly_flattens_module_leaf(tmp_path: Path):
    root = _generate_pyi(BASIC_SOURCE, tmp_path / "contracts")
    _copy_modified_entry(root, "flatten_m1.pyi")
    native_object = _compile_native_object(BASIC_SOURCE, tmp_path / "native")

    module, _payload = _build_pyi_cli(root, native_object, tmp_path / "pyi_build")

    assert not hasattr(module, "m1")
    values = np.array([1.0, 2.0], dtype=np.float64)
    module.add1(np.int32(values.size), values)
    np.testing.assert_array_equal(values, np.array([1.0, 2.0], dtype=np.float64))


def test_entry_can_alias_one_module_procedure_at_the_root(tmp_path: Path):
    root = _generate_pyi(BASIC_SOURCE, tmp_path / "contracts")
    _copy_modified_entry(root, "alias_increment.pyi")
    native_object = _compile_native_object(BASIC_SOURCE, tmp_path / "native")

    module, _payload = _build_pyi_cli(root, native_object, tmp_path / "pyi_build")

    assert not hasattr(module, "m1")
    assert not hasattr(module, "add1")
    values = np.array([1.0, 2.0], dtype=np.float64)
    module.increment(np.int32(values.size), values)
    np.testing.assert_array_equal(values, np.array([1.0, 2.0], dtype=np.float64))


def test_entry_rejects_colliding_wildcard_exports(tmp_path: Path):
    entry = tmp_path / "api.pyi"
    first = tmp_path / "first.pyi"
    second = tmp_path / "second.pyi"
    entry.write_text("from .first import *\nfrom .second import *\n", encoding="utf-8")
    declaration = "def update(value: Int32) -> Int32: ...\n"
    first.write_text(declaration, encoding="utf-8")
    second.write_text(declaration, encoding="utf-8")

    with pytest.raises(ValueError, match="Conflicting .pyi exports for 'update'"):
        build_pyi_extension(entry, native_objects=[tmp_path / "unused.o"])


def test_module_leaf_can_be_the_entry_contract(tmp_path: Path):
    root = _generate_pyi(BASIC_SOURCE, tmp_path / "contracts")
    leaf = root.parent / "m1.pyi"
    native_object = _compile_native_object(BASIC_SOURCE, tmp_path / "native")

    module, payload = _build_pyi_cli(leaf, native_object, tmp_path / "pyi_build")

    assert payload["module_name"] == "m1"
    assert payload["sources"] == [str(leaf)]
    assert not hasattr(module, "m1")
    values = np.array([1.0, 2.0], dtype=np.float64)
    module.add1(np.int32(values.size), values)


def test_mixed_entry_exposes_externals_at_root_and_modules_as_children(tmp_path: Path):
    source = tmp_path / "mixed_api.f90"
    source.write_text(MIXED_SOURCE, encoding="utf-8")
    entry = _generate_pyi(source, tmp_path / "contracts")
    native_object = _compile_native_object(source, tmp_path / "native")

    module, payload = _build_pyi_cli(entry, native_object, tmp_path / "pyi_build")

    contract = entry.read_text(encoding="utf-8")
    assert "from . import m1" in contract
    assert "@external\ndef func() -> None: ..." in contract
    assert payload["sources"] == [str(entry), str(entry.parent / "m1.pyi")]
    assert module.func() is None
    values = np.array([1.0, 2.0], dtype=np.float64)
    module.m1.add1(np.int32(values.size), values)
    np.testing.assert_array_equal(values, np.array([2.0, 3.0], dtype=np.float64))


def test_one_entry_preserves_multiple_native_module_namespaces(tmp_path: Path):
    source = tmp_path / "multi_api.f90"
    source.write_text(MULTI_MODULE_SOURCE, encoding="utf-8")
    entry = _generate_pyi(source, tmp_path / "contracts")
    native_object = _compile_native_object(source, tmp_path / "native")

    module, payload = _build_pyi_cli(entry, native_object, tmp_path / "pyi_build")

    assert entry.read_text(encoding="utf-8") == "from . import first_mod\nfrom . import second_mod\n"
    assert payload["sources"] == [
        str(entry),
        str(entry.parent / "first_mod.pyi"),
        str(entry.parent / "second_mod.pyi"),
    ]
    assert not hasattr(module, "shared_call")
    assert module.first_mod.shared_call() is None
    assert module.second_mod.shared_call() is None


def test_scale_runtime_contract(scale_runtime_module):
    _assert_scale_runtime_contract(scale_runtime_module)


def test_module_variable_runtime_contract(module_variable_runtime_module):
    _assert_module_variable_runtime_contract(module_variable_runtime_module)
