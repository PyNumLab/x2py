"""Pointer argument, result, association, and handle-readiness tests."""

import subprocess
from pathlib import Path

import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    wrapper_source,
)

POINTERS_F90_SOURCE = wrapper_source("fpointers_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_pointer_array_handles_block_until_descriptor_handoff_exists(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    with pytest.raises((subprocess.CalledProcessError, ValueError)) as exc_info:
        _build_source_or_generated_pyi_and_import(
            POINTERS_F90_SOURCE,
            tmp_path,
            {
                "bind_c_fpointers_f90_wrapper.f90",
                "fpointers_f90_wrapper.c",
                "fpointers_f90_wrapper.h",
            },
            CONTRACT_FIXTURES / "fpointers_f90",
            pyi_parity_build_mode,
        )

    error = exc_info.value.stderr if isinstance(exc_info.value, subprocess.CalledProcessError) else str(exc_info.value)
    assert "pointer descriptor-argument handoff needs generated handle support" in error
