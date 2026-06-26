"""Real BLAS/LAPACK compact external contract smoke tests."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests._shared.pyi_fixture_packages import assert_generated_pyi_package_matches_fixture
from tests.wrapper.fortran._support import wrapper_source
from x2py import build_pyi_extension

EXPECTED_CONTRACT_PACKAGE = Path(__file__).parent / "contracts" / "real_blas_lapack"
BLAS_FILENAMES = ("dasum.f", "daxpy.f", "ddot.f", "dscal.f")
LAPACK_FILENAMES = ("dlabad.f", "dlaed5.f", "dlamrg.f")
EXPECTED_ROUTINES = tuple(path.stem for path in map(Path, (*BLAS_FILENAMES, *LAPACK_FILENAMES)))
EXPECTED_NATIVE_ROUTINES = tuple(name.upper() for name in EXPECTED_ROUTINES)


def _compiler() -> str:
    compiler = shutil.which("gfortran")
    if compiler is None:
        pytest.skip("gfortran is required for real BLAS/LAPACK wrapper tests")
    return compiler


def _archiver() -> str:
    archiver = shutil.which("ar")
    if archiver is None:
        pytest.skip("ar is required for real BLAS/LAPACK archive wrapper tests")
    return archiver


def _copy_real_library_sources(workdir: Path) -> tuple[Path, ...]:
    source_root = workdir / "sources"
    sources = []
    for folder, filenames in (("blas", BLAS_FILENAMES), ("lapack", LAPACK_FILENAMES)):
        target_dir = source_root / folder
        target_dir.mkdir(parents=True, exist_ok=True)
        for filename in filenames:
            source = wrapper_source(filename)
            target = target_dir / filename
            shutil.copyfile(source, target)
            sources.append(target)
    return tuple(sources)


def _generate_contract(source_root: Path, package: Path) -> Path:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source_root),
            "--language",
            "fortran",
            "--pyi",
            "--out",
            str(package),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return package / "__init__.pyi"


def _compile_native_objects(sources: tuple[Path, ...], native_dir: Path) -> tuple[Path, ...]:
    native_dir.mkdir(parents=True, exist_ok=True)
    objects = []
    for source in sources:
        native_object = native_dir / f"{source.stem}.o"
        subprocess.run(
            [
                _compiler(),
                "-fPIC",
                "-c",
                str(source),
                "-o",
                str(native_object),
                "-J",
                str(native_dir),
                "-I",
                str(native_dir),
            ],
            check=True,
        )
        objects.append(native_object)
    return tuple(objects)


def _archive_objects(path: Path, objects: tuple[Path, ...]) -> Path:
    subprocess.run([_archiver(), "rcs", str(path), *(str(obj) for obj in objects)], check=True)
    return path


def _shared_library(path: Path, objects: tuple[Path, ...]) -> Path:
    subprocess.run(
        [_compiler(), "-shared", "-o", str(path), *(str(obj) for obj in objects)],
        capture_output=True,
        text=True,
        check=True,
    )
    return path


def _import_extension(module_name: str, build_dir: Path):
    sys.modules.pop(module_name, None)
    sys.path.insert(0, str(build_dir))
    try:
        return importlib.import_module(module_name)
    finally:
        sys.path.remove(str(build_dir))


@pytest.mark.parametrize("native_shape", ["objects", "archive", "shared_library", "named_library"])
def test_real_blas_lapack_folder_generates_compact_contract_and_importable_wrapper(
    tmp_path: Path,
    native_shape: str,
):
    sources = _copy_real_library_sources(tmp_path)
    entry = _generate_contract(tmp_path / "sources", tmp_path / "contracts")
    native_objects = _compile_native_objects(sources, tmp_path / "native")
    if native_shape == "objects":
        native_kwargs = {"native_objects": native_objects}
        expected_link_items = [{"kind": "object", "path": str(native_object)} for native_object in native_objects]
    elif native_shape == "archive":
        archive = _archive_objects(tmp_path / "native" / "libreal_blas_lapack.a", native_objects)
        native_kwargs = {"native_objects": [archive]}
        expected_link_items = [{"kind": "archive", "path": str(archive)}]
    elif native_shape == "shared_library":
        shared = _shared_library(tmp_path / "native" / "libreal_blas_lapack.so", native_objects)
        native_kwargs = {"native_objects": [shared]}
        expected_link_items = [{"kind": "shared_library", "path": str(shared)}]
    else:
        named = _shared_library(tmp_path / "native" / "libreal_blas_lapack.so", native_objects)
        native_kwargs = {
            "native_libraries": ["real_blas_lapack"],
            "native_library_dirs": [named.parent],
        }
        expected_link_items = [{"kind": "named_library", "name": "real_blas_lapack"}]

    result = build_pyi_extension(
        entry,
        extension_name="real_blas_lapack",
        output_dir=tmp_path / "build",
        **native_kwargs,
    )
    module = _import_extension(result.module_name, result.output_dir)

    generated_contracts = sorted(path.relative_to(entry.parent).as_posix() for path in entry.parent.rglob("*.pyi"))
    text = entry.read_text(encoding="utf-8")
    bridge = (result.output_dir / f"bind_c_{result.module_name}_wrapper.f90").read_text(encoding="utf-8").upper()

    assert_generated_pyi_package_matches_fixture(entry.parent, EXPECTED_CONTRACT_PACKAGE)
    assert generated_contracts == ["__init__.pyi"]
    assert text.count("@external") == len(EXPECTED_ROUTINES)
    assert text.count("@bind(") == len(EXPECTED_NATIVE_ROUTINES)
    assert "DX: Float64[Flat]" in text
    assert "DY: Float64[Flat]" in text
    assert "INDEX: Int32[Flat]" in text
    assert "REAL(F64), INTENT(INOUT) :: DX(*)" in bridge
    assert "REAL(F64), INTENT(INOUT) :: DY(*)" in bridge
    assert "INTEGER(I32), INTENT(INOUT) :: INDEX(*)" in bridge
    native_plan = result.native_build_plan.to_dict()
    assert native_plan["link_items"] == expected_link_items
    assert native_plan["compilation_units"] == []
    assert native_plan["module_dirs"] == []
    assert [name for name in EXPECTED_ROUTINES if hasattr(module, name)] == list(EXPECTED_ROUTINES)

    x = np.array([1.0, 2.0, 3.0], dtype=np.float64)
    y = np.array([10.0, 20.0, 30.0], dtype=np.float64)
    module.daxpy(np.int32(3), np.float64(2.0), x, np.int32(1), y, np.int32(1))
    np.testing.assert_allclose(y, [12.0, 24.0, 36.0])
    assert module.ddot(np.int32(3), x, np.int32(1), y, np.int32(1)) == np.float64(168.0)
    assert module.dasum(np.int32(3), y, np.int32(1)) == np.float64(72.0)

    index = np.zeros(5, dtype=np.int32)
    values = np.array([1.0, 4.0, 7.0, 2.0, 8.0], dtype=np.float64)
    module.dlamrg(np.int32(3), np.int32(2), values, np.int32(1), np.int32(1), index)
    np.testing.assert_array_equal(index, [1, 4, 2, 3, 5])
