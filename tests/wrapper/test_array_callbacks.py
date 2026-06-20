"""Array callback argument and result conversion tests."""

from pathlib import Path

import numpy as np

from tests.wrapper._support import _build_text_and_import

CALLBACK_ARRAY_F90_TEXT = Path(__file__).with_name("fcallback_array_f90.f90").read_text(encoding="utf-8")


def test_immediate_dummy_procedure_converts_array_arguments_and_results(tmp_path: Path):
    module = _build_text_and_import(
        CALLBACK_ARRAY_F90_TEXT,
        "fcallback_array_f90.f90",
        tmp_path,
        {
            "bind_c_fcallback_array_f90_wrapper.f90",
            "fcallback_array_f90_wrapper.c",
            "fcallback_array_f90_wrapper.h",
        },
    )
    values = np.asfortranarray(np.array([1.0, 2.0, 3.0], dtype=np.float64))

    assert module.apply_reduce(lambda count, data: data[:count].sum(), np.int32(3), values) == np.float64(6.0)
    transformed = np.empty_like(values)
    result = module.apply_transform(
        lambda count, data: np.asfortranarray(data[:count] * 2.0),
        np.int32(3),
        values,
        transformed,
    )
    assert result is transformed
    np.testing.assert_array_equal(transformed, np.array([2.0, 4.0, 6.0], dtype=np.float64))
