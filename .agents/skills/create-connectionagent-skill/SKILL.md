---
name: create-connectionagent-skill
description: Use when authoring or refreshing an official ConnectionAgent Skill in ca-skills. Follow frozen CA-SL v1alpha4 author syntax, Schema/Owner rules and the unqualified PDU example migration decisions.
---

# Create or update an official ConnectionAgent Skill

## Authority

- Official Skill source and Skill-authored language semantics: this repository.
- Current **unqualified** v1alpha4 examples: `examples/skills/establish-pdu-session/` and `examples/skills/establish-pdu-session-mas/`. Old v0.2 baselines: `examples/legacy/`.
- Current source provenance: `docs/current-5gc-skill-baseline.md`.
- Normative language authority: `docs/skill-language-spec.v1alpha4.zh-CN.md` at frozen SHA `7f84393` (the unversioned alias only redirects).
- Procedure Script authority: v1alpha4 §32.1/F.6; `docs/script-contract.md` is historical v0 guidance.
- Schema ownership: `docs/schema-ownership.md`.
- Procedure semantics: v1alpha4 §12/§22.1; `docs/authoring-model.md` is supporting commentary.
- Semantic token registry: `language/semantic-tokens.v1.json`.
- Practical syntax: `references/authoring-syntax.md` (check for v1alpha4, not an authority to override the frozen spec).

## Workflow

1. Decide whether the asset is an executable Skill, model-context package or externally owned Tool/Observation contract.
2. Read `examples/MIGRATION-REVIEW-v1alpha4.md` and the current 5GC baseline before copying an example; no proposed Owner identity is approved. Legacy packages under `examples/legacy/` are behavioral references only and cannot be linked as v1alpha4.
3. Keep English `SKILL.md` model-facing: business goal, applicability, supported profile, required facts, invalid inferences, completion and uncertainty. Do not expose Host/Runtime/Provider/Fabric/adapter/deployment internals.
4. For an executable Skill, maintain the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio.
5. Keep deterministic workflow in `procedure.yaml`. Use one root `start`/`nodes` DAG with stages `precondition/operation/observation/postcondition`, `operation.tool: Alias::ExportId` or `operation.script`, and explicit `arguments`; preserve business gates and forbid author `wait/await/poll/reconcile`.
6. Use Scripts only for deterministic local computation. Script identity is the package-relative file path; use strict `main(input: InputTypedDict) -> OutputTypedDict` (F.6); the input Schema is derived, never duplicated. Do not add metadata or independent local Tool IDs.
7. Put only Skill-owned public schemas in `schemas/`. Import Tool/Host/Observation Owner schemas as read-only caller-supplied contracts; never fabricate them.
8. Use one `cases/<case>/case.yaml` per semantic obligation. Cases are source material; never claim execution or qualification without owner-run evidence.
9. Put optional model knowledge in flat or logically grouped `references/` Markdown; list exact paths in `SKILL.md`. References are not automatically loaded.
10. Before claiming Compiler compatibility, verify the actual target Compiler against every source construct and imported reference. Source hygiene is not Compiler acceptance.
11. Before completing a source change or recommending a PR for merge, run the reusable review skill at [.agents/skills/review-connectionagent-skill/SKILL.md](../review-connectionagent-skill/SKILL.md) against the exact current head and resolve P0/P1 findings. In particular, map one primary business action per Node and co-locate supplementary Observation stages with the Operation they support; do not add standalone Observation-only Nodes by default.

## Validation language

- `SOURCE_SYNCED`: source files are present and provenance is recorded.
- `SOURCE_HYGIENE_PASS`: repository-local structural checks passed.
- `COMPILE_PASS`: the actual target Compiler completed successfully.
- `LINK_PASS`: all declared local/imported references resolved.
- `RUNTIME_PASS`: the admitted Runtime path executed successfully.
- `QUALIFIED`: a separately owned qualification gate passed.
- `LIVE_PASS`: the real target environment completed its acceptance scenario.

Never use a lower status as evidence for a higher one.
