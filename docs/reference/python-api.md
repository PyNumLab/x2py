---
title: Python API Reference
audience: users, developers
prerequisites: installation
related: cli-commands.md, ../developer-guide/maintainer-guide.md
status: maintained
---

# Python API Reference

This page documents the checked public symbols exported from `x2py.__all__`.
The names below are the supported import surface for callers that use x2py as a
library.

```python
import x2py

sorted(x2py.__all__)
```

## CLI entrypoint

| Symbol | Purpose |
| --- | --- |
| `main` | Runs the `python3 -m x2py` command-line interface. Prefer the CLI for shell workflows and the functions below for Python workflows. |

## C parser API

| Symbol | Purpose |
| --- | --- |
| `parse_c_file` | Parses one C source or header into a `CFile`. |
| `parse_c_project` | Parses multiple C files into a `CProject`. |
| `CFile` | Parsed C file model. |
| `CProject` | Parsed C project model. |
| `CParseError` | Error raised for C parse failures. |

The parser APIs expect already-selected inputs. CLI-only features such as
language inference, directory expansion, command-line validation, and compiler
preprocessing option parsing live in the CLI layer.

## Fortran parser API

| Symbol | Purpose |
| --- | --- |
| `parse_fortran_file` | Parses one Fortran file into a `FortranFile`. |
| `parse_fortran_project` | Parses multiple Fortran files into a `FortranProject`. |
| `FortranFile` | Parsed Fortran file model. |
| `FortranProject` | Parsed Fortran project model. |
| `FortranModule` | Parsed module model. |
| `FortranSubmodule` | Parsed submodule model. |
| `FortranProgram` | Parsed program model. |
| `FortranBlockData` | Parsed block-data unit model. |
| `FortranDerivedType` | Parsed derived-type model. |
| `FortranInterface` | Parsed interface model. |
| `FortranProcedureSignature` | Parsed function or subroutine signature model. |
| `FortranArgument` | Parsed procedure argument model. |
| `FortranParseError` | Error raised for Fortran parse failures. |

## Semantic conversion API

| Symbol | Purpose |
| --- | --- |
| `fortran_file_to_semantic_modules` | Converts a parsed Fortran file to semantic module models. |
| `fortran_project_to_semantic_modules` | Converts a parsed Fortran project to semantic module models. |
| `fortran_module_to_semantic_module` | Converts one parsed Fortran module to one semantic module. |
| `collect_semantic_compile_time_requirements` | Collects semantic values that must be known at compile time. |
| `resolve_semantic_compile_time_values` | Resolves collected compile-time requirements. |
| `CToIRConverter` | Stateful C-to-semantic-IR converter. |
| `c_file_to_semantic_module` | Converts one parsed C file to one semantic module. |
| `c_file_to_semantic_modules` | Converts one parsed C file to semantic modules. |
| `c_project_to_semantic_module` | Converts a parsed C project to one semantic module. |
| `c_project_to_semantic_modules` | Converts a parsed C project to semantic modules. |
| `c_function_to_semantic_function` | Converts one parsed C function to a semantic function. |
| `c_parameter_to_semantic_argument` | Converts one parsed C parameter to a semantic argument. |
| `c_struct_to_semantic_class` | Converts one parsed C struct to a semantic class. |
| `c_type_to_semantic_type` | Converts one parsed C type to a semantic type. |

Semantic conversion is the boundary between parser models and wrapper-facing
contracts. Use readiness checks before assuming a semantic module can be wrapped.

## Semantic `.pyi` contract API

| Symbol | Purpose |
| --- | --- |
| `parse_pyi_text` | Parses semantic `.pyi` source text. |
| `load_pyi_file` | Loads and parses one semantic `.pyi` file. |
| `load_pyi_modules` | Loads semantic `.pyi` modules from files or directories. |
| `convert_pyi_to_ir` | Converts parsed semantic `.pyi` content to semantic IR. |

Editable `.pyi` files are a contract surface. User-private declarations in a
`.pyi` file are distinct from source-private Fortran declarations omitted from
generated stubs.

## Readiness and stub emission API

| Symbol | Purpose |
| --- | --- |
| `assess_semantic_wrap_readiness` | Checks semantic IR for wrapper readiness and reports blockers. |
| `assess_pyi_wrap_readiness` | Checks semantic `.pyi` input for wrapper readiness and reports blockers. |
| `emit_module_stubs` | Emits semantic Python `.pyi` text from semantic module models. |
| `opaque_dependency_modules` | Computes opaque dependency modules needed for emitted stubs. |

## Wrapper build API

| Symbol | Purpose |
| --- | --- |
| `build_fortran_extension` | Builds a Python extension from Fortran source inputs. |
| `build_pyi_extension` | Builds a Python extension from semantic `.pyi` contracts plus explicit native artifacts. |
| `build_pyi_extension_from_manifest` | Replays a saved semantic `.pyi` wrapper build manifest, either building directly or regenerating `Makefile.x2py`. |
| `WrapperBuildResult` | Result model returned by wrapper build functions. |
| `NativeBuildPlan` | Structured native implementation compile/link plan attached to a wrapper build result. |
| `NativeCompilationUnit` | Native source compilation unit and produced object recorded in a native build plan. |
| `NativePrebuiltArtifact` | Caller-supplied native object, archive, or shared library recorded in a native build plan. |
| `NativeLinkItem` | One ordered object, archive, shared library, named library, or linker argument in a native link plan. |

Fortran source wrapper builds own the normal source-to-extension workflow.
Semantic `.pyi` wrapper builds require explicit native implementation inputs
such as native Fortran sources, objects, libraries, and include/module
directories. Inspect
`WrapperBuildResult.native_build_plan` when a caller needs the native
compilation units, produced objects, prebuilt artifacts, module/include
directories, library directories, or ordered native link items separately from
the semantic contract paths. Semantic `.pyi` build results also expose a
normalized replay `manifest`; Makefile mode writes that manifest to
`<out-dir>/x2py-build.json` before generating `Makefile.x2py`.

## Target type and NumPy helpers

| Symbol | Purpose |
| --- | --- |
| `FortranTypeProbeError` | Error raised for Fortran type probing failures. |
| `FortranTypeProbeReport` | Report model for Fortran type probing. |
| `build_fortran_type_probe_source` | Builds the source used to probe Fortran type properties. |
| `fortran_type_probe_expressions` | Produces expressions used by the Fortran type probe. |
| `probe_fortran_type_expressions` | Runs Fortran type probes for selected expressions. |
| `evaluate_fortran_type_requirements` | Evaluates semantic requirements against a Fortran type probe report. |
| `SEMANTIC_DTYPE_TO_NUMPY_DTYPE` | Default semantic dtype to NumPy dtype map. |
| `semantic_dtype_to_numpy_dtype` | Maps one semantic dtype to a NumPy dtype. |
| `semantic_dtype_to_numpy_dtype_map` | Returns a semantic dtype to NumPy dtype mapping. |
| `semantic_type_to_numpy_dtype` | Maps one semantic type to a NumPy dtype. |
| `numpy_dtype_expression` | Returns the generated expression for a NumPy dtype. |

These helpers are public because wrapper contracts need deterministic target
type and NumPy dtype mapping. The CLI type-probe flags are documented in
[CLI Commands Reference](cli-commands.md).

## Current boundaries

- Runtime wrapping of user-supplied C libraries is not part of the public
  wrapper-build API yet.
- Parser functions do not run CLI path expansion or command-line preprocessing
  validation.
- Generated module, function, and class reference pages are still planned; this
  page is the maintained public-symbol inventory until those pages exist.
