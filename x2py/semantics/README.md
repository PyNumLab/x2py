# Semantics Package

This package owns the language-neutral contract between native parser facts,
editable `.pyi` files, readiness diagnostics, and wrapper code generation.

## Entry Points

| File | Owns |
| --- | --- |
| `models.py` | Semantic IR dataclasses and metadata keys. |
| `fortran2ir.py` | Fortran parser facts to semantic modules. |
| `c2ir.py` | C parser facts to semantic modules. |
| `pyi_parser.py` | User-editable semantic `.pyi` loading and validation. |
| `readiness.py` | Support blockers and readiness reports before wrapper codegen. |
| `ir2ast.py` | Semantic IR to codegen AST lowering for wrapper generation. |

## Pipeline Position

```text
parser facts or .pyi contract
  -> semantic modules
  -> readiness blockers
  -> codegen AST
```

`ir2ast.py` is the boundary where semantic contracts become generated-wrapper
implementation details. Ownership and lifetime policy must come through
`x2py/ownership_policy.py`, not scattered local guesses.

## Tests And Docs

- Semantic reference: `docs/reference/semantic-ir.md`
- `.pyi` reference: `docs/reference/semantic-pyi-format.md`
- `.pyi` wrapper checklist: `docs/roadmap/semantic-pyi-wrapper-checklist.md`
- Source navigation: `docs/developer-guide/source-map.md`, `docs/developer-guide/feature-to-code-map.md`
- Pipeline map: `docs/internal-architecture/pipeline-map.md`
- Semantic tests: `tests/semantics/`
- `.pyi` tests: `tests/pyi/`
- Wrapper behavior that reaches `ir2ast.py`: `tests/wrapper/fortran/`
