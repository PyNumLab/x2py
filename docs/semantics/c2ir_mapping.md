# C To Semantic IR Mapping

Status: first C semantic conversion subset implemented in `semantics/c2ir.py`.
The converter consumes `c_parser` models and emits the same language-neutral
semantic IR used by Fortran and edited `.pyi` files.

## Supported Identity Subset

- C translation unit -> one `SemanticModule` named from the source file stem.
- C function -> `SemanticFunction`, preserving native name and parameter order.
- C parameter -> `SemanticArgument`.
- `void` return -> `None`.
- `_Bool` -> `Bool`.
- `char` -> `Int8` with `c_char_policy` metadata; `signed char` -> `Int8`;
  `unsigned char` -> `UInt8`.
- `short`, `int`, `long`, and `long long` map to fixed signed integer names
  using the current Linux-oriented defaults: `Int16`, `Int32`, `Int64`,
  `Int64`.
- Unsigned integer spellings map to `UInt16`, `UInt32`, `UInt64`, and
  `UInt64`; fixed-width typedef spellings such as `uint32_t` map to the
  matching `UInt*` fallback.
- `float` -> `Float32`; `double` -> `Float64`.
- `float _Complex` -> `Complex64`; `double _Complex` -> `Complex128`.
- Local typedef chains are resolved when their parser model definitions are
  available.
- `size_t` maps to `SizeT` without a target probe; supplied
  `x2py.c_type_probe` facts override standard typedefs with width-specific
  `Int*`, `UInt*`, or `Float*` semantic names.
- Opaque standard-type probe facts such as `FILE` create named opaque semantic
  classes when referenced by converted declarations.
- Object-like numeric macros and enum constants become `Final`-style semantic
  variables through the `Constant` constraint.
- Struct definitions become `SemanticClass` entries. Incomplete structs become
  opaque classes and may be used through direct `Ptr(...)` identity contracts.
- Explicit multi-header conversion resolves a struct to the header that defines
  it. Other generated stubs import that owner class instead of emitting
  duplicate definitions.
- Structs originating from private included headers remain usable through
  generated owner-module `class Name(Opaque): pass` dependency stubs.
- Declared C arrays, including adjusted array parameters, become semantic array
  storage contracts with C order for rank greater than one.
- Pointers become explicit `SemanticStorageContract` pointer/reference
  metadata. `const` on the pointee makes the storage read-only, and `restrict`
  is preserved as aliasing metadata.

## Conservative Blockers

The converter does not silently invent wrapper policy. It attaches
`readiness_blockers` metadata that the semantic readiness checker reports:

- unresolved typedef or unknown type references;
- macro-dependent declarations in raw C input;
- variadic functions;
- function pointer/callback signatures without edited `.pyi` `Callable`
  policy;
- mutable numeric or `void *` pointer parameters without ownership,
  scalar-reference, or array policy;
- arrays with unknown extents;
- incomplete or external opaque structs used by value;
- unions used in semantic signatures;
- `long double`, `volatile`, `_Atomic`, bitfields, and unsupported declarator
  compositions.

The current C semantic path supports `--language c --semantics`,
`--language c --wrap-readiness`, and starter exact-contract
`--language c --pyi` output for this supported subset. Generated stubs remain
conservative: ambiguous ownership, callback, ABI-extension, and Pythonic
projection policy stays out of the generated `.pyi` until supplied by the
semantic model or an edited interface. In particular, an unresolved typedef is
not assumed to be opaque because its ABI representation is unknown.
