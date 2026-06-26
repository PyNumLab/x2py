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
| Build orchestration | `x2py/wrapping.py` | ordered Fortran sources or `.pyi` contracts plus explicit native artifacts | `WrapperBuildResult`, `NativeBuildPlan`, and generated artifact plan | wrapper build-mode tests |
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

## Concept Ownership Rules

The pipeline keeps separate concepts for contract facts, policy decisions,
generated implementation, and emitted source. Similar names across layers do
not mean those classes should be merged.

| Concept family | Owner | What belongs there | What must stay out |
| --- | --- | --- | --- |
| Parser facts | parser packages | Source syntax, native declaration structure, source locations, and parser diagnostics | Wrapper policy, Python API projection, generated names, and compile/link decisions |
| Semantic IR | `x2py/semantics/models.py` and source-to-IR converters | Language-neutral contract facts: public names, native identities, source origins, visibility, type/storage/intent facts, module/class/function/variable structure, and metadata that must survive `.pyi` round trips | Generated bodies, temporaries, target-language scopes, include/import mechanics, CPython calls, and printer-only syntax |
| Readiness and ownership policy | `x2py/semantics/readiness.py`, `x2py/ownership_policy.py`, and lowering checks | Support blockers and policy choices for ownership, lifetime, output projection, replacement, and ABI safety | Raw parser syntax and backend-specific statement trees |
| Core codegen AST | `x2py/codegen/models/` and `x2py/semantics/ir2ast.py` outputs | The implementation plan after a semantic contract is accepted: generated functions, variables as storage locations, statements, expressions, control flow, temporaries, scopes, and imports/includes | Source-contract authority, `.pyi` persistence, and readiness-only facts |
| Backend codegen AST | `x2py/codegen/bridges/`, `x2py/codegen/bindings/`, and backend API helpers | Fortran bridge nodes, C/CPython binding nodes, target ABI/API calls, and backend-specific adapter structure | Language-neutral semantic meaning |
| Printers and compilation | `x2py/codegen/printers/`, `x2py/compiling/`, and wrapper orchestration | Text emission, generated artifact layout, compiler commands, native objects, libraries, include directories, and link inputs | Semantic support decisions and generated-AST rewriting policy |
| Naming policy | `x2py/naming/` | Shared public-name and generated-symbol decisions for Python, C, and Fortran targets | Semantic IR ownership or codegen tree ownership |

Use these rules when adding a new notion:

- Put it in semantic IR when the fact changes the user-visible or native
  contract, must be preserved in `.pyi`, is needed for source-free wrapper
  replay, or is required before readiness can decide support.
- Put it in readiness or ownership policy when it is a safety decision rather
  than a source fact: for example borrowed versus copied data, visible versus
  hidden native outputs, replacement rules, destructor ownership, or unsupported
  ABI combinations.
- Put it in codegen when it exists because emitted wrapper code needs it:
  generated bodies, temporaries, low-level storage variables, scopes, imports,
  includes, bridge calls, CPython API calls, cleanup paths, and target-language
  expressions.
- Put it in compiling or wrapping when it describes build inputs or build
  execution: sources, objects, libraries, library directories, include
  directories, compiler flags, link items, runtime support files, and generated
  artifact paths.
- Put it in naming when the same source symbol needs stable Python, C, or
  Fortran spellings, reserved-word handling, or collision-free generated names.
  The naming layer is a shared policy service, not a semantic model and not a
  codegen AST node.

Merge or move concepts only when their invariants match:

- Merge a shared object only when it has the same meaning and lifetime in every
  layer and carries no generated implementation state. Small immutable value
  objects such as identity, origin, scalar-kind descriptors, or naming-policy
  results are candidates.
- Move a codegen concept into semantics only when it can be represented without
  a generated body, temporary, scope, include, or target-language expression and
  the fact is needed for `.pyi`, readiness, or source-free replay.
- Move a semantic concept into codegen only when it does not change the public
  contract, native contract, readiness, or `.pyi` representation and exists only
  to print or compile wrapper code.
- Keep concepts split when they share a word but not an invariant. A semantic
  function is a callable contract; a codegen function is an emitted body. A
  semantic variable is a public/native value contract; a codegen variable is a
  storage location in generated code. A semantic datatype is an API/ABI fact; a
  codegen datatype can be a concrete Fortran, C, CPython, NumPy, or bridge
  representation.

Examples:

- `@bind` and a native procedure name belong to semantic identity. The bridge
  symbol used to call it belongs to codegen naming and lowering.
- `@raises`, `@hold_gil`, output projection, and ownership metadata belong to
  semantic policy/readiness. The generated CPython error checks, GIL calls, and
  cleanup statements belong to codegen.
- Python keyword avoidance for a public name, such as a native `def` routine,
  belongs to naming policy. The chosen public spelling is stored where the
  contract needs it, while target-specific helper symbols stay generated.
- Codegen `Scope`, `FunctionDef`, body statements, temporaries, decorators,
  includes, and backend datatypes stay out of `x2py/semantics/models.py`.

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
