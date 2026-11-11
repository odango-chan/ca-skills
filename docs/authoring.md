# Authoring ConnectionAgent Skills

This guide describes the current official source model in `ca-skills`. It is a practical guide, not a duplicate machine grammar.

For the current two 5GC packages and their validation limits, see [Current 5GC Skill baseline](current-5gc-skill-baseline.md). Project root permissions and the `skills/` / `lib/` / `output/` model are defined in [Project Layout](project-layout.md). For Procedure node preparation and verification semantics, see [Authoring model](authoring-model.md).

## 1. Choose the right asset

- **Executable Skill:** owns a business goal and a deterministic assurance source. It uses `SKILL.md` plus the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio and semantic Cases.
- **Model-context or routing package:** provides business semantics to the Agent but does not itself define a Runtime Procedure.
- **Capability / Tool contract:** owns one governed operation and its input/output/effect contract. Do not wrap a primitive operation in a Skill merely to rename it.

## 2. Package shape

An executable Skill normally has:

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/       # optional flat Markdown
├── schemas/           # optional Skill-owned payload schemas
└── scripts/           # optional governed local compute
```

Do not create empty directories, package-root `README.md` / `MIGRATION.md`, `examples/`, or maintainer `design/` folders.

## 3. Write the model-facing Skill

Keep `SKILL.md` focused on:

- when the Skill applies and the supported profile;
- the business goal and required facts;
- normalization and disambiguation;
- inferences the model must not make;
- business completion, failure and uncertainty semantics.

Do not copy the deterministic Procedure graph into prose. Do not put Host/Runtime internals, adapter names, Provider/Fabric topology, deployment endpoints, credentials, or transport implementation details into model-facing context. Keep maintainer integration notes under `docs/`.

A model response, action acknowledgement or transport success is not a substitute for independently established business facts.

## 4. References

Use a flat `references/*.md` directory. The Skill lists exact paths and explains what each file is useful for. Reference loading is optional and model-selected; do not create `preload/` or `on-demand/` directories or infer loading policy from directory names.

References are supplemental knowledge, not live evidence, authorization, or a second execution graph.

## 5. Assurance and Procedure

For an executable Skill, `assurance/` is all-or-nothing:

- `contract.yaml` defines the Skill goal, resource boundary, preconditions and final postconditions;
- `procedure.yaml` defines deterministic workflow, data bindings and outcome routing;
- `predicates.yaml` defines evidence requirements and deterministic judgments.

The current 5GC source also uses node-level `preconditions` and `postconditions`. Their ordering and outcome semantics are described in [Authoring model](authoring-model.md). Do not remove them to satisfy the legacy Toolchain schema: its current `procedure-source.schema.yaml` does not model these fields.

## 6. Cases

Each Case is one `cases/<case>/case.yaml`. Cases express semantic obligations. A source Case, schema check, or hand-authored expected result is not proof that a Runtime or qualification test has executed.

The conventional PDU Session package contains 36 semantic obligations; its `cases/README.md` explicitly states that they are not executable Runtime fixtures yet.

## 7. Scripts and schemas

Skill-local Python scripts are governed deterministic local computation. They may normalize, select, derive or evaluate supplied data. They must not call Providers, MCP servers, networks, shell workflows, clocks, databases or credentials.

Keep Skill-owned schemas under `schemas/`. Do not infer constraints from arbitrary Python function bodies. The future Compiler may generate only what can be derived from explicit declarations; existing schemas remain authoritative for constraints that cannot be inferred.

## 8. Imported Tool contracts

External Tool contracts belong under project `lib/` as imported read-only snapshots. Do not hand-edit them or copy them into every Skill.

The current `lib/tools/createdsession.tool.yaml` resolves the conventional Skill's 12 declared Capabilities. The MAS Skill's 16 `ca.pdu_session.*` Capabilities remain unresolved; do not invent an approved ToolCatalog from its design-only contract draft.

## 9. Compiler and verification status

The legacy `ca-skill-toolchain` remains the machine authority for packages that fit its existing v1alpha1 schemas. It does not currently support the node-level Procedure `preconditions/postconditions` used by the conventional PDU Session source.

The stateless `ca-skill-compiler` v0 design is accepted, but implementation is not started. Until it supports the current source constructs and Library resolution, the current 5GC source baseline must be reported as **source present / compiler-link validation NOT_RUN or BLOCKED**. Never silently lower, delete or reinterpret unsupported semantics to manufacture a PASS.

The existing commands are:

```bash
make verify
python3 -B scripts/verify.py --compile skills/<name>
```

They still delegate to the legacy Toolchain; a result for a legacy-compatible package is not evidence that the new 5GC source baseline has compiled. Compiler build success, when available, will still not mean Runtime qualification or live 5GC acceptance.
