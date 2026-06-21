---
title: Inspect A C API
audience: users, developers
prerequisites: installation
related: ../verified-cookbook.md, ../../developer-guide/c-parser-reference.md
status: maintained
---

# Inspect A C API

Use this recipe when you want source facts, semantic IR, `.pyi`, or readiness
for a C header. This is an inspection workflow, not a runtime C wrapper build.

## Input

<!-- x2py-doc-source: tests/data/c/general/math_api.h -->
```c
#ifndef X2PY_GENERAL_MATH_API_H
#define X2PY_GENERAL_MATH_API_H

double norm2(int n, const double x[static 1]);
void scale(int n, double alpha, double x[static 1]);
double dot(int n, const double *restrict x, const double *restrict y);
void fill_identity3(double a[static 3][3]);

#endif
```

## Parse Source Facts

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --parse
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/c/general/math_api.h
  Language: c
  Functions: 4
  Structs: 0
  Unions: 0
  Enums: 0
  Typedefs: 0
  Variables: 0
  Macros: 0
  Includes: 0
  Diagnostics: 0
```

## Generate Semantic IR And `.pyi`

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --semantics
```

<!-- x2py-doc-test: run -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --pyi
```

## Check Readiness

<!-- x2py-doc-test: exact -->
```bash
python3 -m x2py tests/data/c/general/math_api.h --language c --wrap-readiness
```

Expected output:

<!-- x2py-doc-test-output -->
```text
File: tests/data/c/general/math_api.h
  Source: c
  Semantic modules: math_api
  Wrappable: yes
  Public functions: 4
  Public classes: 0
  Public variables: 0
  No semantic readiness blockers detected.
```

## Notes

`Wrappable: yes` means the semantic contract has no known readiness blockers.
It does not mean x2py currently has a runtime wrapper backend for user C
libraries.
