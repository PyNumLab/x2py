---
title: User Guide
audience: users
prerequisites: getting started
related: data-types.md, fortran-wrapper.md, ../language-support/index.md
status: maintained
publication: reviewed
---

# User Guide

The user guide continues from the completed
[Getting Started](../getting-started/index.md) workflow. Start with the datatype
mapping, then follow the workflow group that matches the native API you are
wrapping. Each page states the current supported subset, Python API shape,
limitations, troubleshooting route, and runtime evidence.

## Start Here

- [Data types](data-types.md): Fortran storage, semantic `.pyi` names, exact
  NumPy dtypes, strings, arrays, and generated classes.
- [Wrapping functions](wrapping-functions.md)
- [Wrapping subroutines](wrapping-subroutines.md)
- [Wrapping modules](wrapping-modules.md)
- [Arrays](arrays.md)
- [Optional arguments](optional-arguments.md)
- [Generic interfaces](generic-interfaces.md)

## Storage And Objects

- [Allocatables](allocatables.md)
- [Pointers](pointers.md)
- [Wrapping derived types](wrapping-derived-types.md)
- [Memory management](memory-management.md)

## Runtime Behavior

- [Callbacks](callbacks.md)
- [Enumerations](enumerations.md)
- [Error handling](error-handling.md)

## Build And Deployment

- [Packaging](packaging.md)
- [Distribution](distribution.md)

## Contract References

- [Fortran wrapper guide](fortran-wrapper.md): complete contract and evidence
  ledger for the generated runtime surface.
- [Editing semantic `.pyi` contracts](editing-semantic-pyi-contracts.md):
  intentional changes to generated wrapper policy.
- [Semantic `.pyi` format](../reference/semantic-pyi-format.md): annotation and
  metadata reference.
- [Language feature matrix](../language-support/feature-matrix.md): central
  supported, partial, unsupported, and planned status.

The workflow pages explain the normal source-driven wrapper. Edit a semantic
`.pyi` only after the generated behavior is understood and the native artifacts
needed by a `.pyi`-driven build are available.
