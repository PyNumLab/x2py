# Fortran Parser Package

This package owns Fortran source facts before semantic conversion. It preserves
modules, procedures, declarations, derived types, visibility, and diagnostics
needed by wrapper and inspection workflows.

## Entry Points

| File | Owns |
| --- | --- |
| `parser.py` | Recursive Fortran parser, project assembly, namespace collection, kind resolution hooks. |
| `lexer.py` | Fortran line preprocessing, comment stripping, and token preparation. |
| `models.py` | Parser model dataclasses and diagnostics. |
| `type_resolver.py` | Parser-level type and kind helpers. |
| `cli.py` | Human-readable Fortran parse reports and parser CLI behavior. |
| `utils.py` | Small parser utilities shared inside the package. |

## Tests And Docs

- Public reference: `docs/developer/fortran-parser-reference.md`
- User recipe: `docs/user/examples/recipes/inspect-fortran-api.md`
- Source navigation: `docs/developer/source-map.md`, `docs/developer/feature-to-code-map.md`
- Parser tests: `tests/parser/`
- Fixture suite: `tests/parser/test_fortran_fixture_suite.py`
- Semantic handoff tests: `tests/semantics/test_fortran2ir.py`

Parser support alone does not establish wrapper runtime support. Wrapper
features need semantic lowering, readiness policy, codegen, compilation, and
runtime tests.
