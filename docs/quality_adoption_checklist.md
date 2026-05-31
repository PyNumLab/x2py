# Quality Stack Adoption Checklist

This file tracks the staged adoption of the Python quality stack. Update it
whenever a QA task is completed, a new gap is discovered, or a tool is made
stricter. Do not mark an item complete without a passing command, reviewed
report, or merged configuration change.

The recurring checks remain required after adoption is complete. The adoption
sections track the finite work needed to reach the intended steady state.

Last reviewed: 2026-05-31

## General Goal

Adopt a practical, production-quality Python QA stack that reduces real bugs
and makes regressions easier to detect without adding unnecessary complexity or
static typing requirements.

The completed stack should:

- detect parser, compiler, AST, semantic-IR, and code-generation regressions;
- generate and preserve edge cases that hand-written examples may miss;
- expose weak tests through focused mutation testing;
- identify dead code, suspicious patterns, unsafe behavior, dependency
  vulnerabilities, and maintainability risks;
- detect hidden test-order and performance regressions;
- keep fast, stable checks blocking on pull requests while running expensive
  fuzzing, mutation, and benchmark work on schedules or manual dispatch;
- ratchet strictness gradually so historical debt is reduced without obscuring
  meaningful failures.

## How To Use This Checklist

For every parser, compiler, AST, semantic-IR, or code-generation change:

- [ ] Run the fast pre-commit checks.
- [ ] Run focused unit and regression tests for the changed subsystem.
- [ ] Run the CI-shaped pytest and coverage workflow when the change can affect
      subprocesses, parsing, semantic conversion, or generated output.
- [ ] Run the relevant Hypothesis property tests.
- [ ] Run a focused mutmut campaign when behavior or assertions changed.
- [ ] Review Vulture and Radon output when functions, classes, or control flow
      changed.
- [ ] Run Bandit when subprocess, filesystem, deserialization, or execution
      behavior changed.
- [ ] Run pip-audit when dependencies changed.
- [ ] Run benchmarks when parser, semantic conversion, or code-generation hot
      paths changed.
- [ ] Update this checklist with newly completed work and newly discovered
      debt.

Use the commands and workflow explanations in
[`quality.md`](quality.md). Keep expensive checks focused locally; scheduled
GitHub Actions jobs provide broader repeated coverage.

## Current Baseline

Validated locally on 2026-05-31:

- [x] Full CI-shaped pytest run: `3474 passed`.
- [x] Combined xdist and subprocess branch coverage: `95.31%`, above the
      configured `95%` gate.
- [x] Ruff lint and changed-file Ruff formatting checks pass.
- [x] Pre-commit hooks pass.
- [x] Vulture reports no current findings.
- [x] Bandit reports no medium- or high-severity findings.
- [x] pip-audit reports no known dependency vulnerabilities.
- [x] Hypothesis CI profile passes all current property tests.
- [x] Hypothesis fuzz profile passes `1000` C and `1000` Fortran generated
      fragments without unexpected exceptions.
- [x] Parser benchmarks pass; local means are approximately `33-34 ms`.
- [x] Focused `c_parser/type_resolver.py` mutation campaign completed.
      Assertions and implementation fixes improved the result from `142/206`
      killed mutants to `174/215`, followed by targeted kills for six more
      survivors.
- [x] Radon baseline reviewed: average complexity is `C (19.01)`.

## Ruff

Goal: hard-gate likely bugs now, then remove historical formatting and lint
debt in controlled batches.

Adoption target:

- `ruff check .` reports zero findings.
- `ruff format --check .` passes for the entire Python tree.
- Baseline ignores are removed one family at a time until only reviewed,
  documented exceptions remain.
- New or materially changed functions stay at cyclomatic complexity `20` or
  below unless a narrow exception is documented.

Why: zero enabled-rule findings and whole-tree formatting make Ruff a
predictable gate. The complexity limit prevents new debt while historical
parser functions are improved incrementally.

- [x] Install Ruff through the `qa` optional dependency.
- [x] Configure bug-focused lint families and Ruff formatting.
- [x] Run `ruff check .` in CI.
- [x] Run Ruff lint and formatting in pre-commit.
- [x] Require Ruff formatting for changed Python files in CI.
- [x] Remove the first safe baseline-ignore families: `B009`, `C420`, `F402`,
      and `UP035`.
- [ ] Format the historical Python tree in a dedicated mechanical change.
- [ ] Change CI from changed-file formatting to `ruff format --check .`.
- [ ] Review and remove baseline ignores one rule family at a time.
- [ ] Lower `tool.ruff.lint.mccabe.max-complexity` from `50` toward `20`.
- [ ] Define a stricter complexity policy for new or materially changed
      functions without forcing unrelated parser rewrites.

## Hypothesis

Goal: generate edge cases and validate invariants across parsers,
transformations, and code generation.

Adoption target:

- Every parser, AST, semantic-IR, and code-generation subsystem has at least
  one property, metamorphic, or round-trip invariant where the behavior allows
  one.
- Pull-request CI runs `250` examples per property through the `ci` profile.
- Scheduled fuzzing runs at least `1000` generated fragments per parser.
- Every meaningful minimized failure is stored as a focused regression test.

Why: fixed examples cover known behavior, while generated examples explore
combinations and boundaries that are easy to miss in parser/compiler code.
Saving minimized failures prevents rediscovery of the same bug.

- [x] Configure `dev`, `ci`, and `fuzz` profiles.
- [x] Add a dedicated `tests/property` test directory.
- [x] Run bounded fuzz tests on a schedule and by manual dispatch.
- [x] Cover basic C generated prototypes, deterministic JSON, and whitespace
      metamorphism.
- [x] Cover basic Fortran generated subroutines, argument order, case
      metamorphism, and parse-to-semantic-to-Pyi round trips.
- [x] Check that arbitrary bounded C and Fortran fragments only raise
      parser-owned errors.
- [x] Add generated C nested declarators: pointers, arrays, callbacks, and
      composed types.
- [x] Add generated C preprocessing cases: raw directive rejection,
      linemarkers, includes, and compiler extensions.
- [x] Add generated Fortran module, derived-type, kind, include, and
      preprocessor cases.
- [ ] Add AST and semantic-IR transformation invariants.
- [ ] Add code-generation escaping, stable-ordering, and parse-back invariants.
- [ ] Store each meaningful minimized Hypothesis failure as a regression test.

## Mutmut

Goal: find weak tests by proving that meaningful implementation mutations are
killed by behavioral assertions.

Adoption target:

- Every subsystem in the mutation progress table receives a focused campaign.
- Every survivor is reviewed and classified as killed by a new assertion,
  fixed as a real bug, or documented as behaviorally equivalent.
- No meaningful survivor remains unexplained.
- Establish per-subsystem mutation-score baselines after review, then prevent
  unexplained score regressions. Do not use one arbitrary whole-project score
  as a substitute for survivor review.

Why: mutation scores are useful trend signals, but equivalent mutations can
survive without exposing a test weakness. The real quality goal is to eliminate
unexplained meaningful survivors.

- [x] Configure `tool.mutmut.paths_to_mutate`.
- [x] Add the manual GitHub Actions mutation job.
- [x] Add `tools/run_mutmut.py` to avoid the mutmut 3.5.0 child-process
      reaping failure observed locally.
- [x] Document focused local mutation workflow and survivor review.
- [x] Run the first focused campaign for `c_parser/type_resolver.py`.
- [x] Fix the discovered duplicate typedef-cycle diagnostic bug.
- [x] Add assertions for typedef resolution on variables and aggregate
      members.
- [x] Add assertions for unresolved `struct`, `union`, and `enum` references.
- [ ] Review the remaining meaningful `c_parser/type_resolver.py` survivors.
- [ ] Run focused mutation campaigns for each subsystem below.
- [ ] Record survivor decisions: add a test, fix a bug, or document why the
      mutation is behaviorally equivalent.
- [ ] Run a full-project manual GitHub Actions campaign after subsystem passes
      are stable.

Mutation subsystem progress:

| Subsystem | Initial Campaign | Meaningful Survivors Reviewed | Notes |
| --- | --- | --- | --- |
| `c_parser/type_resolver.py` | [x] | [ ] | Found duplicate cycle diagnostics and missing resolver assertions. |
| `c_parser/lexer.py` | [ ] | [ ] | Prioritize token boundaries and malformed input. |
| `c_parser/preprocessor.py` | [ ] | [ ] | Prioritize branch metadata and linemarkers. |
| `c_parser/parser.py` | [ ] | [ ] | Split into focused grammar areas to keep runs bounded. |
| `c_parser/models.py` | [ ] | [ ] | Prioritize stable serialization and cycle handling. |
| `fortran_parser/lexer.py` | [ ] | [ ] | Prioritize comments and continuation lines. |
| `fortran_parser/parser.py` | [ ] | [ ] | Split into declarations, units, preprocessing, and resolution. |
| `fortran_parser/type_resolver.py` | [ ] | [ ] | Prioritize kinds and dependency resolution. |
| `semantics/c2ir.py` | [ ] | [ ] | Prioritize AST-to-IR field mapping and blockers. |
| `semantics/fortran2ir.py` | [ ] | [ ] | Prioritize kinds, arrays, and compile-time values. |
| `semantics/pyi_parser.py` | [ ] | [ ] | Prioritize parse-back invariants. |
| `semantics/pyi_printer.py` | [ ] | [ ] | Prioritize escaping and stable ordering. |
| `semantics/readiness.py` | [ ] | [ ] | Prioritize blocker selection and diagnostics. |
| `x2py/preprocessing.py` | [ ] | [ ] | Prioritize external command and linemarker handling. |
| `x2py/cli.py` | [ ] | [ ] | Prioritize command routing and reports. |

## Vulture

Goal: remove dead code and make newly introduced dead definitions fail CI.

Adoption target:

- `vulture` reports zero findings at `min_confidence = 80`.
- CI remains blocking.
- Ignore patterns stay narrow and documented; broad naming exclusions are not
  added merely to silence a report.

Why: an 80% confidence threshold catches likely dead code without making the
gate noisy. A clean blocking baseline prevents unused code from accumulating
again.

- [x] Configure project paths and initial ignore patterns.
- [x] Run Vulture in GitHub Actions as an advisory report.
- [x] Add a manual pre-commit hook.
- [x] Remove the first confirmed dead parameters from the Fortran parser.
- [x] Reach a clean current Vulture report.
- [x] Review intentional public, visitor, and plugin-style APIs. Remove broad
      `_helper_*`, `visit_*`, and `__getattr__` exclusions; retain only pytest
      discovery names.
- [x] Make Vulture blocking in GitHub Actions.

## Radon

Goal: track risky control flow and reduce complexity where it improves
maintainability and regression resistance.

Adoption target:

- Immediate guardrail: do not worsen the current project average of
  `C (19.01)`.
- New or materially changed functions should remain at complexity `20` or
  below unless a reviewed exception is documented.
- Long-term ratchet: reduce the project average toward `15` and remove
  unreviewed `D`, `E`, and `F` hotspots through focused tests and gradual
  decomposition.
- Maintainability reports should not regress for changed modules; investigate
  modules graded below `B` when modifying them.

Why: Radon cyclomatic-complexity grades are `A = 1-5`, `B = 6-10`,
`C = 11-20`, `D = 21-30`, `E = 31-40`, and `F = 41+`. The current average is
near the top of `C`, so preventing regression is the first safe gate. Moving
toward `15` reduces branching risk without forcing a broad parser rewrite.

- [x] Configure cyclomatic-complexity and maintainability reports.
- [x] Run Radon reports in GitHub Actions as advisory output.
- [x] Add a manual pre-commit complexity report.
- [x] Record the initial average complexity baseline: `C (19.01)`.
- [x] Review the first high-complexity report.
- [x] Prioritize a small set of hotspots for focused tests and gradual
      decomposition.
- [ ] Decide the blocking policy: maximum complexity for new or materially
      changed functions, allowed exceptions, and ratchet schedule.
- [ ] Add the chosen blocking policy to CI.

Initial hotspot register:

| Hotspot | Current Action |
| --- | --- |
| `c_parser/lexer.py:split_top_level_c_source` | Added generated nested-comma and function-body delimiter properties; decompose only with these regressions pinned. |
| `c_parser/models.py:c_model_to_dict` | Expand serialization invariants before decomposition. |
| `c_parser/parser.py` normalization and old-style-definition checks | Refactor only alongside focused grammar tests. |
| `fortran_parser/parser.py:visit_file` and `visit_project` | Split only after unit and project traversal regressions are pinned. |
| `fortran_parser/cli.py:_format_report` | Extract formatting sections with output tests. |
| `semantics/fortran2ir.py:_iter_fortran_variable_contexts` | Add context-mapping tests before decomposition. |
| `x2py/cli.py:main` and `_build_preprocessing_config` | Extract routing/configuration helpers with CLI tests. |

## Bandit

Goal: block new medium- and high-confidence security risks and review lower
severity findings deliberately.

Adoption target:

- Blocking scan reports zero medium- or high-severity findings at medium or
  higher confidence.
- Low-severity findings are reviewed whenever subprocess, filesystem,
  deserialization, or execution trust boundaries change.
- Intentional findings remain visible or receive narrow, documented
  suppressions.

Why: the blocking threshold catches actionable security risks without failing
CI on parser sentinel strings or intentional argv-based compiler execution.
Low-severity review still matters when trust boundaries move.

- [x] Configure Bandit for production Python packages.
- [x] Run Bandit as a blocking CI check.
- [x] Run Bandit in pre-commit.
- [x] Verify no current medium- or high-severity findings.
- [x] Review low-severity findings and document intentional cases narrowly.
- [ ] Repeat low-severity review when subprocess, file, or execution behavior
      changes.

## Pip-Audit

Goal: fail CI when project dependencies have known vulnerabilities.

Adoption target:

- `pip-audit .` reports zero known vulnerabilities for the isolated project
  dependency set.
- CI remains blocking.
- Any temporary exception is documented with an owner, reason, and removal
  date.

Why: dependency vulnerabilities can appear after code is merged. A blocking
audit catches newly published advisories even when application code did not
change.

- [x] Install pip-audit through the `qa` optional dependency.
- [x] Audit the isolated project dependency set with `pip-audit .`.
- [x] Run pip-audit as a blocking CI check.
- [x] Verify the current dependency set has no known vulnerabilities.
- [ ] Re-run locally whenever dependencies change.

## Pytest-Randomly

Goal: detect hidden order dependence and make failures reproducible.

Adoption target:

- Stable-seed pull-request CI and changing-seed scheduled CI both pass.
- There are zero known order-dependent tests.
- Every discovered failure records its seed until a regression test and fix
  are merged.

Why: test-order failures usually reveal shared global state or incomplete
cleanup. Recording the seed turns an intermittent failure into a reproducible
one.

- [x] Install and run pytest-randomly in the normal CI suite.
- [x] Use a stable CI seed for reproducible pull-request failures.
- [x] Run a changing seed in the scheduled/manual quality workflow.
- [x] Document how to reproduce a failing seed locally.
- [ ] Review scheduled failures and add regression tests for every discovered
      ordering dependency.

## Pytest-Benchmark

Goal: detect meaningful parser and code-generation performance regressions
without introducing flaky gates.

Adoption target:

- Collect at least `10` successful GitHub Actions benchmark artifacts before
  selecting blocking thresholds.
- Cover representative generated workloads and add real-corpus workloads where
  they provide stable signal.
- Define per-benchmark thresholds from observed CI variance. As an initial
  review rule, investigate a median slowdown above `15%` and confirm it with a
  rerun before blocking a change.

Why: parser performance matters, but local and shared-runner timings vary.
Thresholds should be based on CI history so the gate catches meaningful
regressions without becoming flaky.

- [x] Install pytest-benchmark and register the benchmark marker.
- [x] Add a representative C parser benchmark.
- [x] Add a representative Fortran parse-to-semantic-to-Pyi benchmark.
- [x] Run benchmarks on a schedule and by manual dispatch.
- [x] Upload benchmark JSON from GitHub Actions.
- [ ] Collect enough GitHub Actions history to establish stable baselines.
- [ ] Add representative real-corpus benchmarks where they improve signal.
- [ ] Define regression thresholds and comparison workflow.
- [ ] Make stable regression thresholds blocking.

## Supporting Infrastructure

These are not additional analyzers, but the stack is incomplete without them.

### Pytest And Coverage

Goal: keep behavioral regression coverage broad and make subprocess execution
visible in the reported branch coverage.

Adoption target:

- The full test suite passes on supported Python versions.
- Combined branch coverage remains at or above `95%`.
- Meaningful changed branches receive focused tests; coverage-only assertions
  are not added merely to increase the percentage.

Why: the percentage is a regression floor, not a substitute for useful
assertions. Combining worker and subprocess data is required because this
project exercises compiler and preprocessing boundaries.

- [x] Run pytest in CI on Python `3.10`, `3.11`, and `3.12`.
- [x] Enable branch coverage.
- [x] Enable parallel coverage data for subprocess and xdist workers.
- [x] Combine coverage data before reporting.
- [x] Enforce `fail_under = 95`.
- [ ] Add focused tests when meaningful changed branches are not covered;
      avoid adding low-value tests solely to increase the percentage.

### Pytest-Xdist

Goal: keep the broad suite fast while proving that tests are isolated enough
to run concurrently.

Adoption target:

- The full suite passes with `pytest -n auto`.
- Parallel coverage files combine successfully.
- There are zero known tests that require serial execution because of leaked
  shared state; unavoidable external-resource constraints are documented
  narrowly.

Why: xdist reduces feedback time and exposes hidden shared-state assumptions.
It is fully adopted only when parallel execution is reliable, not merely
enabled.

- [x] Install pytest-xdist through the `qa` optional dependency.
- [x] Run the normal CI suite with `-n auto`.
- [x] Combine parallel coverage data before reporting.
- [ ] Record and fix any future parallel-only regression.

### Pre-Commit

Goal: catch fast, deterministic issues before CI.

Adoption target:

- Commit-stage hooks stay fast enough for normal local use and pass with zero
  findings.
- Expensive or report-oriented tools remain available as manual hooks.

Why: pre-commit should shorten feedback loops without encouraging developers
to bypass it because expensive analysis runs on every edit.

- [x] Run Ruff formatting, Ruff linting, and Bandit on commit.
- [x] Provide manual Vulture and Radon hooks.
- [ ] Decide whether any additional fast, stable check belongs on commit after
      the initial rollout settles.

### GitHub Actions

Goal: enforce stable quality gates on every pull request and run expensive
discovery checks often enough to find deeper regressions.

Adoption target:

- Pull-request and push workflows pass for tests, coverage, Ruff, Bandit,
  pip-audit, and Vulture.
- Scheduled/manual workflows run fuzzing, changing random seeds, benchmarks,
  and mutation testing at their documented cadence.
- Actionable scheduled failures are recorded in this checklist until fixed.

Why: separating fast blocking gates from heavier discovery workflows keeps
pull-request feedback practical while still exercising the deeper QA stack.

- [x] Keep fast blocking checks on pull requests and pushes.
- [x] Keep mutation testing manual because it is expensive.
- [x] Run fuzzing, changing random-order tests, and benchmarks on schedule or
      manual dispatch.
- [ ] Review scheduled workflow results regularly and record actionable
      failures in this checklist.

## Progress Log

Add a row when a QA adoption task or subsystem campaign is completed.

| Date | Area | Result | Follow-up |
| --- | --- | --- | --- |
| 2026-05-31 | Initial stack integration | Added configuration, CI, pre-commit, documentation, Hypothesis tests, and benchmarks. | Continue staged strictness rollout. |
| 2026-05-31 | Vulture | Removed dead Fortran parser parameters; report is clean. | Make blocking after API whitelist review. |
| 2026-05-31 | Mutmut: `c_parser/type_resolver.py` | Fixed duplicate typedef-cycle diagnostics and added resolver regression assertions. | Review remaining meaningful survivors and continue subsystem campaigns. |
| 2026-05-31 | Full validation | `3437 passed`, combined coverage `95.13%`, security and dependency scans clean. | Preserve the baseline while ratcheting stricter checks. |
| 2026-05-31 | Ruff ratchet | Enabled `B009`, `C420`, `F402`, and `UP035` after localized cleanup. | Continue one safe rule family at a time. |
| 2026-05-31 | Vulture | Narrowed ignore names and made the clean report blocking in CI. | Keep API exclusions narrow. |
| 2026-05-31 | Bandit | Reviewed 19 low-severity parser-token, template-token, and argv-based subprocess findings. | Re-review when command trust boundaries change. |
| 2026-05-31 | Hypothesis and Radon hotspot | Added generated nested C declarators and top-level lexer delimiter properties. | Expand preprocessing generators next. |
| 2026-05-31 | Parser preprocessing boundary | Added generated Fortran structure/preprocessing properties and aligned raw Fortran/C macro handling around compiler-required errors. | Expand AST and semantic-IR invariants next. |
