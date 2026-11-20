---
name: modify-pdu-session-mas
description: CA-SL v1alpha5 source-aligned OpenAMSM MAS PDU Session modification Procedure.
---

# Modify PDU Session — OpenAMSM MAS

**Source language:** CA-SL v1alpha5 (`connectionagent.io/v1alpha5`).

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package is an authored, source-aligned Procedure candidate. MAS ToolCatalog, typed Operation Schemas, CapabilityContracts and Evidence Guarantees are not published. Every `mas::` identity below remains a candidate reference; linking MUST fail closed until the exact Owner exports exist.

## Scope

Modify an already-existing PDU Session. This Skill does not create a Session, replace the establishment Procedure, or implement a general SMF state machine.

The Host classifies authenticated ingress before Invocation creation and selects this Procedure only for a new business modification. It distinguishes UE-initiated, AMF/RAN-initiated and trusted network-triggered events, and correlates all work to the exact existing Session generation. A later N2 response that completes an already-pending establishment or modification Operation MUST resume that original Owner occurrence; it MUST NOT start this Skill.

## Source plan

Pinned OpenAMSM source: `tools/nw-agent/plans/modify/pdu-mod-v3.yaml`, workflow `wf-certified-pdu-mod-v3`, MAS capability `sm-mas-ops/3.2`, OES DSL `1.3`.

| Step | OES Operation | Treatment |
|---|---|---|
| m0 | SC.UPDATE_SM_CONTEXT | Included as a new Owner callable; source declares output `lifecycle`, no step inputs |
| m2 | CA.UPDATE_CHARGING (optional) | Not in the base Procedure: source marks it optional but supplies no applicability predicate. Do not call it unconditionally or invent a trigger rule |
| m3 | UPN.MODIFY_UP_SESSION | First distinct occurrence; source input `up_intent='1'`, output `n4_seid` |
| m4 | SSM.SIGNAL_UE_AN | Reuses the existing SSM operation with the modification occurrence's correlation; outputs AN tunnel data |
| m5 | UPN.MODIFY_UP_SESSION | Second distinct occurrence; consumes m3 `n4_seid` and m4 AN tunnel data; output `n3_synced` |

The two UPN calls are separate mutation occurrences. They MUST have independent invocation/effect/receipt identities and MUST NOT share or overwrite a generic “modify” receipt. The callable identity may be reused only if the Owner contract defines occurrence-scoped idempotency and evidence.

## Lifecycle and safety

- Host binds SUPI, PSI, Host resource identity and generation; these are not caller-selected MAS arguments.
- m0 updates the existing SM Context. m3 applies the source-defined N4 modification; m4 obtains the access-network result; m5 applies the distinct follow-up N4 modification.
- m4's AMF transfer acceptance is not proof of AN adoption. The final predicate requires source-defined tunnel data and m5's N3 synchronization result.
- `m2 UPDATE_CHARGING` remains an explicit optional source step, not silently treated as executed.
- No automatic retry, compensate-then-replan, or new Session creation is authored. Mutation `OUTCOME_UNKNOWN` remains unresolved pending exact-original Owner reconciliation.
- Request entry variants are classification metadata. Their actual Nsmf/Namf wire fields and callbacks belong to the Host/Integration contracts, not to invented Skill syntax.

## Qualification blockers

1. Publish exact Owner callable identities, Effects, input/output Schemas and Outcome/Evidence contracts for m0, m3, m4 and m5.
2. Prove the two m3/m5 mutation occurrences have independent occurrence identities and exact-original reconciliation.
3. Publish the applicability rule and typed contract for optional m2 before adding it to an executable branch.
4. Publish the trusted Host Context Schema and ingress-classification contract.
5. Execute successful, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE cases.

See [source mapping](references/openamsm-operation-mapping.md). This package is not linked, executable, or qualified.
