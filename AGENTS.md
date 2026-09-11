# AGENTS.md

## Repository role

`ca-skills` contains official ConnectionAgent Skill source and model-visible routing-policy assets.

Keep Platform, Runtime, Sandbox, Benchmark, Agent-loop, and UI implementation out of this repository.

## Working rules

- Official packages live under `skills/<package>/`.
- `SKILL.md` is the package-root **model-facing** entry point. Keep it thin and focused on domain semantics, normalization, selection/use conditions, and boundaries the model must not guess or bypass.
- Model-facing Markdown under `skills/` is written in English.
- An executable Skill uses the complete `assurance/{contract.yaml,procedure.yaml,predicates.yaml}` trio. Do not add a standalone `evidence.yaml`.
- Qualification cases use one `cases/<case>/case.yaml` per case. Case coverage follows semantic obligations; do not hard-code a required case count in repository scripts.
- Package-root `README.md`, `MIGRATION.md`, and `examples/` are not part of the official package shape.
- `references/preload/` is only for small domain context needed on most invocations. Put optional Skill-local detail under `references/on-demand/`; neither directory should become an architecture manual.
- Skill-local `scripts/` are governed deterministic local-compute assets. Do not hide Provider I/O, network access, credentials, or deployment logic in them.
- Do not place ProviderBinding, ObservationBinding, deployment endpoints, Runtime state machines, Sandbox worlds, Benchmark scoring, or Web behavior in Skill model context.

## Authoring guidance

Human guides:

- English: `docs/authoring.md`
- Chinese: `docs/authoring.zh-CN.md`

Repository-local authoring workflow:

```text
.agents/skills/create-connectionagent-skill/
```

Its `SKILL.md` contains workflow and loading rules. Load `references/authoring-syntax.md` only when editing assurance source, governed Scripts, or Cases. Use `references/skill-granularity.md` when deciding Skill vs routing policy vs Runtime Capability.

Do not duplicate the full Skill grammar in `AGENTS.md`, README, or other prose. The current machine schemas/compiler in `ca-skill-toolchain` are authoritative.

For current official `assurance/procedure.yaml`, author against `schemas/v1alpha1/procedure-source.schema.yaml`, not historical/internal procedure source shapes.

## Source and execution boundary

- `skills/` is the official source catalog.
- Skill Platform freezes/compiles source before Runtime execution; Runtime does not execute the live working tree.
- Custom ZIP/directory/Git imports belong to the Platform workspace/import flow and must not write into `skills/` or silently become official source.
- Routing is Agent-owned. A routing-policy package such as `5gc-intent` is model context, not a preliminary executable Runtime hop.

## Verification

Use the single repository verification entrypoint:

```bash
make verify
```

For one executable package:

```bash
python3 -B scripts/verify.py --compile skills/<name>
```

Do not add per-Skill root validators or another compile helper. Generic source-language validation belongs to Skill Platform; package hygiene belongs in `scripts/verify.py`.

Compile or local preflight success is not production qualification.

## Ownership

- Skill source and authoring guidance: `ca-skills`
- Machine schemas, compiler, Artifact/Variant build, Qualification: `ca-skill-toolchain`
- Goal interpretation, routing, planning/model loop: `ca-agent`
- Admission, Provider/Observation binding, Evidence Gate, deterministic execution, Reconcile: `ca-runtime`
- Environment simulation, fault injection, ground truth: `ca-sandbox`
- Independent evaluation cases and verdicts: `ca-benchmarks`
- Product UI: `ca-console`

## Frozen authoring model

The current Skill language and assurance authoring model are frozen.

Do not change source syntax for convenience, cleanup, provider differences, deployment binding, qualification shortcuts, or benchmark-specific needs.

A language change is allowed only when a concrete product scenario demonstrates an expressiveness gap that cannot be solved by ProviderBinding, ObservationBinding, Runtime behavior, qualification, Sandbox, or integration work.

When such a gap is proven, treat the change as a language revision. Update the owning Skill Platform schemas/compiler together with official Skill examples and Cases, authoring guidance, and compatibility notes as needed. Re-run `make verify` before establishing a new frozen baseline.
