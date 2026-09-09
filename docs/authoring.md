# Authoring ConnectionAgent Skills

This document is the human-facing entry point for creating and reviewing official ConnectionAgent Skill source.

The repository-local authoring assistant at `.agents/skills/create-connectionagent-skill/SKILL.md` contains the workflow and core invariants. Detailed practical syntax lives in `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md` and should be loaded only when assurance, Script, or Case source is being authored. `connectionagent-skill-platform` remains the normative machine-language authority.

## 1. Decide what you are authoring

Before creating a package, classify the asset.

### Executable Skill

Create an executable Skill when the model needs a product/domain-level capability whose execution must be governed by deterministic assurance.

An executable Skill normally contains `SKILL.md` plus the complete `assurance/` extension.

### Model-context or routing-policy package

A model-context package provides business semantics or routing policy to the Agent but is not executed as a preliminary Runtime Procedure.

`skills/5gc-intent` is the current example. Routing itself is Agent-owned behavior. Do not model routing as “Skill A executes and returns an `ExecutionTarget` for Skill B”.

### Capability

A low-level Provider action is normally a Runtime Capability, not a standalone Skill. Create a Skill only when there is meaningful product/domain semantics, planning context, or assurance composition above the primitive action.

For the practical granularity boundary, see `.agents/skills/create-connectionagent-skill/references/skill-granularity.md`.

## 2. Canonical package shapes

A model-context-only package may be as small as:

```text
skills/<name>/
├── SKILL.md
├── references/
└── schemas/
```

A governed executable Skill adds the complete assurance extension:

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/
├── schemas/
└── scripts/
```

Only create optional directories when they contain real assets.

Current package rules:

- `assurance/` is all-or-nothing;
- there is no standalone `evidence.yaml`;
- qualification cases use one `cases/<case>/case.yaml` file;
- package-root `examples/`, `README.md`, and `MIGRATION.md` are not canonical;
- explanatory examples belong under `references/samples/`;
- model-facing Markdown under `skills/` is authored in English.

## 3. Keep `SKILL.md` thin

`SKILL.md` is the single package-root model-facing entry point. Keep only information that materially affects model decisions:

- when the Skill or policy applies;
- business/domain meaning;
- input normalization and disambiguation;
- model-facing structured input/output expectations;
- constraints the model must not guess or bypass.

Do not copy Runtime or Platform mechanics into model context. Avoid Provider implementation mappings, deployment endpoints, ObservationBinding details, Runtime state machines, qualification status, Benchmark scoring rules, migration history, and architecture tutorials.

## 4. Current authoring syntax authority

Use these Platform schemas for official source authoring:

| Source asset | Platform schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| governed Script metadata | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

For current `assurance/procedure.yaml`, author from `procedure-source.schema.yaml`. The current source model is object-form Procedure vNext (`procedures -> start/nodes`), not the older array/type/action authoring shape that can still appear in historical or internal schemas.

The practical syntax reference is `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md`. Keep detailed YAML/Python examples there rather than duplicating them in the main authoring Skill or this guide.

## 5. Observation, Evidence Gate, and Predicate

Observation acquisition and Predicate judgment are separate concerns.

At Runtime, required observations are materialized first. The Evidence Gate checks presence, freshness, and validity before the evaluator runs. Missing, stale, unavailable, or invalid required evidence produces `UNKNOWN` without pretending that the Predicate evaluated to `FAIL`.

Use CEL for small auditable deterministic assertions and a governed Predicate Script for genuinely complex deterministic domain judgment. Predicate Scripts operate only on already-materialized inputs/evidence and must not call Providers, MCP servers, the network, or hidden workflows.

## 6. Qualification cases

Skill qualification cases are source-package assets, not Benchmark definitions.

Write exactly one `case.yaml` per case directory. Coverage follows semantic obligations, not a fixed Case count. Cover normal success, relevant failure/denial, `UNKNOWN`/reconcile paths, budget handling, and independent postcondition verification where the Procedure/Profile makes them meaningful.

Do not duplicate cases merely by changing an operation identifier, and do not treat an injected fixture result as proof of the business outcome.

## 7. Authoring workflow

Use this sequence for a new Skill or structural change:

1. Read repository `AGENTS.md` and this guide.
2. Classify the asset as executable Skill, model-context/routing policy, or lower-level Capability.
3. Inspect one or two adjacent official packages with similar semantics.
4. Reuse Registry Capability/Predicate/schema contracts before creating local ones.
5. Use `.agents/skills/create-connectionagent-skill/SKILL.md` for the workflow and core invariants.
6. Load `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md` only when assurance, Script, or Case source must be written or changed.
7. For one executable package, run focused compile:

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

   Set `CONNECTIONAGENT_SKILL_PLATFORM_ROOT=/path/to/connectionagent-skill-platform` when the Platform checkout is not the sibling `../connectionagent-skill-platform`.

8. Before delivery, run the repository gate:

   ```bash
   make verify
   ```

9. Run any additional SQ/production admission work required by the target profile in the owning Platform/Runtime/Sandbox environment.

A successful source check or focused compile does **not** make a Skill production-qualified.

## 8. Normative authority

Use this precedence when prose and implementation disagree:

1. cross-repository machine-contract/current-stage decisions in `odango-chan/connectionagent`;
2. current machine schemas and compiler validation in `odango-chan/connectionagent-skill-platform`;
3. repository-local package rules in `AGENTS.md`;
4. the repository-local authoring workflow and references.

The goal is one language contract with useful progressive authoring views, not multiple independently maintained language definitions.
