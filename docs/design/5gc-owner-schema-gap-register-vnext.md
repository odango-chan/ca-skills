# 5GC Owner Schema Gap Register — vNext

Status: **CODE-DERIVED AUDIT / NOT YET OWNER-PUBLISHED EXPORT BUNDLE**
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

## 4. Critical semantic distinction: three schema layers

Do not collapse these into one context-observations.schema.yaml:

1. **Generic Host Observation / Evidence Envelope** — Host-owned: observationRef, status (AVAILABLE / KNOWN_ABSENT / UNKNOWN), normalized value presence rules, provenance, source fact refs, correlation refs, world/snapshot lineage, observed-at/freshness and evidence capability.
2. **Owner READ Operation Output Schema** — owned by the Provider / Fabric / Host / adapter that exposes the read. Declares its exact request scope, normalized output shape, and guarantees. Every Observation read is a READ Operation and belongs to exactly one Capability.
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

1. Every one of the 17 Observation refs is assigned to one actual owner and one READ Operation / Capability (or explicitly marked as an internal observation projection that will be surfaced by a READ Operation).
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
| ca-provider-5gc | `schemas/provider-observation-read-request.schema.yaml`, `schemas/provider-observation-read-result.schema.yaml` | Owner schema present on main | Six raw Provider Observation refs: UE registration, SMF PDU context, UPF PFCP resources, N4 initial resources, SMF RAN setup, N4 forwarding resources |
| ca-provider-5gc | `contracts/proposed/createdsession-operation-context/v0alpha1/{request,result}.schema.yaml` | Proposed | Supports operation-context facts used by PCF/NAS preparation; not a general Host Context schema |
| ca-provider-5gc | `contracts/proposed/createdsession-pcf-create-inputs/v0alpha2/{request,result}.schema.yaml` | Proposed | Exact PCF input-read readiness, held-request lineage, allocated address, field provenance; not PCF create governance or association ownership |
| env-fabric | `contracts/proposed/createdsession-held-request-read/v0alpha1/{request,result}.schema.yaml` | Proposed | Exact held SMF request, hold/lifecycle/current instance, request digest and deadline; does not prove sender authorization, create or delivery |
| env-fabric | `contracts/proposed/createdsession-pcf-create-governance/v0alpha1/result.schema.yaml` | Proposed | Hold state, sender authorization, competing-create state, lifecycle isolation and evidence refs; matches the semantic owner for `createdsession.pcf_create_governance` |
| env-fabric | `contracts/proposed/createdsession-lifecycle-isolation/v0alpha1/evidence.schema.yaml` | Proposed | Operator-owned isolation declaration consumed by Fabric; not an Agent business fact |
| env-fabric | `contracts/proposed/createdsession-amf-n1n2-transfer/v0.1/transfer-result.schema.yaml` | Proposed candidate | Detailed Fabric transfer attempt record; needs an explicit normalized Host Observation projection and lifecycle/correlation mapping |
| ca-agent-demo / Host | `src/ca_agent_host/runtime/observation/model.py`; `agent/context/base.py`, `loader.py`, `projection.py` | Runtime implementation on main | Python value models exist for ObservationEvidence, SourceFactEvidence, ContextFact, BaseContext, PlanningContext, ContextRequirement, ContextOffer and ModelVisibleContext; no complete versioned JSON Schema export bundle |
| ca-agent-demo / Host | `src/ca_agent_host/integrations/env_fabric/contracts/createdsession-pcf-create-governance-result.schema.yaml` and Provider mirrored wire schemas | Host-side integration mirrors/projections | These are Host integration contracts, not replacements for the Fabric/Provider source-of-truth schemas |

### 9.1 Corrections to the initial gap classification

- The six Provider Observation schemas are real owner files in ca-provider-5gc main, not only Host-local mirrors.
- Fabric already has proposed held-request, PCF governance, lifecycle-isolation and AMF transfer schemas. Do not create duplicate schemas in ca-agent-demo.
- Provider already has proposed operation-context and PCF-create-inputs schemas. They cover specific operation outputs, not generic Host Context.
- The remaining major gap is the **Host-owned generic envelope and context export**, plus normalized Host Observation projections for Fabric/Provider/adapter results and a stable release/publication boundary for proposed owner contracts.
- A proposed schema is not automatically a stable exported contract. Compiler should only link a schema included in the selected dependency snapshot with explicit owner identity/version and a supported contract status.

