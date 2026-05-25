# Documentation

The repository [`README.md`](../README.md) is the starting point for usage and
examples. Contribution and pull-request requirements remain in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Architecture And Semantic Interfaces

- [Semantic multilanguage wrapper runtime architecture](architecture/semantic_multilanguage_wrapper_runtime_architecture.md):
  long-term architecture and runtime model.
- [Wrapper `.pyi` format](semantics/pyi_format.md): editable semantic
  interface syntax and conversion behavior.
- [Self-contained C semantic `.pyi` specification](semantics/c_pyi_self_contained_specification.md):
  staged C wrapper interface design.

## Parser Frontends

### Fortran

- [Fortran parser reference](fortran/fortran_parser.md): supported subset,
  command-line usage, APIs, and diagnostics.
- [Fortran parser implementation reference](fortran/parser_implementation_reference.md):
  implementation inventory, testing workflow, and maintenance guard policy.

### C

- [C parser reference](c_parser/c_parser_reference.md): implemented parse-only
  frontend behavior and testing workflow.
- [C parser architecture plan](c_parser/c_parser_architecture.md): design and
  integration decisions.
- [C parser CLI workflow plan](c_parser/c_parser_cli_workflow.md): command
  surface and output contracts.
- [C parser remaining work checklist](c_parser/c_parser_implementation_checklist.md):
  pending implementation tasks.

## Fixture Notes

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
