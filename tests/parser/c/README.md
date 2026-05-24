# C Parser Tests

This directory contains active tests for the implemented partial C parser and
narrowly scoped skipped tests for genuinely deferred input/corpus work.

Unskip tests one capability at a time on a short-lived `c-parser/*` branch, then
merge only into `c-parser/main`.

Guidelines:

- keep these tests separate from the Fortran parser tests
- keep wrap-readiness tests under `tests/semantics`, not under parser tests
- do not import `c_parser` at module import time while a roadmap test is skipped
- activate or remove roadmap tests once matching active coverage lands
- add fixtures and goldens only when the corresponding schema is stable
- keep cJSON as the first real-world corpus target once corpus tests start

## Intentional Skips

The normal parser test run retains skips only for the pinned/provenanced
cJSON corpus roadmap and compiler-preprocessed `.i`/`#line` behavior, which
are not implemented yet. CLI, public API, and current project-resolution
coverage are active.

When `C_PARSER_UPDATE_GOLDENS=1` is set, golden inventory checks are skipped
while their corresponding comparison tests rewrite the expected output. Those
update-mode skips are workflow behavior, not unsupported parser input.

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

Each logical project produces one output, for example `math_api.json` for
`math_api.c` plus `math_api.h`, `cJSON.json` for the cJSON pair, and
`jsmn.json` or `linmath.json` for unpaired headers. The NanoSVG header pair
produces `nanosvg.json`; STB produces one golden per top-level library input.

Regenerate all parser goldens with:

```bash
python -m tests.parser.c.generate_c_parser_goldens
```

Regenerate selected projects by naming either input relative to
`tests/data/c/`; matching siblings are included automatically:

```bash
python -m tests.parser.c.generate_c_parser_goldens general/math_api.c json/cJSON.h
```

The fixture comparison test also supports the explicit update mode:

```bash
C_PARSER_UPDATE_GOLDENS=1 python -m pytest -q tests/parser/c/test_c_fixture_suite.py
```

## Error Goldens

Fatal diagnostic fixtures live in `tests/data/c/errors/parser/` and their
expected metadata lives in `fixtures/errors/`. Regenerate them with:

```bash
python -m tests.parser.c.errors.generate_c_parser_error_goldens
```

or update through the active regression test:

```bash
C_PARSER_UPDATE_GOLDENS=1 python -m pytest -q tests/parser/c/test_c_error_fixture_suite.py
```
