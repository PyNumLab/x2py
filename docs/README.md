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
- [Self-contained C semantic `.pyi` specification](semantics/c_pyi_self_contained_specification.md):
  staged C wrapper interface design.

## Roadmap And Backlog

- [x2py checklist](x2py_checklist.md):
  pending frontend, shared semantics, and `.pyi` tasks.

## Parser Frontends

### Fortran

- [Fortran parser reference](fortran/fortran_parser.md): supported subset,
  command-line usage, APIs, and diagnostics.
- [Fortran parser implementation reference](fortran/parser_implementation_reference.md):
  implementation inventory, testing workflow, and maintenance guard policy.

### C

- [C parser reference](c_parser/c_parser_reference.md): implemented parser
  behavior, semantic handoff, and testing workflow.
- [C parser architecture plan](c_parser/c_parser_architecture.md): design and
  integration decisions.
- [C parser CLI workflow plan](c_parser/c_parser_cli_workflow.md): command
  surface and output contracts.

## Fixture Notes

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
