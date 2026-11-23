# OpenAMSM MAS Modify / Release source mapping

**Status: SCHEME C / SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.**
This document records the current merged-OpenAMSM **Scheme C** occurrences used by
the two v1alpha5 Procedures. It is not a published Owner ToolCatalog, trusted
DependencySnapshot, mutation receipt, Host acceptance or Runtime result. Owner
publication is still absent, and no live 5GC E2E result is claimed for the CA-SL
layer.

## Pinned source baseline

- Repository: odango-chan/env-openamsm
- Source commit: 594dec78b95bff4fdc34deac8a3a9681fb41228f
- Historical Modify plan: upstream/openamsm/tools/nw-agent/plans/modify/pdu-mod-v3.yaml
  - Blob SHA: 8a2caf343c29bb64cbb09b29994c79ac8ad5da05
- Historical Release plan: upstream/openamsm/tools/nw-agent/plans/release/pdu-rel-v4.yaml
  - Blob SHA: 849c3206569d452a663d1b8d42a63ffdc367be31

Relevant implementation blobs at the 594dec78 source pin:

| Source file | Blob SHA | What it grounds |
| --- | --- | --- |
| src/smf/mas/common/mas-facade.c | c4f71e8c5209a1288a56f5f588fe44ae4fa14cba | MAS operation dispatch and release branch selection |
| src/smf/mas/sc/session_context.c | c7763919785870f4350b8779b59563dc64533a5e | SC lifecycle transitions and release phases |
| src/smf/mas/ca/charge_adapter.c | f9fb7772d316a8e2848acf18af009aa6641c1406 | Charging update/delete are local skip markers |
| src/smf/mas/upn/upnode.c | 0993e8ed35c691dc7dc76a682b5f1b4d23fa38cc | UPN QoS-delta and user-plane delete branches |
| src/smf/mas/ssm/ssm_ue.c | e59acacea03532a102d699edbbd7a0a07662f8f9 | N1 parse/build/confirm branches and pending N1/N2 completion |
| src/smf/mas/pa/policy_adapter.c | 110924c66cfe3455407c3ad4cdffb3e3292338b1 | PCF association delete |
| src/smf/mas/se/session_exposure.c | bafdc069522eb1e2c8f0a3c08eed28745abbcd48 | Local in-memory event marker only |
| lib/pfcp/xact.h | bbdb879d217fe7ec360a661ac22a5b08865e115c | Numeric PFCP delete trigger constants |

The existing Establishment mapping in this repository pins commit
77c0a2f8511c3498d1270f059881b3cf0f7f5eeb. The Modify and Release plan blobs are
byte-identical at that pin and at 594dec78b95bff4fdc34deac8a3a9681fb41228f, so
the historical plan pins remain a common provenance reference.

## Historical OES plan shape (superseded, not implemented)

The pinned `pdu-mod-v3.yaml` / `pdu-rel-v4.yaml` plans are retained only as source
provenance. Their declared step sequence is superseded by the merged Owner
Scheme C transaction and is **not** the sequence these Procedures implement.
The OES plan placed release signalling between the user-plane deletion and the
policy deletion; Scheme C sends the N1/N2 release command first, waits for both
confirmations, and only then runs the cleanup. Do not cite the pinned plan as an
execution order.

| Historical OES step | Historical operation | Scheme C replacement |
| --- | --- | --- |
| m0 | SC.UPDATE_SM_CONTEXT | no prepare occurrence in Scheme C |
| m3 | UPN.MODIFY_UP_SESSION (intent) | merged into `apply-qos-delta` |
| m4 | SSM.SIGNAL_UE_AN (modify) | `parse-n1` + `apply-qos-delta` |
| m5 | UPN.MODIFY_UP_SESSION (QoS delta) | `apply-qos-delta` |
| r2 | UPN.DELETE_UP_SESSION | `delete-user-plane` |
| r3 | SSM.SIGNAL_UE_AN (release) | `build-command` + `confirm-n1` + `confirm-n2` |
| r4 | PA.DELETE_SM_POLICY | `delete-policy` |
| r5 | SC.RELEASE_SM_CONTEXT | `release-sm-context` |
| r6 | SE.EMIT_EVENTS | `emit-release-event` |

The historical plan's empty `start_inputs` no longer blocks this Skill: the
Scheme C Release Request carries the numeric `trigger` as a public field and the
Build occurrence consumes it.

## Current Scheme C occurrences

### Modify

| CA-SL node | Owner callable | Effect | Inputs | Declared Owner outputs |
| --- | --- | --- | --- | --- |
| `validate-modify-request` | none (Predicate) | - | `supi`, `pduSessionId`, `entryKind` | - |
| `parse-n1` | `SSM.PARSE_N1_MODIFY` | READ | `ue_identity`, `psi`, `parse_n1=1`; exact retained raw N1 from trusted private context | `qfi`, `five_qi`, `gfbr_ul`, `gfbr_dl`, `mfbr_ul`, `mfbr_dl`, `requested_kind` |
| `apply-qos-delta` | `UPN.MODIFY_QOS_DELTA` | MUTATION | `ue_identity`, `psi`, `qos_flows_delta=1`, plus the parsed target | `qos_delta_state`, `n1n2_dispatched` (APPLIED only), applied target |
| `verify-modify-completion` | none (Postcondition) | - | `parse-n1` output, `apply-qos-delta` output | - |

### Release

| CA-SL node | Owner callable | Effect | Inputs | Declared Owner outputs |
| --- | --- | --- | --- | --- |
| `validate-release-request` | none (Predicate) | - | `supi`, `pduSessionId`, `entryKind` | - |
| `parse-n1` | `SSM.PARSE_N1_RELEASE` | READ | `ue_identity`, `psi`, `parse_n1=1`; exact retained raw N1 | `release_intent`, `psi`, `pti`, optional `cause` |
| `build-command` | `SSM.BUILD_RELEASE_COMMAND` | MUTATION | `ue_identity`, `psi`, `release=1`, `mode=build`, `trigger`, parsed `pti` | `release_phase`, `n1_sm_hex`, `n2_sm_hex`, `n2_sm_info_type`, `release_txn`, `release_generation` |
| `confirm-n1` | `SSM.RELEASE_CONFIRM_N1` | MUTATION | `ue_identity`, `psi`, `release_confirm=n1`, `release_txn`, `release_generation` | `n1_released` |
| `confirm-n2` | `SSM.RELEASE_CONFIRM_N2` | MUTATION | `ue_identity`, `psi`, `release_confirm=n2`, `release_txn`, `release_generation` | `n2_released`, `release_ready` |
| `delete-policy` | `PA.DELETE_SM_POLICY_C` | MUTATION | `ue_identity`, `psi`, `release=1`, `trigger` | `terminated` |
| `delete-user-plane` | `UPN.DELETE_UP_SESSION` | MUTATION | `ue_identity`, `psi`, `trigger` | `released` |
| `emit-release-event` | `SE.EMIT_RELEASE_EVENT_C` | MUTATION | `ue_identity`, `psi`, `ev=RELEASED` | `last_event` |
| `release-sm-context` | `SC.RELEASE_SM_CONTEXT_C` | MUTATION | `ue_identity`, `psi`, `release=1`, `finalize=1`, `trigger` | `lifecycle` |
| `verify-release-completion` | none (Postcondition) | - | every preceding Owner output | - |

## Public request boundary

Both request Schemas are closed (`additionalProperties: false`) and carry only
public fields:

- Modify: required `[pduSessionId, entryKind]`; `entryKind` is one of
  `UE_INITIATED`, `AMF_INITIATED`, `NETWORK_TRIGGERED`.
- Release: required `[pduSessionId, entryKind, trigger]`; `entryKind` is only
  `UE_INITIATED`, and `trigger` is the numeric Owner trigger enum 1..7.

The raw N1 and the Host-private release transaction id are not Skill-authored
request fields. The parsed QoS delta (`qosFlowsDelta`) is not a request field
either; it is Provider-injected from the read-only parse result. Private
`sessionRef`, `smContextRef`, `generation`, `stepId`, `invocationId`,
`idempotencyKey` and `streamId` never appear in a request Schema.

## Read-only parse and the single PTI binding

Both `parse-n1` occurrences are READ. The parse is read-only and must not mutate session state; it only decodes the exact retained N1. In particular, the release
parse must not bind the PTI to the session. The Build occurrence is the only PTI
binding: it is the transaction-controlled binding that records
`release_txn` / `release_generation`, and both confirmations are bound to that
same original Run.

## Optional steps and non-claims

- Modify `CA.UPDATE_CHARGING` is optional and has no source-defined applicability
  predicate, so it is omitted. Its adapter only writes a local charging marker
  and records `NOT_IMPL_skip`; it does not create a CHF charging reservation.
- Release `CA.DELETE_CHARGING` is optional and has no applicability predicate, so
  it is omitted. It only clears a local marker and records `NOT_IMPL_skip`; it
  does not delete a CHF charging resource.
- Release `COMPENSATE_RELEASE` is `execute: skip`. It is not a Procedure node.
  No compensation, retry or replan strategy is imported.
- `last_event` is a local in-memory marker; it is not a durable event, a 3GPP SM
  Context Status Notify or evidence of external delivery.
- `lifecycle=RELEASING` is not `RELEASED`; the Host owns any later ResourceMap
  tombstone and it is outside the Skill.

## Qualification boundary

The current OpenAMSM agent_step admission path rejects standard Nsmf business
Update / Release admission. A private Host / Owner binding and a published Owner
contract are required; the Skill does not bypass that gate.

The existing ca-client-tools MAS v0.2.0 candidate is not a trusted published
ToolCatalog. The Scheme C callable IDs, input/output Schemas, Outcomes, commit
receipts and Evidence Guarantees are proposed Owner exports only. Until the
Owner publishes them, both Skills remain NOT_LINKABLE / NOT_QUALIFIED and no
live 5GC E2E PASS may be claimed for CA-SL.

The [Owner outcome contract](mas-lifecycle-owner-contract.md) defines the required
receipt, Scope, pending-operation and failure semantics. The [acceptance
matrix](mas-lifecycle-acceptance-matrix.md) separates static source checks from
runtime scenarios that have not been run.
