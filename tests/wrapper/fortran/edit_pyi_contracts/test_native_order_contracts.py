"""Editable contracts that expose native argument order without @native_call."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

NATIVE_CALL_EXAMPLES_F90_SOURCE = wrapper_source("fnative_call_examples_f90.f90")
MODIFIED_CONTRACT = Path(__file__).parent / "modified_contracts" / "fnative_call_examples_native_order" / "__init__.pyi"


def test_editable_contract_can_use_native_order_arguments_without_native_call(tmp_path: Path):
    contract_text = MODIFIED_CONTRACT.parent.joinpath("fnative_call_examples_f90.pyi").read_text(encoding="utf-8")
    assert "@native_call" not in contract_text

    native_object = _compile_native_object(NATIVE_CALL_EXAMPLES_F90_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        MODIFIED_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    status = np.empty((), dtype=np.int32)
    assert module.scalar_status(np.int32(4), status) is None
    assert status[()] == np.int32(15)

    vector = np.empty(4, dtype=np.float64)
    assert module.fill_vector(np.int32(4), vector) is None
    np.testing.assert_allclose(vector, np.array([1.5, 3.0, 4.5, 6.0], dtype=np.float64))

    matrix = np.array([[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]], dtype=np.float64, order="F")
    shifted = np.empty((2, 3), dtype=np.float64, order="F")
    assert module.shift_matrix(np.int32(2), np.int32(3), matrix, shifted) is None
    np.testing.assert_allclose(shifted, matrix + 10.0)

    inout = np.array([2.0, 5.0, 7.0], dtype=np.float64)
    scale_status = np.empty((), dtype=np.int32)
    assert module.scale_with_status(inout, scale_status) is None
    assert scale_status[()] == np.int32(3)
    np.testing.assert_allclose(inout, np.array([4.0, 10.0, 14.0], dtype=np.float64))

    assert module.fixed_inout("abc     ") is None
    assert module.make_label("      ") is None

    mixed_values = np.empty(3, dtype=np.float64)
    mixed_status = np.empty((), dtype=np.int32)
    assert module.summarize_mixed(np.int32(3), mixed_values, mixed_status, "      ") == np.float64(3.75)
    assert mixed_status[()] == np.int32(23)
    np.testing.assert_allclose(mixed_values, np.array([11.0, 12.0, 13.0], dtype=np.float64))

    point = module.summary_point()
    assert module.make_point(np.int32(7), point) is None
    assert point.total == np.float64(7.5)
    assert point.code == np.int32(107)
