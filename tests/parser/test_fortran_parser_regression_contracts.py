"""Focused regression contracts for the Fortran parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from fortran_parser.models import FortranArgument, FortranDerivedType, FortranModule, FortranProcedureSignature
from fortran_parser.parser import (
    FortranParser,
    _ParserScope,
    _SourceUnit,
    _UnitParts,
    parse_fortran_project,
)
from x2py import FortranParseError, parse_fortran_file


def _lines(*values: str) -> list[tuple[str, int, str]]:
    return [(value, lineno, value) for lineno, value in enumerate(values, start=1)]


def _unit(kind: str, name: str | None, *values: str) -> _SourceUnit:
    lines = _lines(*values)
    return _SourceUnit(kind=kind, name=name, lines=lines, start_line=1, end_line=len(lines))


def test_unit_region_helpers_preserve_specification_execution_and_contains_boundaries():
    parser = FortranParser()
    unit = _unit(
        "procedure",
        "work",
        "subroutine work()",
        "integer :: value",
        "type :: local_state",
        "end type local_state",
        "value = 1",
        "contains",
        "subroutine inner()",
        "end subroutine inner",
        "end subroutine work",
    )
    parts = _UnitParts(
        header=unit.lines[0],
        specification=[unit.lines[1]],
        execution=[unit.lines[4]],
        contains=[unit.lines[6], unit.lines[7]],
        footer=unit.lines[-1],
    )

    assert parser._helper_direct_contains_line(unit, filename="regions.f90") == 6
    assert parser._helper_child_unit_region(unit, parts, _SourceUnit("derived_type", "unknown", [], None, None)) == (
        "specification"
    )
    assert parser._helper_child_unit_region(
        unit, parts, _unit("derived_type", "local_state", "type :: local_state")
    ) == ("specification")
    assert (
        parser._helper_child_unit_region(
            unit,
            parts,
            _SourceUnit("interface", None, [], start_line=5, end_line=5),
        )
        == "execution"
    )
    assert (
        parser._helper_child_unit_region(
            unit,
            parts,
            _SourceUnit("procedure", "inner", [], start_line=7, end_line=8),
        )
        == "contains"
    )

    assert parser._helper_has_preferred_unit_end_ahead(unit.lines, 0, "procedure", "work") is True
    assert parser._helper_has_preferred_unit_end_ahead(unit.lines, 0, "procedure", "missing") is False
    assert parser._helper_has_preferred_unit_end_ahead(unit.lines[:-1], 0, "procedure", "work") is False
    immediate_type = _lines("type :: immediate", "end type immediate")
    assert parser._helper_has_preferred_unit_end_ahead(immediate_type, 0, "derived_type", "immediate") is True
    assert parser._helper_has_unit_end_ahead(immediate_type, 0, "derived_type") is True
    assert parser._helper_has_unit_end_ahead(unit.lines, 2, "derived_type") is True
    assert parser._helper_has_unit_end_ahead(unit.lines, 6, "procedure") is True
    assert parser._helper_has_unit_end_ahead(unit.lines[:-1], 0, "procedure") is True

    immediate_contains = _unit("module", "owner", "module owner", "contains", "end module owner")
    assert parser._helper_direct_contains_line(immediate_contains, filename="regions.f90") == 2


def test_source_preparation_rejects_raw_cpp_and_preserves_root_units_and_source_form(tmp_path: Path):
    parser = FortranParser()
    lines, root_scope, units = parser._helper_prepare_source_units(
        """
module owner_mod
end module owner_mod
subroutine global_step()
end subroutine global_step
""",
        filename="prepare_contract.f90",
    )

    assert root_scope == _ParserScope(kind="file", name=None)
    assert [(unit.kind, unit.name, unit.start_line, unit.end_line) for unit in units] == [
        ("module", "owner_mod", 2, 3),
        ("procedure", "global_step", 4, 5),
    ]
    assert [line for line, _lineno, _source in lines if line.strip()] == [
        "module owner_mod",
        "end module owner_mod",
        "subroutine global_step()",
        "end subroutine global_step",
    ]
    assert parser._source_form("fixed.f") == "f77"
    assert parser._source_form("modern.f90") == "modern"
    assert parser._source_form(None) == "unknown"

    source_path = tmp_path / "path_input.f90"
    source_path.write_text("module from_path\nend module from_path\n", encoding="utf-8")
    assert parser._looks_like_existing_source_path(source_path) is True
    assert parser._looks_like_existing_source_path("module inline\nend module inline\n") is False
    assert parser._looks_like_existing_source_path(object()) is False

    with pytest.raises(FortranParseError) as error:
        parser._helper_prepare_source_units("#define VALUE 1\nmodule bad\nend module bad\n", filename="raw_cpp.f90")

    assert error.value.base_message == "Fortran CPP directives require compiler preprocessing before parsing."
    assert error.value.filename == "raw_cpp.f90"
    assert error.value.line_number == 1
    assert error.value.source_line == "#define VALUE 1"
    assert error.value.code == "PARSE_PREPROCESSING_REQUIRED"


def test_unit_end_and_header_validation_preserve_public_diagnostics():
    parser = FortranParser()

    assert parser._helper_parse_unit_end("module", "end module owner_mod") == (True, "owner_mod")
    assert parser._helper_parse_unit_end("block_data", "end") == (True, None)
    assert parser._helper_parse_unit_end("procedure", "end function value") == (True, "value")
    assert parser._helper_unit_end_matches("enum", "end enum") is True
    assert parser._helper_unit_label("block_data") == "block data"
    assert parser._parse_submodule_header("submodule (ancestor_mod:parent_mod) child_mod", "headers.f90").parent == (
        "parent_mod"
    )
    assert parser._split_submodule_parent("ancestor_mod:parent_mod") == ("parent_mod", "ancestor_mod")
    assert parser._split_submodule_parent("parent_mod") == ("parent_mod", None)
    assert parser._parse_interface_header("abstract interface") == (True, None)
    assert parser._parse_interface_header("interface callbacks") == (True, "callbacks")

    with pytest.raises(FortranParseError) as module_error:
        parser._parse_module_header(
            "module bad-name",
            filename="headers.f90",
            lineno=3,
            source_line="module bad-name",
        )
    assert module_error.value.base_message == "Unsupported or malformed module header: module bad-name"
    assert module_error.value.filename == "headers.f90"
    assert module_error.value.line_number == 3
    assert module_error.value.source_line == "module bad-name"
    assert module_error.value.code == "PARSE_MALFORMED_HEADER"

    with pytest.raises(FortranParseError) as procedure_error:
        parser._helper_validate_possible_unit_header(
            "module procedure bad(x)",
            filename="headers.f90",
            lineno=4,
            source_line="module procedure bad(x)",
        )
    assert (
        procedure_error.value.base_message
        == "Unsupported or malformed module procedure header: module procedure bad(x)"
    )
    assert procedure_error.value.filename == "headers.f90"
    assert procedure_error.value.line_number == 4
    assert procedure_error.value.source_line == "module procedure bad(x)"
    assert procedure_error.value.code == "PARSE_MALFORMED_HEADER"


def test_unit_part_splitting_skips_nested_units_and_preserves_executable_boundary():
    parser = FortranParser()
    unit = _unit(
        "procedure",
        "work",
        "subroutine work()",
        "integer :: counter",
        "interface",
        "  subroutine callback()",
        "  end subroutine callback",
        "end interface",
        "counter = counter + 1",
        "contains",
        "subroutine inner()",
        "end subroutine inner",
        "end subroutine work",
    )

    parts = parser._helper_split_unit_parts(unit, parser._helper_unit_grammar("procedure"), filename="parts.f90")

    assert [line for line, _lineno, _source in parts.specification] == ["integer :: counter"]
    assert [line for line, _lineno, _source in parts.execution] == ["counter = counter + 1"]
    assert parts.contains == []
    assert parts.header == unit.lines[0]
    assert parts.footer == unit.lines[-1]


def test_nonexecution_child_units_keep_specification_and_contains_children_only():
    parser = FortranParser()
    unit = _unit(
        "procedure",
        "work",
        "subroutine work()",
        "type :: local_state",
        "end type local_state",
        "call setup()",
        "interface",
        "  subroutine hidden()",
        "  end subroutine hidden",
        "end interface",
        "contains",
        "subroutine inner()",
        "end subroutine inner",
        "end subroutine work",
    )

    children = parser._helper_nonexecution_child_units(
        unit,
        parent_scope=_ParserScope(kind="procedure", name="work"),
        filename="children.f90",
    )

    assert [(child.kind, child.name, child.start_line, child.end_line) for child in children] == [
        ("derived_type", "local_state", 2, 3),
        ("procedure", "inner", 10, 11),
    ]


def test_sibling_unit_validation_ignores_unnamed_units_and_preserves_duplicate_diagnostics():
    parser = FortranParser()
    parser._helper_validate_sibling_units(
        [
            _unit("enum", None, "enum, bind(c)", "end enum"),
            _unit("enum", None, "enum, bind(c)", "end enum"),
        ],
        parent_scope=_ParserScope(kind="module", name="owner_mod"),
        filename="siblings.f90",
    )

    with pytest.raises(FortranParseError) as duplicate_module:
        parser._helper_validate_sibling_units(
            [
                _unit("module", "owner_mod", "module owner_mod", "end module owner_mod"),
                _unit("module", "Owner_Mod", "module Owner_Mod", "end module Owner_Mod"),
            ],
            parent_scope=_ParserScope(kind="file", name=None),
            filename="siblings.f90",
        )

    assert duplicate_module.value.base_message == "Duplicate module name 'Owner_Mod' in file scope."
    assert duplicate_module.value.filename == "siblings.f90"
    assert duplicate_module.value.line_number == 1
    assert duplicate_module.value.source_line == "module Owner_Mod"
    assert duplicate_module.value.code == "PARSE_DUPLICATE_UNIT"

    with pytest.raises(FortranParseError) as duplicate_procedure:
        parser._helper_validate_sibling_units(
            [
                _unit("procedure", "step", "subroutine step()", "end subroutine step"),
                _unit("procedure", "STEP", "subroutine STEP()", "end subroutine STEP"),
            ],
            parent_scope=_ParserScope(kind="module", name="owner_mod"),
            filename="siblings.f90",
        )

    assert duplicate_procedure.value.base_message == "Duplicate procedure name 'STEP' in module 'owner_mod'."
    assert duplicate_procedure.value.filename == "siblings.f90"
    assert duplicate_procedure.value.line_number == 1
    assert duplicate_procedure.value.source_line == "subroutine STEP()"
    assert duplicate_procedure.value.code == "PARSE_DUPLICATE_PROCEDURE"


def test_finalize_proc_resolves_signature_arguments_imports_and_uses_without_exposing_resolved_params():
    parser = FortranParser()
    signature = FortranProcedureSignature(
        "scale",
        "subroutine",
        arguments=[
            FortranArgument("count", base_type="integer"),
            FortranArgument("values", base_type="real", kind="rk", shape=["count"]),
        ],
    )

    finalized = parser._finalize_proc(
        {
            "signature": signature,
            "symbols": {argument.name.lower(): argument for argument in signature.arguments},
            "uses": {"precision_mod": []},
            "local_params": {"rk": "8", "count": "4"},
            "imports": {"state_t", "callback"},
            "filename": "finalize_contract.f90",
        }
    )

    assert finalized is not signature
    assert [(argument.name, argument.base_type, argument.kind, argument.shape) for argument in finalized.arguments] == [
        ("count", "integer", "", []),
        ("values", "real", "8", ["4"]),
    ]
    assert finalized.attributes == ["import(callback)", "import(state_t)"]
    assert finalized.uses == {"precision_mod": []}
    assert finalized.variables == {}


def test_finalize_proc_duplicate_argument_diagnostic_preserves_header_metadata():
    parser = FortranParser()
    signature = FortranProcedureSignature(
        "step",
        "subroutine",
        arguments=[FortranArgument("value"), FortranArgument("VALUE")],
    )

    with pytest.raises(FortranParseError) as error:
        parser._finalize_proc(
            {
                "signature": signature,
                "symbols": {},
                "uses": {},
                "filename": "finalize_contract.f90",
                "header_lineno": 12,
                "header_source_line": "subroutine step(value, VALUE)",
            }
        )

    assert error.value.base_message == "Duplicate argument name 'VALUE' in procedure 'step'."
    assert error.value.filename == "finalize_contract.f90"
    assert error.value.line_number == 12
    assert error.value.source_line == "subroutine step(value, VALUE)"
    assert error.value.code == "PARSE_DUPLICATE_ARGUMENT"


def test_compile_time_resolution_helpers_preserve_kind_shape_values_and_literal_policy():
    parser = FortranParser()
    signature = FortranProcedureSignature(
        "consume",
        "subroutine",
        module="api_mod",
        arguments=[FortranArgument("values", base_type="real", kind="rk_alias", shape=["n + 1"])],
    )
    signature.variables["local_n"] = FortranArgument(
        "local_n",
        base_type="integer",
        value="n + 2",
        symbolic_value="n + 2",
        value_type="expression",
        is_parameter=True,
    )

    parser._resolve_signature_kinds(
        signature,
        {
            "api_mod": {"rk": "4 + 4", "rk_alias": "rk", "n": "3"},
        },
    )

    assert signature.arguments[0].kind == "8"
    assert signature.arguments[0].shape == ["4"]
    assert signature.variables["local_n"].value == "5"
    assert signature.variables["local_n"].symbolic_value == "n + 2"

    module = FortranModule("api_mod")
    module.variables.append(
        FortranArgument(
            "values",
            base_type="real",
            kind="rk_alias",
            shape=["0:n"],
            value="n + 2",
            symbolic_value="n + 2",
            value_type="expression",
            is_parameter=True,
        )
    )
    parser._resolve_module_variable_kinds(module, {"api_mod": {"rk": "8", "rk_alias": "rk", "n": "3"}})

    assert module.variables[0].kind == "8"
    assert module.variables[0].shape == ["0:3"]
    assert module.variables[0].lbound == ["0"]
    assert module.variables[0].ubound == ["3"]
    assert module.variables[0].value == "5"

    assert parser._resolve_kind_expression("len=n + 1", {"n": "3"}) == "len=4"
    assert parser._resolve_symbol_reference("alias", {"alias": "target", "target": "8"}) == "8"
    assert parser._resolve_module_parameter_values({"M": {"a": "4", "b": "a + 2"}}) == {"m": {"a": "4", "b": "6"}}
    assert parser._collect_relevant_local_params(
        FortranProcedureSignature(
            "shape",
            "subroutine",
            arguments=[FortranArgument("values", kind="rk", shape=["n"])],
        ),
        {"rk": "base", "base": "4", "n": "m + 1", "m": "3", "unused": "10"},
    ) == {"rk": "base", "base": "4", "n": "m + 1", "m": "3"}
    assert parser._extract_symbol_names("n + max(m, 2) .and. flag") == {"n", "max", "m", "flag"}
    assert parser._normalize_parameter_value("2.0d+0") == "2"
    assert parser._normalize_parameter_value("selected_real_kind(12)") is None
    assert parser._is_literal_parameter_value("(/ 1, 2, .true. /)") is True
    assert parser._safe_eval_int_expr("max(3, 7) + len_trim('abc   ')") == 10
    assert parser._infer_implicit_base_type("index") == "integer"
    assert parser._infer_implicit_base_type("alpha") == "real"


def test_declaration_push_preserves_module_variables_parameters_and_bounds():
    parser = FortranParser()
    module = FortranModule("owner_mod")
    scope = _ParserScope(kind="module", name=module.name, model=module, module_owner=module.name)
    meta = parser._new_decl_meta("real", "rk")
    meta.update({"parameter": True, "shape": ["0:n"], "rank": 1})

    parser._helper_push_declaration_to_scope(
        scope,
        meta=meta,
        right="weights = 1.0_rk",
        role="module_variable",
        filename="declarations.f90",
        lineno=4,
        source_line="real(kind=rk), parameter, dimension(0:n) :: weights = 1.0_rk",
    )

    assert [(var.name, var.base_type, var.kind, var.shape, var.lbound, var.ubound) for var in module.variables] == [
        ("weights", "real", "rk", ["0:n"], ["0"], ["n"])
    ]
    assert module.variables[0].is_parameter is True
    assert module.variables[0].value == "1"
    assert module.variables[0].symbolic_value == "1.0_rk"
    assert module.variables[0].value_type == "expression"


def test_declaration_push_preserves_type_field_metadata_and_duplicate_field_diagnostic():
    parser = FortranParser()
    dtype = FortranDerivedType("state_t")
    scope = _ParserScope(kind="derived_type", name=dtype.name, model=dtype)
    meta = parser._new_decl_meta("integer", "i4")
    meta.update({"pointer": True, "shape": [":"], "rank": 1})

    parser._helper_push_declaration_to_scope(
        scope,
        meta=meta,
        right="ids, IDs",
        role="type_field",
        filename="declarations.f90",
        lineno=7,
        source_line="integer(kind=i4), pointer, dimension(:) :: ids, IDs",
    )

    assert [(field.name, field.base_type, field.kind, field.pointer, field.shape) for field in dtype.fields] == [
        ("ids", "integer", "i4", True, [":"]),
        ("IDs", "integer", "i4", True, [":"]),
    ]
    with pytest.raises(FortranParseError) as error:
        parser._validate_derived_type_fields(dtype, filename="declarations.f90")

    assert error.value.base_message == "Duplicate field 'IDs' in derived type 'state_t'."
    assert error.value.filename == "declarations.f90"
    assert error.value.code == "PARSE_DUPLICATE_FIELD"


def test_procedure_declaration_push_updates_dummy_or_records_local_type_and_duplicate_metadata():
    parser = FortranParser()
    signature = FortranProcedureSignature(
        "apply",
        "subroutine",
        arguments=[FortranArgument("callback"), FortranArgument("value")],
    )
    state = parser._new_procedure_scope_state(
        signature,
        symbols={argument.name.lower(): argument for argument in signature.arguments},
    )
    scope = _ParserScope(kind="procedure", name=signature.name, model=signature, state=state)
    proc_meta = parser._new_decl_meta("procedure", "callback_iface")
    proc_meta["external"] = True

    parser._helper_push_declaration_to_scope(
        scope,
        meta=proc_meta,
        right="callback",
        role="procedure_symbol",
        filename="declarations.f90",
        lineno=9,
        source_line="procedure(callback_iface), external :: callback",
    )
    local_meta = parser._new_decl_meta("real", "rk")
    parser._helper_push_declaration_to_scope(
        scope,
        meta=local_meta,
        right="scratch",
        role="procedure_symbol",
        filename="declarations.f90",
        lineno=10,
        source_line="real(kind=rk) :: scratch",
    )

    assert signature.arguments[0].base_type == "procedure"
    assert signature.arguments[0].kind == "callback_iface"
    assert state["external_symbols"] == {"callback"}
    assert state["declared_local_types"] == {"scratch": {"base_type": "real", "kind": "rk"}}

    with pytest.raises(FortranParseError) as error:
        parser._helper_push_declaration_to_scope(
            scope,
            meta=parser._new_decl_meta("integer", ""),
            right="callback",
            role="procedure_symbol",
            filename="declarations.f90",
            lineno=11,
            source_line="integer :: callback",
        )

    assert error.value.base_message == "Duplicate declaration of symbol 'callback' in procedure 'apply'."
    assert error.value.filename == "declarations.f90"
    assert error.value.line_number == 11
    assert error.value.source_line == "integer :: callback"
    assert error.value.code == "PARSE_DUPLICATE_DECLARATION"


def test_procedure_parameter_lines_preserve_local_parameter_state_and_duplicate_metadata():
    parser = FortranParser()
    signature = FortranProcedureSignature("shape", "subroutine", arguments=[FortranArgument("values")])
    state = parser._new_procedure_scope_state(
        signature,
        symbols={"values": signature.arguments[0]},
    )

    assert parser._handle_proc_parameter_line(
        "integer, parameter :: n = 4, m = n + 2",
        state,
        filename="parameters.f90",
        lineno=5,
        source_line="integer, parameter :: n = 4, m = n + 2",
    )
    assert state["local_params"] == {"n": "4", "m": "n + 2"}
    assert state["legacy_local_params"] == set()
    assert state["implicit_typed_symbols"] == {}

    with pytest.raises(FortranParseError) as error:
        parser._handle_proc_parameter_line(
            "integer, parameter :: n = 8",
            state,
            filename="parameters.f90",
            lineno=6,
            source_line="integer, parameter :: n = 8",
        )

    assert error.value.base_message == "Duplicate PARAMETER declaration of symbol 'n' in procedure 'shape'."
    assert error.value.filename == "parameters.f90"
    assert error.value.line_number == 6
    assert error.value.source_line == "integer, parameter :: n = 8"
    assert error.value.code == "PARSE_DUPLICATE_PARAMETER"


def test_legacy_parameter_lines_respect_implicit_none_and_implicit_typing_contracts():
    parser = FortranParser()
    strict_signature = FortranProcedureSignature("strict", "subroutine")
    strict_state = parser._new_procedure_scope_state(strict_signature, symbols={})
    strict_state["implicit_none"] = True

    with pytest.raises(FortranParseError) as error:
        parser._handle_proc_parameter_line(
            "parameter (zero = 0.0e+0)",
            strict_state,
            filename="parameters.f90",
            lineno=8,
            source_line="parameter (zero = 0.0e+0)",
        )

    assert error.value.base_message == "Unknown datatype for PARAMETER symbol 'zero' in procedure 'strict'."
    assert error.value.filename == "parameters.f90"
    assert error.value.line_number == 8
    assert error.value.source_line == "parameter (zero = 0.0e+0)"
    assert error.value.code == "PARSE_UNKNOWN_PARAMETER_TYPE"

    loose_signature = FortranProcedureSignature("loose", "subroutine")
    loose_state = parser._new_procedure_scope_state(loose_signature, symbols={})
    assert parser._handle_proc_parameter_line(
        "parameter (ival = 2, alpha = 1.0)",
        loose_state,
        filename="parameters.f90",
        lineno=9,
        source_line="parameter (ival = 2, alpha = 1.0)",
    )
    assert loose_state["local_params"] == {"ival": "2", "alpha": "1.0"}
    assert loose_state["implicit_typed_symbols"] == {"ival": "integer", "alpha": "real"}
    assert loose_state["legacy_local_params"] == set()


def test_namespace_collection_preserves_case_insensitive_dependencies_and_exact_payload(tmp_path: Path, monkeypatch):
    sources = {
        "ancestor.f90": "module Ancestor_Mod\nend module Ancestor_Mod\n",
        "parent.f90": "module Parent_Mod\n  use Ancestor_Mod\n  type :: Parent_State\n  end type Parent_State\nend module Parent_Mod\n",
        "helper.f90": "module Helper_Mod\nend module Helper_Mod\n",
        "child.f90": (
            "submodule (Ancestor_Mod:Parent_Mod) Child_Mod\n"
            "  use Helper_Mod\n"
            "  type :: Child_State\n"
            "  end type Child_State\n"
            "end submodule Child_Mod\n"
        ),
        "grandchild.f90": "submodule (Child_Mod) Grandchild_Mod\nend submodule Grandchild_Mod\n",
        "units.f90": (
            "type :: File_State\n"
            "end type File_State\n"
            "program Driver\n"
            "  use Parent_Mod\n"
            "end program Driver\n"
            "block data Init_Data\n"
            "  integer :: seed\n"
            "end block data Init_Data\n"
        ),
    }
    for filename, source in sources.items():
        (tmp_path / filename).write_text(source, encoding="utf-8")

    encodings = []
    original_read_text = Path.read_text

    def read_text(path, *args, **kwargs):
        encodings.append(kwargs.get("encoding"))
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)

    namespace = FortranParser()._helper_collect_namespace(tmp_path)

    ancestor = str(tmp_path / "ancestor.f90")
    parent = str(tmp_path / "parent.f90")
    helper = str(tmp_path / "helper.f90")
    child = str(tmp_path / "child.f90")
    grandchild = str(tmp_path / "grandchild.f90")
    units = str(tmp_path / "units.f90")

    assert encodings and set(encodings) == {"utf-8"}
    assert namespace["module_to_file"] == {
        "ancestor_mod": ancestor,
        "helper_mod": helper,
        "parent_mod": parent,
    }
    assert namespace["submodule_to_file"] == {
        "child_mod": child,
        "grandchild_mod": grandchild,
    }
    assert namespace["file_dependencies"] == {
        ancestor: [],
        child: [ancestor, helper, parent],
        grandchild: [child],
        helper: [],
        parent: [ancestor],
        units: [],
    }
    assert namespace["files"].index(ancestor) < namespace["files"].index(parent)
    assert namespace["files"].index(parent) < namespace["files"].index(child)
    assert namespace["files"].index(helper) < namespace["files"].index(child)
    assert namespace["files"].index(child) < namespace["files"].index(grandchild)
    assert {module.name for module in namespace["modules"]} == {"Ancestor_Mod", "Helper_Mod", "Parent_Mod"}
    assert {submodule.name for submodule in namespace["submodules"]} == {"Child_Mod", "Grandchild_Mod"}
    assert [program.name for program in namespace["programs"]] == ["Driver"]
    assert [block.name for block in namespace["block_data"]] == ["Init_Data"]
    assert {dtype.name for dtype in namespace["types"]} == {"Parent_State", "Child_State", "File_State"}
    assert {module.name: module.filename for module in namespace["modules"]} == {
        "Ancestor_Mod": ancestor,
        "Helper_Mod": helper,
        "Parent_Mod": parent,
    }
    assert {submodule.name: submodule.filename for submodule in namespace["submodules"]} == {
        "Child_Mod": child,
        "Grandchild_Mod": grandchild,
    }


def test_project_registries_preserve_qualified_aliases_values_and_dependencies():
    project = parse_fortran_project(
        {
            "api.f90": """
module api_mod
  type :: state_t
    integer :: id
  end type state_t
  interface callback
    subroutine on_step(x)
      integer, intent(in) :: x
    end subroutine on_step
  end interface callback
contains
  subroutine step(x)
    real, intent(in) :: x
  end subroutine step
end module api_mod
""",
            "child.f90": """
submodule (api_mod) child_mod
  type :: child_state_t
    integer :: id
  end type child_state_t
  interface child_callback
    subroutine child_step(x)
      integer, intent(in) :: x
    end subroutine child_step
  end interface child_callback
contains
  module procedure reset
  end procedure reset
end submodule child_mod
""",
            "units.f90": """
type :: global_state_t
  integer :: id
end type global_state_t
interface global_callback
  subroutine global_step()
  end subroutine global_step
end interface global_callback
program driver
  use api_mod
end program driver
""",
        }
    )

    module = project.modules["api_mod"]
    submodule = project.submodules["child_mod"]

    assert set(project.modules) == {"api_mod"}
    assert set(project.submodules) == {"child_mod"}
    assert set(project.programs) == {"driver"}
    assert project.dependencies == {
        "api_mod": set(),
        "child_mod": {"api_mod"},
        "driver": {"api_mod"},
    }
    assert set(project.procedures) == {"api_mod.step", "step", "child_mod.reset", "reset"}
    assert project.procedures["api_mod.step"] is project.procedures["step"] is module.procedures[0]
    assert project.procedures["child_mod.reset"] is project.procedures["reset"] is submodule.procedures[0]
    assert set(project.derived_types) == {
        "api_mod.state_t",
        "state_t",
        "child_mod.child_state_t",
        "child_state_t",
        "global_state_t",
    }
    assert project.derived_types["api_mod.state_t"] is project.derived_types["state_t"]
    assert project.derived_types["child_mod.child_state_t"] is project.derived_types["child_state_t"]
    assert set(project.interfaces) == {
        "api_mod.callback",
        "callback",
        "child_mod.child_callback",
        "child_callback",
        "global_callback",
    }
    assert project.interfaces["api_mod.callback"] is project.interfaces["callback"]
    assert project.interfaces["child_mod.child_callback"] is project.interfaces["child_callback"]


def test_visit_file_preserves_top_level_models_but_limits_file_symbol_registry():
    parsed = FortranParser().visit_file(
        """
type :: file_state_t
end type file_state_t
interface file_callback
  subroutine on_file()
  end subroutine on_file
end interface file_callback
subroutine global_step()
end subroutine global_step
module api_mod
contains
  subroutine module_step()
  end subroutine module_step
end module api_mod
""",
        filename="visit_file_contract.f90",
    )

    assert [dtype.name for dtype in parsed.derived_types] == ["file_state_t"]
    assert [interface.name for interface in parsed.interfaces] == ["file_callback"]
    assert [procedure.name for procedure in parsed.procedures] == ["global_step"]
    assert [module.name for module in parsed.modules] == ["api_mod"]
    assert set(parsed.symbols) == {"api_mod", "global_step"}
    assert parsed.symbols["api_mod"] is parsed.modules[0]
    assert parsed.symbols["global_step"] is parsed.procedures[0]


def test_visit_project_resolves_cross_file_used_module_parameters_once():
    project = parse_fortran_project(
        {
            "precision.f90": """
module precision_mod
  integer, parameter :: rk = 8
end module precision_mod
""",
            "api.f90": """
module api_mod
  use precision_mod
contains
  subroutine consume(value)
    real(kind=rk), intent(in) :: value
  end subroutine consume
end module api_mod
""",
        }
    )

    procedure = project.procedures["api_mod.consume"]
    assert procedure is project.procedures["consume"]
    assert procedure.arguments[0].kind == "8"
    assert project.dependencies == {
        "api_mod": {"precision_mod"},
        "precision_mod": set(),
    }


def test_visit_project_rejects_duplicate_modules_across_files_with_project_scope_metadata():
    with pytest.raises(FortranParseError) as duplicate:
        parse_fortran_project(
            {
                "first.f90": "module shared_mod\nend module shared_mod\n",
                "second.f90": "module shared_mod\nend module shared_mod\n",
            }
        )

    assert duplicate.value.base_message == "Duplicate symbol 'shared_mod' in project module scope."
    assert duplicate.value.filename is None
    assert duplicate.value.line_number is None
    assert duplicate.value.source_line is None
    assert duplicate.value.code == "PARSE_DUPLICATE_SYMBOL"


def test_project_topological_files_are_dependency_first_sorted_and_cycle_tolerant():
    ordered = FortranParser._topological_files(
        {
            "consumer.f90": {"module_a.f90", "module_b.f90"},
            "module_b.f90": set(),
            "module_a.f90": set(),
            "cycle_left.f90": {"cycle_right.f90"},
            "cycle_right.f90": {"cycle_left.f90"},
        }
    )

    assert ordered[:3] == ["module_a.f90", "module_b.f90", "consumer.f90"]
    assert ordered[3:] == ["cycle_left.f90", "cycle_right.f90"]


def test_project_encoding_is_forwarded_to_explicit_path_inputs(tmp_path: Path):
    source = tmp_path / "latin1.f90"
    source.write_bytes("! caf\xe9\nmodule encoded_mod\nend module encoded_mod\n".encode("latin-1"))

    project = parse_fortran_project([source], encoding="latin-1")

    assert project.files[0].encoding == "latin-1"
    assert project.files[0].source.startswith("! caf\xe9")


def test_project_encoding_is_forwarded_to_directory_namespace_collection(tmp_path: Path):
    source = tmp_path / "latin1.f90"
    source.write_bytes("! caf\xe9\nmodule encoded_mod\nend module encoded_mod\n".encode("latin-1"))

    project = parse_fortran_project(tmp_path, encoding="latin-1")

    assert set(project.modules) == {"encoded_mod"}
    assert project.files[0].encoding == "latin-1"
    assert project.files[0].source.startswith("! caf\xe9")


def test_scope_include_import_and_derived_type_binding_contracts():
    parser = FortranParser()
    state = {}
    parser._proc_scope_add_include(state, "shared.inc")
    parser._proc_scope_add_imports(state, ["State_T", " ", "Callback"])

    assert state == {
        "includes": ["shared.inc"],
        "imports": {"state_t", "callback"},
    }

    dtype = parser._init_derived_type(
        "type, extends(parent(kind)), public :: child",
        current_module="owner_mod",
    )
    assert dtype == FortranDerivedType(
        name="child",
        module="owner_mod",
        extends="parent(kind)",
        attributes=["public"],
    )
    malformed = parser._init_derived_type("type, extends(parent :: child", current_module="owner_mod")
    assert malformed == FortranDerivedType(
        name="child",
        module="owner_mod",
        attributes=["extends(parent"],
    )

    parser._parse_derived_type_contains_line("procedure, pass(self), public :: update, reset", dtype)
    parser._parse_derived_type_contains_line("generic, public :: assignment(=) => assign_child, assign_other", dtype)
    parser._parse_derived_type_contains_line("FINAL :: cleanup, destroy", dtype)

    assert dtype.methods == ["update", "reset"]
    assert dtype.procedure_bindings == [
        {"name": "update", "attrs": ["pass(self)", "public"]},
        {"name": "reset", "attrs": ["pass(self)", "public"]},
    ]
    assert dtype.generic_bindings == [
        {
            "name": "assignment(=)",
            "targets": ["assign_child", "assign_other"],
            "attrs": ["public"],
        }
    ]


def test_unknown_procedure_declaration_diagnostic_preserves_public_metadata():
    parser = FortranParser()
    state = {"signature": FortranProcedureSignature(name="work", kind="subroutine")}

    with pytest.raises(FortranParseError) as error:
        parser._handle_unknown_proc_declaration(
            "@@@",
            state,
            filename="procedure_contract.f90",
            lineno=8,
            source_line="@@@",
        )

    assert error.value.base_message == "Invalid Fortran syntax in procedure 'work' specification part: @@@"
    assert error.value.filename == "procedure_contract.f90"
    assert error.value.line_number == 8
    assert error.value.source_line == "@@@"
    assert error.value.code == "PARSE_INVALID_SYNTAX"


def test_unknown_procedure_declaration_kind_preserves_declaration_and_invalid_syntax_split():
    parser = FortranParser()
    state = {"signature": FortranProcedureSignature(name="work", kind="subroutine")}

    with pytest.raises(FortranParseError) as declaration_error:
        parser._handle_unknown_proc_declaration(
            "vector(kind=4) :: value",
            state,
            filename="procedure_contract.f90",
            lineno=9,
            source_line="vector(kind=4) :: value",
        )

    assert (
        declaration_error.value.base_message
        == "Unknown or unsupported datatype declaration for procedure 'work': vector(kind=4) :: value"
    )
    assert declaration_error.value.filename == "procedure_contract.f90"
    assert declaration_error.value.line_number == 9
    assert declaration_error.value.source_line == "vector(kind=4) :: value"
    assert declaration_error.value.code == "PARSE_UNSUPPORTED_DECLARATION"

    with pytest.raises(FortranParseError) as syntax_error:
        parser._handle_unknown_proc_declaration(
            "call work()",
            state,
            filename="procedure_contract.f90",
            lineno=10,
            source_line="call work()",
        )

    assert (
        syntax_error.value.base_message == "Invalid Fortran syntax in procedure 'work' specification part: call work()"
    )
    assert syntax_error.value.filename == "procedure_contract.f90"
    assert syntax_error.value.line_number == 10
    assert syntax_error.value.source_line == "call work()"
    assert syntax_error.value.code == "PARSE_INVALID_SYNTAX"


def test_contains_line_validation_accepts_spec_alternatives_without_mutating_scope_and_reports_invalid_lines():
    parser = FortranParser()
    module = FortranModule("owner_mod")
    scope = _ParserScope(kind="module", name=module.name, model=module, module_owner=module.name)

    parser._helper_validate_contains_lines(
        scope,
        _lines("", "# marker", "include 'shape.inc'", "integer :: macro_decl"),
        filename="contains_contract.f90",
    )

    assert module.variables == []

    with pytest.raises(FortranParseError) as error:
        parser._helper_validate_contains_lines(
            scope,
            _lines("@@@"),
            filename="contains_contract.f90",
        )

    assert error.value.base_message == "Invalid Fortran syntax in module 'owner_mod' contains part: @@@"
    assert error.value.filename == "contains_contract.f90"
    assert error.value.line_number == 1
    assert error.value.source_line == "@@@"
    assert error.value.code == "PARSE_INVALID_SYNTAX"


def test_malformed_type_bound_declaration_diagnostic_preserves_public_metadata():
    parser = FortranParser()
    dtype = FortranDerivedType("state_t")

    with pytest.raises(FortranParseError) as error:
        parser._parse_derived_type_contains_line(
            "FINAL :: 123",
            dtype,
            filename="type_bound_contract.f90",
            lineno=9,
            source_line="FINAL :: 123",
        )

    assert error.value.base_message == "Unsupported or malformed type-bound declaration in type 'state_t': FINAL :: 123"
    assert error.value.filename == "type_bound_contract.f90"
    assert error.value.line_number == 9
    assert error.value.source_line == "FINAL :: 123"
    assert error.value.code == "PARSE_UNSUPPORTED_TYPE_BOUND_DECLARATION"


def test_interface_and_enum_validation_keep_scanning_after_valid_lines():
    parser = FortranParser()
    scope = _ParserScope(kind="interface", name="Callbacks")

    with pytest.raises(FortranParseError) as interface_error:
        parser._helper_validate_interface_lines(
            scope,
            _lines("", "# marker", "MODULE PROCEDURE :: First, Second", "PROCEDURE(Callback) :: Handler", "@@@"),
            filename="interface_contract.f90",
        )
    assert interface_error.value.base_message == "Invalid Fortran syntax in interface 'Callbacks': @@@"
    assert interface_error.value.filename == "interface_contract.f90"
    assert interface_error.value.line_number == 5
    assert interface_error.value.source_line == "@@@"
    assert interface_error.value.code == "PARSE_INVALID_SYNTAX"

    valid_enum = _unit("enum", None, "enum, bind(c)", "", "# marker", "ENUMERATOR :: First = 1, Second", "end enum")
    parser._helper_validate_enum_unit(valid_enum, filename="enum_contract.f90")

    invalid_enum = _unit("enum", None, "enum, bind(c)", "enumerator :: valid = 1", "integer :: invalid", "end enum")
    with pytest.raises(FortranParseError) as enum_error:
        parser._helper_validate_enum_unit(invalid_enum, filename="enum_contract.f90")
    assert enum_error.value.base_message == "Invalid Fortran syntax in enum specification part: integer :: invalid"
    assert enum_error.value.filename == "enum_contract.f90"
    assert enum_error.value.line_number == 3
    assert enum_error.value.source_line == "integer :: invalid"
    assert enum_error.value.code == "PARSE_INVALID_SYNTAX"


@pytest.mark.parametrize(
    ("visitor_name", "unit", "expected_message"),
    [
        (
            "_helper_validate_enum_unit",
            _unit("enum", None, "enum, bind(c)", "type :: nested", "end type nested", "end enum"),
            "Invalid Fortran syntax in enum '<unnamed>' specification part: type :: nested",
        ),
        (
            "visit_interface_unit",
            _unit(
                "interface", "callbacks", "interface callbacks", "type :: nested", "end type nested", "end interface"
            ),
            "Invalid Fortran syntax in interface 'callbacks': type :: nested",
        ),
        (
            "visit_derived_type_unit",
            _unit("derived_type", "outer", "type :: outer", "type :: nested", "end type nested", "end type outer"),
            "Invalid Fortran syntax in derived type 'outer' specification part: type :: nested",
        ),
        (
            "visit_block_data_source_unit",
            _unit(
                "block_data",
                "init_data",
                "block data init_data",
                "type :: nested",
                "end type nested",
                "end block data init_data",
            ),
            "Invalid Fortran syntax in block data 'init_data' specification part: type :: nested",
        ),
    ],
)
def test_nested_units_rejected_by_restricted_scopes_preserve_public_metadata(visitor_name, unit, expected_message):
    parser = FortranParser()
    visitor = getattr(parser, visitor_name)

    with pytest.raises(FortranParseError) as error:
        if visitor_name == "_helper_validate_enum_unit":
            visitor(unit, filename="nested_contract.f90")
        else:
            visitor(unit, parent_scope=_ParserScope(kind="file", name=None), filename="nested_contract.f90")

    assert error.value.base_message == expected_message
    assert error.value.filename == "nested_contract.f90"
    assert error.value.line_number == 2
    assert error.value.source_line == "type :: nested"
    assert error.value.code == "PARSE_INVALID_SYNTAX"


@pytest.mark.parametrize(
    ("line", "expected_message", "expected_code"),
    [
        (
            "!$omp threadprivate(counter)",
            "Unsupported OpenMP declarative directive in module 'owner_mod': !$omp threadprivate(counter)",
            "PARSE_UNSUPPORTED_OPENMP_DIRECTIVE",
        ),
        (
            "type :: missing_end",
            "Missing end derived type for derived type 'missing_end'.",
            "PARSE_MISSING_DERIVED_TYPE_END",
        ),
        (
            "call work()",
            "Executable statement is not allowed in module specification part 'owner_mod': call work()",
            "PARSE_EXECUTABLE_IN_SPECIFICATION",
        ),
        (
            "@@@",
            "Invalid Fortran syntax in module 'owner_mod' specification part: @@@",
            "PARSE_INVALID_SYNTAX",
        ),
        (
            "weirdtype value",
            "Unknown or unsupported datatype declaration in module 'owner_mod': weirdtype value",
            "PARSE_UNSUPPORTED_DECLARATION",
        ),
    ],
)
def test_module_like_spec_diagnostics_preserve_public_metadata(line, expected_message, expected_code):
    parser = FortranParser()
    module = FortranModule("owner_mod")
    scope = _ParserScope(kind="module", name=module.name, model=module, module_owner=module.name)

    with pytest.raises(FortranParseError) as error:
        parser._helper_visit_module_like_spec_line(
            scope,
            line,
            filename="module_contract.f90",
            lineno=7,
            source_line=line,
        )

    assert error.value.base_message == expected_message
    assert error.value.filename == "module_contract.f90"
    assert error.value.line_number == 7
    assert error.value.source_line == line
    assert error.value.code == expected_code


@pytest.mark.parametrize(
    ("line", "expected_message", "expected_code"),
    [
        (
            "type :: missing_end",
            "Missing end derived type for derived type 'missing_end'.",
            "PARSE_MISSING_DERIVED_TYPE_END",
        ),
        (
            "!$omp threadprivate(counter)",
            "Unsupported OpenMP declarative directive in type 'state_t': !$omp threadprivate(counter)",
            "PARSE_UNSUPPORTED_OPENMP_DIRECTIVE",
        ),
        (
            "@@@",
            "Invalid Fortran syntax in type 'state_t' specification part: @@@",
            "PARSE_INVALID_SYNTAX",
        ),
        (
            "weirdtype value",
            "Unknown or unsupported datatype declaration in type 'state_t': weirdtype value",
            "PARSE_UNSUPPORTED_DECLARATION",
        ),
    ],
)
def test_type_spec_diagnostics_preserve_public_metadata(line, expected_message, expected_code):
    parser = FortranParser()
    dtype = FortranDerivedType("state_t")
    scope = _ParserScope(kind="derived_type", name=dtype.name, model=dtype)

    with pytest.raises(FortranParseError) as error:
        parser._helper_visit_type_spec_line(
            line,
            scope,
            filename="type_contract.f90",
            lineno=7,
            source_line=line,
        )

    assert error.value.base_message == expected_message
    assert error.value.filename == "type_contract.f90"
    assert error.value.line_number == 7
    assert error.value.source_line == line
    assert error.value.code == expected_code


@pytest.mark.parametrize(
    ("visitor_name", "entity_name"),
    [
        ("visit_fortran_module", "module"),
        ("visit_fortran_submodule", "submodule"),
        ("visit_fortran_interface", "interface"),
        ("visit_fortran_derived_type", "derived type"),
        ("visit_fortran_program", "program"),
        ("visit_fortran_block_data_unit", "block data unit"),
    ],
)
def test_singular_parser_entrypoint_diagnostics_preserve_names_entities_and_filename(visitor_name, entity_name):
    parser = FortranParser()

    with pytest.raises(FortranParseError) as error:
        getattr(parser, visitor_name)("", filename="empty_contract.f90")

    assert error.value.base_message == f"{visitor_name}() expected exactly one {entity_name}, but none were found"
    assert error.value.filename == "empty_contract.f90"
    assert error.value.code == "PARSE_WRONG_ENTRYPOINT"


@pytest.mark.parametrize(
    ("visitor_name", "header_parser", "header_result", "unit_kind", "entity_name"),
    [
        ("visit_module_unit", "_parse_module_header", None, "module", "module"),
        ("visit_submodule_unit", "_parse_submodule_header", None, "submodule", "submodule"),
        ("visit_program_unit", "_parse_program_header", None, "program", "program"),
        ("visit_block_data_source_unit", "_parse_block_data_header", None, "block_data", "block data"),
        ("visit_derived_type_unit", "_init_derived_type", None, "derived_type", "derived-type"),
        ("visit_interface_unit", "_parse_interface_header", (False, None), "interface", "interface"),
    ],
)
def test_source_unit_visitor_defensive_diagnostics_preserve_public_metadata(
    monkeypatch,
    visitor_name,
    header_parser,
    header_result,
    unit_kind,
    entity_name,
):
    parser = FortranParser()
    monkeypatch.setattr(parser, header_parser, lambda *args, **kwargs: header_result)

    with pytest.raises(FortranParseError) as error:
        getattr(parser, visitor_name)(
            _unit(unit_kind, "broken", "broken header", "broken footer"),
            parent_scope=_ParserScope(kind="file", name=None),
            filename="visitor_contract.f90",
        )

    assert error.value.base_message == f"Expected {entity_name} unit."
    assert error.value.filename == "visitor_contract.f90"
    assert error.value.line_number == 1
    assert error.value.source_line == "broken header"
    assert error.value.code == "PARSE_EXPECTED_UNIT"


def test_derived_type_collection_retains_sibling_and_nested_scope_contexts():
    parser = FortranParser()
    types = parser._collect_derived_type_source_units(
        """
type :: global_state
end type global_state
module owner_mod
  type :: first_state
  end type first_state
  type :: second_state
  end type second_state
contains
  subroutine work()
    type :: local_state
    end type local_state
  end subroutine work
end module owner_mod
""",
        filename="nested_types.f90",
    )

    assert [(unit.name, scope.kind, scope.name, scope.module_owner) for unit, scope in types] == [
        ("global_state", "file", None, None),
        ("first_state", "module", "owner_mod", "owner_mod"),
        ("second_state", "module", "owner_mod", "owner_mod"),
        ("local_state", "procedure", "work", "owner_mod"),
    ]
    assert [(scope.parent.kind, scope.parent.name) if scope.parent else None for _unit, scope in types] == [
        None,
        ("file", None),
        ("file", None),
        ("module", "owner_mod"),
    ]


def test_unit_models_preserve_filename_propagation():
    parsed = parse_fortran_file(
        """
module owner_mod
end module owner_mod
submodule (owner_mod) child_mod
end submodule child_mod
program driver
end program driver
block data init_data
end block data init_data
""",
        filename="unit_models.f90",
    )

    assert parsed.modules[0].filename == "unit_models.f90"
    assert parsed.submodules[0].filename == "unit_models.f90"
    assert parsed.programs[0].filename == "unit_models.f90"
    assert parsed.block_data_units[0].filename == "unit_models.f90"
