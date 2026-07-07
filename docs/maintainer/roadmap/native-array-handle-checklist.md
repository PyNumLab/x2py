---
title: Native Array Handle Checklist
audience: maintainers
prerequisites: semantic .pyi format, ownership policy, allocatables, pointers
related: index.md, ../../user/reference/semantic-pyi-format.md, ../../user/guide/allocatables.md, ../../user/guide/pointers.md
status: active-roadmap
---

# Native Array Handle Checklist

This is the implementation and verification checklist for native Fortran array
descriptor handles:

- `Allocatable[T[...]]`
- `Pointer[T[...]]`

Use this page as the canonical checklist for this feature. The original prompts
are consolidated here; future implementation should use this page instead of
re-reading those prompts.

The intended implementation is one shared native-array handle path with
descriptor-specific operations layered on top. Keep Allocatable and Pointer as
separate public contract types, but do not build two unrelated parser, policy,
runtime, bridge, or binding stacks.

Scalar allocatable and pointer procedure projections are not part of this array
handle work. Scalars continue to use ordinary nullable Python values plus
`@native_call` descriptor projections such as `Allocatable(Arg(i))`,
`Pointer(Arg(i))`, `Allocatable(Return(...))`, and `Pointer(Return(...))`.

## Core Contract Decisions

- [ ] `Allocatable[T[...]]` means a Python handle to a native allocatable array
  descriptor.
- [ ] `Pointer[T[...]]` means a Python handle to a native pointer array
  descriptor.
- [ ] `Allocatable[T[...]]` and `Pointer[T[...]]` are handles, not NumPy arrays.
- [ ] `T[...]` remains the ordinary array data-buffer contract.
- [ ] Passing a handle to an `Allocatable[T[...]]` or `Pointer[T[...]]`
  parameter uses descriptor semantics.
- [ ] Passing a handle to a `T[...]` parameter uses normal array-actual
  semantics. For native wrapper calls, prefer passing the handle's native array
  actual to the normal Fortran array dummy instead of implicitly calling
  `.to_numpy()`.
- [ ] Normal `T[...]` parameters require a valid array actual: allocatable
  handles must be allocated, pointer handles must be associated, and
  allocated/associated zero-length arrays remain valid.
- [ ] Unallocated allocatable handles and unassociated pointer handles are
  accepted only by descriptor-handle parameters such as `Allocatable[T[...]]`
  and `Pointer[T[...]]`, where that state belongs inside the handle.
- [ ] Plain NumPy arrays are rejected for `Allocatable[T[...]]` and
  `Pointer[T[...]]` descriptor parameters.
- [ ] `| None` on a handle means the handle object itself may be absent, such
  as for a native optional dummy.
- [ ] Unallocated allocatable state lives inside the allocatable handle:
  `h.allocated is False` and `h.to_numpy() is None`.
- [ ] Unassociated pointer state lives inside the pointer handle:
  `p.associated is False` and `p.to_numpy() is None`.
- [ ] `Annotated[T[...], Allocatable]` is not an active public allocatable-array
  spelling after migration.
- [ ] `Annotated[T[...], Pointer]` is not an active public pointer-array
  spelling after migration.
- [ ] `Snapshot[T]` is removed from generated and accepted active semantic
  `.pyi` contracts for this feature.
- [ ] Whole-object snapshots are treated as a future feature, not part of this
  contract.
- [ ] Borrowed views, detached snapshots, and descriptor handles remain distinct
  concepts in docs, diagnostics, runtime names, and tests.

## Public `.pyi` Examples

### Allocatable Handles

```python
from x2py.contracts import Allocatable, Float64, Int32

values: Allocatable[Float64[:]]

class box:
    values: Allocatable[Float64[:]]

def resize(values: Allocatable[Float64[:]], n: Int32) -> None: ...

def make_values(n: Int32) -> Allocatable[Float64[:]]: ...

def maybe_optional(
    values: Allocatable[Float64[:]] | None = ...,
) -> None: ...

def scale(values: Float64[:]) -> None: ...
```

`scale()` is ordinary array-data semantics. It may accept an allocated
`Allocatable[Float64[:]]` at runtime by passing the handle's native array actual
to the normal Fortran array dummy. It does not receive an allocatable dummy
descriptor.

### Pointer Handles

```python
from x2py.contracts import Float64, Int32, Pointer

values: Pointer[Float64[:]]

class box:
    values: Pointer[Float64[:]]

def reassociate(
    values: Pointer[Float64[:]],
    target: Pointer[Float64[:]],
) -> None: ...

def maybe_optional(
    values: Pointer[Float64[:]] | None = ...,
) -> None: ...

def scale(values: Float64[:]) -> None: ...
```

`scale()` is ordinary array-data semantics. It may accept an associated
`Pointer[Float64[:]]` at runtime by passing the handle's native array actual to
the normal Fortran array dummy. It does not receive a pointer dummy descriptor.

## Call Compatibility Model

For a normal array data signature:

```python
from x2py.contracts import Allocatable, Float64, Pointer

def f(x: Float64[:]) -> None: ...

plain: Float64[:]
allocatable: Allocatable[Float64[:]]
pointer: Pointer[Float64[:]]

f(plain)
f(allocatable)
f(pointer)
```

all three calls are valid when the runtime value can provide usable
`Float64[:]` data:

- `f(plain)` passes the NumPy/data-buffer value directly;
- `f(allocatable)` verifies that the handle is allocated and compatible, then
  passes the wrapped native allocatable array actual to the normal Fortran array
  dummy;
- `f(pointer)` verifies that the handle is associated and compatible, then
  passes the wrapped native pointer array actual to the normal Fortran array
  dummy.

This mirrors Fortran argument association: a non-allocatable array dummy can be
called with ordinary, allocatable, or pointer actual arrays when the actual
array is present/associated and otherwise valid. At the Python boundary this is
not allocatable-or-pointer dummy descriptor semantics; the callee sees a normal
array dummy. It also is not an implicit `.to_numpy()` conversion.

If the user writes `f(allocatable.to_numpy())` or `f(pointer.to_numpy())`, that
is the explicit public extraction path. The result is treated like any other
ordinary array argument and must pass the normal validation rules, including
non-`None` state and any mutability requirements.

For descriptor signatures:

```python
def g(x: Allocatable[Float64[:]]) -> None: ...

def h(x: Pointer[Float64[:]]) -> None: ...
```

`g()` requires an allocatable handle and `h()` requires a pointer handle. A
plain NumPy array is rejected because it has no native allocatable or pointer
descriptor to pass.

Internally, model this as a handle with an array-data facet plus descriptor
facts, not as a global rewrite of the base array type. For example, an
`Allocatable[Float64[:]]` value should expose or carry:

- array data type: `Float64[:]`;
- descriptor kind: `allocatable`;
- descriptor operations: allocation state, descriptor passing, deallocate, and
  resize.

A `Pointer[Float64[:]]` value should expose or carry:

- array data type: `Float64[:]`;
- descriptor kind: `pointer`;
- descriptor operations: association state, descriptor passing, nullify, and
  any policy-gated allocation/deallocation operations.

The implementation may use predicates or metadata equivalent to
`is_allocatable` and `is_pointer` on the specific handle semantic type, but
plain `Float64[:]` itself remains the data-buffer contract. Do not make a
normal array parameter infer descriptor semantics merely because a handle is
accepted as an array-like runtime value.

## Recommended Implementation Order

### 1. Documentation And Contract Sync

Update the public docs first so the intended behavior is explicit before code
changes.

- [ ] Update `docs/user/guide/allocatables.md`.
- [ ] Update `docs/user/guide/pointers.md`.
- [ ] Update `docs/user/reference/semantic-pyi-format.md`.
- [ ] Update memory-management or language-support pages if they describe
  allocatable or pointer arrays as NumPy arrays, `ndarray | None`, metadata
  annotations, or `Snapshot[T]`.
- [ ] Document that `Allocatable[T[...]]` is a handle, not an ndarray.
- [ ] Document that `Pointer[T[...]]` is a handle to pointer association state,
  not an ndarray.
- [ ] Document that `h.to_numpy()` returns a borrowed view, read-only detached
  copy, or `None` depending on completed policy and current allocation state.
- [ ] Document that `p.to_numpy()` returns the current target view or `None`,
  and can expose strided pointer targets when descriptor support is available.
- [ ] Document that passing a handle to a handle parameter is descriptor
  passing, while passing a handle to `T[...]` uses normal array-actual
  semantics through the handle's native array-data facet.
- [ ] Document call compatibility for `def f(x: T[...])`: ordinary arrays,
  allocated allocatable handles, and associated pointer handles are accepted
  as array actuals without implicit `.to_numpy()` conversion.
- [ ] Document that normal `T[...]` parameters reject unallocated allocatable
  handles and unassociated pointer handles because there is no valid array
  actual to pass. Allocated or associated zero-length arrays are still valid.
- [ ] Document that explicit `f(h.to_numpy())` is a separate user-requested
  ndarray path and follows ordinary ndarray validation.
- [ ] Document that parameters annotated as `Allocatable[T[...]]` or
  `Pointer[T[...]]` pass native descriptors, so they require the corresponding
  handle object. Ordinary arrays are accepted only by normal `T[...]`
  parameters.
- [ ] Document that plain ndarray inputs are rejected for descriptor-handle
  parameters.
- [ ] Document that module allocatables and pointer arrays expose handles, not
  `ndarray | None` module attributes.
- [ ] Document that derived allocatable and pointer fields expose handles.
- [ ] Document that allocatable function results can return owned handles only
  when x2py creates stable owner storage.
- [ ] Document that pointer handles do not imply target ownership.
- [ ] Document that pointer `nullify()` is default, while pointer
  `allocate()`, `deallocate()`, and `resize()` require explicit policy.
- [ ] Document stale-view hazards after descriptor-changing operations,
  reassociation, nullification, deallocation, or reallocation.
- [ ] Remove active public examples of `Annotated[T[...], Allocatable]`,
  `Annotated[T[...], Pointer]`, and `Snapshot[T]` for this feature.

### 2. Public Contract Symbols, Parser, And Printer

Implement the public contract wrappers once and parameterize by descriptor kind.

- [ ] Add `Allocatable[...]` as a real array-handle contract wrapper.
- [ ] Add `Pointer[...]` as a real array-handle contract wrapper.
- [ ] Parse `Allocatable[T[...]]` into a semantic representation for a native
  allocatable array handle.
- [ ] Parse `Pointer[T[...]]` into a semantic representation for a native
  pointer array handle.
- [ ] Parse optional absent handles as `Allocatable[T[...]] | None = ...` and
  `Pointer[T[...]] | None = ...`.
- [ ] Preserve normal `T[...]` type identity as array data semantics, not
  descriptor semantics.
- [ ] Reject `Snapshot[T]` in active `.pyi` contracts with a clear diagnostic.
- [ ] Remove `Snapshot` from `x2py.contracts` and `CONTRACT_SYMBOLS` once
  active tests and docs are migrated.
- [ ] Reject or fully migrate `Annotated[T[...], Allocatable]` from active
  public contracts.
- [ ] Reject or fully migrate `Annotated[T[...], Pointer]` from active public
  contracts.
- [ ] Keep metadata-only allocatable or pointer facts only as temporary internal
  migration facts, not as accepted public syntax.
- [ ] Print generated module allocatables as `Allocatable[T[...]]`.
- [ ] Print generated derived allocatable fields as `Allocatable[T[...]]`.
- [ ] Print allocatable descriptor arguments and supported handle results as
  `Allocatable[T[...]]`.
- [ ] Print generated module pointer arrays as `Pointer[T[...]]`.
- [ ] Print generated derived pointer fields as `Pointer[T[...]]`.
- [ ] Print pointer descriptor arguments and supported handle results as
  `Pointer[T[...]]`.

### 3. Semantic IR Representation

Create one semantic representation family for native array handles with a
descriptor-kind field rather than separate unrelated models.

- [ ] Represent common native-array handle facts:
  - descriptor kind: allocatable or pointer;
  - element semantic type;
  - dtype;
  - rank;
  - shape metadata when statically known;
  - array data type/facet used when a handle is passed to a normal `T[...]`
    parameter;
  - string element length metadata when applicable;
  - optional-absent handle state;
  - source origin: module variable, derived field, argument, or result;
  - native access path.
- [ ] Keep handle semantic types distinct from normal array semantic types.
- [ ] Store allocatable/pointer descriptor facts on the handle semantic type,
  not as a global mutation of the plain array type.
- [ ] Permit shared predicates or metadata equivalent to `is_allocatable` and
  `is_pointer` on handle semantic types when that helps policy dispatch.
- [ ] Keep each handle's base array data type available for ordinary `T[...]`
  call compatibility.
- [ ] Keep scalar descriptor projection metadata on the existing scalar
  nullable-value path, not on array handle types.
- [ ] Preserve `T[...]` arguments/results as normal array data in semantic IR
  even when runtime may later accept a handle through data coercion.
- [ ] Model `Snapshot[T]` as unsupported or future-only rather than active
  semantic IR.

### 4. Post-IR Policy Completion

Complete every semantic decision before `ir2ast.py`. Bridge and binding
generators must dispatch from these decisions rather than inferring policy from
datatype, intent, origin, dotted access shape, alias metadata, or local memory
checks.

- [ ] Add one completed native-array-handle policy decision shared by
  Allocatable and Pointer.
- [ ] Complete descriptor kind before lowering: allocatable or pointer.
- [ ] Complete handle kind before lowering:
  - `borrowed_module_descriptor`;
  - `borrowed_field_descriptor`;
  - `argument_descriptor`;
  - `owned_result_descriptor`;
  - `optional_absent_handle`;
  - `unsupported`.
- [ ] Complete ownership and lifetime retention before lowering.
- [ ] Complete whether the Python handle is borrowed or owned before lowering.
- [ ] Complete getter behavior before lowering.
- [ ] Complete Python setter exposure, if any, before lowering.
- [ ] Complete native setter assignment behavior, if any, before lowering.
- [ ] Complete output projection/readback behavior before lowering.
- [ ] Complete release responsibility and generated destroy behavior before
  lowering.
- [ ] Complete `.to_numpy()` policy before lowering:
  - `borrowed_view`;
  - `descriptor_view`;
  - `contiguous_view`;
  - `copy_only`;
  - `read_only_detached_copy`;
  - `unsupported`.
- [ ] Complete nullability and optional-absent-handle behavior before lowering.
- [ ] Complete contract-value storage mode before lowering: `stack`, `heap`, or
  `alias`.
- [ ] Fail readiness with a clear diagnostic when descriptor ownership, target
  lifetime, shape, addressability, release responsibility, or extraction policy
  is incomplete.

#### Allocatable Policy Items

- [ ] Complete allocated-state support.
- [ ] Complete addressability/aliasability policy for `h.to_numpy()`.
- [ ] Use `borrowed_view` only when safe and legal addressability is proven.
- [ ] Use read-only detached copy when live aliasing is not safe.
- [ ] Do not expose live NumPy views for non-addressable Fortran allocatables.
- [ ] Do not call a read-only borrowed view a snapshot; snapshots are detached
  copies.
- [ ] Complete `deallocate()` permission.
- [ ] Complete `resize(shape)` permission.
- [ ] Complete function-result ownership as wrapper-owned stable descriptor
  storage.
- [ ] Mark unsupported allocatable array forms as readiness blockers rather than
  silently falling back to NumPy-array copy behavior.

#### Pointer Policy Items

- [ ] Complete association-state support.
- [ ] Complete target lifetime policy.
- [ ] Complete `to_numpy()` extraction policy:
  - descriptor view;
  - contiguous view;
  - copy-only fallback if explicitly implemented;
  - unsupported.
- [ ] Complete `nullify()` permission as the default pointer descriptor
  operation.
- [ ] Complete `allocate(shape)` permission only when explicit pointer policy
  allows allocation through this pointer.
- [ ] Complete `deallocate()` permission only when explicit pointer policy
  allows deallocation through this pointer.
- [ ] Complete `resize(shape)` permission only when explicit pointer policy
  allows resize through this pointer.
- [ ] Do not expose pointer `allocate()`, `deallocate()`, or `resize()` when
  policy disallows those operations.
- [ ] Treat pointer handle ownership as descriptor/association access by
  default, not target ownership.
- [ ] For pointer results, support `owned_result_descriptor` only when stable
  owner storage and target lifetime are explicit; otherwise block readiness.

### 5. Shared Runtime Handle Foundation

Add or reuse one internal runtime base for both public handle classes.

- [ ] Implement or reuse `NativeArrayHandleBase`.
- [ ] Put shared dtype metadata on the base.
- [ ] Put shared rank metadata on the base.
- [ ] Put shared shape-query dispatch on the base.
- [ ] Put shared `to_numpy()` dispatch on the base.
- [ ] Put shared owner/lifetime retention on the base.
- [ ] Put shared generated ops table/accessor storage on the base.
- [ ] Put shared borrowed-vs-owned descriptor kind on the base.
- [ ] Leave room for optional generation or stale-view tracking later.
- [ ] Implement `AllocatableHandle` as a descriptor-specific subclass.
- [ ] Implement `PointerHandle` as a descriptor-specific subclass.

#### Allocatable Runtime API

- [ ] `h.allocated -> bool`
- [ ] `h.shape -> tuple[int, ...] | None`
- [ ] `h.to_numpy() -> ndarray | None`
- [ ] `h.deallocate()`
- [ ] `h.resize(shape)`
- [ ] `h.to_numpy()` returns `None` when unallocated.
- [ ] `h.to_numpy()` returns a live mutable borrowed view when
  addressability/aliasability policy proves it safe.
- [ ] `h.to_numpy()` returns a read-only detached NumPy snapshot when live
  aliasing is not safe.
- [ ] Users can call `.copy()` on the returned NumPy array when they need
  independent lifetime.

#### Pointer Runtime API

- [ ] `p.associated -> bool`
- [ ] `p.shape -> tuple[int, ...] | None`
- [ ] `p.to_numpy() -> ndarray | None`
- [ ] `p.nullify()`
- [ ] Optional, policy-gated `p.allocate(shape)`
- [ ] Optional, policy-gated `p.deallocate()`
- [ ] Optional, policy-gated `p.resize(shape)`
- [ ] `p.to_numpy()` returns `None` when unassociated.
- [ ] `p.to_numpy()` returns a live borrowed NumPy view when associated and
  descriptor extraction is supported.
- [ ] `p.to_numpy()` supports strided views when descriptor support is
  available.
- [ ] `p.to_numpy()` raises a clear error when descriptor extraction is
  unavailable and no fallback is supported.
- [ ] Old borrowed views are documented as stale after native code nullifies,
  reassociates, deallocates, or otherwise changes the pointer target.

### 6. IR-to-AST And Codegen Model

Lower only completed policy decisions into named implementation methods.

- [ ] Add codegen model nodes or metadata for native-array handle creation.
- [ ] Add codegen model nodes or metadata for generated native-array handle ops.
- [ ] Route Allocatable and Pointer handles through the same lowering path with
  descriptor-kind-specific operations.
- [ ] Keep `@native_call Addr(Arg(i))` as data-address projection only.
- [ ] Select descriptor passing from `Allocatable[T[...]]` or
  `Pointer[T[...]]` plus completed policy, not from `Addr`.
- [ ] Lower unsupported policy decisions to readiness/codegen blockers, not
  fallback behavior.

### 7. Bridge Generation

Generate descriptor-access routines through the shared handle-ops shape, then
specialize operation bodies by descriptor kind.

- [ ] Generate module allocatable handles as borrowed descriptor handles.
- [ ] Create module allocatable handle objects at module initialization.
- [ ] Store generated operation pointers/accessors for module allocatable
  variables.
- [ ] Do not move ownership out of the Fortran module for ordinary module
  allocatable attribute reads.
- [ ] Generate derived-field allocatable handles as borrowed descriptor handles.
- [ ] Keep the parent wrapper object alive for derived-field allocatable
  handles.
- [ ] Generate field operations that access `parent%field`.
- [ ] Generate owned allocatable function-result handles when policy supports
  stable owner storage.
- [ ] Use wrapper-owned native storage for allocatable results, such as a
  derived owner type with an allocatable component.
- [ ] Move native allocatable function results or hidden output allocations into
  owner storage using `move_alloc` where applicable.
- [ ] Return a native pointer to owner storage for owned allocatable handles.
- [ ] Generate destroy routines called by the Python handle finalizer for owned
  allocatable handles.
- [ ] Generate module pointer handles as borrowed descriptor handles.
- [ ] Create module pointer handle objects at module initialization.
- [ ] Store generated operation pointers/accessors for module pointer variables.
- [ ] Do not transfer ownership of pointer targets for module pointer handles.
- [ ] Generate derived-field pointer handles as borrowed descriptor handles.
- [ ] Keep the parent wrapper object alive for derived-field pointer handles.
- [ ] Generate field operations that access `parent%field`.
- [ ] Generate pointer descriptor-argument handoff for `Pointer[T[...]]`
  parameters.
- [ ] Generate allocatable descriptor-argument handoff for
  `Allocatable[T[...]]` parameters.
- [ ] Do not guess compiler-specific descriptor layouts.

#### Pointer Descriptor Extraction

- [ ] Use TS 29113 / Fortran 2018 C descriptors for general pointer-array
  `to_numpy()` when this path is enabled.
- [ ] Use `ISO_Fortran_binding.h` only for descriptor-based pointer interop
  paths.
- [ ] Do not require `ISO_Fortran_binding.h` globally.
- [ ] Build NumPy shape from descriptor `dim[i].extent`.
- [ ] Build NumPy strides from descriptor `dim[i].sm`.
- [ ] Read descriptor `base_addr`, `elem_len`, `rank`, `dim[i].lower_bound`,
  `dim[i].extent`, and `dim[i].sm` for pointer views.
- [ ] Support strided pointer targets when descriptor support is available.
- [ ] If descriptor support is unavailable, choose one explicit policy:
  contiguous-only pointer views when shape/address are safely available,
  explicitly implemented copy fallback, or readiness failure with a clear
  diagnostic.

### 8. Python Binding Generation

Keep descriptor-handle argument conversion separate from normal array data
conversion. For normal `T[...]` parameters, support both ordinary ndarray inputs
and native handle inputs, but do not implement handle inputs by implicitly
calling `.to_numpy()`. The handle path should route to a native array-actual
handoff when the wrapped call is native.

- [ ] Accept `AllocatableHandle` objects for `Allocatable[T[...]]` parameters.
- [ ] Reject plain NumPy arrays for `Allocatable[T[...]]` parameters.
- [ ] Accept `PointerHandle` objects for `Pointer[T[...]]` parameters.
- [ ] Reject plain NumPy arrays for `Pointer[T[...]]` parameters.
- [ ] Accept `None` for optional-absent handle parameters only when the `.pyi`
  annotation includes `| None`.
- [ ] Convert `None` optional handles into native absent optional dummies, not
  into unallocated or unassociated handle objects.
- [ ] For normal `T[...]` parameters, accept ndarray inputs through the existing
  array data path.
- [ ] For normal `T[...]` parameters, accept allocated allocatable handles only
  by validating the handle state and passing the wrapped native allocatable
  array actual to the normal native array dummy.
- [ ] For normal `T[...]` parameters, accept associated pointer handles only by
  validating the handle state and passing the wrapped native pointer array
  actual to the normal native array dummy.
- [ ] Share dtype, rank, shape, layout, and mutability validation policy between
  ndarray inputs and handle inputs for `T[...]`, while keeping the ndarray
  pointer/shape handoff and native-handle array-actual handoff as separate
  implementation methods.
- [ ] Treat explicit `h.to_numpy()` or `p.to_numpy()` in user code as ordinary
  ndarray input, including rejection of `None` or read-only arrays when the
  native dummy requires writable storage.
- [ ] Reject unallocated allocatable handles for `T[...]` unless nullable
  data-buffer behavior is explicitly implemented.
- [ ] Reject unassociated pointer handles for `T[...]` unless nullable
  data-buffer behavior is explicitly implemented.

### 9. Compilation And Build Gating

- [ ] Require descriptor interop support only when a generated wrapper uses the
  pointer C-descriptor path.
- [ ] Do not require `ISO_Fortran_binding.h` for allocatable-only builds.
- [ ] Do not require `ISO_Fortran_binding.h` for pointer builds that do not use
  descriptor-based pointer interop.
- [ ] Emit a clear readiness or build diagnostic when pointer descriptor interop
  is required but unavailable.

## Test Checklist

### Parser And Printer Tests

- [ ] Parse and print `Allocatable[Float64[:]]`.
- [ ] Parse and print `Allocatable[String[:][:]]`.
- [ ] Parse and print `Allocatable[Float64[:, :]]`.
- [ ] Parse and print `Allocatable[Float64[:]] | None = ...`.
- [ ] Parse and print `Pointer[Float64[:]]`.
- [ ] Parse and print `Pointer[Float64[:, :]]`.
- [ ] Parse and print `Pointer[String[8][:]]` if string arrays are supported.
- [ ] Parse and print `Pointer[Float64[:]] | None = ...`.
- [ ] Verify normal `T[...]` type identity remains array data semantics even
  when runtime can accept handles by data coercion.
- [ ] Verify `Allocatable[T[...]]` and `Pointer[T[...]]` retain a base array
  data type that matches the wrapped `T[...]` annotation.
- [ ] Reject `Snapshot[T]` in active contracts.
- [ ] Reject or migrate `Annotated[T[...], Allocatable]`.
- [ ] Reject or migrate `Annotated[T[...], Pointer]`.
- [ ] Verify no generated `.pyi` uses `Snapshot[T]`.
- [ ] Verify no generated active `.pyi` uses public
  `Annotated[T[...], Allocatable]` or `Annotated[T[...], Pointer]` for array
  descriptor handles.

### Semantic IR And Policy Tests

- [ ] Verify Allocatable and Pointer handles use the same semantic handle
  representation family with distinct descriptor kinds.
- [ ] Verify handle types are distinct from normal array data types.
- [ ] Verify handle semantic types carry descriptor facts without mutating the
  plain array semantic type.
- [ ] Verify handle semantic types expose the base array data type used for
  `T[...]` call compatibility.
- [ ] Verify module-variable, derived-field, argument, result, and optional
  absent handle origins complete policy before lowering.
- [ ] Verify bridge/binding layers dispatch from completed policy decisions.
- [ ] Verify incomplete ownership, lifetime, release, addressability, or
  descriptor-extraction facts produce readiness blockers.
- [ ] Verify pointer allocation/deallocation/resize permissions are absent or
  blocked unless explicit pointer policy allows them.

### Shared Runtime Handle Tests

- [ ] Verify `AllocatableHandle` and `PointerHandle` use the same common
  `to_numpy()`, `shape`, dtype, rank, owner-retention, and ops-table path.
- [ ] Verify common shape metadata is reported consistently.
- [ ] Verify common dtype metadata is reported consistently.
- [ ] Verify handles keep required module, parent object, or owner storage alive.

### Allocatable Runtime Tests

- [ ] Module allocatable attribute is a handle object.
- [ ] `h.allocated` updates after allocate, deallocate, and resize.
- [ ] `h.shape` updates after allocate, deallocate, and resize.
- [ ] `h.to_numpy()` returns `None` when unallocated.
- [ ] `h.to_numpy()` returns a mutable borrowed view when
  aliasable/addressable.
- [ ] Mutating a borrowed view mutates native storage when policy allows a live
  view.
- [ ] `h.to_numpy()` returns a read-only detached snapshot when not
  aliasable/addressable.
- [ ] Derived allocatable field is a handle object.
- [ ] Derived-field handle keeps the parent wrapper alive.
- [ ] Derived-field `deallocate()` operates on `parent%field`.
- [ ] Derived-field `resize(shape)` operates on `parent%field`.
- [ ] Allocatable function result returns an owned handle.
- [ ] Owned result handle finalizer deallocates native owner storage.
- [ ] Owned result handle `to_numpy()` works after the bridge returns.
- [ ] `Allocatable[T[...]]` parameter accepts allocatable handles.
- [ ] `Allocatable[T[...]]` parameter rejects plain ndarray.
- [ ] `T[...]` parameter accepts ndarray.
- [ ] `T[...]` parameter accepts allocated allocatable handle through native
  array-actual handoff, without implicitly calling `h.to_numpy()`.
- [ ] `T[...]` parameter applies the same dtype, rank, shape, layout, and
  mutability validation policy to ndarray inputs and allocated allocatable
  handles.
- [ ] Explicit `T[...]` calls with `h.to_numpy()` follow the ordinary ndarray
  path and reject `None` or read-only arrays when writable storage is required.
- [ ] `T[...]` parameter rejects unallocated allocatable handle unless nullable
  data-buffer behavior is explicitly supported.

### Pointer Runtime Tests

- [ ] Module pointer attribute is a handle object.
- [ ] `p.associated` reflects association state.
- [ ] `p.shape` reflects association state and target shape.
- [ ] `p.to_numpy()` returns `None` when unassociated.
- [ ] `p.to_numpy()` returns a borrowed view when associated and supported.
- [ ] `p.nullify()` disassociates the native pointer descriptor.
- [ ] Derived pointer field is a handle object.
- [ ] Derived-field pointer handle keeps the parent wrapper alive.
- [ ] Derived-field pointer operations access `parent%field`.
- [ ] Pointer associated with a slice returns a NumPy view with expected shape
  and strides when C descriptors are available.
- [ ] If C descriptors are unavailable, test the selected explicit fallback:
  contiguous-only view, copy fallback, or clear readiness diagnostic.
- [ ] Pointer `deallocate()` and `resize()` are absent or raise when policy
  disallows them.
- [ ] Pointer `allocate()`, `deallocate()`, and `resize()` work only when
  explicit pointer policy allows them.
- [ ] `Pointer[T[...]]` parameter accepts pointer handles.
- [ ] `Pointer[T[...]]` parameter rejects plain ndarray.
- [ ] `T[...]` parameter accepts associated pointer handle through native
  array-actual handoff, without implicitly calling `p.to_numpy()`.
- [ ] `T[...]` parameter applies the same dtype, rank, shape, layout, and
  mutability validation policy to ndarray inputs and associated pointer
  handles.
- [ ] Explicit `T[...]` calls with `p.to_numpy()` follow the ordinary ndarray
  path and reject `None` or read-only arrays when writable storage is required.
- [ ] `T[...]` parameter rejects unassociated pointer handle unless nullable
  data-buffer behavior is explicitly supported.

### Build Gating Tests

- [ ] Pointer descriptor interop includes or requires `ISO_Fortran_binding.h`
  only when descriptor-based pointer interop is used.
- [ ] Allocatable-only builds do not require `ISO_Fortran_binding.h`.
- [ ] Builds that need unavailable pointer descriptor interop fail with a clear
  diagnostic rather than guessing descriptor layout.

### Documentation Regression Tests

- [ ] Public docs show `Allocatable[T[...]]` for allocatable array handles.
- [ ] Public docs show `Pointer[T[...]]` for pointer array handles.
- [ ] Public docs do not show `Annotated[T[...], Allocatable]` as the active
  public spelling.
- [ ] Public docs do not show `Annotated[T[...], Pointer]` as the active public
  spelling.
- [ ] Public docs do not show `Snapshot[T]` as an active array descriptor
  contract.
- [ ] Public docs explain `to_numpy()` as the explicit user-facing extraction
  operation for both handle types, not the required internal implementation of
  handle-to-native calls.

## Completion Criteria

The feature is complete only when all of these are true:

- [ ] Allocatable and Pointer array handles share one internal handle
  foundation.
- [ ] Public contract syntax is `Allocatable[T[...]]` and `Pointer[T[...]]`.
- [ ] Active parser/printer paths reject or remove the old annotation and
  snapshot forms.
- [ ] Post-IR policy completes every handle decision before `ir2ast.py`.
- [ ] Bridge and binding generation dispatch from completed policy only.
- [ ] Runtime handles expose the documented APIs and state transitions.
- [ ] Pointer descriptor extraction never guesses compiler-specific descriptor
  layout.
- [ ] Build gating keeps descriptor interop requirements local to the paths that
  need them.
- [ ] Runtime tests cover module variables, derived fields, arguments, data
  coercion, owned allocatable results, pointer association, pointer nullify, and
  pointer policy gating.
- [ ] Documentation and generated `.pyi` fixtures no longer present old public
  forms as active contracts.
