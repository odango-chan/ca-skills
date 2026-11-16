---
name: establish-pdu-session
description: CA-SL v1alpha4 illustrative Open5GS / UE-requested initial PDU Session establishment source.
---

# Establish PDU Session — 5GC

**Source language:** CA-SL v1alpha4 (pinned normative specification `7f84393ee8c395e4d8c39a74cb5000a1f896588d`).

**Adoption state: NOT_QUALIFIED.** This is an authoring and editor example, **not** a linked, executable or approved 5GC Skill. Its `urn:example:` dependency identities and evidence guarantees are illustration-only; there is no trusted v1alpha4 ToolCatalog or CapabilityContracts publication in this repository. The Compiler **must fail closed** when those exports or their exact version/trust bindings are absent.

## Scope and business progression

One admitted, initial IPv4 / SSC1, local non-roaming PDU Session request with no secondary authentication requirement. Host/Owner must bind UE, PSI, Invocation lifecycle, resource and late callback to the exact admitted instance; none of those execution identities are Skill-authored context.

The conventional SMF procedure follows the 3GPP sequence: Step 4 UDM Session Management Subscription retrieval and subscription; Step 7b PCF SM Policy Association establishment; native SMF Step 8 session/UPF selection within N4 preparation; N4 Session Establishment; Step 11 N1/N2 transfer; access-network completion through the SMF-side Step 15 result; the SMF's N4 Session Modification; and durable resource responsibility.

The Skill keeps business decisions visible:
- Step 4 Postconditions verify the UDM response and whether the requested DNN, S-NSSAI, PDU Session Type and SSC Mode are allowed by the subscription. The compatibility check is a Predicate Script within the Step 4 Postcondition, not a separate Procedure Node.
- The Step 7b PCF Create Owner consumes the validated UDM read result and SDM subscription handle, derives the PCF request internally, and performs its pre-dispatch governance. The Skill exposes only the business action and its association-ownership result; it has no intermediate PCF input-building Script or readiness Predicate.
- Step 8 is native SMF processing, not an independent Skill business result in this profile. The UPN Owner performs native UPF/session-address selection as part of N4 preparation; its N4 Operation Result carries the effective configuration consumed by N1/N2 preparation.
- After Step 15, the SMF continues its own N4 Session Modification. The Skill invokes one local CA Mock Tool that waits for Fabric to receive the matching real N4 Modification Response and returns the typed completion result/Evidence. The Mock does not send another N4 request and does not query SMF context.

The Skill does **not** expose Host/Runtime plumbing. Hold binding, Claim, callback/waiter correlation, Journal, exact-original Reconcile, PCF request preparation/governance, operation-context lookup, N1/N2 response-artifact preparation and the deferred step 17 SBI response obligation are internal to Host/Owner adapters. The SSM Operation may remain pending for the exact step 15 event; that is an Owner completion contract, not an author-level Wait. Runtime resumes the same Invocation after the Operation returns. These mechanisms remain mandatory and must be covered by trusted contracts; hiding them does not remove their safety requirements.

The target UPN/SSM Owner callables and the local N4-completion Mock Tool contract/Evidence are **not published**. See the [migration decision register](../../MIGRATION-REVIEW-v1alpha4.md). The old complete 5GC business Case catalog is retained in `examples/legacy/establish-pdu-session/cases/` for migration review, not imported as v1alpha4 test fixtures.

## Host invocation boundary (outside the Procedure)

The incoming TS 23.502 §4.3.2.2.1 step 3 CreateSMContext Request is the Host ingress trigger, not an authored Procedure Node. Host is responsible for source/action/identity admission, duplicate suppression, business-instance association, Invocation lifecycle and correlation before Skill execution. These details remain Host-private and reach Tool adapters only through trusted Host-to-Tool / Runtime dispatch metadata.

The later step 15 Nsmf_PDUSession_UpdateSMContext Request is not a new Skill invocation. Host admits the inbound request, matches it to the exact pending update-sm-context Owner Operation using trusted UE/PSI/HostBusinessInstance and transfer-operation association, and supplies it to that Operation. Once the Owner returns the validated result, Runtime resumes the same Invocation at the pending Node; the graph does not restart at start. Duplicate, stale and late callbacks are handled by Host/Owner correlation and late-result responsibility, never by selecting a new Skill.

Host retains the exact step 15 request/response transport obligation privately. After the local Mock Tool has confirmed the real N4 Modification result and the Procedure has reached its terminal business outcome, Host emits the paired step 17 Nsmf_PDUSession_UpdateSMContext Response for that exact request. No response handle, ingressRef or lifecycleRef is exposed to Skill source. The response mapping for definitive failure and unresolved outcomes remains an Owner/Host contract publication gate.

The Skill's global Contract Precondition validates only the admitted business request profile. It is not an ingress-eligibility or Host-lifecycle check. The first Procedure Node is the Step 4 UDM interaction, get-sm-subscription-data.

## 3GPP Traceability — SMF view

**Pinned reference:** 3GPP TS 23.502 V18.12.0 (Release 18), §4.3.2.2.1; N4 procedures §4.4.1.2–§4.4.1.3. This table describes intended mapping, not Owner approval or product conformance.

| Procedure Node | 3GPP source / interaction | Classification and SMF responsibility |
|---|---|---|
| `get-sm-subscription-data` | step 4 — `Nudm_SDM_Get` | `3GPP_NATIVE`: retrieve Session Management Subscription data. |
| `subscribe-sm-data` | step 4 — `Nudm_SDM_Subscribe` | `3GPP_NATIVE`: subscribe to Session Management Subscription updates; Owner adapter internally binds and claims the exact original request. |
| `establish-sm-policy-association` | step 7b — `Npcf_SMPolicyControl_Create` | `3GPP_NATIVE`: the PCF Owner consumes the UDM read result and SDM subscription handle, derives the request, enforces pre-dispatch governance and returns the authoritative association result/Evidence. |
| `establish-n4-session` | step 8 native SMF session/UPF selection, then steps 10a–10b; §4.4.1.2 N4 Session Establishment | `CA_ADAPTER`: UPN Owner performs native selection and N4 establishment as one interaction boundary; its result carries the effective configuration required by N1/N2. |
| `transfer-n1n2-message` | step 11 — `Namf_Communication_N1N2MessageTransfer` | `3GPP_NATIVE`: SMF transfers N1/N2 information to AMF. The adapter prepares the response and binds the exact request internally; ACK does not prove RAN acceptance. |
| `update-sm-context` | step 15 — `Nsmf_PDUSession_UpdateSMContext Request` (AMF → SMF); access-network setup in steps 12–14 precedes it | `CA_ADAPTER`: the SSM Owner Operation completes asynchronously when Host correlates the exact inbound request to this pending Operation. Runtime resumes the same Invocation; it is not a new Skill invocation. |
| `receive-n4-session-modification` | steps 16a–16b; §4.4.1.3 N4 Session Modification Request/Response | `CA_ADAPTER`: a local CA Mock Tool waits for Fabric to receive the matching real SMF N4 Response and returns its typed completion result; it does not send N4. |
| `ca-transfer-resource-responsibility` | CA lifecycle handoff after successful network procedure | `CA_EXTENSION`: no direct 3GPP procedure counterpart. |
| `ca-transfer-failed-resource-responsibility` | CA lifecycle handoff after confirmed failure | `CA_EXTENSION`: no direct 3GPP procedure counterpart. |
| `verify-pdu-session-establishment` | final facts derived from steps 15–17 | `CA_EXTENSION`: final Goal proof over authoritative network facts and resource responsibility. |

**Resolved service entry/exit boundaries:** step 3 `Nsmf_PDUSession_CreateSMContext Request` and its early step 5 response belong to the Host service ingress/exit boundary; step 5 is not final Goal proof. Step 15 `Nsmf_PDUSession_UpdateSMContext Request` is admitted by Host and correlated to the pending `update-sm-context` Operation in the existing Invocation. Step 17 `Nsmf_PDUSession_UpdateSMContext Response` is the paired Host service exit for that exact request, emitted after Fabric has received the real N4 Modification Response and the Procedure has reached its terminal business outcome. Neither response is a new Skill Node or a new Skill invocation. The exact Host/Owner transport, timeout and failure-response contract remains NOT_PUBLISHED; the example does not claim live conformance.

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
| `urn:example:connectionagent:capability:ca:n4-session-modification-completion-read:v1` | Illustrative least-privilege access to the local Mock completion result; exact Capability ID NOT PUBLISHED |
| `urn:example:connectionagent:capability:ca:resource-responsibility:v1` | CA resource lifecycle handoff |

The exact IDs must be replaced only by matching trusted CapabilityContracts exports. Generic legacy grants such as `fivegc-session-mutation` are not sufficient evidence of narrow NF/service authorization.

## Runtime and evidence boundary

**No author-level Wait/Await/Poll, Hold, Claim, waiter, Journal or Reconcile.** These are Host/Runtime/Owner-adapter responsibilities, not Skill business steps. The Procedure MUST NOT expose `holdRef`, `waiterRef`, `claimRef` or `journalRef` as arguments or outputs. The responsible adapter resolves exact correlation from trusted Invocation Context and Owner state, preserves UE/Session/ingress/lifecycle/current-instance binding, claims once, sends once, records the original operation and reconciles only that exact operation. If the Owner cannot prove these guarantees, linking must fail closed.

The PCF Create adapter must internally derive its request from the exact UDM read result and SDM subscription handle, then verify the exact held PCF request, pre-N4 baseline, lifecycle isolation and absence of a competing forwarded Create before dispatch. Its association-owned Evidence must bind the durable result to the exact Skill occurrence, UE/PSI and request; PCF input-readiness and governance intermediates are not separate Skill Predicates. The AMF N1/N2 transfer adapter must internally resolve the exact held request, validate delivery context and response artifact, and only then claim and dispatch. These are mandatory Owner pre-dispatch guarantees, not author Nodes or extra Capability grants.

Asynchronous access-network completion belongs to the SSM Owner Operation. Host correlates the later step 15 request to the pending Operation and Runtime resumes the same Invocation; the Operation may report success only when its published contract and authoritative Result/Evidence prove the relevant SMF-side completion. An AMF transfer acknowledgement alone never proves RAN adoption or N4 forwarding readiness.

N4 Session Modification is performed by the real SMF while processing the Step 15 request. The local CA Mock Tool owns only the wait/correlation against Fabric's matching N4 Modification Response and returns the typed result/Evidence consumed by `establishment.n4.forwarding_ready`. It does not issue a second N4 request, query network state, or replace the SMF's protocol work. Its ToolCatalog/Schema/Capability/Evidence contract remains unpublished.

Every Mutation `OUTCOME_UNKNOWN` goes to an explicit safe stop. An Owner-published `mutation.reconcile` can be used **only through the Host common safety boundary**, not an authored `reconcile` Node. The only successful Invocation edge is `verify-pdu-session-establishment.postcondition.routes.PASS: SUCCEEDED`, where all listed predicates must pass with authoritative, fresh, same-lifecycle Evidence.

**Known blockers:** missing exact v1alpha4 Owner/Capability publications, checked output Schemas and Evidence descriptors, confirmed callable input identities, and Compiler/Studio/Host §45.2 execution evidence. Do **not** infer completion or production readiness from YAML syntax checks.


## Context ownership

The Skill receives only the Host-resolved opaque UE subject handle (ueRef) plus its own validated request. It does not receive ingressRef, lifecycleRef, instanceId, hold, waiter or journal metadata. Host ingress admission and business-instance correlation finish before this Procedure starts; the request-profile Predicate is a business gate, not a Host lifecycle check.

This Skill does not declare a direct Observation. It consumes the validated business request and the declared Operation Results/Evidence. The local CA Mock Tool supplies the N4 completion result only after Fabric receives the matching real SMF N4 Modification Response; it does not read an SMF context projection. See the CA Agent Host 5GC context boundary: https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/design/5gc-agent-context-access-boundary-v1alpha4.md.
