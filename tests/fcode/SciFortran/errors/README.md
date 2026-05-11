# SciFortran parse-failing fixtures

This directory contains **only** SciFortran fixtures that are currently expected to fail parsing.

Source of truth for failures: `tests/fcode/SciFortran/errors/SciFortran_errors.json`.

## Workflow

1. Every `*.f90` file in this folder **must** appear in `SciFortran_errors.json` with:
   - `fixture`: relative path (for example `SciFortran/errors/GAUSS_QUADRATURE.f90`)
   - `message_fragments`: snippets describing the expected parser error
2. Tests assert these files still fail with the documented error fragments.
3. When a file is fixed so it parses successfully:
   - move the file out of `SciFortran/errors/` into `SciFortran/`
   - remove its entry from `SciFortran/errors/SciFortran_errors.json`
   - add/update its golden `*.json` fixture next to the Fortran file in `SciFortran/`

If a file remains in `SciFortran/errors/` but parses successfully, tests should fail to force cleanup.
