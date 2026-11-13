# Skill Package Layout and Source Ownership

This document defines the Skill source package, not a workspace or package-manager layout. Skill Studio owns dependency selection and project configuration. Compiler consumes a virtual file set and does not require a physical project `lib/` or `output/` directory.

## Canonical vNext Skill source

~~~text
skills/<skill-name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case-name>/
│       └── case.yaml
├── references/       # optional model knowledge
├── schemas/          # Skill-owned schemas only
└── scripts/          # Skill-owned deterministic Python
~~~

The three assurance files have separate responsibilities:

- `contract.yaml` — public Skill declaration: Goal, public Request Schema, required Host Context facts / Schemas, shared dependency identities, and Capability Grants.
- `procedure.yaml` — one deterministic execution graph: Procedure input projections, start, four business node types, routes, Reconcile edges and final Postcondition.
- `predicates.yaml` — reusable Predicate definitions, ordered parameter signatures and CEL / Predicate Script evaluators.

The Contract is authored source. It is not deleted or wholly generated. The Compiler may derive a normalized Runtime contract projection from Contract + Procedure + Predicate + resolved dependencies, but that is a build artifact, not a replacement for the author-facing Contract.

## Contract fields and generated metadata

Keep business declarations that matter to authoring and review:

- Goal and public Request Schema.
- Required Context facts and exact Context Projection Schema identities.
- Public dependency identities needed by the Skill (ToolCatalog, Host Context, Observation and shared Schema exports).
- Exact Capability grants selected from trusted deployment CapabilityContracts.

Do not repeat machine wrapper fields that are determined elsewhere:

- No authored `apiVersion` or `kind`; BuildRequest / Compiler Target selects the language version, and file paths determine source kinds.
- No authored `metadata.name`; the Package root determines Skill identity.
- No `entryProcedure`; a Skill has one entry Procedure graph in vNext.
- No Contract-level `postconditions`; the final Postcondition is an executable node in `procedure.yaml`.
- No dependency download URL, branch, version lock, digest or registry instruction in the Skill Contract. Studio resolves exact snapshots in project/build configuration.

An Owner Schema ID may itself contain an immutable revision component (for example `...:v1`). Preserve that identity exactly; it is not the same as repeating a language `apiVersion` in every source file.

## Schema and Script ownership

- `schemas/` contains only interfaces owned by the Skill, such as its public Request Schema.
- Do not copy imported Tool / Host / Observation Schemas into an individual Skill package.
- Do not author Procedure Script Input Schemas. The call-site `arguments` mapping and source contracts derive the effective input projection.
- Do not author Script Output Schemas. Strict return `TypedDict` declarations generate read-only JSON Schema in BuildResult.
- Predicate Script inputs derive from Predicate.parameters plus the exact call-site positional bindings.
- Generated output is not written back into the Skill source tree.

## Public dependencies and Capability Grants

Dependencies and grants are separate declarations:

- A dependency makes an Owner-published contract available for linking and editing. It does not grant permission to execute it.
- A Capability Grant is the Skill's explicit authorization request. It does not provide the ToolCatalog, Operation Schema or Observation Schema needed to compile a reference.
- Procedure references exact exported Operation / Observation identities. Contract dependencies identify the public Owner packages or export groups that provide those identities.
- The trusted deployment-owned CapabilityContracts input independently maps each Capability to exact callable membership and Effect. Compiler verifies that every external callable is covered by exactly one granted Capability and that its Effect matches. Runtime still performs admission.

At Skill creation, Studio should offer a guided selection flow over the available public dependency catalog and trusted CapabilityContracts:

1. Select required shared dependencies (Host Context, ToolCatalog / Observation contracts, shared Schema libraries).
2. Select the exact Context projections / facts the Skill needs.
3. Select Capability grants from the trusted Capability catalog.
4. Create or select the Skill-owned public Request Schema.
5. Generate / update `contract.yaml`; add exact call references as the Procedure is authored.

These selections remain editable later in a dedicated Dependencies / Capabilities view. Studio fetches the chosen dependency bytes and supplies exact immutable `DependencySnapshot` inputs plus the trusted CapabilityContracts to Compiler. Compiler only parses, links and validates; it does not search registries, download dependencies, manage locks or resolve versions.

The Contract records stable dependency identities and grants, not the currently downloaded copies. Exact selected dependency snapshots / revisions belong to Studio project configuration or Build input. If a dependency changes, Studio can show the impact and re-run linking without silently rewriting the Skill's declared public requirements.

## Imported external contracts

Compiler receives imported contracts as exact immutable DependencySnapshot inputs. A logical dependency alias is used in source references (for example `host-context::urn:...` or `ca::sbi.udm.sm_data.get`); it is not a physical folder path or a stable Owner identity.

- Imported ToolCatalog contracts define exact Operation and Observation callable identities.
- Host dependencies define Subject / Facts / Ingress Context Projection Schemas and Evidence handling.
- Observation-owner dependencies define query payload Schemas and guarantees.
- Deployment-owned CapabilityContracts define exact callable membership and Effect and are supplied separately from ordinary dependencies.

Do not maintain a second field-level Schema map when the Contract already references the exact Context Schema identities. Do not infer a Schema from `requiredFacts`.

## Compiler output and external dependency closure

Compiler returns BuildResult as an in-memory file map. Studio decides how to display generated projections and whether to export a ZIP or folder. No physical `output/` directory is required by the language or Compiler.

Source Schema files may be YAML serialization of JSON Schema. The generated Schema serialization (YAML versus canonical JSON) is a separate Compiler Artifact Contract decision; source YAML remains authoritative.

Compiler must not copy every external dependency file into the Skill package or output indiscriminately. It resolves exact referenced exports and Schema IDs. If a self-contained deployment bundle is required, include only the transitive dependency closure reachable from this Skill's compiled graph, preserving Owner identity and exact dependency revision. Whether to embed that closure or retain exact external references is a separate packaging decision.

Compiler does not manage workspace folders, imported sources, dependency versions, locks, caches, Git, Upload or MCP. Those are caller / Studio concerns.
