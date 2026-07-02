---
title: Error Handling
audience: users, advanced users
prerequisites: common beginner workflow, data types
related: ../reference/diagnostic-codes.md, ../troubleshooting/index.md, callbacks.md
status: maintained
---

# Error Handling

Failures occur at different layers. Parse and readiness diagnostics reject an
unsafe contract before code generation; compiler and linker failures occur
during the native build; Python exceptions report wrapper validation and
conversion failures; some native termination and callback failures terminate
the process.

## Complete Status-Projection Example

Create `solver.f90`:

```fortran
module solver
  implicit none
contains
  subroutine solve(value, status, message)
    integer(4), intent(in) :: value
    integer(4), intent(out) :: status
    character(len=32), intent(out) :: message

    if (value < 0) then
      status = 1
      message = "negative input"
    else
      status = 0
      message = ""
    end if
  end subroutine solve
end module solver
```

Generate an editable contract package:

```bash
python3 -m x2py solver.f90 --pyi --out contracts/solver
```

In `contracts/solver/solver_api.pyi`, keep the generated native types and add
the explicit status policy:

```python
@raises(status="status", message="message", success=0)
@native_call([Ref(Arg(0)), Return("status", 0), Return("message", 1)])
def solve(
    value: Const(Int32),
) -> tuple[Int32, String[32]]: ...
```

Build that contract against the same simple native source:

```bash
python3 -m x2py contracts/solver/__init__.pyi \
  --native-fortran-sources solver.f90 \
  --out-dir build/solver \
```

The success outputs are consumed, while a nonzero status becomes
`RuntimeError` with the native message:

```python
import sys
import numpy as np

sys.path.insert(0, "build/solver")
import solver

api = solver.solver
assert api.solve(np.int32(1)) is None

try:
    api.solve(np.int32(-1))
except RuntimeError as error:
    assert "negative input" in str(error)
else:
    raise AssertionError("expected RuntimeError")
```

Status projection is opt-in. Without `@raises`, status and message remain
ordinary outputs. Follow
[Editing Semantic `.pyi` Contracts](editing-semantic-pyi-contracts.md) before
changing a generated contract.

## Failure Layers

| Layer | Typical failure | User action |
| --- | --- | --- |
| preprocessing or parsing | invalid syntax, missing include, unsupported declaration | read the diagnostic code and source location |
| semantic readiness | unsupported ownership, ABI, pointer, array, or callback policy | check the feature matrix; do not force code generation |
| wrapper generation | invalid name, ambiguous overload, inconsistent contract | inspect generated `.pyi` and declaration path |
| compilation or linking | missing compiler, module, object, symbol, or library | rerun with `--verbose`; inspect the native build plan |
| import | missing shared dependency, wrong ABI, wrong output path | inspect the shared library and runtime environment |
| Python call | wrong dtype, rank, shape, layout, writeability, class, or callable | pass a value matching the generated contract |
| native execution | application status output | return it normally or opt into documented `@raises` policy |
| native termination | `stop`, `error stop`, abort, fatal finalizer | isolate risky calls; Python cannot recover |
| callback boundary | callback exception or invalid result | traceback is printed and the host process aborts |

## Python Exception Types

- `TypeError` covers wrong Python object type, scalar dtype, array dtype/rank/
  shape/layout/writeability, wrong generated class, non-callable callback, and
  failed result conversion.
- `ValueError` covers invalid wrapper options and contract values where a Python
  value is structurally wrong rather than the wrong object category.
- `MemoryError` reports failure to allocate a required Python result copy.
- `RuntimeError` is used by explicit native status projection.
- `ImportError` or loader-specific `OSError` can report extension or shared
  dependency loading failures.

Exact wording is not a substitute for the stable category. Diagnostic codes
for inspection stages are listed in
[Diagnostic Codes](../reference/diagnostic-codes.md).

## Cleanup Guarantees

Validation that fails before native entry releases generated temporaries and
does not call the routine. Successful and exceptional conversion paths release
call-local storage according to completed ownership policy. Wrapper-owned
objects use their generated deallocator; borrowed views do not free native
storage.

No cleanup promise can recover from process termination, native memory
corruption, or a fatal callback boundary.

## Evidence And Troubleshooting

Status-to-exception projection and GIL policy are exercised by
[`test_runtime_policies.py`](../../tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py).
Validation failures are exercised throughout the focused wrapper suites, and
fatal callback behavior by
[`test_scalar_callbacks.py`](../../tests/wrapper/fortran/callbacks/test_scalar_callbacks.py).

Route environmental failures through
[Troubleshooting](../troubleshooting/index.md). Use `--debug` only when an x2py
traceback is needed; ordinary user diagnostics should remain concise.
