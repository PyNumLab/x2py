# Documentation

Start with:

- [Tutorial](tutorial.md): the supported end-to-end workflow from Fortran
  source to an imported extension, plus semantic `.pyi` editing, readiness,
  and the current C boundary.
- [Verified examples cookbook](examples.md): copy-paste Fortran wrapper builds
  and calls, CLI inspection commands, compiler preprocessing recipes, Python
  API snippets, and blocker examples.
- [Fortran wrapper guide](fortran_wrapper.md): the complete generated Python
  contract, wrapper mechanism, ownership, lifetime, build modes, and current
  limitations.
- [Developer guide](developper_guide.md): implementation ownership, support
  evidence rules, parser references, focused tests, fixture generators, and
  change workflows.

The repository [`README.md`](../README.md) remains the user-facing project
overview. Contribution and pull-request requirements remain in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## User Contract References

- [Semantic IR reference](semantics.md)
- [Semantic `.pyi` format](pyi_format.md)
- [Diagnostic code registry](diagnostic_codes.md)
- [Fortran wrapper guide](fortran_wrapper.md): supported Python API, examples,
  ownership, lifetime, naming, concurrency, and current limitations

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

Design documents describe deferred or long-term decisions. They are not
evidence for behavior beyond the runtime Fortran contracts proved by the
[Fortran wrapper guide](fortran_wrapper.md) and its linked tests. In
particular, the wrapper backend for user-supplied C inputs remains future work.

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
