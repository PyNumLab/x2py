"""Tests split by stable ownership concept from `test_handle_policy_dispatch.py`."""

from tests._shared.ownership_policy_support import (
    ADDRESS_ROLE_METADATA,
    ADDRESS_ROLE_PROJECTION,
    AssignmentMode,
    BindCScalarModuleVariable,
    CPythonBindingGenerator,
    CPythonCodePrinter,
    CodegenAction,
    DestructionPolicy,
    FCodePrinter,
    FortranToCBridgeGenerator,
    MODULE_VARIABLE_INITIALIZER_UNSUPPORTED_BLOCKER,
    NativeArrayBuildRequirement,
    NativeBarrierAction,
    ObjectKind,
    OwnershipOwner,
    POLICY_COMPLETION_PREPARED_METADATA,
    PYTHON_EXPORTS_METADATA,
    PYTHON_EXPORTS_PREPARED_METADATA,
    PythonBarrierAction,
    RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_MODULE_VARIABLE_INITIALIZER_METADATA,
    RESOLVED_OWNERSHIP_POLICY_METADATA,
    RESOLVED_RETURN_OWNERSHIP_POLICY_METADATA,
    RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA,
    RESOLVED_SNAPSHOT_FIELD_ACTION_METADATA,
    Scope,
    SemanticClass,
    SemanticConstraint,
    SemanticField,
    SemanticFunction,
    SemanticModule,
    SemanticType,
    SemanticVariable,
    SetterAction,
    StorageMode,
    TransferMode,
    _array_type,
    _derived_type,
    _scalar_type,
    _semantic_ir_to_codegen_ast,
    complete_semantic_policies,
    native_array_descriptor_kind,
    native_array_handle_build_requirements,
    parse_pyi_text,
    pytest,
    replace,
    semantic_ir_to_codegen_ast,
    set_ownership_metadata,
)


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


def test_derived_module_constant_uses_wrapper_owned_copy_without_setter():
    constant_type = _derived_type("rgb_color")
    constant_type.constraints.append(SemanticConstraint("Constant"))
    module = SemanticModule(
        name="colors",
        variables=[SemanticVariable("black", constant_type)],
        classes=[
            SemanticClass(
                "rgb_color",
                fields=[
                    SemanticField("r", _scalar_type()),
                    SemanticField("g", _scalar_type()),
                    SemanticField("b", _scalar_type()),
                ],
            )
        ],
    )

    complete_semantic_policies(module)

    variable = module.variables[0]
    storage = variable.metadata[RESOLVED_OWNERSHIP_POLICY_METADATA]
    getter = variable.metadata[RESOLVED_GETTER_OWNERSHIP_POLICY_METADATA]
    setter = variable.metadata[RESOLVED_SETTER_OWNERSHIP_POLICY_METADATA]
    assert storage.kind is ObjectKind.DERIVED_TYPE
    assert storage.owner is OwnershipOwner.WRAPPER
    assert storage.transfer is TransferMode.WRAPPER_INSTANCE
    assert storage.destruction is DestructionPolicy.WRAPPER_DEALLOC
    assert getter.transfer is TransferMode.WRAPPER_INSTANCE
    assert setter.setter_action is SetterAction.OMIT

    lowered = _semantic_ir_to_codegen_ast(module, Scope(name=module.name, scope_type="module"))
    generator = FortranToCBridgeGenerator("", 0)
    generator.scope = lowered.scope
    constant = generator._visit_Variable(lowered.variables[0])
    assert isinstance(constant, BindCScalarModuleVariable)
    assert constant.setter_function is None


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
