---
title: Inspect A Fortran API
audience: users, developers
prerequisites: basic wrapper tutorial
related: ../verified-cookbook.md, ../../reference/semantic-pyi-format.md
status: maintained
---

# Inspect A Fortran API

Use this recipe when you want to understand a Fortran declaration before
building a wrapper.

## Input

<!-- x2py-doc-source: tests/data/fortran/general/basic_subroutine.f90 -->
```fortran
module m1
contains
subroutine add1(n, x)
  integer, intent(in) :: n
  real(kind=8), intent(inout), dimension(n) :: x
end subroutine add1
end module m1
```

## Parse Source Facts

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --parse
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/basic_subroutine.f90
  Modules: 1
    - module m1 (vars=0, uses=0)
      Procedures: 1
        - subroutine add1(n:integer[0], x:real(8)[1])
```

## Generate Semantic `.pyi`

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --pyi
```

Expected output:

<!-- x2py-doc-test-output -->
```python
File: tests/data/fortran/general/basic_subroutine.f90
Root contract: basic_subroutine/basic_subroutine.pyi
from . import m1

Module contract: m1.pyi
def add1(
    n: Ptr(Const(Int32)),
    x: Float64[n]
) -> None: ...
```

## Check Readiness

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/fortran/general/basic_subroutine.f90 --wrap-readiness
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/fortran/general/basic_subroutine.f90
  Source: fortran
  Semantic modules: m1
  Wrappable: yes
  Public functions: 1
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```

## Notes

- Parser output is source facts, not wrapper policy.
- `.pyi` output is the editable semantic contract.
- Readiness detects blockers before generated wrapper code is emitted.
