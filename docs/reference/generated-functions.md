---
title: Generated Functions Reference
audience: users
prerequisites: wrapping functions, wrapping subroutines
related: generated-modules.md, generated-classes.md, semantic-pyi-format.md, ../user-guide/wrapping-functions.md
status: maintained
---

# Generated Functions Reference

x2py exposes supported Fortran functions, subroutines, and type-bound
procedures as Python callables. The generated semantic `.pyi` contract is the
authoritative signature: it records the Python-visible argument list, return
shape, native argument projection, dtype, rank, mutability, and visibility.

Use [Wrapping Functions](../user-guide/wrapping-functions.md) and
[Wrapping Subroutines](../user-guide/wrapping-subroutines.md) for source-first
workflows. This page is the compact reference for the callable surface those
workflows produce.

## Placement And Signature Shape

| Native declaration | Python placement | Contract marker |
| --- | --- | --- |
| Standalone external procedure | Generated extension root | `@external` |
| Procedure contained in a Fortran module | Generated child module | no `@external` |
| Type-bound procedure | Generated class method | `Pass()` in native projection when needed |
| Public generic interface | One Python callable with generated overload dispatch | `@overload("specific_name")` |
| Private or removed declaration | Not exported | `@private`, `private[...]`, or omitted |

The visible Python signature follows the semantic `.pyi`, not the raw native
dummy list. Ordinary scalar inputs are value-shaped, such as `Const(Int32)` or
`Const(Float64)`, even when the native call passes temporary reference-backed
storage. Arrays, strings, derived objects, optional values, and callbacks keep
their explicit semantic annotations.

## Return Projection

A Fortran function's direct result is the first Python return value. Native
output or replacement arguments follow in native argument order. A subroutine
with no visible outputs returns `None`.

When the Python-visible signature hides or reorders native arguments, the
contract uses `@native_call(...)` and `Returns[...]` to preserve the native call
shape:

```python
@native_call([Ref(Arg(0)), Arg(1)])
def fill_vector(
    n: Const(Int32),
    values: Float64[n]
) -> Returns["values", Float64[n]]: ...

@native_call([Ref(Arg(0)), Ref(Arg(1)), Arg(2), Arg(3)])
def shift_matrix(
    n: Const(Int32),
    m: Const(Int32),
    values: Annotated[Const(Float64[n, m]), ORDER_F],
    out: Annotated[Float64[n, m], ORDER_F]
) -> Returns["out", Annotated[Float64[n, m], ORDER_F]]: ...
```

`Returns["name", Type]` names a projected Python return. `tuple[...]` is used
when a callable has more than one Python return value. `@native_call` entries
such as `Arg(0)`, `Ref(Arg(0))`, `Return("status", 0)`, `Len(...)`,
`IsPresent(...)`, and `Work(...)` are described in
[Semantic `.pyi` Format](semantic-pyi-format.md#misuse-diagnostics-and-risk).

Edited native-order contracts may omit `@native_call` only when every native
dummy argument remains visible in native order. In that lower-level form,
caller-supplied output storage is part of the visible Python call.

## Validation And Exceptions

Generated callables validate the pieces needed for a safe native call before
or during dispatch:

- dtype, scalar width, rank, shape, order, stride, and writeability;
- required versus optional arguments, including `None` for supported optional
  forms;
- generated class instance type and ownership for derived-type arguments;
- callback arity and immediate-call lifetime;
- overload distinguishability; and
- readiness blockers for unsupported ownership, pointer, allocatable, or
  projection policies.

Argument errors are reported as Python exceptions instead of silently coercing
to a different contract. Native failures projected through documented status or
message outputs follow the behavior described in
[Error Handling](../user-guide/error-handling.md).

## Overloads

x2py overload metadata is not `typing.overload`. The generated semantic
contract keeps one public name and links each public implementation back to a
specific native procedure:

```python
@overload("convert_integer")
@native_call([Ref(Arg(0))])
def convert(
    value: Const(Int32)
) -> Int32: ...

@overload("convert_real")
@native_call([Ref(Arg(0))])
def convert(
    value: Const(Float64)
) -> Float64: ...
```

Dispatch is exact. Indistinguishable overloads block generation instead of
choosing by declaration order.

## Evidence And Maintenance

Function and subroutine call surfaces are covered by
[`test_native_call_examples.py`](../../tests/wrapper/fortran/function_calls/test_native_call_examples.py),
[`test_output_arguments.py`](../../tests/wrapper/fortran/function_calls/test_output_arguments.py),
[`test_optional_arguments.py`](../../tests/wrapper/fortran/function_calls/test_optional_arguments.py), and
[`test_generic_interfaces.py`](../../tests/wrapper/fortran/naming/test_generic_interfaces.py).

When a callable signature rule changes, update this page together with the
semantic `.pyi` reference, generated contract fixtures under
`tests/wrapper/fortran/*/contracts/`, and the relevant user-guide workflow.
