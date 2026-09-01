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
    ├── cases/
    ├── references/
    ├── scripts/
    └── examples/
```

The package directory is a repository path. The canonical Skill identity is the schema-valid `name` declared by the package and frozen into the build artifact.

## Migration rule

Official Skills are migrated from `connectionagent-skill-platform/skills/` into this repository using an additive-first process:

1. establish the equivalent Skill source package here and validate it;
2. make Skill Platform integration/qualification consume the independent Skill source;
3. remove the official Skill from Skill Platform, leaving only the minimum compiler/schema fixtures required by that repository.

## Current gateway-oriented Skills

The repository now includes source packages for:

- `core5g-intent` -> generic `[TASK: 5GC-INTENT]` routing;
- `core5g-file-transfer` -> `[TASK: 5GC-FILE-TRANSFER]` and `[TASK: 5GC-VG-RELEASE]`;
- `wifi-file-transfer` -> `[TASK: WIFI-TRANSFER]`.

Gateway task markers are external protocol identifiers. They do not need to equal the internal Skill name.
