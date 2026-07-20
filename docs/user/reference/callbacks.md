---
title: Callbacks Reference
audience: advanced users, developers
prerequisites: semantic .pyi format, data types
related: semantic-pyi-format.md, ../guide/callbacks.md, generated-functions.md
status: maintained
publication: draft
---

# Callbacks Reference

Callback contracts are native-facing. A normal generated function signature
describes how Python calls the wrapper; a `@prototype` declaration describes
the native callback signature invoked through the generated adapter.

The callable argument list therefore preserves callback argument order,
value/reference calling, rank, shape, character length, and result shape. It
does not repeat native callback direction.

## Immediate Callback Scope

Supported callbacks are call-scoped. The generated wrapper keeps the Python
callable alive only for the active wrapped call, installs a callback context,
passes a generated Fortran adapter to the native routine, and clears the context
when the wrapped call returns.

Policy completion records the callback ABI, primitive-scalar value projection,
reference writeback for non-scalar storage, context lifecycle, entering-thread
rule, GIL actions, and fatal action before wrapper planning. Direct
wrapper-plan generation then emits one typed Fortran adapter and one native
trampoline per callback site. Neither backend infers callback transport, shape,
or ownership from generated locals.

Native code must not store the callback or call it later. Stored procedure
pointers, optional dummy procedures, asynchronous callbacks, and cross-thread
callback invocation are unsupported.

## Prototype Argument Forms

Declare a named prototype once and use its name as the callback argument type:

```python
from x2py.contracts import Float64, Int32, prototype

@prototype
def transform(count: Int32, values: Float64[count]) -> Float64[count]: ...

def apply_transform(callback: transform, ...) -> ...: ...
```

Prototype arguments use ordinary semantic types. Reference passing is the
default; `Value(T)` is the only callback argument ABI override.

| Spelling | Fortran callback dummy | Python callback object |
| --- | --- | --- |
| `Int32` | scalar reference dummy | owned `np.int32` scalar value |
| `Value(Float64)` | scalar `value` dummy | owned `np.float64` scalar value |
| `Float64[n]` | array reference dummy | writable NumPy array view |
| `point_t` | derived reference dummy | generated wrapper object |
| `Value(point_t)` | derived `value` dummy | wrapper over the call-local value copy |

`Addr(...)` is unnecessary inside callback signatures because reference is the
default. `Value(...)` is required only when the native callback dummy has the
Fortran `value` attribute.

Prototypes are semantic declarations and never become Python runtime exports.
A prototype defined in another contract module is referenced through a normal
relative semantic import. That import supplies the signature identity and
complete transport contract. Post-IR policy decides whether the backend may use
an implicit external declaration or must import and use the named native
prototype. The explicit path obtains native direction from that real interface;
the semantic prototype does not repeat it.

## Character Arguments

Fixed-length character reference dummies use their ordinary type spelling:

```python
from x2py.contracts import String, prototype

@prototype
def update_label(label: String[8]) -> None: ...
```

The Python callback receives a NumPy scalar bytes array, such as `np.ndarray`
with shape `()` and dtype `S8`, and writes through that storage:

```python
def update(label):
    label[...] = b"done    "
```

Generated `.pyi` contracts emit `String[n]` regardless of native callback
direction. Callback context makes reference character storage mutable without
adding direction metadata to the annotation.

## Results And Copy-Back

Scalar callback results are converted from the Python return value. Primitive
scalar arguments are always owned NumPy scalar values and never scalar-storage arrays, so
scalar reference writeback is unsupported. Array, derived, and
character-storage reference arguments are copied back before the Fortran
adapter returns to native code.

Callback exceptions, invalid callback return conversion, and unsupported
cross-thread callback execution are fatal at the callback boundary: x2py prints
the Python traceback and aborts the host process.
