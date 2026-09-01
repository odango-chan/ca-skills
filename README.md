# ConnectionAgent Skills

`connectionagent-skills` is the repository for official ConnectionAgent **Skill source assets**.

This repository owns Skill packages that can be compiled, qualified, and consumed by the Skill Platform. It does not implement the Skill Platform, Agent loop, Runtime, Sandbox, or Web application.

## Repository boundary

This repository owns:

- `SKILL.md`;
- Skill-local `assurance/` assets;
- vendor/qualification `cases/` when they belong to the Skill source package;
- `references/`;
- Skill-local `scripts/` and their metadata;
- Skill examples and documentation.

This repository does not own:

- Skill Compiler / ProcedurePatch apply / SkillProfile resolution -> `connectionagent-skill-platform`;
- LLM / Agent loop / model adapters -> `connectionagent-agent`;
- Procedure execution / Session / Event / Evidence / Reconcile -> `connectionagent-runtime`;
- 5GC simulated world / fault injection -> `connectionagent-sandbox`;
- production UI -> `connectionagent-web`.

## Package layout

```text
skills/
└── <skill-package>/
    ├── SKILL.md
    ├── assurance/
    │   ├── contract.yaml
    │   ├── procedure.yaml
    │   ├── evidence.yaml
    │   └── predicates.yaml
    ├── cases/
    ├── references/
    ├── schemas/
    ├── scripts/
    └── examples/
```

The target assurance model keeps four concerns separate:

```text
procedure.yaml   -> where a Predicate is required

evidence.yaml    -> what typed Observations are required and how they may be acquired

predicates.yaml   -> how the prepared evaluation context is judged

scripts/*.py      -> only genuinely complex deterministic Predicate logic or local computation
```

Target Predicate authoring uses two evaluator forms:

- **CEL** for small, auditable boolean judgement, including collection aggregation;
- **Python** for richer deterministic branching, correlation, semantic conflict handling, and diagnostics.

Missing, stale, invalid, or unavailable required Observations are handled by the Runtime Evidence Gate and produce `UNKNOWN` before normal CEL evaluation. Skill-local Python evaluators remain `local_compute` with denied network access and must not hide Tool dispatch or workflow execution.

The package directory is a repository path. The canonical Skill identity is the schema-valid `name` declared by the package and frozen into the build artifact.

## Migration rule

Official Skills are migrated from `connectionagent-skill-platform/skills/` into this repository using an additive-first process:

1. establish the target Skill source package here;
2. refactor Skill Platform and Runtime contracts to consume the target package model;
3. qualify the independent Skill source against the new contracts;
4. remove superseded official/fixture assets from old locations.

The current gateway-oriented branch is intentionally authored toward the target Predicate/Evidence model rather than preserving the legacy scalar Predicate authoring contract.

## Current gateway-oriented Skills

The repository now includes source packages for:

- `core5g-intent` -> generic `[TASK: 5GC-INTENT]` routing;
- `core5g-file-transfer` -> `[TASK: 5GC-FILE-TRANSFER]` and `[TASK: 5GC-VG-RELEASE]`;
- `wifi-file-transfer` -> `[TASK: WIFI-TRANSFER]`.

Gateway task markers are external protocol identifiers. They do not need to equal the internal Skill name.
