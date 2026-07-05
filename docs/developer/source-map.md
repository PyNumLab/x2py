---
title: Source Map
audience: developers, contributors
prerequisites: repository checkout, developer guide
related: feature-to-code-map.md, testing-strategy.md
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
| `x2py/fortran_type_probe.py` | Fortran kind/storage facts and cache | semantic Fortran conversion and wrapper builds |
| `x2py/type_mapping_report.py` | Generated target datatype mapping examples | documentation example tests |

<!-- X2PY_C_DOCS_START
| `x2py/preprocessing.py` | Compiler-backed source preprocessing and dependency facts | C and Fortran parser input loading |
| `x2py/c_type_probe.py` | C ABI type facts and cache | semantic C conversion and type mapping docs |
X2PY_C_DOCS_END -->

## Common Change Routes

Use this table when you know the behavior you need to change but not the
owning layer. Open the first file, then follow the downstream files only as the
change crosses ownership boundaries.

| Change area | Open first | Public docs to update | Focused evidence |
| --- | --- | --- | --- |
| CLI flags, stage selection, output formatting, diagnostics | `x2py/cli.py` | `docs/user/reference/cli-commands.md`, `docs/user/tutorials/basic-wrapper.md`, `docs/user/examples/verified-cookbook.md` | `tests/parser/test_cli.py`, `tests/tools/test_documentation_examples.py` |
| Compiler preprocessing, include paths, macros, and target flags | `x2py/preprocessing.py` | `docs/user/examples/recipes/compiler-preprocessing.md`, `docs/developer/fortran-parser-reference.md` | `tests/parser/test_preprocessing_cli.py`, `tests/parser/test_preprocessor_and_execution_boundaries.py` |
| Fortran parser facts and diagnostics | `x2py/fortran_parser/parser.py` | `docs/developer/fortran-parser-reference.md`, `docs/user/examples/recipes/inspect-fortran-api.md` | `tests/parser/`, `tests/parser/test_fortran_fixture_suite.py` |
| Semantic `.pyi` parsing, conversion, printing, package generation, and round-trip behavior | `x2py/pyi_parser/parser.py`, `x2py/pyi_pipeline.py`, `x2py/semantics/pyi2ir.py`, `x2py/codegen/printers/pyi_printer.py` | `docs/user/reference/semantic-pyi-format.md`, `docs/user/guide/editing-semantic-pyi-contracts.md`, `docs/user/examples/recipes/semantic-pyi-contracts.md` | `tests/pyi/`, `tests/pyi/test_contract_package_generation.py`, `tests/semantics/test_pyi_printer.py` |
| Readiness blockers and support claims | `x2py/semantics/readiness.py` | `docs/user/reference/diagnostic-codes.md`, `docs/user/language-support/feature-matrix.md` | `tests/semantics/test_semantic_wrap_readiness.py`, readiness fixture tests |
| Source-driven Fortran wrapper orchestration | `x2py/wrapping.py` | `docs/user/guide/fortran-wrapper.md`, `docs/user/examples/recipes/build-and-import-cli.md` | `tests/wrapper/fortran/build_from_source/test_build_modes.py`, `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py` |
| Semantic `.pyi` wrapper orchestration from native artifacts | `x2py/wrapping.py`, `x2py/pyi_pipeline.py`, `x2py/semantics/pyi2ir.py` | `docs/user/guide/fortran-wrapper.md`, `docs/user/reference/semantic-pyi-format.md` | `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py`, `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py` |
| Ownership, lifetime, output projection, and unsupported wrapper policy | `x2py/semantics/policy_completion.py`, `x2py/ownership_policy.py`, `x2py/semantics/ir2ast.py` | `docs/user/guide/fortran-wrapper.md`, `docs/user/guide/editing-semantic-pyi-contracts.md` | `tests/semantics/test_ir2ast.py`, `tests/wrapper/fortran/` |
| Native compilation, runtime support, and shared-library linking | `x2py/compiling/python_wrapper.py`, `x2py/compiling/runtime_support.py` | `docs/user/guide/fortran-wrapper.md`, `docs/developer/build-system.md` | `tests/wrapper/fortran/build_from_source/test_runtime_abi.py`, `tests/wrapper/fortran/build_from_source/test_build_modes.py` |
| Public Python exports | `x2py/__init__.py` | `README.md`, `docs/user/reference/python-api.md` | `tests/parser/test_parser_public_entrypoints.py` |
| Source navigation documentation | `docs/developer/source-map.md`, `docs/developer/feature-to-code-map.md`, package README files | `docs/developer/source-map.md` | `tests/tools/test_documentation_structure.py` |

<!-- X2PY_C_DOCS_START
| Compiler preprocessing, include paths, macros, target flags | `x2py/preprocessing.py` | `docs/user/examples/recipes/compiler-preprocessing.md`, `docs/developer/c-parser-reference.md`, `docs/developer/fortran-parser-reference.md` | `tests/parser/test_preprocessing_cli.py`, `tests/parser/test_preprocessor_and_execution_boundaries.py` |
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
| C parser facts and diagnostics | `x2py/c_parser/parser.py` | `docs/developer/c-parser-reference.md`, `docs/user/examples/recipes/inspect-c-api.md` | `tests/parser/c/`, `tests/semantics/test_c2ir.py` |
| Semantic IR shape and cross-stage metadata | `x2py/semantics/models.py`, `x2py/semantic_metadata.py`, `x2py/semantics/fortran2ir.py`, `x2py/semantics/c2ir.py` | `docs/user/reference/semantic-ir.md` | `tests/semantics/test_fortran2ir.py`, `tests/semantics/test_c2ir.py` |
| Generated Fortran bridge | `x2py/codegen/bridges/fortran_to_c.py`, `x2py/codegen/printers/fcode.py` | `docs/user/guide/fortran-wrapper.md` | `tests/wrapper/fortran/`, generated artifact assertions |
| Generated CPython binding and Python-visible runtime behavior | `x2py/codegen/bindings/c_to_python.py`, `x2py/codegen/printers/cpythoncode.py` | `docs/user/guide/fortran-wrapper.md`, `docs/user/reference/python-api.md` | `tests/wrapper/fortran/` |
X2PY_C_DOCS_END -->

## Package Map

| Package | Purpose | Main files | Primary tests and docs |
| --- | --- | --- | --- |
| `x2py/fortran_parser/` | Fortran lexer, recursive parser, models, type resolver, and parser CLI helpers | `parser.py`, `lexer.py`, `models.py`, `type_resolver.py`, `cli.py` | `tests/parser/`, `tests/parser/fortran/`, `docs/developer/fortran-parser-reference.md` |
| `x2py/compiling/` | Native compile objects, compiler command orchestration, shared-library linking, and runtime support installation | `basic.py`, `compilers.py`, `python_wrapper.py`, `runtime_support.py` | `tests/wrapper/fortran/build_from_source/test_build_modes.py`, `tests/wrapper/fortran/build_from_source/test_runtime_abi.py` |
| `x2py/stdlib/` | Native runtime support files copied into generated wrapper builds | `x2py_runtime/` | wrapper runtime tests |
| `x2py/utilities/` | Small shared Python utilities | `metaclasses.py`, `strings.py` | tests that exercise callers |

<!-- X2PY_C_DOCS_START
| `x2py/c_parser/` | C lexer, parser, models, preprocessing metadata, and C parser CLI helpers | `parser.py`, `lexer.py`, `models.py`, `preprocessor.py`, `type_resolver.py`, `cli.py` | `tests/parser/c/`, `docs/developer/c-parser-reference.md` |
| `x2py/pyi_parser/` | Semantic `.pyi` text/file parsing to Python AST. | `parser.py` | `tests/pyi/test_pyi_to_ir.py`, `docs/user/reference/semantic-pyi-format.md` |
| `x2py/semantics/` | Language-neutral semantic IR, source-to-IR conversion, `.pyi` AST conversion, policy completion, readiness, and codegen lowering | `models.py`, `fortran2ir.py`, `c2ir.py`, `pyi2ir.py`, `policy_completion.py`, `readiness.py`, `ir2ast.py` | `tests/semantics/`, `tests/pyi/`, `docs/user/reference/semantic-ir.md`, `docs/user/reference/semantic-pyi-format.md` |
| `x2py/codegen/` | Codegen AST, bridge and binding generation, printers, and semantic `.pyi` printing | `models/`, `bridges/fortran_to_c.py`, `bindings/c_to_python.py`, `printers/`, `binding_pipeline.py` | `tests/wrapper/`, `tests/semantics/test_pyi_printer.py`, `docs/user/guide/fortran-wrapper.md` |
| `x2py/naming/` | Unified public-name and generated-symbol policy for Python, C, and Fortran targets | `policy.py` | naming, visibility, and wrapper runtime tests |
X2PY_C_DOCS_END -->

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
| `x2py/fortran_type_probe.py` | Fortran kind and storage probing. |
| `x2py/ownership_policy.py` | Central ownership, transfer, destruction, and generated-action policy. |
| `x2py/fortran_parser/parser.py` | Fortran parser project model and diagnostics. |
| `x2py/fortran_parser/cli.py` | Fortran parser report formatting. |
| `x2py/semantic_metadata.py` | Cross-stage semantic metadata keys that survive parser, policy, printer, and lowering boundaries. |
| `x2py/semantics/models.py` | Semantic IR dataclasses and core model metadata. |
| `x2py/semantics/fortran2ir.py` | Fortran parser facts to semantic modules. |
| `x2py/pyi_parser/parser.py` | Minimal `.pyi` text/file parsing to Python AST. |
| `x2py/pyi_pipeline.py` | Semantic `.pyi` text/file/path-set conversion and external-type reconciliation. |
| `x2py/semantics/pyi2ir.py` | Semantic `.pyi` AST conversion and validation. |
| `x2py/semantics/policy_completion.py` | Post-IR semantic policy completion before readiness and lowering. |
| `x2py/semantics/readiness.py` | Support blockers and readiness reporting. |
| `x2py/semantics/ir2ast.py` | Semantic IR to codegen AST lowering. |
| `x2py/codegen/binding_pipeline.py` | Ordered bridge and binding generation. |
| `x2py/codegen/printers/fcode.py` | Fortran source printing. |
| `x2py/codegen/printers/pyi_printer.py` | Semantic `.pyi` printing. |
| `x2py/compiling/basic.py` | Native compile object model. |
| `x2py/compiling/compilers.py` | Compiler command execution and tool lookup. |
| `x2py/compiling/python_wrapper.py` | Generated wrapper compilation and shared-library linking. |
| `x2py/compiling/runtime_support.py` | Runtime support installation for generated wrappers. |
| `x2py/naming/policy.py` | Public wrapper names and generated target-language symbols. |
| `x2py/stdlib/` | Runtime support payload copied into generated builds. |

<!-- X2PY_C_DOCS_START
| `x2py/c_type_probe.py` | C target ABI type probing. |
| `x2py/c_parser/parser.py` | C parser project model and diagnostics. |
| `x2py/c_parser/cli.py` | C parser report formatting and preprocessing integration. |
| `x2py/semantics/c2ir.py` | C parser facts to semantic modules. |
| `x2py/codegen/bridges/fortran_to_c.py` | Fortran bind(C) bridge generation. |
| `x2py/codegen/bindings/c_to_python.py` | CPython extension binding generation. |
| `x2py/codegen/bindings/cpython_api.py` | CPython C API helper nodes. |
| `x2py/codegen/bindings/numpy_cpython_api.py` | NumPy C API helper nodes. |
| `x2py/codegen/printers/ccode.py` | C source printing. |
| `x2py/codegen/printers/cpythoncode.py` | CPython C source printing. |
X2PY_C_DOCS_END -->

## Layer-To-Layer Route

For source-driven Fortran wrappers, read in this order:

<!-- X2PY_C_DOCS_START
```text
x2py/cli.py
  -> x2py/wrapping.py
  -> x2py/preprocessing.py
  -> x2py/fortran_parser/parser.py
  -> x2py/fortran_type_probe.py
  -> x2py/semantics/fortran2ir.py
  -> x2py/semantics/policy_completion.py
  -> x2py/semantics/readiness.py
  -> x2py/semantics/ir2ast.py
  -> x2py/codegen/bridges/fortran_to_c.py
  -> x2py/codegen/bindings/c_to_python.py
  -> x2py/compiling/python_wrapper.py
  -> tests/wrapper/fortran/
```
X2PY_C_DOCS_END -->

For semantic `.pyi` builds, the parser branch is replaced by:

```text
x2py/pyi_parser/parser.py
  -> x2py/pyi_pipeline.py
  -> x2py/semantics/pyi2ir.py
  -> x2py/semantics/policy_completion.py
  -> x2py/semantics/readiness.py
  -> x2py/semantics/ir2ast.py
```

<!-- X2PY_C_DOCS_START
For inspection-only C workflows, the path currently stops at semantic IR,
`.pyi`, and readiness:
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
```text
x2py/cli.py
  -> x2py/c_parser/parser.py
  -> x2py/c_type_probe.py
  -> x2py/semantics/c2ir.py
  -> x2py/codegen/printers/pyi_printer.py
  -> x2py/semantics/policy_completion.py
  -> x2py/semantics/readiness.py
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
Runtime wrapping of user-supplied C inputs is not implemented yet.
X2PY_C_DOCS_END -->

## Package-Level Notes

The hardest source packages also have local README files:

- `x2py/README.md`
- `x2py/fortran_parser/README.md`
- `x2py/semantics/README.md`
- `x2py/codegen/README.md`
- `x2py/compiling/README.md`

<!-- X2PY_C_DOCS_START
- `x2py/c_parser/README.md`
X2PY_C_DOCS_END -->

Keep these files short. They should tell developers where to enter the code,
what the package owns, what it must not own, and where the tests and public docs
live.
