# Fortran Wrapper Implementation Checklist

This document tracks the remaining work needed for broad Fortran-to-Python
runtime wrapper support. It is an implementation roadmap, not evidence that an
unchecked feature is supported.

Work through the sections in order unless a section explicitly has no
dependency on earlier work. A feature is complete only when its generated
extension is compiled, imported, and exercised from Python.

## Status Rules

- `[x]` means the behavior has an end-to-end runtime wrapper test.
- `[ ]` means implementation or runtime evidence is still missing.
- Parser or semantic tests alone do not establish wrapper support.
- Do not add compatibility aliases or legacy entry points while completing a
  checklist item unless they are explicitly required.

## Definition Of Done

Every feature section must satisfy the applicable items below before all of its
boxes are checked.

- [ ] The Python-visible API and ownership behavior are documented.
- [ ] The parser preserves every source fact required by the wrapper.
- [ ] Semantic IR preserves the contract without relying on source-text
  reconstruction.
- [ ] Readiness reports a precise blocker when the contract is incomplete or
  unsupported.
- [ ] Semantic IR conversion to codegen AST preserves the contract.
- [ ] Generated Fortran and C code compile without hand edits.
- [ ] Runtime tests call the imported extension and verify results, mutation,
  lifetime, and failure behavior.
- [ ] Negative tests verify deterministic Python exceptions for invalid calls.
- [ ] Fixed-form and free-form coverage is added where the feature exists in
  both language forms.
- [ ] User documentation states the supported subset and its limitations.

## Verified Baseline

These behaviors already have compiled wrapper tests and should remain passing
while the checklist is implemented.

- [x] Single-source fixed-form and free-form wrapper builds.
- [x] Scalar integer, real, complex, and logical calls and results.
- [x] Rank-1 contiguous and positive-stride array arguments.
- [x] Rank-2 and rank-3 Fortran-ordered array arguments.
- [x] Rejection of C-ordered, zero-stride, and negative-stride arrays where the
  Fortran contract does not permit them.
- [x] Fixed-length, assumed-length, and allocatable character function results.
- [x] Basic derived-type construction, scalar fields, default `pass`, explicit
  non-first `pass(name)`, and `nopass` type-bound methods.
- [x] Allocatable rank-1 and rank-2 derived-type fields exposed as NumPy arrays.

## 1. Generic Procedure Interfaces

Current state: named module interfaces and type-bound generics are preserved as
semantic overload sets, emitted with explicit x2py
`@overload("specific_procedure")` links, and dispatched by the generated C
extension. Dispatch is exact by scalar/array dtype, rank, and generated
extension class. Fortran inheritance is retained semantically but is not yet
Python C-type inheritance, so derived wrappers require explicit specific
procedures.

- [x] Define the Python API for a generic name with multiple concrete Fortran
  procedures.
- [x] Preserve module generic interfaces in semantic IR.
- [x] Preserve type-bound generic bindings and their visibility.
- [x] Resolve each generic target to a concrete procedure or emit a readiness
  blocker for missing targets.
- [x] Define dispatch precedence by Python/NumPy dtype.
- [x] Define dispatch precedence by scalar versus array rank.
- [x] Define dispatch for derived-type arguments and inheritance.
- [x] Reject indistinguishable overloads with a deterministic generation error.
- [x] Generate `.pyi` overload declarations for unambiguous overload sets.
- [x] Generate one Python-visible callable that selects the correct native
  target.
- [x] Test integer, real, and complex overloads under one generic name.
- [x] Test scalar and array overloads under one generic name.
- [x] Test no-match and ambiguous-match errors.

## 2. Defined Operators And Assignment

Current state: module-level and type-bound defined operators are preserved as
semantic overload sets, mapped to Python slots or documented named methods,
and dispatched in the generated C extension. Defined assignment is explicit
mutating `assign(...)`; Python `=` is never intercepted.

- [x] Preserve `operator(...)` and `assignment(=)` names in semantic IR.
- [x] Resolve every operator target through its generic binding.
- [x] Map arithmetic operators to `__add__`, `__sub__`, `__mul__`,
  `__truediv__`, and `__pow__` where signatures permit.
- [x] Map unary operators to `__pos__` and `__neg__`.
- [x] Map relational operators to `__eq__`, `__ne__`, `__lt__`, `__le__`,
  `__gt__`, and `__ge__`.
- [x] Define reverse-operator behavior such as `__radd__` for mixed operand
  types.
- [x] Define whether safe in-place forms such as `__iadd__` are generated.
- [x] Expose named defined operators such as `.cross.` as documented Python
  methods rather than inventing Python syntax.
- [x] Define `assignment(=)` behavior: copy, mutation, replacement, and
  self-assignment.
- [x] Preserve Fortran overload selection when multiple concrete procedures
  implement one operator.
- [x] Test derived-type/derived-type and derived-type/scalar operands.
- [x] Test reflected operands, unsupported operands, and exception messages.
- [x] Test that temporary results and assigned objects have correct lifetimes.

## 3. Output Arguments And Multiple Results

Current state: intent metadata and projection information exist in semantic IR,
but the runtime bridge does not consistently project output arguments into
Python return values.

- [ ] Define Python return behavior for scalar `intent(out)` arguments.
- [ ] Define Python return behavior for array `intent(out)` arguments.
- [ ] Define whether callers may provide preallocated output arrays.
- [ ] Define tuple ordering for multiple output arguments and function results.
- [ ] Preserve `intent(in)`, `intent(out)`, and `intent(inout)` through codegen
  AST conversion.
- [ ] Consume semantic projection mappings during wrapper generation.
- [ ] Return newly produced scalar outputs directly to Python.
- [ ] Return multiple outputs as a stable Python tuple.
- [ ] Verify that `intent(inout)` mutates the supplied Python object and is not
  duplicated unnecessarily.
- [ ] Handle a function result combined with output dummy arguments.
- [ ] Test scalar, array, string, and derived-type outputs.
- [ ] Test output allocation failures and invalid preallocated output shapes.

## 4. Optional Arguments

Current state: optional facts are parsed and stored in semantic IR, but codegen
AST conversion currently drops the Python-call omission contract.

- [ ] Preserve optional status through semantic IR to codegen AST conversion.
- [ ] Define omission separately from explicitly passing `None`.
- [ ] Generate correct Fortran `present(...)` behavior through the binding
  layer.
- [ ] Ensure positional and keyword calls preserve native argument order.
- [ ] Place optional Python parameters after required parameters without
  changing native positions.
- [ ] Support optional scalar arguments.
- [ ] Support optional array arguments.
- [ ] Support optional character arguments.
- [ ] Support optional derived-type arguments.
- [ ] Support optional output and inout arguments.
- [ ] Test omitted, supplied, and `None` cases.
- [ ] Test multiple independent optional arguments and mixed keyword calls.

## 5. `value` And Existing `bind(C)` Calls

Current state: `value` and procedure `bind(C)` attributes are parsed, but the
runtime path needs explicit ABI tests and complete name handling.

- [ ] Preserve by-value versus by-reference scalar calling conventions through
  code generation.
- [ ] Preserve procedure `bind(C)` metadata in semantic IR.
- [ ] Preserve and use `bind(C, name="...")` external names.
- [ ] Avoid generating an unnecessary Fortran shim when an existing C ABI can
  be called safely.
- [ ] Support interoperable scalar integer, real, complex, logical, and
  character kinds.
- [ ] Validate unsupported non-interoperable declarations before compilation.
- [ ] Test by-value and by-reference versions of the same scalar type.
- [ ] Test an existing `bind(C)` procedure with a renamed external symbol.
- [ ] Test ABI failure diagnostics for unsupported declarations.

## 6. Allocatable Dummy Arguments And Results

Current state: allocatable derived-type fields work in a limited form.
Allocatable dummy arguments, replacement semantics, and general results are not
covered end to end.

- [ ] Define ownership for `allocatable, intent(out)` results returned to
  Python.
- [ ] Define replacement behavior for `allocatable, intent(inout)` arguments.
- [ ] Define who deallocates native storage and when.
- [ ] Preserve allocation state and deferred shape through all IR layers.
- [ ] Return `None` or a documented sentinel for unallocated values.
- [ ] Safely expose newly allocated rank-1 and multidimensional arrays.
- [ ] Invalidate or detach stale Python views after native reallocation.
- [ ] Support allocatable scalar derived types where feasible.
- [ ] Test allocate, reallocate, deallocate, and unallocated paths.
- [ ] Test object destruction without leaks or double frees.

## 7. Pointer Arguments, Results, And Association

Current state: pointer facts are preserved in semantic storage contracts, but
general pointer ownership and association are not a supported runtime contract.

- [ ] Define borrowed, owned, and nullable pointer policies.
- [ ] Define pointer association and reassociation behavior visible to Python.
- [ ] Preserve target and contiguity requirements needed by the pointer.
- [ ] Support associated and unassociated scalar pointers.
- [ ] Support associated and unassociated array pointers.
- [ ] Keep native pointer targets alive while Python views reference them.
- [ ] Prevent Python from freeing borrowed native storage.
- [ ] Detect or block dangling pointer results when lifetime cannot be proven.
- [ ] Test aliasing between two Python-visible pointers to the same target.
- [ ] Test null association, reassociation, owner destruction, and target
  reallocation.

## 8. Array-Valued Function Results

Current state: character function results have specialized support, but general
numeric and derived-type array results do not have complete shape and ownership
handling.

- [ ] Support explicit-shape numeric array results.
- [ ] Support automatic-shape numeric array results.
- [ ] Support allocatable numeric array results.
- [ ] Support pointer array results under an explicit lifetime policy.
- [ ] Support multidimensional Fortran-order results.
- [ ] Preserve dtype, rank, bounds, and contiguity in the returned NumPy array.
- [ ] Define copy versus zero-copy behavior for each result category.
- [ ] Support arrays of derived types or report a precise blocker.
- [ ] Test zero-sized, rank-1, rank-2, and rank-3 results.
- [ ] Test result lifetime after temporary wrapper objects are destroyed.

## 9. Remaining Array Contracts

Current state: explicit-shape and assumed-shape arrays are tested for selected
ranks. Several descriptor and bounds cases remain unsupported or unverified.

- [ ] Test assumed-size arrays and define how their missing final extent is
  supplied.
- [ ] Implement deferred-shape allocatable and pointer arrays.
- [ ] Implement assumed-rank `dimension(..)` with explicit accepted rank and
  dtype policy.
- [ ] Implement assumed-type `type(*)` or emit a stable readiness blocker.
- [ ] Preserve and validate non-default lower bounds.
- [ ] Support zero-length dimensions.
- [ ] Test ranks 4 through the selected maximum supported rank.
- [ ] Define a deterministic maximum rank and reject higher ranks early.
- [ ] Support arrays of character values or emit a precise blocker.
- [ ] Support arrays of derived types or emit a precise blocker.
- [ ] Detect shape mismatches before entering Fortran.
- [ ] Define overlapping input/output memory behavior.
- [ ] Test read-only NumPy inputs for `intent(in)` and writable requirements for
  `intent(out/inout)`.
- [ ] Test byte order, dtype mismatch, alignment, and unsafe cast failures.

## 10. Derived Types Across Procedure Boundaries

Current state: classes, fields, and basic type-bound methods are tested. General
derived-type arguments, results, arrays, nested components, and ownership are
not fully covered.

- [ ] Support scalar derived-type arguments for `intent(in)`.
- [ ] Support scalar derived-type arguments for `intent(inout)`.
- [ ] Support scalar derived-type output arguments and function results.
- [ ] Support nested derived-type components.
- [ ] Define copy versus reference behavior for each intent.
- [ ] Preserve private component visibility.
- [ ] Support allocatable and pointer components using the ownership policies
  from sections 6 and 7.
- [ ] Support arrays of derived types or explicitly defer them.
- [ ] Prevent use-after-free when child objects or field views outlive parents.
- [ ] Test identity, mutation, copy, nested fields, and destruction order.

## 11. Inheritance And Polymorphism

Current state: `extends(...)` is represented semantically, while runtime
inheritance and general polymorphic calls are not verified.

- [ ] Generate Python inheritance for supported Fortran extension types.
- [ ] Preserve base-component layout and initialization.
- [ ] Support `class(base)` scalar arguments with known concrete dynamic types.
- [ ] Support polymorphic results under an explicit ownership policy.
- [ ] Define accepted dynamic types for allocatable polymorphic values.
- [ ] Support abstract types as non-instantiable Python base classes.
- [ ] Support deferred type-bound procedures or report readiness blockers.
- [ ] Define behavior for overridden type-bound procedures.
- [ ] Handle `class(*)` and `select type` contracts or reject them explicitly.
- [ ] Test base calls, overridden calls, upcasting, invalid dynamic types, and
  object lifetime.

## 12. Constructors, Initialization, And Finalizers

Current state: Python can allocate basic wrapped classes, but default component
initialization, user constructors, and Fortran finalization are not complete
runtime contracts.

- [ ] Preserve default component initialization expressions.
- [ ] Define the generated default Python constructor signature.
- [ ] Map supported generic constructor interfaces to Python construction.
- [ ] Define keyword initialization for public components.
- [ ] Preserve and resolve `final` procedure metadata instead of discarding it.
- [ ] Invoke final procedures exactly once for owned native instances.
- [ ] Do not finalize borrowed instances.
- [ ] Define behavior when a finalizer fails or terminates execution.
- [ ] Test default initialization, custom construction, partial construction,
  garbage collection, and repeated deletion.

## 13. Dummy Procedures, Procedure Pointers, And Callbacks

Current state: procedure declarations and interfaces can be parsed, but callback
signature, lifetime, threading, and exception behavior are incomplete.

- [ ] Resolve dummy procedures through explicit or abstract interfaces.
- [ ] Represent callback argument and result types as a complete semantic
  callable contract.
- [ ] Distinguish immediate-call callbacks from stored callbacks.
- [ ] Define Python callback lifetime and native registration ownership.
- [ ] Define callback invocation from non-Python native threads.
- [ ] Acquire and release the GIL correctly around callbacks.
- [ ] Define Python exception propagation through Fortran and C boundaries.
- [ ] Support procedure-pointer association and null procedure pointers.
- [ ] Support callback context/state without relying on global mutable state.
- [ ] Test scalar, array, and derived-type callback arguments.
- [ ] Test stored callbacks, unregistering, exceptions, threads, and object
  destruction.

## 14. Module Variables And Constants

Current state: module variables reach semantic IR and lower-level codegen has
partial machinery, but public runtime behavior is not systematically tested.

- [ ] Expose public scalar module variables with typed getters and setters.
- [ ] Expose public module arrays with explicit copy/view and lifetime policy.
- [ ] Expose parameters as read-only Python constants.
- [ ] Reject writes to parameters and private variables.
- [ ] Support allocatable module variables using section 6 ownership rules.
- [ ] Support pointer module variables using section 7 ownership rules.
- [ ] Define synchronization and thread-safety expectations for global state.
- [ ] Define whether `save` variables are exposed or remain procedure-internal.
- [ ] Decide whether common blocks are supported, shimmed, or explicitly
  rejected.
- [ ] Test mutation visibility across Python calls and multiple module objects.

## 15. Fortran Enums

Current state: `enum, bind(C)` syntax is validated, but enumerator metadata is
not exported to semantic IR or Python.

- [ ] Add parser models for enum blocks and enumerators.
- [ ] Preserve explicit and implicit enumerator values.
- [ ] Convert Fortran enums to semantic enums.
- [ ] Emit `.pyi` enum declarations.
- [ ] Generate Python `IntEnum` or document another stable representation.
- [ ] Accept enum members and documented integer coercions as arguments.
- [ ] Return enum members from functions and fields.
- [ ] Preserve `bind(C)` underlying representation.
- [ ] Test explicit values, implicit increments, invalid values, and round trips.

## 16. Character Edge Cases

Current state: common scalar character arguments and results work. Mutable,
optional, array, encoding, and embedded-NUL behavior remains incomplete.

- [ ] Support `intent(out)` scalar character arguments.
- [ ] Support `intent(inout)` scalar character arguments.
- [ ] Support optional character arguments.
- [ ] Support allocatable character dummy arguments.
- [ ] Support character arrays or emit a precise blocker.
- [ ] Define truncation and padding behavior for fixed lengths.
- [ ] Define embedded NUL handling for Fortran and `c_char` strings.
- [ ] Define encoding for default character and non-ASCII text.
- [ ] Support or reject non-default character kinds explicitly.
- [ ] Validate hidden-length ABI behavior across supported compilers.
- [ ] Test empty strings, exact length, truncation, padding, Unicode, embedded
  NUL, and mutable outputs.

## 17. Scalar Types And Kind Coverage

Current state: selected common 32-bit and 64-bit scalar types are exercised.
The semantic map is broader than the runtime evidence.

- [ ] Test signed integer kinds corresponding to 8, 16, 32, and 64 bits.
- [ ] Test logical arguments, results, and arrays for supported storage sizes.
- [ ] Test real kinds corresponding to 32 and 64 bits.
- [ ] Decide whether real 80/128-bit values are supported, converted, or
  blocked.
- [ ] Test complex kinds corresponding to 64 and 128 bits.
- [ ] Decide whether complex 160/256-bit values are supported, converted, or
  blocked.
- [ ] Test `iso_fortran_env` named kinds.
- [ ] Test `iso_c_binding` named kinds.
- [ ] Use compiler probing when kind numbers do not imply portable storage.
- [ ] Reject unsupported target mappings before wrapper compilation.
- [ ] Test scalar and array round trips at min/max, NaN, infinity, and complex
  edge values.

## 18. Derived-Type Layout And Interoperability

Current state: native derived types are accessed through generated wrappers,
but complete `bind(C)`, `sequence`, and layout-sensitive contracts are not
verified.

- [ ] Preserve `bind(C)` and `sequence` type attributes in semantic IR.
- [ ] Preserve component declaration order and interoperable component facts.
- [ ] Define when direct C layout access is allowed.
- [ ] Use generated accessors when direct layout cannot be proven.
- [ ] Support interoperable `bind(C)` types passed by value where ABI-safe.
- [ ] Block non-interoperable by-value transfers with a precise diagnostic.
- [ ] Define padding, alignment, and compiler-layout validation policy.
- [ ] Test nested interoperable types and mixed scalar fields.
- [ ] Test layout behavior across each supported compiler/platform pair.

## 19. Multiple Files, Modules, And Submodules

Current state: runtime wrapper builds require one generated semantic module from
one source path.

- [ ] Accept multiple source files in one wrapper build.
- [ ] Build a dependency graph from `use` associations.
- [ ] Compile modules in dependency order.
- [ ] Support renamed and `only` imports across wrapped modules.
- [ ] Define one-extension versus multiple-extension packaging.
- [ ] Support standalone external procedures alongside modules.
- [ ] Support submodules and separate module procedures.
- [ ] Accept prebuilt module/include/library search paths.
- [ ] Detect duplicate modules and dependency cycles before compilation.
- [ ] Include all source and module dependencies in incremental rebuild logic.
- [ ] Test a multi-file project with derived types, generics, and submodules.

## 20. Visibility, Naming, And Python Surface

Current state: some public/private and native/Python naming information exists,
but collision behavior needs end-to-end policy and tests.

- [ ] Export only public Fortran procedures, types, bindings, and variables.
- [ ] Preserve private type-bound procedures as non-public implementation
  details.
- [ ] Handle Fortran case-insensitive collisions deterministically.
- [ ] Handle Python keywords and invalid Python identifiers.
- [ ] Handle generic names colliding with concrete procedure names.
- [ ] Handle module, type, field, and method names that collide after Python
  normalization.
- [ ] Preserve `bind(C, name=...)` native names without changing the Python API
  unintentionally.
- [ ] Define and document any name-mangling policy.
- [ ] Test collisions, private symbols, renamed imports, and error messages.

## 21. Runtime Errors, Concurrency, And Portability

Current state: the tested build path uses GNU Fortran on the local/CI platform.
Production runtime behavior and compiler portability remain broader work.

- [ ] Define behavior for `stop` and `error stop` without terminating the Python
  process where technically possible.
- [ ] Define status-code and error-message projection to Python exceptions.
- [ ] Release the GIL around long-running native calls where safe.
- [ ] Preserve the GIL around calls that can invoke Python callbacks.
- [ ] Define thread safety for module variables and wrapped object state.
- [ ] Test recursive and reentrant calls.
- [ ] Test OpenMP-enabled procedures and document supported host-memory rules.
- [ ] Decide policy for coarrays, teams, events, and device/offload memory.
- [ ] Verify supported behavior with GNU Fortran.
- [ ] Add compiler-specific verification for LLVM Flang, Intel, and NVHPC only
  when those compilers become supported targets.
- [ ] Add platform verification for Linux, macOS, and Windows only when their
  compiler toolchains are supported.
- [ ] Test debug and optimized builds for ABI-sensitive behavior.
- [ ] Add leak, use-after-free, and double-free checks for ownership-heavy
  features.

## Recommended Execution Order

Use this order to minimize rework:

1. Generic procedure interfaces.
2. Defined operators and assignment.
3. Output arguments and multiple results.
4. Optional arguments.
5. `value` and existing `bind(C)` calls.
6. Allocatable dummy arguments and results.
7. Pointer arguments, results, and association.
8. Array-valued function results.
9. Remaining array contracts.
10. Derived types across procedure boundaries.
11. Inheritance and polymorphism.
12. Constructors, initialization, and finalizers.
13. Dummy procedures, procedure pointers, and callbacks.
14. Module variables and constants.
15. Fortran enums.
16. Character edge cases.
17. Scalar types and kind coverage.
18. Derived-type layout and interoperability.
19. Multiple files, modules, and submodules.
20. Visibility, naming, and Python surface.
21. Runtime errors, concurrency, and portability.

When a section is completed, replace only its verified boxes with `[x]` and
link the section to the runtime tests that prove the behavior.
