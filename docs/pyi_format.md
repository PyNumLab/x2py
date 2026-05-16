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
arguments, use a call map.

## Call Maps

`@call_map(...)` records the native call projection when the Python signature is
not the same as the Fortran call signature. Identity mappings are omitted.

For an `intent(out)` argument projected as a Python return:

```python
@call_map(NativeArg("x", 1, source="return", position=0, intent="out"))
def make_vector(n: Int32) -> Float64[Shape("n"), ORDER_F]: ...
```

This means native argument `x` is at Fortran position `1`, but Python receives it
as return value `0`.

For an `intent(inout)` argument, the value is both a Python argument and a Python
return:

```python
@call_map(NativeArg("x", 0, source="arg", position=0, result=0, intent="inout"))
def scale(
    x: Float64[Shape(":"), ORDER_F]
) -> Returns["x", Float64[Shape(":"), ORDER_F]]: ...
```

For argument reordering:

```python
@call_map(NativeArg("a", 0, source="arg", position=1), NativeArg("b", 1, source="arg", position=0))
def f(b: Float64, a: Int32) -> None: ...
```

The fields are `native_name`, `native_position`, `source`, Python `position`,
optional `result`, and `intent`.

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
