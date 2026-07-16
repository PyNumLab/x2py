"""Phase 9 policy, plan, and pre-emission class validation."""

from pathlib import Path

import pytest

from x2py.pipeline.pyi import pyi_file_to_semantic_module
from x2py.semantics.policy_completion import complete_semantic_policies
from x2py.semantics.wrapper_policy import ClassInvocationKind, OverloadMatchKind
from x2py.wrapper_codegen import WrapperCodeGenerator, WrapperPlanner

ROOT = Path(__file__).parents[1] / "wrapper" / "fortran"
INHERITANCE = ROOT / "derived_types" / "contracts" / "finheritance_f90" / "finheritance_f90.pyi"
OVERLOADS = ROOT / "naming" / "contracts" / "fconstructor_overloads_phase9" / "foverloads_f90.pyi"
BOUND_CONSTRUCTOR = ROOT / "derived_types" / "contracts" / "fbound_constructor_phase9" / "fclasses_f90.pyi"


def _plan(contract: Path):
    module = pyi_file_to_semantic_module(contract, module_name=contract.stem)
    complete_semantic_policies(module)
    return WrapperPlanner().build(module)


def _surface(plan, name: str):
    return next(
        surface for namespace in plan.namespaces for surface in namespace.classes if name in surface.python_names
    )


def test_inheritance_and_polymorphism_are_completed_before_planning():
    plan = _plan(INHERITANCE)
    base = _surface(plan, "base_shape")
    circle = _surface(plan, "circle")
    derived = next(
        item
        for namespace in plan.namespaces
        for item in namespace.derived_types
        if item.type_identity == circle.type_identity
    )
    describe = next(
        function
        for namespace in plan.namespaces
        for function in namespace.functions
        if function.binding.python_name == "describe_shape"
    )

    assert circle.base_identities == (base.type_identity,)
    assert [field.name for field in derived.fields] == ["size", "radius"]
    assert tuple(variant.python_name for variant in describe.arguments[0].polymorphic.variants) == (
        "box",
        "circle",
        "base_shape",
    )


def test_class_overloads_project_exact_typed_matches_and_type_bound_calls():
    plan = _plan(OVERLOADS)
    surface = _surface(plan, "accumulator")
    method = next(overload for overload in surface.overloads if overload.python_name == "add")
    constructor = surface.constructor.overload

    assert constructor is not None
    for overload in (method, constructor):
        assert tuple(matches[0].kind for matches in overload.candidate_matches) == (
            OverloadMatchKind.NUMPY_SCALAR,
            OverloadMatchKind.NUMPY_SCALAR,
        )
        assert tuple(matches[0].semantic_type_name for matches in overload.candidate_matches) == (
            "Int32",
            "Float64",
        )
        assert all(
            candidate.class_call.invocation is ClassInvocationKind.TYPE_BOUND for candidate in overload.candidates
        )
        assert all(candidate.class_call.type_bound_name == "add" for candidate in overload.candidates)


def test_bound_constructor_links_one_existing_method_function_plan():
    plan = _plan(BOUND_CONSTRUCTOR)
    surface = _surface(plan, "vector")
    target = surface.constructor.target
    namespace = plan.namespaces[0]

    assert target is not None
    assert target is surface.methods[0].function
    assert target.binding.python_name.startswith("_x2py_class_")
    assert target.binding.public is False
    assert "_x2py_class_" not in namespace.docstring


def test_class_docstrings_describe_only_the_public_surface():
    plan = _plan(BOUND_CONSTRUCTOR)
    surface = _surface(plan, "vector")

    assert "Constructor\n-----------\nvector(dx, dy) -> vector" in surface.docstring
    assert "Fields\n------\nx : float64\ny : float64" in surface.docstring
    assert "Methods\n-------\nshift(dx, dy) -> None" in surface.docstring
    assert "vector(dx, dy) -> vector" in surface.constructor.docstring
    assert "dx : float64" in surface.constructor.docstring
    assert "shift(dx, dy) -> None" in surface.methods[0].docstring
    assert "Updates the wrapped native instance in place." in surface.methods[0].docstring
    assert "owner" not in surface.methods[0].docstring
    assert "_x2py_class_" not in surface.docstring


def test_overload_docstrings_distinguish_candidates_by_public_types():
    plan = _plan(OVERLOADS)
    surface = _surface(plan, "accumulator")
    method = next(overload for overload in surface.overloads if overload.python_name == "add")

    assert "add(value: int32) -> None" in method.docstring
    assert "add(value: float64) -> None" in method.docstring
    assert "Dispatches to a native operation on the wrapped instance." in method.docstring
    assert "accumulator(value: int32) -> accumulator" in surface.constructor.docstring
    assert "accumulator(value: float64) -> accumulator" in surface.constructor.docstring
    assert "_x2py_class_" not in method.docstring
    assert "accumulator_add_" not in method.docstring


def test_invalid_class_graph_and_overload_edits_fail_before_emission():
    inheritance = _plan(INHERITANCE)
    _surface(inheritance, "circle").base_identities = (("missing", "base"),)
    with pytest.raises(ValueError, match="missing-or-late-class-base"):
        WrapperCodeGenerator().generate(inheritance)

    overloads = _plan(OVERLOADS)
    overload = next(item for item in _surface(overloads, "accumulator").overloads if item.python_name == "add")
    overload.candidate_matches = (overload.candidate_matches[0], overload.candidate_matches[0])
    with pytest.raises(ValueError, match="ambiguous-overload"):
        WrapperCodeGenerator().generate(overloads)


def test_incomplete_type_bound_receiver_fails_before_bridge_generation():
    plan = _plan(OVERLOADS)
    overload = next(item for item in _surface(plan, "accumulator").overloads if item.python_name == "add")
    overload.candidates[0].class_call.type_bound_name = None

    with pytest.raises(ValueError, match="incomplete-type-bound-call"):
        WrapperCodeGenerator().generate(plan)
