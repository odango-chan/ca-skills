# 5GC Executable Schema & Observation Source Inventory

Status: **SOURCE AUDIT / 5GC ONLY**  
Reference implementation: `odango-chan/ca-agent-demo` `main` (inspect exact commit before copying any schema).

## 1. Scope decision

`ca-agent-demo` is the executable 5GC reference implementation and the source from which this repository's 5GC contract work must be derived. Its `establish-pdu-session` Skill has a real, previously verified 5GC execution path. The `establish-pdu-session-mas` material is a future design/adapter direction and **does not currently have a runnable end-to-end path**. It must not be used as the baseline for shared schemas, Binding Resolver acceptance, or executable examples.

Keep the following states separate:

| Surface | Status | Use in contract work |
|---|---|---|
| `establish-pdu-session` | Executable 5GC baseline | Normative source evidence, subject to owner boundaries |
| `establish-pdu-session-mas` | Not runnable / not fully owner-backed | Design-only; no production schema inference or PASS claim |
| Generic Host / Runtime models | Implemented shared machinery | Reuse only the generic fields actually represented by code |
| Provider / Fabric / Tool owner contracts | External owner boundaries | Consume exact owner schemas; do not duplicate or redefine them in a Skill |

## 2. Source-of-truth precedence

Use this order when reconstructing a schema:

1. **Owner's versioned wire schema and implementation** (for example Provider request/result schemas plus its validator/normalizer).
2. **`ca-agent-demo` owner adapter implementation and composition** showing which exact Observation ref / Operation is registered to which owner.
3. **Real integration tests and successful execution evidence** proving the implemented projection and correlation behavior.
4. **Admitted 5GC Skill source** (`assurance/contract.yaml`, `procedure.yaml`, `predicates.yaml`, request schema) describing how the Skill consumes those facts.
5. Historical docs, proposed MAS schemas, or synthetic fixtures are explanatory only and cannot override the above.

A field appearing in a Procedure `with` block is a consumer reference, not proof that its producer schema or owner semantics are known.

## 3. Executable 5GC Skill-owned inputs and procedure contract

Primary sources:

- `skills/establish-pdu-session/assurance/contract.yaml`
- `skills/establish-pdu-session/assurance/procedure.yaml`
- `skills/establish-pdu-session/assurance/predicates.yaml`
- `skills/establish-pdu-session/schemas/establishment-request.schema.yaml`
- `skills/establish-pdu-session/scripts/*.py` and their adjacent `*-input.schema.yaml` / output schemas

The current request schema requires `pduSessionId` (1..15), `pti` (1..254), `requestType` (=1), `dnn`, `sNssai`, `servingPlmn`, `requestedPduSessionType` (=IPV4), and `requestedSscMode` (=1). The Procedure explicitly sources its UE reference from `context.subject.ueRef`, request values from `context.request.*`, and ingress/lifecycle refs from `context.facts.*`. These context paths are dependencies on Host/owner material; they are not Skill-owned schema definitions.

## 4. Operation / Capability schemas

The executable 5GC Tool contract authority in `ca-agent-demo` is:

- `tools/contracts/createdsession.tool.yaml` — exact Operation identities, READ/MUTATION effects, and input/output JSON Schemas.
- `tools/contracts/capabilities/createdsession.capabilities.yaml` — deployment Capability → Operation grouping and independent expected-effect cross-check.
- `tools/registrations/default.yaml` — explicit Operation → implementation registration; registration is not the schema/effect authority.

Do not use `skills/establish-pdu-session-mas/design/tool-contract.yaml` as an executable contract. It is explicitly proposed/not-ready.

## 5. Observation is not one transport and not all Fabric

In the 5GC implementation, `ObservationRequest` is a read-only request to the Runtime's exact-ref ObservationSource registry. It carries `observation_ref`, grounded `scope`, and optional `correlation_refs`. `AcquiredObservation` returns `AVAILABLE`, `KNOWN_ABSENT`, or `UNKNOWN`, a normalized value when definite, and evidence. See:

- `src/ca_agent_host/runtime/observation/model.py`
- `src/ca_agent_host/runtime/observation/source.py`
- `src/ca_agent_host/runtime/composite.py` (`CompositeObservationSource` rejects duplicate owners and returns UNKNOWN for an unregistered ref).

Observation refs route to different owners:

| Observation family / refs | Owner / implementation evidence |
|---|---|
| `ue.registration.snapshot`, `smf.pdu_session.context`, `upf.pfcp_session.resources`, `n4.initial_resources.snapshot`, `smf.ran_setup.snapshot`, `n4.forwarding_resources.snapshot` | `ca-provider-5gc` wire contract; consumer schemas in `src/ca_agent_host/integrations/ca_provider_5gc/contracts/provider-observation-read-{request,result}.schema.yaml`; ref allowlist and normalized projection in `integrations/ca_provider_5gc/client.py` and `observation_source.py` |
| `createdsession.procedure_context` | Deployment ingress owner: `integrations/env_fabric/ingress_observation.py` ref constant plus `integrations/fivegc/composition.py` registration of the Fabric resident ingress |
| `createdsession.n4_baseline`, `createdsession.n4_initial_resources` | Open5GS adapter in `tools/adapters/open5gs/n4_evidence.py`, backed by Provider reads and exact instance/baseline stores |
| `createdsession.ran_setup_result`, `createdsession.n4_forwarding_resources` | `tools/adapters/open5gs/core_network_evidence.py`, backed by Provider reads and the confirmed N4 instance |
| `createdsession.pcf_create_governance` | `tools/adapters/open5gs/pcf_governance.py`; composed as a Fabric/hold-governance owner in `integrations/fivegc/provider_resident.py` |
| `createdsession.pcf_hold`, `createdsession.udm_hold`, `createdsession.n1n2_hold` | Open5GS adapter projections in `pcf_hold.py`, `udm_hold.py`, `n1n2_hold.py`; exact hold control is backed by the Fabric hold-control client |
| `createdsession.pcf_create_inputs`, `createdsession.policy_operation_context`, `createdsession.nas_delivery_context` | Provider-backed operation-context / PCF-input owner adapters and per-invocation stores (`pcf_inputs.py`, `context.py`) |
| `createdsession.udm_subscription_resource`, `createdsession.pcf_association_resource`, `createdsession.lifecycle_registration`, `createdsession.resource_responsibility` | Local evidence/reference-journal projections in `resource_evidence.py` and `responsibility.py`; their underlying mutation/receipt provenance remains owner-bound |
| `createdsession.amf_transfer_result` | C-resident AMF transfer evidence source in `tools/adapters/open5gs/n1n2_evidence.py` and `integrations/fivegc/c_resident.py` |

The exact registered owner map is assembled by `integrations/fivegc/provider_resident.py` and `integrations/fivegc/composition.py`; use that composition rather than assuming a prefix such as `createdsession.*` implies Fabric ownership.

## 6. Generic Host Context and Evidence model

`src/ca_agent_host/agent/context/base.py` defines the current Python model: immutable `BaseContext`, `PlanningContext`, `ContextFact`, `ContextRequirement`, visibility, grounded subject, provenance (`authority`, `source_ref`, `freshness`), and resolver lineage. `context/loader.py` accepts only registered read-only resolvers and checks the exact requirement/fact identity. `requirements.py` derives missing exact facts from grounded Predicate atoms.

`src/ca_agent_host/runtime/observation/model.py` defines the acquired Observation/evidence envelope, correlation refs, source fact evidence, and evidence capability. These Python dataclasses are the implemented Host model; do not claim there is already a complete shared JSON Schema for every ContextFact or Observation payload. Domain-specific normalized Observation values are governed by each source owner's schema.

## 7. What this means for Semantic Field Identity / Binding Resolver

- First executable acceptance target must be the real 5GC `establish-pdu-session` Skill and its **actual owner-backed schemas**.
- MAS's 11-field / 16-call / 176-mapping example remains an exploratory shape exercise only. Its ToolCatalog is not-ready and MAS is not end-to-end runnable; those counts are not a compiler acceptance baseline and must not be described as safely removable mappings.
- Do not annotate the 5GC Operation inputs with identities merely because the Procedure has similar-looking fields. Semantic IDs must be assigned by the actual field owners after the exact producer/consumer semantics and schema are verified.
- Keep exact handle lineage (`ingressRef`, `lifecycleRef`, hold refs, operation-context refs, N4 instance refs, evidence refs) explicit unless the owner contract proves a unique producer instance and the existing Compiler proves source availability and Schema compatibility.
- A 5GC compiler migration must compile the complete real admitted closure, use the existing `checkBindings` validation, and compare candidate bindings against the authored Procedure. No source `with` removal until exact equivalence is demonstrated.

## 8. Explicit non-goals

This inventory does not create new Host or Observation schemas, does not promote MAS to executable, does not make all Observation refs Fabric-backed, and does not authorize copying owner schemas into `ca-skills` without owner provenance. It is a map of the current 5GC implementation and its contract authorities.