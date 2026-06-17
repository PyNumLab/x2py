# Fortran Wrapper Implementation Checklist

This document tracks the remaining work needed for broad Fortran-to-Python
runtime wrapper support. It is an implementation roadmap, not evidence that an
unchecked feature is supported.

Work through the sections in order unless a section explicitly has no
dependency on earlier work. A feature is complete only when its generated
extension is compiled, imported, and exercised from Python.

Most remaining implementation work in this checklist is expected to be in
`x2py/semantics/ir2ast.py` and `x2py/codegen/`. Some items may still require
targeted changes elsewhere, but those two areas should contain nearly all of
the wrapper behavior work.

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

Example: a module interface `norm` with `norm_i32`, `norm_f64`, and `norm_vec`
becomes one Python callable that dispatches by dtype and rank. This section is
mostly straightforward now; the remaining risk is accepting two specifics that
look different in Fortran but collapse to the same Python/NumPy signature.

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

Example: `interface operator(+)` maps to `__add__` and, when argument order
allows it, `__radd__`; `interface assignment(=)` maps to `obj.assign(rhs)`.
The main design choice is fixed: Python syntax is used only where Python has a
matching operation. Named Fortran operators such as `.cross.` remain named
methods because inventing syntax would hide dispatch and error behavior.

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

Current state: intent metadata and projection information exist in semantic IR.
Allocatable array function results and allocatable `intent(out)` array dummy
arguments use a copy-return policy: the Fortran bridge copies allocated native
storage into C memory, deallocates the Fortran temporary, and returns a NumPy
array that owns the copied memory. General output projection for scalar,
non-allocatable array, string, derived-type, and multi-output combinations is
still incomplete.

Example: `call solve(a, x, info)` where `x` and `info` are `intent(out)` could
return `(x, info)`, or require a caller-provided mutable `x` and return only
`info`. The choice affects allocation, tuple ordering, and whether Python can
distinguish `intent(out)` from `intent(inout)` mutation.
For allocatable `intent(out)` arrays and allocatable array function results the
chosen path is copy-return. Unallocated allocatable results return `None`.
`intent(inout)` allocatable replacement remains section 6 work because Python
must decide whether the existing object is replaced, detached, or mutated.

- [ ] Define Python return behavior for scalar `intent(out)` arguments.
- [x] Define Python return behavior for allocatable array `intent(out)`
  arguments.
- [ ] Define Python return behavior for non-allocatable array `intent(out)`
  arguments.
- [ ] Define whether callers may provide preallocated output arrays.
- [ ] Define tuple ordering for multiple output arguments and function results.
- [x] Preserve `intent(in)`, allocatable `intent(out)`, and `intent(inout)`
  through codegen AST conversion.
- [ ] Preserve non-allocatable `intent(out)` through codegen AST conversion.
- [ ] Consume semantic projection mappings during wrapper generation.
- [ ] Return newly produced scalar outputs directly to Python.
- [ ] Return multiple outputs as a stable Python tuple.
- [ ] Verify that `intent(inout)` mutates the supplied Python object and is not
  duplicated unnecessarily.
- [ ] Handle a function result combined with output dummy arguments.
- [x] Test allocatable array outputs and allocatable array function results.
- [ ] Test scalar, non-allocatable array, string, and derived-type outputs.
- [ ] Test output allocation failures and invalid preallocated output shapes.

## 4. Optional Arguments

Current state: optional facts are parsed and stored in semantic IR, but codegen
AST conversion currently drops the Python-call omission contract.

Example: `subroutine step(dt, max_iter, tol)` with optional `max_iter` and
`tol` should allow `step(dt)`, `step(dt, tol=1e-8)`, and deterministic handling
of `None`. The key issue is that omitted and explicitly passed `None` are not
always equivalent to Fortran `present(...)`, especially for optional outputs or
arrays.

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

Example: `integer(c_int), value :: n` must be passed by value, while the same
declaration without `value` remains by reference. Existing `bind(C,
name="...")` procedures can sometimes be called directly, but only when every
argument has an interoperable ABI; otherwise a Fortran shim is still needed.

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

Current state: allocatable derived-type fields and target-backed module arrays
are exposed as borrowed zero-copy NumPy views with `None` for unallocated
storage. Allocatable array function results and allocatable `intent(out)` array
dummies are copied into NumPy-owned memory before returning to Python.
Replacement semantics for allocatable `intent(inout)` remain blocked.

Example: `real(c_double), allocatable :: values(:)` inside a wrapped derived
type is read as `obj.values`, returning either `None` or a borrowed NumPy view.
For dummy arguments such as `real, allocatable, intent(out) :: values(:)`, x2py
uses a copy-return policy: after the native call, allocated Fortran storage is
copied to C memory that NumPy owns through its generated base capsule, then the
Fortran allocatable is deallocated. A plain NumPy view over Fortran-allocated
storage would not automatically make NumPy the owner; ownership requires either
this copy or a capsule/base object whose destructor calls the correct Fortran
deallocation routine.

- [x] Define ownership for `allocatable, intent(out)` array results returned to
  Python using copy-return NumPy-owned storage.
- [ ] Define replacement behavior for `allocatable, intent(inout)` arguments.
- [x] Define who deallocates native storage and when for allocatable
  copy-return arrays.
- [ ] Preserve allocation state and deferred shape through all IR layers.
- [x] Return `None` for unallocated copy-return arrays.
- [x] Safely expose newly allocated rank-1 and multidimensional copy-return
  arrays.
- [ ] Invalidate or detach stale Python views after native reallocation.
- [ ] Support allocatable scalar derived types where feasible.
- [ ] Test allocate, reallocate, deallocate, and unallocated paths.
- [ ] Test object destruction without leaks or double frees.

## 7. Pointer Arguments, Results, And Association

Current state: pointer facts are preserved in semantic storage contracts, but
general pointer ownership and association are not a supported runtime contract.

Example: `real, pointer :: p(:)` may be associated with module storage, a
derived-type field, a dummy argument target, or nothing. Possible paths are:
expose only nullable borrowed views, create owner capsules for known allocated
targets, or block all pointer results until lifetime can be proven. The hard
issue is reassociation: Python may hold a view while Fortran points `p`
somewhere else.

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

Example: `function spectrum(n) result(x); real :: x(n)` can return a copied
NumPy array because the result is temporary, while `real, pointer :: x(:)` or
`real, allocatable :: x(:)` needs an explicit lifetime owner. The design choices
are copy for all function arrays, zero-copy only where ownership is stable, or a
mixed policy based on result category.

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

Example: `a(n, m)` is straightforward when `n` and `m` are known arguments, but
`a(*)`, `dimension(..)`, non-default lower bounds, and rank greater than the
selected maximum need explicit Python-side validation rules. The main decisions
are how callers supply missing extents, which ranks are accepted, and whether
copies are allowed for non-contiguous or byte-swapped arrays.

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

Example: `subroutine update(p)` with `type(particle), intent(inout) :: p`
should mutate the native instance behind the Python wrapper. Passing derived
types by value, returning new derived instances, nested components, and arrays
of derived types each need separate ownership and layout decisions; scalar
borrowed fields are simpler than replacement of whole objects.

- [ ] Support scalar derived-type arguments for `intent(in)`.
- [ ] Support scalar derived-type arguments for `intent(inout)`.
- [ ] Support scalar derived-type output arguments and function results.
- [ ] Support nested derived-type components.
- [ ] Define copy versus reference behavior for each intent.
- [ ] Preserve private component visibility.
- [x] Support allocatable components using the borrowed-view policy from
  section 6.
- [ ] Support pointer components using the ownership policy from section 7.
- [ ] Support arrays of derived types or explicitly defer them.
- [x] Prevent parent destruction while borrowed field views exist.
- [ ] Test identity, mutation, copy, nested fields, and destruction order.

## 11. Inheritance And Polymorphism

Current state: `extends(...)` is represented semantically, while runtime
inheritance and general polymorphic calls are not verified.

Example: `class(shape), intent(in) :: s` may receive a `circle` or `box` at
runtime. Options include Python inheritance mirroring Fortran extension types,
explicit dynamic-type tags with checked casts, or blocking polymorphic calls.
The difficult part is preserving Fortran dispatch and finalization when the
declared type and dynamic type differ.

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

Example: a type with default field values and `final :: cleanup` should produce
a Python object whose native storage is initialized exactly once and finalized
exactly once. The main choices are whether construction is always generated,
whether generic constructor interfaces map to `__init__`, and how finalizer
failures are represented without corrupting Python object destruction.

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

Example: `subroutine integrate(f)` where `f` is a dummy procedure can call a
Python function immediately, while storing `f` for later needs a persistent
callback handle. Possible paths are immediate-call callbacks only, registered
callbacks with explicit unregister, or full procedure-pointer support. Stored
callbacks require GIL, exception, and lifetime policy.

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

Current state: module variables reach semantic IR. Target-backed allocatable
module arrays are exposed through explicit getters as borrowed zero-copy NumPy
views with `None` for unallocated storage. Native module storage remains owned
by the Fortran module for the process lifetime.

Example: `real(c_double), allocatable, target :: values(:)` is exposed as
`get_values() -> ndarray | None`; users call wrapped Fortran allocation and
deallocation routines explicitly. Existing views are borrowed and are not
tracked: if Fortran reallocates or deallocates `values`, a previous NumPy view
may dangle, so callers must copy when they need independent lifetime. Scalar
module variables are a separate path: they can be property-like getters/setters
unless they are `parameter`, in which case they should become read-only Python
constants.

- [ ] Expose public scalar module variables with typed getters and setters.
- [x] Expose public allocatable module arrays with explicit copy/view and
  lifetime policy.
- [ ] Expose parameters as read-only Python constants.
- [ ] Reject writes to parameters and private variables.
- [x] Support allocatable module variables using section 6 ownership rules.
- [ ] Support pointer module variables using section 7 ownership rules.
- [ ] Define synchronization and thread-safety expectations for global state.
- [ ] Define whether `save` variables are exposed or remain procedure-internal.
- [ ] Decide whether common blocks are supported, shimmed, or explicitly
  rejected.
- [ ] Test mutation visibility across Python calls and multiple module objects.

## 15. Fortran Enums

Current state: `enum, bind(C)` syntax is validated, but enumerator metadata is
not exported to semantic IR or Python.

Example: `enum, bind(C); enumerator :: red = 1, blue; end enum` should preserve
explicit and implicit integer values. The main design choice is whether Python
gets `enum.IntEnum`, plain integer constants, or both; argument conversion and
return values must then consistently preserve or coerce enum identity.

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

Example: `character(len=8), intent(inout) :: name` can truncate, pad, and mutate
in place, while `character(len=:), allocatable` needs allocation ownership.
Decisions include whether Python `str` or `bytes` is the public type for each
kind, how embedded NULs behave, and whether character arrays are supported or
blocked with a precise diagnostic.

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

Example: `integer(kind=selected_int_kind(18))` may be 64-bit on one compiler and
unavailable or different elsewhere. Straightforward cases are common C
interoperable kinds; the riskier path needs compiler probing so kind numbers do
not get mistaken for byte sizes. Unsupported kinds should fail before wrapper
compilation.

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

Example: a `type, bind(C) :: point` with two `real(c_double)` components can
share C layout if padding and alignment are proven, while ordinary Fortran
types should use generated accessors. The decision is whether to expose direct
memory views for interoperable types only, or always route through accessors to
avoid compiler-layout assumptions.

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

Example: module `solver` may `use mesh, only: grid`, and a submodule may
implement procedures declared in the parent module. The likely path is a module
dependency graph with ordered compilation and one generated extension; open
issues are duplicate module names, renamed imports, prebuilt module files, and
incremental rebuild invalidation across all sources.

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

Example: Fortran names `class`, `Class`, and `class_` can collide after Python
normalization or keyword escaping. This section is mostly policy and diagnostic
work: decide one mangling rule, apply it consistently to modules, types,
methods, fields, and generated helpers, and fail deterministically when two
public symbols still collide.

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

Example: `error stop` inside wrapped Fortran can terminate the process unless
the runtime path intercepts it, and a long OpenMP region may need GIL release
without allowing unsafe Python callbacks. Possible paths are GNU-only documented
support first, then compiler-specific verification for each additional ABI and
platform after the core behavior is stable.

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
