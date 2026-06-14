"""Property-based invariants for semantic-IR transformations."""

from __future__ import annotations

from dataclasses import asdict

import pytest

pytest.importorskip("hypothesis")

from hypothesis import given, strategies as st

from x2py.c_parser import parse_c_file
from x2py.semantics.c2ir import c_file_to_semantic_modules
from x2py.semantics.fortran2ir import fortran_file_to_semantic_modules, resolve_semantic_compile_time_values
from x2py.semantics.models import (
    EXTERNAL_TYPE_REF_METADATA,
    OwnershipPolicy,
    SemanticArgument,
    SemanticArrayContract,
    SemanticConstraint,
    SemanticFunction,
    SemanticModule,
    SemanticStorageContract,
    SemanticType,
)
from x2py.semantics.pyi_parser import parse_pyi_text
from x2py.codegen.printers.pyi_printer import emit_module
from x2py import parse_fortran_file


_C_SCALAR_TYPES = st.sampled_from(
    [
        ("_Bool", "Bool"),
        ("double", "Float64"),
        ("float", "Float32"),
        ("int", "Int"),
    ]
)
_FORTRAN_SCALAR_TYPES = st.sampled_from(
    [
        ("integer", "Int32"),
        ("logical", "Bool"),
        ("real", "Float32"),
        ("real(4)", "Float32"),
    ]
)
_SHARED_VALUE_TYPES = st.sampled_from(
    [
        ("_Bool", "logical", "Bool"),
        ("double", "real(8)", "Float64"),
        ("float", "real", "Float32"),
    ]
)
_SEMANTIC_SCALAR_TYPES = st.sampled_from(["Bool", "Float32", "Float64", "Int32"])
_PYI_IDENTIFIER_STEMS = st.from_regex(r"[a-z][a-z0-9_]{0,8}", fullmatch=True)
_NATIVE_NAMES = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789_ -!\"'\\\n\t",
    min_size=1,
    max_size=12,
)


@st.composite
def c_scalar_prototypes(draw):
    source_result, semantic_result = draw(_C_SCALAR_TYPES)
    parameter_ids = draw(st.lists(st.integers(min_value=0, max_value=99), max_size=6, unique=True))
    parameter_types = draw(st.lists(_C_SCALAR_TYPES, min_size=len(parameter_ids), max_size=len(parameter_ids)))
    parameters = [
        f"{source_type} p_{parameter_id}"
        for parameter_id, (source_type, _semantic_type) in zip(parameter_ids, parameter_types, strict=True)
    ]
    parameter_text = ", ".join(parameters) if parameters else "void"
    source = f"{source_result} transform({parameter_text});\n"
    expected_parameters = [
        (f"p_{parameter_id}", semantic_type)
        for parameter_id, (_source_type, semantic_type) in zip(parameter_ids, parameter_types, strict=True)
    ]
    return source, semantic_result, expected_parameters


@st.composite
def fortran_scalar_subroutines(draw):
    parameter_ids = draw(st.lists(st.integers(min_value=0, max_value=99), max_size=6, unique=True))
    parameter_types = draw(st.lists(_FORTRAN_SCALAR_TYPES, min_size=len(parameter_ids), max_size=len(parameter_ids)))
    parameters = [f"p_{parameter_id}" for parameter_id in parameter_ids]
    declarations = "".join(
        f"  {source_type}, intent(in), value :: {parameter}\n"
        for parameter, (source_type, _semantic_type) in zip(parameters, parameter_types, strict=True)
    )
    source = f"subroutine transform({', '.join(parameters)})\n{declarations}end subroutine transform\n"
    expected_parameters = [
        (parameter, semantic_type)
        for parameter, (_source_type, semantic_type) in zip(parameters, parameter_types, strict=True)
    ]
    return source, expected_parameters


@st.composite
def canonical_semantic_types(draw):
    name = draw(_SEMANTIC_SCALAR_TYPES)
    storage_kind = draw(st.sampled_from(["value", "reference", "array"]))
    read_only = draw(st.booleans())
    constraints = [SemanticConstraint("Finite")] if draw(st.booleans()) else []
    ownership = OwnershipPolicy(mutable=not read_only)

    if storage_kind == "value":
        storage = SemanticStorageContract(kind="value", read_only=True) if read_only else None
        return SemanticType(
            name=name,
            dtype=name,
            constraints=constraints,
            ownership=OwnershipPolicy(),
            storage=storage,
        ), "in"

    if storage_kind == "reference":
        storage = SemanticStorageContract(
            kind="reference",
            read_only=read_only,
            mutable=not read_only,
            pointer_depth=1,
        )
        return SemanticType(
            name=name,
            dtype=name,
            constraints=constraints,
            ownership=ownership,
            storage=storage,
        ), "in" if read_only else "inout"

    shape = [str(bound) for bound in draw(st.lists(st.integers(min_value=1, max_value=32), min_size=1, max_size=3))]
    order = draw(st.sampled_from(["default", "ORDER_F", "ORDER_ANY"]))
    if order == "default":
        order = "ORDER_C" if len(shape) > 1 else None
    array = SemanticArrayContract(
        rank=len(shape),
        shape=list(shape),
        order=order,
        axes=["dense" for _dimension in shape],
        contiguous=True,
        allocatable=draw(st.booleans()),
        pointer=draw(st.booleans()),
    )
    storage = SemanticStorageContract(
        kind="array",
        read_only=read_only,
        mutable=not read_only,
        array=array,
    )
    return SemanticType(
        name=name,
        dtype=name,
        rank=len(shape),
        shape=list(shape),
        constraints=constraints,
        ownership=ownership,
        storage=storage,
    ), "in" if read_only else "inout"


@pytest.mark.property
@given(c_scalar_prototypes())
def test_generated_c_ast_to_semantic_ir_is_deterministic(case):
    source, expected_result, expected_parameters = case

    first = c_file_to_semantic_modules(parse_c_file(source, filename="generated.h"))[0]
    second = c_file_to_semantic_modules(parse_c_file(source, filename="generated.h"))[0]

    assert asdict(first) == asdict(second)
    assert len(first.functions) == 1
    function = first.functions[0]
    assert function.return_type is not None
    assert function.return_type.name == expected_result
    assert [(arg.name, arg.semantic_type.name) for arg in function.arguments] == expected_parameters


@pytest.mark.property
@given(fortran_scalar_subroutines())
def test_generated_fortran_ast_to_semantic_ir_is_deterministic(case):
    source, expected_parameters = case

    first = fortran_file_to_semantic_modules(
        parse_fortran_file(source, filename="generated.f90"),
        standalone_module_name="generated",
    )[0]
    second = fortran_file_to_semantic_modules(
        parse_fortran_file(source, filename="generated.f90"),
        standalone_module_name="generated",
    )[0]

    assert asdict(first) == asdict(second)
    assert len(first.functions) == 1
    function = first.functions[0]
    assert [(arg.name, arg.semantic_type.name) for arg in function.arguments] == expected_parameters


@pytest.mark.property
@given(_SHARED_VALUE_TYPES)
def test_generated_c_and_fortran_value_arguments_share_semantic_contract(case):
    c_type, fortran_type, semantic_type = case
    c_module = c_file_to_semantic_modules(parse_c_file(f"void consume({c_type} value);\n", filename="generated.h"))[0]
    fortran_module = fortran_file_to_semantic_modules(
        parse_fortran_file(
            f"subroutine consume(value)\n  {fortran_type}, intent(in), value :: value\nend subroutine consume\n",
            filename="generated.f90",
        ),
        standalone_module_name="generated",
    )[0]

    c_argument = c_module.functions[0].arguments[0]
    fortran_argument = fortran_module.functions[0].arguments[0]
    assert c_argument.semantic_type.name == semantic_type
    assert fortran_argument.semantic_type.name == semantic_type
    assert c_argument.semantic_type == fortran_argument.semantic_type
    assert c_argument.semantic_type.origin.source_language == "c"
    assert fortran_argument.semantic_type.origin.source_language == "fortran"


@pytest.mark.property
@given(n=st.integers(min_value=1, max_value=999), m=st.integers(min_value=1, max_value=999))
def test_generated_semantic_specialization_is_non_mutating_and_idempotent(n, m):
    module = SemanticModule(
        name="generated",
        variables=[
            SemanticArgument(
                name="values",
                semantic_type=SemanticType(
                    name="Float64",
                    dtype="Float64",
                    rank=2,
                    shape=["1:n", "m + 1"],
                    constraints=[SemanticConstraint("Extent", ["n", {"upper": "m"}])],
                    metadata={"bounds": ("n", ["m"])},
                    storage=SemanticStorageContract(
                        kind="array",
                        metadata={"extent": "n"},
                        array=SemanticArrayContract(
                            rank=2,
                            shape=["1:n", "m + 1"],
                            lower_bounds=["1", "0"],
                            upper_bounds=["n", "m"],
                            source_shape=["1:n", "0:m"],
                            metadata={"extent": {"first": "n", "second": "m"}},
                        ),
                    ),
                ),
            )
        ],
        metadata={"shape": ["n", "m"]},
    )
    original = asdict(module)

    resolved = resolve_semantic_compile_time_values(module, {"n": n, "m": m})

    assert asdict(module) == original
    semantic_type = resolved.variables[0].semantic_type
    assert semantic_type.shape == [f"1:{n}", f"{m} + 1"]
    assert semantic_type.constraints[0].arguments == [str(n), {"upper": str(m)}]
    assert semantic_type.metadata == {"bounds": (str(n), [str(m)])}
    assert semantic_type.storage is not None
    assert semantic_type.storage.metadata == {"extent": str(n)}
    assert semantic_type.storage.array is not None
    assert semantic_type.storage.array.shape == [f"1:{n}", f"{m} + 1"]
    assert semantic_type.storage.array.lower_bounds == ["1", "0"]
    assert semantic_type.storage.array.upper_bounds == [str(n), str(m)]
    assert semantic_type.storage.array.source_shape == [f"1:{n}", f"0:{m}"]
    assert semantic_type.storage.array.metadata == {"extent": {"first": str(n), "second": str(m)}}
    assert asdict(resolve_semantic_compile_time_values(resolved, {"n": n, "m": m})) == asdict(resolved)


@pytest.mark.property
@given(_NATIVE_NAMES)
def test_generated_pyi_escaping_round_trips_native_names(native_name):
    module = SemanticModule(
        name="generated",
        variables=[SemanticArgument(native_name, SemanticType("Int32", dtype="Int32"))],
        functions=[
            SemanticFunction(
                name="consume",
                native_name="consume",
                arguments=[SemanticArgument(native_name, SemanticType("Int32", dtype="Int32"))],
            )
        ],
    )

    emitted = emit_module(module)
    reparsed = parse_pyi_text(emitted, module_name="generated")

    assert reparsed.variables[0].name == native_name
    assert reparsed.functions[0].arguments[0].name == native_name


@pytest.mark.property
@given(st.lists(_PYI_IDENTIFIER_STEMS, min_size=1, max_size=6, unique=True))
def test_generated_pyi_synthetic_imports_are_stably_sorted(type_stems):
    type_names = [f"type_{stem}" for stem in type_stems]

    def import_lines(names):
        module = SemanticModule(
            name="generated",
            variables=[
                SemanticArgument(
                    f"value_{index}",
                    SemanticType(
                        type_name,
                        dtype=type_name,
                        metadata={
                            EXTERNAL_TYPE_REF_METADATA: {
                                "name": type_name,
                                "local_name": type_name,
                                "origin_module": "types",
                                "representation": "opaque",
                            }
                        },
                    ),
                )
                for index, type_name in enumerate(names)
            ],
        )
        return [line for line in emit_module(module).splitlines() if line.startswith("from ")]

    expected = [f"from types import {', '.join(sorted(type_names))}"]
    assert import_lines(type_names) == expected
    assert import_lines(reversed(type_names)) == expected


@pytest.mark.property
@given(st.lists(canonical_semantic_types(), max_size=5))
def test_generated_semantic_ir_round_trips_through_pyi(arguments):
    module = SemanticModule(
        name="generated",
        functions=[
            SemanticFunction(
                name="consume",
                native_name="consume",
                arguments=[
                    SemanticArgument(f"value_{index}", semantic_type, intent=intent)
                    for index, (semantic_type, intent) in enumerate(arguments)
                ],
            )
        ],
    )

    emitted = emit_module(module)
    reparsed = parse_pyi_text(emitted, module_name="generated")

    assert reparsed == module
