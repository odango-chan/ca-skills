---
name: establish-pdu-session
description: CA-SL v1alpha4 illustrative Open5GS / UE-requested initial PDU Session establishment source.
---

# Establish PDU Session — 5GC

**Source language:** CA-SL v1alpha4 (pinned normative specification `7f84393ee8c395e4d8c39a74cb5000a1f896588d`).

**Adoption state: NOT_QUALIFIED.** This is an authoring and editor example, **not** a linked, executable or approved 5GC Skill. Its `urn:example:` dependency identities and evidence guarantees are illustration-only; there is no trusted v1alpha4 ToolCatalog or CapabilityContracts publication in this repository. The Compiler **must fail closed** when those exports or their exact version/trust bindings are absent.

## Scope and business progression

One admitted, initial IPv4 / SSC1, local non-roaming PDU Session request. Never substitute an arbitrary UE, PSI, lifecycle, resource or late callback; identity and Scope require independent Host/Owner proof.

The conventional SMF procedure follows the 3GPP sequence: Step 4 UDM Session Management Subscription retrieval and subscription; Step 7b PCF SM Policy Association establishment; Step 8 SMF local session-configuration selection; N4 Session Establishment; Step 11 N1/N2 transfer; access-network completion through the SMF-side Step 15 result; N4 Session Modification; and durable resource responsibility.

The Skill keeps business decisions visible:
- Step 4 Postconditions verify the UDM response and whether the requested DNN, S-NSSAI, PDU Session Type and SSC Mode are allowed by the subscription.
- A local Script constructs the PCF policy inputs for Step 7b.
- A separate local Script performs Step 8 session-configuration selection. Its output is passed explicitly to N4 establishment and subsequent session preparation.

The Skill does **not** expose Host/Runtime plumbing. Hold binding, Claim, waiter correlation, Journal, exact-original Reconcile, PCF request preparation/governance, operation-context lookup and N1/N2 response-artifact preparation are internal to the responsible Owner/Tool adapters. These mechanisms remain mandatory and must be covered by their trusted contracts; hiding them does not remove their safety requirements.

The target UPN/SSM Owner callables and their v1alpha4 schemas/evidence are **not published**. See the [migration decision register](../../MIGRATION-REVIEW-v1alpha4.md). The old complete 5GC business Case catalog is retained in `examples/legacy/establish-pdu-session/cases/` for migration review, not imported as v1alpha4 test fixtures.

## 3GPP Traceability — SMF view

**Pinned reference:** 3GPP TS 23.502 V18.12.0 (Release 18), §4.3.2.2.1; N4 procedures §4.4.1.2–§4.4.1.3. This table describes intended mapping, not Owner approval or product conformance.

| Procedure Node | 3GPP source / interaction | Classification and SMF responsibility |
|---|---|---|
| `admit-create-sm-context-request` | §4.3.2.2.1 step 3 — AMF → SMF `Nsmf_PDUSession_CreateSMContext Request` | `CA_EXTENSION`: validate admitted invocation, identity and lifecycle. |
| `get-sm-subscription-data` | step 4 — `Nudm_SDM_Get` | `3GPP_NATIVE`: retrieve Session Management Subscription data. |
| `subscribe-sm-data` | step 4 — `Nudm_SDM_Subscribe` | `3GPP_NATIVE`: subscribe to Session Management Subscription updates; Owner adapter internally binds and claims the exact original request. |
| `build-sm-policy-association-inputs` | step 7b — SMF local construction of the PCF policy request from the validated subscription | `3GPP_LOCAL`: pure Script data transformation; no external call and no Capability. |
| `establish-sm-policy-association` | step 7b — `Npcf_SMPolicyControl_Create` | `3GPP_NATIVE`: establish the SM Policy Association. Owner adapter internally resolves PCF request inputs and enforces pre-dispatch governance. |
| `select-session-configuration` | step 8 — SMF local session-configuration selection (including the admitted SSC Mode / PDU Session Type profile) | `3GPP_LOCAL`: pure Script selection; no SBI operation and no Capability. |
| `establish-n4-session` | steps 10a–10b; §4.4.1.2 N4 Session Establishment | `CA_ADAPTER`: UPN Owner completes N4 establishment; the callable is not a 3GPP SBI operation. |
| `transfer-n1n2-message` | step 11 — `Namf_Communication_N1N2MessageTransfer` | `3GPP_NATIVE`: SMF transfers N1/N2 information to AMF. The adapter prepares the response and binds the exact request internally; ACK does not prove RAN acceptance. |
| `complete-an-resource-setup` | steps 12–15; step 15 is `Nsmf_PDUSession_UpdateSMContext Request` | `CA_ADAPTER`: SSM wraps the asynchronous access-network completion. AMF/(R)AN/UE own steps 12–14; the SMF receives the result through step 15. |
| `modify-n4-session` | steps 16a–16b; §4.4.1.3 N4 Session Modification | `CA_ADAPTER`: UPN Owner completes forwarding modification. |
| `ca-transfer-resource-responsibility` | CA lifecycle handoff after successful network procedure | `CA_EXTENSION`: no direct 3GPP procedure counterpart. |
| `ca-transfer-failed-resource-responsibility` | CA lifecycle handoff after confirmed failure | `CA_EXTENSION`: no direct 3GPP procedure counterpart. |
| `verify-pdu-session-establishment` | final facts derived from steps 15–17 | `CA_EXTENSION`: final Goal proof over authoritative network facts and resource responsibility. |

**Open 3GPP boundaries:** TS 23.502 step 5 `Nsmf_PDUSession_CreateSMContext Response` is an early response and is not final PDU Session establishment. Step 17 `Nsmf_PDUSession_UpdateSMContext Response` is the later response after the access-network result and N4 modification. The current graph still needs an explicit decision on whether each response is owned by the SMF entry/Host boundary or a dedicated Owner operation. Do not infer that either response is covered by a later PCF/N4 result or by the final Predicate alone.

Step 9 (SMF-initiated SM Policy Association Modification) is conditional and must be included only when the admitted profile requires it. Step 16c (UDM UECM Registration), step 18 (SM Context Status Notify) and step 21 (unsubscription) also require explicit applicability decisions; omission is not implicit PASS.

### Capability mapping

The following are illustrative IDs only; they are **not** published CapabilityContracts exports. Procedure Scripts and Runtime-internal coordination are deliberately absent from this list.

| Capability placeholder | Standard / CA scope |
|---|---|
| `urn:example:connectionagent:capability:3gpp:nudm-sdm-get:v1` | UDM `Nudm_SDM_Get` |
| `urn:example:connectionagent:capability:3gpp:nudm-sdm-subscribe:v1` | UDM `Nudm_SDM_Subscribe` |
| `urn:example:connectionagent:capability:3gpp:npcf-sm-policy-control-create:v1` | PCF `Npcf_SMPolicyControl_Create` |
| `urn:example:connectionagent:capability:3gpp:n4-session-establishment:v1` | UPF N4 Session Establishment |
| `urn:example:connectionagent:capability:3gpp:namf-communication-n1n2-transfer:v1` | AMF `Namf_Communication_N1N2MessageTransfer` |
| `urn:example:connectionagent:capability:ca:ssm-access-network-completion:v1` | SSM adapter for SMF-side access-network completion / Step 15 result |
| `urn:example:connectionagent:capability:3gpp:n4-session-modification:v1` | UPF N4 Session Modification |
| `urn:example:connectionagent:capability:ca:resource-responsibility:v1` | CA resource lifecycle handoff |

The exact IDs must be replaced only by matching trusted CapabilityContracts exports. Generic legacy grants such as `fivegc-session-mutation` are not sufficient evidence of narrow NF/service authorization.

## Runtime and evidence boundary

**No author-level Wait/Await/Poll, Hold, Claim, waiter, Journal or Reconcile.** These are Host/Runtime/Owner-adapter responsibilities, not Skill business steps. The Procedure MUST NOT expose `holdRef`, `waiterRef`, `claimRef` or `journalRef` as arguments or outputs. The responsible adapter resolves exact correlation from trusted Invocation Context and Owner state, preserves UE/Session/ingress/lifecycle/current-instance binding, claims once, sends once, records the original operation and reconciles only that exact operation. If the Owner cannot prove these guarantees, linking must fail closed.

The PCF Create adapter must internally verify the exact held PCF request, pre-N4 baseline, lifecycle isolation and absence of a competing forwarded Create before dispatch. The AMF N1/N2 transfer adapter must internally resolve the exact held request, validate delivery context and response artifact, and only then claim and dispatch. These are mandatory Owner pre-dispatch guarantees, not author Nodes or extra Capability grants.

Asynchronous access-network completion belongs to the SSM Owner Operation. It may report success only when its published contract and authoritative Result/Evidence prove the relevant SMF-side completion; an AMF transfer acknowledgement alone never proves RAN adoption or N4 forwarding readiness.

Every Mutation `OUTCOME_UNKNOWN` goes to an explicit safe stop. An Owner-published `mutation.reconcile` can be used **only through the Host common safety boundary**, not an authored `reconcile` Node. The only successful Invocation edge is `verify-pdu-session-establishment.postcondition.routes.PASS: SUCCEEDED`, where all listed predicates must pass with authoritative, fresh, same-lifecycle Evidence.

**Known blockers:** missing exact v1alpha4 Owner/Capability publications, checked output Schemas and Evidence descriptors, confirmed callable input identities, and Compiler/Studio/Host §45.2 execution evidence. Do **not** infer completion or production readiness from YAML syntax checks.


## Context ownership

The Skill receives only the Host-resolved opaque UE subject handle (ueRef) plus its own validated request. It does not receive ingressRef, lifecycleRef, instanceId, hold, waiter or journal metadata.

The Agent may request explicit read-only Observations only for context owned by the SMF MAS. It does not directly query AMF, UDM, PCF, UPF or other NF context. If a Tool needs non-SMF context, the responsible Tool/Owner adapter obtains and validates it internally and returns its declared Operation Result/Evidence.

This initial PDU Session establishment flow does not need a pre-existing SMF context query: the SM Context is created by the procedure itself. Do not turn SESSION_NOT_FOUND into a successful precondition. See the CA Agent Host 5GC context boundary: https://github.com/odango-chan/ca-agent-demo/blob/main/docs/design/5gc-agent-context-access-boundary-v1alpha4.md.
