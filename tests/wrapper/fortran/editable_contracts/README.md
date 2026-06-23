# Editable Contracts

Scope: modified `.pyi` runtime contracts that intentionally alter visibility,
validation, ownership, lifetime, error, projection, or export behavior.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/editable_contracts`

Native data path: `tests/data/fortran/wrapper/feature_parity/` until dedicated
editable-contract native cases are added.

Contract fixtures: none yet; modified, handwritten, and invalid editable
runtime contracts will live under `contracts/<case>/`.

Roadmap items: Stage 1 subject routing and Stage 6 editable contract semantics.

Tests: none yet; current temporary edited-entry assertions are in
`../contract_generation/test_pyi_wrapper_builds.py`.
