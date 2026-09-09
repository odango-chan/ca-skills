# ConnectionAgent Skills

Official Skill source for ConnectionAgent.

This repository contains model-facing Skill descriptions, Skill-local assurance source, qualification cases, routing-policy/model-context packages, and authoring guidance.

Chinese version: [`README.zh-CN.md`](README.zh-CN.md)

## Repository layout

```text
connectionagent-skills/
├── skills/                  # official Skill and routing-policy source
├── docs/                    # authoring guides
├── scripts/verify.py        # repository verification entrypoint
└── .agents/skills/
    └── create-connectionagent-skill/
```

An executable Skill normally uses:

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/    # optional
├── schemas/       # optional
└── scripts/       # optional governed local compute
```

A routing-policy or model-context package may contain only `SKILL.md` and optional model-facing references or schemas.

## Authoring

Start with:

- English: [`docs/authoring.md`](docs/authoring.md)
- 中文：[`docs/authoring.zh-CN.md`](docs/authoring.zh-CN.md)

The repository-local authoring assistant is:

```text
.agents/skills/create-connectionagent-skill/
```

Its `SKILL.md` contains the authoring workflow. Detailed YAML, Script, and Case syntax is kept in `references/authoring-syntax.md` and checked against the current `connectionagent-skill-platform` schemas/compiler.

A few package rules are worth keeping in mind:

- `SKILL.md` is the package-root model-facing entry point;
- executable Skills use the complete `assurance/` trio;
- there is no standalone `evidence.yaml`;
- each qualification case is one `cases/<case>/case.yaml`;
- package-root `README.md`, `MIGRATION.md`, and `examples/` are not part of the Skill package format;
- model-facing Markdown under `skills/` is written in English;
- deployment endpoints, Provider bindings, Observation bindings, and Runtime state do not belong in Skill source.

## Source and execution

`skills/` is the official source catalog. Skill Platform discovers and compiles this source into immutable Artifact/Variant form before Runtime execution.

Runtime does not execute the working tree directly. A change to this repository therefore does not alter an already admitted Artifact or an existing Run.

Custom ZIP, directory, or Git imports belong to the Platform workspace/import flow. They do not write into `skills/` or become official source merely by being imported.

The main ownership split is:

| Repository | Responsibility |
| --- | --- |
| `connectionagent-skills` | official Skill source and authoring guidance |
| `connectionagent-skill-platform` | machine schemas, compiler, build and qualification |
| `connectionagent-agent` | goal interpretation, routing and planning |
| `connectionagent-runtime` | admission, binding and deterministic execution |
| `connectionagent-sandbox` | controlled environment and fault injection |
| `connectionagent-benchmarks` | independent evaluation cases and verdicts |

## Routing policy

`skills/5gc-intent` is a model-visible routing-policy package. It has no `assurance/` and is not executed as a preliminary Runtime Procedure.

Agent routing selects from the admitted Skill set; Runtime still performs the final Artifact/Variant admission and execution.

## Current packages

| Package | Role | Status |
| --- | --- | --- |
| `5gc-intent` | routing policy / model context | non-executable |
| `5gc-file-transfer` | product Skill | local source/compile/case/Q4 preflight complete; production deployment admission pending |
| `wifi-file-transfer` | product Skill | local source/compile/case/Q4 preflight complete; production deployment admission pending |
| `ue-registration` | reference Skill | production-qualified reference |
| `ensure-session-qos` | reference Skill | production-qualified reference |
| `download-object-by-deadline` | reference Skill | production-qualified reference |
| `query-weather-for-ue` | reference Skill | production-qualified reference |

The remaining production work for the file-transfer Skills is deployment and binding closure rather than Skill-language work.

## Authoring model freeze

The current Skill language and assurance authoring model are frozen. New Skills and normal maintenance should use the existing language rather than extend it.

A syntax change requires a demonstrated product-level expressiveness gap that cannot be solved in ProviderBinding, ObservationBinding, Runtime, qualification, Sandbox, or integration. Any approved language revision must update the owning Platform schemas/compiler and the affected official Skills, Cases, and authoring guidance together, then pass `make verify` before a new baseline is established.

## Verification

Run the repository gate with:

```bash
make verify
```

For a focused compile of one executable Skill:

```bash
python3 -B scripts/verify.py --compile skills/<name>
```

Set `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` when `connectionagent-skill-platform` is not available as sibling `../connectionagent-skill-platform`.

Compile or local preflight success is not, by itself, production qualification.
