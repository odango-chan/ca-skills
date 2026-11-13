> **Status notice (2026-11-13):** Historical design rationale and open-decision record. The comprehensive [CA-SL vNext Specification](../skill-language-spec.zh-CN.md) is now the sole normative language document. If this design note conflicts with it, the specification takes precedence. Do not implement syntax directly from this note without checking the current specification.

# Capability & Authoring Model vNext

Status: **DESIGN-REVIEW (5GC semantic boundaries converged; Owner contracts and syntax not frozen)**  
Scope: ca-skills authoring language and contracts. This is a design proposal, not an implementation claim. v0.2 remains authoritative until a separately reviewed migration is approved.

## 1. Goals

Unify Capability, Operation, Procedure, Predicate, data binding, Schema ownership, and Evidence semantics. Reduce repetitive YAML without hiding behavior. Keep builds deterministic, inspectable, reproducible without Skill Studio, and preserve current 5GC behavior and evidence guarantees.

## 2. Semantic model

### 2.1 Capability, Operation, Tool

- Capability is a stable logical ability identity and authorization/grouping boundary.
- Operation is the exact callable interface for a business action exposed under a Capability; it declares Effect and Input/Output contracts.
- Initial Effects remain READ and MUTATION.
- Tool is the common implementation/registration and contract unit. Its ToolCatalog may publish Operation interfaces and specialized Observation query interfaces; Tool itself is not a second authoring-level authorization identity.
- An Observation Tool is a specialized read-only Tool contract. Its query interface uses the same contract shape, dependency publication, Schema ownership and Capability authorization as other callable Tool interfaces; its Effect is READ. It is not a parallel registry.
- Procedure calls and Predicate data dependencies resolve through the same ToolCatalog/dependency identity system. Operation IDs and Observation query IDs remain distinct exact exported identities; neither is inferred from the other.
- The Capability contract explicitly enumerates every exact callable interface grouped under each Capability: business Operations and Observation query interfaces. A Skill grant authorizes only that declared membership; no hierarchy, naming convention, Tool display name, or implicit expansion may add callables. Compiler verifies exact membership and Effect agreement; Runtime still performs deployment admission and authorization.

### 2.2 Fact, Observation, acquisition

These terms must not be collapsed:

- **Fact**: a statement about domain, environment, or execution state.
- **Observation**: an independently addressable, read-only query capability exposed as a specialized Tool contract. It describes what authoritative fact/state can be queried, its QueryContext, normalized output Schema, owner, scope, temporal semantics, freshness and Evidence guarantees. It belongs to the Tool contract system; it is not a parallel ObservationSource/registry subsystem.
- **Observation Tool**: a Tool whose callable surface is read-only and whose contract follows the same ToolCatalog, dependency snapshot, Schema, Capability and Runtime admission rules as other Tools. Its Effect is READ. It may expose multiple Observation query identities; an Observation is not required for every Operation, and there is no one-to-one mapping between Mutation Operations and Observations.
- **Acquisition**: invoking an Observation Tool's declared query interface to obtain an authoritative current or stored fact. It is an explicit callable interaction, not hidden Predicate behavior.
- Observations may be backed by asynchronous events, Environment snapshots, Owner stores, or Runtime journals/projections. The original event producer, fact owner, projection/storage owner, and Observation Tool implementation may differ; the contract must identify the authority and lineage rather than treating the adapter as the fact owner.
- A Fabric event is not itself a callable Observation. An Observation Tool may query an owned Fabric journal/projection. Event time must remain distinguishable from receipt/acquisition time.
- Retire the legacy independent Observation Ref → ObservationSource implementation registry. Preserve Observation identities and query contracts as ToolCatalog contracts, with exact dependency aliases, Owner Schemas, READ Effect and Capability authorization. Existing adapters may remain internal implementations of those Tool contracts during migration.

An Operation output and an Observation are distinct sources. A prior Operation output should be used directly when it already contains the exact value and sufficient correlated Evidence. An Observation Tool is invoked only when the Agent/Procedure needs additional authoritative context; it is not automatically called after every Operation and is not a polling mechanism.

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
- Predicate consumes explicitly supplied business values: a prior Operation output, a trusted Context projection, a value returned by an Observation Tool query, or a combination. Each value retains its source and temporal lineage.
- If additional current/independent context is required, the Agent/Procedure explicitly invokes the authorized Observation Tool query and binds its typed output and Evidence to the consumer. Reuse an adequate prior Operation output/projection rather than issuing a redundant query.
- Predicate retains PASS / FAIL / UNKNOWN semantics and does not name Provider endpoints, Fabric routes, adapters, or implementation classes.
- **Compatibility note:** current v0.2 Host `PredicateEngine.evaluate()` acquires each declared `observations` entry during Predicate evaluation through `CompositeObservationSource`. Making Predicate pure is therefore a breaking execution-model change. Migration must schedule equivalent acquisition at the same control-flow point and preserve scope, freshness, conditional `when`, evidence validation, UNKNOWN behavior, and trace semantics; it must not eagerly acquire all facts at Procedure entry or duplicate a shared snapshot.

## 3. Unified authoring and reference rules

- Procedure Operation calls and Observation Tool queries resolve through the same ToolCatalog/dependency identity system; Predicate inputs bind explicitly to either producer.
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


### 4.3.1 Minimal input projection and opt-in defaults

The binding model must distinguish **available data** from **data actually passed to a consumer**. Availability never implies forwarding.

- A Skill Request Schema describes the public request surface; it does not require every field to be projected into every Procedure.
- `context.projections` grants access to named Host/Owner projections. It does not inject those projections into Procedure inputs or downstream calls.
- `Procedure.inputs` is the Procedure's actual input interface. Declare only values consumed by that Procedure or intentionally shared with its descendants; do not mirror the complete Context or Request.
- An Operation's Input Schema is its callable interface. Its `required` properties must be supplied. Optional properties are omitted unless the call intentionally uses them.
- A Predicate declares an ordered, typed function signature: parameter names/order plus either a primitive type or an authoritative Schema reference. Host-attached Evidence remains a separate reserved projection and is not a reason to add business parameters.
- A Procedure Script has no separately authored Input Schema in this model. Its call-site `with` is its input projection; keep those bindings explicit unless a future, separately reviewed Script input declaration makes a safe default possible.

The proposed `with.from: input` shorthand is an **opt-in same-name projection**, not blanket argument forwarding:

- It considers only the callee's declared input properties; caller fields not declared by the callee are never forwarded.
- It supplies same-named **required** callee inputs from the current caller's `input.<name>`.
- Optional callee inputs are not supplied by default, even when a same-named caller field exists. They require an explicit per-field binding.
- A per-field binding overrides the default for that target input, including an intentional source rename.
- If a required target has no same-named caller input under this shorthand, compilation fails. It does not fall back to another namespace or guess another source.
- The shorthand does not read `context.*`, prior-node outputs, parent Procedure state, or any other ambient source.
- It is limited to named-object binding contracts (Operation and Procedure). Predicate uses its ordered `parameters` / positional `arguments` form. Script retains explicit call-site `with` because it has no independent parameter signature.
- Every generated binding receives the same schema, type/nullability, producer-availability, scope, authorization and control-flow checks as an explicit binding.

Example:

~~~yaml
with:
  from: input
  sNssai:
    from: input.slice
~~~

Here the required same-name inputs are projected from the caller's `input`; the optional `sNssai` is deliberately opted in and renamed. No other caller fields are passed.

Requiredness is not a suggestion: if an Operation declares a parameter required but the business operation genuinely does not need it, correct the Owner's Operation contract rather than fabricating a value or weakening the call-site check. An omitted optional property is distinct from an explicit `null`; `null` is valid only when the consumer Schema allows it. JSON Schema `default` annotations do not cause the Compiler or Runtime to synthesize values. Any operational default must be defined by the contract owner.

Conditional availability and semantic identity need separate treatment:

- The same-name shorthand is an author-selected projection, not a heuristic that searches arbitrary fields. If source and target contracts publish semantic-field identities, those identities must agree; a conflict is an error. Similar names or compatible primitive types alone never authorize global auto-binding.
- If semantic-field identities are not yet published, `with.from: input` records the author's explicit same-name intent, while Compiler still validates the declared schemas and types. It must not generalize that intent to other namespaces or other consumers.
- A source produced only on one branch may satisfy a consumer only when control-flow analysis proves it is available on every path reaching that consumer. Prefer placing the consumer inside the branch that establishes the value. Do not silently turn a missing value into `null`.
- An optional target may be omitted only when its contract defines absence as valid. If a conditionally produced value is required for a particular branch, make that branch's requirement explicit and prove the producer dominates the consumer.
- Nested object projection, field extraction, coercion and normalization are not implied by same-name binding. Use an explicit source path and a declared deterministic transform where a shape or type change is required.


The exact YAML surface remains open until the grammar review addresses reserved-key collisions (for example, a target input literally named `from`), and positive/negative fixtures cover required-only defaults, optional opt-in, explicit override, absent required input, extra caller fields, null-versus-omitted, and Script exclusion.

### 4.4 Source versus generated plan

- Author-declared context projections and exceptional mappings are persisted in Skill source.
- Unique contract-derived mappings are not repeated in every node's YAML.
- Compiler emits a complete explicit Binding Plan in its intermediate/compiled artifact: target input, source identity/path, schema/type, producer identity, path availability, and declared transforms.
- Studio displays generated and authored mappings, their origin, and validation state. Editing a generated mapping persists a source-level override/projection, never Studio-only state.
- A “materialize/fix binding” action may write a generated choice to source when a stable explicit override is desired; it is not required for deterministic builds.

### 4.6 Predicate function signature and positional invocation (PROPOSED)

A Predicate is a pure, reusable function-like resource. Its definition owns an ordered, typed parameter signature; its Procedure call supplies positional source expressions in exactly that order. The signature is complete when the Predicate is authored and is independently available to CEL analysis, Python tooling and Compiler validation.

Definition:

~~~yaml
predicates:
  createdsession.udm.hold_bound:
    parameters:
      - hold: ca::schemas/udm-hold
      - dnn: string
      - sst: integer
    evaluator:
      type: cel
      expression: >-
        hold.operationKind == "UDM_SDM_SUBSCRIPTION_CREATE" &&
        hold.holdRef != "" &&
        hold.currentInstanceRef != "" &&
        hold.heldRequestDigest != "" &&
        hold.dnn == dnn &&
        hold.sst == sst
~~~

Call:

~~~yaml
verify:
  predicate: createdsession.udm.hold_bound
  arguments:
    - node.udm-hold.output
    - input.dnn
    - input.sst
~~~

Semantics:

- `parameters` is an ordered list of single-entry mappings: `- parameterName: primitiveType` or `- parameterName: exactSchemaRef`. Each list item must contain exactly one key; names must be unique. The value is one of the supported primitive types (`string`, `integer`, `number`, `boolean`) or an authoritative Schema reference; structured objects/arrays use Schema references. This is the Predicate's typed function signature, not a separate JSON Schema file. List order defines positional argument order; YAML mapping order is never used.
- `arguments` is an ordered list of source expressions. Argument i binds to parameter i. Arity mismatch, duplicate parameter names, unresolved sources, incompatible types, or unavailable producers are compile errors.
- Parameter names are local to the Predicate definition. Procedure node names and source paths never leak into the evaluator.
- The Predicate signature establishes the consumer's expected types at authoring time. Authoritative Producer/Context Schemas establish the actual source types at each call site. Compiler checks assignability from each source to the declared parameter and statically checks CEL against the signature. It does not infer the Predicate interface from whichever call site happens to be found first.
- No optional positional parameters, skipped positions, implicit nulls, implicit defaults, type coercion, or argument reordering are introduced in this proposal. If a Predicate genuinely has different required inputs, define separate predicates or make the input projection explicit in a separately reviewed design.
- The Predicate evaluator sees only its declared business parameters. Host/Runtime Evidence remains a reserved, separately attached projection for Script evaluators and assurance validation; it is not an extra positional business argument.
- Predicate evaluation remains pure. Observation Tool queries are explicit Tool calls, never hidden Predicate acquisition. Skill-level Wait/polling is not part of vNext; asynchronous completion belongs inside the invoked Tool/Provider Operation, which returns its final result and correlated Evidence.
- The call lowers to the same canonical Binding Plan used by other consumers. Runtime does not infer argument sources.

### 4.7 Invocation syntax consistency

Consistency is defined at the semantic and compiler layers, not by forcing every resource into positional arguments.

- **Operation** inputs are owned by an external Owner Input Schema: named object properties with types, requiredness and constraints. Do not infer positional order from JSON Schema property order. Operation calls therefore retain explicit named source bindings / the existing binding-map form.
- **Procedure** inputs are a named Procedure interface. Child Procedure calls retain explicit named bindings unless a future ordered signature is deliberately added to the Procedure contract.
- **Predicate** owns an explicit ordered, typed `parameters` signature, so positional `arguments: [...]` are deterministic, concise and independently type-checkable.
- **Procedure Script** has no independent parameter signature; its call-site projection defines the exact `input` object. It retains explicit named `with` bindings.
- All forms use the same source-reference vocabulary, Producer/Consumer validation, type/nullability checks, path-availability checks, authorization boundaries, and canonical Binding Plan representation.
- Do not add a polymorphic `arguments` field that sometimes means an ordered list and sometimes means a named map. Do not add aliases solely to make YAML look uniform.

This is an intentional, explainable syntax distinction based on interface ownership. Revisit only if a real Operation/Procedure contract introduces a stable ordered signature without duplicating its Schema.

### 4.5 Procedure and Predicate share the model

- Procedure Operation inputs and Predicate evaluator inputs use the same Binding Plan machinery. Predicate's positional arguments are normalized into that shared plan.
- Predicate has no separate Observation Binding registry or binding dialect.
- Predicate parameters are bound positionally from declared Context/producers, prior Operation outputs, or explicitly invoked Observation Tool query results.
- Observation Tool acquisition is visible in the execution/dataflow plan and audit trail; it is never hidden inside verify.

## 5. Requiredness and validation

- Public Skill request requiredness belongs to the Skill-owned Request JSON Schema.
- Operation input requiredness belongs to the Operation Input Schema owned by its contract owner.
- Procedure-specific public inputs, if needed, have an explicit Procedure input contract and do not duplicate Operation requiredness.
- Context availability belongs to the Context Contract / Procedure context projection. Existing spec.context.requiredFacts identifies required fact identifiers; it is not a field-level schema.
- Predicate parameters are required positional arguments; their types are established by the referenced Producer/Context Schemas.
- Compiler checks schema/reference validity, binding completeness, type/nullability, producer availability, and statically knowable control/data dependency order.
- Runtime checks actual values, dynamic presence, freshness, correlation, and Evidence validity.
- Do not repeat requiredness in every with mapping.

## 6. Schema and contract ownership

| Schema / contract | Owner |
|---|---|
| Public Skill Request Schema | Skill |
| Operation Input/Output Schema | Operation/Tool contract owner |
| Observation Tool QueryContext/Input and Output Schema | Observation Tool Owner; published through ToolCatalog |
| Observation QueryContext/Input and Output Schema | Observation Tool Owner; published in ToolCatalog |
| Shared Context Contract/Schema | Host contract authority, versioned and consumed by Skills |
| Generic Evidence Envelope | Host |
| Source/evidence guarantees | Authoritative producer and trusted acquisition adapter, limited to what each can attest |
| Normalized projection Schema | Explicit projection/normalization owner |
| Predicate parameter signature | Skill Predicate; declares ordered parameter names and expected types, referencing authoritative Schemas for structured values |
| Predicate Script input | Derived from the owning Predicate signature; no separately authored Input Schema |
| Script input/output contract | Skill |

From the Skill author's perspective, Schemas primarily constrain payloads consumed by Procedure Scripts and Predicates. When a payload is produced by an Operation or Observation Tool, the same owner-published payload Schema serves as that callable contract's Output Schema and the consumer's type authority; do not create a second copy just because it crosses a producer/consumer boundary. A Predicate's ordered, typed `parameters` name the values it consumes and establish the expected types when the Predicate is authored. For structured values, they reference the authoritative Schema rather than copying it. At each call site, Compiler checks the actual Producer/Context Schema against that declared type. Predicate Script input is derived from this same signature; there is no separately authored Predicate Input Schema or Script Input Schema, and no Predicate may redefine an Owner's payload.

An Observation Tool query uses its own ToolCatalog Input/Output contract and Owner-published Schema. Do not duplicate the same payload schema in a parallel Observation registry. If an event/journal/projection changes the structure, that projection owner owns its schema. Transformations require explicit input/output contracts and preserve lineage to source evidence. Host must not invent domain schemas.

## 7. Procedure and Predicate relationship

- Procedure describes execution order, control flow, explicit calls, and data dependencies.
- Predicate describes a condition and its evaluation logic.
- Agent/Procedure invokes an authorized Observation Tool query when independent/current authoritative state is needed, then verifies the Predicate using the result/Evidence.
- Predicate may consume a preceding Operation output if it meets the declared assurance requirements; avoid redundant READ.
- Predicate may combine Procedure-provided inputs and multiple READ outputs.
- Mutation response alone does not prove resulting external state.
- Event-driven facts remain supported: an Observation Tool may query an authoritative event/journal/projection; Evidence preserves event time separately from acquisition/receipt time.

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
- `establish-pdu-session` is the mandatory executable migration fixture. `establish-session-mas` is a structural/reference fixture for shared Context and future multi-Skill boundaries only; it is not required to run end-to-end for this feasibility review.
- Preserve deterministic 5GC behavior and live E2E guarantees.
- Compiler and Studio consume the same canonical contracts/examples; neither redefines semantics independently.
- Compare old/new execution plans and demonstrate equivalent or intentionally corrected data/evidence lineage.

## 12. Open decisions before syntax freeze

The 5GC semantic mapping itself is consolidated in [Binding Migration Rehearsal §§18–24](binding-migration-rehearsal-vnext.md): six current Capability groups / twelve Operation Effect memberships, all 17 legacy Observation refs, all five Script identities, and a behavior-preserving target Procedure. Host PR #198 proposes Subject/Facts/Evidence refs; Host PR #200 proposes normalized projection Schemas; inventory PR #199 remains docs-only; Provider PR #50 proposes the full GetSmData wire result Schema. These remain Draft/unmerged. The selected UDM vNext mapping is the exact Host Tool `output.result` (`runtime_value()` projection) plus same-receipt Host Evidence. The Host-facing payload needs its own Schema, distinct from the Provider wire Schema. The normalized legacy projections are migration inputs, not a mandate to create one Observation Tool per legacy ref. MAS shared-snapshot semantics remain a structural reference question, not an executable acceptance gate.

The following syntax and owner-publication gates remain open:
- exact Observation Tool query contract and ToolCatalog representation, including how an Observation Tool may expose multiple query identities while reusing the common Tool/Capability/Schema contract;
- the canonical Predicate Script input projection: source mapping is complete for the two 5GC evaluator Scripts; derive their named `input.<parameter>` projection from the Predicate `parameters` signature and every positional `verify.arguments` call site, plus the Host Evidence projection, without authoring a second Script Input Schema file. Procedure Script inputs remain derived per call site and Script outputs remain strict TypedDict-generated schemas. The Predicate call syntax is now proposed; current ca-agent-demo `localTools` / metadata is not the official v0.2 Script dialect;
- exact representation/location of Procedure context projection;
- exact location of exceptional mappings (node-level with vs Procedure-level bindings);
- stable semantic-field identity vocabulary for automatic binding (must not rely on property-name equality); first executable use should be actual 5GC shared Context fields and Operation input parameters. The 11 MAS common-context names remain a structural candidate list only, not owner-backed evidence or an acceptance gate;
- whether Deployment binding overlays are needed and how they are versioned/identified;
- exact binding of the qualified Capability namespace to the deployment-owned CapabilityContracts build input: Skill source grants Capability IDs only and must not define membership/Effects; static membership proof requires the target deployment's immutable CapabilityContracts as an explicit trusted BuildRequest input, separate from ordinary Skill dependency snapshots. The Capability alias-to-input binding and trust provenance remain open; without that input only Runtime admission can be claimed;
- Evidence vocabulary and temporal fields;
- normalized projection contract and lineage representation;
- whether procedure.yaml remains under assurance/ or moves in a separately justified directory redesign.

The source-based migration rehearsal is recorded in [Binding Migration Rehearsal — 5GC and MAS](binding-migration-rehearsal-vnext.md), including the consolidated Owner dependency order in §24. It maps all 17 legacy 5GC Observation refs to explicit Operation-output reuse, Context projections, or Observation query needs and preserves the six existing Capability groups / twelve Operations as the current baseline. The two other `ref` entries in `predicates.yaml` are Script evaluator identities, not Observations. MAS shared-snapshot ownership remains a future structural question. v0.2 currently acquires ObservationSource data inside PredicateEngine; vNext moves acquisition to explicit Observation Tool calls, not into Predicate.\n\nThese syntax/contract decisions do not permit hidden Runtime behavior, ambiguous binding, or weakened Evidence guarantees.

## 13. Source-backed observation mapping

See [Observation Owner and Acquisition Inventory](observation-owner-inventory-vnext.md) for source ownership and [Binding Migration Rehearsal §19](binding-migration-rehearsal-vnext.md#19-complete-17-ref-predicate-input-and-acquisition-migration) for the corresponding Procedure points and target inputs. All **17** 5GC Predicate Observation refs are mapped; the two additional `ref` entries identify Script evaluators, not Observations. MAS still requires an authoritative snapshot owner and Observation Tool query contract. Exact vNext Observation Tool identities and Schema/Evidence exports remain open; no running source has been removed.

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

The generic Observation/Evidence envelope and domain Observation payloads remain distinct. The relevant Tool Operation or Observation query Output Schema owns its domain payload; the shared Host/Runtime contract owns only the generic Evidence/provenance fields. Do not invent one aggregate Observation Schema ID that claims to describe all 5GC payloads. The exact treatment of legacy `spec.context.schemas.observations` is part of the Predicate/Observation Tool migration, not a shortcut in this dependency change.

A logical dependency alias may appear only as the namespace prefix of an exported contract reference; Skill YAML never contains a dependency source locator, repository, source kind, revision, digest, cache key, or physical path. Studio Workspace Configuration maps aliases to locked snapshots. Compiler receives snapshot bytes and verifies their input digest. Compiler does not export digest values in BuildResult.

The current 5GC Host Subject / Facts / Evidence and Observation contracts remain external Owner dependencies. Skill must not copy their bodies into its own package, and Studio must not fabricate missing owner files. See [Dependency Identity & 5GC Owner Schema Resolution](dependency-identity-and-owner-schema-resolution-vnext.md) for the cross-repository inventory and acceptance gates.

The stable Schema identity rule (`$id`) is the selected vNext direction; the complete Skill Language syntax and breaking migration are not yet frozen. Existing v0.2 source and Compiler behavior remain authoritative until a separately reviewed migration is implemented.


### Capability grants and Tool Operation linking

The Skill grants qualified Capability identities in `allowedResources.capabilities` (`capability-contract-alias::capability-id`); a Procedure node calls one exact qualified Operation (`tool-dependency-alias::operation-id`). The independent, deployment-owned CapabilityContracts maps each Capability to its owner and exact callable interfaces (Operation IDs and Observation query IDs) with expected Effects, while ToolCatalog declares each callable interface's schemas and declared Effect. For static proof, the Compiler BuildRequest must receive the target deployment's immutable CapabilityContracts as an explicit trusted input **separate from ordinary Skill dependency snapshots**; the ToolCatalog remains part of the resolved dependency set. Compiler then proves every invoked callable interface belongs to exactly one Capability, that the Skill grants that Capability, and that the Tool Effect matches the independently declared expected Effect. If the trusted CapabilityContracts input is absent, the Compiler cannot claim static authorization proof; Runtime admission remains authoritative. Observation is a specialized read-only Tool contract, not a second contract system. Its query interface, Input/Output Schemas, Owner, READ Effect and Capability membership are published through the same ToolCatalog/CapabilityContracts inputs as other Tools. The legacy ObservationSource registry is an implementation detail to retire; Skills refer to the exported Observation Tool query contract, not its adapter class.


## 16. Candidate 5GC Predicate inputs and Observation Tool queries (NOT FROZEN)

The source rehearsal supports a small authoring surface that reuses the existing v0.2 binding vocabulary rather than inventing a second Observation binding language.

### 16.1 Pure Predicate function signature and invocation

Candidate definition:

~~~yaml
predicates:
  createdsession.udm.subscription_usable:
    parameters:
      - udmReadResult: host-context::urn:connectionagent:5gc:udm-read-result:v1
    evaluator:
      type: script
      ref: scripts/evaluate_udm_read.py
~~~

Procedure postcondition:

~~~yaml
verify:
  predicate: createdsession.udm.subscription_usable
  arguments:
    - nudm-sdm-get.output.result
~~~

Semantics:

- `parameters` declares ordered evaluator-local names and expected types. For a structured parameter, the authoritative Producer/Context Schema is referenced; it is not copied. The Predicate signature is the consumer contract, while the Producer Schema remains the source contract. No duplicate Predicate Input Schema is authored.
- `arguments` is positional and must have exactly the same arity/order as `parameters`.
- Compiler resolves each source expression and validates producer availability and assignability to the already-declared Predicate parameter type at every call site. CEL is checked against the Predicate signature at definition time, independently of Procedure call sites.
- The evaluator receives only the declared business parameter projection. Procedure node names and source paths do not leak into the Predicate definition.
- Runtime attaches Host Evidence to the corresponding producer-backed parameter separately from its business payload. The Binding Plan preserves parallel lineage: exact producer, source path, schema/owner, invocation/scope, and attached Evidence refs/guarantees.
- Predicate Script receives the named parameter projection as `input.<name>`; its strict Output TypedDict remains unchanged. Compiler derives the Script's input type environment from the owning Predicate signature and may expose generated editor/type-checking metadata, but does not create a second authored Input Schema or ask the Script to redefine it. The Script cannot invent or rewrite Evidence refs.
- A CEL Predicate refers to the declared parameter names directly; it does not read a hidden `input` global.
- No acquisition occurs inside `verify`. Observation Tool queries, when needed, are explicit authorized Tool calls. There is no Skill-level Wait or polling construct.

For the UDM example, the Predicate consumes the business payload `udmReadResult`, bound from `nudm-sdm-get.output.result`; Host attaches Provider Evidence correlated to the same full receipt/invocation/transaction/record. The legacy `sbi.operation.result` ObservationSource was reading the same immutable `CreatedSessionUDMResult` from an attempt-local store; vNext should reuse the exact Tool output and Evidence rather than create a duplicate Observation query.


### 16.2 Former wait paths — removed from vNext Skill model

The three legacy `ca.session.evidence.await` nodes are not represented in vNext Skill YAML. They are removed from the Skill-level execution graph.

Their asynchronous protocol/service completion responsibilities move into the owning Tool/SMF Operations:
- N4 resource establishment/completion: `UPN.CREATE_UP_SESSION`;
- RAN signaling/adoption: `SSM.SIGNAL_UE_AN`;
- N4 forwarding modification/completion: `UPN.MODIFY_UP_SESSION`.

Each Operation must return its final normalized result and correlated Evidence before the Procedure advances. Host retains invocation deadline, cancellation, correlation and UNKNOWN handling as Runtime controls. These controls do not create a Skill-level Wait/Await/Poll node or a separate callable `ca.session.evidence.await` requirement.

Observation Tools remain available for independent queries of authoritative context. They must not be used to poll completion of an Operation whose asynchronous lifecycle belongs inside that Operation.

### 16.3 What this candidate does not solve yet

The first UDM / Hold / N4 slice demonstrates the core boundary, but not all 17 refs are ready to migrate:

- `createdsession.procedure_context` is a captured ingress-event projection. ca-agent-demo PR [#200](https://github.com/odango-chan/ca-agent-demo/pull/200) proposes its `procedure-context` payload Schema; PR #198 Subject/Facts still exposes only the ingress/lifecycle handles. The payload export remains Draft/unmerged and must preserve the trusted ingress event's source provenance.
- `createdsession.lifecycle_registration` and `createdsession.resource_responsibility` read the Host reference journal. PR #200 proposes both normalized payload Schemas; their source authority is the Agent reference journal, not Provider/Open5GS state. Keep them distinct from static Subject/Facts fields. These exports remain Draft/unmerged and must use the actual Host journal owner identity.
- The nine prior-Operation-owned local projections read attempt-local stores populated by existing Operations. Their direct Operation outputs are not all equivalent: some return only handles while the ObservationSource adds normalized fields or validates local-store state. Expose typed projections over the same stored artifact and attach its Evidence, without another external network read.
- The full Runtime `ObservationEvidence` envelope remains Host-internal by design. Skill consumes each Owner/adapter domain Output Schema plus the narrow Host Script Evidence-reference projection; do not publish one aggregate Observation payload Schema or the full internal envelope merely to satisfy a Compiler file-count target.

### 16.4 Impact on the current 5GC Operation set

The current Skill has 12 legacy unique Operations, including the legacy `ca.session.evidence.await`. vNext removes that Skill-level wait callable and moves the three asynchronous completion responsibilities inside their owning SMF/Tool Operations. Observation query contracts are independently represented in ToolCatalog and CapabilityContracts; they are not a mandatory one-per-Operation pairing. Final callable identities must be counted from the authoritative ToolCatalog and CapabilityContracts inventory.

The complete behavior-preserving semantic Procedure outline—covering all 17 Predicate inputs, the two fresh lifecycle gates, removal of the three Skill-level waits, independent Observation queries where required, exact Operation reuse, and reconciliation/finalization paths—is recorded in [Binding Migration Rehearsal §22](binding-migration-rehearsal-vnext.md#22-behavior-preserving-target-procedure-outline-syntax-neutral-not-frozen). It is deliberately syntax-neutral; §16 remains a candidate, not frozen YAML.


## 17. Implementation decisions — 2026-11-13

The following decisions supersede exploratory alternatives elsewhere in this design note and are the implementation baseline:

1. **Breaking version:** vNext uses `connectionagent.io/v1alpha2`. The Compiler rejects v0.2 constructs; no dual parser, field mapper or compatibility path is retained.
2. **Pure Predicates:** Predicate definitions declare ordered, typed `parameters` using concise single-entry mappings (`- hold: schema-ref`, `- dnn: string`). They do not declare or acquire Observations. Procedure `verify.arguments` supplies positional source expressions. CEL reads parameter names directly; Predicate Scripts receive `input.<parameter>`.
3. **Observation is a specialized Tool:** Observation is an independently addressable read-only query capability published through the same ToolCatalog, dependency, Owner Schema, CapabilityContracts and Runtime admission model as other Tools. Retire only the legacy ObservationSource implementation registry; preserve Observation query identities and contracts. No one-to-one pairing with Operations is required.
4. **Explicit query:** when additional authoritative context is required, Agent/Procedure invokes an exact authorized Observation Tool query. Reuse an adequate prior Operation output or trusted Context projection instead of adding redundant queries. Predicate evaluation never triggers acquisition.
5. **No Skill-level Wait:** asynchronous protocol/service completion is encapsulated by the owning Tool/SMF Operation. It returns its final result and correlated Evidence; Host deadline/cancellation/correlation remain Runtime controls.
6. **Capability separation:** Skill grants Capability IDs only. A single deployment-owned CapabilityContracts input maps each exact callable ID (Operation or Observation query) to one Capability and Effect. Compiler cross-checks that mapping against the imported ToolCatalog.
7. **No physical library paths:** Studio supplies dependency snapshots to BuildRequest. Skill source references imported Operations/Schemas by dependency alias plus exact exported ID, never by `lib/` path.
8. **No dependency manager in Compiler:** no resolver lifecycle, manifest, lock, cache or digest output. The caller supplies the exact bytes.
9. **Explicit source binding:** every source expression is explicit. Named-object consumers use `with/from`; Predicate uses ordered positional `verify.arguments`. Semantic-ID-based automatic source discovery is deferred and is not required for the 5GC migration.
10. **Evidence is separate:** business payload and provenance/Evidence remain separate. Runtime validates Evidence before definite Predicate truth; Script `evidenceUsed` may only cite attached refs.
11. **5GC-first:** migrate the 5GC Skill and its 36 Cases / three References as the business baseline. MAS remains non-executable design material and is not used to invent missing contracts.

The source migration rehearsal remains required to prove that the new Observation Tool contracts and Operation outputs preserve all legacy fact, scope, freshness, correlation and Evidence behavior. It is not a substitute for implementation tests. Host-published Context projections may satisfy facts already captured at ingress; an Observation Tool query is not required when that exact trusted projection is already available.
