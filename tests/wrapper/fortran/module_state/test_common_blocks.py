"""Common-block visibility and internal-storage behavior tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import _build_source_or_generated_pyi_and_import, wrapper_source

COMMON_BLOCK_F90_SOURCE = wrapper_source("fcommon_block_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_common_block_storage_stays_internal_to_wrapped_fortran(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        COMMON_BLOCK_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fcommon_block_f90_wrapper.f90",
            "fcommon_block_f90_wrapper.c",
            "fcommon_block_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fcommon_block_f90",
        pyi_parity_build_mode,
    )

    assert not hasattr(module, "shared_value")
    assert not hasattr(module, "get_shared_value")
    assert not hasattr(module, "set_shared_value")

    module.write_shared(np.int32(17))
    assert module.read_shared() == np.int32(17)
    module.write_shared(np.int32(-3))
    assert module.read_shared() == np.int32(-3)
