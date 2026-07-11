# .pyi Tests

Scope: semantic `.pyi` generation, fixture round-trips, explicit Fortran
contract-package output, and `.pyi` parser/printer behavior that does not
compile or import a runtime wrapper extension.

Fixture layout:

- `fixtures/general/` stores source-owned exact generation goldens.
- `fixtures/wrapper_contracts/` stores explicit `--pyi --out` package
  expectations used by package-generation tests.
- Runtime wrapper contracts that are built with native objects stay under
  `tests/wrapper/fortran/<subject>/contracts/`.

Explicit package fixtures can be refreshed after a reviewed contract-format
change with:

```bash
WRAPPER_UPDATE_PYI_FIXTURES=1 python3 -m pytest -q tests/pipeline/pyi_builds/test_contract_package_generation.py
```
