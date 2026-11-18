> **Status notice (2026-11-13):** Legacy ObservationSource ownership inventory. It records current implementation/source facts, not the final vNext public contract model. The [CA-SL vNext Specification](../../skill-language-spec.zh-CN.md) defines Observation Query as a specialized read-only Tool contract and is authoritative for new syntax.

# Observation Owner and Acquisition Inventory — vNext

Status: **SOURCE OWNER MAPPED / READ CONTRACT MIGRATION NOT READY**  
Date: 2026-11-12  
Sources: `odango-chan/ca-agent-demo` main, especially `skills/establish-pdu-session/assurance/predicates.yaml`, `skills/establish-pdu-session-mas/assurance/predicates.yaml`, `src/ca_agent_host/integrations/fivegc/provider_resident.py`, `src/ca_agent_host/integrations/fivegc/composition.py`, and `tools/adapters/open5gs/`.

## 1. Corrected inventory basis

The 5GC `predicates.yaml` contains **17 distinct Observation refs**, not 19. The other two `ref:` values are **script evaluator references** (`skill.evaluate-transfer-start` and `skill.evaluate-udm-read`) and are not Observation sources. This corrects the initial lexical count in the migration rehearsal. MAS has **17 predicates** consuming a single distinct `mas.establishment.snapshot` Observation ref.

The mapping below establishes **current Runtime source registration/code ownership**, not formal vNext READ Operation completeness. The current production acquisition API remains `ObservationSource.acquire(ObservationRequest)`. These entries do not prove that an equivalent READ Operation, Output Schema, source guarantee, or Studio/Compiler contract already exists.

## 2. Current 5GC Ref → registered source mapping

| Predicate Observation Ref | Registered source class / module | Immediate source / fact provenance | Acquisition shape | Migration status |
|---|---|---|---|---|
| `createdsession.procedure_context` | Resident ingress source; `integrations/env_fabric/ingress_observation.py` and `integrations/fivegc/composition.py` | Trusted Fabric/resident ingress, exact HELD message | Captured ingress context/projection | Source registered; READ contract TODO |
| `createdsession.udm_hold` | `CreatedSessionUdmHoldObservationSource`, `tools/adapters/open5gs/udm_hold.py` | Fabric-held UDM transaction, through hold store | Read exact hold projection | Source registered; READ contract TODO |
| `createdsession.pcf_hold` | `CreatedSessionPcfHoldObservationSource`, `tools/adapters/open5gs/pcf_hold.py` | Fabric-held PCF transaction, through hold store | Read exact hold projection | Source registered; READ contract TODO |
| `createdsession.pcf_create_inputs` | `CreatedSessionPcfCreateInputsObservationSource`, `tools/adapters/open5gs/pcf_inputs.py` | Provider-built PCF input handle/store | Read prepared input projection | Source registered; READ contract TODO |
| `createdsession.pcf_create_governance` | `CreatedSessionPcfGovernanceObservationSource`, `tools/adapters/open5gs/pcf_governance.py` | Fabric hold-control governance query + hold store | Fresh owner governance read (conditional wiring) | Source registered conditionally; READ contract TODO |
| `createdsession.udm_subscription_resource` | `CreatedSessionResourceObservationSource`, `tools/adapters/open5gs/resource_evidence.py` | Resource-evidence store populated by managed operations | Read resource responsibility projection | Source registered; READ contract TODO |
| `createdsession.pcf_association_resource` | same `CreatedSessionResourceObservationSource` | Resource-evidence store | Read resource responsibility projection | Source registered; READ contract TODO |
| `createdsession.n4_baseline` | `CreatedSessionN4BaselineObservationSource`, `tools/adapters/open5gs/n4_evidence.py` | Provider SMF/UPF N4 read + baseline store | Live owner read/baseline capture, exact Pre-N4 scope (conditional wiring) | Source registered conditionally; READ contract TODO |
| `createdsession.n4_initial_resources` | `CreatedSessionN4ObservationSource`, `tools/adapters/open5gs/n4_evidence.py` | Provider SMF/UPF read + N4 baseline/resource store | Live owner read + projection (conditional wiring) | Source registered conditionally; READ contract TODO |
| `createdsession.n1n2_hold` | `CreatedSessionN1N2HoldObservationSource`, `tools/adapters/open5gs/n1n2_hold.py` | Fabric-held N1/N2 transaction, hold store | Read exact hold projection | Source registered; READ contract TODO |
| `createdsession.nas_delivery_context` | `CreatedSessionOperationContextObservationSource`, `tools/adapters/open5gs/context.py` | Provider operation-context store | Read prepared context projection | Source registered; READ contract TODO |
| `createdsession.amf_transfer_result` | `CreatedSessionAMFTransferObservationSource`, `tools/adapters/open5gs/n1n2_evidence.py` | AMF transfer evidence store; attached by `integrations/fivegc/c_resident.py` | Read operation result evidence | Source registered in C composition; READ contract TODO |
| `createdsession.ran_setup_result` | `CreatedSessionRANSetupObservationSource`, `tools/adapters/open5gs/core_network_evidence.py` | Provider current RAN adoption read + N4 baseline anchor | Live owner read (conditional wiring) | Source registered conditionally; READ contract TODO |
| `createdsession.n4_forwarding_resources` | `CreatedSessionN4ForwardingObservationSource`, `tools/adapters/open5gs/core_network_evidence.py` | Provider current forwarding read + N4 baseline anchor | Live owner read (conditional wiring) | Source registered conditionally; READ contract TODO |
| `createdsession.resource_responsibility` | `CreatedSessionReferenceObservationSource`, `tools/adapters/open5gs/responsibility.py` | Agent reference journal | Read responsibility/lifecycle projection | Source registered; READ contract TODO |
| `sbi.operation.result` | `CreatedSessionUDMObservationSource`, `tools/adapters/open5gs/udm_evidence.py` | Provider UDM read result store | Read exact prior invocation result/receipt | Source registered; output reuse candidate |
| `createdsession.lifecycle_registration` | `CreatedSessionReferenceObservationSource`, `tools/adapters/open5gs/responsibility.py` | Agent reference journal | Read lifecycle projection | Source registered; READ contract TODO |

Source evidence: `provider_resident.py` composes the internal sources and enumerates `covered_observations`; `c_resident.py` attaches AMF-transfer evidence; `composition.py` attaches deployment ingress; `runtime/composite.py` routes exact refs, rejecting duplicate registrations. Optional flags for governance/N4/core-network sources matter: a known source class does not imply it is enabled in every deployment.

### 2.1 Important distinctions

- The current `ca.session.udm_hold.bind`, `ca.session.pcf_hold.bind`, `ca.session.pcf_create_inputs.read` and `ca.session.operation_context.read` Operations are **not automatically equivalent** to their corresponding Observation refs. An Operation may create a handle/projection; the Observation Source may independently validate its current scope and state. Migration must compare the exact Output Schema, authority, freshness, and correlation before reusing the Operation output.
- N4 baseline is specifically a **Pre-N4** fact anchored to an exact policy association and lifecycle; Post-N4 current forwarding is different. Do not merge those refs into a generic N4 read.
- `sbi.operation.result` is the exact prior UDM Tool Operation output, not an independent network read. `nudm-sdm-get.output.result` is the Host-normalized `CreatedSessionUDMResult.runtime_value()` projection; vNext binds that exact output and attaches Host Evidence from the same full Provider receipt, preserving invocation/transaction/request/record/digest/target/source provenance and freshness. The normalized projection needs its own Host Schema, distinct from the Provider wire-result Schema.
- `createdsession.pcf_create_governance` may be absent when governance wiring is disabled; an absent owner is not proof of readiness.
- Observation sources expose `EvidenceCapability`, and some supply true owner provenance/observed time while others have weaker contracts. **Do not infer uniform evidence strength from the common interface.**
- The generic `CaProvider5GCObservationSource` in `integrations/ca_provider_5gc/observation_source.py` is a separate provider observation adapter; it declares `UNPROVEN_EVIDENCE_CAPABILITY` and must not be silently substituted for stronger CreatedSession-specific owner sources.

## 3. MAS snapshot analysis

Current `establish-pdu-session-mas/assurance/predicates.yaml` contains **17 Predicates** all referencing `mas.establishment.snapshot` with the same broad UE/PDU session/ingress/lifecycle scope and a 5s freshness requirement.

The reviewed MAS design in `skills/establish-pdu-session-mas/design/tool-contract.yaml` is marked **NOT_READY**: external MAS adapters, per-field outputs, independent Effect contracts, reconcile results, and owner-grade proofs are not implemented. Its listed Operations are business operations; this review has not established a registered, owner-backed MAS snapshot READ Operation.

Consequently:
- snapshot producer, storage/projection owner, scope, generation identity, and observation time are **OPEN**;
- there is no basis to claim all 17 conditions share one authoritative snapshot instance merely because they share a Ref;
- repeated predicates must preserve their freshness and exact invocation/session association; a cached result may be reused only with a declared cache/freshness policy;
- `stateRef` is an opaque attested handle in the draft, not a generic substitute for the actual facts underlying each predicate;
- do not fabricate `mas.establishment.snapshot.read` until the MAS owner and schema are verified.

## 4. Required vNext mapping contract

For each entry, the future mapping table must specify these fields before declaring migration complete:

`observationRefLegacy`, `factSemanticId`, `authority`, `factProducer`, `projectionOwner`, `acquisitionOperationId`, `operationEffect`, `inputSchemaRef`, `outputSchemaRef`, `scopeSchemaRef`, `correlationFields`, `timeSemantics`, `freshnessPolicy`, `evidenceGuarantees`, `reuseFromProducer`, `deploymentAvailability`, `negativeOrUnknownSemantics`, `requiredRegressionCases`.

A legacy Observation Ref may map to:
1. an existing prior Operation output **with sufficient verified evidence**;
2. an existing READ Operation whose returned fact/evidence genuinely matches;
3. a new owner-declared READ Operation reading authoritative current or stored facts;
4. a governed deterministic projection with an explicit owner and preserved evidence lineage.

These are **mapping alternatives**, not permission for the Compiler or Runtime to choose by string similarity. Any missing authority or ambiguous scope must fail closed.

## 5. Migration gates

| Gate | Pass criterion | Current result |
|---|---|---|
| M0: source inventory | Every actual Predicate Observation Ref mapped to current registered source class | **PASS for 5GC (17/17 source-class mappings); MAS source owner OPEN** |
| M1: authority and schemas | Exact authoritative producer, data schema, correlation, and evidence guarantees for each ref | **OPEN** |
| M2: replacement READ or producer output | Explicit equivalent Operation/acquisition contract for every required fact | **OPEN** |
| M3: Compiler binding | Deterministic semantic input mapping, exact producer path, definite assignment, no field-name guessing | **OPEN** |
| M4: execution equivalence | Same ordering, Effect, wait/reconcile, PASS/FAIL/UNKNOWN, freshness and resource identity | **OPEN** |
| M5: live acceptance | Previously passing 5GC real E2E and negative cases remain equivalent | **NOT RUN (design only)** |

## 6. Decision

The semantic direction of `Capability & Authoring Model vNext` remains viable. This inventory supports **removing the parallel callable identity**, not deleting the fact-owner boundaries or evidence guards.

Do not freeze a final Predicate YAML shape or remove `ObservationSource` until M1–M4 have passing fixtures. The next implementation spike should first define shared Context semantic identifiers for MAS context fan-out and then independently close the owner-backed observation contracts. The two tracks can proceed without forcing an invalid snapshot abstraction.


## 7. Normalized output schema follow-up (2026-11-12)

The owner-side field-level audit is recorded in [ca-agent-demo Draft PR #199](https://github.com/odango-chan/ca-agent-demo/pull/199), pinned to the runnable 5GC implementation snapshot. It enumerates the normalized `AcquiredObservation.value` fields for all 17 refs and distinguishes them from Provider/Fabric wire schemas. Treat this as a migration inventory, not a requirement to create 17 new callable READ Operations or to re-run every source. Reuse an existing Operation output or owner projection when its exact data, scope and evidence are sufficient; introduce a distinct acquisition contract only where the vNext Predicate input actually requires one.

The Host Subject/Facts and Script-facing Predicate Evidence-reference schemas are separately proposed in [ca-agent-demo Draft PR #198](https://github.com/odango-chan/ca-agent-demo/pull/198). Its focused schema workflow currently passes 3 tests. These exports remain unmerged; they expose the ingress/lifecycle handles and Evidence refs, not the full ingress or journal payloads.


## 8. Normalized output Schema publication update (2026-11-12)

ca-agent-demo Draft PR [#200](https://github.com/odango-chan/ca-agent-demo/pull/200) proposes 15 normalized projection Schemas covering 16 of the 17 legacy Observation refs (the two resource-ownership refs share a structural Schema while retaining distinct fact identities). These include the ingress `procedure-context` payload and the two Host reference-journal projections, in addition to adapter outputs. They describe current normalized projections, not the final vNext READ Operation contract set. The focused Schema/fixture workflow passes 5 tests; the PR remains unmerged. The remaining `sbi.operation.result` value is the Host-normalized `CreatedSessionUDMResult.runtime_value()` payload, also returned as the Tool's `output.result`; it needs a separate Host-owned Schema. Provider PR #50 proposes the full upstream GetSmData wire Schema but remains Draft with zero check-runs. After it is accepted, refresh the Host adapter's pinned Provider snapshot/digest, publish the Host projection Schema, and link ToolCatalog `outputSchema.result` to the Host Schema. The runnable `ca-agent-demo` compatibility copy has three legacy UDM schemas (two inputs and one output); official `ca-skills/main` does not. The compatibility output Schema makes `evidenceUsed` optional, unlike the official TypedDict, so do not import those files as official Skill contracts.


## 9. Provider nested UDM Output Schema follow-up (2026-11-12)

The remaining upstream nested subscription schema gap now has a Provider-owned proposal in [ca-provider-5gc PR #50](https://github.com/odango-chan/ca-provider-5gc/pull/50). It replaces broad `type: object` placeholders in the v0alpha2 GetSmData result with the exact Go-projection shape (S-NSSAI, DNN, PDU session types, SSC modes, optional AMBR and QoS/ARP), and enforces MATCHED-only subscription presence.

PR #50 is OPEN / DRAFT and no CI run has yet been observed. Even after it merges, the Host adapter's `runtime_value()` projection remains a distinct schema to publish: it deliberately excludes responder/deployment-binding details and carries only the exact operation/record/selection fields and optional MATCHED subscription consumed by the Predicate.


## 10. 5GC vNext acquisition-path classification

The 17 legacy refs do **not** imply 17 new callable READ Operations. Source inspection of the runnable `ca-agent-demo/main` shows three acquisition patterns:

| Pattern | Legacy refs | Existing producer / source | vNext treatment |
|---|---|---|---|
| Captured ingress projection | `createdsession.procedure_context` | Fabric/resident ingress captures the exact HELD event; Host ingress ObservationSource projects its procedure fields | PR #200 now proposes `procedure-context.schema.yaml` for this payload. PR #198 Subject/Facts expose only ingress/lifecycle refs and do not replace it. Keep event time and source Evidence; the new payload Schema remains draft/unmerged and needs the actual Host ingress export identity |
| Prior Operation-owned artifact + local projection | `createdsession.udm_hold`, `createdsession.pcf_hold`, `createdsession.n1n2_hold`, `createdsession.pcf_create_inputs`, `createdsession.nas_delivery_context`, `createdsession.amf_transfer_result`, `createdsession.udm_subscription_resource`, `createdsession.pcf_association_resource`, `sbi.operation.result` | Existing Operations capture/fetch the authoritative material and populate attempt-local stores; legacy ObservationSources read those same stores and add normalized fields/Evidence. They do not currently show a second external network read | Preserve the existing Operation identity and local projection. Reuse the direct Operation output only after proving exact payload, scope, freshness and Evidence equivalence; otherwise expose a typed Host/adapter projection over the same stored artifact. Do not invent another external read |
| Host journal projection | `createdsession.lifecycle_registration`, `createdsession.resource_responsibility` | Host-owned `CreatedSessionReferenceJournal` | PR #200 now proposes normalized payload Schemas for both. Their source authority is the Agent reference journal (`ca-agent-demo-reference-journal`), not Provider or Open5GS network state. Keep them distinct from static Subject/Facts fields; the proposed export remains draft/unmerged and must be published under the Host journal owner identity |
| Independent owner READ | `createdsession.pcf_create_governance`, `createdsession.n4_baseline`, `createdsession.n4_initial_resources`, `createdsession.ran_setup_result`, `createdsession.n4_forwarding_resources` | PCF governance calls Fabric `read_governance()`; N4/RAN/forwarding sources call the Provider observation client | Five acquisition points across four exact read shapes. N4 baseline and post-N4 initial resources use the same Provider selector/result union at different Procedure points; keep their temporal roles distinct |

The current code supports a useful minimal estimate: **5 independent read acquisitions across 4 distinct owner-read shapes**. N4 baseline and post-N4 initial-resource checks use the same Provider `n4.initial_resources.snapshot` selector and discriminated result shape at two different Procedure points; keep the Pre-N4 and Post-N4 business meanings distinct, but they can share one exact READ Operation identity with a union Output Schema. The other shapes are Fabric PCF governance, Provider RAN setup, and Provider N4 forwarding.

The 9 prior-Operation-owned local projections are not all byte-for-byte reusable from Tool Operation outputs. Source inspection confirms concrete differences: the PCF Create Inputs Operation returns six handles/digests while its Predicate projection has eleven fields; Operation Context returns only `contextRef`/`runtimeInvocationRef` while its Predicate projection has five fields; the three Hold bind outputs omit normalized `bindingStatus`; resource-ownership values are derived from the exact committed-result store; AMF transfer's nested result needs the ObservationSource's nullable-field normalization. By contrast, `sbi.udm.sm_data.get.output.result` is the exact `runtime_value()` payload currently compared by the UDM evaluator. Preserve the exact producer artifact, scope, freshness and Evidence; where the Operation output is insufficient, expose a typed local projection over that same stored result. Never add a second external network request just to replace the old Observation Ref. PR #200 now proposes payload Schemas for all 3 Host-owned projections (ingress plus two journal views); these remain draft/unmerged. PR #198 is the separate Subject/Facts/Evidence-ref export and does not contain those payloads.

The existing Operations that already capture prior material are:

- `sbi.udm.sm_data.get` → exact `sbi.operation.result` projection;
- `ca.session.udm_hold.bind`, `ca.session.pcf_hold.bind`, `ca.session.n1n2_hold.bind` → the corresponding Hold projections;
- `ca.session.pcf_create_inputs.read` → PCF Create input projection;
- `ca.session.operation_context.read` → NAS delivery context projection;
- `sbi.udm.sdm_subscription.create`, `sbi.pcf.sm_policy.create` → the two resource-ownership projections;
- `sbi.amf.n1n2.transfer` → AMF transfer-result projection;
- `ca.session.resource_responsibility.transfer` → responsibility-journal update/projection.

These are not all full payloads in the current ToolCatalog output: several currently return refs/handles while the ObservationSource reads the exact attempt-local store and adds normalized fields plus Evidence. vNext must make the materialized typed result/Evidence available to Predicate without duplicating the external effect. This may mean extending the Operation result projection, not inventing a second Operation.

### 10.1 Bounded wait is orchestration, not the fact payload

The current `ca.session.evidence.await` is a Host READ/wait primitive. It polls the declared ObservationSources under a bounded wait plan and returns only `evidenceRefs`. The subsequent PredicateEngine evaluation performs the final acquisition and receives the normalized value. For N4 this means a bounded series of Provider reads followed by a separate final Provider read.

The vNext authoring model must decide whether this remains a Host orchestration Operation or becomes a Procedure-level bounded-wait construct over an exact owner READ Operation. Either representation must:

- declare the owner READ and exact scope rather than hide a source lookup behind Predicate evaluation;
- preserve the bounded budget/deadline and `KNOWN_ABSENT/CONTINUE` policy;
- keep the final typed READ result and Evidence separate from the wait's evidence-reference summary;
- pass the final result to a pure Predicate without another hidden acquisition.

Do not create a generic `observation.read` callable identity or one new Operation per legacy Observation ref just to remove the old registry. The exact four owner-read shapes above are the starting point; confirm their owner contracts and Capability grouping during the first 5GC migration slice.


### 10.2 Candidate explicit READ Operation surface

The Provider Owner currently exposes one generic `ProviderObservationReadRequest/Result` API whose request contains an `observationRef` selector and whose result is a ref-discriminated union. That is a valid Provider transport contract, but the Skill should not author raw Provider Observation refs as callable identities.

The adapter can expose exact READ Operation identities over that generic Provider API:

| Candidate Operation surface | Fixed Provider selector | Procedure use |
|---|---|---|
| N4 initial-resources read | `n4.initial_resources.snapshot` | `PRE_CREATE` takes exact `pcfPolicyAssociationRef` + `fabricHoldRef` and returns `baselineRef`; `POST_CREATE` takes that exact `baselineRef` plus the same policy-association handle, returns `baselineEvidenceRef` and the confirmed `currentSessionInstanceRef` |
| SMF RAN-setup read | `smf.ran_setup.snapshot` | Takes the exact `currentSessionInstanceRef` from the final post-N4 result plus lifecycle; output must echo and prove that same instance |
| UPF N4-forwarding read | `n4.forwarding_resources.snapshot` | Takes the same exact `currentSessionInstanceRef` from the final post-N4 result plus lifecycle; output proves exactly one matching SMF/UPF pair for that instance |
| Fabric PCF-governance read | Exact `holdRef` from the bound `pcfHold`, plus lifecycle and invocation scope | Acquires current hold/sender/competing-create/lifecycle-isolation facts; Capability grouping remains an Owner decision |

These are semantic candidates, not frozen Operation IDs. Each adapter-facing Operation should have an exact Input/Output contract and a Capability membership. Its adapter fixes the Provider selector; Skill source does not pass a generic `observationRef`.

Candidate Capability grouping:
- group the three Provider assurance reads under one Provider-owned CreatedSession assurance Capability;
- include the PCF governance read in the existing Fabric CreatedSession hold Capability only if Fabric confirms that governance is part of that same authorization boundary; otherwise publish a separate Fabric governance Capability.

The existing Provider main generic Observation request/result schemas still use relative filename `$id` values. Provider PR #50 separately proposes an absolute URL `$id` for the UDM v0alpha2 result, but it remains Draft/unaccepted; the N4/RAN/forwarding exports still need stable absolute versioned identities (or an equivalent explicit export identity). The Fabric PCF governance Schema already has an absolute URL `$id`, but it is still proposed and not yet an approved stable export.

The normalized Operation Output Schemas remain owned by the adapter exposing these Operations; they must not be confused with the Provider wire-result Schema. This keeps the new Skill contract small and typed while preserving the Provider's existing generic transport API behind the adapter.
