# Skill Schema Ownership v0

> Compatibility note (2026-11-12): this document describes the current v0.2 source-tree convention. In vNext, Skill source must not bind to physical `lib/` paths. The `lib/**` paths below are current local source locators only; see [Capability & Authoring Model vNext §15](design/capability-authoring-model-vnext.md#15-dependency-identity-versus-local-lib-layout) for the target dependency-identity model. Existing v0.2 compilation behavior remains unchanged until a separately reviewed migration.

The source tree must contain only schemas owned by the Skill. A file being present in a Skill folder does not make that Skill the owner of every data shape it consumes.

| Contract | Owner | Source / Compiler treatment |
| --- | --- | --- |
| Public Skill Request | Skill author | `spec.inputs.requestSchema` points to `schemas/**`; Compiler resolves `context.request.*` from it. |
| Tool Operation Input / Output | Tool owner | Imported ToolCatalog under logical `lib/tools/**`; Compiler links exact Operation IDs and uses its Schemas. |
| Host Subject / Facts | Agent Host owner | Explicit `spec.context.schemas.subject/facts` paths into logical `lib/host/**`; missing files are `EXTERNAL_SCHEMA_MISSING`. |
| Observation payload | Observation source owner | Explicit `spec.context.schemas.observations` path into logical `lib/observations/**`. |
| Predicate evidence/provenance projection | Host / Runtime owner | Explicit `spec.context.schemas.evidence` path into logical `lib/host/**`. Never infer it from a Script or Case fixture. |
| Procedure Script input | No separate file owner | Derived per call site from `with:` Producer references. |
| Predicate Script input | Host evaluation context + declared observations | Derived from Request, explicit Host Schemas and Predicate observation declarations. |
| Script output | Skill Script | Generated from the Script's strict Output `TypedDict`; read-only BuildResult output, not author source. |

`context.requiredFacts` is a list of required fact identifiers, **not** a field-level data Schema. `Procedure.inputs.*.type` is at most an author assertion checked against its Producer; it cannot replace a missing Producer Schema.

## Current PDU Session external dependencies

The current conventional PDU Contract declares these logical Owner inputs:

- `lib/host/subject.schema.yaml`
- `lib/host/facts.schema.yaml`
- `lib/host/evidence.schema.yaml`
- `lib/observations/context-observations.schema.yaml`

These are references to required Owner contracts, not Schemas authored or fabricated in this repository. The current official `lib/` snapshot contains only `lib/tools/createdsession.tool.yaml` (12 Operations); the Host/Observation Schema files are not bundled. A strict build must report these missing inputs until the actual owners supply them. `root-routing-profile-v0.5.schema.json` is deployment configuration and is not a substitute.

## Compiler / Studio boundary

`ca-skills` owns Skill-authored contracts and official examples. Studio/caller prepares file bytes and supplies imported Owner/Tool contracts in the Compiler's logical `lib/**` namespace. Compiler parses and links supplied bytes; it does not discover, fetch, persist, version, lock or refresh dependencies. `outputFiles` are Compiler results; Studio decides how to display or export them.


## Additional Tool Owner Schema gap

The pinned `lib/tools/createdsession.tool.yaml` is an approved ToolCatalog snapshot, but the `sbi.udm.sm_data.get` Operation currently declares `outputSchema.properties.result` only as `{type: object}` with no nested `properties`. The conventional selection Script reads nested fields under `udmResult.subscription` (including S-NSSAI, DNN, PDU Session Types, SSC Modes, AMBR and default QoS), as well as response and provenance fields.

That broad `object` declaration is not sufficient evidence for those nested fields. The Compiler must not infer them from the Script body or restore the removed Skill-owned `selection-input.schema.yaml` as a workaround. Until the Tool Owner supplies a complete Operation Output Schema, strict linking of those nested accesses must remain an explicit unresolved/unsupported producer-schema diagnostic.

This is separate from the missing Host Subject/Facts/Evidence and Observation Owner Schemas above.


## vNext direction: no Skill-authored physical library paths

The vNext model separates **what a Skill depends on** from **where the dependency bytes live**:

- Skill source declares a stable dependency / exported contract identity, not `lib/...`.
- Plugin-managed Workspace Configuration resolves that identity to a pinned source and immutable snapshot, and manages versioning, integrity, import, refresh, and cache.
- Compiler receives Skill source plus resolved dependency snapshots in a deterministic logical namespace. It never fetches or manages dependencies.
- Studio may display resolved imports in a read-only `lib/` tree, but that is not a mandatory source layout or a locator authored in the Skill.
- No new mandatory project manifest or lockfile is introduced solely to encode paths; use the accepted Plugin-managed configuration boundary.

Until this migration is separately approved, the current v0.2 `lib/...` references remain compatibility syntax. Do not change them piecemeal or invent the missing Host / Observation owner schemas.


## vNext Predicate and Script I/O ownership (design review)

The table above remains the current v0.2 compatibility rule. For the proposed pure-Predicate vNext model, the corresponding ownership is:

- **Procedure Script input:** derive the effective input projection from that Procedure Script call site's `with/from` bindings. Do not author a separate Script Input Schema.
- **Predicate input interface:** declare named values in `Predicate.inputs`; each Procedure `verify.with/from` call site supplies them. The effective Predicate Script input is derived from that declaration, all call sites, and the producer/Context contracts. Multiple call sites must be compatible.
- **Predicate Script Evidence:** Runtime attaches Host-generated Evidence separately to each producer-backed input. Evidence is not a Script-authored field or a substitute for the business payload.
- **Script output:** generate the output Schema from the Script's strict return `TypedDict`. Do not maintain a parallel authored per-Script Output Schema.
- **READ Operation output:** the Tool/adapter Owner owns the domain payload Output Schema. Host owns only the generic Evidence/provenance projection. Do not retain one aggregate Observation payload Schema as a substitute for the individual READ outputs.
- **Execution policy:** Sandbox, timeout, budget and permissions remain Host/Runtime policy, not Script metadata.

The current `spec.context.schemas.observations` path is v0.2 compatibility syntax. In vNext, Observation acquisition is scheduled explicitly and each Predicate consumes declared inputs; domain payload contracts follow their actual READ Operation or stored-artifact projection owner. The exact YAML placement and shared Context/Evidence projection syntax remain design-review items.

The PR branch adds `predicate-evaluation-result.schema.yaml` as a package-level Predicate evaluation result Schema candidate. It is **not** a per-Script Output Schema and is not currently linked by official `ca-skills` v0.2 source. Its shape overlaps with the `PredicateEvaluationResult` return `TypedDict` used by both evaluator Scripts, but it is not generated from those declarations. Keep it separate from per-Script output contracts, which remain generated from each Script's strict return `TypedDict`. Its exact vNext consumer/owner/link is deferred; do not expand this candidate as part of the current input/acquisition migration.
