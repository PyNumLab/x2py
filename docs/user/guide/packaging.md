---
title: Packaging
audience: users, packagers
prerequisites: common beginner workflow
related: distribution.md, ../reference/cli-commands.md, ../tutorials/packaging.md
status: maintained
---

# Packaging

x2py currently produces an importable native extension and its build artifacts;
it does not provide a stable Python wheel backend or project template. The
supported packaging workflow is therefore local project integration: keep the
native source and Python tests under version control, rebuild into an explicit
directory, and treat generated native artifacts as replaceable build output.

## Complete Local Project Example

Reuse `scale.f90`, whose complete source is first shown in the
[README Quick Start](../../../README.md#quick-start). Place that file in this
simple project:

```text
scale-project/
  src/
    scale.f90
  build/
  python/
    check_scale.py
```

Build from the project root:

```bash
python3 -m x2py src/scale.f90 --out-dir build/scale
```

Put the following result check in `python/check_scale.py`:

```python
import sys
import numpy as np

sys.path.insert(0, "build/scale")
import scale

assert scale.scale(np.float64(3.0), np.float64(2.5)) == np.float64(7.5)
```

Run it from the project root:

```bash
python3 python/check_scale.py
```

No output means the assertion passed.

## Generated Package Shape

The extension module name normally comes from the first source filename.
Contained native modules become child Python modules; standalone procedures
remain at the extension root. `--out NAME` selects a different extension name.

Use the selected output directory as the import location during development.
The shared-library filename is platform-specific, so avoid hard-coding a suffix
outside project-specific build scripts.

## Generated Artifacts

An output directory can contain native object and module files, generated
wrapper sources, runtime support, build metadata, and the importable extension.
These files are build products. Do not edit them as the source of the public
API; change the native source or an intentional semantic `.pyi` contract.

The extension is tied to its Python implementation, NumPy ABI, platform,
architecture, compiler ABI, and linked native dependencies. Merely copying it
into another project is not a portable packaging guarantee.

## Editable Makefile

Generate a Makefile when a local build needs inspectable commands or controlled
flags:

```bash
python3 -m x2py src/scale.f90 \
  --wrap \
  --makefile \
  --out-dir build/scale

make -f build/scale/Makefile.x2py X2PY_FFLAGS=-O3 X2PY_CFLAGS=-O3
```

Makefile mode is an explicit wrapper submode, so the command keeps `--wrap`.
Makefile mode and verbose direct compilation are separate modes. The generated
Makefile expects GNU Make and a POSIX-style shell. Semantic `.pyi` Makefile
builds also write `x2py-build.json`, which can regenerate or replay the build.

## Rebuild Policy

Rebuild when source, source order, compiler, flags, Python, NumPy, native
dependencies, or the semantic contract changes. For a contract-changing build,
remove the selected output directory first so stale objects and modules cannot
mask the new build:

```bash
rm -rf build/scale
python3 -m x2py src/scale.f90 --out-dir build/scale
```

Keep sources, explicit contracts, build commands, and Python assertions under
version control. Keep `build/` out of version control unless a release process
deliberately captures platform-specific artifacts.

## Import Paths

During local development, add the build directory to `sys.path`, set
`PYTHONPATH`, or run Python from a location where the extension is importable.
x2py does not currently install the extension into a project package or manage
editable Python installs automatically.

## Limitations

- No stable wheel-building backend or generated `pyproject.toml` integration.
- No automatic repair or bundling of external native shared libraries.
- No cross-platform artifact promise.
- No automatic native dependency discovery or source reordering.
- No guarantee that a copied extension imports under another Python or NumPy ABI.

## Evidence And Troubleshooting

Output names, directories, native build plans, verbose mode, and Makefile option
validation are exercised by
[`test_build_modes.py`](../../../tests/wrapper/fortran/build_from_source/test_build_modes.py).
Multi-source package shape is exercised by
[`test_multi_source_builds.py`](../../../tests/wrapper/fortran/multiple_files/test_multi_source_builds.py).

For compile or link failures, rerun with `--verbose` and inspect the emitted
native commands; Build Issues expands that diagnosis later. Distribution later
explains the requirements for sharing an artifact with another machine or
environment.
