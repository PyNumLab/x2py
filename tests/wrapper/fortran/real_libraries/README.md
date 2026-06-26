# Real Libraries

Scope: BLAS/LAPACK-style wrapper evidence, mixed object/archive/shared-library
bundles, and large multi-contract native link plans.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/real_libraries`

Native data path: `tests/data/fortran/wrapper/`, with selected real BLAS and
LAPACK routines copied from the parser corpus into the flat wrapper-owned
fixture corpus.

Contract fixtures: generated compact contracts are compared against checked-in
expected packages under `contracts/<case>/`. Use
`WRAPPER_UPDATE_PYI_FIXTURES=1 python3 -m pytest -q
tests/wrapper/fortran/real_libraries` to intentionally refresh those expected
packages after a reviewed contract change. Future modified, handwritten, and
invalid library-scale contracts should use sibling roots such as
`modified_contracts/<case>/`.

Roadmap items: Stage 1 subject routing and Stage 7 library-scale and
mixed-bundle evidence.

Tests: `test_real_blas_lapack.py`, `test_stage7_native_bundles.py`.
