"""Character copy-in/copy-out, length, Unicode, and NUL tests."""

from pathlib import Path
import shutil

import pytest

from tests.wrapper.fortran._support import (
    _build_source_or_generated_pyi_and_import,
    _compile_native_object,
    _import_from_build_dir,
    _sole_native_module,
    wrapper_source,
)
from x2py import build_pyi_extension

CHARACTER_EDGES_F90_SOURCE = wrapper_source("fcharacter_edges_f90.f90")
CONTRACT_FIXTURES = Path(__file__).parent / "contracts"


def test_fortran_character_edge_cases_follow_copy_in_copy_out_policy(
    pyi_parity_build_mode: str,
    tmp_path: Path,
):
    module = _build_source_or_generated_pyi_and_import(
        CHARACTER_EDGES_F90_SOURCE,
        tmp_path,
        {
            "bind_c_fcharacter_edges_f90_wrapper.f90",
            "fcharacter_edges_f90_wrapper.c",
            "fcharacter_edges_f90_wrapper.h",
        },
        CONTRACT_FIXTURES / "fcharacter_edges_f90",
        pyi_parity_build_mode,
    )

    original = "abc     "
    assert module.fixed_inout(original) == "Zbc    !"
    assert original == "abc     "
    with pytest.raises(TypeError, match="exactly 8 bytes"):
        module.fixed_inout("abc")
    assert module.fixed_inout("abcdefgh") == "Zbcdefg!"
    with pytest.raises(TypeError, match="exactly 8 bytes"):
        module.fixed_inout("abcdefghi")
    assert module.assumed_inout("abc") == "Qbc"
    assert module.assumed_inout("") == ""
    assert module.optional_inout() is None
    assert module.optional_inout(None) is None
    assert module.optional_inout("abc") == "Pbc"
    assert module.make_out() == "go    "
    assert module.unicode_echo("café") == "café"

    with pytest.raises(TypeError, match="embedded NUL"):
        module.assumed_inout("a\0b")
    with pytest.raises(TypeError, match="embedded NUL"):
        module.unicode_echo("a\0b")


def test_fixed_hidden_string_output_matches_legacy_and_wrapper_plan_routes(tmp_path: Path, monkeypatch):
    """Replay the existing hidden output through a reduced contract entry."""
    native_object = _compile_native_object(CHARACTER_EDGES_F90_SOURCE, tmp_path / "native")
    modules = {}
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        contract_package = tmp_path / f"{route}_hidden_string_result"
        shutil.copytree(CONTRACT_FIXTURES / "fcharacter_edges_f90", contract_package)
        (contract_package / "__init__.pyi").write_text(
            "from .fcharacter_edges_f90 import make_out\n",
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
        modules[route] = module if hasattr(module, "make_out") else _sole_native_module(module)

    assert modules["legacy"].make_out() == "go    "
    assert modules["wrapper_plan"].make_out() == "go    "

    monkeypatch.setenv("X2PY_WRAPPER_FAIL_ALLOC", "1")
    with pytest.raises(MemoryError, match="Unable to allocate copy-return output string"):
        modules["wrapper_plan"].make_out()


def test_fixed_string_replacement_and_identity_match_legacy_and_wrapper_plan_routes(
    tmp_path: Path,
    monkeypatch,
):
    """Replay projected and discarded mutation against one existing native routine."""
    native_object = _compile_native_object(CHARACTER_EDGES_F90_SOURCE, tmp_path / "native")
    modules = {}
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        contract_package = tmp_path / f"{route}_fixed_string_writeback"
        contract_package.mkdir()
        (contract_package / "__init__.pyi").write_text(
            "from .fcharacter_edges_f90 import fixed_discard, fixed_replacement\n",
            encoding="utf-8",
        )
        (contract_package / "fcharacter_edges_f90.pyi").write_text(
            """from x2py.contracts import Returns, String, bind

@bind("fixed_inout")
def fixed_replacement(name: String[8]) -> Returns["name", String[8]]: ...

@bind("fixed_inout")
def fixed_discard(name: String[8]) -> None: ...
""",
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
        modules[route] = module if hasattr(module, "fixed_replacement") else _sole_native_module(module)

    for module in modules.values():
        original = "abc     "
        assert module.fixed_replacement(original) == "Zbc    !"
        assert original == "abc     "
        assert module.fixed_discard(original) is None
        assert original == "abc     "
        with pytest.raises(TypeError, match="exactly 8 bytes"):
            module.fixed_replacement("abc")
        with pytest.raises(TypeError, match="exactly 8 bytes"):
            module.fixed_discard("abcdefghi")

    monkeypatch.setenv("X2PY_WRAPPER_FAIL_ALLOC", "1")
    with pytest.raises(MemoryError, match="Unable to allocate mutable string buffer for argument name"):
        modules["wrapper_plan"].fixed_replacement("abc     ")


def test_assumed_and_optional_string_replacements_match_legacy_and_wrapper_plan_routes(
    tmp_path: Path,
    monkeypatch,
):
    """Replay runtime-length and absent/concrete presence through a reduced entry."""
    native_object = _compile_native_object(CHARACTER_EDGES_F90_SOURCE, tmp_path / "native")
    modules = {}
    for route, route_kwargs in (
        ("legacy", {"_force_legacy_wrapper_route": True}),
        ("wrapper_plan", {"_force_wrapper_plan_route": True}),
    ):
        contract_package = tmp_path / f"{route}_assumed_optional_string_writeback"
        shutil.copytree(CONTRACT_FIXTURES / "fcharacter_edges_f90", contract_package)
        (contract_package / "__init__.pyi").write_text(
            "from .fcharacter_edges_f90 import assumed_inout, optional_inout\n",
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
        modules[route] = module if hasattr(module, "assumed_inout") else _sole_native_module(module)

    for module in modules.values():
        assumed_original = "abc"
        optional_original = "abc"
        assert module.assumed_inout(assumed_original) == "Qbc"
        assert module.assumed_inout("") == ""
        assert module.optional_inout() is None
        assert module.optional_inout(None) is None
        assert module.optional_inout(optional_original) == "Pbc"
        assert assumed_original == "abc"
        assert optional_original == "abc"
        with pytest.raises(TypeError, match="embedded NUL"):
            module.assumed_inout("a\0b")
        with pytest.raises(TypeError, match="embedded NUL"):
            module.optional_inout("a\0b")

    monkeypatch.setenv("X2PY_WRAPPER_FAIL_ALLOC", "1")
    assert modules["wrapper_plan"].optional_inout() is None
    assert modules["wrapper_plan"].optional_inout(None) is None
    with pytest.raises(MemoryError, match="Unable to allocate mutable string buffer for argument name"):
        modules["wrapper_plan"].assumed_inout("abc")
    with pytest.raises(MemoryError, match="Unable to allocate mutable string buffer for argument label"):
        modules["wrapper_plan"].optional_inout("abc")
