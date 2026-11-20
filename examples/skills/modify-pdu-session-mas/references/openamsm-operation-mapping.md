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

The Skill-owned Request Schema accepts the three Host-classified entry families:

- `UE_REQUESTED` (F03)
- `AMF_RAN_REQUESTED` (F04, only when proven to be a new business modification)
- `NETWORK_TRIGGERED` (F05, including trusted PCF/AF/SMF events)

This is Host classification metadata, not an OES Operation argument. The F05 source plan comments specifically cover PCF-initiated and AF-QoS modifications; the F04 new-business variant remains unqualified until the Host/Owner proves its mapping. The Host must authenticate the original ingress, resolve it to one existing Session generation and select this Procedure only for a new modification. A late response that completes an already-pending establishment or modification Owner operation resumes that original occurrence; it must not create a second Modify Run.

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
| m0 | `mas::SC.UPDATE_SM_CONTEXT` | `ue_identity: string`, `psi: integer` (both scope-only; no OES business inputs) | `lifecycle: string` (source success value `OPERATIONAL`) | MUTATION; SC context update completion |
| m3 | `mas::UPN.MODIFY_UP_SESSION` | scope-only `ue_identity` + `psi`; `upIntent: string` (literal `"1"`; Owner adapter maps to OES `up_intent`) | `n4_seid: string` | MUTATION; UP intent applied and existing N4 SEID returned |
| m4 | `mas::SSM.SIGNAL_UE_AN` | scope-only `ue_identity` + `psi`; no OES business inputs | `an_tunnel: string`, `an_tunnel_teid: string`, `an_tunnel_ip: string` | MUTATION; exact correlated AN result, not transfer ACK |
| m5 | `mas::UPN.MODIFY_UP_SESSION` | scope-only `ue_identity` + `psi`; `anTunnelTeid: string`, `anTunnelIp: string`, `n4Seid: string` (Owner adapter maps to OES snake_case fields) | `n3_synced: string` | MUTATION; second distinct N4/N3 synchronization occurrence |

`ue_identity` is bound from `context.supi`; `psi` is bound from the validated 3GPP `context.request.pduSessionId`. They are public Owner Scope arguments only and MUST NOT be forwarded as OES business fields. m3 and m5 deliberately share the backend MAS operation and candidate callable identity but not an invocation/effect/receipt identity. Their distinct input/output profiles require an exact Owner contract; the existing Establishment s11 profile only matches m5. The shared SSM callable is also used by Establishment and Release; its published Input Schema must model the closed call profiles without accepting ambiguous combinations. The exact Schema IDs, Evidence Guarantee IDs, ownerOutcomes and mutation.reconcile binding remain Owner-owned and unpublished.

## Predicate Evidence publication boundary

Only m4 and m5 use the exact candidate Evidence Guarantee identities already present in ca-client-tools PR #14 (`ssm.access-network-ready` and `upn.n3-synchronized`). They remain untrusted because PR #14 is not a published Owner snapshot.

m0's `lifecycle` and m3's `n4_seid` are Operation outputs and therefore require Owner Evidence. No exact Guarantees for these facts exist in the current candidate package. Their `evidence.requires` entries are intentionally withheld rather than filled with invented IDs. Under frozen v1alpha5, the Compiler must report `PREDICATE_EVIDENCE_REQUIRED` until the Owner publishes the exact Guarantees and descriptors. This is an intentional NOT_LINKABLE blocker, not a PASS.

## Cross-repository Owner candidate alignment

Reviewed `odango-chan/ca-client-tools` PR #14, head `17c29f5b1b5751a785d0e314361da3eacc4774a5`, candidate package `mas-owner-candidate/v0.1.0`. It is Draft, NOT_QUALIFIED, NOT_DEPLOYABLE and NOT_LINKABLE; its Schema IDs are `urn:example` placeholders, not trusted snapshots.

| This Procedure occurrence | Existing candidate mapping | Decision |
|---|---|---|
| m3 UPN modify before AN | Candidate `UPN.MODIFY_UP_SESSION` / s11 requires AN tunnel tuple + n4 SEID and returns only `n3_synced` | **Not a shape match.** The first occurrence accepts only the Owner-facing `upIntent` profile (mapped to OES `up_intent`) and returns `n4_seid`. Owner must publish a separate closed profile / output contract, or a compiler-supported discriminated union; do not pretend s11's current schema covers m3. |
| m4 SSM signal | Candidate `SSM.SIGNAL_UE_AN` / s10 output Schema matches the AN tuple; current s10 input Schema requires establishment session keys, UE address and N4 SEID | Output Schema candidate is reused by ID in the Predicate. Input profile is not a match: Modify m4 has an empty OES input map and must bind the already-existing Session privately. Owner must publish this closed context-bound profile; do not make all fields optional on an unbounded Tool. |
| m5 UPN modify after AN | Candidate `UPN.MODIFY_UP_SESSION` / s11 input fields and `n3_synced` output match this occurrence | Reuse the existing candidate callable and output Schema; keep the m5 receipt distinct from m3. |
| m0 SC update context | No candidate callable/schema in PR #14 | New Owner export required. |

Exact candidate output Schema IDs referenced by this Procedure are `mas::urn:example:openamsm:mas:ssm-signal-ue-an-result:v1` for m4 and the candidate `mas::urn:example:openamsm:mas:upn-modify-up-session-result:v1` remains the output target for m5 once the Owner binding is confirmed. The current candidate m5 Schema contains only `n3_synced`; m3's `n4_seid` is deliberately read as a primitive output field and still requires a new Owner output contract.

## Qualification gaps

1. Publish exact callable IDs, Effects, schemas, outcomes and Evidence Guarantees for m0/m3/m4/m5.
2. Prove the m3/m5 occurrence identity and exact-original reconciliation behavior.
3. Define m4's callback binding, pending disposition, deadline and exact completion output for each supported ingress class.
4. Publish the trusted Host Context Schema and ingress-classification contract.
5. Run success, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE cases.

## Qualification scenario matrix (design obligations; NOT_RUN)

| Scenario | Setup / fault | Required result |
|---|---|---|
| M-01 success / UE | F03 new UE modification; same existing Session generation; m4 returns correlated AN tunnel tuple | m0 → m3 → m4 → m5; final Postcondition PASS → SUCCEEDED; m3/m5 have distinct receipts |
| M-02 success / network | F05 trusted PCF/AF event; existing Session selected by Host | New Modify Run only after authenticated Owner event; same m0/m3/m4/m5 graph; no duplicate PCF policy update |
| M-03 AMF/RAN new business | F04 classified as a genuinely new modification, not a response to a pending operation | Host/Owner must explicitly prove admission and mapping; otherwise reject / NOT_QUALIFIED, never guess |
| M-04 denied | Deny each callable in turn | No later Node dispatch; DENIED follows the declared FAILED route |
| M-05 failed after side effects | Fail m3, m4 or m5 after earlier stages completed | SAFE_STOPPED with prior mutation responsibility retained |
| M-06 unknown mutation | Lose the result of m0/m3/m5 after dispatch | UNRESOLVED; only exact-original authorized Reconcile may resolve; no new mutation dispatch |
| M-07 duplicate callback | Deliver the same m4 AN result twice | One original m4 occurrence completes once; duplicate is recorded/rejected, no second m5 |
| M-08 wrong generation | Callback identifies another Session generation for the same UE/PSI | Reject before binding output; no m5 dispatch |
| M-09 late callback | Deliver callback after original Run deadline/terminal state | Do not start a new Modify Run or attach to a newer generation |
| M-10 mixed UE | Interleave two UE/PSI modifications | All Operation outputs, receipts and callbacks remain invocation- and generation-scoped |

These are acceptance targets, not executable Case Runner files. The CA-SL specification delegates the physical `case.yaml` format to the separate Case Runner contract; no ad-hoc case syntax is invented here.
