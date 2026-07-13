"""Compiled legacy/direct-plan parity for Phase 3 scalar writeback."""

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


def test_scalar_copy_in_out_returns_replacement_through_both_routes(tmp_path: Path):
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

    results = []
    modules = []
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        result = build_pyi_extension(
            contract,
            native_objects=[native_object],
            native_include_dirs=[native_object.parent],
            output_dir=tmp_path / route,
            **route_kwargs,
        )
        results.append(result)
        modules.append(_sole_native_module(_import_from_build_dir(result.module_name, result.output_dir)))

    assert [tuple(path.name for path in result.generated_sources) for result in results] == [
        (
            "bind_c_scalar_writeback_wrapper.f90",
            "scalar_writeback_wrapper.c",
            "scalar_writeback_wrapper.h",
        ),
        (
            "bind_c_scalar_writeback_wrapper.f90",
            "scalar_writeback_wrapper.c",
            "scalar_writeback_wrapper.h",
        ),
    ]
    legacy_bridge = (tmp_path / "legacy" / "bind_c_scalar_writeback_wrapper.f90").read_text(encoding="utf-8")
    plan_bridge = (tmp_path / "wrapper_plan" / "bind_c_scalar_writeback_wrapper.f90").read_text(encoding="utf-8")
    plan_c = (tmp_path / "wrapper_plan" / "scalar_writeback_wrapper.c").read_text(encoding="utf-8")
    assert "function bind_c_bump(value_0001) bind(c) result(value_mutable)" in legacy_bridge
    assert legacy_bridge.count("integer(i32) :: value_mutable") == 1
    assert 'subroutine bind_c_bump(value) bind(c, name="bind_c_bump")' in plan_bridge
    assert "void bind_c_bump(int32_t * value);" in plan_c
    for module in modules:
        original = np.int32(4)
        replacement = module.bump(original)
        assert original == np.int32(4)
        assert replacement == np.int32(5)
        with pytest.raises(TypeError):
            module.bump("bad")
