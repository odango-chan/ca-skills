---
name: create-connectionagent-skill
description: Use when authoring or refreshing an official ConnectionAgent Skill package in ca-skills. Follow the current source baseline, package boundaries, references model, assurance semantics and compiler compatibility status.
---

# Create or update an official ConnectionAgent Skill

## Authority

- Official Skill source and authoring semantics: this repository.
- Current 5GC examples: `skills/establish-pdu-session/` and `skills/establish-pdu-session-mas/`.
- Current source/compatibility record: `docs/current-5gc-skill-baseline.md`.
- Canonical source-language and semantic-token contract: `docs/skill-language-spec.md`.
- Machine-readable semantic-token and symbol/reference catalog: `spec/skill-language-tokens.yaml`.
- Project root and read-only Library / generated Output behavior: `docs/project-layout.md`.
- Canonical source-language and semantic-token contract: `docs/skill-language-spec.md`.
- Procedure node semantics: `docs/authoring-model.md`.
- Practical syntax notes: `references/authoring-syntax.md`.
- Legacy machine schemas/compiler: `ca-skill-toolchain`, only for constructs represented by its current schemas.
- Target stateless multi-Skill compiler: `ca-skill-compiler`; design accepted, implementation not started.

## Workflow

1. Decide whether the asset is an executable Skill, a model-context package, or an externally owned Capability/Tool contract.
2. Read the current 5GC baseline before using examples. Other historical packages under `skills/` are out of current scope and are not syntax authorities.
3. Keep the English `SKILL.md` model-facing: business goal, applicability, profile, required facts, invalid inferences, completion and uncertainty. Do not expose Host/Runtime/Provider/Fabric/adapter/deployment internals.
4. For an executable Skill, maintain the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio.
5. Keep the deterministic workflow in `procedure.yaml`; do not duplicate its graph in prose. Respect ordered node preconditions/postconditions and native reconciliation semantics where used by the current source baseline.
6. Use one `cases/<case>/case.yaml` per semantic obligation. Never claim a Case has executed or qualified without owner-run evidence.
7. Put optional model knowledge in flat `references/*.md` files and list exact paths in `SKILL.md`. Do not use `preload/` or `on-demand/` directory conventions.
8. Use `scripts/` only for governed deterministic local computation. Never put network or Provider I/O in Skill Scripts.
9. Resolve external Tool contracts through read-only project `lib/` imports. Never invent a ToolCatalog from a design draft or infer implementation readiness from a contract snapshot.
10. Before claiming compiler compatibility, verify that the active compiler supports every source construct and every imported reference. The legacy Toolchain does not support the node-level `preconditions/postconditions` used by the current conventional PDU Session Skill.

## Validation language

Use precise statuses:

- `SOURCE_SYNCED`: source files are present and provenance is recorded.
- `STATIC_SOURCE_CHECKED`: only explicit structural checks were run.
- `COMPILE_PASS`: the actual target compiler completed successfully.
- `LINK_PASS`: all declared local/imported references resolved.
- `RUNTIME_PASS`: the admitted Runtime path executed successfully.
- `QUALIFIED`: the required qualification owner gate passed.
- `LIVE_PASS`: the real target environment completed its acceptance scenario.

Never use a lower status as evidence for a higher one.
