---
title: User Guide
audience: users
prerequisites: getting started
related: fortran-wrapper.md, ../language-support/index.md
status: planned-documentation
---

# User Guide

The user guide is organized by workflows instead of implementation modules.
Each topic will use this shape: concept, usage, examples, limitations, best
practices, and related topics.

## Workflow Topics

- [Fortran wrapper guide](fortran-wrapper.md)
- [Wrapping functions](wrapping-functions.md)
- [Wrapping subroutines](wrapping-subroutines.md)
- [Wrapping modules](wrapping-modules.md)
- [Wrapping derived types](wrapping-derived-types.md)
- [Arrays](arrays.md)
- [Allocatable arrays](allocatable-arrays.md)
- [Pointer arguments](pointer-arguments.md)
- [Optional arguments](optional-arguments.md)
- [Generic interfaces](generic-interfaces.md)
- [Enumerations](enumerations.md)
- [Callbacks](callbacks.md)
- [Error handling](error-handling.md)
- [Memory management](memory-management.md)
- [Packaging](packaging.md)
- [Distribution](distribution.md)

## TODO

- TODO: Promote implemented contracts from `fortran-wrapper.md` into
  workflow pages with links back to runtime evidence.
- TODO: Keep unsupported or partial workflows marked with current language
  support status until tests prove runtime behavior.
