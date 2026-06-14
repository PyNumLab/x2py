from pathlib import Path

from x2py import parse_fortran_file
from x2py.codegen.models.core import ClassDef
from x2py.codegen.models.datatypes import (
    CustomDataType,
    NumpyFloat64Type,
    NumpyInt64Type,
    NumpyNDArrayType,
)
from x2py.codegen.scope import Scope
from x2py.semantics.fortran2ir import fortran_module_to_semantic_module
from x2py.semantics.ir2ast import semantic_ir_to_codegen_ast


FORTRAN_CLASS_SOURCE = Path(__file__).parents[1] / "wrapper" / "fclasses_f90.f90"


def test_modern_fortran_derived_type_and_type_bound_methods_become_codegen_class():
    parsed = parse_fortran_file(
        FORTRAN_CLASS_SOURCE.read_text(),
        filename=str(FORTRAN_CLASS_SOURCE),
    )
    semantic_module = fortran_module_to_semantic_module(parsed)

    scope = Scope(name=semantic_module.name, scope_type="module")
    codegen_module = semantic_ir_to_codegen_ast(semantic_module, scope)

    assert [str(cls.name) for cls in codegen_module.classes] == [
        "vector",
        "vector_store",
    ]
    vector, vector_store = codegen_module.classes
    assert isinstance(vector, ClassDef)
    assert str(vector.name) == "vector"
    assert isinstance(vector.class_type, CustomDataType)
    assert vector.class_type.name == "vector"

    assert [str(attribute.name) for attribute in vector.attributes] == ["x", "y"]
    assert all(attribute.class_type is NumpyFloat64Type() for attribute in vector.attributes)

    assert [str(method.name) for method in vector.methods] == ["scale", "magnitude"]
    scale = vector.methods_as_dict["scale"]
    self_arg = scale.arguments[0]
    assert self_arg.bound_argument
    assert self_arg.var.class_type is vector.class_type
    assert self_arg.var.cls_base is vector

    magnitude = vector.methods_as_dict["magnitude"]
    assert magnitude.arguments[0].bound_argument
    assert magnitude.results.var.class_type is NumpyFloat64Type()

    assert isinstance(vector_store, ClassDef)
    assert isinstance(vector_store.class_type, CustomDataType)
    assert vector_store.class_type.name == "vector_store"
    assert [str(attribute.name) for attribute in vector_store.attributes] == ["values"]
    values = vector_store.attributes[0]
    assert isinstance(values.class_type, NumpyNDArrayType)
    assert values.class_type.element_type is NumpyFloat64Type()
    assert values.memory_handling == "heap"

    assert [
        vector_store.scope.get_python_name(method.name)
        for method in vector_store.methods
    ] == [
        "allocate_values",
        "make",
    ]
    allocate_values = vector_store.methods_as_dict["allocate_values"]
    assert allocate_values.arguments[0].bound_argument
    assert allocate_values.arguments[0].var.class_type is vector_store.class_type
    assert allocate_values.arguments[1].var.class_type is NumpyInt64Type()

    make = vector_store.methods_as_dict["make"]
    assert str(make.name) == "make_vector_store"
    assert not make.arguments[0].bound_argument
    assert make.arguments[0].var.class_type is NumpyInt64Type()
    assert make.arguments[1].var.class_type is NumpyFloat64Type()
    assert make.results.var.class_type is vector_store.class_type
