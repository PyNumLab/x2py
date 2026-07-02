"""Runtime evidence for post-IR policy-dispatched editable contracts."""

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

NATIVE_SOURCE = wrapper_source("fnative_call_examples_f90.f90")
IMMUTABLE_CONTRACT = Path(__file__).parent / "modified_contracts" / "fnative_call_examples_immutable" / "__init__.pyi"
IMMUTABLE_KINDS_CONTRACT = (
    Path(__file__).parent / "modified_contracts" / "fnative_call_examples_immutable_kinds" / "__init__.pyi"
)
CONTRADICTORY_OWNERSHIP_CONTRACT = (
    Path(__file__).parent / "invalid_contracts" / "contradictory_ownership" / "__init__.pyi"
)


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


def test_immutable_scalar_string_array_and_derived_policies_return_replacements(tmp_path: Path):
    native_object = _compile_native_object(NATIVE_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        IMMUTABLE_KINDS_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    replacement_status = module.scalar_status(np.int32(4))
    assert replacement_status == np.int32(15)

    original_label = "abc     "
    replacement_label = module.fixed_inout(original_label)
    assert original_label == "abc     "
    assert replacement_label == "Xbc    !"

    original_values = np.array([2.0, 5.0, 7.0], dtype=np.float64)
    status = np.empty((), dtype=np.int32)
    replacement_values = module.scale_with_status(original_values, status)
    np.testing.assert_allclose(original_values, np.array([2.0, 5.0, 7.0], dtype=np.float64))
    np.testing.assert_allclose(replacement_values, np.array([4.0, 10.0, 14.0], dtype=np.float64))

    replacement_point = module.make_point(np.int32(7))
    assert replacement_point.total == np.float64(7.5)
    assert replacement_point.code == np.int32(107)


def test_contradictory_ownership_contract_fails_before_bridge_generation(tmp_path: Path):
    native_object = _compile_native_object(NATIVE_SOURCE, tmp_path / "native")

    with pytest.raises(
        ValueError,
        match=r"values.*native/copy_return/native_owner.*no supported destruction policy",
    ):
        build_pyi_extension(
            CONTRADICTORY_OWNERSHIP_CONTRACT,
            native_objects=[native_object],
            native_include_dirs=[native_object.parent],
            output_dir=tmp_path / "pyi_build",
        )

    assert not (tmp_path / "pyi_build" / "bind_c_fnative_call_examples_f90_wrapper.f90").exists()
