# Dependency Identity & 5GC Owner Schema Resolution — vNext

Status: **DESIGN PROPOSAL / ALIGNMENT REQUIRED BEFORE COMPILER IMPLEMENTATION**
Date: 2026-11-12
Scope: ca-skills Skill source references, Skill Studio Plugin-managed Configuration v0.1, Compiler input boundary, and the executable conventional 5GC Skill only.

Related frozen/authoritative designs:
- [Skill Studio Plugin-managed Configuration & Tool Integration v0.1](https://github.com/odango-chan/ca-skill-studio-demo/blob/main/docs/architecture/plugin-managed-configuration-v0.1.md)
- [Compiler v0.1 contract PR #4](https://github.com/odango-chan/ca-skill-compiler/pull/4) (Draft; its current `lib/**` logical-path input model needs alignment before implementation)
- [Capability & Authoring Model vNext](capability-authoring-model-vnext.md)
- [5GC Schema & Observation Source Inventory](5gc-schema-source-inventory-vnext.md)
- [Schema Ownership v0](../schema-ownership.md)

## 1. Decisions

1. Skill source must not name physical workspace paths such as `lib/host/subject.schema.yaml`.
2. Do not add a `dependency:` locator, repository URL, source kind, revision, digest, cache key, or local path to SkillContract. Those belong to Plugin-managed Workspace Configuration and its lock.
3. Skill source may name a stable **exported contract identity** when a contract must be referenced explicitly. That identity names *what* is consumed, not *where* bytes are stored.
4. The Workspace Configuration maps the declared dependency set to source acquisition, exact revision, selected exported contracts, immutable snapshot digest and snapshot bytes. It owns Add / Refresh / Update Lock / Remove.
5. Compiler receives Skill source and already-resolved immutable dependency snapshots through a versioned in-memory BuildRequest. It verifies the canonical snapshot digest and links stable exported contract identities. It does not fetch, select, lock, cache, or update dependencies.
6. A Studio `Dependencies` TreeView is the user-facing view of these dependencies. A physical `lib/` folder is neither required nor the source of truth. If an implementation renders a read-only virtual tree, that is presentation only.
7. The current v0.2 `spec.context.schemas.*: lib/...` paths remain compatibility syntax until an explicit breaking language migration. Do not mix old paths and new IDs in one Skill source file.

## 2. Correct boundary: no second dependency manifest in Skill source

The frozen Studio v0.1 design already provides project-scoped native settings:
- `connectionAgent.skillStudio.dependencies`
- `connectionAgent.skillStudio.dependencyLock`

Studio owns source selection (Upload, MCP discovery, Git, Built-in), acquisition, normalization, immutable snapshot persistence, lock updates, refresh, export, and cache. User Settings are not authoritative for shareable project dependencies; workspace-folder scope is.

Therefore:
- Do **not** add `dependency` / `repository` / `source` blocks to `assurance/contract.yaml`.
- Do **not** introduce `skill-project.yaml`, `skill.lock.yaml`, or another mandatory project manifest.
- Do **not** make the Compiler discover dependencies from the workspace or network.
- Do **not** use physical `lib/**` paths as the vNext dependency identity.
- Do not confuse dependency presence with Agent Host Provider Binding, authorization, Runtime readiness, or tool execution permission.

The Skill source should contain only language-level references to the exported contract it consumes. For example, a future schema-reference syntax may identify a stable owner contract ID such as `ca.host.context/subject`; this is illustrative only and is **not frozen YAML syntax**. The dependency settings resolve that exported ID to a pinned immutable snapshot.

For Tools, continue to use globally stable exact Operation IDs in Procedure calls and Capability grants. The selected dependency snapshot must export the exact Operation ID and ToolCatalog contract. For MCP collisions, Studio's dependency identity/alias distinguishes source snapshots; the Operation ID within each snapshot must still be linked unambiguously under the Compiler's versioned reference rules. Never guess based on server discovery order or tool display name.

## 3. Compiler input contract: current v0.1 mismatch to resolve

The current Compiler v0.1 Draft #4 defines:
`BuildRequest { files: File[], targets?: string[] }`
and restricts file paths to `skills/**` and logical `lib/**`. It describes `lib/**` as a caller-assembled in-memory namespace, so it does not require a physical workspace folder. However, the frozen Studio v0.1 design explicitly calls for the new Go BuildRequest and logical Tool references, and says no `lib/` fallback. A path-only `lib/**` namespace loses the dependency identity and immutable snapshot boundary that Studio must pass and Compiler must verify.

Before Compiler v0.1 implementation is accepted, align the wire contract with a versioned resolved-dependency input. The conceptual shape should be:

- authored Skill files, with paths rooted only in the Skill source namespace;
- a collection of resolved dependency snapshots, each identified by stable dependency identity and canonical content digest;
- each snapshot carries its immutable file bytes / exported contracts, with paths local to that snapshot rather than globally mounted beneath `lib/`;
- selected Skill targets.

The exact JSON shape, digest preimage/canonicalization, duplicate-ID rules, size limits, and schema-reference spelling are owned by the Compiler contract and must be frozen with cross-language golden vectors. Studio implements the same digest algorithm and supplies the lock-pinned bytes. This proposal does not prescribe an unreviewed wire schema or create a second ProjectContext object.

The Compiler must reject:
- missing dependency identity or digest;
- duplicate dependency IDs or duplicate exported contract IDs;
- a digest mismatch;
- an export that does not contain the exact referenced Operation / Schema;
- ambiguous references across snapshots;
- incompatible versions or unsupported schema dialects;
- dependency bytes that are not included in the normalized request.

No live Git/MCP/URL lookup is permitted during Check, LSP analysis, or Build.

## 4. 5GC dependency inventory: actual owner, not a Skill-owned copy

The first and only executable acceptance baseline is `ca-agent-demo`'s conventional `establish-pdu-session` Skill and its real 5GC ToolCatalog / integration implementation. MAS is not end-to-end runnable and is excluded from this inventory's acceptance criteria.

| Required contract | Current evidence / owner boundary | Current state | Required next action |
|---|---|---|---|
| Host Subject Context | Skill uses `context.subject.ueRef`; Host Context model is implemented in `ca-agent-demo/src/ca_agent_host/agent/context/base.py` and related projection/loader code | Formal exported owner Schema absent from ca-skills snapshot | Host owner publishes versioned Subject Schema and stable export ID |
| Host Facts Context | Skill requires `createdsession_ingress`, `createdsession_lifecycle`; Host context loader / resolvers and ingress integration establish their provenance | Formal exported owner Schema absent from ca-skills snapshot | Host owner publishes Facts Schema, fact identity, provenance and availability semantics |
| Generic Evidence Envelope | Runtime Observation model carries evidence/provenance/correlation and temporal semantics | Formal shared exported Schema absent from ca-skills snapshot | Host/Runtime owner publishes generic envelope separately from domain payload schemas |
| Observation payloads | 17 distinct 5GC Predicate Observation refs are registered to multiple owners/adapters; see Observation Owner Inventory | Existing runtime source registry works; vNext READ Operation and per-output schemas not yet complete | For each migrated READ Operation, actual source owner publishes its Output Schema and evidence/freshness/scope guarantees; do not fabricate one universal payload schema |
| 5GC ToolCatalog | `ca-agent-demo/tools/contracts/createdsession.tool.yaml`, imported in current ca-skills snapshot as `lib/tools/createdsession.tool.yaml` | 12 Operations imported; pinned snapshot currently records source commit `4395982fa6efb97714b97901603b2dfb7018c4d0` | Move from path-based import to Studio dependency snapshot; refresh only after source revision review |
| Capability contract | Deployment-owned Capability → Operation/effect registry in ca-agent-demo | Separate deployment authorization/effect cross-check; not interchangeable with ToolCatalog | Decide whether and how the deployment-owned contract is exported as a separate dependency; do not assume Skill Tool import implies deployment authorization |
| UDM subscription output | Current ToolCatalog says `result: {type: object}`, while selection Script reads nested subscription data | Producer Schema is too broad for strict nested linking | Tool owner must publish exact nested output Schema; do not infer from Script or restore Skill-owned shadow Schema |
| Skill Request Schema | `skills/establish-pdu-session/schemas/establishment-request.schema.yaml` | Skill-owned and present | Remains inside Skill source; no external dependency |

The Host Subject/Facts/Evidence schemas are separate contracts even if a future Host package groups them into one immutable snapshot. The dependency may be one package, but the exported contract identities and versioning remain individually addressable.

## 5. Observation migration must not be faked by dependency import

The current 5GC runtime has 17 distinct Predicate Observation refs. They route to multiple owners: Provider, Fabric ingress/hold, Open5GS adapter projections, and Host reference/evidence journals. A single imported `context-observations.schema.yaml` cannot be assumed to describe all those domain payloads.

Under the vNext model:
- generic Observation/Evidence envelope fields are Host/Runtime-owned;
- each READ Operation's domain result Schema is owned by the Operation / fact owner;
- provenance, scope, correlation, freshness, and evidence guarantees are declared by the relevant authoritative owner and acquisition adapter;
- Predicate consumes the acquired READ output/evidence through the common binding model;
- source-specific READ contracts must be introduced only when they preserve the current exact ref scope, conditional acquisition, freshness, UNKNOWN and trace semantics.

Do not remove the current ObservationSource registry or rewrite Predicate syntax until a per-ref migration matrix proves equivalence. This dependency/schema design does not itself migrate runtime behavior.

## 6. 5GC-first acceptance gates

1. Pin and record the exact `ca-agent-demo` source commit used for each imported ToolCatalog / owner contract snapshot.
2. Obtain the actual Host Subject, Facts and Evidence exported schemas from their owner; no Skill-side copies.
3. Obtain/derive each Observation READ output Schema from its actual owner implementation and existing integration tests, preserving owner boundaries.
4. Close the UDM nested subscription Output Schema gap at the Tool owner.
5. Freeze Compiler dependency snapshot input and digest golden vectors in coordination with Studio v0.1.
6. Import the pinned snapshots through Studio Dependencies settings; compile the conventional 5GC Skill without any physical `lib/` folder.
7. Compare effective bindings, diagnostics, generated output and Predicate Evidence behavior against the current 5GC baseline.
8. Keep every existing 5GC `with/from` mapping until full build and runtime/evidence equivalence are demonstrated.
9. Keep MAS excluded until its ToolCatalog, owner schemas and real end-to-end execution evidence exist.

## 7. Non-goals

This proposal does not create missing Host/Observation schemas, does not define MAS contracts, does not change current v0.2 Skill YAML, does not authorize a Compiler merge, and does not claim a successful 5GC build with the new dependency model. It defines the cross-repository alignment required before implementation.
