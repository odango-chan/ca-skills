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
| Host Context model | agent/context/base.py, projection, requirements, loader and resolvers | Implemented Python Subject / Facts / ContextFact / ContextRequirement / provenance and resolver behavior; Host PR #198 merged Invocation Context and Script Evidence-reference Schemas | Stable Host Schema exports are on ca-agent-demo/main; full Runtime Operation Evidence remains a separate vNext Runtime gap |
| Skill Request | skills/establish-pdu-session/schemas/establishment-request.schema.yaml | Real Skill-owned public input contract | Does not substitute for Host Context or Observation schemas |

## 3. Observation reference inventory

The following are the exact distinct ref values in the executable 5GC Skill's PredicateSet. Two Script evaluator refs are listed separately because they are Skill-owned Script references, not Observation sources.

| Predicate Observation Ref | Actual source / owner family | Current schema evidence | Gap / treatment |
|---|---|---|---|
| createdsession.procedure_context | Fabric ingress resident / env-fabric | Ingress observation implementation and source registration; Host PR #200 merged the normalized `procedure-context` payload Schema | Preserve trusted ingress source provenance; Fabric wire contract remains a separate candidate and needs stable owner identity/freshness guarantees |
| createdsession.udm_hold | Fabric hold-control + Open5GS hold adapter | Host PR #200 merged the normalized projection Schema | The Agent loopback pending/claim wire still lacks its own Owner Schema. Preserve exact selector, lifecycle, correlation and deadline checks |
| createdsession.pcf_hold | Fabric hold-control + Open5GS hold adapter | Host PR #200 merged the normalized projection Schema | The Agent loopback pending/claim wire still lacks its own Owner Schema. Preserve exact selector, lifecycle, correlation and deadline checks |
| createdsession.n1n2_hold | Fabric hold-control + Open5GS hold adapter | Host PR #200 merged the normalized projection Schema | The Agent loopback pending/claim wire still lacks its own Owner Schema. Preserve exact selector, lifecycle, correlation and deadline checks |
| createdsession.pcf_create_inputs | Provider-backed operation-context / PCF-input adapter | Host PR #200 merged the 11-field normalized Predicate projection Schema | The Tool output itself carries six handles/digests only. Resolve the exact stored Provider result and Evidence locally; do not add another network read |
| createdsession.pcf_create_governance | Fabric/hold-governance owner | Host PR #200 merged the normalized Host projection; Fabric PR #81 merged the governance READ Tool contract and exact request Schema | The Fabric result Schema remains under `contracts/proposed`; preserve UNKNOWN when required owner evidence is absent. Preserve UNKNOWN when required owner evidence is absent; no fabricated PASS |
| createdsession.udm_subscription_resource | Host resource-evidence / reference journal | Host PR #200 merged the shared structural `resource-ownership` projection Schema | Bind the exact committed subscription result and durable resource Evidence; keep distinct from PCF association fact identity |
| createdsession.pcf_association_resource | Host resource-evidence / reference journal | Host PR #200 merged the shared structural `resource-ownership` projection Schema | Bind the exact committed PCF result and durable resource Evidence; keep distinct from UDM subscription fact identity |
| createdsession.n4_baseline | Open5GS N4 adapter backed by Provider SMF/UPF reads | Host PR #200 merged normalized baseline Schema and two-branch fixture | Preserve `PRE_CREATE` baseline identity and `baselineRef`; raw Provider payload and normalized adapter projection remain distinct |
| createdsession.n4_initial_resources | Open5GS N4 evidence adapter | Host PR #200 merged normalized post-create N4 Schema | Require exact baseline lineage (`baselineEvidenceRef`) and exact confirmed `currentSessionInstanceRef`; do not select latest-per-UE |
| createdsession.n4_forwarding_resources | Open5GS core-network evidence adapter | Host PR #200 merged normalized forwarding Schema | READ must consume the exact confirmed N4 instance and prove the matching SMF/UPF pair |
| createdsession.ran_setup_result | Open5GS core-network evidence adapter | Host PR #200 merged normalized RAN setup Schema | READ must consume and echo the exact confirmed N4 instance, not latest-per-UE |
| createdsession.nas_delivery_context | Provider operation-context / NAS delivery preparation | Host PR #200 merged normalized delivery-context Schema | Operation Context output only carries context/invocation refs, so resolve the five-field projection from the exact stored Provider result and Evidence |
| createdsession.amf_transfer_result | Host C-resident AMF transfer evidence source | Host PR #200 merged normalized transfer-result Schema | Preserve exact operation/transaction correlation and nullable response-field normalization over the captured transfer result |
| createdsession.lifecycle_registration | Host lifecycle registry / journal | Host PR #200 merged normalized lifecycle-journal payload Schema; Host PR #203 also merged the explicit lifecycle READ Operation | Exact journal identity, lifecycle selector and freshness remain required |
| createdsession.resource_responsibility | Host resource-responsibility journal | Host PR #200 merged normalized responsibility-journal payload Schema; Host PR #203 also merged the explicit responsibility READ Operation | Prove durable journal state, coverage and retained pending responsibilities; mutation success alone is insufficient |
| sbi.operation.result | Host-facing result of the preceding UDM Provider Operation | Provider PR #50 proposes the full upstream GetSmData result Schema; Host `CreatedSessionUDMResult.runtime_value()` defines the normalized Tool `output.result` | vNext binds the exact Host Tool `output.result` plus same-receipt Host Evidence. A separate Host projection Schema is required for this Skill-facing payload; Provider PR #50 validates the upstream response inside Host and is not a substitute. ToolCatalog remains broad `object`, and Host pins an older broad Provider snapshot. Preserve exact Operation/invocation/transaction/record identity; never model a global untyped result |

Script references (not Observations): skill.evaluate-transfer-start, skill.evaluate-udm-read.

## 3.1 Exact Host implementation mapping

This mapping was checked against ca-agent-demo/main source files. These are Runtime ObservationSource projections and adapters; the source files do not imply that every ref is a separately callable Tool.

| Observation Ref | Actual Host implementation | Owner wire/source contract currently consumed | Export status |
|---|---|---|---|
| createdsession.procedure_context | integrations/env_fabric/ingress_observation.py + createdsession_ingress.py / resident ingress | Flat Fabric Agent ingress contract; HTTP action ref/revision metadata | Host PR #200 merged the normalized payload Schema; Fabric wire Schema remains a separate candidate. Stable Host ingress export identity and source provenance remain required |
| createdsession.udm_hold | tools/adapters/open5gs/udm_hold.py + fabric_hold.py | Fabric GET /demo/hold/v1/pending holdView | Host PR #200 merged the normalized Host payload Schema; raw pending/claim loopback wire still has no exact Owner Schema. Proposed held-request-read is not a byte-for-byte replacement |
| createdsession.pcf_hold | tools/adapters/open5gs/pcf_hold.py + fabric_hold.py | Same pending/claim wire, PCF-specific exact selector | Normalized Host payload Schema proposed in PR #200; raw pending/claim loopback wire still has no exact Owner Schema |
| createdsession.n1n2_hold | tools/adapters/open5gs/n1n2_hold.py + fabric_hold.py | Same pending/claim wire, N1/N2-specific scope | Normalized Host payload Schema proposed in PR #200; raw pending/claim loopback wire still has no exact Owner Schema |
| createdsession.pcf_create_inputs | integrations/ca_provider_5gc/createdsession_pcf_create_inputs.py | Provider proposed PCF-create-inputs v0alpha2 request/result | Host PR #200 merged the normalized Host Predicate payload Schema; Tool output is only six handles/digests and the 11-field payload comes from the exact stored Provider result |
| createdsession.pcf_create_governance | tools/adapters/open5gs/pcf_governance.py | Fabric POST /demo/hold/v1/governance | Host PR #200 merged the normalized Host payload Schema; Fabric PR #81 merged the governance Tool contract. The upstream result Schema remains under `contracts/proposed`. |
| createdsession.udm_subscription_resource | tools/adapters/open5gs/resource_evidence.py + integrations/ca_provider_5gc/createdsession_dispatch.py | Provider operation-dispatch v0alpha1 result + Fabric transaction evidence | Host PR #200 merged the shared normalized `resource-ownership` Schema; source still joins the exact committed result and durable resource Evidence |
| createdsession.pcf_association_resource | tools/adapters/open5gs/resource_evidence.py + integrations/ca_provider_5gc/createdsession_dispatch.py | Same dispatch result, PCF-specific result validation | Host PR #200 merged the shared structural Schema; retain separate PCF fact identity and exact association handle |
| createdsession.n4_baseline | tools/adapters/open5gs/n4_evidence.py | Provider N4 initial-resource Observation plus pre-mutation exact read | Host PR #200 merged the normalized baseline Schema and two-branch fixture. Preserve `PRE_CREATE` baselineRef separately from post-create instance identity |
| createdsession.n4_initial_resources | tools/adapters/open5gs/n4_evidence.py | Provider n4.initial_resources.snapshot | Host PR #200 merged the normalized post-create Schema. Require exact baselineEvidenceRef and currentSessionInstanceRef lineage |
| createdsession.n4_forwarding_resources | tools/adapters/open5gs/core_network_evidence.py | Provider n4.forwarding_resources.snapshot + confirmed N4 instance join | Host PR #200 merged the normalized forwarding Schema. READ must be scoped to the exact confirmed N4 instance and SMF/UPF pair |
| createdsession.ran_setup_result | tools/adapters/open5gs/core_network_evidence.py | Provider smf.ran_setup.snapshot + confirmed N4 instance join | Host PR #200 merged the normalized RAN Schema. READ must be scoped to and echo the exact confirmed N4 instance |
| createdsession.nas_delivery_context | integrations/ca_provider_5gc/createdsession_operation_context.py | Provider operation-context v0alpha1 purpose=nas-and-n2-delivery | Host PR #200 merged the normalized Host payload Schema. Tool output is only context/invocation refs; five-field projection comes from exact stored Provider result |
| createdsession.amf_transfer_result | tools/adapters/open5gs/n1n2_evidence.py + integrations/ca_provider_5gc/createdsession_transfer.py | Provider resident-transfer result / Fabric transfer evidence | Host PR #200 merged the normalized Host projection Schema. Preserve operation correlation and nullable-field normalization |
| createdsession.lifecycle_registration | tools/adapters/open5gs/responsibility.py | Host CreatedSession reference journal | Host PR #200 merged the normalized lifecycle-journal payload Schema; PR #203 merged the explicit lifecycle READ Operation. Exact Host journal owner identity and freshness remain required |
| createdsession.resource_responsibility | tools/adapters/open5gs/responsibility.py | Host CreatedSession reference journal | Host PR #200 merged the normalized responsibility-journal payload Schema; PR #203 merged the explicit responsibility READ Operation. It must prove durable coverage and retained pending responsibilities |
| sbi.operation.result | tools/adapters/open5gs/udm_evidence.py and resource_evidence.py | Exact invocation + transaction-keyed Provider result evidence | Legacy ObservationSource and Tool output both expose `CreatedSessionUDMResult.runtime_value()`. vNext binds the exact Host Tool `output.result` plus same-receipt Evidence; publish one Host projection Schema for that payload and reuse it for the Tool output and legacy Observation value. Do not create another network READ or a global untyped result |

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
| ca-agent-demo / Host | `src/ca_agent_host/agent/host/schemas/*` and `src/ca_agent_host/integrations/fivegc/contracts/observations/*` | Merged Owner exports: PR #198 (3 focused tests) and PR #200 (7 focused tests; 15 schemas covering 16/17 Observation refs) | Invocation Context, Script Evidence-reference and normalized Observation projection Schemas are available on ca-agent-demo/main; they are not the full Runtime Operation Evidence envelope |
| ca-agent-demo / Host | `src/ca_agent_host/integrations/env_fabric/contracts/createdsession-pcf-create-governance-result.schema.yaml` and Provider mirrored wire schemas | Consumer snapshots / projections | The PCF governance mirror is byte-identical to Fabric's proposed result Schema; mirrors are not replacements for the Fabric/Provider source-of-truth schemas |

### 9.1 Corrections to the initial gap classification

- The six Provider Observation schemas are real owner files in ca-provider-5gc main, not only Host-local mirrors.
- Fabric already has proposed held-request, PCF governance, lifecycle-isolation and AMF transfer schemas. Do not create duplicate schemas in ca-agent-demo.
- Provider already has proposed operation-context and PCF-create-inputs schemas. They cover specific operation outputs, not generic Host Context.
- PR #198 and PR #200 are merged and publish the narrow Host surfaces needed by the Skill: Invocation Context, Script-facing Evidence refs, ingress procedure context, and reference-journal payload projections. The full Runtime `ObservationEvidence` dataclasses remain Host-internal by design; they are not a required Skill export. The remaining gaps are stable Owner publication/aliasing, the Host-normalized UDM Tool/Observation result Schema, exact adapter-facing READ Operation contracts, proven same-receipt Evidence attachment, and the separate Fabric loopback pending/claim wire Schema.
- A proposed schema is not automatically a stable exported contract. Compiler should only link a schema included in the selected dependency snapshot with explicit owner identity/version and a supported contract status.



## 10. Cross-repository schema publication status (2026-11-12)

The following parallel Owner work is now verified and must be treated as the implementation baseline, not re-created:

| PR | Owner repository | Contribution | Latest observed status |
|---|---|---|---|
| [ca-agent-demo #198](https://github.com/odango-chan/ca-agent-demo/pull/198) | Agent Host | CA Invocation Context and Script-facing Predicate Evidence reference Schemas | OPEN / DRAFT; focused CI **3 passed, 0 failed** |
| [ca-agent-demo #199](https://github.com/odango-chan/ca-agent-demo/pull/199) | Agent Host | Code-derived normalized output inventory for all 17 refs | OPEN / DRAFT; docs-only, refreshed with UDM SD semantics |
| [ca-agent-demo #200](https://github.com/odango-chan/ca-agent-demo/pull/200) | Agent Host + Open5GS adapters | 15 normalized output Schema files covering 16/17 refs; two-branch N4 Schema fixture | OPEN / DRAFT; focused CI **5 passed, 0 failed** |
| [ca-provider-5gc #50](https://github.com/odango-chan/ca-provider-5gc/pull/50) | Provider | Exact nested UDM GetSmData subscription Output Schema; removes broad object placeholders | OPEN / DRAFT; **no GitHub check-runs observed** |

PR #50 proposes the upstream Provider wire-result Schema used inside the Host adapter; it is not yet accepted or linked. The Tool Operation `output.result` is the Host-normalized `runtime_value()` projection, not the Provider wire result. vNext binds that exact Host result plus same-receipt Evidence, so a separate Host projection Schema is required. Before static linking is claimed, accept the Provider `$id`, refresh the Host adapter's vendored Provider snapshot/digest, publish the Host projection `$id`, and link ToolCatalog `outputSchema.result` to the Host Schema.

PR #200's dedicated normalized-Schema/fixture workflow passed **7 tests**; it does not re-run the live 5GC flow or claim every ObservationSource output has been exhaustively replayed. The focused suite validates the 15 Schema shapes/fixtures and exercises a real UDM Hold source projection; it is not an exhaustive 15-source replay. PR #198's Host Owner Schema workflow passed **3 tests**; it publishes Invocation Context and Script-facing Evidence-reference Schemas, not the full Runtime Operation Evidence envelope.

The two Agent PRs now carry byte-identical, narrow CI workflow definitions, avoiding a same-path workflow-add conflict. Each branch runs the dedicated schema test files that are present there; no additional source-output conformance suite is required for the current feasibility review.

The generic Runtime ObservationEvidence dataclasses remain Host-internal. This is intentional until a separate cross-runtime consumer needs that envelope; do not publish it merely to satisfy a Compiler file-count target.


## 11. Consolidated Owner Export Map (2026-11-12)

This is the cross-repository export inventory for the runnable conventional 5GC Skill. Repository paths below are **audit locators only**; they are not proposed Skill syntax. The vNext Skill references a stable exported contract identity qualified by a logical dependency alias. Studio resolves aliases to owner-published snapshots; Compiler receives the resolved bytes and does not fetch, lock, cache, or manage packages.

| Contract / export | Owner and source locator | Identity / scope | Current state and consumer rule |
|---|---|---|---|
| Skill Request Schema | `ca-skills/skills/establish-pdu-session/schemas/establishment-request.schema.yaml` | `$id: establishment-request.schema.yaml` | Skill-owned authority for `context.request`; do not duplicate in Host or Observation exports |
| Legacy Script input/output Schema files | 11 files under `ca-agent-demo/skills/establish-pdu-session/schemas/` | Legacy `connectionagent-tool` metadata contract | Present only in the Agent-side legacy dialect; intentionally not copied into official ca-skills v0.2. Procedure Script inputs are derived per call site, Script outputs are generated from TypedDict, and Predicate evaluator input is derived from Host schemas plus declared observations. The legacy UDM/selection projections remain useful evidence for the open vNext Predicate-input projection decision, not importable v0.2 source contracts |
| ToolCatalog | `ca-agent-demo/tools/contracts/createdsession.tool.yaml`; mirrored in `ca-skills/lib/tools/createdsession.tool.yaml` | `ca-agent-demo.tool/v1 ToolCatalog`, metadata name `createdsession` | 12 Operations. `sbi.udm.sm_data.get.outputSchema.result` remains broad `type: object`; after Provider #50 is accepted and the Host projection Schema is published, link this field to the Host `runtime_value()` export. Separately refresh the Host adapter's pinned Provider wire-schema snapshot/digest |
| CapabilityContracts data | `ca-agent-demo/tools/contracts/capabilities/createdsession.capabilities.yaml` | `ca-agent-host.capability-contracts/v1 CapabilityContracts`, metadata name `5gc-createdsession-capabilities` | Deployment-owned mapping: 6 Capability groups / 12 Operation memberships. Runtime Host checks it; Compiler PR5 does not import or statically link it yet |
| CA Invocation Context | `ca-agent-demo` PR #198: `src/ca_agent_host/integrations/fivegc/contracts/invocation-context.schema.yaml` | `urn:connectionagent:ca:context:invocation:v1` | Merged Host Owner export with UE and exact ingress/lifecycle references |
| Script Evidence refs | `ca-agent-demo` PR #198: `src/ca_agent_host/agent/host/schemas/predicate-evidence-refs.schema.yaml` | `urn:connectionagent:host:predicate-evidence-refs:v1` | Merged Host projection; not the full Runtime Operation Evidence envelope |
| Normalized Observation outputs | `ca-agent-demo` PR #200: `src/ca_agent_host/integrations/fivegc/contracts/observations/procedure-context.schema.yaml` plus `tools/adapters/open5gs/contracts/observations/*.schema.yaml` | 15 identities: `createdsession.procedure_context`, `createdsession.amf_transfer_result`, `createdsession.lifecycle_registration`, `createdsession.n1n2_hold`, `createdsession.n4_baseline`, `createdsession.n4_forwarding_resources`, `createdsession.n4_initial_resources`, `createdsession.nas_delivery_context`, `createdsession.pcf_create_governance`, `createdsession.pcf_create_inputs`, `createdsession.pcf_hold`, `createdsession.ran_setup_result`, `createdsession.resource_ownership`, `createdsession.resource_responsibility`, `createdsession.udm_hold` (all `urn:connectionagent:5gc:observation:*:v1`) | Merged normalized-output bundle; 15 Schemas cover 16/17 legacy Observation refs because resource ownership shares one structural Schema; 7 focused Schema/fixture tests pass. The remaining `sbi.operation.result` / UDM Tool output needs a separate Host-owned normalized projection Schema; it is not the Provider wire Schema |
| Provider UDM GetSmData result | `ca-provider-5gc/schemas/proposed/provider-udm-get-v0alpha2-result.schema.yaml`, PR #50 | `https://connectionagent.io/proposed/provider-udm-get/v0alpha2/result.schema.yaml` | Proposed Owner schema; PR #50 Draft, no CI check-runs. Not a stable export yet |
| Fabric Agent ingress | `env-fabric/contracts/proposed/createdsession-agent-ingress/v0.1/agent-message.schema.yaml` | `https://service-fabric.io/contracts/createdsession-agent-ingress/v0.1/agent-message.schema.yaml` | Candidate, explicitly not an approved product API. Any reserved-SD wire semantics remain an Owner contract question; Host PR #200 does not change cross-component SD handling |
| Fabric PCF governance | `env-fabric/contracts/proposed/createdsession-pcf-create-governance/v0alpha1/result.schema.yaml` | `https://connectionagent.io/proposed/env-fabric/createdsession-pcf-create-governance/v0alpha1/result.schema.yaml` | Fabric PCF governance Tool contract is merged via PR #81 and its focused validator proves the Tool output schema is identical to this proposed Owner result Schema. The Go runtime still uses the same result contract; the Host normalized Observation projection is a separate merged PR #200 Schema |
| Fabric held-request read | `env-fabric/contracts/proposed/createdsession-held-request-read/v0alpha1/result.schema.yaml` | `https://connectionagent.io/proposed/env-fabric/createdsession-held-request-read/v0alpha1/result.schema.yaml` | Proposed Provider-facing read contract; not the loopback pending/claim API currently consumed by Agent |
| Fabric loopback Hold control | Actual `GET /demo/hold/v1/pending` and `POST /demo/hold/v1/claim` in `env-fabric/internal/inline/sbi/demo_hold_http.go` | No published Schema identity | Missing Owner export. Agent currently parses the wire shape manually. Do not pretend the held-request-read contract covers this API |
| Host normalized `sbi.operation.result` / Tool result | `ca-agent-demo` `CreatedSessionUDMResult.runtime_value()` | Current Host-facing Tool `output.result` and legacy Observation payload | This is the Skill-facing normalized result and requires its own Host-owned Schema. The Provider PR #50 Schema is the separate upstream HTTP result contract validated inside Host. Reuse one Host projection Schema for Tool `outputSchema.result` and the legacy Observation payload; keep the current ObservationSource behavior until the breaking vNext migration is approved |

### 11.1 Complete normalized Observation export identities

The 15 merged normalized Observation Schema identities from PR #200 are:

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

1. Use the runnable `ca-agent-demo` legacy UDM consumer schemas only as behavior/field-shape references. They are not present in authoritative `ca-skills/main` and must not be imported as official Skill contracts or treated as Provider Output Schemas. Do not create a duplicate Skill schema for the Provider result.
2. Keep nested `sbi.operation.result` producer bindings explicit while Provider PR #50 remains unaccepted and the ToolCatalog still exposes broad `result: object`. Once the Provider Schema is accepted, refresh the Host pinned wire snapshot; publish the separate Host `runtime_value()` projection Schema and link ToolCatalog `outputSchema.result` to it. Bind the exact Host Tool output plus same-receipt Evidence.
3. Model the exact stored-result acquisition and its evidence when migrating `createdsession.udm.subscription_usable` to a pure Predicate. Reuse the prior Operation output only if its data and evidence prove the same invocation/transaction identity; do not issue another external UDM Get merely to satisfy the authoring syntax.
4. Keep Capability → Operation → Effect linking as a contract requirement for the new model. Compiler implementation is a later consumer task; this design review does not add or reimplement Compiler behavior.


## 8. vNext acquisition map — implementation authority

The 17 entries in §3 are a legacy Predicate Observation inventory, **not** a target count of callable READ Operations. For vNext they map as follows:

| Legacy source class | Count | New source model |
|---|---:|---|
| Captured ingress projection | 1 | Host Invocation Context `context.ingress`, with Host Evidence attached separately |
| Prior-Operation local projections | 9 | Exact prior Operation output / stored artifact plus Evidence from that same invocation; no duplicate network READ |
| Host journal facts | 2 | Explicit Host READ Operations: lifecycle registration and resource responsibility |
| Independent domain acquisition points | 5 | Provider N4 baseline, Provider post-create N4 resources, Provider RAN setup, Provider N4 forwarding, Fabric PCF governance |

There are four domain READ shapes if the Provider N4 Operation uses a required `phase: PRE_CREATE | POST_CREATE` discriminator and preserves the distinct `baselineRef` / `baselineEvidenceRef` / `currentSessionInstanceRef` lineage. If that contract cannot be made exact, split baseline and post-create into separate Operation IDs.

The initial vNext addition is therefore **six new READ Operations** (one phase-discriminated N4, RAN, forwarding, Fabric governance, Host lifecycle journal, Host responsibility journal), raising the existing 12 Operations to 18. If N4 must be split, the total is 19. The existing bounded `ca.session.evidence.await` remains a Host orchestration Operation; it polls an exact granted READ Operation, returns only a wait summary, and is followed by a separate final READ.

Capability assignment is explicit: the three Provider reads use a new Provider assurance Capability; Fabric governance uses a Fabric-owned Capability unless Fabric confirms it belongs to the existing hold boundary; the two Host journal reads belong to the Host Runtime Capability. The Skill grants these Capability IDs, not Operation IDs.

This vNext map supersedes any earlier wording in this document that treated the Host journal facts as passive Context fields, left their acquisition boundary undecided, or counted only four new Operations. It also supersedes any suggestion that the 17 legacy Observation refs should remain Predicate acquisition declarations.

## 14. Live vNext source-to-Owner audit (2026-11-13)

Audited against migration head 35ed77d4c9393b90608b92476dc78b97a32f8fb4, the current ca-agent-demo/main ToolCatalog and CapabilityContracts, and the open Owner PR heads listed below. This is a contract-link audit, not a Compiler build.

### 14.1 Operation coverage

The conventional 5GC Procedure contains 22 call sites across 18 distinct Operation IDs. The current Agent-demo ToolCatalog exports 12 Operations. Six Procedure Operations are not yet present in that catalog:

| Missing Operation ID | Owner boundary | Required treatment |
|---|---|---|
| ca.session.lifecycle.registration.read | Agent Host | Publish exact READ Tool contract and normalized output Schema |
| ca.session.n4.initial_resources.read | Provider / N4 adapter | Publish exact READ contract with PRE_CREATE / POST_CREATE phase and baseline lineage |
| ca.session.pcf_create_governance.read | env-fabric | Publish exact Fabric-owned governance READ contract and result Schema |
| ca.session.ran_setup.read | Provider / RAN adapter | Publish exact READ contract and normalized result Schema |
| ca.session.n4.forwarding.read | Provider / N4 adapter | Publish exact READ contract and normalized result Schema |
| ca.session.resource_responsibility.read | Agent Host | Publish exact Host journal READ contract and normalized result Schema |

The existing bounded wait, responsibility transfer, and remaining 12 Operations are already represented in the current catalog. Do not create local/shadow Tool definitions in this Skill to fill the six gaps.

### 14.2 Capability coverage

The Skill Contract grants eight Capability IDs. The current deployment CapabilityContracts document defines six. These two grants are not yet backed by a published deployment contract:

- provider-5gc.createdsession.assurance — intended for the three Provider assurance READ Operations above.
- env-fabric.createdsession.governance — intended for the Fabric PCF governance READ.

The two Host READ Operations must be added to the existing Host Runtime Capability membership only after the Host Owner publishes their exact contracts. Do not create another Host Capability or infer membership from an Operation name.

The current 12 ToolCatalog Operations and 12 deployment Operation memberships are internally covered; this does not cover the six new Procedure Operations.

### 14.3 UDM result Schema chain

The UDM sbi.udm.sm_data.get Tool output still declares outputSchema.result: {type: object}. Provider PR #50 proposes the nested Provider response Schema but remains Draft and has no observed CI run. Host PR #200 explicitly defers the distinct Host-normalized runtime_value() projection Schema until the Provider contract is accepted. Therefore the Skill's udmReadResult binding does not yet have a closed authoritative imported Output Schema.

Do not bind the Provider wire Schema directly as the Tool output Schema: Provider HTTP output and Host-normalized Tool output.result are different contracts. Required order: accept and verify Provider Schema; refresh Host's pinned Provider snapshot; publish the Host-normalized result Schema; link the ToolCatalog output to that Host Schema; then statically link the Skill Predicate input.

### 14.4 Host Context and normalized outputs

- Host PR #198 merged the Invocation Context and Predicate Evidence-reference Schemas; focused workflow: 3 passed.
- Host PR #200 merged 15 normalized projection Schemas covering 16 of 17 legacy refs; focused workflow: 7 passed. They are not the final READ Operation contract set.
- Host PR #199 is a code-derived inventory, not an exported contract.
- These PRs must be reviewed and merged by their Owners before the aliases are treated as stable imports.

### 14.5 Acceptance decision

The conventional 5GC source is **partially migrated, not statically linkable and not build-accepted**. Its five Skill Scripts (three Procedure Scripts and two Predicate Scripts) have the required main(input: dict) -> NonEmptyTypedDict shape, and all 16 declared Predicates are present. Those local checks do not compensate for missing imported Operation/Capability/Schema contracts.

The vNext Compiler is also not yet an acceptance gate: the current Compiler implementation targets v0.2 and does not load/link the v1alpha2 CapabilityContracts and Owner export set. Do not run a v0.2 build and label it v1alpha2 acceptance.
### 14.6 Strict Script source-shape audit

All five Script assets referenced by the conventional 5GC Procedure and PredicateSet were fetched from the migration head and checked:

| Script | Entry point | Return contract | Legacy metadata |
|---|---|---|---|
| scripts/select_establishment_configuration.py | main(input: dict) | EstablishmentSelectionOutput (TypedDict) | none found |
| scripts/build_pcf_policy_inputs.py | main(input: dict) | PcfPolicyInputsOutput (TypedDict) | none found |
| scripts/build_n1n2_delivery.py | main(input: dict) | N1N2DeliveryOutput (TypedDict) | none found |
| scripts/evaluate_udm_read.py | main(input: dict) | PredicateEvaluationResult (TypedDict) | none found |
| scripts/evaluate_transfer_start.py | main(input: dict) | PredicateEvaluationResult (TypedDict) | none found |

The return types are non-empty TypedDicts. The nested output fields use the supported Literal / Annotated / list / nested TypedDict / NotRequired forms, including the functional TypedDict form for PCF QoS. No authored Script Input Schema, `# /// connectionagent-tool` metadata, or per-Script execution policy was found. This closes the source-shape audit only; it does not replace Compiler-generated schema validation or the still-blocked vNext static link.
### 14.7 Resource ownership Observation projection omitted the semantic resource reference

The vNext Procedure binds the Predicate input directly to the Mutation Operation output (`with: subscription from nudm-sdm-subscribe.output`, and the equivalent PCF binding). The current Host ToolCatalog output includes the semantic resource ref, but not the three ownership assertions. The legacy Observation projection is a separate path and is not the source bound by these vNext Predicate calls.

- The UDM ToolCatalog Mutation Output already exposes optional top-level `subscriptionRef`.
- The PCF ToolCatalog Mutation Output already exposes optional top-level `policyResultRef`.
- The Host UDM Mutation output already exposes `subscriptionRef`; the PCF Mutation output already exposes `policyResultRef`.
- The Host dispatch backends durably record the exact committed Provider/Fabric operation outcome in the reference journal before returning the output.
- The vNext Predicates require the three ownership assertions (`creationState=CREATED`, `ownership=AGENT`, `managementState=DURABLE`) in addition to the kind-specific reference.

Thus the vNext gap is at the Host's normalized Mutation Operation output contract. The Host—not Provider—must combine the exact Provider/Fabric committed resource evidence with its successful durable journal write before asserting that the resource is created, Agent-owned and durably managed.

**Implemented and merged in Host PR #202:** UDM and PCF dispatch backends add the three ownership fields only after the exact committed operation outcome is durably recorded. The same rule applies after an exact GET reconciliation has itself been durably recorded, because the ToolCatalog reuses the output shape for reconcile results. The ToolCatalog Output Schemas require those fields whenever `subscriptionRef` / `policyResultRef` is present. Focused CI passed **48 tests** at `2582931952d66b7e2a3a20695903b2ce043945e4`. This makes the direct Procedure `with` input shape available from the Host ToolCatalog contract. The change is separate from PR #200, which publishes legacy Observation projections and is not the output source bound by vNext. Final vNext Compiler static-link verification remains pending.

## 15. Conventional 5GC qualification-case first-pass mapping

The current Agent-demo package contains exactly 36 case files. Its own `cases/README.md` explicitly classifies them as semantic qualification obligations, not executable Runtime fixtures; it also says their old PlanningContext / availableResources envelope is not a vNext execution contract and must not be mechanically rewritten into a new Case DSL. The following is a first-pass mapping of their business purposes to the vNext control/ownership boundary, not a claim that the expected terminal/postcondition fields have all been requalified:

| Cases | Preserved business obligation | vNext boundary to review |
|---|---|---|
| 01 | Complete supported profile; RAN, N4 and durable responsibility all proven | Full Procedure + final Contract |
| 02 | Missing/ambiguous ingress cannot start | Host admission before Procedure; no synthetic Skill-side ingress fallback |
| 03–04 | Partial/ambiguous UDM result remains UNKNOWN; target rejection is a definite failure | UDM READ output + `createdsession.udm.subscription_usable` |
| 05 | Missing address/callback or unsafe competing-create state blocks PCF creation | PCF create-input READ, Fabric governance READ, lifecycle precondition |
| 06–07 | UDM subscription / PCF association ownership cannot be inferred from a create response or Location | Additional Owner assurance contract gap in §14.7 |
| 08 | PCF success does not prove initial N4 resources | PRE_CREATE baseline, PCF mutation, bounded wait and POST_CREATE N4 READ |
| 09–10 | Stale instance / missing authorization, or invalid response artifact, blocks delivery | Operation-context READ, delivery-context Predicate, response preparation and local Script |
| 11 | AMF 202 acknowledgement is not the admitted transfer-complete result | `createdsession.amf.transfer_initiated` remains UNKNOWN outside exact accepted response |
| 12–14 | Definite RAN failure, late/ambiguous RAN evidence, or N4 forwarding mismatch must stop | RAN READ, N4 forwarding READ, exact current-session correlation |
| 15 | Core-network completion does not require fabricated UE-internal observation | Final Contract uses the defined core-network facts only |
| 16 | Network success does not erase durable resource responsibility | Responsibility transfer + Host responsibility READ |
| 17–20 | Unknown UDM/PCF/AMF mutation is reconciled exactly once; denied preparation or UDM read causes no later mutation | Native reconcile nodes; preparation and admission fail-closed paths |
| 21–28 | Handoff/finalization uncertainty or NOT_COMMITTED must not become success or trigger blind retry | Responsibility transfer outcomes, original-operation reconciliation, SAFE_STOPPED |
| 29–30 | Known unready lifecycle or unavailable lifecycle proof blocks first NF resource create | Host lifecycle registration READ before UDM Subscribe and PCF Create |
| 31 | UNKNOWN read-only fact stops before mutation | READ preconditions and tri-state Predicate routing |
| 32 | Action budget exhaustion after UDM Subscribe prevents PCF Create while preserving responsibility | Runtime action budget; resource-responsibility transfer's separately authorized budget treatment |
| 33–34 | Missing required subscription fields fail local selection; producer/evidence mismatch remains UNKNOWN | Selection Script's derived output Schema; UDM Predicate evidence correlation |
| 35–36 | Even reconciled COMMITTED / NOT_COMMITTED outcomes conservatively stop this invocation; no retry | Reconcile nodes terminate at SAFE_STOPPED |

### 15.1 First-pass observations

- The current Procedure has corresponding control-flow boundaries for the majority of these obligations; cases 06–07 expose the concrete ownership assurance mismatch in §14.7 rather than a reason to restore old Observation acquisition.
- Case 02 is an ingress-admission test, not a Procedure input validation test. The vNext invocation Context is materialized only after Host admission.
- Case 15 is an explicit negative requirement: do not add a UE-internal observation merely to make the success graph look more complete.
- Cases 32, 35 and 36 are Runtime/reconciliation semantics and must remain obligations even though they are not new Procedure business steps.
- Before declaring case review complete, compare each case's expected planning status, terminal and Contract postconditions against the actual vNext source. Do not copy the old synthetic PlanningContext or `availableResources` declarations into a vNext Case file.

## 16. Reference review

The three existing business References were read in the current Agent-demo source:

- `3gpp-procedure.md`: actor responsibilities and causal boundaries; explicitly distinguishes AMF transfer acknowledgement, RAN acceptance, initial N4 resources, forwarding and UE acceptance.
- `failure-handling.md`: preserves PASS/FAIL/UNKNOWN, exact-operation reconciliation, no blind retry, and durable responsibility after resource creation.
- `session-selection.md`: separates exact UE request, subscription-constrained selection and effective policy/allocation state; disallows silent substitution.

Their content remains useful as model-facing business guidance and is not an alternate executable Procedure or Evidence source. No new Case DSL or Reference copy was added to the official Skill package in this pass.
### 15.2 Case 32 has an unresolved expected-outcome conflict

Case 32 currently expects `FAILED / ACTION_BUDGET_EXHAUSTED` with `createdsession.resources.managed = NOT_EVALUATED`, and its purpose text explicitly says durable-responsibility qualification still needs implementation. However, the current deployment CapabilityContracts document declares `ca.session.resource_responsibility.transfer` as the one budget-exempt finalization Operation, and the vNext Procedure routes a failed PCF Create caused by exhausted action budget through `finalize-resource-responsibility` (transfer, then Host responsibility READ).

These two statements cannot both be the final acceptance expectation. If the budget exemption is retained, the correct business obligation after the UDM subscription has been created is to retain/transfer durable resource responsibility despite the exhausted normal action budget; Case 32 should then expect the final responsibility predicate to be evaluated and pass, while the overall invocation remains FAILED. If the Case's NOT_EVALUATED expectation is intentional, the deployment budget exemption and the vNext finalizer behavior must instead be explicitly revised, with an accepted explanation for how the already-created UDM resource remains owned. Do not silently pick one interpretation. This decision is now an explicit blocker for the final Case 32 review.
### 15.3 Exact legacy Case expectation inventory

All 36 `expect` blocks were also read. Every case currently declares `planningStatus: READY`; the expected terminal distribution is:

| Expected terminal | Cases |
|---|---|
| SUCCEEDED | 01, 15 |
| FAILED | 04, 10, 12, 19, 23, 29, 32, 33 |
| UNRESOLVED | 02, 03, 05–09, 11, 13, 16, 24, 30, 31, 34 |
| SAFE_STOPPED | 17, 18, 20–22, 25–28, 35, 36 |

The expected Contract postconditions intentionally distinguish `PASS`, `FAIL`, `UNKNOWN`, and `NOT_EVALUATED`; notably, a stopped or failed invocation may still require `createdsession.resources.managed = PASS` if a resource was already created and the responsibility handoff completed. Case 16 specifically expects the responsibility predicate to remain UNKNOWN when the manager receipt is missing. These values must not be normalized into one generic failure result.

The complete expected postcondition inventory remains in the original case files in ca-agent-demo; the official vNext Skill does not duplicate those legacy YAML envelopes. Case 32 remains the one identified unresolved expected-outcome conflict (§15.2).
### 14.8 Host-owned READ Operation contracts: exact source and migration boundary

The two missing Host READ Operations already have a concrete source of truth in the Demo Host: `CreatedSessionReferenceJournal.lifecycle(lifecycleRef)`. The current legacy adapter `CreatedSessionReferenceObservationSource` projects the same journal state into Observation values, but vNext must expose it through the Owner's READ Operation output because the Procedure binds the Operation output directly.

| Operation | Input | Output (normalized Host value) | Effect |
|---|---|---|---|
| `ca.session.lifecycle.registration.read` | `ueRef`, `lifecycleRef` | `lifecycleRef`, `registrationState`, `receiverState`, `lateResultResponsibility` | READ |
| `ca.session.resource_responsibility.read` | `ueRef`, `lifecycleRef` | `lifecycleRef`, `managementState`, `allResourcesCovered`, `pendingResponsibilitiesRetained`, optional `transferRef` | READ |

Owner-side rules:

- Both supplied identifiers must exactly match the frozen invocation context (`subject.ueRef` and `facts.createdsession_lifecycle`); they are selectors, not caller assertions.
- The source is the durable Host reference journal. No Provider/Fabric request is made, no resource mutation occurs, and no old Observation registry is consulted.
- Lifecycle output reports the journal's durable registration and receiver readiness. A missing record or missing freshness metadata returns unresolved, never a fabricated READY value.
- Responsibility output maps journal state to `ACCEPTED` only for the exact recorded transfer; otherwise it reports `RETAINED`. `allResourcesCovered` is true only after that transfer. Pending late-result responsibility remains independently represented.
- The output Schemas are Host-owned normalized values, not copies of the SQLite row or the full journal/evidence envelope.

**Why these Operations are not added to the current legacy ToolCatalog in isolation:** the current Demo registration test intentionally requires exact equality between the legacy Skill's allowed Operation set, the ToolCatalog Operation set and the frozen registration map. Adding vNext-only Operations to that catalog would either expand the legacy Skill's grant surface or break its exact registration invariant. Publish these READ exports together with the vNext deployment ToolCatalog/CapabilityContracts snapshot and its registration transition; do not silently widen the legacy Skill's authority merely to make the new source link.


The two Host journal READs are grouped under the separate Capability
`ca-agent-host.createdsession.reference`, granted explicitly by the vNext
Skill contract. They are not appended to the legacy
`ca-agent-host.createdsession.runtime` Capability or its legacy registration.
This keeps the READ authority independently reviewable and avoids widening the
legacy Skill's granted Operation set. Host PR #203 is merged. It publishes this Capability and its two Operation
contracts as a separate vNext dependency snapshot; the deployment later
composes that snapshot with Provider/Fabric snapshots and one complete
deployment Registration.


### 14.9 Fabric PCF governance READ owner export

Fabric already implements a read-only governance projection for one exact held
PCF create. The HTTP route is POST-based for its JSON request body, but it does
not claim, forward, deliver or mutate the hold; its Tool Effect is READ. The
vNext Procedure now binds the exact `holdRef` from the preceding
`ca.session.pcf_hold.bind` output rather than asking Fabric to rediscover the
hold from a broader UE/session selector.

Fabric PR #81 is merged to env-fabric/main (`a8d3f621`). It publishes the exact
`holdRef` request Schema and the `ca.session.pcf_create_governance.read` Tool
contract. Its output Schema is kept identical to the existing Fabric-owned
`createdsession-pcf-create-governance/v0alpha1/result.schema.yaml`; focused CI
passed. This closes the contract declaration gap only; the full deployment
CapabilityContracts and Tool Registration still need to bind the Fabric
operation to its HTTP implementation.

### 14.10 Runtime Operation Evidence seam is not implemented by the current Host

A final source audit found a distinct Runtime blocker that must not be confused
with Tool Output Schema publication:

- The current Host `CallExecution` contains `outcome`, `output`,
  `provenance`, `effect_kind` and uncertainty metadata. It has no structured
  Operation Evidence field.
- The current Runtime engine copies `CallExecution.provenance` into trace
  material as `owner_result`. That is diagnostic trace material, not the
  Predicate Evidence channel.
- Operation output values are made available to later Procedure bindings, but
  the current Predicate evaluation path does not attach same-invocation Owner
  Evidence refs to those values.
- The vNext Language Spec requires a READ Operation to return one normalized
  value and Evidence from the same invocation, and requires the Host to attach
  Evidence separately from business values before a Predicate may return a
  definite verdict.

Therefore PR #202 and PR #203 close important Owner output / READ contracts,
but they do **not** complete the vNext Evidence path. Do not smuggle Evidence
into business output fields, Script globals or trace payloads. The Runtime needs
a generic typed Operation Evidence result seam, exact producer-to-Predicate
attachment, and validation that the Evidence belongs to the same operation
invocation and normalized output. Predicate Scripts may receive only the
attached Evidence refs, never the full Evidence envelope. This is a required
Runtime/Compiler integration gate before static-link or live acceptance can be
claimed.

### 14.11 Provider assurance READs: exact phase and instance binding

The existing Demo sources provide enough concrete implementation material to
specify the three Provider-backed READ Operation shapes, but they are still
ObservationSource adapters, not callable vNext Tool Operations. The vNext
Tool wrapper must reuse their exact baseline/resource joins and must not
weaken them.

| Operation | Required additional binding | Normalized output | Existing source |
|---|---|---|---|
| `ca.session.n4.initial_resources.read` | `phase=PRE_CREATE`: `pcfPolicyAssociationRef` + `fabricHoldRef`; `phase=POST_CREATE`: `pcfPolicyAssociationRef` + exact `baselineRef` | PRE_CREATE baseline value; POST_CREATE oneOf `NO_N4_PAIR` / `NEW_PAIR` value | `CreatedSessionN4BaselineObservationSource` and `CreatedSessionN4ObservationSource` |
| `ca.session.ran_setup.read` | exact `currentSessionInstanceRef` from POST_CREATE N4 output | Provider RAN fields plus `currentInstanceBound`, `baselineRanEndpointPresent`, `lifecycleRef` | `CreatedSessionRANSetupObservationSource` |
| `ca.session.n4.forwarding.read` | exact `currentSessionInstanceRef` from POST_CREATE N4 output | Provider forwarding fields plus `lifecycleRef` | `CreatedSessionN4ForwardingObservationSource` |

All three share the exact attempt selector:
`ueRef`, `pduSessionId`, `pti`, `requestType`, `ingressRef`,
`lifecycleRef`. The operation wrapper must validate each selector field
against the frozen invocation context; it must not accept a caller-selected
UE/session or lifecycle.

Two important checks are not currently performed by the legacy source when
extra keys are present in the Observation scope (the source's `_scope`
helper selects required keys and ignores extras):

1. POST_CREATE must compare the supplied `baselineRef` to the exact
   `baselineEvidenceRef` returned by the baseline store/source. A different
   baseline is UNRESOLVED.
2. RAN setup and N4 forwarding must compare the supplied
   `currentSessionInstanceRef` to the exact instance confirmed by the shared
   N4 baseline store and to the instance in the Provider response. A mismatch
   is UNRESOLVED.

The output schemas are already drafted in Host PR #200 for the legacy
normalized values. They can be reused as the starting normalized Output
Schemas for these READ Operations, but their contract IDs and same-invocation
Evidence behavior must be explicitly exported for vNext. The Provider wire
Schemas remain separate from these Host-normalized outputs.

Do not implement these as a second independent read path that bypasses the
existing Pre-N4 baseline, PCF commit time ordering, new-instance confirmation,
SMF/UPF pair exactness, or RAN/N4 same-instance correlation. The phase router
and the two caller-handle comparisons are mandatory parts of the vNext
Operation implementation.

### 14.12 Host-normalized UDM READ result export

Host PR #205 is merged to `ca-agent-demo/main` at
`fdd9c7dffbef6ffbeaa2797b363632a0b20ed1a5`. It publishes the exact
Host-owned Schema for `CreatedSessionUDMResult.runtime_value()` at:

`https://connectionagent.io/ca-agent-host/createdsession/udm-runtime-value/v1alpha1/schema.yaml`

The export is intentionally distinct from Provider PR #50's upstream wire
Schema. It contains the Skill-facing business value only:
`operationId`, transaction/request/Fabric record handles, record digest,
event time, network outcome, selection, HTTP metadata and selected
subscription. Provider deployment-binding identity, responder identity,
response-body digest and NF instance identity remain outside that projection.

The vNext Skill dependency snapshot imports the exact Host Schema under
`lib/schemas/ca/createdsession-udm-runtime-value-v1alpha1.schema.yaml` and
embeds that exact document at
`lib/tools/createdsession.tool.yaml` →
`sbi.udm.sm_data.get.outputSchema.properties.result`. The repository source
hygiene validator enforces byte-for-byte identity between the imported Owner
Schema and the ToolCatalog result projection. This static link is complete in
the Skill dependency snapshot; the legacy Host ToolCatalog on
`ca-agent-demo/main` remains deliberately unchanged because its stand-in
registration tests still require the existing open result object.
