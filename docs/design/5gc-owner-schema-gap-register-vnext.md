# 5GC Owner Schema Gap Register — vNext

Status: **CODE-DERIVED AUDIT / OWNER EXPORTS IN DRAFT; COMPLETE IMPORTABLE BUNDLE NOT YET AVAILABLE**
Audit source: odango-chan/ca-agent-demo main, commit 38012852827437185c6343c2b544acad401084e1.
Executable baseline: conventional establish-pdu-session only. MAS is excluded.

## 1. Audit conclusion

The current 5GC execution path has real owner-specific contracts and Python runtime models, but it does **not** yet provide one complete, versioned, importable dependency bundle containing all Host Context, Observation, Evidence and Capability exports required by a future no-lib Compiler build.

Do not create shadow copies in the Skill package to make the compiler pass. Missing owner exports are blockers to the new build, not permission to weaken schema validation.

## 2. What exists today

| Surface | Existing artifact / implementation | What it proves | What it does not prove |
|---|---|---|---|
| Tool Operation contract | tools/contracts/createdsession.tool.yaml | 12 exact Operation IDs, declared READ/MUTATION Effect, adapter binding, Input/Output/Reconcile schemas | Several nested result bodies are broad type: object; not all producer fields are statically linkable |
| Capability → Operation | tools/contracts/capabilities/createdsession.capabilities.yaml | 6 deployment Capabilities, owner, exact Operation membership and independently expected Effect | Not a Skill-authored grant; deployment-owned authorization/effect registry |
| Tool implementation registration | tools/registrations/default.yaml | Exact Operation → implementation selection | Not Capability membership, schema authority, authorization or READY by itself |
| Provider Observation wire | ca-provider-5gc main: schemas/provider-observation-read-request.schema.yaml and provider-observation-read-result.schema.yaml (mirrored into Host integration) | Owner-published request/result envelope and six Provider Observation refs with ref-conditional payload schemas | Does not define Fabric, Host journal, or Host adapter-normalized Observation payloads |
| Host Observation model | runtime/observation/model.py | Implemented Python envelope: request, status, normalized value, evidence, correlation and evidence capability | No standalone versioned JSON Schema export for the generic envelope |
| Host Context model | agent/context/base.py, projection, requirements, loader and resolvers | Implemented Python Subject / Facts / ContextFact / ContextRequirement / provenance and resolver behavior | No complete exported JSON Schema for Subject and Facts namespaces |
| Skill Request | skills/establish-pdu-session/schemas/establishment-request.schema.yaml | Real Skill-owned public input contract | Does not substitute for Host Context or Observation schemas |

## 3. Observation reference inventory

The following are the exact distinct ref values in the executable 5GC Skill's PredicateSet. Two Script evaluator refs are listed separately because they are Skill-owned Script references, not Observation sources.

| Predicate Observation Ref | Actual source / owner family | Current schema evidence | Gap / treatment |
|---|---|---|---|
| createdsession.procedure_context | Fabric ingress resident / env-fabric | Ingress observation implementation and source registration | Publish owner Output Schema and provenance/scope/freshness guarantees |
| createdsession.udm_hold | Fabric hold-control + Open5GS hold adapter | Hold client and adapter projection | Publish exact READ result schema |
| createdsession.pcf_hold | Fabric hold-control + Open5GS hold adapter | Hold client and adapter projection | Publish exact READ result schema |
| createdsession.n1n2_hold | Fabric hold-control + Open5GS hold adapter | Hold client and adapter projection | Publish exact READ result schema |
| createdsession.pcf_create_inputs | Provider-backed operation-context / PCF-input adapter | Tool Operation input/output is partly declared; local projection code exists | Close exact normalized result Schema; do not use broad object |
| createdsession.pcf_create_governance | Fabric/hold-governance owner | Governance adapter / resident composition | Current Predicate deliberately remains UNKNOWN when required owner evidence is absent; no fabricated PASS schema |
| createdsession.udm_subscription_resource | Host resource-evidence / reference journal | Local evidence adapter | Publish evidence projection schema and provenance |
| createdsession.pcf_association_resource | Host resource-evidence / reference journal | Local evidence adapter | Publish evidence projection schema and provenance |
| createdsession.n4_baseline | Open5GS N4 adapter backed by Provider SMF/UPF reads | Provider Observation result schema has N4/SMF/UPF data; adapter derives exact baseline | Publish adapter's normalized baseline schema separately from raw Provider payload |
| createdsession.n4_initial_resources | Open5GS N4 evidence adapter | Provider N4 / PFCP / SMF payload schemas plus adapter projection | Publish normalized N4 initial resource schema |
| createdsession.n4_forwarding_resources | Open5GS core-network evidence adapter | Provider SMF/UPF/RAN source schemas plus adapter projection | Publish normalized forwarding schema |
| createdsession.ran_setup_result | Open5GS core-network evidence adapter | Provider smf.ran_setup.snapshot schema plus adapter projection | Publish normalized RAN setup schema |
| createdsession.nas_delivery_context | Provider operation-context / NAS delivery preparation | Tool Operation ca.session.establishment_response.prepare gives partial source schema | Publish normalized delivery-context schema |
| createdsession.amf_transfer_result | Host C-resident AMF transfer evidence source | C-resident transfer result / evidence projection | Publish normalized transfer-result schema and correlation guarantees |
| createdsession.lifecycle_registration | Host lifecycle registry / journal | Host resolver and lifecycle registration implementation | Publish fact/Observation schema and lifecycle provenance |
| createdsession.resource_responsibility | Host resource-responsibility journal | Operation contract and local evidence projection | Publish responsibility projection schema |
| sbi.operation.result | Generic result of the exact preceding Provider Operation invocation | Operation output schemas and invocation receipt | Must be parameterized by exact Operation identity; not a global untyped result payload |

Script references (not Observations): skill.evaluate-transfer-start, skill.evaluate-udm-read.

## 3.1 Exact Host implementation mapping

This mapping was checked against ca-agent-demo/main source files. These are Runtime ObservationSource projections and adapters; the source files do not imply that every ref is a separately callable Tool.

| Observation Ref | Actual Host implementation | Owner wire/source contract currently consumed | Export status |
|---|---|---|---|
| createdsession.procedure_context | integrations/env_fabric/ingress_observation.py + createdsession_ingress.py / resident ingress | Flat Fabric Agent ingress contract; HTTP action ref/revision metadata | Fabric contract schema exists under contracts/proposed/createdsession-agent-ingress/v0.1; adapter consumes flat message + headers |
| createdsession.udm_hold | tools/adapters/open5gs/udm_hold.py + fabric_hold.py | Fabric GET /demo/hold/v1/pending holdView | No exact versioned JSON Schema for current pending/claim wire; proposed held-request-read schema is not a byte-for-byte replacement |
| createdsession.pcf_hold | tools/adapters/open5gs/pcf_hold.py + fabric_hold.py | Same pending/claim wire, PCF-specific exact selector | Same gap |
| createdsession.n1n2_hold | tools/adapters/open5gs/n1n2_hold.py + fabric_hold.py | Same pending/claim wire, N1/N2-specific scope | Same gap |
| createdsession.pcf_create_inputs | integrations/ca_provider_5gc/createdsession_pcf_create_inputs.py | Provider proposed PCF-create-inputs v0alpha2 request/result | Owner schema exists; Host validates pinned vendored copy |
| createdsession.pcf_create_governance | tools/adapters/open5gs/pcf_governance.py | Fabric POST /demo/hold/v1/governance | Proposed Fabric result schema exists; exact Host mirror is pinned in env_fabric/contracts |
| createdsession.udm_subscription_resource | tools/adapters/open5gs/resource_evidence.py + integrations/ca_provider_5gc/createdsession_dispatch.py | Provider operation-dispatch v0alpha1 result + Fabric transaction evidence | Provider proposed result schema exists; Host joins exact committed result into a local Observation |
| createdsession.pcf_association_resource | tools/adapters/open5gs/resource_evidence.py + integrations/ca_provider_5gc/createdsession_dispatch.py | Same dispatch result, PCF-specific result validation | Same |
| createdsession.n4_baseline | tools/adapters/open5gs/n4_evidence.py | Provider N4 initial-resource Observation plus pre-mutation exact read | Raw Provider schema exists; normalized baseline projection has no separate exported Schema |
| createdsession.n4_initial_resources | tools/adapters/open5gs/n4_evidence.py | Provider n4.initial_resources.snapshot | Raw Provider schema exists; normalized Host projection has no separate exported Schema |
| createdsession.n4_forwarding_resources | tools/adapters/open5gs/core_network_evidence.py | Provider n4.forwarding_resources.snapshot + confirmed N4 instance join | Raw Provider schema exists; normalized Host projection has no separate exported Schema |
| createdsession.ran_setup_result | tools/adapters/open5gs/core_network_evidence.py | Provider smf.ran_setup.snapshot + confirmed N4 instance join | Raw Provider schema exists; normalized Host projection has no separate exported Schema |
| createdsession.nas_delivery_context | integrations/ca_provider_5gc/createdsession_operation_context.py | Provider operation-context v0alpha1 purpose=nas-and-n2-delivery | Proposed Provider schema exists; Host predicate projection is narrower |
| createdsession.amf_transfer_result | tools/adapters/open5gs/n1n2_evidence.py + integrations/ca_provider_5gc/createdsession_transfer.py | Provider resident-transfer result / Fabric transfer evidence | Provider has Go validation and proposed schemas; exact Host-normalized projection schema is missing |
| createdsession.lifecycle_registration | tools/adapters/open5gs/responsibility.py | Host CreatedSession reference journal | Host-local prototype contract identity only; no exported payload Schema |
| createdsession.resource_responsibility | tools/adapters/open5gs/responsibility.py | Host CreatedSession reference journal | Host-local prototype contract identity only; no exported payload Schema |
| sbi.operation.result | tools/adapters/open5gs/udm_evidence.py and resource_evidence.py | Exact invocation + transaction-keyed Provider result evidence | Not a global payload: it is a source selector over operation-specific result records; needs a discriminated/parameterized owner contract if exported |

### 3.2 Fabric pending/claim contract mismatch (important)

The Host's current hold adapter uses the actual Demo wire implemented in env-fabric main:
- GET /demo/hold/v1/pending returns {holds:[holdView,...]}.
- POST /demo/hold/v1/claim returns a hold/grant/binding/heldRequest result.
- POST /demo/hold/v1/governance returns the PCF governance projection.

The proposed Fabric `createdsession-held-request-read/v0alpha1` request/result is a separate read-only contract for one holdRef. It is useful owner material but it is **not** the exact schema for the current pending/claim endpoints. Do not mark the hold adapter schema gap closed until the current wire is published or the adapter is explicitly migrated to the proposed contract and verified against Fabric implementation.

## 4. Critical semantic distinction: three schema layers

Do not collapse these into one context-observations.schema.yaml:

1. **Generic Host Observation / Evidence Envelope** — Host-owned: observationRef, status (AVAILABLE / KNOWN_ABSENT / UNKNOWN), normalized value presence rules, provenance, source fact refs, correlation refs, world/snapshot lineage, observed-at/freshness and evidence capability.
2. **Owner READ Operation Output Schema** — owned by the Provider / Fabric / Host / adapter that exposes the read. Declares its exact request scope, normalized output shape, and guarantees. Observation payloads are owner-published read-only source contracts. They are not automatically callable Tool Operations. If an owner explicitly exposes an Observation read as a Tool Operation, that Operation must belong to exactly one Capability.
3. **Skill Predicate consumption contract** — Skill-owned: which Observation ref it requires, scope expression, freshness requirement and evaluator. It consumes materialized facts; it does not own the producer payload schema or acquire the Observation itself.

An ObservationSource implementation can remain an internal Runtime adapter behind a READ Operation. Do not expose both an independently callable Tool and a second parallel Observation tool identity for the same read.

## 5. Capability / Tool relationship

The executable 5GC deployment currently has six Capability groups and twelve Operations. A direct comparison of ca-agent-demo/main confirms: ToolCatalog declares 12 Operations; CapabilityContracts maps 12/12 Operations; there are no Tool-only or Capability-only Operations, no duplicate Operation membership, and all 12 declared READ/MUTATION Effects match exactly. The groups are:

| Capability | Operations |
|---|---|
| provider-5gc.createdsession.udm | sbi.udm.sm_data.get; sbi.udm.sdm_subscription.create |
| provider-5gc.createdsession.pcf | sbi.pcf.sm_policy.create |
| provider-5gc.createdsession.context | ca.session.operation_context.read; ca.session.pcf_create_inputs.read; ca.session.establishment_response.prepare |
| env-fabric.createdsession.hold | ca.session.pcf_hold.bind; ca.session.udm_hold.bind; ca.session.n1n2_hold.bind |
| ca-provider-5gc.createdsession.transfer | sbi.amf.n1n2.transfer |
| ca-agent-host.createdsession.runtime | ca.session.evidence.await; ca.session.resource_responsibility.transfer |

This exact map is verified in the current audited 5GC source. The independent Capability contract maps each Operation to exactly one Capability and expected Effect. ToolCatalog owns callable Operation schemas and declared Effect. The Compiler's future static link must:

- load ToolCatalog and CapabilityContracts from the resolved dependency set;
- reject an Operation missing from either contract;
- reject duplicate Operation membership across Capabilities;
- reject Tool Effect versus Capability expected Effect disagreement;
- reject a Procedure call whose Operation is not in exactly one Capability granted by the Skill;
- keep deployment authorization, runtime admission and backend READY outside Compiler's claims.

The current 5GC Skill's allowedResources.capabilities contains direct Operation IDs for compatibility. Do not silently reinterpret these as Capability IDs. A separate language migration must replace them with the real Capability IDs while preserving the exact set of callable Operations.

## 6. Required Owner publications before WP3

| Owner | Required export |
|---|---|
| Agent Host | Versioned Subject Schema; Facts / ContextFact Schema; generic Observation/Evidence Envelope Schema; lifecycle/resource responsibility projection schemas |
| ca-provider-5gc | Versioned READ Operation contracts and exact normalized result schemas for Provider-backed Observation reads; tighten UDM nested subscription result |
| env-fabric | Versioned ingress, hold and governance READ result schemas with scope, lifecycle, status and provenance semantics |
| Open5GS adapter owner | Versioned normalized N4 baseline, N4 initial resources, forwarding resources and RAN setup result schemas |
| Host C-resident owner | Versioned AMF transfer result and evidence schema |
| Capability contract owner | Versioned CapabilityContracts export with exact Capability → Operation → Effect mapping |

Each export must have stable Schema/Capability identity and a version. A JSON Schema $id alone is not sufficient to establish owner trust; source provenance and publication ownership must be explicit in the resolved dependency snapshot metadata managed by Studio.

## 7. WP2 acceptance gates

1. Every one of the 17 Observation refs is assigned to its actual owner and exact source contract. Record whether it is an internal ObservationSource projection or an explicitly callable Tool Operation; only the latter requires Capability membership. Do not manufacture Operations merely to force an Observation into the Tool model.
2. Each READ Operation has exact request and result schemas; no generic object placeholders for fields consumed by Predicate or Procedure.
3. Generic Host envelope is separated from each owner-specific normalized payload.
4. Capability membership is exact, unique and Effect-consistent with ToolCatalog.
5. Missing or UNKNOWN evidence remains UNKNOWN; schemas do not claim that a source can prove what its implementation cannot.
6. No MAS schema or unverified design artifact enters the executable 5GC dependency set.

## 8. Non-goals

This register does not create owner schemas, change the 5GC Runtime, replace ObservationSource, turn the currently blocked governance Predicate into PASS, or assert the 5GC Skill is newly compiled by the vNext Compiler. It records the code-derived gaps to close before the no-lib compile acceptance.


### 5.1 Verified Capability coverage result

Audit script comparison of the two source YAML documents returned: Tool Operations = 12; Capability membership entries = 12; Capability groups = 6; Tool-only = 0; Capability-only = 0; duplicate membership = 0; Effect mismatches = 0. This is a source-contract consistency result, not a Runtime authorization or READY assertion.


## 9. Owner repository source audit (2026-11-12)

The earlier statement that several owner schemas were simply absent was too broad. The source repositories already contain substantial **proposed** owner contracts. They must be consumed as owner-owned sources (and promoted/versioned through their own release process), not copied into the Skill or Compiler repository.

| Owner | Existing source contract | Maturity | Mapping / limitation |
|---|---|---|---|
| ca-provider-5gc | `schemas/provider-observation-read-request.schema.yaml`, `schemas/provider-observation-read-result.schema.yaml` | Owner schema present on main; `$id` values are relative filenames, not yet stable absolute vNext export IDs | Six raw Provider Observation refs are exposed through one ref-discriminated wire API. The Skill should not call that generic selector directly; adapter-facing vNext Operations should expose exact N4 initial-resource, SMF RAN-setup and UPF N4-forwarding read identities |
| ca-provider-5gc | `contracts/proposed/createdsession-operation-context/v0alpha1/{request,result}.schema.yaml` | Proposed | Supports operation-context facts used by PCF/NAS preparation; not a general Host Context schema |
| ca-provider-5gc | `contracts/proposed/createdsession-pcf-create-inputs/v0alpha2/{request,result}.schema.yaml` | Proposed | Exact PCF input-read readiness, held-request lineage, allocated address, field provenance; not PCF create governance or association ownership |
| env-fabric | `contracts/proposed/createdsession-held-request-read/v0alpha1/{request,result}.schema.yaml` | Proposed | Exact held SMF request, hold/lifecycle/current instance, request digest and deadline; does not prove sender authorization, create or delivery. This is a Provider-facing read path, not the Agent's loopback `/demo/hold/v1/pending` / `/claim` API |
| env-fabric | `contracts/proposed/createdsession-agent-ingress/v0.1/agent-message.schema.yaml` | Candidate / not approved product API | Flat Agent ingress message; its `sd` field allows the full 24-bit range, but the `0xFFFFFF` no-SD sentinel semantics were not explicit in the owner README at the audit point |
| env-fabric | `contracts/proposed/createdsession-pcf-create-governance/v0alpha1/result.schema.yaml` | Proposed | Hold state, sender authorization, competing-create state, lifecycle isolation and evidence refs; matches the semantic owner for `createdsession.pcf_create_governance` |
| env-fabric | `contracts/proposed/createdsession-lifecycle-isolation/v0alpha1/evidence.schema.yaml` | Proposed | Operator-owned isolation declaration consumed by Fabric; not an Agent business fact |
| env-fabric | `contracts/proposed/createdsession-amf-n1n2-transfer/v0.1/transfer-result.schema.yaml` | Proposed candidate | Detailed Fabric transfer attempt record; needs an explicit normalized Host Observation projection and lifecycle/correlation mapping |
| ca-agent-demo / Host | `src/ca_agent_host/agent/host/schemas/*` and `src/ca_agent_host/integrations/fivegc/contracts/observations/*` | Draft Owner exports: PR #198 (3 schemas) and PR #200 (15 schemas, 16/17 Observation refs) | Real Subject/Facts/Script Evidence-reference and normalized Observation projections are proposed; PR #198 focused CI 3 passed and PR #200 focused CI 5 passed; both remain unmerged |
| ca-agent-demo / Host | `src/ca_agent_host/integrations/env_fabric/contracts/createdsession-pcf-create-governance-result.schema.yaml` and Provider mirrored wire schemas | Consumer snapshots / projections | The PCF governance mirror is byte-identical to Fabric's proposed result Schema; mirrors are not replacements for the Fabric/Provider source-of-truth schemas |

### 9.1 Corrections to the initial gap classification

- The six Provider Observation schemas are real owner files in ca-provider-5gc main, not only Host-local mirrors.
- Fabric already has proposed held-request, PCF governance, lifecycle-isolation and AMF transfer schemas. Do not create duplicate schemas in ca-agent-demo.
- Provider already has proposed operation-context and PCF-create-inputs schemas. They cover specific operation outputs, not generic Host Context.
- The remaining major gap is the **Host-owned generic envelope and context export**, plus normalized Host Observation projections for Fabric/Provider/adapter results and a stable release/publication boundary for proposed owner contracts.
- A proposed schema is not automatically a stable exported contract. Compiler should only link a schema included in the selected dependency snapshot with explicit owner identity/version and a supported contract status.



## 10. Cross-repository schema publication status (2026-11-12)

The following parallel Owner work is now verified and must be treated as the implementation baseline, not re-created:

| PR | Owner repository | Contribution | Latest observed status |
|---|---|---|---|
| [ca-agent-demo #198](https://github.com/odango-chan/ca-agent-demo/pull/198) | Agent Host | Host Subject, Facts and Script-facing Predicate Evidence reference schemas | OPEN / DRAFT; focused CI **3 passed, 0 failed** |
| [ca-agent-demo #199](https://github.com/odango-chan/ca-agent-demo/pull/199) | Agent Host | Code-derived normalized output inventory for all 17 refs | OPEN / DRAFT; docs-only, refreshed with UDM SD semantics |
| [ca-agent-demo #200](https://github.com/odango-chan/ca-agent-demo/pull/200) | Agent Host + Open5GS adapters | 15 normalized output Schema files covering 16/17 refs; two-branch N4 Schema fixture | OPEN / DRAFT; focused CI **5 passed, 0 failed** |
| [ca-provider-5gc #50](https://github.com/odango-chan/ca-provider-5gc/pull/50) | Provider | Exact nested UDM GetSmData subscription Output Schema; removes broad object placeholders | OPEN / DRAFT; **no GitHub check-runs observed** |

PR #50 is specifically intended to close the upstream Provider wire-schema blocker for `sbi.operation.result`. It does **not** by itself publish the Host adapter's normalized `AcquiredObservation.value` Schema. That Host projection still needs to be added after the Provider schema is accepted, the Agent consumer snapshot is refreshed, and the ToolCatalog output contract is linked to the imported Provider schema.

PR #200 currently runs the dedicated normalized-Schema/fixture test file (**5 passed**); it does not re-run the live 5GC flow or claim every ObservationSource output has been revalidated. PR #198 runs the Host Owner Schema tests (**3 passed**); it publishes the Subject/Facts and Script-facing Evidence-reference projections, not the full Runtime ObservationEvidence envelope.

The two Agent PRs now carry byte-identical, narrow CI workflow definitions, avoiding a same-path workflow-add conflict. Each branch runs the dedicated schema test files that are present there; no additional source-output conformance suite is required for the current feasibility review.

The generic Runtime ObservationEvidence dataclasses remain Host-internal. This is intentional until a separate cross-runtime consumer needs that envelope; do not publish it merely to satisfy a Compiler file-count target.


## 11. Consolidated Owner Export Map (2026-11-12)

This is the cross-repository export inventory for the runnable conventional 5GC Skill. Repository paths below are **audit locators only**; they are not proposed Skill syntax. The vNext Skill references a stable exported contract identity qualified by a logical dependency alias. Studio resolves aliases to owner-published snapshots; Compiler receives the resolved bytes and does not fetch, lock, cache, or manage packages.

| Contract / export | Owner and source locator | Identity / scope | Current state and consumer rule |
|---|---|---|---|
| Skill Request Schema | `ca-skills/skills/establish-pdu-session/schemas/establishment-request.schema.yaml` | `$id: establishment-request.schema.yaml` | Skill-owned authority for `context.request`; do not duplicate in Host or Observation exports |
| Skill Predicate input/output schemas | `ca-agent-demo/skills/establish-pdu-session/schemas/udm-read-evaluation-input.schema.yaml` and `predicate-evaluation-result.schema.yaml` | `udm-read-evaluation-input.schema.yaml`, `predicate-evaluation-result.schema.yaml` | Skill-owned consumer contracts present in the executable ca-agent-demo copy but absent from ca-skills/main at the audited paths. They do not replace Provider/Host Owner schemas; the nested subscription shape must remain traceable to the Provider contract |
| ToolCatalog | `ca-agent-demo/tools/contracts/createdsession.tool.yaml`; mirrored in `ca-skills/lib/tools/createdsession.tool.yaml` | `ca-agent-demo.tool/v1 ToolCatalog`, metadata name `createdsession` | 12 Operations. `sbi.udm.sm_data.get.outputSchema.result` remains broad `type: object`; after Provider #50 is accepted, link the imported Provider result schema rather than duplicating nested fields |
| CapabilityContracts data | `ca-agent-demo/tools/contracts/capabilities/createdsession.capabilities.yaml` | `ca-agent-host.capability-contracts/v1 CapabilityContracts`, metadata name `5gc-createdsession-capabilities` | Deployment-owned mapping: 6 Capability groups / 12 Operation memberships. Runtime Host checks it; Compiler PR5 does not import or statically link it yet |
| Host Subject | `ca-agent-demo` PR #198: `src/ca_agent_host/integrations/fivegc/contracts/skill-subject.schema.yaml` | `urn:connectionagent:5gc:skill-context:subject:v1` | Draft Owner export; CI 38 passed with the combined Host/UDM test workflow |
| Host Facts | `ca-agent-demo` PR #198: `src/ca_agent_host/integrations/fivegc/contracts/skill-facts.schema.yaml` | `urn:connectionagent:5gc:skill-context:facts:v1` | Draft Owner export; exact ingress/lifecycle handles, no inferred business facts |
| Script Evidence refs | `ca-agent-demo` PR #198: `src/ca_agent_host/agent/host/schemas/predicate-evidence-refs.schema.yaml` | `urn:connectionagent:host:predicate-evidence-refs:v1` | Draft Host projection; not the full Runtime ObservationEvidence envelope |
| Normalized Observation outputs | `ca-agent-demo` PR #200: `src/ca_agent_host/integrations/fivegc/contracts/observations/procedure-context.schema.yaml` plus `tools/adapters/open5gs/contracts/observations/*.schema.yaml` | 15 identities: `createdsession.procedure_context`, `createdsession.amf_transfer_result`, `createdsession.lifecycle_registration`, `createdsession.n1n2_hold`, `createdsession.n4_baseline`, `createdsession.n4_forwarding_resources`, `createdsession.n4_initial_resources`, `createdsession.nas_delivery_context`, `createdsession.pcf_create_governance`, `createdsession.pcf_create_inputs`, `createdsession.pcf_hold`, `createdsession.ran_setup_result`, `createdsession.resource_ownership`, `createdsession.resource_responsibility`, `createdsession.udm_hold` (all `urn:connectionagent:5gc:observation:*:v1`) | Draft normalized-output bundle; 15 Schemas cover 16/17 refs because resource ownership shares one structural Schema; 5 focused Schema/fixture tests pass. `sbi.operation.result` remains deferred |
| Provider UDM GetSmData result | `ca-provider-5gc/schemas/proposed/provider-udm-get-v0alpha2-result.schema.yaml`, PR #50 | `https://connectionagent.io/proposed/provider-udm-get/v0alpha2/result.schema.yaml` | Proposed Owner schema; PR #50 Draft, no CI check-runs. Not a stable export yet |
| Fabric Agent ingress | `env-fabric/contracts/proposed/createdsession-agent-ingress/v0.1/agent-message.schema.yaml` | `https://service-fabric.io/contracts/createdsession-agent-ingress/v0.1/agent-message.schema.yaml` | Candidate, explicitly not an approved product API. Any reserved-SD wire semantics remain an Owner contract question; PR #200 does not change cross-component SD handling |
| Fabric PCF governance | `env-fabric/contracts/proposed/createdsession-pcf-create-governance/v0alpha1/result.schema.yaml` | `https://connectionagent.io/proposed/env-fabric/createdsession-pcf-create-governance/v0alpha1/result.schema.yaml` | Proposed Fabric Owner result; required fields match `demoHoldGovernance`'s current JSON response, the Go governance test's wire struct and Agent's strict manual parser; Agent mirror is byte-identical. However `scripts/contract_gate.py` scans only canonical `schemas/v1alpha1`, not `contracts/proposed`, and the Go test does not validate its captured JSON against this Schema. Add a proposed-contract schema gate. Normalized Observation projection is a separate PR #200 Schema |
| Fabric held-request read | `env-fabric/contracts/proposed/createdsession-held-request-read/v0alpha1/result.schema.yaml` | `https://connectionagent.io/proposed/env-fabric/createdsession-held-request-read/v0alpha1/result.schema.yaml` | Proposed Provider-facing read contract; not the loopback pending/claim API currently consumed by Agent |
| Fabric loopback Hold control | Actual `GET /demo/hold/v1/pending` and `POST /demo/hold/v1/claim` in `env-fabric/internal/inline/sbi/demo_hold_http.go` | No published Schema identity | Missing Owner export. Agent currently parses the wire shape manually. Do not pretend the held-request-read contract covers this API |
| Host normalized `sbi.operation.result` | `ca-agent-demo` `CreatedSessionUDMObservationSource.runtime_value()` | Not yet exported | Blocked on Provider's exact nested subscription result; after Provider #50 is accepted, publish a separate Host Observation projection Schema and test the real source |

### 11.1 Complete normalized Observation export identities

The 15 proposed Observation Schema identities in PR #200 are:

- `urn:connectionagent:5gc:observation:createdsession.procedure_context:v1`
- `urn:connectionagent:5gc:observation:createdsession.amf_transfer_result:v1`
- `urn:connectionagent:5gc:observation:createdsession.lifecycle_registration:v1`
- `urn:connectionagent:5gc:observation:createdsession.n1n2_hold:v1`
- `urn:connectionagent:5gc:observation:createdsession.n4_baseline:v1`
- `urn:connectionagent:5gc:observation:createdsession.n4_forwarding_resources:v1`
- `urn:connectionagent:5gc:observation:createdsession.n4_initial_resources:v1`
- `urn:connectionagent:5gc:observation:createdsession.nas_delivery_context:v1`
- `urn:connectionagent:5gc:observation:createdsession.pcf_create_governance:v1`
- `urn:connectionagent:5gc:observation:createdsession.pcf_create_inputs:v1`
- `urn:connectionagent:5gc:observation:createdsession.pcf_hold:v1`
- `urn:connectionagent:5gc:observation:createdsession.ran_setup_result:v1`
- `urn:connectionagent:5gc:observation:createdsession.resource_ownership:v1`
- `urn:connectionagent:5gc:observation:createdsession.resource_responsibility:v1`
- `urn:connectionagent:5gc:observation:createdsession.udm_hold:v1`

### 11.2 UDM SD semantic correction

No cross-component SD sentinel normalization is part of these Owner Schema PRs. Keep raw ingress semantics and adapter-normalized Observation values as separate contracts; do not infer or silently change the reserved-value meaning as part of the Skill vNext feasibility work.

## 12. Compiler consumption and Capability static-link audit

The current Compiler v0.1 implementation does not yet consume the complete Owner export set:

- `internal/compiler/library.go` imports only `lib/tools/*.yaml` ToolCatalog files. It does not load Host, Observation, or CapabilityContracts exports.
- `internal/compiler/schema_refs.go` resolves project-local JSON Pointer references from imported files and explicitly forbids remote/absolute references. This is appropriate for a no-network Compiler, but the caller must supply the exact referenced Owner schemas in the resolved dependency snapshot.
- `internal/compiler/skills.go` checks that `context.schemas.subject/facts/observations/evidence` paths are present for Script Predicates. The current v0.2 path-based `lib/...` compatibility model is not yet the vNext identity-based Owner export model. In addition, the latest executable `ca-agent-demo` Skill copy contains `UdmReadEvaluationInput` and `PredicateEvaluationResult` schemas plus `evaluate_udm_read.py`, but the audited `ca-skills/main` Skill source does not yet contain those files. Because `ca-skills` is the authoritative Skill input, this source refresh must happen before Compiler can build that latest Skill from the authoritative repo. The consumer schema's nested `subscription` shape is not a substitute for the Provider Owner Output Schema.
- Compiler PR #4 defines a CapabilityContracts JSON Schema, but the current PR #5 core has no CapabilityContracts loader/linker. `allowedResources.capabilities` is currently checked as a string sequence; it is not statically resolved from Capability IDs to Operations and Effects.
- Runtime Host does load the deployment-owned CapabilityContracts file and cross-checks it with ToolCatalog operation/effect declarations before execution. The current source audit found 12/12 Tool Operations mapped, 6 Capability groups, no missing/duplicate memberships and no Effect mismatches. This is runtime/deployment validation, not Compiler static proof.
- Compiler PR #7 is a candidate-only semantic binding resolver spike; PR #8 is a schema-engine spike. Neither currently integrates CapabilityContracts linking into the v0.1 build path.

Therefore the answer to “can Capability authorization be statically validated?” is: **the contract model is designed to support it, and the Host validates it at runtime, but the current Compiler implementation does not yet prove it at compile time.** Do not claim static authorization until the Compiler imports CapabilityContracts and proves every called Operation belongs to exactly one granted Capability with matching Effect.

## 13. Current vNext feasibility gates

1. Use the existing Skill-owned UDM consumer schemas for the first migration rehearsal: `selection-input.schema.yaml`, `udm-read-evaluation-input.schema.yaml` and `predicate-evaluation-result.schema.yaml`. Do not block this review on Provider PR #50 or create a duplicate Skill schema for the Provider result.
2. Keep nested `sbi.operation.result` producer bindings explicit while the Provider Output Schema remains broad. No field inference or automatic binding is allowed without the Owner contract.
3. Model the exact stored-result acquisition and its evidence when migrating `createdsession.udm.subscription_usable` to a pure Predicate. Reuse the prior Operation output only if its data and evidence prove the same invocation/transaction identity; do not issue another external UDM Get merely to satisfy the authoring syntax.
4. Keep Capability → Operation → Effect linking as a contract requirement for the new model. Compiler implementation is a later consumer task; this design review does not add or reimplement Compiler behavior.
