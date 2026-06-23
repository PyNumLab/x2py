"""Recursive and reentrant native runtime call tests."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import _build_and_import, wrapper_source

RECURSION_SOURCE = wrapper_source("fruntime_recursion_f90.f90")


def test_recursive_native_runtime_calls(tmp_path: Path):
    module = _build_and_import(
        RECURSION_SOURCE,
        tmp_path,
        {
            "bind_c_fruntime_recursion_f90_wrapper.f90",
            "fruntime_recursion_f90_wrapper.c",
            "fruntime_recursion_f90_wrapper.h",
        },
    )

    assert module.factorial(np.int32(5)) == np.int32(120)
    assert [module.add_one(np.int32(i)) for i in range(5)] == [1, 2, 3, 4, 5]
