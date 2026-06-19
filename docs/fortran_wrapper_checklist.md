# Fortran Wrapper Implementation Checklist

This document tracks the remaining work needed for broad Fortran-to-Python
runtime wrapper support. It is an implementation roadmap, not evidence that an
unchecked feature is supported.

The canonical ownership, lifetime, borrowed-view, snapshot-copy, and destruction
rules are defined in `docs/fortran_wrapper_ownership_policy.md`. Checklist
sections may summarize those rules, but implementation decisions should use the
ownership policy document as the source of truth.

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
Numeric, logical, fixed-length scalar character, and scalar derived-type
`intent(out)` dummy arguments, non-allocatable array `intent(out)` dummy
arguments, allocatable array `intent(out)` dummy arguments, and function results
combined with output dummy arguments are projected into the documented Python
return shape. Allocatable array function results and allocatable `intent(out)`
array dummy arguments use a copy-return policy: the Fortran bridge copies
allocated native storage into C memory, deallocates the Fortran temporary, and
returns a NumPy array that owns the copied memory.

The Python API distinguishes output projection from in-place mutation:

- A scalar, non-allocatable `intent(out)` dummy is hidden from the Python
  signature. The bridge allocates native temporary storage, passes it to
  Fortran, converts the written value after the call, and returns it to Python.
  Generated `.pyi` stubs expose the by-reference return type, such as
  `Ptr(Float64)`. A primitive scalar return is reserved for by-value semantics.
- A scalar `character, intent(out)` dummy follows the same hidden output rule
  and is returned as a new Python `str`.
- A scalar `character, intent(inout)` dummy stays in the Python signature but is
  projected back as a replacement value because Python `str` is immutable. The
  wrapper copies the input string into mutable native character storage, calls
  Fortran, and returns a new Python `str` with the post-call value. The original
  Python `str` object is unchanged.
- A scalar derived-type `intent(out)` dummy follows the same hidden output rule
  and is returned as a Python wrapper object for the produced native value.
- An `intent(out), allocatable` dummy is hidden from the Python signature. The
  wrapper lets Fortran allocate it and returns the result. If it remains
  unallocated, Python receives `None`. Allocatable array outputs use
  copy-return NumPy-owned storage: the bridge copies the allocated native
  storage into C memory, deallocates the Fortran temporary, and returns a NumPy
  array with `Ownership: Python-owned`. If that copy allocation fails after
  Fortran produced a non-empty shape, Python raises `MemoryError`; this is
  distinct from the `None` result used for a genuinely unallocated output.
- A non-allocatable array-like `intent(out)` dummy stays in the Python
  signature because the caller must provide storage. The wrapper validates
  dtype, rank, shape, and layout, Fortran writes into the supplied object, and
  the same Python object is returned. Its initial contents are ignored.
- An `intent(inout)` dummy stays in the Python signature, is mutated in place,
  and is not duplicated into the return value unless explicit `intent(out)`
  values require a tuple.

If a Fortran function has both a function result and one or more `intent(out)`
dummy arguments, Python returns a tuple. Tuple order is always the function
result first, followed by `intent(out)` values in Fortran dummy argument order.
This order covers hidden scalar outputs, allocatable outputs, and
caller-provided non-allocatable array outputs. Generated NumPy-style docstrings
and `.pyi` stubs must match these signatures: `.pyi` `Returns["name", T]`
annotations are used only for returned values that are also present as
Python-visible arguments, such as caller-provided non-allocatable output arrays.
Hidden scalar and allocatable outputs use plain return annotations, with
allocatable outputs written as `T | None` to represent the unallocated case.
Caller-provided array outputs remain under `Parameters` with `Intent: out`, and
returned arrays document Python ownership and copy overhead when applicable.

`intent(inout)` allocatable replacement remains section 6 work because Python
must decide whether the existing object is replaced, detached, or mutated.

- [x] Define Python return behavior for scalar `intent(out)` arguments.
- [x] Define Python return behavior for allocatable array `intent(out)`
  arguments.
- [x] Define Python return behavior for non-allocatable array `intent(out)`
  arguments.
- [x] Define whether callers may provide preallocated output arrays.
- [x] Define tuple ordering for multiple output arguments and function results.
- [x] Preserve `intent(in)`, allocatable `intent(out)`, and `intent(inout)`
  through codegen AST conversion.
- [x] Preserve non-allocatable `intent(out)` through codegen AST conversion.
- [ ] Consume semantic projection mappings during wrapper generation.
- [x] Return newly produced scalar outputs directly to Python.
- [x] Return multiple outputs as a stable Python tuple.
- [x] Verify that `intent(inout)` mutates the supplied Python object and is not
  duplicated unnecessarily.
- [x] Handle a function result combined with output dummy arguments.
- [x] Test allocatable array outputs and allocatable array function results.
- [x] Test scalar and non-allocatable array outputs.
- [x] Test string and derived-type outputs.
- [x] Test invalid preallocated output dtype, rank, shape, and layout.
- [x] Test output allocation failure exceptions.

## 4. Optional Arguments

Current state: optional facts are parsed and stored in semantic IR, preserved
through codegen AST conversion, and consumed by the generated Python, C, and
Fortran binding layers. Python-visible optionals may be omitted or passed as
`None`; supplied concrete values make the native Fortran dummy present.

Example: `subroutine step(dt, max_iter, tol)` with optional `max_iter` and
`tol` should allow `step(dt)`, `step(dt, tol=1e-8)`, and deterministic handling
of `None`. The key issue is that omitted and explicitly passed `None` are not
always equivalent to Fortran `present(...)`, especially for optional outputs or
arrays.

The Python wrapper contract is:

- Optional Python parameters are emitted after required parameters, but the
  native dummy argument name and position are preserved in the generated binding
  layer.
- Omitting a Python-visible optional argument means no actual argument is
  passed to the Fortran procedure, so `present(dummy)` is false.
- Passing `None` is accepted for Python-visible optional arguments and also
  means no native actual argument is passed. It is distinct from passing a real
  scalar, array, string, or derived-type wrapper value, all of which make
  `present(dummy)` true.
- Optional `intent(inout)` arguments are Python-visible optional parameters.
  When supplied, they are mutated according to the normal inout rules. When
  omitted or passed as `None`, the native dummy is absent and no mutation
  occurs.
- Optional caller-provided `intent(out)` arrays are Python-visible optional
  parameters. Supplying an array makes the dummy present, validates the array,
  mutates it in place, and returns the same array according to the Section 3
  output-projection rules. Omitting it or passing `None` makes the dummy absent
  and returns `None` for that output position.
- Optional scalar or derived-type `intent(out)` dummies remain hidden outputs.
  Because they are return values rather than Python parameters, the wrapper
  requests them by passing native temporary storage, so `present(dummy)` is
  true and the produced value is returned using the Section 3 projection rules.

- [x] Preserve optional status through semantic IR to codegen AST conversion.
- [x] Define omission separately from explicitly passing `None`.
- [x] Generate correct Fortran `present(...)` behavior through the binding
  layer.
- [x] Ensure positional and keyword calls preserve native argument order.
- [x] Place optional Python parameters after required parameters without
  changing native positions.
- [x] Support optional scalar arguments.
- [x] Support optional array arguments.
- [x] Support optional character arguments.
- [x] Support optional derived-type arguments.
- [x] Support optional output and inout arguments.
- [x] Test omitted, supplied, and `None` cases.
- [x] Test multiple independent optional arguments and mixed keyword calls.

## 5. `value` And Existing `bind(C)` Calls

Current state: `value` and procedure `bind(C)` attributes are parsed, but the
runtime path needs explicit ABI tests and complete name handling.

Example: `integer(c_int), value :: n` must be passed by value, while the same
declaration without `value` remains by reference. Existing `bind(C,
name="...")` procedures can sometimes be called directly, but only when every
argument has an interoperable ABI; otherwise a Fortran shim is still needed.

The Python API does not expose ABI mechanics. A scalar `value` dummy is still a
normal Python scalar argument, but the generated native call passes the C value
itself instead of a pointer. A scalar dummy without `value` remains a
by-reference Fortran dummy and is routed through the generated shim. Procedure
`bind(C)` metadata is preserved separately from the Python name. When an
existing `bind(C)` procedure has only interoperable scalar `value` arguments and
an interoperable scalar result or no result, the C extension calls the existing
external symbol directly, including the spelling from `bind(C, name="...")`.
Any non-interoperable declaration, by-reference dummy, array, character buffer,
derived type, optional argument, output argument, pointer, or allocatable dummy
keeps the generated Fortran shim path or raises a readiness/generation blocker
before compilation if no safe ABI is defined.

- [x] Preserve by-value versus by-reference scalar calling conventions through
  code generation.
- [x] Preserve procedure `bind(C)` metadata in semantic IR.
- [x] Preserve and use `bind(C, name="...")` external names.
- [x] Avoid generating an unnecessary Fortran shim when an existing C ABI can
  be called safely.
- [x] Support interoperable scalar integer, real, complex, logical, and
  character kinds.
- [x] Validate unsupported non-interoperable declarations before compilation.
- [x] Test by-value and by-reference versions of the same scalar type.
- [x] Test an existing `bind(C)` procedure with a renamed external symbol.
- [x] Test ABI failure diagnostics for unsupported declarations.

## 6. Allocatable Dummy Arguments And Results

Current state: allocatable derived-type fields and target-backed module arrays
are exposed as borrowed zero-copy NumPy views with `None` for unallocated
storage. Allocatable array function results and allocatable `intent(out)` array
dummies are copied into NumPy-owned memory before returning to Python.
Allocatable array `intent(inout)` dummies use replace-and-return semantics.

Array transfer mode follows the native storage category and owner, not only the
syntactic position where the array appears. Top-level allocatable outputs are
copy-return values because they cross the Python boundary as temporary
replacement storage. Allocatable fields are different because the containing
native instance owns the allocation, so Python may borrow a view whose base
keeps that wrapper alive. Pointer arrays do not have an intrinsic owner and
therefore do not inherit the borrowed-field policy merely by appearing inside a
returned derived type; section 7 defines their snapshot-or-block behavior.

Example: `real(c_double), allocatable :: values(:)` inside a wrapped derived
type is read as `obj.values`, returning either `None` or a borrowed NumPy view.
For dummy arguments such as `real, allocatable, intent(out) :: values(:)`, x2py
uses a copy-return policy: after the native call, allocated Fortran storage is
copied to C memory that NumPy owns through its generated base capsule, then the
Fortran allocatable is deallocated. A plain NumPy view over Fortran-allocated
storage would not automatically make NumPy the owner; ownership requires either
this copy or a capsule/base object whose destructor calls the correct Fortran
deallocation routine.

For an `allocatable, intent(inout)` array dummy, Python passes either `None` or
a NumPy array with the required dtype, rank, and Fortran-compatible layout.
`None` represents an initially unallocated native dummy. A supplied NumPy array
is copied into a temporary native allocatable before the call; the Python array
is never mutated in place. After the call, the final native allocation state is
projected back using the same copy-return policy as allocatable outputs:
unallocated becomes `None`, allocated storage becomes a new NumPy-owned array,
and the temporary Fortran allocation is deallocated. If a caller still holds an
old borrowed view from a field or module variable, x2py cannot invalidate that
object after unrelated native reallocation; the supported rule is detach by
copy for dummy-argument replacement and document borrowed-view lifetime limits
for fields and module variables. Allocatable scalar derived-type dummy
arguments remain blocked unless a future ownership policy defines construction,
replacement, and destruction of the wrapped scalar object.

- [x] Define ownership for `allocatable, intent(out)` array results returned to
  Python using copy-return NumPy-owned storage.
- [x] Define replacement behavior for `allocatable, intent(inout)` arguments.
- [x] Define who deallocates native storage and when for allocatable
  copy-return arrays.
- [x] Preserve allocation state and deferred shape through all IR layers.
- [x] Return `None` for unallocated copy-return arrays.
- [x] Safely expose newly allocated rank-1 and multidimensional copy-return
  arrays.
- [x] Invalidate or detach stale Python views after native reallocation.
- [x] Report a precise blocker for allocatable scalar derived types until
  construction, replacement, and destruction ownership policy is feasible.
- [x] Test allocate, reallocate, deallocate, and unallocated paths.
- [x] Test object destruction without leaks or double frees.

## 7. Pointer Arguments, Results, And Association

Current state: pointer facts are preserved in semantic storage contracts.
Procedure-level pointer support exists for the conservative snapshot subset:
pointer `intent(in)` scalars and arrays are call-local associations to
Python-owned values, pointer scalar function results are copied into ordinary
Python scalar values, and pointer array function results are copied into
Python-owned NumPy arrays. Unassociated results become `None`. General pointer
ownership, borrowed pointer views, and pointer reassociation are not supported
runtime contracts. Pointer module variables and pointer
derived-type fields follow the same ownership rule as pointer results: they may
be exposed only as Python-owned snapshot copies when association state, shape,
dtype, nullability, contiguity, target owner, and deallocation obligations are
known. Otherwise readiness must block them. They must not become borrowed NumPy
views only because they are fields of a Python-owned wrapper object.

Example: `real, pointer :: p(:)` may be associated with module storage, a
derived-type field, a dummy argument target, newly allocated storage, or
nothing. The final association state alone does not say who owns the target,
whether Python may free it, whether another Fortran object still aliases it, or
whether the target remains valid after the call.

The procedure-level subset is narrower than general Fortran pointer support:

- A pointer `intent(in)` array dummy may be associated with Python-owned NumPy
  array storage only for the duration of the native call. If Fortran saves or
  re-associates that pointer, the behavior is outside the supported contract.
- A pointer `intent(in)` scalar dummy is associated with a wrapper temporary
  containing the converted Python scalar only for the duration of the native
  call. Python does not observe writes or reassociation through that pointer.
- A pointer scalar function result is copied through wrapper-owned temporary
  storage before control returns to Python. Associated results become ordinary
  Python scalar values; unassociated results become `None`.
- A pointer array function result is returned as a snapshot copy when the wrapper
  can prove association state, shape, dtype, contiguity, target owner, and
  deallocation obligations. Associated results become Python-owned values;
  unassociated results become `None`.
- Pointer `intent(out)` and `intent(inout)` dummy arguments are blocked by
  default. They need extra user policy before wrapper generation because an
  associated result could be a callee allocation that should be deallocated
  after copying, a borrowed module or field target that must not be deallocated,
  a strided section, or a target with a longer native lifetime.
- Module pointer variables and derived-type pointer components use
  snapshot-or-block behavior. If the required array facts are available, a
  getter may return a Python-owned copy of the current target or `None` for an
  unassociated pointer. Required facts include target owner and deallocation
  obligations so snapshotting does not leak callee allocations or free borrowed
  targets. Mutating that returned array does not mutate native memory, and
  repeated access may return a new snapshot. Borrowed pointer views remain
  explicit future work that needs owner tracking and
  stale-view/reassociation rules.

Semantic `.pyi` files represent the complete pointer policy with
`PointerPolicy(...)`. The metadata records `nullable`, `transfer`,
`target_owner`, `lifetime`, `deallocation`, `shape_source`, `contiguity`,
`reassociation`, `aliasing`, and `mutability`. Supplying metadata does not
enable a transfer mode that the backend does not implement: borrowed views and
general pointer output/reassociation remain blocked. The required facts are
described in
`docs/wrapper_design_notes.md#fortran-allocatable-and-pointer-reassociation`;
they include nullability, transfer mode, owner/lifetime, shape source,
contiguity or stride rules, deallocation policy, reassociation behavior,
aliasing, and mutability.

- [x] Define temporary association for pointer `intent(in)` array arguments.
- [x] Define temporary association for pointer `intent(in)` scalar arguments.
- [x] Define snapshot-copy behavior for associated pointer array function
  results and `None` for unassociated results.
- [x] Define snapshot-copy behavior for associated scalar pointer function
  results and `None` for unassociated results.
- [x] Block pointer `intent(out)` and `intent(inout)` dummy arguments; preserve
  explicit pointer policy metadata without enabling unsupported reassociation
  lowering.
- [x] Preserve target, pointer, rank, bounds, contiguity, and association facts
  needed by pointer wrappers.
- [x] Add semantic `.pyi` policy metadata for nullable pointers, transfer mode,
  target owner, lifetime, deallocation, shape source, contiguity, reassociation,
  aliasing, and mutability.
- [x] Report precise readiness blockers when pointer policy metadata is missing
  or contradicts the native declaration.
- [x] Support associated and unassociated scalar pointer results.
- [x] Support associated and unassociated array pointer results.
- [ ] Keep native pointer targets alive while Python borrowed views reference
  them.
- [ ] Prevent Python from freeing borrowed native storage.
- [x] Detect or block dangling borrowed pointer results when lifetime cannot be
  proven; supported scalar and array pointer results are detached snapshots.
- [x] Test pointer `intent(in)` call-local association.
- [x] Test pointer scalar `intent(in)` call-local association.
- [x] Test pointer scalar result snapshot copies and unassociated `None`.
- [x] Test pointer array result snapshot copies and unassociated `None`.
- [x] Test blocked pointer `intent(out)` and `intent(inout)` arguments without
  explicit policy metadata.
- [x] Test the snapshot aliasing rule: two Python-visible pointer results for
  the same target are independent copies.
- [x] Test null association and snapshot survival after Python input-owner
  destruction.
- [ ] Test native pointer reassociation, native owner destruction, and target
  reallocation once borrowed views or reassociated outputs are supported.

## 8. Array-Valued Function Results

Current state: numeric array-valued function results are returned as
copy-return NumPy arrays. Explicit-shape and automatic-shape results are copied
from the temporary Fortran result into Python-owned C storage, and the NumPy
array owns that copied storage through a capsule base object. Allocatable array
function results use the same copy-return policy as allocatable output dummies:
allocated results, including zero-sized allocations, become Python-owned NumPy
arrays; unallocated results become `None`. Pointer array function results use
the section 7 snapshot policy: associated results are copied into Python-owned
NumPy arrays and unassociated results become `None`.

Example: `function spectrum(n) result(x); real :: x(n)` returns a new NumPy
array whose lifetime is independent of the Fortran temporary. Multidimensional
results preserve Fortran order. Arrays of derived types are not yet exposed
because their element layout, construction, and destruction policy are section
10 work.

Decision: array-valued function results are copy-return only. x2py does not
expose zero-copy borrowed views for function results because the native
temporary, allocatable result, or pointer association does not provide a stable
Python-visible lifetime. Numeric function result arrays are supported through
rank 15. Derived-type array results remain blocked with a precise diagnostic.

- [x] Support explicit-shape numeric array results.
- [x] Support automatic-shape numeric array results.
- [x] Support allocatable numeric array results.
- [x] Support pointer array results using the snapshot-copy policy from section
  7.
- [x] Support multidimensional Fortran-order results.
- [x] Preserve dtype, rank, bounds, and contiguity in the returned NumPy array.
- [x] Define copy versus zero-copy behavior for each result category.
- [x] Support arrays of derived types or report a precise blocker.
- [x] Test zero-sized results and every supported rank from 1 through 15.
- [x] Test result lifetime after temporary wrapper objects are destroyed.

## 9. Remaining Array Contracts

Current state: numeric explicit-shape, assumed-size, assumed-shape,
allocatable, pointer, and assumed-rank array contracts are supported only
within the settled subset below. Python supplies the storage and full extents
for assumed-size dummy arguments; the wrapper validates rank, dtype, layout,
writeability, native byte order, alignment, and every declared extent it can
express from integer literals, constants, and scalar argument names. The
omitted final assumed-size extent is not inferred from companion arguments;
callers must pass an array that is large enough for the native routine's
documented use.

The deterministic maximum supported rank is 15. Ranks above 15 are rejected
before wrapper generation. Rank 1 arrays may be any contiguous order when the
Fortran contract is contiguous. Rank greater than 1 arrays use Fortran order
unless the contract explicitly comes from a C-side interface.

`intent(in)` arrays may be read-only. `intent(out)` and `intent(inout)` arrays
must be writeable. x2py requires native-endian, aligned arrays and does not
perform implicit dtype casts or byte swaps. Overlapping Python-visible arrays
are not copied or de-aliased by the wrapper; calls are forwarded to Fortran and
the native aliasing rules and routine semantics apply.

Assumed-rank `dimension(..)` numeric dummy arguments are supported by a
generated rank-dispatch bridge for actual NumPy array ranks 1 through 15. The
bridge receives the runtime rank from the Python layer, selects a rank-specific
Fortran pointer view, and forwards that fixed-rank view to the native
procedure. When a procedure has multiple assumed-rank dummy arguments, the
bridge nests the rank dispatch so each dummy is viewed at its own runtime rank.
Rank 0 scalars are not accepted by the automatic `dimension(..)` policy.
Assumed-type `type(*)` descriptors remain blocked until dtype and layout are
supplied by a `.pyi` policy. Character arrays and derived-type arrays are also
blocked until their element ABI, layout, construction, and ownership policies
are defined.

Example: `a(n, m)` is straightforward when `n` and `m` are known arguments, but
`a(*)`, `dimension(..)`, non-default lower bounds, and rank greater than the
selected maximum need explicit Python-side validation rules.

Decision: numeric explicit-shape, assumed-size, assumed-shape, allocatable,
pointer, and assumed-rank dummy contracts are supported through rank 15 when
their extents can be validated by the wrapper contract. x2py validates inputs
and forwards the native call without implicit copying, de-aliasing, dtype
conversion, byte swapping, or alignment repair. Assumed-rank is implemented as
generated Fortran rank dispatch over NumPy array ranks 1 through 15.
Assumed-type, character arrays, and derived-type arrays remain blocked until
their descriptor, ABI, and element ownership policies are defined.

- [x] Test assumed-size arrays and define how their missing final extent is
  supplied.
- [x] Implement supported deferred-shape allocatable and pointer arrays, and
  block pointer replacement without explicit policy.
- [x] Implement assumed-rank `dimension(..)` for numeric NumPy array ranks 1
  through 15 with generated rank dispatch.
- [x] Implement assumed-type `type(*)` or emit a stable readiness blocker.
- [x] Preserve and validate non-default lower bounds.
- [x] Support zero-length dimensions.
- [x] Test every supported rank from 1 through 15.
- [x] Define a deterministic maximum rank and reject higher ranks early.
- [x] Support arrays of character values or emit a precise blocker.
- [x] Support arrays of derived types or emit a precise blocker.
- [x] Detect shape mismatches before entering Fortran.
- [x] Define overlapping input/output memory behavior.
- [x] Test read-only NumPy inputs for `intent(in)` and writable requirements for
  `intent(out/inout)`.
- [x] Test byte order, dtype mismatch, alignment, and unsafe cast failures.

## 10. Derived Types Across Procedure Boundaries

Current state: scalar derived-type values are supported across procedure
boundaries through the generated Fortran/C bridge. Python wrapper objects hold a
native derived-type instance pointer. Scalar `intent(in)` and `intent(inout)`
arguments are passed by reference to that native instance; `intent(inout)` may
mutate the existing Python object. Scalar `intent(out)` dummies are hidden from
the Python signature and returned as new wrapper objects. Scalar derived-type
function results are copied into new Python-owned wrapper objects.

Nested scalar derived-type components are exposed as borrowed child wrapper
objects. The child keeps its parent Python wrapper alive, so accessing a nested
component after the parent name is deleted remains valid for the child wrapper's
lifetime. Private components are omitted from Python get/set descriptors.
Allocatable components keep the section 6 borrowed-view policy. Pointer
components keep the section 7 pointer policy: snapshot copy when the wrapper
can prove association state, shape, dtype, nullability, contiguity, target
owner, and deallocation obligations, or a readiness blocker otherwise. A
returned Python-owned wrapper object owns the native derived-type instance
itself, but it does not automatically own targets reachable through pointer
components. Arrays of derived types remain explicitly deferred with the section
8/9 derived-type-array blocker.

Owned derived-type wrappers are destroyed by the generated Python object's
deallocation path, not by a public user-facing destroy method. That deallocation
path calls a generated Fortran-aware destroy helper for the wrapper-owned native
instance. The helper releases allocatable components and invokes Fortran
finalization. Borrowed child wrappers and borrowed field views keep the owning
wrapper alive and do not destroy native storage themselves. Pointer component
targets are not destroyed with the wrapper unless explicit pointer policy says
the containing object owns those targets and supplies the release behavior.

Example: `subroutine update(p)` with `type(particle), intent(inout) :: p`
should mutate the native instance behind the Python wrapper. Passing derived
types by value, returning new derived instances, nested components, and arrays
of derived types each need separate ownership and layout decisions; scalar
borrowed fields are simpler than replacement of whole objects.

- [x] Support scalar derived-type arguments for `intent(in)`.
- [x] Support scalar derived-type arguments for `intent(inout)`.
- [x] Support scalar derived-type output arguments and function results.
- [x] Support nested derived-type components.
- [x] Define copy versus reference behavior for each intent.
- [x] Preserve private component visibility.
- [x] Support allocatable components using the borrowed-view policy from
  section 6.
- [x] Apply the section 7 snapshot-or-block policy to pointer components.
- [x] Support arrays of derived types or explicitly defer them.
- [x] Prevent parent destruction while borrowed field views exist.
- [x] Test identity, mutation, copy, nested fields, and destruction order.

## 11. Inheritance And Polymorphism

Current state: supported Fortran extension types generate Python C-extension
inheritance for the static `extends(...)` hierarchy. The derived Python type
uses the base Python type as `tp_base`, so inherited base fields and methods are
visible on derived wrapper objects, and overridden type-bound procedures resolve
through the derived Python type.

This is static wrapper inheritance with a closed generated dispatch set for
scalar polymorphic input dummies. Type-bound passed-object arguments declared as
`class(self_type)` are accepted for concrete wrapped methods. A scalar
`class(base), intent(in)` argument is accepted by dispatching through the same
generated overload mechanism used for ordinary generic interfaces: the Python
wrapper checks the runtime wrapper class and selects a concrete bridge for the
base type or one of its known wrapped descendants. Polymorphic `intent(out)` and
`intent(inout)` arguments, polymorphic results, arrays, allocatable scalars, and
pointer scalars remain blocked until a dynamic-type, allocation, replacement,
and ownership policy defines how native dynamic type is preserved. `class(*)`
remains an assumed-type descriptor contract and is blocked with the same
explicit dtype/descriptor policy as `type(*)`. Abstract types and deferred
type-bound procedures report readiness blockers when those source facts are
available.

Example: `class(shape), intent(in) :: s` may receive a `shape`, `circle`, or
`box` wrapper at runtime when `circle` and `box` are known wrapped extension
types. The generated Python dispatcher orders concrete descendants before the
base class so a `circle` instance selects the `circle` bridge rather than the
more general `shape` bridge.

- [x] Generate Python inheritance for supported Fortran extension types.
- [x] Preserve base-component layout and initialization.
- [x] Dispatch scalar `class(base), intent(in)` arguments over the known wrapped
  base/descendant class set.
- [x] Block polymorphic results until an explicit ownership policy is supplied.
- [x] Define accepted dynamic types for allocatable polymorphic values as none
  until explicit policy metadata exists.
- [x] Report readiness blockers for abstract types instead of instantiating
  them.
- [x] Support deferred type-bound procedures or report readiness blockers.
- [x] Define behavior for overridden type-bound procedures.
- [x] Handle `class(*)` and `select type` contracts or reject them explicitly.
- [x] Test base calls, overridden calls, upcasting, invalid dynamic types, and
  object lifetime.

## 12. Constructors, Initialization, And Finalizers

Current state: generated Python classes allocate native Fortran storage through
the Fortran bridge, so component default initialization runs during native
allocation. For wrapped Fortran classes without a user-visible `__init__`, x2py
generates a keyword-only Python constructor for public rank-0 numeric, logical,
and complex components. Omitted keywords keep the native allocation state, which
includes Fortran default component initialization where present. Private
components, arrays, allocatables, pointers, character components, and derived
components are not constructor keywords yet.

Edited `.pyi` stubs control whether the generated keyword constructor remains
part of the Python surface. Removing the generated `__init__(self, *, ...)`
declaration suppresses the keyword constructor instead of recreating it during
wrapper generation. A class left without any `__init__` keeps only native
allocation and has no Python initializer arguments. To choose one concrete
native initializer, bind `__init__` directly with `@bind("specific_name")`. The
target must be another method declared in the same class with the same
Python-call signature and return type. Public targets expose both the target
method and construction; `@private` targets expose only construction. Private
targets remain in the `.pyi` because the `.pyi` is a standalone wrapper input
and must carry the native initializer signature even when Python users cannot
call that initializer directly. The target keeps the native class argument,
while the Python constructor declaration omits that argument because Python
supplies the newly allocated instance. Constructor overload declarations still
load and round-trip only beside the generated field constructor, but overloaded
`tp_init` runtime lowering is not implemented yet and code generation reports an
explicit blocker.

Private visibility has two sources in this contract. Ordinary declarations that
are private in the Fortran source are omitted from generated `.pyi` files;
private overload specifics may remain only when required to resolve a public
overload from the standalone `.pyi`. A `@private` decorator or `private[...]`
annotation in an edited `.pyi` is a user-imposed wrapper contract on an
otherwise public declaration, so it remains printed and loadable.

Example: a type with default field values and `final :: cleanup` should produce
a Python object whose native storage is initialized exactly once and finalized
exactly once. Failed `tp_init` calls still deallocate the native instance that
was allocated by `tp_new`, so Fortran finalization also runs exactly once for
failed construction attempts. Borrowed child wrappers are marked as aliases;
their deallocator releases only the Python wrapper and parent reference, while
the owning parent remains responsible for finalizing the native component.

Generic interfaces whose name collides with a derived type are recognized as
Fortran constructor interfaces but are not mapped to Python construction yet.
They produce the `fortran_generic_constructor_unsupported` readiness blocker
instead of silently replacing the generated keyword constructor or creating a
duplicate Python symbol.

Fortran final subroutines have no status return through which `tp_dealloc` can
report failure. Finalizers must complete normally. A finalizer that executes
`stop`, `error stop`, aborts, or otherwise terminates native execution terminates
the process; Python exception recovery is not attempted from `tp_dealloc`.

- [x] Preserve default component initialization expressions.
- [x] Define the generated default Python constructor signature.
- [x] Map supported generic constructor interfaces to Python construction or
  report an explicit readiness blocker when no safe mapping exists.
- [x] Define keyword initialization for public components.
- [x] Preserve and resolve `final` procedure metadata instead of discarding it.
- [x] Invoke final procedures exactly once for owned native instances.
- [x] Do not finalize borrowed instances.
- [x] Define behavior when a finalizer fails or terminates execution.
- [x] Test default initialization, custom construction, partial construction,
  garbage collection, and repeated deletion.

## 13. Module Variables And Constants

Current state: module variables reach semantic IR. Public scalar numeric,
logical, and complex module variables are exposed through explicit typed
`get_<name>()` and `set_<name>(value)` functions, so mutation writes through to
the native Fortran module storage and is visible to later wrapped calls.
Target-backed allocatable module arrays are exposed through explicit getters as
borrowed zero-copy NumPy views with `None` for unallocated storage. Native
module storage remains owned by the Fortran module for the process lifetime.
Public `parameter` values are emitted as `Final[...]` constants with literal
values when the source expression can be preserved as a Python literal; no
setter is generated for parameters. Private variables are omitted from the
generated module and receive no accessors.

Example: `real(c_double), allocatable, target :: values(:)` is exposed as
`get_values() -> ndarray | None`; users call wrapped Fortran allocation and
deallocation routines explicitly. Existing views are borrowed and are not
tracked: if Fortran reallocates or deallocates `values`, a previous NumPy view
may dangle, so callers must copy when they need independent lifetime. Scalar
module variables are a separate path: they use explicit getter/setter functions
unless they are `parameter`, in which case they become Python constants in the
generated module namespace. Python's normal module attribute rebinding is not
intercepted, so direct assignment such as `mod.nmax = 3` can shadow the exported
constant name in Python but does not modify native Fortran storage.

All generated Python calls execute while holding the CPython GIL; x2py does not
add a separate lock around Fortran module state. This serializes ordinary calls
from Python threads in one interpreter, but it does not protect against native
threads, callbacks, external libraries, or other code that accesses the same
Fortran globals. Applications that have such concurrent access must synchronize
it outside the generated wrapper.

Module variables have module lifetime in Fortran whether their `save` attribute
is implicit or explicit, so public scalar and allocatable module variables use
the same exposure rules. Procedure-local `save` variables remain internal to
their procedure and are never exported as module variables. Common blocks stay
entirely inside the native Fortran implementation. Wrapped procedures may read
or write them normally, but variables associated with a common block are not
exported as Python module variables. x2py does not model, copy, own, or shim
common-block storage.

- [x] Expose public scalar module variables with typed getters and setters.
- [x] Expose public allocatable module arrays with explicit copy/view and
  lifetime policy.
- [x] Expose parameters as read-only Python constants.
- [x] Prevent native writes to parameters and private variables; parameters
  have no setter and private variables are not exported.
- [x] Support allocatable module variables using section 6 ownership rules.
- [x] Support pointer module variables using section 7 ownership rules by
  snapshotting only with complete explicit policy and blocking otherwise.
- [x] Define synchronization and thread-safety expectations for global state.
- [x] Define whether `save` variables are exposed or remain procedure-internal.
- [x] Decide whether common blocks are supported, shimmed, or explicitly
  rejected.
- [x] Test mutation visibility across Python calls and multiple module objects.

## 14. Fortran Enums

Current state: `enum, bind(C)` syntax is validated and enumerator metadata is
preserved as ordinary integer constants. Enums are not exposed as semantic
datatypes and do not generate Python `Enum` or `IntEnum` classes.

Example: `enum, bind(C); enumerator :: red = 1, blue; end enum` should preserve
explicit and implicit integer values and emit:

```python
red: Final[Int32] = 1
blue: Final[Int32] = 2
```

The same integer-constant policy applies to C enums. C enum tags may be kept as
metadata for documentation, but arguments, returns, fields, and variables use
the underlying integer type.

- [x] Add parser models for enum blocks and enumerators.
- [x] Preserve explicit and implicit enumerator values.
- [x] Convert Fortran enums to ordinary semantic integer constants.
- [x] Emit `.pyi` `Final[...]` integer constants for enumerators.
- [x] Document that Python `Enum` and `IntEnum` classes are not generated.
- [x] Keep enum arguments, returns, and fields as ordinary integer types.
- [x] Preserve `bind(C)` underlying representation as integer metadata.
- [x] Test explicit values, implicit increments, negative values, and round trips.

## 15. Character Edge Cases

Current state: common scalar character arguments and results work. Scalar
`intent(out)` characters are hidden outputs, and scalar `intent(inout)`
characters use replacement projection because Python `str` is immutable.
Optional scalar character arguments follow the normal optional omission rules.
Character arrays and mutable allocatable character dummy arguments remain
blocked with precise readiness diagnostics.

Example: `character(len=8), intent(inout) :: name` can truncate, pad, and mutate
in place, while `character(len=:), allocatable` needs allocation ownership.
Decisions resolved for scalar default-character, `kind=1`, and `c_char` paths:
Python `str` is the public type; CPython UTF-8 bytes are used at the ABI
boundary; fixed-length dummies truncate input bytes to the declared length and
pad shorter inputs with blanks; returned fixed-length values include the full
post-call Fortran buffer, including trailing blanks. Assumed-length
`intent(inout)` dummies use the encoded input byte length. Python input with an
embedded NUL byte is rejected before the native call because the public result
path uses a NUL-terminated C string. Character arrays and mutable allocatable
character dummy arguments are not silently exposed.

- [x] Support `intent(out)` scalar character arguments.
- [x] Support `intent(inout)` scalar character arguments.
- [x] Support optional character arguments.
- [x] Reject mutable allocatable character dummy arguments with a precise
  blocker.
- [x] Emit a precise blocker for character arrays.
- [x] Define truncation and padding behavior for fixed lengths.
- [x] Define embedded NUL handling for Fortran and `c_char` strings.
- [x] Define encoding for default character and non-ASCII text.
- [x] Support default, `kind=1`, and `c_char` character kinds; reject other
  character kinds explicitly.
- [x] Validate hidden-length ABI behavior through generated `bind(C)` shims
  instead of exposing compiler-specific hidden length arguments directly.
- [x] Test empty strings, exact length, truncation, padding, Unicode, embedded
  NUL, and mutable outputs.

## 16. Scalar Types And Kind Coverage

Current state: runtime wrapper coverage includes signed integer storage
corresponding to 8, 16, 32, and 64 bits; default logical results and one-byte
logical storage such as `logical(c_bool)` and compiler-confirmed `logical*1`
arrays; real storage corresponding to 32 and 64 bits; and complex storage
corresponding to 64 and 128 bits. `iso_fortran_env` names such as `int8`,
`int16`, `int32`, `int64`, `real32`, and `real64`, and common
`iso_c_binding` scalar names such as `c_int32_t`, `c_float`, `c_double`,
`c_float_complex`, and `c_double_complex`, are resolved through compiler
probing during wrapper builds.

Example: `integer(kind=selected_int_kind(18))` may be 64-bit on one compiler and
unavailable or different elsewhere. Straightforward cases are common C
interoperable kinds; the riskier path uses compiler probing so kind numbers do
not get mistaken for byte sizes. Unsupported target mappings fail during
semantic lowering before wrapper compilation.

Real storage wider than 64 bits is blocked for wrappers. Complex storage wider
than 128 bits is also blocked. x2py does not down-convert those values because
doing so would silently lose precision and would not preserve NumPy dtype
round-trip behavior. Logical storage is supported through default logical
results and the direct one-byte Boolean ABI path used by `logical(c_bool)` and
compiler-confirmed `logical*1`; wider explicit logical kinds are blocked
because they do not have a portable Python/NumPy bool round-trip contract.

- [x] Test signed integer kinds corresponding to 8, 16, 32, and 64 bits.
- [x] Test logical arguments, results, and arrays for supported storage sizes.
- [x] Test real kinds corresponding to 32 and 64 bits.
- [x] Decide whether real 80/128-bit values are supported, converted, or
  blocked.
- [x] Test complex kinds corresponding to 64 and 128 bits.
- [x] Decide whether complex 160/256-bit values are supported, converted, or
  blocked.
- [x] Test `iso_fortran_env` named kinds.
- [x] Test `iso_c_binding` named kinds.
- [x] Use compiler probing when kind numbers do not imply portable storage.
- [x] Reject unsupported target mappings before wrapper compilation.
- [x] Test scalar and array round trips at min/max, NaN, infinity, and complex
  edge values.

## 17. Derived-Type Layout And Interoperability

Current state: all wrapped Fortran derived types, including `bind(C)` and
`sequence` types, use the same opaque native-instance representation. Python
field reads and writes always call generated Fortran accessors. The generated C
layer never declares a matching C struct, computes a component offset, or
exposes a direct structured-memory view, so it makes no padding or alignment
assumptions.

The parser and semantic IR preserve `bind(C)` and `sequence` attributes,
component declaration order, and each component's existing source type, kind,
rank, shape, and storage facts. Semantic class metadata records the current
`accessors` layout policy. A `bind(C)` procedure that takes an interoperable
derived type, including a `value` argument, is still routed through the
generated Fortran bridge: C passes an opaque instance pointer to the bridge and
the Fortran compiler performs any required value copy when the bridge calls the
original procedure. Non-`bind(C)` derived types in a `bind(C)` procedure are
rejected before code generation with a derived-type ABI diagnostic.

Direct C layout access is not enabled, even for interoperable types. A future
optimization may use compiler-validated size, alignment, padding, component
offset, and nested-layout facts to expose direct memory views for interoperable
`bind(C)` types. That optimization must be explicit and must fall back to the
accessor path whenever validation is unavailable.

- [x] Preserve `bind(C)` and `sequence` type attributes in semantic IR.
- [x] Preserve component declaration order and interoperable component facts.
- [x] Define when direct C layout access is allowed.
- [x] Use generated accessors when direct layout cannot be proven.
- [x] Support interoperable `bind(C)` types passed by value where ABI-safe.
- [x] Block non-interoperable by-value transfers with a precise diagnostic.
- [x] Define padding, alignment, and compiler-layout validation policy.
- [x] Test nested interoperable types and mixed scalar fields.
- [x] Test layout behavior through the configured compiler/platform test path.

## 18. Multiple Files, Modules, And Submodules

Current state: runtime wrapper builds accept one or more user-supplied Fortran
source paths and produce one Python extension module/shared library. x2py does
not discover missing source files, infer a dependency graph, or reorder the
project: callers must pass every source needed by the wrapped API in a compiler
valid order. The build compiles each supplied source to an object, links all
objects into the generated extension, and emits one generated Fortran
`bind(C)` bridge that imports each wrapped Fortran module and contains the C ABI
procedures for the merged Python surface. The first generated semantic module
sets the Python extension name; later modules and standalone procedures are
merged into that extension.

Example: module `solver` may `use mesh, only: grid`, and a submodule may
implement procedures declared in the parent module. The user passes the mesh
source, parent module source, and submodule source in the same invocation. If
the compiler can compile those files in that order, x2py builds a single
importable extension from them. Standalone external procedures from multiple
files are merged into the same extension surface, which supports BLAS-style
source sets where routines are spread across many files but should be imported
from one generated Python module.

Generated semantic `.pyi` files remain module-based, not file-based. A source
file that defines two Fortran modules writes two `.pyi` files when `--pyi --out`
is used without an explicit filename. An explicit `--out api.pyi` remains an
aggregate override for callers that intentionally want a single stub file.

Passing `--makefile` writes `Makefile.x2py` beside the generated wrapper sources
without compiling native objects or the extension. Its rules cover every source
compile, generated-wrapper compile, runtime-support compile, and shared-library
link command prepared by x2py. The Makefile records the resolved compiler
executables and working directory, and exposes `FC`, `CC`, `X2PY_LD`,
`X2PY_FFLAGS`, `X2PY_CFLAGS`, and `X2PY_LDFLAGS` so users can edit or override
compilers and performance flags. Extra compile flags are placed after x2py's
defaults, so a later option such as `-O3` overrides the default optimization
level. User Fortran sources are conservatively chained in supplied order because
x2py does not infer their dependency graph; generated C/runtime work remains
available to `make -j`. This output targets GNU Make and a POSIX shell and is not
the portable native-Windows build path. Separately, `--verbose` performs the
direct build and prints each exact shell-escaped command as it runs.
`--makefile` and `--verbose` are mutually exclusive.

- [x] Accept multiple source files in one wrapper build.
- [x] Define one-extension packaging for a multi-source wrapper invocation.
- [x] Support standalone external procedures alongside modules.
- [x] Compile supplied sources in caller-provided order and link all source
  objects into the extension.
- [x] Generate one Fortran `bind(C)` bridge module that imports wrapped modules
  and merges their C ABI wrappers.
- [x] Generate one `.pyi` file per Fortran module for implicit `--pyi --out`
  writes, including multiple modules from one source file.
- [x] Document that source discovery, dependency ordering, and incremental
  dependency graph construction are caller/build-system responsibilities.
- [x] Test multi-file wrapper builds for module procedures and standalone
  external procedures.
- [x] Emit an editable Makefile that reproduces the complete native build and
  exposes compiler and extra-flag overrides.
- [x] Keep exact-command verbose compilation and Makefile generation as
  separate, mutually exclusive modes.
- [ ] Resolve renamed/`only` import collisions across wrapped modules.
- [ ] Wrap submodule and separate-module procedures as additional public API.
- [ ] Accept prebuilt module and library search paths in wrapper compilation.

## 19. Visibility, Naming, And Python Surface

Current state: public wrapper names follow the policy in
`docs/fortran_wrapper_naming_policy.md`. Public Fortran identifiers are
case-normalized to lowercase for Python, Python keywords are escaped with a
trailing underscore, invalid identifier characters are replaced with
underscores, and remaining public-name collisions are fixed by appending a
deterministic numeric suffix. Passing `--strict-wrapper-names` disables those
fixes and turns any name that needs escaping, or any collision after
normalization, into a deterministic generation error before native compilation.

Example: Fortran names `class`, `Class`, and `class_` can collide after Python
normalization or keyword escaping. In default mode the wrapper exposes the first
as `class_` and fixes later collisions with suffixes such as `class__2`; strict
mode rejects the same surface instead of guessing. `bind(C, name=...)` preserves
the native ABI symbol but never changes the Python API name by itself.

- [x] Export only public Fortran procedures, types, bindings, and variables.
- [x] Preserve private type-bound procedures as non-public implementation
  details.
- [x] Handle Fortran case-insensitive collisions deterministically.
- [x] Handle Python keywords and invalid Python identifiers.
- [x] Handle generic names colliding with concrete procedure names.
- [x] Handle module, type, field, and method names that collide after Python
  normalization.
- [x] Preserve `bind(C, name=...)` native names without changing the Python API
  unintentionally.
- [x] Define and document any name-mangling policy.
- [x] Test collisions, private symbols, renamed imports, and error messages.

## 20. Dummy Procedures, Procedure Pointers, And Callbacks

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

## Remaining sections

20. Dummy procedures, procedure pointers, and callbacks.
21. Runtime errors, concurrency, and portability.

When a section is completed, replace only its verified boxes with `[x]` and
link the section to the runtime tests that prove the behavior.
