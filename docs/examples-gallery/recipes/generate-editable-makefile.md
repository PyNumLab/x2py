---
title: Generate An Editable Makefile
audience: users, developers
prerequisites: basic wrapper tutorial, GNU Make, supported compiler toolchain
related: ../verified-cookbook.md, ../../user-guide/fortran-wrapper.md
status: maintained
---

# Generate An Editable Makefile

Use this recipe when you want x2py to generate wrapper sources and
`Makefile.x2py`, then let your build environment run the compile and link
steps.

## Generate The Build Files

```bash
python3 -m x2py tests/data/fortran/wrapper/fruntime_abi_f90.f90 \
  --makefile \
  --out-dir build/fruntime_abi \
  --json
```

This writes generated wrapper sources, runtime support, dependency files, and
`build/fruntime_abi/Makefile.x2py`.

## Build With GNU Make

```bash
make -f build/fruntime_abi/Makefile.x2py -j4 \
  X2PY_FFLAGS=-O3 \
  X2PY_CFLAGS=-O3 \
  X2PY_LDFLAGS=-O3
```

The generated Makefile exposes these variables for local override:

| Variable | Meaning |
| --- | --- |
| `FC` | Fortran compiler |
| `CC` | C compiler |
| `X2PY_LD` | Link command |
| `X2PY_FFLAGS` | Extra Fortran compiler flags |
| `X2PY_CFLAGS` | Extra C compiler flags |
| `X2PY_LDFLAGS` | Extra linker flags |

## Notes

- `--makefile` generates the build plan without compiling immediately.
- `--makefile` and `--verbose` are mutually exclusive.
- Makefile generation is for source-driven Fortran builds. It is not supported
  for `.pyi` wrapper builds that consume explicit native artifacts.
- User Fortran sources remain in caller-provided order. Generated independent
  objects may be built in parallel by Make.
