"""Runtime evidence for post-IR policy-dispatched editable contracts."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

NATIVE_SOURCE = wrapper_source("fnative_call_examples_f90.f90")
IMMUTABLE_CONTRACT = Path(__file__).parent / "modified_contracts" / "fnative_call_examples_immutable" / "__init__.pyi"


def test_immutable_array_policy_copies_in_and_returns_replacement(tmp_path: Path):
    native_object = _compile_native_object(NATIVE_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        IMMUTABLE_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    original = np.array([2.0, 5.0, 7.0], dtype=np.float64)
    original.setflags(write=False)
    status = np.empty((), dtype=np.int32)

    replacement = module.scale_with_status(original, status)

    np.testing.assert_allclose(original, np.array([2.0, 5.0, 7.0], dtype=np.float64))
    np.testing.assert_allclose(replacement, np.array([4.0, 10.0, 14.0], dtype=np.float64))
    assert replacement is not original
    assert status[()] == np.int32(3)
