---
name: modify-pdu-session-mas
description: Source-aligned CA-SL v1alpha5 Modify Procedure for the OpenAMSM MAS pdu-mod-v3 profile.
---

# Modify PDU Session — OpenAMSM MAS profile

**Source language:** CA-SL v1alpha5.

**Adoption state: NOT_QUALIFIED / NOT_LINKABLE.** This package defines a source-aligned Procedure. The required MAS ToolCatalog exports, new v0.3.0 candidate Schemas, mutation receipts, Evidence Guarantees, Owner identity and deployment CapabilityContracts are not published. Compiler linking must fail closed.

## Scope

This Skill models modification of an already admitted PDU Session. It is separate from initial establishment and release. The Host authenticates and classifies the ingress, binds the exact SUPI / PSI / current session generation, and invokes this Procedure with a normalized request envelope.

The Skill does not create an SM Context, re-query AMF registration, consume raw NAS / NGAP bytes, or expose Host / Owner correlation handles. The original binary payload and private session references remain inside the responsible Host / Owner adapters.

## Entry variants

The Host constructs request.entryKind after authenticating and classifying the business event:

- UE_INITIATED — a new UE-originated modification delivered through Nsmf UpdateSMContext.
- AMF_INITIATED — a new AMF-originated UpdateSMContext business action.
- NETWORK_TRIGGERED — a trusted internal Owner event, such as a PCF / AF policy trigger or a local network decision.

These variants converge on the same pinned pdu-mod-v3 sequence. This classification belongs to the Host; it is not new CA-SL syntax. A response that completes an already pending Operation is not a new entry variant.

**Important:** an N2 Setup Response that completes the existing Establishment s10 OWNER_DEFERRED occurrence must resume that same Establishment Operation in the original Run. It must not start this Modify Skill or create a new Run. The same rule applies to a late response for a pending Modify m4 occurrence: it belongs to m4's original Owner invocation and generation.

## Source progression

The Procedure includes only mandatory OES steps:

1. m0 — SC.UPDATE_SM_CONTEXT; updates the existing SM Context lifecycle. Its declared OES output is lifecycle.
2. m3 — UPN.MODIFY_UP_SESSION with up_intent=1 and no AN tunnel; prepares the UPN state and returns n4_seid.
3. m4 — SSM.SIGNAL_UE_AN; this Modify occurrence obtains the AN tunnel tuple. The Owner must keep it pending until the matching AN result is known.
4. m5 — UPN.MODIFY_UP_SESSION with the m3 N4 SEID and m4 AN tunnel; performs the PFCP modification and returns n3_synced.

m3 and m5 call the same underlying OES operation but are different Mutation occurrences with different input and output shapes. m3 therefore uses a distinct typed CA callable profile; m5 reuses the existing s11 candidate callable and its exact v0.2.0 input/output Schemas. m4 also uses a distinct callable profile: the Establishment s10 input Schema is not valid for the Modify occurrence.

The source plan marks m2 CA.UPDATE_CHARGING optional and supplies no applicability predicate. It is deliberately omitted; the Procedure does not call it unconditionally. The pinned CA adapter is a NOT_IMPL_skip marker, not a CHF charging reservation. No charging capability is granted by this Skill.

## Host / Owner boundary

The current OpenAMSM agent_step admission path rejects the standard Nsmf business Update route. The missing Owner-private binding and publication are explicit blockers. This Skill does not relax that protocol gate or invent a new public SBI route.

Every callable occurrence is a candidate MUTATION. The Owner must provide exact occurrence identity, durable commit receipts, SUPI / PSI / generation Scope binding and Evidence. A raw HTTP response, a source marker, or a reused session value is not proof of the current invocation.

See the [pinned operation mapping](references/openamsm-operation-mapping.md), the shared [source mapping](../../../docs/mas-lifecycle-source-mapping.md), the [Owner outcome contract](../../../docs/mas-lifecycle-owner-contract.md) and the [acceptance matrix](../../../docs/mas-lifecycle-acceptance-matrix.md).

## Goal boundary

A successful Invocation proves that the mandatory source-declared Modify Owner steps completed for the same SUPI / PSI / generation: the SM Context is operational, the m3 intent result is available, m4 has the matching AN tunnel, and m5 confirms N3 synchronization.

This is not proof of live 5GC qualification, user-plane traffic success, a CHF reservation, Host ResourceMap mutation, or completion of an unrelated Establishment callback.
