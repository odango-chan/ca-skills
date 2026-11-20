# OpenAMSM source mapping — Release PDU Session

**Status: SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.**

## Pinned source

- Repository: `odango-chan/env-openamsm`
- Source snapshot recorded by the lifecycle design: `77c0a2f8511c3498d1270f059881b3cf0f7f5eeb`
- Current imported plan path: `upstream/openamsm/tools/nw-agent/plans/release/pdu-rel-v4.yaml`
- Plan identity: `wf-certified-pdu-rel-v4`, `sm-mas-ops/3.2`, `oes-dsl/1.3`
- Retrieved plan blob: `849c3206569d452a663d1b8d42a63ffdc367be31`

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

The source plan configures `on_error.strategy=compensate_then_replan_once`. This OES policy is deliberately NOT translated into CA-SL retry or compensation behavior. The CA-SL/Host boundary uses the exact-original authorized Reconcile contract only; an unknown mutation outcome never causes a fresh release dispatch.

## Procedure mapping decisions

- r1 is omitted because it is optional and the plan provides no applicability rule. No CHF deletion is claimed.
- r2 passes the Host-classified `trigger` through exactly as the source plan requires. The trigger is a constrained Skill request value; Host must authenticate and classify the originating event.
- r3 reuses `mas::SSM.SIGNAL_UE_AN` with `release='1'`. Its Owner contract must distinguish release occurrence identity from any establishment/modify SSM operation and prove the correct callback binding.
- r4 and r5 use new candidate callable identities. Their plan inputs are only the literal release marker; Session scope is bound by the trusted Host/Owner context, not invented Procedure arguments.
- r6 is a local MAS event emission. It is not evidence that AMF received a 3GPP Status Notify.
- r7 is not a Procedure Node. The OES source marks it `execute: skip`; its configured replan strategy is not imported.

## Qualification gaps

1. Publish exact callable IDs, Effects, schemas, outcomes and Evidence Guarantees for r2–r6.
2. Prove N4 deletion, AN release signaling, PCF deletion and SM Context release against the same SUPI/PSI/Session generation.
3. Define r3's pending/callback behavior and the exact protocol response obligations.
4. Define r1 applicability before including optional charging deletion.
5. Prove durable resource tombstone, duplicate/late callback rejection and exact-original Reconcile without re-dispatch.
6. Run success, denied, UNKNOWN, duplicate, wrong-generation, late-callback and mixed-UE tests.
