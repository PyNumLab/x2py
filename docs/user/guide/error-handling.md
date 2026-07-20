---
title: Error Handling
audience: users, advanced users
prerequisites: common beginner workflow, data types
related: ../reference/diagnostic-codes.md, ../troubleshooting/index.md, callbacks.md
status: maintained
publication: reviewed
---

# Error Handling

Failures occur at distinct stages. Parsing rejects syntax that x2py cannot
model; semantic conversion records contract facts; post-IR policy completion
records every wrapper decision and its precise unsupported reason; wrapper
planning retrieves those completed decisions and raises at the owning
declaration; compilation and linking diagnose native-language and build failures;
Python calls validate values at runtime. Some native termination and callback
failures terminate the process.

This is the general error guide for x2py. The Diagnostic Codes reference lists
stable parser and preprocessing categories; this page explains what to do at
each stage.

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
python3 -m x2py generate --pyi solver.f90 --out contracts/solver
```

In `contracts/solver/solver.pyi`, keep the generated native types and add
the explicit status policy:

```python
from x2py.contracts import Addr, Arg, Int32, Return, String, native_call, raises

@raises(status="status", message="message", success=0)
@native_call([Addr(Arg(0)), Return("status", 0), Return("message", 1)])
def solve(
    value: Int32,
) -> tuple[Int32, String[32]]: ...
```

Build that contract against the same simple native source:

```bash
python3 -m x2py contracts/solver/__init__.pyi \
  --native-fortran-sources solver.f90 \
  --out-dir build/solver
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
ordinary outputs. Editing Semantic `.pyi` Contracts later defines the supported
workflow for changing a generated contract.

## Failure Layers

| Layer | Typical failure | User action |
| --- | --- | --- |
| preprocessing or parsing | missing include, unsupported parser syntax, or a declaration x2py cannot model | read the diagnostic code and source location |
| semantic conversion | unresolved contract type, missing compile-time fact, or incomplete imported contract data | correct the source facts or edit the generated `.pyi` contract |
| post-IR policy completion and wrapper planning | unsupported ownership, ABI, pointer, array, callback, overload, or storage decision; inconsistent completed policy | read the owner path and reason in the wrapper-build error; planning does not retry another route |
| compilation or linking | missing compiler, module, object, symbol, or library | rerun with `--verbose`; inspect the native build plan |
| import | missing shared dependency, wrong ABI, wrong output path | inspect the shared library and runtime environment |
| Python call | wrong dtype, rank, shape, layout, writeability, class, or callable | pass a value matching the generated contract |
| native execution | application status output | return it normally or opt into documented `@raises` policy |
| native termination | `stop`, `error stop`, abort, fatal finalizer | isolate risky calls; Python cannot recover |
| callback boundary | callback exception or invalid result | traceback is printed and the host process aborts |

## Wrapper Build Errors

The default wrapper build is the only compiled-wrapper decision path. With no
subcommand, it completes semantic policy, projects the typed wrapper plan,
generates source, and invokes the native build. There is no separate wrapper
selector, preflight report, or support-analysis command to run.

An unsupported completed policy stops at its owner while the wrapper build
follows that path. For example:

```text
x2py: error: Semantic class 'shapes.shape' has unsupported derived-type policy: abstract derived types need a non-instantiable Python class policy
```

The owner path points at the declaration whose completed decision cannot be
implemented. Fix that contract in the source or editable `.pyi`, then rerun
the same wrapper-build command.

Examples include a missing completed policy, an unsupported derived-type shape,
an incomplete callback contract, or an unsafe ownership/array layout. These are
ordinary errors from the real policy-completion or planning call, not entries in
a separate report.

Do not duplicate native-language validation in these stages. If x2py has enough
information to build the semantic contract and plan, errors such as an invalid
defined operator or invalid native source syntax remain the native compiler's
responsibility. The compiler command and diagnostic are shown by `--verbose`.

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
for inspection stages are catalogued later in the Diagnostic Codes reference.

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
[`test_runtime_policies.py`](../../../tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py).
Validation failures are exercised throughout the focused wrapper suites, and
fatal callback behavior by
[`test_scalar_callbacks.py`](../../../tests/wrapper/fortran/callbacks/test_scalar_callbacks.py).

Troubleshooting later provides focused routes for environmental failures. Use
`--debug` only when an x2py traceback is needed; ordinary user diagnostics
should remain concise.
