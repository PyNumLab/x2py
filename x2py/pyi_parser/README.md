# Semantic `.pyi` Parser Package

This package owns syntax-only parsing for semantic `.pyi` contracts. It reads
inline text or files and returns Python AST modules. Semantic interpretation is
handled by `x2py/semantics/pyi2ir.py`, and combined file/text loading is handled
by `x2py/pyi_pipeline.py`.
