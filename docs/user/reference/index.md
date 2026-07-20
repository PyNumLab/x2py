---
title: Reference
audience: users, developers
prerequisites: getting started
related: cli-commands.md, python-api.md, semantic-ir.md, semantic-pyi-format.md, callbacks.md
status: maintained
publication: draft
---

# Reference

Reference pages describe the command, API, and data contracts that user guides
and developer guides depend on. Workflow guidance belongs in tutorials, examples,
and user guides; this section stays close to the public surfaces.

## Pages

- [CLI commands](cli-commands.md)
- [Python API](python-api.md)
- [Semantic IR](semantic-ir.md)
- [Semantic .pyi format](semantic-pyi-format.md)
- [Callbacks](callbacks.md)
- [Diagnostic codes](diagnostic-codes.md)
- [Generated functions](generated-functions.md)
- [Generated modules](generated-modules.md)
- [Generated classes](generated-classes.md)
- [Configuration files](configuration-files.md)

## Generated Wrapper Surface

The generated function, module, and class pages document the maintained Python
surface produced by wrapper builds. They are manually maintained references
backed by checked contracts and runtime tests. A generated-reference toolchain
can replace the inventory details later, but it must preserve the same public
rules.
