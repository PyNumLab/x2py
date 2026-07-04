"""Verbose direct-build and default output-location tests."""

import importlib
import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import _assert_fmath_examples, _sole_native_module, wrapper_source
from x2py.compiling.basic import CompileObj
from x2py.preprocessing import PreprocessingConfig
from x2py.wrapping import NativeBuildPlan, NativeLinkItem, build_fortran_extension

VERBOSE_SOURCE = wrapper_source("verbose_api.f90")
DEFAULT_OUTPUT_SOURCE = wrapper_source("fdefault_output.f")
SCALE_SOURCE = wrapper_source("scale.f90")
SCALAR_SOURCE = wrapper_source("fmath.f")


def test_verbose_mode_prints_full_direct_build_commands(tmp_path: Path):
    source = tmp_path / "verbose_api.f90"
    shutil.copyfile(VERBOSE_SOURCE, source)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--verbose",
            "--out-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    command_lines = result.stdout.splitlines()

    assert any(str(source) in line and "-c" in line for line in command_lines)
    assert any("bind_c_verbose_api_wrapper.f90" in line and "-c" in line for line in command_lines)
    assert any("verbose_api_wrapper.c" in line and "-c" in line for line in command_lines)
    c_wrapper_command = next(line for line in command_lines if "verbose_api_wrapper.c" in line and "-c" in line)
    c_wrapper_parts = shlex.split(c_wrapper_command)
    assert "-O3" in c_wrapper_parts
    assert "-DNDEBUG" in c_wrapper_parts
    assert "-g" not in c_wrapper_parts
    assert any("-shared" in line and "verbose_api" in line for line in command_lines)
    assert any(line.startswith(">> Command completed in ") for line in command_lines)
    assert any(line.startswith(">> Timing :: Wrapper creation: ") for line in command_lines)
    assert any(line.startswith(">> Timing :: Wrapper printing: ") for line in command_lines)
    assert any(line.startswith(">> Timing :: Wrapper compilation: ") for line in command_lines)
    assert "Built extension:" in result.stdout


def test_verbose_mode_prints_custom_wrapper_flags(tmp_path: Path):
    source = tmp_path / SCALE_SOURCE.name
    shutil.copyfile(SCALE_SOURCE, source)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--out",
            "SCALE_debug",
            "--out-dir",
            str(tmp_path / "build" / "SCALE_debug"),
            "--verbose",
            "--compiler",
            "gfortran",
            "--wrapper-fortran-flags=-O2",
            "--wrapper-c-flags=-O2",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    command_lines = result.stdout.splitlines()

    fortran_wrapper_command = next(
        line for line in command_lines if "bind_c_SCALE_debug_wrapper.f90" in line and "-c" in line
    )
    c_wrapper_command = next(line for line in command_lines if "SCALE_debug_wrapper.c" in line and "-c" in line)
    link_command = next(line for line in command_lines if "-shared" in line and "SCALE_debug" in line)
    assert "-O2" in shlex.split(fortran_wrapper_command)
    assert "-O2" in shlex.split(c_wrapper_command)
    assert "-O2" in shlex.split(link_command)


def test_fortran_wrapper_default_places_extension_beside_source(tmp_path: Path):
    source = tmp_path / DEFAULT_OUTPUT_SOURCE.name
    shutil.copyfile(DEFAULT_OUTPUT_SOURCE, source)

    cmd = [sys.executable, "-m", "x2py", str(source), "--json"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)

    build_dir = tmp_path / "__x2py__"
    shared_library = Path(payload["shared_library"])
    assert shared_library.parent == tmp_path
    assert shared_library.name == "fdefault_output.so"
    assert shared_library.exists()
    assert Path(payload["output_dir"]) == build_dir
    assert (build_dir / "bind_c_fdefault_output_wrapper.f90").exists()
    assert not list(tmp_path.glob("*_wrapper.c"))


def test_fortran_wrapper_default_module_name_does_not_collide_with_root_function(tmp_path: Path):
    source = tmp_path / SCALE_SOURCE.name
    shutil.copyfile(SCALE_SOURCE, source)

    result = subprocess.run(
        [sys.executable, "-m", "x2py", str(source), "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    shared_library = Path(payload["shared_library"])
    assert payload["module_name"] == "scale"
    assert shared_library.parent == tmp_path
    assert shared_library.name == "scale.so"
    assert shared_library.exists()

    sys.modules.pop("scale", None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module("scale")
    finally:
        sys.path.remove(str(tmp_path))
    assert module.scale(np.float64(3.0), np.float64(2.5)) == np.float64(7.5)


def test_fortran_wrapper_out_names_importable_shared_library(tmp_path: Path):
    source = tmp_path / SCALE_SOURCE.name
    output_name = tmp_path / "SCALE"
    shutil.copyfile(SCALE_SOURCE, source)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "x2py",
            str(source),
            "--out",
            str(output_name),
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)

    shared_library = Path(payload["shared_library"])
    assert shared_library == output_name.with_suffix(".so")
    assert shared_library.is_file()
    assert payload["module_name"] == "SCALE"
    assert any(path.name.startswith("SCALE.") and path.suffix == ".so" for path in tmp_path.iterdir())
    assert str(shared_library) in payload["generated_files"]

    sys.modules.pop("SCALE", None)
    sys.path.insert(0, str(tmp_path))
    try:
        module = importlib.import_module("SCALE")
    finally:
        sys.path.remove(str(tmp_path))
    assert module.scale(np.float64(3.0), np.float64(2.5)) == np.float64(7.5)


def test_internal_preprocessing_mode_still_builds_importable_runtime_wrapper(tmp_path: Path):
    source = tmp_path / SCALAR_SOURCE.name
    build_dir = tmp_path / "build"
    shutil.copyfile(SCALAR_SOURCE, source)

    result = build_fortran_extension(
        source,
        output_dir=build_dir,
        preprocessing=PreprocessingConfig(),
    )

    assert result.compiled is True
    assert result.build_makefile is None
    assert any(
        path.name == "python_runtime.c" and path.parent.name == "x2py_runtime" for path in result.generated_files
    )

    sys.modules.pop(result.module_name, None)
    sys.path.insert(0, str(build_dir))
    try:
        module = _sole_native_module(importlib.import_module(result.module_name))
    finally:
        sys.path.remove(str(build_dir))
    _assert_fmath_examples(module)


def test_source_build_result_records_structured_native_plan(tmp_path: Path):
    source = tmp_path / SCALAR_SOURCE.name
    shutil.copyfile(SCALAR_SOURCE, source)

    result = build_fortran_extension(source, output_dir=tmp_path)

    plan = result.native_build_plan
    object_path = tmp_path / "fmath.o"
    assert isinstance(plan, NativeBuildPlan)
    assert result.to_dict()["native_build_plan"] == plan.to_dict()
    assert plan.compilation_units[0].source == source
    assert plan.compilation_units[0].object_path == object_path
    assert plan.compilation_units[0].language == "fortran"
    assert plan.produced_objects == (object_path,)
    assert plan.prebuilt_artifacts == ()
    assert plan.module_dirs == (tmp_path,)
    assert plan.include_dirs == (tmp_path,)
    assert plan.link_items == (NativeLinkItem("object", object_path),)
    assert "native_inputs" not in result.to_dict()


def test_native_link_plan_serializes_interleaved_item_kinds():
    plan = NativeBuildPlan(
        link_items=(
            NativeLinkItem("object", Path("objects/entry.o")),
            NativeLinkItem("linker_argument", "-Wl,--start-group"),
            NativeLinkItem("archive", Path("lib/libsolver.a")),
            NativeLinkItem("shared_library", Path("lib/libsupport.so")),
            NativeLinkItem("named_library", "lapack"),
            NativeLinkItem("linker_argument", "-Wl,--end-group"),
        )
    )

    assert plan.to_dict()["link_items"] == [
        {"kind": "object", "path": "objects/entry.o"},
        {"kind": "linker_argument", "argument": "-Wl,--start-group"},
        {"kind": "archive", "path": "lib/libsolver.a"},
        {"kind": "shared_library", "path": "lib/libsupport.so"},
        {"kind": "named_library", "name": "lapack"},
        {"kind": "linker_argument", "argument": "-Wl,--end-group"},
    ]


def test_compile_object_dependency_modules_keep_caller_order(tmp_path: Path):
    first = CompileObj("first.f90", tmp_path)
    archive = CompileObj("libsolver.a", tmp_path)
    shared = CompileObj("libsupport.so", tmp_path)
    main = CompileObj("wrapper.c", tmp_path, dependencies=(first, archive, shared))

    assert main.extra_modules == (
        first.module_target,
        archive.module_target,
        shared.module_target,
    )


def test_wrapper_build_rejects_empty_source_list(tmp_path: Path):
    with pytest.raises(ValueError, match="at least one Fortran source"):
        build_fortran_extension([], output_dir=tmp_path)


def test_wrapper_build_rejects_missing_source(tmp_path: Path):
    missing = tmp_path / "missing.f90"

    with pytest.raises(FileNotFoundError, match="Fortran source not found"):
        build_fortran_extension(missing, output_dir=tmp_path)


def test_wrapper_build_rejects_makefile_verbose_combination(tmp_path: Path):
    source = tmp_path / DEFAULT_OUTPUT_SOURCE.name
    shutil.copyfile(DEFAULT_OUTPUT_SOURCE, source)

    with pytest.raises(ValueError, match="makefile generation and verbose direct compilation"):
        build_fortran_extension(source, output_dir=tmp_path, makefile=True, verbose=True)
