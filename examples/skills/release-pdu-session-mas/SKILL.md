---
name: release-pdu-session-mas
description: CA-SL v1alpha5 source-aligned OpenAMSM MAS PDU Session release Procedure.
---

# Release PDU Session — OpenAMSM MAS

**Source language:** CA-SL v1alpha5 (`connectionagent.io/v1alpha5`).

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package is a source-aligned authoring candidate. MAS ToolCatalog, typed Operation Schemas, CapabilityContracts and Evidence Guarantees are not published. Candidate identities must fail closed at link time.

## Scope

Release an already-existing PDU Session for a Host-classified UE-requested, AMF-requested or trusted network-triggered release. The Host authenticates the source, selects the exact Session generation and supplies the classified trigger. This Procedure does not create a new Session and does not absorb a late callback belonging to a different Run or generation.

## Source plan

Pinned OpenAMSM plan: `tools/nw-agent/plans/release/pdu-rel-v4.yaml`, workflow `wf-certified-pdu-rel-v4`, `sm-mas-ops/3.2`, `oes-dsl/1.3`.

| Step | OES Operation | Treatment |
|---|---|---|
| r1 | CA.DELETE_CHARGING (optional) | Omitted from the base graph until applicability is defined; no claim of CHF release |
| r2 | UPN.DELETE_UP_SESSION | Required; receives the classified `trigger`; outputs `released` |
| r3 | SSM.SIGNAL_UE_AN | Required; `release='1'` and exact `trigger`; no OES output fields |
| r4 | PA.DELETE_SM_POLICY | Required; `release='1'` |
| r5 | SC.RELEASE_SM_CONTEXT | Required; `release='1'`; outputs `lifecycle` |
| r6 | SE.EMIT_EVENTS | Required async-capable local event with `ev='RELEASED'`; no output fields |
| r7 | SC.COMPENSATE_RELEASE | Source says `execute: skip`; not an authored Node and not an automatic retry |

The OES plan's `compensate_then_replan_once` is not imported into CA-SL. Mutation UNKNOWN requires exact-original authorized Owner reconciliation; it MUST NOT dispatch a new release mutation.

## Qualification blockers

1. Publish exact Owner callable identities, Effects, Schemas, outcomes and Evidence Guarantees.
2. Prove release ordering and Owner receipts across UPF, AN signaling, PCF association and SM Context lifecycle.
3. Define r3's callback/continuation behavior and the required protocol response obligations for each trigger variant.
4. Define r1 applicability before including the optional charging deletion.
5. Prove resource tombstone, duplicate, wrong-generation, late-callback and mixed-UE safety.

See [source mapping](references/openamsm-operation-mapping.md). This package is not linked, executable or qualified.
