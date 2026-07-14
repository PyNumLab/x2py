---
title: Wrapper Plan Migration Checklist
audience: maintainers
prerequisites: pipeline map, semantic IR, ownership policy
related: ../internal-architecture/pipeline-map.md, ../../user/reference/semantic-ir.md, semantic-pyi-wrapper-checklist.md, index.md
status: active-roadmap
---

# Wrapper Plan Migration Checklist

This file is the canonical implementation contract for wrapper-plan migration.
It replaces the generic semantic-IR wrapper lowering route one eligible module
at a time. The migration changes representation and generation organization; it
does not intentionally change the established Python, native ABI, ownership, or
build behavior of a migrated lane.

## Canonical Pipeline

```text
Semantic IR
  -> post-IR policy completion
  -> WrapperPlanner.build(module)
  -> editable ModulePlan
  -> WrapperCodeGenerator.generate(plan)
       -> freeze and validate the received plan
       -> recursively synthesize C binding nodes
       -> recursively synthesize Fortran bridge nodes
       -> print backend nodes
       -> RenderedGeneratedWrapperArtifacts
  -> existing build/link orchestration
```

There is no public or wrapper-domain representation between `ModulePlan` and
backend syntax nodes. `CModule`, `CHeader`, `CFunction`, `FortranModule`, and
`FortranFunction` are direct printer inputs, not another wrapper planning
stage.

The public generation boundary is deliberately small:

```python
complete_semantic_policies(module)
plan = WrapperPlanner().build(module)
artifacts = WrapperCodeGenerator().generate(plan)
```

`WrapperCodeGenerator.generate` accepts `ModulePlan` only. It does not accept
semantic modules, build a plan itself, select an alternate lowering route, or
retry a prior route after direct generation begins.

Semantic `.pyi` generation remains outside this route. A semantic `.pyi`
contract can supply the semantic module consumed by planning, but planning does
not change `.pyi` emission.

## One Shared Plan, Explicit Backend Views

`ModulePlan` is one shared semantic-and-ABI contract. It is not a C plan joined
to a Fortran plan and it does not contain backend nodes or source text.

Every owner that crosses or coordinates the boundary has binding and bridge
child plans in the same editable tree:

```text
ModulePlan
  binding: BindingModulePlan
  bridge: BridgeModulePlan
  functions: FunctionPlan ...
    binding: BindingFunctionPlan
    bridge: BridgeFunctionPlan
    arguments: ArgumentTransferPlan ...
      binding: BindingArgumentPlan
      bridge: BridgeArgumentPlan
      native_call_slot: NativeCallSlotPlan
      transformations: TransformationPlan ...
    results: ResultPlan ...
      binding: BindingResultPlan
      bridge: BridgeResultPlan
      native_call_slot: NativeCallSlotPlan | None
      transformations: TransformationPlan ...
    lifecycle: LifecycleActionPlan ...
      binding: BindingLifecyclePlan | None
      bridge: BridgeLifecyclePlan | None
    native_call_slots: ordered references to argument/result slots plus
      function-owned literal or helper slots
```

`ArgumentTransferPlan` remains the only argument-owner record; do not add a
generic duplicate `ArgumentPlan`. Its backend-facing child plans are
deliberately distinct and directly editable:

- `binding: BindingArgumentPlan` describes the Python input, its C conversion
  action, and
  the C handoff value/role it produces;
- `bridge: BridgeArgumentPlan` describes the C ABI slot, value-versus-address
  convention,
  native action, and Fortran value that the bridge consumes;
- `native_call_slot` records the exact native-call position and source;
- an argument or hidden result's `native_call_slot` is the same mutable record
  referenced from `FunctionPlan.native_call_slots`, not a copied record that a
  maintainer must edit twice;
- result and lifecycle records identify later producers, consumers, ordering,
  and responsibility through their own binding and bridge views;
- native slots and lifecycle actions are subordinate transfer details, not
  parallel datatype-policy systems. They remain indexed on `FunctionPlan`
  because native ABI order and success/failure lifecycle order may span more
  than one argument or result. A function-owned literal, status helper, or
  other ABI slot may also have no single argument/result owner.

The action vocabulary keeps source placement, data transfer, and native ABI
transport orthogonal. `ResultPlan.source_kind` says whether a result comes from
a `direct_return` or `hidden_output`; `CodegenAction` says how the value moves
or is owned (`DIRECT_VALUE`, `COPY_OUT`, `WRAPPER_INSTANCE`, and so on). A
hidden scalar therefore remains `DIRECT_VALUE`, while hidden strings and
ordinary arrays are `COPY_OUT`; hidden descriptor-owned objects use their
completed ownership action. `HIDDEN_OUTPUT` is not a codegen action because
hiddenness is a source location, not a transfer operation.

Likewise, `NativeBarrierAction.PASS_ARRAY_BUFFER` means the Phase 6 data-buffer
ABI whose handoff plan carries data, rank, extents, strides, and itemsize.
`NativeBarrierAction.PASS_NATIVE_DESCRIPTOR` is reserved for the persistent
native descriptors and handles introduced in Phase 7. Neither backend may use
one action as a fallback for the other.

`NativeBarrierAction.PASS_RAW_ADDRESS` is the third, deliberately narrower
array transport: one caller-supplied opaque address plus separately completed
pointee rank, shape, element type, and orientation facts. It does not authorize
NumPy extraction, a packed array-buffer ABI, or a native descriptor. Scalar,
fixed-string, and array raw addresses reuse this action and
`ArgumentHandoffMode.OPAQUE_ADDRESS`; their object kind then selects the named
bridge association method. Do not add datatype-specific raw-address actions.

The binding input and bridge input may have different representations: a C
binding commonly receives `PyObject *`, produces a C scalar or address, and
the bridge then consumes a value or pointer according to its ABI slot. The plan
therefore records the producer/consumer handoff contract explicitly; it does
not assume identical types or actions. This keeps both backend plans in one
coherent editable tree while preventing them from drifting into disconnected
top-level plans. `CBindingGenerator` reads only binding views plus shared
handoff/order facts needed to create C nodes; `FortranBridgeGenerator` reads
only bridge views plus shared native-call order needed to create Fortran nodes.
Neither backend output is an input to the other backend.

An owner may have only one active backend side when completed policy places the
behavior entirely in one backend, but that ownership must be explicit in the
plan rather than inferred during lowering.

### Transformation Layer Ownership

Every representation transformation has one explicit
`TransformationPlan.layer`: `BINDING` or `BRIDGE`. The record also names its
phase (`COPY_IN`, `NATIVE_MUTATION`, `COPY_OUT`, or `CLEANUP`), typed action,
source representation, target representation, and reason. These records are
subordinate to the `ArgumentTransferPlan` or `ResultPlan` that owns the value;
they are not a parallel datatype-policy hierarchy.

Use the binding layer for transformations involving Python objects or NumPy
semantics: dtype/layout conversion, Python encoding/decoding, reference and
identity handling, copy-back into caller objects, and Python-owned temporary
cleanup. Use the bridge layer for transformations wholly between the ABI and a
native-language representation: Fortran character representation, native
descriptor/result materialization, derived native layout, or native-only
allocation and copy.

One logical conversion and its inverse/cleanup must stay at one layer. If a
workflow genuinely needs both layers, policy completion records two distinct
transformations separated by a named intermediate ABI representation. A
backend consumes only transformations assigned to it and fails validation if
asked to lower an action owned by the other backend. Method location, datatype,
`intent`, and available local storage never select the transformation layer.
For `COPY_F`, copy-in, conditional copy-out, and cleanup are all binding-owned;
the bridge has no `COPY_F` transformation and reuses its ordinary ORDER_F
association path.

### Editable Signature And Native Intent Boundary

The semantic `.pyi` signature is authoritative for the Python-facing call
shape. The source converter may use native `intent` to propose the initial
generated signature, but that proposal is not backend policy. A user may
reorder visible Python arguments, keep a native output dummy as caller-supplied
storage, project it into a Python result, or introduce hidden bridge storage.
After the semantic contract is constructed or edited, completed native-call
slots must account for every required native position exactly once; stored
source `intent` must not silently override that mapping by hiding, exposing,
reordering, allocating, or projecting a Python value.

Bridge dummies and backend-local variables use the most permissive declaration
that is compatible with the selected ABI, normally no `intent` or an internal
`intent(inout)`-equivalent writable local. The called native procedure enforces
its actual `intent(in)`, `intent(out)`, or `intent(inout)` contract. Required
interoperability attributes such as `value`, optional presence fields, standard
descriptor attributes, and true bridge-output parameters remain explicit ABI
facts; they are not permission for a backend to reconstruct the user-facing
signature from native `intent`.

The plan includes every fact required for mechanical lowering:

- owner path and plan-node kind;
- typed Python, native, and result actions;
- semantic datatype, datatype family, and precision/type facts;
- Python/native handoffs and bridge ABI slots;
- native-call slots in their exact order;
- result and output projection;
- ownership, transfer, destruction, mutability, writeback, release
  responsibility, storage mode, nullability, and lifecycle ordering; and
- every typed lowering choice required by a supported backend.

It contains decisions and facts, never generator method names. In particular,
there are no handler-name fields, handler records, or plan-owned handler
registries. The planner uses the completed policy actions already represented
by `PythonBarrierAction`, `NativeBarrierAction`, and `CodegenAction`; a new
typed action is added only when none of those can identify a necessary
mechanical behavior. Free-form string actions are forbidden.

## Ownership Boundary

Post-IR policy completion decides object kind, ownership, transfer,
destruction, mutability, writeback, nullability, output projection, release
responsibility, contract-value storage (`stack`, `heap`, or `alias`), getter
behavior, native setter assignment, Python setter exposure, ABI order, and
lifecycle order before planning starts.

`WrapperPlanner` only projects those completed decisions and datatype facts
into readable editable records. It may traverse owners, preserve declared
order, assign stable owner paths, and wire already-decided producers to
consumers. It must not derive or replace policy from a datatype, `intent`,
decorator spelling, `is_alias`, dotted owner shape, local memory observation,
or a missing field.

No code after planning may infer, replace, or override semantic policy. Backend
contexts may allocate temporary names and create declarations, error paths,
reference-count operations, and local cleanup statements after selecting a
typed lowering case. Those are emitted-code mechanics, not plan policy.

`WrapperPlanner.build(module)` returns an editable `ModulePlan`. Maintainers
may edit its ordinary fields to inspect an experiment before generation. A
permanent behavior change belongs in the semantic contract and completed policy
rather than in a backend exception.

## Generator-Owned Freezing and Validation

Every consumer freezes the exact object it receives:

```text
editable ModulePlan -- WrapperCodeGenerator --> frozen ModulePlan
editable backend modules -- source printers --> frozen backend modules
editable generated artifacts -- build integration --> frozen artifacts
```

At the start of `WrapperCodeGenerator.generate(plan)`, the generator must:

1. recursively freeze that exact plan object;
2. run the complete binding/bridge plan-consistency validation on the final
   edited plan;
3. ask each backend to preflight only its own implementation capability; and
4. recursively lower the validated plan into backend nodes before the printers
   consume those nodes.

Later mutation of the received plan raises `FrozenStageRecordError`. Backend
nodes remain editable until their printer consumes them. Generated artifacts
remain editable until `_build_rendered_wrapper_extension(...)` consumes them.

`WrapperPlanner` does not validate its output. It mechanically projects an
editable plan, which may temporarily be inconsistent while a maintainer edits
it. `WrapperCodeGenerator` owns the private structured validation methods and
is the only validation consumer. There is no standalone validator class or
public validation operation.

`WrapperCodeGenerator._validate_plan()` is the single plan-consistency gate.
It validates the complete binding/bridge graph after the editable plan has
been frozen and before either backend preflight or visitor runs. The gate stays
small by composing `_plan_diagnostics()` from typed private diagnostics for
namespaces, functions, arguments, results, lifecycle actions, and module
variable getter/setter action families. A cross-view invariant belongs to the
diagnostic for the lowest plan node that contains both views; for example, a
module-variable diagnostic validates Python setter exposure against its native
assignment and bridge setter role.

`CBindingGenerator.require_supported()` and
`FortranBridgeGenerator.require_supported()` are later backend-local
capability preflights. They may reject a completed action, primitive type,
descriptor kind, or ABI combination that their own backend cannot implement,
but they do not establish whether binding and bridge views agree. Backend
visitors and `_lower_*` methods mechanically consume the decisions owned by
their view. Their exhaustive unmatched-action errors remain defensive
protection for direct backend use; the public generation path must report a
cross-view inconsistency from `_validate_plan()` first. No generator infers
consistency by reading the other backend's plan view.

Structural validation preserves these invariants:

- module getter actions and roles agree, and Python setter exposure agrees with
  native assignment, bridge setter roles, descriptor kinds, and constant state;
- binding producer and bridge consumer roles agree;
- bridge ABI coverage, positions, and owner roles are complete;
- native-call slot coverage, exact ordering, hidden literals, and hidden
  results agree, including hidden-result native and codegen actions;
- direct and hidden result producer/consumer roles agree;
- writeback, cleanup, and release actions use available source roles in their
  declared order, and advertised roles exactly match their plan producers;
- positions and symbolic roles are neither duplicate nor missing; and
- external and bind-target requirements are complete.

## Direct Recursive Lowering

`WrapperCodeGenerator` owns two private backend visitors:

```python
c_module, c_header = CBindingGenerator().visit(plan)
fortran_module = FortranBridgeGenerator().visit(plan)
```

They are private implementation organization inside direct generation, not
public stages. Both visitors recursively traverse the same plan tree and
return actual C or Fortran nodes (or tuples of actual nodes where a child needs
multiple declarations or statements).

The recursive shape is:

```text
ModulePlan
  -> binding and bridge module contexts and backend nodes
  -> NamespacePlan
       -> directly owned FunctionPlan and ModuleVariablePlan records
       -> binding/bridge argument transfers, result projection, lifecycle actions
       -> complete backend function and namespace nodes
  -> complete backend module node
```

An argument visitor returns the C or Fortran declarations/statements/parameters
needed for that backend. A result visitor returns the backend result nodes.
Lifecycle visitors return backend writeback, cleanup, or release nodes. Parent
visitors assemble these concrete child results directly into complete syntax
nodes. Do not introduce another wrapper-specific transport model.

The public orchestration stays visibly direct:

```python
class WrapperCodeGenerator:
    def generate(self, plan: ModulePlan) -> RenderedGeneratedWrapperArtifacts:
        plan.freeze()
        self._validate_plan(plan)
        self._c_generator.require_supported(plan)
        self._fortran_generator.require_supported(plan)

        c_module, c_header = self._c_generator.visit(plan)
        fortran_module = self._fortran_generator.visit(plan)

        c_source = self._c_printer.doprint(c_module)
        c_header_source = self._c_printer.doprint(c_header)
        fortran_source = self._fortran_printer.doprint(fortran_module)
        return self._rendered_artifacts(
            plan.owner_path,
            c_source,
            c_header_source,
            fortran_source,
        )
```

The generator constructs `RenderedGeneratedWrapperArtifacts` directly from the
printed source plus artifact metadata. It does not duplicate native build plans,
compiler selection, link ordering, runtime-support installation, or compilation
policy; those remain in existing build/link orchestration.

## Direct Lowering Methods

Each backend visitor dispatches plan nodes by class through
`_visit_<PlanClass>`. A visitor method then calls a typed
`_lower_<subject>` helper for each completed action family owned by that
backend. The helper uses an explicit, exhaustive action match and calls one
concrete `_lower_<subject>_<action>` implementation method. For example:

```python
def _visit_ModuleVariablePlan(self, plan):
    return (
        *self._lower_module_getter(plan),
        *self._lower_module_setter(plan),
    )

def _lower_module_getter(self, plan):
    match plan.binding.getter_action:
        case ModuleGetterAction.CONSTANT_VALUE:
            return self._lower_module_getter_constant_value(plan)
        case ModuleGetterAction.DIRECT_VALUE:
            return self._lower_module_getter_direct_value(plan)
        case ModuleGetterAction.NULLABLE_SNAPSHOT:
            return self._lower_module_getter_nullable_snapshot(plan)
    raise ValueError(...)
```

The C binding dispatches only from binding-owned actions, and the Fortran
bridge dispatches only from bridge-owned actions. In particular, native module
setter generation consumes the completed bridge assignment action rather than
the Python setter-exposure action. Post-IR policy completion records
`AssignmentMode.NONE` when no native setter is exposed and
`AssignmentMode.VALUE_COPY` for supported scalar value write-through; bridge
lowering does not reconstruct that choice from the Python setter action.
Backend support checks retain genuine ABI and capability validation; action
dispatch itself raises explicitly for every unsupported value, including an
unsupported alias assignment.

Do not synthesize implementation method names, use `getattr` to execute
lowering, retain a fallback behavior, or store dispatcher names in the plan.
Do not create extra getter or setter plan nodes solely to gain more
`_visit_<PlanClass>` methods. Both visitor and lowering methods return backend
syntax nodes; printers remain the only layer that renders those nodes as source
text.

Primitive dtype spelling and converter differences live in the intentionally
scalar-specific `PrimitiveScalarTypeRegistry`; they do not duplicate control
flow methods or select semantic policy.

Within policy, planning, support analysis, validation, and both backend
visitors, family-specific helpers stay in visibly labeled contiguous groups:
scalar helpers, string helpers, and ordinary-array helpers. Put a short section
comment above every such group so maintainers can find one datatype family
without scanning interleaved lowering methods. Generic orchestration remains
outside those groups and dispatches into them through the completed typed
actions.

## Migration and Route Rules

The legacy route remains the behavioral oracle until a lane has direct-plan
parity. Route selection is atomic per merged extension: a generation unit uses
either the direct wrapper-plan route or the legacy route. It never combines one
backend from one route with the other backend from the other route.

An unsupported owner may select the legacy route before planning. Once the plan
route is selected, planning, validation, lowering, printing, or compilation
failure fails the build; it must not fall back to legacy generation.

Support reports and rollout gates keep scalar, string, and ordinary-array
input, optional, writeback, direct-result, and hidden-result lanes distinct.
Evidence for one datatype family must not make another family production
eligible accidentally.

For each lane:

1. replay an existing passing `tests/wrapper` case through the legacy route and
   retain its generated artifacts;
2. record the relevant legacy source paths, ABI/call order, ownership and
   cleanup behavior, artifact requirements, and runtime assertions;
3. complete every missing semantic decision before planning;
4. add the smallest required plan record and directly named lowering method;
5. produce the same complete artifact set through the direct route;
6. inspect differences, compile both routes, and run the existing assertions;
7. update checklist evidence only after direct-route parity is proven.

Generated source is diagnostic evidence, not a byte-for-byte golden. Backend
temporary names and equivalent control flow may differ, but ABI, conversion,
ownership, cleanup, call order, and artifact requirements must remain proven.

During this migration the full real-library BLAS/LAPACK wrapper corpus is
excluded locally and in CI until final cutover. General native-bundle coverage
remains active.

## Staged Walkthrough

`tools/wrapper_plan_staged_walkthrough.py` is the maintained hand-inspection
path. It shows only the source/contract entry, policy completion, plan creation,
a direct edit, direct generation, artifact inspection, build, and runtime use:

```python
module = ...
complete_semantic_policies(module)

plan = WrapperPlanner().build(module)
namespace = next(item for item in plan.namespaces if item.python_path == ())
function = namespace.functions[0]
function.bridge.native_name = "SUB_R8"

binding = CBindingGenerator()
bridge = FortranBridgeGenerator()
print(function.arguments[0].binding.optional_mode)
print(function.arguments[0].bridge.optional_mode)

artifacts = WrapperCodeGenerator(
    c_generator=binding,
    fortran_generator=bridge,
).generate(plan)

# inspect generated files
# build and run
```

It does not expose standalone validation. Printed plan inspection uses the
actual namespace, owner, and completed action records. The backend visitors
make the corresponding explicit action matches visible in their typed lowering
helpers.

## Required Evidence

Focused tests must prove:

- `WrapperPlanner.build(module)` returns a directly mutable plan;
- direct edits to binding and bridge views change the relevant generated C and
  Fortran source;
- `WrapperCodeGenerator.generate(plan)` freezes the exact consumed plan;
- module visitors recursively include generated function nodes;
- function visitors recursively include argument, result, and lifecycle nodes;
- directly named backend lowering methods cover every supported plan action;
- unsupported combinations fail explicitly;
- source printers freeze backend module nodes;
- generated artifacts remain editable until build consumption, which freezes
  them;
- source and semantic-`.pyi` entries preserve compiled runtime parity; and
- backend lowering does not reconstruct semantic policy.

Use package-export inspection and focused migration checks to prove removal of
obsolete internal representations; do not preserve tests whose only assertion
is that a removed API is absent.

## Recovered Roadmap Scope

The detailed migration queue below is retained from the original roadmap. The
obsolete Phase 0-2 emitter/fragment architecture is replaced by the simplified
direct-plan checklist later in this file; all later semantic lanes, matrix rows,
verification gates, and completion records remain explicit.

## Existing Wrapper Suite As The Migration Queue

`tests/wrapper` is the behavioral source and final acceptance suite for this
migration. Migrate its existing generation units one by one; do not create a
parallel wrapper suite or new native source fixtures merely to make the new
route easier to exercise.

- Phase 0A adds a maintained migration matrix to this file covering every
  Python test node under `tests/wrapper`. Each row records whether the test
  generates a wrapper, the source/contract generation unit it uses, its
  relevant feature lanes, and one status:
  `not-applicable`, `deferred-real-library`, `legacy`, `dual-route`, or
  `wrapper-plan`.
- Existing source files, contract fixtures, build helpers, runtime assertions,
  failure assertions, and ABI assertions are reused as written whenever they
  already cover the migrated behavior. Do not copy their behavior into a new
  test with a smaller invented source.
- A new native source or contract fixture is allowed only when the audit proves
  that accepted production behavior has no existing test. Record that coverage
  gap and its owning semantic lane here before adding the fixture; migration
  convenience is not sufficient justification.
- Whole-generation-unit routing still applies. An existing test moves to
  `dual-route` only when every runtime-required feature in its module is
  supported. If a nominally scalar fixture also contains results, strings,
  arrays, decorators, module state, or classes, leave it on the legacy route
  until those lanes are complete rather than carving out a narrower fixture.
- Dual-route parity reuses the same existing fixture and assertion function for
  legacy and wrapper-plan builds through internal test orchestration. Do not
  add a public route flag, duplicate the behavioral assertions, or require
  byte-identical generated source.
- Once parity passes and production eligibility is widened, that existing test
  moves to `wrapper-plan`. Keep deliberate legacy execution only in the
  migration parity harness until final cutover.
- The final target is not merely that `tests/wrapper` passes. Every test in the
  suite must be represented in the migration matrix, and every test that
  generates a runtime wrapper must use the wrapper-plan route after cutover.
  Tests that only inspect documentation, layout, parsing, or `.pyi` generation
  may be `not-applicable` but must still pass.
- During active migration, every local and GitHub Actions pytest invocation
  excludes
  `tests/wrapper/fortran/real_libraries/test_real_blas_lapack.py`. Mark its BLAS
  and LAPACK rows `deferred-real-library`; do not use either corpus for lane
  parity or general migration verification. General native-bundle tests in
  `test_stage7_native_bundles.py` remain active because they test linker/build
  mechanics independently of the full BLAS/LAPACK corpora.

### Wrapper Test Migration Matrix

Matrix rows use pytest selector patterns. A row ending in `::*` covers every
collected test node in that Python file when all nodes share the same
generation classification. A row ending in `[*]` covers the parametrized nodes
for that test function. The structural layout test expands these selectors
against live `python3 -m pytest --collect-only -q tests/wrapper` output, so a
new wrapper test node must either match an existing row intentionally or add a
new row here before later implementation starts.

Statuses have the meanings defined above: `legacy` still uses the current
`semantic_ir_to_codegen_ast()` route, `dual-route` runs the same generation
unit and runtime assertions through both implementations, `wrapper-plan` uses
only `WrapperPlan -> WrapperCodeGenerator`, `not-applicable` does not generate
a runtime wrapper, and `deferred-real-library` is reserved for the full BLAS
and LAPACK corpus until Phase 12.

#### Current Wrapper Route Counts

These are collected pytest-node counts, not matrix-row counts. The structural
layout test derives them from live `tests/wrapper` collection and fails if this
summary, the exhaustive matrix, and the test tree disagree.

| Status | Collected nodes |
| --- | ---: |
| `wrapper-plan` | 94 |
| `dual-route` | 5 |
| `legacy` | 123 |
| `not-applicable` | 96 |
| `deferred-real-library` | 2 |

#### Recorded Route Progression

This history keeps phase movement visible instead of replacing the previous
snapshot with only the latest totals. Phase 2D moved all 17 dual-route nodes
and 44 legacy nodes to production plan routing, then added two parametrized
plan-route nodes. Phase 2E adds two scalar-only parity nodes, and Phase 2F adds
one isolated direct-return plus hidden-output scalar aggregation node. The
original mixed integration nodes retain their real array/string/object
blockers.

| Proven checkpoint | `wrapper-plan` | `dual-route` | `legacy` | `not-applicable` | `deferred-real-library` | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Before Phase 2D | 0 | 17 | 178 | 95 | 2 | 292 |
| Phase 2D complete | 63 | 0 | 134 | 95 | 2 | 294 |
| Phase 2E scalar isolation | 65 | 0 | 134 | 95 | 2 | 296 |
| Phase 2F scalar result aggregation | 66 | 0 | 134 | 95 | 2 | 297 |
| Phase 5A required string values | 67 | 0 | 134 | 95 | 2 | 298 |
| Phase 5B fixed string results | 69 | 0 | 134 | 95 | 2 | 300 |
| Phase 5C fixed string writeback | 70 | 0 | 134 | 95 | 2 | 301 |
| Phase 5C assumed/optional string writeback | 71 | 0 | 134 | 95 | 2 | 302 |
| Phase 5D fixed string storage/raw addresses | 72 | 0 | 134 | 95 | 2 | 303 |
| Phase 5 production route reconciliation | 76 | 0 | 130 | 95 | 2 | 303 |
| Phase 6 ordinary arrays | 78 | 5 | 130 | 95 | 2 | 310 |
| Phase 6G raw array addresses | 80 | 5 | 130 | 95 | 2 | 312 |
| Phase 6 `COPY_F` representation copy | 81 | 5 | 130 | 95 | 2 | 313 |
| Phase 7 native handles/descriptors | 88 | 5 | 129 | 96 | 2 | 320 |
| Phase 7 production route reconciliation | 94 | 5 | 123 | 96 | 2 | 320 |

Migration is complete only when `legacy`, `dual-route`, and
`deferred-real-library` are all zero. At that point every runtime-generating
node must be `wrapper-plan`; `not-applicable` may remain only for tests that do
not generate a wrapper. Until then, moving a node from `legacy` to `dual-route`
records proven parity, and moving it from `dual-route` to `wrapper-plan`
records final removal of its legacy execution.

#### Complete Route Ledger

For a `legacy` row, the feature-lane column identifies what still blocks the
new route. For `dual-route` and `wrapper-plan` rows, it identifies the behavior
already covered by the new generator.

| Pytest selector | Generation unit | Feature lanes / blockers | Status |
| --- | --- | --- | --- |
| `tests/wrapper/fortran/arrays/test_array_contracts.py::*` | source/generated-.pyi parity or parametrized route | ordinary arrays | `legacy` |
| `tests/wrapper/fortran/arrays/test_array_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/arrays/test_array_results.py::test_array_results_follow_data_buffer_and_descriptor_handle_contracts[*]` | production plan route in source/generated-.pyi parity modes | fixed/runtime-shape ordinary array results; owned allocatable descriptor results; namespace preservation | `wrapper-plan` |
| `tests/wrapper/fortran/arrays/test_array_results.py::test_ordinary_array_results_match_legacy_and_wrapper_plan_routes` | production output-only plan route with deliberate legacy rollback comparison | fixed/runtime-shape ordinary array results; ranks one through fifteen; Fortran order; zero-sized results; allocation/copy/release failure paths | `wrapper-plan` |
| `tests/wrapper/fortran/arrays/test_array_results.py::test_owned_allocatable_results_match_legacy_and_wrapper_plan_routes` | reduced owned-result contract with deliberate legacy rollback comparison | allocated and zero-sized wrapper-owned `CFI_CDESC_T` function-result handles; extraction and release | `wrapper-plan` |
| `tests/wrapper/fortran/arrays/test_assumed_rank_arrays.py::test_assumed_rank_arguments_dispatch_to_runtime_rank[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_assumed_rank_arrays.py::test_assumed_rank_bridge_dispatches_each_runtime_rank_argument[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_assumed_rank_arrays.py::test_assumed_rank_arrays_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing assumed-rank native unit | runtime ranks one through fifteen; mutable storage; rank validation; native-handle actuals deferred to Phase 7 | `dual-route` |
| `tests/wrapper/fortran/arrays/test_bind_c_array_type.py::*` | non-generating: legacy model/printer/policy unit coverage | legacy model/printer mechanics; ordinary arrays; native handles/descriptors | `not-applicable` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_rank2_contiguous_contract_requires_fortran_contiguous[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_rank2_assumed_shape_accepts_fortran_ordered_strided_views[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_rank2_assumed_shape_rejects_non_positive_strides[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_rank2_explicit_shape_requires_fortran_contiguous[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_rank3_contiguous_contract_requires_fortran_contiguous[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_rank3_assumed_shape_accepts_fortran_ordered_strided_views[*]` | source/generated-.pyi parity | ordinary arrays; native-handle actuals deferred to Phase 7 | `legacy` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::test_dense_strided_and_projected_arrays_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing multidimensional native unit | dense/explicit extents; positive-strided views; zero-sized axes; projected output identity; native-handle actuals deferred to Phase 7 | `dual-route` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_init_entry_uses_resolved_parent_name_from_inside_package` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_output_name_override_replaces_entry_inference` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_recursive_graph_preserves_module_and_symbol_aliases_and_ignores_support_imports` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_recursive_graph_reports_cycles_before_codegen` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_recursive_graph_reports_missing_relative_contract_before_native_validation` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_source_build_preserves_modules_and_root_externals` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_complete_general_source_preserves_namespaces_through_both_routes[*]` | production plan route with deliberate legacy rollback comparison | Python namespace hierarchy; native import aliases; scalar inputs/results; void calls | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_entry_can_alias_one_module_procedure_at_the_root` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_entry_rejects_colliding_wildcard_exports` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_entry_wildcard_import_explicitly_flattens_module_leaf` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_generated_pyi_fixture_builds_from_native_object_without_source_reparse` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_generated_pyi_matches_checked_in_fixture` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_mixed_entry_exposes_externals_at_root_and_modules_as_children` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_module_leaf_can_be_the_entry_contract` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_module_variable_runtime_contract[*]` | source/generated-.pyi parity or parametrized route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_mutable_module_variable_default_initializes_native_storage` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_one_entry_preserves_multiple_native_module_namespaces` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_cli_accepts_exactly_one_entry_contract` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_cli_preserves_explicit_ordered_link_items` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_cli_requires_a_native_link_input` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_makefile_manifest_and_replay_workflows` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_manifest_records_pointer_descriptor_interop_requirements` | non-generating: manifest serialization unit | completed native-array build requirements and local standard-descriptor headers | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_accepts_exactly_one_entry_contract` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_a_missing_native_artifact` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_invalid_address_contracts_before_codegen[*]` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_invalid_projection_before_codegen` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_python_suffix_as_semantic_contract` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_reduced_entry_generates_only_reachable_module_variable_bindings` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_scale_runtime_contract[*]` | source/generated-.pyi parity or parametrized route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_source_named_root_discovers_and_builds_module_leaf` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_compile_object_dependency_modules_keep_caller_order` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_fortran_wrapper_default_module_name_does_not_collide_with_root_function` | direct wrapper/build route | build/compile/link orchestration | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_fortran_wrapper_default_places_extension_beside_source` | direct wrapper/build route | build/compile/link orchestration | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_fortran_wrapper_out_names_importable_shared_library` | direct wrapper/build route | build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_internal_preprocessing_mode_still_builds_importable_runtime_wrapper` | direct wrapper/build route | build/compile/link orchestration; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_native_link_plan_serializes_interleaved_item_kinds` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_source_build_result_records_structured_native_plan` | direct wrapper/build route | build/compile/link orchestration | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_verbose_mode_prints_custom_wrapper_flags` | direct wrapper/build route | build/compile/link orchestration | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_verbose_mode_prints_full_direct_build_commands` | direct wrapper/build route | build/compile/link orchestration | `wrapper-plan` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_wrapper_build_rejects_empty_source_list` | non-generating: validation/failure-path assertion | build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_wrapper_build_rejects_makefile_verbose_combination` | non-generating: validation/failure-path assertion | build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_wrapper_build_rejects_missing_source` | non-generating: validation/failure-path assertion | build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_source/test_compiler_verbose.py::*` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_runtime_abi.py::*` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_source_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/callbacks/test_all_callback_shapes.py::*` | source/generated-.pyi parity or parametrized route | callbacks/trampolines | `legacy` |
| `tests/wrapper/fortran/callbacks/test_array_callbacks.py::*` | source/generated-.pyi parity or parametrized route | callbacks/trampolines; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/callbacks/test_callback_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/callbacks/test_derived_callbacks.py::*` | source/generated-.pyi parity or parametrized route | callbacks/trampolines; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/callbacks/test_scalar_callbacks.py::*` | source/generated-.pyi parity or parametrized route | callbacks/trampolines; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/derived_types/test_borrowed_finalizers.py::*` | source/generated-.pyi parity or parametrized route | derived types/snapshots; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/derived_types/test_constructors_and_finalizers.py::*` | source/generated-.pyi parity or parametrized route | derived types/snapshots; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/derived_types/test_derived_layout.py::*` | source/generated-.pyi parity or parametrized route | derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/derived_types/test_derived_type_boundaries.py::*` | source/generated-.pyi parity or parametrized route | derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/derived_types/test_derived_type_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/derived_types/test_derived_type_methods.py::*` | source/generated-.pyi parity or parametrized route | derived types/snapshots; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/derived_types/test_inheritance.py::*` | source/generated-.pyi parity or parametrized route | derived types/snapshots; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/derived_types/test_pointers.py::test_module_and_derived_pointer_handles_track_native_association[*]` | source/generated-.pyi parity or parametrized route | derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/derived_types/test_pointers.py::test_module_native_array_handles_match_legacy_and_wrapper_plan_routes` | reduced module-only contract with deliberate legacy rollback comparison | borrowed pointer/allocatable handles; descriptor calls; strided extraction; ordinary array actuals; operation permissions | `wrapper-plan` |
| `tests/wrapper/fortran/derived_types/test_pointers.py::test_pointer_array_handles_block_on_unsupported_result_owner_policy[*]` | source/generated-.pyi parity or parametrized route | derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/derived_types/test_pointers.py::test_pointer_descriptor_views_preserve_slice_shape_strides_and_parent_lifetime` | direct wrapper/build route | derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::test_editable_contract_can_use_native_order_arguments_without_native_call` | direct wrapper/build route | semantic .pyi generation/parsing; raw array addresses completed by Phase 6G; derived result remains Phase 8 | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::test_raw_array_addresses_match_legacy_and_wrapper_plan_routes` | reduced edited semantic `.pyi` entries over existing vector/matrix native routines | raw numeric addresses; visible scalar-storage extents; rank one/two; default C and explicit Fortran orientation; mutation; integer-only conversion | `wrapper-plan` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::test_copy_f_preserves_logical_axes_through_binding_owned_temporary` | reduced edited semantic `.pyi` entries over the existing matrix native routine | explicit C-to-Fortran representation copy; native-input and inout calls; projected original identity; binding-owned copyback and cleanup | `wrapper-plan` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::test_fixed_string_storage_and_raw_address_match_legacy_and_wrapper_plan_routes` | reduced edited semantic `.pyi` entry over the existing `fnative_call_examples_f90` native unit | fixed mutable rank-zero NumPy bytes storage; raw fixed-string addresses; in-place mutation; rank/dtype/itemsize/writability/type validation | `wrapper-plan` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_ownership_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py::test_contradictory_ownership_contract_fails_before_bridge_generation` | non-generating: policy validation before bridge generation | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `not-applicable` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py::test_immutable_array_policy_copies_in_and_returns_replacement` | direct wrapper/build route | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py::test_immutable_scalar_string_array_and_derived_policies_return_replacements` | direct wrapper/build route | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_surface_edit_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; classes/methods/properties/overloads; naming/visibility/dispatch | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_visibility_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; scalar module visibility and namespace projection | `wrapper-plan` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_compact_blas_like_folder_generates_one_external_entry_and_preserves_separate_objects` | direct wrapper/build route | external symbols/native linkage; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_external_bind_renames_python_export_without_changing_native_call` | direct wrapper/build route | scalar external symbol; explicit bridge interface; renamed export | `wrapper-plan` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_external_bridge_uses_explicit_interface_and_no_module_use` | direct wrapper/build route | scalar external symbol; explicit bridge interface | `wrapper-plan` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_fixed_form_standalone_external_runtime_parity[*]` | source/generated-.pyi parity or parametrized route | scalar external symbol; explicit bridge interface | `wrapper-plan` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_free_form_standalone_external_runtime_parity[*]` | source/generated-.pyi parity or parametrized route | scalar external symbol; explicit bridge interface | `wrapper-plan` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_generated_external_contracts_are_non_empty_root_fragments` | direct wrapper/build route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_handwritten_c_order_flat_contract_passes_rank_preserving_bridge_view` | direct wrapper/build route | external symbols/native linkage; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_module_procedure_bridge_uses_native_module_scope` | direct wrapper/build route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_namespace_imported_module_rejects_external_marker_before_codegen` | non-generating: validation/failure-path assertion | external symbols/native linkage | `not-applicable` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_one_source_with_several_standalone_externals_exports_each_at_root[*]` | source/generated-.pyi parity or parametrized route | scalar external symbols; explicit bridge interfaces | `wrapper-plan` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_package_entry_rejects_non_external_root_declaration_before_codegen` | non-generating: validation/failure-path assertion | external symbols/native linkage | `not-applicable` |
| `tests/wrapper/fortran/function_calls/test_function_call_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/function_calls/test_native_call_examples.py::test_native_call_examples_build_from_generated_pyi_and_native_shared_library` | direct wrapper/build route | native-call projections; ordinary arrays; strings; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/function_calls/test_native_call_examples.py::test_native_call_examples_cover_scalar_array_string_and_object_projection[*]` | source/generated-.pyi parity or parametrized route | native-call projections; ordinary arrays; strings; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_fixed_form_optional_arguments_drive_fortran_present_behavior[*]` | source/generated-.pyi parity or parametrized route | optional/presence; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_fixed_optional_scalar_wrapper_plan_route_matches_all_presence_states` | production plan route with deliberate legacy rollback comparison | optional/presence; scalar inputs/results; build/artifact integration | `wrapper-plan` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_allocatable_scalar_descriptor_distinguishes_omitted_none_and_value` | production plan route with deliberate legacy rollback comparison | optional/presence; nullable scalar descriptor; build/artifact integration | `wrapper-plan` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_array_descriptors_match_legacy_and_wrapper_plan_routes` | reduced optional descriptor contract with deliberate legacy rollback comparison | omitted/`None` absence; present unallocated/unassociated and allocated/associated handle states; kind/dtype validation | `wrapper-plan` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_arguments_drive_fortran_present_behavior[*]` | source/generated-.pyi parity or parametrized route | optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_array_buffers_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing optional native unit | omitted/`None`/present ordinary array storage; mutation; projected identity; native-handle actuals deferred to Phase 7 | `dual-route` |
| `tests/wrapper/fortran/function_calls/test_scalar_writeback_plan.py::test_scalar_copy_in_out_returns_replacement_through_both_routes` | production plan route with deliberate legacy rollback comparison | scalar copy-in/native mutation/copy-out/cleanup; build/artifact integration | `wrapper-plan` |
| `tests/wrapper/fortran/function_calls/test_output_arguments.py::test_output_arguments_and_multiple_results_follow_python_projection_rules[*]` | source/generated-.pyi parity | mixed-type multiple-result aggregation; ordinary arrays; strings; derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/function_calls/test_output_arguments.py::test_hidden_ordinary_array_output_matches_legacy_and_wrapper_plan_routes` | production output-only plan route with deliberate legacy rollback comparison | fixed/runtime-shape hidden ordinary array output; zero-sized output; allocation/copy failure paths | `wrapper-plan` |
| `tests/wrapper/fortran/layout_rules/test_wrapper_guide_layout.py::*` | non-generating: wrapper docs/test layout | test/docs layout | `not-applicable` |
| `tests/wrapper/fortran/module_state/test_allocatable_replacement.py::test_allocatable_inout_arrays_mutate_and_return_the_same_handle[*]` | source/generated-.pyi parity route | module variables/state; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/module_state/test_allocatable_replacement.py::test_allocatable_replacement_has_no_native_memory_errors[*]` | source/generated-.pyi parity route | module variables/state; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/module_state/test_allocatable_replacement.py::test_projected_allocatable_descriptor_matches_legacy_and_wrapper_plan_routes` | reduced owned-result plus projected-descriptor contract with deliberate legacy rollback comparison | direct persistent descriptor mutation; allocation/reallocation/deallocation; same-handle result identity | `wrapper-plan` |
| `tests/wrapper/fortran/module_state/test_allocatable_views.py::test_allocatable_module_fields_and_results_expose_lifetime_safe_handles[*]` | source/generated-.pyi parity with one mixed generation unit | derived class/field handles and parent retention remain Phase 8/9 blockers | `legacy` |
| `tests/wrapper/fortran/module_state/test_allocatable_views.py::test_scalar_descriptor_module_variables_return_copied_optional_values[*]` | production plan route in source/generated-.pyi parity modes | rank-zero allocatable/pointer arguments, writeback, results, and copied nullable module values | `wrapper-plan` |
| `tests/wrapper/fortran/module_state/test_allocatable_views.py::test_plain_allocatable_module_array_exposes_handle_with_read_only_extraction[*]` | production plan route in source/generated-.pyi parity modes | detached read-only snapshots of plain allocatable module arrays; capsule-owned lifetime | `wrapper-plan` |
| `tests/wrapper/fortran/module_state/test_common_blocks.py::*` | source/generated-.pyi parity or parametrized route | scalar calls with internal common-block storage | `wrapper-plan` |
| `tests/wrapper/fortran/module_state/test_module_state.py::test_aliased_derived_module_object_borrows_native_state[*]` | source/generated-.pyi parity or parametrized route | module variables/state; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/module_state/test_module_state.py::test_scalar_module_variables_use_attributes_and_parameters_have_no_native_setter[*]` | source/generated-.pyi parity or parametrized route | module variables/state | `legacy` |
| `tests/wrapper/fortran/module_state/test_module_state_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/module_state/test_scalar_module_variable_plan.py::test_whole_scalar_module_variable_behavior_matches_legacy_route[*]` | production plan route with deliberate legacy rollback comparison | scalar inputs/results; scalar module variables/state; build/artifact integration | `wrapper-plan` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_makefile_mode_reproduces_multi_source_build` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_file_modules_build_one_merged_extension` | direct wrapper/build route | scalar multi-source build/link orchestration; module variables/state | `wrapper-plan` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_file_standalone_procedures_build_one_merged_extension` | direct wrapper/build route | scalar multi-source external symbols and link orchestration | `wrapper-plan` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_source_generated_contract_build_matches_source_runtime_and_link_order` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state; semantic .pyi generation/parsing | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_source_modified_entry_preserves_modules_and_adds_documented_alias` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_source_pyi_out_writes_one_flat_combined_package` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state; semantic .pyi generation/parsing | `legacy` |
| `tests/wrapper/fortran/naming/test_defined_operators.py::*` | source/generated-.pyi parity or parametrized route | naming/visibility/dispatch; classes/methods/properties/overloads; operators; generic dispatch | `legacy` |
| `tests/wrapper/fortran/naming/test_generic_interfaces.py::*` | source/generated-.pyi parity or parametrized route | naming/visibility/dispatch; classes/methods/properties/overloads; generic dispatch | `legacy` |
| `tests/wrapper/fortran/naming/test_naming_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/naming/test_visibility_naming.py::test_strict_wrapper_names_reject_python_name_fixes` | direct wrapper/build route | naming/visibility/dispatch; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/naming/test_visibility_naming.py::test_visibility_and_default_python_name_fixing_policy[*]` | source/generated-.pyi parity or parametrized route | naming/visibility/dispatch; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_real_blas_lapack.py::*` | full BLAS/LAPACK wrapper generation unit | external symbols/native linkage; build/compile/link orchestration; broad wrapper corpus | `deferred-real-library` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_duplicate_native_definitions_report_linker_error` | direct wrapper/build route | scalar external symbols; linker failure propagation | `wrapper-plan` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_imported_contracts_resolve_from_one_archive_or_shared_library[*]` | source/generated-.pyi parity or parametrized route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_incompatible_native_artifact_reports_linker_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_missing_module_directory_reports_compile_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_missing_symbol_reports_native_link_or_loader_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_mixed_module_external_bundle_resolves_all_native_input_kinds` | direct wrapper/build route | scalar module/external symbols; ordered native inputs and library directories | `wrapper-plan` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_required_transitive_named_library_resolves_runtime_symbol` | direct wrapper/build route | scalar external symbol; transitive named library | `wrapper-plan` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_static_archive_dependency_order_resolves_transitive_library` | direct wrapper/build route | scalar external symbol; ordered archive linkage | `wrapper-plan` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_static_archive_groups_resolve_cyclic_archive_dependencies` | direct wrapper/build route | scalar external symbol; archive-group linkage | `wrapper-plan` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_unavailable_dependent_shared_library_reports_loader_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/runtime_behavior/test_openmp_runtime.py::*` | direct wrapper/build route | runtime policies/errors/GIL; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/runtime_behavior/test_runtime_behavior_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py::*` | source and edited-.pyi production plan route with deliberate legacy rollback comparison | runtime policies/errors/GIL | `wrapper-plan` |
| `tests/wrapper/fortran/runtime_behavior/test_runtime_recursion.py::*` | source/generated-.pyi parity or parametrized route | runtime policies/errors/GIL; scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/scalars/test_fortran_enums.py::test_fortran_enums_preserve_integer_runtime_surface[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/scalars/test_fortran_enums.py::test_fortran_enums_preserve_values_in_generated_pyi_contract` | direct wrapper/build route | scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/scalars/test_scalar_boundary_plan.py::*` | scalar-only copied native routines with deliberate legacy/direct-plan parity | primitive scalar kinds; value and `Addr(Arg(i))` inputs; hidden output; copy-in/copy-out; rank-zero storage; raw `Addr(T)`; native slot reordering; direct-plus-hidden result tuple assembly | `wrapper-plan` |
| `tests/wrapper/fortran/scalars/test_scalar_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/scalars/test_scalar_kinds.py::*` | source/generated-.pyi parity or parametrized route | scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/scalars/test_value_and_bind_c.py::*` | source/generated-.pyi parity or parametrized route | scalar inputs/results; native-call projections | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_fmath_scalar_sources_match_legacy_and_wrapper_plan_routes[*]` | production plan route with deliberate legacy rollback comparison using the existing `fmath.f` and `fmath_f90.f90` generation units | scalar inputs/results; native-call projections; Python namespaces; build/artifact integration | `wrapper-plan` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_f90_wrapper_pipeline_builds_importable_extension[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_fortran_wrapper_pipeline_builds_importable_extension[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results | `wrapper-plan` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_required_array_buffers_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fmath_arrays_f90` native unit | required rank-one dense buffers; exact dtype/rank/order/alignment/writeability; zero length; native-handle actuals deferred to Phase 7 | `dual-route` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_edited_modern_string_contract_wraps_full_axis_spelling_set` | edited semantic `.pyi` contract | strings; fixed/assumed inputs; arrays; mutable string storage | `legacy` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_legacy_fortran_character_arguments_and_results[*]` | production plan route from source/generated-.pyi parity | fixed-form strings; fixed/assumed inputs; fixed results | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_modern_fortran_character_arguments_and_results[*]` | source/generated-.pyi parity | strings; fixed/assumed inputs; fixed/deferred results; arrays; writeback | `legacy` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_deferred_allocatable_string_results_match_legacy_and_wrapper_plan_routes` | reduced scalar descriptor result contract with deliberate legacy rollback comparison | runtime length; nullable copy-out; UTF-8 data; allocation failure | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_deferred_character_array_handles_match_legacy_and_wrapper_plan_routes` | reduced descriptor-result and projected-descriptor contract with deliberate legacy rollback comparison | hidden/direct owned deferred-character arrays; runtime `S3`/`S4`/`S5` width; projected identity; nullable rank-zero result | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_fixed_width_character_arrays_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fstrings_f90` native unit | fixed-width `NPY_STRING` array itemsize; rank/dtype/zero-size validation; native-handle actuals deferred to Phase 7 | `dual-route` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_raw_fixed_width_character_arrays_match_legacy_and_wrapper_plan_routes` | reduced edited semantic `.pyi` entry over the existing `fstrings_f90` native unit | raw fixed-width character array address; literal shape; element length; integer-only conversion | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_required_scalar_string_inputs_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fstrings_f90` native unit | required fixed/assumed scalar string inputs; default/kind-1/`c_char`; UTF-8 length and NUL validation; scalar results | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_fixed_string_results_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fstrings_f90` native unit | direct fixed string results; trailing blanks; default/`c_char`; allocation failure | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_edge_cases.py::test_fortran_character_edge_cases_follow_copy_in_copy_out_policy[*]` | production plan route from source/generated-.pyi parity | strings; fixed/assumed input/output; optional presence; Unicode/NUL handling | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_edge_cases.py::test_fixed_hidden_string_output_matches_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fcharacter_edges_f90` native unit | fixed hidden string output; trailing blanks; allocation failure | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_edge_cases.py::test_fixed_string_replacement_and_identity_match_legacy_and_wrapper_plan_routes` | reduced edited semantic `.pyi` entry over the existing `fcharacter_edges_f90` native unit | fixed immutable replacement and discarded identity; exact length; trailing blanks; allocation failure | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_character_edge_cases.py::test_assumed_and_optional_string_replacements_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fcharacter_edges_f90` native unit | assumed-length and optional immutable replacement; empty/omitted/`None`/concrete states; NUL rejection; concrete-only allocation failure | `wrapper-plan` |
| `tests/wrapper/fortran/strings/test_string_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |

## Incremental Protocol

For each lane:

1. Select and run an existing passing `tests/wrapper` generation unit through
   the legacy route. Retain and inspect its complete generated artifact set.
2. Trace the current lowering, binding, bridge, node/API-model, printer,
   runtime-helper, and build paths that produced those artifacts, and record the
   observed behavior and existing tests that make them the migration baseline.
3. Expand this checklist with the lane's exact scope, exclusions, source-path
   baseline, required backend behavior, plan fields, and validation invariants.
4. Complete every policy field required by the lane in post-IR policy
   completion; do not start its planner while semantic decisions remain
   scattered or implicit.
5. Implement the lane's hierarchical plan records, planner visitors,
   ABI/handoff specs, generator-owned structural checks, directly named backend
   lowering methods, source-printer support, and support-report coverage.
6. Implement the minimum dependency-closed backend slice in
   `x2py.wrapper_codegen`: copy small suitable pieces, rewrite oversized legacy
   classes as minimal equivalents, and add only the intermediate tests required
   by the contract above.
7. Generate the plan from policy-completed semantic IR, invoke the directly
   named binding and bridge lowering methods, assemble complete backend modules,
   and print complete internal artifacts.
8. Compare the new generated artifacts with the retained legacy artifacts and
   explain every material difference before compilation.
9. Compile the internal artifacts before changing production route selection.
10. Run the same eligible existing fixtures and assertions through both routes
   and compare compiled runtime behavior, failure paths, native-call mapping,
   and artifact requirements.
11. Extend the whole-module support predicate so a generation unit uses the
   wrapper-plan route only when all its elements belong to completed lanes.
   Keep the old route for generation units containing unsupported lanes.
12. Update every affected `tests/wrapper` migration-matrix row and mark the lane
    complete only when the reused parity tests pass and every intentional
    difference from the baseline is separately documented.

Do not start a later lane by guessing. Each lane must define the handoff specs
and consistency checks it needs.

## Mandatory Expansion Gate For Broad Phases

Phases 5 through 10 are roadmap envelopes, not complete implementation
checklists. Before implementation starts on one of them, update this file and
split that phase into dependency-ordered sub-lanes. The expansion must be based
on an audit of the live semantic models, completed policies, existing
bridge/binding behavior, decorators, and focused wrapper tests.

Each expanded sub-lane must state:

- the exact included and excluded semantic cases;
- the completed-policy fields it consumes and any decisions that still need to
  move into post-IR policy completion;
- plan records, action keys, handoff specs, native-call slots, lifecycle phases,
  and required generated artifacts;
- binding and bridge handler names and which backend-local helper values they
  may create;
- validation invariants across Python input/result, binding handoff, bridge
  handoff, native call, writeback, cleanup, ownership, and release;
- the whole-module support-predicate change that makes the sub-lane eligible;
- existing `tests/wrapper` nodes that cover the sub-lane, their migration-matrix
  status changes, and dual-route parity evidence against the legacy route;
- the exact legacy source path and consumed behavior for every isolated
  primitive, whether it is copied or rewritten, its minimal dependency closure,
  baseline evidence, and a reason for every behavior with no legacy source;
- dependencies on earlier lanes and the legacy behavior that can be removed
  when the sub-lane is complete.

Do not mark a broad phase complete from its current envelope items. Mark its
expanded sub-lanes individually, then close the phase only after all live cases
in its audited support matrix are either migrated or explicitly removed from
the product contract.

## Dependency-Ordered Checklist

### Foundation and semantic authority

- [x] Establish the isolated `x2py.wrapper_codegen` package boundary and
  visitor infrastructure.
- [x] Complete the first primitive lane in general wrapper policy before
  planning, including native-call order, result projection, ownership, and
  lifecycle facts.
- [x] Build editable `ModulePlan`, `FunctionPlan`, transfer, result, ABI,
  native-slot, and lifecycle records from completed wrapper policy.
- [x] Refactor each cross-boundary owner into explicit binding and bridge child
  plans, including module/function/result/lifecycle scope as well as arguments.
- [x] Remove plan-owned method names and handler registries; add typed
  datatype-family facts required by direct lowering.
- [x] Keep structural plan validation private to `WrapperCodeGenerator`, with
  no planner-time validation or standalone validator class, and verify every
  listed invariant after direct plan edits.

### Direct generator boundary

- [x] Change `WrapperCodeGenerator.generate` to consume only `ModulePlan`,
  freeze it, validate it, validate lowering support, recursively generate
  backend nodes, print them, and return artifacts directly.
- [x] Implement recursive `CBindingGenerator` synthesis of complete C modules,
  headers, and functions from plan nodes.
- [x] Implement recursive `FortranBridgeGenerator` synthesis of complete
  Fortran modules and functions from plan nodes.
- [x] Replace plan-selected method names with directly named backend lowering
  methods selected by the visible `_lower_{subject}_{action.value}` rule.
- [x] Ensure backend node printers, artifact construction, and build
  consumption retain their distinct freezing boundaries.

### Scalar parity and route evidence

- [x] Replay the existing scalar source and semantic-`.pyi` baseline through
  the direct generator and compare generated artifacts and runtime behavior.
- [x] Update the staged walkthrough to use only plan editing and the public
  generator boundary.
- [x] Retire superseded internal representations, their package exports,
  orchestration, validation, documentation, and focused tests.
- [x] Run focused wrapper-codegen and pipeline tests; the walkthrough for both
  supported entry choices where practical; `tests/wrapper` excluding LAPACK;
  documentation checks; `git diff --check`; the required static-analysis suite;
  and `tools/check_wrapper_codegen_complexity.py`.

## Phase 3 — Scalar Inout, Optional, And Descriptor-Like Scalars

Scope: scalar copy-in/copy-out, optional arguments, present-but-null descriptor
values, and scalar allocatable/pointer descriptor boundaries.

Phase 3 legacy replay audit:

- `foptional_fixed.f` uses one nullable value pointer at the Bind-C ABI.
  Omission and explicit `None` both pass a null pointer because both mean that
  the ordinary optional dummy is absent; a concrete scalar uses call-local
  storage, and the bridge branches on `c_associated(...)` before calling the
  native function with or without the optional keyword.
- The existing optional allocatable-scalar contract uses two independent ABI
  pointers. The value pointer is null for explicit `None`, while the presence
  pointer is non-null for both `None` and a concrete value. Omission leaves both
  null. The bridge therefore distinguishes absent, present-unallocated, and
  present-with-value states without inferring presence from the value pointer.
- Immutable scalar replacement uses copy-in storage, native mutation of that
  storage, copy-out to a new Python scalar, and scope-owned stack cleanup. The
  caller's original NumPy scalar remains unchanged. The audit found no existing
  runtime wrapper test for this primitive-scalar `Returns["argument", T]`
  contract, so `test_scalar_writeback_plan.py` is the recorded coverage-gap
  fixture for this lane.
- The first legacy replay of that coverage gap exposed a duplicate declaration
  of the mutable scalar result. The legacy bridge now promotes the copy-in
  temporary to the Bind-C function result and removes it from the ordinary
  local-declaration set. Both routes compile, and incompatible Python values
  fail with `TypeError` before the native call. Stack temporaries and local
  allocatable descriptors require no explicit release action; their procedure
  scope owns cleanup on normal return.

The Phase 3 plan records optional mode, nullable value and presence handoffs,
and four ordered scalar replacement phases: `copy_in`, `native_mutation`,
`copy_out`, and `cleanup`. Generator preflight requires the complete phase set,
an existing source handoff, the correct binding/bridge owner for each phase,
and a Python result target for copy-out. Forced whole-module route selection
accepts these completed lanes after the dual-route evidence below. Automatic
production selection still remains on the legacy route under the independent
GIL parity deferral recorded for Phase 2D.

- [x] Audit and record the legacy copy-in/out, optional presence, nullable
  scalar descriptor, cleanup, and failure-path behavior for this lane.
- [x] Add or rewrite only the additional optional/descriptor nodes, API
  primitives, local-state helpers, and printer cases required by this lane,
  with baseline tests.
- [x] Represent copy-in, native mutation, copy-out, and cleanup as explicit
  writeback phases.
- [x] Preserve the three-state optional rule: omitted argument, explicit `None`,
  and present concrete value are distinct when the native ABI needs them.
- [x] Represent scalar descriptor presence tokens and nullable value handoffs in
  the plan.
- [x] Validate that a writeback consumes an existing binding/bridge handoff and
  writes to a Python-visible target or result slot.
- [x] Emit and print complete inout/optional/descriptor-capable modules
  internally, then compile and compare both routes for all three presence
  states, mutation, writeback, cleanup, ABI, and failures.
- [x] Widen whole-module route eligibility to this lane only after parity, and
  complete it before moving arrays or handles to the plan path.

## Phase 4 — Scalar Module Variables

Scope: scalar module variables. Derived-type fields remain in Phases 8 and 9
because their wrapper instance, owner, and property lifecycle must already be
represented before field access can use the plan route.

Phase 4 legacy replay audit:

- `fmodule_vars_f90.f90` establishes the ordinary scalar state contract. Its
  legacy bridge emits value-returning getters and value-argument setters;
  binding accessors run with the GIL held, aliases route to the same native
  storage, deletion fails, and contract initializers call the native setter at
  import. A `parameter` is instead copied into the Python module dictionary, so
  rebinding it is local to that module object and never mutates native storage.
  This whole source remains legacy because it also owns `rgb_color` and derived
  module objects from later phases.
- The scalar subset of `fscalar_descriptors_f90` establishes nullable
  allocatable and pointer reads. The legacy bridge returns null for absent
  storage or allocates and copies one detached scalar; the binding converts the
  copy, frees it, and rejects descriptor replacement. Its whole source cannot
  migrate in Phase 4 because it also contains nullable snapshot-result forms
  from a later lane. Allocation failure is deliberately injected with
  `X2PY_WRAPPER_FAIL_ALLOC` and preserves the legacy null/`None` surface.
- No existing generation unit contained only the already completed scalar
  function lanes plus every Phase 4 getter, setter, constant, descriptor,
  initialization, reload, and failure behavior. The bounded
  `test_scalar_module_variable_plan.py` whole-module fixture records that
  coverage gap; it contains no strings, arrays, classes, or later-phase owner.

The plan keeps only completed typed facts: Python names, getter and setter
actions, initializer or constant value, datatype family, native name/module,
native assignment, descriptor kind, and handoff roles. Both backends invoke
directly named lowering methods with matching subject/action suffixes wherever
their behavior is shared; datatype and descriptor facts stay method inputs.
The generator validates the complete frozen plan before either backend emits
anything, including binding/bridge getter agreement and the rule that a Python
write-through setter must have a compatible bridge setter role. Forced
whole-module selection now accepts `scalar-module-variables`; automatic
production selection remains independently deferred by the Phase 2D GIL gate.

- [x] Audit and record the legacy scalar module-variable getter, setter,
  rejected replacement, module initialization, and attribute-routing behavior.
- [x] Add or rewrite only the additional module/type nodes, getter/setter API
  primitives, initialization nodes, and printer cases required by this lane,
  with baseline tests.
- [x] Represent getter behavior, setter exposure, native setter assignment, and
  rejected replacement behavior in module-variable plans.
- [x] Add binding actions for Python attribute get/set around scalar values.
- [x] Add bridge actions for scalar module-variable read/write.
- [x] Validate getter/setter pair consistency: a Python setter cannot exist
  without a compatible bridge setter handoff.
- [x] Keep ordinary Python module-name rebinding semantics separate from native
  module-variable storage.
- [x] Emit and print complete module-variable-capable modules internally, then
  compile and compare both routes for get/set behavior, rejection paths,
  initialization, cleanup, ABI, and generated artifacts.
- [x] Widen whole-module route eligibility to scalar module variables only after
  that parity evidence passes.

### Phase 3/4 whole-unit namespace correction

The post-Phase 4 review found that scalar lowering itself matched the legacy
route, but the parity helper unwrapped a sole native child module before making
assertions. That hid a public-surface difference: the legacy route retained
Fortran modules as Python child namespaces while the plan route flattened their
members at the extension root. The support analyzer also accepted colliding
procedures from separate native modules and allowed the failure to reach the
Fortran compiler.

This correction is part of the completed scalar foundation rather than a new
datatype lane:

- [x] Add a concise `NamespacePlan` beneath `ModulePlan`; place functions and
  variables in namespace nodes instead of flattening them into the module.
- [x] Complete Python export paths in post-IR export policy, including
  namespace-local keyword and collision fixes, then mechanically group plan
  owners by those paths without reconstructing namespace policy in either
  backend.
- [x] Generate root, child, and nested Python modules while keeping native
  module imports and generated bridge symbols unambiguous.
- [x] Support ordinary scalar subroutines with no projected result through the
  existing native call plus Python `None` result path.
- [x] Reject duplicate Python exports and generated symbols before either
  backend emits source.
- [x] Use one visible lowering naming rule in both backends:
  `_lower_argument_<optional-mode>`, `_lower_result_<codegen-action>`,
  `_lower_writeback_<codegen-action>`, `_lower_module_getter_<getter-action>`,
  and `_lower_module_setter_<setter-action>`. Do not store method-name strings
  in the plan or hide these selections in backend dictionaries.
- [x] Remove scalar prefixes from general wrapper concepts, including the
  function, argument, result, native-slot, lifecycle, node, and printer policy
  surfaces. Retain scalar naming only for permanently scalar-specific ABI type
  facts and actions.
- [x] Update the staged walkthrough to print the namespace tree, typed actions,
  and the directly corresponding binding and bridge method names.
- [x] Compile both routes from the existing complete
  `contract_mixed_module_external.f90`, `contract_import_graph.f90`,
  `contract_multi_module.f90`, `contract_standalone_only.f90`, and
  `contract_same_name.f90` fixtures; compare the real extension root and child
  namespaces without `_sole_native_module` normalization.

## Phase 2D — Native Call Runtime Envelope

This is the next dependency-closed migration lane. Complete it before Phase 5
so the already proven scalar generation units can move from temporary
`dual-route` evidence to production `wrapper-plan` routing instead of adding
more datatype lanes behind the same runtime gate.

Scope: the binding-owned runtime envelope around an otherwise completed native
call. This phase includes default GIL release, explicit `@hold_gil`, and native
status/message projection through `@raises(...)`. Status projection is included
because the existing `fruntime_policy_f90` generation unit tests it together
with both GIL modes and whole-generation-unit routing cannot split that module.

Excluded from this phase:

- strings, arrays, descriptors, derived types, and callbacks, which remain in
  their datatype or callback phases;
- callback re-entry and callback exception/abort behavior, which remain in
  Phase 10;
- OpenMP array execution and Makefile-specific behavior, which remain blocked
  by the array and cross-cutting build lanes;
- general Python exception translation that is not selected by a completed
  native status policy.

The existing legacy/runtime oracle is
`tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py` in both its
source-driven and semantic-`.pyi`-driven forms. It proves that an ordinary
native pause releases the GIL, `@hold_gil` keeps it held, successful status
returns produce the declared Python result, failing status returns raise the
selected exception with the native message, and emitted C places
`Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS` only around eligible native
calls. `test_recursive_native_runtime_calls` is the scalar regression unit to
run after the call envelope works. Do not use the OpenMP or callback fixtures
as the first parity unit.

The plan and generators must follow these boundaries:

- Post-IR policy completion owns `hold_gil` and the complete native status
  error decision, including status source, message source, success value, and
  Python exception kind. The planner only projects those completed facts.
- Keep the runtime facts concise and function-owned. Extend the existing
  binding-facing function plan rather than adding a second function plan or a
  backend dispatcher table. The bridge continues to lower native call slots
  and result storage mechanically; it does not decide GIL or Python exception
  policy.
- Argument parsing and conversion, Python result construction, status/message
  conversion, exception creation, writeback, and Python-owned cleanup always
  run with the GIL held. For the default policy, release the GIL immediately
  before the bridge call and reacquire it immediately after that call. For
  `hold_gil=True`, emit no release region.
- Perform status evaluation and raise the selected Python exception only after
  the GIL has been reacquired. Validate before emission that every status and
  message projection names an existing native result slot with a compatible
  completed handoff.
- Use directly named lowering methods that follow the existing visible naming
  rule. Do not infer runtime policy from result types, function names, emitted
  locals, or the presence of status-like native arguments.

The completed legacy audit found one binding-owned envelope in both oracle
builds. The legacy binding parsed and converted Python inputs with the GIL
held, emitted `Py_BEGIN_ALLOW_THREADS` immediately before the bridge call and
`Py_END_ALLOW_THREADS` immediately after it by default, and omitted both
macros for `@hold_gil`. Only after reacquiring the GIL did it convert hidden
status/message outputs, compare status with `success`, construct
`RuntimeError`, suppress those policy outputs from the declared Python result,
and decref converted result objects on both the failure and success paths. A
missing or incompatible status/message name was previously rediscovered from
raw decorator dictionaries and result datatypes in `ir2ast` and the legacy C
binding; Phase 2D moved that decision to typed post-IR completion and left the
legacy route as a dispatch consumer for rollback parity.

The direct plan route now preserves that ordering with explicit released-call
and held-call lowering methods. Its fixed native message handoff is
bridge-owned null-terminated storage that the binding converts and frees after
the GIL is reacquired. Generated symbol spelling differs from the legacy
artifacts, but the same source and edited-`.pyi` concurrency, exception,
cleanup, and runtime assertions pass. Production cutover also reused the
existing rendered-artifact build path for inferred native module include
directories, native library directories, `.pyi` manifests, verbose timing,
and scalar external explicit interfaces; no legacy retry was added.

- [x] Audit and record the exact legacy GIL release/hold region, status/message
  projection, exception construction, result suppression, cleanup, and failure
  behavior from both existing runtime-policy tests.
- [x] Complete the native status error decision in post-IR policy before
  planning; retain the already completed `hold_gil` fact as its single source
  of truth.
- [x] Extend the concise function plan with only the binding-facing runtime
  facts needed for GIL and status-error lowering, and validate all referenced
  native result slots before either backend emits source.
- [x] Add direct binding lowering for the released-call and held-call envelopes
  plus post-call status projection. Keep the bridge call and result-slot
  lowering on their existing paths.
- [x] Replay both source and semantic-`.pyi` forms of
  `test_runtime_policies.py` through legacy and wrapper-plan routes using the
  same concurrency, exception, artifact, and generated-C assertions.
- [x] Run `test_recursive_native_runtime_calls` through the wrapper-plan route
  as the scalar recursion regression; leave OpenMP and callbacks in their
  later lanes.
- [x] After dual-route parity passes, remove the blanket Phase 2D production
  deferral. Let whole-generation-unit support select `wrapper-plan` only for
  units whose feature lanes are complete; do not add fallback or per-function
  mixed routing.
- [x] Move the eligible scalar matrix rows from `dual-route` or `legacy` to
  `wrapper-plan`, update the live route counts, and prove their default builds
  no longer invoke `semantic_ir_to_codegen_ast()`.
- [x] Finish this phase only when the production `wrapper-plan` count is
  nonzero and the already completed scalar baseline no longer depends on the
  legacy route outside deliberate rollback diagnostics.

## Phase 2E — Scalar Boundary Completion and Test Isolation — Complete

Complete the scalar public boundary before stopping this migration lane. This
phase does not begin strings or arrays. It separates scalar evidence from
mixed generation units so whole-unit routing cannot hide whether one scalar
policy is implemented.

Scope: every supported primitive scalar kind; ordinary Python scalar values;
`Addr(Arg(i))` call-local address projection; projected scalar copy-in/copy-out;
caller-owned rank-zero NumPy storage spelled `T[()]`; caller-supplied integer
raw addresses spelled `Addr(T)`; and visible or hidden scalar `in`, `out`, and
`inout` behavior. For a mixed native fixture whose declarations cannot be
safely sliced, add a small distinctly named scalar-only native test routine
that preserves the policy decision under test.

The boundary contract remains:

- `T` accepts a Python/NumPy scalar value. When native code only reads it, the
  wrapper converts into call-local storage. When native code writes through an
  address projection and the contract projects `Returns["name", T]`, the
  wrapper performs copy-in, native mutation, and copy-out to a replacement
  Python scalar; the caller's immutable scalar object is not mutated.
- `T[()]` accepts a rank-zero NumPy array with exactly the declared dtype. The
  wrapper validates caller storage and passes its data address; native `out` or
  `inout` mutation remains visible in that same array and the Python call
  returns `None` unless the contract declares another result.
- `Addr(T)` accepts an integer address such as `array.ctypes.data`. The wrapper
  converts it to a raw pointer and forwards that same address without copying
  or owning the pointee. Mutation is therefore observed through caller-owned
  storage.
- `@native_call(...)` controls only native slot order and value/address/result
  projection. It does not change which Python representation (`T`, `T[()]`, or
  `Addr(T)`) the declared argument accepts.
- Use one necessary-copy rule. For interoperable scalar replacement, the
  binding's converted C scalar is the copy-in storage and the bridge passes
  that same storage directly to the native routine; after mutation the binding
  converts it once to the Python replacement. `c_f_pointer` association for
  `T[()]` or `Addr(T)` is not a data copy. A bridge-local data copy is allowed
  only when the native representation actually changes, such as descriptor,
  string-buffer, or ownership-snapshot construction.
- Enforce that rule with a completed `BridgeDataAction` on every argument,
  result, and native-call output slot. `DIRECT_TRANSFER` reuses boundary
  storage, `ASSOCIATE_VIEW` may create only a non-owning native view,
  `COPY_REPRESENTATION` is the sole bridge data-copy permission and requires a
  non-empty policy reason, and `BLOCKED` keeps the whole generation unit off
  the plan route. A non-copying action carrying a copy reason is also invalid.
  New array, string, or object support must complete this fact before route
  eligibility is widened.

Excluded: simultaneous multiple-result tuple assembly; rank-positive arrays;
strings including fixed status buffers except for already completed Phase 2D
status projection; derived types; callbacks; and any compatibility fallback to
the legacy generator.

- [x] Record scalar-only tests separately from mixed array/string/derived
  generation units in the route ledger; use copied minimal native routines
  when fixture declarations are coupled.
- [x] Cover every primitive scalar kind exercised by the scalar runtime suite
  through the direct registry and both binding/bridge generators.
- [x] Add direct named binding and bridge lowering for rank-zero numeric/logical
  storage using the completed `SCALAR_STORAGE` and `PASS_STORAGE_ADDRESS`
  decisions; validate dtype, rank zero, and writability before the native call.
- [x] Add direct named binding and bridge lowering for primitive raw addresses
  using the completed `RAW_ADDRESS` and `PASS_RAW_ADDRESS` decisions; accept an
  integer address and forward it without copy or ownership inference.
- [x] Prove isolated scalar input, hidden output, copy-in/copy-out `inout`,
  caller-storage `out`/`inout`, and raw-address `out`/`inout` behavior through
  compiled legacy/direct-plan parity where applicable.
- [x] Prove scalar copy-in/copy-out reuses one binding local and does not add a
  redundant bridge-local value copy.
- [x] Prove plan validation rejects an unexplained bridge copy, a copy reason
  on a non-copying path, and any still-blocked bridge data action.
- [x] Prove isolated `@native_call` argument mapping, including `Addr(Arg(i))`
  and hidden `Return(...)` slots, without arrays determining route selection.
- [x] Move only proven scalar-only nodes to `wrapper-plan`, update collected
  route counts, and leave the original mixed integration nodes on their real
  datatype blockers.

## Phase 2F — Multiple Scalar Result Assembly — Complete

This is result aggregation, not another scalar boundary representation. The
first isolated oracle is the `with_scalar` policy from
`test_output_arguments.py`: one direct primitive scalar function return plus
one hidden primitive scalar output, assembled into a Python tuple in declared
result order. Keep it separate from arrays, strings, derived types, and native
handles before widening the plan route.

The completed representation is an ordered `FunctionWrapperPolicy.results`
tuple and an ordered `FunctionPlan.results` tuple. Each Python-visible result
has its own `ResultPolicy` and `ResultPlan`, including its binding consumer and
`result_position`. A direct native function return has
`source_kind="direct_return"` and no native-call slot. A hidden output has
`source_kind="hidden_output"` and references the exact same mutable
`NativeCallSlotPlan` stored in `FunctionPlan.native_call_slots`. The bridge
uses the sole direct result, when present, to select its function result and
passes every hidden result through its completed output-address slot. It does
not assemble Python results.

After the native call, the binding converts each result from its completed
source role exactly once. One result is returned directly; two or more are
assembled into a Python tuple in ascending `result_position`. Tuple allocation,
reference transfer, and failure cleanup are binding-local emission details,
not semantic policy. Before either backend emits source, validation requires
result positions to cover `0..N-1` exactly once, at most one direct result,
every hidden result to share its function native-call slot, and every
non-status native output slot to have exactly one binding result consumer.
Phase 2F does not combine these consumers with projected argument writeback;
that broader aggregation remains blocked until it receives its own completed
policy.

- [x] Add a scalar-only copied native routine and contract for a direct return
  plus hidden scalar `Return(...)` slot.
- [x] Represent every Python result as an explicit binding consumer while
  preserving the bridge's direct-return and output-address ABI roles.
- [x] Validate contiguous result positions and reject unclaimed outputs before
  either backend emits source.
- [x] Prove compiled legacy/direct-plan parity, then update the route counts.

## Phase 5 — Strings

Scope: non-descriptor scalar character values, fixed-length strings, assumed-
length call inputs, immutable replacement, mutable rank-zero byte storage, and
raw fixed-length character addresses. Character arrays remain in Phases 6 and
7; allocatable or pointer scalar character values remain in Phase 7; character
fields remain in Phases 8 and 9; character callbacks remain in Phase 10.

The legacy wrapper is the behavioral oracle for this phase. In particular,
`CPythonBindingGenerator._convert_python_string_value_argument()` and
`_convert_python_string_storage_argument()` define Python conversion,
validation, allocation, and writeback behavior, while
`FortranToCBridgeGenerator._build_string_argument()`,
`_build_string_storage_argument()`, `_convert_raw_string_argument()`, and
`_convert_string_result()` define the bridge representation. The public
contract and observable oracle are
`docs/user/guide/fortran-wrapper.md`, `docs/user/guide/data-types.md`,
`docs/user/reference/semantic-pyi-format.md`,
`tests/wrapper/fortran/strings/test_character_arguments.py`, and
`tests/wrapper/fortran/strings/test_character_edge_cases.py`. Direct-plan
lowering may use different temporary names or an equivalent internal C ABI,
but it must preserve the legacy Python behavior, native argument order,
character payload, length, ownership, cleanup, and result projection.

Strings use the same completed-policy and planning pipeline as the other
rank-zero scalar families:

```text
ArgumentPolicy -> ArgumentTransferPlan -> NativeCallSlotPlan
ResultPolicy -> ResultPlan
LifecyclePolicy -> LifecycleActionPlan
```

Do not add a parallel string plan hierarchy or plan-owned handler names.
Numeric and logical primitive families share registry-backed lowering because
their generated structure is the same. `DatatypeFamily.STRING` dispatches to
its own directly named binding and bridge lowering methods because character
conversion and ABI structure differ. The existing `STRING_VALUE`,
`STRING_STORAGE`, `PASS_CALL_LOCAL_ADDRESS`, `PASS_STORAGE_ADDRESS`,
`PASS_RAW_ADDRESS`, and generic codegen/lifecycle actions remain authoritative;
add a new typed action only if those completed actions cannot identify a real
semantic choice.

Every string argument plan records the completed fixed positive character
length or the absence of a fixed length. The binding-to-bridge handoff records
both the payload address and encoded payload length when the bridge needs both;
this is an ABI fact in the existing argument transfer, not a new planning
stage. A fixed `String[n]` Python value must encode to exactly `n` bytes. A
plain `String` input carries its runtime UTF-8 byte length. Embedded NUL is
rejected before the native call. The bridge may copy bytes into Fortran
character storage only when `BridgeDataAction.COPY_REPRESENTATION` and its
non-empty policy reason were completed before planning.

The phase is split into the following dependency-ordered sub-lanes.

### Phase 5A — Required Read-Only String Values

Included: required rank-zero `String[n]` and `String` Python `str` inputs;
default character, kind `1`, and `c_char`; fixed-length exact encoded-byte
validation; assumed-length runtime payload size; embedded-NUL rejection; and
primitive scalar or void results already supported by earlier phases.

Excluded: writable inputs, projected replacement, optional strings, string
results, mutable `String[n][()]` storage, raw `Addr(String[n])`, arrays,
allocatable/deferred results, fields, and callbacks.

Completed policy must provide `ObjectKind.STRING`,
`PythonBarrierAction.STRING_VALUE`,
`NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS`,
`CodegenAction.CALL_LOCAL_INPUT`, `StorageMode.STACK`, required presence,
`BridgeDataAction.COPY_REPRESENTATION`, and the reason that C UTF-8 bytes are
materialized as Fortran character storage. Planning projects those facts into
the ordinary argument/native-slot records. The C binding method
`_lower_argument_required_string_value()` validates `str`, extracts UTF-8 plus
byte length, rejects embedded NUL, and enforces a fixed length when present.
The Fortran bridge method `_lower_argument_required_string_value()` receives
the payload address and length, associates a byte view, copies it into one
backend-local character temporary, and passes that temporary in the completed
native-call position.

Validation requires a string-value Python action, call-local-address native
action, character-buffer handoff, one matching payload-length role, required
presence, no projected result, and a justified representation copy. Whole-unit
eligibility widens only for generation units containing this lane plus already
completed scalar/result/runtime lanes. Replay uses the existing
`fstrings_f90` native object and contract package with a reduced entry that
exports only existing read-only scalar string procedures; both routes run the
same fixed/assumed-length, kind, NumPy-string-scalar, wrong-length, and embedded
NUL assertions. The mixed original string nodes remain `legacy` because their
units also contain string results, writable strings, arrays, and allocatables.

- [x] Complete Phase 5A policy, ordinary plan projection, validation, named C
  and Fortran lowering, reduced-entry dual-route runtime parity, support
  predicate, and migration-ledger evidence.

### Phase 5B — Fixed-Length String Results And Hidden Outputs

Included: direct fixed-length scalar character results and fixed-length hidden
`intent(out)` results, including trailing blanks. The binding receives a
NUL-terminated C-owned copy, converts the full payload to a Python-owned
`str`, and releases the temporary exactly once. The bridge allocates and fills
that copy only through completed `COPY_REPRESENTATION` policy. Deferred-length
and nullable allocatable or pointer results remain in Phase 7 because their
runtime length and allocation state are descriptor lifecycle facts, not
scalar-string conversion facts.

Both forms reuse the ordinary ordered `ResultPolicy -> ResultPlan` path and
record the fixed positive `character_length` on the result. A direct native
function result has `source_kind="direct_return"`,
`CodegenAction.COPY_OUT`, no native-call slot, and a bridge function result of
`type(c_ptr)`. The bridge first receives the native value in backend-local
`character(kind=c_char, len=n)` storage, then allocates `n + 1` bytes through
the existing `x2py_malloc` interface, copies all `n` characters, appends
`c_null_char`, and returns the pointer. A hidden output has
`source_kind="hidden_output"`, `CodegenAction.COPY_OUT`,
`NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS`, and references the exact same
fixed-length `NativeCallSlotPlan` used by the function. Its existing output
slot receives native character storage, then performs the same justified
allocation and copy after the native call.

In both cases, binding lowering checks for a null allocation, converts the
NUL-terminated UTF-8 payload with the same observable behavior as the legacy
`Py_BuildValue("s", ...)` path, frees the C allocation exactly once even when
Python conversion fails, and returns the Python-owned `str`. Phase 5B supports
exactly one Python-visible string result per function; mixed or multiple
string result aggregation remains blocked until cleanup of every unconverted
native allocation is explicitly planned. A function that combines a public
fixed string result with native status-error projection is blocked for the
same reason: the status failure path must not bypass the string allocation's
planned release.

Validation requires a fixed positive length, `ObjectKind.STRING`, Python-owned
copy-return ownership, no Python barrier action, the source-appropriate
codegen/native action, `BridgeDataAction.COPY_REPRESENTATION` with the standard
fixed-string copy reason, and matching result/native-slot lengths for hidden
outputs. Direct results must not carry a native-call slot; hidden results must
share their function slot by identity. The C and Fortran backends dispatch
`DatatypeFamily.STRING` to `_lower_result_fixed_string()` methods instead of
the primitive scalar registry.

Replay direct results from the existing `fstrings_f90` native object with a
reduced contract entry exporting `char_result_default`,
`char_result_c_char`, `string_result_fixed`, `string_result_padded`, and
`string_result_c_char`. Replay the hidden output from the existing
`fcharacter_edges_f90.make_out` unit through another reduced entry. Run the
same trailing-blank and returned-value assertions through legacy and direct
routes. The original mixed nodes remain `legacy` on deferred results, writable
strings, optionality, or arrays.

- [x] Complete fixed-length direct and hidden string result policy, result-plan
  length facts, allocation/failure cleanup, binding conversion, bridge copy,
  validation, legacy/direct parity, support widening, and ledger updates.

### Phase 5C — Immutable String Output And Inout Replacement

Included: fixed and assumed-length Python `str` output/inout dummies, including
the pass-by-address mutable native call. Python strings remain immutable: the
binding creates mutable call-local storage; the bridge passes that storage to
the native dummy; a declared `Returns["name", String...]` consumer returns a
replacement string; identity form discards native mutation and returns `None`.
Fixed buffers retain their complete post-call contents and trailing blanks;
assumed-length buffers use the encoded input length. Optional omitted,
explicit-`None`, and concrete-value states are handled here after required
replacement works.

The first Phase 5C slice is required fixed-length `String[n]` only. A projected
replacement consumes completed `ObjectKind.STRING`, Python-owned
`COPY_RETURN`, `PYTHON_REFCOUNT`, stack contract storage,
`PythonBarrierAction.STRING_VALUE`,
`NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS`,
`CodegenAction.COPY_IN_OUT`, native mutation, result projection, and
`BridgeDataAction.COPY_REPRESENTATION` with the fixed-string replacement copy
reason. The ordinary argument plan records those facts plus the fixed positive
character length, and its binding and bridge views both carry the completed
codegen action. The same mutable native-call slot is referenced throughout;
there is no second output slot.

The binding validates the input exactly as Phase 5A does, allocates one
`n + 1` byte call-local buffer through `x2py_malloc`, copies all `n` encoded
bytes, and appends NUL. Allocation failure raises `MemoryError` before native
execution. The bridge receives the mutable buffer and length, materializes
backend-local `character(kind=c_char, len=n)` storage, passes that storage to
the native dummy, then copies the complete post-call value back into the
binding buffer and restores the NUL terminator. After the call, binding
`_lower_writeback_string()` converts the replacement with the same
`Py_BuildValue("s", ...)` behavior as the legacy route and frees the call-local
buffer exactly once whether conversion succeeds or fails.

The existing ordered lifecycle records remain authoritative:

```text
COPY_IN (binding allocation and input copy)
  -> NATIVE_MUTATION (bridge-local character call and copyback)
  -> COPY_OUT (binding Python replacement conversion)
  -> CLEANUP (binding call-local buffer release)
```

Validation requires the completed ownership/action facts, fixed result
position, one shared payload/length handoff, matching argument and native-slot
lengths/actions/copy reasons, exactly one complete lifecycle phase set, bridge
copyback ownership only for `COPY_IN_OUT`, and binding cleanup after conversion.
A replacement combined with native status-error projection stays blocked until
the status failure path also releases the mutable buffer. Multiple projected
results remain blocked by the existing single-writeback lane.

A fixed identity contract uses the already-completed `CALL_LOCAL_INPUT` action,
the same call-local bridge character representation, no lifecycle result, and
returns `None`. Native writes affect only that temporary and are deliberately
discarded. Its binding buffer remains the borrowed read-only UTF-8 input because
the bridge never copies mutation back across the boundary. Assumed-length,
optional, mutable `String[n][()]`, and raw-address forms remain excluded from
this first slice.

Replay both forms from the existing `fcharacter_edges_f90.fixed_inout` native
unit through a reduced edited contract that exports one projected replacement
and one identity spelling bound to the same native symbol. Run the same exact
length, trailing-blank, input-immutability, returned-value, and allocation
failure assertions through legacy and direct routes before widening the
whole-unit support predicate.

The second Phase 5C slice keeps the same completed ownership, barrier,
representation-copy, and four-phase lifecycle records while removing the
compile-time-length restriction. For required assumed-length `String`, the
binding-recorded UTF-8 byte length is the native character length and the
replacement allocation size. A zero-byte input is valid: replacement owns a
one-byte NUL-only buffer, the bridge materializes a zero-length character
value, and binding returns the empty Python string after releasing the buffer.
Fixed strings still require the exact declared encoded length.

Optional string values use the completed `OptionalMode.NULLABLE_VALUE`; they
do not invent a descriptor or reinterpret optionality as semantic nullability.
The binding ABI always carries the string payload pointer and runtime byte
length. Omitted and explicit `None` both send a null pointer with length zero,
so the bridge leaves the native optional dummy absent and a projected
replacement returns `None`. A concrete value is validated before native
execution, including embedded-NUL rejection and any fixed-length constraint.
Projected replacement allocates and owns the mutable `length + 1` buffer only
for that concrete value; identity form borrows the read-only payload and
discards native mutation exactly as the required identity path does.

The bridge tests pointer association to choose the existing optional native
call branch. Only the present branch associates the payload, creates
`character(kind=c_char, len=runtime_length)` call-local storage, and invokes
the native optional dummy. Copyback is likewise guarded by pointer association,
so an absent optional never touches unassociated storage. Concrete projected
replacement restores the NUL terminator after copying all runtime-length
bytes. Binding then returns the concrete replacement and frees its allocation
exactly once, or returns `None` without calling `free` for the absent states.
Status-error combination and multiple projected replacements remain blocked
by the same explicit cleanup exclusions as the fixed required slice.

Replay `assumed_inout` and `optional_inout` from the existing
`fcharacter_edges_f90` contract through a reduced entry module. Compare legacy
and direct routes for empty and non-empty assumed-length values, omitted,
explicit-`None`, and concrete optional states, input immutability, embedded-NUL
rejection before native execution, and allocator failure only for concrete
projected replacements.

- [x] Complete fixed required replacement and discarded-identity policy,
  writeback lifecycle, named lowering, cleanup, validation, parity, support
  widening, and ledger updates.
- [x] Add assumed-length replacement and optional presence only after the fixed
  required path is proven; preserve legacy empty-string and omitted/`None`
  behavior and reject embedded NUL before native execution.

### Phase 5D — Mutable Storage And Raw Fixed-Length Addresses

Included: `String[n][()]` caller-owned rank-zero NumPy bytes storage and
`Addr(String[n])` caller-supplied integer addresses. The storage path validates
rank zero, dtype `S<n>`, native byte order/alignment where applicable, and
writability before aliasing the caller buffer. The raw-address path does not
own or validate the pointee. Both use the declared fixed length; mutable
deferred-length scalar storage remains blocked.

Both forms complete policy before planning and share no Phase 5C replacement
lifecycle. `String[n][()]` records `ObjectKind.STRING`, caller ownership,
`IN_PLACE`, caller destruction, alias contract/boundary storage,
`PythonBarrierAction.STRING_STORAGE`,
`NativeBarrierAction.PASS_STORAGE_ADDRESS`, `CodegenAction.IN_PLACE_ARGUMENT`,
native mutation, no result projection, and a fixed positive character length.
`Addr(String[n])` records the same caller ownership, in-place transfer, caller
destruction, mutation, and no result projection, but the contract value itself
uses stack storage while `PythonBarrierAction.RAW_ADDRESS` and
`NativeBarrierAction.PASS_RAW_ADDRESS` preserve the unsafe caller-supplied
address. The raw pointee is never adopted, released, sized, or validated by
x2py. This corrects the pre-5D raw-string decision that incorrectly retained
immutable-string call-local ownership despite the completed raw-address
barriers.

The ordinary argument plan carries the fixed length and uses
`ArgumentHandoffMode.OPAQUE_ADDRESS` for both forms. There is one pointer ABI
field and no runtime length field: the fixed character length comes only from
the completed plan. The binding storage handler accepts exactly a rank-zero
NumPy `NPY_STRING` array whose itemsize is `n`, requires alignment and
writability, and forwards `PyArray_DATA` without allocating or copying.
The raw handler accepts an integer and uses the existing `PyLong_AsVoidPtr`
path; it deliberately does not inspect the pointee, its allocation extent, or
its lifetime.

The native character scalar is not directly C interoperable, so both forms
record `BridgeDataAction.COPY_REPRESENTATION` with a boundary-specific reason.
The bridge associates the incoming address with exactly `n`
`character(kind=c_char)` bytes, copies them into backend-local
`character(kind=c_char, len=n)` storage, invokes the native dummy, and copies
all `n` post-call bytes back. It does not append NUL, allocate, free, infer
ownership, or create a Python result. These helper locals are emitted-code
details selected by the completed storage/raw policy.

Optional storage/address arguments and projected returns remain blocked in
this phase. `String[()]` and `Addr(String)` are rejected by the semantic `.pyi`
contract because the bridge has no fixed extent; arrays and callback storage
remain owned by their later lanes. Validation rejects edited plans with a
missing/nonpositive length, the wrong owner/transfer/destruction/storage mode,
an inconsistent barrier or handoff, a runtime length role, an unjustified copy
reason, missing mutation, or result projection before either backend lowers.

Replay `fixed_inout_storage` and `fixed_inout_raw` from the existing
`fnative_call_examples_f90` edited contract through a reduced entry bound to
the same `fixed_inout` native routine. Compare legacy and direct routes for
complete eight-byte mutation, rank/dtype/itemsize/writability failures, raw
integer type rejection, and lack of Python return. Keep the existing mixed
native-order test on the legacy route because its array and derived-type
neighbors belong to later phases; add the reduced replay as a separate
wrapper-plan ledger node.

- [x] Complete mutable string-storage and raw-address policy, address handoff,
  bridge association/copyback mechanics, validation, legacy/direct parity,
  support widening, and ledger updates.

### Phase 5 Completion

Descriptor-backed scalar character values are deliberately outside this
phase. A contract such as `String | None` with
`result=Allocatable(Return(...))` carries allocation state, runtime element
length, descriptor ownership, and native release responsibility. It must enter
the direct route only through Phase 7's shared allocatable/pointer descriptor
plan; it remains a rank-zero Python `str | None` result rather than a native
array handle. Phase 5 must not add a character-only descriptor ABI or cleanup
path.

- [x] Expand the phase under the mandatory expansion gate from the live
  policies, legacy binding/bridge implementation, public string contract, and
  focused wrapper tests.
- [x] Validate fixed/runtime length sources, payload/length role agreement,
  result ownership, writeback consumers, and cleanup responsibility before
  either backend emits source.
- [x] Keep string behavior in directly named string lowering methods while
  reusing the ordinary scalar planning records and lifecycle flow.
- [x] Finish Phase 5 only when all non-descriptor scalar string sub-lanes are
  proven and every affected matrix row is either `wrapper-plan` or blocked by
  a later array, descriptor, field, or callback lane recorded in the ledger.

## Phase 6 — Ordinary Arrays

Scope: NumPy data-buffer arrays that do not require native descriptor handles.

The ordinary-array lane borrows or copies NumPy data buffers; it never creates
or consumes a persistent native descriptor handle. `Allocatable[T[...]]`,
`Pointer[T[...]]`, rank-zero allocatable/pointer scalars, and a native handle
used as the actual value for an ordinary array dummy all remain in Phase 7.
Caller-supplied `Addr(T[...])` storage is the distinct Phase 6G follow-up and
must complete before Phase 7.
Derived-type arrays remain in Phase 8, fields in Phases 8 and 9, and callback
arrays in Phase 10. The full BLAS/LAPACK generation unit remains deferred until
final cutover even when individual ordinary-array shapes become supported.

Whole-generation-unit rollout preserves that Phase 7 boundary. Output-only
ordinary array results and hidden outputs may select the production plan route
now. A generation unit with an ordinary array actual remains on the legacy
route, even after its NumPy-buffer path has direct-route parity, because route
selection cannot know whether a caller will pass a NumPy array or a supported
native descriptor handle. Those reduced array-actual rows remain `dual-route`
with the native-handle caller contract recorded as their sole Phase 7 blocker;
the direct route is forced only by the internal parity harness.

The public behavior is defined by the NumPy array contract in
`docs/user/guide/fortran-wrapper.md`, the array spelling and metadata rules in
`docs/user/reference/semantic-pyi-format.md`, and the existing array wrapper
tests. The legacy binding validates exact dtype, rank, every expressible
extent, native byte order, alignment, layout/stride requirements, and
writeability for mutable storage before the native call. It does not cast,
byte-swap, repair alignment, de-alias overlapping storage, or silently copy a
rejected layout. Read-only source `intent(in)` storage may remain read-only;
edited `.pyi` array storage is writable unless a completed policy says
otherwise. Zero-sized dimensions are valid when the rest of the contract is
valid.

Every ordinary array remains in the existing
`ArgumentPolicy -> ArgumentTransferPlan -> NativeCallSlotPlan` or
`ResultPolicy -> ResultPlan` flow. An argument embeds one editable array
handoff spec containing element family, concrete or runtime rank, declared
shape expressions, axis modes, order, contiguity, itemsize when relevant,
writeability, and the exact ABI roles for data, extents, upper bounds, strides,
runtime rank, or itemsize. Policy completion selects
`PythonBarrierAction.ARRAY_STORAGE`,
`NativeBarrierAction.PASS_ARRAY_BUFFER`, and either
`BridgeDataAction.ASSOCIATE_VIEW` for caller storage or an explicit copy action
and reason. Planning must not reconstruct any of those choices from rank,
shape spelling, or datatype. The binding and bridge dispatch only to directly
named array implementation methods selected by those completed facts.

The binding checks the NumPy object before extracting `PyArray_DATA`, shape,
and element strides. The bridge receives only the fields named by the handoff
spec, associates the pointer with the completed element type and extents, and
constructs a stride slice only when the plan explicitly allows it. C-oriented
flat storage reverses bridge association extents only when the completed order
requires it. Backend-local pointer views and slice expressions are emitted-code
details; dtype, rank, extent, order, stride acceptance, mutation, projection,
copy, and ownership are semantic policy.

The phase is dependency-ordered as follows.

### Phase 6A — Required Rank-One Contiguous Buffers

Included: required concrete-rank-one ordinary arrays with dense contiguous
axes (`T[:]`) for the existing bool, integer, real, and complex primitive
families; caller-owned borrowed/in-place storage; scalar or void neighbors and
results already supported by earlier phases; native position reordering; and
zero-length buffers. The binding requires an exact NumPy dtype, rank one,
native byte order, alignment, contiguity, and writeability only when completed
ownership says native code mutates the storage. It forwards the data address
and runtime extent. The bridge creates one typed rank-one pointer view with
`c_f_pointer` and passes that view in the completed native-call position.

This slice records `ArgumentHandoffMode.ARRAY_BUFFER` and
`BridgeDataAction.ASSOCIATE_VIEW`; it performs no allocation, element copy,
writeback action, release, or Python result projection. Explicit/fixed extent
expressions, `Flat`, multidimensional order, strided axes, optionality,
projected output identity, array results, character arrays, assumed rank, and
native-handle actuals remain in later sub-lanes. Replay one existing
`fmath_arrays_f90` contiguous routine through a reduced semantic `.pyi` entry
and compare legacy/direct behavior for mutation, dtype, rank, alignment,
byte-order, contiguity, writeability, zero length, and native argument order.

- [x] Complete required rank-one contiguous array policy, editable handoff
  spec, validation, named C/Fortran lowering, reduced legacy/direct parity,
  support widening, and ledger evidence.

### Phase 6B — Declared Extents, Flat Storage, And Dense Rank

Included: fixed and visible-symbol extent expressions, lower-bound-derived
extents, assumed-size `Flat`, ranks two through fifteen, `ORDER_F` and
`ORDER_C`, dense contiguous layout, and zero-sized axes. Shape expressions are
resolved against existing scalar handoff roles before backend emission; the
bridge association order follows the completed layout. Any expression that
cannot be represented by available roles remains blocked rather than being
recomputed in a backend.

Order is an exact-storage selector, not an implicit conversion selector.
`ORDER_F` preserves logical axes over Fortran-contiguous storage. `ORDER_C`
passes the original C-contiguous address and reverses bridge extents, so native
Fortran observes the transposed storage view. Preserving the same logical axes
while accepting the opposite layout uses explicit `COPY_F` metadata, never an
inference from order. The owning `ArgumentTransferPlan` records C source order,
F native order, copy-in, conditional copy-out, original-object projection, and
temporary cleanup. The binding performs both copy directions and owns the
NumPy temporary. The bridge receives the temporary through the unchanged
ORDER_F association path and performs neither half of this representation
conversion.

The initial `COPY_F` lane includes required, concrete-rank, dense numeric
ndarray arguments. It excludes `Flat`, assumed-rank, strided, optional and
character arrays, native descriptor arguments, and handle actuals until each
has separate policy and parity evidence.

`Flat` is one axis marker and never collapses a multidimensional plan:
`T[:, Flat]` remains rank two in Fortran order, while
`Annotated[T[Flat, :], ORDER_C]` is its C-order orientation. The bridge reverses
only the C-order association extents. For an external assumed-size interface,
an explicit prefix such as `T[3, Flat]` may lower to `a(3, *)`; a runtime-only
prefix uses the standards-valid sequence-associated `a(*)` declaration while
the bridge retains every runtime extent and the completed logical rank.

- [x] Complete declared-shape evaluation, flat-storage orientation,
  multidimensional dense handoff, validation, parity, and ledger evidence.
- [x] Complete explicit C-to-Fortran representation copies through `COPY_F`,
  including native-input and inout calls through the same binding-owned copy
  lifecycle, projected original identity, temporary cleanup, direct bridge
  reuse, validation, and compiled parity. Native `intent` remains owned by the
  called procedure and is not duplicated in the semantic `.pyi` or bridge
  temporary.

### Phase 6C — Positive-Strided Ordinary Views

Included: `::` axes and bounded stride-aware axes, runtime upper bounds and
element strides, Fortran-oriented positive-stride slicing, contiguous views as
a valid special case, and degenerate zero-size strides. Negative, zero on an
addressable axis, incompatible C-oriented, broadcast, and otherwise invalid
layouts fail before the native call. No copy-to-contiguous fallback is inferred.

- [x] Complete stride roles, upper bounds, positive-stride bridge slices,
  layout validation, parity, and ledger evidence.

### Phase 6D — Output Storage And Projected Identity

Included: ordinary `intent(out)`/`intent(inout)` caller buffers and
`Returns["name", T[...]]` projections. Native code mutates the same validated
NumPy storage; the binding returns the original Python array object with one
owned reference rather than constructing a second array or copying elements.
Read-only output storage fails before the call. Multiple projections compose
with the existing ordered result aggregation only after every projected array
identity and failure-path reference is planned.

- [x] Complete in-place output ownership, projected identity/reference
  lifecycle, multiple-result aggregation, parity, and ledger evidence.

### Phase 6E — Ordinary Array Results And Hidden Outputs

Included: non-allocatable direct array results and hidden output arrays whose
shape and element ownership are fully expressible without persistent native
descriptors. The plan records the producer, every runtime extent, allocation
owner, copy or transfer action, Python NumPy construction, and release on
success and every failure path. Nullable allocatable/pointer results remain in
Phase 7.

- [x] Complete ordinary result/hidden-output allocation, shape projection,
  copy ownership, cleanup, parity, and ledger evidence.

### Phase 6F — Optional, Assumed-Rank, And Character Buffers

Included: ordinary optional NumPy arrays, numeric assumed-rank dispatch from
one through fifteen, and fixed-width NumPy bytes character arrays with planned
itemsize. Omitted ordinary optional arrays remain distinct from present
storage. Assumed-rank plans carry a runtime-rank role and validate the supported
range before bridge dispatch. Character arrays use exact `NPY_STRING` itemsize
and remain raw fixed-width bytes; deferred descriptor-backed character values
remain in Phase 7. Fixed-shape character array direct results and hidden
outputs reuse the Phase 6E copy-result path with their itemsize included in
NumPy dtype construction and bridge byte-count calculation.

- [x] Complete optional presence, assumed-rank dispatch, character itemsize,
  validation, parity, and ledger evidence.

### Phase 6A-F Ordinary-Buffer Completion

- [x] Expand the phase under the mandatory expansion gate from live semantic
  array contracts, legacy binding/bridge lowering, public docs, and focused
  wrapper tests.
- [x] Define array handoff specs for every supported data, rank, shape, stride,
  order, itemsize, writeability, result, and lifecycle role.
- [x] Validate every completed array policy and handoff role before either
  backend emits source.
- [x] Finish Phases 6A-F only when every ordinary-array buffer matrix row is
  migrated or remains blocked solely by an explicitly later descriptor,
  derived, field, callback, or deferred-real-library lane.

### Phase 6G — Raw Array Addresses — Complete

Implementation status: complete. Required raw array addresses now use the
shared completed policy, `ArgumentTransferPlan`, native slot, centralized
validation, and named binding/bridge lowering paths. The dependency-closed
numeric and fixed-character runtime rows have passed compiled legacy/direct
parity and moved to `wrapper-plan`.

Scope: required Python-visible type-level raw-address array arguments such as
`Addr(Float64[n])`. The caller supplies one Python integer address, x2py
forwards it as one opaque C address, and the bridge associates a typed native
array view using rank, shape, element type, and orientation facts completed
before `ir2ast.py`. There is no NumPy object, runtime handle, persistent native
descriptor, data copy, ownership transfer, or automatic release.

This lane follows Phase 6 because its semantic object kind is
`ObjectKind.NUMPY_ARRAY` and its pointee layout reuses the array shape record.
It remains a distinct transport from an ordinary array buffer. The fixed
dispatch algorithm is:

1. match `ObjectKind.NUMPY_ARRAY`;
2. match the completed Python barrier action;
3. lower `ARRAY_STORAGE` through the Phase 6A-F buffer path or `RAW_ADDRESS`
   through Phase 6G;
4. require the matching native action, handoff mode, bridge data action, and
   array-shape facts; and
5. fail validation rather than substituting the other transport.

The same algorithm already separates scalar and string value, storage, and
raw-address forms. Phase 6G must extend that system; it must not add a parallel
raw-pointer planner, a datatype-based backend branch, or a special function or
module plan.

#### Public Contract And Explicit Non-Scope

The maintained public contract is already documented in
`docs/user/reference/semantic-pyi-format.md` and
`docs/user/guide/data-types.md`. Preserve it exactly:

- `Addr(T[d1, ..., dr])` is depth one and has positive rank;
- the pointee dtype is primitive;
- every extent expression is resolved from literals and visible scalar
  arguments or visible rank-zero scalar storage;
- the integer carries no dtype, rank, shape, order, alignment, bounds,
  ownership, or lifetime metadata;
- x2py cannot prove that the supplied address actually points to compatible,
  sufficiently large, live storage; and
- edited semantic `.pyi` raw-address storage is mutable caller storage unless
  a completed policy explicitly says otherwise.

The initial compiled oracle is `Addr(Float64[n])`. Before declaring the lane
complete, audit every public primitive family already accepted by semantic
policy, including bool, integer, real, complex, and fixed-width character
array pointees. Add compiled coverage for a family only when an existing native
routine can prove it without broadening the public contract. A fixed scalar
`Addr(String[n])` remains the completed Phase 5D string path; a rank-positive
`Addr(String[k][n, ...])` is an array path and must carry both the fixed element
length and the resolved array shape.

Explicitly excluded from this lane are:

- scalar `Addr(T)`, already completed in Phase 2E;
- fixed scalar `Addr(String[n])`, already completed in Phase 5D;
- NumPy `T[...]` storage, already completed in Phases 6A-F;
- unresolved or assumed shapes such as `Addr(Float64[:])`, assumed rank,
  assumed size, and stride-marker shapes;
- optional, nullable, projected, direct-result, and hidden-output raw addresses
  unless a separate public-contract audit first proves their intended Python
  ownership and absence/result behavior;
- wrapped/derived pointees, pointer graphs deeper than one, and callbacks;
- `Allocatable[T[...]]`, `Pointer[T[...]]`, runtime native handles, and C
  descriptors, which belong to Phase 7; and
- any implicit conversion from an ndarray or runtime handle to its address.

#### One Action Vocabulary, Three Array Transports

| Contract | Object kind | Python action | Native action | Handoff mode | Bridge data action |
| --- | --- | --- | --- | --- | --- |
| NumPy `T[...]` | `NUMPY_ARRAY` | `ARRAY_STORAGE` | `PASS_ARRAY_BUFFER` | `ARRAY_BUFFER` | `ASSOCIATE_VIEW` |
| Raw `Addr(T[...])` | `NUMPY_ARRAY` | `RAW_ADDRESS` | `PASS_RAW_ADDRESS` | `OPAQUE_ADDRESS` | `ASSOCIATE_VIEW` |
| Native descriptor contract | completed handle kind | completed handle action | `PASS_NATIVE_DESCRIPTOR` | Phase 7 descriptor mode | completed Phase 7 action |

`ASSOCIATE_VIEW` means the bridge creates a typed, non-owning view; it does not
mean that the Python binding extracted a NumPy buffer. The Python and native
barrier actions remain the authoritative distinction. Do not introduce names
such as `PASS_RAW_ARRAY`, `COPY_RAW_ARRAY`, or datatype-specific address
actions.

The completed ownership/action tuple for the required mutable public form is:

- `OwnershipOwner.CALLER`;
- `TransferMode.IN_PLACE`;
- `DestructionPolicy.CALLER`;
- `StorageMode.STACK` for the call-local pointer carrier, not for the pointee;
- `CodegenAction.IN_PLACE_ARGUMENT`;
- `PythonBarrierAction.RAW_ADDRESS`;
- `NativeBarrierAction.PASS_RAW_ADDRESS`;
- `ArgumentHandoffMode.OPAQUE_ADDRESS`; and
- `BridgeDataAction.ASSOCIATE_VIEW` with no copy reason.

If a retained source-derived contract can be read-only, policy may instead
complete `CALL_LOCAL` / `CALL_LOCAL_INPUT` / `NONE` destruction. Both
backends must consume that completed tuple; neither may infer mutability from
the pointee type or raw-address spelling. A raw array never has copy-in,
copy-out, projected-identity, allocation, destruction, release, or lifecycle
actions in this lane.

#### Required Policy And Plan Shape

Keep the feature under the existing `ArgumentTransferPlan`:

```text
ArgumentTransferPlan
  object_kind = NUMPY_ARRAY
  binding.python_action = RAW_ADDRESS
  bridge.native_action = PASS_RAW_ADDRESS
  bridge.handoff_mode = OPAQUE_ADDRESS
  bridge.data_action = ASSOCIATE_VIEW
  array = ArrayHandoffPlan
  native_call_slot = the same referenced NativeCallSlotPlan
```

Do not add `RawArrayPlan`, a second native slot, or a raw-address lifecycle
owner. Generalize the existing completed `ArrayHandoffPolicy` and
`ArrayHandoffPlan` only enough to carry raw pointee layout:

- concrete rank and one shape expression per axis;
- one `data_role` equal to the binding/bridge/native-slot address role;
- `extent_reference_roles` naming the existing visible scalar handoff roles
  used by each shape expression;
- the completed orientation used for native pointer association;
- fixed character element length/itemsize when the pointee family is string;
  and
- no binding-extracted runtime rank, extent, upper-bound, stride, or itemsize
  ABI roles.

For a raw address, the shape record describes the pointee view; it does not
describe fields packed by the binding. A visible `n` used by
`Addr(Float64[n])` already has its own `ArgumentTransferPlan` and native-call
slot. Reference that role rather than passing a duplicate array extent. A
literal extent requires no extra ABI field. The bridge resolves the shape
expression from those planned native role names.

Post-IR policy completion must explicitly select multidimensional orientation
before planning. Preserve the current legacy interpretation, including its
default orientation, only after capturing a rank-two artifact/runtime oracle.
Do not leave `ir2ast.py`, a codegen-model `order` default, or the bridge's local
shape reversal to make that decision.

#### Completed Direct-Plan Seams

The implementation split completed array policy by Python barrier action,
selected `OPAQUE_ADDRESS` and `ASSOCIATE_VIEW` before lowering, projected raw
pointee layout into the shared array record, omitted packed NumPy-buffer roles,
and added named raw-address checks and association methods to both backends.
Ordinary-array buffer checks remain unchanged and fail closed; neither backend
substitutes one transport for another.

#### Dependency-Ordered Implementation Slices

##### Phase 6G1 — Complete Raw Array Policy

- [x] Make the `NUMPY_ARRAY` boundary validator dispatch on
  `PythonBarrierAction` and add a named raw-address branch with the exact
  ownership/action tuple above.
- [x] Complete raw pointee rank, shape expressions and their visible-scalar
  dependencies, primitive family, fixed character element length, and
  orientation before `ir2ast.py`.
- [x] Complete `OPAQUE_ADDRESS` and `ASSOCIATE_VIEW` from the action pair; do
  not infer either in a backend.
- [x] Keep unresolved dimensions, unsupported pointee families, optionality,
  projection, nullability, and deeper pointer graphs blocked with owner-path
  diagnostics.
- [x] Freeze current behavior for zero/negative extent expressions, zero or
  negative integer addresses, and integer overflow against the public docs and
  legacy conversion before changing any rule. If a rule changes, change it in
  policy and public docs, not in one backend.

Audit result: resolved zero and negative extent expressions remain accepted
without a positivity check; integer zero becomes a null pointer without a
conversion error; negative integers follow `PyLong_AsVoidPtr`; and pointer-size
overflow raises `OverflowError`. Public documentation now states that these are
unsafe caller responsibilities, and tests prove the conversion guard and
generated shape without dereferencing an invalid address.

##### Phase 6G2 — Project And Validate The Shared Plan

- [x] Populate the existing `ArgumentTransferPlan.array` and its shared
  `NativeCallSlotPlan.array` with one identical raw pointee layout record.
- [x] Reuse the scalar/string address handoff role and
  `ArgumentHandoffMode.OPAQUE_ADDRESS`; add no raw-array ABI action.
- [x] Resolve every shape symbol to an existing visible scalar role and reject
  unavailable, cyclic, hidden, non-scalar, or result-only dependencies before
  lowering.
- [x] Split central array diagnostics by the completed Python action so buffer
  validation still requires packed extent/layout roles while raw validation
  forbids them.
- [x] Add editable-plan tests that independently corrupt object kind, Python
  action, native action, handoff mode, bridge data action, rank, shape,
  reference roles, element family, character length, orientation, and native
  slot identity.

##### Phase 6G3 — Reuse Binding Raw-Address Extraction

- [x] Reuse `_lower_argument_required_raw_address()` for the Python integer
  check and `PyLong_AsVoidPtr` conversion. Scalar, string, and array raw
  addresses should share this extraction code.
- [x] Emit one `void *` handoff value and no `PyArray_*`, dtype, rank, shape,
  layout, writeability, or itemsize checks.
- [x] Keep object-kind-specific logic out of the conversion method; array
  shape affects only validation, the bridge view, and native call.
- [x] Preserve the existing conversion rule under which integer zero produces
  a null pointer without itself raising a Python conversion error. Prove that
  rule without dereferencing the null pointer; runtime tests must never call
  native code with an invalid test address.

##### Phase 6G4 — Add Named Raw Array Bridge Association

- [x] Add directly named raw-array declaration and association methods in the
  array method group. Dispatch to them only for
  `NUMPY_ARRAY` / `RAW_ADDRESS` / `PASS_RAW_ADDRESS` /
  `OPAQUE_ADDRESS` / `ASSOCIATE_VIEW`.
- [x] Declare one `type(c_ptr), value` bridge parameter and one backend-local
  typed pointer view. The local view is an emitted-code helper, not a new plan
  owner.
- [x] Associate the view with `c_f_pointer` using only the planned shape and
  orientation, then pass that view in the existing native-call slot position.
- [x] Preserve fixed character element length when the pointee is a character
  array. Do not pass a runtime itemsize unless a future public contract
  explicitly requires one.
- [x] Emit no copy, writeback, allocation, release, descriptor, or NumPy
  mechanics.

##### Phase 6G5 — Prove The Route Before Widening It

- [x] Retain semantic conversion coverage in
  `tests/semantics/conversion/pyi/test_calls_and_projections.py` for round-trip,
  visible extent sources, primitive pointees, and rejection of unresolved or
  wrapped forms.
- [x] Add focused completed-policy tests for every authoritative action and
  blocker, plus `array-raw-address-inputs` support classification.
- [x] Add `tests/wrapper_codegen/test_phase6g_raw_array_addresses.py` for plan
  shape, edits, validation, C nodes, Fortran nodes, native order, and the
  absence of buffer/descriptor/lifecycle nodes.
- [x] Extract `fill_vector_raw` from
  `test_editable_contract_can_use_native_order_arguments_without_native_call`
  into a reduced legacy/direct-plan parity test. Cover mutation through a valid
  `raw_vector.ctypes.data`, ndarray rejection, wrong Python types, a visible
  rank-zero scalar extent, and the established native argument order.
- [x] Prove raw-array native argument reordering in the direct-plan generated
  call test. The legacy AST route retains only a projection marker and is not
  an oracle for reordered projection-slot lowering.
- [x] Add literal and arithmetic extent-role cases. Add a rank-two runtime
  parity case before freezing default/explicit orientation. Add a fixed-width
  character-array case if the public family audit retains that contract.
- [x] Keep the broad native-order test `legacy` until its derived-type owner is
  migrated; only the reduced raw-array row may move to `wrapper-plan` here.
- [x] Run the focused policy/plan/backend tests, the relevant wrapper test,
  documentation checks, wrapper-codegen complexity checker, and required
  static-analysis suite before changing route support.

#### Phase 6G Exit Gate

- [x] Expand raw array addresses as the explicit next lane using the public
  contract, completed semantic policy, legacy binding/bridge primitives, and
  the existing compiled `Addr(Float64[n])` oracle.
- [x] Complete Phases 6G1 through 6G5 without changing the public raw-address
  contract or introducing a parallel action vocabulary.
- [x] Prove that one maintainer algorithm—object kind, Python action, native
  action, handoff mode, data action, then typed shape facts—covers ordinary and
  raw arrays without backend inference.
- [x] Move only dependency-closed raw-array test rows after generated-artifact
  comparison and compiled legacy/direct parity pass.
- [x] Begin Phase 7 only after this exit gate is complete. Phase 7 must consume
  the established distinction among array buffers, raw addresses, and native
  descriptors rather than revisiting it.

## Phase 7 — Native Array Handles And Descriptors

Implementation status: complete, pending the final verification gate recorded
at the end of this phase. Phase 6G completed first. The direct route now owns
the dependency-closed Phase 7A-H cases while every field, pointer-result,
callback, and deferred-real-library exclusion remains on its later blocker.

Scope: migrate the existing native descriptor and runtime-handle contract into
the wrapper-plan path without redefining that public contract. The maintained
`native-array-handle-checklist.md` remains the feature-level behavioral oracle;
this section owns only its migration into completed wrapper policy,
`ArgumentTransferPlan`, `ResultPlan`, `ModuleVariablePlan`, subordinate native
slots and lifecycle actions, direct C/Fortran lowering, and production route
selection.

The shared descriptor family includes:

- rank-positive `Allocatable[T[...]]` and `Pointer[T[...]]` handle arguments;
- optional-absent array handles, where omission or `None` means the native
  optional dummy is absent;
- projected writable descriptors whose mutation must remain attached to the
  same caller handle;
- wrapper-owned allocatable array results and hidden outputs;
- borrowed module allocatable and pointer handles plus their generated operation
  tables;
- native handles passed as actual values to ordinary `T[...]` dummies without
  an implicit `.to_numpy()` call;
- build requirements for standard C descriptors; and
- the remaining rank-zero allocatable/pointer result cases, including nullable
  deferred-length scalar character values, which return copied Python values
  rather than native-array handle objects.

Allocatable and Pointer remain separate public contract types but share one
plan and lowering structure. Descriptor kind selects only the operations that
genuinely differ: allocation state versus association state, allowed
shape-changing operations, target lifetime, extraction policy, and release.
Do not create independent allocatable and pointer planner hierarchies.

### Phase 7 Boundary And Explicit Non-Scope

The following four boundaries must remain distinct:

| Python contract | Planned Python input | Native transport | Owner phase |
| --- | --- | --- | --- |
| `T[...]` with a NumPy array | validated NumPy storage | `PASS_ARRAY_BUFFER` | Phase 6 |
| `T[...]` with an allocated/associated native handle actual | validated handle array-data facet | `PASS_ARRAY_BUFFER` | Phase 7A |
| `Allocatable[T[...]]` / `Pointer[T[...]]` | matching runtime handle object | `PASS_NATIVE_DESCRIPTOR` | Phase 7B onward |
| `Addr(T[n, ...])` | caller-supplied integer address | `PASS_RAW_ADDRESS` | Phase 6G prerequisite, not Phase 7 |

`Addr(Float64[n])` is a supported public semantic `.pyi` contract when
every extent is a literal or an expression over visible scalar arguments or
rank-zero scalar storage. It accepts an integer such as `array.ctypes.data` and
forwards that address without ownership, dtype, alignment, lifetime, or bounds
validation. Parsing, policy completion, printing, and both compiled wrapper
routes support it through the completed
`RAW_ADDRESS` / `PASS_RAW_ADDRESS` selector pair. Do not misclassify this raw
pointer as a NumPy buffer, native handle, or C descriptor while maintaining
Phase 7.

Other exclusions and dependencies are:

- ordinary NumPy-only buffer extraction, shape, stride, output identity, and
  copy-result behavior already completed in Phase 6;
- caller-supplied raw array addresses, completed separately by the Phase 6G
  entry dependency;
- derived-type field attachment, class construction, parent-wrapper creation,
  and property orchestration, which require Phases 8 and 9 even though the
  shared native-handle plan must already be reusable by those later owners;
- pointer results without completed stable owner storage and target lifetime;
- callback descriptor arguments or results, which remain in Phase 10;
- compiler-private descriptor layout inspection or copying;
- any implicit `.to_numpy()` conversion when a native handle is passed to an
  ordinary array dummy; and
- the deferred BLAS/LAPACK generation unit until final cutover.

### Existing Semantic Authority And Legacy Oracle

Do not redesign the public feature while migrating it. Reuse these completed
sources of truth:

- `x2py/semantics/native_array_handles.py` defines
  `NativeArrayHandlePolicy`, `ArrayInteropPolicy`, handle facts, descriptor
  kinds, and completed build requirements.
- `x2py/semantics/policy_completion.py` completes handle kind, origin, owner,
  owner retention, descriptor ownership, getter/setter behavior, output
  projection, release, target lifetime, destruction, extraction, interop,
  nullability, storage mode, operations, and blockers before `ir2ast.py`.
- `x2py/runtime/handles.py` owns the reusable runtime protocol, including
  `_native_array_actual_argument_for_binding_positional`,
  `_native_array_descriptor_argument_for_binding_positional`, and
  `_native_array_descriptor_handoff_for_binding_positional`. Direct lowering
  must call these helpers rather than duplicate their Python validation.
- `x2py/codegen/bindings/c_to_python.py` is the legacy binding oracle. Its
  `_ARRAY_INTEROP_POLICY_DISPATCHER`, `_NATIVE_ARRAY_HANDLE_DISPATCHER`,
  descriptor-argument handlers, owned-result handlers, operation wrappers, and
  descriptor reader define the currently passing C behavior.
- `x2py/codegen/bridges/fortran_to_c.py` is the legacy bridge oracle. Its
  corresponding dispatchers, descriptor-argument handlers, module/field
  operation generators, and owned-allocatable result helpers define the
  currently passing Fortran behavior.
- `x2py/pipeline/build.py` already derives native-array build requirements from
  completed semantic policy and records them in manifests. The wrapper plan
  must carry and emit the matching artifact requirements without rediscovering
  them from generated source text.

The legacy generators are behavioral oracles, not dependencies of
`x2py/wrapper_codegen`. Reuse the runtime helpers and completed semantic
records directly. Rewrite the smallest equivalent node/lowering methods in the
direct generators; do not import legacy binding/bridge generator methods or
legacy codegen-model nodes into the wrapper-plan package.

### Completed Direct-Plan Shape

Wrapper policy now carries the completed native-handle and array-actual facts.
`ArgumentTransferPlan`, `ResultPlan`, and `ModuleVariablePlan` distinguish a
NumPy data-buffer transfer, a normal array dummy receiving a handle actual, and
a descriptor-handle transfer. Central validation fails closed when any typed
handoff, operation, role, ownership fact, or required header is inconsistent;
neither backend infers policy from datatype or `descriptor_boundary`.

### Required Plan Shape

Keep all descriptor-specific state subordinate to the existing datatype-
varying owners:

```text
ArgumentTransferPlan
  array: ArrayHandoffPlan | None
  native_array_actual: NativeArrayActualPlan | None
  native_array_handle: NativeArrayHandlePlan | None
    handoff: NativeDescriptorHandoffPlan
  native_call_slot: NativeCallSlotPlan

ResultPlan
  native_array_handle: NativeArrayHandlePlan | None
  native_call_slot: NativeCallSlotPlan | None

ModuleVariablePlan
  native_array_handle: NativeArrayHandlePlan | None

FunctionPlan
  native_call_slots: shared ordered references
  lifecycle actions: ordered handle materialization/release references
```

`NativeCallSlotPlan` and `LifecycleActionPlan` are not competing top-level
semantic owners. A native slot is the argument/result ABI facet shared by its
owning transfer plan, while lifecycle records are function-wide ordering
indexes back to argument/result roles. Descriptor ownership, release, and
operation policy stay under `ArgumentTransferPlan`, `ResultPlan`, or
`ModuleVariablePlan`. Backend-local CFI storage, copy buffers, and failure
cleanup remain inside the named lowerer selected by those plans.

`NativeArrayActualPlan` is used only when an ordinary `T[...]` argument permits
a runtime native handle as another source for the existing array-buffer ABI. It
records the explicitly accepted Python source kinds and the shared dtype, rank,
shape, layout, writeability, native-byte-order, alignment, and ABI-role checks.
It never carries descriptor ownership or extraction policy.

`NativeArrayHandlePlan` is one editable projection of the completed handle
policy. It must contain, using typed values rather than free-form backend
method names:

- descriptor kind and handle kind;
- origin, owner, owner-retention mode, descriptor ownership, and borrowed state;
- element datatype family, dtype, rank, declared shape, order, and character
  element length when applicable;
- getter behavior, Python setter exposure, and native setter assignment;
- output projection and same-handle identity requirements;
- release responsibility, target lifetime, destroy behavior, and storage mode;
- `.to_numpy()` extraction action and allowed generated operations;
- descriptor-interop requirement and required headers;
- nullability and optional-absent-handle behavior; and
- one `NativeDescriptorHandoffPlan` with its ABI form and symbolic roles.

`NativeDescriptorHandoffPlan` must distinguish these typed ABI forms:

- `FACT_PACKED_CALL_LOCAL`: a non-projected descriptor argument supplies
  validated standard descriptor facts; the binding passes those fields and the
  bridge establishes call-local standard C descriptor storage.
- `DIRECT_STANDARD_DESCRIPTOR`: a projected writable handle passes its
  persistent standard-descriptor pointer so allocation, deallocation,
  reassociation, and shape changes remain attached to that handle.
- `OWNED_RESULT_STORAGE`: an allocatable result is materialized into persistent
  wrapper-owned CFI storage and later destroyed by the runtime handle.

The handoff records the descriptor-pointer role when present, `base_addr`,
`elem_len`, runtime rank, per-axis lower-bound/extent/stride-multiplier roles,
an optional presence role, owner-storage role, and generated-operation roles.
The `NativeCallSlotPlan` and its owning argument or hidden result must reference
the same mutable handoff record; do not duplicate descriptor facts that a
maintainer would need to edit twice.

Convert the current string-valued completed policy selectors into typed plan
enums or validate and translate them exactly once while building wrapper
policy. Backends must not match raw strings such as `argument_descriptor`,
`projected_handle`, or `pointer_c_descriptor` to choose behavior.

### Consistent Action Vocabulary

Reuse the existing orthogonal actions:

| Case | `ObjectKind` | Python action | Native action | `CodegenAction` | Bridge data action |
| --- | --- | --- | --- | --- | --- |
| Ordinary array with ndarray or handle actual | `NUMPY_ARRAY` | `ARRAY_STORAGE`, with explicitly planned accepted sources | `PASS_ARRAY_BUFFER` | existing Phase 6 input/in-place action | `ASSOCIATE_VIEW` |
| Read-only descriptor handle argument | `NUMPY_ARRAY` | `WRAPPER_INSTANCE` | `PASS_NATIVE_DESCRIPTOR` | `CALL_LOCAL_INPUT` | `ASSOCIATE_VIEW` |
| Writable projected descriptor handle | `NUMPY_ARRAY` | `WRAPPER_INSTANCE` | `PASS_NATIVE_DESCRIPTOR` | `IN_PLACE_ARGUMENT` | `DIRECT_TRANSFER` |
| Owned allocatable handle result | `NUMPY_ARRAY` | `NONE` | `NONE` or hidden `PASS_NATIVE_DESCRIPTOR` | `WRAPPER_INSTANCE` | `COPY_REPRESENTATION` with an ownership-transfer reason |
| Borrowed module handle getter | `NUMPY_ARRAY` | module getter action `NATIVE_ARRAY_HANDLE` | operation-specific | `BORROWED_VIEW` | completed per operation |

Using `WRAPPER_INSTANCE` for the Python handle is consistent with the existing
action axis: the binding validates and consumes a generated runtime wrapper
object, while `ObjectKind.NUMPY_ARRAY` still identifies its array semantic
family. Add a new Python action only if a proven backend operation cannot be
expressed by this existing pair. Add `ArgumentHandoffMode.NATIVE_DESCRIPTOR`
because descriptor tuples are a genuinely different binding-to-bridge ABI from
`ARRAY_BUFFER`; do not overload the Phase 6 mode.

Keep rank-zero descriptor values on the scalar or string object-kind route.
Their result action creates a Python scalar/string or `None`, not
`WRAPPER_INSTANCE`, and they must not carry `NativeArrayHandlePlan`.

### Cross-Backend Validation Invariants

Before either backend emits source, `_validate_plan()` must reject every one of
these inconsistencies:

- a descriptor plan whose completed `ObjectKind` is not `NUMPY_ARRAY`;
- `PASS_ARRAY_BUFFER` carrying descriptor ownership or CFI roles;
- `PASS_NATIVE_DESCRIPTOR` carrying ordinary data-buffer handoff roles without
  a descriptor handoff;
- a disagreement among handle policy, interop ABI, descriptor kind, handle
  kind, argument/result plan, and native-call slot;
- a required handle accepting `None`;
- an optional absent handle without a presence role, or a required handle with
  one;
- collapsing optional absence into present-unallocated/present-unassociated
  state: an absent handle has null fields and a null presence token, whereas a
  present handle may have null `base_addr` but must have a non-null presence
  token;
- fact-packed handoff for a projected writable descriptor, or direct persistent
  descriptor handoff for a policy that does not permit descriptor mutation;
- direct descriptor handoff without a typed
  `_NativeArrayDescriptorHandoff`-compatible runtime operation;
- descriptor dtype, rank, shape, element length, or per-axis field counts that
  disagree with the declared handle data facet;
- pointer reassociation, allocation, deallocation, or resize without completed
  `PointerPolicy` permission;
- a pointer result without stable owner storage and target lifetime;
- an owned result without wrapper ownership, heap/alias boundary storage,
  destroy behavior, owner retention, or a failure-path release action;
- a borrowed module/field handle that claims to destroy native owner storage;
- descriptor-view extraction without its completed C-descriptor build
  requirement;
- a C-descriptor header requirement on a generation unit whose completed plans
  do not need that interop; and
- any semantic helper temporary represented by a fabricated
  `OwnershipDecision`. Call-local CFI variables, decoded-dimension locals,
  pointer views, status locals, and operation tables are backend-local emitted
  storage inside the already selected method.

### Phase 7A — Ordinary Array Dummies Accepting Native Handle Actuals

Included: concrete-rank numeric `T[...]` arguments already supported by Phase 6
when the runtime value is either a valid ndarray, an allocated allocatable
handle, or an associated pointer handle. The handle path validates the same
dtype, rank, shape, layout, writeability, byte-order, and alignment contract,
then calls the handle's internal `array_actual` operation and packs the existing
Phase 6 pointer/extent/stride ABI. It never calls `.to_numpy()` and never passes
the allocatable/pointer descriptor to the ordinary native dummy.

Initially excluded: optional, assumed-rank, character, and unsupported
noncontiguous handle actuals. Audit each against live runtime-helper behavior
before widening this sub-lane; a rejected form must remain an explicit blocker,
not silently fall back to `.to_numpy()` or a raw address.

Those exclusions remain visible as the uncompleted
`array-handle-actuals-excluded` rollout lane. Their direct Phase 6 ndarray
lowerers remain testable with a forced wrapper-plan route, but automatic
production selection stays on the legacy route until each corresponding handle
source has parity evidence.

Legacy oracle: `CPythonBindingGenerator._native_array_actual_argument_body`,
the normal-array runtime helpers in `x2py/runtime/handles.py`, and the existing
Phase 6 bridge array-buffer lowering. Reuse the runtime helpers and bridge ABI;
rewrite only the minimal direct binding call and source-kind branch.

Plan and lowering requirements:

- [x] Add `NativeArrayActualPlan` or equivalent accepted-source facts beneath
  the existing ordinary `ArgumentTransferPlan`; keep
  `PASS_ARRAY_BUFFER`, `ArgumentHandoffMode.ARRAY_BUFFER`, and
  `ArrayHandoffPlan` unchanged.
- [x] Make the C binding's named ordinary-array input method call
  `_native_array_actual_argument_for_binding_positional` with only planned
  validation flags and ABI-field selections.
- [x] Keep the Fortran bridge on the exact Phase 6 array-buffer method; it must
  not know whether Python supplied an ndarray or a handle.
- [x] Validate that handle actuals are allocated/associated, have a non-null
  data address, and satisfy the same declared contract as ndarray inputs;
  preserve allocated/associated zero-length arrays.
- [x] Add the `array-native-handle-actuals` support lane and remove the current
  production gate on ordinary array actuals only after reduced compiled parity
  proves both runtime source kinds and all rejection paths.
- [x] Reuse the normal-array calls in
  `test_module_and_derived_pointer_handles_track_native_association` and
  allocatable handle fixtures as the legacy baseline, but extract a class-free,
  dependency-closed parity contract so Phase 8 does not determine this lane's
  route.

### Phase 7B — Required Read-Only Descriptor Handle Arguments

Included: required, non-projected `Allocatable[T[...]]` and
`Pointer[T[...]]` arguments. The Python binding accepts only the matching
runtime handle class. A present unallocated allocatable or unassociated pointer
is still a present descriptor argument and may carry a null `base_addr`.

The binding uses the existing descriptor runtime helper to obtain validated
standard descriptor facts. The bridge establishes rank-specific call-local CFI
storage from `base_addr`, `elem_len`, rank, and dimension records, then passes
the native allocatable or pointer dummy. This association is an emitted-code
view, not a semantic data copy.

Legacy oracle:

- binding `_bind_allocatable_descriptor_argument`,
  `_bind_pointer_descriptor_argument`, and
  `_bind_fact_packed_native_array_descriptor_argument`;
- bridge `_bridge_allocatable_descriptor_argument`,
  `_bridge_pointer_descriptor_argument`, and
  `_bridge_native_array_descriptor_argument`; and
- runtime `_native_array_descriptor_argument_for_binding_positional`.

- [x] Carry the completed `NativeArrayHandlePolicy` and descriptor
  `ArrayInteropPolicy` into `ArgumentPolicy`, `ArgumentTransferPlan`, and its
  shared native slot.
- [x] Add `ArgumentHandoffMode.NATIVE_DESCRIPTOR` and a
  `FACT_PACKED_CALL_LOCAL` descriptor handoff with exact symbolic roles.
- [x] Add directly named C and Fortran descriptor-input methods grouped under
  the native-array-handle family; backend-local tuple items and CFI locals may
  be created only inside those selected methods.
- [x] Validate matching handle class, descriptor kind, dtype, rank, declared
  shape, and element length before the call. Reject ndarray inputs.
- [x] Add separate `allocatable-descriptor-inputs` and
  `pointer-descriptor-inputs` support lanes after reduced descriptor-argument
  parity passes.
- [x] Replay the descriptor calls in
  `test_pointer_descriptor_views_preserve_slice_shape_strides_and_parent_lifetime`
  and the allocatable descriptor fixtures through minimal class-free contracts;
  retain the mixed original nodes as legacy until all their later owners migrate.

### Phase 7C — Optional Absent Descriptor Handles

Included: `Allocatable[T[...]] | None = ...` and
`Pointer[T[...]] | None = ...` callable arguments. Omission and explicit
`None` both mean native `present(...)` is false. A present handle remains
present even when its descriptor has absent allocation/association state.

This is a two-level handle-presence contract, not the Phase 3 scalar descriptor
three-state value contract. Do not reuse the value pointer as the presence
token. The runtime helper already produces null fact fields plus null presence
for absence, and a distinct non-null token for every present handle.

- [x] Project `optional_absent`, `nullable`, presence mode, and the dedicated
  presence role from completed handle policy without inspecting the Python
  object in planning or bridge code.
- [x] Generate both required and optional fact-packed descriptor calls through
  the Phase 7B methods, adding only the planned presence ABI field and native
  branch.
- [x] Validate required-versus-optional annotation, field count, presence role,
  and the distinction between absent handle and present null `base_addr`.
- [x] Add `optional-native-array-handles` route coverage only after compiled
  tests exercise omission, explicit `None`, present allocated/associated,
  present unallocated/unassociated, wrong handle kind, and wrong dtype/rank.
- [x] Treat the lack of one isolated compiled optional array-handle fixture as
  a coverage gap: create a reduced semantic `.pyi` entry over an existing
  native optional descriptor routine instead of inventing behavior from the
  runtime-only tests.

### Phase 7D — Writable And Projected Descriptor Handles

Included: descriptor arguments whose allocation, deallocation, resize,
reassociation, or nullification must remain visible through the same Python
handle, plus a matching projected result that returns that identical handle.
Allocatable mutation follows completed ownership. Writable pointer descriptor
mutation requires explicit `PointerPolicy` permissions and target-lifetime
facts.

Fact-packed call-local descriptors are forbidden here because native mutation
would be discarded at return. The binding must request the handle's typed
persistent standard-descriptor pointer and the bridge must pass it directly.
Returning the projection increments/transfers the existing Python reference; it
does not construct a replacement handle or call `.to_numpy()`.

The direct handoff requires generated persistent standard-descriptor storage.
Wrapper-owned result handles provide it. Borrowed module handles expose current
descriptor facts for read-only calls, but they are not accepted for projected
writable mutation because a reconstructed call-local descriptor would lose the
native descriptor update.

Legacy oracle:

- binding `_bind_direct_native_array_descriptor_argument` and
  `_bind_projected_native_array_handle_result`;
- bridge descriptor argument dispatch with completed output projection; and
- runtime `_native_array_descriptor_handoff_for_binding_positional`.

- [x] Add `DIRECT_STANDARD_DESCRIPTOR` handoff and same-handle result identity
  to the owning `ArgumentTransferPlan`, shared native slot, `ResultPlan` or
  lifecycle consumer, and function-wide result order.
- [x] Reuse `CodegenAction.IN_PLACE_ARGUMENT` and `DIRECT_TRANSFER`; do not add
  a descriptor-copy action for same-handle mutation.
- [x] Plan success and failure reference handling so a projected handle is
  returned exactly once and borrowed caller storage is never destroyed.
- [x] Validate operation permissions, descriptor ownership, target lifetime,
  direct handoff type, result identity, and optional presence before emission.
- [x] Add `projected-native-array-handles` support only after
  `test_allocatable_inout_arrays_mutate_and_return_the_same_handle` has a
  reduced legacy/direct-plan parity replay covering allocation, reallocation,
  deallocation, identity, wrong input types, and native-memory checks.
- [x] Keep writable pointer reassociation blocked unless the completed policy
  proves every required permission and lifetime fact; never downgrade it to a
  read-only fact-packed call.

### Phase 7E — Owned Allocatable Results And Hidden Outputs

Included: rank-positive allocatable direct function results and hidden output
descriptors whose completed policy selects `owned_result_descriptor`. A valid
allocatable function result is allocated when returned; an unallocated
nonpointer function result is a nonconforming native procedure and the wrapper
does not compensate for it. An allocatable output dummy may validly remain
unallocated and still returns a present `AllocatableArray` handle whose state
lives inside that handle. Pointer handle results remain blocked until stable
owner storage and target lifetime are explicit.

For a numeric direct allocatable function result, the bridge assigns the native
function expression once into a procedure-local allocatable and then uses
`move_alloc` to transfer that allocation into the allocatable `intent(out)`
dummy backed by persistent wrapper-owned `CFI_CDESC_T(rank)` storage. The move
does not copy the array payload. Do not insert a collector helper, an
`allocated(...)` guard, or a second intrinsic assignment. The native function
must return an allocated, defined result; an unallocated result is a
nonconforming native procedure and remains the user's responsibility rather
than a wrapper fallback. Other procedure-local storage remains permitted only
when representation conversion genuinely requires it, such as
deferred-character byte materialization. The binding constructs the complete
generated operation table and Python handle only after owner storage is valid.
Ownership transfers to the handle exactly once; every earlier failure path
releases the persistent allocation and any genuinely required bridge-local
allocation.

Character-element handles carry runtime `elem_len` and declared element-length
policy in the same descriptor record. Because a deferred character width is
unknown until the native result exists, the bridge first copies the bytes and
the binding then establishes and allocates persistent CFI storage with that
runtime width. This is a named lowering method under the same result handle
plan, not a separate string-result ownership hierarchy.

Legacy oracle:

- binding `_bind_owned_allocatable_result_handle`, owned-result operation
  builders, `_bind_materialized_native_array_handle_result`, and destroy body;
- bridge `_bridge_owned_allocatable_result_handle` plus allocatable result
  helper/copy logic; and
- the runtime handle factory and exactly-once `close()`/finalizer protocol.

- [x] Attach one `NativeArrayHandlePlan` with `OWNED_RESULT_STORAGE` to direct
  and hidden `ResultPlan` owners; hidden outputs share their exact descriptor
  native slot.
- [x] Use `CodegenAction.WRAPPER_INSTANCE` and an explained
  `COPY_REPRESENTATION` only for materialization into persistent owner storage;
  source hiddenness remains `source_kind`, not a codegen action.
- [x] Record owner storage, materialization, handle construction, ownership
  transfer, destroy behavior, and release responsibility under the result's
  typed handle plan. Keep backend-local CFI allocation/copy/free nodes inside
  the selected result lowerer rather than fabricating lifecycle policy records.
- [x] Require generated `shape`, `array_actual`, `descriptor`, extraction/state,
  allowed mutation, and `destroy` operations before publishing the handle.
- [x] Validate CFI rank, dtype, element length, allocated state, owner
  retention, release responsibility, destroy behavior, and all success/failure
  paths before emission.
- [x] Add `owned-allocatable-results` and
  `owned-allocatable-hidden-outputs` support lanes after reduced parity from
  `test_array_results_follow_data_buffer_and_descriptor_handle_contracts`,
  `test_output_arguments_and_multiple_results_follow_python_projection_rules`,
  and `test_allocatable_module_fields_and_results_expose_lifetime_safe_handles`.
- [x] Keep pointer result tests on their explicit policy blocker; do not make
  their matrix rows `wrapper-plan` merely because allocatable results pass.

### Phase 7F — Borrowed Module Handles And Generated Operations

Included: rank-positive allocatable and pointer module variables exposed as one
stable borrowed handle object at module initialization. Repeated attribute reads
return the same handle. Replacement assignment is rejected. The generated
operation table accesses current native state and includes only operations
allowed by completed policy.

Allocatable operations include allocation state, shape, array actual,
descriptor handoff, extraction, deallocation, and resize where allowed. Pointer
operations include association state, shape, array actual, descriptor handoff,
nullification, extraction, and policy-gated allocation/deallocation/resize.
Borrowed module handles retain the Python module and never destroy native-owned
descriptor storage.

Deferred-character handles also expose runtime `element_length`. Shape-only
`allocate` and `resize` operations are omitted because they cannot state the
new character width; native procedures that declare the width remain the
authoritative mutation path.

Legacy oracle: the bridge's `_native_array_module_handle`,
`_native_array_module_handle_operations`, and operation-specific module methods;
the binding's `_bind_borrowed_native_array_module_handle`, operation wrappers,
and handle creation; and the current runtime handle factory.

- [x] Add a native-handle getter action and one `NativeArrayHandlePlan` beneath
  `ModuleVariablePlan`; keep Python attribute exposure and native operation
  generation in its binding and bridge child views.
- [x] Plan operation roles and export names explicitly while leaving operation
  call locals backend-local. Do not store generated method names in the plan.
- [x] Validate stable handle identity, module owner retention, rejected
  replacement, descriptor kind, operation completeness, and borrowed/no-destroy
  lifecycle.
- [x] Add `allocatable-module-handles` and `pointer-module-handles` support
  lanes only after module-only reduced parity covers state changes, zero-length
  state, extraction policy, operation permissions, stale-view behavior, and
  module lifetime.
- [x] Use `test_allocatable_module_fields_and_results_expose_lifetime_safe_handles`,
  `test_plain_allocatable_module_array_exposes_handle_with_read_only_extraction`,
  and the module portion of
  `test_module_and_derived_pointer_handles_track_native_association` as legacy
  oracles. Split out field/class assertions, which remain Phase 8/9 work.

### Phase 7G — Pointer Descriptor Extraction And Build Requirements

Included: pointer `descriptor_view`, `contiguous_view`, `copy_only`, and
explicitly unsupported extraction actions already selected by completed
policy; standard descriptor decoding; positive and negative strides; and local
build/header requirements.

Only `descriptor_view` and persistent allocatable owner storage require standard
C descriptor support. Generated code may read `CFI_cdesc_t` through
`ISO_Fortran_binding.h` when the completed plan requests it. It must never guess
or expose a compiler-private descriptor layout. Unsupported toolchains fail
readiness/build with the completed owner path and requirement.

- [x] Carry typed extraction and descriptor-interop actions plus required
  headers into handle/module/result plans and rendered artifact metadata.
- [x] Reuse the runtime descriptor-view helper for shape, stride, buffer-window,
  dtype, rank, and null-address validation; direct C lowering only decodes the
  standard descriptor fields into its expected mapping.
- [x] Add directly named C descriptor-reader and operation-wrapper methods;
  decoded dimension objects and mapping temporaries remain binding-local.
- [x] Validate that build requirements equal the union of completed plans,
  appear in replayable manifests, and do not leak into wrappers that need only
  ordinary buffers or non-CFI borrowed allocatable handles.
- [x] Replay
  `test_pointer_descriptor_views_preserve_slice_shape_strides_and_parent_lifetime`
  and `test_pyi_manifest_records_pointer_descriptor_interop_requirements`, plus
  focused `tests/runtime/handles`, before enabling
  `pointer-descriptor-extraction`.
- [x] Preserve the explicit readiness failure when required C descriptor
  support is unavailable; no contiguous-copy fallback may be inferred in the
  backend.

### Phase 7H — Remaining Rank-Zero Descriptor Results And Strings

Phase 3 already owns ordinary and optional scalar descriptor inputs, including
omitted/present-null/present-value state. Phase 4 already owns nullable scalar
descriptor module reads as copied Python snapshots. Do not rebuild those paths
or turn rank-zero descriptors into runtime handle objects.

Included here: direct scalar descriptor function results, hidden scalar
descriptor outputs, projected scalar descriptor readback, and allocatable or
pointer scalar character results with runtime/deferred length. The Python result
is `T | None` or `String | None`; absent allocation/association returns `None`.
An allocated/associated value is copied exactly once before the call-local or
native descriptor is released. Deferred-length strings use runtime element
length and preserve the existing encoding/byte contract.

- [x] Add a subordinate scalar-descriptor handoff/result record to the existing
  scalar or string `ArgumentTransferPlan`/`ResultPlan`; do not attach
  `NativeArrayHandlePlan` or use `ObjectKind.NUMPY_ARRAY` for rank zero.
- [x] Complete result source, descriptor kind, presence, runtime element length,
  copy action/reason, release owner, and failure cleanup in wrapper policy before
  planning.
- [x] Reuse existing Phase 3 presence records and typed lifecycle ordering;
  extend named scalar/string result lowering only for the descriptor producer
  and copy/release steps.
- [x] Validate direct versus hidden descriptor source, nullable result spelling,
  result ordering, runtime string length, null state, copy count, and cleanup on
  conversion/status failure.
- [x] Add isolated legacy/direct parity for numeric allocatable and pointer
  results and for `string_result_deferred` from
  `test_modern_fortran_character_arguments_and_results`, including an absent
  result and non-ASCII encoded data.
- [x] Keep pointer array results blocked even after pointer scalar values pass;
  copied scalar readback does not prove array target lifetime.

### Derived Fields Remain A Recorded Later Dependency

The shared handle plan must be capable of recording
`borrowed_field_descriptor`, `owner_retention=parent_wrapper`, field operation
roles, and parent-owned destruction behavior. Do not add field/class traversal
or route eligibility in Phase 7. `BindCNativeArrayHandleProperty`, field
operation generation, and the field portions of allocatable/pointer tests remain
legacy oracles for Phases 8 and 9, where the owning wrapper instance and property
lifecycle exist in the plan.

This boundary prevents Phase 7 from either duplicating future `FieldPlan`
ownership or falsely marking mixed module-and-field generation units supported.

### Legacy Primitive Inventory And Rewrite Rule

| Primitive | Legacy source | Direct-plan treatment |
| --- | --- | --- |
| Normal array handle actual | binding `_native_array_actual_argument_body`; runtime normal-array helpers | reuse runtime helper and Phase 6 bridge ABI; rewrite minimal binding nodes |
| Required/optional descriptor argument | binding descriptor argument helpers; bridge descriptor handlers | rewrite named direct methods around shared runtime packer and planned CFI roles |
| Projected writable descriptor | binding direct descriptor handler; bridge descriptor projection | rewrite direct pointer handoff and identity lifecycle; no fact-packed fallback |
| Owned allocatable result | binding owned-result/operation helpers; bridge allocatable result helper | rewrite minimal CFI owner-storage and result lifecycle nodes; assign once locally and transfer the allocation into the CFI-backed output dummy with `move_alloc` |
| Borrowed module handle | binding handle creation/operation wrappers; bridge module operations | rewrite under `ModuleVariablePlan`; reuse runtime factory |
| Pointer descriptor view | binding descriptor reader; runtime view helper | reuse runtime view helper; rewrite only standard-descriptor decoding nodes |
| Scalar descriptor result | legacy scalar descriptor/result conversion | extend existing scalar/string plan route; do not create an array handle |
| Build requirement | semantic `native_array_handle_build_requirements`; build manifest | reuse completed requirements and carry them through rendered artifacts |

For every primitive, first retain generated legacy C/Fortran/header artifacts
from the cited passing wrapper test. Explain each material direct-plan artifact
difference before compilation. Copy a small legacy method only when it already
matches the direct node API and complexity limit; otherwise rewrite the minimal
equivalent. Do not copy legacy dispatcher classes, scope mutation machinery, or
datatype/policy inference.

### Route And Test Migration Matrix For Phase 7

Mixed rows retain their later derived/field owners. The dependency-closed
Phase 7 rows were split, proved through both routes, and then recorded as
`wrapper-plan` in the complete ledger.

| Existing node or group | Current role/status | Phase 7 owner and target |
| --- | --- | --- |
| `arrays/test_array_results.py::test_array_results_follow_data_buffer_and_descriptor_handle_contracts[*]` | ordinary/allocatable result generation unit; `wrapper-plan` | Phase 6 ordinary and Phase 7E allocatable results now share the production plan route |
| `build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_manifest_records_pointer_descriptor_interop_requirements` | non-generating manifest policy; `not-applicable` | Phase 7G plan/header union is covered by direct generated-artifact tests |
| `derived_types/test_pointers.py::test_module_and_derived_pointer_handles_track_native_association[*]` | module, normal-array actual, and field mix; `legacy` | split Phase 7A/7F module subsets; field subset remains Phase 8/9 |
| `derived_types/test_pointers.py::test_pointer_descriptor_views_preserve_slice_shape_strides_and_parent_lifetime` | module/field descriptor views; `legacy` | Phase 7B/7G module subset; field owner remains Phase 8/9 |
| `derived_types/test_pointers.py::test_pointer_array_handles_block_on_unsupported_result_owner_policy[*]` | explicit supported blocker; `legacy` | remain blocker until owner/lifetime policy changes; never auto-promote |
| `edit_pyi_contracts/test_ownership_contracts.py::*` | module, field, result lifetime mix; `legacy` | Phase 7E/7F subsets; field/finalizer owners remain Phase 8/9 |
| `function_calls/test_optional_arguments.py::test_optional_allocatable_scalar_descriptor_distinguishes_omitted_none_and_value` | scalar baseline; `wrapper-plan` | reuse Phase 3 behavior; no status change |
| `function_calls/test_output_arguments.py::test_output_arguments_and_multiple_results_follow_python_projection_rules[*]` | mixed scalar/array/string/derived/allocatable outputs; `legacy` | Phase 7E reduced allocatable result; retain mixed row |
| `module_state/test_allocatable_replacement.py::*` | projected same-handle descriptor mutation plus a derived factory generation unit; `legacy` | Phase 7D reduced parity is `wrapper-plan`; the broad factory/class unit remains Phase 8/9 |
| `module_state/test_allocatable_views.py::test_allocatable_module_fields_and_results_expose_lifetime_safe_handles[*]` | module, result, and derived-field mix; `legacy` | field/class owner retention remains Phase 8/9 |
| `module_state/test_allocatable_views.py::test_scalar_descriptor_module_variables_return_copied_optional_values[*]` | scalar descriptor arguments/results/module state; `wrapper-plan` | source conversion records descriptor kind and argument/return reference before completed Phase 7H policy |
| `module_state/test_allocatable_views.py::test_plain_allocatable_module_array_exposes_handle_with_read_only_extraction[*]` | plain allocatable module snapshot; `wrapper-plan` | Phase 7F binding-owned detached read-only snapshot and capsule lifetime |
| `strings/test_character_arguments.py::test_modern_fortran_character_arguments_and_results[*]` | fixed strings plus deferred allocatable result; `legacy` | Phase 7H reduced deferred-result parity; retain mixed row as needed |
| `edit_pyi_contracts/test_native_order_contracts.py::test_editable_contract_can_use_native_order_arguments_without_native_call` | includes raw `Addr(Float64[n])` plus a derived result; `legacy` | raw-array subset is the completed Phase 6G prerequisite; derived subset remains Phase 8 |

| Completed sub-lane | Dependency-closed compiled evidence |
| --- | --- |
| Phase 7A, 7B, 7F, and 7G | `derived_types/test_pointers.py::test_module_native_array_handles_match_legacy_and_wrapper_plan_routes` |
| Phase 7C | `function_calls/test_optional_arguments.py::test_optional_array_descriptors_match_legacy_and_wrapper_plan_routes` |
| Phase 7D | `module_state/test_allocatable_replacement.py::test_projected_allocatable_descriptor_matches_legacy_and_wrapper_plan_routes` |
| Phase 7E numeric | `arrays/test_array_results.py::test_owned_allocatable_results_match_legacy_and_wrapper_plan_routes` |
| Phase 7E deferred character | `strings/test_character_arguments.py::test_deferred_character_array_handles_match_legacy_and_wrapper_plan_routes` |
| Phase 7H numeric | `scalars/test_scalar_boundary_plan.py::test_scalar_descriptor_results_copy_values_or_none_through_wrapper_plan_route` |
| Phase 7H deferred scalar character | `strings/test_character_arguments.py::test_deferred_allocatable_string_results_match_legacy_and_wrapper_plan_routes` and the nullable case in the deferred-character handle test |
| Phase 7H source/default projection | `module_state/test_allocatable_views.py::test_scalar_descriptor_module_variables_return_copied_optional_values[*]` |

Required focused intermediate coverage includes:

- completed semantic handle/interop policy projection tests;
- editable plan tests for every descriptor kind, handoff form, operation set,
  ownership, optional presence state, and lifecycle edit;
- C and Fortran preflight rejection of mismatched or incomplete descriptor
  plans;
- generated artifact assertions for standard descriptor fields, optional
  presence, operation functions, owner storage, destroy paths, and local header
  requirements;
- runtime helper tests under `tests/runtime/handles` without duplicating their
  validation in wrapper-codegen tests; and
- compiled legacy/direct parity for each reduced sub-lane before any migration
  ledger or production-route change.

### Phase 7 Completion

- [x] Expand Phase 7 under the mandatory gate using the live completed policy,
  runtime handle implementation, legacy backends, build integration, public
  contract, and focused wrapper tests.
- [x] Complete the shared typed handle, array-actual, and descriptor-handoff
  plan records without adding a parallel top-level plan hierarchy.
- [x] Complete every missing semantic selector before `ir2ast.py`; remove
  bridge-created `ArrayInteropPolicy` and fabricated semantic ownership choices.
- [x] Finish Phases 7A through 7H individually with legacy artifact capture,
  direct lowering, validation, compiled parity, route evidence, and matrix
  updates.
- [x] Preserve the completed Phase 6G raw-address boundary while keeping every
  derived-field, pointer-result, callback, and deferred-real-library exclusion
  on its explicit later blocker.
- [x] Run focused policy/plan/backend tests, relevant runtime-handle tests,
  documentation checks, the wrapper suite excluding LAPACK, the wrapper-codegen
  complexity checker, and the required static-analysis suite before declaring
  implementation complete.
- [x] Close Phase 7 only when every live non-field native-handle/descriptor case
  is migrated or explicitly removed from the product contract, and no backend
  infers descriptor policy or silently substitutes a data buffer, raw pointer,
  `.to_numpy()` extraction, or copy fallback.

Closure evidence: 538 focused semantic/policy/plan/backend/runtime tests, 1,133
documentation and layout tests, and all 318 wrapper tests outside the deferred
BLAS/LAPACK file pass. The wrapper-codegen complexity check, Ruff, formatting,
Bandit, Vulture, whitespace, and explicit-base Radon policy pass; full Radon
complexity and maintainability reports were also recorded. The source/default
scalar-descriptor projection now records its descriptor kind and argument or
return reference before policy completion. Binding and bridge lowering dispatch
only from the resulting typed plans; the remaining mixed derived-field unit is
an explicit Phase 8/9 blocker rather than a descriptor fallback.

## Phase 8 — Derived Types And Snapshots

Scope: opaque derived-type wrappers, borrowed views, wrapper-owned instances,
and snapshot copies.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate, separating origin, owned/borrowed/aliased/snapshot lifetime,
  input/result/field/module-state use, destruction, owner retention, and
  recursive member cases found in the live contract.

- [ ] Define derived-type handoff specs for wrapper address, owned instance,
  borrowed instance, and snapshot copy.
- [ ] Represent destruction/release responsibility in the result/writeback plan.
- [ ] Add binding and bridge actions for derived-type input, result, field
  access, and snapshot creation.
- [ ] Represent scalar and later non-scalar field getter/setter behavior only
  after the owning derived wrapper and class lifecycle are available.
- [ ] Validate owner-retention and release expectations before emission.

## Phase 9 — Classes, Constructors, Properties, And Methods

Scope: generated Python classes, keyword constructors, explicit constructor
bindings, properties, methods, static methods, overloads, and direct
`@bind(func_name)` constructor cases.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate. Inventory class creation and destruction, constructor categories,
  instance/static/type-bound methods, properties, overloads, inheritance or
  type relationships, decorator effects, and module initialization needs
  before defining the sub-lanes.

- [ ] Represent class layout, constructor candidates, explicit constructor
  bindings, default constructor behavior, and property/method plans.
- [ ] Keep `.pyi` constructor text, runtime constructor behavior, and bridge
  calls aligned through the same class plan.
- [ ] Validate that direct constructor bindings are not confused with overload
  dispatch.
- [ ] Validate property setter/getter exposure against bridge handoffs.

## Phase 10 — Callbacks And Trampolines

Scope: callback argument conversion, callback result conversion, adapter
procedures, C trampolines, callback context setup/cleanup, and error/abort
paths.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate. First inventory callback signature categories, context lifetime,
  re-entry/GIL behavior, exception propagation, abort paths, recursion, and the
  scalar/string/array/derived argument-result combinations actually supported
  by the product contract.

- [ ] Define callback handoff specs for Python callable validation, callback
  context, native adapter arguments, trampoline arguments, and callback results.
- [ ] Represent callback setup and cleanup as call-scoped plan phases.
- [ ] Add binding/bridge actions for scalar, array, string, and derived callback
  arguments/results only after those lanes are stable for ordinary calls.
- [ ] Validate callback result and argument handoffs across binding, bridge,
  adapter, and trampoline steps before emission.

## Phase 11 — Cross-Cutting Wrapper Suite Completion

Scope: existing wrapper tests whose generation units combine completed semantic
lanes or exercise build and runtime behavior rather than introducing one new
datatype lane.

- [ ] Reconcile every remaining `legacy` or `dual-route` matrix row by owning
  test area: `build_from_source`, `build_from_pyi`, `edit_pyi_contracts`,
  `external_routines`, `multiple_files`, `naming`, `runtime_behavior`, and
  `real_libraries`.
- [ ] Group remaining rows into dependency-ordered waves by their actual
  unsupported owner paths. Do not implement a broad test directory as one
  special case and do not add per-test backend fallbacks.
- [ ] For every newly discovered semantic or backend gap, expand the applicable
  earlier lane or add an explicit sub-lane here, then follow the complete
  policy -> plan -> backend -> emission -> compiled parity -> route sequence.
- [ ] Prove source-driven and semantic-`.pyi`-driven builds use the same route
  selector and wrapper planner while retaining their existing build assertions.
- [ ] Prove edited-policy contracts, external symbols, multiple-source builds,
  naming/generic interfaces, runtime policies, recursion, OpenMP, and real
  library-independent native bundles preserve their existing assertions
  through the wrapper-plan route.
- [ ] Keep non-wrapper-generating tests, including layout and generated-`.pyi`
  checks, marked `not-applicable` to route selection but passing in the same
  suite.
- [ ] Run every `tests/wrapper` test except
  `test_real_blas_lapack.py` locally and in CI as the pre-cutover gate.
- [ ] Finish this phase only when every nondeferred matrix row is either
  `wrapper-plan` or justified `not-applicable`; no nondeferred row may remain
  `legacy` or `dual-route`. BLAS/LAPACK rows remain
  `deferred-real-library` until Phase 12.

## Phase 12 — Cutover And Removal

- [ ] Re-audit collected Python test nodes under `tests/wrapper` and reconcile
  them with the migration matrix. No test may be missing from the matrix.
- [ ] After every other migration row is complete, restore the full
  `test_real_blas_lapack.py` run and any required native-cache preparation in
  local opt-in verification and GitHub Actions.
- [ ] Run both BLAS and LAPACK generation units through legacy and wrapper-plan
  routes using their existing assertions. Resolve parity before changing their
  matrix rows from `deferred-real-library` to `wrapper-plan`.
- [ ] Require every wrapper-generating test row to be `wrapper-plan`; no row may
  remain `legacy` or `dual-route`. Confirm route diagnostics show that every
  runtime wrapper generation unit uses the new route.
- [ ] Run the complete `tests/wrapper` suite in CI, including restored BLAS and
  LAPACK coverage, and require every test to pass before legacy deletion.
- [ ] Track which lanes still use the old `semantic_ir_to_codegen_ast()` path.
- [ ] Track route support at whole-generation-unit granularity and keep
  unsupported owner-path diagnostics stable until the corresponding lane is
  migrated.
- [ ] Keep completed legacy lanes available for deliberate rollback until all
  live lanes have parity evidence and the final cutover is approved; do not
  delete old handlers incrementally merely because one fixture uses the plan
  route.
- [ ] Do not move modified isolated nodes or printers back into the legacy
  package during migration. After final cutover, remove the legacy package
  pieces proven unused and keep `x2py.wrapper_codegen` as the canonical
  generator rather than performing a second package rename.
- [ ] Remove old lowering/codegen code only after every live wrapper lane has a
  wrapper-plan route and focused verification.
- [ ] Remove the temporary legacy route and its route diagnostics after every
  live generation unit is supported; do not replace it with compatibility
  shims or per-function fallback.
- [ ] Remove migration-only dual-route orchestration after the complete existing
  wrapper suite proves the wrapper-plan route and legacy rollback is no longer
  supported. Keep the existing behavioral fixtures and assertions.
- [ ] Keep source printers only for the remaining generated source fragments they
  still own, or replace them with narrower emitters once the model layer is no
  longer needed.

## Verification

- [ ] Documentation-only changes run
  `python3 -m pytest -q tests/docs/test_examples.py tests/docs/test_structure.py`
  and `git diff --check`.
- [ ] Wrapper-plan code changes run the affected existing `tests/wrapper` nodes,
  the minimal intermediate contract tests required above, and the required
  static-analysis suite from `AGENTS.md`.
- [ ] Wrapper-codegen implementation changes pass
  `python3 tools/check_wrapper_codegen_complexity.py` with no handler waiver.
- [ ] Runtime wrapper tests are required when generated behavior changes.
- [ ] Every migrated lane runs eligible existing fixtures and assertions through
  both routes. Compare behavior and ABI-relevant call mapping; do not require
  byte-identical source when mechanical organization differs.
- [ ] Structural dependency tests prove complete generator isolation: no
  imports from `x2py.wrapper_codegen` to `x2py.codegen` or in the reverse
  direction.
- [ ] BLAS and LAPACK full-library wrapper tests remain excluded locally and in
  GitHub Actions throughout Phases 0-11. Re-enable both only at the explicit
  Phase 12 gate after every other migration row is complete.

## Completion Record

- [ ] The final report for each lane names the plan actions added, the binding
  and bridge handlers they dispatch to, and the handoff specs validated.
- [ ] The final report lists old lowering/codegen paths still used by unsupported
  lanes.
- [ ] The final cutover report includes the completed `tests/wrapper` migration
  matrix and confirms every wrapper-generating row uses the wrapper-plan route.
- [ ] The final report includes focused verification commands and results.
- [ ] The final report includes the changed-stage breakdown required by
  `AGENTS.md` and names every test file added or updated with the behavior it
  covers.
## Session Continuation Protocol

The stable continuation prompt is:

```text
Continue implementing the wrapper-plan migration checklist.
```

On continuation: read this checklist and `AGENTS.md`; inspect the dirty
worktree; choose the first unchecked dependency-closed item; replay the
existing passing wrapper test before extending a lane; implement code and tests
together; run required verification; and check items only from live evidence.
Do not reset unrelated user changes, infer missing policy in lowering, or use a
new fallback after direct plan generation starts.
