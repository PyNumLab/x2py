# Documentation

Use the audience-specific entrypoints first:

- [User documentation](user.md): CLI/API usage, parser output, diagnostics,
  generated `.pyi` files, semantic contracts, and readiness.
- [Developer documentation](developer.md): parser and semantic implementation
  references, focused test files, fixture generators, CLI test commands, and
  maintenance workflows.

The repository [`README.md`](../README.md) remains the user-facing project
overview. Contribution and pull-request requirements remain in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Reference Files

- [C parser reference](c_parser.md)
- [Fortran parser reference](fortran_parser.md)
- [Semantic IR and `.pyi` reference](semantics.md)
- [Wrapper design notes](wrapper_design_notes.md)
- [Diagnostic code registry](diagnostic_codes.md)
- [Quality assurance](quality.md)
- [Semantic multilanguage wrapper runtime architecture](architecture/semantic_multilanguage_wrapper_runtime_architecture.md)

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
