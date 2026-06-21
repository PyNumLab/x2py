---
title: Use Python Inspection APIs
audience: users, developers
prerequisites: installation
related: ../verified-cookbook.md, ../../reference/python-api.md, ../../reference/semantic-ir.md
status: maintained
---

# Use Python Inspection APIs

Use this recipe when tests or tools need to inspect source declarations without
going through the CLI preprocessing path.

Direct parser APIs accept controlled source strings and paths. They do not run
the shared CLI compiler preprocessing pipeline.

## Parse Inline Fortran

<!-- x2py-doc-test: exact -->
```python
from x2py import parse_fortran_file

parsed = parse_fortran_file(
    "subroutine ping(n)\n"
    "  integer, intent(in) :: n\n"
    "end subroutine ping\n",
    filename="inline.f90",
)

print(parsed.procedures[0].name)
```

Expected output:

<!-- x2py-doc-test-output -->
```text
ping
```

## Parse Inline C

<!-- x2py-doc-test: exact -->
```python
from x2py import parse_c_file

parsed = parse_c_file("int add(int a, int b);", filename="inline.h")

print([function.name for function in parsed.functions])
```

Expected output:

<!-- x2py-doc-test-output -->
```text
['add']
```

## Convert C To Semantic IR

<!-- x2py-doc-test: exact -->
```python
from x2py import (
    assess_semantic_wrap_readiness,
    c_file_to_semantic_modules,
    emit_module_stubs,
    parse_c_file,
)

parsed = parse_c_file("int add(int a, int b);", filename="inline.h")
modules = c_file_to_semantic_modules(parsed)

print(emit_module_stubs(modules)["inline"])
print(assess_semantic_wrap_readiness(modules)["wrappable"])
```

Expected output:

<!-- x2py-doc-test-output -->
```text
def add(
    a: Int,
    b: Int
) -> Int: ...
True
```

## Check An Edited `.pyi` String

<!-- x2py-doc-test: exact -->
```python
from x2py import assess_semantic_wrap_readiness, parse_pyi_text

module = parse_pyi_text(
    """
from typing import Callable

def integrate(
    objective: Callable[[Float64], Float64],
    x0: Float64
) -> Float64: ...
""",
    module_name="solver",
)

report = assess_semantic_wrap_readiness(module, source="solver.pyi")
print(report["wrappable"])
```

Expected output:

<!-- x2py-doc-test-output -->
```text
True
```

## Notes

- Use the CLI when project headers, macros, include directories, or compiler
  target flags matter.
- Use these APIs when your test already owns a small source string or parsed
  fixture.
