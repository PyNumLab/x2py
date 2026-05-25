# C Parser Remaining Work Checklist

Status: forward backlog only. Completed historical implementation items were
moved into `docs/c_parser/c_parser_reference.md`; this file keeps only work
that still needs a decision, implementation, tests, or release validation.

## Step 1: Parser Cleanup Before C Semantics

- [ ] Keep Fortran parser behavior unchanged unless a future task explicitly
      requires shared infrastructure changes.
- [ ] Keep any C wrappability assessment in the semantic layer, not inside the
      parser package.
- [ ] Split `CParser` internals into smaller visitor/helper classes only if the
      class grows past what remains readable.
- [ ] Decide whether macros belong only in `CFile.macros` or also in project
      symbol indexes.
- [ ] If `--parse-c` is added, make it an alias for `--language c --parse` and
      add CLI tests for the alias.
- [ ] Allow same function under mutually exclusive preprocessor branches.
- [ ] Make parser diagnostics report "no functions found" only when
      appropriate.
- [ ] Safely fold simple enum integer expressions, or document the exact
      boundary for preserving expression text.
- [ ] Decide how much enum expression folding is safe without compiler
      semantics.
- [ ] Decide whether unions map to semantic IR at all in v1.
- [ ] Feed C standard-type probe reports into C semantic conversion once the
      C semantic converter exists.

## Step 2: Project And Include Policy

- [ ] Decide whether project parsing should parse all included system headers
      when they are found locally.
- [ ] Decide how to handle generated headers.
- [ ] Decide whether include graph keys should be path-keyed, module-keyed, or
      both.

## Step 3: Semantic Readiness

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
- [ ] Ensure readiness output is stable in JSON and human CLI when served by the
      semantic layer.
- [ ] Ensure diagnostics identify exactly which units block wrapping.
- [ ] Ensure common unsupported C constructs produce actionable messages.
- [ ] Document readiness codes and examples.
- [ ] Decide which pointer cases are blockers versus warnings.
- [ ] Decide how semantic readiness should treat opaque handles.
- [ ] Decide exact readiness code names for callback APIs that are parsed but
      missing user-supplied `.pyi` policy.

## Step 4: Semantic IR Conversion

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
- [ ] Map arrays to `Shape` and `ORDER_C`.
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
- [ ] Decide whether the current semantic IR needs richer pointer/ownership
      constraints.
- [ ] Standardize unsigned integer semantic type names.
- [ ] Decide whether struct, union, and enum representation requires semantic
      model extensions.

## Step 5: C `.pyi` Generation And Policy

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

## Step 6: Corpus And Stabilization

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

## Guardrails For All Remaining Work

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
- Do not modify Fortran parser behavior as part of C parser work unless a shared
  change is explicitly planned, tested, and documented.
