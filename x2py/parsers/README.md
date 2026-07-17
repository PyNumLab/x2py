# Parser Frontends

This namespace groups syntax-level frontends without flattening their
language-specific models:

- `x2py.parsers.c` parses C source and headers.
- `x2py.parsers.fortran` parses Fortran source and provides parser reports.
- `x2py.parsers.pyi` parses semantic `.pyi` contracts to Python AST.

Cross-language semantic interpretation belongs to `x2py.semantics`, while
preprocessing and build orchestration belong to `x2py.pipeline`. Stable parser
convenience functions remain exported from the `x2py` package root.

See `docs/developer/source-map.md`, `docs/developer/feature-to-code-map.md`,
`docs/developer/c-parser-reference.md`, `docs/developer/fortran-parser-reference.md`, and
`docs/user/reference/semantic-pyi-format.md` for maintained behavior.
