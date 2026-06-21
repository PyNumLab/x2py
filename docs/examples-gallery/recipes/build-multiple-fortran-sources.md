---
title: Build Multiple Fortran Sources
audience: users, developers
prerequisites: basic wrapper tutorial, supported compiler toolchain
related: ../verified-cookbook.md, ../../user-guide/fortran-wrapper.md
status: maintained
---

# Build Multiple Fortran Sources

Use this recipe when one Python extension needs declarations or implementations
from more than one Fortran source file.

## Build

Pass every source in compiler-valid order. The first semantic module names the
merged extension:

```bash
python3 -m x2py \
  tests/wrapper/fortran/multi_source_builds/modules/first_api.f90 \
  tests/wrapper/fortran/multi_source_builds/modules/second_api.f90 \
  --wrap \
  --out-dir build/multi_api \
  --json
```

## Import

```python
import sys

import numpy as np

sys.path.insert(0, "build/multi_api")
import first_api

assert first_api.add_one(np.int32(4)) == np.int32(5)
assert first_api.double_value(np.int32(4)) == np.int32(10)
```

## Ordering Rules

x2py does not discover missing sources and does not reorder dependencies. Put
module providers before module consumers, matching the order your compiler
expects for a direct native build.

## Notes

- The output is one Python extension, not one extension per source file.
- Use `--out-dir` to keep all generated and native artifacts together.
- Use [Generate an editable Makefile](generate-editable-makefile.md) when you
  need your build system to run the compile/link step later.
