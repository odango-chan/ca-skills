# vNext Binding Migration Rehearsal — 5GC and MAS

Status: **SOURCE REVIEW COMPLETE / FULL 5GC SOURCE MAPPING RECORDED / OWNER-CONTRACT CLOSURE PENDING**  
Date: 2026-11-12  
Target design: [Capability & Authoring Model vNext](capability-authoring-model-vnext.md)  
Source repository: `odango-chan/ca-agent-demo`, `main`  
Source tree commit audited for the official sample sync: `38012852827437185c6343c2b544acad401084e1`

> This is a read-only source rehearsal. No Skill source, ToolCatalog, Runtime, or live 5GC environment was modified. Counts below are lexical counts from the six YAML files and should not be interpreted as a compiler-derived count of removable mappings.

## 1. Executive result

The executable conventional 5GC Skill supports the proposed direction. MAS is retained only as a structural/reference fixture because it does not yet have a runnable end-to-end path. The comparison exposes an important distinction:

- **The MAS draft** appears to repeat the same Procedure context across many Operation calls, which is a useful design hypothesis for contract-backed automatic binding. Its ToolCatalog is NOT_READY and the Skill is not end-to-end runnable, so this is not executable evidence or the first acceptance target.
- **5GC** has a useful Procedure input projection already, but it also has deeply intentional, identity-sensitive bindings involving Fabric holds, exact UDM/PCF transactions, lifecycle, invocation, policy association, and N1/N2 artifacts. These must not be simplified merely because their types are strings or their field names match.
- **5GC and the MAS design fixture** both use Predicate-level Observation Ref declarations. They cannot be migrated by simply replacing `observations:` with an Operation call. For executable acceptance, only 5GC is authoritative; MAS remains a structural reference.
- Existing Tool contracts largely declare JSON Schema names and types. They do not yet provide a sufficiently rich, shared semantic-field identity vocabulary to safely infer every same-named field. Automatic binding cannot be enabled by property-name equality alone.

Conclusion: retain the proposed Binding Plan, but validate its first executable use against the real 5GC shared context projection and contract-backed fan-out, not the MAS draft or unrestricted producer inference. Keep exact producer handles and assurance-sensitive references explicit until contracts prove their semantic identity.

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
| Predicate definitions | 17 | 17 |
| Unique Observation Refs | 17 | 1 |
| Observation scope | Predicate-specific, several scope shapes | Same session scope repeated |
| Freshness examples | 5s and 1h | 5s |

The 17 MAS Predicates all refer to `mas.establishment.snapshot` with the same general UE/PDU-session/ingress/lifecycle scope and 5s freshness. This strongly suggests a shared acquired snapshot/projection with multiple pure evaluations, not 17 separate reads.

The 5GC Skill has 17 Predicate definitions and 18 Procedure `verify` occurrences (`createdsession.lifecycle.ready` is checked at two distinct mutation gates). Its PredicateSet contains 19 `ref` values: 17 distinct Observation Refs plus two Script evaluator paths. The 17 Observation Refs include procedure context, UDM/PCF/N1N2 holds, PCF create inputs/governance, N4 baseline/resources, delivery context, AMF transfer, RAN setup, forwarding, resource responsibility, operation result, and lifecycle registration. These refs represent materially different authorities and assurance questions; they must not be collapsed into one generic snapshot.

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

1. Completed for the current source and Procedure call sites in §§18–21; Owner Output Schema and Evidence closure remains open as recorded in §21.
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

## 11. Follow-up owner inventory

See [Observation Owner and Acquisition Inventory](observation-owner-inventory-vnext.md) for the 17/17 current 5GC source-class registrations, deployment conditions, evidence caveats, and unresolved MAS Snapshot authority. This corrects the earlier lexical 19 count that included two evaluator Script refs.

## 12. Isolated Compiler feasibility spike (2026-11-12)

The prototype is tracked as [ca-skill-compiler PR #7](https://github.com/odango-chan/ca-skill-compiler/pull/7), Draft, based on Compiler PR #5. It adds `internal/bindingspike/` without modifying the existing `internal/compiler/bindings.go` or the paused Schema Engine work.

A locally executed Go 1.23 standalone test of the proposed algorithm passed: synthetic consumer inputs using the **11 actual MAS field names** across 16 call sites yielded **176 deterministic candidate mappings**; representative 5GC UE/Ingress/Lifecycle aliases and negative cases also passed. The semantic identifiers in those tests are deliberately proposed annotations, not current ca-skills v0.2 schema fields. Producer definite availability is supplied by fixtures, not yet computed from the actual CFG; type checking is a strict primitive comparison rather than current Compiler's full JSON Schema reasoning.

**Interpretation:** the spike supports feasibility of context fan-out with explicit semantic contracts. It does not authorize removing any current `with` mappings yet. Actual YAML source ingestion, semantic-field ownership, CFG dominance, complete schema checks, Compilation IR output, and old-vs-new execution/evidence equivalence remain acceptance gates.


## 13. Executable 5GC baseline versus current v0.2 source dialect (2026-11-12)

A file-level comparison was made between the runnable `ca-agent-demo/main` Skill and the official `ca-skills/main` Skill. This is a **semantic/source-contract divergence**, not just a missing-file sync.

| Surface | Runnable `ca-agent-demo` baseline | Official `ca-skills` v0.2 contract | vNext decision needed |
|---|---|---|---|
| Skill-local scripts | `contract.yaml` lists `localTools`; Predicate evaluator refs use `skill.evaluate-*` identities | No `localTools`; evaluator refs are package-relative `scripts/*.py` | Keep Scripts as Skill-owned local computation, not a Tool/Operation/Capability; define one stable Script reference form |
| Script declaration | Python metadata block `connectionagent-tool` declares name, input/output schema, effect and sandbox; input/output classes are empty `dict` subclasses | Metadata block is forbidden; `main(input: dict) -> TypedDict`; sandbox policy is Host-owned | Decide the vNext Script contract without creating a second Tool identity or source-controlled execution policy |
| Script schemas | Legacy Skill-owned Script input Schema files are present in `ca-agent-demo` | Procedure and Predicate Script inputs are derived from declared call-site/Predicate bindings; Script output Schema is generated from strict `TypedDict`; no authored Script Input Schema | Preserve the semantic input projection in the Predicate/Procedure binding declarations; let Compiler derive the effective Script input contract, not a separate Schema file |
| Context Owner schemas | Current executable `contract.yaml` omits `context.schemas`; Host exports are proposed separately in ca-agent-demo PR #198 | v0.2 requires explicit Owner Schema references when those namespaces are used | vNext should use exact versioned Owner `$id` references, not copy physical `lib/` paths |
| Capability grant | The 12 Operation IDs appear in `allowedResources.capabilities` | v0.2 permits direct Operation grants for compatibility | vNext grants the six actual Capability IDs and links each Procedure call to one exact member Operation |

The current `ca-agent-demo` files therefore serve as the **behavior and execution baseline**, but they must not be copied wholesale into `ca-skills` and declared v0.2-conformant. The difference is precisely what the vNext migration must resolve. The Procedure's business ordering and exact producer paths remain the baseline; the authoring representation is what is under review.

Recommended semantic boundary for vNext (syntax remains open): a Script is Skill-owned deterministic local computation, **not** a Tool, Operation or Capability. The current `localTools` list and `skill.*` identities must not become a second authorization/operation namespace. Keep one stable package-relative Script identity. Both Procedure and Predicate Script inputs are derived from their declared bindings plus the relevant Host Context/Evidence contracts; no separate Script Input Schema file is authored. A Skill-owned Predicate interface may declare the semantic inputs, while the Compiler derives and validates the effective projection across all call sites. Script outputs need one strict contract source (authored or generated, not two competing schemas). Sandbox, timeout and execution permissions remain Host-owned, never Python-comment metadata.

The runnable `ca-agent-demo` 5GC copy contains legacy Skill-owned consumer projections for the UDM path (not part of official `ca-skills` v0.2 source):
- `selection-input.schema.yaml` constrains the subscription result consumed by `select_establishment_configuration.py`;
- `udm-read-evaluation-input.schema.yaml` constrains the exact receipt/result consumed by `evaluate_udm_read.py`;
- `predicate-evaluation-result.schema.yaml` constrains the evaluator's PASS / FAIL / UNKNOWN result.

These are **consumer input/output contracts**, not the Provider's Operation Output Schema. For the current feasibility review, the Provider's nested GetSmData result Schema may remain deferred: the existing Skill contracts already constrain what the business logic consumes. The consequence is explicit: until the Provider Output Schema is available, a future Compiler cannot statically prove nested producer fields from the broad ToolCatalog `result: object`; keep those bindings explicit and do not auto-infer their fields. Do not duplicate the Skill consumer projection into the Provider contract.

## 14. Predicate acquisition timing: actual 5GC behavior

The current implementation has two distinct acquisition points that a pure-Predicate migration must account for:

1. `PredicateEngine.evaluate()` evaluates the declared `when` and `scope`, calls `ObservationSource.acquire()`, validates correlation/freshness/evidence capability, then passes the normalized payload and evidence references to CEL or the Script evaluator.
2. `ca.session.evidence.await` uses `BoundedEvidenceWaiter` to call the same ObservationSource while waiting. Its Operation output contains only `evidenceRefs`; it does **not** return the normalized Observation payload. The subsequent Predicate evaluation therefore acquires the Observation again.

This is not a reason to keep acquisition hidden in Predicate. It is a migration constraint: the vNext Procedure must explicitly represent the bounded wait and the Predicate's actual input acquisition. It must not mistake `evidenceRefs` for the Observation payload or silently remove the second verification read. A later design may consolidate the two only after an old/new execution comparison proves equivalent timing, freshness, correlation, trace and UNKNOWN behavior.

For the N4 initial-resource path, preserve the distinction between `KNOWN_ABSENT` and `AVAILABLE`: the wait's `CONTINUE` policy treats a proven pre-convergence absence as “not yet”, while the Predicate decides whether the final acquired state satisfies the condition. This must not become a generic Boolean wait.

## 15. Minimal 5GC feasibility slice before syntax freeze

Use three existing paths to prove the new model, without implementing a Compiler:

| Slice | Existing behavior to preserve | vNext proof required |
|---|---|---|
| UDM Get → selection / `subscription_usable` | One exact GetSmData invocation returns `invocationId`, `result` and Provider provenance. The attempt-local result store holds that same immutable Provider result; the legacy ObservationSource projects it and constructs SourceFactEvidence without another network Get | Model the exact prior Operation output plus an equivalent Runtime Evidence projection as Predicate inputs. Preserve invocation/transaction/record/target correlation and UNKNOWN on source-binding mismatch; keep nested result binding explicit while the Provider Output Schema is deferred |
| Hold bind → hold-bound Predicate | The bind Operation fetches the Fabric hold and stores the exact immutable record in an attempt-local Host store. The ObservationSource reads that same stored record, adds `bindingStatus` and owner Evidence; it does not issue a second Fabric request | Pass the bind Operation output plus an equivalent Host-generated Evidence projection to the pure Predicate. Do not invent another Fabric READ; preserve exact scope, holdRef, currentInstanceRef, deadline and correlation checks |
| N4 bounded wait → initial-resources Predicate | Exact Pre-N4 policy-association scope; bounded retries; `KNOWN_ABSENT` with `CONTINUE`; final Predicate verifies actual resources | Represent wait/acquisition explicitly and supply the final typed Observation + Evidence to a pure Predicate without losing the wait policy or changing the verdict |

These three slices exercise the key vNext claims: reuse of a prior Operation result, reuse of an Operation result with a Host-generated Evidence projection, and a genuinely bounded owner read. In both UDM result and Hold binding, the legacy ObservationSource reads an attempt-local store populated by the preceding Operation; it does not issue another external network request. The migration can remove that duplicate local projection only if the Operation result and Runtime Evidence together preserve the exact same correlation, freshness, scope and provenance guarantees.

The N4 wait remains different: it repeatedly acquires the owner fact and returns only evidence refs; the following Predicate reacquires the payload. Preserve that explicit wait-plus-final-read sequence initially. Do not collapse it to one sample unless a separate old/new comparison proves equivalent behavior.

The remaining 5GC refs can then be mapped using the same alternatives in the Owner Inventory. No MAS execution is required for this first executable feasibility decision.


## 16. Concrete 5GC first-slice mapping (behavior-preserving, syntax-neutral)

This section records what the current runnable code actually does. It is a semantic migration rehearsal, not final YAML syntax.

### 16.1 UDM Get result → selection and pure Predicate

Current path:

- `sbi.udm.sm_data.get` performs the one external Provider GetSmData call and returns `invocationId` plus the Skill-facing `result` projection.
- The same immutable `CreatedSessionUDMResult` is stored under exact `(ueRef, invocationRef, transactionRef)`.
- The legacy `sbi.operation.result` ObservationSource reads that attempt-local store and constructs Provider SourceFactEvidence. It does **not** perform another external UDM Get.
- `evaluate_udm_read.py` compares the `udmReadReceipt.result` passed by the Procedure's `verify.with` mapping with `observations.response`, then classifies the exact response as PASS / FAIL / UNKNOWN. This `udmReadReceipt` is a Predicate-local input projection, not a field in the Host `context.subject` schema.
- `selection-input.schema.yaml` separately constrains the value consumed by `select_establishment_configuration.py`; `udm-read-evaluation-input.schema.yaml` constrains the Predicate input; `predicate-evaluation-result.schema.yaml` constrains the evaluator result.

vNext mapping:

- Keep the UDM Get as one READ Operation.
- Make the exact Operation result and its Provider Evidence available to the pure Predicate as declared inputs. The current attempt-local result-store projection may remain as an internal materialization step if needed to preserve the independent receipt-vs-result comparison; it must not become another network call.
- Preserve exact invocation, transaction, request, Provider record, selected target and source-binding checks. If the Operation output does not carry enough information to construct equivalent Evidence, enrich the Host Operation result/Evidence projection rather than inventing another Provider request.
- Defer the Provider's full nested result Output Schema from this first feasibility slice. The existing Skill consumer schemas already constrain the business logic; keep nested producer paths explicit until the Provider Owner Schema is available.

### 16.2 UDM Hold bind → hold-bound pure Predicate

Current path:

- `ca.session.udm_hold.bind` performs the one Fabric pending-Hold lookup and stores the exact immutable `FabricUdmHold` in `CreatedSessionUdmHoldStore`.
- The Operation returns the hold/request/current-instance refs, digest, operation kind, scope and deadline.
- The legacy `CreatedSessionUdmHoldObservationSource` reads the **same local stored record**, checks exact selector/lifecycle/hold correlation and deadline, adds `bindingStatus: CURRENT`, and constructs the Fabric SourceFactEvidence. It does not issue a second Fabric request.

vNext mapping:

- Treat `ca.session.udm_hold.bind` as the READ Operation that acquires the hold.
- Supply its exact output plus a Host-generated Evidence projection to the pure Predicate. Preserve the current selector, lifecycle, hold ref, current instance, request digest, deadline and correlation checks.
- Do not add a second Fabric READ Operation just to replace the legacy Observation Ref. The current source is a local evidence projection over the bind result, not an independent owner read.

### 16.3 N4 bounded wait → final pure Predicate

Current path:

- `ca.session.evidence.await` repeatedly calls the N4 ObservationSource under the admitted wait scope, deadline and observation budget. For initial N4 resources, `KNOWN_ABSENT` means “not yet” and the declaration uses `CONTINUE`.
- The wait Operation returns only `evidenceRefs`, not the normalized N4 payload.
- The subsequent PredicateEngine evaluation calls the ObservationSource again, validates freshness/correlation/evidence, and passes the final normalized payload to CEL.

vNext mapping:

- Preserve the bounded wait as an explicit step with its exact scope, deadline, budget and `KNOWN_ABSENT/CONTINUE` policy.
- Preserve the final acquisition as an explicit READ step after the wait; its typed payload and Evidence become the pure Predicate inputs. This mirrors the current two acquisition points and avoids treating evidence refs as payload.
- Do not collapse wait and final read into one sample in the first migration. That would change the current timing semantics and requires a separate old/new equivalence decision.

### 16.4 Result of the first-slice rehearsal

These three existing paths show that pure Predicate is feasible without turning all 17 legacy Observation refs into new network Operations:

- UDM result: reuse one prior external READ Operation plus its exact stored-result Evidence projection.
- UDM Hold: reuse one Fabric READ Operation plus a local Host Evidence projection.
- N4 convergence: preserve an explicit bounded wait followed by a final owner READ.

This is enough to validate the core model boundary. The full 17-ref source classification is now recorded in [Observation Owner and Acquisition Inventory](observation-owner-inventory-vnext.md): 1 captured ingress projection, 9 prior-Operation-owned local projections, 2 Host journal projections, and 5 independent owner-read acquisitions across 4 distinct read shapes. The nine local projections do not imply that all existing Operation outputs can be reused unchanged; exact payload/Evidence equivalence must be proved or exposed through a local typed projection over the same stored artifact. The three Host-owned payload schemas are proposed in PR #200, but their stable export identity and release status remain open. Therefore the vNext model does not require 17 new network READ Operations, but it does require explicit owner contracts for every consumed projection.


### 16.5 Capability and Operation count check

The current 5GC Procedure calls **12 unique Operation IDs** across 14 call nodes; `ca.session.evidence.await` is called three times. The deployment CapabilityContracts currently maps all 12 Operations into six Capability groups with exact READ/MUTATION Effect agreement.

The vNext migration can preserve those 12 callable identities and change the Skill grant from the compatibility-era 12 Operation IDs to the six actual Capability IDs. The four independent owner-read shapes identified above are the only candidate additions:

- three Provider READ Operations (N4 initial resources, SMF RAN setup, UPF N4 forwarding), grouped under one new Provider assurance Capability;
- one Fabric PCF governance READ Operation, added to the existing Fabric hold Capability only if that is the Owner-approved authorization boundary; otherwise it requires a separate Capability.

That gives a candidate 16 unique callable Operations if `ca.session.evidence.await` remains a Host orchestration Operation. If bounded wait becomes a Procedure control-flow construct, it gives 15. This count is an impact estimate, not a frozen Capability/Operation contract.


## 17. Official 5GC source synchronization result (2026-11-12)

The official source comparison between `ca-agent-demo/main@38012852827437185c6343c2b544acad401084e1` and `ca-skills/main@3fce09aca32b6a6faf6ec3e9a204d38cc129ec38` found:

- 50 shared files: **42 byte-identical**, 8 different.
- The Procedure, all 36 Cases, all three Reference documents and the public Request Schema are byte-identical.
- All five Script `main()` business bodies are equivalent. Differences are the legacy Agent-side `connectionagent-tool` metadata/input-class annotations versus the official v0.2 `main(input: dict) -> TypedDict` form. Keep the official typed declarations; no behavior rewrite is needed.
- `assurance/contract.yaml` intentionally differs: official v0.2 has explicit Host/Observation Schema references and no `localTools`; do not copy the Agent-side legacy `localTools` list.
- `assurance/predicates.yaml` differs only in Script evaluator identity: keep package-relative `scripts/*.py` refs, not legacy `skill.*` IDs.
- The Agent tree contains 11 additional legacy Script input/output Schema files. They are not copied: v0.2 derives Procedure Script inputs per call site, generates Script output Schemas from strict `TypedDict`, and retains only genuinely Skill-owned authored Schemas. Their shapes are migration evidence for the Predicate binding declarations and Compiler-derived effective input contract, not a reason to restore the old metadata contract.

The only business-source refresh needed was `SKILL.md`, which has been synchronized in [ca-skills PR #25](https://github.com/odango-chan/ca-skills/pull/25). Its source-hygiene workflow passes. The sync updates current Harness prerequisites, decision facts, opaque context ownership, exact occurrence/evidence rules, integration boundary, completion and recovery guidance, while redirecting maintainer links to the authoritative ca-skills docs.

This confirms the official 5GC sample's deterministic Procedure and Script business logic were already aligned with the runnable baseline. Remaining source differences are intentional language-boundary differences or unresolved Owner dependency exports—not stale Procedure behavior.


## 18. Capability → Operation → Effect migration: complete current 5GC map

The current executable 5GC deployment has **six Capability groups and twelve unique callable Operations**. Every current Operation belongs to exactly one Capability, and the expected Effect agrees with the ToolCatalog declaration. This is the complete existing authorization map; it is not a proposal to keep granting Operations directly.

| Capability ID | Owner | Exact Operation | Effect | Current Procedure call site |
|---|---|---|---|---|
| `provider-5gc.createdsession.udm` | `ca-provider-5gc` | `sbi.udm.sm_data.get` | READ | `nudm-sdm-get` |
| `provider-5gc.createdsession.udm` | `ca-provider-5gc` | `sbi.udm.sdm_subscription.create` | MUTATION | `nudm-sdm-subscribe` |
| `provider-5gc.createdsession.pcf` | `ca-provider-5gc` | `sbi.pcf.sm_policy.create` | MUTATION | `npcf-sm-policy-control-create` |
| `provider-5gc.createdsession.context` | `ca-provider-5gc` | `ca.session.operation_context.read` | READ | `resolve-effective-session-configuration` |
| `provider-5gc.createdsession.context` | `ca-provider-5gc` | `ca.session.pcf_create_inputs.read` | READ | `resolve-pcf-create-inputs` |
| `provider-5gc.createdsession.context` | `ca-provider-5gc` | `ca.session.establishment_response.prepare` | READ | `prepare-establishment-response` |
| `env-fabric.createdsession.hold` | `env-fabric` | `ca.session.pcf_hold.bind` | READ | `bind-pcf-hold` |
| `env-fabric.createdsession.hold` | `env-fabric` | `ca.session.udm_hold.bind` | READ | `bind-udm-hold` |
| `env-fabric.createdsession.hold` | `env-fabric` | `ca.session.n1n2_hold.bind` | READ | `bind-n1n2-hold` |
| `ca-provider-5gc.createdsession.transfer` | `ca-provider-5gc` | `sbi.amf.n1n2.transfer` | MUTATION | `namf-communication-n1n2-message-transfer` |
| `ca-agent-host.createdsession.runtime` | `ca-agent-host` | `ca.session.evidence.await` | READ | `await-initial-resources`, `await-ran-result`, `await-forwarding` |
| `ca-agent-host.createdsession.runtime` | `ca-agent-host` | `ca.session.resource_responsibility.transfer` | MUTATION | `transfer` |

### 18.1 Exact old → new grant transformation

Current compatibility source lists the twelve Operation IDs above under `allowedResources.capabilities`. The vNext Skill grant must instead list the six Capability IDs, qualified by an alias bound to the deployment's immutable, trusted CapabilityContracts build input:

- `<capability-contract-alias>::provider-5gc.createdsession.udm`
- `<capability-contract-alias>::provider-5gc.createdsession.pcf`
- `<capability-contract-alias>::provider-5gc.createdsession.context`
- `<capability-contract-alias>::env-fabric.createdsession.hold`
- `<capability-contract-alias>::ca-provider-5gc.createdsession.transfer`
- `<capability-contract-alias>::ca-agent-host.createdsession.runtime`

Procedure calls continue to name one exact Operation, qualified by the alias resolving its ToolCatalog contract. The Compiler must link each call to exactly one Capability membership across the resolved ToolCatalog contracts and the separately supplied trusted CapabilityContracts input, then cross-check the Tool Effect against the independently declared expected Effect. If the trusted CapabilityContracts input is absent, static authorization proof cannot be claimed; Runtime admission remains authoritative. The Skill does not grant an entire Tool by display name, owner name, prefix, or implicit hierarchy.

The CapabilityContracts alias is a logical build-input binding, not a normal Skill dependency locator: the deployment-owned CapabilityContracts must be supplied as a separate trusted Compiler input, not inferred from ordinary Skill dependency snapshots. The ToolCatalog alias resolves the Operation contracts from the ordinary resolved dependency set. Neither alias is a repository/path/revision field in Skill YAML. The exact alias values are not frozen here.

The deployment-owned `budgetExemptOperations` entry for `ca.session.resource_responsibility.transfer` is not an additional Skill grant and is not an Effect. It remains a separate Runtime budget policy.

### 18.2 Additional READs required by the pure-Predicate migration

The six-group map above is complete for the current twelve Operations, but it is not yet the final vNext Operation set. The source inventory identifies four independent READ shapes:

1. Provider N4 initial-resources read. It is used at two Procedure points: Pre-N4 baseline and Post-N4 initial-resource verification. One exact Operation identity may serve both points if its Output Schema is a discriminated result that preserves the distinct temporal/business meanings.
2. Provider SMF RAN-setup read.
3. Provider UPF N4-forwarding read.
4. Fabric PCF-create-governance read.

The first three Provider reads are candidates for one new Provider assurance Capability. The Fabric governance read may join `env-fabric.createdsession.hold` only if Fabric confirms that it is the same authorization boundary; otherwise it needs a separate Capability. These are Owner decisions, not a Skill-side grouping choice.

The current `ca.session.evidence.await` is a Host orchestration/wait Operation, not one of the four owner-read shapes. If the proposed Procedure-level `wait` construct replaces it, the current Host Operation leaves the Skill grant and the candidate total is **15 unique callable Operations** (11 retained + 4 new READs). If it remains a Host orchestration Operation, the candidate total is **16**. The six existing Capability groups are therefore the migration baseline, not a frozen final count after new READ contracts are introduced.

## 19. Complete 17-ref Predicate input and acquisition migration

The source count is **17 distinct Observation Refs**. The two additional `ref` values in `predicates.yaml` are evaluator Script paths and are not Observation Refs. The following table maps every current Predicate to its actual Procedure point and the minimum vNext input/acquisition treatment.

| Predicate | Current Observation Ref | Current Procedure point | Source class | vNext input / acquisition treatment | Existing scope and freshness |
|---|---|---|---|---|---|
| `createdsession.ingress.eligible` | `createdsession.procedure_context` | Entry Procedure applicability | Captured ingress projection | Declare an `ingressContext` input from the trusted Host ingress projection before Procedure entry. This is already-captured event context, not a new network READ inside the Procedure. | UE, PSI, PTI, request type, ingress; 5s |
| `createdsession.udm.hold_bound` | `createdsession.udm_hold` | After `bind-udm-hold` | Prior-Operation local projection | The `bind-udm-hold` Tool output already carries the held-request fields (hold/request/current-instance refs, digest, operation kind, DNN/S-NSSAI, environment, lifecycle and deadline) but not `bindingStatus`. The ObservationSource rechecks the exact selector, lifecycle, correlation and deadline, then attaches Fabric Evidence. Reuse that exact output/artifact only with equivalent checks; do not synthesize `CURRENT` merely from call success. | UE, DNN, SST, ingress, lifecycle; 5s |
| `createdsession.pcf.hold_bound` | `createdsession.pcf_hold` | After `bind-pcf-hold` | Prior-Operation local projection | The `bind-pcf-hold` Tool output carries hold/request/current-instance, policy-association, digest, operation-kind, environment, lifecycle and deadline, but not `bindingStatus`. The ObservationSource additionally validates the exact selector/held-request correlation and attaches Fabric Evidence. Reuse the exact bound artifact with those checks; do not infer the normalized state from the handle alone. | UE, PSI, ingress, lifecycle; 5s |
| `createdsession.pcf.create_inputs.ready` | `createdsession.pcf_create_inputs` | After `resolve-pcf-create-inputs` | Prior-Operation local projection | The Tool output contains only `pcfCreateInputsRef`, `runtimeInvocationRef`, `pcfPolicyAssociationRef`, `fabricHoldRef`, `fabricHoldRequestDigest` and `selectionDigest`. The 11-field Predicate projection also contains allocated IPv4/IPv6-prefix values, `fieldSources`, lifecycle and normalized binding status. Build that projection from the exact stored Provider result already captured by this READ plus its Evidence; the Tool output alone is insufficient, and no second network read is needed. | UE, PSI, PTI, request type, ingress, lifecycle; 5s |
| `createdsession.pcf.create_governed` | `createdsession.pcf_create_governance` | Before `sbi.pcf.sm_policy.create` | Independent Fabric READ | Schedule the exact PCF-governance READ before the Predicate and bind its result/Evidence as `governance`. The source is conditional today; absent or unadmitted governance remains UNKNOWN and blocks the mutation. | UE, PSI, lifecycle, ingress; 5s |
| `createdsession.udm.subscription_owned` | `createdsession.udm_subscription_resource` | After `nudm-sdm-subscribe` | Prior-Operation local projection | Build the resource-ownership projection from the exact committed subscription result already stored by the mutation backend, then attach its Provider/Fabric Evidence. The normalized `creationState` / `ownership` / `managementState` fields are not a substitute for the committed response and durable resource-evidence record; a successful mutation response alone is not proof of Agent ownership. | UE, PSI, PTI, request type, ingress, lifecycle; 1h |
| `createdsession.pcf.association_owned` | `createdsession.pcf_association_resource` | After `npcf-sm-policy-control-create` | Prior-Operation local projection | Build the same structural resource-ownership projection from the exact committed PCF result and its evidence store. Preserve the distinction between Agent management responsibility and native PCF association exclusivity; do not infer ownership from the PCF mutation's success status alone. | UE, PSI, PTI, request type, ingress, lifecycle; 1h |
| `createdsession.n4.baseline_clear` | `createdsession.n4_baseline` | PCF-create preconditions, before mutation | Independent Provider READ | Call the N4 initial-resources READ at the Pre-N4 point with exact `pcfPolicyAssociationRef` and `fabricHoldRef`; bind its `baselineRef` result and Evidence as `n4Baseline`. Preserve the exact baseline handle; do not treat it as a post-mutation session instance. | UE, PSI, PTI, request type, ingress, lifecycle, policy association, Fabric hold; 5s |
| `createdsession.n4.initial_resources_ready` | `createdsession.n4_initial_resources` | `await-initial-resources` sub-Procedure | Independent Provider READ | Wait on the exact N4 initial-resources READ, then perform the separate final READ using the exact `n4Baseline.baselineRef` and same `pcfPolicyAssociationRef` / lifecycle. Bind the final payload/Evidence as `n4InitialResources`; require its `baselineEvidenceRef` to match that exact baseline. The wait's evidence-reference summary is not the Predicate payload. | UE, PSI, PTI, request type, ingress, lifecycle, exact baseline ref, policy association; 5s |
| `createdsession.n1n2.hold_bound` | `createdsession.n1n2_hold` | After `bind-n1n2-hold` | Prior-Operation local projection | The `bind-n1n2-hold` Tool output carries hold/request/current-instance, digest, operation kind, target NF, SUPI, environment, lifecycle and deadline, but not `bindingStatus`. Preserve the ObservationSource's exact selector, deadline and held-request checks and attach Fabric Evidence; the current call site passes only `holdRef`. | UE, PSI, ingress, lifecycle; 5s |
| `createdsession.delivery_context.ready` | `createdsession.nas_delivery_context` | After `resolve-effective-session-configuration` (`ca.session.operation_context.read`) | Prior-Operation local projection | The `ca.session.operation_context.read` Tool output contains only `contextRef` and `runtimeInvocationRef`. The five-field Predicate payload (`bindingStatus`, address allocation, NAS-input completeness, delegated-caller authorization and sender reservation) comes from the exact stored Provider result. Resolve that same handle/invocation/purpose from the local store, preserve expiry/freshness and attach Evidence; the handle alone is insufficient and no second network read is needed. | UE, PSI, PTI, request type, ingress, lifecycle; 5s |
| `createdsession.amf.transfer_initiated` | `createdsession.amf_transfer_result` | After `namf-communication-n1n2-message-transfer` | Prior-Operation local projection | Reuse the exact `sbi.amf.n1n2.transfer` output's nested `result` plus its Evidence and the expected `operationRef`. The Tool output already carries the operation correlation, network outcome, target AMF/binding, and captured response fields; the ObservationSource additionally normalizes omitted optional `responseOrigin` / `cause` values to null. Preserve that projection and the exact operation/transaction correlation; no second Provider read is needed. | UE, PSI, PTI, request type, ingress, lifecycle, operation ref; 1h |
| `createdsession.ran.setup_accepted` | `createdsession.ran_setup_result` | `await-ran-result` sub-Procedure | Independent Provider READ | Wait on the exact SMF RAN-setup READ, then perform a final READ explicitly bound to `n4InitialResources.currentSessionInstanceRef` and lifecycle. Bind its typed payload/Evidence as `ranSetup`; reject any different or latest-per-UE instance. | UE, PSI, PTI, request type, ingress, lifecycle, exact confirmed N4 instance; 1h |
| `createdsession.n4.forwarding_ready` | `createdsession.n4_forwarding_resources` | `await-forwarding` sub-Procedure | Independent Provider READ | Wait on the exact UPF N4-forwarding READ, then perform a final READ explicitly bound to the same `n4InitialResources.currentSessionInstanceRef` and lifecycle. Bind its typed payload/Evidence as `n4Forwarding`; require the exact SMF/UPF pair and reject any different or latest-per-UE instance. | UE, PSI, PTI, request type, ingress, lifecycle, exact confirmed N4 instance; 5s |
| `createdsession.resources.managed` | `createdsession.resource_responsibility` | After Host `transfer` | Host journal projection | Bind a Host-owned responsibility-journal projection as `resourceResponsibility`. The transfer result may be reused only if it proves the same durable journal state, coverage and retained pending responsibilities; do not infer this from the mutation response. | UE, PSI, PTI, request type, ingress, lifecycle; 5s |
| `createdsession.udm.subscription_usable` | `sbi.operation.result` | After `nudm-sdm-get` | Prior-Operation local projection | The existing `verify.with` binds the full `nudm-sdm-get.output` receipt (`invocationId` plus `result`). The acquired `sbi.operation.result` payload is exactly the `result` subobject returned by `CreatedSessionUDMResult.runtime_value()`; the current evaluator compares these for equality. Declare `output.result` as the Predicate input and attach Provider Evidence correlated to the same invocation/transaction. This is reuse of the exact prior Get, not a second network request. The Provider PR #50 schema describes the full Provider result; it is not the narrower Host-normalized `runtime_value()` Schema, which remains a separate export. | UE, exact invocation ID and transaction ref; 1h |
| `createdsession.lifecycle.ready` | `createdsession.lifecycle_registration` | Before UDM Subscribe and again before PCF Create | Host journal projection | Bind a Host-owned lifecycle-journal READ/projection as `lifecycleRegistration` at both verification points. Preserve the two fresh evaluations; do not reuse the pre-Subscribe result at the later PCF gate without proving it is still within the 5s freshness contract. `lifecycleRef` selects the exact record; it is not itself proof that registration is durable or the receiver is ready. | UE, PSI, PTI, request type, ingress, lifecycle; 5s |

### 19.1 What becomes explicit in Procedure

The matrix yields the following complete classification:

- **1 captured ingress projection**: supplied before Procedure entry from the trusted ingress event. PR #200 also proposes its `procedure-context` payload Schema; PR #198 Subject/Facts only carries the ingress/lifecycle references and does not replace that payload.
- **9 prior-Operation local projections**: reuse the exact stored artifact from an existing Operation. Reuse its direct output only where payload, scope, freshness and Evidence are equivalent; otherwise expose a typed local projection over that same artifact. Never add another external read merely to replace the old Observation Ref.
- **3 Host-owned projections**: one captured ingress payload plus two reference-journal views. PR #200 now proposes normalized payload Schemas for all three; PR #198 separately proposes Subject/Facts handles and Script Evidence refs. These remain draft/unmerged and must be exported under the actual Host ingress/reference-journal owner identities, not mistaken for Provider or Open5GS source facts. A journal reference is not the journal state.
- **5 independent owner-read acquisition points across 4 shapes**: PCF governance, N4 baseline, N4 initial resources after convergence, RAN setup, and N4 forwarding. N4 baseline and post-N4 initial resources can share one exact READ Operation identity only if its output is discriminated and the two Procedure points remain distinct.

Every Predicate must receive its business payload through declared `Predicate.inputs` and a Procedure producer/READ binding. Existing implicit `observations.*`, `subject`, `request` and `facts` access must not survive as hidden evaluator inputs. The current entry Procedure's context projection remains the natural source for request/subject/fact fields; the exact shared Predicate context-projection syntax is still open and must not be replaced by repeated ad-hoc copies.

The current scope and freshness declarations are part of the assurance contract. They must move to the exact READ/producer binding and Predicate input contract without widening scope, substituting a different resource handle, or relabeling acquisition time as source observation time. Host-generated Evidence remains a separate projection at `input.evidence.<alias>`; Scripts cannot author or rewrite it.

## 20. Script identity and I/O contract: 5GC source mapping

The official `ca-skills/main` source already uses package-relative Script references. The runnable `ca-agent-demo` copy's `localTools`, `skill.evaluate-*` identities and `connectionagent-tool` metadata are legacy dialect and are not to be copied into the official package.

| Script identity (package-relative path) | Role and current call site | Input fields from current binding | Strict output TypedDict |
|---|---|---|---|
| `scripts/select_establishment_configuration.py` | Procedure Script, `select-subscription-configuration` | `dnn`, `sNssai`, `requestedPduSessionType`, `requestedSscMode` from Procedure inputs; `udmResult` from `nudm-sdm-get.output.result` | `EstablishmentSelectionOutput` |
| `scripts/build_pcf_policy_inputs.py` | Procedure Script, `build-pcf-policy-inputs` | `subscriptionData` and `subscriptionSource` from `select-subscription-configuration.output` | `PcfPolicyInputsOutput` |
| `scripts/build_n1n2_delivery.py` | Procedure Script, `build-n1n2-delivery` | `preparedResponse` from `prepare-establishment-response.output`; `operationContextRef` from `resolve-effective-session-configuration.output.contextRef`; `policyResultRef` from PCF Create output; `pduSessionType` from Procedure input | `N1N2DeliveryOutput` |
| `scripts/evaluate_udm_read.py` | Predicate evaluator, `createdsession.udm.subscription_usable` | Candidate explicit input: `udmReadResult` from `nudm-sdm-get.output.result`; exact Provider Evidence attached separately and correlated to the full receipt's invocation/transaction | `PredicateEvaluationResult` |
| `scripts/evaluate_transfer_start.py` | Predicate evaluator, `createdsession.amf.transfer_initiated` | Candidate explicit input: transfer result projection plus expected `amfTransferOperationRef`; exact transfer Evidence attached separately | `PredicateEvaluationResult` |

### 20.1 One Script identity; inputs derived at the use site

- A Script is identified by its package-relative source path. Procedure `script` and Predicate `evaluator.ref` use the same identity form; Script is not a Tool, Operation, Capability, or external Effect.
- A Procedure Script's effective input contract is derived from the Binding declarations at its call site. The three current Procedure Scripts already have explicit `with` maps; no separate hand-maintained Script Input Schema is needed.
- A Predicate Script's effective input contract is derived from its declared `Predicate.inputs` plus **all** Procedure `verify.with/from` call sites. Multiple call sites must provide compatible values; a missing or incompatible required input is a build error. No standalone Script Input Schema is authored.
- The Script's output contract is generated from its strict return `TypedDict`, including `Annotated` constraints, `Literal` values and `NotRequired` fields. For this Skill the return types are `EstablishmentSelectionOutput`, `PcfPolicyInputsOutput`, `N1N2DeliveryOutput` and `PredicateEvaluationResult` (the latter is used by both Predicate evaluators).
- Sandbox, timeout, resource budget and execution permissions remain Host/Runtime policy. They are not Script-authored metadata and must not return through the legacy `connectionagent-tool` block.
- The eleven Agent-side legacy Script input/output Schema files remain migration evidence only. They are not copied into the official package and do not become a second source of input definitions.

### 20.2 Predicate evaluator input correction

The current evaluator implementations still read the v0.2 implicit envelope:

- `evaluate_udm_read.py` reads `input.observations.response`, `input.evidence` and `input.subject.udmReadReceipt`. The runnable `ca-agent-demo/main` compatibility copy also contains `udm-read-evaluation-input.schema.yaml` and legacy `connectionagent-tool` metadata, but the authoritative `ca-skills/main` source does **not** contain that authored input Schema or metadata. Its official evaluator uses package-relative Script identity and TypedDict-generated output. Treat the Agent-side legacy input Schema as behavior/field-shape evidence only, not as an official Skill contract or Provider Output Schema. Under the pure-Predicate candidate the evaluator reads declared `input.udmReadResult` and Host-attached Evidence; exact invocation/transaction checks remain grounded in the Evidence attached to the same full producer receipt.
- `evaluate_transfer_start.py` reads `input.observations.response`, `input.evidence` and `input.subject.amfTransferOperationRef`. Under the pure-Predicate candidate the transfer result and expected operation ref are declared inputs, with Evidence attached separately; the response's operation identity, target-service provenance and capture-complete checks remain.

These are migration targets, not source edits. The official v0.2 scripts remain unchanged until the language and Host input projection are approved. The proposed Provider UDM v0alpha2 result Schema is a full upstream result contract; `CreatedSessionUDMResult.runtime_value()` is a narrower Host Predicate payload and still needs its own normalized export.

The PR branch also adds `schemas/predicate-evaluation-result.schema.yaml` as a package-level Predicate evaluation result Schema candidate. It is not a per-Script Output Schema and is not linked by the current official `contract.yaml`, `predicates.yaml`, `procedure.yaml` or `SKILL.md`. Its shape only partially overlaps with the `PredicateEvaluationResult` return `TypedDict` used by both current evaluator Scripts: the TypedDict requires `evidenceUsed`, while this Schema does not; this Schema additionally allows `summary` and `details`. It is not generated from those declarations. Keep it separate from the per-Script output contract: each Script output Schema remains generated from its strict return `TypedDict`. Its exact vNext consumer/owner/link is deferred; this input/acquisition migration does not need to redesign Predicate result output.

## 21. End-to-end 5GC migration rehearsal result and remaining gates

The source-backed mapping now covers the complete current Skill surface:

| Source surface | Current baseline | vNext semantic transformation | Status |
|---|---|---|---|
| Skill contract | Request Schema; two required fact IDs; twelve direct Operation grants; physical `lib/` Host/Observation Schema paths | Keep the Skill-owned Request Schema and fact requirements; replace direct grants with qualified Capability IDs; reference exact versioned Host Subject/Facts/Evidence identities; remove the aggregate Observation payload schema from the Predicate context and use each READ Operation's Owner Output Schema for its domain payload | Semantically mapped; trusted CapabilityContracts binding and Owner exports remain open |
| Procedure | Existing typed context projection, 12 unique Operations / 14 call nodes, explicit resource/transaction handles, reconciliation and terminal branches | Preserve order and explicit handles; allow only contract-proven context auto-binding; add the four independent READ shapes; make the three bounded waits explicit over exact READs or retain a Host wait Operation by a separately approved choice | Semantically mapped; exact wait syntax and new Operation contracts remain open |
| PredicateSet | 17 Observation Refs, per-ref scope/freshness, CEL or two Script evaluators | Replace acquisition-coupled `observations` with declared `inputs`; schedule READs/projections in Procedure; keep Predicate evaluation pure and preserve tri-state outcomes | All 17 refs mapped; Owner contracts and shared context/Evidence input syntax remain open |
| Scripts | Three Procedure Scripts and two Predicate evaluator Scripts; official paths already package-relative | Keep one path identity; derive Procedure Script inputs from call-site Binding, Predicate Script inputs from Predicate declaration plus every call site, and output Schemas from strict TypedDict | Source mapping complete; evaluator input migration awaits Predicate syntax |
| Cases / References | 36 Cases and three Reference documents are already byte-identical across the two repositories | Keep them unchanged as behavior/failure examples; use them to review old/new outcome and recovery equivalence, not as schema owners | No source refresh required |

### 21.1 Owner and semantic blockers

The migration is now complete as a **source/behavior mapping**, but it is not yet an importable or executable vNext Skill. The following are real gates, not reasons to fabricate schemas:

1. **Host payload exports:** PR #198 publishes Subject/Facts and Script Evidence refs; PR #200 additionally proposes the ingress `procedure-context` payload and both Host reference-journal projections (`lifecycle_registration`, `resource_responsibility`). Source inspection matches these projections to the current ingress and journal implementations. They remain Draft/unmerged; confirm the actual Host export namespace and journal owner identity before treating them as stable dependencies. The full Runtime `ObservationEvidence` dataclass remains internal by design.
2. **Normalized local projections:** PR #200's 15 schemas cover 16/17 refs. Source inspection confirms the schemas describe normalized projections, not raw wire results. Several prior Operation outputs are only handles/refs: PCF Create Inputs returns six handles/digests while its Predicate projection has eleven fields; Operation Context returns only `contextRef`/`runtimeInvocationRef` while its Predicate projection has five fields. These need typed projections from the same stored result plus Evidence, not a second network read. Hold bindings also need the existing deadline/correlation rechecks and normalized `bindingStatus`.
3. **Fabric governance and Hold wire:** PR #200 proposes the normalized PCF-governance payload Schema. The upstream governance result remains a proposed Fabric contract, and the loopback pending/claim wire still has no separate Owner-published Schema; the Provider-facing held-request-read contract is not the same API. Keep this behind the Fabric adapter and do not import the similarly named schema as a substitute.
4. **Provider N4/RAN reads:** exact adapter-facing READ Operation identities, Input/Output Schemas, freshness/scope guarantees and Capability membership still need Owner publication. The generic Provider Observation transport selector must remain behind the adapter; Skill source must not pass raw `observationRef` values. N4 baseline and post-N4 checks use the same upstream selector at different phases and must remain distinct in the normalized result.
5. **UDM nested result:** Provider PR #50 proposes an absolute-`$id` full GetSmData result Schema, but remains Draft with no observed check-runs. It does not replace the separate Host-normalized `runtime_value()` projection Schema. The legacy UDM consumer input Schema exists only in the runnable `ca-agent-demo` compatibility copy, not official `ca-skills/main`; do not restore/import it as a Provider Output Schema.
6. **Predicate and wait syntax:** the `Predicate.inputs` shape, shared context projection, Evidence projection, and exact wait/final-read relationship must be frozen together. In particular, the current wait acquisition and subsequent final Predicate acquisition must not be collapsed accidentally.
7. **Capability extension:** the six existing Capability memberships are verified, but the four new READ candidates need owner-approved memberships. The Provider assurance group and Fabric governance grouping are not yet frozen.
8. **Compiler claims:** current Compiler v0.1 does not yet statically link CapabilityContracts or resolve the complete Owner export set. This rehearsal proves source-level feasibility only; it does not claim a successful vNext build.

### 21.2 Cross-repository status checked for this rehearsal

At the time of this update:

- ca-skills PR #24 remains OPEN / DRAFT. Its current Source Hygiene result is tracked on the PR and must be checked against the latest head before review or merge.
- ca-skills PR #25 remains OPEN / DRAFT; its source-hygiene success is recorded separately and does not validate vNext migration.
- ca-agent-demo PRs #198, #199 and #200 remain OPEN / DRAFT. The focused results recorded by their owners are 3 passed for #198 and 5 passed for #200; #199 is documentation/inventory only.
- ca-provider-5gc PR #50 remains OPEN / DRAFT with no observed GitHub check-runs.

The current `ca-agent-demo/main` and `ca-skills/main` sources remain unchanged. No live 5GC operation, Runtime behavior, Compiler implementation or MAS execution is part of this rehearsal.

### 21.3 Feasibility verdict

- **Semantic expressiveness: YES, conditionally.** The current flow can be represented without 17 new network READ Operations or a generic `observation.read` tool. The target needs the six existing Capability grants, explicit producer-backed Predicate inputs for the nine local projections, Host-owned ingress/journal projections, and four exact owner READ shapes. N4 baseline and post-N4 resources are two call points over one discriminated READ contract. The three bounded waits remain separate from the final payload READ.
- **Contract-complete / statically buildable: NOT YET.** Three Host projections and the normalized payload/Evidence equivalence for the nine local projections are not fully exported; the four READ shapes and their Capability memberships are not Owner-approved; the shared Predicate Context/Evidence and wait syntax are not frozen; and the trusted deployment CapabilityContracts BuildRequest binding is not implemented by the current Compiler.
- **Behavior-preserving migration: plausible, not yet proven.** The old control-flow, exact handles, tri-state results, freshness, scope and recovery branches can be retained in the candidate mapping. Equivalence still requires the missing Owner contracts and an old/new plan comparison. In particular, both `createdsession.lifecycle.ready` call sites must remain separate fresh checks, and each wait must be followed by the final READ that currently feeds PredicateEngine.

This answers the feasibility question narrowly: the semantic model has enough concepts to describe the 5GC flow, but the current draft is not yet a complete vNext contract package. The next useful step is to close the specific Owner exports and freeze only the shared input/Evidence/wait boundary—not to build a Compiler or expand the abstraction surface.


## 22. Behavior-preserving target Procedure outline (syntax-neutral; NOT FROZEN)

This is the target **semantic Procedure**, not proposed final YAML syntax. It keeps the current 5GC order, exact handles, mutations, failure branches, reconciliation and terminal responsibility transfer. It changes only where Predicate data is acquired and how it is passed to a pure Predicate.

### 22.1 Main path

| Stage | Ordered producer / action steps | Pure Predicate input and gate | Continue on PASS |
|---|---|---|---|
| Entry / UDM read | Use the already-captured Host ingress context; call existing `sbi.udm.sm_data.get` | Bind `nudm-sdm-get.output.result` as `udmReadResult`; attach Evidence correlated to the full receipt's `invocationId` / transaction. Evaluate `createdsession.udm.subscription_usable` | UDM Subscribe |
| UDM Subscribe preparation | Run `select_establishment_configuration.py`; call `ca.session.udm_hold.bind` | Project `udmHold` from the exact bound hold plus its validated scope/deadline and Evidence. Evaluate `createdsession.udm.hold_bound`; separately evaluate `createdsession.ingress.eligible` from captured `ingressContext`; acquire a fresh Host journal projection for `createdsession.lifecycle.ready` | Call existing `sbi.udm.sdm_subscription.create` |
| UDM ownership | Keep the existing Subscribe mutation and exact subscription resource handle | Project `udmSubscriptionResource` from the exact committed mutation result / resource-evidence store and Evidence. Evaluate `createdsession.udm.subscription_owned` | PCF Create preparation |
| PCF Create preparation | Call `ca.session.pcf_hold.bind`; call existing `ca.session.pcf_create_inputs.read`; run `build_pcf_policy_inputs.py` | Evaluate `createdsession.pcf.hold_bound` from `pcfHold`; evaluate `createdsession.pcf.create_inputs.ready` from the typed 11-field `pcfCreateInputs` projection over the same stored Provider result; acquire N4 baseline using the exact N4 READ with phase `PRE_CREATE` and evaluate `createdsession.n4.baseline_clear`; acquire Fabric governance for the exact hold and evaluate `createdsession.pcf.create_governed`; acquire a **fresh** lifecycle journal projection and evaluate `createdsession.lifecycle.ready` again | Call existing `sbi.pcf.sm_policy.create` |
| PCF ownership | Keep the existing PCF Create mutation and exact association handle | Project `pcfAssociationResource` from the exact committed mutation result / resource-evidence store and Evidence. Evaluate `createdsession.pcf.association_owned` | Bounded wait for initial N4 resources |
| Initial N4 convergence | Bounded wait over the exact Provider N4 initial-resources READ, phase `POST_CREATE`, with the existing deadline/budget and `KNOWN_ABSENT / CONTINUE` behavior; after convergence, perform one final READ | Bind the final typed payload as `n4InitialResources` with its final-read Evidence. Its `baselineEvidenceRef` must equal the exact `n4Baseline.baselineRef`, and its `currentSessionInstanceRef` becomes the explicit lineage handle for RAN/N4 forwarding. Evaluate `createdsession.n4.initial_resources_ready` | NAS/N2 delivery preparation |
| NAS/N2 preparation | Call existing `ca.session.operation_context.read` for `nas-and-n2-delivery`; resolve its exact stored result; call existing `ca.session.establishment_response.prepare`; run `build_n1n2_delivery.py`; call existing `ca.session.n1n2_hold.bind` | Evaluate `createdsession.delivery_context.ready` from the five-field `deliveryContext` projection; evaluate `createdsession.n1n2.hold_bound` from `n1n2Hold` plus exact hold checks and Evidence | Call existing `sbi.amf.n1n2.transfer` |
| AMF transfer | Keep the existing single-sender / exact hold claim and Provider mutation | Bind the nested transfer result plus expected `operationRef` as `amfTransferResult`, attach transfer Evidence, and evaluate `createdsession.amf.transfer_initiated` | Bounded wait for RAN setup |
| RAN setup | Bounded wait over the exact Provider SMF RAN-setup READ; after convergence, perform one final READ | Bind the final result and Evidence as `ranSetup`, with `currentSessionInstanceRef` equal to the exact instance from `n4InitialResources`. Evaluate `createdsession.ran.setup_accepted` | Bounded wait for N4 forwarding |
| N4 forwarding | Bounded wait over the exact Provider UPF N4-forwarding READ; after convergence, perform one final READ | Bind the final result and Evidence as `n4Forwarding`, with `currentSessionInstanceRef` equal to the same exact instance from `n4InitialResources`. Evaluate `createdsession.n4.forwarding_ready` | Successful finalization |
| Finalization | Keep the existing `ca.session.resource_responsibility.transfer` mutation with its exact lifecycle and disposition | Read the Host reference-journal projection as `resourceResponsibility`; evaluate `createdsession.resources.managed` | `done` on PASS; preserve `safe-stopped` / `unresolved` outcomes on failure |

### 22.2 Exact Predicate input inventory

The 17 Predicate definitions consume these named business inputs. The two `createdsession.lifecycle.ready` call sites intentionally consume **two different fresh acquisitions** of the same logical input:

- Captured Host input: `ingressContext`.
- Existing Operation outputs / local projections: `udmReadResult`, `udmHold`, `pcfHold`, `pcfCreateInputs`, `udmSubscriptionResource`, `pcfAssociationResource`, `n1n2Hold`, `deliveryContext`, `amfTransferResult`.
- Independent owner READ results: `governance`, `n4Baseline`, `n4InitialResources`, `ranSetup`, `n4Forwarding`.
- Host journal projections: `lifecycleRegistration`, `resourceResponsibility`.

The `resourceOwnership` Schema may be shared structurally by the UDM subscription and PCF association values, but the two Predicate inputs retain distinct producer identity, resource handle and Evidence. Likewise, `n4Baseline` and `n4InitialResources` remain distinct named inputs even if one phase-discriminated READ Operation supplies both.

For every producer-backed input, Host attaches the Evidence projection separately. The business payload is not nested inside or reconstructed from Evidence. Predicate Scripts receive neither a generic `observations` map nor hidden `subject/request/facts` fallbacks. Their effective input contract is derived from the declared Predicate interface, all Procedure call sites and the resolved producer/Context schemas.

### 22.3 Wait and acquisition rules

1. The three current waits remain three explicit orchestration points: post-PCF N4 convergence, SMF RAN setup, and UPF N4 forwarding.
2. A wait targets one exact owner READ identity and exact scope. It preserves the current bounded deadline/budget and `KNOWN_ABSENT / CONTINUE` semantics.
3. A wait result is only a convergence/control result. It is **not** the final Predicate business payload.
4. After convergence, the Procedure performs the final typed READ and passes that exact payload plus its Evidence to the pure Predicate. No hidden acquisition occurs during Predicate evaluation.
5. The N4 READ may use one Operation identity with a discriminated `PRE_CREATE` / `POST_CREATE` input/output union. If an Owner cannot guarantee that union contract, use two exact READ identities instead. Either way, the baseline and post-create semantics remain separate.
6. Do not introduce a generic `observation.read` Operation and do not expose raw Provider `observationRef` selectors in Skill source.
7. The N4 lineage is explicit across phases: the Pre-N4 result supplies `n4Baseline.baselineRef`; the post-N4 result must echo it as `baselineEvidenceRef` and supplies `currentSessionInstanceRef`; the RAN and N4-forwarding READs must consume that exact instance ref. An adapter may verify these handles against its attempt-local store, but may not silently select the latest baseline or session by UE.

### 22.4 Authorization and failure behavior

- The existing twelve Operation grants migrate to the six current Capability IDs as recorded in §18. The three Provider assurance READs require one new Provider-owned Capability membership set. Fabric governance is added to the existing Hold Capability only if Fabric confirms the same authorization boundary; otherwise it gets its own Capability.
- If Procedure-level `wait` replaces `ca.session.evidence.await`, the latter leaves the Skill's callable Operation set. The candidate is then **15 callable Operations** (11 retained + 4 new READs); retaining the Host wait Operation yields **16**. This is a design count, not a frozen registry.
- Every existing Predicate keeps its PASS / FAIL / UNKNOWN meaning and route. Operation failure, denial and unresolved mutation outcomes retain their current failed / unresolved paths.
- Keep all exact resource and lifecycle handles explicit: UE, PSI, PTI, ingress, lifecycle, Fabric hold, policy association, UDM invocation/transaction, operation, response artifact, `n4Baseline.baselineRef`, `n4InitialResources.currentSessionInstanceRef`, exact N4 pair/evidence refs, and confirmed N4 instance. Do not infer one handle from another or from matching field names.
- Keep all existing reconciliation nodes for UDM Subscribe, PCF Create, AMF transfer and resource-responsibility transfer. Keep the three finalization paths (`success`, `failed`, `unresolved`) and their safe-stop behavior. The migration must not simplify away uncertainty or late-result responsibility.

### 22.5 What this outline proves—and does not prove

This outline demonstrates that the current 5GC Procedure can be expressed with pure Predicates and explicit acquisition without creating 17 new READ Operations, without a generic Observation tool, and without changing the business order.

It does **not** freeze the YAML placement of `Predicate.inputs`, the `wait` syntax, exact new Operation IDs, dependency aliases, or the trusted CapabilityContracts BuildRequest binding. It also does not claim the missing Owner READ contracts or Host `sbi.operation.result` projection have been published. Those remain the gates in §21.1. The current `ca-skills/main` and `ca-agent-demo/main` trees contain 36 `case.yaml` files, one Cases README and three Reference documents (40 blobs total); all 40 blob SHAs are byte-identical across the two repositories. This migration does not modify them, so the semantic outline can be reviewed against the existing 36 behavior cases and three references without refreshing fixtures.

## 23. Case and Reference semantic coverage review

The complete 5GC fixture set was reviewed against the target Procedure outline. `ca-skills/main` and `ca-agent-demo/main` still contain the same 36 `case.yaml` files, one Cases README and three Reference documents; the 40 corresponding file blobs are byte-identical. No Case or Reference source was changed by this migration rehearsal.

### 23.1 Case-to-target coverage

| Case group | Cases | Existing business obligation | vNext element that must preserve it |
|---|---|---|---|
| Success and ingress/UDM gates | 01–04 | Complete profile succeeds; missing ingress, partial/ambiguous/untrusted UDM evidence remains UNKNOWN; explicit target rejection remains FAIL | Captured `ingressContext`; pure `udmReadResult` plus same-invocation Provider Evidence; preserve PASS / FAIL / UNKNOWN and stop-before-mutation routing |
| Subscription and PCF ownership/governance | 05–07 | Missing address/callback or governance blocks creation; unknown subscription ownership remains with the durable manager; a returned PCF Location is not exclusive association ownership | Typed `pcfCreateInputs` and governance READ; exact committed-result/resource-evidence projections for UDM subscription and PCF association; preserve separate ownership predicates |
| N4 baseline and NAS delivery prerequisites | 08–10 | PCF success does not prove initial N4; stale instance or missing allocation/delegated-caller/sender proof blocks NAS; invalid/stale response artifact stops locally | `PRE_CREATE` baseline and exact baseline handle; bounded `POST_CREATE` wait plus final typed READ; explicit confirmed `currentSessionInstanceRef`; five-field operation-context projection; unchanged response-preparation Script |
| AMF acknowledgement, RAN and forwarding | 11–15 | AMF 202 is not completion; RAN rejection is FAIL; late/ambiguous RAN evidence is UNKNOWN; UPF forwarding failure cannot be masked by SMF remote-DL; no UE-internal observation is required | Separate transfer, RAN and N4-forwarding facts; exact operation/transaction correlation; same confirmed N4 instance across RAN and UPF; no new UE READ |
| Durable responsibility and uncertain mutations | 16–18, 20–28, 35–36 | Missing manager receipt leaves responsibility UNKNOWN; UDM Subscribe, PCF Create and AMF transfer uncertainty reconciles the exact mutation once; late-result responsibility survives all exits; `NOT_COMMITTED` does not authorize retry or successful handoff; conservative recovery still SAFE_STOPPED | Keep existing mutation/reconciliation Operations and their exact handles; Host responsibility-journal projection; preserve `failed`, `unresolved`, `safe-stopped` and terminal responsibility semantics without collapsing them into Predicate FAIL |
| Local denial, lifecycle and read-only uncertainty | 19, 23, 29–31 | Denied response preparation cannot transfer; denied UDM read cannot create resources; known unready lifecycle is FAIL; unavailable lifecycle proof is UNKNOWN; read-only UNKNOWN stops before mutation | Local Script/Operation boundary; two separate fresh `lifecycleRegistration` gates; explicit READ status and tri-state mapping; no inferred PASS |
| Budget and subscription-shape validation | 32–34 | Budget exhaustion after SDM creation stops before PCF; missing required AMBR/QoS fields blocks first mutation; UDM producer/evidence mismatch is UNKNOWN | Runtime-owned budget/deadline; `select_establishment_configuration.py` output contract; exact `udmReadResult`/Evidence invocation lineage; no extra UDM Get |

### 23.2 Reference-to-target constraints

- **`references/3gpp-procedure.md`**: preserve actor boundaries and the non-implications between UDM response, SDM Subscribe, PCF Create, initial N4, AMF transfer acknowledgement, RAN acceptance and N4 forwarding. The target outline retains separate acquisition and Predicate gates for each layer; no lower-layer success becomes a higher-layer verdict.
- **`references/failure-handling.md`**: preserve tri-state interpretation, exact-mutation reconciliation, no blind retry, durable ownership after resource creation, bounded waits and the rule against repeated verification without a relevant world change. The new `wait` is Host orchestration and its final READ remains explicit.
- **`references/session-selection.md`**: preserve requested, subscription-constrained and effective configuration as separate layers. Keep the admitted DNN/S-NSSAI/PDU Session Type/SSC request unchanged; do not infer permission from HTTP 200, rewrite the request, truncate or normalize `allowedSscModes`, or treat selection as allocation/readiness.

### 23.3 What the fixture set does not prove

1. The 36 Cases are authored branch obligations, not live 5GC evidence. Case 01 explicitly says it is synthetic; several later cases likewise label themselves synthetic or qualification obligations.
2. Their common terminal assertion surface is the three downstream predicates `createdsession.ran.setup_accepted`, `createdsession.n4.forwarding_ready` and `createdsession.resources.managed`. Earlier failure cases mark downstream predicates `NOT_EVALUATED`. They do **not** directly assert every one of the 17 Predicate input projections or prove the 15 PR #200 Schema payloads against all 15 live ObservationSources.
3. Case 31 explicitly says Runtime normalization is blocked by Toolchain #131 and that its fixture is not execution evidence. Case 32 says budget/cancellation mapping and durable responsibility still need implementation qualification. Cases 21–28 and 35–36 are synthetic conservative-recovery obligations, not proof that every recovery outcome has been qualified in the running Host.
4. Case 34 delegates concrete receipt/digest mismatch coverage to pure-compute vectors. Those vectors must remain in the future Predicate evaluator regression set; the Case alone does not replace them.

Therefore the existing 36 Cases and three References are sufficient as **unchanged behavioral constraints** for this semantic migration, but they are not a substitute for new vNext binding/schema conformance tests. Before a future Compiler/Runtime implementation is accepted, add focused fixtures for each derived Predicate input projection, producer/Evidence correlation, the N4 phase union and exact instance lineage. Keep those new tests separate from the authored Case/Reference package; do not rewrite the existing examples merely to fit candidate syntax.