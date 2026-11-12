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
- `sbi.operation.result` can sometimes reuse the exact earlier UDM operation output, but its current store lookup and proof of invocation/transaction identity must survive.
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

The owner-side field-level audit is now recorded in [ca-agent-demo Draft PR #199](https://github.com/odango-chan/ca-agent-demo/pull/199), pinned to the same 5GC implementation snapshot. It enumerates the normalized `AcquiredObservation.value` fields for all 17 refs and distinguishes those values from Provider/Fabric wire schemas. No Observation output schemas are claimed as published by that PR; it is an inventory only. The next work must publish adapter-owned output Schemas and validate them by running the actual ObservationSource implementations with deterministic owner clients/stores.

The Host Subject/Facts and Predicate Evidence-reference schemas are separately proposed in [ca-agent-demo Draft PR #198](https://github.com/odango-chan/ca-agent-demo/pull/198), with focused schema tests passing. They are not on `main` until merged.


## 8. Normalized output Schema publication update (2026-11-12)

ca-agent-demo Draft PR [#200](https://github.com/odango-chan/ca-agent-demo/pull/200) now proposes 15 exported Schema files covering 16 of the 17 conventional 5GC Observation refs (the two resource-ownership refs share a structural Schema while retaining distinct fact identities). It includes strict normalized projections and a two-branch schema for N4 initial resources. The remaining `sbi.operation.result` output is intentionally blocked by the Provider UDM nested `subscription` Output Schema gap; no broad `object` fallback is introduced. PR #200 is not merged and its focused CI is pending, so these are proposed exports only.


## 9. Provider nested UDM Output Schema follow-up (2026-11-12)

The remaining upstream nested subscription schema gap now has a Provider-owned proposal in [ca-provider-5gc PR #50](https://github.com/odango-chan/ca-provider-5gc/pull/50). It replaces broad `type: object` placeholders in the v0alpha2 GetSmData result with the exact Go-projection shape (S-NSSAI, DNN, PDU session types, SSC modes, optional AMBR and QoS/ARP), and enforces MATCHED-only subscription presence.

PR #50 is OPEN / DRAFT and no CI run has yet been observed. Even after it merges, the Host adapter's `runtime_value()` projection remains a distinct schema to publish: it deliberately excludes responder/deployment-binding details and carries only the exact operation/record/selection fields and optional MATCHED subscription consumed by the Predicate.
