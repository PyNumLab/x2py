# External Routines

Scope: standalone external procedures, root exports, handwritten external
`.pyi` contracts, and flat-buffer contracts whose Python layout is more
specific than the native assumed-size dummy.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/external_routines`

Native data path: `tests/data/fortran/wrapper/` for dedicated
single-file, multi-procedure, BLAS-like standalone external, and C-order
flat-buffer fixtures.

Contract fixtures: generated package expectations live under
`contracts/<case>/` and are refreshed only with
`WRAPPER_UPDATE_PYI_FIXTURES=1`. Handwritten external contract fixtures live
under `handwritten_contracts/<case>/`.

Roadmap items: Stage 1 subject routing, Stage 4 standalone procedure parity,
and Stage 8 flat-buffer external-contract evidence.

Tests: `test_external_procedures.py`.
