# OpenAMSM source mapping — Modify PDU Session

**Status: SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.**

## Pinned source

- Repository: `odango-chan/env-openamsm`
- Source snapshot recorded by the lifecycle design: `77c0a2f8511c3498d1270f059881b3cf0f7f5eeb`
- Current imported plan path: `upstream/openamsm/tools/nw-agent/plans/modify/pdu-mod-v3.yaml`
- Plan identity: `wf-certified-pdu-mod-v3`, `sm-mas-ops/3.2`, `oes-dsl/1.3`
- Retrieved plan blob: `8a2caf343c29bb64cbb09b29994c79ac8ad5da05`

## Exact plan inventory

| Step | MAS operation | Inputs | Outputs | Required |
|---|---|---|---|---|
| m0 | SC.UPDATE_SM_CONTEXT | none (`inputs: {}`) | lifecycle | no declared input |
| m2 | CA.UPDATE_CHARGING | none | charging_ref | optional |
| m3 | UPN.MODIFY_UP_SESSION | up_intent = literal `'1'` | n4_seid | up_intent |
| m4 | SSM.SIGNAL_UE_AN | none (`inputs: {}`) | an_tunnel_teid, an_tunnel_ip, an_tunnel | none declared |
| m5 | UPN.MODIFY_UP_SESSION | an_tunnel_teid/ip from m4; n4_seid from m3 | n3_synced | all three values |

The plan comments explicitly state that for PCF-initiated / AF QoS / stock UE modification, PCC is already on the Session through SmPolicyNotify or local TFT. The modification plan MUST NOT POST Npcf policy update. Policy-first IP backfill belongs to establishment (s6u), not Modify.

## Procedure mapping decisions

- m0 is a new candidate callable `mas::SC.UPDATE_SM_CONTEXT`; its exact input map is empty and its output `lifecycle` is expected to be `OPERATIONAL` after the source implementation returns success.
- m2 is deliberately not invoked in the base Procedure. The source marks it optional but provides no applicability predicate. Calling it unconditionally or inventing an applicability condition would not be source-aligned.
- m3 and m5 both use `mas::UPN.MODIFY_UP_SESSION`, but they are separate Node occurrences and separate mutations. Owner publication MUST bind each receipt/effect to the exact Run + Node occurrence + Session generation; the m5 receipt MUST NOT be reused from m3.
- m3 sends only `up_intent: "1"`. With no AN tunnel tuple, the current UPN implementation applies the UP intent and returns the existing `n4_seid`; it does not perform the final N3 tunnel synchronization.
- m4 reuses `mas::SSM.SIGNAL_UE_AN` with an empty input map. Its pending Owner operation owns correlation to the matching AMF/RAN response and returns the exact AN tunnel tuple only when its completion contract is satisfied.
- m5 consumes the m4 tunnel tuple and m3 `n4_seid`; the UPN implementation performs the N4 modification and reports `n3_synced`.
- The Procedure does not invent arguments from SUPI/PSI or private Session handles where the OES plan declares none. Host binds the selected Owner Session and generation out-of-band under the trusted Context/Owner contract.

## Ingress classification

The Skill-owned Request Schema accepts only the source-described new modification classes:

- `UE_REQUESTED`
- `PCF_INITIATED`
- `AF_QOS_INITIATED`

This is Host classification metadata, not an OES Operation argument. The Host must authenticate the original ingress, resolve it to one existing Session generation and select this Procedure only for a new modification. A late response that completes an already-pending establishment or modification Owner operation resumes that original occurrence; it must not create a second Modify Run.

## SBI entry and continuation classification

The business Request Schema uses the flowbook's three entry families:

| Family | Public ingress / event | Host decision |
|---|---|---|
| F03 | `Nsmf_PDUSession_UpdateSMContext` with N1 5GSM PDU Session Modification Request | Start a new Modify Run after resolving the existing Session generation |
| F04 | `Nsmf_PDUSession_UpdateSMContext` carrying an AMF/RAN-originated modification context | Start a new Run only when classification proves this is a new business modification; the pinned OES plan has no explicit ingress discriminator, so this remains a Host/Owner qualification item |
| F05 | Trusted PCF/AF/SMF network-triggered event, followed by the applicable Namf N1/N2 flow | Start or continue a Modify Run only through the authenticated private Owner-event binding |

An UpdateSMContext carrying the response to an already-pending establishment or modification (including the original s10 occurrence) is not F04 new work. It MUST be correlated to the original Owner/Run occurrence and resume it; it MUST NOT create another Modify Run. The Request Schema records the Host's classification after this distinction has been made. The trigger is not an OES plan argument and does not authorize the caller to choose the Session.

## Owner interface closure matrix

The following are the exact source-derived field shapes the Owner package must publish. They are **requirements for the future Owner export**, not published Schema IDs or a claim that a current ToolCatalog already contains them.

| Node occurrence | Candidate callable | Input shape required by this Procedure | Output shape required by this Procedure | Effect / proof boundary |
|---|---|---|---|---|
| m0 | `mas::SC.UPDATE_SM_CONTEXT` | empty object | `lifecycle: string` (source success value `OPERATIONAL`) | MUTATION; SC context update completion |
| m3 | `mas::UPN.MODIFY_UP_SESSION` | `up_intent: string` (literal `"1"`) | `n4_seid: string` | MUTATION; UP intent applied and existing N4 SEID returned |
| m4 | `mas::SSM.SIGNAL_UE_AN` | empty object | `an_tunnel: string`, `an_tunnel_teid: string`, `an_tunnel_ip: string` | MUTATION; exact correlated AN result, not transfer ACK |
| m5 | `mas::UPN.MODIFY_UP_SESSION` | `an_tunnel_teid: string`, `an_tunnel_ip: string`, `n4_seid: string` | `n3_synced: string` | MUTATION; second distinct N4/N3 synchronization occurrence |

m3 and m5 deliberately share a callable ID but not an invocation/effect/receipt identity. The Owner export must support both input profiles without treating one occurrence's receipt as the other's. The shared SSM callable is also used by Establishment and Release; its published Input Schema must model the supported call profiles without accepting ambiguous combinations. The exact Schema IDs, Evidence Guarantee IDs, ownerOutcomes and mutation.reconcile binding remain Owner-owned and unpublished.

## Qualification gaps

1. Publish exact callable IDs, Effects, schemas, outcomes and Evidence Guarantees for m0/m3/m4/m5.
2. Prove the m3/m5 occurrence identity and exact-original reconciliation behavior.
3. Define m4's callback binding, pending disposition, deadline and exact completion output for each supported ingress class.
4. Publish the trusted Host Context Schema and ingress-classification contract.
5. Run success, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE cases.
