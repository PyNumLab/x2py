import pytest

from x2py.contracts import CONTRACT_SYMBOLS
from x2py.semantic_metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    PROJECTED_OUTPUT_METADATA,
    SCALAR_STORAGE_CATEGORY,
    SNAPSHOT_TYPE_METADATA,
)
from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator
from x2py.codegen.printers.pyi_printer import PyiPrinter
from x2py.codegen.scope import Scope
from x2py.ownership_policy import (
    AssignmentMode,
    CodegenAction,
    DestructionPolicy,
    NativeBarrierAction,
    NativeBarrierDispatcher,
    ObjectKind,
    OwnershipContext,
    OwnershipDecision,
    OwnershipOwner,
    OwnershipPolicyResolver,
    PolicyActionDispatcher,
    PythonBarrierAction,
    PythonBarrierDispatcher,
    SetterAction,
    SnapshotFieldAction,
    StorageMode,
    TransferMode,
    codegen_action_for_variable,
    default_ownership_policy,
    set_ownership_metadata,
)
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast as _semantic_ir_to_codegen_ast
from x2py.semantics.models import (
    POLICY_COMPLETION_PREPARED_METADATA,
    MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
    PYTHON_EXPORTS_METADATA,
    PYTHON_EXPORTS_PREPARED_METADATA,
    RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA,
    RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA,
    RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA,
    ProjectionMapping,
    SemanticArgument,
    SemanticArrayContract,
    SemanticClass,
    SemanticField,
    SemanticFunction,
    SemanticModule,
    SemanticStorageContract,
    SemanticType,
    SemanticVariable,
)
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.pyi_pipeline import pyi_text_to_semantic_module as _parse_pyi_text


CONTRACT_IMPORT = f"from x2py.contracts import {', '.join(sorted(CONTRACT_SYMBOLS))}\n"


def parse_pyi_text(source: str, *args, **kwargs):
    if "x2py.contracts" in source:
        return _parse_pyi_text(source, *args, **kwargs)
    return _parse_pyi_text(f"{CONTRACT_IMPORT}{source}", *args, **kwargs)


def _scalar_type(name: str = "Int32") -> SemanticType:
    return SemanticType(name=name, dtype=name)


def semantic_ir_to_codegen_ast(node, *args, **kwargs):
    if isinstance(node, SemanticModule):
        complete_semantic_policies(node)
    return _semantic_ir_to_codegen_ast(node, *args, **kwargs)


def _string_type() -> SemanticType:
    return SemanticType(name="String", dtype="String")


def _array_type(
    *,
    allocatable: bool = False,
    pointer: bool = False,
    metadata: dict[str, object] | None = None,
) -> SemanticType:
    return SemanticType(
        name="Float64",
        dtype="Float64",
        rank=1,
        shape=[":"],
        metadata=metadata or {},
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(
                rank=1,
                shape=[":"],
                allocatable=allocatable,
                pointer=pointer,
            ),
        ),
    )


def _scalar_storage_type() -> SemanticType:
    return SemanticType(
        name="Int32",
        dtype="Int32",
        rank=0,
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=0, shape=[], category=SCALAR_STORAGE_CATEGORY),
        ),
    )


def _string_storage_type() -> SemanticType:
    return SemanticType(
        name="String",
        dtype="String",
        rank=0,
        metadata={"fortran_character_length": "8"},
        storage=SemanticStorageContract(
            kind="array",
            array=SemanticArrayContract(rank=0, shape=[], category=SCALAR_STORAGE_CATEGORY),
        ),
    )


def _address_type(role: str) -> SemanticType:
    return SemanticType(
        name="Int32",
        dtype="Int32",
        storage=SemanticStorageContract(kind="address", metadata={ADDRESS_ROLE_METADATA: role}),
    )


def _derived_type(
    name: str = "point",
    *,
    metadata: dict[str, object] | None = None,
) -> SemanticType:
    return SemanticType(name=name, dtype=name, metadata=metadata or {})


def _read_only_argument_context(**kwargs) -> OwnershipContext:
    return OwnershipContext.argument(**kwargs)


def _writable_argument_context(**kwargs) -> OwnershipContext:
    return OwnershipContext.argument(writes_argument=True, **kwargs)


def _hidden_output_context(**kwargs) -> OwnershipContext:
    return OwnershipContext.argument(reads_argument=False, writes_argument=True, **kwargs)


def test_default_policy_decisions_cover_public_object_kinds():
    resolver = default_ownership_policy

    scalar = resolver.decide_semantic_type(_scalar_type(), OwnershipContext.result())
    assert scalar.owner is OwnershipOwner.PYTHON
    assert scalar.transfer is TransferMode.BY_VALUE
    assert scalar.codegen_action is CodegenAction.DIRECT_VALUE

    string = resolver.decide_semantic_type(_string_type(), OwnershipContext.result())
    assert string.owner is OwnershipOwner.PYTHON
    assert string.transfer is TransferMode.COPY_RETURN

    string_replacement = resolver.decide_semantic_type(
        _string_type(),
        _writable_argument_context(projects_result=True),
    )
    assert string_replacement.owner is OwnershipOwner.PYTHON
    assert string_replacement.transfer is TransferMode.COPY_RETURN
    assert "immutable Python strings" in string_replacement.reason

    caller_array = resolver.decide_semantic_type(_array_type(), _hidden_output_context())
    assert caller_array.owner is OwnershipOwner.CALLER
    assert caller_array.transfer is TransferMode.IN_PLACE
    assert caller_array.codegen_action is CodegenAction.IDENTITY_OUTPUT

    projected_caller_array = resolver.decide_semantic_type(
        _array_type(),
        _hidden_output_context(projects_result=True, python_visible=True),
    )
    assert projected_caller_array.transfer is TransferMode.IN_PLACE
    assert projected_caller_array.codegen_action is CodegenAction.IDENTITY_OUTPUT

    allocatable_output = resolver.decide_semantic_type(
        _array_type(allocatable=True),
        _hidden_output_context(projects_result=True, python_visible=False),
    )
    assert allocatable_output.owner is OwnershipOwner.PYTHON
    assert allocatable_output.transfer is TransferMode.COPY_RETURN
    assert allocatable_output.storage_mode is StorageMode.HEAP
    assert allocatable_output.nullable is True

    module_allocatable = resolver.decide_semantic_type(
        _array_type(allocatable=True, metadata={"aliased": True}),
        OwnershipContext.module_variable(),
    )
    assert module_allocatable.owner is OwnershipOwner.NATIVE
    assert module_allocatable.transfer is TransferMode.BORROWED_VIEW
    assert module_allocatable.destruction is DestructionPolicy.NATIVE_OWNER

    snapshot_module_allocatable = resolver.decide_semantic_type(
        _array_type(allocatable=True),
        OwnershipContext.module_variable(),
    )
    assert snapshot_module_allocatable.owner is OwnershipOwner.PYTHON
    assert snapshot_module_allocatable.transfer is TransferMode.SNAPSHOT_COPY
    assert snapshot_module_allocatable.destruction is DestructionPolicy.PYTHON_REFCOUNT

    derived_output = resolver.decide_semantic_type(_derived_type(), OwnershipContext.result())
    assert derived_output.owner is OwnershipOwner.WRAPPER
    assert derived_output.transfer is TransferMode.WRAPPER_INSTANCE

    aliased_module_object = resolver.decide_semantic_type(
        _derived_type(metadata={"aliased": True}),
        OwnershipContext.module_variable(),
    )
    assert aliased_module_object.owner is OwnershipOwner.NATIVE
    assert aliased_module_object.transfer is TransferMode.BORROWED_VIEW
    assert aliased_module_object.destruction is DestructionPolicy.NATIVE_OWNER
    assert aliased_module_object.boundary_storage_mode is StorageMode.ALIAS

    plain_module_object = resolver.decide_semantic_type(
        _derived_type(),
        OwnershipContext.module_variable(),
    )
    assert plain_module_object.owner is OwnershipOwner.PYTHON
    assert plain_module_object.transfer is TransferMode.SNAPSHOT_COPY
    assert plain_module_object.destruction is DestructionPolicy.PYTHON_REFCOUNT

    projected_derived_output = resolver.decide_semantic_type(
        _derived_type(),
        _hidden_output_context(projects_result=True, python_visible=True),
    )
    assert projected_derived_output.transfer is TransferMode.IN_PLACE
    assert projected_derived_output.codegen_action is CodegenAction.IDENTITY_OUTPUT

    hidden_derived_output = resolver.decide_semantic_type(
        _derived_type(),
        _hidden_output_context(projects_result=True, python_visible=False),
    )
    assert hidden_derived_output.transfer is TransferMode.WRAPPER_INSTANCE
    assert hidden_derived_output.codegen_action is CodegenAction.HIDDEN_OUTPUT

    derived_field = resolver.decide_semantic_type(_derived_type(), OwnershipContext.field())
    assert derived_field.owner is OwnershipOwner.WRAPPER
    assert derived_field.transfer is TransferMode.BORROWED_VIEW
    assert derived_field.destruction is DestructionPolicy.WRAPPER_DEALLOC


def test_default_policy_completes_python_and_native_barrier_actions():
    pointer_projection = _address_type(ADDRESS_ROLE_PROJECTION)
    pointer_projection.metadata["fortran_pointer"] = True
    cases = [
        (
            "scalar_value",
            _scalar_type(),
            _read_only_argument_context(),
            PythonBarrierAction.SCALAR_VALUE,
            NativeBarrierAction.PASS_VALUE,
        ),
        (
            "scalar_address_projection",
            _address_type(ADDRESS_ROLE_PROJECTION),
            _read_only_argument_context(),
            PythonBarrierAction.SCALAR_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        ),
        (
            "scalar_storage",
            _scalar_storage_type(),
            _writable_argument_context(),
            PythonBarrierAction.SCALAR_STORAGE,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
        ),
        (
            "pointer_scalar_address_projection",
            pointer_projection,
            _read_only_argument_context(),
            PythonBarrierAction.SCALAR_VALUE,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
        ),
        (
            "array_storage",
            _array_type(),
            _read_only_argument_context(),
            PythonBarrierAction.ARRAY_STORAGE,
            NativeBarrierAction.PASS_ARRAY_DESCRIPTOR,
        ),
        (
            "string_value",
            _string_type(),
            _writable_argument_context(projects_result=True),
            PythonBarrierAction.STRING_VALUE,
            NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        ),
        (
            "string_storage",
            _string_storage_type(),
            _writable_argument_context(),
            PythonBarrierAction.STRING_STORAGE,
            NativeBarrierAction.PASS_STORAGE_ADDRESS,
        ),
        (
            "raw_address",
            _address_type(ADDRESS_ROLE_RAW),
            _read_only_argument_context(),
            PythonBarrierAction.RAW_ADDRESS,
            NativeBarrierAction.PASS_RAW_ADDRESS,
        ),
        (
            "wrapper_instance",
            _derived_type(),
            _read_only_argument_context(),
            PythonBarrierAction.WRAPPER_INSTANCE,
            NativeBarrierAction.PASS_WRAPPER_ADDRESS,
        ),
    ]

    for label, semantic_type, context, python_action, native_action in cases:
        decision = default_ownership_policy.decide_semantic_type(semantic_type, context)
        assert decision.python_barrier_action is python_action, label
        assert decision.native_barrier_action is native_action, label


def test_allocatable_array_field_is_wrapper_owned_borrowed_view():
    decision = default_ownership_policy.decide_semantic_type(
        _array_type(allocatable=True),
        OwnershipContext.field(),
    )

    assert decision.owner is OwnershipOwner.WRAPPER
    assert decision.transfer is TransferMode.BORROWED_VIEW
    assert decision.destruction is DestructionPolicy.WRAPPER_DEALLOC
    assert decision.storage_mode is StorageMode.HEAP
    assert decision.borrowed is True
    assert decision.nullable is True


def test_policy_handler_dictionary_changes_one_object_kind():
    def native_scalar_handler(_facts, _context):
        return OwnershipDecision(
            ObjectKind.SCALAR,
            OwnershipOwner.NATIVE,
            TransferMode.BORROWED_VIEW,
            DestructionPolicy.NATIVE_OWNER,
            borrowed=True,
        )

    resolver = OwnershipPolicyResolver({ObjectKind.SCALAR: native_scalar_handler})

    scalar = resolver.decide_semantic_type(_scalar_type(), OwnershipContext.result())
    array = resolver.decide_semantic_type(_array_type(allocatable=True), OwnershipContext.result())

    assert scalar.owner is OwnershipOwner.NATIVE
    assert scalar.transfer is TransferMode.BORROWED_VIEW
    assert array.owner is OwnershipOwner.PYTHON
    assert array.transfer is TransferMode.COPY_RETURN


def test_codegen_action_dispatcher_routes_policy_actions_to_named_methods():
    class FakeVar:
        rank = 1
        ownership_decision = OwnershipDecision(
            ObjectKind.NUMPY_ARRAY,
            OwnershipOwner.PYTHON,
            TransferMode.SNAPSHOT_COPY,
            DestructionPolicy.PYTHON_REFCOUNT,
            storage_mode=StorageMode.ALIAS,
            codegen_action=CodegenAction.SNAPSHOT_COPY,
        )

    class Target:
        def snapshot(self, var, decision, marker):
            return marker, var.rank, decision.codegen_action

    dispatcher = PolicyActionDispatcher(
        {(ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "snapshot"},
    )

    assert dispatcher.dispatch(Target(), FakeVar(), "seen") == (
        "seen",
        1,
        CodegenAction.SNAPSHOT_COPY,
    )


def test_codegen_action_dispatcher_rejects_missing_policy_pairs():
    class FakeVar:
        ownership_decision = OwnershipDecision(
            ObjectKind.STRING,
            OwnershipOwner.TEMPORARY,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.CALL_LOCAL,
            codegen_action=CodegenAction.CALL_LOCAL_INPUT,
        )

    dispatcher = PolicyActionDispatcher({})

    with pytest.raises(ValueError, match="string/call_local_input"):
        dispatcher.handler_name(FakeVar())


def test_barrier_dispatchers_route_completed_actions_to_named_methods():
    class FakeVar:
        ownership_decision = OwnershipDecision(
            ObjectKind.SCALAR,
            OwnershipOwner.CALLER,
            TransferMode.CALL_LOCAL,
            DestructionPolicy.NONE,
            codegen_action=CodegenAction.CALL_LOCAL_INPUT,
            python_barrier_action=PythonBarrierAction.SCALAR_VALUE,
            native_barrier_action=NativeBarrierAction.PASS_VALUE,
        )

    class Target:
        def python_scalar(self, var, decision, marker):
            return marker, var.ownership_decision.python_barrier_action, decision.python_barrier_action

        def native_value(self, var, decision, marker):
            return marker, var.ownership_decision.native_barrier_action, decision.native_barrier_action

    python_dispatcher = PythonBarrierDispatcher({PythonBarrierAction.SCALAR_VALUE: "python_scalar"})
    native_dispatcher = NativeBarrierDispatcher({NativeBarrierAction.PASS_VALUE: "native_value"})

    assert python_dispatcher.dispatch(Target(), FakeVar(), "py") == (
        "py",
        PythonBarrierAction.SCALAR_VALUE,
        PythonBarrierAction.SCALAR_VALUE,
    )
    assert native_dispatcher.dispatch(Target(), FakeVar(), "native") == (
        "native",
        NativeBarrierAction.PASS_VALUE,
        NativeBarrierAction.PASS_VALUE,
    )


def test_barrier_dispatchers_reject_missing_completed_actions():
    decision = OwnershipDecision(
        ObjectKind.SCALAR,
        OwnershipOwner.CALLER,
        TransferMode.CALL_LOCAL,
        DestructionPolicy.NONE,
        codegen_action=CodegenAction.CALL_LOCAL_INPUT,
        python_barrier_action=PythonBarrierAction.RAW_ADDRESS,
        native_barrier_action=NativeBarrierAction.PASS_RAW_ADDRESS,
    )

    with pytest.raises(ValueError, match="Python-barrier handler"):
        PythonBarrierDispatcher({}).handler_name_for_decision(decision, "x")
    with pytest.raises(ValueError, match="native-barrier handler"):
        NativeBarrierDispatcher({}).handler_name_for_decision(decision, "x")


def test_bridge_and_binding_generators_expose_ownership_action_maps():
    assert (
        CPythonBindingGenerator._RESULT_DETAIL_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY)
        ]
        == "_snapshot_copy_result_detail_lines"
    )
    assert (
        CPythonBindingGenerator._RESULT_POLICY_DISPATCHER.handlers[(ObjectKind.SCALAR, CodegenAction.SNAPSHOT_COPY)]
        == "_convert_snapshot_policy_scalar_result"
    )
    assert (
        CPythonBindingGenerator._RESULT_POLICY_DISPATCHER.handlers[
            (ObjectKind.DERIVED_TYPE, CodegenAction.SNAPSHOT_COPY)
        ]
        == "_convert_snapshot_policy_custom_result"
    )
    assert CPythonBindingGenerator._SNAPSHOT_FIELD_DISPATCHER == {
        SnapshotFieldAction.SCALAR_COPY: "_snapshot_scalar_field_value_expr",
        SnapshotFieldAction.ARRAY_COPY: "_snapshot_array_field_value_expr",
        SnapshotFieldAction.NESTED_SNAPSHOT: "_snapshot_nested_field_value_expr",
    }
    assert (
        CPythonBindingGenerator._PYTHON_BARRIER_DISPATCHER.handlers[PythonBarrierAction.SCALAR_STORAGE]
        == "_convert_python_scalar_storage_argument"
    )
    assert (
        CPythonBindingGenerator._PYTHON_BARRIER_DISPATCHER.handlers[PythonBarrierAction.STRING_VALUE]
        == "_convert_python_string_value_argument"
    )
    assert (
        CPythonBindingGenerator._PYTHON_BARRIER_DISPATCHER.handlers[PythonBarrierAction.STRING_STORAGE]
        == "_convert_python_string_storage_argument"
    )
    assert (
        FortranToCBridgeGenerator._NATIVE_BARRIER_DISPATCHER.handlers[NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS]
        == "_convert_native_call_local_address_argument"
    )
    assert (
        FortranToCBridgeGenerator._NATIVE_BARRIER_DISPATCHER.handlers[NativeBarrierAction.PASS_RAW_ADDRESS]
        == "_convert_native_raw_address_argument"
    )
    assert (
        CPythonBindingGenerator._ARGUMENT_CAST_GUARD_DISPATCHER.handlers[
            (ObjectKind.SCALAR, CodegenAction.IDENTITY_OUTPUT)
        ]
        == "_append_unchecked_argument_cast"
    )
    assert (
        CPythonBindingGenerator._ARGUMENT_CAST_GUARD_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT)
        ]
        == "_append_replacement_argument_cast"
    )
    assert (
        CPythonBindingGenerator._RESULT_NOTE_DISPATCHER.handlers[(ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT)]
        == "_copy_return_result_notes"
    )
    assert FortranToCBridgeGenerator._NDARRAY_RESULT_DISPATCHER.handlers == {
        (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY): "_build_snapshot_copy_array_result",
        (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW): "_build_borrowed_array_result",
        (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_OUT): "_build_copy_return_array_result",
        (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT): "_build_copy_return_array_result",
        (ObjectKind.NUMPY_ARRAY, CodegenAction.HIDDEN_OUTPUT): "_build_copy_return_array_result",
    }
    assert (
        FortranToCBridgeGenerator._ALLOCATABLE_RESULT_HELPER_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_OUT)
        ]
        == "_uses_heap_allocatable_result_helper"
    )
    dispatchers = (
        (FortranToCBridgeGenerator, "_NATIVE_BARRIER_DISPATCHER"),
        (FortranToCBridgeGenerator, "_FUNCTION_ARGUMENT_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_RESULT_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_REPLACEMENT_RESULT_DISPATCHER"),
        (FortranToCBridgeGenerator, "_NDARRAY_RESULT_DISPATCHER"),
        (FortranToCBridgeGenerator, "_ALLOCATABLE_RESULT_HELPER_DISPATCHER"),
        (FortranToCBridgeGenerator, "_FIELD_SETTER_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_FIELD_GETTER_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_MODULE_VARIABLE_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_MODULE_ARRAY_GETTER_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_CALLBACK_ARGUMENT_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_CALLBACK_RESULT_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_PYTHON_BARRIER_DISPATCHER"),
        (CPythonBindingGenerator, "_ARGUMENT_DETAIL_DISPATCHER"),
        (CPythonBindingGenerator, "_ARGUMENT_CAST_GUARD_DISPATCHER"),
        (CPythonBindingGenerator, "_RESULT_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_RESULT_DETAIL_DISPATCHER"),
        (CPythonBindingGenerator, "_RESULT_NOTE_DISPATCHER"),
        (CPythonBindingGenerator, "_PROPERTY_SETTER_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_BORROWED_GETTER_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_ARGUMENT_RETURN_PROJECTION_DISPATCHER"),
        (CPythonBindingGenerator, "_PROJECTED_ARGUMENT_OBJECT_DISPATCHER"),
        (CPythonBindingGenerator, "_ARRAY_ACCESS_VALIDATION_DISPATCHER"),
        (CPythonBindingGenerator, "_ARRAY_RELEASE_POLICY_DISPATCHER"),
    )
    for generator, dispatcher_name in dispatchers:
        dispatcher = getattr(generator, dispatcher_name)
        assert dispatcher.handlers
        assert all(hasattr(generator, handler_name) for handler_name in dispatcher.handlers.values())

    assert set(FortranToCBridgeGenerator._NATIVE_BARRIER_DISPATCHER.handlers) == {
        NativeBarrierAction.PASS_VALUE,
        NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS,
        NativeBarrierAction.PASS_STORAGE_ADDRESS,
        NativeBarrierAction.PASS_RAW_ADDRESS,
        NativeBarrierAction.PASS_ARRAY_DESCRIPTOR,
        NativeBarrierAction.PASS_WRAPPER_ADDRESS,
    }
    assert set(CPythonBindingGenerator._PYTHON_BARRIER_DISPATCHER.handlers) == {
        PythonBarrierAction.SCALAR_VALUE,
        PythonBarrierAction.SCALAR_STORAGE,
        PythonBarrierAction.ARRAY_STORAGE,
        PythonBarrierAction.STRING_VALUE,
        PythonBarrierAction.STRING_STORAGE,
        PythonBarrierAction.RAW_ADDRESS,
        PythonBarrierAction.WRAPPER_INSTANCE,
    }
    assert (
        FortranToCBridgeGenerator._RESULT_POLICY_DISPATCHER.handlers.keys()
        == CPythonBindingGenerator._RESULT_POLICY_DISPATCHER.handlers.keys()
    )
    assert (
        CPythonBindingGenerator._ARGUMENT_RETURN_PROJECTION_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.COPY_IN_OUT, True)
        ]
        == "_project_native_argument_return"
    )
    assert (
        CPythonBindingGenerator._PROJECTED_ARGUMENT_OBJECT_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.IN_PLACE_ARGUMENT, True)
        ]
        == "_record_projected_argument_object"
    )
    assert (
        CPythonBindingGenerator._ARRAY_ACCESS_VALIDATION_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.IDENTITY_OUTPUT)
        ]
        == "_writable_array_access_validation"
    )
    assert (
        FortranToCBridgeGenerator._FIELD_SETTER_POLICY_DISPATCHER.handlers[SetterAction.WRITE_THROUGH]
        == "_build_field_setter"
    )
    assert (
        FortranToCBridgeGenerator._FIELD_SETTER_POLICY_DISPATCHER.handlers[SetterAction.REJECT_REPLACEMENT]
        == "_skip_field_setter"
    )
    assert (
        FortranToCBridgeGenerator._FIELD_GETTER_POLICY_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.BORROWED_VIEW)
        ]
        == "_append_borrowed_array_field_getter"
    )
    assert (
        FortranToCBridgeGenerator._MODULE_VARIABLE_POLICY_DISPATCHER.handlers[
            (ObjectKind.DERIVED_TYPE, CodegenAction.BORROWED_VIEW)
        ]
        == "_derived_module_variable"
    )
    assert (
        FortranToCBridgeGenerator._MODULE_VARIABLE_POLICY_DISPATCHER.handlers[
            (ObjectKind.DERIVED_TYPE, CodegenAction.SNAPSHOT_COPY)
        ]
        == "_snapshot_derived_module_variable"
    )
    assert (
        CPythonBindingGenerator._ARRAY_RELEASE_POLICY_DISPATCHER.handlers[DestructionPolicy.PYTHON_REFCOUNT]
        == "_release_python_owned_array_memory"
    )
    assert (
        CPythonBindingGenerator._ARRAY_RELEASE_POLICY_DISPATCHER.handlers[DestructionPolicy.BLOCKED]
        == "_blocked_array_release_policy"
    )


def test_immutable_replacement_policy_is_complete_before_ir_lowering():
    module = parse_pyi_text(
        """
def normalize(
    values: Annotated[Float64[:], Immutable]
) -> Returns["values", Float64[:]]: ...
""",
        module_name="immutable_values",
    )

    complete_semantic_policies(module)

    decision = module.functions[0].arguments[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert decision.kind is ObjectKind.NUMPY_ARRAY
    assert decision.codegen_action is CodegenAction.COPY_IN_OUT
    assert decision.storage_mode is StorageMode.STACK
    assert decision.boundary_storage_mode is StorageMode.STACK
    assert decision.projects_result is True
    assert decision.python_visible is True


def test_immutable_derived_output_selects_wrapper_instance_and_replacement_blocks():
    semantic_type = _derived_type("point")
    semantic_type.metadata["python_value_mutability"] = "immutable"

    output = default_ownership_policy.decide_semantic_type(
        semantic_type,
        _hidden_output_context(projects_result=True, python_visible=True),
    )
    assert output.owner is OwnershipOwner.WRAPPER
    assert output.transfer is TransferMode.WRAPPER_INSTANCE
    assert output.destruction is DestructionPolicy.WRAPPER_DEALLOC
    assert output.codegen_action is CodegenAction.HIDDEN_OUTPUT

    replacement = default_ownership_policy.decide_semantic_type(
        semantic_type,
        _writable_argument_context(projects_result=True, python_visible=True),
    )
    assert replacement.is_blocked
    assert replacement.blocker == "immutable derived replacement is not implemented"


@pytest.mark.parametrize(
    ("owner", "transfer", "destruction", "context"),
    [
        ("python", "copy_return", "python_refcount", OwnershipContext.result()),
        ("python", "snapshot_copy", "python_refcount", OwnershipContext.result()),
        ("caller", "call_local", "none", _read_only_argument_context()),
        ("caller", "in_place", "caller", _writable_argument_context()),
        ("native", "borrowed_view", "native_owner", OwnershipContext.module_variable()),
        ("wrapper", "borrowed_view", "wrapper_dealloc", OwnershipContext.field()),
        ("temporary", "call_local", "call_local", _read_only_argument_context()),
    ],
)
def test_explicit_supported_ownership_triples_remain_codegen_ready(
    owner: str,
    transfer: str,
    destruction: str,
    context: OwnershipContext,
):
    metadata: dict[str, object] = {}
    set_ownership_metadata(
        metadata,
        owner=owner,
        transfer=transfer,
        destruction=destruction,
    )

    decision = default_ownership_policy.decide_semantic_type(
        _array_type(metadata=metadata),
        context,
    )

    assert decision.owner.value == owner
    assert decision.transfer.value == transfer
    assert decision.destruction.value == destruction
    assert not decision.is_blocked


@pytest.mark.parametrize(
    ("owner", "transfer", "destruction"),
    [
        ("native", "copy_return", "native_owner"),
        ("native", "borrowed_view", "python_refcount"),
        ("python", "copy_return", "native_owner"),
        ("python", "borrowed_view", "python_refcount"),
        ("wrapper", "wrapper_instance", "python_refcount"),
    ],
)
def test_contradictory_ownership_triples_fail_closed(
    owner: str,
    transfer: str,
    destruction: str,
):
    metadata: dict[str, object] = {}
    set_ownership_metadata(
        metadata,
        owner=owner,
        transfer=transfer,
        destruction=destruction,
    )

    decision = default_ownership_policy.decide_semantic_type(
        _array_type(metadata=metadata),
        OwnershipContext.result(),
    )

    assert decision.is_blocked
    assert decision.owner is OwnershipOwner.UNKNOWN
    assert decision.transfer is TransferMode.BLOCKED
    assert decision.destruction is DestructionPolicy.BLOCKED
    assert f"{owner}/{transfer}/{destruction}" in decision.blocker


def test_explicit_blocked_policy_normalizes_all_lifetime_axes():
    metadata: dict[str, object] = {}
    set_ownership_metadata(
        metadata,
        owner="native",
        transfer="blocked",
        destruction="native_owner",
    )

    decision = default_ownership_policy.decide_semantic_type(
        _array_type(metadata=metadata),
        OwnershipContext.result(),
    )

    assert decision.owner is OwnershipOwner.UNKNOWN
    assert decision.transfer is TransferMode.BLOCKED
    assert decision.destruction is DestructionPolicy.BLOCKED
    assert decision.codegen_action is CodegenAction.BLOCKED


def test_documented_transfer_and_destruction_modes_resolve_or_fail_closed():
    cases = [
        ("by_value", _scalar_type(), OwnershipContext.result()),
        ("call_local_none", _scalar_type(), _read_only_argument_context()),
        ("call_local_cleanup", _string_type(), _hidden_output_context()),
        ("caller_in_place", _array_type(), _writable_argument_context()),
        ("copy_return", _array_type(), OwnershipContext.result()),
        ("snapshot_copy", _array_type(pointer=True), OwnershipContext.result()),
        (
            "native_borrowed_view",
            _array_type(allocatable=True, metadata={"aliased": True}),
            OwnershipContext.module_variable(),
        ),
        ("wrapper_borrowed_view", _array_type(allocatable=True), OwnershipContext.field()),
        ("wrapper_instance", _derived_type(), OwnershipContext.result()),
        ("wrapper_in_place", _derived_type(), _writable_argument_context()),
        ("blocked", _array_type(pointer=True), _hidden_output_context()),
    ]

    decisions = [
        default_ownership_policy.decide_semantic_type(semantic_type, context)
        for _label, semantic_type, context in cases
    ]
    transfer_modes = {decision.transfer for decision in decisions}
    destruction_modes = {decision.destruction for decision in decisions}

    assert transfer_modes == set(TransferMode)
    assert destruction_modes == set(DestructionPolicy)

    for label, decision in zip((case[0] for case in cases), decisions, strict=True):
        if decision.transfer is TransferMode.BLOCKED:
            assert decision.is_blocked, label
            assert decision.codegen_action is CodegenAction.BLOCKED, label
            assert decision.blocker, label
        else:
            assert not decision.is_blocked, label
            assert decision.codegen_action is not CodegenAction.BLOCKED, label


def test_pyi_policy_metadata_round_trips_pointer_detached_copy_and_blocks_getters():
    blocked_type = _array_type(pointer=True)
    blocked = default_ownership_policy.decide_semantic_type(blocked_type, OwnershipContext.field())
    assert blocked.is_blocked

    metadata: dict[str, object] = {}
    set_ownership_metadata(
        metadata,
        owner="python",
        transfer="snapshot_copy",
        destruction="python_refcount",
    )
    overridden = default_ownership_policy.decide_semantic_type(
        _array_type(pointer=True, metadata=metadata),
        OwnershipContext.field(),
    )
    assert overridden.is_blocked
    assert overridden.blocker == "pointer array field and module detached-copy accessors are not implemented"
    module_overridden = default_ownership_policy.decide_semantic_type(
        _array_type(pointer=True, metadata=metadata),
        OwnershipContext.module_variable(),
    )
    assert module_overridden.is_blocked
    assert module_overridden.blocker == "pointer array field and module detached-copy accessors are not implemented"

    module = parse_pyi_text(
        """
class box:
    values: Annotated[
        Float64[:],
        Pointer,
        Ownership("python"),
        Transfer("snapshot_copy"),
        Destruction("python_refcount"),
    ]
""",
        module_name="policy_box",
    )
    field_type = module.classes[0].fields[0].semantic_type
    parsed = default_ownership_policy.decide_semantic_type(field_type, OwnershipContext.field())
    assert parsed.is_blocked

    result = default_ownership_policy.decide_semantic_type(field_type, OwnershipContext.result())
    assert result.owner is OwnershipOwner.PYTHON
    assert result.transfer is TransferMode.SNAPSHOT_COPY
    assert result.destruction is DestructionPolicy.PYTHON_REFCOUNT
    assert result.codegen_action is CodegenAction.SNAPSHOT_COPY

    emitted = PyiPrinter().emit(field_type)
    assert 'Ownership("python")' in emitted
    assert 'Transfer("snapshot_copy")' in emitted
    assert 'Destruction("python_refcount")' in emitted


def test_complete_pointer_policy_metadata_round_trips_and_blocks_borrowed_views():
    module = parse_pyi_text(
        """
value: Annotated[
    Float64[:],
    Pointer,
    PointerAssociation("runtime"),
    PointerPolicy(
        nullable=True,
        transfer="snapshot_copy",
        target_owner="module",
        lifetime="module",
        deallocation="never",
        shape_source="pointer_bounds",
        contiguity="contiguous",
        reassociation="snapshot_final",
        aliasing="independent_copy",
        mutability="copy",
    ),
]
""",
        module_name="pointer_policy",
    )
    semantic_type = module.variables[0].semantic_type
    policy = semantic_type.metadata["pointer_policy"]
    assert policy == {
        "nullable": True,
        "transfer": "snapshot_copy",
        "target_owner": "module",
        "lifetime": "module",
        "deallocation": "never",
        "shape_source": "pointer_bounds",
        "contiguity": "contiguous",
        "reassociation": "snapshot_final",
        "aliasing": "independent_copy",
        "mutability": "copy",
    }
    assert semantic_type.metadata["fortran_pointer_association"] == "runtime"
    emitted = PyiPrinter().emit(semantic_type)
    assert 'PointerAssociation("runtime")' in emitted
    assert "PointerPolicy(nullable=True" in emitted
    assert 'mutability="copy")' in emitted

    policy["transfer"] = "borrowed_view"
    decision = default_ownership_policy.decide_semantic_type(semantic_type, OwnershipContext.module_variable())
    assert decision.is_blocked
    assert "owner retention" in decision.blocker


def test_pointer_policy_metadata_requires_every_fact():
    with pytest.raises(ValueError, match="missing: lifetime"):
        parse_pyi_text(
            """
value: Annotated[
    Float64[:],
    Pointer,
    PointerPolicy(
        nullable=True,
        transfer="snapshot_copy",
        target_owner="module",
        deallocation="never",
        shape_source="pointer_bounds",
        contiguity="contiguous",
        reassociation="snapshot_final",
        aliasing="independent_copy",
        mutability="copy",
    ),
]
""",
            module_name="incomplete_pointer_policy",
        )


def test_recursive_module_policy_map_includes_nested_fields_and_functions():
    module = SemanticModule(
        name="geometry",
        variables=[
            SemanticVariable(
                "values",
                _array_type(allocatable=True, metadata={"aliased": True}),
            )
        ],
        classes=[
            SemanticClass(
                "particle",
                fields=[SemanticField("origin", _derived_type("point"))],
                classes=[
                    SemanticClass(
                        "buffer",
                        fields=[SemanticField("values", _array_type(allocatable=True))],
                    )
                ],
            )
        ],
        functions=[
            SemanticFunction(
                "build",
                arguments=[SemanticArgument("n", _scalar_type())],
                return_type=_array_type(allocatable=True),
            )
        ],
    )

    decisions = default_ownership_policy.decide_semantic_module(module)

    assert decisions["geometry.values"].owner is OwnershipOwner.NATIVE
    assert decisions["geometry.particle.origin"].owner is OwnershipOwner.WRAPPER
    assert decisions["geometry.particle.buffer.values"].transfer is TransferMode.BORROWED_VIEW
    assert decisions["geometry.build.n"].transfer is TransferMode.CALL_LOCAL
    assert decisions["geometry.build.return"].transfer is TransferMode.COPY_RETURN


def test_policy_completion_attaches_decisions_before_ir_lowering():
    module = SemanticModule(
        name="generated_policy",
        variables=[
            SemanticVariable(
                "module_values",
                _array_type(allocatable=True, metadata={"aliased": True}),
            )
        ],
        classes=[
            SemanticClass(
                "buffer",
                fields=[SemanticField("values", _array_type(allocatable=True))],
            )
        ],
        functions=[
            SemanticFunction(
                "replace",
                arguments=[
                    SemanticArgument(
                        "values",
                        _array_type(allocatable=True),
                        metadata={PROJECTED_OUTPUT_METADATA: True},
                    )
                ],
                return_type=None,
                projection=[
                    ProjectionMapping(
                        python_name="values",
                        native_name="values",
                        native_position=0,
                        python_position=0,
                        result_position=0,
                    )
                ],
            )
        ],
    )

    complete_semantic_policies(module)

    assert module.metadata[POLICY_COMPLETION_PREPARED_METADATA] is True
    assert module.variables[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].owner is OwnershipOwner.NATIVE
    module_setter = module.variables[0].metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    assert module_setter.codegen_action is CodegenAction.CALL_LOCAL_INPUT
    assert module_setter.setter_action is SetterAction.REJECT_REPLACEMENT
    assert (
        module.variables[0].metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA].codegen_action
        is CodegenAction.BORROWED_VIEW
    )
    assert module.classes[0].fields[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].owner is OwnershipOwner.WRAPPER
    assert (
        module.classes[0].fields[0].metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA].codegen_action
        is CodegenAction.CALL_LOCAL_INPUT
    )
    assert (
        module.functions[0].arguments[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].transfer
        is TransferMode.COPY_RETURN
    )
    assert RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA not in module.functions[0].metadata

    codegen_module = semantic_ir_to_codegen_ast(
        module,
        Scope(name=module.name, scope_type="module"),
    )

    module_var = codegen_module.variables[0]
    field_var = codegen_module.classes[0].attributes[0]
    arg_var = codegen_module.funcs[0].arguments[0].var

    assert module_var.ownership_decision.owner is OwnershipOwner.NATIVE
    assert module_var.getter_ownership_decision.codegen_action is CodegenAction.BORROWED_VIEW
    assert module_var.setter_ownership_decision.assignment_mode is AssignmentMode.VALUE_COPY
    assert module_var.setter_ownership_decision.setter_action is SetterAction.REJECT_REPLACEMENT
    assert field_var.ownership_decision.owner is OwnershipOwner.WRAPPER
    assert field_var.getter_ownership_decision.codegen_action is CodegenAction.BORROWED_VIEW
    assert field_var.setter_ownership_decision.assignment_mode is AssignmentMode.VALUE_COPY
    assert field_var.setter_ownership_decision.setter_action is SetterAction.REJECT_REPLACEMENT
    assert arg_var.ownership_decision.owner is OwnershipOwner.PYTHON
    assert codegen_action_for_variable(arg_var) is CodegenAction.COPY_IN_OUT


def test_policy_completion_converts_native_addr_projection_after_python_boundary_parsing():
    module = parse_pyi_text(
        """
@native_call([Addr(Arg(0))])
def inspect(value: Int32) -> None: ...
""",
        module_name="native_projection_policy",
    )
    argument = module.functions[0].arguments[0]

    assert argument.semantic_type.storage is None

    complete_semantic_policies(module)

    assert argument.semantic_type.storage.kind == "address"
    assert argument.semantic_type.storage.metadata[ADDRESS_ROLE_METADATA] == ADDRESS_ROLE_PROJECTION
    decision = argument.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert decision.python_barrier_action is PythonBarrierAction.SCALAR_VALUE
    assert decision.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS


def test_policy_completion_prunes_unexported_entry_declarations_before_lowering():
    exported_variable = SemanticVariable(
        "counter",
        _scalar_type(),
        metadata={PYTHON_EXPORTS_METADATA: [{"namespace": (), "name": "counter"}]},
    )
    omitted_variable = SemanticVariable(
        "scale",
        _scalar_type("Float64"),
        metadata={PYTHON_EXPORTS_METADATA: []},
    )
    exported_function = SemanticFunction(
        "summarize",
        return_type=_scalar_type(),
        metadata={PYTHON_EXPORTS_METADATA: [{"namespace": (), "name": "summarize"}]},
    )
    omitted_function = SemanticFunction("scaled_counter", return_type=_scalar_type("Float64"))
    private_helper = SemanticFunction(
        "hidden_helper",
        return_type=_scalar_type(),
        visibility="private",
        metadata={PYTHON_EXPORTS_METADATA: []},
    )
    module = SemanticModule(
        name="entry_contract",
        variables=[exported_variable, omitted_variable],
        functions=[exported_function, omitted_function, private_helper],
        metadata={PYTHON_EXPORTS_PREPARED_METADATA: True},
    )

    complete_semantic_policies(module)

    assert module.variables == [exported_variable]
    assert module.functions == [exported_function, private_helper]
    assert POLICY_COMPLETION_PREPARED_METADATA in module.metadata


def test_scalar_accessor_policies_are_complete_before_ir_lowering():
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("counter", _scalar_type())],
        classes=[SemanticClass("point", fields=[SemanticField("x", _scalar_type())])],
    )

    complete_semantic_policies(module)

    for variable in (module.variables[0], module.classes[0].fields[0]):
        getter = variable.metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA]
        setter = variable.metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
        assert getter.codegen_action is CodegenAction.DIRECT_VALUE
        assert getter.storage_mode is StorageMode.STACK
        assert setter.codegen_action is CodegenAction.CALL_LOCAL_INPUT
        assert setter.assignment_mode is AssignmentMode.VALUE_COPY
        assert setter.setter_action is SetterAction.WRITE_THROUGH


def test_module_variable_initializer_policy_is_complete_before_ir_lowering():
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("counter", _scalar_type(), default_value="41")],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    assert variable.metadata[RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA] == "41"
    assert variable.metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA].setter_action is SetterAction.WRITE_THROUGH


def test_unsupported_module_variable_initializer_is_readiness_blocker():
    module = SemanticModule(
        name="labels",
        variables=[SemanticVariable("label", SemanticType("String"), default_value='"ready"')],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    assert RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA not in variable.metadata
    assert variable.metadata["readiness_blockers"] == [
        {
            "code": MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
            "message": "Module variable initializers require scalar storage with a write-through native setter.",
            "item": {
                "item": "label",
                "setter_action": "reject_replacement",
                "reason": "completed setter policy does not expose write-through native assignment",
            },
        }
    ]


def test_derived_field_setter_policy_uses_value_copy_write_through():
    module = SemanticModule(
        name="layout",
        classes=[
            SemanticClass("point"),
            SemanticClass("tagged_point", fields=[SemanticField("position", _derived_type("point"))]),
        ],
    )

    complete_semantic_policies(module)

    setter = module.classes[1].fields[0].metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    assert setter.kind is ObjectKind.DERIVED_TYPE
    assert setter.assignment_mode is AssignmentMode.VALUE_COPY
    assert setter.setter_action is SetterAction.WRITE_THROUGH


def test_aliased_derived_module_object_is_borrowed_and_rejects_replacement():
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("current", _derived_type("box", metadata={"aliased": True}))],
        classes=[SemanticClass("box", fields=[SemanticField("value", _scalar_type())])],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    storage = variable.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    getter = variable.metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA]
    setter = variable.metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    assert storage.owner is OwnershipOwner.NATIVE
    assert storage.transfer is TransferMode.BORROWED_VIEW
    assert storage.boundary_storage_mode is StorageMode.ALIAS
    assert getter.codegen_action is CodegenAction.BORROWED_VIEW
    assert setter.setter_action is SetterAction.REJECT_REPLACEMENT

    codegen_module = semantic_ir_to_codegen_ast(
        module,
        Scope(name=module.name, scope_type="module"),
    )
    codegen_variable = codegen_module.variables[0]
    assert codegen_variable.is_target is True
    assert codegen_variable.ownership_decision.owner is OwnershipOwner.NATIVE
    assert codegen_variable.setter_ownership_decision.setter_action is SetterAction.REJECT_REPLACEMENT


def test_plain_derived_module_object_is_completed_as_snapshot_contract():
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("current", _derived_type("box"))],
        classes=[
            SemanticClass("point", fields=[SemanticField("x", _scalar_type())]),
            SemanticClass(
                "box",
                fields=[
                    SemanticField("value", _scalar_type()),
                    SemanticField("origin", _derived_type("point")),
                    SemanticField("values", _array_type(allocatable=True, metadata={"aliased": True})),
                ],
            ),
        ],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    storage = variable.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    getter = variable.metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA]
    setter = variable.metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    assert storage.owner is OwnershipOwner.PYTHON
    assert storage.transfer is TransferMode.SNAPSHOT_COPY
    assert storage.destruction is DestructionPolicy.PYTHON_REFCOUNT
    assert variable.semantic_type.metadata[SNAPSHOT_TYPE_METADATA] is True
    assert getter.codegen_action is CodegenAction.SNAPSHOT_COPY
    assert setter.setter_action is SetterAction.REJECT_REPLACEMENT
    point, box = module.classes
    assert point.fields[0].metadata[RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA] is SnapshotFieldAction.SCALAR_COPY
    assert box.fields[0].metadata[RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA] is SnapshotFieldAction.SCALAR_COPY
    assert box.fields[1].metadata[RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA] is SnapshotFieldAction.NESTED_SNAPSHOT
    assert box.fields[2].metadata[RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA] is SnapshotFieldAction.ARRAY_COPY


def test_plain_derived_module_snapshot_blocks_unsupported_nested_pointer_field():
    pointer_field = _array_type(pointer=True)
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("current", _derived_type("box"))],
        classes=[
            SemanticClass(
                "box",
                fields=[
                    SemanticField("value", _scalar_type()),
                    SemanticField("values", pointer_field),
                ],
            )
        ],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    storage = variable.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    getter = variable.metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA]
    assert storage.is_blocked
    assert (
        storage.blocker
        == "snapshot field box.values is a pointer array without a completed pointer detached-copy policy"
    )
    assert getter.is_blocked
    assert SNAPSHOT_TYPE_METADATA not in variable.semantic_type.metadata
    assert all(RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA not in field.metadata for field in module.classes[0].fields)


@pytest.mark.parametrize(
    ("field", "extra_classes", "expected_blocker"),
    [
        (
            SemanticField("nested", _derived_type("box")),
            [],
            "snapshot field box.nested creates a recursive derived snapshot cycle",
        ),
        (
            SemanticField("payload", SemanticType("Opaque", dtype="Opaque")),
            [],
            "snapshot field box.payload has no safe scalar copy policy for type 'Opaque'",
        ),
        (
            SemanticField("nested", _derived_type("child", metadata={"fortran_polymorphic": True})),
            [SemanticClass("child", fields=[SemanticField("value", _scalar_type())])],
            "snapshot field box.nested uses unsupported polymorphic or assumed-type storage",
        ),
    ],
)
def test_plain_derived_module_snapshot_blocks_incomplete_recursive_copy_policy(
    field: SemanticField,
    extra_classes: list[SemanticClass],
    expected_blocker: str,
):
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("current", _derived_type("box"))],
        classes=[SemanticClass("box", fields=[field]), *extra_classes],
    )

    complete_semantic_policies(module)

    decision = module.variables[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert decision.is_blocked
    assert decision.blocker == expected_blocker
    assert RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA not in field.metadata


def test_snapshot_annotation_conflicting_with_aliased_storage_blocks_in_policy_completion():
    module = parse_pyi_text(
        """
class box:
    value: Int32

current: Snapshot[Annotated[box, Aliased]]
""",
        module_name="state",
    )

    complete_semantic_policies(module)

    decision = module.variables[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert decision.is_blocked
    assert decision.blocker == "Snapshot[box] conflicts with the completed borrowed_view transfer policy"


def test_explicit_borrowed_derived_field_setter_rejects_replacement():
    child_type = _derived_type("child")
    set_ownership_metadata(
        child_type.metadata,
        owner="wrapper",
        transfer="borrowed_view",
        destruction="wrapper_dealloc",
    )
    module = SemanticModule(
        name="finalizer",
        classes=[
            SemanticClass("child"),
            SemanticClass("parent", fields=[SemanticField("value", child_type)]),
        ],
    )

    complete_semantic_policies(module)

    setter = module.classes[1].fields[0].metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    assert setter.kind is ObjectKind.DERIVED_TYPE
    assert setter.transfer is TransferMode.BORROWED_VIEW
    assert setter.setter_action is SetterAction.REJECT_REPLACEMENT
