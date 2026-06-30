---
title: Common Beginner Workflow
audience: users
prerequisites: first wrapped module
related: ../tutorials/basic-wrapper.md, ../examples-gallery/verified-cookbook.md, ../reference/cli-commands.md
status: maintained
---

# Common Beginner Workflow

Use one repeatable loop for a small Fortran wrapper project: edit native source,
inspect the contract, check readiness, build into a disposable directory, run a
Python assertion, and rebuild cleanly when the contract changes.

## 1. Edit User-Owned Inputs

Keep native sources under `src/` and Python tests under `tests/`. Treat every
file under `build/` as generated output that the next build may replace.

<!-- X2PY_C_DOCS_START
Keep native sources under `src/` and Python tests under `tests/`. Do not edit
generated bridge, C binding, object, module, runtime-support, or shared-library
files under `build/`; the next build can replace them.
X2PY_C_DOCS_END -->

## 2. Inspect Before Compiling

Use the inspection stages independently:

```bash
python3 -m x2py src/scale_api.f90 --parse
python3 -m x2py src/scale_api.f90 --semantics
python3 -m x2py src/scale_api.f90 --pyi
python3 -m x2py src/scale_api.f90 --wrap-readiness
```

The parser report answers what x2py read. Semantic IR answers what native facts
were resolved. The `.pyi` shows the generated wrapper contract. Readiness lists
blockers that must be resolved before wrapper generation.

`Wrappable: yes` means no semantic blocker is known. It does not guarantee that
the compiler, linker, native dependency set, or runtime environment is valid.

## 3. Build Into An Explicit Directory

```bash
python3 -m x2py src/scale_api.f90 \
  --wrap \
  --out-dir build/scale_api \
  --json
```

Keep the JSON result in build logs when debugging. It records the module name,
output directory, shared-library path, generated files, and native build plan.
Use `--verbose` instead of `--json` when you need exact compiler and linker
commands.

## 4. Run A Python Smoke Test

Run at least one successful call with an asserted result, not merely an import:

```python
import sys

import numpy as np

sys.path.insert(0, "build/scale_api")
import scale_api

module = scale_api.fruntime_abi_f90
result = module.scale(np.float64(3.0), np.float64(2.5))
assert result == np.float64(7.5)
```

Also test contract failures that matter to the project, such as wrong dtypes,
wrong rank or shape, non-writable outputs, or unsupported optional arguments.
The generated `.pyi` and the [feature matrix](../language-support/feature-matrix.md)
define which checks are expected.

## 5. Review Generated Artifacts

Generated output normally contains:

| Artifact | Purpose |
| --- | --- |
| `x2py_runtime/` | shared runtime support sources |
| `.o` and `.mod` files | native intermediates |
| `<name>.<extension-suffix>` | importable extension |

<!-- X2PY_C_DOCS_START
| `bind_c_<name>_wrapper.f90` | Fortran-to-C ABI bridge |
| `<name>_wrapper.c` and `.h` | CPython binding |
X2PY_C_DOCS_END -->

Treat these as diagnostic evidence, not editable API definitions. Change the
native source or an intentional semantic `.pyi` contract instead.

## 6. Rebuild Deliberately

For a normal incremental rerun, execute the same x2py command. For a clean
rebuild after changing source order, compiler flags, native dependencies, or
the contract, remove the selected output directory first:

```bash
rm -rf build/scale_api
python3 -m x2py src/scale_api.f90 --wrap --out-dir build/scale_api --json
```

Use `--makefile` when you intentionally want inspectable commands and manual
rebuild control. `--makefile` and `--verbose` are separate modes and cannot be
combined.

## Semantic `.pyi` Review Workflow

Generate a contract package when source inference needs review or intentional
editing:

```bash
python3 -m x2py src/scale_api.f90 --pyi --out contracts
python3 -m x2py contracts/scale_api/scale_api.pyi --wrap-readiness
```

Source-driven `--wrap` and source-driven `--pyi` are separate commands. A
runtime build whose semantic input is an edited `.pyi` must also receive the
native implementation explicitly through options such as
`--native-fortran-sources`, `--native-objects`, or native libraries. Follow
[Editing Semantic .pyi Contracts](../user-guide/editing-semantic-pyi-contracts.md)
before using that advanced path.

## Failure Routing

1. If inspection fails, fix preprocessing, parsing, or semantic diagnostics.
2. If readiness reports a blocker, check the feature matrix and generated
   contract before attempting code generation.
3. If compilation or linking fails, rebuild with `--verbose` and inspect
   [Build Issues](../troubleshooting/build-issues.md).
4. If import or runtime behavior fails, use
   [Runtime Issues](../troubleshooting/runtime-issues.md).
5. If a documented supported behavior fails, reproduce it with the focused
   wrapper test linked by the feature matrix before escalating to full CI.

## Current Boundaries

- Source order for multiple files is caller-controlled; automatic project-wide
  dependency discovery is not the beginner workflow.
- Generated extensions are local native artifacts, not portable wheels.
- Other platforms and compiler ABIs need validation beyond the current Ubuntu
  GNU evidence.

<!-- X2PY_C_DOCS_START
- Runtime wrapping is implemented for Fortran inputs; C-input runtime wrapping
  remains future work.
X2PY_C_DOCS_END -->

## Evidence

CLI build modes, output placement, and clean artifact expectations are checked
by [`test_build_modes.py`](../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
The source-driven runtime call is checked by
[`test_runtime_abi.py`](../../tests/wrapper/fortran/build_from_source/test_runtime_abi.py),
and semantic `.pyi` build requirements by
[`test_pyi_wrapper_builds.py`](../../tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py).
