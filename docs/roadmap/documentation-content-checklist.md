---
title: Documentation Content Checklist
audience: contributors, maintainers
prerequisites: documentation architecture
related: ../documentation-architecture.md, index.md, semantic-pyi-wrapper-checklist.md
status: active-roadmap
---

# Documentation Content Checklist

This checklist tracks documentation pages that exist but are still placeholders,
thin drafts, or missing evidence. It is not an implementation checklist. Use
[Semantic `.pyi` Wrapper Checklist](semantic-pyi-wrapper-checklist.md) for
runtime parity, policy, and wrapper implementation work.

A page is complete only when it gives readers the information they need without
relying on private conversation or implied project knowledge.

## Completion Rule

Move an item from the open queue to completed content evidence only when all of
these are true:

- [ ] The page status is accurate: `maintained` for current public behavior,
  `design` for accepted architecture, or `not-yet-implemented` for explicit
  future behavior.
- [ ] The page explains what is supported now, what is unsupported, and where to
  find the supporting tests, fixtures, examples, or source owner.
- [ ] User-facing pages include a task-oriented workflow, expected output or API
  shape, limitations, and troubleshooting links.
- [ ] Developer-facing pages include ownership boundaries, source routes,
  focused verification commands, and rules for updating related docs.
- [ ] Examples are either executable documentation examples, checked fixtures,
  or clearly labeled illustrative snippets.
- [ ] Reuse earlier examples by reference instead of reprinting them, unless the
  page must be self-contained for a first-time user task.
- [ ] User-facing examples use clean copyable filenames and module names; keep
  fixture-style names such as parser/test abbreviations out of beginner docs.
- [ ] Documentation-only changes use focused docs checks and `git diff --check`;
  reserve the full static-analysis suite for code, tests, build/tooling changes,
  or explicit pre-merge verification.
- [ ] Area indexes, `docs/README.md`, `mkdocs.yml`, related front matter, and
  `tests/tools/test_documentation_structure.py` stay synchronized.

## Open Documentation Queue

Only unfinished documentation content belongs here. When a page is filled, move
the item to completed content evidence and update the page status in the same
change.

The queue is ordered by execution priority and dependency. Complete current
user workflows and their supporting references first. Leave larger example
investments and site-publication decisions until the underlying content is
stable. Within each section, work from foundational pages toward dependent or
more specialized pages.

### User Guide

- [ ] `docs/user-guide/wrapping-functions.md`: document scalar returns, array
  returns, generated Python signatures, native calling limits, and checked call
  assertions.
- [ ] `docs/user-guide/wrapping-subroutines.md`: document `intent(in)`,
  `intent(out)`, `intent(inout)`, hidden versus visible outputs, and tuple or
  storage projection rules.
- [ ] `docs/user-guide/wrapping-modules.md`: document module functions, public
  constants, module variables, saved state, unsupported common-block exposure,
  and generated package shape.
- [ ] `docs/user-guide/arrays.md`: document dtype mapping, rank and shape
  validation, contiguity, stride support, zero-sized arrays, order requirements,
  and NumPy error messages.
- [ ] `docs/user-guide/optional-arguments.md`: document Python call syntax,
  omitted arguments, defaults, unsupported optional combinations, and diagnostics.
- [ ] `docs/user-guide/generic-interfaces.md`: document named generic overloads,
  type-bound overloads, ambiguity handling, operator dispatch, and generated
  `.pyi` overload stubs.
- [ ] `docs/user-guide/allocatable-arrays.md`: document allocatable results,
  borrowed module or component views, replacement semantics, null or unallocated
  state, and ownership limits.
- [ ] `docs/user-guide/pointer-arguments.md`: document supported call-local
  pointer inputs, pointer snapshot results, blocked reassociation cases, and
  lifetime rules.
- [ ] `docs/user-guide/wrapping-derived-types.md`: document generated classes,
  constructors, fields, methods, finalizers, opaque layouts, accessor-only
  behavior, and unsupported polymorphic forms.
- [ ] `docs/user-guide/memory-management.md`: document ownership transfer,
  borrowed views, destructor responsibility, finalization, release limits, and
  the policy-completion source of truth.
- [ ] `docs/user-guide/callbacks.md`: document immediate callback arguments,
  callback signatures, exception behavior, lifetime limits, GIL expectations,
  and unsupported persistent procedure pointers.
- [ ] `docs/user-guide/enumerations.md`: document generated constants or enum
  shapes, supported Fortran enum forms, unsupported forms, and type-checking
  expectations.
- [ ] `docs/user-guide/error-handling.md`: document wrapper validation errors,
  native failure projection, diagnostics, traceback behavior, and cleanup
  guarantees.
- [ ] `docs/user-guide/packaging.md`: document generated packages, generated
  makefiles, native artifacts, rebuild flow, import paths, and local distribution
  assumptions.
- [ ] `docs/user-guide/distribution.md`: document what can be distributed today,
  native dependency constraints, platform caveats, and what remains future work.

### Reference Material

- [ ] `docs/reference/generated-functions.md`: document generated function and
  subroutine signatures, output projection, validation errors, and overload
  representation.
- [ ] `docs/reference/generated-modules.md`: document generated module package
  shape, module-level functions, variables, constants, hidden native names, and
  import rules.
- [ ] `docs/reference/generated-classes.md`: document generated class surfaces,
  constructors, fields, methods, finalizers, ownership metadata, and unsupported
  class shapes.
- [ ] `docs/reference/configuration-files.md`: document public configuration
  files only after their stable contract exists, including build manifests,
  generated makefiles, coverage config, and docs tooling config.

### Troubleshooting, FAQ, And Releases

- [ ] `docs/troubleshooting/index.md`: route users by symptom: install, build,
  compiler, runtime, platform, wrapper contract, and generated artifact issues.
- [ ] `docs/troubleshooting/installation-issues.md`: document missing Python
  headers, NumPy, compiler packages, virtual environments, and platform package
  names.
- [ ] `docs/troubleshooting/build-issues.md`: document compile/link failures,
  missing native libraries, Makefile regeneration, output directories, and
  verbose logs.
- [ ] `docs/troubleshooting/compiler-issues.md`: document compiler detection,
  Fortran flags, preprocessing, ABI probes, GNU ABI assumptions, and kind
  support failures.
- [ ] `docs/troubleshooting/runtime-issues.md`: document import failures,
  symbol lookup errors, dtype or shape errors, callback exceptions, finalization,
  and cleanup symptoms.
- [ ] `docs/troubleshooting/platform-specific-issues.md`: document Linux,
  macOS, Windows, compiler, linker, and shared-library path caveats.
- [ ] `docs/changelog/index.md`: define changelog policy, release-note shape,
  migration notes, and how docs changes are tracked with releases.

<!-- X2PY_C_DOCS_START
- [ ] `docs/faq/index.md`: add answers for source versus `.pyi` builds,
  supported languages, C-input future work, generated files, editable contracts,
  unsupported features, and where to report bugs.
X2PY_C_DOCS_END -->

### Developer And Contributor Guides

- [ ] `docs/developer-guide/adding-a-feature.md`: document the feature workflow
  from contract docs to implementation, tests, fixtures, support matrix, and
  release notes.
- [ ] `docs/developer-guide/adding-a-fortran-construct.md`: document parser,
  semantic, readiness, wrapper, docs, and fixture updates for a new Fortran
  construct.
- [ ] `docs/developer-guide/adding-a-code-generation-backend.md`: document
  backend acceptance criteria, ownership boundaries, generated artifacts, tests,
  and support claims.
- [ ] `docs/developer-guide/testing-strategy.md`: document test layers, focused
  verification paths, fixture regeneration, documentation examples, wrapper
  runtime tests, and static-analysis gates.
- [ ] `docs/developer-guide/build-system.md`: document native compile model,
  generated Makefiles, build manifests, runtime support files, compiler probes,
  and future packaging boundaries.
- [ ] `docs/developer-guide/coding-standards.md`: document Python style,
  documentation front matter, no-compatibility-layer rule, parser/codegen
  organization, and review expectations.
- [ ] `docs/developer-guide/ci-cd.md`: document current GitHub Actions gates,
  coverage policy, static-analysis policy, docs checks, and local caveats for
  CI-only environment values.
- [ ] `docs/developer-guide/release-process.md`: document versioning, changelog,
  release verification, wheel/source distribution limits, and documentation
  publication steps.
- [ ] `docs/contributing/contribution-guide.md`: document setup, issue scope,
  expected docs updates, tests, static checks, and pull-request checklist.
- [ ] `docs/contributing/pull-request-workflow.md`: document branch workflow,
  commit message policy, required evidence, review response, and CI handling.
- [ ] `docs/contributing/review-process.md`: document review focus, support
  claims, docs completeness, fixture quality, and blocking versus advisory
  comments.
- [ ] `docs/contributing/coding-standards.md`: document public contributor style
  rules, docs metadata, TODO markers, and support-claim discipline.

### Design And Internal Architecture

- [ ] `docs/design/overall-architecture.md`: document system components,
  pipeline stages, data contracts, supported language routes, and deferred
  routes.
- [ ] `docs/design/parser-architecture.md`: document parser ownership,
  preprocessing boundaries, model facts, diagnostics, and fixture strategy.
- [ ] `docs/design/semantic-analysis.md`: document source-to-IR lowering,
  `.pyi`-to-IR loading, policy completion, readiness blockers, and invariants.
- [ ] `docs/design/runtime-model.md`: document runtime support files, generated
  wrappers, native state, callbacks, threading, and finalization.
- [ ] `docs/design/error-propagation-model.md`: document diagnostic categories,
  Python exception projection, native failure handling, cleanup, and user-facing
  message shape.
- [ ] `docs/design/memory-ownership-model.md`: finish the design page around
  policy-completion ownership decisions, transfer actions, mutability, setter
  exposure, and release responsibility.
- [ ] `docs/internal-architecture/ast-design.md`: document parser AST, semantic
  IR, codegen AST, what each layer may store, and what must not leak across
  layers.
- [ ] `docs/internal-architecture/semantic-passes.md`: document semantic pass
  ordering, completed policy decisions, readiness checks, and handoff to
  `ir2ast`.
- [ ] `docs/internal-architecture/wrapper-generation-pipeline.md`: finish the
  bridge and binding generation route with current policy-completion boundaries
  and focused evidence.
- [ ] `docs/internal-architecture/type-system.md`: document scalar kinds, arrays,
  characters, derived types, pointers, allocatables, callbacks, and unsupported
  storage forms.
- [ ] `docs/internal-architecture/runtime-layer.md`: document runtime support
  installation, extension initialization, callbacks, cleanup, and shared native
  state.
- [ ] `docs/internal-architecture/ownership-tracking.md`: document ownership
  facts, transfer, borrowing, alias storage, destruction, writeback, and setter
  exposure.
- [ ] `docs/internal-architecture/dependency-analysis.md`: document current
  source ordering, preprocessing dependency facts, generated build plans, and
  future automatic dependency discovery.
- [ ] `docs/internal-architecture/error-handling-pipeline.md`: document
  diagnostic creation, path-aware `.pyi` loader errors, readiness failures,
  generated validation failures, and native runtime errors.
- [ ] `docs/internal-architecture/symbol-tables.md`: document public naming,
  generated-symbol reservation, collision policy, imports, scopes, and package
  names.

<!-- X2PY_C_DOCS_START
- [ ] `docs/design/code-generation.md`: document codegen AST boundaries, bridge
  generation, CPython binding generation, printers, and forbidden semantic
  inference in backends.
- [ ] `docs/design/cpython-integration.md`: document CPython API usage, NumPy
  C API integration, extension module layout, reference ownership, and error
  propagation.
X2PY_C_DOCS_END -->

### Tutorials And Examples

- [ ] `docs/tutorials/numerical-solver.md`: add a fast checked solver fixture,
  build command, Python call, expected numeric output, and validation notes.
- [ ] `docs/tutorials/scientific-library.md`: document a small multi-routine
  library workflow, package shape, generated `.pyi` review, and regression
  checks.
- [ ] `docs/tutorials/modern-fortran-project.md`: document modules, derived
  types, arrays, constructors, and limitations using checked modern Fortran
  examples.
- [ ] `docs/tutorials/large-fortran-codebase.md`: document source ordering,
  dependency strategy, generated contract review, staged verification, and
  current limits for automatic dependency discovery.
- [ ] `docs/tutorials/packaging.md`: document packaging a generated extension,
  native artifacts, wheel limitations, and reproducible build notes.
- [ ] `docs/examples-gallery/blas-wrapper.md`: add the minimal BLAS-style
  runtime example or document the external dependency, with build, import, and
  numerical assertions.
- [ ] `docs/examples-gallery/lapack-wrapper.md`: document the LAPACK example as
  CI-owned by default, including why local runs are optional and what evidence CI
  supplies.
- [ ] `docs/examples-gallery/openmp-example.md`: document supported OpenMP path,
  required compiler flags, runtime environment variables, and fallback behavior.
- [ ] `docs/examples-gallery/object-oriented-fortran.md`: document classes,
  type-bound procedures, construction, finalization, and unsupported object
  model features with checked output.
- [ ] `docs/examples-gallery/ode-solver.md`: add a compact checked ODE fixture,
  expected result tolerance, and failure troubleshooting.
- [ ] `docs/examples-gallery/cfd-mini-example.md`: define a small enough fixture,
  supported array contracts, build command, and runtime validation.
- [ ] `docs/examples-gallery/mpi-example.md`: keep this page explicitly
  not-yet-implemented until MPI build, runtime, and distribution constraints have
  real evidence.

### Project Entry And Site Shell

- [ ] `docs/index.md`: replace the draft landing page with the current project
  promise, supported workflow entry points, installation links, support matrix
  links, limitation links, and a clear path to first successful wrapper build.
- [ ] `docs/documentation-architecture.md`: resolve the remaining generator and
  migration TODOs, then turn the page into the maintained documentation contract.
- [ ] `docs/tutorials/index.md`: explain which tutorials are maintained and which
  are planned, with expected prerequisites and runtime cost.
- [ ] `docs/examples-gallery/index.md`: split verified cookbook recipes from
  planned larger examples and state the evidence required for each example.
- [ ] `docs/design/index.md`: explain which design documents are accepted
  architecture and which are placeholders.
- [ ] `docs/internal-architecture/index.md`: route maintainers to pipeline,
  semantic pass, runtime, type-system, ownership, and symbol-table pages.
- [ ] `docs/contributing/index.md`: route contributors to contribution,
  pull-request, review, and coding-standard pages.

<!-- X2PY_C_DOCS_START
- [ ] `docs/user-guide/index.md`: group user guides by workflow and separate
  current Fortran wrapper support from future C-input wrapper support.
X2PY_C_DOCS_END -->

## Completed Content Evidence

These pages already carry maintained content or active implementation roadmap
evidence. Keep them current as behavior changes, but do not treat them as the
primary placeholder queue.

- [x] `docs/getting-started/index.md`: maintained beginner route from
  installation through the normal rebuild workflow.
- [x] `docs/getting-started/installation.md`: maintained user and contributor
  installation, native prerequisites, header checks, and platform boundaries.
- [x] `docs/getting-started/verification.md`: maintained package, inspection,
  native build, generated-artifact, and escalation checks.
- [x] `docs/getting-started/first-wrapped-function.md`: maintained checked
  scalar build, call result, exact dtype contract, and failure route.
- [x] `docs/getting-started/first-wrapped-module.md`: maintained checked module
  namespace, public state, saved state, visibility, and limitation guide.
- [x] `docs/getting-started/beginner-workflow.md`: maintained edit, inspect,
  readiness, build, smoke-test, artifact-review, and rebuild loop.
- [x] `docs/reference/semantic-ir.md`: maintained Semantic IR contract.
- [x] `docs/reference/semantic-pyi-format.md`: maintained semantic `.pyi`
  contract.
- [x] `docs/reference/cli-commands.md`: maintained CLI reference.
- [x] `docs/reference/python-api.md`: maintained Python API reference.
- [x] `docs/reference/diagnostic-codes.md`: maintained diagnostic registry.
- [x] `docs/user-guide/fortran-wrapper.md`: maintained Fortran wrapper contract.
- [x] `docs/user-guide/editing-semantic-pyi-contracts.md`: maintained editable
  `.pyi` contract guide.
- [x] `docs/tutorials/basic-wrapper.md`: maintained basic wrapper workflow.
- [x] `docs/examples-gallery/verified-cookbook.md`: maintained verified example
  cookbook.
- [x] `docs/examples-gallery/recipes/`: maintained recipe lane for checked
  command and API examples.
- [x] `docs/language-support/feature-matrix.md`: maintained support matrix.
- [x] `docs/developer-guide/maintainer-guide.md`: maintained maintainer guide.
- [x] `docs/developer-guide/source-map.md`: maintained source route map.
- [x] `docs/developer-guide/feature-to-code-map.md`: maintained feature route
  map.
- [x] `docs/developer-guide/repository-structure.md`: maintained repository tree
  reference.
- [x] `docs/developer-guide/fortran-parser-reference.md`: maintained Fortran
  parser reference.
- [x] `docs/developer-guide/quality-assurance.md`: maintained quality and QA
  policy reference.
- [x] `docs/internal-architecture/pipeline-map.md`: maintained pipeline and
  concept-ownership map.
- [x] `docs/roadmap/semantic-pyi-wrapper-checklist.md`: active implementation
  roadmap for semantic `.pyi` wrapper parity.

<!-- X2PY_C_DOCS_START
- [x] `docs/developer-guide/c-parser-reference.md`: maintained C parser
  reference.
X2PY_C_DOCS_END -->
