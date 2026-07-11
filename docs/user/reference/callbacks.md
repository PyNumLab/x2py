---
title: Callbacks Reference
audience: advanced users, developers
prerequisites: semantic .pyi format, data types
related: semantic-pyi-format.md, ../guide/callbacks.md, generated-functions.md
status: maintained
---

# Callbacks Reference

Callback contracts are Fortran-facing. A normal generated function signature
describes how Python calls the wrapper; a `Callable[[...], T]` argument
describes the callback procedure signature that Fortran calls through the
generated adapter.

The callable argument list therefore preserves callback argument order,
value/reference calling, explicit or missing Fortran dummy `intent`, rank,
shape, character length, and result shape.

## Immediate Callback Scope

Supported callbacks are call-scoped. The generated wrapper keeps the Python
callable alive only for the active wrapped call, installs a callback context,
passes a generated Fortran adapter to the native routine, and clears the context
when the wrapped call returns.

Native code must not store the callback or call it later. Stored procedure
pointers, optional dummy procedures, asynchronous callbacks, and cross-thread
callback invocation are unsupported.

## Callable Argument Forms

The callback wrappers are valid only inside `Callable[[...], T]` argument
lists.

| Spelling | Fortran callback dummy | Python callback object |
| --- | --- | --- |
| `Int32` | scalar `value` dummy | Python scalar |
| `In(Float64)` | scalar reference, `intent(in)` | Python scalar |
| `PassByRef(Float64)` | scalar reference, missing intent | rank-zero NumPy scalar storage |
| `Out(Float64)` | scalar reference, `intent(out)` | rank-zero NumPy scalar storage |
| `InOut(Float64)` | scalar reference, `intent(inout)` | rank-zero NumPy scalar storage |
| `Float64[n]` | array reference, missing intent | NumPy array view |
| `In(Float64[n])` | array reference, `intent(in)` | read-only NumPy array view |
| `Out(Float64[n])` | array reference, `intent(out)` | writable NumPy array view |
| `InOut(Float64[n])` | array reference, `intent(inout)` | writable NumPy array view |
| `In(point_t)` | derived reference, `intent(in)` | generated wrapper object |

`Addr(...)` is invalid inside Fortran callback `Callable` signatures. Fortran
is the callback caller, so the contract must describe the Fortran callback
signature rather than a Python raw-address calling convention.

## Character Arguments

Read-only fixed-length character callback dummies use Python strings:

```python
from x2py.contracts import Callable, In, String

callback: Callable[[In(String[8])], None]
```

Writable fixed-length character callback dummies use mutable rank-zero bytes
storage:

```python
from x2py.contracts import Callable, InOut, Out, String

callback: Callable[[Out(String[8][()])], None]
callback: Callable[[InOut(String[8][()])], None]
```

The Python callback receives a NumPy scalar bytes array, such as `np.ndarray`
with shape `()` and dtype `S8`, and writes through that storage:

```python
def update(label):
    label[...] = b"done    "
```

Generated `.pyi` contracts emit `String[n][()]` for Fortran callback
characters with `intent(out)` or `intent(inout)`. Manual contracts reject
`Out(String[n])`, `InOut(String[n])`, and `PassByRef(String[n])` because those
forms would expose an immutable Python `str` where Fortran expects writable
storage.

## Results And Copy-Back

Scalar callback results are converted from the Python return value. Array,
derived, scalar-storage, and character-storage output or inout callback
arguments are copied back before the Fortran adapter returns to native code.

Callback exceptions, invalid callback return conversion, and unsupported
cross-thread callback execution are fatal at the callback boundary: x2py prints
the Python traceback and aborts the host process.
