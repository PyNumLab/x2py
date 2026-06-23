# Native Build

Scope: direct native wrapper builds, output placement, verbose compile/link
commands, generated Makefile-adjacent behavior, and runtime ABI build modes.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/native_build`

Native data path: `tests/data/fortran/wrapper/native_build/` plus shared
runtime fixtures in `tests/data/fortran/wrapper/feature_parity/`.

Contract fixtures: none; this subject builds from native source paths.

Roadmap items: Stage 1 native data routing and Stage 2/7 native build model
evidence.

Tests: `test_build_modes.py`, `test_compiler_verbose.py`, `test_runtime_abi.py`.
