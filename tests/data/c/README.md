C fixture data
==============

This tree holds C-only parser fixtures. Keep these files separate from the
Fortran fixture data so C parser tests can grow without changing the existing
Fortran workflows.

Directories:

- `general/`: small hand-written C headers and sources that mirror the themes
  in `tests/data/fortran/general/`, plus C-specific API shapes.
- `json/`: JSON-library source/header inputs used for grouped project
  regression goldens; diagnostics are permitted in these real-world inputs.
- `tinyexpr/`: tinyexpr source/header inputs used for grouped project
  regression goldens; diagnostics are permitted in these real-world inputs.
- `linmath/`: header-only linmath input used for a one-file project regression
  golden; diagnostics are permitted in this macro-heavy real-world input.
- `nanosvg/`: NanoSVG headers used for one dependent-header project golden;
  `nanosvgrast.h` is parsed with its `nanosvg.h` dependency.
- `stb/`: top-level stb single-file library C inputs, each treated as its own
  one-file project regression golden; nested repository metadata is not a
  parser fixture.
- `errors/parser/`: invalid C snippets for parser diagnostic goldens.
- `corpus/`: future pinned third-party C corpus fixtures with license
  provenance.
- `scientific/`: future scientific C API fixtures.

The C parser is still partial. Fixtures may contain constructs that are not
fully parsed yet when they are useful roadmap examples.

The third-party regression inputs do not replace the planned pinned corpus
layout. Before corpus tests claim library coverage, exact provenance and
license requirements must be recorded under `corpus/`.
