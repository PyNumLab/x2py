# Documentation

Start with:

- [Tutorial](tutorial.md): the supported end-to-end user workflow, semantic
  `.pyi` editing, readiness, and current boundaries.
- [Verified examples cookbook](examples.md): copy-paste CLI commands, compiler
  preprocessing recipes, Python API snippets, and blocker examples.
- [Developer guide](developper_guide.md): implementation ownership, support
  evidence rules, parser references, focused tests, fixture generators, and
  change workflows.

The repository [`README.md`](../README.md) remains the user-facing project
overview. Contribution and pull-request requirements remain in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## User Contract References

- [Semantic IR and `.pyi` reference](semantics.md)
- [Diagnostic code registry](diagnostic_codes.md)

These files identify implemented, maintained contracts. Any design-only
material inside them must be labeled explicitly. The tutorial and examples
should link back to the implemented sections instead of inventing broader
support claims.

## Maintainer References

- [Developer guide](developper_guide.md): maintainer entry point
- [C parser reference](c_parser.md)
- [Fortran parser reference](fortran_parser.md)
- [Quality assurance](quality.md)

## Design Documents

- [Wrapper design notes](wrapper_design_notes.md)
- [Semantic multilanguage wrapper runtime architecture](architecture/semantic_multilanguage_wrapper_runtime_architecture.md)

Design documents describe deferred or long-term wrapper decisions. They are
not evidence that runtime wrapper generation is currently implemented.

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
