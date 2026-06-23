# Standalone

Scope: standalone external procedures, root exports, and handwritten external
`.pyi` contracts.

Focused pytest command: `python3 -m pytest -q tests/wrapper/fortran/standalone`

Native data path: `tests/data/fortran/wrapper/multi_source/standalone/` for
the current multi-source standalone evidence; dedicated standalone parity
fixtures will move here as Stage 4 expands.

Contract fixtures: none yet; standalone generated, modified, handwritten, and
invalid contract fixtures will live under `contracts/<case>/`.

Roadmap items: Stage 1 subject routing and Stage 4 standalone procedure parity.

Tests: none yet; current standalone build coverage is in
`../multi_source/test_multi_source_builds.py` and contract output coverage is in
`../contract_generation/test_contract_package_namespaces.py`.
