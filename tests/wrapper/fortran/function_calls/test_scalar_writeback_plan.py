"""Compiled canonical-plan coverage for scalar writeback."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
)
from x2py import build_pyi_extension


def test_scalar_copy_in_out_returns_replacement(tmp_path: Path):
    source = tmp_path / "scalar_writeback.f90"
    source.write_text(
        """
module scalar_writeback
contains
  subroutine bump(value)
    integer(4), intent(inout) :: value
    value = value + 1
  end subroutine bump
end module scalar_writeback
""",
        encoding="utf-8",
    )
    contract = tmp_path / "scalar_writeback.pyi"
    contract.write_text(
        """
from x2py.contracts import Annotated, Immutable, Int32, Returns

def bump(
    value: Annotated[Int32, Immutable]
) -> Returns["value", Int32]: ...
""",
        encoding="utf-8",
    )
    native_object = _compile_native_object(source, tmp_path / "native")

    result = build_pyi_extension(
        contract,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    assert tuple(path.name for path in result.generated_sources) == (
        "bind_c_scalar_writeback_wrapper.f90",
        "scalar_writeback_wrapper.c",
        "scalar_writeback_wrapper.h",
    )
    plan_bridge = (result.output_dir / "bind_c_scalar_writeback_wrapper.f90").read_text(encoding="utf-8")
    plan_c = (result.output_dir / "scalar_writeback_wrapper.c").read_text(encoding="utf-8")
    assert 'subroutine bind_c_bump(value) bind(c, name="bind_c_bump")' in plan_bridge
    assert "void bind_c_bump(int32_t * value);" in plan_c
    original = np.int32(4)
    replacement = module.bump(original)
    assert original == np.int32(4)
    assert replacement == np.int32(5)
    with pytest.raises(TypeError):
        module.bump("bad")
