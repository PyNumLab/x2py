# Multi Source

Scope: caller-ordered multi-source wrapper builds, module dependencies,
combined generated `.pyi` contract packages, standalone procedure groups, and
generated Makefile dependency ordering.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/multi_source`

Native data path: `tests/data/fortran/wrapper/multi_source/`.

Contract fixtures: generated at runtime in `test_multi_source_builds.py` for
the Stage 3 source/generated/modified contract package parity case.

Roadmap items: Stage 1 native data routing and Stage 3 multi-source combined
contract generation.

Tests: `test_multi_source_builds.py`.
