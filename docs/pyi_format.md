# Wrapper `.pyi` Format

The `.pyi` format is a Python-valid view of the semantic IR. It is meant to be
easy to read and edit first, with extra metadata added only when the wrapper
needs information that normal Python annotations cannot express.

The default printer emits the simplest valid stub it can:

```python
def norm2(
    x: Float64[Shape(':'), FortranContiguous]
) -> Float64: ...
```

Use round-trip mode when the generated file must parse back to the exact same
IR:

```python
from semantics.pyi_printer import emit_module

pyi = emit_module(module, roundtrip=True)
```

Round-trip mode keeps output names even when a beginner-facing stub could omit
them.

## Parameters

Normal parameters are Fortran `intent(in)` values:

```python
def axpy(
    a: Float64,
    x: Float64[Shape(':'), FortranContiguous],
    y: Float64[Shape(':'), FortranContiguous]
) -> Returns["y", Float64[Shape(':'), FortranContiguous]]: ...
```

Optional Fortran arguments use the normal stub default form:

```python
def solve(
    a: Float64[Shape(':', ':'), FortranContiguous],
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
def make_vector(n: Int32) -> Float64[Shape('n'), FortranContiguous]: ...
```

`Returns["name", Type]` is used when the name carries wrapper semantics:

```python
def scale(
    x: Float64[Shape(':'), FortranContiguous]
) -> Returns["x", Float64[Shape(':'), FortranContiguous]]: ...
```

If a name appears both as an argument and in `Returns[...]`, the parser treats
that argument as `intent(inout)`.

If a `Returns[...]` name is not an argument, the parser treats it as
`intent(out)`:

```python
def split(
    x: Float64
) -> tuple[Returns["lo", Float64], Returns["hi", Float64]]: ...
```

Round-trip mode uses this named form for all Fortran output arguments so
`load_pyi_file(path) == original_ir` can hold.

## Type Constraints

Array and storage information is represented as type constraints:

```python
Float64[Shape(':', ':'), FortranContiguous]
Int32[Shape('1:n'), Allocatable]
```

Common constraints include:

- `Shape(...)` for rank and bounds.
- `FortranContiguous` for Fortran-layout arrays.
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
from semantics.pyi_parser import load_pyi_file, parse_pyi_text

module = load_pyi_file("mymodule.pyi")
module = parse_pyi_text(source, module_name="mymodule")
```

Editable stubs do not have to preserve every original Fortran detail. A plain
return type means a normal wrapper return. Use `Returns["name", Type]` when the
wrapper needs to know the Fortran output name or when exact IR round-tripping is
required.
