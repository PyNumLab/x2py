# C Parser Tests

This directory contains active tests for the implemented partial C parser.

Guidelines:

- keep these tests separate from the Fortran parser tests
- keep wrap-readiness tests under `tests/semantics`, not under parser tests
- add fixtures and goldens only when the corresponding schema is stable
- keep the checked-in cJSON regression inputs active while a separately pinned
  and provenanced corpus remains deferred

## Active cJSON Regression

The normal parser test run has no intentionally skipped C parser tests.
`tests/data/c/json/cJSON.h` and `cJSON.c` exercise the header, source and
project paths in `test_c_corpus.py`; a separately pinned copy with license and
source provenance remains documentation work rather than a disabled test.

## Parser Goldens

Active parser goldens cover grouped projects from `tests/data/c/general/`,
`tests/data/c/json/`, `tests/data/c/tinyexpr/`, `tests/data/c/linmath/`, and
`tests/data/c/nanosvg/`, plus top-level C inputs from `tests/data/c/stb/`.
Files sharing a stem are parsed together as a project, with a `.c`
translation-unit input ordered before its `.h` sibling.
Explicit dependent header groups are ordered with the included header before
the dependent header, as in `nanosvg.h` then `nanosvgrast.h`. A source or
header without a matching sibling is serialized as a one-file project.
STB inputs remain separate one-file projects because that distribution is a
collection of independent single-file libraries.
The current parser records the resolved include edge but parses each project
member separately; it does not yet preprocess header contents into the source
translation unit.
The third-party-library inputs are realistic regression inputs for the partial
parser; diagnostics in their goldens are expected and do not claim full
library support.

## Developer Walkthrough

`test_c_parser_developer_tutorial.py` is an executable reading guide for
`c_parser/parser.py`. It shows the shared declaration/declarator gateway, the
`visit_file` dispatch of declaration roles, and the preprocessed linemarker
path without replacing the feature-focused test modules.

Each logical project produces one output, for example `math_api.json` for
`math_api.c` plus `math_api.h`, `cJSON.json` for the cJSON pair, and
`jsmn.json` or `linmath.json` for unpaired headers. The NanoSVG header pair
produces `nanosvg.json`; STB produces one golden per top-level library input.

Regenerate all parser goldens with:

```bash
C_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser/c/test_c_fixture_suite.py
```

Regenerate selected projects by naming either input relative to
`tests/data/c/`; matching siblings are included automatically:

```bash
python -m tests.parser.c.generate_c_parser_goldens general/math_api.c json/cJSON.h
```

## Error Goldens

Fatal diagnostic fixtures live in `tests/data/c/errors/parser/` and their
expected metadata lives in `fixtures/errors/`. Regenerate them with:

```bash
C_PARSER_UPDATE_GOLDENS=1 PYTHONPATH=. pytest -q tests/parser/c/test_c_error_fixture_suite.py
```

The standalone generator modules remain available for targeted refreshes, but
the comparison tests also rewrite their checked-in baselines when
`C_PARSER_UPDATE_GOLDENS=1` is set.
