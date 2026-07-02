# Naming

Scope: Python-visible names, visibility, keyword escaping, name collisions,
generic interfaces, and defined operators.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/naming`

Native data path: `tests/data/fortran/wrapper/`.

Contract fixtures: generated naming and dispatch packages live under
`contracts/<case>/` and are refreshed only with `WRAPPER_UPDATE_PYI_FIXTURES=1`.

Roadmap items: Stage 5 generated-contract runtime parity for generic
interfaces and overload sets, and Stage 8 editable contract visibility and
renaming semantics.

Tests: `test_defined_operators.py`, `test_naming_generated_pyi_contracts.py`,
`test_generic_interfaces.py`, `test_visibility_naming.py`.
