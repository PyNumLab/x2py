"""Tests split by stable ownership concept from `test_handle_policy_dispatch.py`."""

from tests._shared.ownership_policy_support import (
    BindCArrayType,
    BindCFunctionDef,
    BindCNativeArrayDescriptorType,
    BindCNativeArrayHandleVariable,
    BindCPointer,
    CCodePrinter,
    CFIDescriptorType,
    CPythonBindingGenerator,
    CPythonCodePrinter,
    CodegenAction,
    DestructionPolicy,
    FortranToCBridgeGenerator,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    IndexedElement,
    NIL,
    NativeBarrierAction,
    NumpyFloat64Type,
    NumpyNDArrayType,
    ObjectKind,
    PythonBarrierAction,
    PythonObjectType,
    Scope,
    SetterAction,
    Variable,
    _model_call_names,
    _native_array_policy,
    _semantic_ir_to_codegen_ast,
    complete_semantic_policies,
    convert_to_literal,
    parse_pyi_text,
    pytest,
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
