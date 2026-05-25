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

- [x] Keep C parsing source-faithful and parse-only. Unsupported syntax and
      unresolved parser facts may produce diagnostics; wrapper readiness and
      policy remain semantic-layer work.
- [x] Keep `CParser` as the current grammar-shaped visitor/helper class; no
      readability-driven class split is needed for the implemented parser
      surface.
- [x] Store macros on each `CFile` and index their recorded project facts in
      `CProject.macros`.
- [x] Use the shared CLI spelling `--language c --parse`; do not add a separate
      `--parse-c` spelling while it would only duplicate that path.
- [x] Expose `parse_c_file` and `parse_c_project` from `x2py` as well as from
      `c_parser`, matching the Fortran public entrypoint style.
- [x] Preserve same-name function variants in mutually exclusive raw
      preprocessor branches. `CFunction.condition_set` uses the Fortran-style
      `gN:bN` branch tokens; ambiguous project names are retained in
      `CProject.conditional_function_variants` instead of being collapsed into
      one `CProject.functions` entry.
- [x] Keep "no functions found" out of parser diagnostics. Whether a source
      has no wrappable public API is a Step 4 semantic-readiness decision.
- [x] Preserve enum initializer expression text in parser models rather than
      folding it without compiler semantics. Later semantic conversion may
      evaluate expressions only with an explicit safe/target-aware policy.
- [x] Preserve `CUnion` source facts in the parser; whether a union maps to
      semantic IR or blocks wrapping is deferred to C semantic conversion.

## Step 2: C Project And Include Policy

- [x] Parse only inputs given by the user: explicit mapping entries, explicit
      file paths, or supported files discovered below an explicit directory.
      Quoted and system includes are recorded as dependency facts; they do not
      cause recursive parsing even when a matching header is locally available.
      This is the same non-recursive policy used for Fortran recorded
      imports/includes.
- [x] Treat generated headers and direct `.i` inputs like other sources: parse
      them only when explicitly supplied or discovered below an explicitly
      supplied directory. Compiler-preprocessed streams remain supported input;
      their linemarkers record origins but do not add recursively parsed files.
- [x] Key C project files and include-graph edges by input/path identity, not
      module identity. An edge uses an already parsed project-file key where
      one matches; otherwise it retains the resolved path or written include
      target as an external dependency fact.

## Step 3: Shared Semantic Model Foundation (Fortran And C)

- [x] Treat the semantic model as language-neutral: Fortran and C parser output
      should converge into the same IR shapes wherever the native contract is
      equivalent.
- [x] Decide whether `SemanticArgument` remains the common model for variables,
      function arguments, fields, and returned argument projections, or whether
      `semantics/models.py` should introduce a clearer `SemanticVariable`
      model and use it consistently.
- [x] Make the chosen variable model represent C function parameters, C globals,
      C struct/union fields, Fortran dummy arguments, Fortran module variables,
      Fortran derived-type components, and projected return values.
- [x] Keep language-specific origin facts as metadata, for example
      `source_language`, `native_name`, `native_scope`, source location, parser
      node kind, and backend lowering hints.
- [x] Split the semantic value type from the storage and calling contract where
      needed, so `Float64`, `Ptr(Float64)`, `Const(Float64[n])`, and a Fortran
      descriptor-backed array are not confused.
- [x] Define one array/storage contract that can represent known C array
      contracts and Fortran array dummies using element type, rank, shape,
      bounds, strides, order, contiguity, mutability, and ownership.
- [x] Decide whether that array/storage contract is represented as a dedicated
      semantic model, a derived semantic type, or structured metadata on
      `SemanticType`; the chosen design must be readable from both generated
      and edited `.pyi` files.
- [x] For Fortran arrays, retain native declaration provenance where available:
      explicit-shape, assumed-size, assumed-shape, assumed-rank,
      deferred-shape, `contiguous`, `allocatable`, `pointer`, rank and source
      bounds. Canonical `.pyi` exposes only storage constraints; Fortran dummy
      bounds are established by native argument association, not passed as
      Python array metadata.
- [ ] For C arrays, use the same array/storage contract only when a real storage
      contract is known; leave unrefined pointers as pointer types instead of
      inventing array shapes.
- [x] Preserve scalar by-reference contracts for both languages with the same
      reference representation, including `Ptr(T)` and `Ptr(Const(T))`.
- [x] Make `intent`, mutability, ownership, aliasing, optionality, defaults,
      constraints, coercions, and contracts work on the shared variable model
      rather than in language-specific side channels.
- [ ] Define how future constraints and coercions attach to variables and
      semantic types, including copy/pack policies, dtype coercions, order
      conversions, scalar temporary creation, pointer ownership, and lifetime.
- [ ] Define semantic blockers for incomplete shared contracts, such as unknown
      Fortran array rank, unknown array category, unsupported allocatable or
      pointer reassociation, unresolved C pointer ownership, and unsupported
      callbacks.
- [x] Keep backend lowering metadata separate from the Python-facing `.pyi`
      contract; generated stubs should describe the visible semantic interface,
      not compiler-private transport details.
- [ ] Add equality and round-trip tests that prove equivalent C and Fortran
      variables compare by semantic contract, not by parser-specific metadata.
- [x] Add model tests for Fortran arrays represented as semantic array/storage
      contracts with shape, rank, generated `ORDER_F`, `Allocatable`, and
      `Pointer`; keep `ORDER_ANY` available for an explicitly edited or
      projected interface.
- [ ] Add model tests for C pointer/array contracts using the same
      array/storage representation when shape and storage facts are known.
- [x] Document the shared variable, array, pointer, ownership, constraint, and
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

- [x] Create `semantics/c2ir.py`.
- [x] Implement `CToIRConverter`.
- [x] Mirror the visitor style of `FortranToIRConverter`.
- [x] Accept C standard-type probe reports as target context for converting
      standard-header aliases and opaque handles once `CToIRConverter` exists.
- [x] Add compatibility helpers such as `c_file_to_semantic_modules`.
- [x] Add `c_function_to_semantic_function`.
- [x] Add `c_struct_to_semantic_class` where appropriate.
- [x] Add `c_project_to_semantic_modules` if project context is needed.
- [x] Keep conversion separate from parser internals.
- [x] Map `void` return to `None`.
- [x] Map `_Bool` to `Bool`.
- [x] Map `char` to an explicit semantic type policy.
- [x] Map signed integer widths.
- [x] Map unsigned integer widths.
- [x] Map `float` to `Float32`.
- [x] Map `double` to `Float64`.
- [x] Map `long double` to a documented type or unsupported diagnostic.
- [x] Map pointers to constraints/metadata.
- [x] Map C arrays to the shared array/storage contract with default `ORDER_C`
      when shape and storage facts are known.
- [x] Map `const` to read-only/ownership metadata.
- [x] Map `restrict` to aliasing metadata.
- [x] Map structs to semantic classes or named semantic types.
- [x] Map unions conservatively.
- [x] Map enums/constants.
- [x] Preserve unresolved semantic types as errors, not `Unknown` output.
- [x] Convert C functions to `SemanticFunction`.
- [x] Preserve native function name.
- [x] Preserve parameter order.
- [x] Mark pointer mutability.
- [ ] Represent array pointer plus size patterns only when known.
- [ ] Add projection metadata only where native and Python signatures diverge.
- [x] Treat out parameters conservatively until ownership/intent policy exists.
- [x] Reject or defer variadic functions.
- [x] Preserve callback/function-pointer facts from C parser models even if
      semantic conversion defers wrapper generation.
- [x] Defer callback conversion unless `.pyi` policy supplies the required
      callback facts.
- [x] Add semantic tests for scalar functions.
- [x] Add semantic tests for pointer input.
- [x] Add semantic tests for const pointer input.
- [ ] Add semantic tests for arrays with explicit size parameter.
- [x] Add semantic tests for structs and opaque handles.
- [ ] Ensure C semantic conversion works for the supported parser subset.
- [x] Ensure unsupported C semantic mappings fail explicitly.
- [x] Enable `--language c --semantics` only after tests pass.
- [ ] Add a semantic fixture workflow for C if stable enough.
- [x] Document C-to-semantic-IR mapping.
- [x] Standardize unsigned integer semantic type names.
- [ ] Decide whether struct, union, and enum representation requires semantic
      model extensions.

### Fortran Conversion

- [x] Update `FortranToIRConverter` to emit the exact native interface described
      in `docs/semantics/pyi_format.md`, not the older placeholder shape
      representation.
- [x] Map Fortran scalar dummy arguments by reference to shared pointer
      contracts: writable storage as `Ptr(T)` and read-only storage as
      `Ptr(Const(T))`.
- [x] Map Fortran `value` scalar dummy arguments and function returns to direct
      semantic scalar values.
- [x] Map Fortran explicit-shape and adjustable arrays to shaped NumPy storage
      contracts with `ORDER_F` where rank and orientation require it.
- [x] Map Fortran assumed-size arrays to known-rank storage contracts with an
      unconstrained final runtime extent where the native declaration uses
      `*`.
- [x] Map Fortran assumed-shape arrays to strided contracts with generated
      `ORDER_F` orientation under the current Fortran-default layout policy;
      an edited interface or later projection may explicitly select
      `ORDER_ANY`.
- [ ] Map Fortran assumed-rank arrays only after the semantic model can
      represent rank-polymorphic array contracts explicitly.
- [ ] Map Fortran `allocatable` and `pointer` dummy arrays to shared array
      contracts with `Allocatable` or `Pointer` metadata and readiness
      blockers for allocation or association changes until policy exists.
      Contracts are represented in IR and `.pyi`; readiness blockers for
      allocation or association changes remain open.
- [x] Convert Fortran bound declarations to required public storage extents;
      retain original source bounds only as internal provenance, since the
      compiled Fortran interface establishes dummy bounds on association.
- [x] Convert Fortran module variables and derived-type components through the
      same variable model used for C variables and fields.
- [x] Ensure language-to-IR conversion retains enough origin metadata for
      backend lowering without making `.pyi` syntax language-specific.
- [x] Add Fortran semantic IR tests for scalar references, explicit-shape
      arrays, assumed-size arrays, assumed-shape arrays, allocatable arrays,
      pointer arrays, derived-type components, and module variables.

### Cross-Language And Shared Conversion Policy

- [ ] Add cross-language IR tests that exercise equivalent C and Fortran
      variables through the same semantic model and readiness path.
- [ ] Decide whether the shared semantic IR needs richer pointer/ownership
      constraints.

## Step 6: `.pyi` Generation, Loading, And Policy

### Shared Generation Contract (Fortran And C)

- [x] Make `.pyi` generation consume semantic IR only; language-specific
      differences should already be encoded as semantic contracts and metadata.
- [x] Update the `.pyi` printer to emit the canonical target notation from
      `docs/semantics/pyi_format.md`, including `T[n, m]`, `T[:, :]`,
      `T[::Strided]`, `Annotated[..., ORDER_F]`,
      `Annotated[..., ORDER_ANY]`, `Allocatable`, and `Pointer`.

### Fortran Stub Generation

- [x] Update Fortran `.pyi` generation to emit exact native interface stubs:
      scalar references as `Ptr(...)`, array dummies as NumPy array
      annotations, explicit `ORDER_F` only when rank and orientation require
      it, and no `@native_call` for the exact interface.
- [x] Ensure Fortran `.pyi` generation preserves source facts that affect
      the visible contract, including rank, storage extent expressions,
      stride/layout policy, `allocatable`, `pointer`, `intent`, optionality,
      and constants. Retain native dummy category and original bound facts
      internally as source provenance rather than emitting
      `ArrayCategory(...)` or `SourceDims(...)` in canonical stubs.
- [x] Ensure generated Fortran stubs do not generalize missing fixed-rank array
      information into rank-polymorphic notation.
- [x] Add Fortran `.pyi` generation tests for exact scalar references,
      explicit-shape arrays, assumed-size arrays, assumed-shape strided arrays,
      contiguous arrays, allocatable arrays, pointer arrays, constants, derived
      type fields, and module variables.

### Shared Loading And Round Trips (Fortran And C)

- [x] Extend `load_pyi_file`, `parse_pyi_text`, and `convert_pyi_to_ir` to load
      the accepted `.pyi` target notation into semantic IR, not just parse a
      subset for readiness.
- [x] Teach the `.pyi` loader to parse canonical `Annotated[...]` metadata into
      semantic storage metadata without losing order, ownership, or
      source-name information; it continues to accept legacy
      `ArrayCategory(...)` and `SourceDims(...)` annotations.
- [x] Teach the `.pyi` loader to parse NumPy-style array subscriptions into the
      shared array/storage contract, including symbolic dimensions, `:`,
      `::Strided`, known rank, rank-polymorphic forms when supported, and
      order metadata.
- [x] Teach the `.pyi` loader to parse `Ptr(...)`, `Const(...)`, `Final[...]`,
      `private[...]`, `Name(...)`, `native_call(...)`, and projected returns
      into the same semantic IR emitted by language converters.
- [ ] Add parser errors for `.pyi` constructs that look valid but cannot be
      converted to complete semantic IR, such as unknown fixed-rank shape,
      unsupported rank-polymorphic arrays, or unsafe allocatable/pointer
      replacement policy.
- [x] Add round-trip tests for Fortran parser output:
      parser model -> semantic IR -> `.pyi` -> semantic IR.
- [x] Add round-trip tests for edited Fortran `.pyi` files loaded directly into
      semantic IR.
- [ ] Add round-trip tests for C parser output:
      parser model -> semantic IR -> `.pyi` -> semantic IR.
- [ ] Add mixed-language semantic fixture tests where C and Fortran stubs load
      through the same `.pyi` loader and readiness checker.
- [x] Keep `.pyi` syntax language-neutral; Fortran and C should differ by
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
