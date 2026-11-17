# CA-SL 5GC Authoring Profile — 3GPP-first Procedure and Capability Mapping

**Status:** Normative repository-level authoring profile for 5GC examples.  
**Language:** CA-SL v1alpha4, pinned at `7f84393ee8c395e4d8c39a74cb5000a1f896588d`.  
**3GPP baseline for the current PDU Session examples:** Release 19; TS 23.502 V19.9.0 for §4.3.2.2.1 and §4.4.1.2–§4.4.1.3. Supporting Stage 2/Stage 3 specifications are independently pinned in §9.1.  
**Baseline review date:** 2026-11-17. The versions are per-specification pins; Release 19 specifications do not share one common version number.  
**Effect:** This profile constrains how this repository authors 5GC Skills. It does not change the frozen CA-SL grammar or replace any 3GPP specification.

## 1. Governing principle

A 5GC Skill is authored from the **SMF point of view** and follows the standard 3GPP business procedure. It is not an independently invented workflow that happens to call 5GC-flavoured tools.

- A **Skill** expresses a stable business goal, such as fulfilling one admitted UE-requested initial PDU Session Establishment.
- Its **Procedure** expresses the complete SMF-owned business procedure for that goal. It may span multiple 3GPP protocol exchanges.
- A **Node** represents one logical 3GPP interaction step or one tightly related group of protocol exchanges, viewed from the SMF's responsibility boundary. A Node will commonly correspond to a Request/Response exchange, but the mapping is not mechanically one Node per message or one Node per internal function.
- Host ingress admission, duplicate suppression, business-instance association, Invocation lifecycle and correlation are pre-Procedure Host services, not Skill Nodes or Predicates. Under the frozen v1alpha4 model, a later inbound protocol request is correlated to the pending Owner Operation in the existing Invocation. The next-revision proposal instead correlates the request to a Node-level Wait and resumes the same Run at that target Node; it does not create a new Skill or Invocation or restart from `start`. These are version-distinct models and MUST NOT be mixed in one v1alpha4 source. A Skill's business request-profile gate belongs on the first business Node as its global Precondition; it must not be named or described as Host admission.
- A Node may contain CA-SL Precondition, Operation, Observation and Postcondition stages. The Operation is the Node's primary business action. An Observation is an optional supplementary READ stage and normally belongs in the same Node, after the Operation and before the Postcondition; it does not create a second business action.
- Do not create a standalone Observation-only Node merely to fetch facts needed by an adjacent Operation. Attach the read to the earliest suitable read-only Operation Node when it must happen before the first mutation, or to the Operation Node whose later decision needs the fresh facts. A standalone Observation-only Node is an exception requiring an independently meaningful business decision boundary and an explicit rationale; it must not be a disguised Host admission/lifecycle check.
- Reuse the Operation Result/Evidence when it already contains authoritative, correctly scoped and fresh facts. An Observation is not callback polling and must not duplicate a fact already proved by the Operation.
- A Node must not be introduced solely for a trivial implementation helper, temporary variable, local copy or one-line mapping. A separate Script Node is justified only when it represents an independently meaningful, typed SMF-local business decision/result that is consumed independently in the 3GPP procedure. It is not justified when the Script merely revalidates or reshapes data already checked at an earlier interaction, or when native SMF processing performs the local work as part of an adjacent 3GPP interaction. In this conventional PDU Session example, the former Step 8 Script only rechecked/remapped UDM subscription fields; it did not select a UPF or allocate a session address. Native Step 8 selection therefore belongs inside the SMF N4 Owner Operation that performs N4 Session Establishment, not in a separate `3GPP_LOCAL` Node. A separate CA Node is permitted when it is an independently meaningful governed Host/Owner action or a meaningful typed Script transformation required by the v1alpha4 dataflow. A standalone Observation-only Node is exceptional and must satisfy the explicit business-boundary rationale above. A CA-specific governed adapter/extension instead uses a clear `ca-` identity, is classified `CA_ADAPTER`/`CA_EXTENSION`, and points to the 3GPP interaction it supports; it must never be mistaken for a standard NF interaction.

**Do not confuse the complete Procedure with one Request/Response.** For example, TS 23.502 §4.3.2.2.1 describes the full UE-requested PDU Session Establishment procedure. Its SMF interactions include UDM subscription retrieval/subscription, PCF SM Policy Association establishment, N4 Session Establishment, N1/N2 transfer, a later Nsmf UpdateSMContext request carrying the access-network result, N4 Session Modification and the corresponding response. These are distinct interaction boundaries within one SMF business procedure.

## 2. Required traceability for every Node

Every business Node in a 5GC Procedure MUST have a traceability entry in the Skill's `SKILL.md` and a concise source comment beside the Node in `procedure.yaml`.

The traceability entry MUST state:

1. Node ID and human-readable 3GPP interaction name.
2. Exact 3GPP source: TS number, Release/version, clause, figure and step(s), where applicable.
3. Protocol direction and participating NFs (for example, SMF → UDM).
4. Canonical 3GPP service operation or protocol procedure/message (for example, `Nudm_SDM_Get`, `Npcf_SMPolicyControl_Create`, N4 Session Establishment).
5. What the SMF is responsible for before the interaction and what the response/result actually proves.
6. Whether the Node is a direct 3GPP interaction, a CA adapter around a 3GPP interaction, or a CA-only extension.

Do not add ad-hoc `3gpp`, `standard`, `step` or `mapping` fields to CA-SL YAML. v1alpha4 does not define those fields. Keep the mapping in comments and the Skill's traceability section/reference document.

## 3. Node naming

Use the canonical 3GPP procedure, service, operation or message name wherever one exists. Node IDs should be short kebab-case renderings of that name, for example:

- `get-sm-subscription-data` — `Nudm_SDM_Get`
- `subscribe-sm-data` — `Nudm_SDM_Subscribe`
- `establish-sm-policy-association` — `Npcf_SMPolicyControl_Create`
- `establish-n4-session` — N4 Session Establishment Request/Response
- `transfer-n1n2-message` — `Namf_Communication_N1N2MessageTransfer`
- `update-sm-context` — `Nsmf_PDUSession_UpdateSMContext`
- `get-sm-subscription-data` — Step 4 `Nudm_SDM_Get`, optionally carrying an entry-time SMF context-presence Observation before any mutation
- `update-sm-context` — Step 15 `Nsmf_PDUSession_UpdateSMContext`, optionally carrying a fresh post-completion SMF context Observation for the Step 16 decision
- `modify-n4-session` — N4 Session Modification Request/Response (SMF N4 Owner Operation)

These are naming examples, not a declaration that the corresponding Owner exports are already published.

Do not use implementation-only names such as `read-operation-context`, `bind-pcf-hold`, `build-n1n2-delivery` or `signal-ran` as the primary business Node name when the Node is actually representing a standard 3GPP interaction. Such helpers must be absorbed into the corresponding Owner Operation/adapter or explicitly identified as CA extensions.

## 4. SMF responsibility boundary

The Procedure MUST be described from the SMF point of view.

- Include interactions the SMF initiates or receives, including the relevant SBI and N4 boundaries.
- Do not model AMF, UE or RAN internal actions as if they were SMF-owned Operations.
- In TS 23.502 §4.3.2.2.1, the AMF↔(R)AN and (R)AN↔UE work in steps 12–14 is not an SMF service call. From the SMF point of view, the relevant result returns through the AMF's `Nsmf_PDUSession_UpdateSMContext Request` in step 15. If a CA Owner adapter wraps or observes the asynchronous access-network completion, label it as a **CA adapter** for the relevant 3GPP steps; do not rename it as a standard 3GPP service operation.
- The initial `Nsmf_PDUSession_CreateSMContext Response` in step 5 is the Integration response adapter's service exit paired with the step 3 ingress request, coordinated through the Host. It is an early response and is not, by itself, proof that the full PDU Session Establishment has completed. Do not use it as the final Goal proof.
- In the frozen v1alpha4 source model, the later `Nsmf_PDUSession_UpdateSMContext Request` in step 15 is admitted through the Host/Integration ingress boundary and matched to the exact pending Owner Operation in the existing Invocation; the Owner returns the validated access-network result and Runtime resumes that Invocation. In the next-revision proposal, step 15 instead satisfies the `wait` on the target `update-sm-context` Node: the Integration ingress adapter authenticates, validates and normalizes the inbound request and derives its correlation key; Generic Host matches the delivery to the exact existing Run/Wait; Runtime resumes the same Run at that Node; and the Agent executes its declared logical SMF Operation with the typed `wait.output`. The latter model does not require an Owner Operation to remain pending merely to receive step 15. When the subsequent N4 decision needs current SMF-owned facts not already present in the Operation Result, place the explicit read-only session-context Observation in that same Node after the Operation completes and before its Postcondition. It is a supplementary synchronous READ, not a standalone Node or callback polling. The SMF N4 Owner then performs N4 Session Modification using the validated RAN result. For the frozen v1alpha4 source model, the paired Step 17 response remains a Host/Integration service-exit obligation and must follow all applicable Step 16 work in the Procedure, including conditional Step 16c UECM registration; it must not be inferred from the N4 Modification result alone. For the next-revision Wait model, the response boundary is the dedicated `prepare-step17-response` Node after all applicable Step 16 actions (successful N4 Modification plus required UECM registration, or the branch-specific Step 15 rejection action) and before Step 18 failure cleanup. `modify-n4-session` alone is not the response boundary. Neither step creates a new Skill or Invocation. Integration/Host/Runtime must retain exact request/response continuity and define timeout, duplicate, late-result and failure-response handling.
- An AMF `Namf_Communication_N1N2MessageTransfer` acknowledgement proves the transfer result defined by that service operation. It does not by itself prove RAN resource acceptance, N4 forwarding readiness or final UE acceptance.
- N4 Session Establishment and N4 Session Modification are separate protocol procedures and separate proof boundaries.

## 5. Operation and Capability mapping

### Operation

Where a standard NF Service Operation exists, the callable's documented mapping MUST use its canonical 3GPP name. Examples include:

- UDM: `Nudm_SDM_Get`, `Nudm_SDM_Subscribe`;
- PCF: `Npcf_SMPolicyControl_Create`;
- AMF: `Namf_Communication_N1N2MessageTransfer`;
- SMF service: `Nsmf_PDUSession_CreateSMContext`, `Nsmf_PDUSession_UpdateSMContext`;
- UPF control: N4 Session Establishment / Modification (PFCP), not an invented SBI operation.

The exact Tool ID used in `operation.tool` MUST still match the trusted ToolCatalog export. If the implementation's internal Tool ID differs from the 3GPP name, preserve the exact callable ID and record the canonical 3GPP mapping beside it. Do not silently rename an existing Owner export in Skill source.

### Capability

A Capability is an authorization grant, not a synonym for a 3GPP service operation. Its name and description MUST make the owning NF/domain and permitted 3GPP service/procedure visible. Prefer narrowly scoped grants such as UDM SDM read/subscribe, PCF SM Policy Association create, AMF N1N2 transfer, N4 establishment/modification and SMF context update over a single opaque `fivegc-session-mutation` grant.

A Capability ID in `contract.yaml` MUST be the exact ID published by a trusted CapabilityContracts package. Authors MUST NOT invent an ID to make a sample appear linkable. Before the Owner publishes the ID, a sample may use an explicitly marked `urn:example:` placeholder and a traceability row, but it remains NOT_QUALIFIED and must fail closed at link time.

## 6. Classify standard interactions and CA extensions

Every Node/Operation mapping must be one of:

| Classification | Meaning | Authoring rule |
|---|---|---|
| `3GPP_NATIVE` | Directly represents a named 3GPP NF Service Operation or protocol procedure | Use canonical 3GPP name and exact clause/step; callable still comes from the Owner ToolCatalog |
| `3GPP_LOCAL` | SMF-local pure computation or decision that is independently meaningful as part of the cited 3GPP procedure and has no external NF call | Use the corresponding SMF business-step name; implement only as a deterministic Skill Script; do not claim an external Capability or network side effect. Do not split request-only preparation for a single NF Tool into its own Node |
| `CA_ADAPTER` | CA Owner implements/orchestrates one or more 3GPP interactions behind a governed callable | Keep the CA Owner ID; state exactly which 3GPP steps it implements and which completion proof it owns |
| `CA_EXTENSION` | Host lifecycle, Evidence, admission, resource responsibility, audit or compensation with no direct 3GPP operation counterpart | Keep a clearly CA-prefixed name; explicitly say “no direct 3GPP operation” and do not imply standardization |

A CA adapter must not claim that a standard NF Service Operation exists when it is actually a multi-step internal orchestration. A CA extension must not be disguised as a 3GPP Node.

Host ingress admission, identity / duplicate checking, HostBusinessInstanceId allocation, Invocation lifecycle, correlation and persistence are not CA_EXTENSION Nodes: they happen before Skill Procedure execution and remain Host-private. Do not create an admit-* Node for these functions. The first business Node may carry the Skill's single global request-profile Precondition; its PASS advances to that Node's next declared stage.

## 7. MAS-specific rule

The current MAS example is a source-aligned policy-first implementation profile, not a normative 3GPP procedure. Its callable identities are candidate references derived from the imported OpenAMSM OES plan; they are not published Owner ToolCatalog exports. Each step MUST be classified `CA_ADAPTER` or `CA_EXTENSION` unless it is an exact 3GPP NF Service Operation.

The MAS Procedure MUST match the actual OES plan outputs and must not invent `stateRef`. In the current source, `UPS.up_anchor` and `IAM.ue_addr` are `"1"/"0"` markers, not an UPF identifier or UE IP address; `UPN.n4_seid` is a single UPF SEID; `SE.last_event` is a local event marker, not step-18 notification. The optional `IAM.CONFIRM_ADDRESS` is omitted for the fixed `LOCAL_POOL` profile. `SAA.SECONDARY_AUTH` is hard-coded to `required='0'` and therefore skips; auth-required profiles are not covered.

The current `CA.CREATE_CHARGING` implementation is `NOT_IMPL_skip` and its `charging_ref="1"` marker is not a resource receipt. It MUST NOT satisfy a charging Predicate or a final Goal. The MAS example remains NOT_QUALIFIED until charging is implemented or a business Owner approves a different profile. The OES `SC.COMPENSATE_RELEASE` operation is Host/Owner reconciliation material only; do not author it as a Skill compensation Node or inherit `compensate_then_replan_once`. See [OpenAMSM Operation Mapping](../examples/skills/establish-pdu-session-mas/assurance/openamsm-operation-mapping.md) for the pinned source mapping and qualification gaps.

## 8. Async inbound request and Wait

This section separates the frozen v1alpha4 authoring rule from the proposed next-revision model. They are not interchangeable.

### 8.1 Current v1alpha4 rule

CA-SL v1alpha4 §21 remains authoritative for the current examples in this PR: no author-level `wait`, `await` or polling Node. The current v1alpha4 source models asynchronous completion as an ordinary business Node whose Owner Operation may remain pending under its published completion contract. The Host/Integration ingress boundary admits the later inbound protocol request and correlates it to that exact pending Operation in the existing Invocation. The Owner returns its contractually validated result and Evidence; Runtime resumes the same Invocation at the pending Node. Current v1alpha4 Procedure YAML MUST NOT add the proposed `wait` field or `wait.output` SourcePath.

### 8.2 Next-revision proposal: Node-level Wait

[CA-SL Node-level Event Wait frozen semantic design baseline, Draft PR #60](https://github.com/odango-chan/ca-skills/pull/60) proposes a different model for the language revision after v1alpha4:

1. The outbound Step 11 `Namf_Communication_N1N2MessageTransfer` Operation routes to the target `update-sm-context` Node.
2. Before dispatching the triggering Operation, Runtime durably arms the expected Wait for the same Run. Host forwards the opaque registration to the 5GC Integration, which binds it to the exact protocol resource. Arming does not activate the Node or start its timeout. For the conventional initial-establishment flow, this binding uses the exact `smContextRef` established by Step 3 and returned in the Step 5 CreateSMContext response; it does not require a fresh context lookup merely to arm Step 15.
3. AMF later sends the Step 15 `Nsmf_PDUSession_UpdateSMContext Request`.
4. The 5GC Integration ingress adapter authenticates the AMF peer, validates and normalizes the request against the exact version-pinned 3GPP API contract, and resolves its protocol correlation to exactly one opaque `expectedIngressRef`. Generic Host persists and forwards the normalized delivery without selecting a Run or Node; Runtime resolves the reference against its authoritative ExpectedIngress record and buffers/accepts it. The Integration contract must distinguish successive UpdateSMContext requests for the same SM Context; if the wire request has no generation discriminator, it must enforce a proven single-flight/tombstone policy or fail closed.
5. Runtime resumes the same Run at `update-sm-context`. The Integration contract's normalized request value becomes the typed `update-sm-context.wait.output`; Host/Integration correlation and transport metadata remain private.
6. The Agent executes the target Node's declared logical SMF Operation using explicit arguments from `wait.output`. Any supplementary SMF Context Observation remains in that same Node after Operation and before Postcondition.
7. The Node's Postcondition evaluates the Operation Result, Observation Result and authoritative Evidence before routing to N4 Session Modification. After the applicable Step 16 path completes (including conditional Step 16c or the branch-specific pre-response N4 Release), the dedicated `prepare-step17-response` Node produces the typed Step 17 response result. The proposed `wait.response.after: prepare-step17-response` binds the paired response to that boundary; Step 18 cleanup remains later.

In this model, the Step 15 inbound request is the event that activates the target Node; it is not delivered to an Owner Operation that has been left pending merely to wait for that request. The Owner still implements the declared callable and owns its actual business effect, normalized Operation Result and Evidence.

The proposed Wait is Node-entry control, not a fifth stage or a separate Wait Node. Its timeout uses the existing route shape as `wait.routes.TIMEOUT`; there is no `onTimeout`. The inbound request Schema is resolved from the trusted, version-pinned 3GPP API request contract through the declared Integration Ingress Operation export. Skill source does not repeat a `payloadSchema` and does not declare a separate EventCatalog. See PR #60 for the proposed grammar, SourcePath, validation and runtime rules.

This proposal is not v1alpha4 syntax. Do not migrate the current v1alpha4 example YAML until a new language version is explicitly frozen and its Compiler/Runtime/Generic Host/Integration contracts are qualified.

### 8.3 Shared 3GPP response and responsibility rules

The paired Step 17 `Nsmf_PDUSession_UpdateSMContext Response` has three distinct responsibilities: Host owns the durable response-obligation record and replay lifecycle; the Integration adapter owns the protocol response Schema, status/error mapping and wire encoding; Runtime emits response-ready when the declared `wait.response.after` boundary is committed. For the Step 15/17 reference flow, the boundary is `prepare-step17-response`, after all applicable Step 16 actions. On the successful branch this means N4 Session Modification and conditional UDM UECM registration; on N2-resource-setup failure it means the required pre-response N4 Release; on required-UPE-unavailable failure Step 16 is skipped and no such pre-response release is invented. Step 18 failure cleanup remains after the response boundary. It is not the terminal Run. Definitive failure and unresolved/unknown response mapping must be explicit in the trusted Integration response contract; they must not be guessed from a Skill terminal label.

Neither model permits an adapter to collapse distinct 3GPP proof boundaries. In particular:

- PCF association creation is not N4 establishment.
- PCF request derivation, Hold binding, pre-N4 baseline validation, lifecycle isolation and competing-create checks are internal to the PCF Create Owner Operation; they are not separate Skill Nodes or Predicates.
- N1N2 transfer initiation is not RAN resource acceptance.
- RAN resource acceptance is not N4 forwarding readiness.
- N4 establishment is not N4 modification.
- For the conventional initial PDU Session example, the SMF N4 Owner owns native Step 8 UPF/session-address selection together with N4 Session Establishment. Its result must expose the effective session configuration needed by the subsequent N1/N2 interaction; the Skill must not pass a separate Script-generated `selection` object.
- An opaque `holdRef`, where required by a published Owner contract, remains an Owner-defined correlation handle; it is not an author Wait instruction.
- The legacy ToolCatalog `waiterRef` field is not v1alpha4 authority and must not be copied into a new Owner publication without an explicit contract decision. The repository verifier rejects `waiterRef` in current v1alpha4 Procedure source.
- A successful internal helper response is not a substitute for a published Owner result and Evidence.

## 9. Current PDU Session reference map

The conventional `establish-pdu-session` example is limited to one admitted, initial, IPv4 / SSC1, local non-roaming request. Its normative procedure reference is 3GPP TS 23.502 V19.9.0 (Release 19), §4.3.2.2.1. It does not claim coverage of emergency requests, existing PDU Session access switching, home-routed roaming, IPv6/IPv4v6 Router Advertisement, Bridge/Router information or conditional secondary authentication / policy-modification branches.

| 3GPP step | SMF-side interaction | Canonical name / boundary |
|---|---|---|
| 3 | AMF → SMF | `Nsmf_PDUSession_CreateSMContext Request` (Host ingress trigger; outside the Skill Procedure) |
| 4 | SMF ↔ UDM | When matching Session Management Subscription data is not already available: `Nudm_SDM_Get`, then `Nudm_SDM_Subscribe`; the example selects this retrieval/subscription path |
| 5 | SMF → AMF | `Nsmf_PDUSession_CreateSMContext Response` (early context response paired with Step 3; not final Goal proof) |
| 6 | SMF ↔ DN-AAA (optional) | PDU Session authentication/authorization; this example excludes profiles requiring secondary authentication |
| 7a–7b | SMF ↔ PCF | PCF selection and SM Policy Association Establishment; `Npcf_SMPolicyControl_Create` is the Step 7b service operation |
| 8 | SMF local processing / UPF selection | Native Step 8 SSC/UPF/session-address selection is owned inside the SMF N4 Owner Operation for this example; it is not a separate Skill Node or SBI callable |
| 9 | SMF ↔ PCF (conditional) | SMF-initiated SM Policy Association Modification; this example admits only the no-trigger result |
| 10a–10b | SMF ↔ UPF | N4 Session Establishment Request/Response; the same `establish-n4-session` business interaction owns Step 8 selection and this N4 exchange |
| 11 | SMF → AMF | `Namf_Communication_N1N2MessageTransfer` carrying N1 SM and N2 SM information |
| 12–14 | AMF ↔ (R)AN ↔ UE | Access-network resource setup and N2 PDU Session Response; not an SMF-owned service call |
| 15 | AMF → SMF | `Nsmf_PDUSession_UpdateSMContext Request` carrying the access-network result; v1alpha4 correlates it to the pending Owner Operation in the same Invocation |
| 16a–16b | SMF ↔ UPF | N4 Session Modification Request/Response |
| 16c | SMF ↔ UDM (conditional) | `Nudm_UECM_Registration` if Request Type is neither Emergency Request nor Existing Emergency PDU Session and the SMF has not already registered this PDU Session |
| 17 | SMF → AMF | `Nsmf_PDUSession_UpdateSMContext Response`, paired with the exact Step 15 request after all applicable Step 16 actions; Host/Integration owns this response boundary |
| 18 | SMF → AMF (conditional failure path) | `Nsmf_PDUSession_SMContextStatusNotify (Release)` when establishment fails after Step 5; release any created N4 sessions, allocated PDU Session address and PCF association; Step 19 is skipped |
| 19 | SMF → UE (conditional) | IPv6 Router Advertisement for IPv6 or IPv4v6 PDU Session types; excluded by this IPv4-only example |
| 20 | SMF ↔ PCF (conditional) | SM Policy Association Modification when the 5GS Bridge/Router information trigger is armed; excluded by this example |
| 21 | SMF ↔ UDM (conditional failure path) | After failure following Step 4, unsubscribe only if the SMF no longer handles another PDU Session for the same `(SUPI, DNN, HPLMN S-NSSAI)` |

The table is a reference map, not a statement that every optional or conditional step is present in every Skill. Each Skill must state its admitted request profile and why omitted branches are not required. The conventional example's Step 4 Get/Subscribe path assumes that matching subscription data is not already available; it is not a claim that every initial request must always repeat both calls.

### 9.1 Independently pinned Release 19 specifications

The following Stage 2 and Stage 3 references were checked against ETSI publications on 2026-11-17. Each specification has its own version number; do not normalize them to a single shared `V19.x.0`.

| Specification | Pinned version | Used for |
|---|---|---|
| TS 23.501 | V19.9.0 | 5GS architecture, SMF/UPF selection, SSC and address-allocation context |
| TS 23.502 | V19.9.0 | PDU Session Establishment and N4 procedure steps |
| TS 23.503 | V19.8.0 | PCC / SM Policy framework and policy-trigger context |
| TS 29.502 | V19.7.0 | `Nsmf_PDUSession` service, CreateSMContext and UpdateSMContext API; OpenAPI Annex A.2 |
| TS 29.571 | V19.7.0 | Common Data Types referenced by the pinned TS 29.502 OpenAPI, including `RefToBinaryData`; OpenAPI Annex A.2 |
| TS 29.500 | V19.7.1 | SBI technical realization, common HTTP/2 retry and request-deadline behavior | [ETSI Work Programme](https://portal.etsi.org/webapp/WorkProgram/Frame_WorkItemList.asp?SearchPage=TRUE+++&butExpertSearch=++Search++&includeNonActiveTB=FALSE+++&optDisplay=ALL+++&qCURRENT_STATE_CODE=finalized+++&qINCLUDE_SUB_TB=True+++&qPROJECT_BOOLEAN=OR+++&qREPORT_TYPE=SUMMARY+++&qSORT=HIGHVERSION+++&qTITLE=TS+29.500+++&titleType=all+++) |
| TS 29.571 | V19.7.0 | Common SBI data types, including `RefToBinaryData` used by Nsmf/Namf OpenAPI schemas | [ETSI PDF](https://www.etsi.org/deliver/etsi_ts/129500_129599/129571/19.07.00_60/ts_129571v190700p.pdf) |
| TS 29.503 | V19.7.0 | UDM SDM and UECM services; OpenAPI Annex A.2 and A.3 |
| TS 29.512 | V19.6.0 | `Npcf_SMPolicyControl` service; OpenAPI Annex A.2 |
| TS 29.518 | V19.8.0 | `Namf_Communication` service and N1N2 Message Transfer; OpenAPI Annex A.2 |
| TS 29.244 | V19.6.0 | PFCP / N4 Session Establishment, Modification and Release |

Primary ETSI PDFs:

- [TS 23.501 V19.9.0](https://www.etsi.org/deliver/etsi_ts/123500_123599/123501/19.09.00_60/ts_123501v190900p.pdf)
- [TS 23.502 V19.9.0](https://www.etsi.org/deliver/etsi_ts/123500_123599/123502/19.09.00_60/ts_123502v190900p.pdf)
- [TS 23.503 V19.8.0](https://www.etsi.org/deliver/etsi_ts/123500_123599/123503/19.08.00_60/ts_123503v190800p.pdf)
- [TS 29.502 V19.7.0](https://www.etsi.org/deliver/etsi_ts/129500_129599/129502/19.07.00_60/ts_129502v190700p.pdf)
- [TS 29.571 V19.7.0](https://www.etsi.org/deliver/etsi_ts/129500_129599/129571/19.07.00_60/ts_129571v190700p.pdf)
- [TS 29.503 V19.7.0](https://www.etsi.org/deliver/etsi_ts/129500_129599/129503/19.07.00_60/ts_129503v190700p.pdf)
- [TS 29.512 V19.6.0](https://www.etsi.org/deliver/etsi_ts/129500_129599/129512/19.06.00_60/ts_129512v190600p.pdf)
- [TS 29.518 V19.8.0](https://www.etsi.org/deliver/etsi_ts/129500_129599/129518/19.08.00_60/ts_129518v190800p.pdf)
- [TS 29.244 V19.6.0](https://www.etsi.org/deliver/etsi_ts/129200_129299/129244/19.06.00_60/ts_129244v190600p.pdf)

**Binary SBI payload contract (normative source mapping):** TS 29.502 V19.7.0 OpenAPI defines `multipart/related` representations for Nsmf operations that carry N1 SM, N2 SM/NGAP or N4/PFCP payloads. The JSON part is `application/json`; binary parts use the operation-specific media type (including `application/vnd.3gpp.5gnas`, `application/vnd.3gpp.ngap` and `application/vnd.3gpp.pfcp`). Multiple binary parts may be present; the exact OpenAPI operation/response schema determines which parts exist. TS 29.571 V19.7.0 §5.4.4.14 defines `RefToBinaryData`: its required `contentId` is the value of the `Content-ID` header on the referenced binary body part. The JSON reference is not the binary payload itself.

The Tool Owner / HTTP adapter owns the MIME boundary, `multipart/related` framing, JSON root part, binary part bytes, per-part media types and `Content-ID` binding. It must support the number of binary parts declared by the selected OpenAPI operation; do not assume one binary part or JSON-only requests. A Skill passes typed business data / payload references under the published Tool Schema. It does not construct raw HTTP multipart framing or invent base64-in-JSON encodings.

For Stage 3 API traceability, use the exact OpenAPI files named by the applicable TS annex. A TS document version pin does not qualify a Tool Owner implementation, its ToolCatalog export, Schema, CapabilityContracts, Evidence or Deployment binding.

### 9.2 Failure-path distinctions

The normal success path must not collapse the standard's failure branches:

- If establishment fails between Step 5 and Step 11, Step 11 carries the PDU Session Establishment Reject and Steps 12–17 are skipped.
- If Step 15 reports failure of user-plane resource setup, the SMF rejects the establishment, releases the N4 Session with the UPF and skips Step 16 before returning the paired Step 17 response.
- If the User Plane Enforcement Policy requires resources and the N2 result says no user-plane resources could be established, the SMF rejects and skips Step 16. Do not invent the N4-release action from the preceding failure branch unless its own trigger is present.
- On a failure after Step 5, Step 18 notifies the AMF and releases any N4 sessions created, any allocated PDU Session address and the PCF association, if present.
- Step 21 is not unconditional cleanup: it applies after failure following Step 4 only when the SMF no longer handles another PDU Session of the same UE for the same DNN and HPLMN S-NSSAI.

Step 17 is the paired protocol response for Step 15, not the Skill Goal proof. The final CA-SL Postcondition and Host/Runtime resource-responsibility gate remain authoritative.

## 10. Review and validation

A 5GC migration is not ready for review closure until:

- every Procedure Node has a 3GPP traceability entry or an explicit CA classification;
- Node names and Operation mappings use canonical 3GPP terminology where available;
- each Capability is traceable to its exact trusted CapabilityContracts export and its NF/service scope;
- all AMF/RAN/UE work is correctly distinguished from SMF-owned interactions;
- both sides of SMF service request/response boundaries are assigned: step 3/5 `Nsmf_PDUSession_CreateSMContext` and step 15/17 `Nsmf_PDUSession_UpdateSMContext` must be explicitly owned by the Skill graph or by a documented Host/service entry/exit boundary;
- every asynchronous completion proof is assigned to the corresponding Owner Operation/adapter;
- supplementary Observations are co-located with the Operation they support, run after that Operation and before its Postcondition, and are not duplicated as standalone Nodes without an explicit business-boundary rationale;
- terminal resource responsibility is enforced by the Host/Runtime §12.8 publish gate, not by a Skill-authored handoff Node or Predicate; a Skill may publish FAILED only when no known resource or external change remains to be handled;
- all legacy business gates and failure Cases remain traceable;
- no unpublished Owner ID, Schema, Evidence or Capability is described as qualified.

Passing repository-local source checks does not establish Compiler, Owner, Runtime, MAS or live 5GC conformance.


## 11. 5GC context ownership and access boundary (2026-11-16)

The Host Subject Context Package ID is reserved as `urn:connectionagent:ca:host-context`; the exact package snapshot and trusted Owner/digest binding are not yet published. Its Skill-visible schema exports the 3GPP `supi` copied from the admitted CreateSMContext request; no Host-generated UE reference exists. The generic Host Session Context ToolCatalog package ID is reserved as `urn:connectionagent:ca:host:smf-session-context`; the separate projection-specific MAS Observation package ID is reserved as `urn:connectionagent:ca:host:smf-mas-observations`. Both are owned by `ca-agent-host`. The `ca-client-tools` repository supplies only the fixed local CLI backend and does not own the CA-SL ToolCatalog or Capability grants.

The Host-owned Observation ToolCatalog is a dependency snapshot for CA-SL linking, not a second Server Tool Catalog. The existing `tool-mcp-gw` Server Tool Catalog and Runtime Resolved CA Toolset / Capability authorization remain authoritative. Host-local adapter dispatch binds an authorized callable to its implementation; it does not grant permissions.

The conventional `establish-pdu-session` example uses two narrowly scoped generic read-only SMF context Observations for different decisions, both co-located with a primary Operation: the entry lookup follows the read-only Step 4 UDM Get and precedes every session-creating or session-mutating Operation; the fresh post-Step-15 read follows completion of the UpdateSMContext Operation and supplies current facts for the N4 decision. Neither is a standalone Procedure Node. The entry lookup distinguishes `ABSENT` (404 `SESSION_NOT_FOUND`), `PRESENT` (including 200 `UNAVAILABLE`) and `UNKNOWN`; the generic adapter returns 404 as a typed Observation result, and only the explicit `ABSENT` Predicate with trusted exact-scope Evidence selects initial creation. A `PRESENT` context must take an explicit existing-context/idempotency/recovery path and must not replay the initial mutation chain. The existing SMF QueryContext interface is only a compatibility backend; it is not a business concept or package dependency in the conventional Skill. The SMF N4 Owner remains responsible for N4 Session Modification. Both examples continue to use `ca-context` for the subject-only Host Context. The MAS policy-first Skill now also uses the generic entry Observation; it does not query all eight projections or assume the target context is absent.

The eight projection-specific compatibility callable IDs and candidate Guarantee DottedIds are recorded in the Host proposal. The conventional `establish-pdu-session` Skill uses the generic `ca-session-context::context.smf.session.read` interface as a supplementary Observation stage within its Step 4 and Step 15 business Nodes. The MAS example also uses the generic interface, but its Node placement is not changed by this conventional-Skill refresh and remains subject to the same architecture review before approval. CapabilityContracts is deployment-owned trusted input: each Capability is owned by the deployment and each callable member by `ca-agent-host`; `ca-client-tools` remains the local CLI backend. Scope policy references are deployment-owned names, not published policy bodies or grants. No Observation Evidence Descriptor is publishable until the exact SMF authority identity and temporal contract are supplied.

The SMF MAS v0.10 response contains no source `observedAt`, `eventTime` or `validUntil`. Host `queryStartedAt` and `receivedAt` are audit bounds only. The Host must not invent source freshness, and the v0.10 response does not supply Host `lifecycleRef`; exact UE/PSI/lifecycle binding must be established through trusted Host execution context.

Non-SMF context needed to complete an Operation remains inside the responsible Tool/Owner adapter. The Skill consumes only that Tool's declared Operation Result/Evidence. The completed [17-ref Legacy Observation Crosswalk](https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/5gc-legacy-observation-crosswalk-v1alpha4.md) records the old Observation source disposition. Do not promote every legacy helper into a Skill Procedure Node.

Host owns ProductTask, AgentInstance, HostBusinessInstance, ingress admission/deduplication, HostBusinessCorrelation (`ingressRef`, `lifecycleRef`) and its request-ledger/transport continuity. Host supplies the stable Runtime Execute `requestId`; ca-runtime owns its `(host, requestId)` RequestStore, fingerprint, deduplication and replay authority, and generates `runId` plus RunRecord/RunEvent, Procedure progression, Action dispatch/outcome, Evidence and Reconcile. The responsible Provider/Owner owns protocol transactions, callbacks, waiter/hold/claim/journal records and resource receipts. These owner-specific values are not `contextSchema`, Predicate inputs or Skill-authored callable arguments. The incoming CreateSMContext Request is a Host ingress trigger, not a Procedure Node. The Skill's business request-profile check belongs on the first business Node, not on an `admit-*` Host Node.

Do not automatically query all eight compatibility projections after each Operation. Query only the exact SMF-owned context/facts required by a business decision and not already present in the Operation Result/Evidence or Host Subject Context.

## 12. 5GC contract publication gates

Before either example Skill can be qualified:

1. Publish the reserved Host Subject Context Package ID `urn:connectionagent:ca:host-context` with its exact Owner snapshot, Schema export and trusted Package ID/Owner/digest binding.
2. Publish the Host-owned HostBusinessCorrelation Schema (`ingressRef`, `lifecycleRef`) and the RuntimeHost `hostBusinessCorrelation` transport extension. Runtime execution identities remain Runtime-owned; do not merge the two owners into a local schema or expose either as Skill-authored inputs.
3. Publish the Host-owned Observation ToolCatalog dependency snapshot with the generic SMF context-read callable and, separately, any projection-specific compatibility callables and their G.4-compatible query/output Schemas. This is not a second Server Tool Catalog; `ca-client-tools` is only the local CLI backend.
4. Publish deployment-owned CapabilityContracts with one least-privilege Capability per Observation callable; Capability owner is the deployment and callable owner is `ca-agent-host`.
5. Publish Evidence Descriptors and deployment Scope policies for the generic SMF context read and any projection-specific compatibility reads, with exact SMF authority, subject/PSI/lifecycle Scope, Invocation correlation and executable freshness semantics. SMF v0.10 alone does not close the temporal gate.
6. Review and accept the completed 17-reference legacy Observation crosswalk; raw UPF/N4 or AMF/RAN snapshots must not be relabelled as SMF context projections by name alone.
7. Publish the generic CA SMF session-context Observation callable, its Schema, Capability and Evidence/Scope contract for both initial PDU Session Skills. Keep the underlying SMF QueryContext compatibility implementation behind the callable; do not expose its legacy implementation naming in the conventional Skill. Publish additional projection-specific Observation callables only when a Procedure actually requires those facts.
8. Qualify each Skill independently with executable v1alpha4 fixtures and the required Compiler/Studio/Host/Runtime/5GC evidence.
