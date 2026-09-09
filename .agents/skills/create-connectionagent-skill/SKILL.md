---
name: create-connectionagent-skill
description: Use when the user asks to design, create, or structurally complete an official ConnectionAgent Skill source package in this repository. Classify the asset, follow the current authoring workflow, load detailed syntax references only when needed, validate with Skill Platform, and report qualification status precisely.
---

# Create ConnectionAgent Skill

Create or structurally complete official ConnectionAgent Skill source in `connectionagent-skills`.

Official source lives only under `skills/<name>/`. This developer workflow is an authoring assistant, not an official business Skill and not a second machine-language authority.

## Authority

Read repository `AGENTS.md` first.

Use this precedence:

1. current cross-repository machine-contract/stage decisions;
2. current Skill Platform schemas and compiler behavior;
3. repository-local `AGENTS.md` rules;
4. this workflow and its references.

For official source authoring, the important Platform schemas are:

- `assurance/contract.yaml` -> `schemas/v1alpha1/skill-contract.schema.yaml`;
- `assurance/procedure.yaml` -> `schemas/v1alpha1/procedure-source.schema.yaml`;
- `assurance/predicates.yaml` -> `schemas/v1alpha1/predicate-set.schema.yaml`;
- `cases/<case>/case.yaml` -> `schemas/v1alpha1/skill-test-case.schema.yaml`;
- governed Script metadata -> `schemas/v1alpha1/script-tool-metadata.schema.yaml`.

For `procedure.yaml`, author from `procedure-source.schema.yaml`. Do not revive older array/type/action source forms.

## Classify before authoring

Choose exactly one primary asset class:

- **Executable Skill** — product/domain goal with deterministic assurance composition;
- **Model-context / routing-policy package** — model-visible semantics only, with no preliminary Runtime Procedure;
- **Runtime Capability** — low-level Provider action; do not create a Skill merely to wrap one primitive call.

Routing is Agent-owned. Do not model routing as one Skill executing to mint authority for another Skill.

When this boundary is unclear, read `references/skill-granularity.md` before creating files.

## Canonical package rules

For an executable Skill:

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/       # optional
├── schemas/          # optional
└── scripts/          # optional governed local compute
```

Keep these rules invariant:

- `assurance/` is all-or-nothing;
- no standalone `evidence.yaml`;
- one `case.yaml` per qualification Case directory;
- no package-root `README.md`, `MIGRATION.md`, or `examples/`;
- no empty placeholder directories;
- model-facing Markdown under `skills/` is English;
- Provider/deployment bindings and Runtime state do not belong in Skill source.

## Keep the package `SKILL.md` thin

The package `SKILL.md` is the single model-facing entry point. Keep only information that materially changes model decisions:

- when the Skill applies;
- business/domain meaning;
- normalization and disambiguation;
- model-facing structured expectations;
- boundaries the model must not guess or bypass.

Do not copy full Procedure graphs, Provider mappings, deployment endpoints, Runtime state machines, qualification status, Benchmark scoring, architecture tutorials, or migration history into model context.

## Load detailed references only when needed

Use progressive disclosure instead of carrying all syntax in this file.

Read `references/authoring-syntax.md` when creating or changing any of these assets:

- `assurance/contract.yaml`;
- `assurance/procedure.yaml`;
- `assurance/predicates.yaml`;
- governed `scripts/*.py`;
- `cases/<case>/case.yaml`.

That reference contains the current practical syntax, bindings, node forms, Predicate/Evidence rules, Script metadata, Case envelope, and links to official examples.

Do not load it for a simple model-context/routing-policy edit that only changes `SKILL.md` or model references.

## Core authoring invariants

Apply these even before opening the detailed syntax reference:

- reuse governed Registry Capability/Predicate/schema contracts before creating local ones;
- Procedure source uses current object-form vNext (`procedures -> start/nodes`);
- use governed outcomes and explicit `on` routing;
- mutation `OUTCOME_UNKNOWN` preserves uncertainty and must reconcile before retry/continuation;
- `applicability.when` is Procedure selection, not Runtime Predicate evaluation;
- Observation acquisition happens before Predicate evaluation;
- missing/stale/unavailable required evidence becomes `UNKNOWN` through the Evidence Gate, not business `FAIL`;
- CEL is for small auditable deterministic assertions; governed Script is for complex deterministic local judgment;
- Predicate Scripts must not call Providers, MCP servers, networks, or acquire additional evidence;
- SkillTestCase is not BenchmarkCase;
- Case coverage follows semantic obligations, not a fixed Case count.

## Workflow

1. Read repository `AGENTS.md`.
2. Classify the request as executable Skill, model-context/routing policy, or Runtime Capability.
3. Inspect one or two adjacent official Skills with similar semantics.
4. Reuse existing governed contracts before introducing new local assets.
5. Read `references/authoring-syntax.md` only if assurance, Script, or Case source must be authored or changed.
6. Write the smallest complete package; do not add speculative files or duplicate language documentation.
7. For one executable package, run focused compile:

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

8. Before delivery, run the repository source/preflight gate:

   ```bash
   make verify
   ```

9. Run any additional SQ/production admission work required by the owning Platform/Runtime/Sandbox environment.
10. Report exactly what ran and what did not run.

`verify.py` uses `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` when set; otherwise it expects sibling `../connectionagent-skill-platform`.

A focused compile or green source gate is not production qualification.

## Do not create parallel contracts

Do not add:

- standalone `evidence.yaml`;
- package-root `examples/`;
- per-Skill root validators such as `scripts/validate_<skill>.py`;
- another compile helper under this authoring workflow;
- Provider/deployment mappings in model context;
- graph coordinates/layout metadata in Skill source;
- `ExecutionTarget.v1`, `RunPlanSnapshot.v1`, `RunPlanRevision.v1`, or generic `PlanDelta.v1` as new cross-repository contracts.

If a concrete scenario appears impossible, first determine whether the gap is actually in ProviderBinding, ObservationBinding, Runtime, qualification, or integration before changing the frozen Skill language.

## Delivery

Report:

- files added/changed/removed;
- semantic decisions and reused contracts;
- exact verification/compile/qualification commands actually run;
- unresolved Platform, Runtime, Provider, Sandbox, or deployment dependencies.

For detailed authoring syntax, read `references/authoring-syntax.md`. For Skill-vs-Capability granularity, read `references/skill-granularity.md`. For the human-oriented repository guide, see `docs/authoring.md`.
