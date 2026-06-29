---
title: First Project
audience: users
prerequisites: installation, verification
related: first-wrapped-function.md, beginner-workflow.md, ../user-guide/packaging.md
status: maintained
---

# First Project

Keep native input, generated output, and Python tests separate. A minimal
project can use this layout:

```text
scale-project/
  src/
    scale_api.f90
  build/
    .gitkeep
  tests/
    test_scale.py
  pyproject.toml
```

`src/` is user-owned native source. `build/` is disposable x2py output.
`tests/` contains Python-level assertions against the generated API.

## Add The First Source

Put the scalar module shown in
[First Wrapped Function](first-wrapped-function.md#source) at
`src/scale_api.f90`. The first source filename determines the extension import
name, so this project produces an extension named `scale_api`. A contained
Fortran module named `fruntime_abi_f90` remains a child namespace inside that
extension.

## Build Into A Dedicated Directory

From `scale-project/`, run:

```bash
python3 -m x2py src/scale_api.f90 \
  --wrap \
  --out-dir build/scale_api \
  --json
```

Using `--out-dir` keeps generated bridge sources, C bindings, runtime support,
objects, module files, and the shared library under `build/scale_api/`.
The returned JSON is the source of truth for the exact shared-library path.

Without `--out-dir`, x2py instead places intermediate files under
`src/__x2py__/` and writes the importable extension beside `src/scale_api.f90`.
The explicit build directory is easier to clean and should be the beginner
default.

## Add An Import Check

Create `tests/test_scale.py` with a path-based import that works for the
platform-specific extension suffix:

```python
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np


shared_libraries = [
    path
    for path in Path("build/scale_api").iterdir()
    if path.name.startswith("scale_api.") and path.suffix in {".so", ".pyd", ".dylib"}
]
assert len(shared_libraries) == 1

spec = spec_from_file_location("scale_api", shared_libraries[0])
extension = module_from_spec(spec)
spec.loader.exec_module(extension)

assert extension.fruntime_abi_f90.scale(
    np.float64(3.0), np.float64(2.5)
) == np.float64(7.5)
```

Run it with:

```bash
python3 tests/test_scale.py
```

For automation, prefer the Python build API shown in
[Verification](verification.md#3-verify-the-native-toolchain), because its
`shared_library` result avoids scanning an output directory.

## Clean And Rebuild

Generated output is not the API source of truth and should not be hand-edited.
For a clean rebuild, remove the selected output directory and run the same
command again:

```bash
rm -rf build/scale_api
python3 -m x2py src/scale_api.f90 --wrap --out-dir build/scale_api --json
```

Keep `build/` out of version control. Keep the native source, Python tests, and
any intentionally edited semantic `.pyi` contracts under version control.

## Current Packaging Boundary

x2py builds a local native extension; it does not currently turn this layout
into a portable wheel. Shared libraries are compiler-, Python-, platform-, and
architecture-specific. Read [Distribution](../user-guide/distribution.md)
before moving an artifact to another machine.

## Next Files To Read

- [First Wrapped Function](first-wrapped-function.md) explains the scalar API
  and dtype failure mode.
- [First Wrapped Module](first-wrapped-module.md) explains child namespaces and
  native module state.
- [Common Beginner Workflow](beginner-workflow.md) adds inspection, readiness,
  rebuild, and artifact review.
- [Fortran Wrapper Guide](../user-guide/fortran-wrapper.md) is the complete
  current runtime contract.

## Evidence

Explicit and default artifact placement is checked by
[`test_build_modes.py`](../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
The scalar import and call are checked by
[`test_runtime_abi.py`](../../tests/wrapper/fortran/build_from_source/test_runtime_abi.py).
