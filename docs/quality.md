# Quality Assurance

This project uses a staged Python QA stack: fast bug-focused checks are suitable
for every pull request, while heavier dead-code, complexity, benchmark, fuzz,
and mutation workflows are run manually or on a schedule.

Track the remaining rollout work and record completed QA passes in the
[`quality adoption checklist`](quality_adoption_checklist.md).

## Tool Roles

- `ruff`: fast linting and formatting. It catches undefined names, unused
  imports, import-order drift, suspicious bug patterns, simplifiable code, and
  very high cyclomatic complexity.
- `hypothesis`: property-based testing. It generates edge cases and shrinks
  failures to small examples, which is useful for parsers, AST transforms, and
  code generators.
- `mutmut`: mutation testing. It changes small pieces of implementation code
  and checks whether tests fail, exposing weak assertions and missing cases.
- `vulture`: dead-code detection. It finds likely unused functions, classes,
  variables, and unreachable definitions.
- `radon`: complexity and maintainability metrics. It identifies functions
  whose control flow is risky enough to deserve decomposition or focused tests.
- `bandit`: security scanning for unsafe Python patterns such as risky
  subprocess, file, crypto, or deserialization usage.
- `pip-audit`: dependency vulnerability scanning against Python advisory data.
- `pytest-randomly`: randomized test order and repeatable random seeds to catch
  hidden test ordering dependencies.
- `pytest-xdist`: parallel pytest execution, useful for keeping broad parser
  and fixture suites fast.
- `pytest-benchmark`: repeatable benchmark tests and JSON output for
  performance regression tracking.

## Install

Install the package plus the QA toolchain:

```bash
python -m pip install -e ".[qa]"
```

If your shell only exposes `python3`, use:

```bash
python3 -m pip install -e ".[qa]"
```

Install pre-commit hooks after the QA extra is available:

```bash
pre-commit install
```

## Test Organization

Use the current test tree as the default split:

- Unit tests: keep narrow behavior tests near the existing domain folders such
  as `tests/parser`, `tests/semantics`, and `tests/pyi`.
- Regression tests: add a test next to the subsystem that failed, with a name
  describing the bug shape. Mark with `@pytest.mark.regression` when useful.
- Property tests: put generated invariant tests in `tests/property`.
- Fuzz-like parser tests: keep bounded generators in `tests/property`, mark
  with `@pytest.mark.fuzz`, and run with the `fuzz` Hypothesis profile.
- Benchmark tests: put explicit benchmarks in `tests/benchmarks` and mark with
  `@pytest.mark.benchmark`.

## Local Commands

Fast inner loop:

```bash
pytest -q
ruff check .
ruff format .
```

CI-like test run with randomized ordering, xdist, subprocess coverage, and the
CI Hypothesis profile:

```bash
HYPOTHESIS_PROFILE=ci \
COVERAGE_PROCESS_START=pyproject.toml \
PYTHONPATH=. \
python -m coverage run -m pytest -q -n auto --randomly-seed=1 \
  --benchmark-disable
python -m coverage combine
python -m coverage report
```

Reproduce a random-order failure:

```bash
pytest -q --randomly-seed=<seed-from-failing-run>
```

Run property tests only:

```bash
pytest -q -m property --hypothesis-profile=ci
```

Run longer fuzz-like tests:

```bash
HYPOTHESIS_PROFILE=fuzz pytest -q -m fuzz --hypothesis-show-statistics
```

Run security and dependency checks:

```bash
bandit -c pyproject.toml -r c_parser fortran_parser semantics x2py --severity-level medium --confidence-level medium
pip-audit . --cache-dir /tmp/pip-audit-cache
```

For a full low-severity Bandit review, omit the severity and confidence flags.
Expect reviewed subprocess usage and parser tokens such as `"*"` to need triage.

Current low-severity Bandit findings were reviewed on 2026-05-31:

- `B105` findings are parser sentinel text such as `"*"` and preprocessing
  template tokens such as `"{source}"`; they are not credentials.
- `B404` and `B603` findings are intentional compiler, probe-executable, and
  preprocessor invocation paths. They pass argument vectors to `subprocess.run`
  without shell execution. Re-review them if command construction or trust
  boundaries change.

Keep these findings visible in full Bandit reports instead of suppressing them
globally.

Run dead-code and complexity reports:

```bash
vulture
radon cc c_parser fortran_parser semantics x2py -n C -s --total-average
radon mi c_parser fortran_parser semantics x2py -s
```

Run mutation testing:

```bash
python tools/run_mutmut.py run
mutmut results
mutmut show <mutant-id>
mutmut tests-for-mutant <mutant-id>
```

The repository wrapper joins mutmut's mutant-generation workers and waits
specifically for its mutation workers. This avoids a process-reaping failure
seen with mutmut 3.5.0. It also keeps mutmut's process-local stats
instrumentation out of fresh CLI subprocesses. Focused workspaces copy the
local package directories so imports resolve consistently when only one module
is mutated.

For a focused local mutation pass, temporarily narrow `tool.mutmut.paths_to_mutate`
in `pyproject.toml` to the subsystem you are improving, then restore it before
committing.

Run benchmarks and save results:

```bash
pytest -q -m benchmark --benchmark-only --benchmark-autosave
pytest-benchmark compare
```

## Hypothesis Patterns

Prefer generated valid subsets before generating arbitrary invalid text. Valid
subset tests give strong invariants with fewer false positives.

Example parser invariant:

```python
from hypothesis import given, strategies as st

from c_parser import parse_c_file


@given(st.lists(st.integers(min_value=0, max_value=20), unique=True))
def test_generated_c_prototypes_preserve_parameter_order(ids):
    params = ", ".join(f"int p_{i}" for i in ids) or "void"
    source = f"int fn({params});\n"

    parsed = parse_c_file(source, filename="generated.h")

    assert parsed.diagnostics == []
    assert [p.name for p in parsed.functions[0].parameters] == [f"p_{i}" for i in ids]
```

Good invariants for this codebase:

- parsing the same source twice produces the same JSON/dict representation;
- generated declarations preserve name order and source locations;
- semantic conversion is deterministic for equivalent parser models;
- Pyi emission can be parsed back into equivalent semantic IR for supported
  subsets;
- malformed input raises parser-owned diagnostic exceptions, not arbitrary
  exceptions.

## Mutation Workflow

Use mutation testing after adding or changing behavior, not on every edit:

1. Run the focused normal tests first.
2. Narrow `tool.mutmut.paths_to_mutate` if the full mutation pass is too broad.
3. Run `python tools/run_mutmut.py run`.
4. Inspect survivors with `mutmut results` and `mutmut show <id>`.
5. Add assertions that fail for real behavioral changes.
6. Avoid tests that only assert implementation details or removed behavior.

For parser/compiler changes, high-value mutants are usually around:

- branch conditions in grammar-unit slicing;
- type/kind normalization;
- source-location arithmetic;
- AST or IR field mapping;
- diagnostic code selection;
- codegen escaping and stable ordering.

## Strictness Defaults

Current defaults are intentionally staged for an existing parser codebase:

- Hard gate: pytest, coverage threshold, Ruff bug-focused lint and formatting,
  Bandit, pip-audit, and Vulture.
- Advisory: Radon full reports, because complexity reduction needs focused
  tests and gradual refactoring.
- Manual: mutmut full-project runs.
- Scheduled or manual: long Hypothesis fuzz profiles, changing random-order
  runs, and performance benchmark comparisons.

After the first cleanup pass, ratchet strictness in this order:

1. Remove Ruff baseline ignores one rule family at a time.
2. Keep Vulture exclusions narrow as new public/plugin APIs are added.
3. Lower Ruff `max-complexity` from 50 toward 20 for new code.
4. Add benchmark comparison thresholds only for stable, meaningful workloads.

## Parser And Codegen Practices

- Store minimal failing parser inputs from Hypothesis in regression tests.
- Keep golden files for broad compatibility, but add small unit tests for the
  exact rule that changed.
- Test round trips where possible: parse, convert to IR, emit, parse again.
- Use metamorphic tests: whitespace changes, declaration order changes, and
  equivalent type spellings should preserve semantics where the language allows.
- Assert diagnostics structurally: code, severity, location, and message class.
- Keep fuzz generators bounded. Prefer many small syntactically valid programs
  over huge random strings in pull-request CI.
- Benchmark parser/codegen hot paths with representative generated sources and
  real corpus fixtures.

## CI Layout

- `.github/workflows/tests.yml` runs pytest with xdist, pytest-randomly,
  Hypothesis CI profile, and coverage combine/report.
- `.github/workflows/quality.yml` runs Ruff, Bandit, pip-audit, blocking Vulture,
  and advisory Radon reports. Manual dispatch runs mutmut. Scheduled/manual jobs run
  bounded parser fuzzing, a changing pytest-randomly seed, and parser/codegen
  benchmarks. Benchmark JSON is uploaded as a workflow artifact for comparison.
- `.pre-commit-config.yaml` runs Ruff and Bandit on commit, with Vulture and
  Radon available as manual reports.

## References

- Ruff configuration: https://docs.astral.sh/ruff/configuration/
- Pytest configuration: https://docs.pytest.org/en/latest/reference/customize.html
- Coverage subprocess behavior: https://coverage.readthedocs.io/en/latest/config.html
- Hypothesis settings profiles: https://hypothesis.readthedocs.io/en/latest/tutorial/settings.html
- Mutmut configuration: https://mutmut.readthedocs.io/en/latest/
- Vulture configuration: https://pypi.org/project/vulture/
- Radon command line: https://radon.readthedocs.io/en/stable/commandline.html
- Bandit configuration: https://bandit.readthedocs.io/en/latest/config.html
- pip-audit: https://github.com/pypa/pip-audit
- pytest-xdist: https://pytest-xdist.readthedocs.io/
- pytest-randomly: https://github.com/pytest-dev/pytest-randomly
- pytest-benchmark: https://pytest-benchmark.readthedocs.io/
