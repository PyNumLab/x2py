---
title: Feature To Code Map
audience: contributors, maintainers
prerequisites: source map, testing strategy
related: source-map.md, ../language-support/feature-matrix.md, ../internal-architecture/pipeline-map.md
status: maintained
---

# Feature To Code Map

Use this page when starting from a user-visible feature. The table points to
the public docs, implementation files, focused tests, and evidence required
before documentation may call the behavior supported.

## Feature Map

| Feature or behavior | Public docs | Main implementation files | Focused tests | Support evidence |
| --- | --- | --- | --- | --- |
| CLI stage selection and output | `docs/tutorials/basic-wrapper.md`, `docs/examples-gallery/verified-cookbook.md`, `docs/reference/cli-commands.md` | `x2py/cli.py`, `x2py/fortran_parser/cli.py`, `x2py/c_parser/cli.py` | `tests/parser/test_cli.py`, parser CLI tests, documentation example tests | Command output and diagnostics match checked expectations |
| Compiler preprocessing | `docs/examples-gallery/recipes/compiler-preprocessing.md`, parser references | `x2py/preprocessing.py`, parser CLI helpers | `tests/parser/test_preprocessing_cli.py`, `tests/parser/test_preprocessor_and_execution_boundaries.py`, C preprocessing tests | Preprocessed input and dependency facts are stable |
| Fortran parse output | `docs/developer-guide/fortran-parser-reference.md` | `x2py/fortran_parser/parser.py`, `models.py`, `lexer.py`, `type_resolver.py` | `tests/parser/test_procedure_and_type_parsing.py`, `tests/parser/test_fortran_fixture_suite.py` | Parser facts and diagnostics match fixtures |
| C parse output | `docs/developer-guide/c-parser-reference.md`, `docs/examples-gallery/recipes/inspect-c-api.md` | `x2py/c_parser/parser.py`, `models.py`, `lexer.py`, `type_resolver.py` | `tests/parser/c/test_c_declarations_and_declarators.py`, `tests/parser/c/test_c_fixture_suite.py` | Parser facts and diagnostics match fixtures |
| Semantic IR | `docs/reference/semantic-ir.md` | `x2py/semantics/models.py`, `fortran2ir.py`, `c2ir.py` | `tests/semantics/test_fortran2ir.py`, `tests/semantics/test_c2ir.py` | Source facts lower without losing wrapper-relevant meaning |
| Semantic `.pyi` generation | `docs/reference/semantic-pyi-format.md` | `x2py/codegen/printers/pyi_printer.py` | `tests/semantics/test_pyi_printer.py`, `tests/semantics/test_pyi_printer_modern_example.py` | Printed `.pyi` round-trips or matches fixtures |
| Semantic `.pyi` loading and editing | `docs/user-guide/editing-semantic-pyi-contracts.md`, `docs/reference/semantic-pyi-format.md`, `docs/examples-gallery/recipes/semantic-pyi-contracts.md`, `docs/roadmap/semantic-pyi-wrapper-checklist.md` | `x2py/semantics/pyi_parser.py`, `x2py/semantics/pyi2ir.py`, `models.py` | `tests/pyi/test_pyi_to_ir.py`, `tests/pyi/test_pyi_fixture_suite.py` | Edited contracts parse to Python AST, then become semantic IR with preserved native facts |
| Readiness blockers | `docs/reference/diagnostic-codes.md`, `docs/reference/semantic-pyi-format.md` | `x2py/semantics/readiness.py` | `tests/semantics/test_semantic_wrap_readiness.py`, readiness fixture tests | Unsupported or incomplete contracts fail before codegen |
| Fortran wrapper orchestration | `docs/user-guide/fortran-wrapper.md`, `docs/examples-gallery/recipes/build-and-import-cli.md`, `docs/examples-gallery/recipes/build-multiple-fortran-sources.md` | `x2py/wrapping.py` | `tests/wrapper/fortran/build_from_source/test_build_modes.py`, multi-source wrapper tests | Builds report artifacts and compile/link as documented |
| Semantic IR to codegen AST | `docs/user-guide/fortran-wrapper.md`, `docs/design/wrapper-design-notes.md` | `x2py/semantics/ir2ast.py`, `x2py/ownership_policy.py` | `tests/semantics/test_ir2ast.py`, `tests/wrapper/fortran/` | Runtime policy is explicit and unsupported cases block |
| Generated Fortran bridge | `docs/user-guide/fortran-wrapper.md` | `x2py/codegen/bridges/fortran_to_c.py`, `x2py/codegen/printers/fcode.py` | `tests/wrapper/fortran/` | Generated bridge compiles and preserves native calling contract |
| Generated CPython binding | `docs/user-guide/fortran-wrapper.md` | `x2py/codegen/bindings/c_to_python.py`, CPython and NumPy binding helpers | `tests/wrapper/fortran/` | Extension imports, validates Python inputs, and returns documented values |
| Native compilation and runtime support | `docs/user-guide/fortran-wrapper.md`, `docs/examples-gallery/recipes/generate-editable-makefile.md`, `docs/developer-guide/build-system.md`, `docs/developer-guide/quality-assurance.md` | `x2py/compiling/`, `x2py/stdlib/x2py_runtime/` | `tests/wrapper/fortran/build_from_source/test_runtime_abi.py`, build-mode tests | Generated sources compile, link, import, and clean up correctly |
| Public API exports | `README.md`, `docs/reference/python-api.md` | `x2py/__init__.py` | `tests/parser/test_parser_public_entrypoints.py`, C public API tests | Import paths are intentional and documented |
| Source documentation architecture | `docs/documentation-architecture.md`, `docs/developer-guide/source-map.md` | `docs/`, package README files, `tests/tools/test_documentation_structure.py` | documentation structure and example tests | Pages have metadata, TODO policy, and source coverage checks |

## First-File Rule

For a feature change, start with the implementation file named in the feature
map and read only the downstream files that the change actually crosses. For
example, a CLI output change normally starts and ends in `x2py/cli.py`, while a
wrapper output-projection change must move through
`x2py/semantics/ir2ast.py`, `x2py/ownership_policy.py`, the bridge generator,
and the CPython binding generator.

When the user-visible behavior changes, update the public docs in the same row
before or alongside the implementation. The documentation structure test keeps
this routing page tied to the source hotspots and package README files.

## Workflow Feature Pointers

| User workflow | Start in code | Do not mark supported until |
| --- | --- | --- |
| Wrapping functions and subroutines | `x2py/semantics/fortran2ir.py`, `x2py/semantics/ir2ast.py`, bridge and binding generators | Runtime tests compile, import, call, and verify return and failure behavior |
| Wrapping modules and module variables | parser module facts, semantic module conversion, naming policy, wrapper generators | Python-visible names, accessors, and unsupported module constructs are tested |
| Derived types | semantic classes, ownership policy, bridge class handling, CPython class binding | Lifetime, construction, field access, finalization, and invalid calls are tested |
| Arrays and allocatables | semantic array contracts, `ir2ast`, ownership policy, bridge/binding array handlers | dtype, shape, rank, contiguity, mutation, returned arrays, and failure paths are tested |
| Pointer arguments | semantic metadata, ownership policy, bridge/binding pointer handlers | Owner, lifetime, association, and blocked cases are explicit and tested |
| Optional arguments | parser optional attributes, semantic arguments, binding argument parsing | Present/absent calls and unsupported combinations are tested |
| Generic interfaces | parser interface facts, semantic overload sets, `FunctionOverloadSet`, binding dispatch | Overload selection and ambiguity failures are tested at runtime |
| Enumerations | parser enum facts, semantic constants/classes, codegen projection | Python-visible values and unsupported enum forms are tested |
| Callbacks | semantic callback types, bridge callback conversion, CPython callback handling | Callback lifetime, exception propagation, and call-scoped behavior are tested |
| Error handling | readiness diagnostics, generated cleanup paths, CPython exception state | Failure path tests prove diagnostics or Python exceptions |
| Packaging and distribution | `x2py/wrapping.py`, `x2py/compiling/`, future packaging integration | Build artifacts, native dependencies, and platform constraints are documented and tested |

## Evidence Rule

A feature can appear in user workflow docs only after the implementation,
focused tests, and runtime evidence match the public claim. Parser or semantic
support alone is not enough for runtime wrapper support.
