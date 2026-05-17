# Wrapper `.pyi` Format

The `.pyi` format is a Python-valid view of the semantic IR. It is meant to be
easy to read and edit first, with extra metadata added only when the wrapper
needs information that normal Python annotations cannot express.

The default printer emits the simplest valid stub it can:

```python
def norm2(
    x: Float64[Shape(':'), ORDER_F]
) -> Float64: ...
```

Emit stubs from semantic IR with `emit_module`:

```python
from semantics.pyi_printer import emit_module

pyi = emit_module(module)
```

## Parameters

Normal parameters are Fortran `intent(in)` values:

```python
def axpy(
    a: Float64,
    x: Float64[Shape(':'), ORDER_F],
    y: Float64[Shape(':'), ORDER_F]
) -> Float64[Shape(':'), ORDER_F]: ...
```

Optional Fortran arguments use the normal stub default form:

```python
def solve(
    a: Float64[Shape(':', ':'), ORDER_F],
    tol: Float64 = ...
) -> None: ...
```

## Return Values

Plain return annotations are preferred when the returned value does not need a
Fortran name:

```python
def value(x: Float64) -> Float64: ...
```

A subroutine with one `intent(out)` result is also printed as a plain return by
default:

```python
def make_vector(n: Int32) -> Float64[Shape('n'), ORDER_F]: ...
```

`Returns["name", Type]` is used only when the return is also an input argument,
which marks the argument as `intent(inout)`:

```python
def scale(
    x: Float64[Shape(':'), ORDER_F]
) -> Returns["x", Float64[Shape(':'), ORDER_F]]: ...
```

If a name appears both as an argument and in `Returns[...]`, the parser treats
that argument as `intent(inout)`.

Unnamed `intent(out)` values use normal return annotations. Multiple outputs
use a tuple:

```python
def split(
    x: Float64
) -> tuple[Float64, Float64]: ...
```

When the stub must preserve how Python values map back to native Fortran
arguments, use a native call projection.

## Native Calls

`@native_call([...])` records the exact native Fortran argument vector from
left to right when the Python signature is not the same as the Fortran call
signature. Identity mappings are omitted by skipping the decorator entirely
when the Python signature already describes the native layout.

Each entry describes the value inserted into the native call.

Core entries:

- `Arg(i)` inserts Python argument position `i`.
- `Return(i)` inserts Python return value position `i`; this is used for
  projected `intent(out)` values.

For an `intent(out)` argument projected as a Python return:

```python
@native_call([Arg(0), Return(0)])
def make_vector(n: Int32) -> Float64[Shape("n"), ORDER_F]: ...
```

This means native argument `0` is Python argument `0`, and native argument `1`
is Python return value `0`.

In Fortran terms, this describes a native call like:

```text
make_vector(n, x)
```

with a Python API:

```python
make_vector(n) -> x
```

For mixed input and output layouts:

```python
@native_call([Arg(0), Return(0), Arg(1)])
def solve(a: Matrix, b: Vector) -> Vector: ...
```

This describes a native call like:

```text
solve(a, x, b)
```

where `x` is returned to Python.

For an `intent(inout)` argument with the same name in the argument and return
projection, no explicit decorator is required:

```python
def scale(
    x: Float64[Shape(":"), ORDER_F]
) -> Returns["x", Float64[Shape(":"), ORDER_F]]: ...
```

For argument reordering:

```python
@native_call([Arg(1), Arg(0)])
def f(b: Float64, a: Int32) -> None: ...
```

This describes a native call `f(a, b)` while exposing the Python signature
`f(b, a)`.

Hidden or derived native arguments can also be represented. These values are
not visible in the Python signature, but are needed to reconstruct the native
call.

Use `Const(value)` to insert a fixed native value:

```python
@native_call([Arg(0), Const(1)])
def step(x: Float64) -> None: ...
```

This describes a native call like:

```text
step(x, mode=1)
```

Use `Len(value)` for hidden string length arguments:

```python
@native_call([Arg(0), Len(Arg(0))])
def print_name(name: String) -> None: ...
```

This describes:

```text
print_name(name, len(name))
```

Use `Shape(value, dim)` for hidden array extents. Dimensions are zero-based in
the projection:

```python
@native_call([
    Arg(0),
    Shape(Arg(0), 0),
])
def sum_vector(
    x: Float64[Shape("n"), ORDER_F]
) -> Float64: ...
```

This describes:

```text
sum_vector(x, n)
```

Use `IsPresent(value)` when a native call receives an explicit optional
presence flag:

```python
@native_call([
    Arg(0),
    Arg(1),
    IsPresent(Arg(1)),
])
def solve(
    a: Matrix,
    b: Vector | None = None,
) -> None: ...
```

Calling `solve(a)` describes a native call like:

```text
solve(a, NULL, .false.)
```

Calling `solve(a, b)` describes:

```text
solve(a, b, .true.)
```

Use `Work(name)` for wrapper-generated temporaries or workspace values:

```python
@native_call([
    Arg(0),
    Work("tmp"),
])
def transform(x: Float64[Shape("n"), ORDER_F]) -> None: ...
```

This records that the wrapper allocates `tmp` internally and passes it to the
native call. This is useful for BLAS/LAPACK workspace arrays and other
compiler- or wrapper-generated temporaries.

Use `@native_call` only for non-obvious projections:

- projected `intent(out)` returns
- argument reordering
- inserted hidden metadata
- generated workspace arguments
- wrapper-generated constants
- mixed input/output layouts

The mental model is:

```text
Construct the native Fortran call using this exact argument vector.
```

## Type Constraints

Array and storage information is represented as type constraints:

```python
Float64[Shape(':', ':'), ORDER_F]
Int32[Shape('1:n'), Allocatable]
```

Common constraints include:

- `Shape(...)` for rank and bounds.
- `ORDER_F` for Fortran-contiguous arrays.
- `ORDER_C` for C-contiguous arrays.
- `Allocatable` for allocatable values.
- `Pointer` for pointer values.

## Visibility

Private procedures and classes use decorators:

```python
@private
def hidden(x: Int32) -> None: ...
```

Private module variables and fields use `private[...]`:

```python
hidden_scale: private[Float64]
```

## Imports

Plain module imports are emitted for bare Fortran `use` statements:

```python
import iso_c_binding
```

For explicit `use ... only:` lists, the printer emits Python `from` imports so
the imported symbols remain visible in the stub:

```python
from iso_c_binding import c_int, c_double
```

For renamed Fortran imports, both sides are preserved with Python alias syntax:

```fortran
use list_input, delete_input => delete_input_list
```

```python
from list_input import delete_input_list as delete_input
```

The `.pyi` parser accepts both `import module` and
`from module import source as target`. In semantic IR, `source` is the
provider-side name and `target` is the local alias; when there is no alias,
`target` is `None`.

## Fortran Names That Are Not Python Identifiers

If a parameter name is not usable as Python syntax, the printer uses a safe
Python name and preserves the original name with `Annotated[..., Name(...)]`:

```python
def call(
    class_: Annotated[Int32, Name("class")]
) -> None: ...
```

Module variables and derived-type fields can use `var[...]`:

```python
var["operator-name"]: Float64
```

Both forms are valid Python syntax and are understood by the `.pyi` parser.

## Loading Edited Stubs

Use these entrypoints to recover semantic IR from a stub:

```python
from semantics.pyi_parser import convert_pyi_to_ir, load_pyi_file, parse_pyi_text

module = load_pyi_file("mymodule.pyi")
module = parse_pyi_text(source, module_name="mymodule")
module = convert_pyi_to_ir(source, module_name="mymodule")
```

To compare an edited `.pyi` file with an existing semantic IR module:

```python
from semantics.pyi_parser import load_pyi_file

edited_ir = load_pyi_file("mymodule.pyi", module_name=existing_ir.name)
assert edited_ir == existing_ir
```

Editable stubs do not have to preserve every original Fortran detail. A plain
return type means a normal wrapper return. Use `Returns["name", Type]` only when
the returned value is also an input argument and must be treated as `inout`.

Function and method argument names are placeholders during IR comparison. For
example, `def f(a: Int32) -> None: ...` and
`def f(b: Int32) -> None: ...` compare equal as functions. The same positional
renaming is applied inside shape expressions such as `Shape('1:n')`. Names
outside function and method argument lists, including module variables and class
fields, remain significant.
