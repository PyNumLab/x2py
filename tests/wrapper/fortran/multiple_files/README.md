# Multiple Files

Scope: caller-ordered multi-source wrapper builds, module dependencies,
combined generated `.pyi` contract packages, standalone procedure groups, and
generated Makefile dependency ordering.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/multiple_files`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated package expectations live under
`contracts/<case>/` and are refreshed only with
`WRAPPER_UPDATE_PYI_FIXTURES=1`. Modified contract fixtures are copied from
the generated package inside the test.

Roadmap items: Stage 1 native data routing and Stage 3 multi-source combined
contract generation.

Tests: `test_multi_source_builds.py`.
