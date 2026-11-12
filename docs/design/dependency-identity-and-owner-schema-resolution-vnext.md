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
3. Skill source may name a stable **dependency alias + exported contract identity** when a contract must be referenced explicitly. The alias is a logical namespace, not acquisition configuration. It names *which locked dependency snapshot* supplies the export, not *where* bytes are stored.
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

The Skill source may contain a qualified exported-contract reference in the form `<dependency-alias>::<exported-contract-id>`. For example, `host-contracts::ca.host.context/subject.v1` identifies one exported Host Schema; `fivegc-tools::sbi.udm.sm_data.get` identifies one exact Operation. The alias is a stable logical namespace configured by Studio, not a repository, URL, MCP connection, revision, digest, or path. The exact YAML positions and escaping/validation rules are part of the versioned Skill language contract.

For Tools, keep Capability and Operation as distinct linked identities. The Capability contract defines `Capability ID -> owner -> exact Operation IDs + expected Effects`; ToolCatalog defines each Operation's callable input/output/reconcile contract. The Skill grants qualified Capability IDs (`dependency-alias::capability-id`) in `allowedResources.capabilities`; Procedure nodes call qualified exact Operation IDs (`dependency-alias::operation-id`). Compiler must prove every called Operation belongs to exactly one Capability in the same resolved snapshot and that the Skill grants that qualified Capability. A Tool Operation is not an independent permission and must never be treated as an ungrouped standalone tool. Where multiple dependency snapshots can export colliding Operation IDs, the source reference must be qualified by dependency alias, e.g. `fivegc-tools::sbi.udm.sm_data.get`; that alias only disambiguates the logical namespace and does not replace the Capability grant. CapabilityContracts and ToolCatalog must be supplied as distinct contracts and cross-checked for exact membership/effect. In the current 5GC deployment, CapabilityContracts is deployment-owned authorization composition, not a Skill-owned dependency: the Skill may request Capability IDs but cannot define or select their Operation membership/Effects. Any compile-time membership proof therefore requires the selected target deployment to supply its trusted CapabilityContracts separately; without that input, only the Skill grant syntax and Operation references can be checked, while actual admission remains a Runtime responsibility. Existing 5GC `allowedResources.capabilities` currently lists Operation IDs; that is a compatibility-era source representation and must be migrated to actual Capability IDs only through a separately reviewed language change preserving exact operation coverage.

## 3. Compiler input contract: proposed v0.2 alignment

Compiler Draft #4 has been revised on its design branch to separate Skill source from resolved dependencies. The proposed wire shape is:

```typescript
type File = { path: string; bytes: Uint8Array };
type ResolvedDependency = {
  dependencyId: string;       // Studio logical alias / reference namespace
  digest: `sha256:${string}`; // input integrity check; not exported by BuildResult
  files: Array<{ path: string; bytes: Uint8Array }>; // snapshot-relative paths
};
type BuildRequest = {
  files: File[]; // skills/** only
  resolvedDependencies: ResolvedDependency[];
  targets?: string[];
};
```

The Compiler owns the canonical snapshot digest algorithm and verifies it; Studio computes and stores the same digest in its lock. The digest is SHA-256 over a versioned binary preimage containing sorted UTF-8 snapshot-relative paths and raw file bytes. It deliberately excludes dependencyId, source URL, revision and other mutable acquisition metadata. See Compiler Draft #4's [dependency snapshot digest contract](https://github.com/odango-chan/ca-skill-compiler/blob/docs/plugin-managed-contract-v01-20261111/docs/design/dependency-snapshot-digest-v0.1.md) and its golden vector.

The Compiler does not need a second dependency manifest or exported-contract list: it indexes exact Operation IDs from ToolCatalog files and stable Schema IDs from JSON Schema `$id` values inside the supplied snapshots. Duplicate dependency IDs, duplicate file paths within a snapshot, digest mismatches, duplicate Operation IDs / Schema IDs, missing exports and ambiguous legacy paths fail closed.

For current v0.2 source compatibility, existing `lib/...` values in `spec.context.schemas` are temporary locators matched against an exact snapshot-relative path across supplied snapshots; zero matches is missing and multiple matches is ambiguous. This does not recreate a global `lib/**` namespace or require a physical `lib/` folder. The vNext language replaces these locators with exact Owner-controlled Schema `$id` strings. It never places dependency IDs/aliases or source metadata in Skill YAML.

BuildResult returns selected Skill source/generated Skill files and a sorted `dependencyClosure` of the dependency aliases actually used. Snapshot digests are verified BuildRequest inputs and are not exported. It does not copy dependency bytes into `outputFiles`; Studio remains responsible for persistence/export and can package the locked snapshots alongside the build result.

This wire change is still a **Draft design**, not an implemented Compiler API. The current Go/WASM v0 API remains the compatibility baseline until the implementation Goal updates both Native and WASM and passes the digest vectors.

## 4. 5GC dependency inventory: actual owner, not a Skill-owned copy

The first and only executable acceptance baseline is `ca-agent-demo`'s conventional `establish-pdu-session` Skill and its real 5GC ToolCatalog / integration implementation. MAS is not end-to-end runnable and is excluded from this inventory's acceptance criteria.

| Required contract | Current evidence / owner boundary | Current state | Required next action |
|---|---|---|---|
| 5GC Skill Subject Context | `FabricResidentSource._materialize()` projects operator-profile `ueRef` | Proposed Owner export in [ca-agent-demo PR #198](https://github.com/odango-chan/ca-agent-demo/pull/198); focused schema test PASS, PR unmerged | Merge Owner export, then pin/import `urn:connectionagent:5gc:skill-context:subject:v1` |
| 5GC Skill Facts Context | `FabricResidentSource._materialize()` projects Fabric `sourceRef` and independent operator lifecycle binding | Proposed Owner export in [ca-agent-demo PR #198](https://github.com/odango-chan/ca-agent-demo/pull/198); focused schema test PASS, PR unmerged | Merge Owner export, then pin/import `urn:connectionagent:5gc:skill-context:facts:v1` |
| Predicate Evidence Reference Projection | `PredicateEngine.evaluate()` passes observation-name → `{refs: source_fact_ids}` to Predicate Scripts | Proposed Host export in [ca-agent-demo PR #198](https://github.com/odango-chan/ca-agent-demo/pull/198); focused schema test PASS, PR unmerged | Merge Owner export, then pin/import `urn:connectionagent:host:predicate-evidence-refs:v1`; keep full Runtime evidence internal |
| Observation payloads | 17 distinct 5GC Predicate Observation refs are registered to multiple owners/adapters; see Observation Owner Inventory | Existing runtime source registry works; vNext READ Operation and per-output schemas not yet complete | For each migrated READ Operation, actual source owner publishes its Output Schema and evidence/freshness/scope guarantees; that Operation is also assigned to exactly one Capability; do not fabricate one universal payload schema |
| 5GC ToolCatalog | `ca-agent-demo/tools/contracts/createdsession.tool.yaml`, imported in current ca-skills snapshot as `lib/tools/createdsession.tool.yaml` | 12 Operations imported; pinned snapshot currently records source commit `4395982fa6efb97714b97901603b2dfb7018c4d0` | Move from path-based import to Studio dependency snapshot; refresh only after source revision review |
| Capability contract | Deployment-owned Capability → Operation/effect registry in ca-agent-demo | Separate deployment authorization/effect cross-check; not interchangeable with ToolCatalog | Decide whether and how the deployment-owned contract is exported as a separate dependency; do not assume Skill Tool import implies deployment authorization |
| UDM subscription output | Current ToolCatalog says `result: {type: object}`, while selection Script reads nested subscription data | Producer Schema is too broad for strict nested linking | Tool owner must publish exact nested output Schema; do not infer from Script or restore Skill-owned shadow Schema |
| Skill Request Schema | `skills/establish-pdu-session/schemas/establishment-request.schema.yaml` | Skill-owned and present | Remains inside Skill source; no external dependency |

The 5GC Subject, 5GC Facts and Host Predicate Evidence-reference schemas are separate contracts even if Studio groups them into one immutable dependency snapshot. The full Runtime `ObservationEvidence` dataclass is not the Script-facing evidence schema. Each exported contract identity remains individually addressable. The current PR #198 exports are not authoritative on `main` until merged.

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


## Observation output Schema status

The owner-side proposal [ca-agent-demo PR #200](https://github.com/odango-chan/ca-agent-demo/pull/200) covers 16/17 normalized 5GC Observation outputs. The upstream Provider nested subscription schema now has a proposal in [ca-provider-5gc PR #50](https://github.com/odango-chan/ca-provider-5gc/pull/50), but it is still OPEN / DRAFT and has no reported CI run. After it is accepted, the Host adapter's normalized `sbi.operation.result` schema must still be published separately. Do not claim the 5GC dependency set is complete until both owner contracts are merged and the Host projection is tested.


## 8. Reference identity correction

The logical dependency alias **is part of a Skill reference namespace**, as required by Skill Studio Plugin-managed Configuration v0.1 for MCP source collisions. It is not dependency acquisition configuration. The stable reference is `<dependency-alias>::<exported-contract-id>`; the alias maps to the locked snapshot in workspace settings. Changing the alias is a source refactor, while changing the locked snapshot behind an alias is an explicit dependency Update Lock operation. Do not claim that Skill source contains no dependency alias at all; the correct prohibition is against source locators and lifecycle metadata.


## 8. Capability / Operation relation and digest output boundary

A Tool is not an independent permission. The Capability owner contract groups exact Operations and their expected effects; ToolCatalog defines callable Operation schemas/effects. Skill grants qualified Capability IDs; Procedure calls qualified Operation IDs; Compiler links each Operation to exactly one granted Capability in the same dependency snapshot and cross-checks the independently declared Effect. Observation remains a separate read-only source/evidence contract and is not automatically promoted to a callable Tool Operation. If an Observation read is explicitly exposed as a Tool Operation, that Operation must belong to exactly one Capability and be authorized by the Skill.

Compiler may verify snapshot digests supplied in BuildRequest as part of integrity validation, but **does not export digest values in BuildResult**. The proposed BuildResult reports only the dependency aliases actually used, diagnostics and generated files. Studio remains the sole owner of dependency lock/digest display and persistence.
