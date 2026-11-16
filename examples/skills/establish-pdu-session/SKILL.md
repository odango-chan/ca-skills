---
name: establish-pdu-session
description: CA-SL v1alpha4 illustrative Open5GS / UE-requested initial PDU Session establishment source.
---

# Establish PDU Session — 5GC

**Source language:** CA-SL v1alpha4 (pinned normative specification `7f84393ee8c395e4d8c39a74cb5000a1f896588d`).

**Adoption state: NOT_QUALIFIED.** This is an authoring and editor example, **not** a linked, executable or approved 5GC Skill. Its `urn:example:` dependency identities and evidence guarantees are illustration-only; there is no trusted v1alpha4 ToolCatalog or CapabilityContracts publication in this repository. The Compiler **must fail closed** when those exports or their exact version/trust bindings are absent.

## Scope and business progression

One admitted, initial IPv4 / SSC1, local non-roaming PDU Session request. Never substitute an arbitrary UE, PSI, lifecycle, resource or late callback; identity and Scope require independent Host/Owner proof.

Conventional 5GC **proposed** progression is UDM SM-data retrieval, UDM SDM Subscribe, PCF SM Policy Create, target `UPN.CREATE_UP_SESSION` N4 completion, prepared N1/N2 transfer, target `SSM.SIGNAL_UE_AN` RAN adoption, target `UPN.MODIFY_UP_SESSION` forwarding, and durable resource responsibility. These three §21 target Owners have **not** published callable contracts or qualified Results/Evidence. See [migration decision register](../../MIGRATION-REVIEW-v1alpha4.md). The old complete 5GC business Case catalog is retained in `examples/legacy/establish-pdu-session/cases/` for migration review, not imported as v1alpha4 test fixtures.

## 3GPP Traceability — SMF view

**Pinned reference:** 3GPP TS 23.502 V18.12.0 (Release 18), §4.3.2.2.1; N4 procedures §4.4.1.2–§4.4.1.3. This table describes intended mapping, not Owner approval or product conformance.

| Procedure Node | 3GPP source / interaction | Classification and SMF responsibility |
|---|---|---|
| `admit-create-sm-context-request` | §4.3.2.2.1 step 3 — AMF → SMF `Nsmf_PDUSession_CreateSMContext Request` | `CA_EXTENSION`: validate admitted invocation, identity and lifecycle. |
| `get-sm-subscription-data` | step 4 — `Nudm_SDM_Get` | `3GPP_NATIVE`: retrieve Session Management Subscription data. Tool ID remains the exact Owner export and is mapped in the implementation record. |
| `validate-and-select-session-configuration` | step 4 subscription validity; step 8 SMF session/UPF selection | `CA_ADAPTER`: local validation/selection; not a separate SBI service operation. |
| `ca-bind-udm-subscription-hold` | supports step 4 | `CA_EXTENSION`: Host/Owner correlation and hold preparation; no direct 3GPP operation. |
| `subscribe-sm-data` | step 4 — `Nudm_SDM_Subscribe` | `3GPP_NATIVE`: subscribe to Session Management Subscription updates. |
| `ca-bind-pcf-policy-hold` | supports step 7b | `CA_EXTENSION`: Host/Owner hold preparation. |
| `ca-read-pcf-create-inputs` | supports step 7b | `CA_ADAPTER`: read and validate governed PCF create inputs. |
| `ca-build-sm-policy-association-inputs` | step 7b | `CA_ADAPTER`: local construction of the PCF request payload. |
| `establish-sm-policy-association` | step 7b — `Npcf_SMPolicyControl_Create` | `3GPP_NATIVE`: establish the SM Policy Association. |
| `establish-n4-session` | steps 10a–10b; §4.4.1.2 N4 Session Establishment | `CA_ADAPTER`: UPN Owner completes N4 establishment; it is not a 3GPP SBI operation. |
| `ca-read-sm-operation-context` | supports step 11 | `CA_EXTENSION`: Host/SMF context preparation. |
| `ca-prepare-pdu-session-establishment-accept` | step 11 N1 SM container — PDU Session Establishment Accept | `CA_ADAPTER`: prepare the N1 SM payload. |
| `ca-build-n1n2-message` | step 11 N1 SM / N2 SM information | `CA_ADAPTER`: build the N1/N2 transfer payload. |
| `ca-bind-n1n2-transfer-hold` | supports step 11 | `CA_EXTENSION`: Host/Owner correlation and hold preparation. |
| `transfer-n1n2-message` | step 11 — `Namf_Communication_N1N2MessageTransfer` | `3GPP_NATIVE`: SMF transfers N1/N2 information to AMF. ACK does not prove RAN acceptance. |
| `complete-an-resource-setup` | steps 12–15; step 15 is `Nsmf_PDUSession_UpdateSMContext Request` | `CA_ADAPTER`: SSM wraps the asynchronous access-network completion. AMF/(R)AN/UE own steps 12–14; the SMF receives the result through step 15. |
| `modify-n4-session` | steps 16a–16b; §4.4.1.3 N4 Session Modification | `CA_ADAPTER`: UPN Owner completes forwarding modification. |
| `ca-transfer-resource-responsibility` | CA lifecycle handoff after successful network procedure | `CA_EXTENSION`: no direct 3GPP procedure counterpart. |
| `ca-transfer-failed-resource-responsibility` | CA lifecycle handoff after confirmed failure | `CA_EXTENSION`: no direct 3GPP procedure counterpart. |
| `verify-pdu-session-establishment` | final facts derived from steps 15–17 | `CA_EXTENSION`: final Goal proof over authoritative network facts and resource responsibility. |

**Open 3GPP boundary:** TS 23.502 step 5 `Nsmf_PDUSession_CreateSMContext Response` is an early response and is not final PDU Session establishment. The current graph still needs an explicit decision on whether this response is owned by the SMF entry/Host boundary or a dedicated Owner operation. Do not infer that step 5 is covered by a later PCF/N4 result.

Step 9 (SMF-initiated SM Policy Association Modification) is conditional and must be included only when the admitted profile requires it. Step 16c (UDM UECM Registration), step 18 (SM Context Status Notify) and step 21 (unsubscription) also require explicit applicability decisions; omission is not implicit PASS.

### Capability mapping

The following are illustrative IDs only; they are **not** published CapabilityContracts exports:

| Capability placeholder | Standard / CA scope |
|---|---|
| `urn:example:connectionagent:capability:3gpp:nudm-sdm-get:v1` | UDM `Nudm_SDM_Get` |
| `urn:example:connectionagent:capability:3gpp:nudm-sdm-subscribe:v1` | UDM `Nudm_SDM_Subscribe` |
| `urn:example:connectionagent:capability:3gpp:npcf-sm-policy-control-create:v1` | PCF `Npcf_SMPolicyControl_Create` |
| `urn:example:connectionagent:capability:3gpp:n4-session-establishment:v1` | UPF N4 Session Establishment |
| `urn:example:connectionagent:capability:3gpp:namf-communication-n1n2-transfer:v1` | AMF `Namf_Communication_N1N2MessageTransfer` |
| `urn:example:connectionagent:capability:3gpp:n4-session-modification:v1` | UPF N4 Session Modification |
| `urn:example:connectionagent:capability:ca:resource-responsibility:v1` | CA resource lifecycle handoff |

The exact IDs must be replaced only by matching trusted CapabilityContracts exports. Generic legacy grants such as `fivegc-session-mutation` are not sufficient evidence of narrow NF/service authorization.

## Runtime and evidence boundary

**No author-level wait/await/poll.** Asynchronous setup completion belongs to the corresponding Tool/Provider/SMF Operation, which may report SUCCEEDED only when its published Owner contract and authoritative Result/Evidence support the required completion. The Procedure's Postcondition verifies that evidence. The legacy callables do **not** yet make those v1alpha4 guarantees; do not treat an old HTTP or N1/N2 dispatch ACK as completed N4/RAN establishment. Host/Runtime retains Deadline, Cancellation and Correlation.

Every Mutation `OUTCOME_UNKNOWN` goes to an explicit safe stop. An Owner-published `mutation.reconcile` can be used **only through the Host common safety boundary**, not an authored `reconcile` Node. The only successful Invocation edge is `verify-pdu-session-establishment.postcondition.routes.PASS: SUCCEEDED`, where all listed predicates must pass with authoritative, fresh, same-lifecycle Evidence.

**Known blockers:** missing exact v1alpha4 Owner/Capability publications, checked output Schemas and Evidence descriptors, confirmed callable input identities, and Compiler/Studio/Host §45.2 execution evidence. Do **not** infer completion or production readiness from YAML syntax checks.
