# Semantic `.pyi` Parser Package

This package owns syntax-only parsing for semantic `.pyi` contracts. It reads
inline text or files and returns Python AST modules. Semantic interpretation is
handled by `x2py/semantics/pyi2ir.py`, and combined file/text loading is handled
by `x2py/pipeline/pyi.py`.

Its canonical parser namespace is `x2py.parsers.pyi`; `parse_pyi_text` and
`parse_pyi_file` also remain stable root-level `x2py` exports.
