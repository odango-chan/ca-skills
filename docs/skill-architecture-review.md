# ConnectionAgent Skill Architecture Review Standard

**Status:** Repository-wide review baseline for official ConnectionAgent Skills.  
**Applies to:** New Skills, source migrations, Procedure refactors, PR reviews and qualification-readiness reviews.  
**Authority:** This document is an authoring/review policy. It does not amend CA-SL v1alpha4 or override a trusted Owner contract. For 5GC Skills, it is supplemented by the 3GPP-first SMF Authoring Profile.

## 1. Review objective

Review a Skill as a business procedure, not as a collection of implementation calls. Establish independently that:

1. the business goal and supported profile are explicit;
2. each Procedure Node represents a coherent business action at the correct responsibility boundary;
3. Skill, Host, Runtime and Tool Owner responsibilities are not mixed;
4. every external fact and side effect has a trusted source and an explicit contract;
5. asynchronous, uncertain and concurrent execution can be handled without duplicating business actions;
6. the final Goal is proven by authoritative evidence; and
7. the source is consistent with the frozen language and is honestly classified by its actual validation level.

Passing YAML/source hygiene is not proof of 3GPP correctness, linkability, runtime correctness or qualification.

## 2. Business action and Node granularity

- A Skill expresses a stable business goal and its applicability profile.
- A Procedure expresses the business process needed to reach that goal.
- Each Node MUST have one primary business action. Avoid one Node per helper function, variable assignment, local mapping or internal implementation step.
- For 5GC Skills, author from the SMF point of view. A business Node SHOULD correspond to one logical 3GPP interaction or a tightly related Request/Response group, using the exact TS, Release, clause and step references. Do not mechanically create one Node per numbered standard step or per internal SBI call.
- A Node's primary action determines its identity and traceability. Its CA-SL stages do not create additional business actions.
- A separate CA Node is justified only by an independently meaningful business decision, governed CA action or explicit lifecycle/resource-responsibility boundary. Mark it CA_ADAPTER or CA_EXTENSION as appropriate and explain why it cannot be absorbed into the primary Owner action.
- A Node MUST NOT claim an action owned by another NF or external actor. For 5GC, AMF, (R)AN and UE actions must not be represented as SMF-owned Operations.
- Every 5GC Node MUST have a traceability entry and an adjacent source comment. Use 3GPP_NATIVE, CA_ADAPTER or CA_EXTENSION accurately; do not disguise CA behavior as a standardized NF operation.

## 3. Operation and Observation placement

Operation is the primary action stage of a business Node. Observation is an optional, read-only supplementary stage. They are distinct CA-SL stages and callable kinds, but normally belong to the same Node.

Required default:

1. Model the primary business action as the Node's Operation.
2. If a later business decision needs authoritative facts not already supplied by the Operation Result/Evidence, place the supplementary Observation in that same Node, after operation and before postcondition.
3. Let the Node's Postcondition evaluate the Operation Result and Observation Result together.
4. Do not create a separate Observation-only Node merely to query context for the preceding or following business action.
5. Do not repeat an Observation when the Operation Result/Evidence already supplies the required facts with adequate authority, scope and freshness.
6. An Observation is not a Wait, callback listener, polling loop, or substitute for an asynchronous Operation completion contract.

A standalone Observation-only Node is an exception, not the default. It requires a documented reason that the read itself is an independently meaningful business decision boundary and that no adjacent Operation Node can own it without misrepresenting the business flow. Classify it as a CA extension where appropriate. Do not use this exception to model Host admission or lifecycle checks.

For a required read before the first mutation, attach it to the earliest suitable read-only business Operation Node. The Observation executes after that read-only Operation and before the Node's Postcondition; it must still precede every session-creating or session-mutating Operation. Do not move a business eligibility decision into Host merely to avoid an Observation stage.

For the conventional initial PDU Session profile:

- the entry UE/PSI context-presence Observation belongs in the get-sm-subscription-data Node, after Nudm_SDM_Get and before its Postcondition; it gates the subsequent subscription/PCF/N4 mutation chain;
- the fresh post-Step-15 SM Context Observation belongs in the update-sm-context Node, after the asynchronous Owner Operation completes and before its Postcondition; it supplies current facts for the N4 Modification decision;
- neither read is a standalone Procedure Node, and neither read polls for callback completion.

## 4. Skill, Host, Runtime and Owner boundaries

| Responsibility | Owner |
|---|---|
| Business goal, applicability, business decisions and static Procedure graph | Skill |
| Invocation admission, business-instance correlation, deduplication and private transport obligations | Host |
| Procedure/Node progression, pending Action state, continuation and execution records | Runtime |
| Protocol transactions, authoritative network facts, callback matching, mutation receipts and Owner-side reconciliation | Tool Owner / Provider |
| Shared callable dispatch, trusted binding and authorization enforcement | Host / Runtime integration under the published contract |

Additional rules:

- Host Invocation lifecycle is not the network Session lifecycle.
- Host-owned instance IDs, ingress references, lifecycle references, response handles, request ledgers, callback tokens, waiter/hold/claim/journal identities and Runtime execution IDs MUST NOT become Skill Context fields or authored Operation arguments.
- The Skill may consume an opaque subject handle and explicit business request fields, plus declared Operation/Observation outputs.
- Network lifecycle facts remain with their authoritative network Owner. The Skill may read them only through an explicitly published, scoped READ callable when a business decision requires them.
- Do not duplicate Host admission, identity association, persistence or lifecycle checks as Skill Predicates.

## 5. Asynchronous messages and continuation

- A later inbound message that completes a pending business Operation MUST be correlated to that exact pending Operation and existing Invocation.
- It MUST NOT select a new Skill, create a second Invocation or restart the Procedure at start.
- Host owns ingress admission and private request/response continuity.
- The protocol Owner owns transaction/callback matching, deduplication, late/duplicate classification, final Operation Result and Evidence.
- Runtime owns pending Action/Node state and resumption of the same Invocation.
- Skill source declares the business Operation and consumes its eventual result. It does not declare author-level Wait/Await/Poll nodes, callback endpoints, transport handles or Host correlation metadata.
- Distinguish message arrival, Operation completion and Procedure completion. They are separate events.
- Define timeout, duplicate, stale, late, uncorrelated and indeterminate outcomes at the Host/Owner boundary. Do not guess paired protocol response behavior from Skill terminal labels.

## 6. Context, dataflow and Predicate rules

- Every Operation and Observation argument MUST have an explicit source.
- Reuse a previous Operation Result or Observation Result when it is authoritative and sufficient; do not re-query or copy it into a second implicit context.
- Predicate evaluators MUST be deterministic and side-effect free. They must not query external systems or read undeclared global Context.
- Script is for deterministic Skill-owned computation, validation or transformation. Do not use Script to reproduce a native NF action, Owner request preparation, protocol encoding, internal state lookup or trivial field remapping.
- Non-SMF facts needed by a 5GC action are acquired and validated inside the responsible Tool/Owner adapter; the Skill consumes only the declared result and Evidence.
- Keep the business request separate from Host-private execution metadata. Use the frozen Schema/Context ownership contract; do not invent aliases, fields or package exports.

## 7. Evidence, Scope and Observation semantics

- A returned JSON value is not automatically trusted Evidence.
- Evidence MUST identify the fact and authoritative source, bind the exact subject and business resource (for example UE/PSI), bind the relevant Invocation/Operation occurrence where required, and satisfy the published temporal/freshness guarantee.
- Never substitute Host receive time for source observation time or invent a validity interval.
- Keep ABSENT, PRESENT, unavailable projection data and UNKNOWN distinct. A successful query that reports an unavailable projection is not proof of absence. Timeout, transport failure, authorization failure and malformed response are not ABSENT.
- A negative result can authorize only the exact business branch that its trusted Evidence and freshness contract support.
- Evidence from another UE, PSI, Invocation, lifecycle or Operation occurrence MUST NOT be reused.
- Do not fan out over every available projection. Read only the exact facts required by the next business decision.

## 8. Mutation, idempotency and recovery

- Distinguish READ from MUTATION and verify the published Effect.
- Identify the exact mutation target, subject, resource and operation occurrence.
- A successful transport response is not automatically proof of the business effect or final Goal.
- OUTCOME_UNKNOWN MUST NOT trigger blind retry, a new mutation or author-authored cleanup.
- Reconciliation is an Owner/Host safety-boundary responsibility over the exact original mutation; it is not a new Skill business action.
- Cleanup or resource-responsibility transfer is permitted only when the original mutation outcome and ownership are sufficiently established by trusted evidence.
- Define duplicate requests, competing creates, idempotency and stale/late callbacks. A point-in-time ABSENT read is not a lock and does not guarantee that the resource remains absent at a later mutation.

## 9. Goal and terminal proof

- Keep Predicate results, Operation outcomes, Procedure terminal outcomes and business Goal proof distinct.
- PASS, FAIL and UNKNOWN are not interchangeable with SUCCEEDED, FAILED, COMMITTED, NOT_COMMITTED or OUTCOME_UNKNOWN.
- Do not infer completion from an intermediate response, acknowledgement, accepted request or committed mutation when later network state is required.
- The final Goal MUST be proved by the final Postcondition aggregate using authoritative, current, same-scope Evidence.
- Do not carry a prior Node's PASS as proof for the final Goal. Reuse the underlying typed result only where its scope and freshness remain valid.
- Every terminal path must have a defined business meaning and retain any unresolved resource/protocol responsibility.

## 10. Contracts, capabilities and implementation isolation

- Use exact trusted ToolCatalog callable identities and exact trusted CapabilityContracts exports.
- A Capability is an authorization grant, not a Tool ID or a 3GPP operation name.
- Never invent an Owner, Tool, Capability, Schema, Evidence Descriptor, Guarantee or Scope policy to make a Skill appear linkable.
- urn:example placeholders are design-only and MUST remain explicitly NOT_QUALIFIED.
- Owner adapters may implement request construction, protocol conversion, local NF processing, internal context reads, pre-dispatch guards and transport details. Do not expose those implementation helpers as extra Skill Nodes unless they are independent business actions.
- Keep traditional 5GC business modeling separate from implementation-specific decompositions such as OpenAMSM internals. Implementation-specific examples must be clearly labeled and must not leak into the conventional 3GPP Skill.

## 11. Review severity and exit criteria

### P0 — architecture correctness (must pass)

- Incorrect 3GPP/NF responsibility mapping or missing primary business interaction.
- Skill/Host/Runtime/Owner boundary violation.
- New Skill/Invocation or graph restart for a callback that belongs to a pending Operation.
- Host lifecycle/correlation internals exposed to Skill.
- Duplicate or unsafe mutation, blind retry after OUTCOME_UNKNOWN, or lost resource/protocol responsibility.
- False Goal success or use of untrusted/out-of-scope Evidence.

### P1 — contract and execution correctness (must pass)

- Incorrect Operation/Observation placement or unnecessary standalone Observation Node.
- Missing/ambiguous arguments, Schema, Tool, Capability, Effect or Owner binding.
- Missing Evidence Scope, source authority, freshness or Invocation/Occurrence binding.
- Incomplete route handling for FAILED, DENIED, UNKNOWN, OUTCOME_UNKNOWN and other published outcomes.
- Unhandled duplicate, concurrent, stale, late or unavailable-context behavior.
- Missing 3GPP traceability or unqualified placeholder presented as published.

### P2 — design quality (should be resolved or explicitly accepted)

- Redundant Node, Predicate, Script, Observation, Schema or data copy.
- Implementation-oriented naming where a business/3GPP name exists.
- Duplicated logic that belongs in an Owner adapter.
- Unclear applicability, optional-step rationale, comments or traceability.
- Missing regression coverage for a known design invariant.

A review may close only when all P0 and P1 findings are resolved or explicitly accepted by the responsible owner. P2 findings may remain with a documented rationale.

## 12. Required review report

Every review must state separately:

1. Business / 3GPP conformance: source clauses, participating NF responsibilities and supported profile.
2. Architecture conformance: Skill, Host, Runtime and Owner boundary; Node granularity; Observation placement; asynchronous continuation.
3. Contract / linkability: exact Tool, Capability, Schema, Evidence and Scope publication status.
4. Source validation: exact commit and tests actually run.
5. Qualification status: Compiler, Linker, Runtime, Host, native/WASM and live-network evidence, each reported only when actually available.

Use explicit statuses such as PASS, FAIL, NOT_RUN, NOT_VERIFIED, NOT_PUBLISHED and NOT_QUALIFIED. A runner-allocation failure is NOT_VERIFIED, not a source test failure. Never promote source hygiene into compile, link, runtime or live qualification.
