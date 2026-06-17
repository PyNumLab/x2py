# Wrapper Design Notes

This file records policy decisions that should wait until wrapper generation is
implemented. The parser and semantic layers should keep collecting source facts,
emitting blockers where policy is missing, and leaving wrapper behavior to the
wrapper phase.

Reference details live in:

- `docs/c_parser.md`
- `docs/fortran_parser.md`
- `docs/semantics.md`
- `docs/fortran_wrapper_checklist.md`

## Known Semantic Gaps To Track

These are source-language concepts that the parser or semantic layer can often
see today, but that still need a stronger `.pyi`, readiness, or wrapper policy
before generated wrappers should treat them as supported behavior.

### C Gaps

| Gap | Current risk | Proposed direction |
| --- | --- | --- |
| Function pointers and callbacks | The parser can capture function-pointer shape, but semantic conversion does not yet preserve a complete callable contract that wrappers can use safely. | Round-trip callback signatures as a first-class semantic callable form, such as a dedicated callback type or `Callable[[...], ...]` plus native callback metadata. Keep wrapper readiness blocked until lifetime, threading, exception, context-pointer, and unregister policy is supplied. |
| Pointer ownership and array extents | Raw pointers, pointer-to-pointer values, unknown extents, output buffers, and arrays of pointers are ambiguous without user policy. | Keep exact pointer topology in semantic IR. Require explicit `.pyi` ownership, borrow, output, shape, nullability, and copy/readback policy before projecting to Python containers or NumPy arrays. |
| Unions | `CUnion` identifies the native type, but it does not say which member is active or whether by-value union ABI is safe. | Continue representing named and anonymous unions explicitly with `CUnion`; require active-member/discriminant policy for high-level access. Prefer a compiled shim or target layout proof for by-value union calls; otherwise keep a readiness blocker. |
| Bitfields | Bit width is parser-visible, but Python field access needs target layout, signedness, padding, and read/write rules. | Preserve bit width, declared base type, containing aggregate, and layout-sensitive attributes. Generate access through a compiled C shim or target layout probe; block direct field projection when layout cannot be proven. |
| ABI and layout attributes | Attributes such as `packed`, `aligned`, `vector_size`, `stdcall`, `ms_abi`, asm labels, and compiler-specific qualifiers can change layout or calls. | Normalize ABI facts into semantic metadata on functions, fields, and classes. Let wrappers accept only the default ABI directly; use generated shims or explicit target support for non-default calling conventions and layout-sensitive attributes. |
| `volatile`, `_Atomic`, and extended scalar types | These require memory-order, side-effect, or target-specific scalar policy that ordinary scalar mapping cannot express. | Add explicit semantic wrappers or metadata for volatile and atomic access, defaulting to blocked wrapper readiness. Extend compiler probing for target scalar spellings such as `_BitInt`, `__int128`, and `_Float128` before assigning stable dtypes. |

### Fortran Gaps

| Gap | Current risk | Proposed direction |
| --- | --- | --- |
| Procedure pointers and dummy procedures | A broad `Procedure` type loses enough signature and lifetime information that wrappers cannot safely call or receive callbacks. | Resolve abstract interface signatures into a first-class semantic callable form. Preserve procedure pointer, optional, pass-through, and callback lifetime facts; block wrapper generation until call direction and ownership policy are explicit. |
| `character(len=...)` and character ABI | Mapping all character forms to `String` loses length, kind, hidden length arguments, fixed buffers, and `bind(c)` byte-string behavior. | Represent character storage with length expression, kind, assumed-length status, array shape, and C-interoperability metadata. Require explicit encoding, termination, copy, and hidden-length ABI handling in wrapper policy. |
| Polymorphic `class(...)` and unlimited polymorphism | Declared base types do not fully capture dynamic type, allocation, dispatch, or `select type` behavior. | Distinguish declared type from dynamic type in semantic metadata. Treat polymorphic dummy arguments and allocatable polymorphic results as blocked until wrapper policy defines accepted dynamic types and allocation behavior. |
| Advanced type-bound procedure details | Default `pass`, explicit `pass(name)`, `nopass`, concrete type-bound generics, and concrete type-bound operators are preserved and wrapped. Finalizers, deferred bindings, overrides, and polymorphic inheritance still need stronger contracts. | Preserve complete binding metadata on semantic classes. Type-bound generics and operators use explicit `.pyi` `@overload("specific")` links and generated C-extension dispatch; unresolved targets are readiness blockers. |
| Derived-type layout and interoperability | `sequence`, `bind(c)`, common ABI expectations, and component layout are wrapper-critical but not yet a complete runtime contract. | Add explicit Fortran derived-type markers and metadata for `bind(c)`, `sequence`, component order, and interoperable layout. Use compiler layout probes or generated Fortran/C shims before passing derived types by value or exposing memory views. |
| Pointer and allocatable ownership | Borrowed zero-copy views are supported for allocatable derived-type fields and target-backed module arrays. Allocatable array results and `intent(out)` dummies use copy-return NumPy-owned storage. Pointer association, allocatable `intent(inout)` replacement, and stale-view invalidation remain policy decisions. | Keep pointer/allocatable, rank, bounds, `intent`, `target`, and contiguity facts in semantic IR. Expose supported fields/module arrays as borrowed views returning `None` when unallocated. Copy allocatable array results and `intent(out)` dummies before returning to Python. Block allocatable `intent(inout)` until replacement policy is defined. |
| Assumed-rank, assumed-type, and optional descriptor-heavy arguments | Descriptors such as `dimension(..)` and `type(*)` can accept many native shapes that Python cannot infer safely. | Represent descriptor category, rank constraints, element type availability, optional presence, and contiguity. Generate wrappers only for explicit accepted rank/dtype policies or through backend shims that validate descriptors. |
| Generic interfaces and operators | Named generics, defined operators, named operators, and defined assignment now preserve explicit concrete-target links. Python cannot intercept `=`, arbitrary named operators, or infer safe in-place mutation. Polymorphic inheritance is not represented by Python C-type inheritance. | Use Python data-model slots for intrinsic operators, `operator_name`/`r_operator_name` methods for named operators, and mutating `assign` methods for defined assignment. Keep exact dtype/rank/extension-class dispatch and reject indistinguishable signatures during generation. |
| Coarrays, teams, events, and directive-driven device/offload behavior | These introduce parallel runtime or device-memory semantics outside normal host wrappers. | Treat as out of the initial wrapper scope. Preserve diagnostics where detected and require a separate runtime design before claiming support. |

## Settled Scope

The C frontend is a declaration and signature parser for wrapper-relevant
interfaces. It does not need to become a full compiler-grade C implementation.
The supported target is the API surface needed to produce or validate wrappers:
functions, variables, structs, enums, typedefs, constants, arrays, pointers,
callbacks, and the metadata needed for readiness decisions.

Generated CPython extension builds copy their bundled C/Python support sources
into an `x2py_runtime/` directory inside the build output. The generated C
extension includes `x2py_runtime/python_runtime.h`. These files are an
implementation detail of the generated extension, but their names are
intentionally x2py-specific so they do not look like user source or a generic
C wrapper.

Generated CPython extensions should expose useful NumPy-style docstrings on the
Python-visible API. The CPython wrapper layer owns this generation because it has
the final callable signatures, hidden projection decisions, class/property
layout, and return conversion policy. These docstrings are for Python users and
should stay compact. Use NumPy-style sections with short type headers such as
`x : ndarray[float64]` and `result : ndarray[float64] or None`. Put only the
facts that are known and useful: rank for arrays, shape only when constrained or
known, layout for rank greater than one as `F-contiguous` or `C-contiguous`,
intent for arguments, mutation for `intent(out)`/`intent(inout)`, ownership
when it matters using `Ownership: Python-owned` or `Ownership: Native-owned`,
and when `None` can be returned. Do not emit placeholder unknowns such as
runtime-determined shape or scalar rank. Avoid long
wrapper-internal explanations. Class docstrings should
summarize fields and methods. Get/set descriptor docstrings should describe
class attributes, including borrowed view lifetimes for allocatable and
pointer-backed arrays. Module variables exposed through getter functions should
document the getter, since CPython modules do not provide a portable
per-variable descriptor docstring for plain module attributes.

Verbose wrapper builds should print the exact compiler command lines they run,
not only the source or target being compiled. The printed command should be
shell-quoted so users can copy it to reproduce object compilation, generated
wrapper compilation, runtime support compilation, and final shared-library
linking.

Normal C parsing uses a real compiler preprocessor first. Macro expansion,
conditional compilation, token paste, stringify, and include resolution belong
to that compiler preprocessing step. The parser should consume the resulting C
translation unit and preserve provenance where useful.

Raw macro-generated declarations are not a separate parser target. If a macro
creates a declaration, that declaration should be visible after preprocessing:

```c
#define DECLARE_SCALE(T) void scale_##T(T *values, int n)

DECLARE_SCALE(double);
```

After preprocessing, the parser should see the expanded declaration and does not
need to understand `DECLARE_SCALE` itself.

C compiler extensions are supported when they appear in C declarations that we
need for wrappers. Unsupported or policy-sensitive extension semantics can still
be represented as diagnostics or readiness blockers. C++ is a separate frontend
problem; C-compatible declarations that survive C preprocessing remain C work.

## Wrapper Decisions To Revisit

### ABI Boundary

We already collect wrapper-relevant declaration facts. The open wrapper-phase
question is how much exact ABI behavior the generated wrapper must model itself
versus delegate to a compiled shim or backend compiler.

Example:

```c
struct Packet {
    unsigned tag : 3;
    unsigned flags : 5;
    double payload;
} __attribute__((packed));

void send_packet(struct Packet packet);
```

The parser can preserve struct members, bitfield facts, attributes, and the
function signature. The wrapper phase must decide whether this can be passed
directly, needs a generated C shim, or should be blocked because exact layout or
calling convention is not safe enough.

### Pointer Ownership And Lifetime

The wrapper must not infer ownership silently. A pointer can mean borrowed
storage, owned allocation, mutable in-place data, read-only data, optional data,
or a sentinel-terminated buffer. The user must provide the missing policy in the
wrapper contract.

Example:

```c
double *make_values(size_t n);
void free_values(double *values);
void scale(double *values, size_t n);
const double *borrow_values(void);
```

These signatures alone do not prove who owns the memory, how long it lives, or
whether Python should copy, borrow, mutate, or free it. The wrapper design
should make that explicit in `.pyi` or another policy layer.

### Pointer, Size, And Output Projections

Explicit projections are allowed. Automatic hidden projection is not. If a C API
uses pointer/size pairs or output buffers, the wrapper can expose a Pythonic
shape only when the user supplies the projection policy, such as through
`@native_call`.

Example:

```c
int read_samples(double *out, size_t capacity, size_t *written);
```

The exact native contract is `out`, `capacity`, and `written`. A wrapper could
project this to `list[float]` or `np.ndarray`, but only after the user says how
large the output should be, who allocates it, how errors are handled, and whether
the result is copied or shared.

### Callback Policy

Callback wrappers need more than the function pointer type. The wrapper must
know whether the native library stores the callback, which Python object keeps it
alive, whether callbacks may happen on native threads, how exceptions propagate,
how `void *ctx` pairs with the callback, and how registration/unregistration
works.

Example:

```c
typedef void (*event_callback)(int code, void *ctx);

void register_callback(event_callback callback, void *ctx);
void unregister_callback(event_callback callback, void *ctx);
```

The parser can record the callback signature. The wrapper phase must decide the
lifetime, context pairing, threading, exception, and unregistration behavior
before generating a Python API.

### Fortran Allocatable And Pointer Reassociation

Fortran allocatable and pointer dummy arguments can replace the storage visible
to the caller. The parser and semantic IR should preserve allocatable/pointer
facts, but wrapper generation must decide Python replacement and lifetime
behavior.

Example:

```fortran
subroutine build_grid(x, n)
  integer, intent(in) :: n
  real, allocatable, intent(out) :: x(:)
end subroutine
```

The Fortran procedure may allocate or reallocate `x`. The wrapper phase must
decide whether Python receives a new array, whether an existing object can be
replaced, who owns the allocation, and how deallocation is handled.

The settled subset is narrower: allocatable derived-type fields and
`target`-backed module allocatable arrays can be exposed as borrowed NumPy
views. Fortran owns the storage. `None` represents an unallocated value. A view
keeps its containing derived-type wrapper alive, but x2py does not track views
or invalidate them when native code reallocates or deallocates the storage.
Users must call `.copy()` when they need independent lifetime. Module
allocatable arrays require the native `target` attribute because the bridge
uses `c_loc`; otherwise readiness reports a blocker rather than generating a
copying fallback.

Pointer reassociation has similar policy questions:

```fortran
subroutine attach_view(x)
  real, pointer, intent(out) :: x(:)
end subroutine
```

The wrapper must define whether `x` becomes a borrowed view, an owned Python
object, or a blocked interface unless the user supplies more policy.

### Fortran Assumed-Rank Wrappers

Assumed-rank arguments preserve source facts today, but wrapper behavior should
wait for a dedicated design. The wrapper must decide how Python rank-polymorphic
inputs map to the native descriptor and what ranks, contiguity, dtype, and shape
contracts are accepted.

Example:

```fortran
subroutine inspect(x)
  real, intent(in) :: x(..)
end subroutine
```

The semantic layer can record that `x` is assumed-rank. The wrapper phase must
decide whether to generate one rank-polymorphic Python entrypoint, generate rank
specializations, require explicit `.pyi` annotations, or block the interface
until the contract is refined.
