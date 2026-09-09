---
name: create-connectionagent-skill
description: Use when the user asks to design, create, or structurally complete an official ConnectionAgent Skill source package in this repository. Follow the repository authoring guide, current Skill Platform machine schemas, and adjacent official packages; run source verification and focused compile checks without claiming production qualification.
---

# Create ConnectionAgent Skill

Create or structurally complete official ConnectionAgent Skill source in `connectionagent-skills`.

Official source lives only under `skills/<name>/`. This developer workflow is an authoring assistant, not an official business Skill and not a second language specification.

## Authority

Read, in order:

1. repository `AGENTS.md`;
2. `docs/authoring.md`;
3. current machine schemas/compiler behavior in `connectionagent-skill-platform`;
4. one or two adjacent official packages with similar semantics.

If prose conflicts with the current Platform machine schema/compiler, the machine contract wins.

## Workflow

1. Classify the requested asset before creating files:
   - executable product/domain Skill;
   - model-context or routing-policy package;
   - lower-level Runtime Capability.
2. Treat routing as Agent-owned behavior. A routing-policy package is model context, not an executable preliminary Skill and does not mint an `ExecutionTarget` for another Skill.
3. Keep `SKILL.md` thin and model-facing. Put only business/domain semantics, normalization/disambiguation, structured expectations, and boundaries the model must not guess or bypass.
4. For executable Skills, use the complete `assurance/contract.yaml`, `assurance/procedure.yaml`, and `assurance/predicates.yaml` extension. Do not create a standalone `evidence.yaml`.
5. Use the current object-form Procedure vNext only. Current node vocabulary is `call`, `verify`, `script`, `procedure`, `for`, `reconcile`, and `terminal`; use the current `with` / `on` binding model. Do not revive legacy ProcedureSet/action/terminal scalar forms or hidden sequencing DSLs.
6. In Predicate source, declare typed observations plus deterministic evaluators. Use CEL for small auditable assertions and governed Script for truly complex deterministic judgment. Evidence acquisition happens before evaluation; Scripts must not call Providers, MCP servers, networks, or hidden workflows.
7. Write qualification cases only as `cases/<name>/case.yaml`. Do not recreate split case files or package-root `examples/`.
8. Reuse governed Capability/Predicate/schema contracts. Skill-local schemas are for private types; Skill-local Scripts are governed deterministic local computation, not Provider I/O.
9. Run `make verify`, then use the focused compile helper when a Platform checkout is available.
10. Report source/compile/SQ results precisely. Compile success is not production qualification.

## Focused compile

```bash
bash .agents/skills/create-connectionagent-skill/scripts/compile-package.sh \
  skills/<name>
```

Set `CONNECTIONAGENT_SKILL_PLATFORM=/path/to/connectionagent-skill-platform` when the Platform checkout is not a sibling of this repository.

Exit codes from the helper preserve the Platform compiler result; environment/configuration problems use `2`, and helper/build failures use `3`.

## Delivery

Report:

- files added/changed/removed;
- semantic decisions and reused contracts;
- exact verification/compile/qualification commands actually run;
- any unresolved Platform, Runtime, Provider, Sandbox, or deployment dependency.

Do not copy the full Procedure/Predicate grammar into this workflow. The reusable authoring explanation belongs in `docs/authoring.md`; normative syntax belongs to Skill Platform.

For package-granularity guidance, see `references/skill-granularity.md`.
