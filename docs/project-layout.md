# Skill Package Layout and Source Ownership

This document defines the Skill source package, not a workspace or package-manager layout. Studio owns its Explorer and project configuration. Compiler consumes a virtual file set and does not require a physical project lib/ or output/ directory.

## Canonical vNext Skill source

~~~text
skills/<skill-name>/
├── SKILL.md
├── assurance/
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case-name>/
│       └── case.yaml
├── references/       # optional model knowledge
├── schemas/          # Skill-owned schemas only
└── scripts/          # Skill-owned deterministic Python
~~~

There is no separately authored assurance/contract.yaml in vNext. procedure.yaml is the single Skill execution source: it declares goal, requestSchema, Capability grants and the Procedure graph. Skill identity is derived from the Package root. Compiler derives language/API version, kind, metadata and any normalized SkillContract projection.

The currently runnable v0.2 Skills may still contain assurance/contract.yaml. They remain unchanged until a separately reviewed vNext migration; the new layout is not a claim that those packages have already migrated.

## Schema and Script ownership

- schemas/ contains only interfaces owned by the Skill, such as its public Request Schema.
- Do not copy imported Tool / Host / Observation Schemas into an individual Skill package.
- Do not author Procedure Script Input Schemas. The call-site arguments mapping and source contracts derive the effective input projection.
- Do not author Script Output Schemas. Strict return TypedDict declarations generate read-only JSON Schema in BuildResult.
- Predicate Script inputs derive from Predicate.parameters plus all call-site positional bindings.
- Generated output is not written back into the Skill source tree.

## Imported external contracts

Compiler accepts imported contracts as exact immutable DependencySnapshot inputs. A logical lib/** namespace may be used by the BuildRequest to organize imported files, but it is not a physical folder authors must maintain in the Skill Package.

- Imported ToolCatalog contracts define exact Operation and Observation callable identities.
- Host dependencies define Subject / Facts / Ingress Context Projection Schemas and Evidence handling.
- Observation-owner dependencies define query payload Schemas and guarantees.
- Deployment-owned CapabilityContracts define exact callable membership and Effect.

A Procedure SourcePath such as context.subject.ueRef makes the Context dependency explicit at the use site. Compiler resolves the corresponding exact Host export from the supplied snapshot. Skill source does not maintain a second context.projections Schema map or an Evidence envelope Schema.

## Compiler output and external dependencies

Compiler returns BuildResult as an in-memory file map. Studio decides how to display generated projections and whether to export a ZIP or folder. No physical output/ directory is required by the language or Compiler.

Source Schema files may be YAML serialization of JSON Schema. The generated Schema serialization (YAML versus canonical JSON) is a separate Compiler Artifact Contract decision; source YAML remains authoritative.

Compiler must not copy every external lib file into the Skill package or output indiscriminately. It resolves exact referenced exports and Schema IDs. If a self-contained deployment bundle is required, include only the transitive dependency closure reachable from this Skill's compiled graph, preserving Owner identity and version. Whether to embed that closure or retain exact external references is a separate packaging decision.

Compiler does not manage workspace folders, imported sources, dependency versions, locks, caches, Git, Upload or MCP. Those are caller / Studio concerns.
