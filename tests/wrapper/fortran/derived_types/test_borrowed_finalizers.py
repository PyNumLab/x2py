"""Borrowed derived-type component lifetime and finalization tests."""

import gc
from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import _build_source_or_generated_pyi_and_import, wrapper_source

BORROWED_FINALIZER_F90_SOURCE = wrapper_source("fborrowed_finalizer_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_borrowed_child_wrapper_never_finalizes_native_component(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        BORROWED_FINALIZER_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fborrowed_finalizer_f90_wrapper.f90",
            "fborrowed_finalizer_f90_wrapper.c",
            "fborrowed_finalizer_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fborrowed_finalizer_f90",
        pyi_parity_build_mode,
    )

    module.reset_final_count()
    owner = module.parent()
    borrowed = owner.value

    del borrowed
    gc.collect()
    assert module.get_final_count() == np.int32(0)

    borrowed = owner.value
    del owner
    gc.collect()
    assert module.get_final_count() == np.int32(0)

    del borrowed
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(1)
