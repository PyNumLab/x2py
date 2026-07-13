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
    results: ResultPlan ...
      binding: BindingResultPlan
      bridge: BridgeResultPlan
      native_call_slot: NativeCallSlotPlan | None
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
| `wrapper-plan` | 78 |
| `dual-route` | 5 |
| `legacy` | 130 |
| `not-applicable` | 95 |
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
| `tests/wrapper/fortran/arrays/test_array_results.py::test_array_results_follow_data_buffer_and_descriptor_handle_contracts[*]` | source/generated-.pyi parity | ordinary arrays; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/arrays/test_array_results.py::test_ordinary_array_results_match_legacy_and_wrapper_plan_routes` | production output-only plan route with deliberate legacy rollback comparison | fixed/runtime-shape ordinary array results; ranks one through fifteen; Fortran order; zero-sized results; allocation/copy/release failure paths | `wrapper-plan` |
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
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_manifest_records_pointer_descriptor_interop_requirements` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; native handles/descriptors | `legacy` |
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
| `tests/wrapper/fortran/derived_types/test_pointers.py::test_pointer_array_handles_block_on_unsupported_result_owner_policy[*]` | source/generated-.pyi parity or parametrized route | derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/derived_types/test_pointers.py::test_pointer_descriptor_views_preserve_slice_shape_strides_and_parent_lifetime` | direct wrapper/build route | derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::test_editable_contract_can_use_native_order_arguments_without_native_call` | direct wrapper/build route | semantic .pyi generation/parsing; native-call projections; arrays and derived types deferred to later lanes | `legacy` |
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
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_arguments_drive_fortran_present_behavior[*]` | source/generated-.pyi parity or parametrized route | optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_array_buffers_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing optional native unit | omitted/`None`/present ordinary array storage; mutation; projected identity; native-handle actuals deferred to Phase 7 | `dual-route` |
| `tests/wrapper/fortran/function_calls/test_scalar_writeback_plan.py::test_scalar_copy_in_out_returns_replacement_through_both_routes` | production plan route with deliberate legacy rollback comparison | scalar copy-in/native mutation/copy-out/cleanup; build/artifact integration | `wrapper-plan` |
| `tests/wrapper/fortran/function_calls/test_output_arguments.py::test_output_arguments_and_multiple_results_follow_python_projection_rules[*]` | source/generated-.pyi parity | mixed-type multiple-result aggregation; ordinary arrays; strings; derived types/snapshots; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/function_calls/test_output_arguments.py::test_hidden_ordinary_array_output_matches_legacy_and_wrapper_plan_routes` | production output-only plan route with deliberate legacy rollback comparison | fixed/runtime-shape hidden ordinary array output; zero-sized output; allocation/copy failure paths | `wrapper-plan` |
| `tests/wrapper/fortran/layout_rules/test_wrapper_guide_layout.py::*` | non-generating: wrapper docs/test layout | test/docs layout | `not-applicable` |
| `tests/wrapper/fortran/module_state/test_allocatable_replacement.py::*` | source/generated-.pyi parity or parametrized route | module variables/state; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/module_state/test_allocatable_views.py::*` | source/generated-.pyi parity or parametrized route | module variables/state; native handles/descriptors | `legacy` |
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
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_fixed_width_character_arrays_match_legacy_and_wrapper_plan_routes` | reduced semantic `.pyi` entry over the existing `fstrings_f90` native unit | fixed-width `NPY_STRING` array itemsize; rank/dtype/zero-size validation; native-handle actuals deferred to Phase 7 | `dual-route` |
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

- [x] Complete declared-shape evaluation, flat-storage orientation,
  multidimensional dense handoff, validation, parity, and ledger evidence.

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

### Phase 6 Completion

- [x] Expand the phase under the mandatory expansion gate from live semantic
  array contracts, legacy binding/bridge lowering, public docs, and focused
  wrapper tests.
- [x] Define array handoff specs for every supported data, rank, shape, stride,
  order, itemsize, writeability, result, and lifecycle role.
- [x] Validate every completed array policy and handoff role before either
  backend emits source.
- [x] Finish Phase 6 only when every ordinary-array matrix row is migrated or
  remains blocked solely by an explicitly later descriptor, derived, field,
  callback, or deferred-real-library lane.

## Phase 7 — Native Array Handles And Descriptors

Scope: `Allocatable[T[...]]`, `Pointer[T[...]]`, scalar descriptor-backed
values including allocatable or pointer `String`, descriptor-backed handoffs,
and runtime native array handle objects.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate and reconcile it with the maintained native-array-handle checklist.
  Split allocatable and pointer behavior only after extracting their shared
  descriptor, presence, runtime element-length, ownership, release,
  module/field, argument, and result sub-lanes. Include nullable deferred-
  length scalar character results in that shared audit rather than creating a
  string-only descriptor path. Keep rank-zero scalar descriptor results as
  copied Python scalar values; reserve native-array handles for rank-positive
  array storage.

- [ ] Define descriptor handoff specs for CFI descriptors, descriptor ownership,
  optional-absent handles, owner retention, extraction policy, and required
  headers.
- [ ] Move bridge-created `ArrayInteropPolicy` decisions into plan generation or
  completed policy for source/contract values.
- [ ] Replace bridge-created semantic `OwnershipDecision` values for generated
  helper temporaries with explicit bridge-local helper specs.
- [ ] Validate descriptor/data-buffer mismatches before emission.
- [ ] Keep generated helper storage local to bridge/binding implementation
  methods; do not represent helper temporaries as semantic ownership policy.

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
