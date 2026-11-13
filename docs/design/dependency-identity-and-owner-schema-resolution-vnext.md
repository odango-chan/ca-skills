# Dependency Identity & Owner Schema Resolution — Skill Language vNext

**Status:** Normative cross-repository implementation boundary (2026-11-13).
**Scope:** `ca-skills`, Skill Studio Plugin-managed Configuration, `ca-skill-compiler`, and the executable conventional 5GC Skill.

This document is aligned with [Skill Language Specification](../skill-language-spec.md) and the frozen [Capability & Authoring Model](capability-authoring-model-vnext.md). It replaces the earlier v0.2 compatibility/path proposal.

## 1. Decisions

1. Skill source never names a physical workspace path such as `lib/host/subject.schema.yaml`.
2. Skill source references imported Tool Operations and Owner Schemas by `<dependency-alias>::<exact-exported-id>`.
3. The alias is a logical namespace mapped by Plugin-managed Workspace Configuration to one supplied dependency snapshot. It is not a repository URL, local path, source kind, revision, digest, cache key or acquisition instruction.
4. Studio owns dependency selection, acquisition, immutable snapshot persistence, locking, refresh and cache. Compiler receives the exact bytes and does not acquire or manage them.
5. Compiler BuildRequest contains Skill source files, dependency snapshots grouped by alias, one separate trusted deployment CapabilityContracts document, and optional targets.
6. Capability IDs in `allowedResources.capabilities` are unqualified exact IDs from that single trusted CapabilityContracts input. Tool/Schema aliases do not qualify or own deployment authorization.
7. Compiler links each exact Operation to exactly one Capability and cross-checks the ToolCatalog Effect against the independently declared Capability Effect. Runtime repeats authorization and Effect admission.
8. No project manifest, lockfile, package resolver, Compiler dependency digest output, or physical `lib/` source layout is introduced.
9. vNext is a breaking replacement. The Compiler rejects v0.2 `lib/**` paths, direct Operation grants and Predicate Observation declarations. No compatibility parser or field mapping remains.

## 2. Compiler input boundary

The caller supplies all source bytes required for one build. Conceptual shape:

```typescript
type File = { path: string; bytes: Uint8Array };

type DependencySnapshot = {
  alias: string;
  files: File[]; // paths are relative to this snapshot
};

type BuildRequest = {
  files: File[]; // Skill source only, under skills/**
  dependencies: DependencySnapshot[];
  capabilityContracts: File; // trusted deployment composition, separate input
  targets?: string[];
};
```

This is an implementation boundary, not a package-manager API. Compiler validates normalized paths, duplicate files/aliases/export IDs, schema structure and exact links. It does not fetch, pin, update, cache or persist any dependency.

BuildResult returns diagnostics and generated Skill-owned output files. It does not export dependency digests or copy dependency snapshots into generated Skill source. Studio owns dependency lock and persistence.

## 3. Imported contract identity

- Tool call: `fivegc-tools::sbi.udm.sm_data.get`
- Owner Schema: `ca-context::urn:connectionagent:ca:context:invocation:v1`
- Capability grant: `provider-5gc.createdsession.udm`

The alias selects the exact caller-supplied snapshot. The ID after `::` remains owned by the producer. Two imported snapshots that export the same ID are ambiguous and fail closed; the Skill must not rely on file order or source path to select one.

CapabilityContracts is not a normal dependency snapshot. It is deployment-owned trusted input. The Skill may grant a Capability ID but cannot define its owner, Operation membership, Effect or budget policy.

## 4. 5GC current Operations and vNext additions

The current executable deployment has six Capability groups and twelve Operations, with exact 1:1 Operation membership and matching READ/MUTATION Effects.

The pure-Predicate migration adds six READ Operations if N4 baseline and post-create initial resources share one phase-discriminated Operation identity:

| New READ | Owner | Capability boundary |
|---|---|---|
| N4 initial-resources read, phase PRE_CREATE / POST_CREATE | Provider/Open5GS adapter | New Provider assurance Capability |
| RAN setup read | Provider/Open5GS adapter | Same Provider assurance Capability |
| N4 forwarding read | Provider/Open5GS adapter | Same Provider assurance Capability |
| PCF create-governance read | env-fabric | Separate Fabric governance Capability unless Fabric confirms it is the same boundary as existing hold binding |
| Lifecycle registration read | Agent Host | Existing Host Runtime Capability |
| Resource responsibility read | Agent Host | Existing Host Runtime Capability |

This produces 18 callable Operations total. If the N4 Owner cannot provide a phase-discriminated result that preserves the PRE_CREATE baseline and POST_CREATE instance lineage, use two exact N4 Operation IDs; the total becomes 19. The existing bounded Host `ca.session.evidence.await` remains an orchestration READ Operation and is not counted as a new domain READ shape.

The five independent domain acquisition points are N4 baseline, post-create N4 resources, RAN setup, N4 forwarding and PCF governance. The two Host journal reads are additional explicit acquisition points. The 17 old Predicate Observation refs are not 17 new READ Operations:

- 1 legacy captured ingress projection whose admission checks move to Host;
- 9 prior-Operation local projections, passed from exact prior outputs and same-invocation Evidence;
- 2 Host journal READs;
- 5 independent domain acquisition points across four READ shapes.

## 5. Evidence and prior-operation results

A READ Operation returns one typed normalized value and Evidence from the same invocation. A Predicate consumes the exact prior output through `verify.with`; it never triggers a duplicate read to reconstruct provenance.

For UDM Get:

- the Provider Owner Schema validates the upstream HTTP response inside Host;
- the Host adapter's normalized `CreatedSessionUDMResult.runtime_value()` needs its own exported Schema;
- ToolCatalog `outputSchema.result` references the Host projection Schema, not the Provider wire Schema;
- Predicate receives the exact `nudm-sdm-get.output.result` and Evidence from the same full Provider receipt;
- no second UDM Get or parallel `sbi.operation.result` acquisition is allowed.

For local projections over hold, operation-context, PCF input, resource-ownership and AMF transfer results, reuse the exact stored artifact. Do not synthesize a `CURRENT` binding status from a handle or mutation success alone. Preserve selector, lifecycle, deadline, transaction, freshness and evidence checks.

## 6. 5GC-first acceptance

1. Publish the Host Invocation Context and Evidence-reference Schemas from their actual owners.
2. Publish typed Tool Output Schemas for all current Operation outputs consumed by Predicates.
3. Add the four domain READ shapes and two Host journal READ Operations with exact Input/Output contracts and Capability membership.
4. Update the trusted CapabilityContracts map and ToolCatalog together; fail closed on missing/duplicate membership or Effect mismatch.
5. Migrate the conventional 5GC Skill to pure Predicate inputs and explicit READ acquisition.
6. Build the 5GC Skill using supplied dependency snapshots without any physical `lib/` folder.
7. Validate the existing 36 Cases and three References as unchanged business constraints, then run focused Compiler/Runtime/5GC acceptance.

MAS remains non-executable design material and is not a prerequisite for 5GC acceptance.
