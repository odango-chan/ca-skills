# Integration Ingress Operation Export — Contract Draft

**Status:** Design / contract draft; not released or frozen.  
**Applies to:** The post-v1alpha4 CA-SL Node-entry Event Wait model.  
**Related language draft:** [CA-SL Node-level Event Wait normative amendment](https://github.com/odango-chan/ca-skills/pull/61).  
**Related semantic baseline:** [Node-level Event Wait design](https://github.com/odango-chan/ca-skills/pull/60).  
**Related Host boundary:** [Generic inbound-event continuation contract](https://github.com/odango-chan/ca-agent-demo/pull/210).

This document defines the proposed package-owned Integration Ingress Operation export consumed by a Skill Compiler and the generic Host/Runtime continuation path. It does not amend CA-SL v1alpha4, define a global event registry, or claim that any Integration adapter currently conforms.

The keywords MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT and MAY are normative within this draft.

## 1. Purpose and design constraints

An Ingress Operation export is a trusted, version-pinned contract published by the Integration Owner responsible for one inbound protocol operation. It binds:

1. exact source NF, service and service-operation identity;
2. pinned source API artifact and exact wire operation;
3. peer authentication and protocol authorization requirements;
4. source request validation and one normalized request Schema;
5. deterministic normalization of path, query, body and supported multipart/binary parts;
6. pre-dispatch correlation bindings to exact triggering ToolCatalog Operations, or to admitted Invocation Context for a start Wait;
7. duplicate, stale-delivery and generation-reuse rules;
8. an optional paired protocol response, its deadline, typed result contract and response mapping.

The export is dependency-owned data, not Skill-authored configuration and not a second authoring language.

The following boundaries are REQUIRED:

- **Integration** owns protocol authentication, API/release selection, wire parsing, source-schema validation, normalization, protocol correlation derivation, protocol deduplication and response encoding.
- **Generic Host** owns durable generic delivery, opaque registration/delivery handles, inbox/outbox relay and private response-obligation records. It does not parse protocol payloads or derive protocol identity.
- **Runtime** owns the authoritative ExpectedIngress registry, exact Run/Node/Wait occurrence, event-versus-timeout arbitration, checkpoint and same-Run continuation.
- **Tool Owner** owns callable Operation/Observation behavior, business results and Evidence.
- **Skill** owns its Procedure and explicit business dataflow. It does not copy the protocol request Schema or declare transport correlation handles.

The export MUST NOT contain credentials, private keys, bearer tokens, client secrets, transport connection handles, Run IDs, Wait occurrence IDs, Host-private references or deployment-specific secret values.

## 2. Identity, ownership and discovery

### 2.1 Export kind

The proposed standalone export shape is:

~~~yaml
apiVersion: connectionagent.io/ingress-operation/v1alpha1
kind: IngressOperation
metadata:
  id: urn:connectionagent:ingress:example:operation:v1
  owner: urn:connectionagent:owner:example-integration
  adapter: example.integration.inbound
spec: {}
~~~

The proposed apiVersion is for this Integration contract family only. It does not assign or imply the next CA-SL language version. The contract remains unpublished until its independent review and release gate pass.

Each file declares exactly one IngressOperation. An Integration package MAY publish multiple such files. No global IngressCatalog, EventCatalog or author-facing event registry is introduced.

The physical file path is non-semantic. The Compiler discovers standalone IngressOperation documents by their exact apiVersion and kind within declared dependency snapshots, subject to package file admission rules. The package MUST NOT rely on directory or filesystem ordering.

### 2.2 Trusted ownership

metadata.id MUST be a stable, non-empty export identity unique within the dependency snapshot. metadata.owner MUST identify the Integration Owner. metadata.adapter MUST identify the Integration-owned runtime adapter implementation.

These fields are not trusted merely because they occur in the export. The Compiler MUST validate the export through the same trusted dependency snapshot, Stable Package ID and Owner-binding process used for ToolCatalog and Schema exports under CA-SL `34.0 and its applicable appendices.

For a multi-Owner dependency snapshot, the trusted caller MUST supply exact (exportKind, exportId) -> owner attribution for the IngressOperation export. Missing or ambiguous attribution fails closed. The export's declared Owner MUST agree with the trusted attribution. A package cannot self-authorize an Owner identity.

### 2.3 Resolution from Skill source

A Wait declaration identifies an event by the exact triple:

~~~yaml
wait:
  event:
    source: AMF
    service: Nsmf_PDUSession
    operation: UpdateSMContext
~~~

The Compiler searches only immutable snapshots selected by the Skill's declared dependency aliases. It MUST compare all three fields exactly, including case and punctuation.

Resolution MUST produce exactly one matching IngressOperation export across those snapshots. Zero matches and multiple matches are distinct build-blocking diagnostics. The Compiler MUST NOT:

- search globally installed adapters or unlisted dependency snapshots;
- infer an export from a ToolCatalog Operation with a similar name;
- infer source NF identity from an inbound body or unauthenticated header;
- select the newest export or use file ordering as a tie-breaker;
- use the OpenAPI operationId in place of the 3GPP service-operation name.

metadata.id is the exact identity of the resolved export recorded in the build/link result. The author-facing event triple is the selector; the export ID is not a replacement for that triple.

### 2.4 Relationship to ToolCatalog

IngressOperation is a distinct dependency export kind, not a ToolCatalog callable and not a Capability member. It represents an inbound protocol boundary, not an action the Skill can dispatch.

The outbound Operation that may trigger a later inbound event remains an ordinary ToolCatalog Operation with its own Owner, Input/Output Schemas, Effect and Capability authorization. The IngressOperation export references that exact ToolCatalog callable identity only as trusted trigger metadata. It does not grant permission to invoke the Operation.

An Integration adapter MAY be implemented by the same deployable component as a Tool adapter. That deployment choice does not merge the public contract kinds or their authorization semantics.

## 3. Logical export structure

### 3.1 Required top-level shape

The logical export MUST contain apiVersion, kind, metadata.id, metadata.owner, metadata.adapter, spec.event, spec.protocol, spec.authentication, spec.request and spec.correlation. spec.response is optional.

Unknown top-level or nested fields MUST be rejected by the export contract version's closed-schema rule. No extension field is silently ignored.

### 3.2 Event identity

spec.event MUST contain exactly:

| Field | Meaning |
|---|---|
| source | Canonical 3GPP peer NF type, such as AMF |
| service | Exact 3GPP service name, such as Nsmf_PDUSession |
| operation | Exact 3GPP service-operation name, such as UpdateSMContext |

source MUST equal the authenticated peer NF type produced by Integration authentication. service and operation identify the 3GPP service interface. They are not inferred from OpenAPI operationId, URL path or a Skill-local label.

### 3.3 Protocol provenance

spec.protocol MUST identify:

- normative source specification and exact release;
- API name and API URI version;
- exact OpenAPI artifact path within the immutable Integration dependency snapshot;
- artifact digest computed under the selected BuildRequest snapshot framing;
- exact OpenAPI operationId, HTTP method and path template;
- request media types and source Schema references;
- each supported protocol response status, media type and source Schema, when a paired response exists.

The source OpenAPI artifact MUST be present in the same immutable dependency snapshot as the IngressOperation export. A URL alone is not an artifact identity. The adapter MUST NOT fetch a moving upstream API document at runtime to decide the contract.

The 3GPP release, API URI version and OpenAPI artifact digest are separate attributes. None may be inferred from the others. The API URI version is the version used in the actual API root/path; the 3GPP release identifies the normative publication; the digest pins the exact OpenAPI bytes.

## 4. Request validation and normalization

### 4.1 Source request contract

For each accepted wire media type, spec.protocol.request MUST identify the source request Schema in the pinned OpenAPI artifact or an exact source Schema export included in the same dependency snapshot. The source reference MUST resolve uniquely. Integration MUST validate the actual request against the selected source contract before normalization.

The accepted media-type set MUST be explicit. Matching rules for parameters and multipart boundaries MUST be defined by the export version and exact protocol contract. The adapter MUST NOT accept a broader media-type family merely because the parser can decode it.

Unsupported API versions, methods, paths, media types, request encodings and source-schema variants MUST be rejected or quarantined. They MUST NOT be coerced into the nearest supported contract.

### 4.2 Normalized request Schema

spec.request.normalizedSchema MUST identify one exact closed JSON Schema export in the CA-SL supported Schema subset. The export MUST include its exact Schema $id and the snapshot-bound digest of the Schema bytes.

The normalized Schema is the only request data contract exposed to the Skill as NodeId.wait.output. It MUST:

- be a closed object with explicitly declared properties;
- use stable field names compatible with the CA-SL SourcePath Identifier grammar;
- exclude Host/Runtime lifecycle and transport metadata;
- distinguish protocol business input from correlation-only values;
- define binary content references as typed immutable references, not raw transport handles;
- contain every required normalized property produced by the mapping.

The Compiler validates this Schema under normal Owner Schema resolution and supported JSON Schema rules. Integration validates and materializes values conforming to it.

### 4.3 Deterministic normalization mapping

The export MUST define a deterministic mapping from each accepted wire representation into the normalized request Schema. Each mapping entry MUST identify one normalized target property using a JSON Pointer relative to the normalized object, one exact source selector, and one permitted deterministic conversion where required.

The source selector is one of:

| Source kind | Selector |
|---|---|
| path | Exact OpenAPI path-parameter name |
| query | Exact OpenAPI query-parameter name |
| header | Exact protocol header name; permitted only when explicitly declared as business input |
| json-body | JSON Pointer into the validated JSON request body |
| multipart-json | Exact multipart part name plus JSON Pointer into that validated JSON part |
| multipart-binary | Exact multipart part name identifying one validated binary part |

The conversion set MUST be closed and versioned. The initial profile permits only identity, strict decimal parse-integer, strict decimal parse-number, strict lowercase parse-boolean and binary-content-ref. Conversion MUST be deterministic and lossless for the target type. Invalid or lossy conversions reject the request; no locale-sensitive parsing, rounding, truncation, implicit stringification or arbitrary CEL/Python mapping is allowed.

Each required normalized property MUST have exactly one mapping for each accepted media-type representation. Duplicate target mappings, conflicting source mappings or an unmapped required property invalidate the export. Unmapped source fields and unrecognized multipart parts MUST be rejected unless the pinned source contract explicitly marks them ignorable and the export records that exact exception. The adapter MUST NOT silently discard a part that may carry business meaning.

The mapping MUST be traceable to the pinned source artifact and source Schema. It is not a second general-purpose transformation language.

### 4.4 Multipart and binary parts

For each accepted multipart media type, the export MUST enumerate exact permitted part names, content types, required/optional status, source Schema for JSON parts, and maximum byte size for binary parts.

A binary part MAY be normalized to a typed immutable content reference only when the export declares:

- exact normalized reference Schema;
- content digest algorithm (SHA-256 in the initial profile);
- byte length and media type;
- immutable storage and access-control semantics;
- retention lifetime covering the Run's permitted processing and recovery window.

The content reference MUST be opaque and protected. It MUST NOT be a reusable public URL, filesystem path or raw transport handle. The Agent/Tool may consume it only through an explicitly authorized Tool contract. If Host/Integration cannot guarantee integrity, access control and retention, the request MUST be rejected or quarantined.

The normalized request MUST NOT inline large binary payloads into the Runtime event envelope. Host transports protected immutable references; Runtime exposes only the typed normalized reference defined by the Schema.

### 4.5 Authentication and authorization

spec.authentication.peer MUST identify the expected NF type and a trusted peer-identity policy export. spec.authentication.authorizationPolicy MUST identify the policy used to authorize that peer to invoke this exact API operation.

Integration MUST establish peer identity from an authenticated transport/security context, such as the deployment's configured SBI security mechanism. It MUST NOT infer peer identity from a JSON property, path parameter, arbitrary HTTP header or caller-supplied label.

The export declares policy identities and required claims; it MUST NOT contain credentials or prescribe one deployment's secret material. Integration MUST validate both peer identity and operation authorization before request normalization is accepted for correlation. Failed authentication/authorization MUST NOT satisfy, reset or reveal an armed Wait.

## 5. Correlation and pre-dispatch trigger bindings

### 5.1 Correlation key

spec.correlation.requestKey MUST declare an ordered, non-empty tuple of JSON Pointers into the normalized request object. The tuple identifies the protocol resource/transaction relevant to one Wait. Integration derives the tuple only after authentication and source validation.

The correlation key is not necessarily a UE identity. SUPI alone MUST NOT be assumed sufficient. A Skill or Host MUST NOT invent ueRef or another synthetic identity. The key MUST use the exact public protocol/resource identity and any trusted Integration association required by the interface.

### 5.2 Trigger Operation identity

For a non-start Wait Node, the export MUST declare every permitted triggering ToolCatalog Operation callable that can cause the inbound event. Each trigger identity MUST include:

- Stable Package ID of the Tool dependency;
- trusted Tool Owner identity;
- exact ToolCatalog callable ID;
- kind: operation.

The trigger MUST resolve to exactly one trusted ToolCatalog Operation export in the Skill's declared dependency snapshots. Observation queries, Capability IDs, display names, free-form labels and network addresses are not valid trigger identities.

The trigger declaration is not an invocation grant. The ordinary Skill Contract Capability grant and Runtime admission rules remain authoritative for dispatching that Operation.

### 5.3 Pre-dispatch binding

For each permitted trigger, the export MUST declare a complete one-to-one binding from the trigger Operation's typed Input Schema to the normalized request correlation key:

- triggerInputPath: JSON Pointer into that exact ToolCatalog Operation Input Schema;
- requestPath: JSON Pointer into the normalized request Schema.

Every member of requestKey MUST be covered exactly once. Each trigger binding MUST resolve to the same requestKey shape. The Compiler MUST verify that each trigger input path exists, is required or otherwise proven present before dispatch, and is statically assignable to the corresponding normalized request field.

Runtime materializes the binding from the already validated Operation arguments immediately before dispatch. It MUST NOT depend on the trigger Operation's output, because the external event may arrive before that output is available. The exact materialized values are passed to Integration as an opaque typed correlation binding through Host. Host and Integration MUST NOT receive runId or waitOccurrenceRef.

For multiple incoming paths to one Wait Node, every path MUST identify one permitted trigger and provide the same complete correlation mapping. A path without a matching trigger is invalid. Different event identities, API versions, normalized Schemas or incompatible correlation contracts require distinct Wait-bearing Nodes.

### 5.4 Start-Node Context binding

A Wait-bearing Procedure start Node has no predecessor trigger Operation. For this case only, the export MAY declare startContextBindings, each containing:

- exact trusted Host Context Schema $id;
- JSON Pointer into that Schema;
- matching normalized request requestPath.

Every requestKey member MUST be covered exactly once. The Compiler MUST resolve the exact Host Context Schema through the declared trusted dependency and verify that the selected field is present and type-compatible at Invocation admission.

Runtime materializes the correlation binding from already-admitted Invocation Context and arms the Wait before activating the start Node. The export MUST NOT cause a new network Observation or a query for a resource that does not yet exist merely to construct the binding.

A start Node with neither complete startContextBindings nor a permitted pre-existing trusted binding is not linkable.

### 5.5 Generation safety and stale delivery

The export MUST define how Integration distinguishes a request for the currently armed Wait from a duplicate or a request belonging to an expired generation.

The initial profile permits exactly two strategies:

1. **wire-discriminator** — the protocol supplies a request/transaction/generation discriminator. The export identifies its exact normalized request path and proves the discriminator is unique within the declared resource scope and retained for duplicate classification.
2. **single-flight-tombstone** — the protocol has no sufficient wire discriminator. The export declares exact resource-key paths, a finite maximum request lifetime, a clock-skew allowance, and a tombstone retention not shorter than their sum. At most one armed Wait may exist for the same resource key. After timeout, cancellation or invalidation, that key cannot be re-armed until the tombstone expires. If the protocol cannot provide a finite maximum request lifetime or Integration cannot enforce this exclusion, the binding is invalid and MUST fail closed.

A private Runtime generation number that is not distinguishable at the protocol boundary is not, by itself, stale-delivery protection.

### 5.6 Duplicate and unmatched requests

The export MUST declare the protocol request identity used for duplicate classification. It MUST distinguish:

- repeated delivery of the same protocol request;
- a distinct valid request for the same resource;
- a late request for an expired/inactivated Wait;
- an authenticated request for which no armed Wait exists;
- an ambiguous request matching more than one armed Wait.

Integration creates one stable deliveryRef per accepted normalized delivery identity. Retries of the same request MUST reuse the same identity. Host deduplicates deliveryRef; Runtime independently enforces one atomic acceptance per Wait occurrence.

Unknown, unmatched, stale or ambiguous requests MUST be rejected or quarantined according to the protocol contract. They MUST NOT create an Invocation, be assigned to the newest Run, or be attached to a later Wait. The protocol response to such requests is Integration-owned.

## 6. Paired protocol response

### 6.1 Optional response contract

If the inbound protocol operation has no paired response obligation, spec.response MUST be omitted. If it has a paired response, spec.response MUST declare the protocol response contract, response deadline behavior, response boundary requirement, success response and failure mappings.

The presence of spec.response is the sole source of truth for whether responseObligationRef is required in the Host delivery envelope. Host MUST NOT fabricate a response obligation for an unpaired request.

### 6.2 Boundary policy

spec.response.boundary.minimum MUST be one of:

- wait-node — completion of the Wait-bearing Node is a permitted response boundary; wait.response.after MAY be omitted or may name a later Node;
- later-node — the response MUST follow a later business Node; wait.response.after is REQUIRED and MUST NOT identify the Wait-bearing Node.

The Compiler checks the Skill-authored wait.response.after against this Integration policy and proves that the selected Node post-dominates the event-accepted edge except for explicitly mapped early terminal failures. The export does not name a Skill NodeId.

### 6.3 Response-result contract

For a body-bearing success response, the export MUST declare:

- result.producer: operation or observation;
- result.schema: one exact Integration-owned closed Schema $id and snapshot-bound digest;
- result.mapping: deterministic field mappings from that Schema to the exact protocol response Schema.

The export MUST NOT declare NodeId.operation.output, NodeId.observation.output, arbitrary SourcePaths or any other Skill-specific identifier. It does not know the Skill's Procedure graph.

At link time, the Compiler resolves wait.response.after (or the default Wait-bearing Node boundary), selects the corresponding operation.output or observation.output of that boundary Node according to result.producer, and verifies that the selected stage exists and its Output Schema is assignable to result.schema. The selected Producer output is the response result. If the boundary Node needs values from earlier Nodes, the Skill MUST pass those values through ordinary Operation/Observation arguments and the boundary Producer MUST expose the response-ready typed output. No implicit lookup of earlier outputs or "latest result" is allowed.

The response mapping MUST use exact source and target JSON Pointers. The initial profile permits identity copies only; source and target types MUST be statically assignable. Every required protocol response field MUST be supplied. Missing fields, unknown paths, incompatible types or ambiguous mapping reject the export/link. Arbitrary scripts, CEL expressions, raw request fields, wait.output, Host metadata, Context paths and terminal Run summaries MUST NOT be used to synthesize a body-bearing response.

A bodyless success response declares its exact status and MUST omit result. A body-bearing success response MUST declare result. The contract MUST NOT permit a runtime choice between body-bearing and bodyless success variants unless the choice is itself a separately declared, typed and statically resolvable response disposition.

### 6.4 Failure responses

For each early terminal disposition that may occur before the selected response boundary (FAILED, UNRESOLVED, SAFE_STOPPED), the export MUST either:

- declare an exact permitted protocol failure status and a bodyless response, if allowed by the protocol; or
- declare a deterministic Integration-owned failure response mapping to the protocol's error Schema.

A failure mapping MUST NOT expose Host-private IDs, Run IDs, correlation keys, raw request data or internal diagnostics. It may expose only protocol-approved error classifications and fixed/typed fields declared by the Integration contract. The Compiler MUST reject an early terminal path when no mapping exists.

A failure response is not a successful business response and does not establish Goal proof. Runtime preserves the original Run outcome and resource responsibility; Integration only fulfills the protocol response obligation.

### 6.5 Response deadline and recovery

Integration MUST declare how it obtains the inbound protocol response deadline and how it handles expiry. That deadline begins after event acceptance and is independent of the pre-event Wait timeout.

Expiry MUST NOT be converted into the Skill's TIMEOUT route or a business Stage Outcome. Integration applies its protocol failure mapping; Host/Runtime preserve the accepted-event checkpoint and unresolved business/resource responsibility. Any Run cancellation uses the existing global cancellation semantics.

The transport response handle is Integration-private and is not assumed to survive process restart. Integration and Host MUST durably retain enough response-obligation state to retry or recover the exact response, or apply the declared explicit failure policy. Runtime receives only the opaque expectedIngressRef association and typed response-ready result; it never receives responseObligationRef.

## 7. Runtime/Host logical envelope boundary

The following are logical ports, not frozen method names or physical DTOs:

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

expectedIngressRef is created by Runtime and bound privately to the exact Run, Node and Wait occurrence. Host and Integration carry it only as an opaque handle. Integration MUST NOT receive or resolve a Run ID or Wait occurrence ID.

ingressContractRef identifies the exact trusted IngressOperation export by package snapshot and export ID. deliveryRef is an Integration-owned idempotency identity. normalizedPayloadRef is a protected immutable reference to the normalized request value. responseObligationRef exists if and only if the export declares a paired response. responseResultRef is present only for a body-bearing response disposition.

Delivery is durable at-least-once plus idempotent acceptance. No distributed exactly-once transport guarantee is implied. Runtime's authoritative state transition and durable checkpoint enforce exactly-once Node entry for one Wait occurrence.

If Host and Runtime use separate persistence stores, the implementation MUST use durable inbox/outbox and idempotent commands. It MUST NOT claim a cross-store atomic transaction unless the selected persistence architecture provides one.

## 8. Compiler linking and validation

The Compiler MUST perform the following checks before accepting a Wait-bearing Skill:

1. Resolve exactly one trusted IngressOperation by the exact event triple in declared dependency snapshots.
2. Validate package snapshot digest, Stable Package ID, Owner attribution, export identity and closed export shape.
3. Verify source OpenAPI artifact path/digest, API release/version, operationId, method/path and media-type references.
4. Resolve and validate the normalized request Schema under the CA-SL supported JSON Schema subset.
5. Validate all source-to-normalized mappings, including required properties, conversions, multipart parts and binary reference Schema.
6. Validate peer identity and authorization policy references against trusted Integration exports.
7. Resolve every trigger identity to one exact ToolCatalog Operation export; validate trigger Input Schema paths and pre-dispatch binding completeness.
8. For a start Wait, validate exact Host Context Schema and complete startContextBindings.
9. Validate generation safety, finite lifetime/tombstone constraints and duplicate identity rules.
10. If paired response exists, validate response boundary policy, response-result Producer kind, response Schema assignability, response field mappings and all permitted early terminal mappings.
11. Include the Wait gate, event-accepted edge, TIMEOUT edge and response boundary in ordinary Procedure reachability, cycle, global Precondition and final Goal proof analysis.

The Compiler MUST NOT execute the Integration adapter, call the network, inspect live protocol messages or use an inbound payload to resolve a missing contract during static linking.

## 9. Failure and diagnostic categories

These are proposed Integration contract/linking diagnostics. They are not additions to the v1alpha4 diagnostic index.

| Code | Phase | Meaning |
|---|---|---|
| INGRESS_EXPORT_INVALID | C_STATIC | Export shape, unknown field, missing required logical property or closed-schema violation |
| INGRESS_EXPORT_NOT_FOUND | C_STATIC | No exact export matches the Wait event triple |
| INGRESS_EXPORT_AMBIGUOUS | C_STATIC | More than one exact export matches the Wait event triple |
| INGRESS_ARTIFACT_INVALID | C_STATIC | Source OpenAPI artifact path/digest/operation identity is missing, mismatched or unresolvable |
| INGRESS_NORMALIZATION_INVALID | C_STATIC | Normalized Schema or source-to-normalized mapping is incomplete, ambiguous or not type-safe |
| INGRESS_AUTH_POLICY_INVALID | C_STATIC | Peer identity or authorization policy reference is absent, untrusted or inconsistent |
| INGRESS_TRIGGER_BINDING_INVALID | C_STATIC | Trigger Operation identity or pre-dispatch input binding cannot be resolved or proven complete |
| INGRESS_GENERATION_POLICY_INVALID | C_STATIC | Correlation cannot uniquely distinguish concurrent or successive Wait occurrences |
| INGRESS_RESPONSE_CONTRACT_INVALID | C_STATIC | Paired response boundary/result contract or failure mapping is invalid |
| INGRESS_DELIVERY_REJECTED | R_RUNTIME | Wire request fails authentication, protocol, media-type, source-schema or normalization validation |
| INGRESS_DELIVERY_UNMATCHED | R_RUNTIME | Authenticated request has no unique armed expected ingress |
| INGRESS_DELIVERY_STALE | R_RUNTIME | Request belongs to an expired, invalidated or tombstoned generation |
| INGRESS_DELIVERY_DUPLICATE | R_RUNTIME | Delivery repeats an already accepted protocol request; idempotent disposition |
| INGRESS_RESPONSE_EXPIRED | R_RUNTIME | Paired response deadline expired; Integration failure policy applies, never the Skill Wait TIMEOUT route |

Exact message text, source locations and diagnostic index allocation are owned by the separately versioned Integration export and CA-SL diagnostic contracts. A runtime delivery disposition MUST NOT become an author-routable Stage Outcome.

## 10. 5GC Step 15/17 reference shape

The conventional SMF-owned flow uses the AMF-originated Nsmf_PDUSession.UpdateSMContext request as the inbound event. The Integration export pins the exact TS 29.502 release and OpenAPI artifact used by the deployment. This example deliberately leaves the release and digests as placeholders; it does not assert that a particular release is deployed.

~~~yaml
apiVersion: connectionagent.io/ingress-operation/v1alpha1
kind: IngressOperation
metadata:
  id: urn:connectionagent:ingress:nsmf-pdusession:update-sm-context:v1
  owner: urn:connectionagent:owner:smf-integration
  adapter: smf.integration.nsmf-pdusession
spec:
  event:
    source: AMF
    service: Nsmf_PDUSession
    operation: UpdateSMContext

  protocol:
    standard: 3GPP TS 29.502
    release: <deployment-pinned-release>
    api:
      name: nsmf-pdusession
      uriVersion: v1
      openapi:
        artifact: OpenAPI/TS29502_Nsmf_PDUSession.yaml
        digest: sha256:<pinned-artifact-digest>
        operationId: UpdateSmContext
        method: POST
        path: /sm-contexts/{smContextRef}/modify
    request:
      mediaTypes:
        - application/json
        - multipart/related
      sourceSchemas:
        - mediaType: application/json
          ref: "#/components/schemas/SmContextUpdateData"
        - mediaType: multipart/related
          ref: "#/components/schemas/SmContextUpdateData"

  authentication:
    peer:
      nfType: AMF
      identityPolicy: urn:connectionagent:security:peer-nf:amf:v1
    authorizationPolicy: urn:connectionagent:security:authorize:nsmf-update-sm-context:v1

  request:
    normalizedSchema: urn:connectionagent:smf:ingress:update-sm-context:v1
    normalizedSchemaDigest: sha256:<pinned-normalized-schema-digest>
    mappings:
      - target: /smContextRef
        from:
          kind: path
          name: smContextRef
        transform: identity
      - target: /updateData
        from:
          kind: json-body
          pointer: ""
        transform: identity
      - target: /n1SmMessage
        from:
          kind: multipart-binary
          part: n1SmMsg
        transform: binary-content-ref
      - target: /n2SmInformation
        from:
          kind: multipart-binary
          part: n2SmInfo
        transform: binary-content-ref
    binaryContent:
      digestAlgorithm: sha-256
      immutable: true
      access: authorized-tool-only
      retention: PT10M
      maxBytes: <deployment-limit>

  correlation:
    requestKey:
      - /smContextRef
    triggers:
      - callable:
          packageId: <trusted-amf-tool-package-id>
          owner: <trusted-amf-tool-owner-id>
          kind: operation
          id: amf.communication.n1n2-message-transfer
        bindings:
          - triggerInputPath: /smContextRef
            requestPath: /smContextRef
    generation:
      mode: single-flight-tombstone
      resourceKeyPaths:
        - /smContextRef
      maxRequestLifetime: <protocol-proven-maximum>
      clockSkewAllowance: <deployment-proven-bound>
      tombstoneRetention: <at-least-the-sum-of-the-two-values>
    deduplication:
      requestIdentity:
        - /smContextRef
      canonicalRequestDigest: sha-256
      retention: <at-least-the-tombstone-retention>

  response:
    boundary:
      minimum: later-node
    deadline:
      source: authenticated-transport-deadline
    success:
      status: 200
      mediaType: application/json
      schemaRef: "#/components/schemas/SmContextUpdatedData"
      result:
        producer: operation
        schema: urn:connectionagent:smf:response-result:update-sm-context:v1
        schemaDigest: sha256:<pinned-response-result-schema-digest>
        mappings:
          - from: /smContextRef
            to: /smContextRef
    failures:
      FAILED:
        status: <protocol-permitted-failure-status>
        mapping: urn:connectionagent:smf:problem-details:failed:v1
      UNRESOLVED:
        status: <protocol-permitted-uncertain-status>
        mapping: urn:connectionagent:smf:problem-details:unresolved:v1
      SAFE_STOPPED:
        status: <protocol-permitted-safe-stop-status>
        mapping: urn:connectionagent:smf:problem-details:safe-stopped:v1
~~~

The sample is a logical shape, not a release-ready artifact. Placeholder Tool package/Owner IDs, release, digest, limits, response schemas and failure mappings MUST be replaced by trusted published values before use. triggerInputPath is a path in the triggering ToolCatalog Operation Input Schema; it is not a Skill SourcePath. The Integration export knows no Skill NodeId.

For this flow, the trigger Operation is the Step 11 Namf_Communication_N1N2MessageTransfer Tool Operation. Its already materialized input supplies the exact smContextRef used to arm the Step 15 Wait. The Integration adapter later authenticates AMF and matches the Step 15 path smContextRef to that armed binding. SUPI alone and invented ueRef are not substitutes.

The Step 17 response boundary is after the required Step 16 N4 Session Modification. boundary.minimum: later-node therefore requires the Skill to declare wait.response.after naming that later Node. The Integration contract declares only the expected response-result Schema and Producer kind; the Compiler resolves the actual operation.output of the Skill's selected boundary Node. If earlier Node data is needed, the Skill passes it explicitly through the boundary Operation arguments.

## 11. Conformance matrix

The following cases are REQUIRED for the future IngressOperation export and its linking/runtime integration. They supplement, but do not modify, the EW cases in the CA-SL Event Wait draft.

| Case | Condition | Required result |
|---|---|---|
| IE-001 | One exact event triple resolves to one trusted export | Link succeeds |
| IE-002 | No export matches the exact triple | INGRESS_EXPORT_NOT_FOUND |
| IE-003 | Two exports match the same triple across declared snapshots | INGRESS_EXPORT_AMBIGUOUS |
| IE-004 | Export Owner differs from trusted dependency attribution | Link fails closed |
| IE-005 | Source OpenAPI artifact digest differs from pinned bytes | INGRESS_ARTIFACT_INVALID |
| IE-006 | OpenAPI operationId/method/path differs from the export | INGRESS_ARTIFACT_INVALID |
| IE-007 | API release or URI version is absent or inferred from another field | INGRESS_ARTIFACT_INVALID |
| IE-008 | Wire media type is not in the exact accepted set | INGRESS_DELIVERY_REJECTED; Wait remains pending |
| IE-009 | Source request fails the pinned source Schema | INGRESS_DELIVERY_REJECTED; Wait remains pending |
| IE-010 | Required normalized property has no mapping | INGRESS_NORMALIZATION_INVALID |
| IE-011 | Two mappings write the same normalized property | INGRESS_NORMALIZATION_INVALID |
| IE-012 | Conversion is lossy, ambiguous or outside the closed conversion set | Request rejected; no normalized delivery |
| IE-013 | Unknown multipart part or unsupported binary representation arrives | Request rejected/quarantined; no silent discard |
| IE-014 | Binary reference is mutable, expired, unauthorized or digest-invalid | Request rejected; no Tool receives the reference |
| IE-015 | Peer NF identity is derived from body/header rather than authenticated context | INGRESS_AUTH_POLICY_INVALID / request rejected |
| IE-016 | Trigger callable resolves to Observation or Capability instead of Operation | INGRESS_TRIGGER_BINDING_INVALID |
| IE-017 | Trigger input path is absent, optional without presence proof or type-incompatible | INGRESS_TRIGGER_BINDING_INVALID |
| IE-018 | Trigger binding depends on trigger Operation output | INGRESS_TRIGGER_BINDING_INVALID |
| IE-019 | One incoming path has no permitted trigger binding | INGRESS_TRIGGER_BINDING_INVALID |
| IE-020 | Start Wait lacks complete trusted Host Context binding | INGRESS_TRIGGER_BINDING_INVALID |
| IE-021 | Two active Runs match one correlation key | INGRESS_DELIVERY_UNMATCHED; never select newest |
| IE-022 | Prior generation times out and a new Wait attempts to reuse its resource key before tombstone expiry | New arm rejected |
| IE-023 | Protocol has no finite maximum request lifetime and no wire discriminator | INGRESS_GENERATION_POLICY_INVALID |
| IE-024 | Duplicate delivery repeats the same protocol request | Same delivery identity; Host/Runtime idempotently accept once |
| IE-025 | Authenticated request has no armed expected ingress | INGRESS_DELIVERY_UNMATCHED; no new Invocation |
| IE-026 | Response absent but Host receives responseObligationRef | Reject invalid envelope |
| IE-027 | Response present but responseObligationRef is absent | Reject invalid envelope |
| IE-028 | Body-bearing response export declares Skill NodeId SourcePath | INGRESS_RESPONSE_CONTRACT_INVALID |
| IE-029 | Boundary Node lacks the declared operation/observation Producer | INGRESS_RESPONSE_CONTRACT_INVALID |
| IE-030 | Boundary Producer output is not assignable to response result Schema | INGRESS_RESPONSE_CONTRACT_INVALID |
| IE-031 | Required wire response field has no result mapping | INGRESS_RESPONSE_CONTRACT_INVALID |
| IE-032 | later-node response policy but wait.response.after is omitted or identifies the Wait Node | WAIT_RESPONSE_BOUNDARY_INVALID |
| IE-033 | Early terminal path has no explicit protocol failure mapping | WAIT_RESPONSE_BOUNDARY_INVALID |
| IE-034 | Response deadline expires after event acceptance | Integration applies response failure policy; never Wait TIMEOUT |
| IE-035 | Restart occurs after response boundary commit but before wire response | Host/Integration recover exact response obligation or apply explicit failure policy |

## 12. Publication gate

This contract draft is not a released export format. Before publication:

1. independently review the logical export and closed Schema against CA-SL `9, `13 and `34.0;
2. confirm exact Integration package trust/Owner attribution and discovery behavior;
3. validate source OpenAPI pinning and normalization against one real 3GPP API release;
4. validate multipart/binary reference lifecycle with the actual Integration/Host storage boundary;
5. validate pre-dispatch trigger binding against the actual Step 11 ToolCatalog Operation Input Schema;
6. validate stale-delivery/tombstone policy against the actual protocol's maximum request lifetime and retry behavior;
7. validate response-result Producer binding against the selected wait.response.after Node and exact response schemas;
8. add exact diagnostic identities/messages and positive/negative fixtures for IE-001–IE-035;
9. cross-review with CA-SL PR #61 and ca-agent-demo PR #210;
10. assign and approve the independent IngressOperation contract version and release.

Until these gates pass, this document is a design artifact only. No Integration package, Compiler, Host, Runtime or Studio conformance is implied.
