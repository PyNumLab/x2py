"""Borrowed derived-type component lifetime and finalization tests."""

import gc
from pathlib import Path

import numpy as np

from tests.wrapper._support import _build_text_and_import

BORROWED_FINALIZER_F90_TEXT = Path(__file__).with_name("fborrowed_finalizer_f90.f90").read_text(encoding="utf-8")


def test_borrowed_child_wrapper_never_finalizes_native_component(tmp_path: Path):
    module = _build_text_and_import(
        BORROWED_FINALIZER_F90_TEXT,
        "fborrowed_finalizer_f90.f90",
        tmp_path,
        {
            "bind_c_fborrowed_finalizer_f90_wrapper.f90",
            "fborrowed_finalizer_f90_wrapper.c",
            "fborrowed_finalizer_f90_wrapper.h",
        },
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
