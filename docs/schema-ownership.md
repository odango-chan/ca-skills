# Schema Ownership — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The comprehensive specification is the sole normative source for Schema ownership, identity, Evidence, Observation and argument binding. If this note conflicts with the specification, the specification takes precedence.

## Ownership summary

- Skill owns its public Request Schema and genuinely Skill-owned data. The Request Schema lives under `schemas/**` and is referenced by `assurance/contract.yaml`.
- Tool Owner owns Operation Input / Output / Reconcile Schemas.
- Observation Owner publishes Query Input and normalized Output Schemas through ToolCatalog.
- Host / Context Owner owns Subject, Facts, Ingress and Evidence-reference projections.
- Contract.requiredFacts lists trusted Host facts available at Admission (not observations acquired inside Procedure). Every Procedure SourcePath using a Host Subject/Facts/Ingress projection must find a Contract.context.schemas declaration and a matching exact Owner Schema through a declared DependencySnapshot. Unused declarations warn; missing/mismatch fails closed.
- Contract declares stable public dependency identities and Capability Grants separately. Dependency identity is not a version lock or download instruction; a Grant is not a dependency.
- Operation / Observation arguments are named mappings checked against Owner Schemas.
- Procedure Script arguments are named mappings that define the exact local input projection; strict return TypedDict generates the output Schema.
- Predicate arguments are ordered positional values checked against Predicate.parameters.
- Predicate Script inputs derive from the Predicate signature plus Host-attached Evidence refs; its strict return TypedDict generates PredicateEvaluationResult.
- Consumers must not copy external Owner Schemas into the Skill package.
- Schema is the JSON Schema data model; YAML and JSON are serialization formats. Source Skill-owned Schemas remain YAML-authoritative. Generated artifact serialization is a separate Compiler Artifact Contract decision.

## Dependency and snapshot boundary

Skill Studio lets the author select public dependencies and Capability Grants from the available catalogs. It writes stable dependency identities and requested grants to Contract, and resolves exact immutable dependency snapshots for the current project / BuildRequest.

Compiler receives each snapshot as `{alias,id,files}` and validates its publisher-provided `dependency.yaml` identity Manifest against the Contract Alias/ID mapping, then checks Owner and exact export identities. It does not fetch, update, lock, cache or version dependencies. Snapshot authenticity remains the responsibility of the trusted caller; Compiler validates internal consistency. The exact selected snapshot revision belongs to Studio project/build configuration, not the Skill's public Contract. If an Owner Schema ID itself contains an immutable revision marker, preserve it exactly.

The trusted deployment CapabilityContracts is supplied separately from ordinary DependencySnapshot inputs. It defines exact callable membership and Effect; imported ToolCatalog bytes provide the corresponding callable schemas. Compiler validates that every external callable is covered by exactly one granted Capability and matches the trusted Effect.
