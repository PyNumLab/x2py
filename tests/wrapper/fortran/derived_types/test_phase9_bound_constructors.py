"""Direct Phase 9 proof for explicit constructor bindings."""

from pathlib import Path

import numpy as np
from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension
from x2py.pipeline import build as build_pipeline

SOURCE = wrapper_source("fclasses_f90.f90")
CONTRACT = Path(__file__).parent / "contracts" / "fbound_constructor_phase9" / "__init__.pyi"


def test_bound_constructor_replaces_field_initialization_and_reuses_method_plan(
    tmp_path: Path,
    monkeypatch,
):
    native_object = _compile_native_object(SOURCE, tmp_path / "native")

    def fail_legacy_lowering(*_args, **_kwargs):
        raise AssertionError("eligible Phase 9 contract must not invoke semantic_ir_to_codegen_ast")

    monkeypatch.setattr(build_pipeline, "semantic_ir_to_codegen_ast", fail_legacy_lowering)
    result = build_pyi_extension(
        CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "wrapper_plan",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    value = module.vector(np.float64(2.0), np.float64(3.0))
    assert (value.x, value.y) == (np.float64(2.0), np.float64(3.0))
    value.shift(np.float64(1.0), np.float64(-1.0))
    assert (value.x, value.y) == (np.float64(3.0), np.float64(2.0))
