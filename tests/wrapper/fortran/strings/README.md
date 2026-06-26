# Strings

Scope: Fortran character arguments, results, fields, fixed-length and
variable-length behavior, and character edge cases.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/strings`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated string packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for character kind,
fixed buffer, deferred storage, and copy-in/copy-out behavior.

Tests: `test_character_arguments.py`, `test_character_edge_cases.py`,
`test_string_generated_pyi_contracts.py`.
