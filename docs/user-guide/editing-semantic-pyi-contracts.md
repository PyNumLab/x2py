---
title: Editing Semantic .pyi Contracts
audience: users, advanced users
prerequisites: Fortran wrapper guide, semantic .pyi format
related: fortran-wrapper.md, ../reference/semantic-pyi-format.md, ../roadmap/semantic-pyi-wrapper-checklist.md
status: maintained
---

# Editing Semantic `.pyi` Contracts

This guide is the user-facing contract for changing a generated semantic
`.pyi` before building a wrapper. It covers the edits x2py handles, the native
facts an edit must preserve, the runtime effect of each supported edit, and the
errors raised for unsafe combinations.

Use the [semantic `.pyi` format reference](../reference/semantic-pyi-format.md)
for the complete grammar. Use this guide to decide whether a proposed edit is a
supported wrapper operation.

## The Editing Workflow

Generate a starter contract package from the native sources:

```bash
python3 -m x2py native/solver.f90 --pyi --out contracts/solver
```

Keep the generated package as a baseline, copy it, and edit the copy:

```text
contracts/
├── generated_solver/
│   ├── __init__.pyi
│   └── solver.pyi
└── edited_solver/
    ├── __init__.pyi
    └── solver.pyi
```

Build the edited entry contract with the same native implementation artifacts:

```bash
python3 -m x2py contracts/edited_solver/__init__.pyi \
  --wrap \
  --native-objects build/solver.o \
  --native-include-dir build/mod \
  --out-dir build/edited-solver
```

The entry `.pyi` is the sole semantic input to wrapper generation. x2py does
not reparse the native source to restore a removed declaration, projection, or
policy. Objects, archives, shared libraries, module files, and optional native
sources supplied to the build are implementation inputs, not hidden semantic
inputs.

## What May And May Not Change

An edited contract contains two kinds of information:

1. **Native facts** describe the implementation that already exists: native
   module and symbol identity, procedure kind, native argument order, ABI type
   and kind, rank, storage category, callback signature, and required native
   imports.
2. **Wrapper policy** describes the Python surface x2py should generate:
   exports, visibility, Python names, overload grouping, result projection,
   validation, mutation, ownership, lifetime, destruction, error translation,
   and GIL behavior.

Wrapper policy is editable. Native facts may be rewritten only when the new
facts still describe the supplied native artifacts. x2py validates structural
consistency, but it cannot inspect an arbitrary object or shared library and
prove its ABI. A structurally valid lie about an opaque native binary can still
fail at compile, link, import, or call time.

The supported edit surface is:

| Edit | Supported effect |
| --- | --- |
| Remove a declaration or entry import | Remove that function, method, variable, class, constructor, class member, or overload candidate from the Python API. |
| Add `@private` or `private[...]` | Retain a declaration as an internal contract input while hiding it from Python. |
| Add a declaration for an existing native symbol | Wrap that symbol when the declaration supplies all required native facts and the artifact implements them. |
| Change the Python export name or namespace | Edit the entry-package import/export tree; use `@bind(...)` when the Python declaration name differs from its native target. |
| Change overload grouping | Add or remove `@overload("specific")` candidates with distinct supported dtype/rank signatures. |
| Change Python/native argument projection | Add or edit `@native_call(...)` and `Returns[...]`, or remove `@native_call` and expose the complete native argument list in native order. |
| Change array validation | Edit dtype, rank, dimensions, `ORDER_C`, `ORDER_F`, `ORDER_ANY`, `Flat`, optionality, and supported pointer/allocatable metadata. |
| Change visible mutation | Use caller-owned writable storage, or `Immutable` plus an explicit replacement result. |
| Change supported ownership/lifetime policy | Supply a valid `Ownership(...)`, `Transfer(...)`, and `Destruction(...)` triple for the declared storage and context. |
| Translate native status to exceptions | Add `@raises(...)` with valid projected status/message values. |
| Keep the GIL | Add `@hold_gil` for a call that must execute while holding the Python GIL. |

The following are not supported edits:

- changing ABI dtype, kind, rank, calling convention, native argument order, or
  native symbol without supplying a matching implementation;
- declaring that arbitrary native storage is wrapper-owned without a generated
  wrapper instance or an implemented native release path;
- requesting a borrowed pointer view without owner retention and stale-view
  invalidation;
- using generic `Annotated` helpers such as `Bounded(...)` or `Finite` as if
  they already generated runtime checks; they currently round-trip as semantic
  constraints only;
- requesting general implicit dtype coercion; wrapper arguments currently use
  the exact documented NumPy dtype unless a specific supported path says
  otherwise; or
- relying on omitted metadata to select a risky copy, borrow, reassociation, or
  destruction policy.

Unsupported policy is a blocker, not a request for x2py to guess.

## Removing And Hiding API Members

### Remove a declaration

Delete a public declaration from the leaf `.pyi` to remove it from the
generated Python API. For example, deleting `next_local` removes the function
without affecting the remaining module variables and functions:

```python
counter: Int32

def summarize() -> Int32: ...
```

This rule applies to top-level functions, module variables, classes, methods,
fields, constructors, and individual overload declarations. x2py does not
recreate a deleted declaration from native source.

For a generated derived-type constructor, removing the generated keyword-only
`__init__(self, *, ...)` declaration also suppresses that constructor. Native
allocation may still exist internally, but the deleted public constructor is
not regenerated.

### Hide a declaration but keep it available internally

Use `@private` for functions, methods, and classes:

```python
@private
def scaled_counter() -> Float64: ...
```

Use `private[...]` for data declarations or arguments:

```python
scale: private[Float64]
```

Private declarations can still supply native types, bindings, or helper facts
needed by other public declarations. User-private declarations remain
printable and reloadable so an edited contract round-trip does not expose them.
Ordinary declarations that were private only in the native source remain
omitted from newly generated starter contracts.

### Remove an overload candidate

Each candidate is an independent declaration. Removing one candidate narrows
runtime dispatch without removing the generic name:

```python
@overload("convert_integer")
def convert(value: Int32) -> Int32: ...

# The generated Float64 candidate was removed intentionally.
```

Calls that no longer match a remaining candidate raise `TypeError`. Do not keep
an empty overload declaration as an absence marker; remove it.

## Adding And Renaming Declarations

### Add a contained procedure already present in a native module

Add the complete callable declaration to the module leaf:

```python
def norm2(values: Float64[:]) -> Float64: ...
```

The leaf filename identifies the native module. The Python name is also the
native procedure name unless `@bind(...)` says otherwise.

### Add or rename a native target

Use `@bind(...)` when the declaration's Python name differs from the native
specific procedure:

```python
@bind("solver_step")
def step(values: Float64[:]) -> Int32: ...
```

For a standalone external symbol, also use `@external`:

```python
@external
@bind("vendor_norm2")
def norm2(values: Float64[:]) -> Float64: ...
```

`@bind(...)` changes name resolution. It does not adapt an incompatible ABI.

### Add an overload candidate

Link every Python overload to one concrete native specific:

```python
@overload("scale_integer")
def scale(value: Int32) -> Int32: ...

@overload("scale_real")
def scale(value: Float64) -> Float64: ...
```

To rename the Python overload group while calling an existing native generic,
preserve the native generic explicitly:

```python
@overload("convert_integer", generic="convert")
def convert_number(value: Int32) -> Int32: ...
```

Candidates must be distinguishable by the implemented runtime dispatcher.
Duplicate dtype/rank signatures are rejected because declaration order must not
silently choose a native procedure.

### Replace the generated constructor

An edited class may bind `__init__` to one concrete native initializer:

```python
class state:
    @bind("init_state")
    def __init__(self, size: Ptr(Const(Int32))) -> None: ...
```

The generated field-keyword constructor and a bound native initializer are
different contracts. Remove the old constructor declaration when replacing it.

## Editing The Call Shape

### Remove `@native_call` and expose native order

When every native dummy remains visible in native order, the edited declaration
does not need `@native_call`:

```python
def scalar_status(
    base: Ptr(Const(Int32)),
    status: Annotated[Ptr(Int32), Intent("out")],
) -> None: ...
```

The caller supplies writable storage for the `intent(out)` scalar:

```python
status = np.empty((), dtype=np.int32)
assert module.scalar_status(np.int32(4), status) is None
assert status[()] == np.int32(15)
```

This exact edit is compiled and exercised by
[`test_native_order_contracts.py`](../../tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py).
It covers scalar, array, matrix, string, mixed-result, and derived-type native
order calls. An ordinary Python `str` cannot observe mutation of the temporary
native character buffer; use a projected replacement when Python must see the
new string.

### Project native arguments into Python returns

Use `Returns[...]` for the Python result contract and `@native_call(...)` when
the native call needs hidden output storage, reordered arguments, constants,
lengths, presence flags, shapes, or work buffers:

```python
@native_call([Arg(0), Return("status", 0)])
def scalar_status(
    base: Ptr(Const(Int32)),
) -> Returns["status", Int32]: ...
```

Removing the explicit `status` parameter and adding the result projection are
one edit. A projection must map every required native argument exactly once;
incomplete, duplicate, or out-of-range mappings are contract errors.

### Make mutation replacement-only

`Immutable` says the original Python-visible object must not be mutated. A
writable native argument therefore needs either an explicit replacement result
or an explicit call-local discarded-mutation policy:

```python
def scale_with_status(
    values: Annotated[Float64[:], Immutable],
    status: Annotated[Ptr(Int32), Intent("out")],
) -> Returns["values", Float64[:]]: ...
```

At runtime, x2py copies `values` into mutable native storage, calls native code,
and returns a different NumPy array. The original remains unchanged. The
compiled evidence is
[`test_policy_dispatch_contracts.py`](../../tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py).

`Immutable` plus `Transfer("borrowed_view")` on a writable value is
contradictory: one requests replacement-only semantics and the other requests a
writable shared view. The contract fails instead of selecting one silently.

## Editing Types, Shapes, Layout, And Optionality

The annotation is runtime policy, not merely an IDE hint. Supported edits can
tighten or broaden validation without changing the native ABI:

```python
def solve(
    matrix: Annotated[Float64[3, 3], ORDER_F],
    rhs: Float64[3],
) -> Float64[3]: ...
```

The wrapper validates exact dtype, rank, shape, layout, writeability, byte
order, alignment, and zero-sized-array rules required by the selected backend
path. Examples of supported changes include:

- `Float64[:, :]` to `Float64[3, 3]` to require one shape;
- `ORDER_F` to `ORDER_ANY` when the native path is implemented for either
  contiguous orientation;
- `T | None` or a default `= ...` for a genuinely optional native argument;
- `Allocatable`, `Pointer`, `FortranTarget`, or `PointerPolicy(...)` when those
  facts match the native declaration and the selected policy path; and
- `Immutable` for a supported replacement or call-local mutation policy.

Changing `Float64[:]` to `Int32[:]`, changing rank, or inventing optionality is
not a Python-only conversion. It changes the declared native ABI and is valid
only when the linked implementation has that ABI.

Generic constraints such as `Bounded(1, 8)` and `Finite` currently survive
parse/print round-trips but do not generate runtime validation. Wrapper
readiness reports `fortran_runtime_constraints_unsupported` instead of building
a wrapper that silently ignores them. General semantic coercions are handled
the same way through `fortran_runtime_coercions_unsupported`.

## Editing Errors And GIL Behavior

Use `@raises(...)` to turn a projected native status into a Python exception:

```python
@raises(status="status", message="message", success=0)
def solve(values: Float64[:]) -> Returns[
    "result", Float64[:],
    "status", Int32,
    "message", String,
]: ...
```

The named status and optional message must exist in the function's projected
results. Successful calls omit status-only implementation results from the
Python value according to the documented projection. Non-success status raises
the generated Python exception before returning an ordinary result.

Wrappers release the GIL around ordinary native calls when the call contract
allows it. Add `@hold_gil` when native code must call Python synchronously or
otherwise requires the current Python thread to retain the GIL:

```python
@hold_gil
def invoke_callback(callback: Callable[[Float64], Float64]) -> Float64: ...
```

These decorators change wrapper runtime policy; they do not change the native
procedure ABI.

## Ownership, Transfer, And Destruction

Ownership edits use a complete policy triple:

```python
Annotated[
    Float64[:],
    Ownership("native"),
    Transfer("borrowed_view"),
    Destruction("native_owner"),
]
```

The three values answer different questions:

- `Ownership(...)`: who owns the authoritative storage?
- `Transfer(...)`: does Python receive a value, temporary, in-place object,
  copy, view, or wrapper instance?
- `Destruction(...)`: which runtime releases owned storage, and at what
  lifetime boundary?

They are not three independent switches. x2py validates the combination
against object kind, native storage category, call position, mutability,
nullability, projection, and available release mechanism. An edit can choose
between implemented boundary behaviors; it cannot retroactively change where a
native allocation came from.

### One `values` example with three owners

The following variants all expose a rank-one `Float64` array named `values`,
but their native storage contexts make their lifetimes different.

#### Fortran-owned module storage

```python
module_values: Annotated[
    Float64[:],
    Allocatable,
    FortranTarget,
    Ownership("native"),
    Transfer("borrowed_view"),
    Destruction("native_owner"),
] | None
```

Python receives a zero-copy NumPy view. Mutation reaches the Fortran module
allocation. NumPy must not free the data. A native allocate/deallocate routine
controls the allocation, and a later native deallocation or reallocation makes
previous views stale. Fetching the property again returns `None` when the
allocatable is unallocated.

Lifecycle:

```text
Fortran allocates -> Python borrows -> Python releases view (no native free)
                                 \-> Fortran deallocates authoritative storage
```

#### Wrapper-owned component storage

```python
class buffer:
    values: Annotated[
        Float64[:],
        Allocatable,
        Ownership("wrapper"),
        Transfer("borrowed_view"),
        Destruction("wrapper_dealloc"),
    ] | None
```

The containing Python extension object owns the native derived-type instance;
the allocatable component belongs to that instance. `values.base` keeps the
wrapper object alive while a view exists. NumPy releases only its view object.
The generated wrapper deallocator finalizes/releases the native instance after
the last owning reference is gone. An explicit native component-deallocation
method may make an existing view stale sooner, so callers must not retain views
across such calls.

Lifecycle:

```text
wrapper allocates instance -> component allocates -> NumPy view retains wrapper
                                           \-> wrapper deallocator finalizes instance
```

#### NumPy-owned copy

```python
@native_call([Arg(0), Return("values", 0)])
def build_values(
    n: Ptr(Const(Int32)),
) -> Annotated[
    Float64[:],
    Allocatable,
    Ownership("python"),
    Transfer("copy_return"),
    Destruction("python_refcount"),
] | None: ...
```

Native code produces allocatable output storage. Before that storage is
released, the bridge copies it into a new Python-visible NumPy allocation.
Later native changes do not affect the array. NumPy or its generated base
capsule releases the copy after Python references are gone.

Lifecycle:

```text
Fortran allocates output -> wrapper copies -> Fortran output is released
                                      \-> NumPy owns and later releases the copy
```

These are three supported ownership outcomes for the same Python-level array
concept, not permission to relabel one allocation arbitrarily. In particular,
changing the module-storage example to `Destruction("wrapper_dealloc")` would
be unsafe: the generated module wrapper has no right to finalize storage owned
by Fortran module state. Use a copy if Python must own an independent lifetime,
or keep the native-owned borrowed view.

### Supported transfer modes

| Transfer | Supported use | Destruction |
| --- | --- | --- |
| `by_value` | Scalar values returned to Python. | `python_refcount` |
| `call_local` | Converted scalar/string/array inputs, pointer inputs associated only for one call, and explicitly discarded immutable mutation. | `none` or `call_local` |
| `in_place` | Caller-supplied writable scalar storage, NumPy arrays, and existing wrapper instances. | `caller` or the existing wrapper's `wrapper_dealloc` |
| `copy_return` | Strings, array results, allocatable outputs, and immutable replacement results copied to Python. | `python_refcount` |
| `snapshot_copy` | Supported pointer function results with complete shape and lifetime facts; Python receives a detached copy. | `python_refcount` |
| `borrowed_view` | Target-backed module allocatables and supported fields/components whose owner remains identifiable. | `native_owner` or `wrapper_dealloc` |
| `wrapper_instance` | Derived-type output represented by a Python extension object owning a native instance. | `wrapper_dealloc` |
| `blocked` | Intentional declaration that no safe implemented transfer exists. | `blocked` |

### Destruction responsibilities

| Destruction | Runtime responsibility |
| --- | --- |
| `python_refcount` | Python, NumPy, or a generated base capsule releases Python-owned storage after references are gone. |
| `wrapper_dealloc` | The generated extension object's deallocator finalizes/releases its native instance. |
| `native_owner` | Fortran module state or an external native owner releases storage; Python only borrows. |
| `caller` | The caller retains and releases the object supplied to x2py. |
| `call_local` | Generated bridge cleanup releases the temporary before the wrapper call returns. |
| `none` | x2py created no persistent owned storage for this boundary value. |
| `blocked` | Release responsibility is unknown, contradictory, or not implemented; generation stops. |

`Ownership("unknown")`, `Transfer("blocked")`, and
`Destruction("blocked")` are useful for making an unresolved contract fail
closed. They are not runtime ownership modes.

### Ownership combinations that fail

Examples include:

- `Immutable` writable storage with `Transfer("borrowed_view")`;
- `Transfer("copy_return")` on an argument with no projected replacement;
- pointer `intent(out)` or `intent(inout)` reassociation without implemented
  owner, shape, lifetime, and release behavior;
- pointer module variables or derived-type pointer fields without an
  implemented snapshot or borrowed-accessor path;
- borrowed pointer views without owner retention and stale-view invalidation;
- `Ownership("native")` with `Destruction("python_refcount")` for the same
  authoritative allocation; and
- `Ownership("python")` with `Destruction("native_owner")`.

The diagnostic identifies the declaration and rejected policy. x2py does not
silently replace these combinations with its default policy.

## Package Exports And Namespaces

The entry `__init__.pyi` controls which leaf modules and declarations enter the
extension's Python export tree. Removing an entry import removes that branch;
adding a relative import adds a contract fragment:

```python
from . import solver
from .helpers import norm2
```

Leaf files continue to identify native modules. Entry imports compose the
Python package; they do not rename native modules or infer object files.
Conflicting exports, missing relative files, and import cycles fail while the
contract graph is loaded.

## Diagnostics For Edited Contracts

Failures occur at the first layer with enough information:

1. **Load errors**: invalid Python syntax, unsupported decorators or metadata,
   untyped parameters, invalid imports, or import cycles. File-based errors
   include the `.pyi` path.
2. **Structural validation errors**: incomplete projections, duplicate native
   positions, invalid `@bind`/`@overload` links, conflicting exports, or public
   declarations exposing private types.
3. **Readiness/policy blockers**: incomplete ownership, lifetime, pointer,
   coercion, mutation, allocation, or release behavior.
4. **Native build/runtime errors**: the supplied artifact does not implement
   the declared symbol or ABI.

Do not fix a policy blocker by deleting metadata until the wrapper happens to
build. The corrected contract must explicitly describe the intended boundary
behavior and its owner.

## Runtime Evidence

Editable-contract runtime fixtures live under
[`tests/wrapper/fortran/edit_pyi_contracts`](../../tests/wrapper/fortran/edit_pyi_contracts/README.md):

- `test_native_order_contracts.py` removes `@native_call` and exposes native
  argument order;
- `test_ownership_contracts.py` applies explicit native-owned, wrapper-owned,
  and Python/NumPy-owned lifetime policies to the same array example;
- `test_visibility_contracts.py` removes and hides declarations while checking
  unaffected runtime behavior;
- `test_surface_edit_contracts.py` removes classes, methods, constructors,
  fields, and overload candidates and adds renamed bindings and overloads; and
- `test_policy_dispatch_contracts.py` proves immutable replacement through the
  completed ownership/action policy.

Broader ownership lifetime evidence is in
[`test_allocatable_views.py`](../../tests/wrapper/fortran/module_state/test_allocatable_views.py)
and
[`test_allocatable_replacement.py`](../../tests/wrapper/fortran/module_state/test_allocatable_replacement.py).
The active completion ledger is the
[semantic `.pyi` wrapper checklist](../roadmap/semantic-pyi-wrapper-checklist.md).
