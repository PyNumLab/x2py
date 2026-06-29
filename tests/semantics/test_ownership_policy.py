import pytest

from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator
from x2py.codegen.printers.pyi_printer import PyiPrinter
from x2py.codegen.scope import Scope
from x2py.ownership_policy import (
    AssignmentMode,
    CodegenAction,
    DestructionPolicy,
    ObjectKind,
    OwnershipContext,
    OwnershipDecision,
    OwnershipOwner,
    OwnershipPolicyResolver,
    PolicyActionDispatcher,
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
    RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA,
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
from x2py.semantics.pyi2ir import parse_pyi_text


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


def _derived_type(name: str = "point") -> SemanticType:
    return SemanticType(name=name, dtype=name)


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
        OwnershipContext.argument("inout", projects_result=True),
    )
    assert string_replacement.owner is OwnershipOwner.PYTHON
    assert string_replacement.transfer is TransferMode.COPY_RETURN
    assert "immutable Python strings" in string_replacement.reason

    caller_array = resolver.decide_semantic_type(_array_type(), OwnershipContext.argument("out"))
    assert caller_array.owner is OwnershipOwner.CALLER
    assert caller_array.transfer is TransferMode.IN_PLACE
    assert caller_array.codegen_action is CodegenAction.IDENTITY_OUTPUT

    projected_caller_array = resolver.decide_semantic_type(
        _array_type(),
        OwnershipContext.argument("out", projects_result=True, python_visible=True),
    )
    assert projected_caller_array.transfer is TransferMode.IN_PLACE
    assert projected_caller_array.codegen_action is CodegenAction.IDENTITY_OUTPUT

    allocatable_output = resolver.decide_semantic_type(
        _array_type(allocatable=True),
        OwnershipContext.argument("out", projects_result=True, python_visible=False),
    )
    assert allocatable_output.owner is OwnershipOwner.PYTHON
    assert allocatable_output.transfer is TransferMode.COPY_RETURN
    assert allocatable_output.storage_mode is StorageMode.HEAP
    assert allocatable_output.nullable is True

    module_allocatable = resolver.decide_semantic_type(
        _array_type(allocatable=True, metadata={"fortran_target": True}),
        OwnershipContext.module_variable(),
    )
    assert module_allocatable.owner is OwnershipOwner.NATIVE
    assert module_allocatable.transfer is TransferMode.BORROWED_VIEW
    assert module_allocatable.destruction is DestructionPolicy.NATIVE_OWNER

    derived_output = resolver.decide_semantic_type(_derived_type(), OwnershipContext.result())
    assert derived_output.owner is OwnershipOwner.WRAPPER
    assert derived_output.transfer is TransferMode.WRAPPER_INSTANCE

    projected_derived_output = resolver.decide_semantic_type(
        _derived_type(),
        OwnershipContext.argument("out", projects_result=True, python_visible=True),
    )
    assert projected_derived_output.transfer is TransferMode.IN_PLACE
    assert projected_derived_output.codegen_action is CodegenAction.IDENTITY_OUTPUT

    hidden_derived_output = resolver.decide_semantic_type(
        _derived_type(),
        OwnershipContext.argument("out", projects_result=True, python_visible=False),
    )
    assert hidden_derived_output.transfer is TransferMode.WRAPPER_INSTANCE
    assert hidden_derived_output.codegen_action is CodegenAction.HIDDEN_OUTPUT

    derived_field = resolver.decide_semantic_type(_derived_type(), OwnershipContext.field())
    assert derived_field.owner is OwnershipOwner.WRAPPER
    assert derived_field.transfer is TransferMode.BORROWED_VIEW
    assert derived_field.destruction is DestructionPolicy.WRAPPER_DEALLOC


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


def test_bridge_and_binding_generators_expose_ownership_action_maps():
    assert (
        CPythonBindingGenerator._RESULT_DETAIL_DISPATCHER.handlers[
            (ObjectKind.NUMPY_ARRAY, CodegenAction.SNAPSHOT_COPY)
        ]
        == "_snapshot_copy_result_detail_lines"
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
    dispatchers = (
        (FortranToCBridgeGenerator, "_ARGUMENT_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_RESULT_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_REPLACEMENT_RESULT_DISPATCHER"),
        (FortranToCBridgeGenerator, "_NDARRAY_RESULT_DISPATCHER"),
        (FortranToCBridgeGenerator, "_MODULE_VARIABLE_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_CALLBACK_ARGUMENT_POLICY_DISPATCHER"),
        (FortranToCBridgeGenerator, "_CALLBACK_RESULT_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_ARGUMENT_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_ARGUMENT_DETAIL_DISPATCHER"),
        (CPythonBindingGenerator, "_RESULT_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_RESULT_DETAIL_DISPATCHER"),
        (CPythonBindingGenerator, "_RESULT_NOTE_DISPATCHER"),
        (CPythonBindingGenerator, "_PROPERTY_SETTER_POLICY_DISPATCHER"),
        (CPythonBindingGenerator, "_BORROWED_GETTER_POLICY_DISPATCHER"),
    )
    for generator, dispatcher_name in dispatchers:
        dispatcher = getattr(generator, dispatcher_name)
        assert dispatcher.handlers
        assert all(hasattr(generator, handler_name) for handler_name in dispatcher.handlers.values())


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


def test_pyi_policy_metadata_changes_pointer_field_behavior_and_round_trips():
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
    assert overridden.owner is OwnershipOwner.PYTHON
    assert overridden.transfer is TransferMode.SNAPSHOT_COPY
    assert overridden.destruction is DestructionPolicy.PYTHON_REFCOUNT
    assert not overridden.is_blocked

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
    assert parsed.transfer is TransferMode.SNAPSHOT_COPY
    assert parsed.codegen_action is CodegenAction.SNAPSHOT_COPY

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
                _array_type(allocatable=True, metadata={"fortran_target": True}),
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
                arguments=[SemanticArgument("n", _scalar_type(), intent="in")],
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
                _array_type(allocatable=True, metadata={"fortran_target": True}),
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
                arguments=[SemanticArgument("values", _array_type(allocatable=True), intent="inout")],
                return_type=None,
                projection=[
                    ProjectionMapping(
                        python_name="values",
                        native_name="values",
                        native_position=0,
                        python_position=0,
                        result_position=0,
                        intent="inout",
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
