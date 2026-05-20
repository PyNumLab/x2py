# C Parser Main Merge Guard

Status: guard policy and tooling.

The C parser effort must not merge into project `main` until the frontend is
mature, stable, and the implementation checklist is complete or explicitly
waived. Work should target `c-parser/main` and short-lived `c-parser/*` feature
branches.

## GitHub Limitation

This repository is private on a GitHub plan where repository rulesets and
classic branch protection are not available through the API. Because of that,
the strongest available repository-level guard is a GitHub Actions check plus
local Git hooks.

The Actions workflow in `.github/workflows/c-parser-main-guard.yml` rejects PRs
targeting `main` when either:

- the head branch starts with `c-parser/`
- the PR changes C parser paths

The only planned override is the label:

```text
c-parser-ready-for-main
```

That label should be used only for the final approved merge after the checklist
is complete.

Important: GitHub Actions workflows protect `main` only after the workflow file
exists on the protected base branch. Until the project intentionally brings
this guard into `main`, the immediate protection is local hooks plus project
discipline.

## Local Hook Guard

Tracked hooks live in:

```text
.githooks/
```

Enable them in a checkout with:

```bash
git config core.hooksPath .githooks
```

These hooks block:

- committing C parser paths while checked out on `main`
- merging `c-parser/*` branches into local `main`
- pushing C parser paths or `c-parser/*` work to remote `main`

They do not block normal work on `c-parser/main`.

## C Parser Paths

The guard treats these as C parser paths:

- `.github/workflows/c-parser-main-guard.yml`
- `.githooks/`
- `docs/c_parser/`
- `c_parser/`
- `tests/c_parser/`
- `tests/parser/c/`
- `tests/data/c/`
- `semantics/c2ir.py`

## Final Merge Requirements

Before any final merge to project `main`:

- the C parser implementation checklist is complete or explicitly waived
- full Fortran tests pass
- C parser tests pass
- CLI behavior is documented and stable
- readiness diagnostics are stable
- semantic IR and `.pyi` behavior are documented if implemented
- the final PR carries `c-parser-ready-for-main`
