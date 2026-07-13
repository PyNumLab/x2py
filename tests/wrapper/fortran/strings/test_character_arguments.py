"""Legacy and modern scalar character argument/result tests."""

from pathlib import Path
import shutil

import numpy as np
import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    _compile_native_object,
    _import_from_build_dir,
    _assert_legacy_string_examples,
    _assert_modern_string_examples,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

STRING_LEGACY_SOURCE = wrapper_source("fstrings.f")
STRING_F90_SOURCE = wrapper_source("fstrings_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_legacy_fortran_character_arguments_and_results(pyi_parity_build_mode: str, tmp_path: Path):
    module = _build_source_or_generated_pyi_and_import(
        STRING_LEGACY_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_wrapper.f90",
            "fstrings_wrapper.c",
            "fstrings_wrapper.h",
        },
        CONTRACT_FIXTURES / "fstrings",
        pyi_parity_build_mode,
    )

    _assert_legacy_string_examples(module)


def test_modern_fortran_character_arguments_and_results(pyi_parity_build_mode: str, tmp_path: Path):
    module = _build_source_or_generated_pyi_and_import(
        STRING_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fstrings_f90_wrapper.f90",
            "fstrings_f90_wrapper.c",
            "fstrings_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fstrings_f90",
        pyi_parity_build_mode,
    )

    _assert_modern_string_examples(module)


def test_edited_modern_string_contract_wraps_full_axis_spelling_set(tmp_path: Path):
    native_object = _compile_native_object(STRING_F90_SOURCE, tmp_path / "native")
    result = build_pyi_extension(
        CONTRACT_FIXTURES / "fstrings_f90_axes" / "__init__.pyi",
        native_objects=[native_object],
        native_include_dirs=[native_object.parent],
        output_dir=tmp_path / "pyi_axes_build",
    )
    module = _sole_native_module(_import_from_build_dir(result.module_name, result.output_dir))

    assert module.string_len_assumed("variable length") == 15
    assert module.string_len_fixed("short   ") == 5
    labels = np.array([b"first", b"second"], dtype="S8")
    assert module.fixed_array_extent(labels) == 16

    label = np.array("abcdefgh", dtype="S8")
    assert module.rewrite_storage(label) is None
    assert label[()] == b"Ybcdefg?"


def test_fixed_width_character_arrays_match_legacy_and_wrapper_plan_routes(tmp_path: Path):
    """Replay one ordinary fixed-width NumPy bytes array without descriptors."""
    native_object = _compile_native_object(STRING_F90_SOURCE, tmp_path / "native")
    modules = {}
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        contract_package = tmp_path / f"{route}_character_array"
        shutil.copytree(CONTRACT_FIXTURES / "fstrings_f90_axes", contract_package)
        (contract_package / "__init__.pyi").write_text(
            "from .fstrings_f90 import fixed_array_extent\n",
            encoding="utf-8",
        )
        result = build_pyi_extension(
            contract_package / "__init__.pyi",
            native_objects=[native_object],
            native_include_dirs=[native_object.parent],
            output_dir=tmp_path / route,
            **route_kwargs,
        )
        module = _import_from_build_dir(result.module_name, result.output_dir)
        modules[route] = module if hasattr(module, "fixed_array_extent") else _sole_native_module(module)

    for module in modules.values():
        labels = np.array([b"first", b"second"], dtype="S8")
        assert module.fixed_array_extent(labels) == 16
        assert module.fixed_array_extent(np.empty(0, dtype="S8")) == 0

    direct = modules["wrapper_plan"]
    with pytest.raises(TypeError):
        direct.fixed_array_extent(np.array([b"short"], dtype="S7"))
    with pytest.raises(TypeError):
        direct.fixed_array_extent(np.array([[b"label"]], dtype="S8"))


def test_required_scalar_string_inputs_match_legacy_and_wrapper_plan_routes(tmp_path: Path):
    """Reuse the existing modern string unit through one scalar-input-only entry."""
    native_object = _compile_native_object(STRING_F90_SOURCE, tmp_path / "native")
    modules = []
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        contract_package = tmp_path / f"{route}_string_inputs"
        shutil.copytree(CONTRACT_FIXTURES / "fstrings_f90", contract_package)
        (contract_package / "__init__.pyi").write_text(
            "\n".join(
                (
                    "from .fstrings_f90 import char_code_default",
                    "from .fstrings_f90 import char_code_len1",
                    "from .fstrings_f90 import char_code_kind1",
                    "from .fstrings_f90 import char_code_c_char",
                    "from .fstrings_f90 import string_len_fixed",
                    "from .fstrings_f90 import string_len_assumed",
                    "from .fstrings_f90 import string_len_c_char",
                    "",
                )
            ),
            encoding="utf-8",
        )
        result = build_pyi_extension(
            contract_package / "__init__.pyi",
            native_objects=[native_object],
            native_include_dirs=[native_object.parent],
            output_dir=tmp_path / route,
            **route_kwargs,
        )
        module = _import_from_build_dir(result.module_name, result.output_dir)
        modules.append(module if hasattr(module, "char_code_default") else _sole_native_module(module))

    for module in modules:
        assert module.char_code_default("A") == ord("A")
        assert module.char_code_len1(np.str_("B")) == ord("B")
        assert module.char_code_kind1("C") == ord("C")
        assert module.char_code_c_char("D") == ord("D")
        assert module.string_len_fixed("short   ") == 5
        assert module.string_len_assumed("variable length") == 15
        assert module.string_len_assumed("") == 0
        assert module.string_len_assumed("café") == 5
        assert module.string_len_c_char("c-char  ") == 6

        with pytest.raises(TypeError, match="str"):
            module.string_len_assumed(b"bytes")
        with pytest.raises(TypeError, match="exactly 8 bytes"):
            module.string_len_fixed("short")
        with pytest.raises(TypeError, match="embedded NUL"):
            module.string_len_assumed("a\0b")


def test_fixed_string_results_match_legacy_and_wrapper_plan_routes(tmp_path: Path, monkeypatch):
    """Replay existing fixed direct results through a result-only contract entry."""
    native_object = _compile_native_object(STRING_F90_SOURCE, tmp_path / "native")
    modules = {}
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        contract_package = tmp_path / f"{route}_string_results"
        shutil.copytree(CONTRACT_FIXTURES / "fstrings_f90", contract_package)
        (contract_package / "__init__.pyi").write_text(
            "\n".join(
                (
                    "from .fstrings_f90 import char_result_default",
                    "from .fstrings_f90 import char_result_c_char",
                    "from .fstrings_f90 import string_result_fixed",
                    "from .fstrings_f90 import string_result_padded",
                    "from .fstrings_f90 import string_result_c_char",
                    "",
                )
            ),
            encoding="utf-8",
        )
        result = build_pyi_extension(
            contract_package / "__init__.pyi",
            native_objects=[native_object],
            native_include_dirs=[native_object.parent],
            output_dir=tmp_path / route,
            **route_kwargs,
        )
        module = _import_from_build_dir(result.module_name, result.output_dir)
        modules[route] = module if hasattr(module, "char_result_default") else _sole_native_module(module)

    for module in modules.values():
        assert module.char_result_default() == "M"
        assert module.char_result_c_char() == "C"
        assert module.string_result_fixed() == "MODERN!!"
        assert module.string_result_padded() == "PAD     "
        assert module.string_result_c_char() == "C-CHAR!!"

    monkeypatch.setenv("X2PY_WRAPPER_FAIL_ALLOC", "1")
    with pytest.raises(MemoryError, match="Unable to allocate copy-return output string"):
        modules["wrapper_plan"].string_result_fixed()
