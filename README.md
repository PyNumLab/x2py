# x2py

x2py generates importable Python extensions from Fortran sources, extracts
native declarations into language-neutral semantic IR, emits editable `.pyi`
interfaces, and reports unsupported or incomplete contracts before code
generation.

<!-- X2PY_C_DOCS_START
Fortran-to-Python wrapper generation plus wrapper-oriented parser and semantic
interface tooling for Fortran and C. x2py builds importable CPython extensions
from Fortran sources, extracts native declarations into language-neutral
semantic IR, emits editable `.pyi` interfaces, and reports unsupported or
incomplete contracts before code generation.
X2PY_C_DOCS_END -->

[![Quality](https://github.com/PyNumLab/x2py/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/PyNumLab/x2py/actions/workflows/quality.yml)
[![codecov](https://codecov.io/gh/PyNumLab/x2py/graph/badge.svg?token=QZRRCS5YO6)](https://codecov.io/gh/PyNumLab/x2py)

## Quick Start

x2py requires Python 3.10 or newer. Install a checkout and inspect the CLI:

```bash
python3 -m pip install -e .
python3 -m x2py --help
```

Expected result: the install command completes successfully, and `--help`
prints the CLI usage with input selection, inspection stages, wrapper builds,
and output options.

The default user-facing action for a single Fortran source is to build a Python
extension. This checked input source exists at
`tests/data/fortran/wrapper/scale.f90`; copy it into your working directory
as `scale.f90` before running the commands below:

<!-- x2py-doc-source: tests/data/fortran/wrapper/scale.f90 -->
```fortran
module scale
contains
  real(8) function scale_scalar(value, factor) result(output)
    real(8), intent(in) :: value
    real(8), intent(in) :: factor
    output = value * factor
  end function scale_scalar
end module scale
```

Build it with the default output locations:

```bash
python3 -m x2py scale.f90
```

By default, x2py writes the importable `.so` beside the input source and keeps
generated build intermediates under `__x2py__/`:

```text
.
  scale.f90
  scale.so
  __x2py__/
    generated-wrapper sources
    x2py_runtime/
```

Name the Python extension and final `.so` explicitly with `--out NAME`:

```bash
python3 -m x2py scale.f90 --out SCALE
```

Expected result:

```text
.
  scale.f90
  SCALE.so
  __x2py__/
    generated-wrapper sources
    x2py_runtime/
```

For a wrapper build, `--out SCALE` selects the Python module name and the final
shared-library filename. The Fortran module namespace is still preserved inside
that Python module.

Use `--out-dir` when you want the shared library and generated intermediates in
an explicit build directory:

```bash
python3 -m x2py scale.f90 \
  --out SCALE \
  --out-dir build/SCALE
```

Expected result:

```text
build/SCALE/
  SCALE.so
  generated-wrapper sources
  x2py_runtime/
```

Generate the semantic `.pyi` contract for the same source:

```bash
python3 -m x2py scale.f90 \
  --pyi \
  --out contracts
```

The command writes the contract package:

```text
contracts/
  __init__.pyi
  scale.pyi
```

Expected package entry (`contracts/__init__.pyi`):

```python
from . import scale
```

Expected leaf contract (`contracts/scale.pyi`):

```python
def scale_scalar(
    value: Ptr(Const(Float64)),
    factor: Ptr(Const(Float64))
) -> Float64: ...
```

Then build the shared library from the package-entry `.pyi` contract and the
same native implementation source:

```bash
python3 -m x2py contracts/__init__.pyi \
  --wrap \
  --native-fortran-sources scale.f90 \
  --out SCALE \
  --out-dir build/SCALE_from_pyi
```

Use `--out NAME` with wrapper builds when you want the import name and final
`.so` filename to differ from the default inferred name.

The `.pyi` build produces the same importable extension shape:

```text
build/SCALE_from_pyi/
  SCALE.so
  generated-wrapper sources
  x2py_runtime/
```

The direct source build preserves the native module namespace, so call the
function through `SCALE.scale.scale_scalar`:

```python
import sys

import numpy as np

sys.path.insert(0, "build/SCALE")
import SCALE

print(SCALE.scale.scale_scalar(np.float64(3.0), np.float64(2.5)))  # 7.5
```

The package-entry `.pyi` build above also preserves the package namespace:

```python
import sys

import numpy as np

sys.path.insert(0, "build/SCALE_from_pyi")
import SCALE

print(SCALE.scale.scale_scalar(np.float64(3.0), np.float64(2.5)))  # 7.5
```

If you build from the leaf contract `contracts/scale.pyi` instead, the leaf
function is the entry point and the call becomes `SCALE.scale_scalar(...)`. If you
want the package-entry build to expose that top-level function, edit
`contracts/__init__.pyi` to re-export it before building.

Both calls print:

```text
7.5
```

The runtime wrapper mechanism is:

```text
Fortran sources
  -> compiler preprocessing and target-type probing
  -> Fortran parser
  -> semantic IR and readiness validation
  -> generated native bridge and Python binding
  -> native compilation and shared-library link
  -> importable Python extension
```

<!-- X2PY_C_DOCS_START
```text
Fortran sources
  -> compiler preprocessing and target-type probing
  -> Fortran parser
  -> semantic IR and readiness validation
  -> generated Fortran bind(C) bridge
  -> generated C/CPython binding and x2py runtime support
  -> native compilation and shared-library link
  -> importable Python extension
```
X2PY_C_DOCS_END -->

The inspection workflow also has four explicit stages:

```text
native source
  -> parser facts
  -> semantic IR
  -> editable .pyi
  -> readiness report
```

| Goal | Command flag |
| --- | --- |
| Inspect native declarations and diagnostics | `--parse` |
| Consume language-neutral semantic facts | `--semantics` |
| Generate an editable semantic interface | `--pyi` |
| Find missing information or unsupported contracts | `--wrap-readiness` |

`Wrappable: yes` means the Fortran semantic contract has no known readiness
blockers. Native compilation and runtime verification remain separate steps.

<!-- X2PY_C_DOCS_START
`Wrappable: yes` means the semantic contract has no known readiness blockers.
The runtime build path accepts one or more ordered Fortran sources. C parsing,
semantic IR, `.pyi`, and readiness are implemented, but wrapping user-supplied
C libraries is a later backend. The generated C code used internally by the
Fortran wrapper is not that future C-input backend.
The [generated target datatype mapping example](docs/reference/semantic-ir.md#generated-linux-x86_64-mapping-example)
shows how the GitHub Actions C and Fortran scalar types map to NumPy dtypes.
X2PY_C_DOCS_END -->

### Fortran

Recognizable Fortran files do not require an explicit language. Parse the same
checked source used in the Quick Start:

Input (`scale.f90`):

<!-- x2py-doc-source: tests/data/fortran/wrapper/scale.f90 -->
```fortran
module scale
contains
  real(8) function scale_scalar(value, factor) result(output)
    real(8), intent(in) :: value
    real(8), intent(in) :: factor
    output = value * factor
  end function scale_scalar
end module scale
```

```bash
python3 -m x2py scale.f90 --parse
```

```text
File: scale.f90
  Modules: 1
    - module scale (vars=0, uses=0)
      Procedures: 1
        - function scale_scalar(value:real(8)[0], factor:real(8)[0]) -> real(8)[0]
```

Generate its editable `.pyi` contract:

```bash
python3 -m x2py scale.f90 --pyi
```

```python
File: scale.f90
Root contract: scale/__init__.pyi
from . import scale

Module contract: scale.pyi
def scale_scalar(
    value: Ptr(Const(Float64)),
    factor: Ptr(Const(Float64))
) -> Float64: ...
```

Check semantic readiness:

```bash
python3 -m x2py scale.f90 --wrap-readiness
```

```text
File: scale.f90
  Source: fortran
  Semantic modules: scale
  Wrappable: yes
  Public functions: 1
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```

Write a draft interface, edit it when source facts are not enough, then check
the edited contract:

```bash
python3 -m x2py scale.f90 --pyi --out contracts
python3 -m x2py contracts/scale.pyi --wrap-readiness
```

Expected result: the first command writes `contracts/scale.pyi`; the
second command reports the same `Wrappable: yes` readiness result shown above.

<!-- X2PY_C_DOCS_START
### C
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
C inputs require explicit C mode. These commands parse the checked C API
fixture, inspect semantic IR, generate its `.pyi`, and check readiness:
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
Input (`tests/data/c/general/math_api.h`):
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-source: tests/data/c/general/math_api.h -->
<!-- X2PY_C_DOCS_START
```c
#ifndef X2PY_GENERAL_MATH_API_H
#define X2PY_GENERAL_MATH_API_H

double norm2(int n, const double x[static 1]);
void scale(int n, double alpha, double x[static 1]);
double dot(int n, const double *restrict x, const double *restrict y);
void fill_identity3(double a[static 3][3]);

#endif
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-test: exact -->
<!-- X2PY_C_DOCS_START
```bash
python3 -m x2py tests/data/c/general/math_api.h &#45;&#45;language c &#45;&#45;parse
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-test-output -->
<!-- X2PY_C_DOCS_START
```text
File: tests/data/c/general/math_api.h
  Language: c
  Functions: 4
  Structs: 0
  Unions: 0
  Enums: 0
  Typedefs: 0
  Variables: 0
  Macros: 0
  Includes: 0
  Diagnostics: 0
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-test: run -->
<!-- X2PY_C_DOCS_START
```bash
python3 -m x2py tests/data/c/general/math_api.h &#45;&#45;language c &#45;&#45;semantics
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-test: run -->
<!-- X2PY_C_DOCS_START
```bash
python3 -m x2py tests/data/c/general/math_api.h &#45;&#45;language c &#45;&#45;pyi
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-test: exact -->
<!-- X2PY_C_DOCS_START
```bash
python3 -m x2py tests/data/c/general/math_api.h &#45;&#45;language c &#45;&#45;wrap-readiness
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_DISABLED: x2py-doc-test-output -->
<!-- X2PY_C_DOCS_START
```text
File: tests/data/c/general/math_api.h
  Source: c
  Semantic modules: math_api
  Wrappable: yes
  Public functions: 4
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```
X2PY_C_DOCS_END -->

## Native Project Inputs

Fortran preprocessing defaults to `gfortran`. Pass the native project's include
directories, definitions, language standard, and target flags when inspecting
or building a real source tree:

```bash
python3 -m x2py scale.f90 --parse \
  --compiler gfortran \
  --std f2018
```

Expected result: the command prints the same parser report shape shown in the
Fortran inspection example, with preprocessing routed through `gfortran`.

For a real project, replace the checked input path with your source path and
add the project's include directories, definitions, and target flags.

<!-- X2PY_C_DOCS_START
The CLI uses compiler preprocessing for native source. C defaults to `cc` and
Fortran defaults to `gfortran`. Pass the native project's important compiler
and target flags:
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
```bash
python3 -m x2py include/api.h &#45;&#45;language c &#45;&#45;parse \
  &#45;&#45;compiler clang \
  -I include \
  -D API_EXPORT= \
  &#45;&#45;std c11 \
  &#45;&#45;compiler-arg=&#45;&#45;sysroot=/opt/sdk
```
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
Compiler-backed semantic, `.pyi`, and readiness stages also measure and cache
target datatype facts. C probing covers primitive ABI widths and signedness;
Fortran probing resolves kind expressions and measures intrinsic storage.
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
C projects can use a compilation database:
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
```bash
python3 -m x2py src/api.c &#45;&#45;language c &#45;&#45;semantics \
  &#45;&#45;compile-commands build/compile_commands.json
```
X2PY_C_DOCS_END -->

Use `--parse --json` for complete machine-readable parser facts and `--out`
to write selected output to a file or beside each source.

## Python API

Public entrypoints cover Fortran extension builds, parsing, semantic
conversion, `.pyi` emission, and readiness:

```python
from x2py import build_fortran_extension

result = build_fortran_extension(
    "scale.f90",
    output_name="SCALE",
    output_dir="build/SCALE",
)
print(result.module_name)
print(result.shared_library)
```

Parser and semantic entrypoints remain available independently:

<!-- X2PY_C_DOCS_START
```python
from x2py import (
    assess_semantic_wrap_readiness,
    c_file_to_semantic_modules,
    emit_module_stubs,
    parse_c_file,
)

parsed = parse_c_file("int add(int a, int b);", filename="api.h")
modules = c_file_to_semantic_modules(parsed)
stubs = emit_module_stubs(modules)
report = assess_semantic_wrap_readiness(modules, source="api.h")
```
X2PY_C_DOCS_END -->

Direct Python parser entrypoints are useful for controlled strings, focused
tests, and already-preprocessed inputs. For native projects with macros,
includes, or target flags, use the compiler-preprocessed CLI path or an
equivalent preprocessing configuration.

## Supported Scope

x2py preserves wrapper-relevant declarations, signatures, types, source
locations, include/use relationships, diagnostics, and semantic metadata.
Current support includes:

- free-form and fixed-form Fortran, procedures, modules, derived types,
  imports, arrays, and wrapper-relevant declaration attributes;
- language-neutral semantic IR, editable `.pyi` interfaces, and semantic
  readiness reports.
- compiled Python extensions from one or more ordered fixed-form or free-form
  Fortran sources, with an optional GNU Make build.

<!-- X2PY_C_DOCS_START
- compiled CPython extensions from one or more ordered fixed-form or free-form
  Fortran sources, including generated Fortran/C bridges and an optional GNU
  Make build;
- C declarations and definitions, variables, typedefs, aggregates, enums,
  pointers, arrays, function pointers, includes, and preprocessing facts;
X2PY_C_DOCS_END -->

<!-- X2PY_C_DOCS_START
Runtime wrapper generation from user C inputs is not implemented yet. It will
reuse the shared semantic contracts after the C backend and its ownership,
ABI, and runtime tests are complete.
X2PY_C_DOCS_END -->

x2py is not a full compiler frontend. It does not silently infer pointer
ownership, callback lifetime, ABI shims, or Python-visible projections.

## Documentation

- [Documentation landing](docs/index.md): draft entry point for the future
  documentation website.
- [Documentation architecture](docs/documentation-architecture.md): site-ready
  directory tree, page metadata contract, and maturity roadmap.
- [Examples cookbook](docs/examples-gallery/verified-cookbook.md): checked Fortran wrapper builds and
  calls, inspection commands, compiler recipes, and Python API examples.
- [Fortran wrapper guide](docs/user-guide/fortran-wrapper.md): generated Python behavior,
  ownership, lifetime, arrays, derived types, callbacks, build modes, and
  limitations.
- [Developer guide](docs/developer-guide/maintainer-guide.md): implementation ownership,
  parser references, testing, fixtures, and change workflows.
- [Tutorial](docs/tutorials/basic-wrapper.md): the complete supported Fortran
  workflow from source inspection to an imported extension.

<!-- X2PY_C_DOCS_START
- [Tutorial](docs/tutorials/basic-wrapper.md): the complete supported user workflow,
  Fortran extension build, semantic interface editing, readiness, and current
  C boundary.
X2PY_C_DOCS_END -->

## Development

Run the full suite from the repository root:

```bash
PYTHONPATH=. python3 -m pytest -q
```

Focused verification commands and fixture-maintenance workflows are in the
[Developer guide](docs/developer-guide/maintainer-guide.md#testing-map).
