---
title: Documentation
audience: users, contributors, maintainers
prerequisites: none
related: index.md, documentation-architecture.md
status: maintained
---

# Documentation

Start with:

- [Documentation site landing](index.md): the draft home page for the future
  documentation website.
- [Documentation architecture](documentation-architecture.md): the page
  metadata standard, recommended repository tree, and maturity roadmap.
- [User guide](user-guide/index.md): the maintained route from Fortran/Python
  datatype mapping through wrapper calls, ownership, runtime behavior,
  packaging, and distribution limits.
- [Verified examples cookbook](examples-gallery/verified-cookbook.md): copy-paste Fortran wrapper builds
  and calls, CLI inspection commands, compiler preprocessing recipes, Python
  API snippets, and blocker examples.
- [Fortran wrapper guide](user-guide/fortran-wrapper.md): the complete generated Python
  contract, wrapper mechanism, ownership, lifetime, build modes, and current
  limitations.
- [Maintainer guide](developer-guide/maintainer-guide.md): implementation ownership, support
  evidence rules, parser references, focused tests, fixture generators, and
  change workflows.
- [Basic wrapper tutorial](tutorials/basic-wrapper.md): the supported
  end-to-end Fortran workflow from source to an imported extension.

<!-- X2PY_C_DOCS_START
- [Basic wrapper tutorial](tutorials/basic-wrapper.md): the supported end-to-end workflow from Fortran
  source to an imported extension, plus semantic `.pyi` editing, readiness,
  and the current C boundary.
X2PY_C_DOCS_END -->

The repository [`README.md`](../README.md) remains the user-facing project
overview. Contribution and pull-request requirements remain in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Site-Ready Documentation Areas

- [Getting started](getting-started/index.md): maintained installation,
  verification, function, module, and rebuild workflows
- [User guide](user-guide/index.md)
- [Tutorials](tutorials/index.md)
- [Examples gallery](examples-gallery/index.md)
- [Reference](reference/index.md)
- [Language support](language-support/index.md)
- [Design documents](design/index.md)
- [Developer guide](developer-guide/index.md)
- [Internal architecture](internal-architecture/index.md)
- [Roadmap](roadmap/index.md)
- [FAQ](faq/index.md)
- [Troubleshooting](troubleshooting/index.md)
- [Changelog](changelog/index.md)
- [Contributing](contributing/index.md)

## User Contract References

- [Semantic IR reference](reference/semantic-ir.md)
- [Semantic `.pyi` format](reference/semantic-pyi-format.md)
- [Semantic `.pyi` wrapper checklist](roadmap/semantic-pyi-wrapper-checklist.md)
- [Documentation content checklist](roadmap/documentation-content-checklist.md)
- [Diagnostic code registry](reference/diagnostic-codes.md)
- [Generated functions](reference/generated-functions.md)
- [Generated modules](reference/generated-modules.md)
- [Generated classes](reference/generated-classes.md)
- [Configuration files](reference/configuration-files.md)
- [Fortran wrapper guide](user-guide/fortran-wrapper.md): supported Python API, examples,
  ownership, lifetime, naming, concurrency, and current limitations

These files identify implemented, maintained contracts. Any design-only
material inside them must be labeled explicitly. The tutorial and examples
should link back to the implemented sections instead of inventing broader
support claims.

## Maintainer References

- [Maintainer guide](developer-guide/maintainer-guide.md): maintainer entry point
- [Source map](developer-guide/source-map.md): source tree ownership,
  entrypoints, package map, and package-local README links
- [Feature to code map](developer-guide/feature-to-code-map.md): feature-first
  route to implementation files, tests, and support evidence
- [Pipeline map](internal-architecture/pipeline-map.md): maintainer route
  through the current wrapper and inspection pipelines
- [Fortran parser reference](developer-guide/fortran-parser-reference.md)
- [Quality assurance](developer-guide/quality-assurance.md)

<!-- X2PY_C_DOCS_START
- [C parser reference](developer-guide/c-parser-reference.md)
X2PY_C_DOCS_END -->

## Design Documents

- [Wrapper design notes](design/wrapper-design-notes.md)
- [Semantic multilanguage wrapper runtime architecture](design/semantic-multilanguage-wrapper-runtime-architecture.md)

Design documents describe deferred or long-term decisions. They are not
evidence beyond the Fortran contracts proved by the
[Fortran wrapper guide](user-guide/fortran-wrapper.md) and its linked tests.

<!-- X2PY_C_DOCS_START
Design documents describe deferred or long-term decisions. They are not
evidence for behavior beyond the runtime Fortran contracts proved by the
[Fortran wrapper guide](user-guide/fortran-wrapper.md) and its linked tests. In
particular, the wrapper backend for user-supplied C inputs remains future work.
X2PY_C_DOCS_END -->

## Archived Old Documentation

The previous top-level documentation files were moved to [old_docs](old_docs/).
They are retained for historical comparison only; active docs and navigation
live in the structured sections above.

README files under `tests/` intentionally remain next to the fixtures or
expected outputs they describe. They are local test-maintenance instructions,
not general project documentation.
