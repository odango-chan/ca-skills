# SMF MAS Establishment Skill — vNext Source Migration

Status: **SOURCE MAPPING / OWNER CONTRACTS OPEN / NOT BUILDABLE**  
Target branch: `feat/5gc-vnext-skill-migration`  
Language target: `connectionagent.io/v1alpha2` (breaking; no v0.2 compatibility path)

## 1. Decision

The MAS establishment source mapping proceeds on the existing 5GC vNext migration branch. It does not create a second migration branch or a parallel Skill implementation.

The first executable migration/acceptance baseline remains the conventional 5GC Skill. The MAS Skill can be mapped against the SMF Scheme C business flow in parallel, but it must not be represented as buildable or executable until the SMF Owner and Host publish the exact contracts it consumes.

The existing Agent-demo MAS ToolCatalog is explicitly marked **NOT_READY**. It is useful as a gap inventory, not as an imported ToolCatalog, Capability registry, or source of authoritative Schemas. Do not copy its broad object outputs, inferred stateRef projections, or proposed ca.pdu_session.* Operation identities into the official vNext package.

The legacy `skills/establish-pdu-session-mas/assurance/procedure.yaml` has been removed from the active Skill source package because it still used the v1alpha1 `procedures:` wrapper, hand-authored input types, and legacy Context paths. Its business mapping is retained in this document. Do not restore an executable `assurance/contract.yaml`, `procedure.yaml`, `predicates.yaml`, or request Schema until the exact Owner ToolCatalog, typed Schemas, CapabilityContracts, and Host ingress/context contracts are available. This is an intentional **not-yet-migrated** state, not a v1alpha2 stub and not a buildable Skill.

## 2. Authoritative business sequence

The source mapping uses the Scheme C v0.3.3 certified Establish Plan and its Catalog version sm-mas-ops/3.2 as the business-order reference. The operation inventory below is a design-backed interface inventory; it is not a substitute for the SMF Owner's versioned vNext ToolCatalog export.

| # | SMF MAS Operation | Required business inputs | Relevant successful outputs | Skill-level meaning |
|---:|---|---|---|---|
| 1 | SC.VALIDATE_SUBSCRIPTION | ue_identity, psi, dnn, s_nssai, s_nssai_sd | sub_summary; As-Built also validated and secondary_auth_required | Validate the requested profile and produce the subscription facts consumed by later steps |
| 2 | SAA.SECONDARY_AUTH | required, ue_identity | phase | The supported profile has no required secondary authentication; the certified Plan still records the disposition |
| 3 | SC.CREATE_SM_CONTEXT | identity/session fields, sub_summary | session_keys, lifecycle, sm_context_ref | Create the exact SM context; sm_context_ref is SMF-issued and is the source for the SMF Location |
| 4 | SC.REGISTER_UECM | ue_identity, psi, session_keys | uecm_registered | Register the exact UE/session context |
| 5 | PA.CREATE_SM_POLICY | identity/session fields, session_keys | up_intent, authorized_qos, policy_assoc_id | Create the initial policy association before anchor/address selection |
| 6 | UPS.DECIDE_ANCHOR | dnn, s_nssai | up_anchor | Select the authorized user-plane anchor |
| 7 | IAM.ALLOCATE_ADDRESS | allocator, dnn, up_anchor | ue_addr | Allocate the UE address |
| 8 | PA.UPDATE_SM_POLICY | identity/session fields, session_keys, ue_addr, policy_assoc_id | updated up_intent, authorized_qos, policy_assoc_id | Update the same policy association with the actual allocated address |
| 9 | CA.CREATE_CHARGING | supi, psi, rating_group_refs | charging_ref | Create charging for the same session occurrence |
| 10 | UPN.CREATE_UP_SESSION | updated up_intent, up_anchor, ue_addr, dnn, s_nssai, pdu_session_type | n4_seid, est_done | Establish initial N4 resources; this does not imply N3 is installed |
| 11 | IAM.CONFIRM_ADDRESS | ue_addr, allocator | ue_addr | Optional in the certified Plan; skip only under an Owner-approved profile condition |
| 12 | SSM.SIGNAL_UE_AN | session_keys, ue_addr, n4_seid | an_tunnel, an_tunnel_teid, an_tunnel_ip | Complete the access-signalling exchange and return the SMF-adopted RAN tunnel |
| 13 | UPN.MODIFY_UP_SESSION | same n4_seid plus an_tunnel_teid/an_tunnel_ip (or Owner-defined up_intent form) | n3_synced; As-Built may also return n4_seid | Install N3 forwarding on the same N4 session |
| 14 | SE.EMIT_EVENTS | ev=ESTABLISHED, optional session_keys | last_event | Emit the establishment event; certified Plan marks this step async_ok |

Failure compensation is SC.COMPENSATE_RELEASE. It is a best-effort SMF compensation operation, not proof that every resource was released.

## 3. No Agent-side Wait nodes

The three legacy wait concepts are removed from the MAS Skill execution graph:

| Legacy wait concept | Exact operation that owns completion | Result consumed by the next step |
|---|---|---|
| Initial N4 establishment wait | UPN.CREATE_UP_SESSION | n4_seid, est_done |
| RAN setup/adoption wait | SSM.SIGNAL_UE_AN | an_tunnel, an_tunnel_teid, an_tunnel_ip |
| N4 forwarding wait | UPN.MODIFY_UP_SESSION | n3_synced on the same N4 session |

These are not merged into one synthetic operation. They remain three distinct MAS Operations and three distinct request/response boundaries.

The SMF may hold an individual MasOrchestration.Invoke request while its own southbound exchange completes. The Agent Host observes one Invoke/Response for that Operation. For SSM.SIGNAL_UE_AN, the Host must concurrently relay the original Namf N1N2MessageTransfer to AMF and forward the original Nsmf UpdateSMContext callback to the SMF's existing southbound entry. The transfer acknowledgement alone is not RAN adoption. No generic Host evidence.await, Agent polling, or QueryContext loop is inserted between these Operations.

## 4. Procedure, Predicate, and Observation rules

### 4.1 Procedure

- One Procedure represents the admitted initial-establishment transaction.
- Each MAS business step remains an explicit call to its exact Owner-published Operation.
- The Procedure preserves policy-first ordering: PA.CREATE_SM_POLICY precedes UPS.DECIDE_ANCHOR and IAM.ALLOCATE_ADDRESS; PA.UPDATE_SM_POLICY follows allocation and uses the same policy association.
- UPN.MODIFY_UP_SESSION consumes the exact n4_seid returned by UPN.CREATE_UP_SESSION and the exact access tunnel returned by SSM.SIGNAL_UE_AN.
- SE.EMIT_EVENTS is not a required success postcondition when the certified Operation contract retains async_ok semantics.
- Compensation is a failure path, not a normal finalization step.

### 4.2 Pure Predicates

v1alpha2 Predicates declare explicit inputs and evaluate only those values. The legacy single mas.establishment.snapshot Observation must not be copied into vNext as a generic boolean snapshot.

Where an Operation Output contains the authoritative result and its same-invocation Evidence is sufficient for the required business assertion, bind that exact output to the Predicate; do not add a second read. If the Owner contract does not provide sufficient typed output or Evidence, the Predicate remains UNKNOWN or the Owner must publish the required projection. Do not infer missing facts from operationRef/stateRef handles.

### 4.3 QueryContext

The SMF MAS QueryContext SBI is a separate, implemented, read-only interface (eight MAS projections; status AVAILABLE/UNAVAILABLE). It is not a Wait operation and is not part of the normal establishment sequence.

A future Skill may consume QueryContext through explicit Owner-published READ Operations for a decision or diagnosis that genuinely requires current MAS context. Those READ Operations need their own exact ToolCatalog identities, schemas, Capability membership, scope, and Evidence guarantees. Until then, do not invent a query Operation ID or use polling to imitate a waiter.

## 5. Host / SMF responsibility boundary

| Responsibility | Owner |
|---|---|
| AMF-facing Nsmf CreateSMContext ingress and request normalization | Agent Host ingress adapter |
| One admitted execution owner, invocation identity, correlation, cancellation, and durable journal | Agent Host |
| SM context creation and authoritative sm_context_ref / SMF Location | SMF / SC |
| UDM, PCF, CHF, UPF and access-network business operations | Respective SMF MAS |
| N1N2 relay and raw Nsmf UpdateSMContext callback forwarding | Agent Host protocol adapter, with SSM owning the outstanding business operation |
| RAN adoption and N4/N3 state | SMF MAS / underlying network owners |
| Final Contract evaluation | Host Runtime using exact producer outputs and Evidence |
| Durable responsibility for created resources and late callbacks/results | Explicitly approved Host/resource owner contract; not an invented MAS operation |
| Best-effort failure compensation | SMF / SC.COMPENSATE_RELEASE |

The MAS Skill must not invent a MAS operation named resources.finalize or operation.reconcile. Runtime reconciliation uses the original Operation identity and native reconcile semantics. If the SMF does not publish an authoritative reconciliation result, preserve UNRESOLVED and responsibility rather than treating a timeout as NOT_COMMITTED.

## 6. Owner and semantic gaps that block a v1alpha2 build

1. **ToolCatalog export:** exact versioned Operation IDs, Input/Output Schemas, requiredness, error/result semantics, and declared Effects for all fourteen Operations and SC.COMPENSATE_RELEASE are not yet present as an approved dependency snapshot.
2. **CapabilityContracts:** exact Capability IDs, one-to-one Operation membership, owner, and expected Effect are deployment/Owner contracts. Do not infer Capability IDs from MAS names or Operation prefixes.
3. **Request/Context mapping:** Scheme C inputs include ue_identity/SUPI, PSI, DNN, S-NSSAI, PDU Session Type, and optional GPSI. The existing Skill request schema does not include SUPI. PTI, requestType, servingPlmn, and SSC mode also need a proven source from the admitted Nsmf request or approved deployment context. Never fill them from a guessed default.
4. **Secondary-auth semantics:** the supported profile excludes required secondary authentication. The certified Plan uses required=0 for SAA.SECONDARY_AUTH, while SC.VALIDATE_SUBSCRIPTION also exposes secondary_auth_required in the As-Built output. The Owner must confirm the exact field and rejection rule before binding it.
5. **UECM versus SDM Subscribe:** the certified Scheme C Plan lists SC.REGISTER_UECM. The Agent-demo proposed ToolCatalog describes a composite subscription.register that also performs SDM Subscribe. Do not silently add, remove, or hide an SDM Subscribe action; the SMF Owner must identify the exact operation that owns it.
6. **Address confirmation:** IAM.CONFIRM_ADDRESS is optional in the certified Plan. The exact skip condition, allocator semantics, and address-lease evidence must be Owner-published.
7. **Event semantics:** SE.EMIT_EVENTS is marked async_ok in the certified Plan. The ToolCatalog must define what successful acceptance means and confirm that event completion is not a PDU establishment postcondition.
8. **Resource responsibility and reconciliation:** SC.COMPENSATE_RELEASE is best-effort. Host must publish the durable responsibility/journal and original-operation reconciliation contracts needed to preserve late results and unknown writes. A successful compensation response alone cannot satisfy resources-managed.
9. **Host ingress and single-owner routing:** the Nsmf-compatible Host ingress, Location response, protocol relay, and mutual exclusion with any other ingress/runner must be approved and exported. The current Fabric ingress cannot be silently treated as the same wire contract.
10. **Cases:** migrate the six MAS synthetic Cases only after the v1alpha2 Case contract and exact Owner contracts are available. Do not retain v1alpha1 cases as a compatibility execution path or call synthetic cases live acceptance.

## 7. vNext source migration rules

- Keep the breaking v1alpha2 source model: exact imported Operation IDs, Capability grants only, one explicit `contextSchema` binding, pure Predicate inputs, and explicit producer lineage.
- Do not copy the proposed ca-agent-demo MAS ToolCatalog into the official package.
- Do not author duplicate Operation Input Schemas or Script Input Schemas inside the Skill.
- Do not create an aggregate MAS snapshot schema or a synthetic Observation Source.
- Do not create a generic Wait node for the three MAS-owned completion boundaries.
- Do not use direct operation IDs as Capability grants; wait for the exact Owner CapabilityContracts.
- Do not declare Compiler build, mock qualification, Host readiness, or live 5GC success until the corresponding contracts and tests exist.

## 8. Acceptance status

| Layer | Status |
|---|---|
| Scheme C operation-order mapping | **MAPPED** |
| No-Agent-Wait semantics | **MAPPED** |
| QueryContext boundary | **MAPPED** |
| SMF ToolCatalog and typed schemas | **OPEN / BLOCKED** |
| CapabilityContracts | **OPEN / BLOCKED** |
| Host ingress / relay / responsibility contracts | **OPEN / BLOCKED** |
| v1alpha2 MAS Procedure build | **NOT RUN / BLOCKED** |
| MAS Mock qualification | **NOT RUN** |
| Live MAS E2E | **NOT RUN** |

For the vNext MAS entry, bind `context.ueRef` and the exact ingress/lifecycle
references under `context.correlation` once the MAS Host Owner confirms that
its admission path produces the CA invocation Schema. Keep `context.request`
Skill-owned. The existing MAS authoring files remain migration inputs pending
that Owner confirmation and the exact Operation contracts.
