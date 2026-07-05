---
title: Callbacks
audience: advanced users
prerequisites: wrapping functions, error handling, data types
related: error-handling.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
---

# Callbacks

x2py supports Python callbacks invoked immediately during one wrapped native
call. Callback annotations are Fortran-facing: they describe the procedure
signature that Fortran will call, then x2py lifts those arguments into Python
objects for the callback invocation.

This is the opposite direction from a normal `.pyi` function signature. A
normal function signature describes how Python calls the wrapper; x2py may
lower that call into any compatible native bridge shape. A `Callable[[...], T]`
argument describes how Fortran calls the callback adapter, so the argument
order, value/reference passing, explicit or missing callback intent, rank,
shape, character length, and result shape are part of the callback contract.

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

Temporary NumPy views and borrowed derived wrappers passed into a Python
callback are valid only for that callback invocation. Retaining them afterward
is unsupported unless the value is explicitly copied.

## Callback Values

Callback argument wrappers are valid only inside `Callable[[...], T]`:

```python
from x2py.contracts import Callable, Float64, In, InOut, Int32, Out, PassByRef

callback: Callable[
    [
        Int32,
        PassByRef(Float64),
        In(Float64),
        Out(Float64),
        InOut(Float64),
        In(Float64[n]),
    ],
    None,
]
```

The wrappers mean:

| Callback spelling | Fortran callback dummy | Python callback object |
| --- | --- | --- |
| `Int32` | scalar `value` dummy | Python scalar value |
| `PassByRef(Float64)` | scalar by reference with missing intent | rank-zero NumPy scalar storage |
| `In(Float64)` | scalar by reference with `intent(in)` | Python scalar value |
| `Out(Float64)` | scalar by reference with `intent(out)` | rank-zero NumPy scalar storage |
| `InOut(Float64)` | scalar by reference with `intent(inout)` | rank-zero NumPy scalar storage |
| `Float64[n]` | array with missing intent | NumPy array view |
| `In(Float64[n])` | array with `intent(in)` | read-only NumPy array view |
| `Out(Float64[n])` | array with `intent(out)` | writable NumPy array view |
| `InOut(Float64[n])` | array with `intent(inout)` | writable NumPy array view |

Array callback arguments require exact dtype, rank, declared shape, alignment,
and required Fortran contiguity. Derived values use the generated wrapper class.
Array, scalar-storage, character-storage, and derived output/inout callback
values are copied back before the callback adapter returns.

## Character Callback Arguments

Read-only fixed-length character callback arguments use Python `str`:

```python
from x2py.contracts import Callable, In, String

callback: Callable[[In(String[8])], None]
```

The callback receives a Python string with exactly eight encoded bytes. Writable
character callback arguments cannot use plain `String[8]`, because Python
strings are immutable. Use mutable rank-zero fixed-width bytes storage instead:

```python
from x2py.contracts import Callable, InOut, Out, String

callback: Callable[[InOut(String[8][()])], None]
callback: Callable[[Out(String[8][()])], None]
```

The callback receives a NumPy scalar bytes array, for example an object with
shape `()` and dtype `S8`. The Python callback writes through that storage:

```python
def rewrite_label(label):
    label[...] = b"done    "
```

Generated `.pyi` contracts use `String[n][()]` automatically for Fortran
callback character dummies with `intent(out)` or `intent(inout)`. Manual
contracts reject these writable immutable forms:

```python
from x2py.contracts import Callable, InOut, Out, String

Callable[[Out(String[8])], None]     # invalid
Callable[[InOut(String[8])], None]   # invalid
```

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

## Future Contract Policy

Future callback contract work should enrich adapter policy, not reshape the
callback call signature. A `Callable[[...], T]` must continue to describe the
Fortran procedure interface that Fortran calls: argument order, value/reference
passing, storage shape, character length, and result type. The Python callable
can adapt argument names or order itself, so callback contracts should not grow
normal wrapper features such as argument reordering or hidden native-call
projection.

The useful future work is explicit policy for how the adapter crosses the
Fortran-to-Python-to-Fortran boundary:

- copy-in, copy-out, borrowed-view, and zero-copy choices;
- dtype conversion, overflow checks, and result coercion;
- fixed-length character encoding, padding, truncation, and writeback rules;
- ownership and lifetime rules for arrays, scalar storage, derived wrappers,
  and temporary callback values;
- writeback protocols for output or inout values that cannot be mutated
  directly by the Python object currently passed to the callback; and
- callback-specific error/result policy beyond the current fatal native
  callback boundary.

This is planned design work, not current support. The semantic `.pyi` wrapper
roadmap later tracks the callback-adapter policy work.

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
