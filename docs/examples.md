# Verified Examples Cookbook

This cookbook collects supported x2py commands and Python API patterns. The
repository fixture commands and inline Python snippets are covered by the
current test suite or can be run directly from the repository root.

Start with the [tutorial](tutorial.md) if this is your first x2py workflow.
Use the [semantic `.pyi` format](pyi_format.md) for the full accepted `.pyi`
contract and the [semantic IR reference](semantics.md) for datatype details.

## Fixture Inputs

The most useful small, checked examples are:

| Purpose | Repository fixture |
| --- | --- |
| Basic Fortran procedure | `tests/data/fortran/general/basic_subroutine.f90` |
| Rich Fortran module, types, arrays, and visibility | `tests/data/fortran/general/modern_pyi_example.f90` |
| Basic C functions, pointers, and arrays | `tests/data/c/general/math_api.h` |
| Generated Fortran semantic interface | `tests/pyi/fixtures/general/modern_pyi_example.pyi` |
| Generated C semantic interface | `tests/pyi/fixtures/c/general/math_api.pyi` |

The core native inputs are included here so the command examples are
self-contained.

### Basic Fortran Input

<!-- x2py-doc-source: tests/data/fortran/general/basic_subroutine.f90 -->
```fortran
module m1
contains
subroutine add1(n, x)
  integer, intent(in) :: n
  real(kind=8), intent(inout), dimension(n) :: x
end subroutine add1
end module m1
```

### Basic C Input

<!-- x2py-doc-source: tests/data/c/general/math_api.h -->
```c
#ifndef X2PY_GENERAL_MATH_API_H
#define X2PY_GENERAL_MATH_API_H

double norm2(int n, const double x[static 1]);
void scale(int n, double alpha, double x[static 1]);
double dot(int n, const double *restrict x, const double *restrict y);
void fill_identity3(double a[static 3][3]);

#endif
```

### Rich Fortran Input

<details>
<summary>Show <code>tests/data/fortran/general/modern_pyi_example.f90</code></summary>

<!-- x2py-doc-source: tests/data/fortran/general/modern_pyi_example.f90 -->
```fortran
module modern_math_physics
  implicit none
  private
  public :: particle, vector3, counter, init_particle, kinetic_energy, scale_vector, dot3, fill_identity3, normalize_particle

  integer :: counter
  real(8) :: hidden_scale

  type :: particle
     integer :: id
     real(8) :: mass
     real(8), dimension(3) :: position
  end type particle

  type :: vector3
     real(8), dimension(3) :: values
  end type vector3

  type :: hidden_state
     integer :: code
  end type hidden_state

contains

  subroutine init_particle(p, pid, mass, x, y, z)
    type(particle), intent(out) :: p
    integer, intent(in) :: pid
    real(8), intent(in) :: mass, x, y, z
    p%id = pid
    p%mass = mass
    p%position = [x, y, z]
  end subroutine init_particle

  function kinetic_energy(p, vx, vy, vz) result(e)
    type(particle), intent(in) :: p
    real(8), intent(in) :: vx, vy, vz
    real(8) :: e
    e = 0.5d0 * p%mass * (vx*vx + vy*vy + vz*vz)
  end function kinetic_energy

  subroutine scale_vector(v, alpha)
    real(8), dimension(:), intent(inout) :: v
    real(8), intent(in) :: alpha
    v = alpha * v
  end subroutine scale_vector

  function dot3(a, b) result(s)
    real(8), dimension(3), intent(in) :: a, b
    real(8) :: s
    s = a(1)*b(1) + a(2)*b(2) + a(3)*b(3)
  end function dot3

  subroutine fill_identity3(a)
    real(8), dimension(3,3), intent(out) :: a
    a = 0.0d0
    a(1,1) = 1.0d0
    a(2,2) = 1.0d0
    a(3,3) = 1.0d0
  end subroutine fill_identity3

  subroutine normalize_particle(p)
    type(particle), intent(inout) :: p
    real(8) :: n
    n = sqrt(dot3(p%position, p%position))
    if (n > 0.0d0) p%position = p%position / n
  end subroutine normalize_particle

  subroutine hidden_proc(x)
    integer, intent(in) :: x
  end subroutine hidden_proc

end module modern_math_physics
```

</details>

## CLI Stage Examples

### Parse

Compact Fortran report:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Compact C report:

```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --parse
```

Full parser payload:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse --json
python3 -m x2py tests/data/c/general/math_api.h --language c --parse --json
```

### Semantic IR

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --semantics
python3 -m x2py tests/data/c/general/math_api.h --language c --semantics
```

The semantic payload includes `semantic_modules` and generated `pyi` text.

### `.pyi` Emission

Print:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
python3 -m x2py tests/data/c/general/math_api.h --language c --pyi
```

Write an explicit interface file:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --pyi --out /tmp/basic_subroutine.pyi
```

Write one interface beside each input:

```bash
python3 -m x2py path/to/fortran_sources --language fortran --pyi --out
```

### Readiness

Human-readable readiness:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
python3 -m x2py tests/data/c/general/math_api.h --language c --wrap-readiness
python3 -m x2py tests/pyi/fixtures/general/basic_subroutine.pyi --wrap-readiness
```

Machine-readable readiness:

```bash
python3 -m x2py tests/pyi/fixtures/general/basic_subroutine.pyi \
  --wrap-readiness --json
```

Read all `.pyi` files beneath a directory as one edited interface set.
Directories always require an explicit frontend, including `.pyi`-only
directories:

```bash
python3 -m x2py path/to/interfaces --language fortran --wrap-readiness
```

### Combine Stages

Print parser facts followed by readiness:

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --parse --wrap-readiness
```

Print a generated `.pyi` followed by readiness:

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/c/general/math_api.h \
  --language c --pyi --wrap-readiness
```

Attach readiness to semantic output:

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --semantics --wrap-readiness
```

## Control Human-Readable Parse Output

Fortran variable sections are compact by default. Expand them with
`--show-vars`:

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/fortran/general/modern_pyi_example.f90 \
  --parse --show-vars
```

Limit every repeated section:

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/modern_pyi_example.f90 \
  --parse --show-vars --print-limit 1
```

This reports totals while showing one item from each repeated section:

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/modern_pyi_example.f90
  Modules: 1
    - module modern_math_physics (vars=2, uses=0)
      Variables: 2
        - counter:integer[0]
        ... 1 more variables
      Derived types: 3
        - type particle (fields=3, methods=0)
          Fields: 3
            - id:integer[0]
            ... 2 more fields
        ... 2 more derived types
      Procedures: 7
        - subroutine init_particle(p:type(particle)[0], pid:integer[0], mass:real(8)[0], x:real(8)[0], y:real(8)[0], z:real(8)[0])
        ... 6 more procedures
```

`--show-vars` is Fortran-only. `--print-limit` works with human-readable C and
Fortran parse reports.

## Input And Project Examples

### Explicit Files

```bash
python3 -m x2py src/types.f90 src/api.f90 --language fortran --parse
python3 -m x2py include/types.h include/api.h --language c --parse
```

### Directories

Directories require an explicit frontend:

```bash
python3 -m x2py src/fortran --language fortran --parse --print-limit 20
python3 -m x2py src/c --language c --parse --print-limit 20
```

Fortran directory discovery is recursive for recognized Fortran suffixes. C
directory discovery includes recognized C source, header, and preprocessed
input suffixes.

### Unknown Suffixes

Use an explicit frontend when the source suffix does not identify the
language:

```bash
python3 -m x2py generated/api.source --language c --parse
python3 -m x2py generated/api.source --language fortran --parse
```

## Compiler Preprocessing

The shared CLI preprocesses source before parsing. This is the supported path
for macros, conditional compilation, target flags, and native includes.

### C Compiler And Flags

```bash
python3 -m x2py include/api.h --language c --parse \
  --compiler clang \
  -I include \
  -D API_EXPORT= \
  -U LEGACY_API \
  --std c11 \
  --compiler-arg=--sysroot=/opt/sdk
```

### C Compilation Database

```bash
python3 -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json
```

Extra wrapper-specific flags can be added to the selected database entry:

```bash
python3 -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json \
  --compiler-arg=-DX2PY_SCAN=1
```

### Fortran Compiler And Flags

```bash
python3 -m x2py src/api.f90 --language fortran --pyi \
  --compiler gfortran \
  -I include \
  -D USE_MPI \
  --std f2008 \
  --compiler-arg=-fdefault-real-8
```

### Custom Command Template

Use a command template for an unsupported compiler family:

```bash
python3 -m x2py include/api.h --language c --parse \
  --preprocessor-adapter command-template \
  --preprocess-template \
  'cc -E {include_dirs} {defines} {undefs} {standard} {compiler_args} {source}'
```

Supported placeholders are `{source}`, `{include_dirs}`, `{defines}`,
`{undefs}`, `{standard}`, and `{compiler_args}`.

### Include Exposure

For C projects, reachable project includes are public by default and system
headers are private. Narrow or override that wrapper-facing surface:

```bash
python3 -m x2py include/api.h --language c --pyi \
  --include-exposure roots-only \
  --public-include 'include/public/*' \
  --private-include 'vendor/*'
```

Private declarations remain available for internal type resolution.

## Output File Examples

Write one parser payload to an explicit path:

```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 \
  --parse --json --out /tmp/basic_subroutine.json
```

Write one parser payload beside each source:

```bash
python3 -m x2py path/to/fortran_sources --language fortran --parse --out
```

Write an explicit `.pyi`:

```bash
python3 -m x2py tests/data/c/general/math_api.h \
  --language c --pyi --out /tmp/math_api.pyi
```

`--out` requires a selected stage. `--json` and `--pyi` cannot both be used
with `--out`.

## Diagnostic Examples

Parser and preprocessing failures are rendered without a Python traceback by
default. Disable ANSI color for logs:

```bash
python3 -m x2py path/to/source.f90 --parse --no-color
```

Re-raise an error with a traceback while debugging:

```bash
python3 -m x2py path/to/source.f90 --parse --debug
```

Stable diagnostic categories are listed in
[diagnostic_codes.md](diagnostic_codes.md).

## Python API Examples

Direct parser APIs accept controlled source strings and paths. They do not run
the shared CLI compiler preprocessing pipeline.

### Parse Inline Fortran

<!-- x2py-doc-test: exact -->
```python
from x2py import parse_fortran_file

parsed = parse_fortran_file(
    "subroutine ping(n)\n"
    "  integer, intent(in) :: n\n"
    "end subroutine ping\n",
    filename="inline.f90",
)

print(parsed.procedures[0].name)  # ping
```

Output:

<!-- x2py-doc-test-output -->
```text
ping
```

### Parse Inline C

<!-- x2py-doc-test: exact -->
```python
from x2py import parse_c_file

parsed = parse_c_file("int add(int a, int b);", filename="inline.h")

print([function.name for function in parsed.functions])  # ['add']
```

Output:

<!-- x2py-doc-test-output -->
```text
['add']
```

### Parse An In-Memory C Project

<!-- x2py-doc-test: exact -->
```python
from x2py import parse_c_project

project = parse_c_project(
    {
        "types.h": "typedef int api_int;",
        "api.h": '#include "types.h"\napi_int answer(void);',
    }
)

print(sorted(project.files))      # ['api.h', 'types.h']
print(sorted(project.functions))  # ['answer']
```

Output:

<!-- x2py-doc-test-output -->
```text
['api.h', 'types.h']
['answer']
```

### Parse An In-Memory Fortran Project

<!-- x2py-doc-test: exact -->
```python
from x2py import parse_fortran_project

project = parse_fortran_project(
    {
        "types.f90": "module types\nend module types\n",
        "api.f90": (
            "module api\n"
            "  use types\n"
            "end module api\n"
        ),
    }
)

print(sorted(project.modules))  # ['api', 'types']
```

Output:

<!-- x2py-doc-test-output -->
```text
['api', 'types']
```

### Convert C To Semantic IR, Emit `.pyi`, And Check Readiness

<!-- x2py-doc-test: exact -->
```python
from x2py import (
    assess_semantic_wrap_readiness,
    c_file_to_semantic_modules,
    emit_module_stubs,
    parse_c_file,
)

parsed = parse_c_file("int add(int a, int b);", filename="inline.h")
modules = c_file_to_semantic_modules(parsed)

print(emit_module_stubs(modules)["inline"])
print(assess_semantic_wrap_readiness(modules)["wrappable"])
```

Output:

<!-- x2py-doc-test-output -->
```text
def add(
    a: Int,
    b: Int
) -> Int: ...
True
```

### Check An Edited `.pyi` String

<!-- x2py-doc-test: exact -->
```python
from x2py import assess_semantic_wrap_readiness, parse_pyi_text

module = parse_pyi_text(
    """
from typing import Callable

def integrate(
    objective: Callable[[Float64], Float64],
    x0: Float64
) -> Float64: ...
""",
    module_name="solver",
)

report = assess_semantic_wrap_readiness(module, source="solver.pyi")
print(report["wrappable"])  # True
```

Output:

<!-- x2py-doc-test-output -->
```text
True
```

### Check `.pyi` Files Or Directories

```python
from x2py import assess_pyi_wrap_readiness, load_pyi_modules

modules = load_pyi_modules("path/to/interfaces")
report = assess_pyi_wrap_readiness("path/to/interfaces")

print([module.name for module in modules])
print(report["wrappable"])
```

## Supported `.pyi` Examples

These examples show semantic syntax accepted by the current loader. They are
contracts and metadata; they are not executable Python wrapper
implementations.

### Scalars, References, And Arrays

```python
def direct(value: Float64) -> Float64: ...
def inspect(value: Ptr(Const(Int32))) -> None: ...
def update(value: Ptr(Float64)) -> None: ...
def scale(n: Int32, values: Float64[n]) -> None: ...
def dot3(a: Const(Float64[3]), b: Const(Float64[3])) -> Float64: ...
```

### Constants, Visibility, And Classes

```python
from typing import Final

nmax: Final[Int32] = 32
hidden_scale: private[Float64]

class particle:
    id: Int32
    mass: Float64
    position: Float64[3]

@private
def helper(x: Ptr(Const(Int32))) -> None: ...
```

### Opaque Types

```python
class context(Opaque):
    pass

def context_create() -> Ptr(context): ...
def context_destroy(ctx: Ptr(context)) -> None: ...
```

### Intent And Array Metadata

```python
def fill(
    values: Annotated[Float64[:], Intent("out")]
) -> None: ...

def fill_matrix(
    values: Annotated[Float64[3, 3], ORDER_F, Intent("out")]
) -> None: ...
```

### Complete Callback Signature

```python
from typing import Callable

def integrate(
    objective: Callable[[Float64], Float64],
    x0: Float64
) -> Float64: ...
```

`Callable[..., Float64]` is accepted syntax but remains semantically
incomplete because the callback argument types are unknown.

### Preserved Projection Metadata

```python
@native_call([Arg(0), Arg(1), Return(0)])
def add(a: Float64, b: Float64) -> Float64: ...
```

The current loader and printer preserve supported `@native_call` metadata.
x2py does not currently execute the projection or generate runtime wrapper
code. Use the [semantic `.pyi` format](pyi_format.md) for the accepted projection
entries and limitations.

## Readiness Blocker Examples

### Missing Callback Signature

```python
def integrate(objective: Procedure, x0: Float64) -> Float64: ...
```

This is blocked because callback argument order, argument types, and return
type are incomplete. Replacing `Procedure` with a complete supported
`Callable[[...], Return]` supplies the semantic signature.

### Missing Compile-Time Constant

```python
from typing import Final

n: Final[Int32]

def fill(values: Float64[n]) -> None: ...
```

This is blocked because `n` has no literal value. Supplying a value makes the
shape resolvable:

```python
n: Final[Int32] = 16
```

### Ambiguous C Pointer Policy

```c
int read_values(double *values, size_t n);
```

The parser can preserve this signature, but semantic readiness reports
`c_pointer_ownership_ambiguous`: the declaration alone does not prove whether
the pointer is borrowed, owned, input, output, or in-place storage. Current
x2py does not invent that policy.

### Unsupported C Variadic Function

```c
int log_msg(const char *fmt, ...);
```

Semantic readiness reports `c_variadic_function`. Current x2py does not
generate a runtime wrapper for the variadic contract.

## More References

- [Tutorial](tutorial.md)
- [Semantic `.pyi` format](pyi_format.md)
- [Semantic IR reference](semantics.md)
- [Diagnostic code registry](diagnostic_codes.md)
- [Developer guide](developper_guide.md): implementation and parser references
