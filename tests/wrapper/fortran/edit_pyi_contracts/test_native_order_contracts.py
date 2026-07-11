"""Editable contracts that expose native argument order without @native_call."""

import ctypes
from pathlib import Path

import numpy as np
import pytest

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

    base = np.array(4, dtype=np.int32)
    status = np.empty((), dtype=np.int32)
    assert module.scalar_status(base, status) is None
    assert status[()] == np.int32(15)
    with pytest.raises(TypeError, match=r"numpy.ndarray"):
        module.scalar_status(np.int32(4), status)

    raw_status = np.empty((), dtype=np.int32)
    assert module.scalar_status_raw(base.ctypes.data, raw_status.ctypes.data) is None
    assert raw_status[()] == np.int32(15)

    vector_size = np.array(4, dtype=np.int32)
    vector = np.empty(4, dtype=np.float64)
    assert module.fill_vector(vector_size, vector) is None
    np.testing.assert_allclose(vector, np.array([1.5, 3.0, 4.5, 6.0], dtype=np.float64))

    raw_vector = np.empty(4, dtype=np.float64)
    assert module.fill_vector_raw(vector_size, raw_vector.ctypes.data) is None
    np.testing.assert_allclose(raw_vector, np.array([1.5, 3.0, 4.5, 6.0], dtype=np.float64))
    with pytest.raises(TypeError):
        module.fill_vector_raw(vector_size, raw_vector)

    rows = np.array(2, dtype=np.int32)
    cols = np.array(3, dtype=np.int32)
    matrix = np.array([[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]], dtype=np.float64, order="F")
    shifted = np.empty((2, 3), dtype=np.float64, order="F")
    assert module.shift_matrix(rows, cols, matrix, shifted) is None
    np.testing.assert_allclose(shifted, matrix + 10.0)

    inout = np.array([2.0, 5.0, 7.0], dtype=np.float64)
    scale_status = np.empty((), dtype=np.int32)
    assert module.scale_with_status(inout, scale_status) is None
    assert scale_status[()] == np.int32(3)
    np.testing.assert_allclose(inout, np.array([4.0, 10.0, 14.0], dtype=np.float64))

    assert module.fixed_inout("abc     ") is None
    with pytest.raises(TypeError, match="exactly 8 bytes"):
        module.fixed_inout("abc")
    raw_label = ctypes.create_string_buffer(8)
    raw_label.raw = b"abc     "
    assert module.fixed_inout_raw(ctypes.addressof(raw_label)) is None
    assert raw_label.raw == b"Xbc    !"
    with pytest.raises(TypeError):
        module.fixed_inout_raw("abc     ")
    storage_label = np.array("abc     ", dtype="S8")
    assert module.fixed_inout_storage(storage_label) is None
    assert storage_label[()] == b"Xbc    !"
    with pytest.raises(TypeError, match="itemsize 8"):
        module.fixed_inout_storage(np.array("abc", dtype="S3"))
    assert module.make_label("      ") is None

    mixed_size = np.array(3, dtype=np.int32)
    mixed_values = np.empty(3, dtype=np.float64)
    mixed_status = np.empty((), dtype=np.int32)
    assert module.summarize_mixed(mixed_size, mixed_values, mixed_status, "      ") == np.float64(3.75)
    assert mixed_status[()] == np.int32(23)
    np.testing.assert_allclose(mixed_values, np.array([11.0, 12.0, 13.0], dtype=np.float64))

    scale = np.array(7, dtype=np.int32)
    point = module.summary_point()
    assert module.make_point(scale, point) is None
    assert point.total == np.float64(7.5)
    assert point.code == np.int32(107)
