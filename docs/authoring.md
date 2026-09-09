# Authoring ConnectionAgent Skills

This document is the human-facing entry point for creating and reviewing official ConnectionAgent Skill source.

It is intentionally **not** a second language specification. `connectionagent-skill-platform` owns the normative machine schemas, compiler validation, Artifact/Variant production, and Qualification semantics. If this guide ever conflicts with the current Platform schema or compiler, the Platform machine contract wins.

## 1. Decide what you are authoring

Before creating a package, classify the asset.

### Executable Skill

Create an executable Skill when the model needs a product/domain-level capability whose execution must be governed by deterministic assurance.

Examples include registration, QoS assurance, deadline-aware transfer, and weather query workflows.

An executable Skill normally contains `SKILL.md` plus the complete `assurance/` extension.

### Model-context or routing-policy package

A model-context package provides business semantics or routing policy to the Agent but is not executed as a preliminary Runtime Procedure.

`skills/5gc-intent` is the current example. Routing itself is Agent-owned behavior. Do not model routing as “Skill A executes and returns an `ExecutionTarget` for Skill B”.

### Capability

A low-level provider action is normally a Runtime Capability, not a standalone Skill. Create a Skill only when there is meaningful product/domain semantics, planning context, or assurance composition above the primitive action.

See `.agents/skills/create-connectionagent-skill/references/skill-granularity.md` for the practical boundary.

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
│   └── <case>/
│       └── case.yaml
├── references/
├── schemas/
└── scripts/
```

Only create optional directories when they contain real assets.

Current package rules:

- `assurance/` is all-or-nothing at the package-layout level;
- there is no standalone `evidence.yaml`;
- qualification cases use one `cases/<case>/case.yaml` file;
- package-root `examples/`, `README.md`, and `MIGRATION.md` are not part of the canonical Skill shape;
- explanatory examples belong under `references/samples/`;
- model-facing Markdown under `skills/` is authored in English.

## 3. Keep `SKILL.md` thin

`SKILL.md` is the single package-root model-facing entry point. Keep only information that materially affects model decisions, such as:

- when the Skill or policy applies;
- business/domain meaning;
- input normalization and disambiguation;
- model-facing structured input/output expectations;
- constraints the model must not guess or bypass.

Do not copy Runtime or Platform mechanics into model context. In particular, avoid Provider implementation mappings, deployment endpoints, ObservationBinding details, Runtime state machines, qualification status, Benchmark scoring rules, migration history, and architecture tutorials.

## 4. Assurance responsibilities

For an executable Skill, the three files under `assurance/` have separate responsibilities:

- `contract.yaml` declares the Skill-local execution/assurance contract and references governed capabilities or schemas;
- `procedure.yaml` declares deterministic workflow structure;
- `predicates.yaml` declares typed observations and deterministic assertions over materialized evidence.

Do not duplicate their full field grammar here. Before authoring or changing these files, inspect the current schemas and compiler behavior in `connectionagent-skill-platform`.

The current Procedure model is the object-form Procedure vNext. Its node vocabulary is `call`, `verify`, `script`, `procedure`, `for`, `reconcile`, and `terminal`, with data/control bindings expressed through the current `with` / `on` model. `for` is the collection construct. Skill source does not carry graph coordinates or deployment Provider bindings.

Procedure selection conditions use the current applicability contract; they are not Predicate definitions.

## 5. Observation, Evidence Gate, and Predicate

Observation acquisition and Predicate judgment are separate concerns.

At Runtime, required observations are materialized first. The Evidence Gate checks presence, freshness, and validity before the evaluator runs. Missing, stale, unavailable, or invalid required evidence produces `UNKNOWN` without pretending that the Predicate evaluated to `FAIL`.

Use:

- CEL for small, auditable deterministic assertions such as comparisons, boolean composition, and straightforward collection checks;
- a governed Predicate Script for genuinely complex deterministic domain judgment.

Predicate Scripts operate only on already-materialized inputs/evidence. They must not call Providers, MCP servers, the network, or hidden workflows. Procedure Scripts and Predicate Scripts share the governed local-compute execution base, but their semantics remain different: a Procedure Script computes workflow data; a Predicate Script judges supplied evidence.

## 6. Qualification cases

Skill qualification cases are source-package assets, not Benchmark definitions.

Write exactly one `case.yaml` per case directory. Cover the semantic classes implied by the procedure and profile, including normal success, governed failure, `UNKNOWN` / reconcile paths, budget handling, and independent postcondition verification where applicable.

Do not duplicate cases merely by changing an operation identifier. Do not treat an injected fixture result as proof of the business outcome.

Benchmark cases remain independently authored evaluation assets and must not use the Skill's internal expected path as their oracle.

## 7. Authoring workflow

Use this sequence for a new Skill or a structural change:

1. Read the repository `AGENTS.md` and this guide.
2. Classify the asset as executable Skill, model-context/routing policy, or lower-level Capability.
3. Inspect one or two adjacent official packages with similar semantics.
4. Inspect the current Platform machine schemas and current-stage decisions before writing assurance source.
5. Author the smallest complete source package; do not create placeholder directories or duplicate language documentation.
6. Run repository verification:

   ```bash
   make verify
   ```

7. When doing focused package work, run the Platform compiler through the local authoring helper:

   ```bash
   bash .agents/skills/create-connectionagent-skill/scripts/compile-package.sh \
     skills/<name>
   ```

   The helper uses `CONNECTIONAGENT_SKILL_PLATFORM` when set, otherwise it looks for a sibling `../connectionagent-skill-platform` checkout.

8. Run the required SQ1/SQ2 gates for the target qualification profile and retain the exact source/artifact digest and evidence.

A successful source check or compile does **not** by itself make a Skill production-qualified. Deployment ProviderBinding, Observation closure, immutable Artifact/Variant admission, and environment-owned qualification remain the responsibility of their owning layers.

## 8. Normative authority

Use this precedence when prose and implementation disagree:

1. cross-repository machine-contract/current-stage decisions in `odango-chan/connectionagent`;
2. current machine schemas and compiler validation in `odango-chan/connectionagent-skill-platform`;
3. repository-local package rules in `AGENTS.md`;
4. this authoring guide and examples.

The goal is one language contract with multiple useful entry points, not multiple copies of the language definition.
