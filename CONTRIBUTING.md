## Contributing

### Pull requests

- **CI must be green before merging**: do not merge a PR unless all checks pass (including `test` and `parser-reference-guard`).
- **Explain fixture/golden updates**: if you update any JSON under `tests/data/fortran/` or `tests/parser/fortran/fixtures/`, include a short note in the PR describing why the expected output changed.
- **Run the QA stack for parser/compiler changes**: install `python -m pip install -e ".[qa]"`, use the workflows in `docs/quality.md`, and update that file when a staged adoption task or scheduled triage item changes.

### Parser reference guard

This repo includes a CI guard that may require updating `docs/fortran/fortran_parser.md` when parser-related files change.

- **Default behavior**: if you change `fortran_parser/` or `tests/data/fortran/`, update `docs/fortran/fortran_parser.md` when the change affects the documented feature inventory or behavior.
- **Bypass (use sparingly)**: add the PR label `ignore-parser-reference-guard` to skip that guard for changes that do not meaningfully affect the reference.
