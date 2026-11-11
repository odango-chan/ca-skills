# Current 5GC Skill Source Baseline

## Source of truth

Both current 5GC Skill packages in this repository were synchronized from:

- Repository: `odango-chan/ca-agent-demo`
- Ref: `main`
- Commit: `4395982fa6efb97714b97901603b2dfb7018c4d0`
- Source root: `skills/`

The source commit is pinned here so future refreshes are explicit and reviewable. The two Skills remain separate profiles; do not combine their workflows or infer that one is a fallback for the other.

## Synchronized packages

| Package | Source files | Contents |
| --- | ---: | --- |
| `establish-pdu-session` | 59 | model guide, assurance trio, 36 Case obligations plus Case index, 3 optional References, 10 schemas, 5 governed Scripts |
| `establish-pdu-session-mas` | 11 | model guide, assurance trio, 6 Case obligations, 1 request schema |

The maintainer-only `design/` directories from the prototype repository were not copied into either Skill package. Relevant authoring semantics are summarized in [Authoring model](authoring-model.md); maintainer-only operation context is in [PDU Session integration notes](skills/establish-pdu-session-integration.md).

The conventional Skill's model-facing guide was also cleaned of prototype-relative design links and adapter-specific integration prose. Its business rules and Procedure source were retained. The detailed operation-handle and integration notes were moved out of model context.

## Imported Library

`lib/tools/createdsession.tool.yaml` is an exact read-only snapshot of:

`odango-chan/ca-agent-demo/tools/contracts/createdsession.tool.yaml`

Source blob: `05a34f38b9974742c9e2d85e0d432cf616ce01e8`

It declares 12 Operations. The conventional Skill's `contract.yaml` lists exactly those 12 Capability IDs; all 12 resolve by name against this snapshot.

The MAS Skill declares 16 `ca.pdu_session.*` Capabilities. None of those 16 Operations is present in the imported ToolCatalog. The MAS prototype's `design/tool-contract.yaml` is a design artifact and is not an approved ToolCatalog, so it was intentionally not imported. MAS dependency resolution remains BLOCKED until the owning Tool contract is supplied and approved.

## Compatibility and acceptance status

### Conventional PDU Session Skill

- The Procedure uses node-level `preconditions` and `postconditions` (three precondition blocks and eight postcondition blocks).
- The current legacy `ca-skill-toolchain/schemas/v1alpha1/procedure-source.schema.yaml` has no node-level `preconditions` or `postconditions` fields.
- The source is synchronized; legacy Toolchain compile compatibility is therefore not claimed.
- Its 36 Cases are explicitly documented by the source `cases/README.md` as semantic qualification obligations, not executable Runtime fixtures.
- Compiler build, Runtime execution, qualification and live 5GC acceptance are NOT_RUN.

### MAS PDU Session Skill

- The source has six Cases and uses native `reconcile` nodes.
- The current imported Library does not contain its 16 declared Capabilities.
- The source-side review in [ca-agent-demo MAS review findings](https://github.com/odango-chan/ca-agent-demo/blob/4395982fa6efb97714b97901603b2dfb7018c4d0/skills/establish-pdu-session-mas/design/skill-review-findings-20261110.md) labels several source corrections as proposed/unverified and records unresolved owner/Tool/Observation dependencies.
- Compiler/link validation, MAS Mock/Live execution, qualification and production readiness are NOT_RUN.

## Compiler transition

The stateless Skill Compiler v0 design is accepted in [ca-skill-toolchain/docs/design/skill-compiler-v0.md](https://github.com/odango-chan/ca-skill-toolchain/blob/main/docs/design/skill-compiler-v0.md), tracked by [#133](https://github.com/odango-chan/ca-skill-toolchain/issues/133). It defines the `skills/`, read-only `lib/` and generated `output/` project model, plus Native and Browser/WASM use of one Core.

The new `ca-skill-compiler` repository currently contains only its bootstrap README; implementation is NOT_STARTED. This source baseline is not represented as compiled, linked, Runtime-ready or qualified.

## Scope of this refresh

- The two packages above are the current 5GC baseline.
- Other pre-existing `skills/*` packages remain unchanged and are outside this migration, per the current scope decision.
- No source files in `ca-agent-demo` or `ca-skill-toolchain` were modified by this refresh.
