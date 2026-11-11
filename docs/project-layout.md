# Skill Package Layout and Source Ownership

This document defines the **Skill package**, not a workspace or package-manager layout. Studio owns its Explorer and project configuration. Compiler consumes a virtual file set and does not require a physical project `lib/` or `output/` directory.

## Canonical Skill package

~~~text
skills/<skill-name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case-name>/
│       └── case.yaml
├── references/       # optional model knowledge
├── schemas/          # Skill-owned public schemas only
└── scripts/          # Skill-owned Python local computation
~~~

`assurance/` is the deterministic source contract. `SKILL.md` is model-facing guidance. Cases are source-level obligations, not Compiler-run tests. References are optional Markdown knowledge, not evidence.

## Schema and Script ownership

- `schemas/` contains only interfaces owned by the Skill, such as its public Request Schema.
- Do not put imported Tool/Host/Observation schemas in an individual Skill package.
- Do not author Script Input Schemas. Procedure `with:` and Predicate Evaluation Context derive Script inputs from Producer contracts.
- Do not author Script Output Schemas. Strict Output `TypedDict` declarations generate read-only JSON Schema in BuildResult.
- Generated output is not written back into the Skill source tree.

## Imported external contracts

Compiler accepts imported contracts in the logical `lib/**` input namespace. This is a BuildRequest path namespace, not a promise that every Studio workspace has a physical `lib/` folder.

- `lib/tools/**`: imported ToolCatalog Operation contracts.
- `lib/host/**`: Host-owned Subject, Facts, Evidence and other context Schemas.
- `lib/observations/**`: Observation-owner payload Schemas.

The source Contract references Owner files explicitly under `spec.context.schemas`. Missing Owner files are reported; do not substitute a deployment Root Routing Profile or infer a Schema from `requiredFacts`.

This repository stores the current approved ToolCatalog snapshot at `lib/tools/createdsession.tool.yaml` for the official PDU example. Its presence does not mean corresponding Tool implementations are deployed or READY.

## Compiler output

Compiler returns `BuildResult.outputFiles` as an in-memory file map. Studio decides how to display the generated projection and whether to export a ZIP or folder. No physical `output/` directory is required by the language or Compiler.

Compiler does not manage workspace folders, imported sources, dependency versions, locks, caches, Git, Upload or MCP. Those are caller/Studio concerns.
