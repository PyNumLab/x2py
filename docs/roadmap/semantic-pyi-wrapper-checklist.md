---
title: Semantic .pyi Wrapper Checklist
audience: developers, maintainers
prerequisites: semantic .pyi format, Fortran wrapper guide
related: ../reference/semantic-pyi-format.md, index.md
status: active-roadmap
---

# Semantic `.pyi` Wrapper Checklist

This checklist tracks the path from semantic `.pyi` files to a fully editable
wrapper contract. A `.pyi` file may be generated from source as a starter
contract or written by the user directly. After that point the `.pyi` file is
the source of truth for the Python wrapper API.

Every `.pyi` wrapper build accepts exactly one entry contract. That entry may
import any number of module leaves or contract fragments through relative
imports. Imported files are discovered recursively; they are not additional
CLI or Python API inputs. Multiple positional `.pyi` inputs and contract
directories are intentionally unsupported.

The end state is that every runtime scenario covered by `tests/wrapper` is
exercised through three build paths:

1. **Source path**: build directly from one or more ordered Fortran sources.
2. **Generated-contract path**: generate the module-aligned `.pyi` files from
   those sources with `--pyi`, then build from the unmodified `.pyi` files plus
   native artifacts. This path must expose the same Python API and runtime
   behavior as the source path.
3. **Modified-contract path**: copy or extend the generated `.pyi` files with
   user-authored visibility, validation, ownership, lifetime, error, or other
   wrapper contracts, then build from the modified `.pyi` files plus the same
   native artifacts. This path must apply the documented edits while preserving
   unaffected behavior.

Equivalence means the same public API and observable runtime behavior; generated
extension binaries are not required to be byte-for-byte identical. Native
source is optional in the second and third paths. Tests may use source to create
the baseline `.pyi` and native artifacts, but `.pyi`-driven wrapper generation
must not reparse source to reconstruct the Python API.

Native implementation sources may still be supplied explicitly as build inputs.
In that mode x2py compiles them without using them as a semantic input: the
entry `.pyi` remains the sole source of truth for the Python API. Precompiled
objects and libraries remain supported and may be mixed with native sources in
one extension-level native build plan.

The remaining work is centralized below in implementation order. Complete each
stage and its focused runtime evidence before starting the next stage. When an
item is complete, move its checked acceptance criterion to the completed
evidence section instead of leaving completed and incomplete work interleaved.

## Remaining implementation queue

Only unfinished work belongs in this section. The ordering is intentional:
contract output and build models stabilize first, feature parity builds on that
foundation, editable policy follows unmodified parity, and library-scale tests
exercise the completed build surface last.

### Stage 5 — Full generated-contract runtime parity

- [x] Allocatable and pointer module variables round-trip their target,
  lifetime, nullability, shape, and transfer contracts.
- [x] Generic interfaces and overload sets rebuild from `.pyi` with the same
  dispatch table, concrete target links, error messages, and Python-visible
  names as the source-driven build.
- [x] Derived-type fields, methods, inheritance metadata, constructors,
  finalizers, borrowed children, and owned result behavior rebuild from `.pyi`
  without consulting the original source declarations.
- [x] Array dtype, rank, shape, order, stride, lower-bound, writeability,
  alignment, byte-order, and zero-extent validation rebuild from `.pyi` with the
  same runtime failures and success cases.
- [x] Character kind, deferred/allocatable storage, fixed buffer, and
  copy-in/copy-out behavior rebuild from `.pyi` with the same Python string
  contract.
- [x] Runtime policies from `.pyi`, including `@hold_gil` and `@raises(...)`,
  are honored by generated C bindings.
- [x] Callback contracts rebuild from `.pyi` with the same call-scoped lifetime,
  GIL handling, exception failure mode, array validation, and derived-type
  conversion behavior.
- [x] Every parity-eligible runtime fixture in `tests/wrapper` has a checked
  generated `.pyi` package fixture under its consuming subject, uses the shared
  source/generated-contract assertion body, and rebuilds without reparsing
  native source.

### Stage 6 — Editable contract semantics

- [ ] Every editable wrapper feature has a modified `.pyi` fixture and a third
  build whose runtime assertions prove the intentional contract change.
- [ ] Removing a public function, method, variable, constructor, overload
  candidate, or class member from `.pyi` removes it from the generated Python
  API.
- [ ] Marking a declaration `@private` or `private[...]` keeps it available as a
  wrapper input when needed internally but hides it from the public Python
  surface.
- [ ] User-private declarations remain printable and loadable, while ordinary
  source-private declarations remain omitted from generated `.pyi` files.
- [ ] `@bind(...)`, `@overload(...)`, and `@native_call(...)` express renamed or
  projected native calls without source reparsing.
- [ ] Function and method contracts express validation, coercion, ownership,
  lifetime, shape, and error-status projection policy consumed by readiness and
  wrapper generation.
- [ ] Contradictory or incomplete edited contracts fail during readiness or
  wrapper generation with precise diagnostics instead of silently falling back
  to source-derived behavior.

### Stage 7 — Replayable JSON, native compilation, and Makefiles

The intended direct workflow is:

```bash
python3 -m x2py contracts/module.pyi \
  --wrap \
  --native-fortran-source native/module.f90 \
  --native-fortran-flag=-O3 \
  --native-fortran-flag=-march=native \
  --native-object vendor/support.o \
  --native-library lapack \
  --out-dir build/module \
  --makefile \
  --json
```

Makefile mode writes `x2py-build.json` first and generates `Makefile.x2py` only
from that normalized manifest. The replay workflows are:

```bash
python3 -m x2py --build-manifest build/module/x2py-build.json --wrap
python3 -m x2py --build-manifest build/module/x2py-build.json --makefile
```

- [ ] Python API `.pyi` builds accept the same output directory, naming,
  Makefile, verbose, and strict-wrapper-name controls as source-driven builds.
- [ ] A deterministic, schema-versioned wrapper build manifest stores the entry
  `.pyi`, recursively discovered contract paths, extension identity, output
  policy, compiler configuration, ordered native compilation units, and native
  link plan as separate structured fields. Relative paths are resolved relative
  to the manifest.
- [ ] Repeated `--native-fortran-source` inputs compile opaque native
  implementation sources in caller-provided dependency order without using
  them to reconstruct the Python API. Produced objects and module files become
  inputs to the extension build plan.
- [ ] Repeated `--native-fortran-flag` inputs preserve optimization, target,
  preprocessing, module, and other caller-supplied compiler options while x2py
  still adds required flags such as position-independent code. Compiler
  selection, flag ordering, output objects, and module directories are recorded
  for replay.
- [ ] Native implementation sources, prebuilt objects, archives, direct shared
  libraries, and named libraries can be mixed in one build. Changing compiler
  flags never changes the `.pyi`-defined Python API or triggers semantic source
  reparsing.
- [ ] `--json` build output includes the normalized manifest and resulting
  artifacts. Makefile mode also writes `<out-dir>/x2py-build.json`; serialization
  is stable enough for exact fixtures and reviewable build changes.
- [ ] `--build-manifest PATH --wrap` validates and executes a saved manifest.
- [ ] `--build-manifest PATH --makefile` regenerates the Makefile without
  requiring positional contracts or repeated native flags.
- [ ] `Makefile.x2py` is a deterministic projection of `x2py-build.json`, with
  no unrecorded compiler or linker inputs. It tracks the manifest, complete
  `.pyi` import graph, and native implementation sources as dependencies and
  preserves compile and link order.
- [ ] Explicit linker arguments support static archive groups, repeated
  archives, whole-archive policy, and required platform-specific link flags.
- [ ] Runtime shared-library lookup is reproducible through recorded rpath or a
  documented loader-path policy, including transitive shared dependencies.

### Stage 8 — Library-scale and mixed-bundle evidence

- [ ] Several contracts imported by one entry resolve from one archive or shared
  library, and one entry resolves from several objects and libraries.
- [ ] Module procedures work with separately supplied `.mod` directories;
  standalone `@external` procedures work without `.mod` inputs.
- [ ] A mixed bundle containing native modules and standalone external
  procedures exposes module members below their namespaces and externals at the
  extension root.
- [ ] The BLAS/LAPACK-style path is tested independently with a static archive,
  a direct shared-library path, and `--native-library` plus
  `--native-library-dir`.
- [ ] Mixed object, archive, direct shared-library, and named-library inputs
  preserve dependency-safe link order and resolve every native symbol.
- [ ] Static archive dependency order, repeated archives or linker groups for
  cyclic dependencies, and required transitive libraries have runtime tests.
- [ ] Missing symbols, duplicate definitions, incompatible artifacts, missing
  `.mod` files, and unavailable dependent shared libraries produce direct
  diagnostics without any source fallback.

## Completed evidence

### Stage 1 — Searchable Test Layout, Contract Output, And Fixtures

Runtime wrapper tests are organized by stable subjects under
`tests/wrapper/fortran/`: `build_from_source/`, `build_from_pyi/`,
`multiple_files/`, `external_routines/`, `real_libraries/`,
`edit_pyi_contracts/`, `arrays/`, `scalars/`, `function_calls/`,
`strings/`, `derived_types/`, `callbacks/`, `module_state/`,
`runtime_behavior/`, `naming/`, and `layout_rules/`.

- [x] Wrapper test modules live under the stable subject directories above,
  using descriptive filenames and subject README files. The index is
  `tests/wrapper/fortran/README.md`.
- [x] Native wrapper source fixtures live under the shared
  `tests/data/fortran/wrapper/` corpus. The wrapper test tree contains no
  Fortran source files.
- [x] Runtime wrapper tests resolve native fixtures through
  `tests/wrapper/fortran/_support.py`, so moved tests no longer depend on
  colocated source fixtures.
- [x] Runtime `.pyi` contracts stay under the consuming subject's
  `contracts/<case>/` tree. Current checked fixtures include
  `build_from_pyi/contracts/runtime_abi/fruntime_abi_f90.pyi`,
  `build_from_pyi/modified_contracts/basic_subroutine/flatten_m1.pyi`,
  `build_from_pyi/modified_contracts/basic_subroutine/alias_increment.pyi`,
  and `build_from_pyi/invalid_contracts/projection_metadata/incomplete_native_call.pyi`.
- [x] Generated `.pyi` packages are checked fixtures. Runtime wrapper contract
  packages live under
  `tests/wrapper/fortran/<subject>/contracts/<case>/`; explicit
  `--pyi --out` package-shape fixtures that do not compile wrappers live under
  `tests/pyi/fixtures/wrapper_contracts/`. Refresh is explicit through
  `WRAPPER_UPDATE_PYI_FIXTURES=1`.
- [x] Modified runtime fixtures use `.pyi`, record their intentional difference
  in the fixture text, and have runtime assertions for both the changed export
  contract and unaffected native behavior.
- [x] `.py` files are rejected as semantic `.pyi` contract inputs by the Python
  API.
- [x] `tests/pyi/fixtures/general/` remains the canonical exact `.pyi`
  generation-regression suite and is not used for compiled runtime contract
  fixtures.
- [x] Explicit Fortran `--pyi --out` package-shape fixtures that do not compile
  runtime wrappers live under `tests/pyi/fixtures/wrapper_contracts/`.
- [x] `tests/wrapper/CHECKLIST_COVERAGE.md` maps roadmap subjects to exact test
  paths.
- [x] `tests/wrapper/fortran/layout_rules/test_wrapper_guide_layout.py`
  enforces the subject tree, README fields, checklist routing, shared native
  fixture data, runtime contract placement, and stale-path rejection.
- [x] Explicit Fortran `--pyi --out` output writes contract packages and rejects
  ambiguous single-file `.pyi` targets so the one-module-per-file rule is
  preserved.

### Stage 2 — Structured Native Build Model

`WrapperBuildResult.native_build_plan` records the extension-level native
implementation build plan separately from semantic `sources`.

- [x] The build result records one structured, extension-level native build plan
  separately from semantic contract paths. The plan distinguishes native
  compilation units, produced objects, prebuilt artifacts, module/include
  directories, library directories, and ordered link items instead of flattening
  them into strings.
- [x] One ordered native-link representation preserves interleaving across
  objects, archives, direct shared libraries, named libraries, and explicit
  linker arguments instead of grouping inputs in a way that changes linker
  semantics.
- [x] Source-driven wrapper builds record caller-supplied native source
  compilation units, produced objects, module/include directories, and object
  link items in `NativeBuildPlan`.
- [x] `.pyi` wrapper builds record semantic contract paths in `sources` and
  caller-supplied native artifacts, include/module directories, library
  directories, and ordered link items in `NativeBuildPlan`.
- [x] The lower compiler object dependency model preserves caller order for
  native object inputs instead of converting them through an unordered set.
- [x] Documentation explains the native build plan with five examples covering
  source builds, `.pyi` object builds, object/archive ordering, direct shared
  libraries, and explicit linker-argument representation.

### Stage 3 — Multi-Source Combined Contract Generation

Explicit Fortran `--pyi --out PATH` now treats `PATH` as the generated contract
package itself. The package entry is `PATH/__init__.pyi`; native module leaves
sit directly under `PATH`.

- [x] Source, generated-contract, and modified-contract parity builds use the
  same extension name and native namespace structure. Only documented Python
  export policy or wrapper contracts may differ.
- [x] Multiple ordered native sources generate one combined contract package
  without losing native imports, dependency objects, cross-module types, source
  order, link order, or extension identity.
- [x] The requested output directory is the contract package itself. It contains
  one `__init__.pyi` entry and one flat `<fortran-module>.pyi` leaf per native
  module; generation adds neither a `combined_extensions/` directory nor
  per-source subdirectories.
- [x] For two ordered sources that each define two native modules,
  `--pyi --out contracts` writes four module leaves directly under `contracts/`
  plus `contracts/__init__.pyi`. The entry imports all four leaves and is the
  sole wrapper input. With no external dependency stubs, these are the only five
  generated contract files.
- [x] Runtime evidence covers source, generated-contract, and modified-entry
  builds for the same two-source package. The generated and modified builds use
  the same extension name as the source build, preserve child module namespaces,
  and link native objects in caller order.
- [x] Documentation explains the combined package behavior with five examples
  covering single-source packages, two-source/four-module packages,
  source-free wrapper builds, Python API parity builds, and modified entry
  export policy.

### Stage 4 — Shared Parity Harness And Standalone Procedures

Standalone external procedure parity now lives in
`tests/wrapper/fortran/external_routines/test_external_procedures.py`. Generated
external-only contract bundles keep one compact entry `.pyi`; native sources,
objects, archives, and libraries remain separate build-plan facts.

- [x] Standalone parity tests use the shared `source` / `generated-pyi`
  parametrized fixture shape, so fixed-form, free-form, and multi-procedure
  external cases share one assertion body per behavior.
- [x] Source-only and generated-`.pyi`-only checks are limited to path-specific
  properties such as exact generated contract text, bridge-source inspection,
  and validation-before-codegen failures.
- [x] One fixed-form source containing one standalone procedure generates a
  non-empty root fragment with `@external` and rebuilds equivalently.
- [x] One free-form source containing one standalone procedure has the same
  `@external` generation and runtime parity.
- [x] One source containing several standalone procedures generates external
  declarations for all of them and exposes each at the extension root.
- [x] Several file-level BLAS/LAPACK-style standalone sources can generate one
  compact entry `.pyi` containing all external declarations while the native
  build plan links the separated objects in caller order.
- [x] `@external` makes the bridge emit an explicit interface and no module
  `use`; a module procedure makes the bridge emit the correct `use <module>`.
- [x] `@external` composes with `@bind("native_name")`: the native external is
  called while the wrapper declaration and root export may use different names.
- [x] A handwritten external `.pyi` plus native artifacts builds without source
  and follows the same placement, binding, validation, and export rules.
- [x] Removing `@external` from a generated package-entry declaration or adding
  it to a declaration inside a child-namespace module contract fails during
  validation before wrapper code generation.

### Stage 5 — In-Progress Generated-Contract Runtime Parity Evidence

- [x] The verified scalar baseline and legacy/F90 fmath array baseline run in
  both `source` and `generated-pyi` modes through the same assertion bodies.
  The generated contracts are compared against checked fixtures, the `.pyi`
  build links only explicit native objects, and generated contracts encode
  normalized Python public names with `@bind(...)` when the native Fortran name
  differs. Scalar-kind, enum-like constant, `value`, and existing `bind(C)`
  ABI cases also run from generated contracts with the same runtime assertions.
- [x] Function-call parity covers optional arguments, hidden output arguments,
  projected return ordering, nullable allocatable copy returns, and validation
  failures in both `source` and `generated-pyi` modes through shared assertion
  bodies. Generated `.pyi` builds clear Fortran `optional` attributes from
  bridge-local result temporaries while preserving Python `None` behavior for
  unallocated allocatables.
- [x] Array parity covers dtype, rank, shape, order, stride, lower-bound,
  writeability, byte-order, alignment, zero-extent validation, multidimensional
  order/stride checks, assumed-rank runtime dispatch up to the supported rank
  boundary, and Python-owned array results in both `source` and `generated-pyi`
  modes through shared assertion bodies.
- [x] Character parity covers fixed-length buffers, assumed-length strings,
  deferred character results, copy-in/copy-out for mutable strings, optional
  character arguments, Unicode round-trips, and embedded-NUL validation in both
  `source` and `generated-pyi` modes. `.pyi` parser regressions keep visible
  inout projected returns visible while preserving explicit output-only
  projection.
- [x] Derived-type parity covers fields, methods, type-bound root target
  procedures, default/keyword constructors, finalizers, borrowed child
  lifetime, scalar object boundaries, inheritance, polymorphic dispatch, and
  pointer snapshot results in both `source` and `generated-pyi` modes. `.pyi`
  parser regressions restore type-bound target metadata from class method
  declarations.
- [x] Callback parity covers scalar, array, and derived callback conversions,
  call-scoped callback lifetime, GIL entry handling, reference cleanup, and
  callback exception abort behavior in both `source` and `generated-pyi` modes.
  `.pyi` parser regressions infer callback dimension argument names so callback
  array result shapes remain explicit.
- [x] Module-state parity covers scalar module attributes, parameter behavior,
  saved native state shared across imports, allocatable module and derived-type
  borrowed views, allocatable replacement/copy-return ownership, nullability,
  and common-block encapsulation in both `source` and `generated-pyi` modes.
- [x] Runtime behavior parity covers recursive native calls in both `source`
  and `generated-pyi` modes, plus edited `.pyi` runtime policy decorators for
  `@hold_gil` and `@raises(...)` using native object builds. OpenMP remains
  source/makefile evidence until Stage 7 adds `.pyi` makefile/native-flag
  replay.
- [x] Naming and generic-interface parity covers public-name normalization,
  visibility filtering, keyword/collision policy, public generic dispatch,
  type-bound binding names, defined operators, comparisons, named operators,
  and assignment behavior in both `source` and `generated-pyi` modes.
  `.pyi` regressions keep class/member name reservations scoped separately,
  import public native generics instead of private specific procedures, and
  preserve keyword-normalized type-bound binding names.

### Stage 8 — Library-Scale And Mixed-Bundle Evidence

Real BLAS/LAPACK object-file evidence now lives in
`tests/wrapper/fortran/real_libraries/test_real_blas_lapack.py`.

- [x] Several selected standalone-procedure files copied from the real
  `tests/data/fortran/blas/` and `tests/data/fortran/lapack/` parser corpora
  build one BLAS/LAPACK-style extension from one generated compact
  `__init__.pyi`.
- [x] The generated contract imports no module leaves, marks every selected
  routine as `@external`, preserves assumed-size array ABI with `Flat`
  dimensions, and builds from separated object files without reparsing native
  source.
- [x] The generated compact BLAS/LAPACK contract is compared against the
  checked-in wrapper fixture under
  `tests/wrapper/fortran/real_libraries/contracts/real_blas_lapack/`;
  refresh is explicit through `WRAPPER_UPDATE_PYI_FIXTURES=1`.
- [x] Runtime evidence imports every selected BLAS/LAPACK routine through the
  normalized Python names and limits numerical checks to a few smoke calls:
  `daxpy`, `ddot`, `dasum`, and `dlamrg`.
- [x] Handwritten external-contract evidence covers C-order flat storage
  (`Annotated[Float64[Flat, 3], ORDER_C]`) by validating a multidimensional
  Python view while passing a rank-preserving bridge view to an assumed-size
  native dummy.

### Immutable Native Contract

Establish the source-free native facts before adding bundle or export policy.
The guarantees in this phase apply to every wrapper construct that x2py claims
to support. Validation proves that the semantic contract is complete and
internally consistent; it cannot inspect an arbitrary object, archive, or
shared library to prove that the supplied binary implements the declared ABI.
Compiler, linker, import, and runtime parity tests provide the remaining
artifact-level evidence.

- [x] A module leaf is named `<fortran-module>.pyi`; that filename is its native
  module identity. Procedure kind, native symbol, contained-versus-external
  status, argument order, ABI types and kinds, rank, intent, and required
  native imports are inferred from ordinary declarations plus `@external`,
  `@bind`, and `@native_call` only where those facts are not implicit.
- [x] Generated `.pyi` retains every native binding fact needed for module
  procedures, standalone external procedures, type-bound procedures, operators,
  assignment overloads, constructors, callbacks, finalizers, and module
  variables.
- [x] User edits may add wrapper validation, ownership, lifetime, error,
  visibility, and projection policy. Validation rejects structurally
  inconsistent declarations and projections; matching an editable contract to
  an opaque caller-supplied binary remains the caller's native build
  responsibility.
- [x] A generated module `.pyi` is sufficient to select the correct native
  module and symbol from supplied objects, archives, or shared libraries; code
  generation never reparses unavailable Fortran source.
- [x] Missing, contradictory, or structurally altered native facts fail during
  `.pyi` validation or readiness with a precise diagnostic before bridge code is
  emitted or native compilation begins.

### Single-Contract Build Foundation

Prove one source-free module contract can build before adding contract bundles.

- [x] Load a generated module-level `.pyi` file and use it as the semantic IR
  input for wrapper code generation.
- [x] Link caller-supplied native object files while skipping parser and
  semantic lowering for native source.
- [x] Build and import a callable-only Fortran module extension from
  `module.pyi --wrap --native-object module.o`.
- [x] Preserve the existing source-driven wrapper path and makefile/verbose
  modes while adding the `.pyi`-driven entrypoint.
- [x] CLI `.pyi` builds accept native object, archive, and shared-library paths
  with `--native-object`.
- [x] CLI `.pyi` builds accept `-l` libraries with `--native-library`.
- [x] CLI `.pyi` builds accept library search/rpath directories with
  `--native-library-dir`.
- [x] CLI `.pyi` builds accept native module/interface include directories with
  `--native-include-dir`.
- [x] CLI `.pyi` builds reject missing native build inputs with a direct error.
- [x] JSON build output reports both the semantic contract sources and the
  explicit native artifact and link inputs.
- [x] Native object files, module search paths, libraries, and library paths can
  be supplied without parsing native source. A general ordered linker-argument
  interface remains in Phase 9.
- [x] Contract files and native artifacts are many-to-many: no code path assumes
  that `name.pyi` must be implemented by `name.o`, or infers an artifact name
  from a contract filename.
### Deterministic Contract Generation And Fixtures

Make generated contracts complete and reproducible before composing them.

- [x] One Fortran module maps to exactly one semantic leaf `.pyi` file named for
  the module, independent of which source file contains it.
- [x] Source-owned fixture generation records a root-contract `.pyi` that
  imports its module leaves. One source containing two modules therefore emits
  two module leaves plus one root contract instead of concatenating
  declarations. That root contract is the sole wrapper input.
- [x] Standalone fixed-form and free-form procedures emit non-empty `.pyi`
  contracts with explicit `@external` placement.
- [x] General parser fixtures check in generated source-owned contract
  directories under `tests/pyi/fixtures/general/`; explicit `--pyi --out`
  package fixtures live under `tests/pyi/fixtures/wrapper_contracts/`; runtime
  parity fixtures live under the consuming `tests/wrapper/fortran/<subject>/`
  `contracts/` tree as they are added.
- [x] The general fixture suite and runtime parity baseline compare regenerated
  `.pyi` text exactly with the checked-in contract, so generator drift is
  explicit in review.
### Single-Entry Assembly And Extension Identity

Compose complete contract graphs from one explicit entry. The old plan for
passing multiple positional `.pyi` files is removed; it conflicts with the
implemented single-entry contract and is not a future feature.

- [x] The CLI and Python API accept exactly one entry `.pyi` and recursively
  discover its relative import graph. Multiple positional `.pyi` inputs and
  contract directories are rejected.
- [x] Imports and cross-module references between `.pyi` files retain the
  native dependency relationship without relying on source-file boundaries.
- [x] A generated entry defines the default Python export surface without
  redefining native module structure. For explicit `--out PATH`, `PATH` is the
  package and `PATH/__init__.pyi` is the entry.
- [x] The entry stem determines extension identity. For `__init__.pyi`, the
  parent directory name is used. `--extension-name` explicitly overrides either
  inference path.
### Python Namespace And Root Export Policy

Only after imported contracts retain native structure may the entry contract
reshape exports.

- [x] The generated Python extension is the root namespace inferred from the
  entry contract or selected by `--extension-name`.
- [x] Every imported Fortran module is preserved as one child namespace of the extension;
  its procedures, variables, derived types, constructors, and overloads remain
  under that namespace instead of being flattened into the extension root.
- [x] Two modules may expose the same public member name without collision. For
  example, `library.module1.func` and `library.module2.func` are distinct.
- [x] Generated, unmodified `.pyi`, and modified module `.pyi` builds preserve
  exactly the same native Fortran module namespace structure. A modified module
  contract cannot move declarations between modules, turn a module procedure
  into a standalone procedure, or otherwise rewrite native topology.
- [x] Standalone external procedures in a mixed entry are exported at the
  extension root while imported modules remain child namespaces.
- [x] The entry `.pyi` may contain standalone external procedures that contribute a root
  contract fragment rather than creating a child namespace from its filename.
- [x] Duplicate public names exported at the extension root fail with a direct
  collision diagnostic unless a modified `.pyi` explicitly renames or hides a
  declaration.
- [x] Module members are not automatically re-exported at the extension root;
  any root-level re-export must be explicit in the entry contract.
- [x] The generated default entry preserves module namespaces with
  imports such as `from . import module1` and `from . import module2`.
- [x] Only the entry contract can reshape the Python-facing export tree by hiding,
  aliasing, selectively re-exporting, or flattening declarations from module
  `.pyi` files.
- [x] `from .module import *` flattening is explicit export policy; duplicate
  exported names fail with a direct collision diagnostic instead of depending
  on import order.

### Parity Harness And Required Test Progression

Each test is added only after the corresponding behavior in Phases 1–5 exists.
Every successful scenario exercises the applicable source,
unmodified-generated-contract, and modified-contract paths. Tests compare the
public API and observable runtime behavior, regenerate checked-in fixtures
exactly, and build `.pyi` paths without reparsing native source.

Source and unmodified-generated-contract parity is enforced by test structure,
not by maintaining two similar test lists. Each parity-eligible test has one
behavioral assertion body and receives an imported wrapper from a fixture
parametrized with the `source` and `generated-pyi` build modes. Pytest therefore
collects both modes from the same test function, so adding or changing an
assertion changes both paths automatically. Do not create separate source and
generated-`.pyi` assertion functions or modules. A path-specific test may opt
out only when it verifies a build-path property that cannot apply to the other
path, such as exact generated `.pyi` text or proving that a `.pyi` build does
not reparse source; the test name or a nearby comment must state that reason.
Modified-contract tests remain separate when they intentionally assert a
different public API or runtime contract.

- [x] Store `.pyi` parity fixtures under the consuming wrapper subject, with
  source-free native-object wrapper smoke coverage under
  `tests/wrapper/fortran/build_from_pyi/contracts/`.
- [x] Generate a `.pyi` from a source fixture, rebuild from the generated `.pyi`
  plus a native object, and compare runtime behavior with the source-driven
  build for the first callable-only fixture.
- [x] Feed the source and generated-`.pyi` builds through one parametrized
  module fixture and the exact same behavioral assertion body for the first
  callable-only fixture.
#### Single-module baseline

- [x] One source containing one Fortran module generates one module leaf plus an
  entry `.pyi`, and produces equivalent source and `.pyi` extensions.

#### Multi-module generation and assembly

- [x] Source-owned fixture generation keeps one contract directory per source.
  Explicit `--pyi --out PATH` instead treats `PATH` as the package directory and
  writes `PATH/__init__.pyi`.
- [x] One source containing two Fortran modules generates two module `.pyi`
  files plus an entry contract inside the package; passing only that entry
  produces both child namespaces in one extension.
- [x] `.pyi` wrapper commands and the Python build API accept exactly one entry
  contract and recursively discover its relative imports; multiple positional
  `.pyi` inputs and contract directories are rejected.
- [x] A module leaf supplied as the entry exposes its declarations at the
  extension root without changing their native module placement.
- [x] The entry stem controls the extension filename, `PyInit_<name>`, JSON
  build result, and import name; `__init__.pyi` uses its resolved parent
  directory, including when invoked from inside that directory.
- [x] `--extension-name` overrides the inferred extension filename, `PyInit_<name>`, JSON
  build result, and successful Python import in every contract-bundle path.

#### Namespace and export policy

- [x] Two modules may each expose `func`, producing `library.module1.func` and
  `library.module2.func` without collision.
- [x] A modified root contract can alias a module procedure at the root
  without changing its native module contract.
- [x] A modified root contract can flatten a module's public names explicitly.
- [x] Flattening modules with colliding public names fails before codegen and
  identifies every conflicting origin; explicit aliases resolve the failure.
- [x] `from . import module1 as solver` exports only `solver` while retaining
  native module `module1`; selective procedure aliases retain native symbols.
- [x] A three-level relative import graph discovers every transitive contract,
  while absolute `typing` and `types` support imports create no graph edge or
  runtime export. Missing files and cycles fail before code generation.
- [x] Source-driven and generated-`.pyi` builds expose the same module children
  and root-level standalone procedures without implicit flattening.

### Established Runtime Feature Contracts

Expand the proven three-path harness across wrapper behavior feature by feature.

- [x] Public module variables are declared directly as module-level annotations.
  Generated native getter/setter bridge functions remain internal and never
  appear in the `.pyi` or as Python-callable procedures.
- [x] Fixed character length uses `String[n]`; non-fixed length uses `String`.
  Resolved semantic dtypes are emitted without source-language kind imports.
