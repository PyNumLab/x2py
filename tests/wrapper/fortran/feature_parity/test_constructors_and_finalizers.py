"""Default/keyword construction and owned-instance finalization tests."""

import gc
from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    wrapper_source,
    _build_text_and_import,
)

CONSTRUCTOR_F90_TEXT = wrapper_source("fconstructors_f90.f90").read_text(encoding="utf-8")


def test_fortran_default_constructor_keywords_and_finalization(tmp_path: Path):
    module = _build_text_and_import(
        CONSTRUCTOR_F90_TEXT,
        "fconstructors_f90.f90",
        tmp_path,
        {
            "bind_c_fconstructors_f90_wrapper.f90",
            "fconstructors_f90_wrapper.c",
            "fconstructors_f90_wrapper.h",
        },
    )

    module.reset_final_count()

    defaulted = module.initialized()
    assert defaulted.id == np.int32(7)
    assert defaulted.scale == np.float64(2.5)

    partial = module.initialized(id=np.int32(11))
    assert partial.id == np.int32(11)
    assert partial.scale == np.float64(2.5)

    keyword = module.initialized(id=np.int32(4), scale=np.float64(6.5))
    assert keyword.id == np.int32(4)
    assert keyword.scale == np.float64(6.5)

    del defaulted
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(1)

    del partial
    del keyword
    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(3)

    with pytest.raises(TypeError):
        module.initialized(np.int32(1))
    gc.collect()
    assert module.get_final_count() == np.int32(4)

    with pytest.raises(TypeError):
        module.initialized(missing=np.int32(1))
    gc.collect()
    assert module.get_final_count() == np.int32(5)

    gc.collect()
    gc.collect()
    assert module.get_final_count() == np.int32(5)
