# CA-SL Next Revision Design: Node-Level Event Wait

**Status:** Design proposal for the language revision after CA-SL v1alpha4.  
**Normative status:** Not frozen; this document does not amend CA-SL v1alpha4.  
**Scope:** Procedure Node entry control, inbound event binding, typed dataflow, timeout routing and Host/Runtime continuation.  
**Decision direction:** Node-level Wait with transition-level semantics; reuse the existing Procedure Graph and `routes` model.

## 1. Problem and design objective

CA-SL v1alpha4 deliberately has no author-level `wait`, `await` or polling node (§21). Its current asynchronous model assigns completion to a pending Tool/Provider/SMF Operation. That rule remains authoritative for v1alpha4.

A future language revision needs to express a different interaction pattern: an external NF initiates a later request to the SMF, the Host receives and correlates that request to an existing Run, and the Agent then executes the business Operation of the target Procedure Node using the validated inbound request.

This is not a request for a second graph, a fifth business stage, or a polling language. The design objective is to express the event gate using the existing Node and routing model.

## 2. Core decision

**Wait is an optional Node-entry control. It is not a Node and is not a business stage.**

A Node may contain:

1. optional `wait` entry control;
2. the existing business stages, in their existing order: `precondition`, `operation`, `observation`, `postcondition`;
3. the existing stage-level `routes`.

The four business stages retain their current meanings and ordering. Wait is evaluated before the first declared business stage. When the expected event is accepted, the Runtime enters that first stage. If the event does not arrive before the deadline, the Wait control outcome is routed through `wait.routes`.

A Wait Node is still a business Node: it must contain at least one of the existing business stages. Wait-only Nodes are not introduced. An Operation is not mandatory merely because a Node has Wait; the author declares the business stages actually needed after the event. Where the inbound request is processed by an existing logical Operation, put the Wait on that Operation's target Node rather than creating a synthetic receive Operation.

This preserves the v1alpha4 concepts of `start`, `nodes`, the four stages, explicit `arguments`, and a single static Procedure Graph.

## 3. Author syntax

Illustrative syntax for 3GPP TS 23.502 Step 15:

```yaml
start: transfer-n1n2-message

nodes:
  transfer-n1n2-message:
    operation:
      tool: <trusted-transfer-operation>
      arguments:
        ...
      routes:
        SUCCEEDED: update-sm-context
        FAILED: SAFE_STOPPED

  update-sm-context:
    wait:
      event:
        source: AMF
        service: Nsmf_PDUSession
        operation: UpdateSMContext
      timeout: PT30S
      routes:
        TIMEOUT: handle-update-timeout

    precondition:
      predicates:
        - predicate: establishment.update_request.valid
          arguments:
            - update-sm-context.wait.output

    operation:
      tool: <trusted-logical-smf-update-operation>
      arguments:
        request: update-sm-context.wait.output
      routes:
        SUCCEEDED: modify-n4-session
        FAILED: SAFE_STOPPED

  handle-update-timeout:
    operation:
      tool: <trusted-timeout-handling-operation>
      arguments: {}
      routes:
        SUCCEEDED: verify-timeout-state
        FAILED: UNRESOLVED
```

The callable IDs above are placeholders, not claims that corresponding Owner exports have been published. The `request` argument is illustrative; actual Operation argument names and paths must match the linked Owner Input Schema. The example does not define a new 3GPP API or change the semantics of Step 15.

### 3.1 Wait fields

The proposed Wait shape is:

- `event`: exact inbound interface identity, using canonical NF/service/operation names;
- `timeout`: required maximum active waiting duration;
- `routes`: required timeout route mapping.

The event identity is not an arbitrary event label. For the 5GC example it identifies the AMF-originated `Nsmf_PDUSession.UpdateSMContext` request. The exact API version and request contract are pinned by the trusted dependency/Host ingress contract, not guessed from a name or selected dynamically at runtime.

### 3.2 One route model, one scoped outcome

There is no `onTimeout` field. The timeout route uses the existing `routes` shape and the existing route-target rules:

```yaml
wait:
  ...
  routes:
    TIMEOUT: handle-update-timeout
```

The key domain is specific to Wait:

- `TIMEOUT` is the only author-declared Wait route key;
- `EVENT_RECEIVED` is the normal Wait completion and proceeds implicitly to the Node's first business stage; it does not need an explicit route;
- `TIMEOUT` is a Wait control outcome, not a Predicate Outcome and not an Operation Outcome. It is not `PASS`, `FAIL`, `UNKNOWN`, `FAILED` or `OUTCOME_UNKNOWN`.

The structure of `routes` and its target values is reused, but its key domain is scoped to the Wait control. It does not extend the §22 Stage Outcome set.

The `TIMEOUT` route is mandatory. It must target another Node or a stopping Invocation terminal (`FAILED`, `UNRESOLVED` or `SAFE_STOPPED`). It MUST NOT target `SUCCEEDED`: a timeout cannot prove the business Goal, and only a final Postcondition aggregate PASS may request `SUCCEEDED`.

If the timeout needs business-state inspection or resource handling, route to a dedicated existing-style business Node. Do not infer failure merely from the absence of a message.

## 4. Schema ownership and unification

**Do not add `payloadSchema` to Skill-authored Wait.** Do not add an independent EventCatalog solely to support Wait.

CA-SL already has a consistent Schema ownership model:

| Data producer / consumer | Schema authority | Skill-side binding |
|---|---|---|
| Tool Operation | Trusted ToolCatalog Owner: `inputSchema` and `outputSchema` | `operation.tool` and `operation.arguments` |
| Observation | Trusted ToolCatalog Owner: `queryContextSchema` and `outputSchema` | `observation.tool` and `observation.arguments` |
| Predicate | Skill PredicateSet: declared `parameters` | `predicates[].arguments` |
| Invocation Host Context | Trusted Host Context Schema | `context.xxx` |
| Skill Request | Skill-owned `requestSchema` | `context.request.xxx` |
| Inbound Wait message | Trusted 3GPP API request contract, resolved through the Host's published ingress contract | `node.wait.output` |

The Skill identifies the inbound interface operation; it does not restate the request-body Schema. The exact request Schema is resolved from the trusted, version-pinned 3GPP API contract exposed through the Host's public ingress contract. That contract binds the canonical source NF, service operation and API version to one request-body Schema. It is a Host/interface contract, not a new author-facing EventCatalog and not a per-Skill Schema declaration.

The Host ingress contract must make this binding deterministic. If the interface identity has no trusted request Schema, resolves to more than one Schema, uses an unsupported Schema dialect, or cannot be linked to the selected dependency snapshot, compilation/admission fails closed. The compiler must not select a similarly named Schema or infer one from the inbound JSON.

For CA-SL static typing, the trusted request-body Schema must be available in the supported Schema dialect (currently JSON Schema Draft 2020-12 under the language's supported subset). If the source 3GPP OpenAPI artifact needs normalization to that subset, the normalized Schema is a trusted Host/dependency export and must retain traceability to the exact API operation and version. The Skill does not own or copy that normalized Schema.

The Host validates the authenticated inbound request against this Schema before exposing it. `wait.output` is the validated, normalized request-body object—not a transport envelope. Headers, callback tokens, Host correlation keys, ingress/lifecycle references and other Host-private metadata remain private and are not implicitly included.

A valid request payload is not automatically Evidence that the requested network action succeeded. It is typed input data for the target Node. Business facts and final Goal still require the existing Owner Output/Evidence and Predicate rules.

## 5. Wait output and SourcePath

The future SourcePath grammar adds Wait as a typed Producer source:

```ebnf
ProducerOutputPath = NodeId, ".", ProducerSource, ".output", { ".", Identifier } ;
ProducerSource     = "operation" | "observation" | "wait" ;
```

Examples:

- `update-sm-context.wait.output`
- `update-sm-context.wait.output.n2SmInfo` (only if that property exists in the trusted request Schema)
- `update-sm-context.wait.output.ueEpsPdnConnection` (only if that property exists in the trusted request Schema)

The exact field names are determined by the pinned API request Schema; these examples do not assert particular fields are required by every profile.

The Wait output becomes available only after the Host has accepted and correlated the event for this Wait occurrence. It may be consumed by:

- the same Node's Precondition, because Wait completes before the first business stage;
- the same Node's Operation, Observation and Postcondition, subject to ordinary Schema/type checks;
- downstream Nodes on paths where the event-received branch has been taken.

It is unavailable on the timeout branch and before event acceptance. Compiler path analysis must reject any reference that is not available on every path reaching the consumer. A timeout handler must not read the timed-out Wait's `wait.output`.

The Wait output is an explicit Producer value. It is not injected into global Context, is not an Operation Result, is not an Observation Result, and does not replace Evidence.

## 6. Execution and Host/Runtime responsibilities

### 6.1 Registration and activation

To avoid losing an event that arrives immediately after a triggering outbound Operation, Host/Runtime must arm the expected target Wait before dispatching the predecessor Operation that can cause the inbound request.

Arming is registration only:

- it does not enter the target Node;
- it does not start the Wait timeout;
- it does not make `wait.output` available;
- it does not cause the target Node's business stages to execute.

If an event arrives after arming but before the target Node is selected, Host durably buffers the validated event for the exact Run and target Wait occurrence. When the selected route activates the target Node, Runtime consumes the buffered event and proceeds to the first business stage. The timeout clock starts only when that Wait is activated, not when it is armed.

If the predecessor chooses a different route, any unselected candidate Wait registration is invalidated and cannot consume the event as though its Node had been selected.

### 6.2 Inbound validation and correlation

Host owns:

- authenticating and authorizing the inbound NF/source;
- resolving the exact service operation and API version;
- validating the request body against the trusted request Schema;
- correlating the request to the exact existing Run, target Node/Wait occurrence and business resource;
- deduplicating repeated delivery and durably buffering early arrivals;
- retaining any paired protocol response obligation privately.

Correlation must be exact across the relevant subject, session/resource, lifecycle and triggering business occurrence. Host-private correlation and transport identifiers MUST NOT become Skill Context fields or authored Operation arguments. A request that cannot be uniquely correlated is rejected or quarantined under the Host ingress contract; it must not create a new Invocation or be broadcast to candidate Runs.

Runtime owns the Run's active Node, Wait activation, timeout clock, continuation and execution trace. On event acceptance, Runtime resumes the same Run at the target Node. The Agent then executes that Node's declared business stages. The event is not a new Skill selection, a second Invocation, a restart from `start`, or a completion result fabricated on behalf of a pending Owner Operation.

The Tool Owner still owns the actual behavior, external side effects, normalized Operation Result and Evidence of its callable. It does not own the Host's inbound Run correlation merely because the request belongs to its protocol domain.

### 6.3 Race, duplicate, timeout and recovery

- Event acceptance and Wait timeout are an atomic race. Exactly one may win for a given Wait occurrence.
- A duplicate delivery of the accepted event is idempotently recognized; it cannot execute the Node twice.
- Once timeout wins, that Wait occurrence is closed. A later event cannot revive the old Run or reopen its `wait.output`.
- Wait identity includes a per-Run occurrence/generation maintained privately by Host/Runtime. A late event for an expired generation cannot satisfy a later Wait with the same 3GPP operation identity.
- Event receipt, Wait activation, selected route, timeout, duplicate/late classification and continuation must be durably traceable across Host/Runtime restart.
- If the event and timeout race during recovery, the durable atomic winner is authoritative; recovery must not accept both.

## 7. Duration and budget semantics

`timeout` uses a restricted, fixed-duration ISO 8601 representation. Examples:

| Value | Meaning |
|---|---|
| `PT30S` | 30 seconds |
| `PT1M` | 1 minute |
| `PT5M` | 5 minutes |
| `PT2H` | 2 hours |
| `P1D` | 1 day |

The language should accept positive fixed durations and reject calendar years/months (for example `P1Y` and `P1M`), zero/negative values and malformed durations. The exact maximum and any fractional-second policy must be frozen with the Runtime deadline contract. The example `PT30S` is illustrative only; it is not a 3GPP-mandated timeout.

The timer begins at Wait activation. Host/Deployment may impose a stricter maximum; the effective wait must not exceed the remaining Invocation deadline. A global Runtime deadline or cancellation remains a Runtime stop condition and is not rewritten as the author's Wait `TIMEOUT` route.

Wait itself does not dispatch a Tool or Script and therefore does not consume the existing Tool/Script Action Budget. It does consume wall-clock time and remains subject to Host/Runtime execution and Node limits.

## 8. Procedure Graph and static validation

The compiler models Wait as an entry-control vertex before the Node's first business stage. It adds:

- an implicit normal `EVENT_RECEIVED` edge from the Wait gate to the Node's first declared business stage;
- the explicit `TIMEOUT` edge from `wait.routes.TIMEOUT` to its selected Node or stopping terminal.

These are control-flow edges, not new business stages. The Wait gate does not produce Predicate PASS/FAIL/UNKNOWN and does not create an Operation/Observation Action.

Static analysis must include both Wait edges in reachability, cycle detection, path-sensitive SourcePath availability, global Precondition pass-through, terminal reachability and final-Postcondition proof checks. The only route to `SUCCEEDED` remains a reachable final Postcondition aggregate PASS directly targeting `SUCCEEDED`. The timeout edge can never provide Goal proof.

If multiple incoming paths converge on a Node with Wait, every path must be compatible with the same exact inbound interface identity and trusted request Schema, and Host must be able to correlate the event to the selected Run/Wait occurrence on every path. If different events or incompatible correlation contracts are required, authors must use distinct target Nodes and converge later through the existing DAG. Runtime does not wait for multiple incoming paths or join concurrent branches.

A Node with Wait must still satisfy the existing requirement to declare at least one business stage. The Node's stage order and same-Node normal progression remain unchanged after the event is accepted.

## 9. 5GC Step 15 mapping

For the conventional SMF-owned initial PDU Session flow, the future-revision mapping is:

1. Step 11 `Namf_Communication_N1N2MessageTransfer` is the outbound Operation.
2. Before dispatching Step 11, Host/Runtime arms the expected Step 15 Wait for the same Run.
3. AMF later sends `Nsmf_PDUSession_UpdateSMContext Request`.
4. Host authenticates, validates and correlates that request to the exact existing Run and `update-sm-context` Wait.
5. Runtime resumes the same Run at `update-sm-context`; `update-sm-context.wait.output` is the validated inbound request body.
6. The Agent executes the `update-sm-context` Node's declared logical SMF Operation using that explicit input. A supplementary SMF Context Observation, if needed, remains in the same Node after Operation and before Postcondition.
7. The Postcondition checks the appropriate RAN adoption and SMF business facts; a successful route proceeds to N4 Session Modification.
8. The paired Step 17 `Nsmf_PDUSession_UpdateSMContext Response` obligation remains Host-private and is fulfilled according to the trusted interface/response contract after the required downstream business work reaches its defined outcome.

This is a conventional 3GPP-facing model. It must not expose OpenAMSM/MAS internal module names or imply that AMF/(R)AN/UE actions are SMF-owned Operations. Exact Tool IDs, input/output Schemas, Evidence and response obligations must come from trusted Owner/Host publications; illustrative IDs are not implementation claims.

## 10. v1alpha4 compatibility boundary

CA-SL v1alpha4 remains frozen and unchanged:

- v1alpha4 §21 continues to prohibit author-level Wait/Await/Poll.
- Existing v1alpha4 Skills and examples must continue to use the v1alpha4 pending-Operation contract; they must not add the proposed `wait` field or `wait.output` SourcePath.
- This proposal does not authorize changing the current v1alpha4 grammar, diagnostics, Compiler, Studio/LSP, Runtime or Host implementation.
- The next language version and its exact version identifier are not assigned by this design note. The feature requires an explicit versioned revision and independent review.

## 11. Normative change inventory for the future revision

| Current v1alpha4 area | Required future-revision work |
|---|---|
| §10.1 structure grammar | Add optional Node-level `wait` and its exact field grammar |
| §12.1 Node execution | Define Wait as pre-stage entry control; retain four business stages |
| §12.9 control-flow proof | Include Wait activation and timeout edges in DAG/path-sensitive checks |
| §13.2–§13.3 SourcePath | Add typed `NodeId.wait.output`, availability and schema-assignability rules |
| §19 Invocation lifecycle | Define Run suspension/resumption and durable Wait occurrence |
| §21 asynchronous semantics | Replace the blanket no-author-Wait rule for the new version with the declarative Node-entry model |
| §22 routes | Define the Wait-scoped `TIMEOUT` key and reuse existing route targets |
| §24 / Annex H | Add static and runtime diagnostics for event binding, Schema resolution, timeout routes and unavailable Wait output |
| Schema/Host contract annexes | Define the trusted inbound interface-to-request-Schema binding and its version/identity rules |

The revision must not add a fifth business stage, a Wait Node kind, a new Outcome family for business stages, `onTimeout`, `payloadSchema`, an author-facing EventCatalog, or a second Procedure Graph.

## 12. Review and acceptance checklist

Before this design can be frozen into a language revision, independent review must confirm:

- [ ] the exact grammar and whether all Wait fields are required;
- [ ] the trusted Host ingress contract shape and exact mapping from 3GPP service operation/API version to request Schema;
- [ ] the supported duration lexical subset, maximum and precedence against global deadlines;
- [ ] mandatory `wait.routes.TIMEOUT` and permitted stopping terminals;
- [ ] same-Node and downstream `wait.output` typing and path-sensitive availability;
- [ ] early-event arming, durable buffering and cancellation of unselected candidate registrations;
- [ ] exact correlation across concurrent UE/PSI/Invocation occurrences;
- [ ] atomic event-versus-timeout behavior and late/duplicate event handling after restart;
- [ ] interaction with global Precondition, Action Budget, Node limits, cancellation and final Goal proof;
- [ ] Step 15/17 response obligation ownership and failure mapping;
- [ ] diagnostics, trace semantics and positive/negative conformance fixtures.

No implementation or product-conformance claim follows from this design document alone.
