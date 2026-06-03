# Quality Assurance

Last reviewed: 2026-06-03

This project uses a staged Python QA stack. Fast bug-focused checks run on pull
requests, while deeper fuzzing and random-order discovery run on schedule or by
manual dispatch.

The selected active quality stack is adopted. Scheduled workflow review and
future Ruff/Radon threshold ratchets are ongoing maintenance, not unfinished
rollout work. Mutation testing and pre-commit are not part of the active stack.

## Active Cadence

| Cadence | Tools |
| --- | --- |
| Pull request and protected-branch push | pytest, coverage.py, stable-seed pytest-randomly, Ruff, Bandit, pip-audit, Vulture, staged Radon policy |
| Weekly and manual dispatch | Hypothesis fuzz profile, changing-seed pytest-randomly |
| Manual triage | Full Radon reports and low-severity Bandit review |

## Install

Install the package plus the QA toolchain:

```bash
python -m pip install -e ".[qa]"
```

If your shell only exposes `python3`, use:

```bash
python3 -m pip install -e ".[qa]"
```

## Local Commands

Fast inner loop:

```bash
pytest -q
ruff check .
ruff format .
```

CI-shaped test and coverage run:

```bash
HYPOTHESIS_PROFILE=ci \
COVERAGE_PROCESS_START=pyproject.toml \
PYTHONPATH=. \
python -m coverage run -m pytest -q --randomly-seed=1
python -m coverage combine
python -m coverage report
```

For subprocess coverage investigations, mirror that command shape before
deciding a fix. A plain local coverage run can miss subprocess data.

Reproduce a random-order failure:

```bash
pytest -q --randomly-seed=<seed-from-failing-run>
```

Run property and fuzz tests:

```bash
pytest -q -m property --hypothesis-profile=ci
HYPOTHESIS_PROFILE=fuzz pytest -q -m fuzz --hypothesis-show-statistics
```

Run security and dependency checks:

```bash
bandit -c pyproject.toml -r c_parser fortran_parser semantics x2py --severity-level medium --confidence-level medium
pip-audit . --cache-dir /tmp/pip-audit-cache
```

Run dead-code and complexity checks:

```bash
vulture
python tools/check_radon_policy.py
radon cc c_parser fortran_parser semantics x2py -n C -s --total-average
radon mi c_parser fortran_parser semantics x2py -s
```

The Radon policy check is blocking. It prevents the reviewed C-or-worse hotspot
average from rising above `19.01` and, when a Git base ref is supplied, rejects
new or worsened changed production blocks above complexity `20`. Full Radon
reports remain advisory for refactor planning.

## Tool Decisions

### pytest And coverage.py

**Role:** behavioral regression backbone and branch-coverage floor.

**Evidence:** recorded full-suite baseline is `3497 passed`; combined
subprocess branch coverage is `95.34%`, above the configured `95%` gate.

**Decision:** keep as required baseline project gates.

### pytest-randomly

**Role:** catches hidden test-order coupling and makes failures reproducible
with seeds.

**Evidence:** normal CI uses `--randomly-seed=1`; scheduled/manual quality runs
use `${{ github.run_id }}` as a changing seed.

**Decision:** keep stable-seed PR CI and changing-seed scheduled/manual runs.

### Hypothesis

**Role:** generates edge cases for parsers, AST transforms, semantic IR, and
code generation.

**Bugs found:** generated code-generation cases exposed quoted `Name(...)`
emission. Generated preprocessing inputs also aligned raw Fortran and C macro
handling around compiler-required errors.

**Decision:** keep bounded property tests in normal test coverage and longer
fuzz profiles on schedule/manual dispatch.

### Ruff

**Role:** fast linting and formatting for undefined names, unused imports,
suspicious patterns, modernization, simplified control flow, and high McCabe
complexity.

**Bugs or issues found:** raw regex issues, formatting drift, and static-risk
maintenance debt. These are static-risk findings, not runtime defects.

**Decision:** keep as a blocking gate. Line-length diagnostics remain
intentionally unselected because wrapping parser diagnostics and embedded test
sources would add noise without improving correctness.

### Bandit

**Role:** security scanning for subprocess, filesystem, deserialization, and
credential-like patterns.

**Evidence:** no medium- or high-severity findings. Reviewed low-severity
findings are parser sentinel/template tokens and intentional argv-based
compiler/preprocessor subprocess calls without shell execution.

**Decision:** keep blocking at medium confidence/severity in CI. Re-review the
full low-severity report after subprocess-boundary changes.

### pip-audit

**Role:** dependency vulnerability scanning.

**Evidence:** no known vulnerability is present in the current dependency set.

**Decision:** keep blocking in CI and re-run locally when dependencies change.

### Vulture

**Role:** dead-code detection.

**Bugs or issues found:** removed dead Fortran parser parameters and unused test
lambda parameters reported by CI.

**Decision:** keep blocking in CI with narrow exclusions.

### Radon

**Role:** complexity and maintainability tracking.

**Evidence:** reviewed average complexity is `C (18.95)`. The staged policy
allows unchanged legacy hotspots while blocking new or worsened changed
production hotspots above complexity `20`.

**Bugs or issues found:** Radon found maintainability hotspots. CI also exposed
that the first staged policy was too strict for unchanged legacy hotspots; the
policy was corrected.

**Decision:** keep `tools/check_radon_policy.py` blocking and keep full Radon
reports advisory/manual.

### GitHub Actions

**Role:** reproducible CI and scheduled discovery.

**Bugs or issues found:** recent remote quality runs found Ruff raw-regex
issues, Ruff formatting drift, Vulture unused test parameters, and the
too-strict Radon policy.

**Decision:** keep. Review scheduled results and record actionable failures
until fixed.

## Historical Mutation Findings

Mutation testing was useful during rollout, but it is no longer an adopted
tool. Do not keep `mutmut` as a regular dependency, workflow, or local wrapper.
A future annual mutation audit can be run outside the normal QA stack if
needed.

Keep the ordinary regression tests and fixes that came from it:

- duplicate typedef-cycle diagnostic coverage;
- cycle-safe union-by-value diagnostics;
- Fortran project namespace collection respecting the requested encoding;
- direct Fortran parser contracts for diagnostics, forwarding, registries,
  ownership, provenance, source locations, boundaries, and loop progress.

## Test Organization

- Unit tests: keep narrow behavior tests near existing domain folders such as
  `tests/parser`, `tests/semantics`, and `tests/pyi`.
- Regression tests: add focused tests next to the subsystem that failed. Mark
  with `@pytest.mark.regression` when useful.
- Property tests: put generated invariant tests in `tests/property`.
- Fuzz-like parser tests: keep bounded generators in `tests/property`, mark
  with `@pytest.mark.fuzz`, and run with the `fuzz` Hypothesis profile.

Good invariants for this codebase:

- parsing the same source twice produces the same JSON/dict representation;
- generated declarations preserve name order and source locations;
- semantic conversion is deterministic for equivalent parser models;
- Pyi emission can be parsed back into equivalent semantic IR for supported
  subsets;
- malformed input raises parser-owned diagnostic exceptions, not arbitrary
  exceptions.

## Adoption Status

Full adoption for the selected stack means:

- fast PR gates are blocking and stable;
- scheduled/manual fuzzing and changing random-order jobs exist;
- Ruff baseline ignores are removed or deliberately retained with a reason;
- Radon has a documented blocking policy for new or materially changed code;
- scheduled workflow failures have a documented triage path.

Current status by area:

| Area | Status | Explanation |
| --- | --- | --- |
| Fast pull-request gates | Complete for adoption | Tests, coverage, Ruff, Bandit, pip-audit, Vulture, and staged Radon are wired as blocking gates. |
| Property and fuzz testing | Complete for adoption | Current parser, AST, semantic-IR, and code-generation invariants exist; future failures still need regression tests. |
| Dead-code detection | Complete for adoption | Vulture is clean and blocking; future public API additions should keep exclusions narrow. |
| Security and dependency scanning | Complete for adoption | Bandit and pip-audit are blocking; low-severity and dependency reviews recur when related code changes. |
| Complexity tracking | Complete for adoption | The staged Radon policy is blocking in CI; future hotspot decomposition can ratchet thresholds further. |
| Scheduled workflow triage | Complete for adoption | Jobs exist and the triage process is documented; scheduled failures remain ordinary maintenance. |

Ongoing maintenance:

1. Review scheduled workflow results regularly and record actionable failures
   until fixed.
2. Lower Ruff/Radon complexity thresholds after hotspot refactors make that
   safe.

## Scheduled Workflow Triage

The `Quality` workflow runs deeper discovery jobs every Monday and by manual
dispatch:

1. Re-run a failing job once to separate actionable failures from transient
   runner or package-index failures.
2. Reproduce actionable fuzz failures with the logged Hypothesis profile and
   save minimized examples as focused regression tests.
3. Reproduce random-order failures with the logged `--randomly-seed` value and
   add a regression test before fixing leaked state.
4. Record each actionable scheduled failure here or in the relevant issue until
   the regression test and fix pass.

## Progress Log

| Date | Area | Result | Follow-up |
| --- | --- | --- | --- |
| 2026-05-31 | Initial stack integration | Added configuration, CI, documentation, and Hypothesis tests. | Continue staged strictness rollout. |
| 2026-05-31 | Bandit | Reviewed low-severity findings and confirmed no medium- or high-severity findings. | Re-review when command trust boundaries change. |
| 2026-05-31 | Hypothesis code generation | Added generated native-name escaping, stable synthetic-import ordering, and semantic-IR-to-Pyi parse-back invariants; fixed quoted `Name(...)` emission. | Keep storing minimized failures. |
| 2026-06-01 | Ruff formatting rollout | Formatted the historical Python tree and changed CI to `ruff format --check .`. | Continue complexity-policy ratchets. |
| 2026-06-01 | Radon and Ruff complexity policy | Added `tools/check_radon_policy.py`, made the staged Radon policy blocking in CI, and lowered Ruff McCabe from `50` to `45`. | Continue hotspot refactors and later threshold ratchets toward `20`. |
| 2026-06-02 | Historical mutation-derived tests | Added direct Fortran parser contracts and fixed the directory namespace encoding bug. | Keep the tests as normal regression coverage. |
| 2026-06-03 | Manual Quality workflow review | Reviewed workflow run `26832679820`: fuzz passed, changing random-order pytest passed, static analysis exposed Ruff fixes, and full-project mutation exceeded the `3h` Actions limit. | Mutation was removed from active adoption; keep scheduled fuzz/random-order review. |
| 2026-06-03 | Quality workflow triage | Reviewed latest Quality runs; run `26856679038` for `remove mutmut` completed successfully. | No actionable scheduled or PR quality failure remains. |
| 2026-06-03 | Final active-stack cleanup | Consolidated quality docs, removed mutation and pre-commit from the active stack, restored the C parser golden generator, and regenerated C parser goldens. | Treat scheduled review and threshold ratchets as ongoing maintenance. |

## References

- Ruff configuration: https://docs.astral.sh/ruff/configuration/
- Pytest configuration: https://docs.pytest.org/en/latest/reference/customize.html
- Coverage subprocess behavior: https://coverage.readthedocs.io/en/latest/config.html
- Hypothesis settings profiles: https://hypothesis.readthedocs.io/en/latest/tutorial/settings.html
- Vulture configuration: https://pypi.org/project/vulture/
- Radon command line: https://radon.readthedocs.io/en/stable/commandline.html
- Bandit configuration: https://bandit.readthedocs.io/en/latest/config.html
- pip-audit: https://github.com/pypa/pip-audit
- pytest-randomly: https://github.com/pytest-dev/pytest-randomly
