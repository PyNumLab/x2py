---
title: Verification
audience: users, contributors
prerequisites: installation
related: first-wrapped-function.md, ../troubleshooting/index.md, ../reference/cli-commands.md
status: maintained
---

# Verification

Verify the Python environment, contract-generation path, and native build path
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

## 2. Verify The Contract Path

Use the `scale.f90` input created in the
[README Quick Start](../../../README.md#quick-start).

From the directory containing `scale.f90`, print the semantic `.pyi` contract
without compiling a wrapper:

```bash
python3 -m x2py generate --pyi scale.f90
```

The generated declaration should look like:

```python
from x2py.contracts import Addr, Arg, Float64, external, native_call

@external
@native_call([Addr(Arg(0)), Addr(Arg(1))])
def scale(
    value: Float64,
    factor: Float64
) -> Float64: ...
```

This verifies preprocessing, parsing, semantic lowering, type probing, and
contract printing. It does not compile or import an extension.

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

From the same directory, build `scale.f90` into a dedicated directory:

```bash
python3 -m x2py scale.f90 \
  --out-dir build/verify
```

The command must create:

- an importable `scale` extension under `build/verify`; and
- generated native bridge, object, native-support, and extension files.

<!-- X2PY_C_DOCS_START
- generated bridge, C binding, object, and native-support files.
X2PY_C_DOCS_END -->

Import the extension from that build directory:

```python
import sys

import numpy as np

sys.path.insert(0, "build/verify")
import scale

assert scale.scale(np.float64(3.0), np.float64(2.5)) == np.float64(7.5)
```

## 4. Inspect Generated Files

`WrapperBuildResult` is the stable way to inspect a Python API build:

```python
from pathlib import Path

from x2py import build_fortran_extension

build = build_fortran_extension(
    "scale.f90",
    output_dir="build/verify",
)

assert build.compiled
assert build.shared_library.is_file()
assert all(Path(path).exists() for path in build.generated_files)
print(build.output_dir)
print(build.shared_library)
```

For CLI builds, add `--verbose` when a compiler or linker command fails; it
prints the exact native commands and stage timings.

## Escalation Path

| Failure | Next action |
| --- | --- |
| `import x2py` or `import numpy` fails | Recheck the active interpreter; Installation Issues is covered later. |
| `--help` works but `.pyi` generation fails | Read the diagnostic; diagnostic codes are catalogued later in the reference section. |
| Compiler executable is missing | Recheck `PATH` and the compiler command; Compiler Issues is covered later. |
| Native compilation or linking fails | Rebuild with `--verbose`; Build Issues is covered later. |
| Build succeeds but import or call fails | Compare the call with the generated contract; Runtime Issues is covered later. |
| The checked smoke test passes but an advanced construct fails | The language feature matrix later records its support status and focused evidence. |

Contributors changing documentation should run
`python3 -m pytest -q tests/docs/test_examples.py tests/docs/test_structure.py`.
Wrapper behavior changes require the focused `tests/wrapper/fortran/...` path;
the full GitHub Actions matrix is the final cross-version evidence.

## Evidence

The linked `scale.f90` input is checked against the repository fixture by
[`test_examples.py`](../../../tests/docs/test_examples.py).
Native artifact placement and runtime calls are checked by
[`test_build_modes.py`](../../../tests/wrapper/fortran/build_from_source/test_build_modes.py)
and
[`test_runtime_abi.py`](../../../tests/wrapper/fortran/build_from_source/test_runtime_abi.py).
