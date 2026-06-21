"""Common-block visibility and internal-storage behavior tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import _build_text_and_import

COMMON_BLOCK_F90_TEXT = Path(__file__).with_name("fcommon_block_f90.f90").read_text(encoding="utf-8")


def test_common_block_storage_stays_internal_to_wrapped_fortran(tmp_path: Path):
    module = _build_text_and_import(
        COMMON_BLOCK_F90_TEXT,
        "fcommon_block_f90.f90",
        tmp_path,
        {
            "bind_c_fcommon_block_f90_wrapper.f90",
            "fcommon_block_f90_wrapper.c",
            "fcommon_block_f90_wrapper.h",
        },
    )

    assert not hasattr(module, "shared_value")
    assert not hasattr(module, "get_shared_value")
    assert not hasattr(module, "set_shared_value")

    module.write_shared(np.int32(17))
    assert module.read_shared() == np.int32(17)
    module.write_shared(np.int32(-3))
    assert module.read_shared() == np.int32(-3)
