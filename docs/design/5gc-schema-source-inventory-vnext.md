# 5GC Executable Schema & Observation Source Inventory

Status: **SOURCE AUDIT / 5GC ONLY**  
Reference implementation: `odango-chan/ca-agent-demo` `main` at `38012852827437185c6343c2b544acad401084e1` (2026-11-12; `fix(live): converge Generic Agent Host 5GC E2E and user plane evidence`). This is the audited source snapshot for this inventory.

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

`src/ca_agent_host/agent/context/base.py` defines the generic planning model (`BaseContext`, `PlanningContext`, `ContextFact`, `ContextRequirement`, visibility, grounded subject, authority/source/freshness and resolver lineage). It is not the same object as the 5GC Skill invocation context materialized by `FabricResidentSource._materialize()`. The latter's exact Subject/Facts schemas are proposed in ca-agent-demo Draft PR #198.

`src/ca_agent_host/runtime/observation/model.py` defines the full internal acquired Observation/evidence envelope, correlation refs, source fact evidence, and evidence capability. Predicate Scripts do not receive this full dataclass; `PredicateEngine.evaluate()` projects only `{refs: source_fact_ids}` per observation name. The proposed Host schema for that narrow projection is in ca-agent-demo Draft PR #198. Domain-specific normalized Observation values still require per-owner schemas.

## 7. What this means for Semantic Field Identity / Binding Resolver

- First executable acceptance target must be the real 5GC `establish-pdu-session` Skill and its **actual owner-backed schemas**.
- MAS's 11-field / 16-call / 176-mapping example remains an exploratory shape exercise only. Its ToolCatalog is not-ready and MAS is not end-to-end runnable; those counts are not a compiler acceptance baseline and must not be described as safely removable mappings.
- Do not annotate the 5GC Operation inputs with identities merely because the Procedure has similar-looking fields. Semantic IDs must be assigned by the actual field owners after the exact producer/consumer semantics and schema are verified.
- Keep exact handle lineage (`ingressRef`, `lifecycleRef`, hold refs, operation-context refs, N4 instance refs, evidence refs) explicit unless the owner contract proves a unique producer instance and the existing Compiler proves source availability and Schema compatibility.
- A 5GC compiler migration must compile the complete real admitted closure, use the existing `checkBindings` validation, and compare candidate bindings against the authored Procedure. No source `with` removal until exact equivalence is demonstrated.

## 8. Explicit non-goals

This inventory does not create new Host or Observation schemas, does not promote MAS to executable, does not make all Observation refs Fabric-backed, and does not authorize copying owner schemas into `ca-skills` without owner provenance. It is a map of the current 5GC implementation and its contract authorities.

## 9. Audit pin

This inventory was derived from `ca-agent-demo` commit `38012852827437185c6343c2b544acad401084e1`. Any schema refresh must compare the target owner schema and implementation against this exact pin (or a newer explicitly reviewed commit), then record the new commit and schema digests. Do not treat the moving `main` name alone as reproducible provenance.


## 10. Host context export update (2026-11-12)

ca-agent-demo Draft PR [#198](https://github.com/odango-chan/ca-agent-demo/pull/198) now publishes three source-backed schemas: 5GC invocation Subject, 5GC invocation Facts, and the Host Predicate Evidence reference projection. Its focused schema workflow currently passes **3 tests** on head `4088e4b4c4350fa9dfe7c194b59ae8f3a467e244`. The PR is still Draft / unmerged, so these schemas are proposed owner exports and must not yet be treated as present in the official `ca-agent-demo/main` dependency snapshot. The full Runtime `ObservationEvidence` model remains internal and is not the Skill's Script-facing Evidence schema.


## 11. Observation output Schema publication update (2026-11-12)

ca-agent-demo Draft PR [#200](https://github.com/odango-chan/ca-agent-demo/pull/200) proposes normalized output Schemas for 16/17 Observation refs. The remaining `sbi.operation.result` requires the Provider Owner to complete the nested UDM subscription result Schema before a strict Skill-facing output Schema can be published. PR #200's focused Schema/fixture workflow currently passes **5 tests**; it remains unmerged, so these are proposed exports only.


## 10. Detailed Owner Schema gap register

The follow-up code-derived audit is maintained in [5GC Owner Schema Gap Register — vNext](5gc-owner-schema-gap-register-vnext.md). It enumerates the exact 17 Predicate Observation refs, separates generic Host Evidence Envelope from owner READ Output Schemas and Skill Predicate consumption, and records the Capability → Operation → Effect linking requirements. Use it as the WP2 checklist before attempting a no-lib Compiler build.


## 12. Owner-export implementation status (2026-11-12)

The code-derived source inventory remains pinned to `ca-agent-demo/main@38012852827437185c6343c2b544acad401084e1`; proposed exports below are separate candidate branches and are not yet part of the official main snapshots.

- Host Context / Script Evidence refs: ca-agent-demo Draft PR #198; three Owner schemas; focused CI **3 passed**.
- Normalized Observation outputs: ca-agent-demo Draft PR #200; 15 Schema identities cover 16/17 refs; focused CI **5 passed**. This is a focused Schema/fixture check only; it does not re-run the live 5GC flow or validate every ObservationSource output.
- Provider GetSmData nested subscription result: ca-provider-5gc Draft PR #50; exact schema and validation script proposed, but no GitHub check-runs observed. The Host-normalized `sbi.operation.result` projection remains a separate missing Schema.
- Fabric ingress, PCF governance and held-request-read contracts remain proposed/candidate sources. The loopback `GET /demo/hold/v1/pending` and `POST /demo/hold/v1/claim` endpoints consumed by Agent still lack a distinct Owner-published wire Schema; the Provider-facing held-request-read contract is not interchangeable with them.

### 12.1 UDM result deferral

The current 5GC Skill already has Skill-owned consumer schemas for the UDM selection Script and UDM Predicate evaluator, plus the shared Predicate evaluation result schema. Those contracts validate what the existing business logic consumes. The Provider's full nested GetSmData Output Schema and the Host-normalized `sbi.operation.result` projection remain separate owner contracts and are deferred from the first vNext feasibility slice. Keep nested producer bindings explicit; do not infer fields from the consumer Schema or block the current Skill review on Provider PR #50.

### 12.2 Compiler consumption status

The current Compiler PR #5 implementation imports only `lib/tools/*.yaml`, resolves project-local references from files supplied in memory, and does not load Host, Observation or CapabilityContracts exports. The CapabilityContracts schema is defined in Compiler PR #4, but the v0.1 Compiler has no CapabilityContracts linker; Runtime Host performs the current 6-Capability / 12-Operation / Effect consistency check. Compile-time Capability → Operation → Effect proof remains an explicit vNext implementation gate, not an existing Compiler feature.

See [5GC Owner Schema Gap Register — vNext](5gc-owner-schema-gap-register-vnext.md) for the consolidated Owner Export Map, exact contract identities and remaining dependency order.
