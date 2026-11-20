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

## Qualification gaps

1. Publish exact callable IDs, Effects, input/output Schemas, outcomes and Evidence Guarantees for r2–r6.
2. Fix and publish the OES `start_inputs.trigger` declaration, then validate the plan against the OES DSL.
3. Prove N4 deletion, AN release signaling, PCF association deletion and SM Context release against the same SUPI/PSI/Session generation.
4. Verify the trigger integer mapping against the exact vendored Open5GS header at the Owner build revision.
5. Prove durable resource tombstone, duplicate/late callback rejection and exact-original Reconcile without re-dispatch.
6. Run success, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE cases.
