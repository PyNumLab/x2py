---
title: x2py Documentation
audience: users, contributors, maintainers
prerequisites: none
related: documentation-architecture.md, getting-started/index.md, user-guide/index.md
status: draft
---

# x2py Documentation

x2py generates Python-facing contracts for native code and currently focuses on
Fortran-to-Python wrapper generation, semantic inspection, editable `.pyi`
contracts, and readiness diagnostics.

## Motivation

Native scientific projects often contain valuable Fortran APIs whose Python
surface needs to be explicit, testable, and maintainable. x2py aims to make the
wrapper contract visible before code generation, preserve native ownership and
ABI constraints, and fail early when a safe Python boundary cannot be proven.

## Main Features

- Source-driven Fortran wrapper generation for importable CPython extensions.
- Parser and semantic inspection for wrapper-relevant Fortran and C facts.
- Editable semantic `.pyi` contracts and readiness reports.
- Generated Fortran bridge, C/CPython binding, and native build artifacts for
  the implemented Fortran path.
- Documentation and test rules that separate implemented support from planned
  or design-only behavior.

## Installation Links

- [Installation](getting-started/installation.md)
- [Verification](getting-started/verification.md)
- [Quick start in the repository README](../README.md#quick-start)

## Start Here

- [Getting started](getting-started/index.md): installation, verification, and
  the first wrapper workflow.
- [User guide](user-guide/index.md): workflow-oriented topics for wrapping,
  arrays, memory, callbacks, packaging, and distribution.
- [Tutorials](tutorials/index.md): guided examples ordered from beginner to
  advanced.
- [Examples gallery](examples-gallery/index.md): complete runnable examples.
- [Reference](reference/index.md): generated API, CLI, and configuration
  reference.
- [Language support](language-support/index.md): supported, partial,
  unsupported, and planned Fortran features.
- [Design documents](design/index.md): high-level architecture explanations.
- [Developer guide](developer-guide/index.md): contributor workflows.
- [Internal architecture](internal-architecture/index.md): maintainer-level
  implementation details.
- [Roadmap](roadmap/index.md): public project direction.
- [FAQ](faq/index.md) and [troubleshooting](troubleshooting/index.md): common
  questions and failure modes.

## TODO

- TODO: Replace this draft landing page with the published website home page
  once the static documentation generator is selected.
- TODO: Add installation badges, release selector links, and generated API
  links after the first documentation website build exists.
