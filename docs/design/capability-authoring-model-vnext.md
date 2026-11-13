# Capability & Authoring Model vNext

Status: **BREAKING V1ALPHA2 IMPLEMENTATION BASELINE (5GC source migration in progress)**  
Scope: ca-skills authoring language and contracts. v1alpha2 is a breaking replacement for v0.2. The migration branch is not yet executable until the Compiler, Host Runtime and Owner contracts are updated; v0.2 remains on the existing mainline only as the pre-migration baseline, not as a compatibility target.

## 1. Goals

Unify Capability, Operation, Procedure, Predicate, data binding, Schema ownership, and Evidence semantics. Reduce repetitive YAML without hiding behavior. Keep builds deterministic, inspectable, reproducible without Skill Studio, and preserve current 5GC behavior and evidence guarantees.

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
- **Compatibility note:** current v0.2 Host `PredicateEngine.evaluate()` acquires each declared `observations` entry during Predicate evaluation through `CompositeObservationSource`. Making Predicate pure is therefore a breaking execution-model change. Migration must schedule equivalent acquisition at the same control-flow point and preserve scope, freshness, conditional `when`, evidence validation, UNKNOWN behavior, and trace semantics; it must not eagerly acquire all facts at Procedure entry or duplicate a shared snapshot.

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
- Context availability belongs to the Contract's explicit `contextSchema` binding and Procedure path bindings. There is no separate `requiredFacts` list or field-level context schema authored by the Skill.
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
- Fixed paths identify the source artifact kind. The vNext Compiler target identifies the language version. Do not repeat `apiVersion`, `kind`, `metadata`, `spec`, `skillType` or wrapper maps such as `procedures:` / `predicates:` in source files. `SKILL.md` frontmatter is the single Skill identity source; the Compiler checks it against the package directory.

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

- v1alpha2 replaces the v0.2 Skill authoring and execution model. The v1alpha2 Compiler rejects v0.2 source forms; do not add compatibility readers, legacy adapters, dual YAML syntax, fallback Schema paths, or compatibility-only projections.
- Existing `ca-skills/main` and `ca-agent-demo/main` remain unchanged until the breaking migration is reviewed and merged. They are migration references, not a runtime compatibility target. The new version does not need to load or execute the old source.
- Retire the independent Observation Ref / Observation Source registry and implicit Predicate-time acquisition from the v1alpha2 execution path. Every independent current-state acquisition is an explicit READ Operation; Host admits ingress and supplies its correlation reference in invocation context; prior Operation data is consumed from that exact Operation output plus its same-invocation Evidence.
- Operation outputs expose the authoritative Owner-published or Host-normalized typed result. Preserve domain normalization when it is part of the Host Operation contract; do not confuse a Host-facing result projection with a compatibility adapter. In particular, `sbi.udm.sm_data.get.output.result` remains the Host-normalized `CreatedSessionUDMResult.runtime_value()` payload with its own Host-owned Schema, while the Provider full result Schema validates the upstream HTTP response inside Host. Both derive from the same Provider receipt and Evidence.
- Retire v0.2 `lib/**` physical-path references in Skill source. External dependencies are referenced by alias-qualified exported contract identity or Schema `$id`; Studio resolves dependency aliases before Compiler input.
- Procedure Script inputs are derived from each call site's bindings. Predicate Script inputs are derived from `Predicate.inputs` and all `verify.with` call sites, with Host Evidence attached separately. Script output Schemas are generated from strict return `TypedDict` declarations. No hand-maintained Script Input/Output Schema copies.
- Existing 36 Cases and three References remain the behavioral acceptance corpus. Their fixtures may be updated to the new source contract; preserving an obsolete source layout is not an acceptance requirement.
- `establish-pdu-session` is the first executable migration target. MAS remains a structural/reference example only; it is not a prerequisite for 5GC implementation.
- Compiler and Runtime implementation are separate implementation workstreams, but the source migration must not be declared complete or merged as executable until both support the v1alpha2 contract.

## 12. Migration status and remaining Owner gates

The v1alpha2 language semantics, including the reduced source envelope and explicit context-schema bindings, are frozen in [Skill Language Specification](../skill-language-spec.md); the 5GC source migration is now being implemented against that contract. The source/Owner mapping is consolidated in [Binding Migration Rehearsal §§18–24](binding-migration-rehearsal-vnext.md). The migration uses eight Capability grants, 18 callable Operations when the N4 READ is phase-discriminated, all 17 legacy Predicate inputs, five Skill Script identities, and all 36 Cases / three References as behavioral obligations.

Current cross-repository work remains Draft/unmerged: Host PR #198 publishes Invocation Context and Script Evidence-reference Schemas; Host PR #200 publishes 15 normalized legacy Observation payload Schemas; Provider PR #50 proposes the upstream GetSmData result Schema but has not yet passed CI. The Host-facing UDM `output.result` Schema is separate from the Provider wire Schema and is still a required Owner publication. The four domain READ shapes and two Host journal READ Operations still need exact Input/Output/Evidence contracts and Capability memberships.

The following are implementation gates, not unresolved authoring-language alternatives:

- publish the six new READ Operation contracts (N4 initial resources, RAN setup, N4 forwarding, PCF-create governance, lifecycle registration journal, resource-responsibility journal) and their exact Capability memberships;
- update `ca.session.evidence.await` to target one exact READ Operation with exact bindings, freshness, bounded budget/deadline and absence policy;
- expand existing Operation outputs where a prior-Operation projection currently comes only from a same-attempt stored artifact; preserve the exact stored artifact and same-receipt Evidence, without adding a second network read;
- publish the Host UDM normalized `runtime_value()` Output Schema and link it to ToolCatalog `sbi.udm.sm_data.get.outputSchema.result`;
- publish and link the Host Context projection Schemas and Host Evidence-reference Schema;
- update the Provider wire Schema snapshot only after Provider PR #50 is accepted and its stable `$id` is published;
- migrate all 36 Cases to the v1alpha2 semantic Case contract and keep the three References unchanged;
- implement Compiler and Host Runtime support, then validate all Predicate inputs, operation/evidence lineage, wait semantics and 36 behavioral obligations.

The source migration does not require a separate paper migration rehearsal; the existing rehearsal is retained as the audit record and is not a gate to implementation.

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

The v1alpha2 Skill source contains no physical `lib/...` dependency paths. External Context Schemas are referenced by alias-qualified exported `$id`; Tool Operations are referenced by alias-qualified exact Operation ID. The v0.2 `lib/...` form is rejected by the v1alpha2 Compiler, not interpreted by a compatibility reader.

For the vNext schema-reference design, use the exported JSON Schema `$id` as the stable contract identity:
- each externally owned standalone Schema declares a globally unique, versioned absolute `$id` (URN form is recommended, e.g. `urn:connectionagent:host:context:subject:v1`);
- `contextSchema` references its exact exported ID through the supplied dependency alias;
- Compiler indexes only the supplied immutable snapshots and resolves exact `$id` matches; it never performs network resolution;
- duplicate IDs, missing IDs, duplicate exports, unsupported dialects and incompatible schemas fail closed;
- the Owner controls and versions the ID. A changed incompatible contract requires a new versioned ID.

The generic Observation/Evidence envelope and domain Observation payloads remain distinct. A READ Operation's Output Schema owns its domain payload; the shared Host/Runtime contract owns only the generic envelope/provenance fields. Do not invent one aggregate Observation Schema ID that claims to describe all 5GC payloads. The exact treatment of legacy `spec.context.schemas.observations` is part of the Predicate/READ acquisition migration, not a shortcut in this dependency change.

A logical dependency alias may appear only as the namespace prefix of an exported contract reference; Skill YAML never contains a dependency source locator, repository, source kind, revision, digest, cache key, or physical path. Studio Workspace Configuration maps aliases to locked snapshots. Compiler receives snapshot bytes and verifies their input digest. Compiler does not export digest values in BuildResult.

The v1alpha2 5GC Host Invocation Context and Evidence-reference contracts remain external Owner dependencies. Skill must not copy their bodies into its own package, and Studio must not fabricate missing owner files. See [Dependency Identity & 5GC Owner Schema Resolution](dependency-identity-and-owner-schema-resolution-vnext.md) for the cross-repository inventory and acceptance gates.

The stable Schema identity rule (`$id`) and v1alpha2 source syntax are frozen in `docs/skill-language-spec.md`. Existing v0.2 source and Compiler behavior remain only on the unchanged pre-migration mainline; no v1alpha2 compatibility behavior is required.


### Capability grants and Tool Operation linking

The Skill grants qualified Capability identities in `allowedResources.capabilities` (`capability-contract-alias::capability-id`); a Procedure node calls one exact qualified Operation (`tool-dependency-alias::operation-id`). The independent, deployment-owned CapabilityContracts maps each Capability to its owner and exact Operations with expected Effects, while ToolCatalog declares each callable Operation's schemas and declared Effect. For static proof, the Compiler BuildRequest must receive the target deployment's immutable CapabilityContracts as an explicit trusted input **separate from ordinary Skill dependency snapshots**; the ToolCatalog remains part of the resolved dependency set. Compiler then proves every Procedure Operation belongs to exactly one Capability, that the Skill grants that qualified Capability, and that the Tool Effect matches the independently declared expected Effect. If the trusted CapabilityContracts input is absent, the Compiler cannot claim static authorization proof; Runtime admission remains authoritative. The v1alpha2 Skill grants the eight exact Capability IDs only: the six existing Capability groups plus the Provider assurance and Fabric governance groups. The deployment-owned CapabilityContracts input remains the sole authority for each Capability's owner, Operation membership and expected Effect. The Skill never defines or duplicates those memberships. There is no Observation Ref namespace or implicit Observation provider in v1alpha2: facts are supplied by explicit Context projections, exact prior Operation outputs, or explicit READ Operations.


## 16. Frozen v1alpha2 Predicate inputs, READ Operations and bounded wait

The syntax in this section follows the normative [Skill Language Specification](../skill-language-spec.md). It is not a second execution model.

### 16.1 Pure Predicate inputs

```yaml
createdsession.udm.subscription_usable:
  inputs: [udmReadResult]
  evaluator:
    type: script
    ref: scripts/evaluate_udm_read.py

createdsession.n4.initial_resources_ready:
  inputs: [resources]
  evaluator:
    type: cel
    expression: >-
      resources.phase == "POST_CREATE" &&
      resources.pairState == "NEW_PAIR" &&
      resources.bindingStatus == "CURRENT" &&
      resources.defaultFlowInstalled == true &&
      resources.uplinkEndpointBound == true &&
      resources.baselineEvidenceRef != "" &&
      resources.currentSessionInstanceRef != ""
```

Procedure supplies every business input explicitly:

```yaml
- verify: createdsession.udm.subscription_usable
  with:
    udmReadResult:
      from: nudm-sdm-get.output.result
```

Semantics:

- `Predicate.inputs` declares only named business values; it does not declare Observation refs, scope, freshness, or acquisition.
- `verify.with` supplies every named input from an exact Context projection or Operation output. The evaluator sees only these declared names.
- Host validates Evidence for both evaluator types and may attach `input.evidence.<alias>.refs` to Python Predicate Script inputs. CEL receives only the declared business values.
- Host/Runtime validates producer, invocation, scope/correlation, source provenance, completeness, freshness and integrity before a definite verdict is allowed. Missing, stale, ambiguous or mismatched Evidence remains UNKNOWN.
- Predicate evaluation is pure. It cannot call an ObservationSource, Provider, Tool, network read or hidden Context global.
- Procedure Script input is derived from the Script call site's `with`; Predicate Script input is derived from `Predicate.inputs` and its `verify.with` call sites. Script output Schema is generated from the strict return `TypedDict`.

### 16.2 READ Operation and Evidence

Every independent domain acquisition is an explicit READ Operation. Its Tool Output contains the normalized typed value; Host/Runtime attaches Evidence from the same invocation and exact source artifact. The Predicate consumes that exact output. Do not create a second read to reconstruct Evidence for a prior Tool result.

The v1alpha2 5GC READ set contains six new READ Operations:

1. `createdsession-tools::ca.session.n4.initial_resources.read` — phase-discriminated `PRE_CREATE` baseline / `POST_CREATE` initial-resource result;
2. `createdsession-tools::ca.session.ran_setup.read` — exact SMF RAN-setup result;
3. `createdsession-tools::ca.session.n4.forwarding.read` — exact UPF N4-forwarding result;
4. `env-fabric-tools::ca.session.pcf_create_governance.read` — exact Fabric PCF-create governance result;
5. `ca-agent-host::ca.session.lifecycle.registration.read` — exact Host lifecycle-registration journal projection;
6. `ca-agent-host::ca.session.resource_responsibility.read` — exact Host resource-responsibility journal projection.

The first three belong to one Provider assurance Capability only if Provider Owner confirms that boundary. Fabric governance belongs to a Fabric-owned Capability. The two Host journal READs belong to the Host Runtime Capability. The exact CapabilityContracts mapping is deployment-owned and supplied separately to the Compiler.

Nine legacy prior-Operation projections remain same-attempt local projections, not additional network reads. Where the existing Operation returns only a handle, expand its typed Output from the exact stored artifact and attach same-receipt Evidence. Do not synthesize normalized fields from a successful call or use latest-per-UE state.

The UDM read is the Host Tool output `nudm-sdm-get.output.result`, which is `CreatedSessionUDMResult.runtime_value()` and has a separate Host-owned Output Schema. The Provider full GetSmData result Schema validates the upstream HTTP response inside Host; it is not substituted for the Host Tool Output Schema. Evidence for the Predicate comes from the same full Provider receipt.

### 16.3 Bounded Host wait Operation

Bounded waiting remains the exact Host Runtime Operation `ca-agent-host::ca.session.evidence.await`. It is not a Predicate feature or a domain Observation identity.

It receives:

- the exact qualified READ Operation ID to poll;
- the exact selector/bindings for that READ Operation;
- the same freshness requirement as the final Predicate input;
- the invocation-inherited wait budget/deadline and cancellation control;
- an explicit `CONTINUE` or `RETURN` policy for authoritative `KNOWN_ABSENT`.

It returns only a wait/evidence summary. After the wait, Procedure performs the final READ Operation separately and passes that final output to the Predicate. The wait and final READ must use the same exact attempt selector and causal handle. The polled READ Operation must also be covered by a Capability granted by the Skill.

The current bounded waiter implementation is not yet v1alpha2-compatible: it derives its target from legacy Predicate `observations` and invokes `ObservationSource`. Host Runtime migration must replace that declaration lookup with the exact READ Operation target while preserving bounded deadline, budget, cancellation, correlation, freshness and absence semantics.

### 16.4 Operation count

The current ToolCatalog has 12 callable Operations, including `ca.session.evidence.await`. Add six READ Operations above; keep the Host wait Operation. The phase-discriminated N4 READ shares one identity across the baseline and post-create points. The target contains **18 callable Operations**. If the Provider cannot guarantee that discriminated N4 contract, split it into two exact READ Operations and the target contains **19**. The wait is included in the 18/19 count; it is not an extra Procedure-only construct.

### 16.5 Script identity and I/O

- All five Scripts use package-relative identity under `scripts/`.
- Each Script entry point remains `def main(input: dict) -> OutputType`.
- Procedure Script input Schema is derived from that call site's `with`.
- Predicate Script input is the declared Predicate input map plus Host-attached Evidence refs.
- Every Script output is a strict same-file `TypedDict`; Compiler generates its closed Output Schema. No separately authored Script Input/Output Schema files, Tool metadata comments, local Tool IDs, sandbox declarations or timeouts remain in the Skill package.

## 17. Implementation decisions — 2026-11-13

The following decisions supersede exploratory alternatives elsewhere in this design note and are the implementation baseline:

1. **Breaking version:** v1alpha2 uses `connectionagent.io/v1alpha2`. The Compiler rejects v0.2 constructs; no dual parser, field mapper or compatibility path is retained.
2. **Pure Predicates:** Predicate definitions declare named `inputs`; they do not declare or acquire Observations. Procedure `verify.with` supplies every input explicitly. CEL uses declared input names as top-level variables. Python Scripts use the `input` dictionary.
3. **Explicit READs:** every domain read is a callable READ Operation with a typed output and Evidence from the same invocation. Predicate evaluation never triggers a second read.
4. **Wait remains a Host Operation:** retain `ca-agent-host::ca.session.evidence.await`, but replace its legacy Observation Ref target with an exact qualified READ Operation plus explicit bindings/freshness/absence policy. It returns a wait summary; Procedure performs the final READ separately.
5. **Capability separation:** Skill grants Capability IDs only. A single deployment-owned CapabilityContracts input maps each exact Operation ID to one Capability and Effect. Compiler cross-checks that mapping against the imported ToolCatalog.
6. **No physical library paths:** Studio supplies dependency snapshots to BuildRequest. Skill source references imported Operations/Schemas by dependency alias plus exact exported ID, never by `lib/` path.
7. **No dependency manager in Compiler:** no resolver lifecycle, manifest, lock, cache or digest output. The caller supplies the exact bytes.
8. **Explicit binding first:** `with/from` is the only source binding in this first vNext implementation. Semantic IDs and auto-binding are deferred; they are not required for the 5GC migration.
9. **Evidence is separate:** business payload and provenance/Evidence remain separate. Runtime validates Evidence before definite Predicate truth; Script `evidenceUsed` may only cite attached refs.
10. **5GC-first executable acceptance; MAS source mapping may proceed in parallel:** the conventional 5GC Skill and its 36 Cases / three References remain the first executable migration baseline. The MAS Skill is now mapped on this same branch against the Scheme C certified Establish operation order (see [MAS vNext Source Migration](mas-vnext-source-migration.md)); this does not make MAS buildable. Its ToolCatalog, typed Operation Schemas, CapabilityContracts, Host ingress, reconciliation, and durable resource-responsibility contracts remain Owner gates. Do not invent or copy proposed contracts to close those gaps.

The migration rehearsal is not an acceptance gate. Paper review identifies Owner gaps; implementation and focused tests are the validation method. The confirmed Host context gap is being closed in `ca-agent-demo`: Host publishes a typed `context.ingress` projection rather than requiring a Skill Predicate to acquire the same ingress through an Observation.
