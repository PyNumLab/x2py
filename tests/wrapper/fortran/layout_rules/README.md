# Layout Rules

Scope: wrapper test layout, documentation routing, checklist coverage, fixture
data routing, stale-path rejection, and codegen organization policy.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/layout_rules`

Native data path: `tests/data/fortran/wrapper/` is validated here but not
compiled directly by this subject.

Contract fixtures: validates contract fixture placement under each consuming
subject's `contracts/<case>/` tree.

Roadmap items: Stage 1 layout guard, checklist coverage, and source-data
routing.

Tests: `test_codegen_structure.py`, `test_wrapper_guide_layout.py`.
