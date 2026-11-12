# vNext Binding Migration Rehearsal — 5GC and MAS

Status: **SOURCE REVIEW COMPLETE / SEMANTIC MAPPING PARTIAL**  
Date: 2026-11-12  
Target design: [Capability & Authoring Model vNext](capability-authoring-model-vnext.md)  
Source repository: `odango-chan/ca-agent-demo`, `main`  
Source tree commit observed during review: `4395982fa6efb97714b97901603b2dfb7018c4d0`

> This is a read-only source rehearsal. No Skill source, ToolCatalog, Runtime, or live 5GC environment was modified. Counts below are lexical counts from the six YAML files and should not be interpreted as a compiler-derived count of removable mappings.

## 1. Executive result

The two real Skills support the proposed direction, but they expose an important distinction:

- **MAS** contains substantial repeated forwarding of the same Procedure context into every Operation. This is the strongest candidate for contract-backed automatic binding.
- **5GC** has a useful Procedure input projection already, but it also has deeply intentional, identity-sensitive bindings involving Fabric holds, exact UDM/PCF transactions, lifecycle, invocation, policy association, and N1/N2 artifacts. These must not be simplified merely because their types are strings or their field names match.
- **Both Skills** still use Predicate-level Observation Ref declarations. They cannot be migrated by simply replacing `observations:` with an Operation call. The actual acquisition owners, source contracts, freshness semantics, and evidence guarantees must first be mapped.
- Existing Tool contracts largely declare JSON Schema names and types. They do not yet provide a sufficiently rich, shared semantic-field identity vocabulary to safely infer every same-named field. Automatic binding cannot be enabled by property-name equality alone.

Conclusion: retain the proposed Binding Plan, but make the first implementation target **shared context projection + contract-backed fan-out**, not unrestricted producer inference. Keep exact producer handles and assurance-sensitive references explicit until contracts prove their semantic identity.

## 2. Source inventory and counts

### 2.1 Procedure source shape

| Metric | `establish-pdu-session` | `establish-pdu-session-mas` |
|---|---:|---:|
| Procedure YAML size | 31,267 chars | 25,158 chars |
| `with:` blocks (lexical) | 33 | 16 |
| `from:` mappings (lexical) | 196 | 230 |
| `call:` occurrences | 14 | 16 |
| Unique called Operations | 12 | 16 |
| `verify:` occurrences | nested postconditions / preconditions | 17 |

The lexical `with` count includes node calls, nested precondition/script calls, postcondition Predicate inputs, and sub-Procedure calls. It is not a count of independent binding declarations.

### 2.2 Predicate / Observation source shape

| Metric | `establish-pdu-session` | `establish-pdu-session-mas` |
|---|---:|---:|
| Predicate definitions | 19 | 17 |
| Unique Observation Refs | 17 | 1 |
| Observation scope | Predicate-specific, several scope shapes | Same session scope repeated |
| Freshness examples | 5s and 1h | 5s |

The 17 MAS Predicates all refer to `mas.establishment.snapshot` with the same general UE/PDU-session/ingress/lifecycle scope and 5s freshness. This strongly suggests a shared acquired snapshot/projection with multiple pure evaluations, not 17 separate reads.

The 5GC Predicates use 17 distinct Observation Refs, including procedure context, UDM/PCF/N1N2 holds, PCF create inputs/governance, N4 baseline/resources, delivery context, AMF transfer, RAN setup, forwarding, resource responsibility, operation result, and lifecycle registration. These refs represent materially different authorities and assurance questions; they must not be collapsed into one generic snapshot.

## 3. 5GC rehearsal: what can and cannot be simplified

### 3.1 Existing context projection is already useful

The entry Procedure declares a typed input projection from:
- `context.subject.ueRef`;
- request fields such as PDU Session ID, PTI, request type, DNN, S-NSSAI, serving PLMN, requested PDU Session type, and SSC mode;
- `context.facts.createdsession_ingress` and `context.facts.createdsession_lifecycle`.

That is a good author-facing boundary. Nodes then bind Operation-specific parameter names from these stable Procedure inputs. This avoids repeating the full Host context path at every call site.

**vNext implication:** retain a typed Procedure context projection (or equivalent canonical Context Contract projection). Do not remove it in favor of an implicit global context bag. It gives the Procedure a declared, reviewable input surface.

### 3.2 High-value automatic-binding candidates

The following are candidates for deterministic generation once semantic field identities are present in Context and Operation contracts:

| Semantic value | Current source pattern | Candidate treatment |
|---|---|---|
| UE identity | Procedure input `ue-ref` → many `ueRef` inputs | Shared context projection + Operation semantic input identity |
| PDU Session ID | `psi` → `pduSessionId` | Shared context projection + semantic identity |
| PTI | `pti` → `pti` | Shared context projection + semantic identity |
| Request type | `request-type` → `requestType` | Shared context projection + semantic identity |
| Ingress reference | `ingress-ref` → `ingressRef` | Shared context projection + exact invocation-scope identity |
| Lifecycle reference | `lifecycle-ref` → `lifecycleRef` | Shared context projection + exact lifecycle identity |
| DNN / S-NSSAI / PLMN | Procedure inputs → Operation parameters | Auto-bind only where Operation contract semantic identity and type/schema match |

These are not automatically safe just because the names or values look alike. In particular, ingress/lifecycle values are attempt-scoped references: their semantic identity and authority must be part of the contract.

### 3.3 Must remain explicit (or require stronger contracts)

The following mappings encode business order, exact resource identity, or ownership and should remain explicit in the initial vNext migration:

- Fabric UDM/PCF/N1N2 `holdRef`, `currentInstanceRef`, waiter association, and held-request digest.
- Exact UDM invocation and transaction references used to answer the request that was actually read.
- PCF create-input handle, policy association, subscription reference, and policy result.
- Operation-context and runtime-invocation handles.
- Prepared N1/N2 response/delivery artifacts and exact AMF transfer operation references.
- Pre-N4 versus Post-N4 identities; a Pre-N4 policy association must not be silently substituted for a Post-N4 session identity.
- Resource responsibility transfer and disposition.
- Script inputs that represent deliberate Skill-owned business projections, such as selected subscription configuration, policy input selection, and N1/N2 delivery selection.

Some of these could eventually be inferred if the Operation contracts expose distinct semantic output identities and the Compiler proves a unique reachable producer. Until then, explicit source paths are a correctness feature, not needless verbosity.

### 3.4 5GC conclusion

The 5GC source does not justify deleting `with/from`. It justifies reducing repeated context plumbing while preserving explicit resource/transaction bindings.

The target is not “fewest mappings”; it is “fewest mappings that are genuinely derivable from authoritative contracts.”

## 4. MAS rehearsal: strong context fan-out opportunity

### 4.1 Repeated common context

The MAS Procedure has 16 Operation call sites. Each passes the same 11 Procedure input values:

- `ue` → `ueRef`
- `ingress` → `ingressRef`
- `lifecycle` → `lifecycleRef`
- `pduSessionId` → `pduSessionId`
- `pti` → `pti`
- `requestType` → `requestType`
- `dnn` → `dnn`
- `sNssai` → `sNssai`
- `servingPlmn` → `servingPlmn`
- `requestedPduSessionType` → `requestedPduSessionType`
- `requestedSscMode` → `requestedSscMode`

That is **176 repeated context-forwarding mappings** (11 × 16) in the current source. The Procedure also declares the 11 context-to-input projections once at its top level.

This is the clearest candidate for vNext authoring reduction. However, the MAS ToolCatalog currently repeats these fields in each Operation Input Schema. The schemas establish parameter names/types/requiredness, but the reviewed material does not yet prove a shared semantic identity for every parameter. A future shared Context Contract plus semantic-field identifiers should let the Compiler resolve the fan-out without 176 handwritten entries.

### 4.2 What remains explicit

After subtracting the 11 top-level context-to-Procedure input projections and the 176 repeated context-forwarding mappings, the remaining **43 `from:` mappings** in the MAS Procedure are Operation-output dependencies, including:
- subscription state → secondary-auth/context creation;
- context state and session keys → UECM/policy;
- policy state, anchor, address, and updated policy outputs;
- charging/resource handles;
- N4 SEID and RAN tunnel TEID/IP;
- event/resource finalization dependencies.

These are real producer/consumer dependencies. They are not equivalent to common context fan-out.

Some may become auto-resolvable when contracts expose semantic output IDs and the target input declares the expected semantic ID. But generic fields such as `stateRef` are not enough: many producers emit a `stateRef`, and it is unsafe to select one by field name or “nearest previous node.” For the initial migration, keep the exact producer explicit for opaque handles and state references.

The MAS ToolCatalog also uses constrained constants (for example, profile-specific request type, PDU Session type, SSC mode, allocator, rating group, and event name). These are not context bindings. They are Skill/deployment policy values and should remain explicit or be represented by a separately owned, versioned profile contract—not inferred from context.

### 4.3 MAS conclusion

MAS provides strong evidence that Binding Plan can materially simplify YAML: common context fan-out should be declared once and resolved against Operation semantic input contracts. Producer-specific resource handles, profile constants, and side-effect ordering remain explicit.

## 5. Observation / Predicate migration findings

### 5.1 Current source model

The current Predicate files declare, per observation:
- `ref`;
- `scope`;
- `freshness`;
- evaluator expression consuming `observations.<name>`.

The Host source confirms a separate ObservationSource abstraction, but the current execution path does **not** keep acquisition separate from Predicate evaluation:
- `ObservationRequest` carries an Observation Ref, grounded scope, and correlation refs;
- `ObservationSource.acquire()` returns an acquired observation with status, normalized value, and evidence;
- `CompositeObservationSource` routes each exact Observation Ref to one trusted source;
- source registrations advertise evidence capability;
- importantly, the current `PredicateEngine.evaluate()` iterates the Predicate's `observations` declarations and calls `self._source.acquire()` itself before evaluating CEL. Acquisition is therefore implicit in the current Predicate execution contract.

The vNext proposal that Predicate evaluation be pure is consequently a **real execution-model migration**, not just a YAML rename. A migration must make acquisition scheduling explicit at the same control-flow point and preserve `when`, scope, freshness, evidence checks, UNKNOWN behavior, and trace/audit semantics. It must not eagerly read all facts at Procedure entry or turn one shared snapshot into many duplicate network calls.

This means the proposed semantic distinction (Fact / Observation / acquisition / Evidence / Predicate) is well motivated. But current source syntax still couples the Predicate declaration to acquisition requirements. It must be migrated deliberately.

### 5.2 MAS

All 17 MAS Predicates refer to the same `mas.establishment.snapshot`. The source does not identify a Skill-local READ Operation that acquires this snapshot, nor does the ToolCatalog excerpt establish an owner-backed snapshot Operation with its own Input/Output Schema and Evidence guarantee.

**Migration blocker:** identify the actual MAS snapshot producer/owner and define its governed READ Operation contract (or explicitly identify the event/journal projection that provides the snapshot). Do not invent a READ Operation merely to make the YAML fit the new model.

### 5.3 5GC

The 17 Observation refs span multiple authorities and phases. The current repository includes distinct Provider, Fabric, and simulation observation-source implementations. The registered source-class mapping for all 17 current 5GC Predicate Observation refs is recorded separately in the owner inventory. This does not yet establish corresponding formally declared READ Operation contracts.

**Migration blocker:** build an Observation inventory with, for every ref:
- authoritative fact producer;
- acquisition/projection owner;
- exact scope and correlation contract;
- Output Schema / normalization contract;
- evidence capability and temporal guarantees;
- whether acquisition is a fresh read, a read of a stored event/journal, or a projection of an earlier Operation output;
- whether a prior Operation already produced sufficient evidence (avoid redundant acquisition).

Only after this inventory can a Predicate be rewritten to consume a prior Operation output or a scheduled READ Operation.

### 5.4 Required design correction

Do not interpret “Predicate is pure” as “all current observation acquisitions must become explicit new network calls.” Some facts are already captured by Fabric or produced by an earlier Operation. The new model must expose the correct read of the authoritative stored fact/projection, or reuse adequate existing output/evidence, without fabricating a new external read.

## 6. Binding classification from this rehearsal

| Binding category | 5GC | MAS | vNext treatment |
|---|---|---|---|
| Context → Procedure input | Present, typed | Present, typed | Keep as declared context projection |
| Procedure context → repeated Operation inputs | Many repeated aliases | 176 repeated mappings | Primary auto-binding target, after semantic contract IDs exist |
| Operation output → Operation input | Exact handles and artifacts | 43 mappings | Auto only with unique semantic producer + definite path; otherwise explicit |
| Operation output → Predicate | Present through postcondition/evaluation patterns | State snapshot predicates | Same Binding Plan; no hidden acquisition |
| Observation Ref → Predicate | 17 unique Observation Refs | 1 shared ref across 17 predicates | Requires owner/acquisition inventory before migration |
| Constant/profile value | A few explicit values | Several constrained profile constants | Keep explicit or move to separately owned versioned profile contract |
| Script input/output | Skill-owned projections | No local scripts in current MAS Procedure | Keep explicit and contract-checked |

## 7. Revised authoring direction (illustrative only)

The following is a conceptual shape, not frozen YAML syntax:

```yaml
procedures:
  establish-session:
    context:
      # A declared projection of the shared Context Contract.
      subject: context.subject
      request: context.request
      facts: context.facts

    nodes:
      validate-subscription:
        call: ca.pdu_session.subscription.validate

      create-context:
        call: ca.pdu_session.context.create
        with:
          subscriptionStateRef:
            from: validate-subscription.output.stateRef
```

For this to compile deterministically:
- the Context Contract must define stable semantic identities for its fields;
- each Operation Input Schema must declare the semantic identity expected by each input;
- the compiler must prove compatible type/nullability and path availability;
- the compiler must not bind generic `stateRef` fields by name;
- any constants remain explicit/profile-owned;
- the compiled Binding Plan records every resolved source even when the source YAML omits routine mappings.

This example intentionally leaves the final syntax open. The actual context projection key and explicit-binding placement must be tested against both fixtures.

## 8. What this rehearsal changes in the design

The rehearsal supports these decisions:
1. Keep Binding Plan as Compiler-generated, complete IR/artifact—not a second hand-authored mapping language.
2. Make shared Context projection + semantic Operation input identity the first automatic-binding capability.
3. Do not automatically collapse producer handles, generic `stateRef`, Fabric holds, or policy/session identities.
4. Preserve a small explicit mapping mechanism for real data dependencies and special values.
5. Keep Procedure and Predicate on the same binding model.
6. Separate Predicate evaluation from acquisition, but migrate Observation Refs only after an owner-by-owner inventory.
7. Do not add `bindings.yaml` for this first iteration.
8. Do not rename `procedure.yaml` based on this rehearsal; it provides no evidence for a filename change.

## 9. Remaining work before syntax freeze

1. Produce the complete 5GC Observation Ref → producer/acquisition/Operation/Schema/Evidence matrix.
2. Identify the MAS snapshot owner and its READ/projection contract; confirm whether it is a single reusable snapshot or several independently refreshed facts.
3. Define stable semantic-field identifiers in the shared Context Contract and Operation contracts.
4. Prototype Compiler resolution for the 11 MAS common context fields and representative 5GC context aliases.
5. Prove branch-sensitive definite assignment and reject ambiguous generic handles such as `stateRef`.
6. Compare compiled old/new plans for both Skills, including Effect, ordering, scope, provenance, freshness, and failure outcomes.
7. Only then freeze the exact YAML keys and whether exceptional bindings live under node-level `with` or a Procedure-level section.

## 10. Non-goals and safety

- No current v0.2 behavior is changed by this rehearsal.
- No live 5GC operation or external mutation is performed.
- No current Observation Source is deleted or replaced.
- No automatic binding is approved solely by matching property names.
- No claim is made that the current Compiler can generate this proposed Binding Plan.
