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
            -> mechanically project completed policy into wrapper plan
            -> validate wrapper plan structure and handoffs
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

The plan should be simple enough for maintainers to read and reproduce by hand.
The supported way to change generated behavior is to change the semantic
contract or completed policy and rebuild the plan, not to patch the plan or add
a backend exception. Validation must fail before any C or Fortran source is
emitted when a completed policy or its mechanically derived plan is
inconsistent.

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
- Recreate the minimum dependency-closed behavior needed by each lane inside the
  isolated generator. For each CPython/NumPy API model, C/Fortran node,
  datatype/literal, naming mechanism, or printer case, either copy a small
  already-suitable implementation or rewrite a smaller class containing only
  fields and methods the new emitters/printers use. These are independent
  implementations, not imports, aliases, subclasses, or adapters around legacy
  model classes.
- The legacy implementation is the behavioral source, not the required class
  design. Record the legacy origin, consumed fields, emitted source behavior,
  and parity evidence before simplifying. Do not preserve unused constructors,
  properties, inheritance, mutation APIs, lookup categories, or future-facing
  fields merely because the legacy class has them.
- Reuse the smallest coherent legacy method-body snippets and helper logic when
  they remain straightforward after switching to the validated plan and
  isolated context. When the legacy method depends on unrelated class state or
  abstractions, rewrite a smaller direct handler from the recorded behavior
  instead of copying that structure. Preserve observable call order, error
  handling, cleanup, and generated-call behavior either way.
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

### Legacy Replay Procedure

The working legacy pipeline makes this a reproduction exercise rather than a
greenfield generator project. Use it as an executable oracle every time a test
or semantic lane is migrated.

1. Select an existing passing `tests/wrapper` test and run its complete
   generation unit through the legacy route with generated artifacts retained.
2. Record the generated C binding source/header, Fortran bridge source,
   generated artifact names and requirements, native-call order, runtime
   behavior, and failure behavior relevant to the lane.
3. Trace those artifacts back through the current Python lowering, binding,
   bridge, node/API-model, printer, runtime-helper, and build-orchestration
   methods. Record the exact source methods and consumed state in this
   checklist before porting them.
4. Complete any semantic decisions exposed by that trace in post-IR policy.
   Do not move an old local decision into the planner or emitter merely because
   that is the quickest textual copy.
5. Copy a small proven implementation unchanged when all of it is needed, or
   rewrite the smallest independent equivalent when the old implementation
   carries unrelated state. Start from the old method bodies and generated
   artifacts; do not invent a replacement mechanism from memory.
6. Generate the same complete artifact set through the new plan route, inspect
   differences against the retained legacy artifacts, then compile and run the
   same existing assertions through both routes.

Generated source is diagnostic evidence, not necessarily a byte-for-byte
golden file. Equivalent backend-local names or mechanical formatting are
allowed, but every ABI, conversion, ownership, cleanup, call-order, and build-
artifact difference must be explained. When a parity failure occurs, rerun and
inspect the working legacy route before changing the new implementation.

Most wrapper tests share conversion, node, printer, and build mechanisms. Once
one mechanism has been reproduced and validated, later tests should reuse the
same new handler or primitive and add only their completed policy/plan mapping
or genuinely new mechanical behavior.

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

## Policy Authority And Planner Boundary

The wrapper planner receives policy-completed semantic owners and converts them
into a wrapper plan. It is not another policy stage.

```text
semantic contract + semantic datatype facts
  -> post-IR policy completion
       -> complete module/function/class/variable/argument/result policies
  -> WrapperPlanner.build(policy-completed module)
       -> frozen WrapperPlan
```

- Datatype states what an object is: scalar family, precision, rank, shape, or
  other representation facts. Completed policy states what wrapper generation
  must do: Python conversion action, bridge/native action, ownership, transfer,
  destruction, mutability/writeback, nullability, output projection, release,
  storage mode, getter/setter behavior, native-call order, and lifecycle order.
- The planner copies those completed decisions and datatype facts into readable
  plan records, assigns stable owner paths and symbolic references, and wires
  already-decided producers to consumers. It may traverse owners, preserve
  declared order, and build deterministic tuples and lookup references.
- The planner must not select an action, ownership mode, ABI behavior, call
  order, writeback, cleanup, result projection, or handler from datatype,
  `intent`, decorators, raw metadata, `is_alias`, dotted-variable shape, local
  memory checks, or a missing policy field. Such a branch means policy
  completion is incomplete and must be moved there.
- Planner complexity is presumed to indicate an incomplete policy boundary.
  A planner branch is allowed only for structural traversal or deterministic
  wiring that cannot change wrapper semantics. Any other exception requires a
  concrete reason recorded in this checklist before implementation and a
  focused test proving that it is structural rather than a hidden decision.
- Every runtime-visible or runtime-required owner must expose a complete typed
  policy before planning. If an argument, result, function, class, module
  variable, decorator effect, or native projection is still represented only
  by scattered facts that the planner would need to interpret, extend post-IR
  policy completion with a typed completed-policy record first.
- The plan retains the completed policy values or stable typed references to
  them so validation and rendering can show why each action was selected. Plan
  records must not use untyped `object` or free-form dictionaries for policy.
- Completed policy is the customization authority. A maintainer who wants
  different generated behavior changes the contract/policy, reruns post-IR
  policy completion when applicable, and rebuilds the plan. There is no direct
  plan-transformation API and no backend-specific customization path.
- The validator checks that the plan is a faithful and structurally consistent
  projection of completed policy. It diagnoses missing policy, unsupported
  completed actions, broken handoffs, and producer/consumer mismatches; it does
  not fill defaults or choose replacement behavior.

## Design Rules

- Post-IR policy completion decides semantic actions. The planner projects those
  decisions into the plan, and binding and bridge emitters consume them. None of
  these stages reconstruct policy from datatype, `intent`, `is_alias`, local
  memory handling, dotted-variable shape, or missing policy.
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
- Initial isolated handlers keep the current dispatch method names when practical,
  so a plan action can be traced directly to the audited legacy method. Add a
  new completed policy action in post-IR policy completion when no existing
  action expresses the required semantic step; never invent a plan-only action
  to avoid completing policy.
- Dispatch should be by semantic lane and action, not by every concrete dtype.
  For example, `Float64`, `Int32`, and `Bool` can share scalar-value handlers
  while dtype remains plan data.
- Every binding output that the bridge consumes is represented by a handoff
  spec in one end-to-end argument/result transfer record. Every bridge native
  argument/result that the native call consumes is represented in that same
  record and the function's `BridgeAbiPlan`/`NativeCallPlan`.
- Validation checks producer/consumer consistency before emission:
  the transfer's Python-side action must produce its handoff, its bridge ABI
  slot must consume that handoff, its native action must satisfy the native-call
  slot, and writeback/result plans must consume values actually produced.
- Keep one readable `ArgumentTransferPlan` for the complete Python argument -> C
  handoff -> bridge ABI -> native argument path. Do not force maintainers to
  join separate binding and bridge subplans. C and Fortran emitters remain
  separate implementations that consume different fields of the same transfer
  record.
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
- Add backend primitives incrementally by lane, not as a wholesale clone of the
  legacy codegen package. Each isolated slice includes only the dependency
  closure needed to generate and print that lane, so its representation can
  evolve without changing the legacy route.
- The binding and bridge emitters both consume the same validated plan. Their
  generated runtime data flow is Python binding -> bridge -> native call, but
  one emitter is not the semantic-policy input to the other.

### Hierarchical Plan Ownership

The plan mirrors semantic ownership. It is hierarchical rather than one flat
list and does not rely on one large planner method.

```text
WrapperPlan
  ModulePlan
    VariablePlan ...
    FunctionPlan
      ArgumentPlan -> ArgumentTransferPlan ...
      ResultPlan ...
      BridgeAbiPlan
      NativeCallPlan
      WritebackPlan/CleanupPlan ...
    ClassPlan
      ConstructorPlan ...
      MethodPlan ...
      PropertyPlan ...
      VariablePlan ...
```

- Create one frozen plan record for each runtime-visible or runtime-required
  semantic owner. The record carries its completed typed policy, datatype facts
  where applicable, stable owner path, and references to its child records.
- The module planner preserves declared member order and visits module
  variables, functions, and classes. The function planner visits arguments and
  results and assembles the already-completed call, ABI, writeback, cleanup, and
  projection records. The class planner does the same for constructors,
  methods, properties, and fields.
- Hidden native arguments/results, decorator projections, reordered native
  slots, and function-local lifecycle steps belong under their owning
  `FunctionPlan`. They are not detached module-level plan objects.
- Each planner visitor method returns one plan node. Only the owning parent
  assembles child nodes into ordered tuples; child visitors do not mutate a
  shared plan or inspect sibling backend output.
- Cross-level and cross-backend relationships use typed references or stable
  owner paths. Do not duplicate a child plan to make it available to both
  emitters.
- Owners that do not affect runtime wrapper generation may be absent only when
  the support analyzer explicitly classifies them as ignorable. An unsupported
  runtime owner selects the whole legacy route before planning.

### Visitor And Class Ownership

Tree traversal in the isolated generator is class-based and follows one
visitor protocol. Production behavior is owned by named classes and methods,
not a collection of module-level orchestration functions.

- Implement a minimal independent `wrapper_codegen.visitor.ClassVisitor` with
  deterministic MRO dispatch and a configurable method prefix. Audit the
  existing visitor algorithm as the behavioral source, but include only the
  behavior the isolated planner, validators, emitters, and printers need.
- `WrapperPlanner(ClassVisitor)` traverses policy-completed semantic owners with
  methods such as `_visit_SemanticModule`, `_visit_SemanticFunction`,
  `_visit_SemanticClass`, and `_visit_SemanticVariable`. These methods only
  copy completed policy/datatype facts and assemble deterministic plan records.
- `WrapperPlanSupportAnalyzer`, `WrapperPlanValidator`, and
  `WrapperPlanRenderer` use the same visitor protocol for semantic or plan-node
  traversal. The C binding and Fortran bridge emitters use visitors to assemble
  module/function/argument/result structure.
- Isolated printers use the same protocol with
  `visitor_method_prefix = "_print"` and explicit `_print_<Node>` methods.
  Unsupported node types fail through the visitor's explicit default path.
- Visitor dispatch answers "which model/node type is this?" Completed-action
  registries answer "which already-decided mechanical implementation runs?"
  Do not replace action registries with `isinstance` ladders inside visitor
  methods, and do not make visitor dispatch another policy selector.
- New production modules expose class APIs: `WrapperPlanner.build(...)`,
  `WrapperPlanSupportAnalyzer.analyze(...)`,
  `WrapperPlanValidator.validate(...)`, `WrapperPlanRenderer.render(...)`, and
  `WrapperCodeGenerator.generate(...)`. Do not add equivalent module-level
  builder, validator, renderer, support, emitter, printer, or generator
  functions.
- A module-level production function is permitted only when a concrete Python
  protocol or external entrypoint requires it and the reason is recorded in
  this checklist before implementation. Dataclasses, enums, constants, test
  functions, and a tool script's `main()` are not orchestration alternatives.
- Structural checks reject undeclared module-level functions in
  `x2py.wrapper_codegen` and reject top-level `isinstance`/`match` traversal
  ladders that bypass the visitor protocol.

### Dispatch Size And Splitting

- A primary emitter dispatcher is keyed by a completed action such as
  `SCALAR_VALUE` or `PASS_VALUE`. Its selected method should implement one
  understandable mechanical case and may delegate repeated node construction
  to small private helpers.
- If a selected method grows because scalar families genuinely use different
  APIs or generated control flow, add a visible secondary dispatcher keyed by
  an explicit backend datatype family such as logical, integer, real, or
  complex. Keep all precisions of a family together when precision changes only
  type data or a conversion-table entry.
- Split again by precision or concrete datatype only when the emitted API,
  range/error handling, declarations, or control flow actually differs. Do not
  create one handler per dtype merely to keep methods short.
- Handler registries and plan rendering expose the complete selected chain, for
  example `_convert_python_scalar_value_argument -> _convert_python_real_value`.
  Missing primary or secondary combinations fail validation/emission rather
  than falling back to a general method.
- When a method becomes difficult to follow, first separate independent phases
  such as declaration, conversion, call argument, and cleanup into node-fragment
  helpers. Use another dispatcher only when there is a real behavioral axis to
  dispatch on.

### Emitter Traceability And Complexity Gates

The repository-wide Ruff/Radon limits protect legacy code but are too permissive
for the new emitter contract. The general changed-block Radon limit is 20 and
the Ruff McCabe limit is 45; neither means a maintainer can reproduce an emitter
step easily. Add a stricter static checker for `x2py.wrapper_codegen` before the
first emitter handlers are implemented.

- Every registered primary handler, secondary handler, and private
  node-fragment helper in `c/binding.py` or `fortran/bridge.py` has Radon
  cyclomatic complexity at most 5 (grade A), at most 25 statements, and control-
  flow nesting depth at most 2.
- Every `WrapperPlanner` visitor method has the same complexity, statement, and
  nesting limits. It may use an explicit completed-policy variant only to
  choose the corresponding plan-record shape. It may not dispatch on datatype,
  decorators, or raw metadata to derive behavior; completed policy already
  contains the selected actions and ordering.
- A registered handler accepts one validated transfer/result plan plus an
  explicit backend emission context and returns an `EmissionFragment`. It must
  not require a maintainer to recreate hidden mutable emitter state before
  calling it in a focused test.
- Module/function assemblers and the top-level artifact orchestrator may have
  cyclomatic complexity at most 10 and at most 50 statements because they
  combine already-selected fragments; they may not perform policy or datatype
  dispatch.
- New node, API-model, naming, and context methods are also kept at Radon
  complexity at most 5 and contain only behavior required by current migrated
  lanes. Copied printer methods may remain outside the stricter handler limit
  when preserving complex legacy formatting; they remain subject to the
  repository Radon non-regression policy and baseline rendering tests.
- Do not add a permanent complexity allowlist for a registered emitter handler.
  A copied legacy handler that exceeds a limit may exist during isolated
  baseline work, but the new route cannot become eligible for that action until
  the handler is split and passes the strict gate.
- Complexity is a trigger for review, not an instruction to add a dispatcher
  blindly. If complexity comes from independent emission phases, extract small
  fragment helpers. If it comes from different datatype-family behavior, add a
  secondary family dispatcher. If precision only selects a type/API table
  value, keep one family handler and use data rather than another dispatcher.
- The checker also verifies that every registry target exists, every registered
  handler is measured, no handler calls a printer, and every secondary
  dispatcher has a total explicit mapping for the supported plan combinations.
  It also enforces the declared module-level-function and visitor rules for the
  isolated package.
- Plan rendering resolves and prints the full primary/secondary handler chain.
  Registry checks verify that every rendered handler exists and is covered by a
  supported plan combination. Compiled parity through existing wrapper tests is
  the default behavioral proof; direct handler tests are reserved for
  mechanical failures that existing fixtures cannot isolate.

Implement this as a dedicated checker such as
`python3 tools/check_wrapper_codegen_complexity.py`. It may reuse Radon's
`cc_visit` and the repository's existing Radon helper code, while adding AST-
based statement count, nesting, registry, and forbidden-printer-call checks.
Run it as a blocking static check for every wrapper-codegen implementation
change.

## Intended Ownership And Files

The exact names may evolve during Phase 0, but responsibilities should remain
separated along these lines:

```text
x2py/wrapper_codegen/
  visitor.py        minimal independent class visitor used by isolated models
  names.py          minimal deterministic NameAllocator; no legacy Scope copy
  types.py          minimal datatype/literal nodes needed by migrated lanes

  plan/
    models.py       frozen readable plan records
    specs.py        handoff, bridge-ABI, native-slot, and structural specs
    build.py        WrapperPlanner visitor: completed policy -> WrapperPlan
    validate.py     WrapperPlanValidator visitor
    support.py      WrapperPlanSupportAnalyzer visitor and route report
    render.py       WrapperPlanRenderer visitor

  c/
    nodes.py        minimal C declarations/statements needed by migrated lanes
    cpython_api.py  minimal CPython API nodes needed by migrated lanes
    numpy_api.py    minimal NumPy C API nodes needed by migrated lanes
    concepts.py     minimal C/CPython helper nodes needed by migrated lanes
    context.py      module/function names, local values, and cleanup state
    binding.py      CPythonBindingEmitter visitor
    printer.py      CPythonCodePrinter visitor with _print_<Node> methods

  fortran/
    nodes.py        minimal Fortran declarations/statements needed by lanes
    context.py      module/function names and local values
    bridge.py       FortranBridgeEmitter visitor
    printer.py      FCodePrinter visitor with _print_<Node> methods

  generate.py      WrapperCodeGenerator class and artifact orchestration
  artifacts.py     complete new-route generated-wrapper artifact result

x2py/pipeline/
  shared route selection and compile/link orchestration
```

This is a permanent responsibility-based package name, not a temporary
`new_codegen` package that would need another migration after cutover. Files
under `c/` and `fortran/` are added only as a migrated lane needs them; the
layout does not authorize copying the entire legacy package up front.

Within the generation boundary there is no shared model identity between the
routes. If a migrated handler needs behavior currently provided by a legacy
`Variable`, datatype, literal, API model, scope, or printer-dispatch base, audit
which parts are actually consumed and implement the smallest independent class
that reproduces those parts. Copy a class unchanged only when it is already
small and all of it is required.

### Naming Without Legacy Scope

Do not copy the general legacy `Scope`. The wrapper plan already resolves
public names, native names, bridge symbols, argument positions, and ABI slots;
the new backend only needs deterministic collision-free names for generated
modules, functions, and local temporaries.

- `NameAllocator` owns `reserve(name)` and `new_name(base)` with deterministic
  suffixing. It does not store semantic variables, classes, decorators,
  symbolic aliases, loops, dotted symbols, imports, or original-name lookup.
- A C or Fortran module emission context owns one module-level allocator for
  generated functions, module objects, helper symbols, and public/ABI names
  reserved from the validated plan.
- Each emitted function receives an explicit function context with its own
  local allocator for arguments, result storage, temporaries, and cleanup
  values. It may reserve module symbols but does not search a parent semantic
  scope.
- Later class support may add a class emission context only when Phase 9 proves
  it is needed. Do not add class/loop/program scope categories during scalar
  phases.
- Public and ABI names come from the plan and cannot be renamed by the backend
  allocator. The allocator handles only backend-local collisions.
- Focused naming tests copy the relevant legacy collision cases and prove stable
  names across repeated generation, but the new allocator API and internal data
  structures remain minimal.

`ir2ast.py` remains the entry to the temporary legacy route; it must not choose
the route or partially invoke the new emitters. The source-driven and `.pyi`-
driven build entrypoints should call one shared orchestration helper rather
than implement different support rules.

The two routes should return one pipeline-owned internal generated-artifact
result shape so the existing compiler/link orchestration does not need to
understand plan actions. That result is an internal build handoff, not a
compatibility API and not a second semantic model.

The isolated C and Fortran layers are thin mechanical backend layers. For each
primitive, preserve the proven legacy behavior and tests needed by the lane
while choosing the smallest new representation that can express it. The
original node, printer, scope, and generator implementations remain untouched
and runnable. Shared compilation receives generated files through the artifact
result and does not import either route's internal models.

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
- Preserve the legacy high-level pattern in isolated form:
  `WrapperCodeGenerator.generate(plan)` constructs complete `fortran_module`
  and `c_module` objects, then passes them to isolated
  `FCodePrinter.doprint(...)` and `CPythonCodePrinter.doprint(...)`
  implementations. Preserve this orchestration and the required module/header
  behavior from legacy codegen rather than inventing a second source-writing
  mechanism.
- Do not copy the legacy sequential dependency where the binding generator
  learns its ABI by consuming the bridge generator's AST. In the new route,
  both complete module trees are independently constructed from the same
  validated `WrapperPlan` and `BridgeAbiPlan`.
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
  the baseline nodes before plan emitters use them. Each isolated printer
  implements only the `_print_<Node>` cases required by currently migrated
  nodes and fails explicitly for unsupported node types; do not copy unused
  printer methods in anticipation of later lanes.
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
    owner_path: OwnerPath
    policy: CompletedModulePolicy
    functions: tuple[FunctionPlan, ...]
    variables: tuple[VariablePlan, ...]
    classes: tuple[ClassPlan, ...]


@dataclass(frozen=True)
class FunctionPlan:
    public_name: str
    native_name: str
    owner_path: OwnerPath
    policy: CompletedFunctionPolicy
    python_arguments: tuple[ArgumentPlan, ...]
    bridge_abi: BridgeAbiPlan
    native_call: NativeCallPlan
    results: tuple[ResultPlan, ...]
    writebacks: tuple[WritebackPlan, ...]


@dataclass(frozen=True)
class ArgumentPlan:
    public_name: str
    owner_path: OwnerPath
    datatype: SemanticType
    policy: OwnershipDecision
    python_position: int | None
    transfer: ArgumentTransferPlan
    writeback: WritebackPlan | None = None


@dataclass(frozen=True)
class ArgumentTransferPlan:
    python_action: PythonBarrierAction
    handoff: HandoffSpec
    bridge_slot: BridgeArgumentRef
    native_action: NativeBarrierAction
    native_slot: NativeArgumentRef


@dataclass(frozen=True)
class NativeCallPlan:
    native_name: str
    arguments: tuple[NativeArgumentRef, ...]
    results: tuple[NativeResultRef, ...]
```

The plan validator owns consistency diagnostics. Binding and bridge emitters
should be able to trust a validated plan and focus on emitted-code mechanics.
`CompletedModulePolicy` and `CompletedFunctionPolicy` stand for typed post-IR
policy records, not plan-owned decisions. Phase 0D must replace these sketch
names with the actual completed semantic policy types and define equivalent
typed policy fields for results, variables, and classes before those owners are
migrated. If policy completion cannot provide such a record, that semantic
stage must be completed before the corresponding planner visitor is written.

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

The exact class-owned call path should be equally direct:

```text
completed = complete_semantic_policies(module)  existing semantic stage
plan = WrapperPlanner().build(completed[0])     completed policy -> WrapperPlan
WrapperPlanValidator().validate(plan)           structural consistency only
WrapperCodeGenerator().generate(plan)
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

`WrapperPlanner._visit_SemanticFunction(f)` visits `x`, copies its `Float64`
datatype and completed `SCALAR_VALUE`/`PASS_VALUE` policy actions, and wires the
pre-decided positions into `ArgumentTransferPlan`. It does not decide that a
`Float64` should use those actions. A different valid completed policy produces
a different plan through the same visitor without changing planner or emitter
code.

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

## Existing Wrapper Suite As The Migration Queue

`tests/wrapper` is the behavioral source and final acceptance suite for this
migration. Migrate its existing generation units one by one; do not create a
parallel wrapper suite or new native source fixtures merely to make the new
route easier to exercise.

- Phase 0A adds a maintained migration matrix to this file covering every
  Python test node under `tests/wrapper`. Each row records whether the test
  generates a wrapper, the source/contract generation unit it uses, the lanes
  that currently block the wrapper-plan route, and one status:
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
`semantic_ir_to_codegen_ast()` route, `not-applicable` does not generate a
runtime wrapper, and `deferred-real-library` is reserved for the full BLAS and
LAPACK corpus until Phase 12.

| Pytest selector | Generation unit | Blocking lanes | Status |
| --- | --- | --- | --- |
| `tests/wrapper/fortran/arrays/test_array_contracts.py::*` | source/generated-.pyi parity or parametrized route | ordinary arrays | `legacy` |
| `tests/wrapper/fortran/arrays/test_array_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/arrays/test_array_results.py::*` | source/generated-.pyi parity or parametrized route | ordinary arrays; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/arrays/test_assumed_rank_arrays.py::*` | source/generated-.pyi parity or parametrized route | ordinary arrays | `legacy` |
| `tests/wrapper/fortran/arrays/test_bind_c_array_type.py::*` | non-generating: legacy model/printer/policy unit coverage | legacy model/printer mechanics; ordinary arrays; native handles/descriptors | `not-applicable` |
| `tests/wrapper/fortran/arrays/test_multidimensional_arrays.py::*` | source/generated-.pyi parity or parametrized route | ordinary arrays | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_init_entry_uses_resolved_parent_name_from_inside_package` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_output_name_override_replaces_entry_inference` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_recursive_graph_preserves_module_and_symbol_aliases_and_ignores_support_imports` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_recursive_graph_reports_cycles_before_codegen` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_recursive_graph_reports_missing_relative_contract_before_native_validation` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_contract_package_runtime.py::test_source_build_preserves_modules_and_root_externals` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_entry_can_alias_one_module_procedure_at_the_root` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_entry_rejects_colliding_wildcard_exports` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_entry_wildcard_import_explicitly_flattens_module_leaf` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_generated_pyi_fixture_builds_from_native_object_without_source_reparse` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_generated_pyi_matches_checked_in_fixture` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_mixed_entry_exposes_externals_at_root_and_modules_as_children` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_module_leaf_can_be_the_entry_contract` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_module_variable_runtime_contract[*]` | source/generated-.pyi parity or parametrized route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_mutable_module_variable_default_initializes_native_storage` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_one_entry_preserves_multiple_native_module_namespaces` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_cli_accepts_exactly_one_entry_contract` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_cli_preserves_explicit_ordered_link_items` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_cli_requires_a_native_link_input` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_makefile_manifest_and_replay_workflows` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_manifest_records_pointer_descriptor_interop_requirements` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_accepts_exactly_one_entry_contract` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_a_missing_native_artifact` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_invalid_address_contracts_before_codegen[*]` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_invalid_projection_before_codegen` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_pyi_python_api_rejects_python_suffix_as_semantic_contract` | non-generating: validation/failure-path assertion | semantic .pyi generation/parsing; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_reduced_entry_generates_only_reachable_module_variable_bindings` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_scale_runtime_contract[*]` | source/generated-.pyi parity or parametrized route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_pyi/test_pyi_wrapper_builds.py::test_source_named_root_discovers_and_builds_module_leaf` | direct wrapper/build route | semantic .pyi generation/parsing; build/compile/link orchestration; scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_compile_object_dependency_modules_keep_caller_order` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_fortran_wrapper_default_module_name_does_not_collide_with_root_function` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_fortran_wrapper_default_places_extension_beside_source` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_fortran_wrapper_out_names_importable_shared_library` | direct wrapper/build route | build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_internal_preprocessing_mode_still_builds_importable_runtime_wrapper` | direct wrapper/build route | build/compile/link orchestration; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_native_link_plan_serializes_interleaved_item_kinds` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_source_build_result_records_structured_native_plan` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_verbose_mode_prints_custom_wrapper_flags` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/build_from_source/test_build_modes.py::test_verbose_mode_prints_full_direct_build_commands` | direct wrapper/build route | build/compile/link orchestration | `legacy` |
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
| `tests/wrapper/fortran/edit_pyi_contracts/test_native_order_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; native-call projections | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_ownership_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py::test_contradictory_ownership_contract_fails_before_bridge_generation` | non-generating: policy validation before bridge generation | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `not-applicable` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py::test_immutable_array_policy_copies_in_and_returns_replacement` | direct wrapper/build route | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_policy_dispatch_contracts.py::test_immutable_scalar_string_array_and_derived_policies_return_replacements` | direct wrapper/build route | semantic .pyi generation/parsing; native handles/descriptors; derived types/snapshots; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_surface_edit_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; classes/methods/properties/overloads; naming/visibility/dispatch | `legacy` |
| `tests/wrapper/fortran/edit_pyi_contracts/test_visibility_contracts.py::*` | direct wrapper/build route | semantic .pyi generation/parsing; classes/methods/properties/overloads; naming/visibility/dispatch | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_compact_blas_like_folder_generates_one_external_entry_and_preserves_separate_objects` | direct wrapper/build route | external symbols/native linkage; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_external_bind_renames_python_export_without_changing_native_call` | direct wrapper/build route | external symbols/native linkage; naming/visibility/dispatch | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_external_bridge_uses_explicit_interface_and_no_module_use` | direct wrapper/build route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_fixed_form_standalone_external_runtime_parity[*]` | source/generated-.pyi parity or parametrized route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_free_form_standalone_external_runtime_parity[*]` | source/generated-.pyi parity or parametrized route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_generated_external_contracts_are_non_empty_root_fragments` | direct wrapper/build route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_handwritten_c_order_flat_contract_passes_rank_preserving_bridge_view` | direct wrapper/build route | external symbols/native linkage; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_module_procedure_bridge_uses_native_module_scope` | direct wrapper/build route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_namespace_imported_module_rejects_external_marker_before_codegen` | non-generating: validation/failure-path assertion | external symbols/native linkage | `not-applicable` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_one_source_with_several_standalone_externals_exports_each_at_root[*]` | source/generated-.pyi parity or parametrized route | external symbols/native linkage | `legacy` |
| `tests/wrapper/fortran/external_routines/test_external_procedures.py::test_package_entry_rejects_non_external_root_declaration_before_codegen` | non-generating: validation/failure-path assertion | external symbols/native linkage | `not-applicable` |
| `tests/wrapper/fortran/function_calls/test_function_call_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/function_calls/test_native_call_examples.py::test_native_call_examples_build_from_generated_pyi_and_native_shared_library` | direct wrapper/build route | native-call projections; ordinary arrays; strings; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/function_calls/test_native_call_examples.py::test_native_call_examples_cover_scalar_array_string_and_object_projection[*]` | source/generated-.pyi parity or parametrized route | native-call projections; ordinary arrays; strings; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_fixed_form_optional_arguments_drive_fortran_present_behavior[*]` | source/generated-.pyi parity or parametrized route | optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_allocatable_scalar_descriptor_distinguishes_omitted_none_and_value` | direct wrapper/build route | optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/function_calls/test_optional_arguments.py::test_optional_arguments_drive_fortran_present_behavior[*]` | source/generated-.pyi parity or parametrized route | optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/function_calls/test_output_arguments.py::*` | source/generated-.pyi parity or parametrized route | scalar inputs/results; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/layout_rules/test_wrapper_guide_layout.py::*` | non-generating: wrapper docs/test layout | test/docs layout | `not-applicable` |
| `tests/wrapper/fortran/module_state/test_allocatable_replacement.py::*` | source/generated-.pyi parity or parametrized route | module variables/state; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/module_state/test_allocatable_views.py::*` | source/generated-.pyi parity or parametrized route | module variables/state; native handles/descriptors | `legacy` |
| `tests/wrapper/fortran/module_state/test_common_blocks.py::*` | source/generated-.pyi parity or parametrized route | module variables/state | `legacy` |
| `tests/wrapper/fortran/module_state/test_module_state.py::test_aliased_derived_module_object_borrows_native_state[*]` | source/generated-.pyi parity or parametrized route | module variables/state; derived types/snapshots | `legacy` |
| `tests/wrapper/fortran/module_state/test_module_state.py::test_scalar_module_variables_use_attributes_and_parameters_have_no_native_setter[*]` | source/generated-.pyi parity or parametrized route | module variables/state | `legacy` |
| `tests/wrapper/fortran/module_state/test_module_state_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_makefile_mode_reproduces_multi_source_build` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_file_modules_build_one_merged_extension` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_file_standalone_procedures_build_one_merged_extension` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_source_generated_contract_build_matches_source_runtime_and_link_order` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state; semantic .pyi generation/parsing | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_source_modified_entry_preserves_modules_and_adds_documented_alias` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state | `legacy` |
| `tests/wrapper/fortran/multiple_files/test_multi_source_builds.py::test_multi_source_pyi_out_writes_one_flat_combined_package` | direct wrapper/build route | build/compile/link orchestration; external symbols/native linkage; module variables/state; semantic .pyi generation/parsing | `legacy` |
| `tests/wrapper/fortran/naming/test_defined_operators.py::*` | source/generated-.pyi parity or parametrized route | naming/visibility/dispatch; classes/methods/properties/overloads; operators; generic dispatch | `legacy` |
| `tests/wrapper/fortran/naming/test_generic_interfaces.py::*` | source/generated-.pyi parity or parametrized route | naming/visibility/dispatch; classes/methods/properties/overloads; generic dispatch | `legacy` |
| `tests/wrapper/fortran/naming/test_naming_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/naming/test_visibility_naming.py::test_strict_wrapper_names_reject_python_name_fixes` | direct wrapper/build route | naming/visibility/dispatch; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/naming/test_visibility_naming.py::test_visibility_and_default_python_name_fixing_policy[*]` | source/generated-.pyi parity or parametrized route | naming/visibility/dispatch; classes/methods/properties/overloads | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_real_blas_lapack.py::*` | full BLAS/LAPACK wrapper generation unit | external symbols/native linkage; build/compile/link orchestration; broad wrapper corpus | `deferred-real-library` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_duplicate_native_definitions_report_linker_error` | direct wrapper/build route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_imported_contracts_resolve_from_one_archive_or_shared_library[*]` | source/generated-.pyi parity or parametrized route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_incompatible_native_artifact_reports_linker_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_missing_module_directory_reports_compile_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_missing_symbol_reports_native_link_or_loader_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_mixed_module_external_bundle_resolves_all_native_input_kinds` | direct wrapper/build route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_required_transitive_named_library_resolves_runtime_symbol` | direct wrapper/build route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_static_archive_dependency_order_resolves_transitive_library` | direct wrapper/build route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_static_archive_groups_resolve_cyclic_archive_dependencies` | direct wrapper/build route | external symbols/native linkage; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/real_libraries/test_stage7_native_bundles.py::test_unavailable_dependent_shared_library_reports_loader_error` | non-generating: validation/failure-path assertion | external symbols/native linkage; build/compile/link orchestration | `not-applicable` |
| `tests/wrapper/fortran/runtime_behavior/test_openmp_runtime.py::*` | direct wrapper/build route | runtime policies/errors/GIL; build/compile/link orchestration | `legacy` |
| `tests/wrapper/fortran/runtime_behavior/test_runtime_behavior_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/runtime_behavior/test_runtime_policies.py::*` | direct wrapper/build route | runtime policies/errors/GIL | `legacy` |
| `tests/wrapper/fortran/runtime_behavior/test_runtime_recursion.py::*` | source/generated-.pyi parity or parametrized route | runtime policies/errors/GIL; scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/scalars/test_fortran_enums.py::test_fortran_enums_preserve_integer_runtime_surface[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/scalars/test_fortran_enums.py::test_fortran_enums_preserve_values_in_generated_pyi_contract` | direct wrapper/build route | scalar inputs/results; module variables/state | `legacy` |
| `tests/wrapper/fortran/scalars/test_scalar_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |
| `tests/wrapper/fortran/scalars/test_scalar_kinds.py::*` | source/generated-.pyi parity or parametrized route | scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/scalars/test_value_and_bind_c.py::*` | source/generated-.pyi parity or parametrized route | scalar inputs/results; native-call projections | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_f90_array_wrapper_distinguishes_contiguous_and_strided_contracts[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_f90_wrapper_pipeline_builds_importable_extension[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_fortran_array_wrapper_pipeline_matches_fmath_results_with_contiguous_arrays[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results; ordinary arrays | `legacy` |
| `tests/wrapper/fortran/scalars/test_verified_baseline.py::test_fortran_wrapper_pipeline_builds_importable_extension[*]` | source/generated-.pyi parity or parametrized route | scalar inputs/results | `legacy` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_edited_modern_string_contract_wraps_full_axis_spelling_set` | direct wrapper/build route | strings | `legacy` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_legacy_fortran_character_arguments_and_results[*]` | source/generated-.pyi parity or parametrized route | strings | `legacy` |
| `tests/wrapper/fortran/strings/test_character_arguments.py::test_modern_fortran_character_arguments_and_results[*]` | source/generated-.pyi parity or parametrized route | strings | `legacy` |
| `tests/wrapper/fortran/strings/test_character_edge_cases.py::*` | source/generated-.pyi parity or parametrized route | strings; optional/presence/writeback | `legacy` |
| `tests/wrapper/fortran/strings/test_string_generated_pyi_contracts.py::*` | non-generating: generated semantic .pyi fixture parity | semantic .pyi generation/parsing | `not-applicable` |

### Phase 0A Current Scalar Baseline

The first migration baseline is
`tests/wrapper/fortran/scalars/test_verified_baseline.py::test_fortran_wrapper_pipeline_builds_importable_extension[*]`.
It is the smallest existing runtime generation unit that directly covers the
initial scalar lane without arrays, strings, module variables, classes, hidden
native outputs, native result projections, or build-bundle behavior. Its
callables do use the current scalar `@bind(...)`, `@external`, and
`@native_call([Addr(Arg(...))])` contract, so the first scalar lane must treat
bind names, external status, scalar address projection, native-call slot order,
and scalar result ownership as completed post-IR policy.

That unit must remain atomic:

- Source mode builds the current source fixture named by `SCALAR_LEGACY_SOURCE`
  through the normal source wrapper route.
- Generated-`.pyi` mode first checks the generated semantic contract fixture at
  `tests/wrapper/fortran/scalars/contracts/fmath`, compiles the native object,
  then builds the same runtime wrapper surface from the checked contract.
- Both modes assert the same public runtime behavior through
  `_assert_fmath_examples(...)`: lower-case scalar functions accept scalar
  Python/NumPy values and return scalar Python/NumPy-compatible results for
  real, integer, complex, and logical families.
- The expected generated artifact set is
  `bind_c_fmath_wrapper.f90`, `fmath_wrapper.c`, and `fmath_wrapper.h`, plus
  shared runtime support installed by the compilation pipeline.

This fixture is not Phase 1-only. The Python arguments are scalar value inputs,
but every callable also has a scalar result. The whole generation unit cannot
move to `dual-route` until Phase 1 scalar inputs and Phase 2 scalar result
projection are both represented, validated, emitted, compiled, and compared
against the legacy route.

#### Current scalar route inventory

| Current behavior or path | Legacy source owner | Proposed wrapper-plan record/action | Required backend behavior | Baseline evidence |
| --- | --- | --- | --- | --- |
| Complete source or generated-`.pyi` semantic module before runtime generation | `x2py/pipeline/build.py`, `x2py/pipeline/pyi.py`, `x2py/semantics/policy_completion.py`, `x2py/semantics/readiness.py` | Route selector receives one policy-completed generation unit | No route selection before policy completion and readiness-owned blockers | `test_fortran_wrapper_pipeline_builds_importable_extension[*]` |
| Lower policy-completed semantic functions to the current codegen AST | `x2py/semantics/ir2ast.py::semantic_ir_to_codegen_ast` | `WrapperPlanner` copies completed module/function/argument/result policy into `ModulePlan`, `FunctionPlan`, `ArgumentTransferPlan`, and later `ResultPlan` | Planner must not infer scalar behavior from datatype or intent | same scalar fixture plus Phase 0C policy tests |
| Python scalar argument conversion dispatches from completed policy | `x2py/codegen/bindings/c_to_python.py::CPythonBindingGenerator._PYTHON_BARRIER_DISPATCHER`; `_convert_python_scalar_value_argument` | `ArgumentTransferPlan.python_action = PythonBarrierAction.SCALAR_VALUE` | Isolated binding handler keeps the audited scalar-value conversion behavior and records the binding-to-bridge value handoff | same scalar fixture |
| Bridge scalar address-projected argument dispatches from completed policy | `x2py/codegen/bridges/fortran_to_c.py::FortranToCBridgeGenerator._NATIVE_BARRIER_DISPATCHER`; `_convert_native_call_local_address_argument` | `ArgumentTransferPlan.native_action = NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS` and bridge ABI call-local address slot | Isolated bridge handler passes the address of call-local scalar storage into the native call without storage/writeback policy inference | same scalar fixture |
| Scalar native call uses completed `@native_call([Addr(Arg(...))])` order | `FortranToCBridgeGenerator._visit_FunctionDef` after `_convert_function_arguments(...)` and native projection lowering | `NativeCallPlan` with deterministic native slots copied from completed scalar native-call slot policy | Validator rejects duplicate, missing, or reordered slots not justified by completed policy | same scalar fixture; hidden/native-only projections remain later lanes |
| Scalar result is returned to Python | legacy bridge result conversion and `CPythonBindingGenerator` result wrapping paths | Phase 2 `ResultPlan` and Python result projection action | Result creation consumes a produced native result; Phase 1 must not fake this as input support | same scalar fixture; Phase 2 expansion owns details |
| Generate bridge and binding source/header artifacts | `x2py/codegen/binding_pipeline.py::BindingPipeline.generate` and `BindingPipeline.write`; `FCodePrinter`; `CPythonCodePrinter` | Phase 0E/1A isolated module/header assembly and printers | New route emits complete Fortran bridge, C binding source, C header, additional imports, and runtime requirements before compilation | expected artifact names asserted by the scalar fixture |
| Compile and link the importable extension | `x2py/compiling/python_wrapper.py::create_shared_library` | Shared generated-wrapper artifact handoff reused by both routes | Compilation/link orchestration stays shared; no new route-specific build policy in emitters | existing wrapper build assertions |

#### Decorator and feature audit reconciliation

The live wrapper suite currently covers direct scalar calls, `@bind(...)`,
`@external`, `@hold_gil`, `@native_call` argument and result projections,
typed hidden literals, `@raises(...)`, optional and presence-token behavior,
strings, ordinary arrays, native array handles/descriptors, module variables,
derived types, snapshots, constructors, methods, properties, overloads,
generic dispatch, visibility/naming policy, callbacks, multiple-source builds,
semantic-`.pyi` replay, native bundles, and full BLAS/LAPACK real-library
corpora. The migration matrix above reconciles those features to the broad
lanes in the existing phase order.

No accepted decorator or native projection is considered migrated by this
audit. Rows remain `legacy` unless their complete generation unit has passed
the required dual-route parity evidence. The full BLAS/LAPACK corpus remains
`deferred-real-library`; general native-bundle tests stay active and legacy
because they cover shared build mechanics independently of the full real
library corpus.

#### Maintained first-lane wrapper-plan contract

For the selected scalar baseline, the planned records must expose these phases
without backend policy inference:

- Python surface: one `FunctionPlan` per public scalar function, lower-case
  Python name, ordered Python scalar value arguments, and one scalar result.
- Binding handoff: each scalar argument has one `ArgumentTransferPlan` using
  `PythonBarrierAction.SCALAR_VALUE`, the existing scalar value conversion
  behavior, and one symbolic value handoff to the bridge.
- Bridge ABI: each transfer consumes that value handoff through the completed
  scalar native action. The selected scalar fixture uses
  `NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS` because every argument is
  address-projected with `Addr(Arg(...))`.
- Native call: each scalar function has completed native-call slots copied from
  `@native_call([Addr(Arg(...))])`, including native position, Python argument
  position, Python/native names, value kind, and the native barrier action.
  Implicit declared-order scalar calls may use the same policy shape, but they
  are not required for the selected baseline evidence.
- Result projection: scalar native results are represented only in Phase 2
  records; Phase 1 planning may record that the selected baseline is blocked
  by scalar result support but must not emit an incomplete runtime wrapper.
- Cleanup and writeback: scalar value inputs have no writeback, destructor, or
  ownership transfer phase. Backend-local error cleanup remains private to the
  binding/bridge implementation methods and is not a plan policy decision.
- Node construction and printing: Phase 0E may reuse or rewrite only the
  dependency-closed legacy node, header/source assembly, printer, and helper
  behavior required by the scalar baseline. It must not import, alias,
  subclass, or adapt legacy codegen model classes in `x2py.wrapper_codegen`.
- Legacy entrypoint: the independent baseline entrypoint is the existing
  `semantic_ir_to_codegen_ast()` route into `BindingPipeline` and
  `create_shared_library()`. Phase 0A records it only; it does not modify
  legacy lowering, nodes, generators, printers, or compilation.

### Phase 0B Isolated Package Contract

Phase 0B introduces infrastructure only. It does not add a route selector,
planner, backend nodes, emitters, printers, compilation, or production
wrapper-plan entrypoint.

The implemented package boundary is:

- `x2py.wrapper_codegen` is an isolated package. It may depend on stable Python
  infrastructure and shared semantic/pipeline value objects when needed later,
  but it must not import `x2py.codegen`.
- Legacy `x2py.codegen` must not import `x2py.wrapper_codegen`.
- A source module that imports both route families must live under
  `x2py.pipeline`, because route selection and shared orchestration belong
  there. No current production module imports both.
- The package currently exports only its independent `ClassVisitor` protocol
  and unsupported-node error. Production wrapper builds do not import the
  package.

The independent visitor contract is intentionally smaller than the legacy
utility visitor:

- dispatch is through `visit(node, ...)`;
- handler names are deterministic `<prefix>_<ClassName>` lookups over the
  node class MRO;
- the default prefix is `_visit`, with an instance-level override for renderer
  or emitter protocols;
- missing support raises `UnsupportedWrapperCodegenNodeError` with the visitor
  type, node type, and prefix.

The blocking `x2py.wrapper_codegen.checks` package checker enforces Phase 0B
static contracts before any emitter handlers exist:

- wrapper-codegen production modules must not import `x2py.codegen`;
- production module-level functions are rejected so generation behavior stays
  on owning classes;
- production `Analyzer`, `Emitter`, `Planner`, `Renderer`, and `Validator`
  classes must inherit `ClassVisitor`;
- each function/method must stay within the wrapper-codegen complexity,
  statement-count, and nesting limits;
- class-level `*_REGISTRY`, `*_DISPATCHER`, and `*_HANDLERS` mappings that
  name handler methods must point at methods on the same class, including
  nested secondary dispatch dictionaries;
- registered handlers and handler-like methods may not call source printers
  directly through `doprint(...)` or `write(...)`.

The pipeline-owned generated-wrapper handoff is
`x2py.pipeline.wrapper_artifacts.GeneratedWrapperArtifacts`. It records only
generated wrapper source files, generated headers, the generated module name,
and runtime-support requirement keys. Native source objects, prebuilt native
artifacts, libraries, include directories, library directories, link order, and
compile/link execution remain owned by the existing build plan and compiler
orchestration.

No new runtime helper API is introduced in Phase 0B. Later lanes may share an
existing runtime helper only when the behavior is unchanged. If the
wrapper-plan route needs different runtime behavior, that helper must have a
separately named generated caller and cleanup contract recorded in the relevant
lane before use.

CPython reference-counting conventions, new/borrowed/stolen-reference rules,
`Py_INCREF`/`Py_DECREF`, and partial-failure cleanup remain binding-emitter
implementation mechanics. They are absent from plan models, rendered plans,
and cross-backend validation.

### Phase 0C Scalar Policy Completion Contract

Phase 0C is a semantic policy phase only. It adds no wrapper-plan records,
planner, backend nodes, emitters, printers, compilation path, or route
selection.

The selected existing scalar semantic fixture is
`tests/wrapper/fortran/scalars/contracts/fmath/__init__.pyi`. Its current
contract surface is:

- public module functions only; no methods, classes, overloads, module
  variables, arrays, strings, hidden outputs, optional arguments, result
  projections, build bundles, or runtime helper selection;
- every callable is marked `@external`;
- every callable has a `@bind(...)` native symbol and lower-case Python
  function name;
- every Python argument is a primitive scalar value, completed by policy as
  `PythonBarrierAction.SCALAR_VALUE`;
- every native argument slot is `Addr(Arg(i))`, completed by policy as an
  address-projected scalar call-local value with
  `NativeBarrierAction.PASS_CALL_LOCAL_ADDRESS`;
- every callable has one scalar value result, completed by policy as
  `CodegenAction.DIRECT_VALUE`, `PythonBarrierAction.NONE`, and
  `NativeBarrierAction.NONE`;
- scalar inputs have no writeback, release, or public setter phase; backend
  cleanup of call-local temporaries remains local to the eventual selected
  handler.

Post-IR policy completion must attach one typed
`ScalarWrapperFunctionPolicy` to each semantic function. A supported scalar
record contains:

- stable owner path, Python name, native symbol, external flag, and bind target;
- one `ScalarWrapperArgumentPolicy` per declared Python argument, including
  owner path, Python position, native position, Python/native names,
  semantic scalar type name, rank, optional flag, completed ownership decision,
  completed codegen action, completed Python barrier action, completed native
  barrier action, storage mode, boundary storage mode, projection flag, and
  Python visibility;
- one `ScalarWrapperResultPolicy` for scalar results, including owner path,
  semantic scalar type name, rank, completed ownership decision, completed
  codegen action, completed Python barrier action, completed native barrier
  action, storage mode, and boundary storage mode;
- one `ScalarWrapperNativeCallSlotPolicy` per native slot, including native
  position, source kind (`implicit` or `projection`), Python position,
  Python/native names, projection value kind, owner path, completed native
  barrier action, and completed codegen action;
- empty writeback, cleanup, and release action tuples for the selected scalar
  fixture.

Unsupported functions still receive a typed scalar-wrapper policy record with
`supported=False` and stable blocker text. Missing policy or blocked policy
must fail through the semantic accessor before planning starts. Later planner
code may consume the typed record, but it must not inspect bridge, binding, or
backend-local implementation state to recover any field listed above.

### Phase 0D Hierarchical Plan-Core Contract

Phase 0D converts completed first-lane scalar policy into route-neutral wrapper
plans only. It adds no backend nodes, source emitters, source printers,
compilation path, route selector, fallback route, or production wrapper-plan
entrypoint.

The plan-core package owns these records:

- `ModulePlan`: one generation-unit plan with the module owner path, tuple of
  function plans, and the completed action-handler registry used by validation
  and rendering.
- `FunctionPlan`: one semantic function owner with Python/native names,
  external/bind metadata, tuple of argument transfer plans, one optional result
  plan, one bridge ABI plan, available symbolic roles, and explicit writeback,
  cleanup, and release lifecycle tuples.
- `ArgumentTransferPlan`: the single cross-boundary transfer record for one
  argument. It contains the completed `PythonBarrierAction`, one binding
  handoff, one bridge ABI slot, the completed `NativeBarrierAction`, and one
  native-call slot reference. Binding and bridge subplans must not be split into
  separate argument policies.
- `BridgeAbiPlan` and `BridgeAbiSlotPlan`: deterministic bridge ABI positions
  and symbolic roles copied from completed scalar policy.
- `NativeCallSlotPlan`: deterministic native-call slot references copied from
  completed scalar native-call slot policy. No native slot may be invented from
  datatype, `intent`, or backend-local state.
- `ResultPlan` and `LifecycleActionPlan`: symbolic result/writeback/cleanup
  consumers. The selected scalar baseline has a scalar result and empty
  lifecycle tuples.
- `HandlerRegistryPlan`: primary Python-barrier handlers, secondary
  native-barrier handlers, and result handlers keyed by existing completed
  `PythonBarrierAction`, `NativeBarrierAction`, and `CodegenAction` values. The
  plan core must not define duplicate action enums.

`WrapperPlanner(ClassVisitor)` owns deterministic structural wiring:

- `_visit_SemanticModule` returns one `ModulePlan` and recursively visits only
  module functions after the support analyzer confirms the whole module is in
  the completed first scalar lane.
- `_visit_SemanticFunction` consumes
  `completed_scalar_wrapper_policy(function)` and returns one `FunctionPlan`.
  Missing or blocked scalar-wrapper policy is an error before planning.
- `_visit_ScalarWrapperArgumentPolicy` and
  `_visit_ScalarWrapperResultPolicy` copy only completed policy values into
  transfer/result records and attach handler names from the class-owned
  registries.

`WrapperPlanValidator(ClassVisitor)` owns pre-emission invariants:

- unknown primary Python action handlers, unknown secondary native action
  handlers, and unknown result handlers;
- missing bridge ABI slots or missing native-call slots on argument transfers;
- inconsistent handoff, bridge-slot, and native-slot symbolic roles;
- duplicate symbolic roles within one function;
- results, writebacks, cleanups, or releases consuming unavailable symbolic
  values.

`WrapperPlanSupportAnalyzer(ClassVisitor)` reports whole-generation-unit
eligibility with stable owner paths and reasons. It does not select routes.

`WrapperPlanRenderer(ClassVisitor)` renders deterministic maintainer text with
owner paths, completed policy action values, handler names, symbolic handoffs,
bridge ABI slots, native slots, and lifecycle order. It must not render backend
nodes, C/Fortran source, CPython reference-counting mechanics, or printer
output.

### Phase 0E Minimal Scalar Backend Foundation Contract

Phase 0E introduces isolated backend syntax, naming, source assembly, and
printer infrastructure only. It does not add scalar plan emitters, binding or
bridge handlers, runtime helper implementations, compilation, route selection,
or generated artifact parity checks.

The legacy inventory for the first scalar backend foundation is:

| Backend concern | Legacy Python source owner | Consumed behavior | Isolated Phase 0E choice |
| --- | --- | --- | --- |
| Generated symbol naming | `x2py/codegen/scope.py::Scope.get_new_name` | deterministic unique names and collision avoidance | rewrite as `NameAllocator`; no semantic scopes, categories, or lookup ownership |
| Module/function contexts | `x2py/codegen/scope.py::Scope` plus binding/bridge generator-local state | per-module and per-function local names | rewrite as explicit `ModuleEmissionContext` and `FunctionEmissionContext` |
| Generic node structure | `x2py/codegen/models/core.py::Module`, `FunctionDef`, `FunctionDefArgument`, `Return`, `Import`, `Declare` | module imports, function signatures, parameters, declarations, statements, returns | rewrite minimal frozen C/Fortran node dataclasses with only printer-consumed fields |
| Scalar datatype/literal spelling | `x2py/codegen/models/datatypes.py` scalar `Numpy*Type` classes and `convert_to_literal` | C/Fortran scalar type spellings and literal text | rewrite as explicit `BackendScalarType` and expression/literal text nodes |
| CPython/NumPy include/API concepts | `x2py/codegen/bindings/cpython_api.py`, `numpy_cpython_api.py`, and `CPythonCodePrinter` | `Python.h`, `numpy/arrayobject.h`, `PyObject*`, `PyArg_ParseTupleAndKeywords`, scalar conversion helper names, `PyMethodDef`, `PyModuleDef`, `import_array` | represent only include/API references as isolated node data; Phase 1 handlers decide which primitives to emit |
| C and header printing | `x2py/codegen/printers/ccode.py::CCodePrinter` and `cpythoncode.py::CPythonCodePrinter` | include lines, header guards, prototypes, function signatures, declarations, expression statements, returns | rewrite `CSourcePrinter` over isolated C nodes only |
| Fortran bridge printing | `x2py/codegen/printers/fcode.py::FCodePrinter` | module/use/contains, `bind(c, name=...)`, scalar declarations, assignments, calls | rewrite `FortranSourcePrinter` over isolated Fortran nodes only |
| Source assembly orchestration | `x2py/codegen/binding_pipeline.py::BindingPipeline.generate/write` | create complete C source, C header, and Fortran module objects, then print modules | rewrite `BackendSourceAssembly.rendered_sources()` for in-memory source strings only |

Every Phase 0E node field is consumed by a Phase 0E printer, source assembly,
or context test. Phase 1 scalar emitters will be the first production
consumers of these nodes; until then tests construct small representative
modules directly. This phase intentionally keeps CPython reference counting,
argument parsing, scalar conversion helper bodies, bridge call bodies, runtime
support installation, file writes, compiler/linker calls, and route eligibility
outside the implementation.

Structural guarantees for this phase:

- no `x2py.wrapper_codegen` backend module imports `x2py.codegen`;
- C and Fortran source printers accept only isolated backend nodes and do not
  import or inspect wrapper-plan models;
- generated-source assertions stay focused on naming, declarations,
  signatures, header guards, includes, `bind(c)` spelling, and
  module-to-printer orchestration rather than full runtime wrapper snapshots.

### Intermediate Test Contract

Add intermediate tests only where they protect a stable boundary or a failure
that the existing compiled wrapper tests cannot isolate.

- Test policy completeness for each newly migrated owner: missing or blocked
  policy fails before planning.
- Test policy-to-plan projection with an existing semantic fixture. Assert the
  owner hierarchy, completed action keys, call/ABI order, handoffs, and one
  concise maintainer rendering for the lane; do not snapshot every plan field.
- Test validator failures with small directly constructed plans. Use
  table-driven cases for invariant categories such as missing/duplicate slots,
  incompatible producer/consumer handoffs, unavailable results/writebacks, and
  unsupported completed actions. Do not add one test per implementation branch.
- Test whole-module support and route selection with existing generation units:
  one fully supported unit and representative units blocked by later lanes.
  Prove that no unit mixes routes and no new-route failure silently retries
  legacy generation.
- Test the isolated visitor, name allocator, dependency boundary, registry
  completeness, and complexity checker directly because they are standalone
  contracts not observable through wrapper runtime behavior.
- Do not require one direct unit test per emitter handler or helper. Registry
  checks prove that the rendered handler exists; the reused compiled wrapper
  tests prove the selected chain's behavior. Add a direct emitter test only for
  a failure or mechanical contract that cannot be reached through an existing
  wrapper fixture.
- Do not add full generated C/Fortran source snapshots. Keep or add focused
  source assertions only when exact source structure is the observable ABI or
  build contract and runtime behavior cannot prove it.
- Add focused node/printer tests only for nontrivial mechanical behavior such as
  precedence, escaping, declaration syntax, or header/source partitioning.
  Do not create one test per node or copied printer method.

The governing rule is one intermediate test per stable contract or failure
category, not one test per class, method, node, or branch.

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
   action registries, ABI/handoff specs, validator, renderer, and support-report
   coverage.
6. Implement the minimum dependency-closed backend slice in
   `x2py.wrapper_codegen`: copy small suitable pieces, rewrite oversized legacy
   classes as minimal equivalents, and add only the intermediate tests required
   by the contract above.
7. Generate the plan from policy-completed semantic IR, dispatch binding and
   bridge handlers into isolated node fragments, assemble complete backend
   modules, and print complete internal artifacts.
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

## Required Execution Order

The checklist order is mandatory. Do not wire the new route into production
build selection while its scalar artifacts exist only as models or uncompiled
source. Complete each subphase and its focused evidence before starting the
next one:

```text
0A tests/wrapper inventory and current-behavior baseline
  -> 0B isolated package and dependency boundary
  -> 0C complete scalar policy
  -> 0D hierarchical wrapper-plan core and validation
  -> 0E minimal scalar backend nodes, names, and printers
  -> 1A internal scalar plan emission
  -> 1B compiled dual-route parity
  -> 1C production route selection
  -> later semantic lanes in numbered order
  -> 11 cross-cutting tests/wrapper completion
  -> 12 cutover and legacy removal
```

Within later lanes, follow the same dependency order: identify the existing
`tests/wrapper` coverage, audit current behavior, expand the lane checklist,
complete policy, add plan records/planner/validation, implement only the
required backend behavior, emit and print nodes internally, compile and compare
the same existing tests through both routes, update the migration matrix, and
only then widen production route eligibility.

### Session Continuation Protocol

Progress is evidence-driven, not calendar-driven. Do not use a time target to
skip a prerequisite, weaken parity, reduce validation, invent a smaller test
fixture, or mark partially completed work as complete.

The minimal user prompt for a new implementation session is:

```text
Continue implementing the wrapper-plan migration checklist.
```

That prompt means the agent must follow this resume procedure before editing:

1. Read this checklist and the repository instructions, then inspect the dirty
   worktree, recent relevant commits, current checklist state, and wrapper-test
   migration matrix. Work with existing user changes; do not reset them.
2. Audit the first unchecked dependency-closed group whose prerequisites are
   genuinely complete. Reconcile stale checkbox state against live code and
   tests before choosing work.
3. If the next item is a broad phase or lacks exact policy fields, legacy source
   paths, plan records, handlers, invariants, and existing test coverage, expand
   it in this file before implementation.
4. Use the legacy replay procedure for the selected existing generation unit.
   Start from its passing test, retained generated artifacts, and traced Python
   implementation rather than designing from memory.
5. Implement one coherent group through its required intermediate checks. Do
   not stop after adding models or copied code when the group's next required
   validation can be completed in the same session.
6. Run the focused existing `tests/wrapper` nodes, required intermediate
   contract tests, wrapper-codegen checker, static-analysis commands, and other
   verification required by `AGENTS.md` for the files changed.
7. Update checkboxes and migration-matrix rows only for behavior proven by the
   required evidence. A legacy test passing does not prove the new route; a row
   becomes `wrapper-plan` only when route diagnostics and parity requirements
   prove it.
8. End the session with the exact completed group, changed pipeline stages,
   legacy paths reused, tests and command results, remaining unsupported paths,
   and the next dependency-ordered unchecked item.

Do not search for a shortcut around an unmet gate. Missing policy goes back to
post-IR completion, unsupported mechanics remain on the explicit legacy route,
and failed parity is investigated against retained legacy artifacts. If the new
route starts recreating most of legacy codegen without materially improving
policy traceability, plan readability, or handler size, stop for an explicit
value review rather than continuing automatically.

## Phase 0 — Foundation Before Production Routing

### Phase 0A — Wrapper Test Inventory And Current Scalar Baseline

- [x] Enumerate every Python test node under `tests/wrapper` and add the
  migration matrix required above. Do not begin implementation with untracked
  wrapper tests.
- [x] Classify each test as non-generating or map it to its complete wrapper
  generation unit and all semantic lanes needed before that unit can use the
  wrapper-plan route.
- [x] Select the first existing generation unit whose coverage best matches the
  initial scalar lane. Record every additional feature in that unit that delays
  atomic route eligibility; do not replace it with a new narrower fixture.
- [x] Inventory the current end-to-end wrapper behavior and implementation paths
  for the first scalar lane, including lowering branches, binding/bridge helper
  methods, CPython/NumPy API primitives, source printers, generated artifacts,
  build integration, and focused runtime fixtures.
- [x] Create a maintained baseline matrix mapping each first-lane current code
  path and observable behavior to its proposed plan action, handler, required
  backend behavior, and parity evidence. Do not define an action from a
  hypothetical implementation.
- [x] Audit every decorator, native-call projection kind, implicit call
  behavior, and generated module/class feature accepted by the live semantic
  model; reconcile the coverage matrix with that audit.
- [x] Confirm the legacy generator's independent entrypoint and baseline tests;
  do not modify legacy lowering, nodes, generators, or printers in this phase.
- [x] Update the maintained wrapper-plan contract with the audited Python
  surface, binding handoff, bridge ABI, native call, result, cleanup, writeback,
  node-construction, and printing phases.

### Phase 0B — Isolated Package Boundary

- [x] Create the `x2py.wrapper_codegen` package skeleton without connecting it
  to production build selection.
- [x] Define and enforce the package boundary: `x2py.wrapper_codegen` cannot
  import `x2py.codegen`, legacy `x2py.codegen` cannot import
  `x2py.wrapper_codegen`, and only pipeline orchestration may eventually import
  both route entrypoints.
- [x] Add dependency tests for that boundary before isolated backend code is
  introduced.
- [x] Implement and test the minimal independent `ClassVisitor` used throughout
  the package, including deterministic MRO lookup, configurable method prefixes,
  and explicit unsupported-node failure.
- [x] Add structural checks requiring visitor-based traversal and rejecting
  undeclared module-level production functions in `x2py.wrapper_codegen`.
- [x] Add the blocking wrapper-codegen complexity/traceability checker before
  emitter handlers are introduced. Cover Radon complexity, statement count,
  nesting depth, registry completeness, secondary-dispatch completeness, and
  forbidden printer calls from handlers.
- [x] Add focused tests for the checker, including one failure fixture for each
  enforced limit and registry/dependency rule.
- [x] Define the pipeline-owned generated-wrapper artifact result shared by both
  routes without duplicating native object/library/link-plan ownership.
- [x] Keep runtime helper APIs shared only when their behavior is unchanged. Add
  separately named new-route helpers when different behavior is required, and
  record their generated callers and cleanup contract.
- [x] Document that CPython reference counting and API ownership conventions are
  binding-emitter-local mechanics and are absent from plan models, rendered
  plans, and cross-backend plan validation.

### Phase 0C — Complete Scalar Policy

- [x] Audit the selected existing scalar generation unit and list every
  module/function/argument/result/decorator/native-projection decision the
  planner would otherwise need to infer.
- [x] Define or complete typed post-IR policy records for the owners needed by
  the first scalar lane. Do not use free-form metadata or planner defaults as a
  substitute for a completed policy field.
- [x] Move any remaining scalar action, call/ABI order, ownership, lifecycle,
  projection, writeback, or cleanup decisions into
  `complete_semantic_policies(...)` before implementing the planner.
- [x] Verify the policy-completed module contains every datatype fact and
  completed policy value needed to reproduce the audited legacy behavior
  without reading bridge, binding, or backend-local state.
- [x] Add only the intermediate policy tests required by the contract above,
  reusing the selected existing semantic fixture and covering missing/blocked
  policy failure before planning.
- [x] Do not add plan models, backend nodes, emitters, printers, compilation, or
  production route selection in this phase.

### Phase 0D — Hierarchical Wrapper Plan Core

- [x] Define the first frozen plan data classes and tuple collections.
- [x] Implement `WrapperPlanner(ClassVisitor)` with explicit `_visit_<Owner>`
  methods that each return one plan record, recursively visit only that owner's
  children, and perform only deterministic structural wiring. Keep each method
  within the strict planner complexity gate.
- [x] Define one `ArgumentTransferPlan` containing the existing completed Python
  action, one binding-to-bridge handoff, bridge ABI slot, completed native
  action, and native-call slot. Do not create separate binding and bridge
  subplans for one argument.
- [x] Define `BridgeAbiPlan`, native-call refs, handoff specs, primary/secondary
  handler registries, and validation errors around existing completed
  `PythonBarrierAction` and `NativeBarrierAction` values. Do not add duplicate
  plan action enums for behavior already represented by completed policy.
- [x] Add a plan validator that catches inconsistent transfer handoffs,
  missing bridge/native-call slots, unknown primary or secondary handlers,
  duplicate symbolic roles, and writebacks/results that consume unavailable
  values.
- [x] Define the whole-generation-unit support report, including stable
  owner-path reasons for unsupported elements, without changing production
  route selection yet.
- [x] Implement class-owned `WrapperPlanSupportAnalyzer`,
  `WrapperPlanValidator`, and `WrapperPlanRenderer` visitor APIs; do not add
  equivalent module-level functions.
- [x] Add deterministic plan rendering that includes symbolic owner paths,
  completed policy values, dispatch handler names, handoffs, bridge ABI slots,
  native slots, and lifecycle order without backend nodes or CPython-specific
  mechanics.
- [x] Verify the planner fails on missing/incomplete policy rather than deriving
  defaults, and the validator produces owner-path diagnostics before node
  emission for policy/plan inconsistency.
- [x] Add one policy-to-plan projection/rendering test for the selected existing
  scalar fixture and table-driven validator tests by invariant category. Do not
  add one test per planner method or plan field.
- [x] Do not add backend nodes, emitters, printers, compilation, or production
  route selection in this phase.

### Phase 0E — Minimal Scalar Backend Foundation

- [x] Inventory the minimum dependency-closed set of scalar C/Fortran nodes,
  datatype/literal behavior, CPython and NumPy API primitives, naming behavior,
  helper concepts, and printer cases required for Phase 1. Record each legacy
  source path and consumed field/method before implementation.
- [x] Implement a minimal `NameAllocator` and module/function emission contexts;
  do not copy legacy `Scope` or its semantic lookup/categories.
- [x] For every required node/API/helper class, choose explicitly between a
  small unchanged copy and a rewritten minimal class. Each new field and method
  must have a current Phase 1 emitter or printer consumer.
- [x] Do not import, alias, subclass, or adapt legacy model classes. Preserve
  required behavior through the isolated implementation and later compiled
  parity evidence.
- [x] Add focused tests only for nontrivial naming/node/printer mechanics that
  the selected existing wrapper fixture cannot isolate. Do not add exhaustive
  node tests or full generated-source snapshots.
- [x] Reproduce the legacy module/header assembly and
  `module -> doprint(module)` orchestration needed to create complete
  `c_module` and `fortran_module` objects before writing source.
- [x] Implement only the C/Fortran printer cases needed by the isolated scalar
  nodes. Verify structurally that the printers consume only isolated nodes and
  cannot import or inspect wrapper-plan models.
- [x] Do not add scalar emitters, compilation, or production route selection in
  this phase.

## Phase 1 — Scalar Function Inputs

Scope: free functions with scalar numeric/logical arguments that are
Python-visible inputs. Scalar call-target decorators and scalar native-call
argument projections are included as separate checklist items; unsupported
projection kinds keep the whole module on the legacy route.

### Phase 1A — Internal Plan Emission

- [ ] Generate plans for scalar value arguments such as `f(x: Float64)`.
- [ ] Populate one end-to-end `ArgumentTransferPlan` per scalar argument rather
  than constructing separate binding and bridge plan objects.
- [ ] Represent Python argument position and `@native_call` native argument order
  explicitly, including reordered arguments.
- [ ] Represent implicit native order, `@bind(...)`, `@external`, and
  `@hold_gil` explicitly; none may be inferred or ignored by the emitters.
- [ ] Represent `Arg(...)`, `Addr(Arg(...))`, and typed numeric/logical hidden
  literals as native argument sources with exact native positions.
- [ ] Reject duplicate, missing, or out-of-range Python/native positions and
  bridge/native-call slots during plan validation.
- [ ] Register the isolated `_convert_python_scalar_value_argument` binding
  handler for `SCALAR_VALUE` and isolated native handlers for `PASS_VALUE`,
  `PASS_CALL_LOCAL_ADDRESS`, or other scalar actions already supported by
  completed policy.
- [ ] Reuse audited legacy method-body snippets where they remain simple;
  otherwise write smaller direct handlers that reproduce the baseline behavior
  using the isolated nodes and explicit contexts.
- [ ] If scalar-family mechanics make a handler difficult to follow, introduce
  a secondary logical/integer/real/complex dispatcher; keep precision as data
  unless it changes emitted APIs, checks, declarations, or control flow.
- [ ] Keep every scalar emitter handler/helper within the strict complexity,
  statement-count, and nesting limits; expose any secondary handler chain in
  plan rendering and registry checks.
- [ ] Validate the transfer handoff, bridge ABI slot, and native-call slot as one
  chain before either emitter runs.
- [ ] Make each scalar binding/bridge handler return isolated node fragments;
  assemble complete C and Fortran module nodes outside individual handlers.
- [ ] Construct complete `c_module` and `fortran_module` objects, then pass them
  to isolated `CPythonCodePrinter.doprint(...)` and `FCodePrinter.doprint(...)`
  implementations to produce the scalar binding source/header and bridge
  source.
- [ ] Assemble module initialization and generated-source requirements with the
  printed files into the complete new-route artifact result.

### Phase 1B — Internal Compilation And Parity

- [ ] Select existing `tests/wrapper` nodes whose complete generation units are
  now covered; do not introduce a new scalar source fixture for parity.
- [ ] Provide test-only orchestration that sends each selected existing module
  directly through legacy and wrapper-plan routes without a public
  compatibility option or production selector change.
- [ ] Compile and import new-route scalar artifacts through the shared compiler
  and linker before making any production module eligible.
- [ ] Reuse the selected tests' existing build helpers and assertions for both
  routes; do not duplicate their behavioral assertions in a new test file.
- [ ] Compare both routes for Python calls/results, native argument order,
  pass-by-value/address behavior, conversion failures, exception state,
  backend-local cleanup, generated artifact requirements, compilation, import,
  and runtime behavior.
- [ ] Resolve every unexplained parity difference or document a separately
  approved behavior correction before proceeding.
- [ ] Change the selected tests' migration-matrix status from `legacy` to
  `dual-route` only after both compiled routes pass.

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
- [ ] Move every newly eligible existing test from `dual-route` to
  `wrapper-plan` in the migration matrix after production selection passes.

## Phase 2 — Scalar Results And Hidden Outputs

Scope: scalar direct returns, hidden scalar outputs, and scalar projected
results.

- [ ] Audit and record the legacy result, hidden-output, result-packaging,
  `@raises`, cleanup, printer, and runtime paths that define this lane's
  baseline.
- [ ] Add or rewrite only the additional result variables, CPython creation
  calls, C/Fortran statements, and printer cases required by this lane, with
  baseline tests.
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
- [ ] Add or rewrite only the additional optional/descriptor nodes, API
  primitives, local-state helpers, and printer cases required by this lane,
  with baseline tests.
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
- [ ] Add or rewrite only the additional module/type nodes, getter/setter API
  primitives, initialization nodes, and printer cases required by this lane,
  with baseline tests.
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
