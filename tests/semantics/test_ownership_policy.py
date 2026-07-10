from dataclasses import replace

import pytest

from x2py.contracts import CONTRACT_SYMBOLS
from x2py.semantic_metadata import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    ADDRESS_ROLE_RAW,
    PROJECTED_OUTPUT_METADATA,
    SCALAR_STORAGE_CATEGORY,
)
from x2py.codegen.bind_c import (
    BindCArrayType,
    BindCFunctionDef,
    BindCNativeArrayDescriptorType,
    BindCNativeArrayHandleProperty,
    BindCNativeArrayHandleVariable,
    BindCPointer,
    native_array_descriptor_argument_type,
)
from x2py.codegen.bindings.c_concepts import CFIDescriptorType
from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.bindings.cpython_api import PythonObjectType
from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator
from x2py.codegen.models.core import (
    Declare,
    FunctionCall,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    IndexedElement,
    Return,
    Variable,
)
from x2py.codegen.models.datatypes import NIL, NumpyFloat64Type, NumpyNDArrayType, convert_to_literal
from x2py.codegen.printers.ccode import CCodePrinter
from x2py.codegen.printers.cpythoncode import CPythonCodePrinter
from x2py.codegen.printers.fcode import FCodePrinter
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
    ArrayInteropPolicy,
    ArrayInteropPolicyDispatcher,
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


def _model_call_names(node, seen=None):
    """Collect function-call names from a generated model subtree."""
    if seen is None:
        seen = set()
    node_id = id(node)
    if node_id in seen:
        return
    seen.add(node_id)
    if isinstance(node, FunctionCall):
        yield str(node.func_name)
    for attr in getattr(node, "_attribute_nodes", ()):
        value = getattr(node, attr)
        if isinstance(value, tuple | list):
            for item in value:
                yield from _model_call_names(item, seen)
        elif value is not None:
            yield from _model_call_names(value, seen)


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
    assert allocatable_output.owner is OwnershipOwner.WRAPPER
    assert allocatable_output.transfer is TransferMode.WRAPPER_INSTANCE
    assert allocatable_output.destruction is DestructionPolicy.WRAPPER_DEALLOC
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
    to_numpy: str = "borrowed_view",
    descriptor_interop: str = "none",
    nullable: bool = False,
    optional_absent: bool = False,
    operations: tuple[str, ...] = ("allocated", "to_numpy"),
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
        to_numpy=to_numpy,
        descriptor_interop=descriptor_interop,
        nullable=nullable,
        optional_absent=optional_absent,
        storage_mode="alias",
        operations=operations,
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


def test_array_interop_dispatcher_routes_completed_abi_selector_to_named_method():
    class Subject:
        name = "values"

    class Target:
        def data_buffer(self, subject, policy, marker):
            return marker, subject.name, policy.abi

        def descriptor(self, subject, policy, marker):
            return marker, subject.name, policy.abi, policy.descriptor_kind

    dispatcher = ArrayInteropPolicyDispatcher(
        {
            ("argument", "data_buffer"): "data_buffer",
            ("argument", "descriptor"): "descriptor",
        },
    )

    assert dispatcher.dispatch(
        Target(),
        Subject(),
        ArrayInteropPolicy(abi="data_buffer", owner="argument values"),
        "argument",
        "seen",
    ) == ("seen", "values", "data_buffer")
    assert dispatcher.dispatch(
        Target(),
        Subject(),
        ArrayInteropPolicy(
            abi="descriptor",
            owner="argument values",
            descriptor_kind="allocatable",
            handle_kind="argument_descriptor",
        ),
        "argument",
        "seen",
    ) == ("seen", "values", "descriptor", "allocatable")


def test_lowering_attaches_one_array_interop_policy_for_data_buffer_and_descriptor_lanes():
    module = parse_pyi_text(
        """
def consume_array(values: Float64[:]) -> Float64[:]: ...
def consume_handle(values: Allocatable[Float64[:]]) -> None: ...
""",
        module_name="array_interop_policy_selectors",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    array_function = lowered.funcs[0]
    handle_function = lowered.funcs[1]

    array_argument_policy = array_function.arguments[0].var.array_interop_policy
    array_result_policy = array_function.results.var.array_interop_policy
    handle_argument = handle_function.arguments[0].var
    handle_argument_policy = handle_argument.array_interop_policy

    assert array_argument_policy.abi == "data_buffer"
    assert array_argument_policy.descriptor_kind is None
    assert array_result_policy.abi == "data_buffer"
    assert handle_argument_policy.abi == "descriptor"
    assert handle_argument_policy.descriptor_kind == "allocatable"
    assert handle_argument_policy.handle_kind == "argument_descriptor"
    assert handle_argument.native_array_handle_policy.descriptor_kind == "allocatable"


def test_native_array_descriptor_argument_codegen_selects_bind_c_tuple_abi():
    class Subject:
        name = "values"

    required_policy = _native_array_policy(handle_kind="argument_descriptor")
    optional_policy = _native_array_policy(
        handle_kind="optional_absent_handle",
        nullable=True,
        optional_absent=True,
    )

    for generator in (FortranToCBridgeGenerator, CPythonBindingGenerator):
        required_type = generator._native_array_descriptor_argument_type(required_policy)
        optional_type = generator._native_array_descriptor_argument_type(optional_policy)

        assert required_type is native_array_descriptor_argument_type(required_policy)
        assert optional_type is native_array_descriptor_argument_type(optional_policy)
        assert required_type is BindCNativeArrayDescriptorType.get_new(has_presence=False)
        assert optional_type is BindCNativeArrayDescriptorType.get_new(has_presence=True)
        assert len(required_type) == 1
        assert len(optional_type) == 2

    bridge = FortranToCBridgeGenerator("", 0)
    binding = CPythonBindingGenerator("", 0)
    assert bridge._native_array_descriptor_argument_type(required_policy) is required_type
    assert bridge._native_array_descriptor_argument_type(optional_policy) is optional_type
    assert binding._native_array_descriptor_argument_type(required_policy) is required_type
    assert binding._native_array_descriptor_argument_type(optional_policy) is optional_type


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
    assert FortranToCBridgeGenerator._ARRAY_INTEROP_POLICY_DISPATCHER.handlers == {
        ("argument", "data_buffer"): "_bridge_data_buffer_argument",
        ("argument", "descriptor"): "_bridge_descriptor_argument",
        ("module_variable", "data_buffer"): "_bridge_data_buffer_module_variable",
        ("module_variable", "descriptor"): "_bridge_descriptor_module_variable",
        ("result", "data_buffer"): "_bridge_data_buffer_result",
        ("result", "descriptor"): "_bridge_descriptor_result",
    }
    assert CPythonBindingGenerator._ARRAY_INTEROP_POLICY_DISPATCHER.handlers == {
        ("argument", "data_buffer"): "_bind_data_buffer_argument",
        ("argument", "descriptor"): "_bind_descriptor_argument",
        ("result", "data_buffer"): "_bind_data_buffer_result",
        ("result", "descriptor"): "_bind_descriptor_result",
    }
    assert (
        FortranToCBridgeGenerator._NATIVE_ARRAY_HANDLE_DISPATCHER.handlers[
            ("allocatable", "borrowed_module_descriptor")
        ]
        == "_bridge_borrowed_native_array_module_handle"
    )
    assert (
        CPythonBindingGenerator._NATIVE_ARRAY_HANDLE_DISPATCHER.handlers[("pointer", "borrowed_module_descriptor")]
        == "_bind_borrowed_native_array_module_handle"
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
        (CPythonBindingGenerator, "_NATIVE_ARRAY_DESCRIPTOR_ARGUMENT_DISPATCHER"),
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
        CPythonBindingGenerator._ARGUMENT_RETURN_PROJECTION_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.CALL_LOCAL_INPUT, True)
        ]
        == "_project_visible_argument_return"
    )
    assert (
        CPythonBindingGenerator._PROJECTED_ARGUMENT_OBJECT_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.CALL_LOCAL_INPUT, True)
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


@pytest.mark.parametrize(
    ("descriptor_kind", "annotation", "expected_operations"),
    [
        (
            "allocatable",
            "Allocatable[Float64[:]]",
            {
                "aligned",
                "allocated",
                "array_actual",
                "deallocate",
                "descriptor",
                "native_byte_order",
                "resize",
                "shape",
                "to_numpy",
                "writeable",
            },
        ),
        (
            "pointer",
            "Pointer[Float64[:]]",
            {
                "aligned",
                "array_actual",
                "associated",
                "contiguous",
                "descriptor",
                "native_byte_order",
                "nullify",
                "shape",
                "writeable",
            },
        ),
    ],
)
def test_native_array_handle_module_variable_bridge_uses_completed_handle_policy_dispatch(
    descriptor_kind,
    annotation,
    expected_operations,
):
    module = parse_pyi_text(
        f"""
values: {annotation}
""",
        module_name=f"{descriptor_kind}_native_handle_bridge_dispatch",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    generator = FortranToCBridgeGenerator("", 0)
    generator.scope = lowered.scope

    handle = generator._visit_Variable(lowered.variables[0])

    assert isinstance(handle, BindCNativeArrayHandleVariable)
    assert handle.native_array_handle_policy.handle_kind == "borrowed_module_descriptor"
    assert handle.native_array_handle_policy.descriptor_kind == descriptor_kind
    assert handle.original_variable is lowered.variables[0]
    assert set(handle.operation_functions) == expected_operations


def test_native_array_handle_module_operations_print_and_wrap_pointer_handoff_results():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
""",
        module_name="native_handle_module_operations",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    bridged = FortranToCBridgeGenerator("", 0)._visit_Module(lowered)

    fortran_code = FCodePrinter("native_handle_module_operations.f90", verbose=0)._visit(bridged)
    assert "function bind_c_private__x2py_values_shape()" in fortran_code
    assert "function bind_c_private__x2py_values_array_actual()" in fortran_code
    assert "function bind_c_private__x2py_values_descriptor()" in fortran_code
    assert "values_descriptor = c_null_ptr" in fortran_code

    cpython_module = CPythonBindingGenerator("", 0)._visit_Module(bridged)
    c_code = CPythonCodePrinter("native_handle_module_operations.c", verbose=0)._visit(cpython_module)
    assert "_native_array_handle_from_generated_ops" in c_code
    assert "PyLong_FromVoidPtr" in c_code
    assert "private__x2py_values_array_actual" in c_code
    assert "private__x2py_values_descriptor" in c_code
    assert "static PyObject* bind_c_private__x2py_values_array_actual(void)" not in c_code
    assert "static PyObject* bind_c_private__x2py_values_descriptor(void)" not in c_code
    assert "static PyObject* bind_c_private__x2py_values_array_actual_wrapper" in c_code
    assert "static PyObject* bind_c_private__x2py_values_descriptor_wrapper" in c_code


def test_native_array_handle_module_shape_changing_operations_use_scalar_extents():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:, :]]
target: Pointer[Float64[:]]
""",
        module_name="native_handle_module_shape_ops",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    bridged = FortranToCBridgeGenerator("", 0)._visit_Module(lowered)
    handles = {str(variable.name): variable for variable in bridged.variable_wrappers}

    assert {"resize"} <= set(handles["values"].operation_functions)
    assert {"allocate", "deallocate", "resize"}.isdisjoint(handles["target"].operation_functions)

    fortran_code = FCodePrinter("native_handle_module_shape_ops.f90", verbose=0)._visit(bridged)
    assert "subroutine bind_c_private__x2py_values_resize(extent_1, extent_2) bind(c)" in fortran_code
    assert "integer(i64), value :: extent_1" in fortran_code
    assert "allocate(values(0:extent_2 - 1_i64, 0:extent_1 - 1_i64))" in fortran_code

    cpython_module = CPythonBindingGenerator("", 0)._visit_Module(bridged)
    c_code = CPythonCodePrinter("native_handle_module_shape_ops.c", verbose=0)._visit(cpython_module)
    assert "private__x2py_values_resize" in c_code

    generator = FortranToCBridgeGenerator("", 0)
    generator.scope = lowered.scope
    pointer_policy = replace(
        lowered.variables[1].native_array_handle_policy,
        operations=("allocate", "associated", "deallocate", "nullify", "resize", "to_numpy"),
    )
    pointer_handle = generator._native_array_module_handle(lowered.variables[1], pointer_policy)

    assert {"allocate", "deallocate", "resize"} <= set(pointer_handle.operation_functions)
    assert pointer_handle.native_array_handle_policy is pointer_policy
    assert pointer_handle.operation_functions["allocate"].arguments[0].var.name == "extent_1"
    assert pointer_handle.operation_functions["resize"].arguments[0].var.name == "extent_1"
    assert "private__x2py_target_allocate" not in c_code


def test_native_array_handle_binding_builds_runtime_handle_from_named_generated_ops():
    module = parse_pyi_text(
        """
values: Allocatable[Float64[:]]
""",
        module_name="native_handle_binding_substrate",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    variable = lowered.variables[0]
    op_original = FunctionDef(
        "__x2py_values_shape",
        (),
        (),
        FunctionDefResult(NIL),
        scope=lowered.scope,
    )
    op_wrapper = BindCFunctionDef(
        "bind_c___x2py_values_shape",
        (),
        (),
        FunctionDefResult(NIL),
        original_function=op_original,
        scope=lowered.scope,
    )
    handle_variable = variable.clone(
        variable.name,
        new_class=BindCNativeArrayHandleVariable,
        operation_functions={"shape": op_wrapper},
        original_variable=variable,
    )

    binding = CPythonBindingGenerator("", 0)
    binding.scope = lowered.scope
    binding._native_array_handle_owner_module = Variable(PythonObjectType(), "mod", memory_handling="alias")
    body = binding._visit_BindCNativeArrayHandleVariable(handle_variable)

    call_names = {name for node in body for name in _model_call_names(node)}
    assert {
        "PyDict_New",
        "PyDict_SetItem",
        "PyImport_ImportModule",
        "PyObject_CallObject",
        "PyObject_GetAttrString",
    } <= call_names
    assert binding._python_object_map[handle_variable].name
    assert handle_variable.operation_functions == {"shape": op_wrapper}


def test_native_array_descriptor_view_reader_builds_runtime_mapping_from_cfi_descriptor_fields():
    binding = CPythonBindingGenerator("", 0)
    binding.scope = Scope(name="descriptor_reader", scope_type="function")
    descriptor_pointer = Variable(BindCPointer(), "descriptor", memory_handling="alias")
    descriptor_result = binding._new_python_object("descriptor_view")

    body = binding._native_array_descriptor_view_body(descriptor_pointer, descriptor_result, rank=2)

    call_names = {name for node in body for name in _model_call_names(node)}
    assert {
        "PyDict_New",
        "PyDict_SetItem",
        "PyList_Append",
        "PyList_New",
        "PyLong_FromLongLong",
        "PyLong_FromVoidPtr",
        "PyUnicode_FromString",
    } <= call_names


def test_native_array_descriptor_view_reader_prints_cfi_descriptor_access_without_global_requirement():
    binding = CPythonBindingGenerator("", 0)
    scope = Scope(name="descriptor_reader", scope_type="function")
    binding.scope = scope
    descriptor_pointer = Variable(BindCPointer(), "descriptor", memory_handling="alias", is_argument=True)
    descriptor_result = binding._new_python_object("descriptor_view")
    body = binding._native_array_descriptor_view_body(descriptor_pointer, descriptor_result, rank=2)
    body.append(Return(descriptor_result))
    function = FunctionDef(
        "decode_descriptor",
        (FunctionDefArgument(descriptor_pointer),),
        body,
        FunctionDefResult(descriptor_result),
        scope=scope,
    )

    printer = CPythonCodePrinter("test.c", verbose=0)
    code = printer._visit(function)

    assert "((CFI_cdesc_t*)descriptor)->base_addr" in code
    assert "((CFI_cdesc_t*)descriptor)->elem_len" in code
    assert "((CFI_cdesc_t*)descriptor)->rank" in code
    assert "((CFI_cdesc_t*)descriptor)->dim[INT64_C(0)].lower_bound" in code
    assert "((CFI_cdesc_t*)descriptor)->dim[INT64_C(1)].extent" in code
    assert "((CFI_cdesc_t*)descriptor)->dim[INT64_C(1)].sm" in code
    assert "PyLong_FromVoidPtr" in code
    assert "PyLong_FromLongLong" in code
    assert "ISO_Fortran_binding" in printer.get_additional_imports()


def test_pointer_descriptor_view_operation_wrapper_decodes_generated_cfi_descriptor_pointer():
    scope = Scope(name="descriptor_view_operation", scope_type="module")
    policy = _native_array_policy(
        descriptor_kind="pointer",
        handle_kind="borrowed_module_descriptor",
        to_numpy="descriptor_view",
        descriptor_interop="pointer_c_descriptor",
        operations=("associated", "nullify", "to_numpy"),
    )
    original = FunctionDef(
        "__x2py_target_to_numpy",
        (),
        (),
        FunctionDefResult(NIL),
        scope=scope,
    )
    descriptor_arg = Variable(BindCPointer(), "descriptor", is_argument=True, memory_handling="alias")
    operation = BindCFunctionDef(
        "bind_c___x2py_target_to_numpy",
        (FunctionDefArgument(descriptor_arg),),
        (),
        FunctionDefResult(NIL),
        original_function=original,
        scope=scope,
    )
    source_variable = Variable(
        NumpyNDArrayType.get_new(NumpyFloat64Type(), 1, "F"),
        "target",
        native_array_handle_policy=policy,
    )
    handle_variable = source_variable.clone(
        source_variable.name,
        new_class=BindCNativeArrayHandleVariable,
        operation_functions={"to_numpy": operation},
        original_variable=source_variable,
    )
    binding = CPythonBindingGenerator("", 0)
    binding.scope = scope

    wrapped = binding._native_array_descriptor_view_operation_wrapper(handle_variable, operation)
    call_names = set(_model_call_names(wrapped.body))
    code = CPythonCodePrinter("test.c", verbose=0)._visit(wrapped)

    assert "bind_c___x2py_target_to_numpy" in call_names
    assert {
        "PyDict_New",
        "PyDict_SetItem",
        "PyLong_FromLongLong",
        "PyLong_FromVoidPtr",
    } <= call_names
    assert "CFI_CDESC_T(1) target_descriptor_storage" in code
    assert "CFI_establish(target_descriptor, NULL, CFI_attribute_pointer, CFI_type_double" in code
    assert "bind_c___x2py_target_to_numpy(target_descriptor)" in code
    assert "((CFI_cdesc_t*)target_descriptor)->base_addr" in code
    assert "((CFI_cdesc_t*)target_descriptor)->dim[INT64_C(0)].sm" in code


def test_native_array_handle_operation_wrapper_uses_descriptor_reader_only_for_pointer_descriptor_view():
    policy = _native_array_policy(
        descriptor_kind="pointer",
        handle_kind="borrowed_module_descriptor",
        to_numpy="descriptor_view",
        descriptor_interop="pointer_c_descriptor",
        operations=("associated", "nullify", "to_numpy"),
    )
    variable = Variable(
        NumpyNDArrayType.get_new(NumpyFloat64Type(), 1, "F"),
        "target",
        native_array_handle_policy=policy,
    )
    binding = CPythonBindingGenerator("", 0)

    assert binding._uses_native_array_descriptor_view_operation_wrapper(variable, "to_numpy") is True
    assert binding._uses_native_array_descriptor_view_operation_wrapper(variable, "associated") is False
    assert (
        binding._uses_native_array_descriptor_view_operation_wrapper(
            variable.clone(
                variable.name,
                native_array_handle_policy=_native_array_policy(
                    descriptor_kind="pointer",
                    handle_kind="borrowed_module_descriptor",
                    to_numpy="unsupported",
                    operations=("associated", "nullify", "to_numpy"),
                ),
            ),
            "to_numpy",
        )
        is False
    )


def test_cfi_descriptor_type_printing_is_local_to_descriptor_reader_path():
    descriptor = Variable(CFIDescriptorType(), "descriptor", memory_handling="alias")
    printer = CCodePrinter("test.c", verbose=0)

    assert printer._get_declare_type(descriptor) == "CFI_cdesc_t*"
    assert "ISO_Fortran_binding" in printer.get_additional_imports()


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

    bridged = FortranToCBridgeGenerator("", 0)._visit_Module(lowered)
    wrapped_field = bridged.classes[0].attributes[0]

    assert isinstance(wrapped_field, BindCNativeArrayHandleProperty)
    assert wrapped_field.owner_class is lowered.classes[0]
    assert wrapped_field.native_array_handle_policy is policy
    expected_operations = {
        "aligned",
        "array_actual",
        "descriptor",
        "native_byte_order",
        "shape",
        "writeable",
        "allocated" if descriptor_kind == "allocatable" else "associated",
        "deallocate" if descriptor_kind == "allocatable" else "nullify",
        "resize" if descriptor_kind == "allocatable" else "descriptor",
    }
    if descriptor_kind == "pointer":
        expected_operations.add("contiguous")
    assert expected_operations <= set(wrapped_field.operation_functions)

    fortran_code = FCodePrinter("field_handle.f90", verbose=0)._visit(bridged)
    assert "self%values" in fortran_code
    if descriptor_kind == "allocatable":
        assert "bound_values = c_loc(values(lbound(values," in fortran_code
        assert "kind=i64)))" in fortran_code

    cpython_module = CPythonBindingGenerator("", 0)._visit_Module(bridged)
    c_code = CPythonCodePrinter("field_handle.c", verbose=0)._visit(cpython_module)
    assert "_native_array_handle_from_generated_ops" in c_code
    assert "values_handle_getter" in c_code


def test_native_array_handle_result_generation_uses_completed_handle_policy_dispatch():
    module = parse_pyi_text(
        """
def make_values() -> Allocatable[Float64[:]]: ...
""",
        module_name="native_handle_result_dispatch",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    bridged = FortranToCBridgeGenerator("", 0)._visit_Module(lowered)
    fortran_code = FCodePrinter("owned_result.f90", verbose=0)._visit(bridged)
    assert "if (allocated(make_values" in fortran_code
    assert "deallocate(make_values" in fortran_code

    cpython_module = CPythonBindingGenerator("", 0)._visit_Module(bridged)
    c_code = CPythonCodePrinter("owned_result.c", verbose=0)._visit(cpython_module)
    assert "sizeof(CFI_CDESC_T(1))" in c_code
    assert "CFI_attribute_allocatable" in c_code
    assert "CFI_allocate(" in c_code
    assert "CFI_deallocate(" in c_code
    assert 'PyUnicode_FromString("owned")' in c_code
    assert "_native_array_handle_from_generated_ops" in c_code


def test_hidden_allocatable_handle_output_completes_as_owned_result_before_lowering():
    module = parse_pyi_text(
        """
@native_call([Return("values", 0)])
def make_values() -> Allocatable[Float64[:]]: ...
""",
        module_name="hidden_allocatable_handle_result",
    )
    complete_semantic_policies(module)

    argument = module.functions[0].arguments[0]
    decision = argument.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    policy = argument.metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]

    assert decision.owner is OwnershipOwner.WRAPPER
    assert decision.transfer is TransferMode.WRAPPER_INSTANCE
    assert decision.destruction is DestructionPolicy.WRAPPER_DEALLOC
    assert decision.codegen_action is CodegenAction.HIDDEN_OUTPUT
    assert decision.native_barrier_action is NativeBarrierAction.PASS_ARRAY_DESCRIPTOR
    assert policy.handle_kind == "owned_result_descriptor"
    assert policy.origin == "projected_result"
    assert policy.owner_retention == "wrapper_owner_storage"
    assert policy.descriptor_ownership == "owned"
    assert policy.output_projection == "projected_handle"

    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    bridged = FortranToCBridgeGenerator("", 0)._visit_Module(lowered)
    cpython_module = CPythonBindingGenerator("", 0)._visit_Module(bridged)
    c_code = CPythonCodePrinter("hidden_owned_result.c", verbose=0)._visit(cpython_module)
    assert "CFI_attribute_allocatable" in c_code
    assert "CFI_allocate(" in c_code
    assert "private__x2py_owned_values_destroy" in c_code


@pytest.mark.parametrize(
    ("descriptor_kind", "annotation"),
    [
        ("allocatable", "Allocatable[Float64[:]]"),
        (
            "pointer",
            "Annotated[Pointer[Float64[:]], PointerPolicy(nullable=True, transfer='call_local', "
            "target_owner='caller', lifetime='call', deallocation='deallocate_resize', "
            "shape_source='pointer_bounds', contiguity='contiguous', reassociation='allocate_resize', "
            "aliasing='descriptor', mutability='mutable')]",
        ),
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
    decision = argument.var.ownership_decision
    policy = argument.var.native_array_handle_policy

    assert decision.codegen_action is CodegenAction.IN_PLACE_ARGUMENT
    assert decision.mutates_native is True
    assert decision.projects_result is True
    assert policy.descriptor_kind == descriptor_kind
    assert policy.handle_kind == "argument_descriptor"
    assert policy.output_projection == "projected_handle"
    assert policy.blocker is None

    bridge = FortranToCBridgeGenerator("", 0)
    bridge.scope = lowered.funcs[0].scope
    bridged = bridge._convert_argument(argument, lowered.funcs[0])

    descriptor_arg = bridged["c_arg"].var
    descriptor_dummy = lowered.funcs[0].scope.collect_tuple_element(
        IndexedElement(descriptor_arg.new_var, convert_to_literal(0)),
    )
    f_printer = FCodePrinter("test.f90", verbose=0)
    f_printer.set_scope(lowered.funcs[0].scope)
    f_printer._kind = lambda expr: "f64"
    fortran_declaration = f_printer._visit(Declare(descriptor_dummy))
    assert descriptor_arg.class_type is BindCNativeArrayDescriptorType.get_new(has_presence=False)
    assert descriptor_dummy.native_array_handle_policy is policy
    assert descriptor_dummy.memory_handling == ("alias" if descriptor_kind == "pointer" else "heap")
    assert descriptor_dummy.is_argument is True
    assert bridged["body"] == []
    assert bridged["optional_presence_var"] is None
    assert CCodePrinter("test.c", verbose=0)._get_declare_type(descriptor_dummy) == "void*"
    assert (", pointer" if descriptor_kind == "pointer" else ", allocatable") in fortran_declaration
    assert f_printer._fortran_argument_access(descriptor_dummy) == "readwrite"
    assert "values" in str(bridged["f_arg"])

    binding = CPythonBindingGenerator("", 0)
    binding.scope = lowered.funcs[0].scope
    collect_arg = Variable(PythonObjectType(), "py_values", memory_handling="alias")
    converted = binding._convert_argument(
        argument.var,
        collect_arg,
        bound_argument=False,
        is_bind_c_argument=False,
    )

    assert converted["args"][0].class_type is BindCNativeArrayDescriptorType.get_new(has_presence=False)
    assert converted["owns_type_check"] is True
    assert len(converted["body"]) > 0
    assert len(converted["default_init"]) == 1


@pytest.mark.parametrize(
    ("descriptor_kind", "annotation"),
    [
        ("allocatable", "Allocatable[Float64[:]]"),
        ("pointer", "Pointer[Float64[:]]"),
    ],
)
def test_native_array_optional_handle_argument_binding_uses_presence_tuple(
    descriptor_kind,
    annotation,
):
    module = parse_pyi_text(
        f"""
def maybe(values: {annotation} | None = ...) -> None: ...
""",
        module_name=f"{descriptor_kind}_optional_handle_argument_binding",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    argument = lowered.funcs[0].arguments[0]
    policy = argument.var.native_array_handle_policy

    assert policy.descriptor_kind == descriptor_kind
    assert policy.handle_kind == "optional_absent_handle"
    assert policy.optional_absent is True

    bridge = FortranToCBridgeGenerator("", 0)
    bridge.scope = lowered.funcs[0].scope
    bridged = bridge._convert_argument(argument, lowered.funcs[0])

    descriptor_arg = bridged["c_arg"].var
    descriptor_dummy = lowered.funcs[0].scope.collect_tuple_element(
        IndexedElement(descriptor_arg.new_var, convert_to_literal(0)),
    )
    presence_var = lowered.funcs[0].scope.collect_tuple_element(
        IndexedElement(descriptor_arg.new_var, convert_to_literal(1)),
    )
    assert descriptor_arg.class_type is BindCNativeArrayDescriptorType.get_new(has_presence=True)
    assert descriptor_dummy.native_array_handle_policy is policy
    assert descriptor_dummy.is_optional is True
    assert descriptor_dummy.memory_handling == ("alias" if descriptor_kind == "pointer" else "heap")
    assert bridged["optional_presence_var"] is presence_var
    assert presence_var.is_argument is True
    assert bridged["body"] == []

    binding = CPythonBindingGenerator("", 0)
    binding.scope = lowered.funcs[0].scope
    collect_arg = Variable(PythonObjectType(), "py_values", memory_handling="alias")
    converted = binding._convert_argument(
        argument.var,
        collect_arg,
        bound_argument=False,
        is_bind_c_argument=False,
    )

    assert converted["args"][0].class_type is BindCNativeArrayDescriptorType.get_new(has_presence=True)
    assert converted["owns_type_check"] is True
    assert len(converted["default_init"]) == 2
    assert len(converted["body"]) > 0


def test_native_array_descriptor_argument_binding_forwards_fixed_rank_one_extent():
    module = parse_pyi_text(
        """
def fill(values: Allocatable[Float64[2]]) -> None: ...
""",
        module_name="allocatable_handle_fixed_extent_binding",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    argument = lowered.funcs[0].arguments[0]
    binding = CPythonBindingGenerator("", 0)

    assert binding._rank_one_fixed_extent(argument.var) == 2


def test_normal_array_bind_c_argument_binding_uses_native_handle_fallback():
    module = parse_pyi_text(
        """
def fill(values: Float64[:]) -> None: ...
""",
        module_name="normal_array_handle_fallback_binding",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    argument = lowered.funcs[0].arguments[0]
    binding = CPythonBindingGenerator("", 0)
    binding.scope = lowered.funcs[0].scope
    collect_arg = Variable(PythonObjectType(), "py_values", memory_handling="alias")

    converted = binding._convert_argument(
        argument.var,
        collect_arg,
        bound_argument=False,
        is_bind_c_argument=True,
    )

    descriptor_type = converted["args"][0].class_type
    assert isinstance(descriptor_type, BindCArrayType)
    assert descriptor_type.has_rank is False
    assert descriptor_type.has_itemsize is False
    assert descriptor_type.has_strides is False
    assert converted["owns_type_check"] is True
    assert len(converted["body"]) == 1
    assert len(converted["body"][0].blocks) == 2
    assert "array_actual_helper" in str(converted["body"][0])


@pytest.mark.parametrize(
    "annotation",
    [
        "Float64[...]",
        "String[8][:]",
    ],
)
def test_normal_array_bind_c_argument_binding_keeps_specialized_array_paths(annotation):
    module = parse_pyi_text(
        f"""
def fill(values: {annotation}) -> None: ...
""",
        module_name="specialized_array_binding",
    )
    complete_semantic_policies(module)
    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    argument = lowered.funcs[0].arguments[0]
    binding = CPythonBindingGenerator("", 0)

    assert binding._bind_c_array_argument_uses_native_handle_fallback(argument.var) is False


def test_optional_normal_array_bind_c_argument_does_not_use_native_handle_fallback():
    argument = Variable(
        NumpyNDArrayType.get_new(NumpyFloat64Type(), 1, "F"),
        "values",
        is_optional=True,
    )
    binding = CPythonBindingGenerator("", 0)

    assert argument.is_optional is True
    assert binding._bind_c_array_argument_uses_native_handle_fallback(argument) is False


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
        (
            "blocked",
            _array_type(pointer=True),
            _hidden_output_context(projects_result=True, python_visible=False),
        ),
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
        "pointer array container descriptor ownership is fixed by its native parent; "
        "use PointerPolicy for extraction and descriptor operations"
    )
    module_overridden = default_ownership_policy.decide_semantic_type(
        _array_type(pointer=True, metadata=metadata),
        OwnershipContext.module_variable(),
    )
    assert module_overridden.is_blocked
    assert module_overridden.blocker == (
        "pointer array container descriptor ownership is fixed by its native parent; "
        "use PointerPolicy for extraction and descriptor operations"
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
    assert "use PointerPolicy for extraction and descriptor operations" in parsed.blocker

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
    assert module_policy.descriptor_interop == "pointer_c_descriptor"
    assert module_policy.requires_pointer_c_descriptor_interop is True
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
    assert field_policy.descriptor_interop == "pointer_c_descriptor"
    assert field_policy.requires_pointer_c_descriptor_interop is True
    assert field_policy.target_lifetime == "parent_wrapper"
    assert field_policy.destroy_behavior == "parent_wrapper_finalizer"
    assert set(field_policy.operations) == {"associated", "nullify", "to_numpy"}


def test_complete_pointer_policy_metadata_round_trips_without_overriding_container_ownership():
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
    assert not decision.is_blocked
    assert decision.owner is OwnershipOwner.NATIVE
    assert decision.transfer is TransferMode.BORROWED_VIEW
    assert decision.destruction is DestructionPolicy.NATIVE_OWNER


def test_complete_contiguous_pointer_policy_enables_module_copy_handle():
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
    assert not handle_policy.is_blocked
    assert handle_policy.getter_behavior == "handle"
    assert handle_policy.to_numpy == "copy_only"
    assert handle_policy.descriptor_interop == "pointer_c_descriptor"
    assert handle_policy.requires_pointer_c_descriptor_interop is True
    assert handle_policy.blocker is None


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
        module.functions[0].arguments[0].metadata[RESOLVED_OWNERSHIP_POLICY_METADATA].transfer is TransferMode.IN_PLACE
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
    assert arg_var.ownership_decision.owner is OwnershipOwner.CALLER
    assert codegen_action_for_variable(arg_var) is CodegenAction.IN_PLACE_ARGUMENT


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
    assert field_target.descriptor_interop == "pointer_c_descriptor"
    assert field_target.requires_pointer_c_descriptor_interop is True
    assert field_target.is_blocked is False
    assert set(field_target.operations) == {"associated", "nullify", "to_numpy"}

    assert argument_values.handle_kind == "argument_descriptor"
    assert argument_values.origin == "argument"
    assert argument_values.owner_retention == "caller_handle"
    assert argument_values.target_lifetime == "call"
    assert argument_values.destroy_behavior == "none"
    assert argument_values.is_blocked is False
    assert argument_values.blocker is None
    assert argument_values.descriptor_interop == "none"
    assert argument_values.requires_pointer_c_descriptor_interop is False
    assert set(argument_values.operations) == {"allocated", "to_numpy"}

    assert optional_target.handle_kind == "optional_absent_handle"
    assert optional_target.optional_absent is True
    assert optional_target.nullable is True
    assert optional_target.owner_retention == "optional_argument"
    assert optional_target.target_lifetime == "absent_or_call"
    assert optional_target.destroy_behavior == "none"
    assert optional_target.is_blocked is False
    assert optional_target.blocker is None
    assert optional_target.descriptor_interop == "pointer_c_descriptor"
    assert optional_target.requires_pointer_c_descriptor_interop is True
    assert set(optional_target.operations) == {"associated", "nullify", "to_numpy"}
    assert "allocate" not in optional_target.operations
    assert "deallocate" not in optional_target.operations
    assert "resize" not in optional_target.operations

    assert managed_target.handle_kind == "argument_descriptor"
    assert managed_target.descriptor_kind == "pointer"
    assert managed_target.target_lifetime == "call"
    assert managed_target.destroy_behavior == "none"
    assert managed_target.is_blocked is False
    assert managed_target.blocker is None
    assert managed_target.to_numpy == "contiguous_view"
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
    assert allocatable_result.is_blocked is False
    assert allocatable_result.descriptor_interop == "owned_allocatable_c_descriptor"
    assert allocatable_result.requires_pointer_c_descriptor_interop is False
    assert allocatable_result.requires_c_descriptor_interop is True
    assert set(allocatable_result.operations) == {"allocated", "deallocate", "resize", "to_numpy"}

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
    copy_target: Annotated[
        Pointer[Float64[:]],
        PointerPolicy(
            nullable=True,
            transfer="snapshot_copy",
            target_owner="caller",
            lifetime="call",
            deallocation="never",
            shape_source="pointer_bounds",
            contiguity="contiguous",
            reassociation="never",
            aliasing="independent_copy",
            mutability="copy",
        ),
    ],
    contiguous_target: Annotated[
        Pointer[Float64[:]],
        PointerPolicy(
            nullable=True,
            transfer="call_local",
            target_owner="caller",
            lifetime="call",
            deallocation="never",
            shape_source="pointer_bounds",
            contiguity="contiguous",
            reassociation="never",
            aliasing="borrowed",
            mutability="view",
        ),
    ],
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

    copy_target = module.functions[0].arguments[0].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    contiguous_target = module.functions[0].arguments[1].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]
    descriptor_target = module.functions[0].arguments[2].metadata[RESOLVED_NATIVE_ARRAY_HANDLE_POLICY_METADATA]

    assert copy_target.to_numpy == "copy_only"
    assert copy_target.requires_pointer_c_descriptor_interop is True
    assert contiguous_target.to_numpy == "contiguous_view"
    assert contiguous_target.requires_pointer_c_descriptor_interop is True
    assert descriptor_target.to_numpy == "descriptor_view"
    assert descriptor_target.requires_pointer_c_descriptor_interop is True

    requirements = native_array_handle_build_requirements(module)

    assert requirements.pointer_c_descriptor_interop is True
    assert requirements.requires_iso_fortran_binding is True
    assert requirements.headers == ("ISO_Fortran_binding.h",)
    assert requirements.items == (
        NativeArrayBuildRequirement(
            owner="native_handle_build.default_target",
            item="default_target",
            descriptor_kind="pointer",
            handle_kind="borrowed_module_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
        NativeArrayBuildRequirement(
            owner="native_handle_build.inspect.copy_target",
            item="copy_target",
            descriptor_kind="pointer",
            handle_kind="argument_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
        NativeArrayBuildRequirement(
            owner="native_handle_build.inspect.contiguous_target",
            item="contiguous_target",
            descriptor_kind="pointer",
            handle_kind="argument_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
        NativeArrayBuildRequirement(
            owner="native_handle_build.inspect.target",
            item="target",
            descriptor_kind="pointer",
            handle_kind="argument_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
    )


def test_native_array_handle_build_requirements_include_default_pointer_descriptor_accessors():
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

    assert requirements.pointer_c_descriptor_interop is True
    assert requirements.requires_iso_fortran_binding is True
    assert requirements.headers == ("ISO_Fortran_binding.h",)
    assert requirements.items == (
        NativeArrayBuildRequirement(
            owner="native_handle_no_interop.target",
            item="target",
            descriptor_kind="pointer",
            handle_kind="borrowed_module_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
        NativeArrayBuildRequirement(
            owner="native_handle_no_interop.box.target",
            item="target",
            descriptor_kind="pointer",
            handle_kind="borrowed_field_descriptor",
            descriptor_interop="pointer_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
    )


def test_owned_allocatable_result_records_local_standard_c_descriptor_build_requirement():
    module = parse_pyi_text(
        """
def make_values() -> Allocatable[Float64[:]]: ...
""",
        module_name="owned_allocatable_build",
    )
    complete_semantic_policies(module)

    requirements = native_array_handle_build_requirements(module)

    assert requirements.pointer_c_descriptor_interop is False
    assert requirements.requires_iso_fortran_binding is True
    assert requirements.headers == ("ISO_Fortran_binding.h",)
    assert requirements.items == (
        NativeArrayBuildRequirement(
            owner="owned_allocatable_build.make_values.return",
            item="return",
            descriptor_kind="allocatable",
            handle_kind="owned_result_descriptor",
            descriptor_interop="owned_allocatable_c_descriptor",
            headers=("ISO_Fortran_binding.h",),
        ),
    )


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
