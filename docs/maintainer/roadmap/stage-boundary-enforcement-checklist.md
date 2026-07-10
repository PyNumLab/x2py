---
title: Stage Boundary Enforcement Checklist
audience: maintainers
prerequisites: pipeline map, semantic IR, ownership policy
related: ../internal-architecture/pipeline-map.md, ../../user/reference/semantic-ir.md, semantic-pyi-wrapper-checklist.md, index.md
status: active-roadmap
---

# Stage Boundary Enforcement Checklist

This checklist tracks the architectural work required to make every wrapper
pipeline transition explicit, one-way, and mechanically enforced. It is not
enough for the main build path to call functions in the intended order. Each
stage must accept only the preceding stage's completed representation, reject
invalid state without repairing it, and leave all earlier-stage decisions
unchanged.

The target pipeline is:

```text
parsed source model
  -> semantic IR draft
  -> policy-completed semantic IR
  -> readiness-approved semantic IR
  -> codegen IR
  -> bridge IR
  -> binding IR
  -> emitted sources
  -> compilation and link result
```

Stages are dependent but monotonic. A later stage may translate or validate the
preceding output. It must not reach backward into parser facts, secretly rerun
an earlier stage, infer a missing semantic decision, or mutate completed policy.

## Incremental Implementation Protocol

This checklist is the implementation prompt and the authoritative progress
record. Do not maintain a second copy of its requirements in a separate prompt.

The normal request for continuing this work is:

> Implement the next coherent group of unchecked items from the stage boundary
> enforcement checklist.

A request may also name a phase or a smaller set of items when a particular
boundary should be handled first.

For every implementation turn:

1. Read `AGENTS.md` and this entire checklist before selecting work.
2. Inspect the live files and existing changes; do not assume an unchecked item
   is still unimplemented or that a checked item is still correct.
3. Select the smallest dependency-closed group that produces a verifiable
   architectural improvement. Do not select unrelated boxes merely because
   they are nearby.
4. State which checklist items are in scope before editing.
5. Update the relevant maintained architecture or public contract docs before
   executable code when behavior or ownership changes.
6. Implement the selected group completely across code, diagnostics, tests,
   documentation, and call sites. Do not add compatibility paths for an old
   stage API.
7. Run focused verification for the selected boundary, followed by every
   repository-required static check for the files changed.
8. Mark an item complete only when its full acceptance criterion has direct
   evidence. Leave partially implemented items unchecked and add a short note
   identifying the remaining work instead of treating partial progress as
   completion.
9. Under the completed item or phase, record the owning files, tests, and exact
   verification evidence needed by the next maintainer to audit the claim.
10. Stop at a coherent stage boundary. Report the next dependency-ready group,
    but do not begin it unless it was part of the stated scope.

Each implementation summary must include the changed-stage breakdown required
by `AGENTS.md`, the checklist items completed, tests added or updated, focused
and static verification results, remaining unchecked dependencies, and any
unrelated pre-existing failure. The checklist is complete only when every
non-negotiable requirement and phase acceptance item has direct evidence.

## Non-Negotiable Contract

- [ ] Semantic draft, policy-completed IR, readiness-approved IR, and codegen IR
  are mechanically distinguishable representations. A mutable metadata boolean
  is not the stage boundary.
- [ ] Policy completion returns a new completed representation and does not
  mutate the caller's semantic draft.
- [ ] Every semantic decision required by lowering, bridge generation, binding
  generation, printing, or build integration is complete before `ir2ast.py`.
- [ ] Completed policy cannot be replaced through a public mutable metadata
  dictionary.
- [ ] Readiness accepts only policy-completed IR, does not invoke policy
  completion, and does not mutate its input.
- [ ] Successful readiness returns a distinct readiness-approved representation.
- [ ] Lowering accepts only readiness-approved IR and cannot invoke readiness or
  policy completion.
- [ ] Bridge and binding generators consume codegen decisions and cannot inspect
  parser models or semantic drafts.
- [ ] Printers emit the representation they receive and cannot invoke semantic
  policy completion or readiness.
- [ ] High-level orchestration invokes every stage explicitly in the documented
  order, with no hidden fallback or compatibility path.

## Boundary Immutability Model

The implementation rule is:

```text
private mutable stage builder
  -> validate the stage result
  -> deeply freeze the stage output
  -> hand the immutable output to the next stage
```

Immutability applies to values crossing stage boundaries, not to every local
object used while constructing them. Parsers, converters, lowerers, generators,
symbol tables, scopes, caches, and compiler-command builders may use mutation
inside their owning stage. Those mutable builders must remain private and must
never be accepted as another stage's input.

- [ ] Parsed-project output is immutable before semantic conversion receives it.
- [ ] Semantic-draft output is immutable before policy completion receives it.
- [ ] Policy-completed output is deeply immutable before readiness receives it.
- [ ] Readiness-approved output is deeply immutable before lowering receives it.
- [ ] Codegen IR is frozen after lowering and before bridge generation.
- [ ] Bridge IR is frozen after bridge generation and before binding generation.
- [ ] Binding IR is frozen after binding generation and before printing.
- [ ] Native build plans and build results are immutable records; execution
  state remains private to the compiler/build runner.
- [ ] Generated source payloads cross their boundary as immutable text and
  immutable artifact descriptions.
- [ ] Runtime handles are explicitly outside the pipeline-freezing rule because
  allocation, association, owner state, and `close()` state are intentionally
  mutable at execution time.
- [ ] A frozen dataclass containing a mutable list, set, dictionary, metadata
  dictionary, or mutable nested semantic object does not satisfy this contract.
- [ ] Boundary collections use tuples, frozensets, deeply copied read-only
  mappings, or equivalently immutable structures.
- [ ] Mutable backing mappings are not retained or exposed after constructing a
  read-only view.
- [ ] Completed policy is represented through typed read-only fields or a typed
  immutable policy bundle rather than replaceable string-key metadata entries.
- [ ] Mutation of a draft, builder, or source metadata object after a transition
  cannot change the frozen output already handed to the next stage.
- [ ] Stage types cannot be forged by setting a marker in a metadata dictionary;
  construction flows through the owning transition function.
- [ ] Tests treat Python's normal supported API as the enforcement boundary;
  deliberate `object.__setattr__`-style interpreter bypasses are not supported
  mutation paths.

## Phase 0 — Live Boundary Audit

- [ ] Inventory every production caller of parsing, source-to-IR conversion,
  policy completion, readiness, lowering, bridge generation, binding
  generation, printing, and compilation.
- [ ] Record the input and output representation of every stage entrypoint.
- [ ] Inventory every mutation of semantic modules, declarations, semantic
  types, metadata, policy decisions, export lists, and readiness blockers.
- [ ] Inventory every call to `complete_semantic_policies()` and classify it as
  the explicit pipeline transition or a hidden stage invocation to remove.
- [ ] Inventory all `_raise_for_*` and blocker construction in `ir2ast.py` and
  classify each check as semantic validity, policy validity, readiness/backend
  support, or a genuine lowering invariant.
- [ ] Audit every bridge/binding branch that reads datatype, `intent`, rank,
  shape, `is_alias`, memory handling, dotted-variable form, nullability,
  storage, ownership, or policy fields.
- [ ] For each audited bridge/binding branch, record whether it is completed
  policy dispatch, permitted backend-local mechanics, or policy inference that
  must move upstream.
- [ ] Confirm the audit includes source-driven builds, semantic `.pyi` builds,
  readiness-only inspection, `.pyi` emission, manifest replay, and Makefile
  generation.

## Phase 1 — Documented Stage-State Model

- [ ] Update the maintained pipeline map with the exact stage-state types and
  allowed transitions.
- [ ] Document which stage owns parser validity, semantic contract validity,
  policy validity, readiness/backend support, lowering invariants, and
  compilation failures.
- [ ] Document the distinction between semantic policy and backend-local emitted
  helper storage.
- [ ] Document which transformations are allowed to be lossy, such as entry
  export pruning, and which source representation remains available for
  diagnostics.
- [ ] Document whether completed and readiness-approved representations are
  immutable snapshots, wrappers around immutable data, or another design with
  equivalent mechanical guarantees.
- [ ] Update source-navigation docs so contributors enter each concern through
  its owning stage rather than a downstream generator.
- [ ] For every stage package, document what it owns, what it consumes, what it
  returns, which internal builders may mutate, what it must never infer, and
  which downstream package may import its public output.
- [ ] Document the runtime-handle exception so pipeline immutability is not
  incorrectly applied to intentionally stateful native runtime objects.

## Phase 2 — Explicit Stage Representations

- [ ] Introduce a semantic draft representation produced by source-to-IR and
  semantic `.pyi` conversion.
- [ ] Introduce a policy-completed representation that cannot be confused with
  the draft type.
- [ ] Introduce a readiness-approved/wrappable representation that cannot be
  constructed by merely setting metadata.
- [ ] Preserve a separate codegen representation for lowering output.
- [ ] Introduce distinct bridge and binding handoff representations when those
  stages currently share a mutable model that either stage can rewrite.
- [ ] Give each stage representation a narrow public construction path owned by
  its transition function; keep mutable builders private to the stage package.
- [ ] Replace mutable policy metadata storage with an immutable completed policy
  bundle or an equivalently sealed representation.
- [ ] Make nested collections and policy maps immutable enough that downstream
  code cannot replace a decision indirectly.
- [ ] Ensure mutation of the original draft after completion cannot affect the
  completed representation.
- [ ] Remove `POLICY_COMPLETION_PREPARED_METADATA` if the new type makes it
  redundant, or limit it to serialized diagnostic provenance rather than using
  it as authority.
- [ ] Do not add aliases, coercions, adapters, or compatibility wrappers that
  allow an old mutable `SemanticModule` to bypass the new boundary.

The intended transition API should be equivalent to this shape, although exact
names may follow the settled package design:

```python
def build_semantic_draft(parsed: ParsedProject) -> SemanticDraft: ...

def complete_policies(draft: SemanticDraft) -> PolicyCompletedIR: ...

def validate_readiness(completed: PolicyCompletedIR) -> WrappableSemanticIR: ...

def lower_to_codegen(wrappable: WrappableSemanticIR) -> CodegenIR: ...

def generate_bridge(codegen: CodegenIR) -> BridgeIR: ...

def generate_binding(bridge: BridgeIR) -> BindingIR: ...
```

- [ ] Each transition rejects every other stage representation rather than
  coercing it or running a missing earlier transition.
- [ ] Each transition returns a new object and leaves its input observably
  unchanged.
- [ ] Stage results expose immutable diagnostic/source provenance without
  retaining a mutable reference to the preceding builder.
- [ ] Equality or stable fingerprints allow tests to prove that validation and
  downstream generation did not mutate an earlier result.

## Phase 3 — Post-IR Policy Completion

Policy completion must own all semantic choices needed downstream, including
choices currently reconstructed from raw facts during lowering or codegen.

- [ ] Complete object kind for every argument, result, field, module variable,
  callback boundary, class instance, and hidden native value.
- [ ] Complete ownership, transfer, destruction, borrowed state, target owner,
  and release responsibility.
- [ ] Complete mutability, native mutation, writeback, assignment mode, and
  replacement behavior.
- [ ] Complete nullability and distinguish omitted arguments from explicit
  present-but-null descriptor values.
- [ ] Complete output projection and hidden/identity/copy result behavior.
- [ ] Complete contract-value and boundary storage modes (`stack`, `heap`, or
  `alias`).
- [ ] Complete Python barrier action and native barrier action.
- [ ] Complete getter behavior, native setter assignment, and Python setter
  exposure for every field and module variable.
- [ ] Complete descriptor/data-buffer array interoperability and all required ABI
  selector facts.
- [ ] Complete pass-by-value, pass-by-address, and call-local address behavior.
- [ ] Complete native array handle kind, ownership, operations, extraction,
  descriptor interop, and build requirements.
- [ ] Complete callback argument/result ownership and barrier decisions.
- [ ] Complete entry export reachability before ownership decisions for the
  retained declarations.
- [ ] Reject attempts to run policy completion on an already-completed
  representation.
- [ ] Ensure policy completion produces path-aware blockers for missing or
  contradictory facts rather than inserting a downstream fallback.

## Phase 4 — Readiness As A Mandatory Gate

- [ ] Make the prepared readiness API accept only policy-completed IR.
- [ ] Remove automatic policy completion from readiness APIs.
- [ ] Make readiness validation non-mutating.
- [ ] Move semantic support and backend-capability blockers out of `ir2ast.py`
  into readiness.
- [ ] Keep policy contradictions in policy completion rather than readiness.
- [ ] Keep only genuine target-AST representability invariants in lowering.
- [ ] Return a distinct readiness-approved representation only when there are no
  blockers.
- [ ] Preserve a structured blocker report when readiness fails.
- [ ] Require both source and semantic `.pyi` wrapper builds to pass readiness
  before lowering.
- [ ] Require manifest replay and Makefile generation to use the same readiness
  gate as direct builds.

## Phase 5 — Mechanical IR-To-AST Lowering

- [ ] Change `semantic_ir_to_codegen_ast()` to accept only readiness-approved
  semantic IR.
- [ ] Add one recursive entry validator that verifies every required completed
  policy category before visiting any declaration.
- [ ] Replace optional `.get(...)` access for required getter, setter, result,
  class, array-handle, storage, barrier, and interoperability decisions with
  required typed access.
- [ ] Move pass-by-value selection from parser-origin inspection into completed
  policy.
- [ ] Move descriptor versus data-buffer interoperability selection into
  completed policy.
- [ ] Audit array category, source shape, target/addressability, optionality,
  projection, and layout conversion so only mechanical representation lowering
  remains.
- [ ] Remove readiness decisions and unsupported-contract policy from lowering.
- [ ] Prove lowering does not mutate the readiness-approved input.
- [ ] Preserve backend-local creation of scopes, names, temporaries, imports,
  statements, and expressions.

## Phase 6 — Bridge And Binding Dispatch

- [ ] Ensure bridge and binding modules cannot import or call
  `OwnershipPolicyResolver`, `default_ownership_policy`, policy completion, or
  readiness.
- [ ] Route semantic behavior through explicit dispatchers keyed by completed
  codegen actions or typed completed policy selectors.
- [ ] Reject missing dispatcher combinations without choosing a default.
- [ ] Remove policy inference based on datatype, `intent`, rank/shape alone,
  `is_alias`, local memory handling, dotted variables, parser origin, or missing
  policy.
- [ ] Limit branches inside selected implementation methods to emitted-code
  mechanics.
- [ ] Represent backend-local helper temporary storage separately from semantic
  `OwnershipDecision` so local implementation details cannot be mistaken for
  contract policy.
- [ ] Prove bridge generation does not mutate or replace completed policy carried
  by codegen IR.
- [ ] Prove binding generation does not mutate or replace completed policy
  carried by bridge/codegen IR.
- [ ] Keep low-level printers free of ownership-aware behavior selection.

## Phase 7 — Printers And Build Orchestration

- [ ] Remove hidden policy completion from `emit_module_stubs()` and other
  printer entrypoints.
- [ ] Make `.pyi` emission orchestration explicitly select the required semantic
  stage before invoking the printer.
- [ ] Make direct source builds visibly call parse, semantic conversion, policy
  completion, readiness, lowering, bridge/binding generation, and compilation
  in order.
- [ ] Make semantic `.pyi` builds visibly call `.pyi` parsing/conversion, native
  contract validation, policy completion, readiness, lowering, bridge/binding
  generation, and compilation in order.
- [ ] Ensure inspection-only CLI stages stop at their declared representation
  and do not mutate it for a later report in the same command.
- [ ] Ensure native array build requirements consume completed/readiness-approved
  policy rather than reconstructing descriptor needs.
- [ ] Remove legacy entrypoints or permissive stage coercions instead of keeping
  compatibility paths.

## Phase 8 — Mechanical Architecture Tests

- [ ] Raw semantic draft is rejected by prepared-readiness entrypoints.
- [ ] Raw semantic draft is rejected by lowering.
- [ ] Policy-completed but readiness-unvalidated IR is rejected by lowering.
- [ ] Removing each required policy category is detected by the recursive stage
  validator before lowering starts.
- [ ] Missing getter, setter, return, class-instance, class-self, array-handle,
  storage, barrier, and interoperability decisions cannot become `None`.
- [ ] Policy completion does not mutate its input draft.
- [ ] Mutating the draft after completion cannot affect completed IR.
- [ ] Readiness does not mutate completed IR or any completed decision.
- [ ] Lowering does not mutate readiness-approved IR or any completed decision.
- [ ] Bridge generation does not mutate or recompute policy.
- [ ] Binding generation does not mutate or recompute policy.
- [ ] Policy completion rejects already-completed input.
- [ ] Wrapper build orchestration invokes stages in the exact documented order.
- [ ] Every stage transition returns a different object from its input and the
  input retains the same stable fingerprint after the call.
- [ ] Parsed-project, semantic-draft, completed, wrappable, codegen, bridge,
  binding, build-plan, and build-result boundary collections reject ordinary
  supported mutation operations.
- [ ] Frozen stage results contain no reachable mutable list, set, dictionary,
  mutable metadata dictionary, or mutable semantic child object.
- [ ] Mutable parser, semantic, lowering, bridge, binding, and build builders are
  not exported from their package's public stage API.
- [ ] Structural AST tests reject prohibited resolver/completion imports from
  lowering, bridge, binding, and printer packages.
- [ ] Structural AST tests reject prohibited raw-fact policy inference in bridge
  and binding code.
- [ ] Structural tests allow narrowly identified backend-local helper planning
  without allowing semantic policy construction in generators.
- [ ] Structural dependency tests enforce the permitted package direction:
  parsing cannot import semantics; semantics cannot import lowering/codegen;
  readiness cannot import lowering; lowering cannot import bridge/binding;
  bridge/binding cannot import parsers or semantic policy resolvers; printers
  cannot invoke earlier stage transitions.
- [ ] Structural dependency tests allow the high-level pipeline orchestrator to
  import and compose stage entrypoints without making orchestration policy
  authority.
- [ ] Runtime-handle tests continue to prove intentional allocation,
  association, ownership, and close-state mutation despite immutable pipeline
  artifacts.
- [ ] Missing dispatcher combinations fail explicitly.
- [ ] Export pruning remains before readiness/lowering, and omitted declarations
  never reach codegen.
- [ ] Semantic `.pyi` round-tripping preserves the editable contract.
- [ ] Source, generated-contract, and modified-contract runtime behavior remains
  unchanged unless an explicitly documented blocker moves earlier.

## Phase 9 — Focused Evidence

- [ ] `tests/semantics/policy/` covers immutable completed
  policy, complete recursive decision sets, and strict dispatcher behavior.
- [ ] `tests/semantics/readiness/` covers the completed-to-
  validated transition and non-mutating readiness.
- [ ] `tests/lowering/test_semantic_ir.py` covers validated-only lowering and absence
  of policy/readiness inference.
- [ ] `tests/codegen/printers/` covers printer-only emission without
  hidden policy completion.
- [ ] `tests/parsing/pyi/` covers semantic draft construction and
  contract round-tripping.
- [ ] `tests/wrapper/fortran/edit_pyi_contracts/` proves edited policy remains
  authoritative through runtime behavior.
- [ ] `tests/architecture/test_dependency_boundaries.py` enforces
  dependency and inference restrictions mechanically.
- [ ] Source and semantic `.pyi` build-mode tests prove the mandatory stage
  sequence.
- [ ] Focused wrapper tests cover scalar, string, array, descriptor, derived
  type, callback, module-variable, and optional-argument boundaries.
- [ ] LAPACK remains excluded from local verification unless separately
  authorized.

## Phase 10 — Verification And Completion Record

- [ ] Focused semantic, `.pyi`, codegen-structure, build-mode, and wrapper tests
  pass.
- [ ] `python3 -m ruff check .` passes.
- [ ] `python3 -m ruff format --check .` passes.
- [ ] Bandit passes with the repository configuration.
- [ ] Vulture passes.
- [ ] The blocking Radon policy passes with an explicit base fallback when local
  CI SHA variables are unavailable.
- [ ] Full Radon complexity and maintainability reports are run and recorded as
  advisory output.
- [ ] `git diff --check` passes.
- [ ] No compatibility shim, fallback path, or legacy stage entrypoint remains.
- [ ] The final implementation report lists every blocker moved, every stage
  representation introduced, every downstream inference removed, and every
  remaining limitation.
- [ ] This checklist is moved from active work to completed evidence only after
  every requirement above has direct test or structural evidence.
