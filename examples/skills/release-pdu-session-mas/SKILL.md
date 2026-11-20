---
name: release-pdu-session-mas
description: CA-SL v1alpha5 source-aligned OpenAMSM MAS PDU Session release Procedure.
---

# Release PDU Session — OpenAMSM MAS

**Source language:** CA-SL v1alpha5 (`connectionagent.io/v1alpha5`).

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package is a source-aligned authoring candidate. MAS ToolCatalog, typed Operation Schemas, CapabilityContracts and Evidence Guarantees are not published. Candidate identities must fail closed at link time.

## Scope

Release an already-existing PDU Session for a Host-classified UE-, PCF-, RAN-, SMF-, local- or AMF-originated release. The Host authenticates the source, maps it to the exact versioned Open5GS delete-trigger value, selects the exact Session generation and supplies the trigger plus the 3GPP `pduSessionId`. This Procedure does not create a new Session and does not absorb a late callback belonging to a different Run or generation.

## Source plan

Pinned OpenAMSM plan: `tools/nw-agent/plans/release/pdu-rel-v4.yaml`, workflow `wf-certified-pdu-rel-v4`, `sm-mas-ops/3.2`, `oes-dsl/1.3`.

| Step | OES Operation | Treatment |
|---|---|---|
| r1 | CA.DELETE_CHARGING (optional) | Omitted until an applicability rule is defined |
| r2 | UPN.DELETE_UP_SESSION | Required; passes the exact Host-classified trigger; outputs `released` |
| r3 | SSM.SIGNAL_UE_AN | Required; `release='1'` and the same trigger; may await correlated AMF release confirmation |
| r4 | PA.DELETE_SM_POLICY | Required; `release='1'`; no OES output declared |
| r5 | SC.RELEASE_SM_CONTEXT | Required; `release='1'`; output lifecycle is `RELEASING` after commit phases |
| r6 | SE.EMIT_EVENTS | Required local event with `ev='RELEASED'`; no OES output declared |
| r7 | SC.COMPENSATE_RELEASE | Source says `execute: skip`; not an authored Node |

The OES plan's `compensate_then_replan_once` is not imported into CA-SL. Mutation UNKNOWN remains unresolved until the exact original Owner invocation is reconciled; it MUST NOT dispatch a new release mutation.

## Execution and trigger rules

Each Owner callable receives `ue_identity: context.supi` and `psi: context.request.pduSessionId` as scope-only arguments. The Owner validates the pair against the Host-bound Session generation and does not forward these identity fields as OES business inputs. The Host MUST reject a pduSessionId that does not identify the selected existing Session.


The Request Schema uses the seven numeric `OGS_PFCP_DELETE_TRIGGER` values from the pinned OpenAMSM/Open5GS header. The Host, not the caller, determines the value from authenticated ingress. In particular, `AMF_RELEASE_SM_CONTEXT` and `AMF_UPDATE_SM_CONTEXT` are distinct values and MUST NOT be collapsed into one generic AMF trigger.

The SSM Operation is not equivalent to “send a transfer and return.” For release signaling, the Owner keeps the exact operation pending until the applicable AMF release confirmation; a transfer acknowledgement alone does not close the Operation. For AMF-originated release/update and local initiation, the source implementation intentionally skips N1/N2 signaling and the original Host/SMF transaction response is handled at the service boundary.

## Owner ingress boundary

The current OpenAMSM `agent_step` path rejects ordinary business Release ingress. The existence of ReleaseSMContext handling and MAS facade operations does not make this Skill callable through that path. Execution requires the separately reviewed Host / CA Client Tools / OpenAMSM Owner-private lifecycle binding. Do not weaken or bypass the external Nsmf admission gate to make this Procedure appear runnable.

## Qualification blockers

1. Publish exact Owner callable identities, Effects, Schemas, outcomes and Evidence Guarantees.
2. Repair the source OES plan's missing `start_inputs.trigger` declaration before claiming the OES plan is executable.
3. Prove release ordering and Owner receipts across UPF, AN signaling, PCF association and SM Context lifecycle.
4. Prove trigger mapping against the exact vendored Open5GS header.
5. Prove resource tombstone, duplicate, wrong-generation, late-callback and mixed-UE safety.

See [source mapping](references/openamsm-operation-mapping.md). This package is not linked, executable or qualified.
