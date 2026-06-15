# Repository Instructions

The active codebase is entirely Python.

Ignore:
- *.f90
- *.f95
- *.for
- *.c
- *.h
- *.json

Do not spend context window or analysis on those files unless explicitly requested.
When asked to change or move an API, import path, command, feature, or behavior, do not add or keep compatibility layers, aliases, shims, fallback paths, or legacy entrypoints unless explicitly requested. A requested change means the old behavior should be removed.
When updating tests, remove obsolete tests that only assert removed/old implementation behavior does not exist. Do not preserve rejection or absence checks for API/features that were intentionally removed unless explicitly requested.
Changes in `x2py/semantics/ir2ast.py`, `x2py/codegen/`, and `x2py/compiling/` are separated from the rest of the project. For modifications limited to those areas, run only `tests/wrapper` tests unless a broader test run is explicitly requested.
When investigating coverage failures, mirror the GitHub Actions workflow before deciding the fix: run coverage with `COVERAGE_PROCESS_START=pyproject.toml`, combine parallel data with `python -m coverage combine`, then run `python -m coverage report`. Do not assume a plain local coverage run matches CI, especially when subprocess tests are involved.
At the end of every change, before the final response, run the complete GitHub Actions static-analysis suite to verify code quality:
- `python -m ruff check .`
- `python -m ruff format --check .`
- `bandit -c pyproject.toml -r c_parser fortran_parser semantics x2py --severity-level medium --confidence-level medium`
- `pip-audit . --cache-dir /tmp/pip-audit-cache`
- `vulture`
- `python tools/check_radon_policy.py --base-ref auto`
- `radon cc c_parser fortran_parser semantics x2py -n C -s --total-average`
- `radon mi c_parser fortran_parser semantics x2py -s`
Treat Ruff, Bandit, pip-audit, Vulture, and the Radon policy as blocking. The full Radon complexity and maintainability reports are advisory but must still be run. If a command cannot run because a dependency, network service, or CI-only environment value is unavailable, state that explicitly in the final response.
When you create a commit add this prefix to the message to know that you did push the commit "codex: ..."
