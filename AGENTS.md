# AGENTS.md

## Repository purpose

This repository owns official ConnectionAgent Skill source assets and model-visible routing policy assets. Keep executable Platform/Runtime logic out of this repository.

## Asset rules

- A Skill or routing-policy package is self-contained under `skills/<package>/`.
- `SKILL.md` is the single package-root human/model entry point.
- Model-facing Markdown under `skills/` is authored in English.
- Governed executable Skills use the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio.
- Machine-readable assurance, procedure, case, schema, and script metadata must stay consistent with contracts owned by `connectionagent-skill-platform` and `connectionagent-runtime`.
- Vendor `cases/` validate the Vendor Skill itself. Customer `SkillProfileQualificationCase` assets are not Vendor cases.
- Do not keep package-root `README.md`, `MIGRATION.md`, or `examples/` directories in official packages.
- Do not copy Runtime state machines, Provider/Observation bindings, Provider implementation mappings, Sandbox simulation worlds, Benchmark scoring logic, or Web behavior into model context.
- Keep `references/preload/` rare and domain-specific. `references/on-demand/` may add Skill-local business/domain semantics, but must not become a second architecture manual.

## Cross-repository ownership

- Skill compiler, schemas, ProcedurePatch, Artifact/Variant and Qualification orchestration: `connectionagent-skill-platform`.
- Runtime admission, reliable execution, Evidence Gate, ObservationBinding, ProviderBinding and Reconcile: `connectionagent-runtime`.
- Goal interpretation, routing execution, LLM/model loop and Host behavior: `connectionagent-agent`.
- Simulation worlds, fault injection and ground truth: `connectionagent-sandbox`.
- Benchmark verdict/certification: `connectionagent-benchmark` / `connectionagent-benchmarks`.
- UI: `connectionagent-web`.

## Change rule

The Skill language and assurance authoring model are frozen unless a concrete product scenario demonstrates an expressiveness gap. Prefer fixing consumers, deployment bindings, qualification, or integration before changing Skill syntax.
