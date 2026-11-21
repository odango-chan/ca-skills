# MAS Modify / Release Owner outcome contract

**Status: REQUIRED CONTRACT / NOT PUBLISHED / NOT_QUALIFIED.** This document specifies the minimum Owner and Host contract needed to link the two v1alpha5 Procedures. The declared stable MAS package identity is wtlab:packages:openamsm:mas-compiler-contract; its ToolCatalog is still an unpublished candidate. This document does not assert that ca-client-tools, OpenAMSM or Generic Host already implements the contract.

## Effect and callable identity

Every callable occurrence in these Procedures is a candidate MUTATION, including local state updates and the r6 in-memory event marker. The trusted ToolCatalog and deployment CapabilityContracts must publish that Effect. No Procedure may infer READ from an operation's name, an HTTP method, or a successful source return code.

The required callable profiles and exact input/output Schema IDs are listed in the [source mapping](mas-lifecycle-source-mapping.md). m5 uses a dedicated UPN.MODIFY_QOS_FLOWS profile with a closed QoS delta. m3, m4, r3 and r6 use separate typed callable profiles because their source input/output shapes do not match the Establishment exports. The Owner must not replace these profiles with a generic optional-field schema.

## Exact invocation and Scope binding

For every invocation the Owner must bind:

- the immutable original Host Invocation / Mutation identity;
- exact public callable ID and private OES step occurrence;
- exact SUPI and PDU Session ID (PSI);
- private SMF session generation and pending-operation correlation;
- authenticated deployment and Owner identity;
- canonical input digest, Effect, Schema version and exact output shape;
- commit state and Evidence for that same original occurrence.

The CA-facing ue_identity and psi values are Scope inputs. The Owner verifies them against the selected session and forwards only the OES fields declared by that step. For OES steps with inputs: {}, these Scope fields are not forwarded as invented OES inputs.

Private sessionRef, smContextRef, stepId, generation IDs, idempotency keys, invocation IDs, stream handles, transport correlation IDs and orchestration credentials must never appear in Skill Request Schemas or public Operation arguments.

## Required Owner outcomes

| Outcome | Authority | Required meaning | Procedure treatment |
| --- | --- | --- | --- |
| SUCCEEDED | Owner | Exact original mutation is committed; every declared OES output field is complete; the required Evidence Guarantee is available for the same occurrence and Scope. | Advance to the Node Postcondition. |
| FAILED | Owner, only if published | Deterministic failure with proof that the exact mutation did not commit and left no residual side effect. | First mutation may terminate FAILED; after earlier committed steps, terminate SAFE_STOPPED. |
| NOT_COMMITTED | Not currently published | Would require a separate trusted receipt proving the exact original mutation did not commit. It is not inferred from a missing response. | No Procedure route and no automatic retry in this design. |
| DENIED | Host / Runtime | Authorization or Scope rejected before Owner dispatch. | First mutation may terminate FAILED; after earlier commits, SAFE_STOPPED. |
| OUTCOME_UNKNOWN | Host / Runtime | Commit state or pending callback cannot be proven, including timeout, restart, missing receipt, stale or mismatched callback. | SAFE_STOPPED; preserve original responsibility. |
| COMMITTED | Host reconciliation result | Commit is proven but the complete original public output / Evidence cannot be recovered. This is not an Owner success. | No Procedure route exists until a trusted exact-original mutation.reconcile contract is published. |

An Owner must not report FAILED for a timeout, process restart, generic HTTP error, missing receipt, pending PFCP result or unknown callback. Those cases remain OUTCOME_UNKNOWN. A raw HTTP 2xx, a MAS status=OK, or a local in-memory flag is not a commit receipt.

The candidate Owner contract must publish SUCCEEDED and a narrowly defined FAILED class for each callable. FAILED is valid only when the Owner can prove no commit and no residual side effect. If the Owner cannot make that proof, it must not return FAILED. No NOT_COMMITTED outcome, retry, compensation or replan is required by these Procedures.

## Per-occurrence completion and Evidence

| Occurrence | Required SUCCEEDED boundary | Required Evidence Guarantee |
| --- | --- | --- |
| m0 SC.UPDATE_SM_CONTEXT | Existing exact SM Context is updated; declared lifecycle output is OPERATIONAL. | mas::sc.context-updated |
| m3 UPN.MODIFY_UP_SESSION_INTENT | The no-tunnel intent branch is applied to the exact session; n4_seid is returned. This is not N3 synchronization. | mas::upn.modify-intent-applied |
| m4 SSM.SIGNAL_UE_AN_MODIFY | The exact Modify signaling occurrence has the matching AN result and returns the declared tunnel tuple. | mas::ssm.modify-an-tunnel-ready |
| m5 UPN.MODIFY_QOS_FLOWS | The exact QFI/5QI/GBR/MBR target is atomic. APPLIED means the PFCP Update QER was accepted and the native N1/N2 Modify was dispatched; ALREADY means the authoritative flow already equals the exact target. Neither means RAN/UE acceptance. | mas::upn.qos-delta-applied |
| r2 UPN.DELETE_UP_SESSION | The exact PFCP Session Deletion completes; released=1 is not returned merely because the delete request was sent. | mas::upn.up-session-released |
| r3 SSM.SIGNAL_UE_AN_RELEASE | For triggers 1, 6 and 7, prove the source-defined no-signal branch. For triggers 2, 3, 4 and 5, wait for the matching AMF release confirmation. | mas::ssm.release-signal-settled |
| r4 PA.DELETE_SM_POLICY | The exact PCF association is deleted or its absence is verified for the same Scope. | mas::pa.policy-association-released |
| r5 SC.RELEASE_SM_CONTEXT | UDM unsubscribe, UECM deregistration and the applicable AMF acknowledgement phases settle; the only public output is lifecycle=RELEASING. | mas::sc.context-release-committed |
| r6 SE.EMIT_RELEASE_EVENT | The source writes the local in-memory RELEASED marker for the exact session. No durability or external delivery is implied. | mas::se.release-event-marker-written |

For r3, r4 and r6 the OES plan declares no output fields. Their Owner output Schema is a closed empty object. The Evidence Guarantee binds to the exact result root and private Owner receipt; do not invent fields such as terminated or last_event.

The Owner receipt is a separate private contract envelope. It must bind original Invocation, callable, private OES occurrence, SUPI, PSI, generation, input digest, commit state, observed time and Evidence. Do not add receipt metadata to the source-declared Operation output Schema.

## Pending operations, duplicate delivery and generation isolation

- m4 remains pending until the matching Modify AN result is correlated to the original occurrence.
- m5 remains pending until the matching PFCP QoS response is accepted and the native N1/N2 Modify dispatch result is known.
- r2 remains pending until the matching PFCP deletion completion.
- r3 remains pending until either the source-defined no-signal branch is proven or the matching AMF release confirmation completes.
- r4 remains pending until PCF deletion settles.
- r5 remains pending through the applicable UDM / UECM / AMF release phases.
- A duplicate original Invocation returns the original settled result and receipt; it never dispatches a second mutation.
- A callback or receipt with a different generation is rejected and cannot satisfy a Predicate.
- A late callback attaches only to its original pending occurrence. It must never resume a cancelled, completed or newer Run.
- Reusing the same PSI under another SUPI must not satisfy the original Scope.
- OUTCOME_UNKNOWN never triggers a blind retry, compensation or new Release sequence. Host reconciliation is allowed only after a trusted exact-original mutation.reconcile contract is published.

The N2 Setup Response that completes Establishment s10 belongs to the original Establishment Owner operation and Run. It must not start Modify or Release.

For D5 m5, the later N2 Modify Response is a separate native continuation. It
may confirm RAN acceptance, but it must not re-complete the MAS invoke. The
Skill Predicate closes at PFCP_APPLIED + N1N2_DISPATCHED; a Host that needs
RAN_MODIFICATION_CONFIRMED or TARGET_STATE_VERIFIED must record a separate,
independent observation and must not derive it from `APPLIED`.

## Host and source blockers

The current OpenAMSM agent_step admission path rejects standard Nsmf business Update / Release admission. A separate Owner-private binding and trusted publication are required. Do not weaken that protocol gate or invent a public SBI route in order to link these Skills.

The pinned Release OES plan declares start_inputs: {} but r2 and r3 reference from_start: trigger. The upstream plan must declare the typed trigger input before the Owner can publish an executable binding. The Skill does not invent a default.

The Host owns external URI ResourceMap tombstoning after the exact Release lifecycle is settled. lifecycle=RELEASING is not a tombstone and is not RELEASED.

Modify m2 CA.UPDATE_CHARGING and Release r1 CA.DELETE_CHARGING are optional without a source-defined applicability predicate, so neither is included. The current adapter only writes or clears a local charging marker and records NOT_IMPL_skip; it does not reserve or delete a CHF resource. Release r7 is execute: skip and is excluded; compensate_then_replan_once is not imported.

Until the Owner publishes the exact callable profiles, MUTATION Effects, input/output Schemas, Owner outcomes, commit receipts, Evidence Guarantees and Owner identity, and until the Host-private bindings and Release trigger declaration are fixed, both Skills remain NOT_LINKABLE / NOT_QUALIFIED.
