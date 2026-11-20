---
name: modify-pdu-session-mas
description: CA-SL v1alpha5 source-aligned OpenAMSM MAS PDU Session modification Procedure.
---

# Modify PDU Session — OpenAMSM MAS

**Source language:** CA-SL v1alpha5 (`connectionagent.io/v1alpha5`).

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package is an authored, source-aligned Procedure candidate. MAS ToolCatalog, typed Operation Schemas, CapabilityContracts and Evidence Guarantees are not published. Every `mas::` identity below remains a candidate reference; linking MUST fail closed until the exact Owner exports exist.

## Scope

Modify an already-existing PDU Session. This Skill does not create a Session, replace the establishment Procedure, or implement a general SMF state machine.

The Host classifies authenticated ingress before Invocation creation and selects this Procedure only for a new business modification. Host classifies three business entry families: UE-requested modification (F03), a new AMF/RAN-requested modification (F04), and a trusted network/PCF/AF-triggered modification (F05). The Host correlates every new Run to the exact existing Session generation. An AMF/RAN N2 response that completes an already-pending establishment or modification Operation is a continuation, not a new business entry: it MUST resume that original Owner occurrence and MUST NOT start this Skill. The F04 new-business variant remains a Host/Owner qualification item because the pinned OES plan does not encode an explicit ingress discriminator.

## Source plan

Pinned OpenAMSM plan: `tools/nw-agent/plans/modify/pdu-mod-v3.yaml`, workflow `wf-certified-pdu-mod-v3`, MAS capability `sm-mas-ops/3.2`, OES DSL `1.3`.

| Step | OES Operation | Treatment |
|---|---|---|
| m0 | SC.UPDATE_SM_CONTEXT | Included; empty input map; output lifecycle returns to OPERATIONAL |
| m2 | CA.UPDATE_CHARGING (optional) | Not in the base Procedure: source marks it optional but supplies no applicability predicate |
| m3 | UPN.MODIFY_UP_SESSION | First distinct occurrence; source input `up_intent='1'`, output `n4_seid` |
| m4 | SSM.SIGNAL_UE_AN | Empty input map; pending Owner operation returns the access-network tunnel tuple |
| m5 | UPN.MODIFY_UP_SESSION | Second distinct occurrence; consumes m3 `n4_seid` and m4 AN tunnel data; output `n3_synced` |

The two UPN calls are separate mutation occurrences. They MUST have independent invocation/effect/receipt identities and MUST NOT share or overwrite a generic “modify” receipt. The callable identity may be reused only if the Owner contract defines occurrence-scoped idempotency and evidence.

## Lifecycle and safety

- Each Owner callable receives `ue_identity: context.supi` and `psi: context.request.pduSessionId` as scope-only arguments. The Owner validates them against the Host-bound Session generation and does not forward them as OES business inputs. The Host must reject a pduSessionId that does not identify the selected existing Session.
- m0 performs the source-defined SM Context update and returns lifecycle to `OPERATIONAL`.
- m3 applies the source-defined UP intent and returns the existing N4 SEID; m4 obtains the access-network tunnel tuple; m5 applies the distinct follow-up N4 modification.
- m4's AMF transfer acceptance is not proof of AN adoption. The final Predicate requires the tunnel tuple and m5's N3 synchronization result.
- `m2 UPDATE_CHARGING` remains an explicit optional source step, not silently treated as executed.
- No automatic retry, compensate-then-replan, or new Session creation is authored. Mutation `OUTCOME_UNKNOWN` remains unresolved pending exact-original Owner reconciliation.

## Owner ingress boundary

The current OpenAMSM `agent_step` path rejects ordinary business Update ingress. The existence of the standard Nsmf Update handler and MAS facade operations does not make this Skill callable through that path. Execution requires the separately reviewed Host / CA Client Tools / OpenAMSM Owner-private lifecycle binding. Do not weaken or bypass the external Nsmf admission gate to make this Procedure appear runnable.

## Qualification blockers

1. Publish exact Owner callable identities, Effects, input/output Schemas and Outcome/Evidence contracts for m0, m3, m4 and m5.
2. Prove the two m3/m5 mutation occurrences have independent occurrence identities and exact-original reconciliation.
3. Publish the applicability rule and typed contract for optional m2 before adding it to an executable branch.
4. Publish the trusted Host Context Schema and ingress-classification contract.
5. Execute successful, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE cases.

See [source mapping](references/openamsm-operation-mapping.md). This package is not linked, executable, or qualified.
