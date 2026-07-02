---
title: Callbacks
audience: advanced users
prerequisites: wrapping functions, error handling, data types
related: error-handling.md, memory-management.md, ../reference/semantic-pyi-format.md
status: maintained
---

# Callbacks

x2py supports Python callbacks invoked immediately during one wrapped native
call. The callback contract records argument order, resolved dtypes, intents,
array rank and shape, derived wrapper types, and optional result type.

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

- Scalars use the matching semantic dtype conversion.
- Arrays require exact dtype, rank, declared shape, alignment, and required
  Fortran contiguity.
- Derived values require the generated wrapper class.
- Array and derived output/inout callback values are copied back before the
  callback adapter returns.

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

## Evidence And Troubleshooting

Scalar lifetime, nesting, GIL behavior, invalid callbacks, and fatal exception
behavior are exercised by
[`test_scalar_callbacks.py`](../../tests/wrapper/fortran/callbacks/test_scalar_callbacks.py).
Array conversion is exercised by
[`test_array_callbacks.py`](../../tests/wrapper/fortran/callbacks/test_array_callbacks.py)
and derived values by
[`test_derived_callbacks.py`](../../tests/wrapper/fortran/callbacks/test_derived_callbacks.py).

Use [Error Handling](error-handling.md) to distinguish ordinary wrapper
exceptions from fatal callback-boundary failures.
