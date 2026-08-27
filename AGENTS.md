# AGENTS.md

## Repository purpose

This repository owns official ConnectionAgent Skill assets. Keep executable platform/runtime logic out of this repository.

## Asset rules

- A Skill is self-contained under `skills/<skill-name>/`.
- `SKILL.md` remains the human/model entry point.
- Machine-readable assurance, procedure, case and script metadata must stay consistent with the machine contracts owned by `connectionagent-skill-platform`.
- Vendor `cases/` validate the Vendor Skill itself. Customer `SkillProfileQualificationCase` assets are not Vendor cases.
- Do not copy Runtime state machines, Provider implementations, Sandbox simulation worlds or Web logic into a Skill.

## Cross-repository ownership

- Skill compiler, schemas, ProcedurePatch and SkillProfile semantics: `connectionagent-skill-platform`.
- Reliable execution, Session/Event, Evidence and Reconcile: `connectionagent-runtime`.
- LLM/model/Agent loop: `connectionagent-agent`.
- Simulation worlds and fault injection: `connectionagent-sandbox`.
- UI: `connectionagent-web`.

## Migration

During migration from `connectionagent-skill-platform`, preserve Skill content first. Refactoring should be a separate, reviewable step unless required to make repository ownership explicit.
