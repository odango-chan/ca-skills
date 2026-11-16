# Schema Ownership — Companion Notes

**Status:** Non-normative Schema ownership companion to the [current CA-SL v1alpha4 specification](skill-language-spec.v1alpha4.zh-CN.md). Historical examples in this note have no authority to override its exact Schema/Evidence/Owner rules; existing unported 5GC source files remain legacy.

The comprehensive specification is the sole normative source for Schema ownership, identity, Evidence, Observation and argument binding. If this note conflicts with the specification, the specification takes precedence.

## Ownership summary

- Skill owns its public Request Schema and genuinely Skill-owned data. The Request Schema lives under `schemas/**` and is referenced by `assurance/contract.yaml`.
- Tool Owner owns Operation Input / Output / Reconcile Schemas.
- Observation Owner publishes Query Input and normalized Output Schemas through ToolCatalog.
- Host owns the Skill-visible Subject Context Schema and the Evidence-reference projection. `contract.yaml` references only the exact subject projection in `contextSchema` (for the current 5GC profile, the admitted 3GPP `supi` only). Host-private ingress, invocation, UE/PSI instance, lifecycle and correlation metadata is a separate execution-context contract; it is not exposed to the Skill and is not an authored Operation/Observation argument. The Host has proposed the private adapter payload Schema `urn:connectionagent:ca:host:tool-execution-context:v1alpha1`; it is an internal Host contract, not a Skill dependency or `contextSchema`.
- Contract declares a direct alias-to-Package-ID map in `dependencies` and requested grants in `capabilities`. Dependency identity is not a version lock or download instruction; a Grant is not a dependency.
- Operation / Observation arguments are named mappings checked against Owner Schemas.
- Procedure Script arguments are named mappings that define the exact local input projection; strict return TypedDict generates the output Schema.
- Predicate arguments are ordered positional values checked against Predicate.parameters.
- Predicate Script inputs derive from the Predicate signature plus Host-attached Evidence refs; its strict return TypedDict generates PredicateEvaluationResult.
- Consumers must not copy external Owner Schemas into the Skill package.
- Schema is the JSON Schema data model; YAML and JSON are serialization formats. Source Skill-owned Schemas remain YAML-authoritative. Generated artifact serialization is a separate Compiler Artifact Contract decision.

## Dependency and snapshot boundary

Skill Studio lets the author select public dependencies and Capability Grants from the available catalogs. It writes stable dependency identities and requested grants to Contract, and resolves exact immutable dependency snapshots for the current project / BuildRequest.

Compiler verifies the existing snapshot digest and compares the Contract Package ID with the trusted caller binding for that alias and digest. It validates Owner and exact export identities before linking. The caller establishes provenance; Compiler consumes supplied bytes and metadata. Preserve immutable revision markers in Owner Schema IDs.

The trusted deployment CapabilityContracts is supplied separately from ordinary DependencySnapshot inputs. It defines exact callable membership and Effect; imported ToolCatalog bytes provide the corresponding callable schemas. Compiler validates that every external callable is covered by exactly one granted Capability and matches the trusted Effect.


## 5GC context and Observation boundary

For the current 5GC profile:

- The Host Subject Context exports the 3GPP `supi` copied from the admitted CreateSMContext request; no Host-generated UE reference is defined. The Skill's Request Schema separately carries business parameters such as `pduSessionId`.
- Host-owned `ingressRef`, `lifecycleRef`, invocation identity, cancellation and journal state are injected through a private Host-to-Tool dispatch context. They must not appear in `contextSchema`, Predicate inputs or Skill-authored callable arguments.
- The Host Subject Context Package ID is reserved as `urn:connectionagent:ca:host-context`; it is not yet published or trusted. The Owner must publish the exact subject Schema snapshot and trusted Package ID/Owner/digest binding before a Skill can link it. The Host-owned HostBusinessCorrelation Schema contains only `ingressRef` and `lifecycleRef`. The Host supplies the stable Runtime Execute `requestId`; ca-runtime owns its `(host, requestId)` RequestStore, fingerprint, deduplication and replay authority. Runtime generates `runId`, `invocationId`, `actionOccurrenceId` / `procedureOccurrenceId` and `dispatchAttemptId`, and resolves `environmentRef`. The proposed RuntimeHost `hostBusinessCorrelation` transport extension is not yet in RuntimeHost.v1; no merged physical Host/Runtime envelope Schema is published.
- The SMF MAS QueryContext SBI v0.10 contract remains owned by the SMF. The separate `ca-5gc-client-tools` package provides the client adapter and typed CA-SL v1alpha4 Observation callables; it must consume the exact SMF Owner wire schema rather than copying or silently redefining it. The reserved client-tools dependency Package ID is `urn:connectionagent:ca:5gc:smf-mas-observations`; it is not yet published.
- Direct Agent Observation scope is limited to SMF-owned MAS projections. AMF/UDM/PCF/UPF/RAN/Fabric context needed by an Operation is acquired inside the responsible Tool/Owner adapter and returned as Operation Result/Evidence.
- The current SMF MAS v0.10 response lacks source `observedAt` / `validUntil` and does not carry Host `lifecycleRef`. Host `queryStartedAt` / `receivedAt` are audit bounds, not source observation time. Exact temporal and lifecycle Scope guarantees are required before a query can be qualified as a v1alpha4 Observation.

The `ca-5gc-client-tools` ToolCatalog is a CA-SL dependency snapshot for linking, not a second Server Tool Catalog; the existing `tool-mcp-gw` catalog and Runtime Resolved CA Toolset remain authoritative. The eight candidate Guarantee IDs and deployment Scope policy names are not published descriptors or grants. See the [SMF MAS Observation Evidence and Scope Profile](https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/5gc-smf-mas-observation-evidence-scope-v1alpha4.md) and [17-ref Legacy Observation Crosswalk](https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/5gc-legacy-observation-crosswalk-v1alpha4.md). See the CA Agent Host [5GC Agent Context and Observation Contracts](https://github.com/odango-chan/ca-agent-demo/blob/docs/5gc-agent-context-boundary-20261116/docs/5gc-agent-context-contracts-v1alpha4.md) for the complete contract boundary and publication gates.
