---
name: establish-pdu-session-mas
description: CA-SL v1alpha4 illustrative SMF MAS policy-first initial PDU Session establishment source.
---

# Establish PDU Session — SMF MAS

**Source language:** CA-SL v1alpha4 (pinned normative specification `7f84393ee8c395e4d8c39a74cb5000a1f896588d`).

**Adoption state: NOT_QUALIFIED.** This is an authoring and editor example, **not** a linked, executable or approved 5GC Skill. Its `urn:example:` dependency identities and evidence guarantees are illustration-only; there is no trusted v1alpha4 ToolCatalog or CapabilityContracts publication in this repository. The Compiler **must fail closed** when those exports or their exact version/trust bindings are absent.

## Scope and business progression

One admitted, initial IPv4 / SSC1, local non-roaming PDU Session request. Never substitute an arbitrary UE, PSI, lifecycle, resource or late callback; identity and Scope require independent Host/Owner proof.

MAS is a **proposed, not Owner-approved policy-first** graph, with per-step Postcondition and confirmed-failure-only cleanup; on OUTCOME_UNKNOWN it stops and retains responsibility. See [migration decision register](../../MIGRATION-REVIEW-v1alpha4.md). The intended sequence is: validate subscription and required authentication disposition, establish context and UECM, create policy, choose UP anchor, allocate address, update policy with actual allocation, create charging and N4, signal RAN, activate forwarding, account for events and transfer durable ownership.

## 3GPP Traceability — SMF view and MAS deviations

**Pinned reference:** 3GPP TS 23.502 V18.12.0 (Release 18), §4.3.2.2.1; N4 procedures §4.4.1.2–§4.4.1.3.

This is a **proposed MAS policy-first implementation graph**, not a standard 3GPP procedure and not Owner-approved. A mapping below identifies the related 3GPP phase; it does not claim the custom MAS operation is a standard NF Service Operation.

| Procedure Node | 3GPP source / interaction | Classification and deviation |
|---|---|---|
| `admit-create-sm-context-request` | §4.3.2.2.1 step 3 — `Nsmf_PDUSession_CreateSMContext Request` | `CA_EXTENSION`: entry admission and lifecycle checks. |
| `validate-sm-subscription` | step 4 — Session Management Subscription retrieval/validation | `CA_ADAPTER`: MAS validation operation; not yet mapped to a published `Nudm_SDM_Get` Owner contract. |
| `resolve-secondary-authentication` | step 6 — optional secondary authentication/authorization | `CA_ADAPTER`: determines whether the admitted profile requires the optional flow. |
| `create-sm-context` | steps 3 and 5 — `Nsmf_PDUSession_CreateSMContext` Request/Response boundary | `CA_ADAPTER`: MAS context creation is not itself the standard Nsmf service operation. |
| `ca-register-uecm` | related to `Nudm_UECM_Registration`; standard flow places step 16c after N4 modification | `CA_ADAPTER` with an explicit ordering deviation: MAS registers earlier. This is not the TS 23.502 default sequence. |
| `establish-sm-policy-association` | step 7b — `Npcf_SMPolicyControl_Create` | `CA_ADAPTER`: MAS policy creation is not yet an approved PCF Owner export. |
| `select-upf-anchor` | step 8 — SMF UPF selection | `CA_ADAPTER`: custom MAS anchor-selection contract. |
| `allocate-pdu-session-address` | step 8 — SMF address allocation | `CA_ADAPTER`: custom MAS allocator. |
| `modify-sm-policy-association` | step 9 — SMF-initiated SM Policy Association Modification / `Npcf_SMPolicyControl_Update` | `CA_ADAPTER`: MAS updates policy with actual allocated address. |
| `ca-create-charging-reservation` | no distinct step in §4.3.2.2.1 | `CA_EXTENSION`: MAS charging reservation. |
| `establish-n4-session` | steps 10a–10b; §4.4.1.2 N4 Session Establishment | `CA_ADAPTER`: MAS user-plane establishment; Owner contract not published. |
| `ca-confirm-pdu-session-address` | related to step 8 allocation | `CA_EXTENSION`: MAS-specific address confirmation. |
| `complete-an-resource-setup` | steps 11–15; step 11 N1N2 transfer, step 15 Nsmf UpdateSMContext Request | `CA_ADAPTER`: wraps access-network completion; AMF/(R)AN/UE own steps 12–14. |
| `modify-n4-session` | steps 16a–16b; §4.4.1.3 N4 Session Modification | `CA_ADAPTER`: MAS forwarding activation. |
| `ca-emit-establishment-events` | potentially related to step 18 SM Context Status Notify, subject to exact mapping | `CA_EXTENSION`: no standard mapping is claimed without an Owner contract. |
| `ca-transfer-resource-responsibility` | no direct step in §4.3.2.2.1 | `CA_EXTENSION`: durable resource ownership. |
| `ca-compensate-confirmed-failure` | failure handling / potentially separate PDU Session Release procedure | `CA_EXTENSION`: not a 3GPP Release procedure unless the Owner contract explicitly implements that procedure. |
| `verify-pdu-session-establishment` | final facts across steps 15–17 | `CA_EXTENSION`: final Goal proof, not a separate 3GPP operation. |

**Open 3GPP boundaries:** TS 23.502 step 5 `Nsmf_PDUSession_CreateSMContext Response` is an early response, not final session establishment. Step 17 `Nsmf_PDUSession_UpdateSMContext Response` follows the access-network result and N4 modification. The MAS graph's custom context operation does not prove either standard response is emitted; the Host/Owner response boundary must be decided explicitly.

### Capability mapping

These are illustrative names, not published CapabilityContracts exports:

| Capability placeholder | Standard / CA scope |
|---|---|
| `urn:example:connectionagent:capability:3gpp:udm-session-management-data:v1` | UDM Session Management Subscription retrieval/registration |
| `urn:example:connectionagent:capability:3gpp:pcf-sm-policy-control:v1` | PCF SM Policy Association create/update |
| `urn:example:connectionagent:capability:3gpp:n4-session-management:v1` | UPF N4 establishment/modification |
| `urn:example:connectionagent:capability:3gpp:amf-communication-n1n2:v1` | AMF N1/N2 transfer |
| `urn:example:connectionagent:capability:ca:mas-session-lifecycle:v1` | MAS-specific context, charging, event and responsibility lifecycle |

The exact IDs must be replaced only by trusted CapabilityContracts exports. The MAS sequence and its non-standard ordering remain NOT_QUALIFIED.

## Runtime and evidence boundary

**No author-level wait/await/poll.** Asynchronous setup completion belongs to the corresponding Tool/Provider/SMF Operation, which may report SUCCEEDED only when its published Owner contract and authoritative Result/Evidence support the required completion. The Procedure's Postcondition verifies that evidence. The legacy callables do **not** yet make those v1alpha4 guarantees; do not treat an old HTTP or N1/N2 dispatch ACK as completed N4/RAN establishment. Host/Runtime retains Deadline, Cancellation and Correlation.

Every Mutation `OUTCOME_UNKNOWN` goes to an explicit safe stop. An Owner-published `mutation.reconcile` can be used **only through the Host common safety boundary**, not an authored `reconcile` Node. The only successful Invocation edge is `verify-pdu-session-establishment.postcondition.routes.PASS: SUCCEEDED`, where all listed predicates must pass with authoritative, fresh, same-lifecycle Evidence.

**Known blockers:** missing exact v1alpha4 Owner/Capability publications, checked output Schemas and Evidence descriptors, confirmed callable input identities, and Compiler/Studio/Host §45.2 execution evidence. Do **not** infer completion or production readiness from YAML syntax checks.
