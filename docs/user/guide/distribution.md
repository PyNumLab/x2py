---
title: Distribution
audience: users, packagers
prerequisites: packaging
related: packaging.md, ../troubleshooting/platform-specific-issues.md, ../getting-started/installation.md
status: maintained
publication: draft
---

# Distribution

The portable distribution unit today is the project source plus a reproducible
native build recipe, not a universal prebuilt wheel. A generated extension may
be shared only with environments that match its Python, NumPy, operating-system,
architecture, compiler ABI, and native-library assumptions.

## Source Distribution Workflow

Reuse the `scale-project` and `scale.f90` source first presented in
[Packaging](packaging.md#complete-local-project-example). Distribute these
inputs:

```text
scale-project/
  src/
    scale.f90
  python/
    check_scale.py
  requirements.txt
  BUILDING.md
```

`BUILDING.md` should record the exact supported build command:

```bash
python3 -m x2py src/scale.f90 --out-dir build/scale
python3 python/check_scale.py
```

The asserted result remains the Python value `7.5`, as shown with the original
source in the packaging example.

Record the required Python and NumPy versions, compiler family, compiler flags,
native libraries, library search paths, source order, and platform assumptions.
The receiving environment rebuilds the extension and runs the same smoke test.

## Sharing A Prebuilt Extension

A prebuilt extension is a platform-specific artifact. Before sharing it, the
producer and consumer must match at least:

- operating system and architecture;
- Python implementation, major/minor version, and extension suffix;
- compatible NumPy runtime ABI;
- native compiler ABI and runtime libraries;
- linked native library versions and load paths; and
- extension module name and expected package namespace.

Use the produced extension file as-is; do not rename it without also preserving
its Python initialization symbol.

Even when these facts appear to match, import and runtime smoke tests on the
target environment are required. Current CI evidence does not establish a
general portability matrix.

## Native Dependencies

x2py can link caller-supplied objects, archives, shared libraries, named
libraries, and library directories for supported builds. It does not bundle,
relocate, or discover those dependencies for distribution. The application or
platform packaging system remains responsible for:

- shipping redistributable native libraries;
- setting runtime loader paths;
- preserving compiler runtime dependencies;
- respecting library licenses; and
- validating symbols and ABI on the target platform.

## Wheels And Source Archives

x2py does not currently claim a stable automated wheel workflow, manylinux or
equivalent compliance, macOS universal binaries, Windows wheel support, or
automatic source-archive build hooks. A project may build custom packaging
around x2py, but that project owns the resulting portability and installation
contract.

Do not label a wheel or source archive as generally supported merely because it
worked on the machine that produced it.

## Platform Boundaries

The verified wrapper path uses a GNU native toolchain on the tested Linux
environment. Other platforms and compilers require their own build, ABI,
import, runtime, ownership, and cleanup evidence. See
[Installation](../getting-started/installation.md) for current prerequisites.

## Release Checklist

Before distributing a wrapper project:

1. Generate and review semantic `.pyi` output.
2. Build from a clean output directory with recorded source order and flags;
   resolve any wrapper-plan errors reported by the default build.
3. Preserve the exact build command, source order, flags, and Makefile manifest
   when one is generated.
4. Run asserted calls for every public routine used by the application.
5. Test expected invalid dtype, rank, shape, and ownership cases.
6. Rebuild and rerun on every claimed target environment.
7. State unsupported platforms and external dependencies explicitly.

## Evidence And Troubleshooting

Local output placement and importable artifact creation are exercised by
[`test_build_modes.py`](../../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
Caller-ordered multi-source and external-library builds are exercised by the
focused wrapper suites recorded later in the language feature matrix.

No repository evidence currently proves universal wheel portability.
Platform-Specific Issues and Build Issues later cover target-environment
limitations and failures while rebuilding from source.
