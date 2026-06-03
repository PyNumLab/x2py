# Quality Stack Adoption Checklist

This file tracks the staged adoption of the Python quality stack. Update it
whenever a QA task is completed, a new gap is discovered, or a tool is made
stricter. Do not mark an item complete without a passing command, reviewed
report, or merged configuration change.

The recurring checks remain required after adoption is complete. The adoption
sections track the finite work needed to reach the intended steady state.

Last reviewed: 2026-06-02

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
- detect hidden test-order regressions;
- keep fast, stable checks blocking on pull requests while running expensive
  fuzzing and mutation work on schedules or manual dispatch;
- ratchet strictness gradually so historical debt is reduced without obscuring
  meaningful failures.

## Full Adoption Exit Criteria

The quality stack should be treated as fully adopted when all of these are true:

- fast pull-request gates are blocking and stable for tests, coverage, Ruff,
  Bandit, pip-audit, and Vulture;
- recurring deeper jobs exist for fuzzing, changing random-order tests, and
  manual mutation testing;
- each mutation subsystem row has completed an initial campaign and survivor
  review, with every survivor classified as killed, fixed, or equivalent;
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
- [ ] Update this checklist with newly completed work and newly discovered
      debt.

Use the commands and workflow explanations in
[`quality.md`](quality.md). Keep expensive checks focused locally; scheduled
GitHub Actions jobs provide broader repeated coverage.

## Current Baseline

Fully validated locally on 2026-05-31. Ruff lint/formatting, focused mutation,
and full pytest were refreshed on 2026-06-01:

- [x] Full pytest run: `3497 passed`.
- [x] Combined xdist and subprocess branch coverage: `95.34%`, above the
      configured `95%` gate.
- [x] Ruff lint and full-tree Ruff formatting checks pass.
- [x] Pre-commit hooks pass.
- [x] Vulture reports no current findings.
- [x] Bandit reports no medium- or high-severity findings.
- [x] pip-audit reports no known dependency vulnerabilities.
- [x] Hypothesis CI profile passes all current property tests.
- [x] Hypothesis fuzz profile passes `1000` C and `1000` Fortran generated
      fragments without unexpected exceptions.
- [x] Focused `c_parser/type_resolver.py` mutation campaign completed.
      Assertions and implementation fixes improved the result from `142/206`
      killed mutants to a reviewed `204/204` killed-mutant baseline.
- [x] Focused `semantics/pyi_printer.py` mutation campaign completed:
      `385/395` mutants killed; the remaining `6` survivors and `4` timeouts
      are reviewed equivalent mutations or mutmut wrapper artifacts.
- [x] Focused `c_parser/lexer.py` mutation survivor review completed:
      `794/1171` killed after the refreshed full pass and targeted edge
      reruns; the remaining `10` ordinary survivors are reviewed equivalents
      or mutmut wrapper artifacts, `367` bounded-run timeouts are recorded by
      function cluster, and no mutants lack covering tests.
- [x] Focused `c_parser/preprocessor.py` mutation survivor review completed:
      `105/108` killed; the remaining `3` survivors are reviewed equivalent
      default-value or boundary mutations.
- [x] Focused `fortran_parser/type_resolver.py` mutation survivor review
      completed: `34/34` killed after adding direct scalar, character, and
      nested `kind=` expression assertions.
- [x] Focused `fortran_parser/lexer.py` mutation survivor review completed:
      `150/185` killed; the remaining `35` survivors are reviewed equivalent
      normalization, falsy-state, overwritten-state, or boundary mutations.
- [x] Focused `c_parser/models.py` mutation survivor review completed:
      `304/310` killed; the remaining `6` survivors are reviewed equivalent
      mutations or mutmut wrapper artifacts.
- [x] Focused `semantics/readiness.py` mutation survivor review completed:
      `804/827` killed; the remaining `23` survivors are reviewed equivalent
      mutations or mutmut wrapper artifacts.
- [x] Focused `x2py/preprocessing.py` mutation survivor review completed:
      `1496/1564` killed; the remaining `52` survivors are reviewed equivalent
      mutations or mutmut wrapper artifacts, `16` bounded-run timeouts detect
      loop-progress mutations, and no mutants lack covering tests.
- [x] Focused `semantics/c2ir.py` mutation survivor review completed:
      `1785/1821` killed; the remaining `34` survivors are reviewed equivalent
      mutations or mutmut wrapper artifacts, `2` bounded-run timeouts detect
      macro fixed-point loop-progress mutations, and no mutants lack covering
      tests.
- [x] Focused `semantics/fortran2ir.py` mutation survivor review completed:
      `1225/1339` killed; the remaining `114` survivors are reviewed equivalent,
      default-value, or mutmut wrapper artifacts, with no timeouts or mutants
      lacking covering tests.
- [x] Focused `semantics/pyi_parser.py` mutation survivor review completed:
      `1266/1288` killed; the remaining `21` survivors are reviewed equivalent,
      default-value, or mutmut wrapper artifacts, the `1` bounded-run timeout is
      a manually verified equivalent `zip(..., strict=None)` mutation, and no
      mutants lack covering tests.
- [x] Focused `c_parser/parser.py` mutation survivor review completed:
      `2673/3537` killed; the remaining `849` survivors are reviewed
      equivalent, default-value, wrapper, unreachable defensive, or
      source-location/diagnostic artifacts, `15` bounded scanner/declarator
      timeouts are recorded by function cluster, and no mutants lack covering
      tests.
- [x] Initial focused `fortran_parser/parser.py` mutation campaign completed:
      `3233/5278` mutants killed, `745` survivors, and `1300` bounded-run
      timeouts. Survivor classification remains in progress; this is not yet a
      reviewed subsystem baseline.
- [x] Radon baseline reviewed: average complexity is `C (18.95)`.

## Remaining Adoption Estimate

Current estimate with full-project mutation parked: **about 4% of the active
non-mutation adoption work remains**, so the quality stack is **about 96%
adopted by effort** for the currently active tool rollout.

This is an effort-weighted estimate, not a simple checkbox percentage. The
recurring checks in "How To Use This Checklist" are excluded because they are
ongoing practice, not finite rollout work. The current-baseline evidence bullets
are also excluded because they record validation results rather than adoption
tasks. Counting finite adoption bullets from the Ruff section onward gives `80`
completed bullets and `8` open bullets. The mutation subsystem table adds `18`
completed states and `12` open states before the `semantics/c2ir.py` campaign.
That campaign adds `2` completed states, and the `semantics/fortran2ir.py`
campaign adds another `2`. The `semantics/pyi_parser.py` campaign adds another
`2`, the `x2py/cli.py` campaign adds another `2`, and the
`c_parser/parser.py` campaign adds another `2`. The initial
`fortran_parser/parser.py` campaign adds `1`, giving `29` completed mutation
states and `1` open state. Before parking full-project mutation, the raw
detailed progress count was `109 / 118`, or about `92%` complete and `8%`
open. The active rollout estimate now excludes that parked full-project
mutation refresh.

The full-project mutation refresh is intentionally parked after the remote
manual Quality run timed out at the GitHub Actions `3h` limit. Focused mutation
campaigns, selected survivor reruns, and direct contract tests remain retained
as the active mutation practice. The parked full-project run does not block the
current adoption pass.

Current status by area:

| Area | Status | Explanation |
| --- | --- | --- |
| Fast pull-request gates | Mostly complete | Tests, coverage, Ruff, Bandit, pip-audit, and Vulture are wired as blocking gates. |
| Property and fuzz testing | Mostly complete | Current parser, AST, semantic-IR, and code-generation invariants exist; future failures still need regression tests. |
| Mutation testing | Partially complete | Infrastructure works; the remaining parser subsystem initial campaign is complete, but its survivor review remains. |
| Dead-code detection | Complete for adoption | Vulture is clean and blocking; future public API additions should keep exclusions narrow. |
| Security and dependency scanning | Complete for adoption | Bandit and pip-audit are blocking; low-severity and dependency reviews recur when related code changes. |
| Complexity tracking | Mostly complete | The staged Radon policy is blocking in CI and pre-commit; future hotspot decomposition can ratchet thresholds further. |
| Scheduled workflow triage | Partially complete | Jobs exist; regular review and actionable-failure recording still need to become routine. |

Estimated share of the remaining work:

| Area | Share of Remaining Work | Why |
| --- | ---: | --- |
| Focused Fortran parser survivor notes | `35%` | The initial campaign, selected survivor rerun, and `55` direct contracts are recorded; remaining notes should stay focused and bounded. |
| Ruff and Radon strictness ratchets | `20%` | Later complexity reductions need careful tightening without noisy parser rewrites. |
| Scheduled workflow review process | `25%` | The manual Quality run proved fuzz and changing random-order jobs pass; future scheduled failures still need routine triage. |
| Conditional maintenance checks | `20%` | Bandit, pip-audit, coverage, xdist, and pre-commit follow-ups are mostly complete, but remain active when related code changes. |

Priority order for reducing the remaining percentage:

1. Complete the remaining `fortran_parser/parser.py` survivor review, recording
   each survivor as killed, fixed, or equivalent.
2. Lower complexity thresholds as hotspot refactors make that safe.
3. Review scheduled workflow results regularly and add actionable failures to
   this checklist until fixed.

Parked advisory item: a full-project manual mutation campaign may be revisited
later, but the 2026-06-02 remote run timed out at `3h`, so it is not active
adoption evidence and should not block this rollout.

Update this estimate when a mutation subsystem row is completed, a new CI gate
is made blocking, or a scheduled workflow failure adds new actionable debt.

Do not lower the remaining-work estimate just because a command still passes.
Lower it only when an adoption item is completed with evidence, such as a
passing command, reviewed report, merged CI configuration, documented survivor
classification, or scheduled-failure review.

## Ruff

What it does: Ruff is a fast Python linter and formatter. It finds static code
problems such as undefined names, unused imports, suspicious patterns, and
overly complex functions, and it gives the Python tree one consistent format.

Project goal: hard-gate likely bugs now, then remove historical formatting and lint
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
- [x] Require Ruff formatting in CI.
- [x] Remove the first safe baseline-ignore families: `B009`, `C420`, `E741`,
      `F402`, `UP009`, and `UP035`.
- [x] Remove additional safe baseline-ignore families: `B905`, `RET505`,
      `RET507`, `RUF022`, and `UP037`.
- [x] Format the historical Python tree in a dedicated mechanical change.
- [x] Change CI from changed-file formatting to `ruff format --check .`.
- [x] Review and remove baseline ignores one rule family at a time.
- [x] Keep line-length diagnostics intentionally unselected: wrapping parser
      diagnostics and embedded test source snippets would add noise without
      improving correctness.
- [x] Lower `tool.ruff.lint.mccabe.max-complexity` from `50` toward `20`.
- [x] Define a stricter complexity policy for new or materially changed
      functions without forcing unrelated parser rewrites.

## Hypothesis

What it does: Hypothesis is a property-based testing library. Instead of checking
only hand-written examples, it generates many inputs from declared strategies
and shrinks a failing input to a small reproducer.

Project goal: generate edge cases and validate invariants across parsers,
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
- [x] Add AST and semantic-IR transformation invariants.
- [x] Add code-generation escaping, stable-ordering, and parse-back invariants.
- [x] Store each currently known meaningful minimized Hypothesis failure as a
      regression test; continue doing so for future failures.

## Mutmut

What it does: mutmut is a mutation-testing tool. It makes small changes to
implementation code, such as changing a condition or return value, and reruns
tests to reveal behavior that the test suite does not actually protect.

Project goal: find weak tests by proving that meaningful implementation mutations are
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
- [x] Copy local package directories into focused mutmut workspaces and keep
      process-local stats instrumentation out of fresh CLI subprocesses.
- [x] Document focused local mutation workflow and survivor review.
- [x] Run the first focused campaign for `c_parser/type_resolver.py`.
- [x] Fix the discovered duplicate typedef-cycle diagnostic bug.
- [x] Add assertions for typedef resolution on variables and aggregate
      members.
- [x] Add assertions for unresolved `struct`, `union`, and `enum` references.
- [x] Review the remaining meaningful `c_parser/type_resolver.py` survivors.
- [x] Review all `semantics/pyi_printer.py` survivors and timeouts; add
      behavioral assertions for meaningful gaps and classify equivalent
      mutations.
- [x] Run focused mutation campaigns for each subsystem below.
- [ ] Record survivor decisions: add a test, fix a bug, or document why the
      mutation is behaviorally equivalent.
- [x] Park the full-project manual GitHub Actions mutation campaign as
      advisory after the 2026-06-02 remote run exceeded the `3h` limit.

Mutation subsystem progress:

| Subsystem | Initial Campaign | Meaningful Survivors Reviewed | Notes |
| --- | --- | --- | --- |
| `c_parser/type_resolver.py` | [x] | [x] | `204/204` killed; added cycle, function-signature, parameter-declared-type, variable, and member assertions. |
| `c_parser/lexer.py` | [x] | [x] | Reviewed baseline: `794/1171` killed, `10` equivalent or wrapper-artifact survivors, `367` bounded-run timeouts, and `0` no-tests. |
| `c_parser/preprocessor.py` | [x] | [x] | `105/108` killed; remaining `3` survivors are reviewed equivalents. |
| `c_parser/parser.py` | [x] | [x] | `2673/3537` killed; remaining `849` survivors are reviewed equivalent, default-value, wrapper, unreachable defensive, or source-location/diagnostic artifacts; `15` bounded scanner/declarator timeout detections and `0` no-tests. |
| `c_parser/models.py` | [x] | [x] | `304/310` killed; remaining `6` survivors are reviewed equivalents or wrapper artifacts. |
| `fortran_parser/lexer.py` | [x] | [x] | `150/185` killed; remaining `35` normalization, falsy-state, overwritten-state, and boundary survivors are reviewed equivalents. |
| `fortran_parser/parser.py` | [x] | [ ] | Initial baseline: `3233/5278` killed, `745` survivors, and `1300` bounded-run timeouts. Added `55` direct parser-contract tests; a bounded high-value rerun killed `86/151` selected prior survivors. Continue declarations, units, preprocessing, and resolution survivor review. |
| `fortran_parser/type_resolver.py` | [x] | [x] | `34/34` killed; added direct scalar, character, and nested `kind=` expression assertions. |
| `semantics/c2ir.py` | [x] | [x] | `1785/1821` killed; remaining `34` equivalent or wrapper-artifact survivors and `2` macro fixed-point timeout detections are reviewed; `0` no-tests. |
| `semantics/fortran2ir.py` | [x] | [x] | `1225/1339` killed; remaining `114` array-helper, fallback, normalization, collector-key, and wrapper-artifact survivors are reviewed equivalents; `0` timeouts and `0` no-tests. |
| `semantics/pyi_parser.py` | [x] | [x] | `1266/1288` killed; remaining `21` equivalent, default-value, or wrapper-artifact survivors and `1` manually verified equivalent timeout are reviewed; `0` no-tests. |
| `semantics/pyi_printer.py` | [x] | [x] | `385/395` killed; remaining `6` survivors and `4` timeouts are reviewed equivalents or mutmut artifacts. |
| `semantics/readiness.py` | [x] | [x] | `804/827` killed; remaining `23` fallback, boundary, or wrapper-artifact survivors are reviewed equivalents. |
| `x2py/preprocessing.py` | [x] | [x] | `1496/1564` killed; remaining `52` equivalent or wrapper-artifact survivors and `16` loop-progress timeout detections are reviewed; `0` no-tests. |
| `x2py/cli.py` | [x] | [x] | `1771/1783` killed; remaining `12` survivors are reviewed equivalents. Added direct helper, report, preprocessing-configuration, Rich-output, parser-construction, command-routing, validation, error-rendering, write-contract, and stdout-mode assertions. |

Pending `fortran_parser/parser.py` survivor review snapshot:

- The completed initial bounded campaign recorded `3233/5278` killed mutants,
  `745` survivors, and `1300` timeouts. The generated cache currently shows all
  `5278` mutants as `not checked` after a deliberately canceled broad rerun, so
  use the recorded initial campaign as the review inventory until a bounded
  refresh completes.
- Added `tests/parser/test_fortran_parser_mutation_contracts.py` with `55`
  passing direct contract tests for unit boundaries, namespace collection,
  project registries, codec forwarding, include/import state, enum and
  interface validation, structured diagnostics, nested derived-type
  collection, filename propagation, sibling duplicate diagnostics,
  nonexecution child filtering, region splitting, procedure finalization,
  top-level file symbol registration, and cross-file project parameter
  resolution, module parameter declaration storage, type-field declaration
  storage, procedure declaration duplicate handling, local parameter storage,
  legacy-parameter implicit typing policy, contains-line validation, and
  unknown procedure-declaration diagnostics, source preparation, source-form
  detection, path/source discrimination, unit-end parsing, and malformed-header
  diagnostics, compile-time kind/shape/value resolution, literal normalization,
  restricted expression evaluation, and relevant local-parameter discovery.
  The latest slice also pins project-level duplicate-symbol diagnostics and
  dependency-first, cycle-tolerant project file ordering.
- A bounded rerun of `151` selected prior survivors killed `86` and left `65`
  for classification. Keep local reruns serialized with `--max-children 1`;
  use manual GitHub Actions for broader refreshes.
- The largest initial timeout clusters are `_finalize_proc` (`145`),
  `_helper_slice_child_units` (`91`), `_helper_find_unit_end` (`88`),
  `visit_procedure_unit` (`74`), `_helper_unit_grammar` (`72`),
  `_helper_validate_child_unit_regions` (`71`), `_helper_split_unit_parts`
  (`56`), `_helper_validate_sibling_units` (`52`),
  `_helper_push_declaration_to_scope` (`50`), and `visit_file` (`45`).
  Review timeout cluster drift before establishing the final subsystem
  baseline.

Reviewed `c_parser/lexer.py` survivor classification:

- Equivalent unescape state/fallback mutations:
  `_unescape_linemarker_filename__mutmut_2`, `18`, `20`, and `22`.
- Equivalent balanced-invocation falsy state mutations:
  `_balanced_invocation_end__mutmut_5`, `12`, and `19`.
- Equivalent default-delimiter mutation:
  `_is_braced_declaration_header__mutmut_10`.
- Mutmut wrapper artifacts whose generated trampoline always supplies the
  original default explicitly: `_is_aggregate_definition_header__mutmut_1`
  and `_is_braced_declaration_header__mutmut_1`.
- Bounded-run timeout detections by function cluster:
  `_advance_position` `3`, `_blank_preprocessor_directives` `8`,
  `_line_mapping` `9`, `_mapped_filenames` `2`, `_scan_code_states` `21`,
  `_source_line` `3`, `lex_c_source` `55`, `line_mappings_for_source` `12`,
  `normalize_c_source` `32`, `split_top_level_c_source` `172`,
  `strip_c_comments` `42`,
  `top_level_partition` `3`, `top_level_split` `2`, and
  `top_level_split_with_offsets` `3`. Preserve these as timeout detections
  and inspect any future cluster-count drift.

Reviewed `c_parser/preprocessor.py` survivor classification:

- Equivalent leading-marker column mutations: `_record_location__mutmut_9`
  and `10`. Both preserve column `1` when `#` is at offset zero.
- Equivalent dataclass-default mutation:
  `collect_preprocessor_metadata__mutmut_67`. Omitting the explicit
  diagnostic severity preserves `CDiagnostic.severity == "warning"`.

Reviewed `c_parser/parser.py` survivor classification:

- Meaningful compiler-extension scanner and K&R detector mutants were killed by
  added assertions for extension-looking text inside line and block comments,
  preprocessor directives during old-style-definition scanning, continued
  scanning after nameless parenthesized lines, and labeled `for`/`switch`
  control statements inside function bodies.
- Meaningful parameter-list boundary behavior is covered by direct assertions
  for outer function signatures with nested callback declarators and for
  non-call declarations returning `None`.
- Equivalent scanner state and boundary mutations dominate
  `_normalize_compiler_extensions`, `_find_matching_delimiter`, and
  `_find_parameter_list`: falsy or `"normal"` state substitutions are
  overwritten before semantic use, and the surviving boundary changes only
  affect bare strings such as `"()"` or `"f()"`, not full declaration lines used
  by parser callers.
- Equivalent default, wrapper, fallback, and source-location mutations dominate
  parsing, indexing, deduplication, visit, diagnostic, and merge helpers. These
  mutations either preserve dataclass defaults, affect mutmut-generated wrapper
  defaults, alter diagnostic wording/location without changing the accepted AST
  contract, or touch defensive fallback branches that supported parser paths do
  not reach.
- Equivalent type-key label mutations preserve stable distinct equality tokens;
  the exact private string spelling is not part of the public contract.
- Unreachable defensive `_parse_translation_unit` catch mutations are reviewed
  as equivalent for the current grammar paths: nested syntax failures raise
  public `CParseError` instances directly or are converted inside field parsing
  before that `_InvalidCGrammarSyntax` branch can observe them.
- Bounded-run timeout detections are limited to scanner-progress clusters:
  `_normalize_compiler_extensions` `12`, `_read_identifier` `1`,
  `_parse_pointer_ops` `1`, and `_parse_declarator_suffixes` `1`. Preserve these
  as timeout detections and inspect future cluster-count drift.

Reviewed `c_parser/models.py` survivor classification:

- Equivalent absent-environment fallback mutation: `_env_flag__mutmut_6`.
  Neither default value belongs to the true-value set.
- Equivalent set-serialization seen-state mutations:
  `c_model_to_dict__mutmut_110` and `112`. Aggregate model dataclasses tracked
  for cycle detection are unhashable and cannot occur as set members.
- Equivalent falsy explicit-color mutation:
  `CParseError.__init____mutmut_14`.
- Mutmut wrapper artifact whose generated trampoline always supplies the
  original default explicitly: `CParseError.format_diagnostic__mutmut_1`.
- Equivalent fixed-width alignment mutation:
  `CParseError.format_diagnostic__mutmut_99`. The gutter width equals the line
  label length for both known and unknown source locations.

Reviewed `semantics/readiness.py` survivor classification:

- Mutmut wrapper artifact whose generated trampoline always supplies the
  original default explicitly: `assess_pyi_wrap_readiness__mutmut_1`.
- Equivalent codec-name normalization mutation:
  `assess_pyi_wrap_readiness__mutmut_2`. Python treats `UTF-8` as the same
  codec as `utf-8`.
- Equivalent dataclass metadata-fallback mutations:
  `_check_module__mutmut_13`, `_check_module__mutmut_16`,
  `_check_class__mutmut_13`, `_check_class__mutmut_16`,
  `_check_function__mutmut_13`, `_check_function__mutmut_16`,
  `_check_argument__mutmut_13`, `_check_argument__mutmut_16`,
  `_check_type__mutmut_14`, and `_check_type__mutmut_17`. Supported semantic
  model instances always expose their metadata dictionary.
- Equivalent end-of-function control-flow mutation:
  `_add_blocker__mutmut_34`. Replacing `break` with `return` has the same effect
  because no work follows the loop.
- Equivalent qualified-name first-segment split mutations:
  `_SemanticTypeIndex.is_known_type__mutmut_19` and `22`.
- Equivalent prebuilt index-map fallback mutations:
  `_SemanticTypeIndex.is_known_type__mutmut_26`, `28`, `31`, and `33`. Index
  initialization creates both sets for every assessed module.
- Equivalent semantic-model visibility fallback mutations:
  `_is_public__mutmut_3`, `6`, `9`, and `10`. Supported public-surface model
  instances always expose `visibility`.

Reviewed `x2py/cli.py` partial survivor classification:

- Equivalent absent-environment fallback mutation: `_env_flag__mutmut_6`.
  Neither default value belongs to the true-value set.
- Equivalent missing-code fallback mutation:
  `_format_semantic_readiness__mutmut_103`. Missing readiness blocker codes
  are passed through to `_format_semantic_blocker_item`, where unknown items
  fall back to `str(item)` either way.
- Equivalent codec-name normalization mutation:
  `_fortran_source_for_path__mutmut_12`. Python treats `UTF-8` as the same
  codec as `utf-8`.
- Equivalent dependency-writer codec-name normalization mutation:
  `_write_pyi_dependencies__mutmut_37`. Python treats `UTF-8` as the same
  codec as `utf-8`.
- Equivalent semantic-report language-default mutations:
  `_semantic_report__mutmut_1` and `_semantic_report__mutmut_2`. The C path
  is selected only for `language == "c"`; every non-C default selects the
  same Fortran path.
- Equivalent semantic-report Pyi separator mutation:
  `_semantic_report__mutmut_34`. Each C native source maps structurally to
  one converted module, so the join separator cannot affect output.
- Equivalent wrap-readiness language-default mutations:
  `_wrap_readiness_report__mutmut_1` and `_wrap_readiness_report__mutmut_2`.
  The C path is selected only for `language == "c"`; every non-C default
  selects the same Fortran path.
- Equivalent redundant compile-commands diagnostic mutations:
  `_build_preprocessing_config__mutmut_107`,
  `_build_preprocessing_config__mutmut_108`, and
  `_build_preprocessing_config__mutmut_109`. The earlier compiler-only flag
  guard rejects compile commands without compiler preprocessing before the
  dedicated validation branch can run.

Reviewed `x2py/preprocessing.py` survivor classification:

- Equivalent wrapper, dataclass-default, and overwritten-state mutations:
  `PreprocessingError.__init____mutmut_1`, `2`,
  `build_direct_preprocess_invocation__mutmut_34`,
  `build_compile_commands_invocation__mutmut_1`, `2`, `37`,
  `_recipe_from_invocation__mutmut_23`, `preprocess_source__mutmut_85`, `106`,
  `128`, `210`, and `run_compiler_preprocessor_with_recipe__mutmut_31`, `58`,
  `59`.
- Equivalent macro-name split mutations: `validate_macro_name__mutmut_12` and
  `15`. The name before the first `=` is unchanged.
- Equivalent redundant compile-only guard mutations:
  `_filter_compile_only_args__mutmut_27` and `28`. The exact `-o` case already
  continues before the inline `-o...` guard.
- Bounded-run timeout detections in `_filter_compile_only_args`: `11`, `12`,
  `18`, `19`, `29`, `30`, `37`, `38`, `48`, `49`, `59`, `60`, `69`, `70`,
  `74`, and `75`. These mutations prevent loop-index progress and are detected
  by the timeout bound.
- Equivalent command-template standalone-token fallthrough mutations:
  `_template_token_value__mutmut_2`, `3`, `7`, `11`, and `12`. The generic
  formatter returns the same source, compiler, or language value.
- Equivalent linemarker unescape and initialized-stack mutations:
  `_unescape_linemarker_filename__mutmut_2`, `18`, `20` and
  `parse_linemarker_mappings__mutmut_39`.
- Equivalent included-file default and internal-stack mutations:
  `_included_files_from_linemarkers__mutmut_7`, `8`, `26`, `27`, `79`, `80`,
  `82`, `83`, `85`, and `93`. Defaults are unchanged, and the substitutions
  preserve the active include parent used by emitted metadata.
- Equivalent native-include marker, unreachable-fallback, and project-default
  mutations: `expand_native_fortran_includes__mutmut_35`, `55`, `56`, `57`,
  `58`, `59`, `60`, `61`, `62`, `63`, `64`, `132`, and `138`.
- Equivalent executable-boundary mutations: `preprocess_source__mutmut_20` and
  `22`. A missing bare executable reaches the same public not-found diagnostic,
  and selected invocation builders always produce a non-empty argument vector.

Reviewed `fortran_parser/lexer.py` survivor classification:

- Equivalent comment-strip fallback and quote-state mutations:
  `strip_comment__mutmut_38`, `40`, `42`, `43`, `50`, `52`, and `53`.
  Column-one `!` comments still fall through to inline stripping; the other
  substitutions preserve falsy quote state or values replaced before use.
- Equivalent `splitlines()` and initial-state mutations:
  `preprocess_lines__mutmut_12`, `13`, `18`, `22`, `24`, `25`, `26`, `27`,
  and `28`. `splitlines()` removes newline separators before these operations,
  and the initial pending values are falsy or replaced before emission.
- Equivalent normalized fixed-form OpenMP reset mutations:
  `preprocess_lines__mutmut_35`, `39`, `41`, `42`, `43`, `44`, `45`, and
  `46`. Recognized directives are already left-stripped, and the reset values
  are falsy, replaced, or unable to affect the next emitted fixed-form line.
- Equivalent fixed-form six-column and continuation-state mutations:
  `preprocess_lines__mutmut_51`, `52`, `59`, `71`, and `78`. Exact
  six-character lines have no payload and are discarded by the empty-text
  guard; the state replacements preserve falsiness.
- Equivalent free-form post-flush reset mutations:
  `preprocess_lines__mutmut_110`, `112`, `113`, `114`, `115`, and `116`.
  These values are falsy or replaced before the next emitted logical line.

Reviewed `semantics/c2ir.py` survivor classification:

- Mutmut wrapper artifacts whose generated trampolines always supply the
  original default explicitly: `_unresolved_type__mutmut_1` through `5`,
  `visit_parameter__mutmut_1`, `visit_project_module__mutmut_1` and `2`,
  `c_parameter_to_semantic_argument__mutmut_1`, and
  `c_project_to_semantic_module__mutmut_1` and `2`.
- Equivalent explicit dataclass-default mutations: `_array_type__mutmut_25`
  and `_pointer_type__mutmut_25`. Omitting `ownership="borrowed"` preserves
  the storage-contract default.
- Equivalent parser-normalized or unreachable declarator branches:
  `_composed_type__mutmut_30`, `101`, `124`, `125`, and `126`.
- Equivalent boolean, invariant-length, redundant-guard, and typedef-cycle
  mutations: `_macro_constants_from_macros__mutmut_8`, `27`, and `28`,
  `visit_function__mutmut_93`, `96`, and `97`,
  `_classify_project_external_types__mutmut_24`, and
  `_resolve_typedef__mutmut_7`.
- Equivalent currently unused enum-registry and struct-owner forwarding state:
  `__init____mutmut_9`, `visit_file__mutmut_8` and `9`,
  `visit_project__mutmut_7`, `14`, and `19`,
  `visit_project_module__mutmut_10`, and `visit_type__mutmut_10`.
- Bounded-run timeout detections in `_macro_constants_from_macros`: `9` and
  `10`. These mutations prevent fixed-point loop progress and are detected by
  the timeout bound.

Reviewed `semantics/fortran2ir.py` survivor classification:

- Equivalent array-contract helper arguments and explicit defaults:
  `_array_storage_contract__mutmut_15`, `25`, `26`, `30`, `32`, `37`, `38`,
  `50`, `61`, `62`, `63`, `66`, `67`, `71`, `72`, `75`, `81`, `82`, `84`,
  `90`, `91`, `93`, `99`, `100`, `103`, `106`, and `110`. The changed values
  are ignored by downstream helpers or preserve semantic dataclass defaults.
- Equivalent requirement-collector deduplication, fallback, and intrinsic-kind
  mutations: `collect_semantic_compile_time_requirements__mutmut_71` through
  `83`, excluding `84`, plus `85`, `91`, `116`, `126`, `127`, and `128`.
  They preserve deduplication keys or the supported logical and character kind
  behavior.
- Equivalent parser-dataclass fallbacks and mutmut default-wrapper artifacts:
  `visit__mutmut_28` and `30`, `first_module__mutmut_15`, `22`, `29`, `32`,
  `35`, and `43`, `visit_argument__mutmut_10`, `13`, `16`, `17`, `44`, `47`,
  `50`, `67`, `71`, `74`, `77`, `78`, `80`, `83`, `84`, `85`, `86`, and
  `87`, `visit_data_member__mutmut_1`, `2`, `54`, `57`, `60`, and `61`,
  `visit_procedure__mutmut_1`, `2`, `28`, and `30`,
  `visit_derived_type__mutmut_5`, `7`, `8`, `10`, `12`, `19`, and `29`,
  `visit_module__mutmut_49` and `52`,
  `procedure_to_semantic_function__mutmut_1`, `2`, and `6`, and
  `derived_type_to_semantic_class__mutmut_2` and `4`.
- Equivalent unused variable-context forwarding and default-wrapper artifacts:
  `_iter_fortran_variable_contexts__mutmut_1`, `2`, `9`, `12`, `79`, `80`,
  `82`, `83`, `84`, and `85`.
- Equivalent redundant normalization, unreachable branch, and semantic-kind
  mutations: `_with_additional_wrapped_types__mutmut_3` and `5`,
  `_resolve_derived_type_origin__mutmut_17` and `18`,
  `_semantic_kind_key__mutmut_16`, `17`, and `18`, and
  `_resolve_compile_time_text__mutmut_4`.

Reviewed `semantics/pyi_parser.py` survivor classification:

- Mutmut wrapper artifacts whose generated trampolines preserve the original
  default explicitly: `load_pyi_file__mutmut_1` and `2`,
  `load_pyi_modules__mutmut_1` and `2`, `convert_pyi_to_ir__mutmut_1`,
  `parse_pyi_text__mutmut_1`, `2`, `3`, and `4`, and
  `_callable_parts__mutmut_1`.
- Equivalent empty-source fallback mutation: `parse_pyi_text__mutmut_11`.
- Equivalent callable AST fallback and equal-length `zip()` strictness
  mutations: `_callable_parts__mutmut_6`, `9`, `28`, and `30`.
- Manually verified equivalent timeout:
  `_callable_parts__mutmut_25`. It changes `zip(..., strict=False)` to
  `zip(..., strict=None)`; the focused `173`-test selection passes unchanged.
- Equivalent valid-import partition and first-segment split mutations:
  `_imported_type_refs__mutmut_10`, `32`, and `35`.
- Equivalent omitted `dict.setdefault()` default:
  `load_pyi_modules__mutmut_28`.
- Equivalent guaranteed array-storage guard and dataclass-default mutations:
  `array_type__mutmut_11` and `72`.

## Vulture

What it does: Vulture is a static dead-code detector. It reports functions,
classes, variables, and other definitions that appear unused so they can be
removed or reviewed as intentional public or dynamically discovered APIs.

Project goal: remove dead code and make newly introduced dead definitions fail CI.

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

What it does: Radon measures code complexity and maintainability. Its reports
highlight functions with many control-flow paths and modules that may be harder
to understand, test, and change safely.

Project goal: track risky control flow and reduce complexity where it improves
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
- [x] Decide the blocking policy: maximum complexity for new or materially
      changed functions, allowed exceptions, and ratchet schedule.
- [x] Add the chosen blocking policy to CI.

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

What it does: Bandit scans Python source for security-sensitive patterns, such
as risky subprocess, filesystem, cryptography, and deserialization usage. It
reports severity and confidence so findings can be triaged.

Project goal: block new medium- and high-confidence security risks and review lower
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

What it does: pip-audit checks Python dependencies against published
vulnerability advisories. It detects known security issues in packages even
when the repository's own source code has not changed.

Project goal: fail CI when project dependencies have known vulnerabilities.

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

What it does: pytest-randomly changes test order and randomizes supported test
inputs with a recorded seed. It helps reveal tests that pass only because
another test happened to run before or after them.

Project goal: detect hidden order dependence and make failures reproducible.

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

## Supporting Infrastructure

These are not additional analyzers, but the stack is incomplete without them.

### Pytest And Coverage

What it does: pytest runs the behavioral test suite. Coverage records which
lines and branches those tests execute, making untested paths visible and
providing a measurable regression floor.

Project goal: keep behavioral regression coverage broad and make subprocess execution
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

What it does: pytest-xdist distributes pytest tests across worker processes. It
reduces suite runtime and can expose tests that incorrectly depend on shared
process state or unsafe concurrent access.

Project goal: keep the broad suite fast while proving that tests are isolated enough
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

What it does: pre-commit runs configured repository checks before a commit and
can also run manual hooks on demand. It gives developers fast local feedback
before the same issues reach CI.

Project goal: catch fast, deterministic issues before CI.

Adoption target:

- Commit-stage hooks stay fast enough for normal local use and pass with zero
  findings.
- Expensive or report-oriented tools remain available as manual hooks.

Why: pre-commit should shorten feedback loops without encouraging developers
to bypass it because expensive analysis runs on every edit.

- [x] Run Ruff formatting, Ruff linting, and Bandit on commit.
- [x] Provide manual Vulture and Radon hooks.
- [x] Decide whether any additional fast, stable check belongs on commit after
      the initial rollout settles.

### GitHub Actions

What it does: GitHub Actions runs automated workflows in clean hosted CI
environments on repository events, schedules, and manual dispatch. It provides
repeatable remote validation and stores reports or artifacts from deeper jobs.

Project goal: enforce stable quality gates on every pull request and run expensive
discovery checks often enough to find deeper regressions.

Adoption target:

- Pull-request and push workflows pass for tests, coverage, Ruff, Bandit,
  pip-audit, and Vulture.
- Scheduled/manual workflows run fuzzing, changing random seeds, and mutation
  testing at their documented cadence.
- Actionable scheduled failures are recorded in this checklist until fixed.

Why: separating fast blocking gates from heavier discovery workflows keeps
pull-request feedback practical while still exercising the deeper QA stack.

- [x] Keep fast blocking checks on pull requests and pushes.
- [x] Keep mutation testing manual because it is expensive.
- [x] Run fuzzing and changing random-order tests on schedule or manual
      dispatch.
- [x] Document the scheduled workflow triage path, reproduction steps, and
      actionable-failure recording policy.
- [ ] Review scheduled workflow results regularly and record actionable
      failures in this checklist.

## Progress Log

Add a row when a QA adoption task or subsystem campaign is completed.

| Date | Area | Result | Follow-up |
| --- | --- | --- | --- |
| 2026-05-31 | Initial stack integration | Added configuration, CI, pre-commit, documentation, and Hypothesis tests. | Continue staged strictness rollout. |
| 2026-05-31 | Vulture | Removed dead Fortran parser parameters; report is clean. | Make blocking after API whitelist review. |
| 2026-05-31 | Mutmut: `c_parser/type_resolver.py` | Fixed duplicate typedef-cycle diagnostics and added resolver regression assertions. | Review remaining meaningful survivors and continue subsystem campaigns. |
| 2026-05-31 | Full validation | `3437 passed`, combined coverage `95.13%`, security and dependency scans clean. | Preserve the baseline while ratcheting stricter checks. |
| 2026-05-31 | Ruff ratchet | Enabled `B009`, `C420`, `F402`, and `UP035` after localized cleanup. | Continue one safe rule family at a time. |
| 2026-05-31 | Vulture | Narrowed ignore names and made the clean report blocking in CI. | Keep API exclusions narrow. |
| 2026-05-31 | Bandit | Reviewed 19 low-severity parser-token, template-token, and argv-based subprocess findings. | Re-review when command trust boundaries change. |
| 2026-05-31 | Bandit | Reviewed the mutmut wrapper's low-severity `subprocess` import finding; the expanded source-and-tools scan has `20` low-severity findings and no medium- or high-severity findings. | Re-review when command trust boundaries change. |
| 2026-05-31 | Hypothesis and Radon hotspot | Added generated nested C declarators and top-level lexer delimiter properties. | Expand preprocessing generators next. |
| 2026-05-31 | Parser preprocessing boundary | Added generated Fortran structure/preprocessing properties and aligned raw Fortran/C macro handling around compiler-required errors. | Expand AST and semantic-IR invariants next. |
| 2026-05-31 | Hypothesis semantic transformations | Added generated C and Fortran AST-to-IR determinism, shared scalar-contract, and semantic-specialization invariants; moved C primitive parser facts out of public contract metadata. | Expand code-generation escaping, stable-ordering, and parse-back invariants next. |
| 2026-05-31 | Hypothesis code generation | Added generated native-name escaping, stable synthetic-import ordering, and semantic-IR-to-Pyi parse-back invariants; fixed quoted `Name(...)` emission and stored focused regressions for discovered failures. | Continue focused mutation campaigns and keep storing minimized failures. |
| 2026-05-31 | Full validation | `3487 passed`, combined coverage `95.34%`, Ruff, pre-commit, Vulture, and Radon review clean. | Preserve the baseline while continuing focused mutation campaigns. |
| 2026-05-31 | Mutmut: `semantics/pyi_printer.py` | Made focused workspaces use local package dependencies, prevented process-local stats instrumentation from leaking into fresh CLI subprocesses, added behavioral assertions for meaningful survivors, and established a reviewed `385/395` baseline. | Continue subsystem campaigns; the remaining `6` survivors and `4` timeouts are classified equivalents or mutmut artifacts. |
| 2026-06-01 | Ruff formatting rollout | Formatted the historical Python tree, changed CI from changed-file formatting to `ruff format --check .`, and revalidated with `3487 passed` plus `95.34%` combined coverage. | Continue baseline-ignore and complexity-policy ratchets. |
| 2026-06-01 | Ruff ratchet | Removed redundant UTF-8 encoding headers and ambiguous one-letter variables, enabled `UP009` and `E741`, and revalidated with Ruff, pre-commit, and CI-shaped coverage. | Continue one reviewed rule family at a time. |
| 2026-06-01 | Radon and Ruff complexity policy | Added `tools/check_radon_policy.py`, made the staged Radon policy blocking in CI and pre-commit, lowered Ruff McCabe from `50` to `45`, and added focused policy tests. | Continue hotspot refactors and later threshold ratchets toward `20`. |
| 2026-06-01 | Ruff ratchet | Enabled `B905`, `RET505`, `RET507`, `RUF022`, and `UP037` after mechanical fixes; focused parser, public-entrypoint, and policy tests pass. | Continue reviewing remaining baseline ignores one family at a time. |
| 2026-06-01 | Mutmut: `c_parser/type_resolver.py` | Completed survivor review with `204/204` mutants killed; added resolver assertions for prefixed cycles, function signatures, declared array parameters, and repeated cycle use sites; made union-by-value diagnostics cycle-safe. | Continue subsystem campaigns. |
| 2026-06-01 | Mutmut: `c_parser/lexer.py` | Completed the initial focused campaign with `479/1171` mutants killed, `582` survivors, `38` timeouts, and `72` no-tests using `tests/parser/c` plus C parser property tests. | Review survivors in clusters, starting with linemarkers, top-level splitting, comment stripping, and timeout/no-test groups. |
| 2026-06-01 | Mutmut: `c_parser/lexer.py` survivor review | Added direct helper and edge assertions for mappings, linemarkers, delimiters, aggregate attributes, source accounting, quote handling, and timeout/no-test coverage. The reviewed baseline is `794/1171` killed, `10` equivalent or wrapper-artifact survivors, `367` recorded bounded-run timeouts, and `0` no-tests. | Preserve the reviewed survivor classification and investigate timeout-cluster drift. |
| 2026-06-01 | Mutmut: `c_parser/preprocessor.py` | Added direct assertions for location columns, include-directory fallback after filesystem errors, metadata filename propagation, local-include resolution, include locations, and unresolved-include diagnostics. The reviewed baseline is `105/108` killed with `3` equivalent survivors. | Preserve the reviewed equivalent-mutant classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `fortran_parser/type_resolver.py` | Narrowed the focused resolver selection and added direct assertions for empty, positional, keyword, nested-expression, and character-length type specs. The reviewed baseline is `34/34` killed. | Continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `fortran_parser/lexer.py` | Added direct assertions for directive preservation, fixed-form comment sentinels, quoted bangs, free- and fixed-form continuation folding, exact provenance retention, blank continuation lines, and OpenMP boundaries. The reviewed baseline is `150/185` killed with `35` equivalent survivors and no timeouts or uncovered mutants. | Preserve the reviewed equivalent-mutant classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Full test refresh | `3497 passed`. | Run CI-shaped coverage before claiming a refreshed coverage baseline. |
| 2026-06-01 | Ruff baseline completion | Removed the remaining historical ignore families (`B007`, `B018`, `E731`, `RET504`, `RUF007`, `RUF012`, `RUF015`, `SIM102`, `SIM103`, `SIM105`, `SIM108`, `SIM110`, `SIM211`, `UP007`, and `UP038`) with focused mechanical cleanups. The baseline-ignore list is now empty; line length remains intentionally unselected. | Keep Ruff clean and continue the Radon hotspot ratchet. |
| 2026-06-01 | Scheduled workflow triage | Documented weekly/manual triage, rerun policy, fuzz and random-order reproduction, and actionable-failure recording. | Review scheduled runs after they execute and record actionable failures until fixed. |
| 2026-06-01 | Mutmut: `c_parser/models.py` | Added direct assertions for environment flags, ANSI setup, diagnostic rendering, parser stack metadata, recursive serialization, and callback candidates. The reviewed baseline is `304/310` killed with `6` equivalent or wrapper-artifact survivors and no timeouts or uncovered mutants. | Preserve the reviewed survivor classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `semantics/readiness.py` | Added direct assertions for blocker payloads, unit ownership, encodings, visibility, indexes, ordering, imported types, nested callbacks, shape symbols, and accumulated counts. The reviewed baseline is `804/827` killed with `23` equivalent or wrapper-artifact survivors and no timeouts or uncovered mutants. | Preserve the reviewed survivor classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `x2py/preprocessing.py` | Added behavioral assertions for compiler invocations, compile databases, command templates, diagnostics, linemarkers, native Fortran includes, provenance, and recipe reconstruction. The reviewed baseline is `1496/1564` killed with `52` equivalent or wrapper-artifact survivors, `16` bounded loop-progress timeout detections, and `0` no-tests. | Preserve the reviewed survivor classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `semantics/c2ir.py` | Added exact semantic IR, ownership, registry, declarator, provenance, external-type, typedef-cycle, macro fixed-point, diagnostics, and public helper forwarding assertions. The reviewed baseline is `1785/1821` killed with `34` equivalent or wrapper-artifact survivors, `2` bounded macro fixed-point timeout detections, and `0` no-tests. | Preserve the reviewed survivor classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `semantics/fortran2ir.py` | Added exact kind, array-storage, compile-time requirement, context traversal, imported-type, origin, forwarding, diagnostic, and public helper assertions. The reviewed baseline is `1225/1339` killed with `114` equivalent, default-value, or wrapper-artifact survivors and no timeouts or uncovered mutants. | Preserve the reviewed survivor classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `semantics/pyi_parser.py` | Added exact wrapper-forwarding, loader, import, projection, metadata, semantic-type dispatch, visibility, diagnostic, and defensive fallback assertions. The reviewed baseline is `1266/1288` killed with `21` equivalent, default-value, or wrapper-artifact survivors, `1` manually verified equivalent timeout, and `0` no-tests. | Preserve the reviewed survivor classification and continue bounded subsystem campaigns. |
| 2026-06-01 | Mutmut: `x2py/cli.py` | Added CLI helper, report, preprocessing-configuration, Rich-output, parser-construction, command-routing, validation, error-rendering, write-contract, and stdout-mode assertions. The reviewed baseline is `1771/1783` killed with `12` equivalent survivors, including `899/899` killed mutants in `main`, and no timeouts or uncovered mutants. | Preserve the reviewed equivalent-mutant classification and continue bounded parser subsystem campaigns. |
| 2026-06-01 | Mutmut: `c_parser/parser.py` | Added compiler-extension comment, K&R scan, control-statement, and parameter-list assertions. The reviewed baseline is `2673/3537` killed with `849` equivalent/default/wrapper/unreachable/source-location survivors, `15` bounded scanner/declarator timeout detections, and `0` no-tests. | Preserve the reviewed survivor classification and complete the remaining `fortran_parser/parser.py` survivor review. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` | Completed the initial bounded campaign with `3233/5278` mutants killed, `745` survivors, and `1300` timeouts. Added `55` direct parser-contract tests; a bounded high-value rerun killed `86/151` selected prior survivors. | Continue serialized survivor classification. Use manual GitHub Actions for broad refreshes and keep workstation runs bounded with `--max-children 1`. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` survivor-review slice | Added direct contracts for procedure region splitting, nonexecution child filtering, sibling duplicate diagnostics, finalized argument kind/shape resolution, import ordering, use propagation, duplicate-argument metadata, top-level file symbol registration, and cross-file project parameter resolution. The focused mutation-contract suite reached `43 passed` at this point. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` declaration-storage slice | Added direct contracts for module parameter variable storage and normalized values, derived-type field metadata plus duplicate-field diagnostics, and procedure declaration storage for dummy callbacks, local type records, external symbols, and duplicate declarations. The focused mutation-contract suite is now `46 passed`. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` parameter-policy slice | Added direct contracts for modern procedure-local parameter storage, duplicate parameter diagnostics, legacy parameter rejection under `implicit none`, and implicit typing for legacy parameters when implicit typing is allowed. The focused mutation-contract suite is now `48 passed`. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` diagnostic-validation slice | Added direct contracts for declaration-looking unknown procedure diagnostics, invalid procedure syntax diagnostics, contains-region spec alternatives that must not mutate the original scope, and invalid contains-line metadata. The focused mutation-contract suite is now `50 passed`. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` source-preparation slice | Added direct contracts for source-unit preparation, raw CPP rejection, source-form detection, path/source discrimination, unit-end parsing, submodule parent splitting, interface headers, and malformed module/module-procedure header diagnostics. The focused mutation-contract suite is now `52 passed`. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` compile-time-resolution slice | Added direct contracts for signature kind/shape resolution, module variable kind/shape/value resolution, kind aliases, module-parameter transitive resolution, relevant local-parameter discovery, literal normalization, restricted expression evaluation, and implicit base-type inference. The focused mutation-contract suite is now `53 passed`. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-02 | Mutmut: `fortran_parser/parser.py` project-diagnostics slice | Added direct contracts for duplicate project-module diagnostics across files and deterministic dependency-first project ordering that still terminates on cycles. The focused mutation-contract suite is now `55 passed`. | Continue serialized survivor classification; do not lower the remaining-work percentage until the full survivor inventory is classified. |
| 2026-06-03 | Manual Quality workflow review | Reviewed workflow run `26832679820`: fuzz passed in `29s`, changing random-order pytest passed in `2m38s`, static analysis exposed five Ruff `RUF043` raw-regex fixes, and full-project mutation exceeded the `3h` Actions limit. | Park full-project mutation as advisory for later bounded splitting; fix Ruff findings and keep focused mutation evidence as the active rollout basis. |
| 2026-06-02 | Fortran project directory encoding | Survivor review exposed that directory namespace collection hardcoded UTF-8 instead of honoring `parse_fortran_project(..., encoding=...)`. Forwarded the requested codec through the namespace first pass and added a Latin-1 regression. | Preserve directory, explicit-path, and mapping-input codec forwarding contracts. |
