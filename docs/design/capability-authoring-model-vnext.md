# Capability & Authoring Model vNext

Status: **BREAKING VNext IMPLEMENTATION BASELINE (5GC source migration in progress)**  
Scope: ca-skills authoring language and contracts. This is a design proposal, not an implementation claim. v0.2 remains authoritative until a separately reviewed migration is approved.

## 1. Goals

Unify Capability, Operation, Procedure, Predicate, data binding, Schema ownership, and Evidence semantics. Reduce repetitive YAML without hiding behavior. Keep builds deterministic, inspectable, reproducible without Skill Studio, and preserve the 5GC business behavior and evidence guarantees. This is a new Demo-stage version: no v0.2 compatibility layer or dual syntax is required.

## 2. Semantic model

### 2.1 Capability, Operation, Tool

- Capability is a stable logical ability identity and authorization/grouping boundary.
- Operation is the exact callable interface exposed under a Capability; it declares Effect and Input/Output contracts.
- Initial Effects remain READ and MUTATION.
- Tool is an implementation/registration unit exposing Operations, not a second authoring-level capability identity.
- Procedure calls and Predicate data dependencies use the same exact Operation ID namespace.
- The Capability contract explicitly enumerates the exact Operations grouped under each Capability. A Skill grant authorizes only that declared membership; no hierarchy, naming convention, Tool display name, or implicit expansion may add Operations. Compiler verifies exact membership and Effect agreement; Runtime still performs deployment admission and authorization.

### 2.2 Fact, Observation, acquisition

These terms must not be collapsed:

- **Fact**: a statement about domain, environment, or execution state.
- **Observation**: a captured, scoped representation of a Fact with source and temporal context. It is a result/data concept, not a separate callable identity, Tool category, or registry.
- **Acquisition**: obtaining an Observation. A governed READ Operation is the normal callable interface for querying an authoritative current or stored fact.
- Observations may originate from asynchronous events, Environment snapshots, or Runtime journals/projections. The original event producer, fact owner, projection/storage owner, and reader may be different components.
- A Fabric event is not itself a READ Operation. A READ Operation over Fabric's journal/projection is. Event time must remain distinguishable from receipt/acquisition time.
- The independent Observation Ref → Observation Source registry is to be retired through behavior-preserving migration. Its useful ownership, provenance, scope, and evidence semantics must move to the relevant fact/Operation contracts and governed bindings.

Thus, Observation is not synonymous with an Operation output, and not every READ output is automatically an Observation suitable for assurance. A READ Operation is a standard way to acquire one.

### 2.3 Evidence

- Evidence is validated support for a factual claim, not the Fact payload and not another Capability.
- The authoritative producer declares its guarantees; a trusted collector/adapter attests only to what it actually observed; Host defines the generic Evidence envelope; Runtime validates it.
- Preserve distinct temporal meanings where applicable: event/occurrence time, source observation time, collector receipt/acquisition time, Runtime processing time. Never relabel receipt time as observation time.
- Evidence requirements may include provenance, scope/correlation, freshness, completeness, and integrity.
- A successful Mutation response (including HTTP 201) proves the operation response, not automatically the resulting external state.
- Runtime preserves PASS / FAIL / UNKNOWN. Missing, stale, uncorrelated, conflicting, or insufficient evidence must not become PASS.

### 2.4 Predicate

- Predicate declares a condition and deterministic evaluation logic over explicitly supplied inputs and evidence.
- Predicate evaluation is pure with respect to external acquisition: it must not secretly call Tools, Providers, or network reads.
- Predicate may consume a prior Operation output, an Observation acquired by a prior READ Operation, or both.
- If a current/independent fact must be read, Procedure (or another explicit orchestration construct) schedules the READ Operation. Its output/evidence is then bound to the Predicate.
- Predicate retains PASS / FAIL / UNKNOWN semantics and does not name Provider endpoints, Fabric routes, adapters, or implementation classes.
- Predicate evaluation is pure. All required acquisition is represented explicitly by a READ Operation or a captured invocation Context projection at the exact control-flow point. No implicit ObservationSource lookup remains in the target model.

## 3. Unified authoring and reference rules

- Procedure call and Predicate input dependencies reference the same exact Operation ID namespace.
- No independent Observation Ref namespace is introduced for callable fact acquisition.
- Procedure and Predicate use the same source-reference vocabulary and Binding Plan machinery.
- with/from remains available for exceptional mappings, overrides, and disambiguation; it is not routine boilerplate.
- No implicit previous-node binding, field-name guessing, string interpolation, dynamic selector, or Runtime parameter guessing.
- Every effective binding must have a unique, type-compatible, statically identifiable source and be valid on every path where consumed.
- Ambiguous or unresolved bindings are compile errors with actionable diagnostics.
- Repository source plus versioned shared contracts must be sufficient to compile without Studio state.

## 4. Binding model and Binding Plan

### 4.1 Three kinds of binding information

1. **Context projection**: Procedure declares which approved invocation-context namespaces/projections it can use. A shared Context Contract defines their fields, semantic identities, types, and guarantees.
2. **Producer/consumer dataflow**: Operation outputs and other declared producers may feed later Operation inputs or Predicate inputs. Compiler resolves these from explicit contracts, schemas, control flow, and unique producer relationships.
3. **Exceptional explicit mapping**: author provides a local mapping (currently with/from) when defaults are absent, override is intentional, or disambiguation is needed.

Do not add a mandatory bindings.yaml merely to relocate every with entry. Keep binding close to its Procedure/Predicate dataflow unless migration evidence demonstrates a separate file is materially better.

### 4.2 Ownership

- Operation Contract owns parameter names, types, requiredness, and semantic input requirements. It must not hard-code Host-specific paths such as subject.ueRef or request.pduSessionId.
- Shared Context Contract defines available context fields, semantic identities, types, and guarantees.
- Skill/Procedure declares its context projection and intentional mappings from context/producers to Operation inputs.
- Deployment may provide environment-specific binding overlays only if explicitly permitted by a versioned contract; overlays must be inspectable and included in build identity, never hidden mutable Runtime state.
- Compiler resolves the effective Binding Plan. Runtime executes it and validates actual values; Runtime does not infer sources.

### 4.3 Deterministic automatic resolution

Compiler may auto-resolve only when:
- target input is known from the Operation Input Schema/contract;
- eligible source is explicitly exposed by Context Contract or produced by a declared Operation;
- semantic identity/contract compatibility is established, not merely similar property names;
- type and nullability are compatible;
- source is definitely available on every path reaching the consumer;
- no competing source or conflicting override exists.

Rules:
- one valid source: auto-bind;
- no source for a required input: compile error;
- multiple valid sources: require author/Studio disambiguation;
- no source for an optional input: leave absent; invent no default;
- conditionally produced source: reject unless control-flow analysis proves availability or an explicit guarded/optional construct validates it;
- conversions are never implicit; any conversion is a declared deterministic transform with input/output contracts and provenance behavior.

Field-name equality alone is not a semantic binding contract. A stable semantic-field identifier vocabulary may be needed; its exact representation remains open.

### 4.4 Source versus generated plan

- Author-declared context projections and exceptional mappings are persisted in Skill source.
- Unique contract-derived mappings are not repeated in every node's YAML.
- Compiler emits a complete explicit Binding Plan in its intermediate/compiled artifact: target input, source identity/path, schema/type, producer identity, path availability, and declared transforms.
- Studio displays generated and authored mappings, their origin, and validation state. Editing a generated mapping persists a source-level override/projection, never Studio-only state.
- A “materialize/fix binding” action may write a generated choice to source when a stable explicit override is desired; it is not required for deterministic builds.

### 4.5 Procedure and Predicate share the model

- Procedure Operation inputs and Predicate evaluator inputs use the same Binding Plan machinery.
- Predicate has no separate Observation Binding registry or binding dialect.
- Predicate inputs come from declared context/producers or explicitly scheduled READ Operations.
- READ acquisition is visible in the execution/dataflow plan and audit trail; it is never hidden inside verify.

## 5. Requiredness and validation

- Public Skill request requiredness belongs to the Skill-owned Request JSON Schema.
- Operation input requiredness belongs to the Operation Input Schema owned by its contract owner.
- Procedure-specific public inputs, if needed, have an explicit Procedure input contract and do not duplicate Operation requiredness.
- Context availability belongs to the Context Contract / Procedure context projection. Existing spec.context.requiredFacts identifies required fact identifiers; it is not a field-level schema.
- Predicate inputs inherit requiredness from their declared input contract and referenced producer outputs.
- Compiler checks schema/reference validity, binding completeness, type/nullability, producer availability, and statically knowable control/data dependency order.
- Runtime checks actual values, dynamic presence, freshness, correlation, and Evidence validity.
- Do not repeat requiredness in every with mapping.

## 6. Schema and contract ownership

| Schema / contract | Owner |
|---|---|
| Public Skill Request Schema | Skill |
| Operation Input/Output Schema | Operation/Tool contract owner |
| Shared Context Contract/Schema | Host contract authority, versioned and consumed by Skills |
| Generic Evidence Envelope | Host |
| Source/evidence guarantees | Authoritative producer and trusted acquisition adapter, limited to what each can attest |
| Normalized projection Schema | Explicit projection/normalization owner |
| Predicate-specific evaluation projection | Skill, only for its own derived/selected view; must not redefine producer payload |
| Script input/output contract | Skill |

From the Skill author's perspective, Schemas primarily constrain **inputs consumed by Procedure Scripts and Predicates**. When that payload is produced by a READ Operation, the same owner-published payload Schema serves as that Operation's Output Schema and the consumer's input contract; do not create a second copy just because it crosses a producer/consumer boundary. A Predicate interface may declare the semantic fields it consumes when it combines several sources or reshapes Host Context plus Evidence; the Compiler derives the effective Script input contract from those declarations and all call sites. This does not create a separate authored Script Input Schema, and it must not redefine an owner's payload.

An Observation acquired through a READ Operation uses that Operation's Output Schema. Do not duplicate the same payload schema under observations. If an event/journal/projection changes the structure, that projection owner owns its schema. Transformations require explicit input/output contracts and preserve lineage to source evidence. Host must not invent domain schemas.

## 7. Procedure and Predicate relationship

- Procedure describes execution order, control flow, explicit calls, and data dependencies.
- Predicate describes a condition and its evaluation logic.
- Procedure schedules READ when independent/current authoritative state is needed, then verifies the Predicate using the result/evidence.
- Predicate may consume a preceding Operation output if it meets the declared assurance requirements; avoid redundant READ.
- Predicate may combine Procedure-provided inputs and multiple READ outputs.
- Mutation response alone does not prove resulting external state.
- Event-driven facts remain supported: Procedure can read an authoritative event/journal/projection through its READ Operation; evidence preserves event time separately from acquisition/receipt time.

## 8. YAML authoring conventions

### 8.1 File names

Do not rename files solely to make singular/plural forms uniform. Keep current contract.yaml, procedure.yaml, and predicates.yaml as candidate vNext entry names unless concrete tooling/authoring evidence justifies a coordinated rename. The earlier requirement to rename procedure.yaml to procedures.yaml is withdrawn. File names identify canonical entry points; the top-level YAML shape determines resource cardinality.

External single-resource definitions may retain descriptive suffixes such as *.tool.yaml and *.schema.yaml. Avoid superficial cross-repository churn.

### 8.2 Field names and shape

- Structural fields use camelCase, consistent with apiVersion, requestSchema, requiredFacts.
- Operation input property names match the Operation Input Schema exactly.
- Capability/Operation IDs use stable dot-separated names; Procedure node names and file/directory names use kebab-case.
- Keep one canonical shape per concept; maps for named Procedure/Predicate identities, lists for ordered steps/requirements.
- Keep routine calls concise; do not require repeated with for every input if Binding Plan resolves it deterministically.
- Keep exceptional mappings explicit and near their owner. Exact placement (node-level with versus Procedure-level bindings) remains open until real Skill migration proves the better form.
- Do not add bindings.yaml at this stage.
- Retain the existing apiVersion/kind resource envelope where applicable; do not invent another envelope.

## 9. Skill Studio responsibilities

Studio is a source editor and visual authoring surface, not an independent configuration authority.

Binding Editor should:
- show Operation inputs, resolved source, source kind (Context / producer / explicit), schema/type, nullability, and validation;
- suggest only contract-valid candidates;
- explain uniqueness, ambiguity, incompatibility, or unreachable paths;
- allow explicit selection/override and persist it to Skill source;
- show reverse dataflow (consumers of a producer output);
- refresh diagnostics when nodes, schemas, context projections, or control flow change;
- expose the complete generated Binding Plan for inspection without requiring authors to maintain generated entries.

All persisted behavior must be recoverable from repository source and versioned contracts. No binding may exist only in browser storage, local Studio state, or a private database.

## 10. Compiler and Runtime responsibilities

Compiler:
- links exact Capability/Operation identities;
- validates effective authorization requirements for static consistency;
- validates Operation Input/Output Schema references;
- resolves Context and producer/consumer bindings;
- performs type, nullability, requiredness, and control-flow definite-assignment analysis;
- constructs deterministic Binding Plan and execution/dataflow graph;
- validates Predicate input and Evidence compatibility;
- rejects ambiguous, unresolved, or unreachable bindings.

Runtime:
- executes the compiled plan through governed Tool execution;
- enforces effective authorization, Effect, budgets, timeout, and invocation scope;
- validates dynamic values and Evidence;
- preserves correlation, provenance, temporal semantics, freshness, and tri-state outcomes;
- does not guess bindings or own domain payload schemas;
- records which resolved binding and producer supplied each input.

## 11. Breaking migration rules

- vNext replaces the v0.2 Skill authoring and execution model. Do not add compatibility readers, legacy adapters, dual YAML syntax, fallback Schema paths, or compatibility-only projections.
- The current `ca-agent-demo/main` and `ca-skills/main` are behavioral/source references while the migration branch is under development. They are not a runtime compatibility target; once the new branch is accepted, the vNext Skill and its matching owner contracts replace the old source.
- Retire the independent Observation Ref / Observation Source registry and implicit Predicate-time acquisition. Every required current-state read is an explicit READ Operation; captured ingress data is an explicit Context projection; prior Operation data is consumed from that exact Operation output.
- Operation outputs expose the owner-published typed result directly. Do not retain `runtime_value()` wrappers or add Host projection Schemas solely to preserve an old Skill payload. In particular, the UDM Operation returns the full Provider GetSmData result defined by the Provider Output Schema; Host validates the result and attaches separate Host Evidence from the same receipt.
- Retire v0.2 `lib/**` physical-path references in Skill source. External dependencies are referenced by qualified exported contract identity or Schema `$id`; Studio resolves dependency aliases before Compiler input.
- Procedure Script inputs are derived from each call site's bindings. Predicate Script inputs are derived from `Predicate.inputs` and all `verify.with/from` call sites. Script output Schemas are generated from strict return `TypedDict` declarations. No hand-maintained Script Input/Output Schema copies.
- Existing 36 Cases and three References remain the behavioral acceptance corpus. Their fixtures may be updated to the new contract syntax; preserving an obsolete source layout is not an acceptance requirement.
- `establish-pdu-session` is the first executable migration target. MAS remains a structural/reference example only; it is not a prerequisite for 5GC implementation.
- Compiler and Runtime implementation are separate follow-up work. This migration defines and validates the Skill/Owner source contracts; it must not claim the new source is executable until the Compiler and Host Runtime support it.

## 12. First 5GC vNext implementation decisions

The paper review is complete enough to start implementation. The following are the chosen source-model decisions, not compatibility options:

1. **Predicate inputs:** `Predicate.inputs` declares named business inputs and their Evidence freshness requirements. `verify.with/from` binds each input to an exact Context projection or Operation output. Runtime attaches read-only Host Evidence separately at `input.evidence.<alias>`.
2. **Pure evaluators:** CEL expressions read `input.<alias>`. Predicate Scripts use the same `evaluator.script` property as Procedure Script nodes use with `script`. Both references are package-relative paths such as `scripts/evaluate_udm_read.py`.
3. **Context projection:** Procedure `inputs` explicitly projects only the required `context.request`, `context.subject`, `context.facts` and `context.ingress` namespaces. Their external Schemas are referenced by exact versioned `$id`.
4. **Dependency identity:** Tool calls use `createdsession-tools::operation.id`. Capability grants use `deployment-capabilities::capability.id` and are checked against the separate trusted deployment CapabilityContracts BuildRequest input. Neither alias is a repository path or a source locator.
5. **Wait:** `wait` is a Procedure orchestration node over one exact READ Operation. It references the Predicate input whose Evidence policy it must satisfy, repeats the exact READ bindings, and declares only the authoritative-absence policy. Runtime-inherited deadline, cancellation and budget are not Skill inputs.
6. **UDM result:** the Host Tool output is the complete Provider result object, not a `runtime_value()` projection. The Skill consumes the exact `output` and Host attaches Evidence from that same full Provider receipt. No second UDM Get and no separate Host UDM projection Schema.
7. **Observation mapping:** 1 ingress projection becomes Context; 9 prior-Operation projections become direct typed Operation outputs plus same-receipt Evidence; 2 Host journal projections are served by one Host lifecycle-journal READ; 5 independent acquisition points are served by four READ shapes (phase-discriminated N4, RAN setup, N4 forwarding, PCF governance).
8. **Operation/Capability count:** remove `ca.session.evidence.await`; retain the other 11 existing Operations; add five READ Operations (N4 resources, RAN setup, N4 forwarding, PCF governance, Host lifecycle journal). The target has **16 callable Operations** and **8 Capability grants**. `wait` is not an Operation or Capability.
9. **Bindings:** 5GC identity-sensitive bindings remain explicit. Automatic binding is enabled only when semantic identity, type/nullability and control-flow availability are contract-proven; matching field names alone never authorizes a binding.

### Remaining implementation gates

- Publish the exact READ Operation Input/Output contracts and Capability membership for the five new READ Operations.
- Extend existing Operation Output contracts where the old ObservationSource projected additional fields from the same attempt-local result; return those fields directly from the producing Operation.
- Publish the Host ingress Context Schema and Host lifecycle-journal READ output contract.
- Accept and link the Provider GetSmData result Schema, then make the Host adapter return that exact typed result unchanged.
- Implement the chosen Predicate input / Evidence / wait syntax in the Skill source. Compiler and Runtime support will follow as a separate implementation.
- Rebind all 36 Cases to the new source contract and verify the 3 References still describe the same business semantics.

The detailed source mapping remains documented in [Binding Migration Rehearsal](binding-migration-rehearsal-vnext.md), but no separate migration rehearsal is required before implementation.

## 13. Source-backed observation mapping

See [Observation Owner and Acquisition Inventory](observation-owner-inventory-vnext.md) for source ownership and [Binding Migration Rehearsal §19](binding-migration-rehearsal-vnext.md#19-complete-17-ref-predicate-input-and-acquisition-migration) for the corresponding Procedure points and target inputs. All **17** 5GC Predicate Observation refs are mapped; the two additional `ref` entries identify Script evaluators, not Observations. MAS still requires an authoritative snapshot owner/READ contract. Exact vNext READ Operations and Schema/Evidence exports remain open; no running source has been removed.

## 14. Semantic field identity and pinned-fixture Compiler spike

See [Semantic Field Identity Contract vNext](semantic-field-identity-vnext.md) for the proposed `x-ca-semanticId` JSON Schema annotation, owner boundaries, and eleven MAS common context field identities. These are design-level annotations, not yet supported by v0.2. An ID alone is not proof of scope, type, control-flow availability, or producer identity; exact resource handles remain explicit without stronger contracts.

Compiler [Draft PR #7](https://github.com/odango-chan/ca-skill-compiler/pull/7) now includes an additional `real_fixture_test.go` intended to read pinned MAS / 5GC Procedure and ToolCatalog files and compare proposed auto-bindings with existing `with/from` mappings. Its new fixture tests have been committed but **not yet independently executed/verified**; the earlier synthetic Go unit tests passed locally. No Compiler mainline integration is claimed.


## 15. Dependency identity versus local `lib/` layout

**Decision: Skill source must not bind to physical `lib/` paths, and must not become a second dependency manifest.**

The frozen Skill Studio Plugin-managed Configuration v0.1 already owns project dependencies and locks through native resource-scoped Workspace Configuration (`connectionAgent.skillStudio.dependencies` and `connectionAgent.skillStudio.dependencyLock`). Therefore do not add `dependency:`, repository/source/revision/digest/cache fields, `skill-project.yaml`, or `skill.lock.yaml` to Skill source.

Separate three concerns:

- **Skill source**: names the qualified exported contract it consumes as `<dependency-alias>::<exported-contract-id>` (for example `fivegc-tools::sbi.udm.sm_data.get` or `host-contracts::ca.host.context/subject.v1`). The alias is a stable logical namespace for the locked dependency snapshot, not acquisition configuration. Skill source does not select a source, repository, version, revision, digest, cache key, or local path.
- **Studio Workspace Configuration**: owns dependency selection and source acquisition (Upload, MCP discovery, Git, Built-in), dependency aliases/identity, pinned source revision, lock/integrity metadata, immutable snapshot persistence, import/refresh/Update Lock, export and cache. It maps the Skill's exported contract references to the exact locked snapshot(s). Credentials never enter Skill source or Compiler input.
- **Compiler**: receives Skill source plus already-resolved immutable dependency snapshots through its versioned in-memory BuildRequest. It verifies canonical snapshot digests and links exact exported contract identities. It does not fetch, select, lock, cache, update or persist dependencies.

The read-only **Dependencies** TreeView is the user-facing projection of these snapshots. Do not create a fake `lib/` or `output/` Explorer folder merely to represent them; a physical `lib/` directory is neither required nor the source of truth. The Compiler must not require a global `lib/**` path namespace as the identity of a dependency.

The vNext Skill source contains no physical `lib/...` dependency paths. External Context Schemas are referenced by their exact exported `$id`; Tool Operations and Capabilities are referenced through logical aliases resolved by Studio/BuildRequest. The v0.2 `lib/...` form is removed from the migrated Skill rather than interpreted by a compatibility reader.

For the vNext schema-reference design, use the exported JSON Schema `$id` as the stable contract identity:
- each externally owned standalone Schema declares a globally unique, versioned absolute `$id` (URN form is recommended, e.g. `urn:connectionagent:host:context:subject:v1`);
- `spec.context.schemas.subject/facts/evidence` reference those exact IDs, not dependency IDs or paths;
- Compiler indexes only the supplied immutable snapshots and resolves exact `$id` matches; it never performs network resolution;
- duplicate IDs, missing IDs, duplicate exports, unsupported dialects and incompatible schemas fail closed;
- the Owner controls and versions the ID. A changed incompatible contract requires a new versioned ID.

The generic Observation/Evidence envelope and domain Observation payloads remain distinct. A READ Operation's Output Schema owns its domain payload; the shared Host/Runtime contract owns only the generic envelope/provenance fields. Do not invent one aggregate Observation Schema ID that claims to describe all 5GC payloads. The exact treatment of legacy `spec.context.schemas.observations` is part of the Predicate/READ acquisition migration, not a shortcut in this dependency change.

A logical dependency alias may appear only as the namespace prefix of an exported contract reference; Skill YAML never contains a dependency source locator, repository, source kind, revision, digest, cache key, or physical path. Studio Workspace Configuration maps aliases to locked snapshots. Compiler receives snapshot bytes and verifies their input digest. Compiler does not export digest values in BuildResult.

The 5GC Host Subject / Facts / Ingress / Evidence contracts remain external Owner dependencies. Skill must not copy their bodies into its own package, and Studio must not fabricate missing owner files. See [Dependency Identity & 5GC Owner Schema Resolution](dependency-identity-and-owner-schema-resolution-vnext.md) for the cross-repository inventory and acceptance gates.

The stable Schema identity rule (`$id`) is the selected vNext direction; the complete Skill Language syntax and breaking migration are not yet frozen. Existing v0.2 source and Compiler behavior remain authoritative until a separately reviewed migration is implemented.


### Capability grants and Tool Operation linking

The Skill grants qualified Capability identities in `allowedResources.capabilities` (`capability-contract-alias::capability-id`); a Procedure node calls one exact qualified Operation (`tool-dependency-alias::operation-id`). The independent, deployment-owned CapabilityContracts maps each Capability to its owner and exact Operations with expected Effects, while ToolCatalog declares each callable Operation's schemas and declared Effect. For static proof, the Compiler BuildRequest must receive the target deployment's immutable CapabilityContracts as an explicit trusted input **separate from ordinary Skill dependency snapshots**; the ToolCatalog remains part of the resolved dependency set. Compiler then proves every Procedure Operation belongs to exactly one Capability, that the Skill grants that qualified Capability, and that the Tool Effect matches the independently declared expected Effect. If the trusted CapabilityContracts input is absent, the Compiler cannot claim static authorization proof; Runtime admission remains authoritative. The migrated Skill grants the eight exact qualified 5GC Capability IDs, not Operation IDs. The deployment-owned CapabilityContracts input is the sole authority for each Capability's owner, Operation membership and expected Effect. The Skill never defines or duplicates those memberships. There is no Observation Ref namespace or implicit Observation provider in vNext: current facts are supplied by explicit Context projections, prior Operation outputs, or explicit READ Operations.


## 16. Candidate 5GC Predicate inputs and explicit bounded wait (NOT FROZEN)

The source rehearsal supports a small authoring surface that reuses the existing v0.2 binding vocabulary rather than inventing a second Observation binding language.

### 16.1 Pure Predicate inputs

Candidate:

```yaml
predicates:
  createdsession.udm.subscription_usable:
    inputs:
      udmReadResult: {}
    evaluator:
      type: script
      ref: scripts/evaluate_udm_read.py
```

Procedure postcondition:

```yaml
- verify: createdsession.udm.subscription_usable
  with:
    udmReadResult:
      from: nudm-sdm-get.output.result
```

Semantics:

- `Predicate.inputs` declares the Predicate's named input interface. The Procedure's `verify.with/from` supplies those values using the same source-reference vocabulary and Binding Plan as ordinary Operation inputs. This keeps Predicate logic reusable and keeps producer-specific node names out of the Predicate definition.
- The evaluator receives only the declared values. The Compiler derives the effective Predicate input projection from the Predicate interface plus all Procedure `verify.with/from` call sites and their producer schemas/Context contracts; multiple call sites must provide compatible inputs. No separate Script Input Schema file is required.
- Runtime attaches the Host Evidence projection to each producer-backed input under `input.evidence.<alias>`. Evidence is a separate provenance object, not merged into the business payload and not an arbitrary Skill-authored value.
- The Binding Plan records parallel lineage for each consumed value and its Evidence: exact producer, source path, schema/owner, invocation/scope, and the Evidence refs/guarantees attached to that producer. A Script cannot invent or rewrite Evidence refs.
- The Script changes from reading `input.observations.response` / implicit `input.subject.udmReadReceipt` to the declared `input.udmReadResult`. Its strict Output TypedDict remains unchanged.
- A CEL Predicate uses the same `inputs` map and evaluates those declared names. No acquisition occurs inside `verify`.

The migrated UDM Operation returns the full Provider GetSmData result directly as `nudm-sdm-get.output`. The Predicate binds that exact object as `udmReadResult`; Host attaches Provider Evidence correlated to the same invocation/transaction/record. No wrapper, `runtime_value()` projection, attempt-local ObservationSource lookup or second network Get is required.

Provider PR [#50](https://github.com/odango-chan/ca-provider-5gc/pull/50) proposes the full upstream GetSmData result Schema with an absolute but still proposed `$id`. After Provider acceptance, the Host adapter refreshes its pinned snapshot/digest and returns the validated Provider result unchanged. ToolCatalog `sbi.udm.sm_data.get` Output Schema references the Provider result `$id`; Host Evidence remains a separate Host-owned envelope and is attached to that same result.

The selected vNext path binds the exact full Provider result returned as the Tool Operation output and Host Evidence attached to the same receipt, correlated by invocation, transaction, request, record/digest, target/source provenance and freshness. The Provider-owned result Schema is both the Provider response contract and the Skill-facing Operation Output Schema. Host does not reshape the business payload.

For the Hold path, the same shape consumes the preceding `ca.session.udm_hold.bind` output plus its Host Evidence. The Tool output carries the held-request details but not normalized `bindingStatus`. The current ObservationSource rechecks the exact selector, held-request correlation, lifecycle and deadline against the attempt-local record, then attaches Fabric Evidence. Preserve those checks in a typed local projection over that same stored artifact; do not synthesize `CURRENT` from call success and do not trigger another Fabric pending-Hold request.

### 16.2 Explicit wait over a READ Operation

Candidate:

```yaml
nodes:
  await-initial-resources:
    wait:
      read: fivegc-reads::n4.initial_resources.read
      with:
        ueRef:
          from: input.ue-ref
        pduSessionId:
          from: input.psi
        pti:
          from: input.pti
        requestType:
          from: input.request-type
        ingressRef:
          from: input.ingress-ref
        pcfPolicyAssociationRef:
          from: npcf-sm-policy-control-create.preconditions.resolve-pcf-create-inputs.output.pcfPolicyAssociationRef
        lifecycleRef:
          from: input.lifecycle-ref
        phase: POST_CREATE
        baselineRef:
          from: read-n4-baseline.output.baselineRef
      absencePolicy: CONTINUE
    'on':
      SUCCEEDED: read-initial-resources
      UNKNOWN: unresolved

  read-initial-resources:
    call: fivegc-reads::n4.initial_resources.read
    with:
      ueRef:
        from: input.ue-ref
      pduSessionId:
        from: input.psi
      pti:
        from: input.pti
      requestType:
        from: input.request-type
      ingressRef:
        from: input.ingress-ref
      pcfPolicyAssociationRef:
        from: npcf-sm-policy-control-create.preconditions.resolve-pcf-create-inputs.output.pcfPolicyAssociationRef
      lifecycleRef:
        from: input.lifecycle-ref
      phase: POST_CREATE
      baselineRef:
        from: read-n4-baseline.output.baselineRef
    postconditions:
      steps:
        - verify: createdsession.n4.initial_resources_ready
          with:
            resources:
              from: read-initial-resources.output

```

Predicate interface (the evaluator consumes only the declared input):

```yaml
predicates:
  createdsession.n4.initial_resources_ready:
    inputs:
      resources: {}
    evaluator:
      type: cel
      expression: input.resources.bindingStatus == "CURRENT" && input.resources.defaultFlowInstalled == true && input.resources.uplinkEndpointBound == true
```

Semantics:

- `wait` is a Runtime orchestration node, not a Tool Operation or Capability. It reuses the current bounded waiter policy (invocation deadline/budget, cancellation, exact scope/correlation and `KNOWN_ABSENT/CONTINUE`) but calls the exact declared READ Operation instead of routing through `ObservationSource`.
- The referenced READ Operation must be exact, Effect=READ, present in the resolved Tool/Capability contract set, and covered by the Skill's Capability grant. Compiler validates the reference and input mapping; Runtime rechecks authorization.
- The wait returns only its bounded-wait outcome and audit/evidence refs. It does not pass its last payload as the Predicate input. `KNOWN_ABSENT` follows the declared absence policy; `UNKNOWN` remains non-PASS and is retried only within the same invocation budget/deadline, then routes unresolved. For the N4 example, `POST_CREATE` wait and final READ both consume the exact `baselineRef` captured by the earlier `PRE_CREATE` READ; the final result must echo it as `baselineEvidenceRef` and provide the confirmed `currentSessionInstanceRef`.
- The following explicit READ call obtains the final typed payload and Evidence; the Predicate consumes those declared inputs. This preserves the current wait acquisition followed by final Predicate acquisition and does not treat Evidence refs as payload.
- The wait uses the same declared freshness/correlation requirements as the final Predicate input; the exact syntax for sharing that declaration remains open. Budget and deadline remain invocation-inherited Runtime controls, not arbitrary Skill overrides.

The three current `ca.session.evidence.await` nodes become Procedure `wait` nodes over N4 initial resources, RAN setup and N4 forwarding. N4 baseline and post-N4 initial-resource checks share one phase-discriminated READ Operation: `PRE_CREATE` preserves `NO_N4_PAIR / EXISTING_PAIR`; `POST_CREATE` preserves `NO_N4_PAIR / NEW_PAIR`. The Pre-Create read returns `baselineRef`; the Post-Create read consumes that exact handle, returns matching `baselineEvidenceRef` and the confirmed `currentSessionInstanceRef`. RAN setup and N4-forwarding reads consume that exact instance ref. PCF governance is a direct Fabric READ Operation, not a wait.

### 16.3 What this candidate does not solve yet

The first UDM / Hold / N4 slice demonstrates the core boundary, but not all 17 refs are ready to migrate:

- `createdsession.procedure_context` is a captured ingress-event projection. ca-agent-demo PR [#200](https://github.com/odango-chan/ca-agent-demo/pull/200) proposes its `procedure-context` payload Schema; PR #198 Subject/Facts still exposes only the ingress/lifecycle handles. The payload export remains Draft/unmerged and must preserve the trusted ingress event's source provenance.
- `createdsession.lifecycle_registration` and `createdsession.resource_responsibility` read the Host reference journal. PR #200 proposes both normalized payload Schemas; their source authority is the Agent reference journal, not Provider/Open5GS state. Keep them distinct from static Subject/Facts fields. These exports remain Draft/unmerged and must use the actual Host journal owner identity.
- The nine prior-Operation-owned local projections are folded into the exact producing Operation outputs. Where the current Tool returns only a handle, expand that Operation Output to include the already-derived typed result and attach Evidence from the same receipt. Do not add another external read or retain a parallel ObservationSource.
- The full Runtime `ObservationEvidence` envelope remains Host-internal by design. Skill consumes each Owner/adapter domain Output Schema plus the narrow Host Script Evidence-reference projection; do not publish one aggregate Observation payload Schema or the full internal envelope merely to satisfy a Compiler file-count target.

### 16.4 Impact on the current 5GC Operation set

The current Skill has 12 unique Operations, including `ca.session.evidence.await`. Under this candidate, the three wait nodes become Procedure orchestration and the old wait Operation leaves the Skill grant. Four exact owner READ Operation identities are added: N4 initial resources, RAN setup, N4 forwarding and PCF governance. That yields **15 unique callable Operations** (11 retained + 4 new); the wait construct itself is not a Capability member.

The target ToolCatalog and Capability contract set contains 16 callable Operations: 11 retained existing Operations plus five new READ Operations. The `wait` construct is orchestration and is not a callable Operation.

The complete behavior-preserving semantic Procedure outline—covering all 17 Predicate inputs, the two fresh lifecycle gates, the three bounded waits, four owner READ shapes, exact Operation reuse, and reconciliation/finalization paths—is recorded in [Binding Migration Rehearsal §22](binding-migration-rehearsal-vnext.md#22-behavior-preserving-target-procedure-outline-syntax-neutral-not-frozen). It is deliberately syntax-neutral; §16 remains a candidate, not frozen YAML.
