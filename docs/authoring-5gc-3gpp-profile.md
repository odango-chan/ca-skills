# CA-SL 5GC Authoring Profile — 3GPP-first Procedure and Capability Mapping

**Status:** Normative repository-level authoring profile for 5GC examples.  
**Language:** CA-SL v1alpha4, pinned at `7f84393ee8c395e4d8c39a74cb5000a1f896588d`.  
**3GPP baseline for the current PDU Session examples:** 3GPP TS 23.502 V18.12.0 (Release 18), especially §4.3.2.2.1 and §4.4.1.2–§4.4.1.3.  
**Effect:** This profile constrains how this repository authors 5GC Skills. It does not change the frozen CA-SL grammar or replace any 3GPP specification.

## 1. Governing principle

A 5GC Skill is authored from the **SMF point of view** and follows the standard 3GPP business procedure. It is not an independently invented workflow that happens to call 5GC-flavoured tools.

- A **Skill** expresses a stable business goal, such as fulfilling one admitted UE-requested initial PDU Session Establishment.
- Its **Procedure** expresses the complete SMF-owned business procedure for that goal. It may span multiple 3GPP protocol exchanges.
- A **Node** represents one logical 3GPP interaction step or one tightly related group of protocol exchanges, viewed from the SMF's responsibility boundary. A Node will commonly correspond to a Request/Response exchange, but the mapping is not mechanically one Node per message or one Node per internal function.
- Host ingress admission, duplicate suppression, business-instance association, Invocation lifecycle and correlation are pre-Procedure Host services, not Skill Nodes or Predicates. A Skill's business request-profile gate belongs on the first business Node as its global Precondition; it must not be named or described as Host admission.
- A Node may contain CA-SL Precondition, Operation, Observation and Postcondition stages. Those stages describe the conditions and proof for that 3GPP interaction; they do not change the identity of the interaction.
- A Node must not be introduced solely for a trivial implementation helper, temporary variable, local copy or one-line mapping. A separate Script Node is justified only when it represents an independently meaningful, typed SMF-local business decision/result that is consumed independently in the 3GPP procedure. It is not justified when the Script merely revalidates or reshapes data already checked at an earlier interaction, or when native SMF processing performs the local work as part of an adjacent 3GPP interaction. In this conventional PDU Session example, the former Step 8 Script only rechecked/remapped UDM subscription fields; it did not select a UPF or allocate a session address. Native Step 8 selection therefore belongs inside the UPN Owner Operation that performs N4 Session Establishment, not in a separate `3GPP_LOCAL` Node. A separate CA Node is permitted when it is a governed Host/Owner action or Observation, or a meaningful typed Script transformation required by the v1alpha4 dataflow. A CA-specific governed adapter/extension instead uses a clear `ca-` identity, is classified `CA_ADAPTER`/`CA_EXTENSION`, and points to the 3GPP interaction it supports; it must never be mistaken for a standard NF interaction.

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

- `retrieve-sm-subscription-data` — `Nudm_SDM_Get`
- `subscribe-sm-data` — `Nudm_SDM_Subscribe`
- `establish-sm-policy-association` — `Npcf_SMPolicyControl_Create`
- `establish-n4-session` — N4 Session Establishment Request/Response
- `transfer-n1n2-message` — `Namf_Communication_N1N2MessageTransfer`
- `update-sm-context` — `Nsmf_PDUSession_UpdateSMContext`
- `modify-n4-session` — N4 Session Modification Request/Response

These are naming examples, not a declaration that the corresponding Owner exports are already published.

Do not use implementation-only names such as `read-operation-context`, `bind-pcf-hold`, `build-n1n2-delivery` or `signal-ran` as the primary business Node name when the Node is actually representing a standard 3GPP interaction. Such helpers must be absorbed into the corresponding Owner Operation/adapter or explicitly identified as CA extensions.

## 4. SMF responsibility boundary

The Procedure MUST be described from the SMF point of view.

- Include interactions the SMF initiates or receives, including the relevant SBI and N4 boundaries.
- Do not model AMF, UE or RAN internal actions as if they were SMF-owned Operations.
- In TS 23.502 §4.3.2.2.1, the AMF↔(R)AN and (R)AN↔UE work in steps 12–14 is not an SMF service call. From the SMF point of view, the relevant result returns through the AMF's `Nsmf_PDUSession_UpdateSMContext Request` in step 15. If a CA SSM Owner wraps or observes the asynchronous access-network completion, label it as a **CA adapter** for the relevant 3GPP steps; do not rename it as a standard 3GPP service operation.
- The initial `Nsmf_PDUSession_CreateSMContext Response` in step 5 is not, by itself, proof that the full PDU Session Establishment has completed. Do not use it as the final Goal proof.
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

The current MAS example is a proposed policy-first implementation design, not a normative 3GPP procedure. Its ordering and custom state-management operations MUST be identified as MAS/CA-specific. Each step may cite the related 3GPP phase it supports, but must be labelled `CA_ADAPTER` or `CA_EXTENSION` unless it is an exact 3GPP interaction.

In particular, do not present custom MAS context creation, UECM registration, charging, address confirmation, event emission or cleanup as standard 3GPP NF Service Operations merely because they occur during PDU Session Establishment. Where the MAS sequence intentionally differs from TS 23.502, record the deviation and its business rationale.

## 8. Async completion and Wait

CA-SL v1alpha4 §21 remains authoritative: no author-level Wait/Await/Poll Node. The Owner Operation or CA adapter responsible for the asynchronous 3GPP interaction must own its completion contract, correlation, final result and Evidence. The Procedure may proceed only after that Operation reports a contractually proven result.

This does not permit an adapter to collapse distinct 3GPP proof boundaries. An opaque `holdRef` may be passed only as an Owner-defined correlation handle; it is not an author Wait instruction. The legacy ToolCatalog's `waiterRef` field is not a v1alpha4 authority and must not be copied into a new Owner publication without an explicit contract decision. The repository verifier rejects `waiterRef` in current v1alpha4 Procedure source; use the Owner-published `holdRef` contract if a correlation handle is required. In particular:

- PCF association creation is not N4 establishment.
- PCF request derivation, Hold binding, pre-N4 baseline validation, lifecycle isolation and competing-create checks are internal to the PCF Create Owner Operation; they are not separate Skill Nodes or Predicates.
- N1N2 transfer initiation is not RAN resource acceptance.
- RAN resource acceptance is not N4 forwarding readiness.
- N4 establishment is not N4 modification.
- For the conventional initial PDU Session example, UPN Owner owns native Step 8 UPF/session-address selection together with N4 Session Establishment. Its result must expose the effective session configuration needed by the subsequent N1/N2 interaction; the Skill must not pass a separate Script-generated `selection` object.
- A successful internal helper response is not a substitute for a published Owner result and Evidence.

## 9. Current PDU Session reference map

For the current local/non-roaming, UE-requested initial PDU Session example, the pinned reference is 3GPP TS 23.502 V18.12.0 (Release 18):

| 3GPP step | SMF-side interaction | Canonical name / boundary |
|---|---|---|
| 3 | AMF → SMF | `Nsmf_PDUSession_CreateSMContext Request` (Host ingress trigger; outside the Skill Procedure) |
| 4 | SMF ↔ UDM | Session Management Subscription retrieval and subscription for updates; `Nudm_SDM_Get` and `Nudm_SDM_Subscribe` |
| 5 | SMF → AMF | `Nsmf_PDUSession_CreateSMContext Response` (early context response; not final Goal proof) |
| 6 | SMF ↔ DN-AAA (optional) | PDU Session authentication/authorization; only if the admitted profile requires it |
| 7b | SMF ↔ PCF | SM Policy Association Establishment; `Npcf_SMPolicyControl_Create` |
| 8 | SMF local processing / UPF selection | Native Step 8 selection is internal to the UPN Owner boundary for N4 Session Establishment; it is not a separate Skill Node |
| 9 | SMF ↔ PCF (conditional) | SMF-initiated SM Policy Association Modification |
| 10a–10b | SMF ↔ UPF | N4 Session Establishment Request/Response; the same establish-n4-session Node also owns Step 8 selection |
| 11 | SMF → AMF | `Namf_Communication_N1N2MessageTransfer` carrying N1 SM and N2 SM information |
| 12–14 | AMF ↔ (R)AN ↔ UE | Access-network resource setup and N2 PDU Session Response; not an SMF-owned service call |
| 15 | AMF → SMF | `Nsmf_PDUSession_UpdateSMContext Request` carrying the access-network result |
| 16a–16b | SMF ↔ UPF | N4 Session Modification Request/Response |
| 17 | SMF → AMF | `Nsmf_PDUSession_UpdateSMContext Response` (paired response to step 15) |
| 18 | SMF → AMF | `Nsmf_PDUSession_SMContextStatusNotify` when applicable |
| 21 | SMF ↔ UDM | Unsubscription when applicable |

This table is a reference map, not a statement that every optional or conditional step is present in every admitted Skill profile. The profile and each Skill must state which steps are in scope and why omitted steps are not required.

## 10. Review and validation

A 5GC migration is not ready for review closure until:

- every Procedure Node has a 3GPP traceability entry or an explicit CA classification;
- Node names and Operation mappings use canonical 3GPP terminology where available;
- each Capability is traceable to its exact trusted CapabilityContracts export and its NF/service scope;
- all AMF/RAN/UE work is correctly distinguished from SMF-owned interactions;
- both sides of SMF service request/response boundaries are assigned: step 3/5 `Nsmf_PDUSession_CreateSMContext` and step 15/17 `Nsmf_PDUSession_UpdateSMContext` must be explicitly owned by the Skill graph or by a documented Host/service entry/exit boundary;
- every asynchronous completion proof is assigned to the corresponding Owner Operation/adapter;
- all legacy business gates and failure Cases remain traceable;
- no unpublished Owner ID, Schema, Evidence or Capability is described as qualified.

Passing repository-local source checks does not establish Compiler, Owner, Runtime, MAS or live 5GC conformance.


## 11. 5GC context ownership and access boundary (2026-11-16)

The Host Subject Context Package ID is reserved as `urn:connectionagent:ca:host-context`; the exact package snapshot and trusted Owner/digest binding are not yet published. Its Skill-visible schema exports only opaque `ueRef`. The separate `ca-5gc-client-tools` Observation package ID is reserved as `urn:connectionagent:ca:5gc:smf-mas-observations`; it contains the client-tools ToolCatalog dependency snapshot and typed query/output Schemas when published.

The `ca-5gc-client-tools` ToolCatalog is a dependency snapshot for CA-SL linking, not a second Server Tool Catalog. The existing `tool-mcp-gw` Server Tool Catalog and Runtime Resolved CA Toolset / Capability authorization remain authoritative. Host-local adapter dispatch binds an authorized callable to its implementation; it does not grant permissions.

The two example Skills currently do not invoke any of the eight SMF MAS Observation callables. In particular, the initial PDU Session establishment Skill must not add the `smf-mas-observations` dependency: no pre-existing SMF Session Context exists before the initial SM Context is created. The `ca-context` alias remains the only Host dependency used by the examples.

The eight Observation callable IDs and candidate Guarantee DottedIds are recorded in the `ca-5gc-client-tools` proposal. CapabilityContracts is deployment-owned trusted input: each Capability is owned by the deployment and each callable member by `ca-5gc-client-tools`. Scope policy references are deployment-owned names, not published policy bodies or grants. No Observation Evidence Descriptor is publishable until the exact SMF MAS authority identity and temporal contract are supplied.

The SMF MAS v0.10 response contains no source `observedAt`, `eventTime` or `validUntil`. Host `queryStartedAt` and `receivedAt` are audit bounds only. The Host must not invent source freshness, and the v0.10 response does not supply Host `lifecycleRef`; exact UE/PSI/lifecycle binding must be established through trusted Host execution context.

Non-SMF context needed to complete an Operation remains inside the responsible Tool/Owner adapter. The Skill consumes only that Tool's declared Operation Result/Evidence. The completed [17-ref Legacy Observation Crosswalk](https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/5gc-legacy-observation-crosswalk-v1alpha4.md) records the old Observation source disposition. Do not promote every legacy helper into a Skill Procedure Node.

Host owns ProductTask, AgentInstance, HostBusinessInstance, ingress admission/deduplication, HostBusinessCorrelation (`ingressRef`, `lifecycleRef`) and its request-ledger/transport continuity. Host supplies the stable Runtime Execute `requestId`; ca-runtime owns its `(host, requestId)` RequestStore, fingerprint, deduplication and replay authority, and generates `runId` plus RunRecord/RunEvent, Procedure progression, Action dispatch/outcome, Evidence and Reconcile. The responsible Provider/Owner owns protocol transactions, callbacks, waiter/hold/claim/journal records and resource receipts. These owner-specific values are not `contextSchema`, Predicate inputs or Skill-authored callable arguments. The incoming CreateSMContext Request is a Host ingress trigger, not a Procedure Node. The Skill's business request-profile check belongs on the first business Node, not on an `admit-*` Host Node.

Do not automatically query all MAS after each Operation. Query only when a business decision needs an SMF-owned fact that is not already present in the Operation Result/Evidence or Host Subject Context.

## 12. 5GC contract publication gates

Before either example Skill can be qualified:

1. Publish the reserved Host Subject Context Package ID `urn:connectionagent:ca:host-context` with its exact Owner snapshot, Schema export and trusted Package ID/Owner/digest binding.
2. Publish the Host-owned HostBusinessCorrelation Schema (`ingressRef`, `lifecycleRef`) and the RuntimeHost `hostBusinessCorrelation` transport extension. Runtime execution identities remain Runtime-owned; do not merge the two owners into a local schema or expose either as Skill-authored inputs.
3. Publish the `ca-5gc-client-tools` Owner ToolCatalog dependency snapshot with eight exact Observation callable IDs and G.4-compatible query/output Schemas. This is not a second Server Tool Catalog.
4. Publish deployment-owned CapabilityContracts with one least-privilege Capability per Observation callable; Capability owner is the deployment and callable owner is `ca-5gc-client-tools`.
5. Publish per-MAS Evidence Descriptors and deployment Scope policies with exact SMF authority, subject/PSI/lifecycle Scope, Invocation correlation and executable freshness semantics. SMF v0.10 alone does not close the temporal gate.
6. Review and accept the completed 17-reference legacy Observation crosswalk; raw UPF/N4 or AMF/RAN snapshots must not be relabelled as UPN/SSM projections by name alone.
7. Publish the reserved `smf-mas-observations` Package ID `urn:connectionagent:ca:5gc:smf-mas-observations` only with its complete Owner snapshot and trusted binding. Do not add this dependency to either example until a Procedure actually references an Observation callable.
8. Qualify each Skill independently with executable v1alpha4 fixtures and the required Compiler/Studio/Host/Runtime/5GC evidence.
