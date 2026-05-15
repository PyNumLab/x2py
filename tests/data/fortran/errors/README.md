Stage-specific Fortran inputs that are expected to fail live here.

- `parser/`: invalid or unsupported inputs that should fail during parsing.
- `semantics/`: inputs that parse but should fail semantic conversion.
- `pyi/`: inputs that parse and convert far enough to fail pyi generation.
