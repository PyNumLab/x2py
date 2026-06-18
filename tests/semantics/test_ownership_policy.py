from x2py.codegen.bindings.c_to_python import CPythonBindingGenerator
from x2py.codegen.bridges.fortran_to_c import FortranToCBridgeGenerator
from x2py.codegen.printers.pyi_printer import PyiPrinter
from x2py.codegen.scope import Scope
from x2py.ownership_policy import (
    CodegenAction,
    DestructionPolicy,
    ObjectKind,
    OwnershipActionDispatcher,
    OwnershipContext,
    OwnershipDecision,
    OwnershipOwner,
    OwnershipPolicyResolver,
    TransferMode,
    codegen_action_for_variable,
    default_ownership_policy,
    set_ownership_metadata,
)
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast
from x2py.semantics.models import (
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
from x2py.semantics.pyi_parser import parse_pyi_text


def _scalar_type(name: str = "Int32") -> SemanticType:
    return SemanticType(name=name, dtype=name)


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

    string_replacement = resolver.decide_semantic_type(_string_type(), OwnershipContext.argument("inout"))
    assert string_replacement.owner is OwnershipOwner.PYTHON
    assert string_replacement.transfer is TransferMode.COPY_RETURN
    assert "immutable Python strings" in string_replacement.reason

    caller_array = resolver.decide_semantic_type(_array_type(), OwnershipContext.argument("out"))
    assert caller_array.owner is OwnershipOwner.CALLER
    assert caller_array.transfer is TransferMode.IN_PLACE
    assert caller_array.codegen_action is CodegenAction.IN_PLACE_ARGUMENT

    allocatable_output = resolver.decide_semantic_type(
        _array_type(allocatable=True),
        OwnershipContext.argument("out"),
    )
    assert allocatable_output.owner is OwnershipOwner.PYTHON
    assert allocatable_output.transfer is TransferMode.COPY_RETURN
    assert allocatable_output.memory_handling == "heap"
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
    assert decision.memory_handling == "heap"
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
        )

    class Target:
        def snapshot(self, var, decision, marker):
            return marker, var.rank, decision.codegen_action

        def default(self, var, decision, marker):
            return "default", marker

    dispatcher = OwnershipActionDispatcher(
        {CodegenAction.SNAPSHOT_COPY_ARRAY: "snapshot"},
        "default",
    )

    assert dispatcher.dispatch(Target(), FakeVar(), "seen") == (
        "seen",
        1,
        CodegenAction.SNAPSHOT_COPY_ARRAY,
    )


def test_bridge_and_binding_generators_expose_ownership_action_maps():
    assert CPythonBindingGenerator._RESULT_DETAIL_DISPATCHER.handlers == {
        CodegenAction.SNAPSHOT_COPY_ARRAY: "_snapshot_copy_result_detail_lines",
    }
    assert CPythonBindingGenerator._RESULT_NOTE_DISPATCHER.handlers == {
        CodegenAction.COPY_RETURN_ARRAY: "_copy_return_result_notes",
        CodegenAction.SNAPSHOT_COPY_ARRAY: "_snapshot_copy_result_notes",
        CodegenAction.BORROWED_VIEW: "_borrowed_view_result_notes",
    }
    assert FortranToCBridgeGenerator._NDARRAY_RESULT_DISPATCHER.handlers == {
        CodegenAction.SNAPSHOT_COPY_ARRAY: "_extract_snapshot_copy_array_result",
        CodegenAction.BORROWED_VIEW: "_extract_borrowed_array_result",
        CodegenAction.COPY_RETURN_ARRAY: "_extract_copy_return_array_result",
    }


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
    assert parsed.codegen_action is CodegenAction.SNAPSHOT_COPY_ARRAY

    emitted = PyiPrinter().emit_semantic_type(field_type)
    assert 'Ownership("python")' in emitted
    assert 'Transfer("snapshot_copy")' in emitted
    assert 'Destruction("python_refcount")' in emitted


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


def test_ir_lowering_attaches_policy_decisions_used_by_codegen_dispatch():
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
            )
        ],
    )

    codegen_module = semantic_ir_to_codegen_ast(
        module,
        Scope(name=module.name, scope_type="module"),
    )

    module_var = codegen_module.variables[0]
    field_var = codegen_module.classes[0].attributes[0]
    arg_var = codegen_module.funcs[0].arguments[0].var

    assert module_var.ownership_decision.owner is OwnershipOwner.NATIVE
    assert field_var.ownership_decision.owner is OwnershipOwner.WRAPPER
    assert arg_var.ownership_decision.owner is OwnershipOwner.PYTHON
    assert codegen_action_for_variable(arg_var) is CodegenAction.COPY_RETURN_ARRAY
