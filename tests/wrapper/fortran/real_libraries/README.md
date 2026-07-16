# Real Libraries

Scope: BLAS/LAPACK-style wrapper evidence, mixed object/archive/shared-library
bundles, and large multi-contract native link plans.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/real_libraries`

Native data path: full library contract and runtime coverage reads
`tests/data/fortran/blas/` and `tests/data/fortran/lapack/` directly. Full
native BLAS/LAPACK object files are compiled once into
`.pytest_cache/x2py/real-library-native`, archived once, and linked once into
the shared libraries reused by repeated wrapper test runs. Set
`X2PY_REAL_LIBRARY_NATIVE_CACHE_DIR` to move this cache, including in CI. Object
compilation runs in parallel after required module sources are compiled; set
`X2PY_REAL_LIBRARY_NATIVE_JOBS` to override the default bounded worker count.
Runtime smoke assertions call selected routines from the fully wrapped modules;
they do not build a selected-procedure wrapper.

The full BLAS/LAPACK wrapper builds use `-O0 -g0` for generated wrapper C and
Fortran bridge compilation. These jobs validate large wrapper generation and
import/runtime behavior; they are not runtime-performance benchmarks, so the
fast compile override keeps CI focused on wrapper correctness.

GitHub Actions runs separate BLAS and LAPACK jobs on `ubuntu-24.04`, Python
3.12, and `gfortran-13`. Each job restores its library-specific cache into the
runner temporary directory and rebuilds it on a cache miss. The key includes
the runner OS, pinned compiler profile, selected library, and BLAS/LAPACK source
content. Native object files are reusable only for the same
platform/compiler/source combination; a different runner image, compiler, or
fixture content gets a separate rebuildable cache entry.

Contract fixtures: full generated BLAS and LAPACK packages are compared against
checked-in expected packages under `contracts/blas/` and `contracts/lapack/`.
Use
`WRAPPER_UPDATE_PYI_FIXTURES=1 python3 -m pytest -q
tests/wrapper/fortran/real_libraries` to intentionally refresh those expected
packages after a reviewed contract change. Future modified, handwritten, and
invalid library-scale contracts should use sibling roots such as
`modified_contracts/<case>/`.

Roadmap items: Stage 1 subject routing and Stage 7 library-scale and
mixed-bundle evidence.

Tests: `test_real_blas_lapack.py`, `test_stage7_native_bundles.py`.
