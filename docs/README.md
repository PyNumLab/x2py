# Documentation

The repository [`README.md`](../README.md) is the starting point for usage and
examples. Contribution and pull-request requirements remain in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Diagnostics

- [Diagnostic code registry](diagnostic_codes.md): stable parser error and
  report-diagnostic categories shared by the frontend documentation.

## Architecture And Semantic Interfaces

- [Semantic multilanguage wrapper runtime architecture](architecture/semantic_multilanguage_wrapper_runtime_architecture.md):
  long-term architecture and runtime model.
- [Wrapper `.pyi` format](semantics/pyi_format.md): editable semantic
  interface syntax and conversion behavior.
- [C to semantic IR mapping](semantics/c2ir_mapping.md): implemented C
  semantic conversion subset and blocker policy.
- [Datatype mapping](semantics/datatype_mapping.md): C and Fortran primitive
  type mapping to semantic and NumPy dtype names.
- [Self-contained C semantic `.pyi` specification](semantics/c_pyi_self_contained_specification.md):
  staged C wrapper interface design.

## Roadmap And Backlog

- [x2py checklist](x2py_checklist.md):
  pending frontend, shared semantics, and `.pyi` tasks.
- [Quality assurance](quality.md):
  QA commands, active tool cadence, per-tool benefits, discovered defects,
  adoption status, and scheduled-triage process.

## Parser Frontends

### Fortran

- [Fortran parser reference](fortran/fortran_parser.md): supported subset,
  command-line usage, APIs, diagnostics, implementation inventory, and
  maintenance guard policy.

### C

- [C parser reference](c_parser/c_parser_reference.md): implemented parser
  behavior, command workflow, semantic handoff, architecture notes, and testing
  workflow.

## Fixture Notes

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
