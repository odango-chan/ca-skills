---
name: modify-pdu-session-mas
description: Source-aligned CA-SL v1alpha5 Modify Procedure for the OpenAMSM MAS pdu-mod-v3 profile.
---

# Modify PDU Session — OpenAMSM MAS profile

**Source language:** [CA-SL v1alpha5](https://github.com/odango-chan/ca-skills/blob/main/docs/skill-language-spec.v1alpha5.zh-CN.md).

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package is a source-aligned Procedure draft. The required MAS ToolCatalog exports, v0.3.0 Schemas, mutation receipts, Evidence Guarantees, Owner identity and deployment CapabilityContracts are not published. Compiler linking must fail closed.

## Scope

This Skill models modification of an already admitted PDU Session. It is separate from initial establishment and release. The Host must authenticate and classify the ingress, bind the exact SUPI / PSI / current session generation, and then invoke this Procedure with the normalized request envelope.

The Skill does not create an SM Context, re-query AMF registration, consume raw NAS / NGAP bytes, or expose Host / Owner correlation handles. The original binary payload and private session references remain inside the responsible Host / Owner adapters.

## Entry variants

The Host explicitly normalizes these entry variants into `request.entryKind`:

- `UE_INITIATED` — UE / RAN initiated modification delivered through authenticated `Nsmf_PDUSession_UpdateSMContext`.
- `AMF_INITIATED` — an AMF initiated `Nsmf_PDUSession_UpdateSMContext` business action.
- `NETWORK_TRIGGERED` — a trusted internal Owner event, such as a PCF-triggered or local policy event.

All three variants converge on the same pinned `pdu-mod-v3.yaml` sequence. The source plan does not define separate step graphs for these variants. This classification is Host-owned; it is not new CA-SL syntax.

**Important:** an N2 Setup Response that completes the existing Establishment `s10 OWNER_DEFERRED` occurrence belongs to that same Establishment Run. It must resume the original Operation and must not start this Modify Skill or a new Run.

## Source progression

The Procedure preserves the pinned OpenAMSM step identities:

1. `m0` — `SC.UPDATE_SM_CONTEXT`; updates the existing SM Context lifecycle.
2. `m2` — `CA.UPDATE_CHARGING`; the current adapter only records its local charging marker (`charging_ref="1"`, `NOT_IMPL_skip`). It does not create a CHF charging reservation.
3. `m3` — `UPN.MODIFY_UP_SESSION` with `up_intent="1"`; returns the current N4 SEID.
4. `m4` — `SSM.SIGNAL_UE_AN`; returns the AN tunnel information associated with this exact Modify occurrence.
5. `m5` — the same `UPN.MODIFY_UP_SESSION` callable with the m3 N4 SEID and m4 AN tunnel; confirms N3 synchronization.

The two UPN calls are distinct Mutation occurrences (`m3` and `m5`), not a generic reusable Tool call. The SSM call is bound to occurrence `m4`, not to Establishment `s10` or Release `r3`.

The OES plan marks m2 optional. CA-SL has no optional Operation stage; this fixed source profile includes the current marker-only adapter call and verifies only its local marker. It does not elevate charging to a 3GPP Modify requirement. A future real CHF implementation requires a separately published Owner contract and a reviewed Procedure revision.

## Host / Owner boundary

The current OpenAMSM `agent_step` admission path rejects the standard Nsmf business Update route. The missing Owner-private binding and publication are explicit blockers; this Skill does not relax that protocol admission gate or invent a new public SBI route.

All MAS Operations are candidate MUTATIONs, including the local CA marker. The Owner must provide exact occurrence identity, durable commit receipts, Scope / generation binding and Evidence. HTTP acceptance, a local marker, or a reused session value is not proof of the current invocation.

See [source mapping](../../../docs/mas-lifecycle-source-mapping.md), [Owner outcome contract](../../../docs/mas-lifecycle-owner-contract.md) and [acceptance matrix](../../../docs/mas-lifecycle-acceptance-matrix.md).

## Goal boundary

A successful Invocation proves the source-declared Modify results for the same SUPI / PSI / generation: SM Context remains operational, the m3 intent result is available, the m4 AN tunnel is current, and m5 confirms N3 synchronization. The charging marker is checked only as a local source-step disposition.

This is not a live 5GC qualification result. It does not claim a CHF reservation, user-plane traffic success, a Host ResourceMap transition, or completion of any unrelated Establishment callback.
