---
name: release-pdu-session-mas
description: Source-aligned CA-SL v1alpha5 Release Procedure for the OpenAMSM MAS pdu-rel-v4 profile.
---

# Release PDU Session — OpenAMSM MAS profile

**Source language:** [CA-SL v1alpha5](https://github.com/odango-chan/ca-skills/blob/main/docs/skill-language-spec.v1alpha5.zh-CN.md).

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package is a source-aligned Procedure draft. The required MAS ToolCatalog exports, v0.3.0 Schemas, mutation receipts, Evidence Guarantees, Owner identity and deployment CapabilityContracts are not published. Compiler linking must fail closed.

## Scope

This Skill models release of an existing PDU Session. It does not create a session and does not replace Establishment. The Host authenticates and classifies the ingress, binds the exact SUPI / PSI / current generation, and invokes this Procedure with a normalized request.

The Skill does not expose raw NAS / NGAP bytes, Host ResourceMap keys, Owner session references, invocation IDs, generation IDs or transport correlation handles.

## Entry variants

The Host normalizes the authenticated ingress into `request.entryKind` and `request.trigger`:

- `UE_INITIATED` — UE-requested release received through Nsmf UpdateSMContext.
- `AMF_INITIATED` — AMF-requested release through Nsmf ReleaseSMContext or an UpdateSMContext release action.
- `NETWORK_TRIGGERED` — trusted internal PCF / SMF Owner event.

The source trigger enum is represented to the Skill as a symbolic Host-normalized value. The private Owner adapter must map it to the exact pinned OpenAMSM trigger constant before constructing the OES input. The symbolic value must never be passed directly to a C `atoi`-based trigger field.

This classification is Host-owned, not new CA-SL syntax. The Procedure is not a public SBI endpoint and does not relax OpenAMSM's current `agent_step` admission behavior.

## Source progression

The Procedure follows OES steps r1–r6 from `pdu-rel-v4.yaml`:

1. `r1` — `CA.DELETE_CHARGING`; the pinned adapter clears a local marker (`charging_ref="0"`, `NOT_IMPL_skip`). It does not delete a CHF charging resource.
2. `r2` — `UPN.DELETE_UP_SESSION`; deletes the UP session and requires the exact PFCP deletion completion.
3. `r3` — `SSM.SIGNAL_UE_AN` with `release="1"` and the normalized trigger. For AMF Update / Release and local-initiation paths, no N1/N2 release signal is needed; other supported triggers send N1/N2 and remain pending until the AMF release confirmation is correlated.
4. `r4` — `PA.DELETE_SM_POLICY`; deletes the PCF association when present. A no-association result must be evidenced as `NOT_PRESENT`, not confused with an unverified success.
5. `r5` — `SC.RELEASE_SM_CONTEXT`; completes the source's UDM unsubscribe / UECM deregistration / AMF acknowledgement sequence. The plan exposes `lifecycle="RELEASING"`, not `RELEASED`.
6. `r6` — `SE.EMIT_EVENTS` with `ev="RELEASED"`; this is a local MAS event record only.

The OES plan marks r1 optional. As with Modify m2, this fixed profile includes the current marker-only call because the pinned adapter returns a local disposition. CA-SL has no optional Operation stage. No CHF release is claimed.

OES r7 `COMPENSATE_RELEASE` is an explicit skip and is not imported. The OES `compensate_then_replan_once` policy is not imported: an unknown Mutation result must never trigger a blind retry or a new Release sequence.

## Host / Owner boundary

The current OpenAMSM `agent_step` admission path rejects the standard Nsmf business Release route. The missing Owner-private binding and publication are explicit blockers; this Skill does not relax the protocol admission gate or invent a public SBI route.

Every MAS callable is a candidate MUTATION. The Owner must persist the exact pending occurrence and return final completion only after the relevant PFCP, AMF, PCF and UDM / UECM work has settled. An HTTP 2xx, an accepted request, or an in-memory pending handle is not completion evidence. Late callbacks must remain attached to the original Owner occurrence and generation; they must never resume a newer Run.

The Host owns external URI ResourceMap tombstoning after the exact Release lifecycle has settled. That Host-owned action is outside this Procedure and is not inferred from `lifecycle="RELEASING"`.

See [source mapping](../../../docs/mas-lifecycle-source-mapping.md), [Owner outcome contract](../../../docs/mas-lifecycle-owner-contract.md) and [acceptance matrix](../../../docs/mas-lifecycle-acceptance-matrix.md).

## Goal boundary

A successful Invocation proves the source-declared Release results for the same SUPI / PSI / generation, including UP-session deletion, settled UE/AN signaling disposition, policy-association release disposition, SM Context release progression and local release-event recording.

It does not claim a real CHF deletion, a 3GPP SM Context Status Notify from r6, a Host ResourceMap tombstone, or product / live 5GC qualification.
