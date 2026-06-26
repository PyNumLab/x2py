# Edit `.pyi` Contracts

Scope: modified `.pyi` runtime contracts that intentionally alter visibility,
validation, ownership, lifetime, error, projection, or export behavior.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/edit_pyi_contracts`

Native data path: `tests/data/fortran/wrapper/` until dedicated
editable-contract native cases are added.

Contract fixtures: planned modified, handwritten, and invalid editable runtime
contracts will live under sibling roots such as `modified_contracts/<case>/`
when this subject gets dedicated tests.

Roadmap items: Stage 1 subject routing and Stage 6 editable contract semantics.

Tests: none yet; current temporary edited-entry assertions are in
`../build_from_pyi/test_pyi_wrapper_builds.py`.
