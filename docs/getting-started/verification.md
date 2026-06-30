---
title: Verification
audience: users, contributors
prerequisites: installation
related: first-wrapped-function.md, ../troubleshooting/index.md, ../reference/cli-commands.md
status: maintained
---

# Verification

Verify the Python environment, inspection path, and native build path
separately. This makes a failure easier to route.

## 1. Verify The Installed Package

Run these commands from the activated environment:

```bash
python3 -c "from importlib.metadata import version; import x2py; print(version('x2py'))"
python3 -c "import numpy; print(numpy.__version__)"
python3 -m x2py --help
```

The first two commands prove that x2py and NumPy import from the selected
interpreter. The third proves that the module entrypoint is installed.

## 2. Verify The Inspection Path

This checked command parses a repository fixture without compiling a wrapper:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/basic_subroutine.f90
  Source: fortran
  Semantic modules: m1
  Wrappable: yes
  Public functions: 1
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```

This verifies preprocessing, parsing, semantic lowering, type probing, and
readiness. It does not compile or import an extension.

## 3. Verify The Native Toolchain

Check compiler discovery before running a build:

```bash
gfortran --version
```

<!-- X2PY_C_DOCS_START
```bash
gfortran &#45;&#45;version
gcc &#45;&#45;version
```
X2PY_C_DOCS_END -->

Then build the checked scalar fixture into a dedicated directory:

```bash
python3 -m x2py tests/data/fortran/wrapper/scale.f90 \
  --wrap \
  --out-dir build/verify \
  --json
```

The JSON result must report:

- `compiled` as `true`;
- `module_name` as `scale`;
- an existing `shared_library` under `build/verify`; and
- generated native bridge, object, runtime-support, and extension paths.

<!-- X2PY_C_DOCS_START
- generated bridge, C binding, object, and runtime-support paths.
X2PY_C_DOCS_END -->

Import the extension through the Python API result so the platform-specific
shared-library suffix does not need to be guessed:

```python
from importlib.util import module_from_spec, spec_from_file_location

import numpy as np

from x2py import build_fortran_extension

build = build_fortran_extension(
    "tests/data/fortran/wrapper/scale.f90",
    output_dir="build/verify",
)
spec = spec_from_file_location(build.module_name, build.shared_library)
extension = module_from_spec(spec)
spec.loader.exec_module(extension)

assert extension.scale(np.float64(3.0), np.float64(2.5)) == np.float64(7.5)
```

## 4. Inspect Generated Files

`WrapperBuildResult` is the stable way to inspect a Python API build:

```python
from pathlib import Path

from x2py import build_fortran_extension

build = build_fortran_extension(
    "tests/data/fortran/wrapper/scale.f90",
    output_dir="build/verify",
)

assert build.compiled
assert build.shared_library.is_file()
assert all(Path(path).exists() for path in build.generated_files)
print(build.output_dir)
print(build.shared_library)
```

For CLI builds, `--json` exposes the same fields. Add `--verbose` when a
compiler or linker command fails; it prints the exact native commands and stage
timings.

## Escalation Path

| Failure | Next action |
| --- | --- |
| `import x2py` or `import numpy` fails | Recheck the active interpreter and [Installation Issues](../troubleshooting/installation-issues.md). |
| `--help` works but readiness fails | Read the diagnostic and the [diagnostic code reference](../reference/diagnostic-codes.md). |
| Compiler executable is missing | Use [Compiler Issues](../troubleshooting/compiler-issues.md). |
| Native compilation or linking fails | Rebuild with `--verbose` and use [Build Issues](../troubleshooting/build-issues.md). |
| Build succeeds but import or call fails | Use [Runtime Issues](../troubleshooting/runtime-issues.md). |
| The checked smoke test passes but an advanced construct fails | Check the [feature matrix](../language-support/feature-matrix.md), then run the focused wrapper test area named by that row. |

Contributors changing documentation should run
`python3 -m pytest -q tests/tools/test_documentation_examples.py tests/tools/test_documentation_structure.py`.
Wrapper behavior changes require the focused `tests/wrapper/fortran/...` path;
the full GitHub Actions matrix is the final cross-version evidence.

## Evidence

The readiness output is executed by
[`test_documentation_examples.py`](../../tests/tools/test_documentation_examples.py).
Native artifact placement and runtime calls are checked by
[`test_build_modes.py`](../../tests/wrapper/fortran/build_from_source/test_build_modes.py)
and
[`test_runtime_abi.py`](../../tests/wrapper/fortran/build_from_source/test_runtime_abi.py).
