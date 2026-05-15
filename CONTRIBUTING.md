## Contributing

### Pull requests

- **CI must be green before merging**: do not merge a PR unless all checks pass (including `test` and `parser-reference-guard`).
- **Explain fixture/golden updates**: if you update any JSON under `tests/data/fortran/` or `tests/parser/fortran/fixtures/`, include a short note in the PR describing why the expected output changed.

### Parser reference guard

This repo includes a CI guard that may require updating `parser_implementation_reference.md` when parser-related files change.

- **Default behavior**: if you change `fortran_parser/` or `tests/data/fortran/`, update `parser_implementation_reference.md` when the change affects the documented feature inventory or behavior.
- **Bypass (use sparingly)**: add the PR label `ignore-parser-reference-guard` to skip that guard for changes that do not meaningfully affect the reference.
