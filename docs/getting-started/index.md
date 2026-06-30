---
title: Getting Started
audience: users
prerequisites: repository checkout
related: installation.md, verification.md, ../tutorials/basic-wrapper.md
status: maintained
---

# Getting Started

This section takes you from a source checkout to an imported Python extension.
The supported beginner path wraps Fortran source with the GNU native toolchain.

<!-- X2PY_C_DOCS_START
This section takes you from a source checkout to an imported Python extension.
The shortest supported path wraps Fortran source with the GNU compiler
toolchain. C parsing and interface inspection are available, but runtime
wrapping of user-supplied C code is not implemented yet.
X2PY_C_DOCS_END -->

## Beginner Path

Follow these pages in order:

1. [Install x2py and its native prerequisites](installation.md).
2. [Verify Python, NumPy, the CLI, and the compilers](verification.md).
3. [Build and call a scalar function](first-wrapped-function.md).
4. [Create a minimal project](first-project.md).
5. [Work with a Fortran module and its saved state](first-wrapped-module.md).
6. [Use the normal edit, inspect, build, test, and rebuild loop](beginner-workflow.md).

The [basic wrapper tutorial](../tutorials/basic-wrapper.md) combines inspection,
semantic `.pyi` generation, readiness, compilation, and import into one longer
walkthrough. Use the pages here when you need one step at a time.

## What You Will Build

The checked beginner example exposes a Fortran function through an importable
Python extension:

<!-- X2PY_C_DOCS_START
The checked beginner example exposes a Fortran function as an importable
CPython extension:
X2PY_C_DOCS_END -->

```python
import numpy as np

import scale

result = scale.scale(np.float64(3.0), np.float64(2.5))
assert result == np.float64(7.5)
```

The first example is a standalone procedure exposed directly at the extension
root. The next module example introduces contained Fortran modules as Python
child namespaces.

## Current Boundary

- Python 3.10 or newer is required; CI currently verifies 3.10, 3.11, and 3.12.
- The verified platform is Ubuntu Linux with `gfortran-13`. Other compilers and
  operating systems need their own ABI validation.
- Exact NumPy scalar dtypes and array contracts are part of the generated API.
- Runtime wrapper builds require GNU Fortran and native build tools, Python
  development headers, and NumPy development files.
- A readiness result describes the semantic contract; native compilation and
  runtime behavior still require their own verification.

<!-- X2PY_C_DOCS_START
- Runtime wrapper builds use GNU Fortran and C compilers, Python development
  headers, and NumPy headers.
- A readiness result of `Wrappable: yes` describes the semantic contract; it
  does not create a C-input runtime backend.
X2PY_C_DOCS_END -->

Check the [language feature matrix](../language-support/feature-matrix.md) before
depending on an advanced construct. Installation, compiler, build, and import
failures are routed through [Troubleshooting](../troubleshooting/index.md).

## Evidence

The standalone example used throughout this section is checked against its
fixture by
[`test_documentation_examples.py`](../../tests/tools/test_documentation_examples.py),
and its `7.5` runtime result is checked by
[`test_build_modes.py`](../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
