# CA-SL Node-level Event Wait — Normative Amendment Draft

**Status:** Normative text draft for the language revision after CA-SL v1alpha4.  
**Semantic baseline:** FROZEN by the design record in [ca-skills PR #60](https://github.com/odango-chan/ca-skills/pull/60).  
**Integration export contract:** under independent design review in [ca-skills PR #62](https://github.com/odango-chan/ca-skills/pull/62).  
**Generic Host/Runtime continuation contract:** [ca-agent-demo PR #210](https://github.com/odango-chan/ca-agent-demo/pull/210).  
**Normative publication status:** NOT FROZEN / NOT RELEASED.  
**Version identity:** Unassigned. This draft MUST NOT be interpreted as v1alpha4 or used to infer the next language version identifier.

## 0. Effect and compatibility

This document translates the frozen Node-level Event Wait semantic baseline into proposed normative clauses. It is a delta against the published CA-SL v1alpha4 specification, not a replacement for that specification and not a new released language version.

The following v1alpha4 rules remain unchanged for connectionagent.io/v1alpha4:

- §10.1 does not admit the wait field.
- §13.2 does not admit wait as a Producer source.
- §21 continues to prohibit author-level wait, await and polling Nodes.
- The v1alpha4 §52 authoring guidance remains scoped to v1alpha4; a future full specification MUST replace or qualify that guidance so it no longer contradicts the Node-entry Event Wait model.
- UNSUPPORTED_WAIT / C_STATIC remains the required diagnostic only when the selected language target is v1alpha4, as defined by v1alpha4 §24.1/H. A future-version Compiler MUST NOT emit UNSUPPORTED_WAIT for a valid Node-level Wait declaration.
- Existing v1alpha4 pending-Operation continuation semantics remain authoritative.

A Compiler MUST select exactly one language target before parsing. It MUST NOT accept this draft's grammar when compiling a v1alpha4 package, and MUST NOT silently reinterpret a v1alpha4 package as the future language revision.

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT and MAY are normative terms.

## 1. Amendment to §10.1 — Procedure Node grammar

For the future language revision, amend the abstract Node grammar as follows. All fields not shown retain their v1alpha4 meanings and constraints.

~~~ebnf
Procedure              = map(start: NodeId, nodes: map<NodeId, Node>)
Node                   = map(wait?: Wait,
                             precondition?: Precondition,
                             operation?: Operation,
                             observation?: Observation,
                             postcondition?: Postcondition)

Wait                   = map(event: IngressEventSelector,
                             timeout: FixedDuration,
                             response?: WaitResponse,
                             routes: WaitTimeoutRoutes)

IngressEventSelector   = map(source: NonEmptyExactString,
                             service: NonEmptyExactString,
                             operation: NonEmptyExactString)

WaitResponse           = map(after?: NodeId)
WaitTimeoutRoutes      = map(TIMEOUT: WaitTimeoutTarget)
WaitTimeoutTarget      = NodeId | FAILED | UNRESOLVED | SAFE_STOPPED

FixedDuration          = "P", (DayComponent, ["T", TimeComponents]
                              | "T", TimeComponents)
TimeComponents         = HourComponent, [MinuteComponent], [SecondComponent]
                       | MinuteComponent, [SecondComponent]
                       | SecondComponent
DayComponent           = PositiveInteger, "D"
HourComponent          = PositiveInteger, "H"
MinuteComponent        = PositiveInteger, "M"
SecondComponent        = PositiveInteger, "S"
PositiveInteger        = NonZeroDigit, { Digit }
NonZeroDigit           = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
Digit                  = "0" | NonZeroDigit
~~~

NonEmptyExactString is a non-empty YAML string compared exactly, including case and punctuation, against a trusted Integration Ingress Operation export. It is not a free-form runtime filter.

event.source is the canonical authenticated peer NF type. event.service is the 3GPP service name. event.operation is the 3GPP service-operation name. For example, UpdateSMContext is the service-operation spelling; an OpenAPI operationId such as UpdateSmContext is a distinct artifact field and MUST NOT be substituted for it.

The event mapping MUST contain exactly source, service and operation. response, when present, MUST contain only after. routes MUST contain exactly one key, TIMEOUT. Unknown structural fields are rejected by the normal unknown-field rule; a route key other than TIMEOUT is rejected as WAIT_TIMEOUT_ROUTE_INVALID. A missing event selector, invalid event object shape, wrong selector field type or empty selector string is rejected as WAIT_DECLARATION_INVALID. A missing timeout, non-string timeout or timeout that does not match the duration grammar is rejected as WAIT_TIMEOUT_INVALID. A missing routes mapping or missing TIMEOUT key is rejected as WAIT_TIMEOUT_ROUTE_INVALID.

A Node containing wait MUST also declare at least one of the four existing business stages. wait does not count as a business stage. A Wait-only Node is invalid. The order of execution remains:

1. optional Node-entry wait;
2. optional precondition;
3. optional operation;
4. optional observation;
5. optional postcondition.

No fifth business stage, Wait Node kind, await field, polling field, onTimeout field, payloadSchema field or author-facing EventCatalog is introduced.

### 1.1 Fixed-duration lexical rules

A FixedDuration MUST be a YAML string matching the grammar above.

- Every present component is a positive base-10 integer with no sign, decimal point or leading zero.
- At least one day or time component MUST be present.
- Days are fixed 24-hour periods. Hours, minutes and seconds have their ordinary fixed-duration meanings.
- Calendar years, calendar months, weeks, fractional seconds, negative values, zero values and alternate ISO 8601 spellings are rejected.
- Examples accepted: PT30S, PT1M, PT5M, PT2H, P1D, P1DT2H30M.
- Examples rejected: P1M (calendar month), P1Y, P1W, PT0S, PT-1S, PT0.5S, PT01M, P.

The deployment MUST publish a maximum Event Wait duration. Admission MUST reject a declared duration greater than that maximum. A deployment limit MUST NOT be implemented by silently shortening the authored duration. A malformed duration is a C_STATIC error; exceeding a deployment-specific maximum is an admission rejection before Invocation creation (WAIT_DURATION_LIMIT_EXCEEDED in the Host/Runtime deployment contract). The physical deployment-setting name is outside the Skill grammar.

## 2. Amendment to §12 — Node-entry control semantics

### 2.1 Wait is an entry control, not a stage

A Node's wait is evaluated after control flow selects that Node and before its first declared business stage.

- If the expected event is accepted, Runtime enters the Node's first declared business stage.
- If the Wait deadline wins, Runtime follows wait.routes.TIMEOUT.
- The normal event outcome is implicit. Authors MUST NOT declare an EVENT_RECEIVED route.
- TIMEOUT is a Wait-control outcome, not a Predicate Outcome, Stage Outcome, Operation Outcome or Evidence result.
- Event receipt does not create Evidence, prove a Predicate, satisfy a Precondition or establish the Skill Goal.

The existing four business stages retain their v1alpha4 meanings, order, Outcomes and stage-level routes rules. A Wait-bearing Node is otherwise an ordinary business Node.

### 2.2 Wait timeout route

wait.routes.TIMEOUT is REQUIRED.

Its value MUST be either:

- the ID of another declared Node; or
- FAILED, UNRESOLVED or SAFE_STOPPED.

SUCCEEDED is forbidden. A timeout cannot prove the business Goal. The timeout branch MAY enter ordinary business Nodes to inspect or safely handle state, but the Invocation can become SUCCEEDED only through the existing final Postcondition aggregate PASS edge directly targeting SUCCEEDED.

No other Wait route key is permitted. Missing TIMEOUT, an extra route key, a non-Node/non-terminal value or a terminal target other than the three permitted stopping terminals is rejected as WAIT_TIMEOUT_ROUTE_INVALID. A value that is a syntactically valid NodeId but does not identify a declared Node is rejected by the existing CONTROL_FLOW_DANGLING diagnostic. The Wait route does not extend the §22 Stage Outcome set.

### 2.3 Wait output

An accepted Wait produces one typed value named by the SourcePath NodeId.wait.output. This value is the normalized request value defined by the exact trusted Ingress Operation export. It is not necessarily the raw HTTP body: it MAY include normalized path parameters, query parameters and supported body parts.

wait.output becomes available only after the event has been accepted for that exact Wait occurrence. It MAY be consumed by any declared business stage in the same Node and by downstream Nodes on paths dominated by that event-accepted edge.

It is unavailable:

- before the Wait-bearing Node is activated;
- on the Wait TIMEOUT edge;
- on any path that does not accept the corresponding event;
- after the Wait occurrence has been invalidated, cancelled or timed out.

A timeout handler MUST NOT read the timed-out Wait's output. Compiler path analysis MUST reject any consumer for which the Wait output is not available on every path reaching that consumer.

The normalized request value is ordinary typed input data. It MUST NOT be injected into global Context, treated as an Operation Result or Observation Result, or treated as Evidence. Transport headers, Host correlation keys, expectedIngressRef, deliveryRef, response handles and lifecycle metadata remain private unless the Integration's public normalized request Schema explicitly defines a field as business input.

### 2.4 Authoring example

The following is a syntax illustration. Callable IDs and Predicate IDs are placeholders; they do not claim that the corresponding Owner exports are published.

~~~yaml
start: transfer-n1n2-message
nodes:
  transfer-n1n2-message:
    operation:
      tool: ca::amf.communication.n1n2_message_transfer
      arguments:
        smContextRef: create-sm-context.operation.output.smContextRef
        n1Message: prepare-n1n2.operation.output.n1Message
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
        - predicate: session.update_request.valid
          arguments:
            - update-sm-context.wait.output
      routes:
        FAIL: SAFE_STOPPED
        UNKNOWN: UNRESOLVED
    operation:
      tool: ca::smf.session.update_from_amf
      arguments:
        request: update-sm-context.wait.output
      routes:
        FAILED: SAFE_STOPPED
    postcondition:
      predicates:
        - predicate: session.ran_adoption.confirmed
          arguments:
            - update-sm-context.operation.output
      routes:
        PASS: modify-n4-session
        FAIL: SAFE_STOPPED
        UNKNOWN: UNRESOLVED

  modify-n4-session:
    operation:
      tool: ca::upn.session.modify
      arguments:
        request: update-sm-context.operation.output
      routes:
        SUCCEEDED: verify-final-session
        FAILED: SAFE_STOPPED

  verify-final-session:
    postcondition:
      predicates:
        - predicate: session.goal_satisfied
          arguments:
            - modify-n4-session.operation.output
      routes:
        PASS: SUCCEEDED
        FAIL: SAFE_STOPPED
        UNKNOWN: UNRESOLVED

  handle-update-timeout:
    operation:
      tool: ca::smf.update_timeout.handle
      arguments: {}
      routes:
        SUCCEEDED: SAFE_STOPPED
        FAILED: UNRESOLVED
~~~

This fragment is not a complete Skill: its referenced Nodes, schemas, Predicate declarations, dependency exports and final Goal Postcondition are intentionally omitted. It demonstrates only the Node-entry Wait shape, typed wait.output binding, timeout routing and the Step 17 response boundary. The Integration export MUST identify the triggering transfer callable and prove its pre-dispatch correlation binding. For a body-bearing Step 17 response, its responseResultSources binding may select modify-n4-session.operation.output and MUST validate that exact output against the pinned protocol response Schema.

## 3. Integration Ingress Operation export

### 3.1 Ownership and exact resolution

The Skill MUST declare the Integration package as an ordinary version-pinned dependency. The Compiler resolves the three-part wait.event selector against trusted Ingress Operation exports in those exact dependency snapshots.

Resolution MUST produce exactly one matching export:

- zero matching exports: WAIT_INGRESS_EXPORT_NOT_FOUND;
- more than one matching export: WAIT_INGRESS_EXPORT_AMBIGUOUS.

The Compiler MUST NOT guess from a similar name, inspect an untrusted inbound body to select a Schema, choose the newest export, or fall back to a globally installed EventCatalog.

The Integration export, not the Skill, owns the protocol-specific request contract. The Skill MUST NOT duplicate that contract using an author-declared payloadSchema.

### 3.2 Required logical properties

The trusted Ingress Operation export, serialized as a package-scoped IngressCatalog with proposed apiVersion connectionagent.io/ingresscatalog/v1alpha1 and trusted exportKind ingressOperation, MUST bind, at minimum:

1. canonical peer/source NF type, 3GPP service name and service-operation name;
2. source specification identity and release;
3. exact API URI version, OpenAPI artifact identity and digest, HTTP method, path template and OpenAPI operationId;
4. accepted wire media types;
5. source request Schema references and their digests;
6. one normalized request Schema in the CA-SL supported JSON Schema subset;
7. a deterministic, traceable source-to-normalized mapping for path, query, JSON and supported multipart/binary parts;
8. authenticated peer identity rules and protocol authorization rules;
9. deterministic correlation derivation, including the exact permitted triggering Operation callable identity/identities and the pre-dispatch binding required to arm the Wait;
10. duplicate, stale-delivery, generation-reuse and unmatched-request handling;
11. whether a paired protocol response exists, its response Schema/media types, success and failure mapping, and response-obligation lifecycle;
12. when a response body is required, the typed response-result input Schema, the response-boundary Producer stage type (operation or observation), the protocol response Schema and a deterministic mapping between them;
13. a typed armInputSchema for the pre-dispatch correlationBinding, plus exact bindings from either admitted Invocation Context or triggering Operation arguments.

The package-scoped IngressCatalog field structure, normalization contract, trigger binding shape, stale-delivery policy and response mapping are defined by the independent [Integration Ingress Operation Contract design PR #62](https://github.com/odango-chan/ca-skills/pull/62). This is not a global EventCatalog and does not alter v1alpha4 export kinds.

event.source MUST match the authenticated peer NF type established by the Integration adapter. It MUST NOT be inferred from a body field or an unauthenticated header.

### 3.3 Request normalization and binary content

The Integration adapter owns source-wire parsing, authentication, API version selection, media-type validation, request Schema validation and normalization. Generic Host and Runtime consume only the normalized delivery.

For multipart or binary request parts, the Integration export MUST define the normalized representation. A binary part MAY be represented by a typed immutable content reference only when the export defines and authorizes that representation, its content digest/integrity rules and its retention lifetime. Unsupported or unrepresentable parts MUST be rejected or quarantined; they MUST NOT be silently dropped, truncated or guessed.

A syntactically valid request is not Evidence that the requested network action succeeded. Business facts and the final Goal remain subject to the existing Owner Output, Evidence and Predicate rules.

## 4. Correlation and pre-dispatch registration

### 4.1 Correlation contract

The Integration export MUST define a deterministic correlation binding that maps an authenticated inbound request to exactly one armed Wait occurrence. The binding MUST distinguish:

- concurrent Runs for the same UE or protocol resource;
- successive Wait occurrences for the same resource;
- late requests from an expired or invalidated occurrence;
- duplicate delivery of the same protocol request.

SUPI alone MUST NOT be assumed sufficient. A Skill or Host MUST NOT invent ueRef or another synthetic identity to make correlation appear unique. The binding MUST use the exact protocol/resource identity and trusted Integration association applicable to the interface.

If the wire protocol carries a generation, transaction or request discriminator, the Integration MUST validate and use it. If the protocol has no on-wire discriminator capable of distinguishing a prior occurrence from a later occurrence, the Integration MUST prove an equivalent single-flight and stale-delivery/tombstone policy for that resource. If neither is possible, the Compiler MUST reject the binding with WAIT_CORRELATION_BINDING_INVALID; Runtime MUST NOT guess.

### 4.2 Trigger and arming point

The Integration export MUST identify the trusted triggering Operation callable(s), if any, that can cause the declared inbound event, and MUST define how each correlation key is materialized into its typed armInputSchema before dispatch. Each triggering identity MUST resolve to exactly one trusted ToolCatalog Operation callable export in the declared dependency snapshots, identified by exact Package ID, Owner, kind=operation and Operation ID; the Compiler resolves its Input Schema from that ToolCatalog export. A Capability ID, free-form label, Observation export or network address is not a triggering Operation identity.

For each reachable incoming path to a Wait-bearing Node:

- the Compiler MUST resolve the applicable triggering Operation and verify that it occurs before the target Wait is entered;
- every value needed to derive the correlation binding MUST be available before the triggering Operation is dispatched;
- the binding MUST NOT depend solely on the triggering Operation's output, because that output is unavailable until after the external action may already have caused the event;
- all incoming paths MUST resolve to the same exact Ingress Operation export, normalized request Schema and correlation contract;
- the concrete correlation value MAY differ by Run/path, but each path MUST prove a unique match.

If the Wait-bearing Node is the Procedure start Node, the Integration export MUST declare start arming and bind every correlation key from a path in the already-admitted Invocation Context into the same typed armInputSchema; Runtime MUST arm it before entering the Node. A non-start incoming path with no resolvable triggering Operation/binding is invalid. If different incoming paths require different event identities, API versions, normalized Schemas or incompatible correlation contracts, authors MUST use distinct Wait-bearing Nodes and converge later through the ordinary Procedure graph.

The Integration export's triggering Operation identity is trusted dependency metadata; the Skill does not add a trigger, correlationKey, ueRef, callback token or Host handle field.

### 4.3 Registration lifecycle

Before dispatching a triggering Operation, Runtime MUST:

1. create an opaque expectedIngressRef;
2. bind it privately to the exact Run, target Node and Wait occurrence/generation in the authoritative Runtime registry;
3. ask Generic Host to durably arm the expected ingress and forward the registration to the responsible Integration adapter;
4. receive an acknowledged ARMED disposition before dispatching the triggering Operation.

An arm failure or uncertain arm state MUST prevent dispatch of the triggering Operation until the same idempotent arm request is resolved. Runtime MUST NOT dispatch first and attempt to correlate later.

Registration is not activation:

- it does not enter the target Node;
- it does not start the Wait timeout;
- it does not make wait.output available;
- it does not cause any business stage to execute.

If an authenticated, valid event arrives after registration but before the target Node is selected, Integration submits the normalized delivery and Host durably buffers it against the opaque expectedIngressRef. Runtime consumes it only if the selected route activates that exact Wait occurrence. If another route is selected, the unselected registration is invalidated; a buffered event MUST NOT be reassigned to another Run or Wait.

For a start Node, Runtime arms the Wait from admitted context before activating the Node. The same pre-activation buffering and consumption rules apply.

## 5. Amendment to §13.2 — SourcePath

Amend the Producer source grammar as follows:

~~~ebnf
SourcePath          = ContextPath | ProducerOutputPath
ProducerOutputPath  = NodeId, ".", ProducerSource, ".output",
                      { ".", Identifier }
ProducerSource      = "operation" | "observation" | "wait"
~~~

wait is a Producer source for typed normalized inbound request data; it is not a business stage. Existing operation and observation SourcePath rules remain unchanged.

The Compiler MUST resolve NodeId.wait.output against the normalized request Schema of the exact linked Ingress Operation export. Nested property paths MUST be validated using the same supported Schema subset, Identifier rules, assignability and path-sensitive availability checks as other Producer outputs.

The Wait output MAY be referenced by the Wait-bearing Node's own Precondition because event acceptance occurs before the first business stage. It MAY be referenced by that Node's Operation, Observation and Postcondition, and by downstream Nodes when the event-accepted edge dominates the consumer.

If the consumer is reachable through a path that can bypass event acceptance, including the TIMEOUT route, the source is not available and MUST produce the existing SOURCE_NOT_AVAILABLE / C_STATIC diagnostic. An undeclared property or malformed path MUST produce the existing SOURCE_PATH_INVALID / C_STATIC diagnostic. No new implicit Context projection is created.

The normalized request Schema MUST expose stable field names that satisfy the existing SourcePath Identifier grammar. The Integration adapter MUST normalize source fields that cannot be represented by that grammar; the Skill MUST NOT access raw transport paths or arbitrary JSON pointers.

## 6. Amendment to §12.9 — Procedure graph and static analysis

The Compiler MUST model a Wait-bearing Node as an entry-control vertex immediately before that Node's first declared business stage.

The control-flow graph contains:

- an implicit EVENT_RECEIVED edge from the Wait gate to the Node's first declared business stage;
- one explicit TIMEOUT edge from the Wait gate to the target of wait.routes.TIMEOUT.

EVENT_RECEIVED and TIMEOUT are control-flow labels, not Stage Outcomes. EVENT_RECEIVED MUST NOT appear in author YAML. TIMEOUT is valid only in wait.routes.

The Compiler MUST include the Wait gate and both edges in:

- start reachability and unreachable-node analysis;
- dangling-target checks and cycle detection;
- path-sensitive SourcePath availability and assignability;
- global Precondition pass-through analysis;
- terminal reachability and final Postcondition proof analysis;
- response-boundary reachability and post-dominance analysis.

Both outgoing Wait-control edges preserve the incoming global-Precondition pass-through state; neither edge sets that state to true. Only the existing Contract-referenced Precondition aggregate PASS edge can establish the global gate. A Wait event does not satisfy a global or local Precondition.

The Wait gate cannot create, carry or restore Goal proof. The only edge that can request Invocation SUCCEEDED remains a reachable final Postcondition aggregate PASS edge directly targeting SUCCEEDED. A Wait timeout edge MUST NOT target SUCCEEDED.

The existing DAG invariant remains in force. A timeout route or any other route that introduces a cycle MUST be rejected with the existing CONTROL_FLOW_CYCLE / C_STATIC diagnostic. A Wait Node is entered once per selected path; multiple incoming paths do not form a parallel join. Exactly one selected predecessor path activates a given Wait occurrence for a Run.

### 6.1 Multiple incoming paths

A Wait-bearing Node MAY have multiple incoming control-flow edges. This does not mean Runtime waits for all predecessors.

All incoming paths MUST satisfy §4.2 and resolve to the same exact event identity, Ingress Operation export, normalized request Schema and correlation contract. Each selected path MUST provide a valid pre-dispatch binding before its triggering Operation. If any path cannot do so, the Compiler MUST reject the Wait Node. No path may inherit a correlation value from another predecessor occurrence.

## 7. Amendment to §19 and §21 — Runtime lifecycle

### 7.1 Wait occurrence state

Runtime is the sole authority for Wait occurrence state. At minimum, the logical states are:

~~~text
REGISTERED
  ├─ selected target Node activated ─> ACTIVE
  ├─ predecessor selects another route ─> INVALIDATED
  └─ Run cancelled/stopped ─> CANCELLED

ACTIVE
  ├─ valid delivery wins atomic transition ─> EVENT_ACCEPTED
  ├─ Wait deadline wins atomic transition ─> TIMED_OUT
  └─ Invocation deadline/cancellation wins ─> CANCELLED

EVENT_ACCEPTED
  └─ durable checkpoint and one-time Node entry ─> CONSUMED
~~~

A valid delivery received in REGISTERED is durably buffered but does not activate the Node. When the target Node becomes active, Runtime MUST consider an already-buffered valid delivery before allowing the Wait timer to win. If such a delivery exists, Runtime accepts it and proceeds to the first business stage; registration time is never counted against the Wait timeout.

For an ACTIVE Wait, event acceptance and Wait timeout MUST compete through one authoritative atomic state transition. Exactly one disposition wins. The durable winner is authoritative across recovery. Duplicate Host notifications and duplicate delivery submissions MUST NOT cause a second Node entry.

Once TIMED_OUT, INVALIDATED or CANCELLED, a Wait occurrence is closed. A later event MUST NOT reopen it, populate its output or satisfy a later Wait occurrence.

### 7.2 Deadlines and cancellation

The Wait clock starts only when the target Node becomes ACTIVE. Its authored deadline is Node activation time plus wait.timeout. The effective deadline is the earlier of the authored Wait deadline and the remaining Invocation deadline.

If the authored Wait deadline is strictly earlier and its timeout transition wins the authoritative state transition, Runtime follows wait.routes.TIMEOUT. If the global Invocation deadline is earlier than or equal to the authored Wait deadline, the global deadline takes precedence and Runtime applies the existing global stop semantics; it MUST NOT relabel that stop as the author's TIMEOUT outcome. Cancellation likewise uses the existing global stop semantics. Event acceptance, timeout and global stop are serialized against the same authoritative Wait occurrence; only one durable transition may win.

The inbound protocol response deadline, if the Integration contract defines one, begins after event acceptance and is independent of the pre-event Wait deadline. Integration supplies that deadline to Host/Runtime; it MAY further constrain processing. Its expiry is handled by the Integration response/failure contract, and Runtime preserves the accepted-event checkpoint and any unresolved business/resource responsibility. It is not a Wait TIMEOUT and MUST NOT be converted into an author-routable Stage Outcome. Any resulting Run cancellation MUST use the existing global cancellation semantics.

Wait itself dispatches no Tool or Script and consumes no Tool/Script Action Budget. It consumes wall-clock time and remains subject to deployment Wait limits, Invocation deadline, cancellation, Node limits and durable Runtime resource limits.

### 7.3 Event Wait is not Evidence Wait

Event Wait is push-driven ingress plus continuation of an existing Run. It MUST NOT be implemented as repeated Observation calls, polling, a Predicate, or an Evidence acquisition loop.

The Runtime's Observation-based bounded Evidence waiter remains a distinct mechanism with its existing query, freshness, scope, correlation and observation-budget semantics. The two mechanisms MAY share generic deadline/cancellation utilities, but MUST NOT share their data-source, result, proof or lifecycle semantics.

### 7.4 Durable continuation

An inbound event MUST resume the exact existing Run at the selected Wait-bearing Node. It MUST NOT create a new Invocation, new Root selection, new Skill selection or second Runtime execution.

The current synchronous Invocation API and any existing Observation waiter do not, by themselves, establish this capability. A conforming implementation requires a generic inbound-event continuation port and durable suspended-Run/Wait state. This clause is a future implementation requirement, not a claim about current Host/Runtime conformance.

## 8. Amendment to §12.1 and §22 — paired response boundary

### 8.1 Boundary selection

If the linked Ingress Operation export declares a paired protocol response, the response boundary is:

- the completion of the Wait-bearing Node, including all its declared business stages, when wait.response.after is absent; or
- the completion of the exact Node named by wait.response.after, including all its declared business stages, when the field is present.

wait.response.after MUST identify a declared Node reachable from the event-accepted edge of the Wait-bearing Node. It is response-continuation metadata, not a business stage or route. It does not change the terminal Run condition.

The Compiler MUST prove that the selected response-boundary Node post-dominates the event-accepted edge for every path that does not terminate early in a permitted failure disposition. Every event-accepted path MUST either reach the selected response boundary or terminate earlier with FAILED, UNRESOLVED or SAFE_STOPPED and have an explicit trusted Integration response mapping for that disposition. A path that reaches SUCCEEDED before the response boundary is invalid. The boundary MUST NOT be inferred from the eventual terminal Run.

If the Integration export requires a response boundary later than the Wait-bearing Node, wait.response.after is REQUIRED. If the export allows response at Wait-bearing Node completion, omission is valid. If the export declares no paired response, authoring wait.response is invalid.

### 8.2 Typed response-result binding

A paired response with a body MUST NOT be synthesized from raw inbound request data, Host-private metadata, an eventual terminal Run summary or an untyped aggregate of all prior Node outputs.

The trusted Integration export MUST declare:

- the protocol response Schema and media type for each supported response disposition;
- whether the response is bodyless or body-bearing;
- for a body-bearing response, a typed responseResultSchema and the response-boundary Producer stage type, operation or observation;
- a deterministic Integration-owned mapping from that typed response result to the protocol response Schema;
- explicit fixed failure-response mappings for any permitted early terminal disposition before the selected Producer has produced a result.

The Compiler resolves the exact response SourcePath deterministically from wait.response.after (or the default Wait-bearing Node) and the export's Producer stage type: <response-boundary-node>.<producer>.output. It MUST NOT accept a Skill-specific NodeId or SourcePath embedded in the reusable Integration export. The selected Producer MUST exist at the response-boundary Node, MUST be available on every normal path reaching that boundary, and its Output Schema MUST be assignable to responseResultSchema. The Compiler MUST verify that the Integration mapping supplies each required protocol response field.

If response data originates in an earlier Node, the Skill MUST pass the required values explicitly through the boundary Node's Operation/Observation arguments, and that Producer MUST expose the complete typed response result. Runtime/Integration MUST NOT read arbitrary historical Run outputs, infer the latest output or construct an untyped aggregate.

A bodyless protocol response MAY declare no response-result Producer. A body-bearing response without a valid Producer stage, compatible Output Schema or complete mapping is rejected as WAIT_RESPONSE_MAPPING_INVALID. If the Producer has not produced an available result because the Run terminates before it, the declared early-failure response mapping applies. A completed Producer result may be mapped even when a later Postcondition does not prove the Skill Goal; protocol response mapping is not Goal proof.

### 8.3 Response completion and ownership

When the response boundary is committed, Runtime emits a typed response-ready result associated with the opaque expectedIngressRef, exact Ingress Operation contract and typed response result. Host resolves its private association from expectedIngressRef to the durable response-obligation record and relays the result to Integration.

- Runtime does not receive or emit a protocol response-obligation identity.
- Host retains the private response-obligation record and owns durable relay/recovery.
- Integration owns protocol status/error mapping, headers, body/media serialization and wire response.
- Runtime emits response-ready at the declared boundary, not when the whole Run terminates.
- A transport handle is not assumed to survive process restart. Integration MUST define durable response-obligation recovery or an explicit failure response if the channel is no longer usable.

The response boundary is independent of terminal Run completion. Later unrelated Procedure work MUST NOT delay an already committed paired response.

## 9. Generic Host / Runtime / Integration boundary

The logical responsibilities are:

| Component | Required responsibility | Forbidden responsibility |
|---|---|---|
| Domain Integration | Authenticate peer NF; validate exact API/release/method/path/media; normalize request; derive protocol correlation; deduplicate protocol delivery; encode paired response | Select a Run by heuristic; expose Run identity to external protocol |
| Generic Host | Durably accept and relay normalized deliveries; deduplicate deliveryRef; retain private ingress/response-obligation records; provide inbox/outbox recovery | Parse 3GPP API paths or payloads; derive protocol correlation; resolve expectedIngressRef to Run/Node |
| Runtime | Own ExpectedIngress registry; resolve expectedIngressRef; manage Wait state, deadlines, atomic race, checkpoint and same-Run continuation | Parse original HTTP/SBI wire request; derive protocol identity from raw payload |
| Agent / Tool Owner | Execute declared business stages; own callable effects, normalized Operation Results and Evidence | Own Run correlation or protocol response transport lifecycle |

### 9.1 Logical ports

The following are logical operations, not frozen method names or wire DTOs:

~~~text
Runtime -> Host -> Integration:
  ArmExpectedIngress(
    expectedIngressRef,
    ingressContractRef,
    correlationBinding
  ) -> ARMED | REJECTED

Integration -> Host:
  SubmitInboundDelivery(
    deliveryRef,
    expectedIngressRef,
    ingressContractRef,
    normalizedPayloadRef,
    responseObligationRef?,
    responseDeadline?
  ) -> ACCEPTED | DUPLICATE | REJECTED

Host -> Runtime:
  InboundDeliveryAvailable(
    deliveryRef,
    expectedIngressRef,
    ingressContractRef,
    normalizedPayloadRef
  )

Runtime -> Host:
  ResponseBoundaryCommitted(
    expectedIngressRef,
    ingressContractRef,
    responseResultRef?
  )
~~~

Runtime creates expectedIngressRef and privately binds it to the exact Run, Node and Wait occurrence. Host and Integration carry it only as an opaque handle. Neither may resolve it to a Run or Node. Integration MUST NOT receive runId or waitOccurrenceRef.

deliveryRef is an Integration-owned idempotency identity for one normalized delivery. responseObligationRef is Integration-owned and remains private to Integration/Host. It MUST be present if and only if the pinned Ingress Operation export declares a paired response. responseResultRef is required only for a body-bearing response disposition; it MAY be absent for a bodyless response. normalizedPayloadRef is a protected immutable reference; the typed request value is exposed to Skill code only through wait.output.

Delivery is durable at-least-once plus idempotent acceptance. No distributed exactly-once transport guarantee is implied. Runtime's atomic state transition and durable checkpoint enforce exactly-once Node entry for one Wait occurrence.

If Host and Runtime use separate persistence stores, the implementation MUST use durable inbox/outbox and idempotent commands. It MUST NOT claim a cross-store atomic transaction unless the chosen persistence architecture provides one.

## 10. 5GC reference mapping — TS 23.502 Step 15/17

For the conventional SMF-owned initial PDU Session flow:

1. Step 11 Namf_Communication_N1N2MessageTransfer is the triggering outbound Operation.
2. Before Step 11 is dispatched, Runtime arms the expected Step 15 Wait for the same Run. The Integration binding uses the exact smContextRef established by Step 3 Nsmf_PDUSession_CreateSMContext and returned by the Step 5 successful response's Location resource URI.
3. AMF later sends Step 15 Nsmf_PDUSession_UpdateSMContext Request.
4. The Integration ingress adapter authenticates AMF, validates the exact pinned TS 29.502 API artifact, normalizes path/body/media parts and derives a unique correlation to the armed Wait.
5. Host durably buffers/relays the normalized delivery. Runtime resolves the opaque expectedIngressRef, accepts the event and resumes the same Run at update-sm-context; the request becomes update-sm-context.wait.output.
6. The Agent executes the declared logical SMF Operation using the explicit Wait output. Any supplementary read-only SMF Context Observation remains in that same Node after the Operation and before its Postcondition.
7. The Postcondition checks the appropriate RAN adoption and SMF business facts. The successful route proceeds to N4 Session Modification.
8. The paired Step 17 Nsmf_PDUSession_UpdateSMContext Response is fulfilled when the modify-n4-session response boundary is committed, after required N4 Session Modification and before unrelated later Procedure work.

The exact service-operation name is UpdateSMContext. In the TS 29.502 OpenAPI artifact, the corresponding operationId spelling is UpdateSmContext; the operation is POST /sm-contexts/{smContextRef}/modify under the nsmf-pdusession API. These are distinct names at different layers. The Integration export MUST pin the exact release/API artifact digest and MUST describe JSON and supported multipart/binary request forms. This draft does not select a 3GPP release.

This is a conventional 3GPP-facing SMF model. It MUST NOT expose implementation-specific SMF module names or describe AMF/(R)AN/UE actions as SMF-owned Operations. It MUST NOT query for an SM Context that has not yet been created merely to arm the later Step 15 Wait. SUPI alone and invented ueRef are not substitutes for the exact smContextRef binding in this flow.

## 11. New static diagnostics

The following are proposed future-revision diagnostics. They do not alter the v1alpha4 diagnostic index. Each is a distinct (Code, Phase) identity with Phase=C_STATIC, severity ERROR and build-blocking behavior.

| Code | Trigger |
|---|---|
| WAIT_DECLARATION_INVALID | Required Wait field missing; selector field empty/wrong type; Wait object shape invalid |
| WAIT_TIMEOUT_INVALID | Timeout is not a positive fixed duration in the exact accepted lexical subset |
| WAIT_INGRESS_EXPORT_NOT_FOUND | No exact trusted Ingress Operation export matches the selector in declared dependency snapshots |
| WAIT_INGRESS_EXPORT_AMBIGUOUS | More than one trusted Ingress Operation export matches the selector |
| WAIT_CORRELATION_BINDING_INVALID | Correlation cannot be derived before the trigger; matching is not unique; generation/stale-delivery safety cannot be proven; an incoming path is not covered |
| WAIT_TIMEOUT_ROUTE_INVALID | TIMEOUT is missing, an extra Wait route key is present, the target is not a NodeId or permitted stopping terminal, or a forbidden terminal is selected; an undeclared NodeId uses CONTROL_FLOW_DANGLING |
| WAIT_NODE_STAGE_REQUIRED | Wait-bearing Node declares none of the four business stages |
| WAIT_RESPONSE_BOUNDARY_INVALID | response.after is unknown/unreachable, a normal accepted path bypasses it, a success terminal occurs before it, or the export-required later boundary is omitted |
| WAIT_RESPONSE_MAPPING_INVALID | A body-bearing response has no declared typed Producer-source mapping or the mapping does not supply every required response field; undeclared/unavailable paths and ordinary Schema incompatibility use their existing SourcePath/type diagnostics |

Existing diagnostics are reused for existing categories:

- malformed YAML and duplicate keys: YAML_PARSE_ERROR;
- unknown fields: UNKNOWN_FIELD;
- malformed Node/route graph and cycles: existing CONTROL_FLOW_DANGLING, CONTROL_FLOW_CYCLE and applicable graph diagnostics;
- undeclared Wait output or response-result Producer property: SOURCE_PATH_INVALID;
- Wait output unavailable on a path: SOURCE_NOT_AVAILABLE;
- ordinary Producer/Consumer type mismatch, including response-result Schema incompatibility: INPUT_TYPE_MISMATCH or the applicable existing type diagnostic;
- invalid dependency identity, Owner identity or Schema: the existing dependency/Schema diagnostics.

WAIT_TIMEOUT is a control outcome, not a diagnostic. EVENT_RECEIVED is an implicit control edge, not an Outcome or diagnostic. Event arrival MUST NOT be represented by PASS, SUCCEEDED, UNKNOWN, FAILED or OUTCOME_UNKNOWN.

At Runtime, malformed, unauthenticated, unsupported-version, unsupported-media or schema-invalid wire deliveries are rejected/quarantined by Integration and do not satisfy/reset the Wait. Ambiguous, unknown, stale or invalidated references are rejected/quarantined at the Integration/Host/Runtime boundary. These delivery dispositions are not Skill Stage Outcomes and MUST NOT be author-routable. Exact Runtime/Integration diagnostic identifiers belong to their separately versioned contracts.

## 12. Minimum conformance matrix

The following semantic cases are REQUIRED for future language/Host/Runtime/Integration conformance. They are design test identifiers, not additions to the v1alpha4 E01–E120 set.

| Case | Input / condition | Required result |
|---|---|---|
| EW-001 | Valid event after registration and after Node activation | Same Run resumes once; wait.output is available before first business stage |
| EW-002 | Valid event after registration but before target Node activation | Host durably buffers it; consume only if that exact Node is selected |
| EW-003 | Event before any matching registration | Never create a new Invocation or attach it to a future Wait |
| EW-004 | Invalid peer, API version, media type or normalized request Schema | Integration rejects; Wait remains pending and timer is not reset |
| EW-005 | Unsupported multipart/binary part | Reject/quarantine unless exact pinned export defines its normalized representation |
| EW-006 | Two active Runs match the same protocol correlation | Reject/quarantine as ambiguous; never choose newest |
| EW-007 | Prior Wait times out and later Wait reuses resource identity | Stale prior delivery cannot satisfy later Wait; require wire discriminator or proven single-flight/tombstone rule |
| EW-008 | Event and Wait timeout race | Exactly one durable atomic winner |
| EW-009 | Global Invocation deadline/cancellation wins first | Apply global stop semantics; do not route TIMEOUT |
| EW-010 | Duplicate delivery after event acceptance | Idempotent disposition; no second Node entry |
| EW-011 | Delivery arrives after TIMED_OUT, INVALIDATED or CANCELLED | Cannot reopen Wait or populate wait.output |
| EW-012 | wait.output is referenced on a timeout/bypass path | Compiler emits SOURCE_NOT_AVAILABLE |
| EW-013 | Wait Node has no business stage | Compiler emits WAIT_NODE_STAGE_REQUIRED |
| EW-014 | Wait timeout route targets SUCCEEDED | Compiler emits WAIT_TIMEOUT_ROUTE_INVALID |
| EW-015 | Wait selector resolves to zero/multiple exports | Compiler emits exact not-found/ambiguous diagnostic |
| EW-016 | One incoming path cannot derive correlation before trigger | Compiler emits WAIT_CORRELATION_BINDING_INVALID |
| EW-017 | Multiple incoming paths resolve to different Ingress exports/Schemas | Compiler rejects; authors must use distinct Wait Nodes |
| EW-018 | response.after is bypassed by a normal accepted path | Compiler emits WAIT_RESPONSE_BOUNDARY_INVALID |
| EW-019 | Accepted path terminates early with a mapped failure disposition | Integration emits the declared failure response; no response is fabricated by Runtime |
| EW-020 | Body-bearing paired response lacks typed Producer mapping | Compiler emits WAIT_RESPONSE_MAPPING_INVALID |
| EW-021 | Bodyless paired response uses a declared bodyless status | Response may complete without a response-result Producer |
| EW-022 | Process restarts after delivery persistence but before Runtime notification | Durable relay/recovery delivers same deliveryRef; no new Invocation |
| EW-023 | Process restarts after event acceptance but before Agent Node execution | Runtime checkpoint resumes the same Node exactly once |
| EW-024 | Process restarts after response boundary commit but before protocol response delivery | Host/Integration recover the exact response obligation or apply explicit failure policy |
| EW-025 | Wait is used as an Observation polling loop | Non-conforming; Event Wait and Evidence Wait remain distinct |
| EW-026 | Timeout uses a malformed, fractional, zero, calendar-month or leading-zero duration | Compiler emits WAIT_TIMEOUT_INVALID |
| EW-027 | Declared timeout exceeds the deployment's published maximum | Host admission rejects before Invocation creation with WAIT_DURATION_LIMIT_EXCEEDED; no clamping |
| EW-028 | Body-bearing response mapping selects wait.output, Context or raw request data | Compiler emits WAIT_RESPONSE_MAPPING_INVALID |
| EW-029 | response.after names an unknown or unreachable Node | Compiler emits WAIT_RESPONSE_BOUNDARY_INVALID |
| EW-030 | Event is accepted but the Contract-referenced global Precondition has not passed on every incoming path | Wait edge does not establish the gate; protected Mutation and success remain blocked |
| EW-031 | Integration cannot acknowledge expected-ingress arming before the triggering Operation | Runtime MUST NOT dispatch the triggering Operation; no send-first/correlate-later fallback |
| EW-032 | Wait routes mapping or TIMEOUT key is missing | Compiler emits WAIT_TIMEOUT_ROUTE_INVALID |
| EW-033 | Author declares EVENT_RECEIVED or another key under wait.routes | Compiler emits WAIT_TIMEOUT_ROUTE_INVALID; normal event edge remains implicit |
| EW-034 | event.source/service/operation is empty or has the wrong type | Compiler emits WAIT_DECLARATION_INVALID |
| EW-035 | wait.timeout is missing or is not a YAML string | Compiler emits WAIT_TIMEOUT_INVALID |

## 13. Publication gate

This draft is not a language release. Before normative publication, the following MUST be completed:

1. independent review of the complete amendment against the full CA-SL normative text;
2. final agreement on the logical Integration Ingress Operation export and response-result binding contract;
3. exact diagnostic identities and messages added to the next-version diagnostic index;
4. positive/negative conformance fixtures for EW-001–EW-025, including exact expected diagnostics;
5. cross-review against the package-scoped Integration Ingress Operation export contract in [ca-skills PR #62](https://github.com/odango-chan/ca-skills/pull/62) and the Generic Host inbound-event continuation contract in [ca-agent-demo PR #210](https://github.com/odango-chan/ca-agent-demo/pull/210);
6. a separately approved language version identifier and release decision.

Until then, v1alpha4 remains the only applicable published authoring contract. No implementation or product-conformance claim follows from this draft.
