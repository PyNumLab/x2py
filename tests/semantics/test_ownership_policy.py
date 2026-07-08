import pytest

from x2py.contracts import CONTRACT_SYMBOLS
from x2py.semantic_metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    PROJECTED_OUTPUT_METADATA,
    SCALAR_STORAGE_CATEGORY,
)
from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.bindings.cpython_api import PythonObjectType
from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator
from x2py.codegen.models.core import Variable
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
    RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA,
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
from x2py.semantics.native_array_handles import (
    NativeArrayBuildRequirement,
    NativeArrayHandlePolicy,
    NativeArrayHandlePolicyDispatcher,
    native_array_descriptor_kind,
    native_array_handle_build_requirements,
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
    assert plain_module_object.owner is OwnershipOwner.UNKNOWN
    assert plain_module_object.transfer is TransferMode.BLOCKED
    assert plain_module_object.destruction is DestructionPolicy.BLOCKED
    assert plain_module_object.blocker == (
        "plain derived module variables require Aliased storage; whole-object Snapshot[T] is future-only"
    )

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


def _native_array_policy(
    *,
    descriptor_kind: str = "allocatable",
    handle_kind: str = "borrowed_module_descriptor",
) -> NativeArrayHandlePolicy:
    return NativeArrayHandlePolicy(
        descriptor_kind=descriptor_kind,
        handle_kind=handle_kind,
        origin="module_variable",
        owner="native",
        owner_retention="native_module",
        descriptor_ownership="borrowed",
        borrowed=True,
        getter_behavior="handle",
        python_setter="none",
        native_setter="none",
        output_projection="none",
        release="native_owner",
        target_lifetime="module",
        destroy_behavior="none",
        to_numpy="borrowed_view",
        descriptor_interop="none",
        nullable=False,
        optional_absent=False,
        storage_mode="alias",
        operations=("allocated", "to_numpy"),
    )


def test_native_array_handle_dispatcher_routes_completed_policy_to_named_method():
    class Subject:
        name = "values"

    class Target:
        def handle(self, subject, policy, marker):
            return marker, subject.name, policy.descriptor_kind, policy.handle_kind

    dispatcher = NativeArrayHandlePolicyDispatcher(
        {("allocatable", "borrowed_module_descriptor"): "handle"},
    )

    assert dispatcher.dispatch(Target(), Subject(), _native_array_policy(), "seen") == (
        "seen",
        "values",
        "allocatable",
        "borrowed_module_descriptor",
    )


def test_native_array_handle_dispatcher_rejects_missing_completed_policy_pair():
    dispatcher = NativeArrayHandlePolicyDispatcher({})

    with pytest.raises(ValueError, match="pointer/borrowed_module_descriptor"):
        dispatcher.handler_name_for_policy(
            _native_array_policy(descriptor_kind="pointer"),
            "target",
        )


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
    native_array_handle_keys = {
        ("allocatable", "argument_descriptor"),
        ("allocatable", "borrowed_field_descriptor"),
        ("allocatable", "borrowed_module_descriptor"),
        ("allocatable", "optional_absent_handle"),
        ("allocatable", "owned_result_descriptor"),
        ("pointer", "argument_descriptor"),
        ("pointer", "borrowed_field_descriptor"),
        ("pointer", "borrowed_module_descriptor"),
        ("pointer", "optional_absent_handle"),
    }
    assert set(FortranToCBridgeGenerator._NATIVE_ARRAY_HANDLE_DISPATCHER.handlers) == native_array_handle_keys
    assert set(CPythonBindingGenerator._NATIVE_ARRAY_HANDLE_DISPATCHER.handlers) == native_array_handle_keys
    assert (
        FortranToCBridgeGenerator._NATIVE_ARRAY_HANDLE_DISPATCHER.handlers[
            ("allocatable", "borrowed_module_descriptor")
        ]
        == "_bridge_borrowed_allocatable_handle"
    )
    assert (
        CPythonBindingGenerator._NATIVE_ARRAY_HANDLE_DISPATCHER.handlers[("pointer", "borrowed_module_descriptor")]
        == "_bind_borrowed_pointer_handle"
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
        (FortranToCBridgeGenerator, "_NATIVE_ARRAY_HANDLE_DISPATCHER"),
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
        (CPythonBindingGenerator, "_NATIVE_ARRAY_HANDLE_DISPATCHER"),
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
        FortranToCBridgeGenerator._FIELD_GETTER_POLICY_DISPATCHER.handlers[
            (ObjectKind.SCALAR, CodegenAction.SNAPSHOT_COPY)
        ]
        == "_append_nullable_scalar_field_getter"
    )
    assert (
        FortranToCBridgeGenerator._MODULE_VARIABLE_POLICY_DISPATCHER.handlers[
            (ObjectKind.SCALAR, CodegenAction.SNAPSHOT_COPY)
        ]
        == "_scalar_module_variable"
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


def test_native_array_handle_module_variable_bridge_uses_completed_handle_policy_dispatch():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
""",
        module_name="native_handle_bridge_dispatch",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    generator = FortranToCBridgeGenerator("", 0)

    with pytest.raises(
        NotImplementedError,
        match=r"Native array handle bridge generation is not implemented.*allocatable/borrowed_module_descriptor",
    ):
        generator._visit_Variable(lowered.variables[0])


@pytest.mark.parametrize(
    ("descriptor_kind", "annotation"),
    [
        ("allocatable", "Allocatable[Float64[:]]"),
        ("pointer", "Pointer[Float64[:]]"),
    ],
)
def test_native_array_handle_field_generation_uses_completed_handle_policy_dispatch(
    descriptor_kind,
    annotation,
):
    module = parse_pyi_text(
        f"""
class box:
    values: {annotation}
""",
        module_name=f"{descriptor_kind}_handle_field_dispatch",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    field = lowered.classes[0].attributes[0]
    policy = field.native_array_handle_policy

    assert policy.descriptor_kind == descriptor_kind
    assert policy.handle_kind == "borrowed_field_descriptor"
    assert policy.origin == "derived_field"
    assert policy.owner_retention == "parent_wrapper"
    assert policy.blocker is None

    bridge = FortranToCBridgeGenerator("", 0)
    with pytest.raises(
        NotImplementedError,
        match=rf"Native array handle bridge generation is not implemented.*{descriptor_kind}/borrowed_field_descriptor",
    ):
        bridge._convert_result(field, lowered.classes[0].scope)

    binding = CPythonBindingGenerator("", 0)
    with pytest.raises(
        NotImplementedError,
        match=rf"Native array handle Python binding generation is not implemented.*"
        rf"{descriptor_kind}/borrowed_field_descriptor",
    ):
        binding._convert_result(field, is_bind_c=True, funcdef=None)


def test_native_array_handle_result_generation_uses_completed_handle_policy_dispatch():
    module = parse_pyi_text(
        """
def make_values() -> Allocatable[Float64[:]]: ...
""",
        module_name="native_handle_result_dispatch",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    result = lowered.funcs[0].results.var

    bridge = FortranToCBridgeGenerator("", 0)
    with pytest.raises(
        NotImplementedError,
        match=r"Native array handle bridge generation is not implemented.*allocatable/owned_result_descriptor",
    ):
        bridge._convert_result(result, lowered.funcs[0].scope)

    binding = CPythonBindingGenerator("", 0)
    with pytest.raises(
        NotImplementedError,
        match=r"Native array handle Python binding generation is not implemented.*allocatable/owned_result_descriptor",
    ):
        binding._convert_result(result, is_bind_c=True, funcdef=lowered.funcs[0])


@pytest.mark.parametrize(
    ("descriptor_kind", "annotation"),
    [
        ("allocatable", "Allocatable[Float64[:]]"),
        ("pointer", "Pointer[Float64[:]]"),
    ],
)
def test_native_array_handle_argument_generation_uses_completed_handle_policy_dispatch(
    descriptor_kind,
    annotation,
):
    module = parse_pyi_text(
        f"""
def fill(values: {annotation}) -> Returns["values", {annotation}]: ...
""",
        module_name=f"{descriptor_kind}_handle_argument_dispatch",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    argument = lowered.funcs[0].arguments[0]
    policy = argument.var.native_array_handle_policy

    assert policy.descriptor_kind == descriptor_kind
    assert policy.handle_kind == "argument_descriptor"
    assert policy.output_projection == "projected_handle"
    assert policy.blocker is None

    bridge = FortranToCBridgeGenerator("", 0)
    with pytest.raises(
        NotImplementedError,
        match=rf"Native array handle bridge generation is not implemented.*{descriptor_kind}/argument_descriptor",
    ):
        bridge._convert_argument(argument, lowered.funcs[0])

    binding = CPythonBindingGenerator("", 0)
    collect_arg = Variable(PythonObjectType(), "py_values", memory_handling="alias")
    with pytest.raises(
        NotImplementedError,
        match=rf"Native array handle Python binding generation is not implemented.*{descriptor_kind}/argument_descriptor",
    ):
        binding._convert_argument(
            argument.var,
            collect_arg,
            bound_argument=False,
            is_bind_c_argument=False,
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


def test_pyi_policy_metadata_round_trips_pointer_array_handle_readiness_blocker():
    default_type = _array_type(pointer=True)
    default_field = default_ownership_policy.decide_semantic_type(default_type, OwnershipContext.field())
    assert not default_field.is_blocked
    assert default_field.owner is OwnershipOwner.WRAPPER
    assert default_field.transfer is TransferMode.BORROWED_VIEW
    assert default_field.destruction is DestructionPolicy.WRAPPER_DEALLOC
    assert default_field.borrowed is True

    default_module = default_ownership_policy.decide_semantic_type(default_type, OwnershipContext.module_variable())
    assert not default_module.is_blocked
    assert default_module.owner is OwnershipOwner.NATIVE
    assert default_module.transfer is TransferMode.BORROWED_VIEW
    assert default_module.destruction is DestructionPolicy.NATIVE_OWNER

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
    assert overridden.blocker == (
        "pointer array field and module handles remain blocked until descriptor extraction, "
        "target lifetime, and release policy are implemented"
    )
    module_overridden = default_ownership_policy.decide_semantic_type(
        _array_type(pointer=True, metadata=metadata),
        OwnershipContext.module_variable(),
    )
    assert module_overridden.is_blocked
    assert module_overridden.blocker == (
        "pointer array field and module handles remain blocked until descriptor extraction, "
        "target lifetime, and release policy are implemented"
    )

    module = parse_pyi_text(
        """
class box:
    values: Annotated[
        Pointer[Float64[:]],
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
    assert "detached-copy accessors" not in parsed.blocker
    assert "descriptor extraction" in parsed.blocker

    result = default_ownership_policy.decide_semantic_type(field_type, OwnershipContext.result())
    assert result.owner is OwnershipOwner.PYTHON
    assert result.transfer is TransferMode.SNAPSHOT_COPY
    assert result.destruction is DestructionPolicy.PYTHON_REFCOUNT
    assert result.codegen_action is CodegenAction.SNAPSHOT_COPY

    emitted = PyiPrinter().emit(field_type)
    assert 'Ownership("python")' in emitted
    assert 'Transfer("snapshot_copy")' in emitted
    assert 'Destruction("python_refcount")' in emitted


def test_plain_pointer_array_container_policy_completes_default_handle_profile():
    module = parse_pyi_text(
        """
value: Pointer[Float64[:]]

class box:
    target: Pointer[Float64[:]]
""",
        module_name="pointer_default_profile",
    )

    complete_semantic_policies(module)

    module_policy = module.variables[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    field_policy = module.classes[0].fields[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]

    assert not module_policy.is_blocked
    assert module_policy.handle_kind == "borrowed_module_descriptor"
    assert module_policy.getter_behavior == "handle"
    assert module_policy.to_numpy == "unsupported"
    assert module_policy.descriptor_interop == "none"
    assert module_policy.requires_pointer_c_descriptor_interop is False
    assert module_policy.target_lifetime == "module"
    assert module_policy.destroy_behavior == "none"
    assert set(module_policy.operations) == {"associated", "nullify", "to_numpy"}
    assert "allocate" not in module_policy.operations
    assert "deallocate" not in module_policy.operations
    assert "resize" not in module_policy.operations

    assert not field_policy.is_blocked
    assert field_policy.handle_kind == "borrowed_field_descriptor"
    assert field_policy.getter_behavior == "handle"
    assert field_policy.to_numpy == "unsupported"
    assert field_policy.descriptor_interop == "none"
    assert field_policy.requires_pointer_c_descriptor_interop is False
    assert field_policy.target_lifetime == "parent_wrapper"
    assert field_policy.destroy_behavior == "parent_wrapper_finalizer"
    assert set(field_policy.operations) == {"associated", "nullify", "to_numpy"}


def test_complete_pointer_policy_metadata_round_trips_and_blocks_borrowed_views():
    module = parse_pyi_text(
        """
value: Annotated[
    Pointer[Float64[:]],
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


def test_complete_pointer_policy_blocks_array_containers_until_handle_readiness():
    module = parse_pyi_text(
        """
value: Annotated[
    Pointer[Float64[:]],
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

    complete_semantic_policies(module)

    handle_policy = module.variables[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    assert handle_policy.is_blocked
    assert handle_policy.getter_behavior == "blocked"
    assert handle_policy.to_numpy == "descriptor_view"
    assert handle_policy.descriptor_interop == "pointer_c_descriptor"
    assert handle_policy.requires_pointer_c_descriptor_interop is True
    assert handle_policy.blocker == (
        "pointer array field and module handles remain blocked until descriptor extraction, "
        "target lifetime, and release policy are implemented"
    )


def test_pointer_policy_metadata_requires_every_fact():
    with pytest.raises(ValueError, match="missing: lifetime"):
        parse_pyi_text(
            """
value: Annotated[
    Pointer[Float64[:]],
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


def test_pointer_policy_unsafe_deallocate_is_explicit_operation_opt_in():
    module = parse_pyi_text(
        """
def consume(
    default_target: Pointer[Float64[:]],
    unsafe_target: Annotated[
        Pointer[Float64[:]],
        PointerPolicy(
            nullable=True,
            transfer="call_local",
            target_owner="external",
            lifetime="call",
            deallocation="unsafe_deallocate",
            shape_source="pointer_bounds",
            contiguity="contiguous",
            reassociation="snapshot_final",
            aliasing="descriptor",
            mutability="mutable",
        ),
    ],
) -> None: ...
""",
        module_name="unsafe_deallocate_policy",
    )

    complete_semantic_policies(module)

    default_target = module.functions[0].arguments[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    unsafe_target = module.functions[0].arguments[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]

    assert set(default_target.operations) == {"associated", "nullify", "to_numpy"}
    assert set(unsafe_target.operations) == {"associated", "deallocate", "nullify", "to_numpy"}
    assert "allocate" not in unsafe_target.operations
    assert "resize" not in unsafe_target.operations

    emitted = PyiPrinter().emit(module.functions[0].arguments[1].semantic_type)
    assert 'deallocation="unsafe_deallocate"' in emitted


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


def test_native_array_handle_policies_complete_before_ir_lowering():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
target_values: Annotated[Allocatable[Float64[:]], Aliased]

class box:
    values: Allocatable[Float64[:]]
    target: Pointer[Float64[:]]

def consume(
    values: Allocatable[Float64[:]],
    managed_target: Annotated[
        Pointer[Float64[:]],
        PointerPolicy(
            nullable=True,
            transfer="call_local",
            target_owner="caller",
            lifetime="call",
            deallocation="deallocate_resize",
            shape_source="pointer_bounds",
            contiguity="contiguous",
            reassociation="allocate_resize",
            aliasing="descriptor",
            mutability="mutable",
        ),
    ],
    maybe_target: Pointer[Float64[:]] | None = ...,
) -> None: ...

def make_values() -> Allocatable[Float64[:]]: ...
def make_target() -> Pointer[Float64[:]]: ...
""",
        module_name="native_handles",
    )

    complete_semantic_policies(module)

    values = module.variables[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    target_values = module.variables[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    field_values = module.classes[0].fields[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    field_target = module.classes[0].fields[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    argument_values = module.functions[0].arguments[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    managed_target = module.functions[0].arguments[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    optional_target = module.functions[0].arguments[2].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    allocatable_result = module.functions[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    pointer_result = module.functions[2].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]

    assert values.descriptor_kind == "allocatable"
    assert values.handle_kind == "borrowed_module_descriptor"
    assert values.origin == "module_variable"
    assert values.owner == "native"
    assert values.owner_retention == "native_module"
    assert values.descriptor_ownership == "borrowed"
    assert values.target_lifetime == "module"
    assert values.destroy_behavior == "none"
    assert values.to_numpy == "read_only_detached_copy"
    assert values.descriptor_interop == "none"
    assert values.requires_pointer_c_descriptor_interop is False
    assert values.storage_mode == "heap"
    assert set(values.operations) == {"allocated", "deallocate", "resize", "to_numpy"}

    assert target_values.handle_kind == "borrowed_module_descriptor"
    assert target_values.owner_retention == "native_module"
    assert target_values.target_lifetime == "module"
    assert target_values.to_numpy == "borrowed_view"
    assert target_values.descriptor_interop == "none"
    assert target_values.requires_pointer_c_descriptor_interop is False

    assert field_values.handle_kind == "borrowed_field_descriptor"
    assert field_values.owner == "wrapper"
    assert field_values.owner_retention == "parent_wrapper"
    assert field_values.release == "wrapper_dealloc"
    assert field_values.target_lifetime == "parent_wrapper"
    assert field_values.destroy_behavior == "parent_wrapper_finalizer"

    assert field_target.descriptor_kind == "pointer"
    assert field_target.handle_kind == "borrowed_field_descriptor"
    assert field_target.target_lifetime == "parent_wrapper"
    assert field_target.destroy_behavior == "parent_wrapper_finalizer"
    assert field_target.getter_behavior == "handle"
    assert field_target.to_numpy == "unsupported"
    assert field_target.descriptor_interop == "none"
    assert field_target.requires_pointer_c_descriptor_interop is False
    assert field_target.is_blocked is False
    assert set(field_target.operations) == {"associated", "nullify", "to_numpy"}

    assert argument_values.handle_kind == "argument_descriptor"
    assert argument_values.origin == "argument"
    assert argument_values.owner_retention == "caller_handle"
    assert argument_values.target_lifetime == "call"
    assert argument_values.destroy_behavior == "none"
    assert argument_values.is_blocked is True
    assert "descriptor-argument handoff needs generated handle support" in argument_values.blocker
    assert argument_values.descriptor_interop == "none"
    assert argument_values.requires_pointer_c_descriptor_interop is False
    assert set(argument_values.operations) == {"allocated", "deallocate", "resize", "to_numpy"}

    assert optional_target.handle_kind == "optional_absent_handle"
    assert optional_target.optional_absent is True
    assert optional_target.nullable is True
    assert optional_target.owner_retention == "optional_argument"
    assert optional_target.target_lifetime == "absent_or_call"
    assert optional_target.destroy_behavior == "none"
    assert optional_target.is_blocked is True
    assert "descriptor-argument handoff needs generated handle support" in optional_target.blocker
    assert optional_target.descriptor_interop == "none"
    assert optional_target.requires_pointer_c_descriptor_interop is False
    assert set(optional_target.operations) == {"associated", "nullify", "to_numpy"}
    assert "allocate" not in optional_target.operations
    assert "deallocate" not in optional_target.operations
    assert "resize" not in optional_target.operations

    assert managed_target.handle_kind == "argument_descriptor"
    assert managed_target.descriptor_kind == "pointer"
    assert managed_target.target_lifetime == "call"
    assert managed_target.destroy_behavior == "none"
    assert managed_target.is_blocked is True
    assert "descriptor-argument handoff needs generated handle support" in managed_target.blocker
    assert managed_target.to_numpy == "descriptor_view"
    assert managed_target.descriptor_interop == "pointer_c_descriptor"
    assert managed_target.requires_pointer_c_descriptor_interop is True
    assert set(managed_target.operations) == {
        "allocate",
        "associated",
        "deallocate",
        "nullify",
        "resize",
        "to_numpy",
    }

    assert allocatable_result.handle_kind == "owned_result_descriptor"
    assert allocatable_result.origin == "result"
    assert allocatable_result.owner == "wrapper"
    assert allocatable_result.owner_retention == "wrapper_owner_storage"
    assert allocatable_result.descriptor_ownership == "owned"
    assert allocatable_result.output_projection == "handle_result"
    assert allocatable_result.release == "wrapper_dealloc"
    assert allocatable_result.target_lifetime == "wrapper_owner_storage"
    assert allocatable_result.destroy_behavior == "handle_finalizer"
    assert allocatable_result.descriptor_interop == "none"
    assert allocatable_result.requires_pointer_c_descriptor_interop is False

    assert pointer_result.handle_kind == "unsupported"
    assert pointer_result.owner_retention == "unknown"
    assert pointer_result.target_lifetime == "unknown"
    assert pointer_result.destroy_behavior == "blocked"
    assert pointer_result.is_blocked is True
    assert pointer_result.descriptor_interop == "none"
    assert pointer_result.requires_pointer_c_descriptor_interop is False
    assert "stable owner storage and target lifetime" in pointer_result.blocker


def test_allocatable_handle_numpy_policy_requires_proven_live_aliasing():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
shared_values: Annotated[Allocatable[Float64[:]], Aliased]
""",
        module_name="allocatable_numpy_policy",
    )

    complete_semantic_policies(module)

    values = module.variables[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    shared_values = module.variables[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]

    assert values.to_numpy == "read_only_detached_copy"
    assert shared_values.to_numpy == "borrowed_view"


def test_native_array_handle_build_requirements_are_selected_from_completed_policy():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
default_target: Pointer[Float64[:]]

def inspect(
    target: Annotated[
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
""",
        module_name="native_handle_build",
    )

    complete_semantic_policies(module)

    requirements = native_array_handle_build_requirements(module)

    assert requirements.pointer_c_descriptor_interop is True
    assert requirements.requires_iso_fortran_binding is True
    assert requirements.headers == ("ISO_Fortran_binding.h",)
    assert requirements.items == (
        NativeArrayBuildRequirement(
            owner="native_handle_build.inspect.target",
            item="target",
            descriptor_kind="pointer",
            handle_kind="argument_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
    )


def test_native_array_handle_build_requirements_ignore_raw_default_handle_syntax():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
target: Pointer[Float64[:]]

class box:
    values: Allocatable[Float64[:]]
    target: Pointer[Float64[:]]
""",
        module_name="native_handle_no_interop",
    )

    complete_semantic_policies(module)

    requirements = native_array_handle_build_requirements(module)

    assert requirements.pointer_c_descriptor_interop is False
    assert requirements.requires_iso_fortran_binding is False
    assert requirements.headers == ()
    assert requirements.items == ()


def test_native_array_handle_build_requirements_require_completed_policy():
    module = parse_pyi_text(
        """
target: Pointer[Float64[:]]
""",
        module_name="native_handle_missing_policy",
    )

    with pytest.raises(ValueError, match="run complete_semantic_policies"):
        native_array_handle_build_requirements(module)


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


@pytest.mark.parametrize(
    ("descriptor_kind", "annotation"),
    [
        ("allocatable", "Allocatable[Float64[:]]"),
        ("pointer", "Pointer[Float64[:]]"),
    ],
)
def test_policy_completion_rejects_addr_projection_for_array_descriptor_handles(
    descriptor_kind,
    annotation,
):
    module = parse_pyi_text(
        f"""
@native_call([Addr(Arg(0))])
def consume(values: {annotation}) -> None: ...
""",
        module_name=f"{descriptor_kind}_addr_projection",
    )
    argument = module.functions[0].arguments[0]

    assert native_array_descriptor_kind(argument.semantic_type) == descriptor_kind

    with pytest.raises(ValueError, match=r"Addr\(Arg\(i\)\) is only valid for primitive scalar values"):
        complete_semantic_policies(module)


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


def test_scalar_descriptor_accessor_policies_are_nullable_snapshots():
    module = parse_pyi_text(
        """
alloc_value: Allocatable[Float64]
ptr_value: Pointer[Int32]

class point:
    alloc_field: Allocatable[Float64]
    ptr_field: Pointer[Int32]
""",
        module_name="descriptor_state",
    )

    complete_semantic_policies(module)

    variables = [
        module.variables[0],
        module.variables[1],
        module.classes[0].fields[0],
        module.classes[0].fields[1],
    ]
    for variable in variables:
        storage = variable.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
        getter = variable.metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA]
        setter = variable.metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
        assert storage.transfer is TransferMode.SNAPSHOT_COPY
        assert storage.nullable is True
        assert storage.codegen_action is CodegenAction.SNAPSHOT_COPY
        assert getter.transfer is TransferMode.SNAPSHOT_COPY
        assert getter.nullable is True
        assert getter.codegen_action is CodegenAction.SNAPSHOT_COPY
        assert setter.setter_action is SetterAction.REJECT_REPLACEMENT

    alloc_module, ptr_module, alloc_field, ptr_field = variables
    assert alloc_module.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].storage_mode is StorageMode.HEAP
    assert alloc_field.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].storage_mode is StorageMode.HEAP
    assert ptr_module.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].storage_mode is StorageMode.ALIAS
    assert ptr_field.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].storage_mode is StorageMode.ALIAS


def test_scalar_descriptor_function_boundaries_use_normal_scalar_values():
    module = parse_pyi_text(
        """
@native_call(
    [Allocatable(Arg(0)), Pointer(Arg(1))],
    result=Pointer(Return(0)),
)
def combine(
    scale: Float64 | None,
    current: Int32 | None,
) -> Float64 | None: ...
""",
        module_name="descriptor_call",
    )

    complete_semantic_policies(module)

    scale, current = module.functions[0].arguments
    result = module.functions[0].metadata[RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA]
    scale_policy = scale.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    current_policy = current.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]

    assert scale_policy.transfer is TransferMode.CALL_LOCAL
    assert scale_policy.storage_mode is StorageMode.STACK
    assert scale_policy.boundary_storage_mode is StorageMode.HEAP
    assert scale_policy.descriptor_boundary is True
    assert scale_policy.python_barrier_action is PythonBarrierAction.SCALAR_VALUE
    assert scale_policy.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS
    assert current_policy.transfer is TransferMode.CALL_LOCAL
    assert current_policy.storage_mode is StorageMode.STACK
    assert current_policy.boundary_storage_mode is StorageMode.ALIAS
    assert current_policy.descriptor_boundary is True
    assert current_policy.python_barrier_action is PythonBarrierAction.SCALAR_VALUE
    assert current_policy.native_barrier_action is NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS
    assert result.transfer is TransferMode.SNAPSHOT_COPY
    assert result.storage_mode is StorageMode.ALIAS
    assert result.nullable is True
    assert result.codegen_action is CodegenAction.SNAPSHOT_COPY


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


def test_plain_derived_module_object_blocks_without_live_borrow_policy():
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
    assert storage.is_blocked
    assert storage.blocker == (
        "plain derived module variables require Aliased storage; whole-object Snapshot[T] is future-only"
    )
    assert getter.is_blocked
    assert setter.setter_action is SetterAction.OMIT
    assert all(
        RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA not in field.metadata
        for semantic_class in module.classes
        for field in semantic_class.fields
    )


def test_stale_snapshot_metadata_blocks_in_policy_completion():
    module = SemanticModule(
        name="state",
        variables=[SemanticVariable("current", _derived_type("box", metadata={"snapshot_type": True}))],
        classes=[SemanticClass("box", fields=[SemanticField("value", _scalar_type())])],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    decision = variable.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    assert decision.is_blocked
    assert decision.blocker == (
        "Snapshot[T] is not an active semantic .pyi contract; whole-object snapshots are future-only"
    )
    assert "snapshot_type" not in variable.semantic_type.metadata


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
