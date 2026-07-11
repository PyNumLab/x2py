---
title: Wrapper Plan Migration Checklist
audience: maintainers
prerequisites: pipeline map, semantic IR, ownership policy
related: ../internal-architecture/pipeline-map.md, ../../user/reference/semantic-ir.md, semantic-pyi-wrapper-checklist.md, index.md
status: active-roadmap
---

# Wrapper Plan Migration Checklist

This checklist replaces the broad "freeze every stage" idea with a smaller,
more useful target: build wrappers from an explicit, readable wrapper plan
instead of sending semantic IR through the current generic lowering/codegen
model first.

This file is the canonical implementation prompt for the migration. Route
granularity, plan structure, supported-lane definitions, validation rules,
emitter ownership, and cutover state must be recorded here before the related
code is changed. A phase heading is not by itself an implementation-ready
specification; the expansion rules below apply to the broader later phases.

The long-term target is:

```text
semantic IR
  -> post-IR policy completion
  -> wrapper-generation route selection
       -> wrapper-plan route
            -> build and validate wrapper plan
            -> binding emitter + bridge emitter
            -> complete generated wrapper artifact set
       -> temporary legacy route
            -> semantic_ir_to_codegen_ast()
            -> existing bridge/binding generation
            -> complete generated wrapper artifact set
  -> shared compilation and link orchestration
  -> importable extension
```

The route selects the complete runtime-wrapper generation path. It does not
select only argument lowering, one function, the binding, or the bridge. Both
routes must produce everything the shared build orchestration needs for one
extension: generated bridge source, generated C/CPython binding source and
headers, module initialization, required imports/includes/runtime support,
generated source compile requirements, and the names and files passed to the
existing compilation/link stage.

Semantic `.pyi` generation and printing are not part of this route and remain
on their current path. The wrapper plan may consume semantic IR loaded from a
`.pyi` contract, but it does not replace or alter `.pyi` emission.

The wrapper plan is the contract between the Python binding, the generated
native bridge, and the native call. A maintainer should be able to open the plan
for one wrapper function and see:

- the Python-visible arguments and result order,
- decorator effects such as `@native_call`, `@bind`, `@raises`, overload
  metadata, hidden native literals, and reordered native arguments,
- the binding action selected for each Python argument/result,
- the bridge handoff produced by binding and consumed by bridge,
- the bridge action selected for the native call,
- copy-in, copy-out, writeback, cleanup, and result projection phases,
- the exact dispatch key that selects each binding and bridge implementation
  method.

The plan should be simple enough for maintainers to read and transform, but
complete enough that invalid edits fail before any C or Fortran source is
emitted.

## Migration Source Of Truth

This is a representation and ownership migration, not a wrapper-behavior
redesign. The current production path through `semantic_ir_to_codegen_ast()`,
the existing bridge and binding generators, the source printers, and the build
orchestration is the behavioral source of truth for each lane until that lane
has completed parity evidence.

- Derive each new plan action and handler from an audited current code path and
  its wrapper tests. Do not invent a new conversion, ABI, call order, cleanup
  order, public/generated-symbol naming contract, runtime helper protocol,
  error behavior, or build artifact layout merely because the new
  representation could support one.
- Preserve settled semantic/public contracts and previously documented bug
  fixes when they are stricter than accidental current implementation behavior.
  Any other intentional behavior change is separate work: document and test it
  independently before changing the migration baseline.
- Copy the minimum dependency-closed set of existing CPython and NumPy API
  models, C and Fortran declaration/statement nodes, datatype/literal models,
  scope/name mechanisms, and source-printer behavior needed by each lane into
  the isolated new generator. These are second independent copies, not imports,
  aliases, subclasses, or adapters around legacy model classes. Copy the current
  behavior first, record its origin and parity evidence, and modify only the new
  copy. Do not make the new route import legacy codegen primitives.
- Shared policy-completed semantic input, stable runtime APIs, the generated-
  artifact handoff, and compilation/link orchestration may remain common. If a
  new route needs changed runtime behavior, add a separately named helper used
  only by that route until cutover; do not change the meaning of a helper still
  used by the legacy generator.
- Keep the legacy route runnable and behaviorally unchanged while a lane is
  introduced. Production route selection is explicit, and tests must be able to
  invoke both routes for an eligible generation unit without a public
  compatibility flag.
- A lane is not migrated merely because the new route compiles. It must match
  the existing route's Python-visible results, native argument/result order,
  mutation and writeback, exceptions, ownership/lifetime behavior, generated
  artifact requirements, and success/failure cleanup behavior.
- Generated source text does not need to be byte-for-byte identical when the
  same behavior and ABI are preserved. Backend-local names and equivalent
  mechanical control flow may differ. Material differences must be explained by
  the new mechanical organization, not by an unplanned semantic change.
- Until final cutover, reverting a lane means deliberately routing its whole
  generation unit through the still-maintained legacy route. It does not mean
  catching a new-route failure and silently retrying legacy generation.

## Route Selection Contract

The initial migration route is atomic for one extension generation unit. In
the current build orchestration that unit is the merged semantic module used to
build one importable extension.

- Route selection runs after post-IR policy completion and before
  `semantic_ir_to_codegen_ast()`.
- The support check recursively inspects every runtime-visible or
  runtime-required element in the merged module: functions, arguments,
  results, hidden native arguments/results, decorator effects, module
  variables, classes, constructors, properties, methods, overload dispatch,
  cleanup, and build requirements.
- The wrapper-plan route is selected only when every such element is covered by
  implemented plan actions, validators, binding handlers, and bridge handlers.
- No accepted decorator, native-call projection kind, or implicit call behavior
  may be ignored by the support check. It must be implemented by a completed
  lane or reported as an unsupported owner path that selects the legacy route.
- If any element is not covered, the whole generation unit uses the temporary
  legacy route. Initially, one extension must not mix plan-generated functions
  with legacy-generated functions, or a plan-generated binding with a
  legacy-generated bridge.
- The route decision returns a structured support report with the selected
  route and owner paths/reasons for every unsupported element. It must be
  inspectable in tests and maintainer diagnostics.
- Unsupported migration coverage may select the legacy route. Invalid or
  inconsistent completed policy must fail before route selection; an error in
  plan construction, validation, emission, or compilation after the plan route
  is selected must fail the build and must not silently retry the legacy route.
- Source-driven and semantic-`.pyi`-driven extension builds use the same route
  selector and the same wrapper-plan builder after producing the merged,
  policy-completed semantic module.

Function-level or mixed-route generation can be considered only after the
module-level migration is complete and only if a concrete need justifies its
extra composition and validation rules. It is not part of this checklist.

## Design Rules

- Post-IR policy completion decides semantic actions. Binding and bridge emitters
  consume those actions; they do not reconstruct them from datatype, `intent`,
  `is_alias`, local memory handling, dotted-variable shape, or missing policy.
- The wrapper plan records action keys, handoff expectations, and native-call
  ordering. It does not contain raw generated C, Fortran, or CPython text.
- Binding and bridge emitters are dispatch tables plus small implementation
  methods. Reuse completed policy actions directly when they already identify
  the behavior, such as `PythonBarrierAction.SCALAR_VALUE` and
  `NativeBarrierAction.PASS_VALUE`; do not create a parallel action vocabulary
  merely to rename them in the plan.
- Each action has exactly one registered handler for its emitter. Validation and
  plan rendering resolve that registry to the exact method name; emitters do not
  dynamically construct method names or run a second policy-selection tree.
- Initial copied handlers keep the current dispatch method names when practical,
  so a plan action can be traced directly to the audited legacy method. Add a
  new plan-only action only when no completed policy action expresses the
  required semantic step; first confirm that the missing distinction does not
  belong in post-IR policy completion.
- Dispatch should be by semantic lane and action, not by every concrete dtype.
  For example, `Float64`, `Int32`, and `Bool` can share scalar-value handlers
  while dtype remains plan data.
- Every binding output that the bridge consumes is represented by a handoff
  spec. Every bridge native argument/result that the native call consumes is
  represented by a native-call spec.
- Validation checks producer/consumer consistency before emission:
  `binding.produces` must match `bridge.expects`, bridge output must match the
  native call slot, and writeback/result plans must consume values that were
  actually produced.
- Local variable names may be generated by a plan context, but the plan should
  carry stable symbolic roles such as `value`, `descriptor`, `shape`, `status`,
  `message`, or `writeback`.
- The old lowering/codegen path may remain temporarily for unsupported lanes,
  but the route must be explicit and tracked by lane and owner path. Do not hide
  a semantic fallback inside binding, bridge, or printer code.
- Plan construction and validation are separate from source emission. Emitters
  may create backend-local names and helper temporaries, but they may not add,
  remove, reorder, or reinterpret semantic actions from the validated plan.
- Backend-specific resource mechanics do not belong in the wrapper plan.
  CPython borrowed/new/stolen-reference rules, `Py_INCREF`/`Py_DECREF`, and
  partial-failure reference cleanup are private binding-emitter mechanics.
  Equivalent compiler/runtime details remain private to their backend.
- A plan may record backend-neutral lifetime relationships such as owned,
  borrowed, transferred, retained owner, destruction responsibility, or
  call-scoped cleanup. The selected backend method mechanically maps those
  relationships and the target API's contract to its local resource handling;
  doing so is implementation, not a new semantic decision.
- Isolation begins after post-IR policy completion. The new generator must not
  import `x2py.codegen`, and legacy `x2py.codegen` modules must not import the
  new generator. High-level pipeline orchestration is the only owner allowed to
  select between them.
- Copy backend primitives incrementally by lane, not as a wholesale clone of
  the legacy codegen package. Each copied slice includes only the dependency
  closure needed to generate and print that lane, so its representation can
  evolve without changing the legacy route.
- Maintainer edits use an explicit immutable plan transformation between plan
  construction and validation. The transformed plan is validated exactly like
  a generated plan; there is no trusted-edit bypass.
- The binding and bridge emitters both consume the same validated plan. Their
  generated runtime data flow is Python binding -> bridge -> native call, but
  one emitter is not the semantic-policy input to the other.

## Intended Ownership And Files

The exact names may evolve during Phase 0, but responsibilities should remain
separated along these lines:

```text
x2py/wrapper_codegen/
  scope.py          copied scope and deterministic name-allocation behavior
  types.py          copied datatype/literal primitives needed by migrated lanes

  plan/
    models.py       frozen readable plan records
    actions.py      action, handoff, and native-pass enums/specs
    build.py        completed semantic IR -> WrapperPlan
    validate.py     cross-boundary consistency validation
    support.py      whole-generation-unit route support report
    render.py       stable maintainer-readable plan rendering

  c/
    nodes.py        copied C declarations/statements needed by migrated lanes
    cpython_api.py  copied CPython API primitives needed by migrated lanes
    numpy_api.py    copied NumPy C API primitives needed by migrated lanes
    concepts.py     copied C/CPython helper concepts needed by migrated lanes
    context.py      new-route local values and cleanup state
    binding.py      validated plan -> complete CPython binding representation
    printer.py      isolated C/CPython source emission

  fortran/
    nodes.py        copied Fortran declarations/statements needed by lanes
    context.py      new-route Fortran names and scopes
    bridge.py       validated plan -> complete native bridge representation
    printer.py      isolated Fortran source emission

  artifacts.py     complete new-route generated-wrapper artifact result

x2py/pipeline/
  shared route selection and compile/link orchestration
```

This is a permanent responsibility-based package name, not a temporary
`new_codegen` package that would need another migration after cutover. Files
under `c/` and `fortran/` are added only as a migrated lane needs them; the
layout does not authorize copying the entire legacy package up front.

Within the generation boundary there is no shared model identity between the
routes. If a migrated scalar handler needs a legacy `Variable`, datatype,
literal, CPython call model, NumPy call model, scope, or printer-dispatch base,
copy that item's complete required dependency slice into
`x2py.wrapper_codegen` first. The copied class may then evolve independently
without changing or importing its legacy counterpart.

`ir2ast.py` remains the entry to the temporary legacy route; it must not choose
the route or partially invoke the new emitters. The source-driven and `.pyi`-
driven build entrypoints should call one shared orchestration helper rather
than implement different support rules.

The two routes should return one pipeline-owned internal generated-artifact
result shape so the existing compiler/link orchestration does not need to
understand plan actions. That result is an internal build handoff, not a
compatibility API and not a second semantic model.

The isolated C and Fortran layers are thin mechanical backend layers. For each
primitive, first copy the proven legacy behavior and tests needed by the lane;
then simplify or modify the new copy only as required by plan-driven emission.
The original node, printer, scope, and generator implementations remain
untouched and runnable. Shared compilation receives generated files through the
artifact result and does not import either route's internal models.

## Node Construction And Printing Contract

Emitters construct backend nodes; printers render backend nodes. Do not mix
these responsibilities.

```text
validated WrapperPlan
  -> Fortran bridge emitter
       -> isolated Fortran module/function/declaration/statement nodes
       -> isolated Fortran printer
       -> bridge source text
  -> CPython binding emitter
       -> isolated C module/function/declaration/statement nodes
       -> isolated C source/header printers
       -> binding source and header text
  -> artifact assembler
       -> complete generated-wrapper artifact result
```

- Both emitters consume the same validated wrapper plan and its explicit bridge
  ABI specification. The binding emitter must not consume the generated
  Fortran AST, and the bridge emitter must not discover information that the C
  binding needs. If either occurs, the shared plan or ABI specification is
  incomplete.
- Each dispatched emitter method returns backend-node fragments such as
  declarations, setup statements, call arguments, result statements,
  success/failure cleanup, and produced symbolic values. A module assembler
  combines those fragments into a complete C or Fortran module node.
- Emitters do not concatenate source text. CPython conversion and reference-
  counting operations are represented by isolated C/API call nodes; Fortran
  declarations, assignments, calls, and control flow use isolated Fortran
  nodes.
- Printers accept only their backend nodes. They own syntax, indentation,
  punctuation, fixed syntax templates, and mechanical rendering of represented
  includes/imports. They must not accept `WrapperPlan`, inspect plan actions,
  choose conversions, add lifecycle behavior, or repair incomplete modules.
- Includes, imports, public/generated symbols, function signatures, and header
  declarations are selected by plan-driven emission and represented as nodes
  before printing. A printer may deduplicate or order them mechanically.
- C source/header and Fortran source printers are independently testable against
  the copied baseline nodes before plan emitters use them.
- `plan/` does not import `c/` or `fortran/`; the C and Fortran backends do not
  import each other; and backend printers import their nodes/types but not plan
  builders, actions, validators, emitters, or pipeline routing. Add structural
  tests for these internal dependency directions with the package skeleton.

## Core Plan Shape

The exact class names can evolve, but the first implementation should stay close
to this shape:

```python
@dataclass(frozen=True)
class WrapperPlan:
    extension_name: str
    module: ModulePlan
    requirements: WrapperArtifactRequirements


@dataclass(frozen=True)
class ModulePlan:
    public_name: str
    functions: tuple[FunctionPlan, ...]
    variables: tuple[VariablePlan, ...]
    classes: tuple[ClassPlan, ...]


@dataclass(frozen=True)
class FunctionPlan:
    public_name: str
    native_name: str
    decorators: DecoratorPlan
    python_arguments: tuple[ArgumentPlan, ...]
    bridge_abi: BridgeAbiPlan
    native_call: NativeCallPlan
    results: tuple[ResultPlan, ...]
    writebacks: tuple[WritebackPlan, ...]


@dataclass(frozen=True)
class ArgumentPlan:
    public_name: str
    semantic_type: object
    python_position: int | None
    binding: BindingStep
    bridge: BridgeStep
    native: NativeArgumentSpec
    writeback: WritebackPlan | None = None


@dataclass(frozen=True)
class BindingStep:
    action: PythonBarrierAction
    produces: tuple[HandoffSpec, ...]


@dataclass(frozen=True)
class BridgeStep:
    action: NativeBarrierAction
    expects: tuple[HandoffSpec, ...]
    produces: tuple[NativeArgumentSpec, ...]


@dataclass(frozen=True)
class NativeCallPlan:
    native_name: str
    arguments: tuple[NativeArgumentRef, ...]
    results: tuple[NativeResultRef, ...]
```

The plan validator owns consistency diagnostics. Binding and bridge emitters
should be able to trust a validated plan and focus on emitted-code mechanics.

The first implementation also needs two non-semantic orchestration records:

- a route support report naming the generation unit, selected route, covered
  lanes, and unsupported owner paths/reasons;
- a generated wrapper artifact result naming the complete bridge/binding
  sources, headers, imports/includes/runtime requirements, generated source
  compilation requirements, and extension initialization name.

These records must not duplicate the native object/library/link plan already
owned by build orchestration.

## Worked Scalar Trace

For a Python-visible scalar procedure equivalent to:

```python
def f(x: Float64) -> None: ...
```

assume post-IR policy completion produces the existing actions
`PythonBarrierAction.SCALAR_VALUE` and
`NativeBarrierAction.PASS_VALUE`. The maintainer-visible plan rendering should
stay approximately this small:

```text
function f(x: Float64) -> None
  argument x
    binding action   scalar_value
    binding handler CPythonBindingEmitter._convert_python_scalar_value_argument
    produces        x.value : Float64
    bridge ABI      f_bridge.x consumes x.value
    bridge action   pass_value
    bridge handler  FortranBridgeEmitter._convert_native_value_argument
    native slot     f argument 0 <- x.value
  result            none
```

The exact top-level call path should be equally direct:

```text
complete_semantic_policies(module)          existing semantic stage
build_wrapper_plan(module)                  completed policy -> WrapperPlan
validate_wrapper_plan(plan)                 handoff/ABI/handler validation
generate_wrapper_artifacts(plan)
  CPythonBindingEmitter.emit_function(f)
    -> _convert_python_scalar_value_argument(x)
    -> isolated C node fragments
  FortranBridgeEmitter.emit_function(f)
    -> _convert_native_value_argument(x)
    -> isolated Fortran node fragments
  CPythonCodePrinter.doprint(c_module)       nodes -> C source/header
  FCodePrinter.doprint(fortran_module)       nodes -> Fortran source
create_shared_library(...)                  existing compilation/link entrypoint
```

At runtime, the generated CPython binding converts the Python argument into the
scalar C handoff, calls the generated bridge symbol, and the bridge invokes the
native procedure using the completed `PASS_VALUE` behavior. CPython reference
counting, concrete temporary names, C declarations, Fortran declarations, and
printer formatting are deliberately absent from the rendered plan.

A scalar plan that requires a maintainer to inspect backend nodes or printer
code to discover either selected handler has failed the readability goal. The
rendered plan is the normal trace; backend nodes and printers are inspected only
when debugging how a selected handler emits source.

## Decorator And Native-Projection Coverage

Decorator and projection handling is part of route support, not an emitter
detail. Maintain a matrix in this section as implementation proceeds. Each row
must eventually name its exact plan representation, validation rules, binding
handler, bridge handler, and focused tests.

| Contract effect | Owning phase | Initial route rule |
| --- | --- | --- |
| Direct scalar call with implicit native order | Phase 1 | Eligible after scalar input actions are complete |
| `@bind(...)` native symbol selection | Phase 1 | Legacy route until symbol selection is explicit in `NativeCallPlan` |
| `@external` native target selection | Phase 1 | Legacy route until target/source-language requirements are explicit |
| `@hold_gil` call behavior | Phase 1 | Legacy route until GIL behavior is an explicit binding call phase |
| `@native_call` scalar `Arg(...)` reordering and `Addr(Arg(...))` | Phase 1 | Legacy route until every native slot and address handoff validates |
| `@native_call` typed numeric/logical hidden literals | Phase 1 | Legacy route until literal type, value, and native slot validate |
| `@native_call` scalar `Return(...)`, `Work(...)`, and direct native result projection | Phase 2 | Legacy route until result/workspace production and consumption validate |
| `@raises(...)` status/message projection | Phase 2 | Legacy route until status, message, success rule, and Python error path validate |
| Optionality and `IsPresent(...)` | Phase 3 | Legacy route until omitted, explicit `None`, present, and presence-token paths validate |
| String `Len(...)` and typed string literals | Phase 5 | Legacy route until the expanded string sub-lanes are complete |
| Array shape/stride/size/itemsize and conversion projections | Phase 6 | Legacy route until the expanded ordinary-array sub-lanes are complete |
| `Allocatable(...)` and `Pointer(...)` native projections | Phase 7 | Legacy route until the expanded descriptor/handle sub-lanes are complete |
| Derived/native type metadata | Phases 8-9 | Legacy route until the relevant derived-type and class sub-lanes are complete |
| `Pass()`, methods, constructors, properties, and `@overload(...)` | Phase 9 | Legacy route until the expanded class sub-lanes are complete |
| Callback decorators, adapters, and trampoline behavior | Phase 10 | Legacy route until the expanded callback sub-lanes are complete |

When the live parser or semantic model accepts an effect missing from this
matrix, add it before implementing or routing that case. Do not treat the table
as proof that every current syntax spelling has already been audited; Phase 0
owns that live inventory.

## Incremental Protocol

For each lane:

1. Audit the current lowering, binding, bridge, printer, runtime-helper, and
   build paths for the lane, and record the observed behavior and focused tests
   that make it the migration baseline.
2. Expand this checklist with the lane's exact scope, exclusions, source-path
   baseline, copied dependencies, plan fields, and validation invariants.
3. Copy the minimum dependency-closed legacy backend primitives required by the
   lane into `x2py.wrapper_codegen`, prove copied baseline behavior, then add
   or adapt isolated node/printer tests.
4. Implement the plan objects, action registries, ABI/handoff specs, validator,
   and support-report coverage for that lane.
5. Generate the plan from policy-completed semantic IR, dispatch binding and
   bridge handlers into isolated node fragments, assemble complete backend
   modules, and print complete internal artifacts.
6. Compile the internal artifacts before changing production route selection.
7. Run the same eligible fixtures through both routes and compare compiled
   runtime behavior, failure paths, native-call mapping, and artifact
   requirements.
8. Extend the whole-module support predicate so a generation unit uses the
   wrapper-plan route only when all its elements belong to completed lanes.
   Keep the old route for generation units containing unsupported lanes.
9. Mark the lane complete only when focused parity tests pass and every
   intentional difference from the baseline is separately documented.

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
- focused generation/runtime tests and parity evidence against the legacy
  route;
- the exact legacy source path for every copied primitive, its dependency
  closure, baseline evidence, modifications in the isolated copy, and a reason
  for every entirely new backend primitive;
- dependencies on earlier lanes and the legacy behavior that can be removed
  when the sub-lane is complete.

Do not mark a broad phase complete from its current envelope items. Mark its
expanded sub-lanes individually, then close the phase only after all live cases
in its audited support matrix are either migrated or explicitly removed from
the product contract.

## Required Execution Order

The checklist order is mandatory. Do not wire the new route into production
build selection while its scalar artifacts exist only as models or uncompiled
source. Complete each subphase and its focused evidence before starting the
next one:

```text
0A current-behavior baseline
  -> 0B isolated package and dependency boundary
  -> 0C copied scalar backend nodes and printers
  -> 0D wrapper-plan core and validation
  -> 1A internal scalar plan emission
  -> 1B compiled dual-route parity
  -> 1C production route selection
  -> later semantic lanes in numbered order
```

Within later lanes, follow the same order: audit current behavior, expand the
lane checklist, copy required backend dependencies, add plan/actions and
validators, emit nodes, print internally, compile and compare both routes, and
only then widen production route eligibility.

## Phase 0 — Foundation Before Production Routing

### Phase 0A — Current Scalar Baseline

- [ ] Inventory the current end-to-end wrapper behavior and implementation paths
  for the first scalar lane, including lowering branches, binding/bridge helper
  methods, CPython/NumPy API primitives, source printers, generated artifacts,
  build integration, and focused runtime fixtures.
- [ ] Create a maintained baseline matrix mapping each first-lane current code
  path and observable behavior to its proposed plan action, handler, copied
  backend dependencies, and parity evidence. Do not define an action from a
  hypothetical implementation.
- [ ] Audit every decorator, native-call projection kind, implicit call
  behavior, and generated module/class feature accepted by the live semantic
  model; reconcile the coverage matrix with that audit.
- [ ] Confirm the legacy generator's independent entrypoint and baseline tests;
  do not modify legacy lowering, nodes, generators, or printers in this phase.
- [ ] Update the maintained wrapper-plan contract with the audited Python
  surface, binding handoff, bridge ABI, native call, result, cleanup, writeback,
  node-construction, and printing phases.

### Phase 0B — Isolated Package Boundary

- [ ] Create the `x2py.wrapper_codegen` package skeleton without connecting it
  to production build selection.
- [ ] Define and enforce the package boundary: `x2py.wrapper_codegen` cannot
  import `x2py.codegen`, legacy `x2py.codegen` cannot import
  `x2py.wrapper_codegen`, and only pipeline orchestration may eventually import
  both route entrypoints.
- [ ] Add dependency tests for that boundary before copied backend code is
  introduced.
- [ ] Define the pipeline-owned generated-wrapper artifact result shared by both
  routes without duplicating native object/library/link-plan ownership.
- [ ] Keep runtime helper APIs shared only when their behavior is unchanged. Add
  separately named new-route helpers when different behavior is required, and
  record their generated callers and cleanup contract.
- [ ] Document that CPython reference counting and API ownership conventions are
  binding-emitter-local mechanics and are absent from plan models, rendered
  plans, and cross-backend plan validation.

### Phase 0C — Copied Scalar Backend Foundation

- [ ] Inventory the minimum dependency-closed set of scalar C/Fortran nodes,
  datatype/literal models, CPython and NumPy API primitives, scopes/naming
  behavior, helper concepts, and printer behavior required for Phase 1. Record
  each legacy source path and baseline test before copying it.
- [ ] Copy those primitives into `x2py.wrapper_codegen` without importing,
  aliasing, subclassing, or adapting legacy model classes.
- [ ] Keep each initial copy behaviorally equivalent to its legacy source before
  modifying it for plan emission.
- [ ] Add isolated node/printer tests proving representative scalar C source,
  C headers, and Fortran source render equivalently to the baseline.
- [ ] Verify the copied C/Fortran printers consume only isolated backend nodes
  and cannot import or inspect wrapper-plan models.

### Phase 0D — Wrapper Plan Core

- [ ] Define the first frozen plan data classes and tuple collections.
- [ ] Define `BridgeAbiPlan`, native-call refs, handoff specs, handler
  registries, and validation errors around existing completed
  `PythonBarrierAction` and `NativeBarrierAction` values. Do not add duplicate
  plan action enums for behavior already represented by completed policy.
- [ ] Add a plan validator that catches mismatched binding/bridge handoffs,
  missing bridge/native-call slots, unknown action handlers, duplicate symbolic
  roles, and writebacks/results that consume unavailable values.
- [ ] Define the whole-generation-unit support report, including stable
  owner-path reasons for unsupported elements, without changing production
  route selection yet.
- [ ] Define a small immutable plan-transformation API so maintainers can alter
  actions, ordering, or handoffs before validation without mutating the
  policy-completed semantic IR.
- [ ] Add deterministic plan rendering that includes symbolic owner paths,
  dispatch handler names, handoffs, bridge ABI slots, native slots, and
  lifecycle order without backend nodes or CPython-specific mechanics.
- [ ] Verify generated and maintainer-transformed plans pass through the same
  validator and produce owner-path diagnostics before node emission.

## Phase 1 — Scalar Function Inputs

Scope: free functions with scalar numeric/logical arguments that are
Python-visible inputs. Scalar call-target decorators and scalar native-call
argument projections are included as separate checklist items; unsupported
projection kinds keep the whole module on the legacy route.

### Phase 1A — Internal Plan Emission

- [ ] Generate plans for scalar value arguments such as `f(x: Float64)`.
- [ ] Represent Python argument position and `@native_call` native argument order
  explicitly, including reordered arguments.
- [ ] Represent implicit native order, `@bind(...)`, `@external`, and
  `@hold_gil` explicitly; none may be inferred or ignored by the emitters.
- [ ] Represent `Arg(...)`, `Addr(Arg(...))`, and typed numeric/logical hidden
  literals as native argument sources with exact native positions.
- [ ] Reject duplicate, missing, or out-of-range Python/native positions and
  bridge/native-call slots during plan validation.
- [ ] Add binding actions for scalar Python object to scalar value/storage.
- [ ] Add bridge actions for scalar pass-by-value, pass-by-address, and
  call-local address where already supported by completed policy.
- [ ] Validate binding-produced scalar handoffs against bridge expectations and
  the shared `BridgeAbiPlan`.
- [ ] Make each scalar binding/bridge handler return isolated node fragments;
  assemble complete C and Fortran module nodes outside individual handlers.
- [ ] Print complete scalar-only bridge source, C/CPython binding source/header,
  module initialization, and generated-source requirements through the isolated
  printers and artifact assembler.

### Phase 1B — Internal Compilation And Parity

- [ ] Provide test-only orchestration that sends the same eligible module
  directly through legacy and wrapper-plan routes without a public
  compatibility option or production selector change.
- [ ] Compile and import new-route scalar artifacts through the shared compiler
  and linker before making any production module eligible.
- [ ] Compare both routes for Python calls/results, native argument order,
  pass-by-value/address behavior, conversion failures, exception state,
  backend-local cleanup, generated artifact requirements, compilation, import,
  and runtime behavior.
- [ ] Resolve every unexplained parity difference or document a separately
  approved behavior correction before proceeding.

### Phase 1C — Production Route Integration

- [ ] Add one shared pipeline selector used by source-driven and semantic-`.pyi`-
  driven builds after policy completion and before any legacy
  `semantic_ir_to_codegen_ast()` call.
- [ ] Select the wrapper-plan route only for complete generation units whose
  recursively inspected elements are all covered by completed scalar-input
  actions, validators, emitters, printers, and parity evidence.
- [ ] Route a generation unit containing any unsupported element entirely
  through the existing path.
- [ ] Add route-selector tests proving one module cannot mix plan and legacy
  functions, bindings, bridges, nodes, or printers.
- [ ] Prove plan construction, validation, emission, printing, compilation, or
  linking failures do not silently retry the legacy route.
- [ ] Keep explicit internal selection of the legacy route available for
  rollback and dual-route tests.

## Phase 2 — Scalar Results And Hidden Outputs

Scope: scalar direct returns, hidden scalar outputs, and scalar projected
results.

- [ ] Audit and record the legacy result, hidden-output, result-packaging,
  `@raises`, cleanup, printer, and runtime paths that define this lane's
  baseline.
- [ ] Copy and baseline-test the additional result variables, CPython creation
  calls, C/Fortran statements, and printer behavior required by this lane.
- [ ] Represent direct native return, hidden output, identity output, and
  projected result lanes in `ResultPlan`.
- [ ] Add bridge actions for scalar result assignment and hidden scalar output
  storage without relying on `is_alias`.
- [ ] Add binding actions for scalar Python result creation.
- [ ] Validate that every Python result consumes a native result or writeback
  that the bridge produces.
- [ ] Cover `@raises` status/message outputs so runtime-status validation is
  represented in the plan, not rediscovered in binding.
- [ ] Emit and print complete result-capable C/Fortran modules internally, then
  compile and compare both routes for values, status/error paths, cleanup, ABI,
  and artifact requirements.
- [ ] Widen whole-module route eligibility to scalar results only after that
  parity evidence passes.

## Phase 3 — Scalar Inout, Optional, And Descriptor-Like Scalars

Scope: scalar copy-in/copy-out, optional arguments, present-but-null descriptor
values, and scalar allocatable/pointer descriptor boundaries.

- [ ] Audit and record the legacy copy-in/out, optional presence, nullable
  scalar descriptor, cleanup, and failure-path behavior for this lane.
- [ ] Copy and baseline-test the additional optional/descriptor nodes, API
  primitives, local-state helpers, and printer behavior required by this lane.
- [ ] Represent copy-in, native mutation, copy-out, and cleanup as explicit
  writeback phases.
- [ ] Preserve the three-state optional rule: omitted argument, explicit `None`,
  and present concrete value are distinct when the native ABI needs them.
- [ ] Represent scalar descriptor presence tokens and nullable value handoffs in
  the plan.
- [ ] Validate that a writeback consumes an existing binding/bridge handoff and
  writes to a Python-visible target or result slot.
- [ ] Emit and print complete inout/optional/descriptor-capable modules
  internally, then compile and compare both routes for all three presence
  states, mutation, writeback, cleanup, ABI, and failures.
- [ ] Widen whole-module route eligibility to this lane only after parity, and
  complete it before moving arrays or handles to the plan path.

## Phase 4 — Scalar Module Variables

Scope: scalar module variables. Derived-type fields remain in Phases 8 and 9
because their wrapper instance, owner, and property lifecycle must already be
represented before field access can use the plan route.

- [ ] Audit and record the legacy scalar module-variable getter, setter,
  rejected replacement, module initialization, and attribute-routing behavior.
- [ ] Copy and baseline-test the additional module/type nodes, getter/setter API
  primitives, initialization nodes, and printer behavior required by this lane.
- [ ] Represent getter behavior, setter exposure, native setter assignment, and
  rejected replacement behavior in module-variable plans.
- [ ] Add binding actions for Python attribute get/set around scalar values.
- [ ] Add bridge actions for scalar module-variable read/write.
- [ ] Validate getter/setter pair consistency: a Python setter cannot exist
  without a compatible bridge setter handoff.
- [ ] Keep ordinary Python module-name rebinding semantics separate from native
  module-variable storage.
- [ ] Emit and print complete module-variable-capable modules internally, then
  compile and compare both routes for get/set behavior, rejection paths,
  initialization, cleanup, ABI, and generated artifacts.
- [ ] Widen whole-module route eligibility to scalar module variables only after
  that parity evidence passes.

## Phase 5 — Strings

Scope: scalar character values, fixed-length strings, deferred-length strings,
and string copy/writeback.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate, separating at least value/storage, fixed/deferred length,
  input/result/inout, optionality, and ownership/lifetime cases found in the
  live contract.

- [ ] Define string handoff specs for value strings, storage strings, fixed
  length, deferred length, and mutable buffers.
- [ ] Add binding and bridge actions for string value input, string storage
  input, string result, and string writeback.
- [ ] Validate length/source expectations before emission.
- [ ] Keep string behavior separate from numeric scalar behavior even when both
  are rank-zero.

## Phase 6 — Ordinary Arrays

Scope: NumPy data-buffer arrays that do not require native descriptor handles.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate, separating at least input/result/inout, hidden outputs, rank/shape
  forms, dtype families, C/Fortran order and striding, optionality, copy versus
  view behavior, and writeability cases found in the live contract.

- [ ] Define array handoff specs for data pointer, dtype, rank, shape, strides,
  contiguity/order, itemsize, and writeability.
- [ ] Add binding actions for NumPy validation and data-buffer extraction.
- [ ] Add bridge actions for array data-buffer passing and shape/stride
  forwarding.
- [ ] Represent hidden array outputs and array copy-out/writeback explicitly.
- [ ] Validate dtype/rank/shape/order expectations in the plan before emitted C
  checks are generated.

## Phase 7 — Native Array Handles And Descriptors

Scope: `Allocatable[T[...]]`, `Pointer[T[...]]`, descriptor-backed handoffs, and
runtime native array handle objects.

- [ ] Before implementation, expand this phase under the mandatory expansion
  gate and reconcile it with the maintained native-array-handle checklist.
  Split allocatable and pointer behavior only after extracting their shared
  descriptor, presence, ownership, release, module/field, argument, and result
  sub-lanes.

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

## Phase 11 — Cutover And Removal

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
- [ ] Keep source printers only for the remaining generated source fragments they
  still own, or replace them with narrower emitters once the model layer is no
  longer needed.

## Verification

- [ ] Documentation-only changes run
  `python3 -m pytest -q tests/docs/test_examples.py tests/docs/test_structure.py`
  and `git diff --check`.
- [ ] Wrapper-plan code changes run focused plan validation tests, focused
  wrapper generation tests, and the required static-analysis suite from
  `AGENTS.md`.
- [ ] Runtime wrapper tests are required when generated behavior changes.
- [ ] Every migrated lane runs eligible fixtures through both routes. Compare
  behavior and ABI-relevant call mapping; do not require byte-identical source
  when mechanical organization differs.
- [ ] Structural dependency tests prove complete generator isolation: no
  imports from `x2py.wrapper_codegen` to `x2py.codegen` or in the reverse
  direction.
- [ ] LAPACK remains excluded from local verification unless separately
  authorized.

## Completion Record

- [ ] The final report for each lane names the plan actions added, the binding
  and bridge handlers they dispatch to, and the handoff specs validated.
- [ ] The final report lists old lowering/codegen paths still used by unsupported
  lanes.
- [ ] The final report includes focused verification commands and results.
- [ ] The final report includes the changed-stage breakdown required by
  `AGENTS.md` and names every test file added or updated with the behavior it
  covers.
