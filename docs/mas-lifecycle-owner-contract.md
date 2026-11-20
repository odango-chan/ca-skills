# MAS Modify / Release Owner outcome contract

**Status: REQUIRED CONTRACT / NOT PUBLISHED / NOT_QUALIFIED.** This document defines the minimum Owner and Host contract required to link the two source-aligned Procedures. It does not assert that ca-client-tools, OpenAMSM or Generic Host already implements it.

## Effect and callable identity

Every callable occurrence used by these Procedures is a candidate `MUTATION`, including the local CA charging markers and the local SE event record. The Skill cannot declare or override Effect; the trusted ToolCatalog and deployment CapabilityContracts must publish it.

The Owner must bind each invocation to all of:

- immutable original Invocation / Mutation identity;
- exact callable ID and private OES `stepId` occurrence;
- exact SUPI and PSI;
- private session generation and correlation;
- authenticated deployment / Owner identity;
- canonical input digest and the exact output Schema branch.

The Host / Owner maps Procedure node IDs `m0/m2/m3/m4/m5` and `r1/r2/r3/r4/r5/r6` to the pinned OES step IDs. A callable ID alone is not an occurrence identity. `sessionRef`, `smContextRef`, `stepId`, idempotency keys, generation IDs and orchestration credentials remain private and must never appear in Skill Request Schemas or Operation arguments.

## Required Owner outcomes

| Outcome | Required meaning | Procedure treatment |
| --- | --- | --- |
| `SUCCEEDED` | The exact original call is proven `COMMITTED`; its complete declared output Schema and required Evidence are available for that occurrence and Scope. | Advance to the Node Postcondition. |
| `FAILED` | Owner proves `NOT_COMMITTED` and proves no residual side effect for a published deterministic failure class. | First operation may stop as `FAILED`; after earlier committed steps, stop as `SAFE_STOPPED`. |
| `NOT_COMMITTED` | Owner provides a trusted receipt proving the exact original call did not commit. This category must be explicitly published; absence of a success response is not proof. | First operation may stop as `FAILED`; after earlier committed steps, stop as `SAFE_STOPPED`. No automatic retry. |
| `OUTCOME_UNKNOWN` | Commit state or callback disposition cannot be proven, including timeout, restart, missing receipt, stale or mismatched callback. | `SAFE_STOPPED`; preserve original responsibility. |
| `COMMITTED` | Host has verified commit but cannot recover the complete original public output / Evidence required by the Procedure. This is a Runtime outcome, not an Owner success. | `SAFE_STOPPED`; never infer Goal from commit alone. |
| `DENIED` | Host rejects authorization / Scope before dispatch; Owner was not invoked. | First operation may stop as `FAILED`; after earlier committed steps, `SAFE_STOPPED`. |

An Owner must not report `FAILED` for a timeout, generic HTTP error, process restart, missing receipt or unknown side effect. Those remain `OUTCOME_UNKNOWN`. A raw HTTP 2xx or MAS `status: OK` is not a commit receipt.

## Commit receipt and Evidence

Each Mutation ToolCatalog export must publish a root-closed receipt Schema with at least the exact original invocation binding and commit state (`COMMITTED` / `NOT_COMMITTED`). The trusted CapabilityContracts must publish the exact callable Effect and Scope. Each Evidence Guarantee must bind the exact callable, original invocation, private OES occurrence, SUPI, PSI, generation, observed time and complete normalized public output.

The candidate Evidence Guarantees referenced by the Procedures are:

- Modify: `mas::sc.context-updated`, `mas::ca.charging-marker-updated`, `mas::upn.modify-intent-applied`, `mas::ssm.modify-an-tunnel-ready`, and the existing candidate `mas::upn.n3-synchronized`.
- Release: `mas::ca.charging-marker-cleared`, `mas::upn.up-session-released`, `mas::ssm.release-signal-settled`, `mas::pa.policy-association-released`, `mas::sc.context-release-committed`, and `mas::se.release-event-recorded`.

None of these candidate guarantees is a trusted published export at this time. In particular:

- the charging guarantees prove only the pinned local marker, never a CHF resource;
- the SSM Release guarantee must prove either that signaling was not required for the exact trigger or that the matching AMF confirmation completed;
- the PA Release guarantee must distinguish `DELETED` from a verified `NOT_PRESENT` association;
- the r6 event guarantee proves a local event record only, not a 3GPP Status Notify.

## Duplicate, generation, callback and UE isolation

- **Duplicate original invocation:** return the original settled result and receipt. Never dispatch a second mutation for the same original invocation.
- **Different invocation:** do not treat an already-present session value as proof that the new mutation committed.
- **Wrong generation:** reject a receipt or callback whose private generation differs from the registered original occurrence. Do not advance the Procedure.
- **Late callback:** attach it only to the original pending occurrence and its retained responsibility. It must not resume a completed, cancelled or newer Run.
- **Mixed UE:** bind evidence and callback to exact SUPI + PSI + generation. The same PSI on another SUPI must never satisfy the original Predicate.
- **Unknown outcome:** the Host may use only a trusted exact-original `mutation.reconcile` READ if its Owner contract, authorization, budget and deadline permit it. Reconcile is Host / Owner behavior, not an authored Procedure node. No blind retry, compensation or replan is allowed.

## Protocol and deployment blockers

The current OpenAMSM `agent_step` path rejects standard Nsmf business Update / Release admission. A separate Owner-private binding and its publication are required. Do not weaken or bypass that protocol gate to make these examples appear executable.

For Release, the Host must classify the authenticated ingress and the Owner adapter must map the symbolic trigger to the exact numeric constant from the pinned source. This mapping is not yet published. A symbolic string must not reach the source's numeric trigger parser unchanged.

The Host owns external URI ResourceMap tombstoning after the exact Release lifecycle is settled. This is not a Skill Operation or a Predicate over `lifecycle="RELEASING"`.

Until the Owner receipts, Schemas, Evidence Guarantees, Owner identity, trigger mapping and deployment CapabilityContracts are published and independently tested, both Skills remain **NOT_LINKABLE / NOT_QUALIFIED**.
