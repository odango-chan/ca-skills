# OpenAMSM MAS Modify / Release source mapping

**Status: SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.** This document records the pinned OES plans, implementation behavior and required CA-facing callable profiles. It is not a published Owner ToolCatalog, trusted DependencySnapshot, mutation receipt or runtime acceptance result.

## Pinned source baseline

- Repository: odango-chan/env-openamsm
- Source commit: 594dec78b95bff4fdc34deac8a3a9681fb41228f
- Modify plan: upstream/openamsm/tools/nw-agent/plans/modify/pdu-mod-v3.yaml
  - Blob SHA: 8a2caf343c29bb64cbb09b29994c79ac8ad5da05
- Release plan: upstream/openamsm/tools/nw-agent/plans/release/pdu-rel-v4.yaml
  - Blob SHA: 849c3206569d452a663d1b8d42a63ffdc367be31

The existing Establishment mapping in this repository pins env-openamsm commit 77c0a2f8511c3498d1270f059881b3cf0f7f5eeb. The Modify and Release plan blobs are byte-identical at that pin and at 594dec78b95bff4fdc34deac8a3a9681fb41228f. The existing ca-client-tools MAS v0.2.0 candidate source map also pins 594dec78. This gives the reused m5 contract a common source basis without changing the Establishment Skill.

Relevant implementation blobs at the 594dec78 source pin:

| Source file | Blob SHA | What it grounds |
| --- | --- | --- |
| src/smf/mas/common/mas-facade.c | c4f71e8c5209a1288a56f5f588fe44ae4fa14cba | MAS operation dispatch and Release branch selection |
| src/smf/mas/sc/session_context.c | c7763919785870f4350b8779b59563dc64533a5e | SC lifecycle transitions and release phases |
| src/smf/mas/ca/charge_adapter.c | f9fb7772d316a8e2848acf18af009aa6641c1406 | Charging update/delete are successful local skip markers |
| src/smf/mas/upn/upnode.c | 0993e8ed35c691dc7dc76a682b5f1b4d23fa38cc | m3/m5 UPN branches and PFCP delete completion |
| src/smf/mas/ssm/ssm_ue.c | e59acacea03532a102d699edbbd7a0a07662f8f9 | Release trigger branches and pending N1/N2 completion |
| src/smf/mas/pa/policy_adapter.c | 110924c66cfe3455407c3ad4cdffb3e3292338b1 | PCF association delete and pending completion |
| src/smf/mas/se/session_exposure.c | bafdc069522eb1e2c8f0a3c08eed28745abbcd48 | Local in-memory event marker only |
| lib/pfcp/xact.h | bbdb879d217fe7ec360a661ac22a5b08865e115c | Numeric PFCP Delete Trigger constants |

## Existing candidate package boundary

The ca-client-tools MAS v0.2.0 source map is an unpublished candidate for the stable package ID wtlab:packages:openamsm:mas-compiler-contract. It contains the Establishment profiles, including:

- SSM.SIGNAL_UE_AN for Establishment s10, with sessionKeys / ueAddrAllocated / n4Seid inputs and the AN tunnel output tuple.
- UPN.MODIFY_UP_SESSION for Establishment s11, with AN tunnel / N4 SEID inputs and n3_synced output.
- SE.EMIT_EVENTS for Establishment s13, with event / sessionKeys inputs and last_event output.

Only the m5 UPN occurrence has the same source operation, input shape and output shape as the existing v0.2.0 UPN candidate. m4 shares the s10 output shape but not its input shape. m3 has a different UPN input and output shape. Release r3 and r6 also have different input and output shapes from the Establishment candidates.

Therefore, m3, m4, r3 and r6 use separate typed callable profiles; they do not widen or alias the existing Establishment exports.

- m5 reuses the existing UPN.MODIFY_UP_SESSION callable and its v0.2.0 input/output Schemas.
- m4 uses a distinct SSM.SIGNAL_UE_AN_MODIFY callable and a new input Schema; it may reuse the exact v0.2.0 AN tunnel output Schema.
- m3 uses a distinct UPN.MODIFY_UP_SESSION_INTENT callable and new input/output Schemas.
- r3 uses a distinct SSM.SIGNAL_UE_AN_RELEASE callable and a new input Schema plus an empty output Schema.
- r6 uses a distinct SE.EMIT_RELEASE_EVENT callable and a new input Schema plus an empty output Schema.

Do not weaken the Establishment Schemas with optional fields, do not publish a generic unbounded Tool, and do not use oneOf / anyOf unions as a substitute for exact profile contracts. The current Compiler Schema subset does not accept those schema combinators. The source step ID remains private Owner binding data; it is not a Skill argument.

## Modify: exact OES-to-Procedure mapping

| CA-SL Node | OES step / operation | Candidate callable | Effect | Candidate input Schema | Candidate output Schema | Exact OES fields |
| --- | --- | --- | --- | --- | --- | --- |
| m0 | m0 SC.UPDATE_SM_CONTEXT | SC.UPDATE_SM_CONTEXT | MUTATION | wtlab:openamsm:mas:v0.3.0:sc-update-sm-context-input | wtlab:openamsm:mas:v0.3.0:sc-update-sm-context-result | OES inputs: none; outputs: lifecycle |
| m3 | m3 UPN.MODIFY_UP_SESSION | UPN.MODIFY_UP_SESSION_INTENT | MUTATION | wtlab:openamsm:mas:v0.3.0:upn-modify-intent-input | wtlab:openamsm:mas:v0.3.0:upn-modify-intent-result | up_intent='1' -> n4_seid |
| m4 | m4 SSM.SIGNAL_UE_AN | SSM.SIGNAL_UE_AN_MODIFY | MUTATION | wtlab:openamsm:mas:v0.3.0:ssm-signal-ue-an-modify-input | wtlab:openamsm:mas:v0.2.0:ssm-signal-ue-an-result | OES inputs: none; outputs: an_tunnel_teid, an_tunnel_ip, an_tunnel |
| m5 | m5 UPN.MODIFY_UP_SESSION | UPN.MODIFY_UP_SESSION | MUTATION | wtlab:openamsm:mas:v0.2.0:upn-modify-up-session-input | wtlab:openamsm:mas:v0.2.0:upn-modify-up-session-result | an_tunnel_teid, an_tunnel_ip, n4_seid -> n3_synced |

The CA-facing ue_identity and psi fields are exact Owner Scope bindings populated from the admitted SUPI and pduSessionId. For m0 and m4 the OES steps declare no inputs; the Owner validates ue_identity / psi for Scope and does not forward them as invented OES inputs. For m3 and m5 the Owner additionally maps the declared CA-facing fields to the exact OES inputs.

m3 and m5 are separate Mutation occurrences even though their OES operation name is the same. The pinned UPN implementation has two different branches: without an AN tunnel, it applies the intent state and returns n4_seid; with the AN tunnel tuple, it parks the PFCP modification and later returns n3_synced. The m3 n4_seid is not proof of m5 N3 synchronization.

## Release: exact OES-to-Procedure mapping

| CA-SL Node | OES step / operation | Candidate callable | Effect | Candidate input Schema | Candidate output Schema | Exact OES fields |
| --- | --- | --- | --- | --- | --- | --- |
| r2 | r2 UPN.DELETE_UP_SESSION | UPN.DELETE_UP_SESSION | MUTATION | wtlab:openamsm:mas:v0.3.0:upn-delete-up-session-input | wtlab:openamsm:mas:v0.3.0:upn-delete-up-session-result | trigger -> released |
| r3 | r3 SSM.SIGNAL_UE_AN | SSM.SIGNAL_UE_AN_RELEASE | MUTATION | wtlab:openamsm:mas:v0.3.0:ssm-signal-ue-an-release-input | wtlab:openamsm:mas:v0.3.0:ssm-signal-ue-an-release-result | release='1', trigger; no OES outputs |
| r4 | r4 PA.DELETE_SM_POLICY | PA.DELETE_SM_POLICY | MUTATION | wtlab:openamsm:mas:v0.3.0:pa-delete-sm-policy-input | wtlab:openamsm:mas:v0.3.0:pa-delete-sm-policy-result | release='1'; no OES outputs |
| r5 | r5 SC.RELEASE_SM_CONTEXT | SC.RELEASE_SM_CONTEXT | MUTATION | wtlab:openamsm:mas:v0.3.0:sc-release-sm-context-input | wtlab:openamsm:mas:v0.3.0:sc-release-sm-context-result | release='1' -> lifecycle |
| r6 | r6 SE.EMIT_EVENTS | SE.EMIT_RELEASE_EVENT | MUTATION | wtlab:openamsm:mas:v0.3.0:se-emit-release-event-input | wtlab:openamsm:mas:v0.3.0:se-emit-release-event-result | ev='RELEASED'; no OES outputs |

The empty output Schemas for r3, r4 and r6 are closed empty objects. They do not add synthetic output properties. Their Evidence Guarantees bind to the exact Operation result root and Owner receipt.

## Candidate Schema shapes

These are required Owner exports, not Skill-owned schemas. They must be published in the MAS Owner package and linked through the exact trusted DependencySnapshot. No duplicate copies are added to the Skill schemas/ directories.

All objects must be closed with additionalProperties=false. All strings below are strings because that is what the pinned OES plan / C adapter exposes; do not silently convert them to numbers.

| Schema profile | Required input fields | Exact output fields |
| --- | --- | --- |
| sc-update-sm-context | ue_identity: SUPI string; psi: integer 1..15 (both Scope-only) | lifecycle: string, expected OPERATIONAL |
| upn-modify-intent | ue_identity, psi (Scope-only), upIntent: const '1' | n4_seid: non-empty decimal string |
| ssm-signal-ue-an-modify | ue_identity, psi (Scope-only) | an_tunnel_teid, an_tunnel_ip, an_tunnel strings; an_tunnel must be '1' |
| upn-modify-up-session (existing v0.2.0) | ue_identity, psi, anTunnelTeid, anTunnelIp, n4Seid | n3_synced string; '1' means the source N3 synchronization branch completed |
| upn-delete-up-session | ue_identity, psi (Scope-only), trigger: integer enum 1..7 | released: string; '1' only after PFCP deletion completion |
| ssm-signal-ue-an-release | ue_identity, psi (Scope-only), release: const '1', trigger: integer enum 1..7 | empty object |
| pa-delete-sm-policy | ue_identity, psi (Scope-only), release: const '1' | empty object |
| sc-release-sm-context | ue_identity, psi (Scope-only), release: const '1' | lifecycle: string, expected RELEASING |
| se-emit-release-event | ue_identity, psi (Scope-only), ev: const RELEASED | empty object |

The Owner receipt is a separate private contract envelope. Do not add invocation IDs, generation IDs, receipt fields, private step IDs, ResourceMap keys or correlation handles to these public operation output Schemas.

## Optional steps and non-claims

- Modify m2 CA.UPDATE_CHARGING is optional and has no source-defined applicability predicate. It is omitted. Its pinned adapter only writes a local charging_ref marker and records NOT_IMPL_skip; it does not create a CHF charging reservation.
- Release r1 CA.DELETE_CHARGING is optional and has no source-defined applicability predicate. It is omitted. Its pinned adapter only clears a local marker and records NOT_IMPL_skip; it does not delete a CHF charging resource.
- Release r7 COMPENSATE_RELEASE is execute: skip. It is not a Procedure Node. The source compensate_then_replan_once strategy is not imported.
- r4 C code may maintain a private terminated marker, but the OES plan declares no r4 output. Do not expose terminated.
- r6 C code updates an in-memory last_event marker, but the OES plan declares no r6 output. Do not expose last_event or describe it as a durable event.
- r6 is not a 3GPP SM Context Status Notify.
- r5 returns lifecycle=RELEASING. It does not expose RELEASED or a Host ResourceMap tombstone.
- The Host owns ResourceMap tombstoning after exact Release settlement; it is not a Skill operation or Predicate.

## Release trigger mapping

The pinned lib/pfcp/xact.h defines:

| Numeric trigger | Source constant |
| ---: | --- |
| 1 | LOCAL_INITIATED |
| 2 | UE_REQUESTED |
| 3 | PCF_INITIATED |
| 4 | RAN_INITIATED |
| 5 | SMF_INITIATED |
| 6 | AMF_RELEASE_SM_CONTEXT |
| 7 | AMF_UPDATE_SM_CONTEXT |

The Skill Request Schema carries the numeric value because the OES plan consumes an integer and the C adapter parses it numerically. The Host derives it from authenticated SBI ingress or a trusted internal event. Symbolic strings must never be passed to the numeric source field.

**Source-plan defect:** pdu-rel-v4.yaml declares start_inputs: {} while r2 and r3 both reference from_start: trigger. The upstream plan must declare the typed start input before the Owner can link these mappings. The Skill does not invent a default or patch the upstream plan.

## Qualification boundary

The current OpenAMSM agent_step admission path rejects standard Nsmf business Update / Release admission. A private Host / Owner binding and a published Owner contract are required. The Skill does not bypass that gate.

The existing ca-client-tools v0.2.0 MAS candidate is not a trusted published ToolCatalog. The new v0.3.0 Schema IDs and callable profiles are proposed Owner exports only. Until the Owner publishes exact callable IDs, MUTATION Effects, input/output Schemas, Owner outcomes, commit receipts and Evidence Guarantees, both Skills remain NOT_LINKABLE / NOT_QUALIFIED.

The [Owner outcome contract](mas-lifecycle-owner-contract.md) defines the required receipt, Scope, pending-operation and failure semantics. The [acceptance matrix](mas-lifecycle-acceptance-matrix.md) separates static source checks from runtime scenarios that have not been run.
