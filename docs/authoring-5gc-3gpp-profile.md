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
- A Node may contain CA-SL Precondition, Operation, Observation and Postcondition stages. Those stages describe the conditions and proof for that 3GPP interaction; they do not change the identity of the interaction.
- A Node must not be introduced solely for a trivial implementation helper, temporary variable, local copy or one-line mapping. A separate CA Node is permitted when it is a governed Host/Owner action or Observation, or a meaningful typed Script transformation required by the v1alpha4 dataflow. An SMF-local pure computation that is part of the standard procedure is classified `3GPP_LOCAL` and keeps a business-step name. A CA-specific governed adapter/extension instead uses a clear `ca-` identity, is classified `CA_ADAPTER`/`CA_EXTENSION`, and points to the 3GPP interaction it supports; it must never be mistaken for a standard NF interaction.

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
| `3GPP_LOCAL` | SMF-local pure computation or decision that is part of the cited 3GPP procedure and has no external NF call | Use the corresponding SMF business-step name; implement only as a deterministic Skill Script; do not claim an external Capability or network side effect |
| `CA_ADAPTER` | CA Owner implements/orchestrates one or more 3GPP interactions behind a governed callable | Keep the CA Owner ID; state exactly which 3GPP steps it implements and which completion proof it owns |
| `CA_EXTENSION` | Host lifecycle, Evidence, admission, resource responsibility, audit or compensation with no direct 3GPP operation counterpart | Keep a clearly CA-prefixed name; explicitly say “no direct 3GPP operation” and do not imply standardization |

A CA adapter must not claim that a standard NF Service Operation exists when it is actually a multi-step internal orchestration. A CA extension must not be disguised as a 3GPP Node.

## 7. MAS-specific rule

The current MAS example is a proposed policy-first implementation design, not a normative 3GPP procedure. Its ordering and custom state-management operations MUST be identified as MAS/CA-specific. Each step may cite the related 3GPP phase it supports, but must be labelled `CA_ADAPTER` or `CA_EXTENSION` unless it is an exact 3GPP interaction.

In particular, do not present custom MAS context creation, UECM registration, charging, address confirmation, event emission or cleanup as standard 3GPP NF Service Operations merely because they occur during PDU Session Establishment. Where the MAS sequence intentionally differs from TS 23.502, record the deviation and its business rationale.

## 8. Async completion and Wait

CA-SL v1alpha4 §21 remains authoritative: no author-level Wait/Await/Poll Node. The Owner Operation or CA adapter responsible for the asynchronous 3GPP interaction must own its completion contract, correlation, final result and Evidence. The Procedure may proceed only after that Operation reports a contractually proven result.

This does not permit an adapter to collapse distinct 3GPP proof boundaries. An opaque `holdRef` may be passed only as an Owner-defined correlation handle; it is not an author Wait instruction. The legacy ToolCatalog's `waiterRef` field is not a v1alpha4 authority and must not be copied into a new Owner publication without an explicit contract decision. The repository verifier rejects `waiterRef` in current v1alpha4 Procedure source; use the Owner-published `holdRef` contract if a correlation handle is required. In particular:

- PCF association creation is not N4 establishment.
- N1N2 transfer initiation is not RAN resource acceptance.
- RAN resource acceptance is not N4 forwarding readiness.
- N4 establishment is not N4 modification.
- A successful internal helper response is not a substitute for a published Owner result and Evidence.

## 9. Current PDU Session reference map

For the current local/non-roaming, UE-requested initial PDU Session example, the pinned reference is 3GPP TS 23.502 V18.12.0 (Release 18):

| 3GPP step | SMF-side interaction | Canonical name / boundary |
|---|---|---|
| 3 | AMF → SMF | `Nsmf_PDUSession_CreateSMContext Request` (Skill entry/admission context) |
| 4 | SMF ↔ UDM | Session Management Subscription retrieval and subscription for updates; `Nudm_SDM_Get` and `Nudm_SDM_Subscribe` |
| 5 | SMF → AMF | `Nsmf_PDUSession_CreateSMContext Response` (early context response; not final Goal proof) |
| 6 | SMF ↔ DN-AAA (optional) | PDU Session authentication/authorization; only if the admitted profile requires it |
| 7b | SMF ↔ PCF | SM Policy Association Establishment; `Npcf_SMPolicyControl_Create` |
| 8 | SMF local processing / UPF selection | Select SSC mode/UPF and allocate session address as applicable |
| 9 | SMF ↔ PCF (conditional) | SMF-initiated SM Policy Association Modification |
| 10a–10b | SMF ↔ UPF | N4 Session Establishment Request/Response for an initial request |
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


## 8. 5GC context ownership and access boundary (2026-11-16)

The CA Agent replaces the SMF-side orchestration role. It directly queries only SMF-owned MAS context through explicit, read-only Observation Queries to the eight existing SMF QueryContext SBI endpoints (SC, PA, UPN, SSM, IAM, UPS, CA and SAA). It does not directly query AMF, UDM, PCF, UPF or other NF context.

Any non-SMF context needed to complete an Operation is obtained and validated inside the responsible Tool/Owner adapter. The Skill consumes only that Tool's declared Operation Result and Evidence. An internal SBI/PFCP/local read by a Tool is not a separate Skill Observation.

Host owns ingress admission, invocation/instance identity, lifecycle, correlation, persistence, holds, journals and late-result responsibility. These are not Skill Predicates, Skill context facts or authored Operation arguments. The Skill-visible Host context is the subject-only ueRef projection; the Skill separately owns its request Schema.

Do not automatically query all MAS after each Operation. Add an Observation only when the Operation Result/Evidence is insufficient. Initial PDU Session establishment has no pre-existing SMF session to query before the initial SM Context is created.

See https://github.com/odango-chan/ca-agent-demo/blob/main/docs/design/5gc-agent-context-access-boundary-v1alpha4.md for endpoint fields, response status semantics, legacy Observation reclassification and qualification gates.
