"""Tests split by stable ownership concept from `test_wrap_readiness.py`."""

from tests._shared.semantic_readiness_support import (
    CONTRACT_IMPORT,
    POLICY_COMPLETION_PREPARED_METADATA,
    RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    SemanticArgument,
    SemanticArrayContract,
    SemanticFunction,
    SemanticModule,
    SemanticOrigin,
    SemanticStorageContract,
    SemanticType,
    _blocker_codes,
    _readiness_from_pyi,
    assess_prepared_semantic_wrap_readiness,
    assess_semantic_wrap_readiness,
    complete_semantic_policies,
    fortran_module_to_semantic_module,
    parse_fortran_file,
    parse_pyi_text,
)


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


def test_prepared_readiness_blocks_missing_native_array_handle_policy():
    module = parse_pyi_text(
        f"""{CONTRACT_IMPORT}
values: Allocatable[Float64[:]]
""",
        module_name="native_policy_missing",
    )
    complete_semantic_policies(module)
    module.variables[0].metadata.pop(RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA)

    report = assess_prepared_semantic_wrap_readiness(module, source="native_policy_missing.pyi")

    blocker = next(
        item for item in report["wrappability_blockers"] if item["code"] == "native_array_handle_policy_missing"
    )
    assert blocker["items"] == [
        {
            "owner": "native_policy_missing.values",
            "item": "values",
        }
    ]


def test_allocatable_handle_codegen_accepts_owned_results_with_standard_cfi_storage():
    report = _readiness_from_pyi(
        """
values: Allocatable[Float64[:]]
target_values: Annotated[Allocatable[Float64[:]], Aliased]

def fill() -> Returns["values", Allocatable[Float64[:]]]: ...

def make_values() -> Allocatable[Float64[:]]: ...

def make_pair() -> tuple[Returns["left", Allocatable[Float64[:]]], Returns["right", Allocatable[Float64[:]]]]: ...
"""
    )

    assert report["wrappable"] is True
    assert "allocatable_replacement_policy_missing" not in _blocker_codes(report)
    assert "allocatable_owner_policy_missing" not in _blocker_codes(report)
    assert "allocatable_multiple_copy_returns_unsupported" not in _blocker_codes(report)
    assert "native_array_handle_codegen_unsupported" not in _blocker_codes(report)


def test_explicit_borrowed_module_allocatable_requires_aliased_storage():
    report = _readiness_from_pyi(
        """
values: Annotated[
    Allocatable[Float64[:]],
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


def test_plain_derived_module_object_blocks_and_borrowing_requires_aliased_storage():
    plain = _readiness_from_pyi(
        """
class box:
    value: Float64

current: box
"""
    )

    assert plain["wrappable"] is False
    plain_blocker = next(
        item for item in plain["wrappability_blockers"] if item["code"] == "fortran_ownership_policy_blocked"
    )
    assert plain_blocker["items"][0]["policy"] == (
        "plain derived module variables require Aliased storage; whole-object Snapshot[T] is future-only"
    )

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


def test_derived_type_parameter_is_a_value_constant_not_mutable_module_storage():
    parsed = parse_fortran_file(
        """
module colors
  type rgb_color
    integer :: r
    integer :: g
    integer :: b
  end type rgb_color
  type(rgb_color), parameter :: black = rgb_color(0, 0, 0)
end module colors
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])

    report = assess_semantic_wrap_readiness(module)

    assert report["wrappable"] is True
    assert "fortran_ownership_policy_blocked" not in _blocker_codes(report)


def test_plain_derived_module_object_with_pointer_field_blocks_until_aliased_policy_is_explicit():
    report = _readiness_from_pyi(
        """
class box:
    values: Pointer[Float64[:]]

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
        "policy": "plain derived module variables require Aliased storage; whole-object Snapshot[T] is future-only",
    } in blocker["items"]
    assert "native_array_handle_codegen_unsupported" not in _blocker_codes(report)


def test_pointer_module_variable_default_handle_policy_is_codegen_ready():
    parsed = parse_fortran_file(
        """
module pointer_module_mod
  real(8), pointer :: values(:)
end module pointer_module_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])

    report = assess_semantic_wrap_readiness(module)

    assert "pointer_c_descriptor_interop_unavailable" not in _blocker_codes(report)
    assert "native_array_handle_codegen_unsupported" not in _blocker_codes(report)
    assert report["wrappable"] is True


def test_pointer_descriptor_view_is_ready_with_standard_c_descriptor_interop():
    report = _readiness_from_pyi(
        """
def inspect(
    values: Annotated[
        Pointer[Float64[:]],
        PointerPolicy(
            nullable=True,
            transfer="call_local",
            target_owner="caller",
            lifetime="call",
            deallocation="never",
            shape_source="pointer_bounds",
            contiguity="strided",
            reassociation="never",
            aliasing="borrowed",
            mutability="view",
        ),
    ],
) -> None: ...
"""
    )

    assert "pointer_c_descriptor_interop_unavailable" not in _blocker_codes(report)
    assert report["wrappable"] is True


def test_shape_readiness_ignores_layout_syntax_and_called_array_intrinsics():
    parsed = parse_fortran_file(
        """
module color_mod
  type :: rgb_color
    integer :: r, g, b
  end type rgb_color
contains
  function dot_colors(v, colors) result(color)
    real(8), intent(in) :: v(:)
    type(rgb_color), intent(in) :: colors(size(v))
    type(rgb_color) :: color
  end function dot_colors
end module color_mod
"""
    )
    module = fortran_module_to_semantic_module(parsed.modules[0])

    report = assess_semantic_wrap_readiness(module)
    blockers = {blocker["code"]: blocker for blocker in report["wrappability_blockers"]}

    assert "unresolved_shape_symbols" not in blockers
    assert blockers["fortran_derived_type_array_policy_missing"]["items"] == [
        {"owner": "color_mod.dot_colors.colors", "item": "colors", "type": "rgb_color"}
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


def test_scalar_descriptor_function_signature_is_wrappable():
    report = _readiness_from_pyi(
        """
@native_call(
    [Allocatable(Arg(0)), Pointer(Arg(1))],
    result=Allocatable(Return(0)),
)
def combine(
    scale: Float64 | None,
    current: Float64 | None,
) -> Float64 | None: ...
"""
    )

    assert report["wrappable"] is True


def test_pointer_descriptor_inputs_pass_while_reassociation_and_result_policies_block():
    report = _readiness_from_pyi(
        """
def inspect(values: Pointer[Float64[:]]) -> None: ...

def attach() -> Returns["values", Pointer[Float64[:]]]: ...

def replace(values: Pointer[Float64[:]]) -> Returns["values", Pointer[Float64[:]]]: ...

def choose() -> Pointer[Float64[:]]: ...
"""
    )

    policy_blocker = next(
        blocker
        for blocker in report["wrappability_blockers"]
        if blocker["code"] == "native_array_handle_policy_blocked"
    )
    assert policy_blocker["items"] == [
        {
            "owner": "solver.attach.values",
            "item": "values",
            "policy": "pointer handle results need stable owner storage and target lifetime policy before wrapping",
            "descriptor_kind": "pointer",
            "handle_kind": "unsupported",
        },
        {
            "owner": "solver.replace.values",
            "item": "values",
            "policy": "pointer array dummy reassociation needs explicit PointerPolicy metadata",
            "descriptor_kind": "pointer",
            "handle_kind": "argument_descriptor",
        },
        {
            "owner": "solver.choose.return",
            "item": "return",
            "policy": "pointer handle results need stable owner storage and target lifetime policy before wrapping",
            "descriptor_kind": "pointer",
            "handle_kind": "unsupported",
        },
    ]

    assert "native_array_handle_codegen_unsupported" not in _blocker_codes(report)


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
