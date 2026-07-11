"""Tests split by stable ownership concept from `test_handle_policy_dispatch.py`."""

from tests._shared.ownership_policy_support import (
    BindCNativeArrayDescriptorType,
    BindCNativeArrayHandleProperty,
    BindCNativeArrayHandleVariable,
    BindCPointer,
    CCodePrinter,
    CPythonBindingGenerator,
    CPythonCodePrinter,
    CodegenAction,
    Declare,
    FCodePrinter,
    FortranToCBridgeGenerator,
    FunctionDef,
    FunctionDefArgument,
    FunctionDefResult,
    IndexedElement,
    PythonObjectType,
    Return,
    Scope,
    Variable,
    _model_call_names,
    _semantic_ir_to_codegen_ast,
    complete_semantic_policies,
    convert_to_literal,
    parse_pyi_text,
    pytest,
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
