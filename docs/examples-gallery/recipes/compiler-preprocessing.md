---
title: Use Compiler Preprocessing Options
audience: users, developers
prerequisites: installation, native project compiler flags
related: ../verified-cookbook.md, ../../developer-guide/c-parser-reference.md, ../../developer-guide/fortran-parser-reference.md
status: maintained
---

# Use Compiler Preprocessing Options

Use this recipe when the native project needs include paths, macros, standards,
or compiler-specific flags before x2py can parse it.

## Direct Compiler Settings

```bash
python3 -m x2py include/api.h --language c --parse \
  --compiler clang \
  -I include \
  -D API_EXPORT= \
  --std c11 \
  --compiler-arg=--sysroot=/opt/sdk
```

## Compilation Database

C projects can use a compilation database:

```bash
python3 -m x2py src/api.c --language c --semantics \
  --compile-commands build/compile_commands.json
```

## Notes

- Pass the same important include paths, macros, and target flags used by the
  native project.
- Compiler-backed semantic and `.pyi` stages can also probe target datatype
  facts.
- These examples are environment-dependent, so they are not marked as automatic
  documentation tests.
