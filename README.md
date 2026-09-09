# ConnectionAgent Skills

`connectionagent-skills` is the source-of-truth repository for official ConnectionAgent **Skill source assets** and model-visible routing policy assets.

The repository intentionally stays small: it defines what a Skill means and, for governed executable Skills, the Skill-local assurance source required by the shared Platform/Runtime contracts. It does not duplicate execution-engine architecture.

## Repository boundary

This repository owns:

- `SKILL.md` model-visible business/domain semantics;
- optional Skill-local `assurance/` source;
- Skill Qualification `cases/` that belong to the source package;
- Skill-local `schemas/`, `scripts/`, and model references;
- official routing-policy/model-context packages such as `5gc-intent`;
- the human-facing authoring guide and repository-local authoring workflow.

This repository does **not** own:

- normative machine grammar, compiler, ProcedurePatch, Artifact/Variant production, or Qualification orchestration — `connectionagent-skill-platform`;
- Agent loop, goal interpretation, routing execution, or model adapters — `connectionagent-agent`;
- Runtime admission, ProviderBinding, ObservationBinding, Procedure execution, Evidence Gate, Predicate execution, or Reconcile — `connectionagent-runtime`;
- environment simulation, fault injection, or ground truth — `connectionagent-sandbox`;
- Benchmark verdicts/certification — `connectionagent-benchmark` / `connectionagent-benchmarks`;
- product UI — `connectionagent-web`.

## Package model

A model-context-only package may contain:

```text
skills/<package>/
├── SKILL.md
├── references/
└── schemas/
```

A governed executable Skill adds the Execution Assurance Extension:

```text
skills/<package>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
├── references/
├── schemas/
└── scripts/
```

`assurance/` is all-or-nothing at the package-layout level. There is intentionally no standalone `evidence.yaml` in the current model.

## Authoring rules

`SKILL.md` is the single package-root human/model entry point. Keep it thin and include only semantics that materially affect model decisions:

- when the Skill or policy applies;
- business/domain meaning;
- normalization and disambiguation rules;
- structured model-facing input/output expectations;
- boundaries the model must not guess or bypass.

Do not copy Runtime or Platform mechanics into model context. In particular, Skill packages should not carry migration histories, Provider implementation mappings, deployment endpoints, ObservationBinding details, Runtime state machines, Benchmark scoring rules, or architecture tutorials.

`references/preload/` is reserved for small domain semantics that must influence essentially every invocation. `references/on-demand/` is for additional Skill-local business/domain detail that may matter only in specific cases. Both are model-context assets and should remain concise. Model-facing Markdown inside `skills/` is authored in English.

Package-root `README.md`, `MIGRATION.md`, and `examples/` are intentionally not part of the canonical package shape. Historical migration notes belong in Git history or cross-repository engineering documentation. Executable qualification fixtures belong in `cases/<case>/case.yaml`; explanatory samples belong in `references/samples/`.

## Authoring entry point

Author guides:

- English: [`docs/authoring.md`](docs/authoring.md)
- 中文：[`docs/authoring.zh-CN.md`](docs/authoring.zh-CN.md)

The repository-local authoring assistant lives at:

```text
.agents/skills/create-connectionagent-skill/
```

Its `SKILL.md` contains the workflow and loading rules. Detailed source syntax is kept under its `references/` directory and validated by the current Skill Platform schemas/compiler.

Authority is split as follows:

```text
connectionagent-skills
  = authoring guidance + official source

connectionagent-skill-platform
  = normative machine schemas + compiler + qualification
```

## Routing policy vs executable Skill

Routing is Agent-owned behavior.

`skills/5gc-intent` is a model-visible routing-policy package for generic 5GC intent. It has no `assurance/` and is not executed as a preliminary Runtime Procedure.

Current routing/execution shape:

```text
Goal / intent
  -> RuntimeHost discovery of admitted Skills
  -> Agent routing / selection
  -> agent.routing_result@1
  -> load selected Skill context
  -> plan entrypoint + canonical input
  -> RuntimeHost ProcedureExecutionRequest
  -> Runtime admission + deterministic execution
```

A resolved routing result does not grant authority. Runtime still admits the immutable Artifact/Variant and owns deployment binding and execution.

The current design does not reintroduce `ExecutionTarget.v1`, `RunPlanSnapshot.v1`, `RunPlanRevision.v1`, or generic `PlanDelta.v1` as cross-repository machine contracts.

## Current official packages

| Package | Role | Current status |
| --- | --- | --- |
| `5gc-intent` | Agent routing policy/model context | non-executable policy asset |
| `5gc-file-transfer` | governed product Skill | source/compile/cases/registry/local Sandbox-Q4 PASS; production deployment admission pending |
| `wifi-file-transfer` | governed product Skill | source/compile/cases/registry/local Sandbox-Q4 PASS; production deployment admission pending |
| `ue-registration` | governed reference Skill | production-qualified reference |
| `ensure-session-qos` | governed reference Skill | production-qualified reference |
| `download-object-by-deadline` | governed reference Skill | production-qualified reference |
| `query-weather-for-ue` | governed reference Skill | production-qualified reference |

For the two file-transfer Skills, the remaining production closure is deployment/lifecycle work, not authoring-model work:

```text
immutable Artifact/Variant admission
production ProviderBinding closure
ObservationCatalog / ObservationBinding closure
```

Do not reopen frozen Skill syntax merely to solve those deployment concerns.

## Source discovery

Official Skills are discovered from this repository through `OfficialSkillSource` and then frozen/compiled by Skill Platform. Runtime never executes the live working tree directly. Custom Skill import belongs to the controlled Platform Workspace path and must not write into this repository.

See [`docs/source-discovery-and-import.md`](docs/source-discovery-and-import.md) for the repository-local source boundary.

## Verification

Run:

```bash
make verify
```

The local entrypoint checks repository/package hygiene and delegates compile, Case, planning, and qualification gates to the owning Platform/Runtime/Sandbox implementations. A green source/preflight gate does not by itself promote a Skill to production-qualified.
