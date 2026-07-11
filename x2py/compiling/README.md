# Compiling Package

This package owns native compiler command construction, compile objects,
generated wrapper compilation, runtime support installation, and shared-library
linking.

## Entry Points

| File | Owns |
| --- | --- |
| `basic.py` | Compile object model and dependency relationships. |
| `compilers.py` | Compiler command execution and tool lookup helpers. |
| `default_compilers.py` | Default compiler selection helpers. |
| `python_wrapper.py` | Generated bridge/binding compilation and shared-library creation. |
| `runtime_support.py` | Copying and compiling x2py runtime support used by generated wrappers. |

## Pipeline Position

```text
generated wrapper source files
  -> compile objects and runtime support
  -> compiler commands
  -> linked Python extension
```

Compilation should not decide semantic ownership, Python API shape, or wrapper
readiness. Those decisions happen before generated sources reach this package.

## Tests And Docs

- Wrapper guide: `docs/user/guide/fortran-wrapper.md`
- Build-system docs: `docs/developer/build-system.md`
- Quality and static checks: `docs/developer/quality-assurance.md`
- Source navigation: `docs/developer/source-map.md`, `docs/developer/feature-to-code-map.md`
- Pipeline map: `docs/maintainer/internal-architecture/pipeline-map.md`
- Build-mode tests: `tests/wrapper/fortran/test_build_modes.py`
- Runtime ABI tests: `tests/wrapper/fortran/test_runtime_abi.py`
