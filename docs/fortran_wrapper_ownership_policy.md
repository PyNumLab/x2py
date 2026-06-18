# Fortran Wrapper Ownership And Lifetime Policy

This document defines the ownership, lifetime, and destruction rules for
generated Fortran-to-Python wrappers. It is the canonical place for answering:

- who owns a value or memory buffer;
- whether Python receives a view or a copy;
- when native storage is destroyed;
- whether mutation through Python is visible to Fortran; and
- when wrapper generation must stop with a readiness blocker.

The document includes both supported behavior and explicit blockers. A case
described as blocked or future explicit-policy work is not implemented behavior.

The central rule is:

> The wrapper must never infer ownership from syntax alone. Ownership follows
> the native storage category, the known owner, and the transfer mode at the
> Python boundary.

For example, an allocatable array dummy argument and an allocatable array field
are both Fortran allocatables, but they do not have the same owner. The dummy
argument crosses the Python boundary as a replacement value, so it is copied
into a Python-owned NumPy array. The field belongs to a containing native
derived-type instance, so Python may borrow a view from that owner.

## Central Policy Mechanism

Ownership decisions must be resolved through `x2py.ownership_policy`, not
re-derived separately in semantic conversion, bridge generation, binding
docstrings, or tests. The resolver returns one decision for each value:

- object kind, such as scalar, string, NumPy array, derived type, module
  variable, or derived-type field;
- owner, such as Python, caller, native code, or wrapper object;
- transfer mode, such as by-value, in-place, copy-return, snapshot-copy,
  borrowed-view, call-local, or wrapper-instance;
- destruction policy, such as Python reference-count cleanup, wrapper
  deallocation helper, native-owner release, caller cleanup, call-local cleanup,
  or blocked; and
- the existing low-level `memory_handling` hint used by code generation
  (`stack`, `heap`, or `alias`).

The resolver is intentionally table/handler driven. Each object kind has a
dedicated handler so policy changes are made in one place and then consumed by
IR lowering, C/Fortran bridge generation, CPython binding generation, docstrings,
and tests.

Code generation must then dispatch from the resolved policy action through
explicit action maps, not by reinterpreting storage flags. Bridge and binding
generators use `OwnershipActionDispatcher` tables keyed by `CodegenAction` and
route each action to a dedicated method. Low-level printers should print the AST
they are given; they should not invent ownership behavior.

`.pyi` files may override policy using `Annotated` metadata:

```python
values: Annotated[
    Float64[:],
    Pointer,
    Ownership("python"),
    Transfer("snapshot_copy"),
    Destruction("python_refcount"),
]
```

Overrides are policy facts, not magic implementation support. A stub can choose
the owner and transfer mode only when it also supplies the native facts needed
by the backend path, such as shape, nullability, target owner, lifetime, and
release behavior.

## Vocabulary

### Python-Owned

Python-owned means the Python object owns the returned value or data buffer.
When its Python reference count reaches zero, normal Python or NumPy destruction
releases it.

Examples:

- Python `int`, `float`, `complex`, `bool`, and `str` results.
- NumPy arrays returned by copy-return or snapshot-copy policy.
- Caller-created NumPy arrays passed to Fortran and later released by Python.

For a Python-owned NumPy array, Fortran must not keep using the array unless a
documented call-local or persistent-reference policy says so.

### Wrapper-Owned

Wrapper-owned means a Python extension object owns a native Fortran instance.
The memory is native, but the lifetime is controlled by the Python wrapper
object.

The wrapper object's deallocation path owns destruction. Users do not need a
normal public `destroy()` method for wrapper-owned values. Internally,
`tp_dealloc` must call a generated Fortran-aware destroy helper for owned
instances. That helper releases allocatable components and deallocates the
native Fortran instance through the Fortran bridge, which invokes Fortran
finalization for owned instances.

Examples:

- `p = make_point()` where `make_point()` returns a Fortran derived type.
- `p = make_point_out(...)` where a hidden `type(point), intent(out)` dummy is
  returned as a Python object.

Wrapper-owned does not mean Python may directly call `free()` on Fortran
allocatable components. Destruction must go through generated Fortran-aware
code.

Borrowed child wrappers set the generated alias flag. Their Python deallocator
does not invoke the native destroy helper or finalization; it releases the child
wrapper and its retained parent reference. Finalization occurs only when the
owning wrapper is destroyed. Fortran final subroutines have no recoverable
status channel through `tp_dealloc`; they must complete normally. Native
termination from a finalizer terminates the process.

### Native-Owned

Native-owned means native code owns the storage independently of a Python value.
Python may receive a borrowed view or accessor, but Python does not destroy the
storage.

Examples:

- A Fortran module allocatable array owned by the module.
- Storage owned by an external library.
- A pointer target owned by unknown native state.

Native-owned storage may require explicit native routines for allocation,
reallocation, or deallocation. Existing Python views are not automatically
invalidated when native code changes the storage.

Native-owned deallocation is not performed by the borrowed Python view. It
happens only when native code executes the owning release operation. In
practice that means one of these cases:

- The wrapped Fortran module provides a routine such as `deallocate_values()`
  that executes `deallocate(values)`. Python may call that wrapped routine, but
  the deallocation is still performed by Fortran.
- An external library provides a release routine such as `destroy_handle()` or
  `free_buffer()`. Python may call a wrapper for that routine, but the library
  owns the release semantics.
- Native code deallocates or reallocates storage internally as part of another
  native call.
- If no release operation or lifetime rule is known, x2py must not invent one.
  It should expose only safe borrowed access when the owner is stable, or block
  the interface when lifetime is unclear.

Borrowed Python views do not call those release routines when the view is
garbage-collected. They only reference the native storage while it remains
valid.

### When Native-Owned Storage Is Destroyed

Native-owned storage is destroyed only when the native owner destroys it. There
is no universal automatic deletion at the Python boundary.

Common cases:

- A Fortran module allocatable variable usually lives until a wrapped Fortran
  routine deallocates or reallocates it, or until process/library teardown. Do
  not rely on process exit as a useful Python lifetime policy.
- A Fortran routine may deallocate or reallocate module storage as part of its
  own logic. Python cannot see that unless the wrapper exposes a fresh getter or
  the routine's documentation states the effect.
- An external library allocation lives until the library's documented release
  routine is called.
- Native static or global storage may live for the whole process and may never
  have a callable release operation.
- A pointer target with unknown owner has unknown lifetime. x2py should block
  borrowed access unless an explicit policy supplies the owner and lifetime.

Therefore, for native-owned storage, Python cleanup does not decide destruction
time. A borrowed view may disappear before the native storage is destroyed, or
native storage may be destroyed while a borrowed view still exists. The latter
case can leave the view invalid, so users must copy when they need independent
lifetime.

### Native-Owned Is Not Wrapper-Owned

Both native-owned and wrapper-owned storage may involve calling Fortran code,
but the ownership obligation is different.

For wrapper-owned storage, the Python object is responsible for exactly one
release of the native instance. The release is automatic and tied to the Python
object's `tp_dealloc` path:

```python
p = make_buffer()
del p
# The generated wrapper deallocation path releases the wrapper-owned native
# buffer instance through a Fortran-aware destroy helper.
```

For native-owned storage, the Python object returned to the user is only an
access path. It is not responsible for release. A native release routine may
still be wrapped as a Python-callable function, but calling that function is an
explicit operation on the native owner, not destruction of the borrowed view:

```python
allocate_values(3)
view = get_values()

del view
# No Fortran deallocation happens.

deallocate_values()
# This calls the wrapped Fortran routine that owns and deallocates the module
# variable.
```

The wrapper is therefore only a call adapter in the native-owned case, not the
owner. If an external library handle or native allocation should be released
automatically when a Python object dies, that value is no longer merely
native-owned borrowed storage; it needs an explicit wrapper-owned handle policy
that names the native release routine and guarantees one release.

### Borrowed View

A borrowed view is a Python object that references native storage owned by
something else. The view must keep that owner alive when the owner is a Python
wrapper object.

Examples:

- `obj.values` for an allocatable array field of a wrapper-owned derived type.
- `get_module_values()` for a target-backed allocatable module array.
- `obj.origin` for a nested scalar derived-type component.

Borrowed views do not destroy storage. They may become invalid if native code
deallocates or reallocates the target and the wrapper cannot track that change.
Users must call `.copy()` when they need independent lifetime.

### Copy-Return

Copy-return means the wrapper copies native output storage into a new
Python-owned value before returning to Python. After the copy, the native
temporary is released by the bridge or by normal native scope exit.

Examples:

- `real, allocatable, intent(out) :: values(:)`
- allocatable array function results
- explicit-shape or automatic array function results
- scalar character results copied to Python `str`

The returned Python object is independent of later native mutation.

### Snapshot Copy

Snapshot copy means Python receives a Python-owned copy of storage that remains
owned somewhere else natively. It is used when Python may inspect current native
state but must not borrow or own the original target.

Examples:

- Pointer array function results when association state, shape, dtype,
  contiguity, nullability, target owner, and deallocation obligations are known.
- Pointer array fields or module variables under an explicit policy that allows
  a snapshot.

Mutating a snapshot does not mutate the native target. Repeated access may
produce a new Python array.

### Call-Local Association

Call-local association means the wrapper associates native dummy storage with a
Python object only for the duration of one native call.

Examples:

- Pointer `intent(in)` array dummy associated with a Python-owned NumPy array.
- Ordinary array input passed to a Fortran procedure.

Fortran must not save the pointer or use it after the call unless explicit
policy records a persistent reference and lifetime rule.

### Blocked

Blocked means wrapper generation must stop with a readiness blocker. This is
required whenever the wrapper cannot prove enough ownership, lifetime,
deallocation, shape, dtype, contiguity, mutability, or aliasing facts to produce
safe Python behavior.

## Ownership Invariants

1. Exactly one owner is responsible for destroying each owned native allocation.
2. Python-owned NumPy arrays are independent Python values unless explicitly
   documented as call-local inputs.
3. Wrapper-owned derived-type instances are destroyed by generated
   Fortran-aware helpers, not by direct Python/C deallocation of their
   components.
4. Borrowed views keep their Python owner alive when the owner is a wrapper
   object.
5. Borrowed views do not protect against native reallocation or deallocation by
   other calls.
6. Pointer targets are not owned by a containing derived type by default.
7. Putting a pointer in a field does not make it safe to borrow.
8. If the wrapper cannot prove destruction behavior, it must block instead of
   leaking, double-freeing, or inventing ownership.

## Scalars

Primitive scalar inputs are converted to native values for the call. No
persistent storage ownership crosses the boundary.

```fortran
subroutine scale(x, factor)
  real(8), intent(inout) :: x
  real(8), intent(in) :: factor

  x = x * factor
end subroutine scale
```

Python-visible scalar mutation requires pointer-backed storage or an explicit
projection policy. For generated Fortran wrappers, scalar `intent(out)` values
are hidden and returned as new Python-owned scalar values:

```fortran
subroutine get_count(count)
  integer, intent(out) :: count

  count = 42
end subroutine get_count
```

```python
count = get_count()
# count is a Python-owned int-like result.
```

No native destruction is needed for primitive Python scalar results.

When a Python-visible value type is immutable but the Fortran dummy argument is
mutable, the wrapper must not claim in-place mutation. It must either block the
form or use replacement projection: copy the Python value into mutable native
temporary storage, call Fortran, copy the final native value back, and return a
new Python-owned value. This rule applies to scalar strings today and is the
default policy for any future immutable public type that needs `intent(inout)`
semantics.

## Strings

Python `str` results are Python-owned. Native character storage is copied into
the Python string before returning.

```fortran
character(len=8) function label()
  label = "ready"
end function label
```

```python
text = label()
# text is a Python-owned str. It does not reference Fortran storage.
```

Deferred-length or allocatable character results follow the same visible
ownership rule: Python receives a new `str`, and the native temporary is
released by the bridge.

Scalar `character, intent(inout)` arguments use the immutable-value replacement
policy: Python passes a `str`, the wrapper copies it into mutable native
character storage for the call, and Python receives a new `str` containing the
post-call value. The original Python `str` is unchanged.

Scalar character conversion is byte-oriented at the ABI boundary. Python input
is encoded with CPython's UTF-8 representation. Fixed-length character dummies
truncate input bytes to the declared length and pad shorter input with blanks;
the returned Python `str` reflects the full fixed-length Fortran buffer,
including trailing blanks. Assumed-length dummies use the encoded input byte
length. Embedded NUL bytes in Python input are rejected before the native call
because the public result path is a NUL-terminated C string.

Character arrays and mutable allocatable character dummy arguments need their
own array storage, allocation, encoding, truncation, and hidden-length policy.
Until that policy is implemented, wrapper generation must block those forms
instead of guessing.

## Ordinary NumPy Array Arguments

For non-allocatable array dummy arguments, the caller provides storage. The
wrapper validates dtype, rank, shape, layout, and writeability.

```fortran
subroutine fill(values)
  real(8), intent(out) :: values(:)

  values = 1.0_8
end subroutine fill
```

```python
values = np.empty(4, dtype=np.float64)
returned = fill(values)

assert returned is values
np.testing.assert_allclose(values, np.ones(4))
```

Ownership stays with the Python array. Fortran writes through the native view
only during the call. The wrapper does not allocate replacement storage.

For `intent(in)`, the same rule applies except the native contract is read-only
from Fortran's point of view:

```fortran
real(8) function total(values)
  real(8), intent(in) :: values(:)

  total = sum(values)
end function total
```

```python
values = np.array([1.0, 2.0, 3.0])
assert total(values) == 6.0
# values is still Python-owned.
```

## Allocatable Array Outputs

Allocatable array dummy outputs cross the Python boundary as replacement
values. They use copy-return ownership.

```fortran
subroutine build_values(n, values)
  integer, intent(in) :: n
  real(8), allocatable, intent(out) :: values(:)

  allocate(values(n))
  values = 2.0_8
end subroutine build_values
```

```python
values = build_values(3)

# values is a Python-owned NumPy array.
# Mutating it does not mutate any Fortran allocation.
values[0] = 9.0
```

The bridge copies the allocated Fortran storage into NumPy-owned memory and
then deallocates the temporary Fortran allocation. If the Fortran dummy remains
unallocated, Python receives `None`.

`allocatable, intent(inout)` array dummies also use replacement semantics:

```fortran
subroutine replace_values(values)
  real(8), allocatable, intent(inout) :: values(:)

  if (allocated(values)) deallocate(values)
  allocate(values(2))
  values = [10.0_8, 20.0_8]
end subroutine replace_values
```

```python
original = np.array([1.0, 2.0], dtype=np.float64)
replacement = replace_values(original)

# original is unchanged and remains Python-owned by the caller.
# replacement is a new Python-owned NumPy array.
```

This avoids stale Python views after Fortran reallocates the dummy.

## Array Function Results

Array-valued function results are copy-return values. The returned NumPy array
owns its data and is independent of the Fortran result temporary.

```fortran
function make_vector(n) result(values)
  integer, intent(in) :: n
  real(8) :: values(n)

  values = 3.0_8
end function make_vector
```

```python
values = make_vector(4)
# Python-owned NumPy array.
```

This policy avoids exposing a view to a Fortran function result whose lifetime
ends at the native boundary.

## Module Arrays

Fortran module variables are native-owned by the module. A target-backed
allocatable module array may be exposed through an explicit getter as a
borrowed view.

```fortran
module store
  real(8), allocatable, target :: values(:)
contains
  subroutine allocate_values(n)
    integer, intent(in) :: n
    if (allocated(values)) deallocate(values)
    allocate(values(n))
  end subroutine allocate_values

  subroutine deallocate_values()
    if (allocated(values)) deallocate(values)
  end subroutine deallocate_values
end module store
```

```python
allocate_values(3)
view = get_values()

# view is a borrowed view of native module storage.
view[0] = 5.0

copy = view.copy()
# copy is Python-owned and independent.

deallocate_values()
# Fortran deallocated the module variable. The borrowed view did not do it.
# Use copy when Python needs data after native deallocation/reallocation.
```

If native code later deallocates or reallocates `values`, previously returned
views are not automatically invalidated. The wrapper may expose
`allocate_values()` and `deallocate_values()` as ordinary wrapped routines, but
Python does not own the module variable. Calling those routines asks Fortran to
change its own storage.

Public scalar numeric, logical, and complex module variables are exposed
through `get_<name>()` and `set_<name>(value)` functions. The getter reads the
current native module storage, and the setter writes through to that storage.
The Python extension module does not own the scalar variable and does not add it
as a mutable module attribute.

Fortran `parameter` declarations are exported as Python constants when their
literal value is available. No setter is generated for a parameter, and
rebinding the Python module attribute does not change native Fortran state.

Private module variables are not exported and receive no getter or setter.
Explicitly saved public module variables follow the same accessor policy as
other module variables because Fortran module storage already has module
lifetime. Procedure-local `save` variables remain implementation details of the
wrapped procedure.

Pointer module variables follow the pointer policy. They are snapshot-copy or
blocked unless explicit metadata proves owner, lifetime, deallocation, shape,
dtype, contiguity, nullability, mutability, and aliasing behavior.

Generated calls hold the CPython GIL and x2py adds no independent lock for
module state. The GIL serializes ordinary calls from Python threads in one
interpreter, but callers must synchronize any concurrent native or external
access themselves. Common blocks remain native implementation details: wrapped
Fortran procedures may access them, but x2py does not expose common-associated
variables, model their layout, or assume ownership of their storage.

## Derived-Type Instances

A generated Python class for a Fortran derived type owns a native instance when
Python constructs or receives that object as a result.

`bind(C)` and `sequence` do not change the Python ownership or representation
policy. Every derived-type instance remains opaque to generated C code, and
component access goes through generated Fortran getters and setters. The bridge
does not infer struct padding, alignment, or component offsets. For a `value`
dummy, it passes the opaque instance to a generated Fortran bridge and lets the
Fortran compiler perform the value copy when calling the original procedure.
Direct memory views for compiler-validated interoperable `bind(C)` types are a
possible future optimization, not the default representation.

```fortran
type :: point
  real(8) :: x
  real(8) :: y
end type point

function make_point(x, y) result(p)
  real(8), intent(in) :: x
  real(8), intent(in) :: y
  type(point) :: p

  p%x = x
  p%y = y
end function make_point
```

```python
p = make_point(1.0, 2.0)

# p is wrapper-owned: the Python object owns a native point instance.
assert p.x == 1.0
p.x = 3.0
```

The Fortran function's local result is not the long-lived Python object. The
bridge must copy or move the produced value into wrapper-owned native storage
before the Fortran temporary goes out of scope. The Fortran temporary is then
destroyed by normal Fortran lifetime rules. The wrapper-owned copy is destroyed
later by the Python wrapper's deallocation path.

For a scalar derived-type `intent(out)` dummy, Python receives the same kind of
wrapper-owned object:

```fortran
subroutine make_point_out(p)
  type(point), intent(out) :: p

  p%x = 1.0_8
  p%y = 2.0_8
end subroutine make_point_out
```

```python
p = make_point_out()
# p is wrapper-owned.
```

For `intent(inout)`, Python passes an existing wrapper-owned instance and
Fortran mutates it in place:

```fortran
subroutine move_point(p, dx)
  type(point), intent(inout) :: p
  real(8), intent(in) :: dx

  p%x = p%x + dx
end subroutine move_point
```

```python
p = point()
p.x = 1.0
move_point(p, 2.0)
assert p.x == 3.0
```

No new owner is created for `intent(inout)`.

## Nested Derived-Type Components

Nested scalar derived-type fields are borrowed child wrappers. The parent owns
the native storage; the child wrapper keeps the parent alive.

```fortran
type :: particle
  type(point) :: origin
  real(8) :: mass
end type particle
```

```python
particle = make_particle()
origin = particle.origin

del particle

# origin keeps the owning wrapper alive.
origin.x = 4.0
```

The child wrapper does not destroy `origin`. It only references storage inside
the parent object. When the last parent or borrowed child reference is gone, the
parent wrapper's deallocation path destroys the whole native `particle`
instance once.

## Derived Types With Allocatable Array Fields

Allocatable fields are owned by the containing native instance. Field access is
a borrowed view, not a top-level copy-return value.

```fortran
type :: buffer
  real(8), allocatable :: values(:)
end type buffer

function make_buffer(n) result(b)
  integer, intent(in) :: n
  type(buffer) :: b

  allocate(b%values(n))
  b%values = 1.0_8
end function make_buffer
```

```python
b = make_buffer(3)
view = b.values

# view is borrowed from b.
assert view.base is b

view[0] = 9.0
# The native field b%values changed.

independent = view.copy()
# independent is Python-owned.
```

The containing wrapper owns the native `buffer` instance. Its generated destroy
helper releases `b%values` when the wrapper is deallocated. The NumPy view keeps
`b` alive, so this is valid:

```python
view = make_buffer(3).values

# view.base keeps the buffer wrapper alive.
np.testing.assert_allclose(view, np.ones(3))
```

If native code deallocates or reallocates `b%values` through a method while an
old view still exists, x2py does not currently invalidate the old view. Users
must copy when they need stable independent lifetime.

## Derived Types With Pointer Array Fields

Pointer fields do not have intrinsic ownership. A pointer component may target
module storage, another field, a dummy argument, a section, external memory, a
callee allocation, or nothing.

```fortran
type :: view_box
  real(8), pointer :: values(:)
end type view_box
```

The containing `view_box` object owns the pointer component variable, but it
does not necessarily own the target. Therefore the wrapper must not expose
`box.values` as a borrowed view by default.

The allowed default is:

- return `None` when the pointer is unassociated and nullability is allowed;
- return a Python-owned snapshot copy when association state, shape, dtype,
  contiguity, target owner, and deallocation obligations are known; or
- report a readiness blocker.

```python
box = make_view_box()
values = box.values

# If supported, values is a snapshot copy.
# Mutating it does not mutate box%values.
values[0] = 9.0
```

If a source type contains both storage and a pointer to that storage, source
syntax still is not enough:

```fortran
type :: self_view
  real(8), allocatable, target :: storage(:)
  real(8), pointer :: view(:)
end type self_view
```

The wrapper cannot assume `view => storage` for all instances and all future
mutations. A later explicit policy may say that `view` borrows from
`self.storage` with owner lifetime, but without that policy the component is
snapshot-or-block.

Destroying the containing wrapper does not deallocate pointer targets unless
explicit pointer policy says the containing object owns them and supplies the
correct release behavior. This prevents double-freeing borrowed targets and
also prevents silently leaking callee allocations by pretending no release is
needed.

## Derived Types With Strings

Scalar character fields, when supported, should be accessed as Python-owned
`str` values. Setting a character field copies data from Python into native
storage under the field's length, kind, truncation, and encoding policy.

```fortran
type :: named_point
  character(len=16) :: name
  real(8) :: x
end type named_point
```

```python
p = named_point()
p.name = "origin"

name = p.name
# name is a Python-owned str, not a borrowed character view.
```

Deferred-length character fields, mutable character buffers, and arrays of
characters require explicit policy before wrapper generation can expose them.

## Derived-Type Arrays

Arrays of derived types are blocked until their element ABI, construction,
destruction, aliasing, and view/copy policy are defined.

```fortran
type(point) :: points(10)
```

The wrapper must not pretend this is a NumPy structured array unless layout and
lifetime are proven. It must also not copy an object graph without defining how
each element and component is constructed and destroyed.

## Pointer Arrays

Pointer arrays use one policy regardless of whether they appear as procedure
results, module variables, or fields:

1. Pointer `intent(in)` array dummies may be call-local associations to
   Python-owned NumPy arrays.
2. Pointer array results and getters may be snapshot copies only when the
   wrapper knows association state, shape, dtype, contiguity, nullability,
   target owner, and deallocation obligations.
3. Pointer `intent(out)` and `intent(inout)` dummy arguments are blocked unless
   explicit policy defines the final association behavior and release rules.
4. Borrowed pointer views are future explicit-policy work, not the default.

```fortran
function selected_values(use_values) result(values)
  logical, intent(in) :: use_values
  real(8), pointer :: values(:)

  nullify(values)
  if (use_values) values => module_values
end function selected_values
```

```python
values = selected_values(True)

# If supported, values is a Python-owned snapshot of module_values.
# It is not a live view unless explicit borrowed-pointer policy says so.
```

## Destruction Rules

The destruction path depends on the owner:

| Owner | Example | Destruction |
| --- | --- | --- |
| Python-owned scalar or string | `count = get_count()` | Python destroys the object normally. |
| Python-owned NumPy array | copy-return or snapshot result | NumPy releases the data buffer or base capsule. |
| Caller-owned NumPy input/output | `fill(values)` | Caller keeps ownership; Python releases when references are gone. |
| Wrapper-owned derived instance | `p = make_point()` | Python wrapper `tp_dealloc` calls a generated Fortran-aware destroy helper. |
| Borrowed child wrapper | `origin = particle.origin` | Child keeps owner alive; child does not destroy native storage. |
| Borrowed allocatable field view | `view = buffer.values` | View keeps wrapper owner alive; view does not destroy native storage. |
| Native-owned module array | `view = get_values()` | Fortran module owns storage; wrapped native routines such as `deallocate_values()` allocate/deallocate. |
| Pointer target | `box.values` target | Not destroyed unless explicit pointer policy says who owns it and how to release it. |
| Call-local temporary | input conversion or bridge temporary | Released by the bridge before returning. |

## Public API Expectations

Docstrings should make ownership visible where it affects user behavior:

- `Ownership: Python-owned` for copy-return and snapshot arrays.
- `Ownership: Native-owned` for borrowed module storage.
- `Ownership: Wrapper-owned` for generated class instances when class-level
  documentation needs to describe destruction.
- Field docs should name borrowed lifetime, for example "borrowed from the
  containing wrapper".
- Pointer-backed properties must say whether they are snapshot copies or
  blocked. They must not look like ordinary borrowed fields.

Python users should not need to call generated destroy methods for normal
wrapper-owned objects. They may call native allocation/deallocation routines
that are part of the wrapped Fortran API, but those calls can invalidate
borrowed views according to the documented native routine behavior.

## Blocker Checklist

Readiness must block when any of these facts are missing for a requested
wrapper behavior:

- target owner;
- lifetime;
- deallocation policy;
- association or allocation state;
- shape and rank;
- dtype and kind;
- contiguity or stride behavior;
- mutability;
- aliasing;
- finalization behavior for owned derived instances; or
- conversion rules for strings or object arrays.

Blocking is the safe behavior. It prevents dangling views, double frees, leaks,
and mutations that appear to affect native state but only affect a copy.
