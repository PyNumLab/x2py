C fixture data
==============

This tree holds C-only parser fixtures. Keep these files separate from the
Fortran fixture data so C parser tests can grow without changing the existing
Fortran workflows.

Directories:

- `general/`: small hand-written C headers and sources that mirror the themes
  in `tests/data/fortran/general/`, plus C-specific API shapes.
- `errors/parser/`: future invalid C snippets for parser diagnostic goldens.
- `corpus/`: future pinned third-party C corpus fixtures with license
  provenance.
- `scientific/`: future scientific C API fixtures.

The C parser is still partial. Fixtures may contain constructs that are not
fully parsed yet when they are useful roadmap examples.
