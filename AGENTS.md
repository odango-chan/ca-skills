# ca-skills repository rules

## Ownership

- This repository owns official ConnectionAgent Skill source and authoring guidance.
- `ca-agent-demo` is a reference implementation/sample source, not the owner of the official catalog.
- `ca-skill-toolchain` contains the legacy machine schemas/compiler.
- The accepted stateless `ca-skill-compiler` v0 design is tracked by [ca-skill-toolchain#133](https://github.com/odango-chan/ca-skill-toolchain/issues/133). The new repository is bootstrap-only; implementation is not yet available.

## Project roots

The project has three fixed semantic roots: `skills/` (editable author source), `lib/` (imported read-only external contracts), and `output/` (generated read-only build projection). Their Explorer permissions and actions are defined in [docs/project-layout.md](docs/project-layout.md). The root folders themselves are not renamed, moved, or deleted through ordinary file actions.

## Current 5GC source baseline

The current 5GC source baseline is:

- `skills/establish-pdu-session/`
- `skills/establish-pdu-session-mas/`

See [Current 5GC Skill baseline](docs/current-5gc-skill-baseline.md). Other pre-existing packages under `skills/` are retained unchanged but are outside this baseline. Do not use them as current authoring examples or spend migration effort on them unless explicitly requested.

## Package rules

- Official packages live under `skills/<name>/`.
- `SKILL.md` is the English, model-facing business entry point. Keep it focused on domain meaning, supported profile, normalization, required facts, invalid inferences, and completion/failure semantics.
- Do not expose internal Host, Runtime, Fabric, Provider, adapter, deployment, endpoint, credential, or transport implementation details in model-facing Skill prose. Put maintainer-only integration notes under `docs/`.
- Do not duplicate a deterministic Procedure graph in `SKILL.md`. The file is business guidance for model-driven execution; the authored Procedure remains the deterministic source.
- An executable Skill uses the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio. Do not add a standalone `evidence.yaml`.
- Each qualification case is one `cases/<case>/case.yaml`. Case source is not evidence that the case has been executed or qualified.
- Package-root `README.md`, `MIGRATION.md`, `examples/`, and maintainer `design/` directories are not part of the official Skill package.
- `references/` contains optional, flat `*.md` business knowledge files.
- `SKILL.md` lists exact reference paths and explains when each may help. Reference loading is model-selected; do not create `preload/` or `on-demand/` subdirectories or encode loading policy in directory names.
- Reference files are not live evidence, do not grant authority, and are not automatically injected into context.
- Skill-local `scripts/` are governed deterministic local computation only. They must not perform Provider I/O, network access, credential access, shell workflows, or uncontrolled side effects.

## Procedure and machine-contract authority

- The current 5GC source baseline includes node-level `preconditions` and `postconditions`; see [Authoring model](docs/authoring-model.md).
- The legacy `ca-skill-toolchain` `procedure-source.schema.yaml` does not currently model those node-level fields. Do not remove or flatten them merely to make the legacy validator pass.
- The new stateless Compiler v0 design is accepted, but its implementation is NOT_STARTED. Until it supports the current source constructs and imported Library references, compiler/link validation for this baseline is NOT_RUN/BLOCKED.
- For legacy packages that fit the existing v1alpha1 contracts, the current `ca-skill-toolchain` schemas/compiler remain their machine authority. Do not claim that this implies the new 5GC baseline has compiled.
- Never invent Capability contracts, Script schemas, or parser behavior. Unsupported features must be reported explicitly, not silently discarded.

## Imported Library

- `lib/` contains exact, read-only snapshots of externally owned Tool contracts used to resolve Skill references.
- The current imported snapshot is `lib/tools/createdsession.tool.yaml`, sourced from `ca-agent-demo/tools/contracts/createdsession.tool.yaml` at the commit recorded in [the baseline](docs/current-5gc-skill-baseline.md).
- Do not edit imported ToolCatalog content in place. Refresh it from its owner and update provenance.
- An imported contract is not proof that an implementation is registered, deployed, READY, or authorized.
- The MAS Skill's 16 `ca.pdu_session.*` references are not present in the current imported catalog. Its design-only `tool-contract.yaml` is not an approved ToolCatalog and must not be imported as one.

## Documentation and verification

- Human guides: `docs/authoring.md` and `docs/authoring.zh-CN.md`.
- Practical syntax notes: `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md`.
- Do not copy the complete machine grammar into prose.
- Use `make verify` only with an explicit understanding that the current script delegates to the legacy Toolchain. A failure caused by the known unsupported source constructs or unresolved MAS imports is a compatibility blocker, not permission to weaken the Skill.
- The future `skillc check/build` commands are targets, not currently available commands.
- Compile success, when available, is source/build evidence only; it is not Runtime qualification or live network acceptance.

## Issue discipline

Search for an existing owner Issue before creating another. The current CreatedSession authoring/semantic-review trail is [ca-skills#20](https://github.com/odango-chan/ca-skills/issues/20); the older Draft PR #21 is superseded by the refreshed source baseline and must not be treated as current source.
