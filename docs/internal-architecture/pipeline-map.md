---
title: Pipeline Map
audience: maintainers
prerequisites: source map, overall architecture
related: ../developer-guide/source-map.md, wrapper-generation-pipeline.md, runtime-layer.md
status: maintained
---

# Pipeline Map

This page is the source-code route through the current wrapper and inspection
pipelines. It complements the user-facing wrapper mechanism in
`docs/user-guide/fortran-wrapper.md` with the implementation files a maintainer should
open at each stage.

## Source-Driven Fortran Wrapper Pipeline

```text
CLI request
  -> wrapper build orchestration
  -> compiler preprocessing
  -> Fortran parser project model
  -> Fortran target kind/storage probes
  -> semantic IR and readiness blockers
  -> codegen AST and ownership policy
  -> generated Fortran bind(C) bridge
  -> generated C/CPython binding
  -> native compile, runtime support install, and link
  -> importable Python extension
  -> wrapper runtime tests
```

| Stage | Main source | Input | Output | Primary evidence |
| --- | --- | --- | --- | --- |
| CLI request | `x2py/cli.py` | source paths and stage flags | selected stage or wrapper build options | `tests/parser/test_cli.py` |
| Build orchestration | `x2py/wrapping.py` | ordered Fortran sources or `.pyi` contracts | `WrapperBuildResult` and generated artifact plan | wrapper build-mode tests |
| Preprocessing | `x2py/preprocessing.py` | source path, compiler config | preprocessed source and dependency facts | preprocessing tests |
| Parser project model | `x2py/fortran_parser/parser.py` | preprocessed Fortran source | parser project with modules, procedures, types, visibility | Fortran parser fixture tests |
| Target probes | `x2py/fortran_type_probe.py` | semantic type requirements and compiler flags | resolved kind/storage facts | Fortran type probe tests |
| Semantic IR | `x2py/semantics/fortran2ir.py` | parser project and target facts | `SemanticModule` objects | semantic Fortran tests |
| Readiness | `x2py/semantics/readiness.py` | semantic modules | blockers and support status | readiness tests and fixtures |
| Codegen lowering | `x2py/semantics/ir2ast.py`, `x2py/ownership_policy.py` | semantic modules | codegen AST with policy decisions | `tests/semantics/test_ir2ast.py`, wrapper tests |
| Bridge generation | `x2py/codegen/bridges/fortran_to_c.py` | codegen AST | Fortran bind(C) bridge AST | wrapper runtime tests |
| Binding generation | `x2py/codegen/bindings/c_to_python.py` | bridge-facing AST | C/CPython extension AST | wrapper runtime tests |
| Printing | `x2py/codegen/printers/` | generated ASTs | wrapper source files | generated build artifacts and wrapper tests |
| Compile and link | `x2py/compiling/` | user objects, wrapper sources, runtime support | shared library | wrapper runtime tests |

## Stage Maintenance Map

| Stage family | First files to read | Source navigation owner |
| --- | --- | --- |
| CLI and output routing | `x2py/cli.py`, parser CLI helpers | `docs/developer-guide/source-map.md`, `docs/developer-guide/feature-to-code-map.md` |
| Source loading and preprocessing | `x2py/preprocessing.py` | `docs/developer-guide/source-map.md`, parser references |
| Parser facts | `x2py/c_parser/parser.py`, `x2py/fortran_parser/parser.py` | parser package README files and parser references |
| Semantic conversion | `x2py/semantics/fortran2ir.py`, `x2py/semantics/c2ir.py`, `x2py/semantics/models.py` | `docs/reference/semantic-ir.md` |
| Editable semantic contracts | `x2py/semantics/pyi_parser.py`, `x2py/codegen/printers/pyi_printer.py` | `docs/reference/semantic-pyi-format.md` |
| Readiness | `x2py/semantics/readiness.py` | `docs/reference/diagnostic-codes.md` |
| Wrapper policy and lowering | `x2py/semantics/ir2ast.py`, `x2py/ownership_policy.py` | `docs/user-guide/fortran-wrapper.md`, ownership docs |
| Bridge and binding generation | `x2py/codegen/bridges/fortran_to_c.py`, `x2py/codegen/bindings/c_to_python.py` | codegen package README and wrapper generation docs |
| Native build | `x2py/compiling/python_wrapper.py`, `x2py/compiling/runtime_support.py` | compiling package README and build-system docs |

## Semantic `.pyi` Wrapper Pipeline

Semantic `.pyi` builds reuse the wrapper backend but start from edited
contracts and explicit native artifacts instead of reparsing native source for
the Python API.

```text
.pyi contract
  -> x2py/semantics/pyi_parser.py
  -> x2py/semantics/readiness.py
  -> x2py/semantics/ir2ast.py
  -> bridge, binding, compile, and link pipeline
```

The `.pyi` path must preserve native ABI facts in the semantic contract. Missing
native build inputs or contradictory contract facts fail before bridge emission
or native compilation.

## Inspection-Only Pipeline

Inspection stages stop before wrapper code generation:

```text
native source
  -> parser facts
  -> semantic IR
  -> semantic .pyi
  -> readiness report
```

C source currently follows this inspection pipeline. Runtime wrapping of
user-supplied C inputs is future backend work and must not be presented as
implemented support.

## Where Failures Should Happen

| Failure type | Preferred owner |
| --- | --- |
| Source cannot be preprocessed | `x2py/preprocessing.py` |
| Native syntax is unsupported | parser package |
| Source facts cannot form a safe semantic contract | semantic conversion or readiness |
| Ownership, lifetime, ABI, or projection policy is unsafe | `x2py/ownership_policy.py`, readiness, or `ir2ast` |
| Generated code cannot represent a supported contract | bridge or binding generator with focused tests |
| Compiler/linker invocation is wrong | `x2py/compiling/` or `x2py/wrapping.py` |
| Python runtime behavior is wrong | generated binding, runtime support, or ownership policy |
