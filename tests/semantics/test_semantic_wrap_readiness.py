import json
import subprocess
import sys
from pathlib import Path

import pytest

from x2py import parse_fortran_file
from x2py.semantics.fortran2ir import fortran_module_to_semantic_module
from x2py.semantics.models import (
    EXTERNAL_TYPE_REF_METADATA,
    POLICY_COMPLETION_PREPARED_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    SemanticArrayContract,
    SemanticArgument,
    SemanticClass,
    SemanticConstraint,
    SemanticFunction,
    SemanticImport,
    SemanticImportItem,
    SemanticMethod,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
    SemanticType,
)
from x2py.semantics.pyi2ir import parse_pyi_text
from x2py.semantics.readiness import (
    _SemanticTypeIndex,
    _constant_names,
    _constant_values,
    _import_index,
    _is_external_type_ref,
    _is_public,
    _iter_expression_values,
    _shape_expressions,
    _shape_symbols,
    assess_pyi_wrap_readiness,
    assess_semantic_wrap_readiness,
)
from x2py import cli as x2py_cli


TEST_FILE = Path(__file__).parent.parent / "data" / "fortran" / "general" / "basic_subroutine.f90"


def _readiness_from_pyi(source: str):
    module = parse_pyi_text(source, module_name="solver")
    return assess_semantic_wrap_readiness(module, source="solver.pyi")


def _blocker_codes(report: dict) -> set[str]:
    return {blocker["code"] for blocker in report["wrappability_blockers"]}


def test_readiness_completes_policy_before_blocker_checks():
    module = SemanticModule(
        name="policy_ready",
        functions=[
            SemanticFunction(
                "scale",
                arguments=[SemanticArgument("values", SemanticType("Float64", dtype="Float64", rank=1))],
            )
        ],
    )

    report = assess_semantic_wrap_readiness(module)

    assert report["wrappable"] is True
    assert module.metadata[POLICY_COMPLETION_PREPARED_METADATA] is True
    decision = module.functions[0].arguments[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert decision.transfer.value == "call_local"


def test_readiness_blocks_generic_constraints_that_have_no_runtime_validator():
    report = _readiness_from_pyi(
        """
def solve(value: Annotated[Int32, Bounded(1, 8), Finite]) -> Int32: ...
"""
    )

    blocker = next(
        item for item in report["wrappability_blockers"] if item["code"] == "fortran_runtime_constraints_unsupported"
    )
    assert blocker["items"] == [
        {
            "owner": "solver.solve.value",
            "item": "value",
            "constraints": ["Bounded", "Finite"],
        }
    ]


def _write_ready_fortran(path: Path) -> Path:
    path.write_text(
        """module m
contains
  subroutine work(n)
    integer, intent(in) :: n
  end subroutine work
end module m
""",
        encoding="utf-8",
    )
    return path


def test_completed_pyi_interface_is_semantically_ready():
    report = _readiness_from_pyi(
        """
from typing import Callable, Final

rk: Final[Int32] = 8
nmax: Final[Int32] = 32

class sim_state:
    n: Int32
    values: Float64[n]

def step(
    state: sim_state,
    t: Float64,
    objective: Callable[[sim_state, Float64], Float64],
    scratch: Float64[nmax]
) -> tuple[Returns["state", sim_state], Returns["score", Float64]]: ...
"""
    )

    assert report["wrappable"] is True
    assert report["wrappability_blockers"] == []


def test_allocatable_policy_blockers_are_reported_for_only_unsupported_cases():
    report = _readiness_from_pyi(
        """
values: Annotated[Float64[:], Allocatable]
target_values: Annotated[Float64[:], Allocatable, Aliased]

def fill() -> Returns["values", Annotated[Float64[:], Allocatable]]: ...

def make_values() -> Annotated[Float64[:], Allocatable]: ...

def make_pair() -> tuple[Returns["left", Annotated[Float64[:], Allocatable]], Returns["right", Annotated[Float64[:], Allocatable]]]: ...
"""
    )

    assert report["wrappable"] is True
    assert "allocatable_replacement_policy_missing" not in _blocker_codes(report)
    assert "allocatable_owner_policy_missing" not in _blocker_codes(report)
    assert "allocatable_multiple_copy_returns_unsupported" not in _blocker_codes(report)
    assert report["wrappability_blockers"] == []


def test_explicit_borrowed_module_allocatable_requires_aliased_storage():
    report = _readiness_from_pyi(
        """
values: Annotated[
    Float64[:],
    Allocatable,
    Ownership("native"),
    Transfer("borrowed_view"),
    Destruction("native_owner"),
]
"""
    )

    assert report["wrappable"] is False
    blocker = next(
        blocker for blocker in report["wrappability_blockers"] if blocker["code"] == "fortran_ownership_policy_blocked"
    )
    assert blocker["items"] == [
        {
            "owner": "solver.values",
            "item": "values",
            "policy": "borrowed module allocatable views require Aliased storage",
        }
    ]


def test_plain_derived_module_object_uses_snapshot_and_borrowing_requires_aliased_storage():
    plain = _readiness_from_pyi(
        """
class box:
    value: Float64

current: box
"""
    )

    assert plain["wrappable"] is True
    assert plain["wrappability_blockers"] == []

    explicit_borrow = _readiness_from_pyi(
        """
class box:
    value: Float64

current: Annotated[
    box,
    Ownership("native"),
    Transfer("borrowed_view"),
    Destruction("native_owner"),
]
"""
    )
    explicit_blocker = next(
        item for item in explicit_borrow["wrappability_blockers"] if item["code"] == "fortran_ownership_policy_blocked"
    )
    assert explicit_blocker["items"][0]["policy"] == ("borrowed derived module objects require Aliased storage")

    aliased = _readiness_from_pyi(
        """
class box:
    value: Float64

current: Annotated[box, Aliased]
"""
    )

    assert aliased["wrappable"] is True
    assert aliased["wrappability_blockers"] == []


def test_derived_module_snapshot_blocks_unsupported_nested_pointer_fields():
    report = _readiness_from_pyi(
        """
class box:
    values: Annotated[Float64[:], Pointer]

current: box
"""
    )

    assert report["wrappable"] is False
    blocker = next(
        item for item in report["wrappability_blockers"] if item["code"] == "fortran_ownership_policy_blocked"
    )
    assert {
        "owner": "solver.current",
        "item": "current",
        "policy": "snapshot field box.values is a pointer array without a completed pointer snapshot policy",
    } in blocker["items"]


def test_pointer_module_variable_uses_snapshot_or_block_ownership_policy():
    parsed = parse_fortran_file(
        """
module pointer_module_mod
  real(8), pointer :: values(:)
end module pointer_module_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])

    report = assess_semantic_wrap_readiness(module)

    blocker = next(
        blocker for blocker in report["wrappability_blockers"] if blocker["code"] == "fortran_ownership_policy_blocked"
    )
    assert blocker["items"] == [
        {
            "owner": "pointer_module_mod.values",
            "item": "values",
            "policy": "pointer array owner, lifetime, shape, and release policy are unknown",
        }
    ]


def test_allocatable_scalar_derived_replacement_reports_precise_blocker():
    parsed = parse_fortran_file(
        """
module alloc_scalar_mod
  type :: item
    integer :: value
  end type item
contains
  subroutine replace(value)
    type(item), allocatable, intent(inout) :: value
  end subroutine replace
end module alloc_scalar_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])
    report = assess_semantic_wrap_readiness(module, source="alloc_scalar_mod.f90")

    blocker = next(
        blocker
        for blocker in report["wrappability_blockers"]
        if blocker["code"] == "allocatable_scalar_replacement_unsupported"
    )
    assert blocker["items"] == [
        {"owner": "alloc_scalar_mod.replace", "item": "value"},
    ]


def test_allocatable_scalar_character_replacement_reports_precise_blocker():
    parsed = parse_fortran_file(
        """
module alloc_character_mod
contains
  subroutine replace(label)
    character(len=:), allocatable, intent(inout) :: label
  end subroutine replace
end module alloc_character_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])
    report = assess_semantic_wrap_readiness(module, source="alloc_character_mod.f90")

    blocker = next(
        blocker
        for blocker in report["wrappability_blockers"]
        if blocker["code"] == "allocatable_scalar_replacement_unsupported"
    )
    assert blocker["items"] == [
        {"owner": "alloc_character_mod.replace", "item": "label"},
    ]


def test_pointer_write_policy_blockers_are_reported_for_writable_dummies():
    report = _readiness_from_pyi(
        """
def inspect(values: Annotated[Float64[:], Pointer]) -> None: ...

def attach() -> Returns["values", Annotated[Float64[:], Pointer]]: ...

def replace(values: Annotated[Float64[:], Pointer]) -> Returns["values", Annotated[Float64[:], Pointer]]: ...

def choose() -> Annotated[Float64[:], Pointer]: ...
"""
    )

    pointer_blocker = next(
        blocker
        for blocker in report["wrappability_blockers"]
        if blocker["code"] == "fortran_pointer_output_policy_missing"
    )
    assert pointer_blocker["items"] == [
        {"owner": "solver.inspect", "item": "values"},
        {"owner": "solver.attach", "item": "values"},
        {"owner": "solver.replace", "item": "values"},
    ]


def test_bind_c_scalar_without_iso_c_kind_reports_readiness_blocker():
    parsed = parse_fortran_file(
        """
module bad_bind_mod
contains
  integer function unsafe(n) bind(C) result(res)
    integer, value, intent(in) :: n
    res = n
  end function unsafe
end module bad_bind_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])
    report = assess_semantic_wrap_readiness(module, source="bad_bind_mod.f90")

    blocker = next(
        blocker for blocker in report["wrappability_blockers"] if blocker["code"] == "fortran_bind_c_abi_unsupported"
    )
    assert blocker["items"] == [
        {"owner": "bad_bind_mod.unsafe", "item": "n"},
        {"owner": "bad_bind_mod.unsafe", "item": "return"},
    ]


def test_remaining_fortran_array_contracts_report_readiness_blockers():
    parsed = parse_fortran_file(
        """
module array_contract_mod
  type :: item
    integer :: value
  end type item
contains
  subroutine assumed_rank(values)
    real(8), intent(in) :: values(..)
  end subroutine assumed_rank
  subroutine character_array(labels)
    character(len=4), intent(in) :: labels(:)
  end subroutine character_array
  subroutine derived_array(items)
    type(item), intent(in) :: items(:)
  end subroutine derived_array
  subroutine high_rank(values)
    real(8), intent(in) :: values(:, :, :, :, :, :, :, :, :, :, :, :, :, :, :, :)
  end subroutine high_rank
end module array_contract_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])
    assumed_type = SemanticType(
        "Any",
        rank=1,
        dtype="Any",
        origin=SemanticOrigin(source_language="fortran", source_type="type(*)"),
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=1, shape=[":"], source_shape=[":"]),
        ),
    )
    module.functions.append(
        SemanticFunction(
            "assumed_type",
            arguments=[SemanticArgument("values", assumed_type)],
        )
    )

    report = assess_semantic_wrap_readiness(module, source="array_contract_mod.f90")

    assert _blocker_codes(report) >= {
        "fortran_assumed_type_policy_missing",
        "fortran_derived_type_array_policy_missing",
        "fortran_array_rank_unsupported",
    }
    assert "fortran_character_array_unsupported" not in _blocker_codes(report)
    assert "fortran_assumed_rank_policy_missing" not in _blocker_codes(report)


def test_polymorphic_arguments_block_except_type_bound_passed_object():
    parsed = parse_fortran_file(
        """
module polymorphic_readiness_mod
  type :: base
  contains
    procedure :: touch
  end type base
contains
  subroutine touch(self)
    class(base), intent(inout) :: self
  end subroutine touch
  subroutine accept(value)
    class(base), intent(in) :: value
  end subroutine accept
  subroutine replace(value)
    class(base), intent(inout) :: value
  end subroutine replace
end module polymorphic_readiness_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])

    report = assess_semantic_wrap_readiness(module, source="polymorphic_readiness_mod.f90")

    blocker = next(
        blocker
        for blocker in report["wrappability_blockers"]
        if blocker["code"] == "fortran_polymorphic_policy_missing"
    )
    assert blocker["items"] == [{"owner": "polymorphic_readiness_mod.replace", "item": "value"}]


def test_abstract_types_and_deferred_bindings_report_readiness_blockers():
    parsed = parse_fortran_file(
        """
module abstract_readiness_mod
  type, abstract :: shape
  contains
    procedure, deferred :: area
  end type shape
end module abstract_readiness_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])

    report = assess_semantic_wrap_readiness(module, source="abstract_readiness_mod.f90")

    assert _blocker_codes(report) >= {
        "fortran_abstract_type_policy_missing",
        "fortran_deferred_type_bound_procedure_unsupported",
    }


def test_imported_type_can_complete_semantic_readiness():
    report = _readiness_from_pyi(
        """
from state_mod import sim_state

def step(state: sim_state) -> Returns["state", sim_state]: ...
"""
    )

    assert report["wrappable"] is True


def test_missing_semantic_type_blocks_readiness():
    report = _readiness_from_pyi(
        """
def step(state: sim_state) -> Returns["state", sim_state]: ...
"""
    )

    assert report["wrappable"] is False
    assert "unresolved_semantic_types" in _blocker_codes(report)


def test_shape_argument_makes_shape_symbol_ready():
    report = _readiness_from_pyi(
        """
def fill(n: Int32, x: Float64[n]) -> None: ...
"""
    )

    assert report["wrappable"] is True


def test_final_constant_needs_literal_value_for_shape_readiness():
    report = _readiness_from_pyi(
        """
n: Final[Int32]

def fill(x: Float64[n]) -> None: ...
"""
    )

    assert report["wrappable"] is False
    assert "missing_compile_time_values" in _blocker_codes(report)


def test_final_constant_literal_value_makes_shape_ready():
    report = _readiness_from_pyi(
        """
n: Final[Int32] = 16

def fill(x: Float64[n]) -> None: ...
"""
    )

    assert report["wrappable"] is True


def test_callback_placeholder_blocks_until_callable_signature_is_supplied():
    report = _readiness_from_pyi(
        """
def integrate(objective: Procedure, x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is False
    assert "callback_signature_incomplete" in _blocker_codes(report)
    blocker = report["wrappability_blockers"][0]["items"][0]
    assert blocker["needs"] == [
        "callback argument order",
        "callback argument types",
        "callback return type",
    ]


def test_callable_with_signature_makes_callback_ready():
    report = _readiness_from_pyi(
        """
from typing import Callable

def integrate(objective: Callable[[Float64], Float64], x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is True


def test_callable_without_argument_list_is_not_enough_for_readiness():
    report = _readiness_from_pyi(
        """
from typing import Callable

def integrate(objective: Callable[..., Float64], x0: Float64) -> Float64: ...
"""
    )

    assert report["wrappable"] is False
    assert "callback_signature_incomplete" in _blocker_codes(report)


def test_assess_pyi_wrap_readiness_expands_directory_and_uses_leaf_filenames(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    first = tmp_path / "first.pyi"
    second = nested / "second.pyi"
    ignored = nested / "ignored.txt"
    first.write_text("def first(x: Int32) -> None: ...\n", encoding="utf-8")
    second.write_text("def second(x: Int32) -> None: ...\n", encoding="utf-8")
    ignored.write_text("not a stub", encoding="utf-8")

    report = assess_pyi_wrap_readiness([tmp_path, first])

    assert report["wrappable"] is True
    assert report["n_modules"] == 2
    assert report["source"] == [str(first), str(second)]
    assert _blocker_codes(report) == set()


def test_assess_pyi_wrap_readiness_honors_explicit_encoding(tmp_path: Path):
    pyi = tmp_path / "latin1.pyi"
    pyi.write_bytes('label: Final[String] = "caf\xe9"\n'.encode("latin-1"))

    report = assess_pyi_wrap_readiness(pyi, encoding="latin-1")

    assert report["wrappable"] is True
    assert report["source"] == [str(pyi)]
    assert _blocker_codes(report) == set()


def test_readiness_reports_unsupported_module_variable_initializer(tmp_path: Path):
    pyi = tmp_path / "labels.pyi"
    pyi.write_text('label: String = "ready"\n', encoding="utf-8")

    report = assess_pyi_wrap_readiness(pyi)

    assert report["wrappable"] is False
    assert "module_variable_initializer_unsupported" in _blocker_codes(report)
    blocker = next(
        blocker
        for blocker in report["wrappability_blockers"]
        if blocker["code"] == "module_variable_initializer_unsupported"
    )
    assert blocker["items"] == [
        {
            "owner": "labels.label",
            "item": "label",
            "setter_action": "reject_replacement",
            "reason": "completed setter policy does not expose write-through native assignment",
        }
    ]


def test_readiness_skips_private_api_and_normalizes_metadata_blocker_items():
    module = SemanticModule(
        name="policy",
        metadata={
            "readiness_blockers": [
                "ignored",
                {"code": "default_item", "message": "default", "item": {"detail": "fallback"}},
                {
                    "code": "scalar_item",
                    "message": "scalar",
                    "items": "detail text",
                    "unit": "policy.override",
                    "unit_kind": "policy",
                },
            ]
        },
        variables=[SemanticArgument("hidden", SemanticType("Undeclared"), visibility="private")],
        classes=[
            SemanticClass(
                name="Private", fields=[SemanticArgument("missing", SemanticType("Undeclared"))], visibility="private"
            ),
            SemanticClass(
                name="Public",
                methods=[
                    SemanticMethod(
                        name="hidden",
                        arguments=[SemanticArgument("missing", SemanticType("Undeclared"))],
                        visibility="private",
                    ),
                    SemanticMethod(name="ready", arguments=[SemanticArgument("value", SemanticType("Int32"))]),
                ],
            ),
        ],
        functions=[
            SemanticFunction(
                name="hidden", arguments=[SemanticArgument("missing", SemanticType("Undeclared"))], visibility="private"
            )
        ],
    )

    report = assess_semantic_wrap_readiness(module)
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}

    assert set(blockers) == {"default_item", "scalar_item"}
    assert blockers["default_item"]["items"][0]["detail"] == "fallback"
    assert blockers["scalar_item"]["items"][0]["detail"] == "detail text"
    units = {unit["unit"]: unit for unit in report["unit_blockers"]}
    assert set(units) == {"policy", "policy.override"}
    assert units["policy.override"]["kind"] == "policy"


def test_readiness_accepts_qualified_types_from_imported_modules_and_aliases():
    report = _readiness_from_pyi(
        """
import state_mod
import mesh_mod as mesh
from values_mod import value_t as imported_value

def step(a: state_mod.state_t, b: mesh.mesh_t, c: imported_value) -> None: ...
"""
    )

    assert report["wrappable"] is True


def test_readiness_empty_public_surface_and_nested_expression_utility():
    report = assess_semantic_wrap_readiness(SemanticModule(name="empty"))

    assert report == {
        "wrappable": False,
        "source": None,
        "n_modules": 1,
        "n_functions": 0,
        "n_classes": 0,
        "n_variables": 0,
        "wrappability_blockers": [
            {
                "code": "no_public_api",
                "message": "The semantic interface does not declare any public wrapper API.",
                "items": [{"owner": "<semantic-ir>", "needs": ["public function, class, or variable"]}],
            }
        ],
        "unit_blockers": [
            {
                "unit": "<semantic-ir>",
                "kind": "module",
                "blockers": [
                    {
                        "code": "no_public_api",
                        "message": "The semantic interface does not declare any public wrapper API.",
                        "items": [{"owner": "<semantic-ir>", "needs": ["public function, class, or variable"]}],
                    }
                ],
            }
        ],
        "why_not_wrappable": ["The semantic interface does not declare any public wrapper API."],
    }
    assert list(_iter_expression_values({"a": ["n", ("m", {"deep": "k"})]})) == ["n", "m", "k"]


def test_readiness_helpers_cover_indexes_constants_shapes_and_visibility():
    imported_modules, aliases, imported_types = _import_index(
        [
            " pkg.mod as short ",
            " pkg.sub ",
            SemanticImport(
                "types_mod",
                [
                    SemanticImportItem("raw_t", "renamed_t"),
                    SemanticImportItem("plain_t"),
                ],
            ),
        ]
    )
    assert imported_modules == {"pkg.mod", "pkg.sub", "types_mod"}
    assert aliases == {"short"}
    assert imported_types == {
        "renamed_t",
        "plain_t",
        "types_mod.raw_t",
        "types_mod.renamed_t",
        "types_mod.plain_t",
    }

    module = SemanticModule(
        name="solver",
        classes=[SemanticClass("local_t")],
        imports=[
            "pkg.mod as short",
            "pkg.sub",
            SemanticImport("types_mod", [SemanticImportItem("raw_t", "renamed_t")]),
        ],
    )
    index = _SemanticTypeIndex([module])
    assert index.is_known_type("Int32", module) is True
    assert index.is_known_type("local_t", module) is True
    assert index.is_known_type("solver.local_t", module) is True
    assert index.is_known_type("renamed_t", module) is True
    assert index.is_known_type("types_mod.raw_t", module) is True
    assert index.is_known_type("types_mod.extra_t", module) is True
    assert index.is_known_type("pkg.sub.extra_t", module) is True
    assert index.is_known_type("short.extra_t", module) is True
    assert index.is_known_type("short.deep.extra_t", module) is True
    assert index.is_known_type("missing_t", module) is False
    assert index.is_known_type("missing.extra_t", module) is False

    constants = [
        SemanticArgument("n", SemanticType("Int32", constraints=[SemanticConstraint("Constant")]), default_value="8"),
        SemanticArgument("unset", SemanticType("Int32", constraints=[SemanticConstraint("Constant")])),
        SemanticArgument("ordinary", SemanticType("Int32"), default_value="5"),
    ]
    assert _constant_values(constants) == {"n": "8"}
    assert _constant_names(constants) == {"n", "unset"}

    semantic_type = SemanticType(
        "Float64",
        shape=["n"],
        storage=SemanticStorageContract(array=SemanticArrayContract(shape=["m", "k + 1"])),
    )
    assert _shape_expressions(semantic_type) == ["n", "m", "k + 1"]
    assert _shape_symbols("2 * n + state.width + _hidden") == {"n", "state", "width", "_hidden"}
    assert _is_public(SemanticFunction("visible")) is True
    assert _is_public(SemanticFunction("hidden", visibility="private")) is False

    external = SemanticType(
        "external_t",
        metadata={
            EXTERNAL_TYPE_REF_METADATA: {
                "name": "external_t",
                "origin_module": "external_mod",
                "representation": "opaque",
            }
        },
    )
    assert _is_external_type_ref(external) is True
    external.metadata[EXTERNAL_TYPE_REF_METADATA]["representation"] = "unsupported"
    assert _is_external_type_ref(external) is False


def test_readiness_reports_unknown_shapes_and_accepts_external_references():
    external = SemanticType(
        "external_t",
        metadata={
            EXTERNAL_TYPE_REF_METADATA: {
                "name": "external_t",
                "origin_module": "external_mod",
                "representation": "wrapped",
            }
        },
    )
    module = SemanticModule(
        "shapes",
        functions=[
            SemanticFunction(
                "run",
                arguments=[
                    SemanticArgument("x", SemanticType("Float64", shape=["missing + 1"])),
                    SemanticArgument("external", external),
                ],
            )
        ],
    )

    report = assess_semantic_wrap_readiness(module)

    assert report["wrappability_blockers"] == [
        {
            "code": "unresolved_shape_symbols",
            "message": "Some shape expressions refer to symbols not supplied by the semantic interface.",
            "items": [{"owner": "shapes.run.x", "item": "x", "symbol": "missing", "expression": "missing + 1"}],
        }
    ]
    assert report["unit_blockers"] == [
        {
            "unit": "shapes.run",
            "kind": "function",
            "blockers": [
                {
                    "code": "unresolved_shape_symbols",
                    "message": "Some shape expressions refer to symbols not supplied by the semantic interface.",
                    "items": [{"owner": "shapes.run.x", "item": "x", "symbol": "missing", "expression": "missing + 1"}],
                }
            ],
        }
    ]


def test_readiness_reports_incomplete_callable_payload():
    module = SemanticModule(
        "callbacks",
        functions=[
            SemanticFunction(
                "run",
                arguments=[
                    SemanticArgument("cb", SemanticType("Callable", metadata={"return": SemanticType("Int32")}))
                ],
            )
        ],
    )

    report = assess_semantic_wrap_readiness(module)

    assert report["wrappability_blockers"] == [
        {
            "code": "callback_signature_incomplete",
            "message": "Some callback or procedure arguments need complete Callable[[...], ...] metadata in the .pyi file.",
            "items": [
                {
                    "owner": "callbacks.run.cb",
                    "item": "cb",
                    "type": "Callable",
                    "needs": [
                        "callback argument order",
                        "callback argument types",
                        "callback return type",
                    ],
                }
            ],
        }
    ]
    assert report["unit_blockers"] == [
        {
            "unit": "callbacks.run",
            "kind": "function",
            "blockers": report["wrappability_blockers"],
        }
    ]


def test_readiness_propagates_context_through_imports_callbacks_and_class_fields():
    nested_callback = SemanticType(
        "Callable",
        metadata={
            "arguments": [
                SemanticType("MissingCallbackArg"),
                SemanticType("Float64", shape=["a + zmissing"]),
                SemanticType("Float64", shape=["n + zmissing"]),
            ],
            "return": SemanticType("types_mod.callback_result_t"),
        },
    )
    module = SemanticModule(
        "edge",
        imports=["types_mod"],
        variables=[
            SemanticArgument("imported", SemanticType("types_mod.variable_t")),
            SemanticArgument(
                "typed_policy",
                SemanticType(
                    "Int32",
                    metadata={"readiness_blockers": [{"code": "type_policy_only", "message": "type policy"}]},
                ),
            ),
            SemanticArgument("n", SemanticType("Int32", constraints=[SemanticConstraint("Constant")])),
        ],
        classes=[SemanticClass("State", fields=[SemanticArgument("missing", SemanticType("MissingField"))])],
        functions=[
            SemanticFunction("placeholder", arguments=[SemanticArgument("cb", SemanticType("Procedure"))]),
            SemanticFunction("imported_result", return_type=SemanticType("types_mod.result_t")),
            SemanticFunction(
                "missing_constant",
                arguments=[SemanticArgument("x", SemanticType("Float64", shape=["n"]))],
            ),
            SemanticFunction(
                "nested",
                arguments=[
                    SemanticArgument("a", SemanticType("Int32")),
                    SemanticArgument("cb", nested_callback),
                ],
            ),
        ],
    )

    report = assess_semantic_wrap_readiness(module)
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}
    units = {unit["unit"]: unit for unit in report["unit_blockers"]}

    assert blockers["unresolved_semantic_types"]["items"] == [
        {"owner": "edge.State.missing", "item": "missing", "type": "MissingField"},
        {"owner": "edge.nested.cb.callback_arg_0", "item": "cb[0]", "type": "MissingCallbackArg"},
    ]
    assert blockers["missing_compile_time_values"]["items"] == [
        {"owner": "edge.missing_constant.x", "item": "x", "symbol": "n", "expression": "n"},
        {"owner": "edge.nested.cb.callback_arg_2", "item": "cb[2]", "symbol": "n", "expression": "n + zmissing"},
    ]
    assert blockers["unresolved_shape_symbols"]["items"] == [
        {
            "owner": "edge.nested.cb.callback_arg_1",
            "item": "cb[1]",
            "symbol": "zmissing",
            "expression": "a + zmissing",
        },
        {
            "owner": "edge.nested.cb.callback_arg_2",
            "item": "cb[2]",
            "symbol": "zmissing",
            "expression": "n + zmissing",
        },
    ]
    assert units["edge.typed_policy"]["kind"] == "variable"
    assert units["edge.State"]["kind"] == "class"
    assert units["edge.placeholder"]["kind"] == "function"
    assert units["edge.missing_constant"]["kind"] == "function"
    assert units["edge.nested"]["kind"] == "function"


def test_readiness_metadata_defaults_and_duplicate_unit_blockers_are_stable():
    module = SemanticModule(
        "defaults",
        functions=[SemanticFunction("ready")],
        metadata={
            "readiness_blockers": [
                {},
                {"code": "repeat", "message": "repeat message", "items": [{"detail": 1}, {"detail": 2}]},
                {"code": "other", "message": "other message", "item": "detail"},
            ]
        },
    )

    report = assess_semantic_wrap_readiness(module)

    assert report["wrappability_blockers"] == [
        {
            "code": "semantic_readiness_blocker",
            "message": "Semantic metadata marks this item as not wrappable.",
            "items": [{"owner": "defaults", "item": "defaults"}],
        },
        {
            "code": "repeat",
            "message": "repeat message",
            "items": [
                {"detail": 1, "owner": "defaults", "item": "defaults"},
                {"detail": 2, "owner": "defaults", "item": "defaults"},
            ],
        },
        {
            "code": "other",
            "message": "other message",
            "items": [{"detail": "detail", "owner": "defaults", "item": "defaults"}],
        },
    ]
    assert report["unit_blockers"] == [
        {
            "unit": "defaults",
            "kind": "module",
            "blockers": report["wrappability_blockers"],
        }
    ]


def test_readiness_preserves_ordering_and_nested_type_context():
    nested_callback = SemanticType(
        "Callable",
        metadata={
            "arguments": [SemanticType("types_mod.input_t")],
            "return": SemanticType("Float64", shape=["n + missing"]),
        },
    )
    module = SemanticModule(
        "ordered",
        imports=["types_mod"],
        variables=[
            SemanticArgument("hidden", SemanticType("MissingPrivate"), visibility="private"),
            SemanticArgument(
                "values",
                SemanticType("Float64", shape=["n + missing"]),
                metadata={"readiness_blockers": [{"code": "variable_policy", "message": "variable message"}]},
            ),
            SemanticArgument("n", SemanticType("Int32", constraints=[SemanticConstraint("Constant")])),
        ],
        classes=[
            SemanticClass("Hidden", visibility="private"),
            SemanticClass(
                "Visible",
                fields=[SemanticArgument("field", SemanticType("types_mod.field_t"))],
                methods=[
                    SemanticMethod("hidden", visibility="private"),
                    SemanticMethod("run", arguments=[SemanticArgument("cb", nested_callback)]),
                ],
            ),
        ],
        functions=[
            SemanticFunction("hidden", visibility="private"),
            SemanticFunction("result", return_type=SemanticType("Float64", shape=["n + missing"])),
        ],
    )

    report = assess_semantic_wrap_readiness(module)
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}
    units = {unit["unit"]: unit for unit in report["unit_blockers"]}

    assert blockers["variable_policy"]["items"] == [{"owner": "ordered.values", "item": "values"}]
    assert blockers["missing_compile_time_values"]["items"] == [
        {"owner": "ordered.values", "item": "values", "symbol": "n", "expression": "n + missing"},
        {
            "owner": "ordered.Visible.run.cb.callback_return",
            "item": "cb.return",
            "symbol": "n",
            "expression": "n + missing",
        },
        {"owner": "ordered.result.return", "item": "return", "symbol": "n", "expression": "n + missing"},
    ]
    assert blockers["unresolved_shape_symbols"]["items"] == [
        {"owner": "ordered.values", "item": "values", "symbol": "missing", "expression": "n + missing"},
        {
            "owner": "ordered.Visible.run.cb.callback_return",
            "item": "cb.return",
            "symbol": "missing",
            "expression": "n + missing",
        },
        {"owner": "ordered.result.return", "item": "return", "symbol": "missing", "expression": "n + missing"},
    ]
    assert set(units) == {"ordered.values", "ordered.Visible.run", "ordered.result"}
    assert units["ordered.values"]["kind"] == "variable"
    assert units["ordered.Visible.run"]["kind"] == "method"
    assert units["ordered.result"]["kind"] == "function"


def test_readiness_counts_accumulate_across_modules_and_skip_private_api():
    modules = [
        SemanticModule(
            "first",
            variables=[
                SemanticArgument("visible", SemanticType("Int32")),
                SemanticArgument("hidden", SemanticType("Int32"), visibility="private"),
            ],
            classes=[
                SemanticClass("Visible", methods=[SemanticMethod("run")]),
                SemanticClass("Hidden", visibility="private"),
            ],
            functions=[
                SemanticFunction("visible"),
                SemanticFunction("hidden", visibility="private"),
            ],
        ),
        SemanticModule(
            "second",
            variables=[SemanticArgument("visible", SemanticType("Int32"))],
            classes=[SemanticClass("Visible", methods=[SemanticMethod("run")])],
            functions=[SemanticFunction("visible")],
        ),
    ]

    report = assess_semantic_wrap_readiness(modules)

    assert report["wrappable"] is True
    assert report["n_modules"] == 2
    assert report["n_functions"] == 4
    assert report["n_classes"] == 2
    assert report["n_variables"] == 2


def test_readiness_report_preserves_blocker_payloads_and_unit_ownership():
    missing_shape_type = SemanticType(
        "Float64",
        shape=["size + n"],
        metadata={"readiness_blockers": [{"code": "type_policy", "message": "type message", "item": {"detail": "t"}}]},
    )
    callback_type = SemanticType(
        "Callable",
        metadata={
            "arguments": [SemanticType("MissingCallbackArg")],
            "return": SemanticType("MissingCallbackReturn"),
        },
    )
    module = SemanticModule(
        name="api",
        metadata={
            "readiness_blockers": [{"code": "module_policy", "message": "module message", "item": {"detail": "m"}}]
        },
        variables=[
            SemanticArgument("n", SemanticType("Int32", constraints=[SemanticConstraint("Constant")])),
            SemanticArgument("hidden", SemanticType("MissingPrivate"), visibility="private"),
        ],
        classes=[
            SemanticClass(
                "State",
                metadata={
                    "readiness_blockers": [
                        {"code": "class_policy", "message": "class message", "item": {"detail": "c"}}
                    ]
                },
                fields=[
                    SemanticArgument("size", SemanticType("Int32")),
                    SemanticArgument("values", missing_shape_type),
                ],
                methods=[
                    SemanticMethod(
                        "apply",
                        arguments=[
                            SemanticArgument(
                                "cb",
                                callback_type,
                                metadata={
                                    "readiness_blockers": [
                                        {
                                            "code": "argument_policy",
                                            "message": "argument message",
                                            "item": {"detail": "a"},
                                        }
                                    ]
                                },
                            )
                        ],
                    ),
                    SemanticMethod(
                        "hidden",
                        arguments=[SemanticArgument("value", SemanticType("MissingPrivate"))],
                        visibility="private",
                    ),
                ],
            )
        ],
        functions=[
            SemanticFunction(
                "hook",
                arguments=[SemanticArgument("cb", SemanticType("Procedure"))],
                metadata={
                    "readiness_blockers": [
                        {"code": "function_policy", "message": "function message", "item": {"detail": "f"}}
                    ]
                },
            ),
            SemanticFunction("unknown", return_type=SemanticType("MissingReturn")),
        ],
    )

    report = assess_semantic_wrap_readiness(module, source=["api.pyi"])
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}
    units = {unit["unit"]: unit for unit in report["unit_blockers"]}

    assert report["wrappable"] is False
    assert report["source"] == ["api.pyi"]
    assert report["n_modules"] == 1
    assert report["n_functions"] == 3
    assert report["n_classes"] == 1
    assert report["n_variables"] == 1
    assert set(blockers) == {
        "argument_policy",
        "callback_signature_incomplete",
        "class_policy",
        "function_policy",
        "missing_compile_time_values",
        "module_policy",
        "type_policy",
        "unresolved_semantic_types",
    }
    assert blockers["module_policy"]["items"] == [{"detail": "m", "owner": "api", "item": "api"}]
    assert blockers["class_policy"]["items"] == [{"detail": "c", "owner": "api.State", "item": "State"}]
    assert blockers["type_policy"]["items"] == [{"detail": "t", "owner": "api.State.values", "item": "values"}]
    assert blockers["missing_compile_time_values"]["items"] == [
        {"owner": "api.State.values", "item": "values", "symbol": "n", "expression": "size + n"}
    ]
    assert blockers["argument_policy"]["items"] == [{"detail": "a", "owner": "api.State.apply.cb", "item": "cb"}]
    assert blockers["unresolved_semantic_types"]["items"] == [
        {"owner": "api.State.apply.cb.callback_arg_0", "item": "cb[0]", "type": "MissingCallbackArg"},
        {"owner": "api.State.apply.cb.callback_return", "item": "cb.return", "type": "MissingCallbackReturn"},
        {"owner": "api.unknown.return", "item": "return", "type": "MissingReturn"},
    ]
    assert blockers["function_policy"]["items"] == [{"detail": "f", "owner": "api.hook", "item": "hook"}]
    assert blockers["callback_signature_incomplete"]["items"] == [
        {
            "owner": "api.hook.cb",
            "item": "cb",
            "type": "Procedure",
            "needs": [
                "callback argument order",
                "callback argument types",
                "callback return type",
            ],
        }
    ]
    assert units["api"]["kind"] == "module"
    assert units["api.State"]["kind"] == "class"
    assert units["api.State.apply"]["kind"] == "method"
    assert units["api.hook"]["kind"] == "function"
    assert units["api.unknown"]["kind"] == "function"
    assert set(units) == {"api", "api.State", "api.State.apply", "api.hook", "api.unknown"}
    assert set(report["why_not_wrappable"]) == {
        "Some callback or procedure arguments need complete Callable[[...], ...] metadata in the .pyi file.",
        "Some compile-time constants are declared but do not have literal .pyi values.",
        "Some semantic type references are not declared by the .pyi interface or its imports.",
        "argument message",
        "class message",
        "function message",
        "module message",
        "type message",
    }


def test_cli_wrap_readiness_uses_pyi_filename_as_native_contract(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text(
        """
n: Final[Int32] = 8

def fill(x: Float64[n]) -> None: ...
""",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)

    assert "Source: pyi" in res.stdout
    assert "Wrappable: yes" in res.stdout
    assert "No semantic readiness blockers detected." in res.stdout


def test_cli_wrap_readiness_json_uses_pyi_filename_as_native_contract(tmp_path: Path):
    pyi = tmp_path / "solver.pyi"
    pyi.write_text("def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    cmd = [sys.executable, "-m", "x2py", str(pyi), "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)

    assert payload[str(pyi)]["source_kind"] == "pyi"
    report = payload[str(pyi)]["wrap_readiness"]
    assert report["wrappable"] is True
    assert _blocker_codes(report) == set()


def test_cli_wrap_readiness_output_from_fortran():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--wrap-readiness"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert f"File: {TEST_FILE}" in res.stdout
    assert "Source: fortran" in res.stdout
    assert "Wrappable: yes" in res.stdout
    assert "No semantic readiness blockers detected." in res.stdout
    assert "Modules:" not in res.stdout


def test_cli_wrap_readiness_json_output_from_fortran():
    cmd = [sys.executable, "-m", "x2py", str(TEST_FILE), "--wrap-readiness", "--json"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(res.stdout)
    assert payload[str(TEST_FILE)]["source_kind"] == "fortran"
    assert payload[str(TEST_FILE)]["wrap_readiness"]["wrappable"] is True


def test_cli_help_includes_semantic_wrap_readiness_examples():
    cmd = [sys.executable, "-m", "x2py", "--help"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "python3 -m x2py path/to/file.f90 --wrap-readiness" in res.stdout
    assert "python3 -m x2py path/to/module.pyi --wrap-readiness" in res.stdout


def test_x2py_main_wrap_readiness_mode_from_inline_source(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--wrap-readiness"])
    assert x2py_cli.main() == 0
    assert "Wrappable: yes" in capsys.readouterr().out


def test_x2py_main_wrap_readiness_json_directory_expands_fortran_and_pyi(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")
    pyi = tmp_path / "solver.pyi"
    pyi.write_text("def fill(n: Int32) -> None: ...\n", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["x2py", str(tmp_path), "--language", "fortran", "--wrap-readiness", "--json"])
    assert x2py_cli.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload[str(f90)]["source_kind"] == "fortran"
    assert payload[str(pyi)]["source_kind"] == "pyi"


def test_wrap_readiness_report_reconciles_edited_pyi_file_set(tmp_path: Path):
    physics = tmp_path / "physics.pyi"
    types_mod = tmp_path / "types_mod.pyi"
    physics.write_text(
        """
from types_mod import particle

def create_particle() -> particle: ...
""",
        encoding="utf-8",
    )
    types_mod.write_text(
        """
class particle:
    mass: Float64
""",
        encoding="utf-8",
    )

    payload = x2py_cli._wrap_readiness_report([str(tmp_path)])
    modules = {module["name"]: module for module in payload[str(physics)]["semantic_modules"]}
    particle_ref = modules["physics"]["functions"][0]["return_type"]["metadata"]["external_type_ref"]

    assert particle_ref["origin_module"] == "types_mod"
    assert particle_ref["wrapped"] is True
    assert particle_ref["representation"] == "wrapped"
    assert payload[str(physics)]["wrap_readiness"]["n_modules"] == 2


def test_x2py_main_semantic_readiness_blocker_formatting():
    text = x2py_cli._format_semantic_readiness(
        {
            "solver.pyi": {
                "source_kind": "pyi",
                "semantic_modules": [{"name": "solver"}],
                "wrap_readiness": {
                    "wrappable": False,
                    "n_functions": 1,
                    "n_classes": 0,
                    "n_variables": 0,
                    "wrappability_blockers": [
                        {
                            "code": "unresolved_semantic_types",
                            "message": "Unresolved semantic types.",
                            "items": [{"owner": "step", "type": "sim_state"}],
                        },
                        {
                            "code": "unresolved_shape_symbols",
                            "message": "Unresolved shape symbols.",
                            "items": [{"owner": "fill", "expression": "n", "symbol": "n"}],
                        },
                        {
                            "code": "missing_compile_time_values",
                            "message": "Missing compile-time values.",
                            "items": [{"owner": "fill", "symbol": "n"}],
                        },
                        {
                            "code": "callback_signature_incomplete",
                            "message": "Callback signature incomplete.",
                            "items": [{"owner": "integrate.objective", "needs": ["callback argument types"]}],
                        },
                        {
                            "code": "no_public_api",
                            "message": "No public API.",
                            "items": [{"owner": "empty", "needs": ["public functions"]}],
                        },
                        {
                            "code": "custom",
                            "message": "Custom blocker.",
                            "items": [{"payload": 1}],
                        },
                    ],
                },
            }
        }
    )

    assert "step uses unresolved type sim_state" in text
    assert "fill shape 'n' uses unresolved symbol n" in text
    assert "fill needs literal value for Final constant n" in text
    assert "integrate.objective needs Callable[[...], ...] metadata (callback argument types)" in text
    assert "empty needs public functions" in text
    assert "{'payload': 1}" in text


def test_x2py_main_argument_validation_errors(tmp_path: Path, monkeypatch, capsys):
    f90 = _write_ready_fortran(tmp_path / "mini.f90")

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--show-vars"])
    with pytest.raises(SystemExit) as show_vars_error:
        x2py_cli.main()
    assert show_vars_error.value.code == 2
    assert "--show-vars/--print-limit require --parse" in capsys.readouterr().err

    monkeypatch.setattr(sys, "argv", ["x2py", str(f90), "--parse", "--print-limit", "-1"])
    with pytest.raises(SystemExit) as print_limit_error:
        x2py_cli.main()
    assert print_limit_error.value.code == 2
    assert "--print-limit must be >= 0" in capsys.readouterr().err

    pyi = tmp_path / "mini.pyi"
    pyi.write_text("def f() -> None: ...\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["x2py", str(pyi)])
    with pytest.raises(SystemExit) as stage_error:
        x2py_cli.main()
    assert stage_error.value.code == 2
    assert "Select at least one stage flag" in capsys.readouterr().err
