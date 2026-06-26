---
title: Source Map
audience: contributors, maintainers
prerequisites: repository checkout, developer guide
related: feature-to-code-map.md, testing-strategy.md, ../internal-architecture/pipeline-map.md
status: maintained
---

# Source Map

Use this page when you need to find the owning source files before changing a
feature. It is populated from the current maintained developer guide and the
current Python package layout.

## Top-Level Entry Points

| Start here | Owns | Continue to |
| --- | --- | --- |
| `x2py/cli.py` | User CLI, stage selection, output routing, diagnostics, wrapper-build option validation | parser frontends, semantic conversion, readiness, `x2py/wrapping.py` |
| `x2py/wrapping.py` | End-to-end Fortran source and semantic `.pyi` extension builds | preprocessing, parser, probes, semantic IR, `ir2ast`, compilation |
| `x2py/__init__.py` | Public Python exports | parser public-entrypoint tests and user examples |
| `x2py/ownership_policy.py` | Central ownership, transfer, destruction, and codegen action policy | semantic lowering and generated bridge/binding handlers |
| `x2py/preprocessing.py` | Compiler-backed source preprocessing and dependency facts | C and Fortran parser input loading |
| `x2py/c_type_probe.py` | C ABI type facts and cache | semantic C conversion and type mapping docs |
| `x2py/fortran_type_probe.py` | Fortran kind/storage facts and cache | semantic Fortran conversion and wrapper builds |
| `x2py/type_mapping_report.py` | Generated target datatype mapping examples | documentation example tests |

## Common Change Routes

Use this table when you know the behavior you need to change but not the
owning layer. Open the first file, then follow the downstream files only as the
change crosses ownership boundaries.

| Change area | Open first | Public docs to update | Focused evidence |
| --- | --- | --- | --- |
| CLI flags, stage selection, output formatting, diagnostics | `x2py/cli.py` | `docs/reference/cli-commands.md`, `docs/tutorials/basic-wrapper.md`, `docs/examples-gallery/verified-cookbook.md` | `tests/parser/test_cli.py`, `tests/tools/test_documentation_examples.py` |
| Compiler preprocessing, include paths, macros, target flags | `x2py/preprocessing.py` | `docs/examples-gallery/recipes/compiler-preprocessing.md`, `docs/developer-guide/c-parser-reference.md`, `docs/developer-guide/fortran-parser-reference.md` | `tests/parser/test_preprocessing_cli.py`, `tests/parser/test_preprocessor_and_execution_boundaries.py` |
| C parser facts and diagnostics | `x2py/c_parser/parser.py` | `docs/developer-guide/c-parser-reference.md`, `docs/examples-gallery/recipes/inspect-c-api.md` | `tests/parser/c/`, `tests/semantics/test_c2ir.py` |
| Fortran parser facts and diagnostics | `x2py/fortran_parser/parser.py` | `docs/developer-guide/fortran-parser-reference.md`, `docs/examples-gallery/recipes/inspect-fortran-api.md` | `tests/parser/`, `tests/parser/test_fortran_fixture_suite.py` |
| Semantic IR shape | `x2py/semantics/models.py`, `x2py/semantics/fortran2ir.py`, `x2py/semantics/c2ir.py` | `docs/reference/semantic-ir.md` | `tests/semantics/test_fortran2ir.py`, `tests/semantics/test_c2ir.py` |
| Semantic `.pyi` parsing, printing, package generation, and round-trip behavior | `x2py/semantics/pyi_parser.py`, `x2py/codegen/printers/pyi_printer.py` | `docs/reference/semantic-pyi-format.md`, `docs/examples-gallery/recipes/semantic-pyi-contracts.md` | `tests/pyi/`, `tests/pyi/test_contract_package_generation.py`, `tests/semantics/test_pyi_printer.py` |
| Readiness blockers and support claims | `x2py/semantics/readiness.py` | `docs/reference/diagnostic-codes.md`, `docs/language-support/feature-matrix.md` | `tests/semantics/test_semantic_wrap_readiness.py`, readiness fixture tests |
| Source-driven Fortran wrapper orchestration | `x2py/wrapping.py` | `docs/user-guide/fortran-wrapper.md`, `docs/examples-gallery/recipes/build-and-import-cli.md` | `tests/wrapper/fortran/build_from_source/test_build_modes.py`, `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py` |
| Semantic `.pyi` wrapper orchestration from native artifacts | `x2py/wrapping.py`, `x2py/semantics/pyi_parser.py` | `docs/user-guide/fortran-wrapper.md`, `docs/reference/semantic-pyi-format.md`, `docs/roadmap/semantic-pyi-wrapper-checklist.md` | `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py`, `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py` |
| Ownership, lifetime, output projection, and unsupported wrapper policy | `x2py/ownership_policy.py`, `x2py/semantics/ir2ast.py` | `docs/user-guide/fortran-wrapper.md`, `docs/design/memory-ownership-model.md`, `docs/roadmap/semantic-pyi-wrapper-checklist.md` | `tests/semantics/test_ir2ast.py`, `tests/wrapper/fortran/` |
| Generated Fortran bridge | `x2py/codegen/bridges/fortran_to_c.py`, `x2py/codegen/printers/fcode.py` | `docs/user-guide/fortran-wrapper.md`, `docs/internal-architecture/wrapper-generation-pipeline.md` | `tests/wrapper/fortran/`, generated artifact assertions |
| Generated CPython binding and Python-visible runtime behavior | `x2py/codegen/bindings/c_to_python.py`, `x2py/codegen/printers/cpythoncode.py` | `docs/user-guide/fortran-wrapper.md`, `docs/reference/python-api.md` | `tests/wrapper/fortran/` |
| Native compilation, runtime support, and shared-library linking | `x2py/compiling/python_wrapper.py`, `x2py/compiling/runtime_support.py` | `docs/user-guide/fortran-wrapper.md`, `docs/developer-guide/build-system.md` | `tests/wrapper/fortran/build_from_source/test_runtime_abi.py`, `tests/wrapper/fortran/build_from_source/test_build_modes.py` |
| Public Python exports | `x2py/__init__.py` | `README.md`, `docs/reference/python-api.md` | `tests/parser/test_parser_public_entrypoints.py` |
| Source navigation documentation | `docs/developer-guide/source-map.md`, `docs/developer-guide/feature-to-code-map.md`, package README files | `docs/documentation-architecture.md` | `tests/tools/test_documentation_structure.py` |

## Package Map

| Package | Purpose | Main files | Primary tests and docs |
| --- | --- | --- | --- |
| `x2py/c_parser/` | C lexer, parser, models, preprocessing metadata, and C parser CLI helpers | `parser.py`, `lexer.py`, `models.py`, `preprocessor.py`, `type_resolver.py`, `cli.py` | `tests/parser/c/`, `docs/developer-guide/c-parser-reference.md` |
| `x2py/fortran_parser/` | Fortran lexer, recursive parser, models, type resolver, and parser CLI helpers | `parser.py`, `lexer.py`, `models.py`, `type_resolver.py`, `cli.py` | `tests/parser/`, `tests/parser/fortran/`, `docs/developer-guide/fortran-parser-reference.md` |
| `x2py/semantics/` | Language-neutral semantic IR, source-to-IR conversion, `.pyi` loading, readiness, and codegen lowering | `models.py`, `fortran2ir.py`, `c2ir.py`, `pyi_parser.py`, `readiness.py`, `ir2ast.py` | `tests/semantics/`, `tests/pyi/`, `docs/reference/semantic-ir.md`, `docs/reference/semantic-pyi-format.md` |
| `x2py/codegen/` | Codegen AST, bridge and binding generation, printers, and semantic `.pyi` printing | `models/`, `bridges/fortran_to_c.py`, `bindings/c_to_python.py`, `printers/`, `binding_pipeline.py` | `tests/wrapper/`, `tests/semantics/test_pyi_printer.py`, `docs/user-guide/fortran-wrapper.md` |
| `x2py/compiling/` | Native compile objects, compiler command orchestration, shared-library linking, and runtime support installation | `basic.py`, `compilers.py`, `python_wrapper.py`, `runtime_support.py` | `tests/wrapper/fortran/build_from_source/test_build_modes.py`, `tests/wrapper/fortran/build_from_source/test_runtime_abi.py` |
| `x2py/naming/` | Python, C, and Fortran name collision policies | `public.py`, `*nameclashchecker.py` | naming, visibility, and wrapper runtime tests |
| `x2py/stdlib/` | Native runtime support files copied into generated wrapper builds | `x2py_runtime/` | wrapper runtime tests |
| `x2py/utilities/` | Small shared Python utilities | `metaclasses.py`, `strings.py` | tests that exercise callers |

## Hotspot Index

These files are the maintained source-navigation anchors. If ownership moves,
update this table, the package README files, and the mechanical checks in
`tests/tools/test_documentation_structure.py` in the same change.

| Hotspot | Owns |
| --- | --- |
| `x2py/__init__.py` | Public Python API exports. |
| `x2py/cli.py` | CLI argument validation, stage selection, output routing, and wrapper-build entry. |
| `x2py/wrapping.py` | End-to-end source and `.pyi` wrapper build orchestration. |
| `x2py/preprocessing.py` | Compiler-backed source preprocessing and dependency facts. |
| `x2py/c_type_probe.py` | C target ABI type probing. |
| `x2py/fortran_type_probe.py` | Fortran kind and storage probing. |
| `x2py/ownership_policy.py` | Central ownership, transfer, destruction, and generated-action policy. |
| `x2py/c_parser/parser.py` | C parser project model and diagnostics. |
| `x2py/c_parser/cli.py` | C parser report formatting and preprocessing integration. |
| `x2py/fortran_parser/parser.py` | Fortran parser project model and diagnostics. |
| `x2py/fortran_parser/cli.py` | Fortran parser report formatting. |
| `x2py/semantics/models.py` | Semantic IR dataclasses and metadata. |
| `x2py/semantics/fortran2ir.py` | Fortran parser facts to semantic modules. |
| `x2py/semantics/c2ir.py` | C parser facts to semantic modules. |
| `x2py/semantics/pyi_parser.py` | Semantic `.pyi` loading and validation. |
| `x2py/semantics/readiness.py` | Support blockers and readiness reporting. |
| `x2py/semantics/ir2ast.py` | Semantic IR to codegen AST lowering. |
| `x2py/codegen/binding_pipeline.py` | Ordered bridge and binding generation. |
| `x2py/codegen/bridges/fortran_to_c.py` | Fortran bind(C) bridge generation. |
| `x2py/codegen/bindings/c_to_python.py` | CPython extension binding generation. |
| `x2py/codegen/bindings/cpython_api.py` | CPython C API helper nodes. |
| `x2py/codegen/bindings/numpy_cpython_api.py` | NumPy C API helper nodes. |
| `x2py/codegen/printers/fcode.py` | Fortran source printing. |
| `x2py/codegen/printers/ccode.py` | C source printing. |
| `x2py/codegen/printers/cpythoncode.py` | CPython C source printing. |
| `x2py/codegen/printers/pyi_printer.py` | Semantic `.pyi` printing. |
| `x2py/compiling/basic.py` | Native compile object model. |
| `x2py/compiling/compilers.py` | Compiler command execution and tool lookup. |
| `x2py/compiling/python_wrapper.py` | Generated wrapper compilation and shared-library linking. |
| `x2py/compiling/runtime_support.py` | Runtime support installation for generated wrappers. |
| `x2py/naming/public.py` | Public wrapper name policy. |
| `x2py/stdlib/` | Runtime support payload copied into generated builds. |

## Layer-To-Layer Route

For source-driven Fortran wrappers, read in this order:

```text
x2py/cli.py
  -> x2py/wrapping.py
  -> x2py/preprocessing.py
  -> x2py/fortran_parser/parser.py
  -> x2py/fortran_type_probe.py
  -> x2py/semantics/fortran2ir.py
  -> x2py/semantics/readiness.py
  -> x2py/semantics/ir2ast.py
  -> x2py/codegen/bridges/fortran_to_c.py
  -> x2py/codegen/bindings/c_to_python.py
  -> x2py/compiling/python_wrapper.py
  -> tests/wrapper/fortran/
```

For semantic `.pyi` builds, the parser branch is replaced by:

```text
x2py/semantics/pyi_parser.py
  -> x2py/semantics/readiness.py
  -> x2py/semantics/ir2ast.py
```

For inspection-only C workflows, the path currently stops at semantic IR,
`.pyi`, and readiness:

```text
x2py/cli.py
  -> x2py/c_parser/parser.py
  -> x2py/c_type_probe.py
  -> x2py/semantics/c2ir.py
  -> x2py/codegen/printers/pyi_printer.py
  -> x2py/semantics/readiness.py
```

Runtime wrapping of user-supplied C inputs is not implemented yet.

## Package-Level Notes

The hardest source packages also have local README files:

- `x2py/README.md`
- `x2py/c_parser/README.md`
- `x2py/fortran_parser/README.md`
- `x2py/semantics/README.md`
- `x2py/codegen/README.md`
- `x2py/compiling/README.md`

Keep these files short. They should tell maintainers where to enter the code,
what the package owns, what it must not own, and where the tests and public docs
live.
