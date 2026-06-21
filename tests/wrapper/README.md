# Wrapper Test Suites

Wrapper tests are separated by source language so Fortran and future C wrapper
contracts can evolve without mixing fixtures, helpers, or backend-specific
expectations.

| Language | Test index | Status |
| --- | --- | --- |
| Fortran | [`fortran/README.md`](fortran/README.md) | Active runtime, build, and semantic `.pyi` parity suite |
| C | `c/README.md` | Future wrapper suite; create when C wrapper runtime work begins |

Run every wrapper language suite with:

```bash
python3 -m pytest -q tests/wrapper
```

Within each language directory, tests are organized by feature. One feature
pytest module owns its source, generated-contract, and modified-contract
scenarios rather than splitting those scenarios across separate test modules.
