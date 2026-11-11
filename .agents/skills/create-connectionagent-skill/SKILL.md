---
name: create-connectionagent-skill
description: Use when authoring or refreshing an official ConnectionAgent Skill in ca-skills. Follow the current Skill Language v0.2, Script Contract, Schema Ownership and current 5GC source baseline.
---

# Create or update an official ConnectionAgent Skill

## Authority

- Official Skill source and Skill-authored language semantics: this repository.
- Current executable source examples: `skills/establish-pdu-session/` and `skills/establish-pdu-session-mas/`.
- Current source provenance: `docs/current-5gc-skill-baseline.md`.
- Language authority: `docs/skill-language-spec.md`.
- Script authority: `docs/script-contract.md`.
- Schema ownership: `docs/schema-ownership.md`.
- Procedure semantics: `docs/authoring-model.md`.
- Semantic token registry: `language/semantic-tokens.v1.json`.
- Practical syntax: `references/authoring-syntax.md`.

## Workflow

1. Decide whether the asset is an executable Skill, model-context package or externally owned Tool/Observation contract.
2. Read the current 5GC baseline before copying an example. Other historical packages under `skills/` are not current syntax authorities.
3. Keep English `SKILL.md` model-facing: business goal, applicability, supported profile, required facts, invalid inferences, completion and uncertainty. Do not expose Host/Runtime/Provider/Fabric/adapter/deployment internals.
4. For an executable Skill, maintain the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio.
5. Keep deterministic workflow in `procedure.yaml`. `call` is a scalar exact Operation ID; preserve business ordering and explicit `with/from` bindings.
6. Use Scripts only for deterministic local computation. Script identity is the package-relative file path; use `main(input: dict) -> OutputTypedDict`. Do not add metadata or independent local Tool IDs.
7. Put only Skill-owned public schemas in `schemas/`. Import Tool/Host/Observation Owner schemas as read-only caller-supplied contracts; never fabricate them.
8. Use one `cases/<case>/case.yaml` per semantic obligation. Cases are source material; never claim execution or qualification without owner-run evidence.
9. Put optional model knowledge in flat or logically grouped `references/` Markdown; list exact paths in `SKILL.md`. References are not automatically loaded.
10. Before claiming Compiler compatibility, verify the actual target Compiler against every source construct and imported reference. Source hygiene is not Compiler acceptance.

## Validation language

- `SOURCE_SYNCED`: source files are present and provenance is recorded.
- `SOURCE_HYGIENE_PASS`: repository-local structural checks passed.
- `COMPILE_PASS`: the actual target Compiler completed successfully.
- `LINK_PASS`: all declared local/imported references resolved.
- `RUNTIME_PASS`: the admitted Runtime path executed successfully.
- `QUALIFIED`: a separately owned qualification gate passed.
- `LIVE_PASS`: the real target environment completed its acceptance scenario.

Never use a lower status as evidence for a higher one.
