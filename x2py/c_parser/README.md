# C Parser Package

This package owns C source facts for inspection workflows. It parses C inputs,
preserves declarations and diagnostics, and feeds semantic conversion. It does
not own runtime wrapping of user-supplied C libraries.

## Entry Points

| File | Owns |
| --- | --- |
| `parser.py` | Translation-unit parsing, project assembly, unsupported construct diagnostics. |
| `lexer.py` | C tokenization and comment/source splitting helpers. |
| `models.py` | Parser model dataclasses and C parse diagnostics. |
| `preprocessor.py` | Preprocessor metadata collection. |
| `type_resolver.py` | C type resolution helpers used by parser and semantics. |
| `cli.py` | C parser CLI report formatting and preprocessing recipe wiring. |

## Tests And Docs

- Public reference: `docs/developer-guide/c-parser-reference.md`
- User recipe: `docs/examples-gallery/recipes/inspect-c-api.md`
- Source navigation: `docs/developer-guide/source-map.md`, `docs/developer-guide/feature-to-code-map.md`
- Parser tests: `tests/parser/c/`
- Semantic handoff tests: `tests/semantics/test_c2ir.py`
- Readiness tests: `tests/semantics/test_c_semantic_readiness.py`

Runtime C-input wrapping is future backend work. Keep C docs clear about the
current boundary: parse, semantic IR, `.pyi`, and readiness are implemented;
compiled wrappers for user C inputs are not.
