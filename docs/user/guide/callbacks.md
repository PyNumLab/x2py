---
title: Callbacks
audience: advanced users
prerequisites: wrapping functions, error handling, data types
related: error-handling.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
---

# Callbacks

x2py supports Python callbacks invoked immediately during one wrapped native
call. A semantic `.pyi` declares each native callback shape once as a named
prototype, then callback-taking procedures refer to that prototype by name.

This is the opposite direction from a normal `.pyi` function signature. A
normal function signature describes how Python calls the wrapper; x2py may
lower that call into any compatible native bridge shape. A `@prototype`
declaration describes how native code calls the callback adapter, so argument
order, value/reference passing, rank, shape, character length, and result shape
are part of the callback contract. Native callback direction is deliberately
not repeated in semantic `.pyi`.

## Complete Callback Example

Create `callbacks.f90`:

```fortran
module callbacks_api
  implicit none
  abstract interface
    real(8) function scalar_callback(value) result(output)
      real(8), intent(in) :: value
    end function scalar_callback
  end interface
contains
  real(8) function apply(callback, value) result(output)
    procedure(scalar_callback) :: callback
    real(8), intent(in) :: value
    output = callback(value)
  end function apply
end module callbacks_api
```

Build it:

```bash
python3 -m x2py callbacks.f90 --out-dir build/callbacks
```

Then pass a Python callable and assert the converted result:

```python
import sys
import numpy as np

sys.path.insert(0, "build/callbacks")
import callbacks

api = callbacks.callbacks_api
result = api.apply(lambda value: np.float64(3.0 * value), np.float64(2.5))
assert result == np.float64(7.5)
```

## Lifetime

The generated wrapper keeps a strong reference to the Python callable only
until the wrapped call returns. Native code must not store the callback or call
it later. Nested callback-taking calls on the same entering Python thread are
supported.

Primitive scalar callback arguments are materialized as independent NumPy
scalar values, so retaining them is safe. Temporary NumPy array views and
borrowed derived wrappers are valid only for that callback invocation.
Retaining either afterward is unsupported unless the value is explicitly
copied.

## Callback Values

Callback arguments use ordinary semantic types. Native code passes them by
reference unless the prototype applies the one ABI override, `Value(T)`:

```python
from x2py.contracts import Float64, Int32, Value, prototype

@prototype
def update_values(
    count: Int32,
    scale: Value(Float64),
    values: Float64[count],
) -> None: ...

def apply_update(callback: update_values, count: Int32) -> None: ...
```

The spellings mean:

| Callback spelling | Fortran callback dummy | Python callback object |
| --- | --- | --- |
| `Int32` | scalar reference dummy | owned `np.int32` scalar value |
| `Value(Float64)` | scalar `value` dummy | owned `np.float64` scalar value |
| `Float64[n]` | array reference dummy | writable NumPy array view |
| `point_t` | derived reference dummy | generated wrapper object |
| `Value(point_t)` | derived `value` dummy | generated wrapper over the call-local value copy |

Array callback arguments require exact dtype, rank, declared shape, alignment,
and required Fortran contiguity. Derived values use the generated wrapper class.
Reference arrays, characters, and derived objects are exposed permissively and
written back before the callback adapter returns. Primitive scalar arguments
are immutable NumPy scalar values even when their native ABI uses a reference.
Scalar reference writeback is unsupported: model a scalar value delivered back
to native code as the declared callback result. A `Value(...)` argument changes
only the native ABI to Fortran `value`; it is also received as an independent
NumPy scalar.

## Character Callback Arguments

Fixed-length character callback arguments use their ordinary semantic spelling:

```python
from x2py.contracts import String, prototype

@prototype
def label_callback(label: String[8]) -> None: ...
```

Because reference callbacks are permissive, the callback receives mutable
rank-zero NumPy bytes storage with shape `()` and dtype `S8`. The Python
callback reads or writes through that storage:

```python
def rewrite_label(label):
    label[...] = b"done    "
```

The semantic callback annotation remains `String[n]`; the callback adapter
chooses mutable scalar storage without encoding native direction in `.pyi`.

A non-callable argument raises `TypeError` before native execution.

## Threads And The GIL

The callback trampoline acquires the Python GIL for the callback and releases
the matching state afterward. The callback must execute on the same Python
thread that entered the wrapped routine. Cross-thread native invocation is not
supported.

Callback-taking calls keep the GIL policy required by the callback bridge.
Do not use callback execution as synchronization for unrelated native state.

## Callback Failures

A callback exception, invalid callback result, or cross-thread invocation
cannot be safely unwound through arbitrary native frames. The wrapper prints
the Python traceback and aborts the host process. It never invents a fallback
return value and continues native execution.

Run untrusted callback behavior in a subprocess if the host application must
survive such failures.

## Unsupported Forms

- stored callback registration and unregistration;
- callbacks invoked after the wrapped call;
- optional dummy procedure arguments;
- procedure pointers and null procedure pointers;
- asynchronous or cross-thread callback invocation; and
- persistent callback ownership during object or library teardown.

## Adapter Policy

The post-IR policy stage completes how the adapter crosses the
Fortran-to-Python-to-Fortran boundary before wrapper generation begins. It
records value versus reference ABI, permissive reference writeback, array shape,
fixed character length, exact derived type identity, call-scoped context
lifetime, entering-thread enforcement, GIL entry, cleanup, and the fatal error
action. The Python binding and Fortran bridge only lower those completed actions.

A `@prototype` declaration is a compile-time semantic declaration, not a
Python runtime export. Its declaration order, value/reference transport,
storage shape, character length, and result type define the callback transport
contract. The Python callable may adapt argument names itself, so prototypes do
not use normal wrapper projection such as `@native_call`.

Post-IR policy selects the weakest correct native declaration from the complete
prototype. Classic scalar, explicit-shape, and assumed-size signatures use an
implicit external declaration. Signatures with optional or descriptor
arguments, polymorphism, or non-scalar/descriptor results use the
named native prototype through an explicit declaration. That path imports the
real interface, including direction facts deliberately omitted from semantic
`.pyi`, so its compiler module file must be available. `Value(...)` alone does
not force the explicit path when a typed external declaration is sufficient.

Future work may add user-selectable policy for:

- borrowed-view, detached-copy, and zero-copy choices;
- dtype conversion, overflow checks, and result coercion;
- fixed-length character encoding, padding, truncation, and writeback rules;
- ownership and lifetime rules for arrays, scalar storage, derived wrappers,
  and temporary callback values;
- writeback protocols for values that cannot be mutated
  directly by the Python object currently passed to the callback; and
- callback-specific error/result policy beyond the current fatal native
  callback boundary.

These choices are not currently user-selectable; unsupported forms remain
blocked instead of selecting a different backend behavior.

## Evidence And Troubleshooting

Scalar lifetime, nesting, GIL behavior, invalid callbacks, and fatal exception
behavior are exercised by
[`test_scalar_callbacks.py`](../../../tests/wrapper/fortran/callbacks/test_scalar_callbacks.py).
Array conversion is exercised by
[`test_array_callbacks.py`](../../../tests/wrapper/fortran/callbacks/test_array_callbacks.py)
and derived values by
[`test_derived_callbacks.py`](../../../tests/wrapper/fortran/callbacks/test_derived_callbacks.py).

Error Handling later distinguishes ordinary wrapper exceptions from fatal
callback-boundary failures.
