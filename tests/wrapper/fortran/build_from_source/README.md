# Build From Source

Scope: direct Fortran source wrapper builds, output placement, verbose compile/link
commands, generated Makefile-adjacent behavior, and runtime ABI build modes.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/build_from_source`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated source-build packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 1 native data routing, Stage 2 structured native build
plan evidence, and Stage 6 manifest/Makefile follow-up evidence.

Tests: `test_build_modes.py`, `test_compiler_verbose.py`,
`test_source_generated_pyi_contracts.py`, `test_runtime_abi.py`.
