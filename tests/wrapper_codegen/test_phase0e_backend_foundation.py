"""Phase 0E tests for isolated scalar backend foundations."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.wrapper.fortran._support import REPO_ROOT
from x2py.wrapper_codegen import (
    ApiReference,
    BackendScalarType,
    BackendSourceAssembly,
    CDeclaration,
    CExpressionStatement,
    CFunction,
    CFunctionPrototype,
    CHeader,
    CInclude,
    CModule,
    CParameter,
    CReturn,
    CSourcePrinter,
    CodeExpression,
    FortranAssignment,
    FortranFunction,
    FortranModule,
    FortranParameter,
    FortranSourcePrinter,
    FortranUse,
    HandlerRegistryPlan,
    ModuleEmissionContext,
    ModulePlan,
    NameAllocator,
    UnsupportedWrapperCodegenNodeError,
)


def test_name_allocator_sanitizes_keywords_and_reuses_module_context_names():
    allocator = NameAllocator(("x",))
    context = ModuleEmissionContext("demo", allocator)

    assert allocator.allocate("return") == "return_"
    assert allocator.allocate("x") == "x_1"
    assert allocator.allocate("2-value") == "x_2_value"

    function_context = context.function_context("demo.add")
    assert function_context.local_name("x") == "x_2"
    assert "x_2" in allocator.used_names


def test_backend_source_assembly_renders_complete_c_header_and_fortran_modules():
    float64 = BackendScalarType(
        semantic_name="Float64",
        c_spelling="double",
        fortran_spelling="real(c_double)",
        python_parse_unit="d",
        numpy_type_macro="NPY_FLOAT64",
    )
    api = ApiReference("import_array", include="numpy/arrayobject.h")
    parameters = (CParameter("self", "PyObject *"), CParameter("args", "PyObject *"))
    c_function = CFunction(
        name="wrap_add_r8",
        return_type="PyObject *",
        parameters=parameters,
        storage="static",
        body=(
            CDeclaration("x", float64.c_spelling, CodeExpression("0.0")),
            CExpressionStatement(CodeExpression(f"{CSourcePrinter().doprint(api)}()")),
            CReturn(CodeExpression("NULL")),
        ),
    )
    assembly = BackendSourceAssembly(
        module_name="fmath",
        c_header=CHeader(
            guard="FMATH_WRAPPER_H",
            includes=(CInclude("Python.h"),),
            prototypes=(CFunctionPrototype("wrap_add_r8", "PyObject *", parameters),),
        ),
        c_module=CModule(
            name="fmath_wrapper",
            includes=(CInclude("Python.h"), CInclude(api.include), CInclude("fmath_wrapper.h", system=False)),
            functions=(c_function,),
        ),
        fortran_module=FortranModule(
            name="bind_c_fmath_wrapper",
            uses=(FortranUse("iso_c_binding", ("c_double",)),),
            procedures=(
                FortranFunction(
                    name="bind_c_add_r8",
                    parameters=(FortranParameter("x", float64.fortran_spelling, ("value",)),),
                    result_name="result",
                    result_type=float64.fortran_spelling,
                    bind_name="ADD_R8",
                    body=(FortranAssignment("result", CodeExpression("x")),),
                ),
            ),
        ),
    )

    rendered = assembly.rendered_sources()

    assert "#ifndef FMATH_WRAPPER_H" in rendered.c_header
    assert "PyObject * wrap_add_r8(PyObject * self, PyObject * args);" in rendered.c_header
    assert '#include "fmath_wrapper.h"' in rendered.c_source
    assert "static PyObject * wrap_add_r8(PyObject * self, PyObject * args)" in rendered.c_source
    assert "double x = 0.0;" in rendered.c_source
    assert "import_array();" in rendered.c_source
    assert "use iso_c_binding, only: c_double" in rendered.fortran_source
    assert 'function bind_c_add_r8(x) result(result) bind(c, name="ADD_R8")' in rendered.fortran_source
    assert "real(c_double), value :: x" in rendered.fortran_source


def test_source_printers_reject_wrapper_plan_models():
    plan = ModulePlan(owner_path="demo", functions=(), handler_registry=HandlerRegistryPlan((), (), ()))

    with pytest.raises(UnsupportedWrapperCodegenNodeError):
        CSourcePrinter().doprint(plan)
    with pytest.raises(UnsupportedWrapperCodegenNodeError):
        FortranSourcePrinter().doprint(plan)


def test_source_printers_do_not_import_wrapper_plan_models():
    path = REPO_ROOT / "x2py" / "wrapper_codegen" / "source_printers.py"
    imports = {
        node.module
        for node in ast.walk(ast.parse(Path(path).read_text(encoding="utf-8")))
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    assert "x2py.wrapper_codegen.plan" not in imports
