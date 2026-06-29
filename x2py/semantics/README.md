# Semantics Package

This package owns the language-neutral contract between native parser facts,
editable `.pyi` files, readiness diagnostics, and wrapper code generation.

## Entry Points

| File | Owns |
| --- | --- |
| `models.py` | Semantic IR dataclasses and metadata keys. |
| `fortran2ir.py` | Fortran parser facts to semantic modules. |
| `c2ir.py` | C parser facts to semantic modules. |
| `pyi_parser.py` | Minimal `.pyi` text/file parsing to Python AST. |
| `pyi2ir.py` | User-editable semantic `.pyi` AST conversion and validation. |
| `native_contract.py` | Source-free native ABI and placement validation. |
| `policy_completion.py` | Complete ownership, transfer, destruction, mutability/writeback, projection, nullability, release, storage, and accessor decisions after full signatures are known. |
| `readiness.py` | Support blockers and readiness reports before wrapper codegen. |
| `ir2ast.py` | Semantic IR to codegen AST lowering for wrapper generation; consumes completed policies. |

## Pipeline Position

```text
C parser facts, Fortran parser facts, or parsed .pyi AST
  -> semantic modules
  -> semantic policy completion
       -> complete boundary action and storage policy
  -> readiness blockers or codegen AST
```

`ir2ast.py` is the boundary where semantic contracts become generated-wrapper
implementation details. Object kind, ownership, transfer, destruction,
mutability/writeback, result projection, nullability, release responsibility,
and contract/boundary storage modes must be completed before this boundary by
`policy_completion.py` using `x2py/ownership_policy.py`. Getter result, native
setter assignment, and Python setter exposure policies are completed there as
well. `readiness.py`,
`ir2ast.py`, bridges, and bindings consume those decisions instead of making
local policy guesses. Bridge and binding dispatch is strict: an unregistered
object-kind/action pair is an error rather than a fallback.

The CLI source inspection path keeps parser and converter selection compact in
`x2py/cli.py` through `_SOURCE_SEMANTIC_PIPELINES[language]`. Each table entry
selects the language parser and parser-to-IR converter; semantic policy
completion remains the next shared stage after those converters produce
`SemanticModule` objects.

## Tests And Docs

- Semantic reference: `docs/reference/semantic-ir.md`
- `.pyi` reference: `docs/reference/semantic-pyi-format.md`
- `.pyi` wrapper checklist: `docs/roadmap/semantic-pyi-wrapper-checklist.md`
- Source navigation: `docs/developer-guide/source-map.md`, `docs/developer-guide/feature-to-code-map.md`
- Pipeline map: `docs/internal-architecture/pipeline-map.md`
- Semantic tests: `tests/semantics/`
- `.pyi` tests: `tests/pyi/`
- Wrapper behavior that reaches `ir2ast.py`: `tests/wrapper/fortran/`
