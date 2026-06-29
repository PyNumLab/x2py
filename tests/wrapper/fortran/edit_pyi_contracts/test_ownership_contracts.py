"""Runtime evidence for explicit editable ownership and destruction triples."""

import gc
from pathlib import Path
import weakref

import numpy as np

from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

NATIVE_SOURCE = wrapper_source("fallocatable_views_f90.f90")
FINALIZER_SOURCE = wrapper_source("fborrowed_finalizer_f90.f90")
OWNERSHIP_CONTRACT = (
    Path(__file__).parent / "modified_contracts" / "fallocatable_views_explicit_ownership" / "__init__.pyi"
)
FINALIZER_CONTRACT = (
    Path(__file__).parent / "modified_contracts" / "fborrowed_finalizer_explicit_ownership" / "__init__.pyi"
)


def test_same_array_concept_uses_native_wrapper_and_numpy_lifetimes(tmp_path: Path):
    native_object = _compile_native_object(NATIVE_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        OWNERSHIP_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    # Native-owned: releasing the NumPy view does not release module storage;
    # the explicit native operation remains responsible for deallocation.
    module.allocate_module_values(np.int32(3))
    native_view = module.module_values
    np.testing.assert_allclose(native_view, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    del native_view
    gc.collect()
    assert module.module_values_sum() == np.float64(6.0)
    module.deallocate_module_values()
    assert module.module_values is None

    # Wrapper-owned: the borrowed field view retains the containing extension
    # object as its base until the view itself is released.
    owner = module.buffer()
    owner.allocate_values(np.int32(3))
    wrapper_view = owner.values
    assert wrapper_view.base is owner
    del owner
    gc.collect()
    np.testing.assert_allclose(wrapper_view, np.array([1.0, 2.0, 3.0], dtype=np.float64))
    retained_owner = wrapper_view.base
    retained_owner.deallocate_values()
    assert retained_owner.values is None

    # Python-owned: native allocatable output is copied into a detached array.
    # Python reference collection then owns the copy's release boundary.
    python_copy = module.build_values(np.int32(4))
    np.testing.assert_allclose(python_copy, np.array([2.0, 4.0, 6.0, 8.0], dtype=np.float64))
    released: list[bool] = []
    weakref.finalize(python_copy, released.append, True)
    del python_copy
    gc.collect()
    assert released == [True]


def test_wrapper_owned_borrow_keeps_owner_alive_and_finalizes_exactly_once(tmp_path: Path):
    native_object = _compile_native_object(FINALIZER_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        FINALIZER_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    module.reset_final_count()
    owner = module.parent()
    borrowed = owner.value

    del owner
    gc.collect()
    assert module.get_final_count() == np.int32(0)

    del borrowed
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(1)
