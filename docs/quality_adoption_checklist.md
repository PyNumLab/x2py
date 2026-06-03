# Quality Stack Adoption Checklist

This file tracks the staged adoption of the Python quality stack. Update it
whenever a QA task is completed, a new gap is discovered, or a tool is made
stricter. Do not mark an item complete without a passing command, reviewed
report, or merged configuration change.

The recurring checks remain required after adoption is complete. The adoption
sections track the finite work needed to reach the intended steady state.

Last reviewed: 2026-06-03

## General Goal

Adopt a practical, production-quality Python QA stack that reduces real bugs
and makes regressions easier to detect without adding unnecessary complexity or
static typing requirements.

The completed stack should:

- detect parser, compiler, AST, semantic-IR, and code-generation regressions;
- generate and preserve edge cases that hand-written examples may miss;
- identify dead code, suspicious patterns, unsafe behavior, dependency
  vulnerabilities, and maintainability risks;
- detect hidden test-order regressions;
- keep fast, stable checks blocking on pull requests while running expensive
  fuzzing work on schedules or manual dispatch;
- ratchet strictness gradually so historical debt is reduced without obscuring
  meaningful failures.

## Full Adoption Exit Criteria

The quality stack should be treated as fully adopted when all of these are true:

- fast pull-request gates are blocking and stable for tests, coverage, Ruff,
  Bandit, pip-audit, Vulture, and the staged Radon policy;
- recurring deeper jobs exist for fuzzing and changing random-order tests;
- Ruff baseline ignores have either been removed or deliberately retained with
  a reason;
- Radon has a documented blocking policy for new or materially changed code;
- scheduled workflow failures have a documented triage path and actionable
  failures are recorded in this checklist until fixed;
- `docs/quality.md` and this checklist explain the current gates, commands,
  remaining debt, and reasons for any non-blocking checks.

After these exit criteria are met, the unchecked items that remain should be
conditional maintenance reminders only, such as re-running Bandit after a
subprocess change or re-running pip-audit after dependency changes.

## How To Use This Checklist

For every parser, compiler, AST, semantic-IR, or code-generation change:

- [ ] Run focused unit and regression tests for the changed subsystem.
- [ ] Run the CI-shaped pytest and coverage workflow when the change can affect
      subprocesses, parsing, semantic conversion, or generated output.
- [ ] Run the relevant Hypothesis property tests.
- [ ] Review Vulture and Radon output when functions, classes, or control flow
      changed.
- [ ] Run Bandit when subprocess, filesystem, deserialization, or execution
      behavior changed.
- [ ] Run pip-audit when dependencies changed.
- [ ] Update this checklist with newly completed work and newly discovered
      debt.

Use the commands and workflow explanations in
[`quality.md`](quality.md). Keep expensive checks focused locally; scheduled
GitHub Actions jobs provide broader repeated coverage.

## Current Baseline

Fully validated locally on 2026-05-31. Ruff lint/formatting and full pytest
were refreshed on 2026-06-01. The remote Quality workflow passed on
2026-06-03 after mutation was removed from the active workflow.

- [x] Full pytest run: `3497 passed`.
- [x] Combined xdist and subprocess branch coverage: `95.34%`, above the
      configured `95%` gate.
- [x] Ruff lint and full-tree Ruff formatting checks pass.
- [x] Vulture reports no current findings.
- [x] Bandit reports no medium- or high-severity findings.
- [x] pip-audit reports no known dependency vulnerabilities.
- [x] Hypothesis CI profile passes all current property tests.
- [x] Hypothesis fuzz profile passes generated C and Fortran fragments without
      unexpected exceptions.
- [x] Radon baseline reviewed: average complexity is `C (18.95)`.
- [x] Historical mutation-derived fixes and regression tests are retained as
      normal tests, but `mutmut` is no longer part of the active stack.

## Remaining Adoption Estimate

Current estimate with mutation testing removed from active adoption: **about
1-2% of the active rollout work remains**, so the quality stack is **about
98-99% adopted by effort** for the currently active tool rollout.

This is an effort-weighted estimate, not a simple checkbox percentage. The
recurring checks in "How To Use This Checklist" are excluded because they are
ongoing practice, not finite rollout work. The current-baseline evidence bullets
are also excluded because they record validation results rather than adoption
tasks.

Current status by area:

| Area | Status | Explanation |
| --- | --- | --- |
| Fast pull-request gates | Complete for adoption | Tests, coverage, Ruff, Bandit, pip-audit, Vulture, and staged Radon are wired as blocking gates. |
| Property and fuzz testing | Mostly complete | Current parser, AST, semantic-IR, and code-generation invariants exist; future failures still need regression tests. |
| Dead-code detection | Complete for adoption | Vulture is clean and blocking; future public API additions should keep exclusions narrow. |
| Security and dependency scanning | Complete for adoption | Bandit and pip-audit are blocking; low-severity and dependency reviews recur when related code changes. |
| Complexity tracking | Mostly complete | The staged Radon policy is blocking in CI; future hotspot decomposition can ratchet thresholds further. |
| Scheduled workflow triage | Partially complete | Jobs exist; regular review and actionable-failure recording still need to become routine. |

Estimated share of the remaining work:

| Area | Share of Remaining Work | Why |
| --- | ---: | --- |
| Ruff and Radon strictness ratchets | `35%` | Later complexity reductions need careful tightening without noisy parser rewrites. |
| Scheduled workflow review process | `45%` | The manual Quality run proved fuzz and changing random-order jobs pass; future scheduled failures still need routine triage. |
| Conditional maintenance checks | `20%` | Bandit, pip-audit, coverage, and xdist follow-ups are mostly complete, but remain active when related code changes. |

Priority order for reducing the remaining percentage:

1. Lower complexity thresholds as hotspot refactors make that safe.
2. Review scheduled workflow results regularly and add actionable failures to
   this checklist until fixed.

Update this estimate when a new CI gate is made blocking or a scheduled
workflow failure adds new actionable debt.

## Ruff

What it does: Ruff is a fast Python linter and formatter. It finds static code
problems such as undefined names, unused imports, suspicious patterns, and
overly complex functions, and it gives the Python tree one consistent format.

- [x] Install Ruff through the `qa` optional dependency.
- [x] Configure bug-focused lint families and Ruff formatting.
- [x] Run `ruff check .` in CI.
- [x] Require Ruff formatting in CI.
- [x] Remove reviewed baseline-ignore families.
- [x] Format the historical Python tree in a dedicated mechanical change.
- [x] Keep line-length diagnostics intentionally unselected.
- [x] Lower `tool.ruff.lint.mccabe.max-complexity` from `50` to `45`.
- [x] Define a stricter complexity policy for new or materially changed
      functions without forcing unrelated parser rewrites.

## Hypothesis

What it does: Hypothesis is a property-based testing library. It generates many
inputs from declared strategies and shrinks a failing input to a small
reproducer.

- [x] Configure `dev`, `ci`, and `fuzz` profiles.
- [x] Add a dedicated `tests/property` test directory.
- [x] Run bounded fuzz tests on a schedule and by manual dispatch.
- [x] Cover generated C and Fortran parser cases.
- [x] Add AST, semantic-IR, and code-generation invariants.
- [x] Store each meaningful minimized failure as a regression test.

## Vulture

What it does: Vulture finds likely unused functions, classes, variables,
imports, and unreachable code.

- [x] Install Vulture through the `qa` optional dependency.
- [x] Configure project paths and narrow exclusions.
- [x] Remove dead Fortran parser parameters.
- [x] Remove unused test lambda parameters reported by CI.
- [x] Run Vulture in the Quality workflow as a blocking check.

## Radon

What it does: Radon reports cyclomatic complexity and maintainability metrics.

- [x] Install Radon through the `qa` optional dependency.
- [x] Add `tools/check_radon_policy.py`.
- [x] Run the staged Radon policy in CI as a blocking check.
- [x] Keep full Radon reports advisory.
- [x] Allow unchanged legacy hotspots while blocking new or worsened changed
      production hotspots.
- [ ] Ratchet thresholds downward after focused hotspot refactors.

## Bandit

What it does: Bandit scans Python code for security-sensitive patterns.

- [x] Install Bandit through the `qa` optional dependency.
- [x] Run Bandit in CI with medium severity and medium confidence gates.
- [x] Review low-severity findings.
- [ ] Re-review when subprocess, filesystem, deserialization, or execution
      behavior changes.

## pip-audit

What it does: pip-audit checks installed dependencies for known vulnerabilities.

- [x] Install pip-audit through the `qa` optional dependency.
- [x] Run pip-audit in CI.
- [x] Record that the current dependency set has no known vulnerabilities.
- [ ] Re-run and review when dependencies change.

## pytest-randomly

What it does: pytest-randomly randomizes test order and controls random seeds.

- [x] Install and run pytest-randomly in the normal CI suite.
- [x] Use a stable CI seed for reproducible pull-request failures.
- [x] Run a changing seed in the scheduled/manual quality workflow.
- [x] Document how to reproduce a failing seed locally.
- [ ] Review scheduled failures and add regression tests for every discovered
      ordering dependency.

## pytest-xdist

What it does: pytest-xdist distributes pytest tests across worker processes.

Project status: xdist is reliable in CI, but there is no recorded controlled
before/after runtime comparison. Do not claim a measured speedup until a serial
versus parallel timing comparison is collected.

- [x] Install pytest-xdist through the `qa` optional dependency.
- [x] Run the normal CI suite with `-n auto`.
- [x] Combine parallel coverage data before reporting.
- [ ] Record a controlled timing comparison if speedup evidence is needed.
- [ ] Record and fix any future parallel-only regression.

## GitHub Actions

What it does: GitHub Actions runs the reproducible CI gates.

- [x] Run the test workflow on Python `3.10`, `3.11`, and `3.12`.
- [x] Run the Quality workflow static gates on pull requests and pushes.
- [x] Run scheduled/manual fuzzing.
- [x] Run scheduled/manual changing-seed test order.
- [x] Remove mutation testing from the active workflow after the 2026-06-02
      full-project run exceeded the `3h` Actions limit.
- [ ] Review scheduled runs and record actionable failures until fixed.

## Historical Mutation Evidence

Mutation testing was useful during the rollout, but it is no longer an adopted
tool. Keep the ordinary tests and fixes that came from it:

- duplicate typedef-cycle diagnostic coverage;
- cycle-safe union-by-value diagnostics;
- Fortran project namespace collection respecting the requested encoding;
- direct Fortran parser contracts for diagnostics, forwarding, registries,
  ownership, provenance, source locations, boundaries, and loop progress.

Future mutation testing can be run as an occasional external audit, for example
annually, without keeping `mutmut` in the normal dependency set or CI workflow.

## Progress Log

| Date | Area | Result | Follow-up |
| --- | --- | --- | --- |
| 2026-05-31 | Initial stack integration | Added configuration, CI, documentation, and Hypothesis tests. | Continue staged strictness rollout. |
| 2026-05-31 | Bandit | Reviewed low-severity findings and confirmed no medium- or high-severity findings. | Re-review when command trust boundaries change. |
| 2026-05-31 | Hypothesis code generation | Added generated native-name escaping, stable synthetic-import ordering, and semantic-IR-to-Pyi parse-back invariants; fixed quoted `Name(...)` emission. | Keep storing minimized failures. |
| 2026-06-01 | Ruff formatting rollout | Formatted the historical Python tree and changed CI to `ruff format --check .`. | Continue complexity-policy ratchets. |
| 2026-06-01 | Radon and Ruff complexity policy | Added `tools/check_radon_policy.py`, made the staged Radon policy blocking in CI, and lowered Ruff McCabe from `50` to `45`. | Continue hotspot refactors and later threshold ratchets toward `20`. |
| 2026-06-02 | Historical mutation-derived tests | Added direct Fortran parser contracts and fixed the directory namespace encoding bug. | Keep the tests as normal regression coverage. |
| 2026-06-03 | Manual Quality workflow review | Reviewed workflow run `26832679820`: fuzz passed, changing random-order pytest passed, static analysis exposed Ruff fixes, and full-project mutation exceeded the `3h` Actions limit. | Remove mutation from active adoption and keep scheduled fuzz/random-order review. |
