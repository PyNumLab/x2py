# Semantic Multilanguage Wrapper and Interoperability Runtime

# Vision

The goal of this project is to create a modern interoperability framework capable of wrapping and connecting libraries written in multiple native languages through a unified semantic API layer.

The system should:

* wrap native libraries from:

  * Fortran
  * C
  * C++
  * Rust
  * CUDA
  * and potentially more languages later
* expose clean Python APIs
* support semantic interoperability between different native runtimes
* support automatic coercions/conversions
* support runtime constraints
* support zero-copy array interoperability when possible
* avoid compiler dependence whenever possible
* avoid forcing users to modify native code
* avoid the limitations of SWIG/f2py-style systems
* support wrapping libraries even when source code is unavailable

The project is not merely a wrapper generator.

It is a:

* semantic wrapper compiler
* interoperability runtime
* runtime coercion engine
* language-independent semantic API system

---

# Core Philosophy

The most important architectural decision is:

> The semantic API layer is the source of truth.

NOT:

* parser ASTs
* compiler internals
* ABI details
* native language syntax

The system separates:

| Concern           | Responsibility               |
| ----------------- | ---------------------------- |
| Semantic API      | `.pyi`-style interface layer |
| Runtime coercions | conversion registry          |
| Constraints       | runtime validation           |
| Native ABI        | backend adapters             |
| Source parsing    | optional helper              |

This separation is the foundation of the whole architecture.

---

# Why Existing Systems Are Not Enough

## SWIG

SWIG is:

* parser-centric
* macro-heavy
* difficult to debug
* weak for scientific arrays
* poor for runtime semantics
* poor for modern interoperability

It also becomes difficult to maintain when:

* ownership becomes complex
* NumPy arrays are involved
* GPU arrays are involved
* runtime conversions are needed
* API remapping becomes advanced

---

## f2py

f2py is:

* Fortran-specific
* procedural
* compiler/build-centric
* not semantic-runtime oriented
* weak for object systems
* weak for heterogeneous runtimes

---

## pybind11

pybind11 is excellent for:

* clean bindings
* modern Python APIs

But:

* bindings are handwritten
* there is no semantic interoperability layer
* no runtime coercion model
* no language-independent abstraction

---

# High-Level Architecture

The architecture is composed of multiple layers.

```text
Native libraries/sources
        ↓
Optional parser frontends
        ↓
Canonical semantic interface layer (.pyi)
        ↓
Semantic IR
        ↓
Runtime coercion system
        ↓
Backend adapters
        ↓
Generated CPython extension
        ↓
Python API
```

---

# Canonical Semantic Interface Layer

The `.pyi`-style interface file is the central abstraction.

It defines:

* semantic APIs
* classes
* functions
* methods
* semantic types
* allowed coercions
* constraints
* ownership semantics
* API remapping

This layer is:

* language-independent
* parser-independent
* editable
* human-readable
* stable

The native parser is NOT the source of truth.

The `.pyi` interface file is.

---

# Example Basic Wrapper

Suppose native Fortran code contains:

```fortran
module sparse_mod

  type :: sparse_matrix
  end type

contains

  subroutine sparse_multiply(A, x)
  end subroutine

end module
```

The semantic interface may look like:

```python
@bind("sparse_matrix")
class SparseMatrix:

    @bind("create_sparse")
    @constructor
    def __init__(self, nrows: int, ncols: int): ...

    @bind("sparse_multiply")
    def multiply(self, x): ...
```

This allows:

* semantic API redesign
* Pythonic APIs
* decoupling native APIs from exposed APIs

Without changing native source code.

---

# API Projection

The framework allows transforming ugly procedural APIs into clean object-oriented APIs.

Example:

Native:

```fortran
call sparse_multiply(A, x)
```

Exposed Python API:

```python
A.multiply(x)
```

This is called:

> semantic API projection.

---

# Semantic Types

Semantic types represent:

> what an object means conceptually.

NOT:

* its memory layout
* its native language representation
* its ABI representation

Examples:

* `Float64Matrix`
* `SparseMatrix`
* `Tensor3D`
* `CSRMatrix`
* `ComplexVector`

Semantic types are language-independent.

---

# Important Distinction: API vs ABI

## API

API describes:

* functions
* methods
* semantic behavior
* user-facing operations

Example:

```python
def solve(A)
```

---

## ABI

ABI describes:

* symbol names
* calling conventions
* memory layout
* array descriptors
* stack/register usage
* compiler-specific representations

Example:

```text
__solver_mod_MOD_solve
```

The framework explicitly separates:

```text
Semantic API
    ≠
Native ABI
```

This is a core architectural principle.

---

# Coercions

Coercions define:

> how one type can be adapted into another.

Examples:

* `int -> float`
* `np.ndarray -> Float64Matrix`
* `TorchTensor -> Float64Matrix`

---

# Declaring Coercions

The semantic interface can declare allowed coercions.

Example:

```python
def func(a: float[From(int)]): ...
```

Meaning:

```text
int -> float
```

is an allowed coercion.

---

# Matrix Example

```python
def solve(
    A: Float64Matrix[
        From(np.ndarray),
        FortranContiguous,
        Writable,
    ]
): ...
```

This means:

* target semantic type:

  * `Float64Matrix`
* allowed coercion:

  * `np.ndarray -> Float64Matrix`
* required constraints:

  * Fortran contiguous
  * writable

---

# Constraints

Constraints define:

> requirements the final adapted representation must satisfy.

Constraints are NOT coercions.

Examples:

* `Positive`
* `Writable`
* `FortranContiguous`
* `CPUResident`
* `Shape(N, N)`
* `Aligned(64)`

---

# Important Concept Separation

The architecture separates:

| Concept         | Meaning                              |
| --------------- | ------------------------------------ |
| Semantic type   | what the object IS                   |
| Coercion        | how another type becomes it          |
| Constraint      | requirements on final representation |
| Backend adapter | semantic object → ABI representation |

This separation is fundamental.

---

# Runtime Coercion Registry

Allowed coercions declared in `.pyi` are implemented through a runtime coercion registry.

Example:

```python
@coercion(np.ndarray, Float64Matrix)
def ndarray_to_matrix(A):
    ...
```

This registers:

```text
np.ndarray -> Float64Matrix
```

inside the runtime registry.

---

# Runtime Dispatch Flow

Suppose:

```python
solve(np.ones((10,10)))
```

Runtime pipeline:

```text
Input object
    ↓
Find semantic target type
    ↓
Find coercion path
    ↓
Apply coercion
    ↓
Validate constraints
    ↓
Backend adapter
    ↓
Native ABI call
```

---

# Coercion Graphs

The runtime should support composed coercions.

Example:

```text
TorchTensor
    ↓
np.ndarray
    ↓
Float64Matrix
```

The runtime can automatically infer:

```text
TorchTensor -> Float64Matrix
```

through graph traversal.

---

# Coercion Metadata

Coercions may contain metadata.

Example:

```python
@coercion(
    np.ndarray,
    Float64Matrix,
    implicit=True,
    cost=1,
    zero_copy=True,
)
def ndarray_to_matrix(A):
    ...
```

Possible metadata:

* implicit/explicit
* safe/unsafe
* cost
* zero-copy
* ownership
* device awareness

---

# Semantic Runtime Objects

The runtime should internally use semantic runtime objects.

Example:

```python
class Float64MatrixObject:
    ptr
    shape
    strides
    owner
    device
```

These objects are:

* language-independent
* runtime-oriented
* semantic representations

NOT:

* NumPy arrays
* Fortran descriptors
* Eigen matrices

---

# Backend Adapters

Backend adapters convert:

```text
Semantic runtime object
    ↓
Native ABI representation
```

Examples:

* Fortran descriptors
* Eigen maps
* C structs
* CUDA tensors

---

# Wrapping Libraries Without Source Code

The framework should support wrapping:

* `.so`
* `.dll`
* static libraries

without source code.

Users provide:

* semantic `.pyi`
* coercions if needed
* optional metadata

No source parsing required.

---

# Optional Parser Frontends

Parsers are helpers.

NOT the foundation.

Possible parsers:

* Fortran parser
* C parser
* C++ parser
* Rust parser

Their role:

* generate starter `.pyi`
* synchronize declarations
* help users bootstrap wrappers

The semantic interface remains canonical.

---

# Mixed-Language Libraries

The framework should support libraries implemented in multiple languages simultaneously.

Example:

* Fortran numerical kernels
* C runtime layer
* C++ object systems
* Rust runtime safety
* CUDA kernels

All unified through:

* semantic types
* coercions
* backend adapters

---

# Example Mixed-Language Workflow

Suppose:

## Fortran solver

```fortran
subroutine solve_system(A,b)
```

## C++ mesh

```cpp
class Mesh {
public:
    void refine();
};
```

## Rust optimizer

```rust
extern "C" fn optimize(...)
```

The Python API may expose:

```python
class Solver:
    def solve(self, A, b)

class Mesh:
    def refine(self)

def optimize(x)
```

The user does not care about implementation language.

---

# Ownership and Lifetime Management

The runtime must manage:

* borrowed references
* owned references
* zero-copy views
* temporary coercions
* destruction policies

This is one of the hardest parts of the system.

---

# Zero-Copy Interoperability

The runtime should avoid unnecessary copies whenever possible.

Examples:

| Conversion              | Strategy  |
| ----------------------- | --------- |
| NumPy F-order → Fortran | zero-copy |
| NumPy → Eigen::Map      | zero-copy |
| Torch CUDA → CPU array  | copy      |

The runtime should optimize coercion paths automatically.

---

# Scientific Computing Focus

The architecture is especially useful for:

* HPC
* FEM
* CFD
* climate models
* tensor runtimes
* numerical libraries
* GPU computing
* scientific Python ecosystems

because these domains already contain:

* mixed-language systems
* difficult interoperability
* legacy Fortran/C++ code
* array-heavy APIs

---

# CPython Extension Backend

The project should generate custom CPython extensions directly.

Reasons:

* full control over runtime
* full control over arrays
* full control over coercions
* better diagnostics
* better ownership handling
* better performance

The project should NOT fundamentally depend on:

* SWIG
* ctypes
* pybind11

although optional backends may exist later.

---

# Diagnostics

Diagnostics are extremely important.

The framework should provide:

* clear coercion errors
* constraint validation errors
* coercion trace visualization
* ownership diagnostics
* backend dispatch diagnostics

Much better than typical SWIG/f2py errors.

---

# Plugin Ecosystem

Third-party ecosystems should be able to register:

* semantic types
* coercions
* constraints
* backend adapters

This allows:

* NumPy support
* Torch support
* JAX support
* CUDA support
* sparse matrix ecosystems
* domain-specific runtimes

---

# Long-Term Goal

The final system becomes:

* a semantic wrapper compiler
* a runtime interoperability framework
* a mixed-language scientific runtime layer
* a semantic coercion engine
* a modern replacement for old wrapper systems

The key innovation is:

```text
Semantic interoperability
instead of
parser-centric wrapper generation
```

---

# Final Summary

The architecture is built around:

```text
Semantic API
        ↓
Coercions
        ↓
Constraints
        ↓
Semantic runtime objects
        ↓
Backend adapters
        ↓
Native execution
```

The project focuses on:

* clean semantic APIs
* runtime interoperability
* mixed-language support
* scientific computing
* extensibility
* high performance
* language independence

while avoiding:

* parser dependence
* compiler dependence
* rigid ABI-centric designs
* old wrapper system limitations.

