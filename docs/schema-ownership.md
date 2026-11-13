# Skill Schema Ownership vNext

**Status:** Normative vNext ownership contract. Physical `lib/**` references and Predicate Observation schemas are not part of this version.

A Skill source file may reference a contract by dependency alias and exact exported ID. It must not encode where the caller stores or acquired the dependency bytes.

| Contract | Owner | vNext source / treatment |
|---|---|---|
| Public Skill Request | Skill | `spec.inputs.requestSchema` points to a Skill-owned file under `schemas/**` |
| Invocation Subject / Facts / Ingress | Host or integration Owner | `spec.context.projections.*` references exact exported Owner Schema IDs |
| Predicate Evidence refs | Host / Runtime | `spec.context.evidenceSchema` references the bounded Host Evidence projection |
| Tool Operation Input / Output / Reconcile | Tool Owner | Imported ToolCatalog contract; Procedure calls one exact Operation ID |
| Capability-to-Operation mapping | Deployment composition owner | One CapabilityContracts input supplied separately to BuildRequest |
| Operation Input / Output | Tool Owner | ToolCatalog Input/Output Schemas are authoritative for every callable Operation |
| Observation query Input / Output | Observation Tool Owner | Same ToolCatalog/Owner Schema contract as other Tools; READ-only QueryContext and normalized result |
| Observation authority / freshness / scope | Observation Tool Owner, validated by Host/Runtime | Declared as Tool contract guarantees; no parallel ObservationSource registry |
| Procedure Script input | No separate file owner | Derived per invocation from that Script call site's explicit `with/from` bindings |
| Predicate parameter signature | Skill Predicate | Ordered typed `parameters` declare names and expected types; structured parameters reference authoritative Schemas |
| Predicate Script input | No separate file owner | Derived from the owning Predicate parameter signature; no Script-authored or separate Predicate Input Schema |
| Predicate Evidence | Host / Runtime | Attached separately from business values; Script may cite only the attached refs |
| Script output | Skill Script | Generated from the strict return `TypedDict`; read-only BuildResult output |

## 1. Dependency references

Studio/caller supplies dependency snapshots in BuildRequest. Skill source uses:

- `<alias>::<operation-id>` for a callable Operation;
- `<alias>::<schema-$id>` for an imported Owner Schema.

The alias is a snapshot selector, not a path, package manager, Git locator or schema owner. The exported ID after `::` remains owned by its producer.

There is no physical `lib/` directory requirement, `lib/...` source reference, manifest, lockfile or digest protocol in Compiler.

## 2. Context and Predicate ownership

- The Skill owns the public Request Schema.
- Host/integration owners publish exact schemas for trusted invocation projections such as subject, facts and ingress.
- Host publishes the bounded Evidence-reference projection; full provenance records remain internal to Runtime.
- Predicate definitions declare an ordered, typed `parameters` signature. They do not declare Observations, scopes, freshness or hidden globals.
- Procedure supplies positional `verify.arguments`. Compiler validates exact arity/order, source path, producer availability and assignability to the Predicate's declared parameter type at every call site.
- The Predicate signature is complete at authoring time and is independently usable for CEL validation and editor tooling; it is not inferred from Procedure call sites.
- Runtime validates Evidence for the same producer invocation before a definite Predicate result is accepted.

No schema is copied into the Skill merely to make a missing Owner dependency compile.

## 3. Fact, Observation and acquisition

A Fact is the domain/environment/execution statement. An Observation is an independently addressable read-only query capability over an Owner's fact/state, exposed as a specialized Tool contract. Its query result is a captured, scoped representation with source and temporal context. Evidence is the separately validated support for that result. These concepts and payloads remain distinct.

Observation Tools use the same ToolCatalog, dependency alias/snapshot, Owner Schema, CapabilityContracts and Runtime admission model as other Tools. Their Effect is READ; their contract declares QueryContext/Input Schema, normalized Output Schema, authority, provenance, scope, correlation, temporal/freshness semantics and Evidence guarantees. The legacy Observation Ref → ObservationSource implementation registry is retired; it is not replaced by a second public registry or Schema system. Existing adapters may remain internal implementations of the published Observation Tool contract during migration.

## 4. READ Operations and prior results

An independently queried fact uses an explicit Observation Tool query. Its Owner publishes the typed QueryContext/Input and normalized Output Schemas through the same ToolCatalog contract and declares the READ Effect and Evidence guarantees. This does not imply that every Operation or Predicate needs an Observation query: a prior Operation output or trusted Context projection may already provide the exact value and adequate correlated Evidence.

If a later Predicate needs a prior Operation result, pass that exact result through its positional `verify.arguments`. Do not reacquire the same resource from a parallel legacy Observation Source and do not infer a value from a local handle alone.

Host journal-backed facts, when independently queried, are exposed through Host-owned Observation Tool contracts. The Skill does not declare Host-internal journal dataclasses.

## 5. Script ownership

Procedure Script input is a per-call-site projection from explicit `with` bindings. Predicate Script input is derived from the owning Predicate's typed `parameters` signature plus Host-attached Evidence refs. Neither kind of Script authors a separate Input Schema. A Script declares only its strict output `TypedDict`; Compiler generates the output Schema.

For Predicate Script, the Predicate is the sole authority for business-input names and types. Compiler may generate a read-only Python type environment/stub for LSP and static analysis, but this is derived tooling output, not another schema source.

## 6. 5GC Owner contract requirements

The 5GC migration uses these exact contract categories:

- Host invocation projections: `subject`, `facts`, `ingress`;
- Host Evidence refs;
- Provider/Fabric/Host ToolCatalogs for the exact READ and MUTATION Operations;
- one deployment CapabilityContracts document mapping each Operation to one Capability and Effect;
- Skill-owned public establishment Request Schema;
- Skill Script output schemas generated by Compiler.

The 36 Cases and three References remain business-semantic source material. They do not define Owner Schemas and are not substitutes for READ outputs or Evidence.
