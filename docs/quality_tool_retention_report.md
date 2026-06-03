# Quality Tool Retention Report

Last reviewed: 2026-06-03

## Purpose

This report records the value, evidence, and recommended steady-state cadence
for the Python QA tools adopted on the `tools` branch. It excludes plain
pytest and coverage.py because those are already baseline project requirements.

## Executive Decision

Keep the active QA stack focused on tools that are useful on regular project
work. Mutation testing is removed from the adopted stack and kept only as an
occasional external audit idea.

| Cadence | Tools |
| --- | --- |
| Every pull request and protected-branch push | pytest-xdist, stable-seed pytest-randomly, Ruff, Bandit, pip-audit, Vulture, staged Radon policy |
| Weekly and manual dispatch | Hypothesis fuzz profile, changing-seed pytest-randomly |
| Manual during scheduled triage | Full Radon reports |

## Evidence Summary

- Ruff lint and full-tree formatting checks pass with no baseline ignore
  families left. Line length remains intentionally unselected.
- Vulture reports no findings after dead Fortran parser parameters and unused
  test lambda parameters were removed.
- Bandit reports reviewed low-severity findings and no medium- or high-severity
  findings.
- pip-audit reports no known vulnerabilities for the current dependency set.
- Radon's staged policy protects a reviewed hotspot average ceiling of `19.01`
  and rejects new or worsened changed production blocks above complexity `20`.
- Hypothesis fuzzing has produced useful parser/code-generation regressions and
  currently passes the scheduled/manual fuzz profile.
- `pytest-xdist` is reliable in CI, but no controlled before/after runtime
  comparison has been recorded, so there is no measured speedup claim.

## Tool Decisions

### pytest-xdist

**Benefit:** parallel workers keep the broad suite practical in CI and exercise
test isolation.

**Evidence:** CI runs pytest with `-n auto`, and parallel coverage data combines
successfully. No controlled runtime comparison was recorded, so the project
does not currently have evidence that xdist improved total test runtime.

**Bugs or gaps found:** no known parallel-only regression remains.

**Decision:** keep in CI if the parallel run remains stable. If the extra
dependency is not worth it, it is safe to remove at the cost of slower CI and
less test-isolation pressure.

### pytest-randomly

**Benefit:** stable and changing seeds detect leaked shared state and make
order-dependent failures reproducible.

**Evidence:** normal CI uses `--randomly-seed=1`; weekly/manual quality runs use
`${{ github.run_id }}` as a changing seed.

**Bugs or gaps found:** no known order-dependent tests remain.

**Decision:** keep the stable seed in pull-request CI and the changing seed in
the weekly/manual workflow.

### Hypothesis

**Benefit:** generated examples exercise parser, AST, semantic-IR, and
code-generation invariants that are expensive to enumerate by hand.

**Evidence:** the CI profile passes; the fuzz profile passed generated C and
Fortran fragments without unexpected exceptions.

**Bugs or gaps found:** generated code-generation cases exposed quoted
`Name(...)` emission, and focused regressions were stored. Generated
preprocessing inputs also aligned raw Fortran and C macro handling around
compiler-required errors.

**Decision:** keep bounded properties in normal tests and the longer fuzz
profile weekly/manual.

### Ruff

**Benefit:** one fast tool enforces formatting and finds undefined names,
unused imports, suspicious patterns, modernization opportunities, simplified
control flow, and very high McCabe complexity.

**Evidence:** Ruff lint and full-tree formatting checks pass. Historical ignore
families were removed in staged batches; McCabe was lowered from `50` to `45`.

**Bugs or gaps found:** Ruff found raw-regex issues, formatting drift, and
maintenance debt. Treat these as static-risk findings, not runtime defects.

**Decision:** keep as a blocking pull-request gate.

### Bandit

**Benefit:** flags Python security-sensitive patterns, especially subprocess,
filesystem, deserialization, and credential-like literals.

**Evidence:** no medium- or high-severity findings. The reviewed low-severity
findings are parser sentinel/template tokens and intentional argv-based
compiler or preprocessor subprocess calls without shell execution.

**Bugs or gaps found:** no exploitable issue was identified. The reviewed
findings document trust boundaries that must be revisited when command
construction changes.

**Decision:** keep blocking at medium confidence/severity in CI. Re-run the
full low-severity review after subprocess-boundary changes.

### pip-audit

**Benefit:** checks installed project dependencies against Python advisory data.

**Evidence:** no known vulnerability is present in the current dependency set.

**Bugs or gaps found:** none in the current dependency set.

**Decision:** keep blocking in CI and re-run locally whenever dependencies
change.

### Vulture

**Benefit:** identifies likely unused code and unreachable definitions.

**Evidence:** the report is clean after narrowing exclusions and removing dead
Fortran parser parameters.

**Bugs or gaps found:** dead parser parameters and unused test lambda
parameters were removed.

**Decision:** keep blocking in CI.

### Radon

**Benefit:** identifies high-complexity hotspots so refactoring and focused
tests are directed at risky control flow.

**Evidence:** the reviewed average is `C (18.95)`. The custom staged gate caps
the C-or-worse hotspot average at `19.01` and changed production blocks at
complexity `20` when they are new or worsened.

**Bugs or gaps found:** Radon found maintainability hotspots. It also exposed
that the first staged policy was too strict for unchanged legacy hotspots; the
policy now allows unchanged pre-existing hotspots.

**Decision:** keep `tools/check_radon_policy.py` blocking in CI. Keep full
Radon reports advisory/manual and ratchet thresholds after focused refactors.

### GitHub Actions

**Benefit:** provides clean reproducible environments for blocking gates and
scheduled discovery work.

**Evidence:** `tests.yml` runs the Python test matrix with xdist,
pytest-randomly, subprocess-aware coverage, and Codecov upload. `quality.yml`
runs blocking static gates on pull requests and pushes, plus weekly/manual fuzz
and changing-seed jobs.

**Bugs or gaps found:** recent remote quality runs found Ruff raw-regex issues,
Ruff formatting drift, Vulture unused test parameters, and a too-strict Radon
policy for unchanged legacy hotspots.

**Decision:** keep. Review scheduled results and record actionable failures in
the checklist.

## Historical Mutation Findings

Mutation testing found valuable bugs and assertion gaps during the rollout, but
it is no longer part of the active tool stack:

- duplicate typedef-cycle diagnostics were fixed;
- union-by-value diagnostics were made cycle-safe;
- Fortran project directory namespace collection was fixed to respect the
  requested source encoding during its first pass;
- direct parser regression tests now pin diagnostics, forwarding, registries,
  ownership, provenance, source locations, boundaries, and loop progress.

Keep those regression tests. Do not keep `mutmut` as a regular dependency,
workflow, or local wrapper. A future annual mutation audit can be done outside
the normal QA stack if needed.

## Repository Helpers

| Helper | Benefit | Decision |
| --- | --- | --- |
| `tools/check_radon_policy.py` | Converts advisory complexity output into a staged regression policy without forcing broad parser rewrites. | Keep blocking. |

## Remaining Before Full Adoption

1. Verify scheduled workflow results regularly and record actionable failures.
2. Continue deliberate Radon threshold reductions as hotspots are refactored.

With mutation removed from active adoption, the remaining non-baseline rollout
work is small: about `1-2%`, mainly routine scheduled-workflow review wording
and future threshold ratchets.
