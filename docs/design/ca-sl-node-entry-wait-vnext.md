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

**Wait is an optional Node-entry control. It is not a Node kind and is not a business stage.**

A Node may contain:

1. optional `wait` entry control;
2. the existing business stages, in their existing order: `precondition`, `operation`, `observation`, `postcondition`;
3. the existing stage-level `routes`.

The four business stages retain their current meanings and ordering. Wait is evaluated before the first declared business stage. When the expected event is accepted, the Runtime enters that first stage. If the event does not arrive before the deadline, the Wait control outcome is routed through `wait.routes`.

A Node with Wait is still a business Node: it must contain at least one of the existing business stages. Wait-only Nodes are not introduced. An Operation is not mandatory merely because a Node has Wait; the author declares the business stages actually needed after the event. In the 5GC Step 15 case, the target Node contains the logical SMF Operation that processes the received UpdateSMContext request. A supplementary Observation, if needed, remains after that Operation and before the same Node's Postcondition.

This preserves `start`, `nodes`, the four business stages, explicit arguments and one static Procedure Graph.

### 2.1 Event Wait is not Runtime Evidence Wait

The existing Generic Agent Host's `BoundedEvidenceWaiter` is an Observation-based bounded acquisition loop: it repeatedly asks an ObservationSource for a declared fact under freshness, scope, correlation, deadline and observation-budget controls. That mechanism is not an inbound-event listener and MUST NOT be repurposed to poll for an AMF request.

The proposed Event Wait is push-driven ingress plus continuation of an existing Run. It does not call an ObservationSource, does not create Evidence, and does not turn message arrival into a Predicate verdict. The two mechanisms may share generic deadline/cancellation utilities, but their data source, lifecycle, result and proof semantics remain distinct.

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
      response:
        after: modify-n4-session
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

  modify-n4-session:
    operation:
      tool: <trusted-n4-session-modification-operation>
      arguments:
        request: update-sm-context.operation.output
      routes:
        SUCCEEDED: <next-business-node>
        FAILED: SAFE_STOPPED

  handle-update-timeout:
    operation:
      tool: <trusted-timeout-handling-operation>
      arguments: {}
      routes:
        SUCCEEDED: SAFE_STOPPED
        FAILED: UNRESOLVED
```

The callable IDs above are placeholders, not claims that corresponding Owner exports have been published. The `request` argument is illustrative; actual Operation argument names and paths must match the linked Owner Input Schema. The example does not define a new 3GPP API or change the semantics of Step 15.

### 3.1 Wait fields and event identity

The proposed Wait shape is:

- `event`: exact inbound interface identity, using canonical source NF type, service name and service-operation name;
- `timeout`: required maximum time the activated Node may wait for that event;
- `response`: optional protocol-response boundary binding, required by an Integration export when a paired response must wait beyond the Wait-bearing Node;
- `routes`: required timeout route mapping.

`event.source` means the authenticated peer NF type, not an untrusted body field. The event identity is not an arbitrary label. For the 5GC example it identifies the AMF-originated `Nsmf_PDUSession.UpdateSMContext` service operation. The exact API artifact, API version, OpenAPI operation, media types and request Schema are pinned by the declared Integration dependency; they are not guessed from a name or negotiated dynamically at runtime.

The event selector does not itself identify a Run. A trusted Integration ingress contract must provide a deterministic correlation binding from the protocol request to exactly one armed Wait occurrence. That binding is Integration-owned and Host-private; Skill source does not declare `ueRef`, callback tokens, operation handles or correlation keys. If the binding cannot produce one unique match, the event is rejected or quarantined rather than assigned to the newest or most convenient Run. The binding must also distinguish successive Wait generations for the same protocol resource; a Host-generated generation number that is absent from the inbound request is not, by itself, a valid discriminator.

### 3.3 Paired response boundary

An inbound request may carry a protocol response obligation. The Integration Ingress Operation export defines the response Schema, allowed protocol outcomes, wire encoding and mapping from the Runtime's declared response-boundary result. The Host retains the durable response-obligation record; Runtime does not choose an HTTP status or serialize the protocol response.

The proposed optional binding is:

```yaml
wait:
  response:
    after: modify-n4-session
```

`response.after` names a Node whose completion (including its declared Postcondition) is the response boundary. If omitted, the boundary is the completion of the Wait-bearing Node. The Compiler must prove that every normal event-accepted path reaches the boundary; a path that terminates earlier must have a trusted Integration failure-response mapping. The response boundary is not the terminal Run: later Procedure work may continue after the paired protocol response has been delivered.

For 3GPP Step 15/17, the boundary must be after the required Step 16 N4 Session Modification. In the illustrative graph above, `modify-n4-session` is therefore the response boundary. The Step 17 response must not wait for unrelated later Procedure work. `response.after` is protocol-continuation metadata, not a fifth business stage or a new Node kind.

### 3.2 One route model, one scoped outcome

There is no `onTimeout` field. The timeout route uses the existing `routes` shape and route-target rules:

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

**Do not add `payloadSchema` to Skill-authored Wait. Do not add a global or author-facing EventCatalog.**

CA-SL already has a consistent Schema ownership model. The inbound event follows the same trusted dependency/export principle, but its contract is owned by the Integration that implements the protocol ingress:

| Data producer / consumer | Schema authority | Skill-side binding |
|---|---|---|
| Tool Operation | Trusted ToolCatalog Owner: `inputSchema` and `outputSchema` | `operation.tool` and `operation.arguments` |
| Observation | Trusted ToolCatalog Owner: `queryContextSchema` and `outputSchema` | `observation.tool` and `observation.arguments` |
| Predicate | Skill PredicateSet: declared `parameters` | `predicates[].arguments` |
| Invocation Host Context | Trusted Host Context Schema | `context.xxx` |
| Skill Request | Skill-owned `requestSchema` | `context.request.xxx` |
| Inbound Wait event | Trusted Integration Ingress Operation export in a declared dependency snapshot | `node.wait.event`; `node.wait.output` is typed by its normalized request Schema |

The Integration package publishes an exact Ingress Operation contract as one of its trusted exports. This is not a second global catalog. At minimum, the export binds:

- canonical peer/source NF type, 3GPP service name and service-operation name;
- exact source specification and OpenAPI artifact identity/digest, API URI version, HTTP method, path template and OpenAPI `operationId`;
- accepted wire media types and their source request Schema references;
- a normalized request Schema in the CA-SL supported JSON Schema subset, plus the traceable normalization mapping;
- the deterministic correlation rule used both when arming a Wait and when receiving the inbound request;
- the paired response contract, response outcome/body mapping and protocol-specific response obligation lifecycle.

The Skill identifies the inbound interface operation; it does not restate the request Schema. The Compiler resolves the event selector against exact Ingress Operation exports in the Skill's declared, version-pinned dependency snapshots. Resolution must produce exactly one export. Zero matches, multiple matches, unsupported Schema dialects, digest mismatch or missing correlation/response bindings fail closed. When the Integration declares a paired response, the Compiler also resolves `response.after` (or the default Wait-bearing Node boundary) and proves that all normal event-accepted paths reach it. The Compiler must not choose a similarly named Schema or infer a contract from an inbound JSON body.

The Integration ingress adapter owns protocol-specific source authentication, wire parsing, validation and normalization. The Generic Host consumes the adapter's normalized delivery and verifies its trusted contract identity; it does not parse 3GPP paths, media types or NF authentication. The Runtime uses the normalized request Schema for ordinary typed Producer/Consumer checking.

If an OpenAPI request uses multipart media types or binary parts, the Integration contract must define their normalized representation. Binary parts may be represented by typed, immutable content references only when the Integration contract publishes and authorizes that representation. Unsupported parts MUST NOT be silently dropped or guessed. The Skill does not copy the source OpenAPI Schema or the normalized Schema into its own package.

A valid request payload is not automatically Evidence that the requested network action succeeded. It is typed input data for the target Node. Business facts and final Goal still require the existing Owner Output/Evidence and Predicate rules.

## 5. Wait output and SourcePath

The future SourcePath grammar adds Wait as a typed Producer source:

```ebnf
ProducerOutputPath = NodeId, ".", ProducerSource, ".output", { ".", Identifier } ;
ProducerSource     = "operation" | "observation" | "wait" ;
```

Examples:

- `update-sm-context.wait.output`
- `update-sm-context.wait.output.smContextRef` (only if the Integration's normalized request Schema exports that property)
- `update-sm-context.wait.output.n2SmInfo` (only if that property exists in the normalized request Schema)

`wait.output` is the Integration contract's normalized request value. It is not necessarily the raw HTTP body: it may include path/query parameters and normalized body parts when the contract declares them. A protocol resource identifier such as `smContextRef` is not Host-private merely because it appears in a URL path; if the target business Operation needs it, the Integration contract must expose it in the normalized request. If it is used only for private correlation, it may remain private. The contract decides this explicitly.

The Wait output becomes available only after the Host has accepted and correlated the event for this Wait occurrence. It may be consumed by:

- the same Node's Precondition, because Wait completes before the first business stage;
- the same Node's Operation, Observation and Postcondition, subject to ordinary Schema/type checks;
- downstream Nodes on paths where the event-received branch has been taken.

It is unavailable on the timeout branch and before event acceptance. Compiler path analysis must reject any reference that is not available on every path reaching the consumer. A timeout handler must not read the timed-out Wait's `wait.output`.

The Wait output is an explicit Producer value. It is not injected into global Context, is not an Operation Result, is not an Observation Result, and does not replace Evidence. Host correlation keys, transport headers, response handles, ingress references and lifecycle/invocation metadata are not part of `wait.output` unless a separate public protocol contract explicitly defines a field as business input.

## 6. Execution and Host/Runtime responsibilities

### 6.1 Registration and activation

To avoid losing an event that arrives immediately after a triggering outbound Operation, the exact target Wait occurrence must be registered before the predecessor Operation is dispatched.

Registration is not activation:

- it does not enter the target Node;
- it does not start the Wait timeout;
- it does not make `wait.output` available;
- it does not cause the target Node's business stages to execute.

The Integration contract must be able to derive the Wait's correlation key before the triggering external action can produce the event. It may derive that key from already admitted protocol/resource context or from an explicit pre-dispatch binding supplied by the responsible Integration/Tool. It MUST NOT rely solely on an Operation output that becomes available only after the external request has already been sent. If the key cannot be armed before dispatch, the triggering action is not safe to expose through this Wait design.

If an event arrives after registration but before the target Node is selected, the Integration adapter resolves it to the opaque `expectedIngressRef` and submits the normalized delivery. Generic Host durably buffers the delivery by that opaque reference; it does not identify the Run or Node. When the selected route activates the target Node, Runtime validates and consumes the buffered event and proceeds to the first business stage. The timeout clock starts only when the target Node is activated, not when it is registered.

If the predecessor chooses a different route, any unselected candidate Wait registration is invalidated and cannot consume the event as though its Node had been selected.

### 6.2 Responsibility split

**Integration ingress adapter owns protocol-specific work:**

- authenticate the peer NF and authorize it for the exact inbound interface;
- resolve the exact API version, method, path and media type from the pinned Ingress Operation contract;
- validate and normalize the wire request, including supported multipart/binary parts;
- derive the protocol correlation from the authenticated request and trusted Integration state, then resolve it to exactly one opaque `expectedIngressRef`;
- deduplicate protocol delivery according to the exact API/release retry contract;
- own response Schema/status/error mapping and protocol response encoding.

**Generic Host owns generic delivery lifecycle:**

- accept only normalized deliveries from an authorized Integration adapter and the exact pinned contract;
- persist the delivery, opaque `expectedIngressRef`, protected payload reference and Host-owned response-obligation reference in its durable inbox;
- deduplicate the same opaque `deliveryRef` and forward the committed delivery through its outbox;
- keep Host ingress/lifecycle and transport/response references private.

Generic Host MUST NOT parse a 3GPP API path, interpret a PDU Session identifier, authenticate an AMF certificate itself, derive protocol correlation or select a Run/Node. Those are Integration and Runtime responsibilities respectively.

**Runtime owns authoritative continuation state:**

- the Run's active Node and Wait occurrence/generation;
- the authoritative ExpectedIngress registry and resolution of `expectedIngressRef` to the exact Run/Node;
- Wait activation, deadline, atomic event-versus-timeout arbitration and cancellation;
- idempotent event acceptance, checkpointing and resumption of the same Run;
- trace, SourcePath availability and exactly-once Node entry after event acceptance.

The Agent executes the target Node's declared business stages. The Tool Owner still owns the actual callable behavior, external side effects, normalized Operation Result and Evidence. It does not own Run correlation merely because the request belongs to its protocol domain.

### 6.3 Required Host/Runtime capability; not an existing implementation claim

The current Generic Agent Host reference path is synchronous: its `InvocationSource` yields a new `ServiceInvocation`, and `Runtime.execute` returns a terminal result. That interface does not by itself provide durable suspended-Run continuation. The existing `BoundedEvidenceWaiter` is not a substitute.

Therefore, the future implementation requires a generic inbound-event continuation port and durable suspended-Run/Wait state in the Host/Runtime boundary. An inbound event MUST be delivered to that continuation port for the exact existing Run; it MUST NOT be represented as a new `ServiceInvocation`, a new Root-selection request or a second Runtime execution. This is a future generic Host/Runtime capability, not a claim that current `ca-agent-demo` main already supports it. No 5GC-specific branch belongs in Generic Host or Runtime.

### 6.4 Race, duplicate, timeout and recovery

- Event acceptance and Wait timeout are an atomic race. Exactly one may win for a given Wait occurrence.
- A malformed, unauthenticated, unsupported-version or schema-invalid delivery does not satisfy or reset the Wait. The Integration adapter rejects it under the protocol contract; the armed Wait remains pending until its own deadline or another Runtime stop condition.
- A duplicate delivery of the accepted event is idempotently recognized; it cannot execute the Node twice. Duplicate response behavior remains Integration-owned.
- Once timeout wins, that Wait occurrence is closed. A later event cannot revive the old Run or reopen its `wait.output`; the Integration adapter handles the late request under the protocol response contract.
- Wait identity includes a per-Run occurrence/generation maintained privately by Host/Runtime. The Integration correlation contract must prove that a late event from an expired generation cannot satisfy a later Wait for the same protocol resource. A private generation number that is not represented or distinguishable at the protocol boundary is not sufficient by itself.
- The Integration correlation contract must distinguish concurrent Runs using the exact protocol/resource identifiers and trusted Integration association available for that operation. SUPI alone is not assumed to be sufficient; `ueRef` MUST NOT be invented. If two Runs match the same correlation key, the event is ambiguous and must be rejected/quarantined.
- If the 3GPP interface provides no on-wire generation/transaction discriminator, the Integration must prove an equivalent single-flight and stale-delivery/tombstone policy for that resource. If it cannot prevent a late prior request from matching a newer Wait, that interface use is not linkable under this design; the Host must not guess.
- Event receipt, Wait registration/activation, selected route, timeout, duplicate/late classification and continuation must be durably traceable across Host/Runtime restart.
- A transport response handle is not assumed to survive process restart. The Integration contract must define durable response-obligation recovery or an explicit failure response if the underlying transport channel is no longer usable.
- If the event and timeout race during recovery, the durable atomic winner is authoritative; recovery must not accept both.

## 7. Duration and deadline semantics

`timeout` uses a restricted, fixed-duration ISO 8601 representation with positive whole-second precision. Examples:

| Value | Meaning |
|---|---|
| `PT30S` | 30 seconds |
| `PT1M` | 1 minute |
| `PT5M` | 5 minutes |
| `PT2H` | 2 hours |
| `P1D` | 24 hours |

The language accepts positive fixed durations and rejects calendar years/months (for example `P1Y` and `P1M`), zero/negative values, fractional seconds and malformed durations. CA-SL does not impose one arbitrary global maximum. A deployment that admits a Skill with Event Wait must publish a generic maximum Event Wait duration; admission rejects a declared timeout above that limit rather than silently shortening it. The exact deployment field name belongs to the Host deployment contract, not this Skill syntax.

The timer begins at target Node activation. The effective Wait deadline is the earlier of the Node activation time plus the declared timeout and the remaining Invocation deadline. If the Wait deadline wins, route `TIMEOUT`. If the global Invocation deadline or cancellation wins first, Runtime stops under its existing global stop semantics; it MUST NOT relabel that stop as the author's `TIMEOUT` outcome.

After the event is accepted, the inbound protocol request's response deadline (if defined by that API/transport contract) is a separate deadline for processing and responding to that request. The Integration adapter supplies that deadline to the Host/Runtime. It may further constrain execution, but its expiry is not the pre-event Wait `TIMEOUT`; the Integration adapter applies the published protocol failure/response mapping and Runtime preserves any unresolved business responsibility. Runtime emits response-ready only when the resolved `response.after` boundary (or default target-Node boundary) is committed, not when the whole Run becomes terminal.

Wait itself does not dispatch a Tool or Script and therefore does not consume the existing Tool/Script Action Budget. It does consume wall-clock time and remains subject to Host/Runtime execution and Node limits.

## 8. Procedure Graph and static validation

The Compiler models Wait as an entry-control vertex before the Node's first business stage. It adds:

- an implicit normal `EVENT_RECEIVED` edge from the Wait gate to the Node's first declared business stage;
- the explicit `TIMEOUT` edge from `wait.routes.TIMEOUT` to its selected Node or stopping terminal.

These are control-flow edges, not new business stages. The Wait gate does not produce Predicate PASS/FAIL/UNKNOWN and does not create an Operation/Observation Action.

Static analysis must include both Wait edges and the resolved response boundary in reachability, cycle detection, path-sensitive SourcePath availability, global Precondition pass-through, terminal reachability and final-Postcondition proof checks. The Compiler must prove that every normal event-accepted path reaches `response.after` (or the default Wait-bearing Node completion); any earlier terminal/failure path requires the Integration's trusted failure-response mapping. The only route to `SUCCEEDED` remains a reachable final Postcondition aggregate PASS directly targeting `SUCCEEDED`. The timeout edge can never provide Goal proof.

### 8.1 Multiple incoming paths

A Node with Wait may have multiple incoming routes, but this is not a parallel join. Exactly one predecessor path selects and activates the Node for a given Run; Runtime does not wait for all predecessors.

All incoming paths must resolve to the same exact event identity, the same pinned Ingress Operation export and the same normalized request Schema. The Integration correlation key must be derivable before the triggering external action on every incoming path. The concrete key value may differ by Run, but its contract and derivation must be valid on every path.

If one incoming path requires a different service operation, API version, normalized Schema or incompatible correlation contract, authors must use distinct target Nodes and converge later through the existing graph. If any path cannot establish a unique correlation key, compilation/admission fails closed. No path may silently inherit a correlation key from a different predecessor occurrence.

A Node with Wait must still declare at least one business stage. After event acceptance, its stage order and same-Node progression remain unchanged.

## 9. 5GC Step 15 mapping

For the conventional SMF-owned initial PDU Session flow, the future-revision mapping is:

1. Step 11 `Namf_Communication_N1N2MessageTransfer` is the outbound Operation.
2. Before dispatching Step 11, the Integration/Host continuation binding registers the expected Step 15 Wait for the same Run.
3. AMF later sends the `Nsmf_PDUSession.UpdateSMContext` service request.
4. The Integration ingress adapter authenticates the AMF peer, validates the exact pinned 3GPP API request, normalizes its path/body/media parts and derives the trusted correlation key.
5. Generic Host persists and forwards the normalized delivery with its opaque `expectedIngressRef`; Runtime resolves that reference against its authoritative ExpectedIngress record, validates and accepts it, then resumes the exact Run at `update-sm-context`. The normalized request becomes the typed `update-sm-context.wait.output`.
6. The Agent executes the `update-sm-context` Node's declared logical SMF Operation using that explicit input. A supplementary SMF Context Observation, if needed, remains in the same Node after Operation and before Postcondition.
7. The Postcondition checks the appropriate RAN adoption and SMF business facts; a successful route proceeds to N4 Session Modification.
8. The Integration adapter fulfills the paired Step 17 `Nsmf_PDUSession.UpdateSMContext` response obligation for the exact inbound request when the `modify-n4-session` response boundary is committed; later unrelated Run work does not delay Step 17.

### 9.1 Exact API binding

The 3GPP service-operation name used in the procedure is `UpdateSMContext`. In the 3GPP TS 29.502 OpenAPI source, the corresponding `operationId` spelling is `UpdateSmContext`; the operation is `POST /sm-contexts/{smContextRef}/modify` under the `nsmf-pdusession` API. These are two names at different layers and must not be silently conflated.

The cited 3GPP SA5 OpenAPI source shows that this request can use `application/json` with `SmContextUpdateData` or `multipart/related` with `jsonData` and binary N1/N2 parts. Its success responses include `200` with `SmContextUpdatedData` and `204` without a response body. The exact release/OpenAPI artifact used by a deployment must be pinned by digest in the Integration Ingress Operation contract; this design note does not select an API release.

Source: [3GPP SA5 TS29502_Nsmf_PDUSession OpenAPI](https://forge.3gpp.org/rep/sa5/CH/-/blame/73b29750fb01ff09eed9ff1f92a4547227557abc/OpenAPI/TS29502_Nsmf_PDUSession.yaml), especially the Update SM Context operation and its request/response media types.

The `smContextRef` path parameter is part of the public 3GPP operation input. The Integration contract must expose it in `wait.output` if the target Operation needs it; if it is used only to correlate the event to a Run, it remains private. The request body is not assumed to be JSON-only, and unsupported multipart/binary content cannot be discarded.

For this conventional initial-establishment flow, the SM Context resource is created by the earlier Step 3 `Nsmf_PDUSession_CreateSMContext` request and identified to AMF by the Step 5 successful response's `Location` resource URI. The Step 15 Wait is therefore armed against that already-established exact `smContextRef` before Step 11 is dispatched. Do not query for a not-yet-created resource at the beginning of the Procedure merely to prepare this later Wait, and do not substitute SUPI alone or an invented `ueRef` for the resource identity.

This is a conventional 3GPP-facing model. It must not expose implementation-specific SMF module names or imply that AMF/(R)AN/UE actions are SMF-owned Operations. Exact Tool IDs, normalized request Schema, input/output Schemas, Evidence and response obligations must come from trusted Owner/Integration publications; illustrative IDs are not implementation claims.

## 10. v1alpha4 compatibility boundary

CA-SL v1alpha4 remains frozen and unchanged:

- v1alpha4 §21 continues to prohibit author-level Wait/Await/Poll.
- Existing v1alpha4 Skills and examples must continue to use the v1alpha4 pending-Operation contract; they must not add the proposed `wait` field or `wait.output` SourcePath.
- This proposal does not authorize changing the current v1alpha4 grammar, diagnostics, Compiler, Studio/LSP, Runtime, Generic Host or Integration implementation.
- The next language version and its exact version identifier are not assigned by this design note. The feature requires an explicit versioned revision and independent review.

## 11. Normative change inventory for the future revision

| Current v1alpha4 area | Required future-revision work |
|---|---|
| §10.1 structure grammar | Add optional Node-level `wait`, `wait.response.after` and their exact field grammar |
| §12.1 Node execution | Define Wait as pre-stage entry control; retain four business stages |
| §12.9 control-flow proof | Include Wait activation and timeout edges in DAG/path-sensitive checks |
| §13.2–§13.3 SourcePath | Add typed `NodeId.wait.output`, normalized request Schema, availability and assignability rules |
| §19 Invocation lifecycle | Define durable Run suspension/resumption, Wait occurrence identity and continuation delivery |
| §21 asynchronous semantics | Replace the blanket no-author-Wait rule for the new version with the declarative Node-entry model; keep Evidence Wait distinct |
| §22 routes | Define the Wait-scoped `TIMEOUT` key and reuse existing route targets |
| §24 / Annex H | Add diagnostics for Ingress Operation resolution, correlation ambiguity, Schema/media normalization, timeout routes and unavailable Wait output |
| Dependency/Integration contracts | Define exact Ingress Operation export, pinned API provenance, normalized request Schema, correlation binding, response mapping and response-boundary binding |
| Host/Runtime contract | Define a generic continuation port and durable suspended-Run/Wait lifecycle; do not add 5GC-specific Host/Runtime branches |

The revision must not add a fifth business stage, a Wait Node kind, a new business-stage Outcome family, `onTimeout`, `payloadSchema`, a global author-facing EventCatalog, a second Procedure Graph, or a 5GC-specific branch in Generic Host/Runtime.

## 12. Review and acceptance checklist

Before this design can be frozen into a language revision, independent review must confirm:

- [ ] exact grammar and required Wait fields;
- [ ] the Integration-owned Ingress Operation export and exact API artifact/version/digest binding;
- [ ] normalized request Schema behavior for path/query parameters, JSON bodies and supported multipart/binary parts;
- [ ] deterministic correlation-key derivation before the triggering external action, unique matching under concurrent Runs and safe generation reuse (including a single-flight/tombstone rule when the protocol has no on-wire generation discriminator);
- [ ] the generic Host continuation port and durable suspended-Run/Wait state, including restart recovery;
- [ ] supported duration lexical subset, deployment maximum and precedence against Invocation and inbound response deadlines;
- [ ] mandatory `wait.routes.TIMEOUT` and permitted stopping terminals;
- [ ] same-Node/downstream `wait.output` typing and path-sensitive availability;
- [ ] early-event registration, durable buffering and cancellation of unselected candidate registrations;
- [ ] atomic event-versus-timeout behavior and late/duplicate handling after restart;
- [ ] interaction with global Precondition, Action Budget, Node limits, cancellation and final Goal proof;
- [ ] Step 15/17 response obligation ownership, `response.after` path proof and failure mapping;
- [ ] diagnostics, trace semantics and positive/negative conformance fixtures.


### 12.1 Minimum conformance matrix

| Scenario | Required result |
|---|---|
| Valid event arrives after Wait registration but before target Node activation | Integration delivery is durably buffered; it is consumed only if the selected route activates that exact Wait occurrence |
| Valid event arrives after target Node activation | The same Run resumes once; `wait.output` becomes available before the Node's first business stage |
| Event arrives before any matching Wait registration | It is not converted into a new Invocation or attached to a future Wait; Integration applies its unmatched-request policy |
| Invalid peer, API version, media type or request Schema | Integration rejects the delivery; it does not satisfy or reset the Wait |
| Unsupported multipart/binary part | Delivery is rejected or quarantined unless the pinned Integration contract defines a normalized representation; no part is silently dropped |
| Two active Runs match the same correlation key | Delivery is ambiguous and is rejected/quarantined; Host must not select the newest Run |
| A prior Wait times out and a later Wait reuses the same resource identity | A stale prior delivery cannot satisfy the later Wait; require a protocol discriminator or proven single-flight/tombstone rule |
| Event and Wait timeout occur concurrently | Exactly one durable atomic winner is recorded; the losing transition cannot execute |
| Duplicate delivery follows an accepted event | The target Node is not entered twice; duplicate protocol response handling remains Integration-owned |
| Global Invocation deadline/cancellation wins before the declared Wait timeout | Runtime applies the global stop semantics; it does not route through the author's `TIMEOUT` branch |
| Inbound protocol response deadline expires after event acceptance | Integration applies the published response failure mapping; this is not reclassified as the pre-event Wait `TIMEOUT` |
| Multiple predecessor paths reach the same Wait Node | The selected path activates once; all paths must use the same Ingress Operation export and provide a valid correlation binding; no implicit graph join occurs |
| One predecessor path cannot establish the required correlation binding | Compiler/admission rejects the Wait Node/path; no fallback to SUPI-only or guessed identity is allowed |
| Paired protocol response is due after a later business Node | Runtime emits response-ready at `response.after` completion, not at Wait-node completion or terminal Run; Host/Integration fulfills the exact response obligation |

These cases are semantic acceptance requirements. They do not imply that the Compiler, Host, Runtime or Integration adapter already implements them.
No implementation or product-conformance claim follows from this design document alone.
