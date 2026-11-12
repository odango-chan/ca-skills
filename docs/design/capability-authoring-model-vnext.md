# Capability & Authoring Model vNext

Status: **DESIGN-REVIEW (revised semantic baseline; syntax not frozen)**  
Scope: ca-skills authoring language and contracts. This is a design proposal, not an implementation claim. v0.2 remains authoritative until a separately reviewed migration is approved.

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

From the Skill author's perspective, Schemas primarily constrain **inputs consumed by Procedure Scripts and Predicates**. When that payload is produced by a READ Operation, the same owner-published payload Schema serves as that Operation's Output Schema and the consumer's input contract; do not create a second copy just because it crosses a producer/consumer boundary. A Skill-owned Predicate input projection is appropriate when it combines several sources or reshapes Host Context plus Evidence, but it must not redefine an owner's payload.

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

## 11. Migration and compatibility

- This is a breaking authoring-language evolution; v0.2 remains current until a separately approved migration lands.
- Do not claim current Compiler/Host supports proposed syntax.
- Do not remove current Observation Source registration/schemas until every existing Observation Ref/fact is mapped to an authoritative producer, acquisition Operation where applicable, owner, input/output contract, evidence guarantee, and regression coverage.
- Event/journal-backed facts map to their actual producer/projection owner; do not fabricate a network READ for facts already authoritatively captured.
- Both establish-pdu-session and establish-session-mas are mandatory migration fixtures.
- Preserve deterministic 5GC behavior and live E2E guarantees.
- Compiler and Studio consume the same canonical contracts/examples; neither redefines semantics independently.
- Compare old/new execution plans and demonstrate equivalent or intentionally corrected data/evidence lineage.

## 12. Open decisions before syntax freeze

The following remain open pending 5GC/MAS migration examples and Compiler feasibility review:
- exact YAML shape for Predicate input declarations and references to explicitly scheduled READ Operations; the migration rehearsal found 17 distinct 5GC Observation Refs and one shared MAS snapshot Ref used by 17 Predicates, whose acquisition owners/contracts still need a complete inventory;
- how explicit acquisition supplies the materialized Observation payload and Evidence to a pure Predicate; current 5GC `evidence.await` returns only evidence refs and PredicateEngine performs a subsequent acquisition, so the migration must preserve or deliberately reconcile both acquisition points;
- the canonical Skill-owned Script contract: stable Script identity, whether Predicate evaluator inputs have explicit Skill-owned projection Schemas, whether Procedure Script inputs are derived from call-site bindings, and one authoritative output-schema source; current ca-agent-demo `localTools` / metadata is not identical to ca-skills v0.2 Script semantics;
- exact representation/location of Procedure context projection;
- exact location of exceptional mappings (node-level with vs Procedure-level bindings);
- stable semantic-field identity vocabulary for automatic binding (must not rely on property-name equality); first required use: shared Context fields and Operation input parameters, validated against the 11 common MAS context inputs and representative 5GC aliases;
- whether Deployment binding overlays are needed and how they are versioned/identified;
- exact Capability-to-Operation authorization expansion semantics, including how the deployment-owned CapabilityContracts currently used by 5GC is supplied to a build: Skill source grants Capability IDs only and must not define membership/Effects; if static membership proof is claimed, the target deployment's immutable CapabilityContracts must be an explicit trusted build input (separate from ordinary Skill dependencies), otherwise only runtime admission can be claimed;
- Evidence vocabulary and temporal fields;
- normalized projection contract and lineage representation;
- whether procedure.yaml remains under assurance/ or moves in a separately justified directory redesign.

The source-based migration rehearsal is recorded in [Binding Migration Rehearsal — 5GC and MAS](binding-migration-rehearsal-vnext.md). It supports shared Context projection plus contract-backed fan-out as the first auto-binding target, while keeping exact producer handles and assurance-sensitive references explicit until semantic output identities exist. The rehearsal traces 17 of the 19 5GC Observation Refs to concrete current owners (two Skill evaluation refs remain untraced), and identifies the MAS shared snapshot owner/READ contract as unresolved. It also confirms that v0.2 currently performs Observation acquisition inside PredicateEngine evaluation, so pure Predicate migration needs explicit acquisition scheduling rather than a syntax-only rewrite.\n\nThese syntax/contract decisions do not permit hidden Runtime behavior, ambiguous binding, or weakened Evidence guarantees.

## 13. Source-backed observation mapping

See [Observation Owner and Acquisition Inventory](observation-owner-inventory-vnext.md). The current 5GC source-class owners have been mapped for all **17** Predicate Observation refs (two additional `ref` entries in the file identify Script evaluators, not Observations). MAS still requires an authoritative snapshot owner/READ contract. Exact vNext replacement Operations and schema/evidence contracts remain open; no running source has been removed.

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

The current v0.2 `spec.context.schemas.*: lib/...` syntax is a **compatibility-era source locator**, not the target vNext language model. Preserve its existing behavior until a separately reviewed breaking migration; do not silently reinterpret or remove it.

For the vNext schema-reference design, use the exported JSON Schema `$id` as the stable contract identity:
- each externally owned standalone Schema declares a globally unique, versioned absolute `$id` (URN form is recommended, e.g. `urn:connectionagent:host:context:subject:v1`);
- `spec.context.schemas.subject/facts/evidence` reference those exact IDs, not dependency IDs or paths;
- Compiler indexes only the supplied immutable snapshots and resolves exact `$id` matches; it never performs network resolution;
- duplicate IDs, missing IDs, duplicate exports, unsupported dialects and incompatible schemas fail closed;
- the Owner controls and versions the ID. A changed incompatible contract requires a new versioned ID.

The generic Observation/Evidence envelope and domain Observation payloads remain distinct. A READ Operation's Output Schema owns its domain payload; the shared Host/Runtime contract owns only the generic envelope/provenance fields. Do not invent one aggregate Observation Schema ID that claims to describe all 5GC payloads. The exact treatment of legacy `spec.context.schemas.observations` is part of the Predicate/READ acquisition migration, not a shortcut in this dependency change.

A logical dependency alias may appear only as the namespace prefix of an exported contract reference; Skill YAML never contains a dependency source locator, repository, source kind, revision, digest, cache key, or physical path. Studio Workspace Configuration maps aliases to locked snapshots. Compiler receives snapshot bytes and verifies their input digest. Compiler does not export digest values in BuildResult.

The current 5GC Host Subject / Facts / Evidence and Observation contracts remain external Owner dependencies. Skill must not copy their bodies into its own package, and Studio must not fabricate missing owner files. See [Dependency Identity & 5GC Owner Schema Resolution](dependency-identity-and-owner-schema-resolution-vnext.md) for the cross-repository inventory and acceptance gates.

The stable Schema identity rule (`$id`) is the selected vNext direction; the complete Skill Language syntax and breaking migration are not yet frozen. Existing v0.2 source and Compiler behavior remain authoritative until a separately reviewed migration is implemented.


### Capability grants and Tool Operation linking

The Skill grants qualified Capability identities in `allowedResources.capabilities` (`dependency-alias::capability-id`); a Procedure node calls one exact qualified Operation (`dependency-alias::operation-id`). The independent Capability contract maps each Capability to its owner and exact Operations with expected Effects, while ToolCatalog declares each callable Operation's schemas and declared Effect. Compiler must prove every Procedure Operation belongs to exactly one Capability in the same resolved dependency snapshot, that the Skill grants that qualified Capability, and cross-check Effects. Existing 5GC source currently places Operation IDs in `allowedResources.capabilities` as a compatibility-era representation; do not silently reinterpret them as Capability IDs. A separately reviewed language migration must change these grants to the six real 5GC Capability IDs qualified by the corresponding dependency alias while preserving exact Operation coverage. Observation is a separate read-only source/evidence contract consumed by Predicate evaluation or the bounded evidence-wait Operation. It is not automatically a Tool or Operation. If an Observation provider is deliberately exposed as a callable Tool Operation, that Operation must belong to exactly one Capability and be covered by the Skill's Capability grant.
