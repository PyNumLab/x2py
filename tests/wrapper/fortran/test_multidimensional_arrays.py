import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import _sole_native_module


SOURCE = Path(__file__).with_name("multid_arrays.f90")
EXPECTED_GENERATED_SOURCES = {
    "bind_c_multid_arrays_wrapper.f90",
    "multid_arrays_wrapper.c",
    "multid_arrays_wrapper.h",
}


@pytest.fixture(scope="module")
def module(tmp_path_factory):
    workdir = tmp_path_factory.mktemp("multid_arrays_wrapper")
    build_dir = workdir / "build"
    source_path = workdir / SOURCE.name
    shutil.copyfile(SOURCE, source_path)

    cmd = [
        sys.executable,
        "-m",
        "x2py",
        str(source_path),
        "--out-dir",
        str(build_dir),
        "--json",
    ]
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.fail(
            f"wrapper build failed\ncommand: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    payload = json.loads(result.stdout)
    generated_sources = {Path(path).name for path in payload["generated_sources"]}
    assert generated_sources == EXPECTED_GENERATED_SOURCES

    sys.modules.pop(SOURCE.stem, None)
    sys.path.insert(0, str(build_dir))
    try:
        return _sole_native_module(importlib.import_module(SOURCE.stem))
    finally:
        sys.path.remove(str(build_dir))


def _matrix(rows=4, cols=3):
    data = np.arange(1, rows * cols + 1, dtype=np.float64)
    return np.asfortranarray(data.reshape((rows, cols), order="F"))


def _strided_matrix(rows=4, cols=3):
    base = _matrix(rows * 2, cols)
    return base[::2, :]


def _strided_matrix_output(shape):
    base = np.zeros((shape[0] * 2, shape[1]), dtype=np.float64, order="F")
    return base[::2, :]


def _checksum2(array):
    total = 0.0
    for i, j in np.ndindex(array.shape):
        total += array[i, j] * (1000.0 * (i + 1) + 10.0 * (j + 1))
    return total


def _c_ordered_strided_matrix(rows=4, cols=3):
    data = np.arange(1, rows * cols * 2 + 1, dtype=np.float64)
    base = np.array(data.reshape((rows, cols * 2), order="C"), order="C")
    return base[:, ::2]


def _reversed_fortran_matrix(rows=4, cols=3):
    base = _matrix(rows * 2, cols)
    return base[::-2, :]


def _broadcast_fortran_like_matrix(rows=4, cols=3):
    row = np.asfortranarray(np.arange(1, cols + 1, dtype=np.float64)[None, :])
    return np.broadcast_to(row, (rows, cols))


def _rank3(shape=(4, 3, 2)):
    data = np.arange(1, np.prod(shape) + 1, dtype=np.float64)
    return np.asfortranarray(data.reshape(shape, order="F"))


def _strided_rank3(shape=(4, 3, 2)):
    base = _rank3((shape[0] * 2, shape[1], shape[2]))
    return base[::2, :, :]


def _strided_rank3_output(shape):
    base = np.zeros((shape[0] * 2, shape[1], shape[2]), dtype=np.float64, order="F")
    return base[::2, :, :]


def _checksum3(array):
    total = 0.0
    for i, j, k in np.ndindex(array.shape):
        total += array[i, j, k] * (10000.0 * (i + 1) + 100.0 * (j + 1) + (k + 1))
    return total


def _c_ordered_strided_rank3(shape=(4, 3, 2)):
    base_shape = (shape[0], shape[1], shape[2] * 2)
    data = np.arange(1, np.prod(base_shape) + 1, dtype=np.float64)
    base = np.array(data.reshape(base_shape, order="C"), order="C")
    return base[:, :, ::2]


def test_rank2_contiguous_contract_requires_fortran_contiguous(module):
    source = _matrix()
    out = np.zeros_like(source, order="F")

    module.scale2_contiguous(source, out)

    np.testing.assert_allclose(out, 2.0 * source)

    c_order_source = np.array(source, order="C", copy=True)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_contiguous(c_order_source, out)

    c_order_out = np.zeros_like(source, order="C")
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_contiguous(source, c_order_out)

    strided_source = _strided_matrix()
    strided_out = np.zeros_like(strided_source, order="F")
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_contiguous(strided_source, strided_out)


def test_rank2_assumed_shape_accepts_fortran_ordered_strided_views(module):
    contiguous_source = _matrix()
    contiguous_out = np.zeros_like(contiguous_source, order="F")

    module.scale2_strided(contiguous_source, contiguous_out)

    np.testing.assert_allclose(contiguous_out, 3.0 * contiguous_source)

    contiguous_checksum = np.zeros(1, dtype=np.float64)
    module.checksum2_strided(contiguous_source, contiguous_checksum)
    np.testing.assert_allclose(contiguous_checksum[0], _checksum2(contiguous_source))

    strided_source = _strided_matrix()
    strided_out = _strided_matrix_output(strided_source.shape)

    module.scale2_strided(strided_source, strided_out)

    np.testing.assert_allclose(strided_out, 3.0 * strided_source)

    strided_checksum = np.zeros(1, dtype=np.float64)
    module.checksum2_strided(strided_source, strided_checksum)
    np.testing.assert_allclose(strided_checksum[0], _checksum2(strided_source))

    c_order_source = np.array(contiguous_source, order="C", copy=True)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_strided(c_order_source, contiguous_out)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.checksum2_strided(c_order_source, contiguous_checksum)

    c_ordered_strided_source = _c_ordered_strided_matrix()
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_strided(c_ordered_strided_source, contiguous_out)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.checksum2_strided(c_ordered_strided_source, contiguous_checksum)

    c_order_out = np.zeros_like(contiguous_source, order="C")
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_strided(contiguous_source, c_order_out)


def test_rank2_assumed_shape_rejects_non_positive_strides(module):
    source = _matrix()
    out = np.zeros_like(source, order="F")
    checksum = np.zeros(1, dtype=np.float64)

    reversed_source = _reversed_fortran_matrix()
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_strided(reversed_source, out)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.checksum2_strided(reversed_source, checksum)

    broadcast_source = _broadcast_fortran_like_matrix()
    assert broadcast_source.strides[0] == 0
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_strided(broadcast_source, out)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.checksum2_strided(broadcast_source, checksum)

    reversed_out = _reversed_fortran_matrix()
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_strided(source, reversed_out)


def test_rank2_explicit_shape_requires_fortran_contiguous(module):
    source = _matrix()
    rows, cols = source.shape
    out = np.zeros_like(source, order="F")

    module.scale2_explicit(np.int32(rows), np.int32(cols), source, out)

    np.testing.assert_allclose(out, 4.0 * source)

    c_order_source = np.array(source, order="C", copy=True)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_explicit(np.int32(rows), np.int32(cols), c_order_source, out)

    strided_source = _strided_matrix(rows, cols)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.scale2_explicit(np.int32(rows), np.int32(cols), strided_source, out)


def test_rank3_contiguous_contract_requires_fortran_contiguous(module):
    source = _rank3()
    out = np.zeros_like(source, order="F")

    module.shift3_contiguous(source, out)

    np.testing.assert_allclose(out, source + 10.0)

    c_order_source = np.array(source, order="C", copy=True)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.shift3_contiguous(c_order_source, out)

    strided_source = _strided_rank3()
    strided_out = np.zeros_like(strided_source, order="F")
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.shift3_contiguous(strided_source, strided_out)


def test_rank3_assumed_shape_accepts_fortran_ordered_strided_views(module):
    contiguous_source = _rank3()
    contiguous_out = np.zeros_like(contiguous_source, order="F")

    module.shift3_strided(contiguous_source, contiguous_out)

    np.testing.assert_allclose(contiguous_out, contiguous_source + 20.0)

    contiguous_checksum = np.zeros(1, dtype=np.float64)
    module.checksum3_strided(contiguous_source, contiguous_checksum)
    np.testing.assert_allclose(contiguous_checksum[0], _checksum3(contiguous_source))

    strided_source = _strided_rank3()
    strided_out = _strided_rank3_output(strided_source.shape)

    module.shift3_strided(strided_source, strided_out)

    np.testing.assert_allclose(strided_out, strided_source + 20.0)

    strided_checksum = np.zeros(1, dtype=np.float64)
    module.checksum3_strided(strided_source, strided_checksum)
    np.testing.assert_allclose(strided_checksum[0], _checksum3(strided_source))

    c_order_source = np.array(contiguous_source, order="C", copy=True)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.shift3_strided(c_order_source, contiguous_out)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.checksum3_strided(c_order_source, contiguous_checksum)

    c_ordered_strided_source = _c_ordered_strided_rank3()
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.shift3_strided(c_ordered_strided_source, contiguous_out)
    with pytest.raises(TypeError, match=r"expected ordering \(F\)"):
        module.checksum3_strided(c_ordered_strided_source, contiguous_checksum)
