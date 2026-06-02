# Quality Tool Retention Report

Last reviewed: 2026-06-02

## Purpose

This report records the value, evidence, and recommended steady-state cadence
for the Python QA tools adopted on the `tools` branch. It is a merge decision
report, not a claim that the rollout is finished. The remaining adoption work is
tracked in the [quality stack adoption checklist](quality_adoption_checklist.md).

## Executive Decision

Keep the full QA stack. The tools have different jobs and should not all run at
the same frequency:

| Cadence | Tools |
| --- | --- |
| Every pull request and protected-branch push | pytest, coverage.py, pytest-xdist, stable-seed pytest-randomly, Ruff, Bandit, pip-audit, Vulture, staged Radon policy |
| Every commit through pre-commit | Ruff format, Ruff lint with fixes, Bandit, staged Radon policy |
| Weekly and manual dispatch | Hypothesis fuzz profile, changing-seed pytest-randomly |
| Manual after behavior or assertion changes | Focused mutmut campaigns through `tools/run_mutmut.py` |
| Manual during scheduled triage | Full Radon reports |

Mutmut should not run on every commit or pull request. Use focused campaigns
before merging risky parser, semantic, preprocessing, or code-generation
changes. Run broader subsystem refreshes periodically and a full-project manual
GitHub Actions campaign after subsystem baselines are stable. A yearly
full-project deep audit is reasonable after that baseline exists.

## Evidence Summary

- Full local pytest baseline: `3497 passed`.
- CI-shaped combined branch coverage baseline: `95.34%`, above the configured
  `95%` floor.
- Ruff lint and full-tree formatting checks pass with no baseline ignore
  families left. Line length remains intentionally unselected.
- Vulture reports no findings after dead Fortran parser parameters were removed.
- Bandit reports `20` reviewed low-severity findings and no medium- or
  high-severity findings.
- pip-audit reports no known vulnerabilities for the current dependency set.
- Radon's staged policy protects a reviewed hotspot average ceiling of `19.01`
  and rejects changed production blocks above complexity `20`.
- The initial `fortran_parser/parser.py` campaign recorded `3233/5278` killed
  mutants, `745` survivors, and `1300` bounded-run timeouts. Its survivor review
  remains open.

The baseline numbers above were collected before this report was written. New
focused Fortran parser contract tests pass, but the full pytest and CI-shaped
coverage baselines have not been refreshed after those additions.

## Tool Decisions

### pytest And coverage.py

**Benefit:** pytest is the behavioral regression backbone. Coverage.py exposes
untested branches across worker and subprocess boundaries and enforces the
project's `95%` floor.

**Evidence:** the recorded full suite is `3497 passed`; combined branch
coverage is `95.34%`. The workflow correctly runs with
`COVERAGE_PROCESS_START=pyproject.toml`, combines parallel data, and reports
after xdist workers and subprocesses finish.

**Bugs or gaps found:** coverage guided focused tests toward weak parser,
semantic, and preprocessing branches. Treat its percentage as a floor, not as
a substitute for behavioral assertions.

**Decision:** keep blocking on every pull request and protected-branch push.

### pytest-xdist

**Benefit:** parallel workers keep the broad suite practical in CI and exercise
test isolation.

**Evidence:** CI runs pytest with `-n auto`, and parallel coverage data combines
successfully. This report does not claim a measured before/after speedup because
no controlled runtime comparison was recorded.

**Bugs or gaps found:** no known parallel-only regression remains.

**Decision:** keep in CI. Prefer serialized local runs when workstation
responsiveness matters.

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

**Evidence:** the CI profile passes; the fuzz profile passed `1000` C and `1000`
Fortran generated fragments without unexpected exceptions.

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

**Bugs or gaps found:** Ruff primarily removed static-risk and maintenance debt.
Do not overstate style findings as runtime defects.

**Decision:** keep on commit and as a blocking pull-request gate. Continue
reviewed rule-family and complexity ratchets.

### Bandit

**Benefit:** flags Python security-sensitive patterns, especially subprocess,
filesystem, deserialization, and credential-like literals.

**Evidence:** no medium- or high-severity findings. The full report has `20`
reviewed low-severity findings: parser sentinel/template tokens and intentional
argv-based compiler or preprocessor subprocess calls without shell execution.

**Bugs or gaps found:** no exploitable issue was identified. The reviewed
findings document trust boundaries that must be revisited when command
construction changes.

**Decision:** keep blocking at medium confidence/severity on commit and in CI.
Re-run the full low-severity review after subprocess-boundary changes.

### pip-audit

**Benefit:** checks installed project dependencies against Python advisory data.

**Evidence:** no known vulnerability is present in the current dependency set.

**Bugs or gaps found:** none in the current dependency set.

**Decision:** keep blocking in CI and re-run locally whenever dependencies
change. It does not belong on every commit because dependency resolution and
advisory access are network-dependent.

### Vulture

**Benefit:** identifies likely unused code and unreachable definitions.

**Evidence:** the report is clean after narrowing exclusions and removing dead
Fortran parser parameters.

**Bugs or gaps found:** dead parser parameters were removed.

**Decision:** keep blocking in CI. Keep it manual in pre-commit to avoid slowing
the normal commit loop.

### Radon

**Benefit:** identifies high-complexity hotspots so refactoring and focused
tests are directed at risky control flow.

**Evidence:** the reviewed average is `C (18.95)`. The custom staged gate caps
the C-or-worse hotspot average at `19.01` and changed production blocks at
complexity `20`.

**Bugs or gaps found:** Radon found maintainability hotspots, not a specific
runtime defect.

**Decision:** keep `tools/check_radon_policy.py` blocking on commit and in CI.
Keep full Radon reports advisory/manual and ratchet thresholds after focused
refactors.

### mutmut

**Benefit:** proves whether tests fail when implementation behavior changes. It
has been the most effective tool for finding weak assertions in parser,
semantic, preprocessing, and code-generation code.

**Evidence:** reviewed subsystem baselines are recorded in the checklist.
Examples include `204/204` killed for `c_parser/type_resolver.py`,
`1785/1821` killed for `semantics/c2ir.py`, and `1496/1564` killed for
`x2py/preprocessing.py`. The remaining `fortran_parser/parser.py` review added
`55` direct contract tests; a bounded selected rerun killed `86/151` prior
survivors.

**Bugs or gaps found:** mutation review exposed and fixed duplicate typedef-cycle
diagnostics, made union-by-value diagnostics cycle-safe, and found that Fortran
project directory namespace collection ignored the requested source encoding
during its first pass. It also exposed missing exact assertions for
diagnostics, forwarding, registries, ownership, provenance, source locations,
boundaries, and loop progress.

**Decision:** keep as focused manual discovery tooling. Do not run it on every
commit or pull request. Keep local parser runs serialized with
`--max-children 1` and an outer timeout; use manual GitHub Actions for broad
refreshes.

### pre-commit

**Benefit:** shortens feedback time before CI.

**Evidence:** commit hooks run Ruff format, Ruff lint, Bandit, and the staged
Radon policy. Vulture and full Radon reports remain available as manual hooks.

**Decision:** keep. Avoid adding expensive or network-dependent checks to the
commit stage.

### GitHub Actions

**Benefit:** provides clean reproducible environments for blocking gates and
scheduled discovery work.

**Evidence:** `tests.yml` runs pytest, xdist, stable-seed pytest-randomly,
subprocess-aware coverage, and Codecov upload on Python `3.10`, `3.11`, and
`3.12`. `quality.yml` runs blocking static gates on pull requests and pushes,
plus weekly/manual fuzz and changing-seed jobs. Mutation remains manual.

**Bugs or gaps found:** scheduled workflow history could not be verified from
this session because the local `gh` credential is expired and remote read
access was unavailable. Regular scheduled triage remains an explicit adoption
gap.

**Decision:** keep. Review scheduled results after each weekly execution and
record actionable failures in the checklist.

## Repository Helpers

| Helper | Benefit | Decision |
| --- | --- | --- |
| `tools/run_mutmut.py` | Works around mutmut 3.5.0 child-process reaping behavior, joins generation workers, and prevents process-local stats instrumentation from leaking into fresh CLI subprocesses. | Keep while the pinned-compatible mutmut range needs the workaround; re-evaluate after mutmut upgrades. |
| `tools/check_radon_policy.py` | Converts advisory complexity output into a staged regression policy without forcing broad parser rewrites. | Keep blocking. |

## Existing Non-QA Integrations

The repository also contains opt-in CodeRabbit review configuration and an
`@claude` GitHub Actions workflow. They are review-assistance integrations, not
part of the deterministic Python QA gate. Keep or remove them according to
repository-maintainer preference; this adoption report does not use them as
evidence that code is correct.

## Remaining Before Full Adoption

1. Complete `fortran_parser/parser.py` survivor classification.
2. Run the full-project manual mutation campaign after subsystem baselines are
   stable.
3. Verify scheduled workflow results regularly and record actionable failures.
4. Continue deliberate Radon threshold reductions as hotspots are refactored.
