# MAS Modify / Release Owner outcome contract

**Status: REQUIRED CONTRACT / NOT PUBLISHED / NOT_QUALIFIED.** This document
specifies the minimum Owner and Host contract needed to link the two v1alpha5
Scheme C Procedures. The declared stable MAS package identity is
`wtlab:packages:openamsm:mas-compiler-contract`; its ToolCatalog is still an
unpublished candidate. This document does not assert that ca-client-tools,
OpenAMSM or Generic Host already implements the contract.

## Effect and callable identity

The trusted ToolCatalog and deployment CapabilityContracts must publish the
Effect of every Scheme C occurrence. `SSM.PARSE_N1_MODIFY` and
`SSM.PARSE_N1_RELEASE` are READ. `UPN.MODIFY_QOS_DELTA`,
`SSM.BUILD_RELEASE_COMMAND`, `SSM.RELEASE_CONFIRM_N1`,
`SSM.RELEASE_CONFIRM_N2`, `PA.DELETE_SM_POLICY_C`, `UPN.DELETE_UP_SESSION`,
`SE.EMIT_RELEASE_EVENT_C` and `SC.RELEASE_SM_CONTEXT_C` are candidate MUTATIONs,
including the local in-memory event marker. No Procedure may infer READ from an
operation's name, an HTTP method, or a successful source return code.

The exact input/output Schema IDs must be published by the merged Owner. Do not
replace these profiles with a generic optional-field schema, and do not widen the
Establishment exports to cover them.

## Exact invocation and Scope binding

For every invocation the Owner must bind:

- the immutable original Host Invocation / Mutation identity;
- exact public callable ID and private Owner occurrence;
- exact SUPI and PDU Session ID (PSI);
- private SMF session generation and pending-operation correlation;
- authenticated deployment and Owner identity;
- canonical input digest, Effect, Schema version and exact output shape;
- commit state and Evidence for that same original occurrence.

The CA-facing `ue_identity` and `psi` values are Scope inputs. The Owner verifies
them against the selected session and resolves the retained raw N1 and any
Host-private transaction state from trusted private context at dispatch time.

**Schema boundary.** The raw N1 and the Host-private release transaction id are
not Skill-authored request fields. They are Provider-injected / Host-private and
must never appear in Skill Request Schemas or public Operation arguments. The
same rule applies to the parsed QoS delta and to private `sessionRef`,
`smContextRef`, `stepId`, generation IDs, idempotency keys, invocation IDs,
stream handles, transport correlation IDs and orchestration credentials.

**Run continuity.** The Release N1/N2 confirmations are separate SBI ingress
events for the same original Run. A confirmation must be bound to the original Run: it is never fabricated from a state string, never re-binds a different
transaction, and never starts a new Run. A duplicate or late answer attaches
only to its original pending occurrence.

## Required Owner outcomes

| Outcome | Authority | Required meaning | Procedure treatment |
| --- | --- | --- | --- |
| SUCCEEDED | Owner | Exact original mutation is committed; every declared Owner output field is complete; the required Evidence Guarantee is available for the same occurrence and Scope. | Advance to the Node Postcondition. |
| FAILED | Owner, only if published | Deterministic failure with proof that the exact mutation did not commit and left no residual side effect. | First mutation may terminate FAILED; after earlier committed steps, terminate SAFE_STOPPED. |
| NOT_COMMITTED | Not currently published | Would require a separate trusted receipt proving the exact original mutation did not commit. It is not inferred from a missing response. | No Procedure route and no automatic retry in this design. |
| DENIED | Host / Runtime | Authorization or Scope rejected before Owner dispatch. | First mutation may terminate FAILED; after earlier commits, SAFE_STOPPED. |
| OUTCOME_UNKNOWN | Host / Runtime | Commit state or pending callback cannot be proven, including timeout, restart, missing receipt, stale or mismatched callback. | SAFE_STOPPED; preserve original responsibility. |
| COMMITTED | Host reconciliation result | Commit is proven but the complete original public output / Evidence cannot be recovered. This is not an Owner success. | No Procedure route exists until a trusted exact-original mutation.reconcile contract is published. |

An Owner must not report FAILED for a timeout, process restart, generic HTTP
error, missing receipt, pending PFCP result or unknown callback. Those cases
remain OUTCOME_UNKNOWN. A raw HTTP 2xx, a MAS `status=OK`, or a local in-memory
flag is not a commit receipt.

The candidate Owner contract must publish SUCCEEDED and a narrowly defined FAILED
class for each callable. FAILED is valid only when the Owner can prove no commit
and no residual side effect. If the Owner cannot make that proof, it must not
return FAILED. No NOT_COMMITTED outcome, retry, compensation or replan is
required by these Procedures.

## Per-occurrence completion and Evidence

| Occurrence | Required SUCCEEDED boundary | Required Evidence Guarantee |
| --- | --- | --- |
| `parse-n1` (Modify) `SSM.PARSE_N1_MODIFY` | READ: the exact retained 0xc9 N1 decodes to exactly one GBR flow description; `qfi`, `five_qi`, `gfbr_ul`, `gfbr_dl`, `mfbr_ul`, `mfbr_dl` and `requested_kind=qos_flow_descriptions` are complete. Non-0xc9, missing or multiple flows fail closed. | `mas::ssm.n1-modify-parsed` |
| `apply-qos-delta` `UPN.MODIFY_QOS_DELTA` | The exact parsed target is atomic. APPLIED means the PFCP Update QER was accepted and the native N1/N2 Modify was dispatched (`n1n2_dispatched=1`); ALREADY means the authoritative flow already equals the exact target and nothing was dispatched. The Postcondition compares all six target fields as canonical decimal strings. Neither state means RAN/UE acceptance. | `mas::upn.qos-delta-applied` |
| `parse-n1` (Release) `SSM.PARSE_N1_RELEASE` | READ: the exact retained 0xd1 N1 decodes with `release_intent=ue_requested`, non-empty `psi` and `pti`. The parse must not bind the PTI or mutate session state. | `mas::ssm.n1-release-parsed` |
| `build-command` `SSM.BUILD_RELEASE_COMMAND` | The Owner builds the N1 Release Command (0xd3) and the N2 PDU Session Resource Release Command for this Run and records `release_txn` / `release_generation`. This is the only PTI binding. | `mas::ssm.release-command-built` |
| `confirm-n1` `SSM.RELEASE_CONFIRM_N1` | The exact N1 Release Complete (0xd4) was accepted for the build transaction and generation (`n1_released=1`). | `mas::ssm.release-n1-confirmed` |
| `confirm-n2` `SSM.RELEASE_CONFIRM_N2` | The exact N2 Release Response was accepted for the same transaction and generation; the Owner reports `n2_released=1` and `release_ready=1` only after both confirmations. | `mas::ssm.release-n2-confirmed` |
| `delete-policy` `PA.DELETE_SM_POLICY_C` | The exact PCF association is terminated for the same Scope (`terminated=1`). | `mas::pa.policy-association-released` |
| `delete-user-plane` `UPN.DELETE_UP_SESSION` | The exact PFCP Session Deletion completes; `released=1` is not returned merely because the delete request was sent. | `mas::upn.up-session-released` |
| `emit-release-event` `SE.EMIT_RELEASE_EVENT_C` | The Owner writes the local in-memory RELEASED marker for the exact session (`last_event=1`). No durability or external delivery is implied. | `mas::se.release-event-marker-written` |
| `release-sm-context` `SC.RELEASE_SM_CONTEXT_C` | The release/finalize phases settle; the only public output is `lifecycle=RELEASING`. | `mas::sc.context-release-committed` |

The Owner receipt is a separate private contract envelope. It must bind original
Invocation, callable, private Owner occurrence, SUPI, PSI, generation, input
digest, commit state, observed time and Evidence. Do not add receipt metadata to
the source-declared Operation output Schema.

## Pending operations, duplicate delivery and generation isolation

- The Build occurrence fixes `release_txn` / `release_generation`; both
  confirmations refer to that same original Run.
- A duplicate original Invocation returns the original settled result and
  receipt; it never dispatches a second mutation.
- A callback or receipt with a different generation or transaction is rejected
  and cannot satisfy a Predicate.
- A late confirmation attaches only to its original pending occurrence. It must
  never resume a cancelled, completed or newer Run.
- Reusing the same PSI under another SUPI must not satisfy the original Scope.
- OUTCOME_UNKNOWN never triggers a blind retry, compensation or new Release
  sequence. Host reconciliation is allowed only after a trusted exact-original
  `mutation.reconcile` contract is published.

The N2 Setup Response that completes Establishment s10 belongs to the original
Establishment Owner operation and Run. It must not start Modify or Release. A
later N2 Modify Response for the Modify transaction is a separate native
continuation; it may confirm RAN acceptance, but it must not re-complete the MAS
invoke and must not be derived from `APPLIED`.

## Completion scopes

`APPLIED` is not RAN/UE acceptance. `PFCP_APPLIED` and `N1N2_DISPATCHED` are
Owner facts on this Operation; `RAN_MODIFICATION_CONFIRMED` requires the separate
N2 Modify Response and `TARGET_STATE_VERIFIED` requires an independent Owner
read. A Host that needs those scopes must record a separate, independent
observation. `ALREADY` is the Owner's authoritative exact-occurrence comparison,
not an independent post-modification read.

## Host and source blockers

The current OpenAMSM agent_step admission path rejects standard Nsmf business
Update / Release admission. A separate Owner-private binding and trusted
publication are required. Do not weaken that protocol gate or invent a public SBI
route in order to link these Skills.

The Host owns external URI ResourceMap tombstoning after the exact Release
lifecycle is settled. `lifecycle=RELEASING` is not a tombstone and is not
RELEASED.

Charging update/delete are optional without a source-defined applicability
predicate, so neither is included. The current adapter only writes or clears a
local charging marker and records `NOT_IMPL_skip`; it does not reserve or delete a
CHF resource. Compensation is `execute: skip`; no retry, compensation or replan
is imported.

Until the Owner publishes the exact callable profiles, MUTATION Effects,
input/output Schemas, Owner outcomes, commit receipts, Evidence Guarantees and
Owner identity, and until the Host-private bindings are fixed, both Skills remain
NOT_LINKABLE / NOT_QUALIFIED. Owner publication is still absent, so no live E2E
PASS is claimed for the CA-SL layer.
