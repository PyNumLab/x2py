# x2py Checklist

Status: forward backlog only. Completed historical C parser implementation
items were moved into `docs/c_parser/c_parser_reference.md`; this file now
tracks remaining parser, shared semantic IR, and `.pyi` work that still needs a
decision, implementation, tests, or release validation. C-specific tasks remain
marked as C-specific, but the semantic model and `.pyi` tasks are expected to
serve both Fortran and C.

Language scope is stated in each section or subsection heading:

- **C** tasks apply only to the C frontend or to C-derived semantic/stub output.
- **Fortran** tasks apply only to the Fortran frontend or to Fortran-derived
  semantic/stub output.
- **Shared (Fortran and C)** tasks define common IR, `.pyi`, readiness, or
  validation behavior used by both languages.
- **Cross-language** tasks compare or exercise both language paths together.

## Step 1: C Parser Frontend Cleanup

- [ ] Keep existing C parser behavior unchanged unless a future task explicitly
      requires shared infrastructure changes.
- [ ] Keep wrappability assessment in the semantic layer, not inside parser
      packages.
- [ ] Split `CParser` internals into smaller visitor/helper classes only if the
      class grows past what remains readable.
- [ ] Decide whether macros belong only in `CFile.macros` or also in project
      symbol indexes.
- [ ] If `--parse-c` is added, make it an alias for `--language c --parse` and
      add CLI tests for the alias.
- [ ] Allow same function under mutually exclusive preprocessor branches.
- [ ] Make C parser diagnostics report "no functions found" only when
      appropriate.
- [ ] Safely fold simple enum integer expressions, or document the exact
      boundary for preserving expression text.
- [ ] Decide how much enum expression folding is safe without compiler
      semantics.
- [ ] Decide whether unions map to semantic IR at all in v1.
- [ ] Feed C standard-type probe reports into C semantic conversion once the
      C semantic converter exists.

## Step 2: C Project And Include Policy

- [ ] Decide whether project parsing should parse all included system headers
      when they are found locally.
- [ ] Decide how to handle generated headers.
- [ ] Decide whether include graph keys should be path-keyed, module-keyed, or
      both.

## Step 3: Shared Semantic Model Foundation (Fortran And C)

- [ ] Treat the semantic model as language-neutral: Fortran and C parser output
      should converge into the same IR shapes wherever the native contract is
      equivalent.
- [ ] Decide whether `SemanticArgument` remains the common model for variables,
      function arguments, fields, and returned argument projections, or whether
      `semantics/models.py` should introduce a clearer `SemanticVariable`
      model and use it consistently.
- [ ] Make the chosen variable model represent C function parameters, C globals,
      C struct/union fields, Fortran dummy arguments, Fortran module variables,
      Fortran derived-type components, and projected return values.
- [ ] Keep language-specific origin facts as metadata, for example
      `source_language`, `native_name`, `native_scope`, source location, parser
      node kind, and backend lowering hints.
- [ ] Split the semantic value type from the storage and calling contract where
      needed, so `Float64`, `Ptr(Float64)`, `Const(Float64[n])`, and a Fortran
      descriptor-backed array are not confused.
- [ ] Define one array/storage contract that can represent known C array
      contracts and Fortran array dummies using element type, rank, shape,
      bounds, strides, order, contiguity, mutability, and ownership.
- [ ] Decide whether that array/storage contract is represented as a dedicated
      semantic model, a derived semantic type, or structured metadata on
      `SemanticType`; the chosen design must be readable from both generated
      and edited `.pyi` files.
- [ ] For Fortran arrays, record the dummy category and properties needed by
      lowering: explicit-shape, assumed-size, assumed-shape, assumed-rank,
      deferred-shape, `contiguous`, `allocatable`, `pointer`, rank, shape,
      lower bounds, and whether replacement or reassociation is possible.
- [ ] For C arrays, use the same array/storage contract only when a real storage
      contract is known; leave unrefined pointers as pointer types instead of
      inventing array shapes.
- [ ] Preserve scalar by-reference contracts for both languages with the same
      reference representation, including `Ptr(T)` and `Ptr(Const(T))`.
- [ ] Make `intent`, mutability, ownership, aliasing, optionality, defaults,
      constraints, coercions, and contracts work on the shared variable model
      rather than in language-specific side channels.
- [ ] Define how future constraints and coercions attach to variables and
      semantic types, including copy/pack policies, dtype coercions, order
      conversions, scalar temporary creation, pointer ownership, and lifetime.
- [ ] Define semantic blockers for incomplete shared contracts, such as unknown
      Fortran array rank, unknown array category, unsupported allocatable or
      pointer reassociation, unresolved C pointer ownership, and unsupported
      callbacks.
- [ ] Keep backend lowering metadata separate from the Python-facing `.pyi`
      contract; generated stubs should describe the visible semantic interface,
      not compiler-private transport details.
- [ ] Add equality and round-trip tests that prove equivalent C and Fortran
      variables compare by semantic contract, not by parser-specific metadata.
- [ ] Add model tests for Fortran arrays represented as semantic array/storage
      contracts with shape, rank, `ORDER_F` or `ORDER_ANY`, `Allocatable`, and
      `Pointer`.
- [ ] Add model tests for C pointer/array contracts using the same
      array/storage representation when shape and storage facts are known.
- [ ] Document the shared variable, array, pointer, ownership, constraint, and
      coercion model before enabling new generator behavior.

## Step 4: C Semantic Readiness

- [ ] Define stable C readiness dictionary keys for the semantic layer.
- [ ] Include counts for functions, structs, unions, enums, typedefs, macros,
      includes, and diagnostics.
- [ ] Include `unsupported_constructs`.
- [ ] Include `unresolved_includes`.
- [ ] Include `unresolved_typedefs`.
- [ ] Include `unresolved_tags`.
- [ ] Include `macro_dependent_declarations`.
- [ ] Include `preprocessing_origin`.
- [ ] Include `unsupported_extensions`.
- [ ] Include `ambiguous_pointer_ownership`.
- [ ] Include `ambiguous_array_extents`.
- [ ] Include `callback_functions`.
- [ ] Include `variadic_functions`.
- [ ] Include `incomplete_public_types`.
- [ ] Include `wrappability_blockers`.
- [ ] Include `unit_blockers`.
- [ ] Include `why_not_wrappable`.
- [ ] Include file-level `wrappable`.
- [ ] Report no functions found.
- [ ] Report unresolved includes.
- [ ] Report unresolved typedefs.
- [ ] Report unresolved struct tags.
- [ ] Report unresolved union tags.
- [ ] Report unresolved enum tags.
- [ ] Report incomplete structs used by value.
- [ ] Report incomplete unions used by value.
- [ ] Report variadic functions.
- [ ] Report K&R functions.
- [ ] Report function pointer return types.
- [ ] Report function pointer parameters.
- [ ] Report callback typedef parameters.
- [ ] Report missing callback `.pyi` policy.
- [ ] Report unsupported bitfields.
- [ ] Report pointer ownership ambiguity.
- [ ] Report non-const pointer mutability ambiguity.
- [ ] Report arrays with unknown extent relationships.
- [ ] Report opaque pointers as warnings or non-blockers if policy allows.
- [ ] Assign function blockers to function units.
- [ ] Assign struct field blockers to struct units.
- [ ] Assign union field blockers to union units.
- [ ] Assign enum value blockers to enum units.
- [ ] Assign typedef blockers to typedef units.
- [ ] Assign include, macro, and file-scope-variable blockers to file units
      when no narrower owner exists.
- [ ] Use qualified names where available.
- [ ] Avoid per-unit ready flags; keep readiness file-level like Fortran.
- [ ] Add tests for every blocker family.
- [ ] Add semantic readiness formatting tests.
- [ ] Ensure C readiness output is stable in JSON and human CLI when served by
      the semantic layer.
- [ ] Ensure diagnostics identify exactly which units block wrapping.
- [ ] Ensure common unsupported C constructs produce actionable messages.
- [ ] Document readiness codes and examples.
- [ ] Decide which pointer cases are blockers versus warnings.
- [ ] Decide how semantic readiness should treat opaque handles.
- [ ] Decide exact readiness code names for callback APIs that are parsed but
      missing user-supplied `.pyi` policy.

## Step 5: Language-To-Semantic IR Conversion

### C Conversion

- [ ] Create `semantics/c2ir.py`.
- [ ] Implement `CToIRConverter`.
- [ ] Mirror the visitor style of `FortranToIRConverter`.
- [ ] Add compatibility helpers such as `c_file_to_semantic_modules`.
- [ ] Add `c_function_to_semantic_function`.
- [ ] Add `c_struct_to_semantic_class` where appropriate.
- [ ] Add `c_project_to_semantic_modules` if project context is needed.
- [ ] Keep conversion separate from parser internals.
- [ ] Map `void` return to `None`.
- [ ] Map `_Bool` to `Bool`.
- [ ] Map `char` to an explicit semantic type policy.
- [ ] Map signed integer widths.
- [ ] Map unsigned integer widths.
- [ ] Map `float` to `Float32`.
- [ ] Map `double` to `Float64`.
- [ ] Map `long double` to a documented type or unsupported diagnostic.
- [ ] Map pointers to constraints/metadata.
- [ ] Map C arrays to the shared array/storage contract with default `ORDER_C`
      when shape and storage facts are known.
- [ ] Map `const` to read-only/ownership metadata.
- [ ] Map `restrict` to aliasing metadata.
- [ ] Map structs to semantic classes or named semantic types.
- [ ] Map unions conservatively.
- [ ] Map enums/constants.
- [ ] Preserve unresolved semantic types as errors, not `Unknown` output.
- [ ] Convert C functions to `SemanticFunction`.
- [ ] Preserve native function name.
- [ ] Preserve parameter order.
- [ ] Mark pointer mutability.
- [ ] Represent array pointer plus size patterns only when known.
- [ ] Add projection metadata only where native and Python signatures diverge.
- [ ] Treat out parameters conservatively until ownership/intent policy exists.
- [ ] Reject or defer variadic functions.
- [ ] Preserve callback/function-pointer facts from C parser models even if
      semantic conversion defers wrapper generation.
- [ ] Defer callback conversion unless `.pyi` policy supplies the required
      callback facts.
- [ ] Add semantic tests for scalar functions.
- [ ] Add semantic tests for pointer input.
- [ ] Add semantic tests for const pointer input.
- [ ] Add semantic tests for arrays with explicit size parameter.
- [ ] Add semantic tests for structs and opaque handles.
- [ ] Ensure C semantic conversion works for the supported parser subset.
- [ ] Ensure unsupported C semantic mappings fail explicitly.
- [ ] Enable `--language c --semantics` only after tests pass.
- [ ] Add a semantic fixture workflow for C if stable enough.
- [ ] Document C-to-semantic-IR mapping.
- [ ] Standardize unsigned integer semantic type names.
- [ ] Decide whether struct, union, and enum representation requires semantic
      model extensions.

### Fortran Conversion

- [ ] Update `FortranToIRConverter` to emit the exact native interface described
      in `docs/semantics/pyi_format.md`, not the older placeholder shape
      representation.
- [ ] Map Fortran scalar dummy arguments by reference to shared pointer
      contracts: writable storage as `Ptr(T)` and read-only storage as
      `Ptr(Const(T))`.
- [ ] Map Fortran `value` scalar dummy arguments and function returns to direct
      semantic scalar values.
- [ ] Map Fortran explicit-shape and adjustable arrays to shaped NumPy storage
      contracts with `ORDER_F` where rank and orientation require it.
- [ ] Map Fortran assumed-size arrays to known-rank storage contracts while
      preserving the missing final extent boundary.
- [ ] Map Fortran assumed-shape arrays to strided contracts with `ORDER_ANY`
      unless `contiguous` or another source fact restricts orientation.
- [ ] Map Fortran assumed-rank arrays only after the semantic model can
      represent rank-polymorphic array contracts explicitly.
- [ ] Map Fortran `allocatable` and `pointer` dummy arrays to shared array
      contracts with `Allocatable` or `Pointer` constraints and readiness
      blockers for allocation or association changes until policy exists.
- [ ] Preserve Fortran lower bounds and source-level dimension expressions when
      they affect wrapper validation or lowering.
- [ ] Convert Fortran module variables and derived-type components through the
      same variable model used for C variables and fields.
- [ ] Ensure language-to-IR conversion retains enough origin metadata for
      backend lowering without making `.pyi` syntax language-specific.
- [ ] Add Fortran semantic IR tests for scalar references, explicit-shape
      arrays, assumed-size arrays, assumed-shape arrays, allocatable arrays,
      pointer arrays, derived-type components, and module variables.

### Cross-Language And Shared Conversion Policy

- [ ] Add cross-language IR tests that exercise equivalent C and Fortran
      variables through the same semantic model and readiness path.
- [ ] Decide whether the shared semantic IR needs richer pointer/ownership
      constraints.

## Step 6: `.pyi` Generation, Loading, And Policy

### Shared Generation Contract (Fortran And C)

- [ ] Make `.pyi` generation consume semantic IR only; language-specific
      differences should already be encoded as semantic contracts and metadata.
- [ ] Update the `.pyi` printer to emit the canonical target notation from
      `docs/semantics/pyi_format.md`, including `T[n, m]`, `T[:, :]`,
      `T[::Strided]`, `Annotated[..., ORDER_F]`,
      `Annotated[..., ORDER_ANY]`, `Allocatable`, and `Pointer`.

### Fortran Stub Generation

- [ ] Update Fortran `.pyi` generation to emit exact native interface stubs:
      scalar references as `Ptr(...)`, array dummies as NumPy array
      annotations, explicit `ORDER_F` only when rank and orientation require
      it, and no `@native_call` for the exact interface.
- [ ] Ensure Fortran `.pyi` generation preserves source facts that affect
      validation or lowering, including rank, shape expressions, lower bounds,
      assumed-shape or assumed-size category, contiguity, `allocatable`,
      `pointer`, `intent`, optionality, and constants.
- [ ] Ensure generated Fortran stubs do not generalize missing fixed-rank array
      information into rank-polymorphic notation.
- [ ] Add Fortran `.pyi` generation tests for exact scalar references,
      explicit-shape arrays, assumed-size arrays, assumed-shape strided arrays,
      contiguous arrays, allocatable arrays, pointer arrays, constants, derived
      type fields, and module variables.

### Shared Loading And Round Trips (Fortran And C)

- [ ] Extend `load_pyi_file`, `parse_pyi_text`, and `convert_pyi_to_ir` to load
      the accepted `.pyi` target notation into semantic IR, not just parse a
      subset for readiness.
- [ ] Teach the `.pyi` loader to parse `Annotated[...]` metadata into semantic
      constraints and metadata without losing order, ownership, array category,
      or source-name information.
- [ ] Teach the `.pyi` loader to parse NumPy-style array subscriptions into the
      shared array/storage contract, including symbolic dimensions, `:`,
      `::Strided`, known rank, rank-polymorphic forms when supported, and
      order metadata.
- [ ] Teach the `.pyi` loader to parse `Ptr(...)`, `Const(...)`, `Final[...]`,
      `private[...]`, `Name(...)`, `native_call(...)`, and projected returns
      into the same semantic IR emitted by language converters.
- [ ] Add parser errors for `.pyi` constructs that look valid but cannot be
      converted to complete semantic IR, such as unknown fixed-rank shape,
      unsupported rank-polymorphic arrays, or unsafe allocatable/pointer
      replacement policy.
- [ ] Add round-trip tests for Fortran parser output:
      parser model -> semantic IR -> `.pyi` -> semantic IR.
- [ ] Add round-trip tests for edited Fortran `.pyi` files loaded directly into
      semantic IR.
- [ ] Add round-trip tests for C parser output:
      parser model -> semantic IR -> `.pyi` -> semantic IR.
- [ ] Add mixed-language semantic fixture tests where C and Fortran stubs load
      through the same `.pyi` loader and readiness checker.
- [ ] Keep `.pyi` syntax language-neutral; Fortran and C should differ by
      semantic contract, not by separate annotation families.

### C Stub Generation And Policy

- [ ] Enable `--language c --pyi` only after semantic conversion is stable.
- [ ] Generate stubs from C semantic modules.
- [ ] Emit scalar functions.
- [ ] Emit pointer constraints when the semantic model supports them.
- [ ] Emit arrays with `ORDER_C`.
- [ ] Emit constants as `Final[...]`.
- [ ] Emit opaque handles as classes or semantic type annotations.
- [ ] Emit structs as classes only when field semantics are intended.
- [ ] Avoid emitting `Unknown`.
- [ ] Emit imports/includes only if represented in semantic IR.
- [ ] Add tests for scalar function stubs.
- [ ] Add tests for constant stubs.
- [ ] Add tests for opaque handle stubs.
- [ ] Add tests for array stubs.
- [ ] Confirm the existing `.pyi` parser accepts generated C stubs.
- [ ] Extend the `.pyi` parser only if semantic IR requires new constructs.
- [ ] Add round-trip tests for C-generated stubs.
- [ ] Add edited-stub tests for C APIs.
- [ ] Add tests that unsupported C stubs fail clearly.
- [ ] Add fixture tests under `tests/pyi/fixtures/c/` if C stubs are stable.
- [ ] Represent pointer/size hidden relationships where known.
- [ ] Represent returned output buffers only with explicit projection metadata.
- [ ] Represent ownership/lifetime metadata if supported by IR.
- [ ] Define `.pyi` policy fields for callback signatures.
- [ ] Define `.pyi` policy fields for callback direction.
- [ ] Define `.pyi` policy fields for call-only versus stored callback
      lifetime.
- [ ] Define `.pyi` policy fields for context/userdata pairing.
- [ ] Define `.pyi` policy fields for callback nullability.
- [ ] Define `.pyi` policy fields for non-default calling conventions.
- [ ] Define `.pyi` policy fields for threading and async invocation.
- [ ] Define `.pyi` policy fields for ownership of callback/context memory.
- [ ] Define `.pyi` policy fields for release/unregistration APIs.
- [ ] Define `.pyi` policy fields for Python exception/error handling.
- [ ] Defer callback projection until those policy fields are supplied by the
      user.
- [ ] Defer arbitrary ABI details.
- [ ] Ensure C `.pyi` output works for the supported semantic subset.
- [ ] Ensure generated stubs parse back into semantic IR.
- [ ] Keep C `.pyi` tests separate from Fortran `.pyi` tests.
- [ ] Document generated C stub shape and limitations.
- [ ] Decide whether existing `.pyi` syntax is expressive enough for ownership
      and callback policy.
- [ ] Decide whether opaque handles need new conventions.
- [ ] Decide whether C callbacks need dedicated `.pyi` policy syntax and later
      semantic model changes.

## Step 7: C Corpus And Stabilization

- [ ] Use cJSON as the first pinned real-world C corpus target.
- [ ] Pin cJSON to an exact tag or commit rather than tracking the moving
      upstream branch.
- [ ] Store cJSON provenance in `tests/data/c/corpus/cjson/SOURCE.md`.
- [ ] Store cJSON license text next to the vendored fixture files.
- [ ] Add `tests/data/c/corpus/cjson/cJSON.h`.
- [ ] Add `tests/data/c/corpus/cjson/cJSON.c`.
- [ ] Treat cJSON corpus tests as parse-only at first.
- [ ] Use cJSON to exercise typedef structs, recursive pointers, `const char *`
      APIs, `size_t`, public declaration macros, numeric/string constants, and
      callback hook members.
- [ ] Keep callback hook members modeled in `c_parser/models.py`, with semantic
      readiness requiring explicit user `.pyi` callback policy metadata before
      claiming they are wrappable.
- [ ] Add zlib or another macro-heavier C library only after cJSON is stable.
- [ ] Add a small real-world C header corpus.
- [ ] Add scientific C API fixtures.
- [ ] Add source/header project fixtures.
- [ ] Add macro-heavy unsupported fixtures.
- [ ] Add callback fixtures.
- [ ] Add variadic function fixtures.
- [ ] Add opaque handle fixtures.
- [ ] Add array-size pattern fixtures.
- [ ] Add typedef-chain fixtures.
- [ ] Add parse-only corpus tests.
- [ ] Add selected parser JSON goldens for representative corpus files.
- [ ] Keep corpus license provenance documented.
- [ ] Run C corpus parse-only tests. The current corpus file is still a skipped
      roadmap test until the corpus workflow is enabled.
- [ ] Audit JSON schema stability.
- [ ] Audit error diagnostic stability.
- [ ] Require green CI for Fortran and C suites.
- [ ] Consider adding a CI guard that requires C parser docs updates for C
      parser changes.
- [ ] Keep fixture/golden workflows stable.
- [ ] Make corpus tests catch regressions.

## Guardrails For C And Shared Remaining Work

These are non-goal constraints, not parser implementation tasks:

- Do not support full compiler-grade C parsing.
- Do not support full C preprocessor compatibility.
- Do not support arbitrary macro expansion.
- Do not parse macro-generated declarations from raw source as ordinary C
  declarations.
- Do not support token-paste or stringify expansion.
- Do not support all compiler extensions.
- Do not support arbitrary GCC extensions.
- Do not support arbitrary MSVC extensions.
- Do not parse C++.
- Do not generate a full ABI model.
- Do not infer pointer ownership silently.
- Do not claim callbacks are safely wrappable before the required `.pyi`
  callback policy is supplied.
- Do not couple shared semantic IR behavior to a single frontend.
- Do not modify existing C parser behavior as part of shared semantic work unless
  the change is explicitly planned, tested, and documented.
