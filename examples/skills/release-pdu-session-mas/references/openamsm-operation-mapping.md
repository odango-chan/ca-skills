# OpenAMSM source mapping — Release PDU Session

**Status: SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.**

## Pinned source

- Repository: `odango-chan/env-openamsm`
- Source snapshot recorded by the lifecycle design: `77c0a2f8511c3498d1270f059881b3cf0f7f5eeb`
- Current imported plan path: `upstream/openamsm/tools/nw-agent/plans/release/pdu-rel-v4.yaml`
- Plan identity: `wf-certified-pdu-rel-v4`, `sm-mas-ops/3.2`, `oes-dsl/1.3`
- Retrieved plan blob: `849c3206569d452a663d1b8d42a63ffdc367be31`
- Open5GS trigger constants: `upstream/openamsm/lib/pfcp/xact.h`, blob `bbdb879d217fe7ec360a661ac22a5b08865e115c`

## Exact plan inventory

| Step | MAS operation | Inputs | Outputs | Required |
|---|---|---|---|---|
| r1 | CA.DELETE_CHARGING | none | charging_ref | optional |
| r2 | UPN.DELETE_UP_SESSION | trigger from workflow start | released | required |
| r3 | SSM.SIGNAL_UE_AN | release='1'; trigger from workflow start | none declared | required |
| r4 | PA.DELETE_SM_POLICY | release='1' | none declared | required |
| r5 | SC.RELEASE_SM_CONTEXT | release='1' | lifecycle | required |
| r6 | SE.EMIT_EVENTS | ev=RELEASED | none declared | required, async_ok |
| r7 | SC.COMPENSATE_RELEASE | execute: skip | none | not executed |

## Trigger contract

The current OpenAMSM C adapter parses `trigger` with `atoi`, so this input is not a free-form label. The pinned Open5GS header defines the exact numeric values:

| Value | Open5GS constant | Release behavior in the current MAS implementation |
|---:|---|---|
| 1 | `OGS_PFCP_DELETE_TRIGGER_LOCAL_INITIATED` | SSM skips UE N1/N2 signaling |
| 2 | `OGS_PFCP_DELETE_TRIGGER_UE_REQUESTED` | SSM sends the release through the existing UpdateSMContext transaction and waits for AMF release confirmation |
| 3 | `OGS_PFCP_DELETE_TRIGGER_PCF_INITIATED` | SSM sends N2 release signaling without a UE N1 command |
| 4 | `OGS_PFCP_DELETE_TRIGGER_RAN_INITIATED` | SSM follows the network-triggered release signaling path |
| 5 | `OGS_PFCP_DELETE_TRIGGER_SMF_INITIATED` | SSM sends UE/network release signaling |
| 6 | `OGS_PFCP_DELETE_TRIGGER_AMF_RELEASE_SM_CONTEXT` | SSM skips N1/N2; Host/SMF responds on the original AMF release transaction |
| 7 | `OGS_PFCP_DELETE_TRIGGER_AMF_UPDATE_SM_CONTEXT` | SSM skips N1/N2; Host/SMF responds on the original AMF update transaction |

The Skill Request Schema carries the exact integer because the current C adapter consumes an integer. Host MUST classify the authenticated ingress and bind the corresponding value; callers MUST NOT choose an arbitrary trigger. A future Owner-facing symbolic enum is acceptable only if its adapter performs this exact version-pinned conversion before entering the C implementation.

## Procedure mapping decisions

- r1 is omitted because it is optional and the plan provides no applicability rule. No CHF deletion is claimed.
- r2 passes the Host-classified numeric `trigger` to the Owner. The UPN implementation persists it before PFCP deletion so r3 sees the same release cause.
- r2's `released` output is exactly `"1"` on immediate success and after the matching PFCP deletion response. A pending PFCP deletion does not complete r2 until the exact parked invocation receives its result.
- r3 invokes `mas::SSM.SIGNAL_UE_AN` with `release: "1"` and the same trigger. For trigger 2, it uses the original UpdateSMContext transaction; for triggers 6/7/1 it returns without N1/N2 signaling; for other supported triggers it follows the corresponding N1/N2 path. For release signaling that is pending, the Owner invocation completes only after the correlated AMF release confirmation; the HTTP transfer acknowledgement alone is not final completion.
- r4 invokes `mas::PA.DELETE_SM_POLICY`. The source plan declares no output. The C adapter may expose an internal `terminated` marker, but this Procedure does not depend on it; successful Operation completion is the step boundary.
- r5 invokes `mas::SC.RELEASE_SM_CONTEXT`. Its implementation sets lifecycle to `RELEASING`, then advances the release commit phases: UDM SDM unsubscription, UECM deregistration and the appropriate AMF-facing release response/notification. The operation completes only after its pending Owner work is resolved. The Procedure verifies the declared output `lifecycle == "RELEASING"`; it does not claim a separate `RELEASED` lifecycle value.
- r6 invokes local `SE.EMIT_EVENTS(ev="RELEASED")`. The C adapter records the event and returns success. The OES plan declares no output, so the Procedure does not invent or bind a `last_event` field.
- r7 is not a Procedure Node. The OES source marks it `execute: skip`; its configured `compensate_then_replan_once` strategy is not imported. Mutation UNKNOWN requires exact-original authorized Owner reconciliation and MUST NOT dispatch a new release mutation.

## Source-plan defect

The pinned OES YAML declares `start_inputs: {}` while r2 and r3 both reference `from_start: trigger`. The referenced start input is therefore not declared by the plan. This is a source-plan contract defect, not something the Skill can repair by inventing an implicit input. The OES plan owner must declare and type `start_inputs.trigger` (integer, constrained to the seven pinned values) before claiming that the source plan itself is executable. The Skill's own Request Schema and Host Context binding do not silently modify that OES plan.

## Owner interface closure matrix

The following are the exact source-derived field shapes the Owner package must publish. They are **requirements for the future Owner export**, not published Schema IDs or a claim that a current ToolCatalog already contains them.

| Node occurrence | Candidate callable | Input shape required by this Procedure | Output shape required by this Procedure | Effect / proof boundary |
|---|---|---|---|---|
| r2 | `mas::UPN.DELETE_UP_SESSION` | `trigger: integer` (one of the seven pinned values) | `released: string` (source success value `"1"`) | MUTATION; matching PFCP deletion completion |
| r3 | `mas::SSM.SIGNAL_UE_AN` | `release: string` (literal `"1"`), `trigger: integer` | no OES output fields | MUTATION; exact release signaling disposition and any required AMF confirmation |
| r4 | `mas::PA.DELETE_SM_POLICY` | `release: string` (literal `"1"`) | no OES output fields | MUTATION; PCF association deletion completion |
| r5 | `mas::SC.RELEASE_SM_CONTEXT` | `release: string` (literal `"1"`) | `lifecycle: string` (source completion value `RELEASING`) | MUTATION; UDM unsubscribe, UECM deregistration and AMF response phases completed |
| r6 | `mas::SE.EMIT_EVENTS` | `ev: string` (literal `RELEASED`) | no OES output fields | MUTATION; local MAS event write completed |

The shared SSM callable is also used by Establishment and Modify. Its published Input Schema must model these distinct call profiles (including release-specific `release` and `trigger`) without accepting ambiguous combinations. No synthetic Output fields are introduced for r3/r4/r6. The exact Schema IDs, Evidence Guarantee IDs, ownerOutcomes and mutation.reconcile binding remain Owner-owned and unpublished.

## Qualification gaps

1. Publish exact callable IDs, Effects, input/output Schemas, outcomes and Evidence Guarantees for r2–r6.
2. Fix and publish the OES `start_inputs.trigger` declaration, then validate the plan against the OES DSL.
3. Prove N4 deletion, AN release signaling, PCF association deletion and SM Context release against the same SUPI/PSI/Session generation.
4. Verify the trigger integer mapping against the exact vendored Open5GS header at the Owner build revision.
5. Prove durable resource tombstone, duplicate/late callback rejection and exact-original Reconcile without re-dispatch.
6. Run success, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE cases.

## Qualification scenario matrix (design obligations; NOT_RUN)

| Scenario | Setup / fault | Required result |
|---|---|---|
| R-01 success / UE request | trigger=2; existing Session and original UpdateSMContext transaction | r2 PFCP delete → r3 uses original UpdateSMContext and waits for correlated release confirmation → r4 → r5 → r6; final PASS → SUCCEEDED |
| R-02 success / AMF release | trigger=6 | r3 performs no N1/N2 signaling; r5 handles the original AMF ReleaseSMContext response |
| R-03 success / AMF update | trigger=7 | r3 performs no N1/N2 signaling; r5 handles the original AMF UpdateSMContext response |
| R-04 success / local | trigger=1 | r3 skips N1/N2; remaining release steps complete |
| R-05 network trigger variants | trigger=3/4/5 | Verify the source-specific PCF/RAN/SMF signaling path and exact AMF confirmation behavior |
| R-06 denied | Deny each callable in turn | No later Node dispatch; DENIED follows the declared FAILED route |
| R-07 failed after partial release | Fail r2/r3/r4/r5 after earlier effects | SAFE_STOPPED; preserve exact Session-generation and residual responsibility |
| R-08 unknown mutation | Lose result of r2/r3/r4/r5 after dispatch | UNRESOLVED; exact-original authorized Reconcile only; never repeat release mutation |
| R-09 duplicate/late callback | Duplicate or late AMF release confirmation | Complete only the original matching occurrence once; reject stale delivery |
| R-10 wrong generation | Callback maps to another Session generation | Reject before applying it to the Release Run |
| R-11 mixed UE | Interleave releases for two UE/PSI pairs | No cross-UE resource, trigger, callback or tombstone association |
| R-12 trigger admission | Supply value outside 1–7 or caller-selected unauthenticated trigger | Request/Host admission fails closed; no Owner mutation |
| R-13 charging | Optional r1 absent | Procedure makes no CHF deletion claim; no synthetic charging receipt |
| R-14 event | r6 succeeds after r5 | Local MAS RELEASED event is recorded; no claim of 3GPP Status Notify |

These are acceptance targets, not executable Case Runner files. The CA-SL specification delegates the physical `case.yaml` format to the separate Case Runner contract; no ad-hoc case syntax is invented here.
