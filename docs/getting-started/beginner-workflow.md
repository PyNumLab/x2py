---
title: Common Beginner Workflow
audience: users
prerequisites: first wrapped module
related: ../tutorials/basic-wrapper.md, ../examples-gallery/verified-cookbook.md, ../reference/cli-commands.md
status: maintained
---

# Common Beginner Workflow

You have already built and called the `scale.f90` example. This page turns that
same file into a repeatable project workflow: keep source under `src/`, build
into `build/`, run a small Python check, and cleanly rebuild when the native
contract changes.

Use the `scale.f90` input from the
[README Quick Start](../../README.md#quick-start). Keep the same filename when
you move it into a project layout.

## 1. Create A Small Project Layout

Keep native sources under `src/` and Python tests under `tests/`. Treat every
file under `build/` as generated output that the next build may replace.

Start with this layout:

```text
scale-project/
  src/
    scale.f90
  build/
  tests/
    test_scale.py
```

Run the remaining commands from `scale-project/`. Keep `src/` and `tests/`
under version control. Do not commit `build/`.

<!-- X2PY_C_DOCS_START
Keep native sources under `src/` and Python tests under `tests/`. Do not edit
generated bridge, C binding, object, module, runtime-support, or shared-library
files under `build/`; the next build can replace them.
X2PY_C_DOCS_END -->

## 2. Review The Contract Before Compiling

Before building, print the semantic `.pyi` contract for the same source:

```bash
python3 -m x2py src/scale.f90 --pyi
```

The output should match the wrapper contract from the
[First Wrapped Function](first-wrapped-function.md) page:

```python
@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def scale(
    value: Float64,
    factor: Float64
) -> Float64: ...
```

This confirms the Python-facing dtype contract and the native scalar-address
projection that code generation will follow. It does not prove that the
compiler, linker, native dependency set, or runtime environment is valid; the
build and smoke test still need to run.

## 3. Build Into An Explicit Directory

```bash
python3 -m x2py src/scale.f90 \
  --wrap \
  --out-dir build/scale \
  --json
```

Build output goes under `build/scale`, leaving `src/scale.f90` untouched. Keep
the JSON result in build logs when debugging. It records the module name, output
directory, shared-library path, generated files, and native build plan. Use
`--verbose` instead of `--json` when you need exact compiler and linker
commands.

## 4. Run A Python Smoke Test

Put this in `tests/test_scale.py`, or run it directly while learning the flow:

```python
import sys

import numpy as np

sys.path.insert(0, "build/scale")
import scale

result = scale.scale(np.float64(3.0), np.float64(2.5))
assert result == np.float64(7.5)
```

Do not stop at “the extension imports.” For each wrapped routine, keep at least
one asserted result. For real projects, also add failure checks that matter to
the contract: wrong dtype, wrong rank or shape, non-writable outputs, or
unsupported optional arguments. The generated `.pyi` and the
[feature matrix](../language-support/feature-matrix.md) define which checks are
expected.

## 5. Review Generated Artifacts

You normally do not need to open generated files. When debugging, expect
`build/scale` to contain:

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

## 6. Rebuild Cleanly When The Contract Changes

For a normal rerun, execute the same build command. After changing source order,
compiler flags, native dependencies, or the wrapper contract, remove the
selected output directory first:

```bash
rm -rf build/scale
python3 -m x2py src/scale.f90 --wrap --out-dir build/scale --json
```

Use `--wrap --makefile` when you intentionally want inspectable commands and
manual rebuild control. `--makefile` and `--verbose` are separate modes and
cannot be combined.

## Advanced Next Step: Edit The Semantic Contract

Stay with source-driven builds until the normal loop is clear. When you need to
review or intentionally edit the semantic `.pyi` contract, generate it
separately:

```bash
python3 -m x2py src/scale.f90 --pyi --out contracts
```

Do not treat this as the beginner default. A runtime build from an edited `.pyi`
must also receive the native implementation explicitly through options such as
`--native-fortran-sources`, `--native-objects`, or native libraries. Follow
[Editing Semantic .pyi Contracts](../user-guide/editing-semantic-pyi-contracts.md)
before using that path.

## Failure Routing

1. If `.pyi` generation fails, fix preprocessing, parsing, or semantic diagnostics.
2. If compilation or linking fails, rebuild with `--verbose` and inspect
   [Build Issues](../troubleshooting/build-issues.md).
3. If import or runtime behavior fails, use
   [Runtime Issues](../troubleshooting/runtime-issues.md).
4. If a documented supported behavior fails, reproduce it with the focused
   wrapper test linked by the feature matrix before escalating to full CI.

Support boundaries are maintained in the
[language feature matrix](../language-support/feature-matrix.md), platform and
toolchain requirements in [Installation](installation.md), and artifact
portability rules in [Distribution](../user-guide/distribution.md).

## Evidence

CLI build modes, output placement, and clean artifact expectations are checked
by [`test_build_modes.py`](../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
The source-driven runtime call is checked by
[`test_runtime_abi.py`](../../tests/wrapper/fortran/build_from_source/test_runtime_abi.py),
and semantic `.pyi` build requirements by
[`test_pyi_wrapper_builds.py`](../../tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py).
