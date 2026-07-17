"""Combined callback contract covering value, storage, arrays, strings, and derived types."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import _build_source_or_generated_pyi_and_import, wrapper_source

CALLBACK_ALL_F90_SOURCE = wrapper_source("fcallback_all_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_immediate_callbacks_cover_all_supported_argument_shapes(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        CALLBACK_ALL_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fcallback_all_f90_wrapper.f90",
            "fcallback_all_f90_wrapper.c",
            "fcallback_all_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fcallback_all_f90",
        pyi_parity_build_mode,
    )

    assert module.apply_value_callback(lambda value: value + 5, np.int32(4)) == np.int32(9)

    scalar_seen = []

    def scalar_callback(value, output, missing):
        scalar_seen.append((value[()], missing[()]))
        value[...] = value[()] + 10.0
        missing[...] = missing[()] + 1.0
        output[...] = value[()] + missing[()]

    assert module.apply_scalar_storage_callback(scalar_callback, np.float64(2.0), np.float64(5.0)) == np.float64(18.0)
    assert scalar_seen == [(np.float64(2.0), np.float64(5.0))]

    values = np.asfortranarray(np.array([1.0, 2.0, 3.0], dtype=np.float64))
    output = np.empty_like(values)

    def array_callback(count, input_values, output_values):
        assert count.shape == ()
        assert count.flags.writeable
        assert input_values.flags.f_contiguous
        assert input_values.flags.writeable
        assert output_values.flags.writeable
        output_values[:count] = input_values[:count] + 1.5

    result = module.apply_array_storage_callback(array_callback, np.int32(3), values, output)
    assert result is output
    np.testing.assert_allclose(output, np.array([2.5, 3.5, 4.5], dtype=np.float64))

    def string_callback(read_label, write_label, update_label):
        assert read_label.shape == ()
        assert write_label.shape == ()
        assert update_label.shape == ()
        assert read_label.dtype.itemsize == 8
        assert write_label.dtype.itemsize == 8
        assert update_label.dtype.itemsize == 8
        assert read_label[()] == b"READONLY"
        assert update_label[()] == b"OLD     "
        write_label[...] = b"WRITTEN!"
        update_label[...] = b"UPDATED!"

    assert module.apply_string_storage_callback(string_callback, "OLD     ") == ("UPDATED!", "WRITTEN!")

    point = module.point_t(x=np.float64(2.0), y=np.float64(5.0))
    shifted = module.apply_point_callback(
        lambda value: module.point_t(x=value.x + 1.0, y=value.y * 2.0),
        point,
    )
    assert isinstance(shifted, module.point_t)
    assert shifted.x == np.float64(3.0)
    assert shifted.y == np.float64(10.0)
