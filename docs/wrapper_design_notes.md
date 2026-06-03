# Wrapper Design Notes

This file records policy decisions that should wait until wrapper generation is
implemented. The parser and semantic layers should keep collecting source facts,
emitting blockers where policy is missing, and leaving wrapper behavior to the
wrapper phase.

Reference details live in:

- `docs/c_parser.md`
- `docs/fortran_parser.md`
- `docs/semantics.md`

## Settled Scope

The C frontend is a declaration and signature parser for wrapper-relevant
interfaces. It does not need to become a full compiler-grade C implementation.
The supported target is the API surface needed to produce or validate wrappers:
functions, variables, structs, enums, typedefs, constants, arrays, pointers,
callbacks, and the metadata needed for readiness decisions.

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
