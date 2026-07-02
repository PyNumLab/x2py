"""Editable contracts that remove or hide public declarations."""

from pathlib import Path

import numpy as np

from tests.wrapper.fortran._support import (
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

MODULE_VARIABLE_SOURCE = wrapper_source("fmodule_vars_f90.f90")
MODIFIED_CONTRACT = Path(__file__).parent / "modified_contracts" / "module_variables_visibility" / "__init__.pyi"


def test_editable_contract_removes_and_hides_public_declarations(tmp_path: Path):
    contract_text = MODIFIED_CONTRACT.parent.joinpath("fmodule_vars_f90.pyi").read_text(encoding="utf-8")
    assert "def next_local" not in contract_text
    assert "scale: private[Float64]" in contract_text
    assert "@private\ndef scaled_counter" in contract_text

    native_object = _compile_native_object(MODULE_VARIABLE_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        MODIFIED_CONTRACT,
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    assert module.counter == np.int32(3)
    module.counter = np.int32(9)
    assert module.counter == np.int32(9)
    assert module.summarize() == np.int32(21)

    assert not hasattr(module, "scale")
    assert not hasattr(module, "scaled_counter")
    assert not hasattr(module, "next_local")
