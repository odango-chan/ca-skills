---
name: create-connectionagent-skill
description: Use when the user asks to design, create, or structurally complete an official ConnectionAgent Skill source package in this repository. Classify the asset, follow the current authoring workflow, load detailed syntax references only when needed, validate with Skill Toolchain, and report qualification status precisely.
---

# Create ConnectionAgent Skill

Create or structurally complete official ConnectionAgent Skill source in `ca-skills`.

Official source lives only under `skills/<name>/`. This developer workflow is an authoring assistant, not an official business Skill and not a second machine-language authority.

## Authority

Read repository `AGENTS.md` first.

Use this precedence:

1. current cross-repository machine-contract/stage decisions;
2. current `ca-skill-toolchain` schemas and compiler behavior;
3. repository-local `AGENTS.md` rules;
4. this workflow and its references.

Important source schemas:

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
- **Runtime Capability** — low-level Provider/read/mutation action; do not create a Skill merely to wrap one primitive call.

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

## Keep package `SKILL.md` thin

`SKILL.md` is the model-facing semantic entry point. Keep only information that materially changes model decisions:

- when the Skill applies;
- business/domain meaning;
- normalization and disambiguation;
- model-facing structured expectations;
- boundaries the model must not guess or bypass;
- when a decision depends on current state, which facts must first be established and which substitute inferences are invalid.

Do **not** make `SKILL.md` a default Tool workflow script. A general-purpose Agent should normally choose among its current model-visible read-only Capabilities from Tool names, descriptions, and schemas.

Prefer:

```text
Before choosing a recovery action, establish current user-plane reachability.
Do not infer user-plane reachability from PDU Session existence.
```

instead of:

```text
Step 1: call user_plane.inspect_connectivity
Step 2: ...
```

Explicitly recommend a business-semantic Capability only when there is genuine domain ambiguity: multiple visible Tools have similar semantics and selecting the correct fact source is itself domain knowledge.

Never expose raw ObservationRefs, ObservationBinding, ObservationSource endpoints, Sandbox trust surfaces, or Service Fabric internal streams as model guidance.

## Skill resource boundary is not Tool authority

For executable Skills, `assurance/contract.yaml.allowedResources.capabilities` is one Skill-level Capability universe / upper-bound input.

It may include:

```text
read-only / inspect Capabilities useful to planning
Procedure-only Capabilities
mutation Capabilities
local compute Capabilities
```

But:

```text
allowedResources.capabilities
  != Runtime Resolved CA Toolset
  != MCP Tool catalog
  != final model-visible Tool list
```

Current architecture:

```text
Runtime Capability Catalog
  + selected/admitted Skill or Artifact
  + SkillContract allowedResources.capabilities
  + Context / Template / AgentProfile / Environment / policy inputs
  -> ca-runtime / Harness
  -> Runtime Resolved CA Toolset
  -> ca-mcp / Host mechanical mapping and optional narrowing
```

Runtime/Harness owns authoritative ConnectionAgent Tool eligibility. `ca-mcp` and Host may mechanically narrow but never widen it. Skill prose cannot grant Tool authority.

Do not add new Skill fields such as:

```text
visibleTools
toolset
planningTools
observationTools
```

unless a future cross-repository machine-contract decision explicitly introduces them.

## Observation and Assurance

When planning depends on current state:

```text
Skill/domain guidance
  -> what must be known / what must not be inferred

Runtime Resolved CA Toolset
  -> eligible read-only Capabilities

Agent
  -> autonomously chooses a visible read-only Tool
  -> ca-mcp
  -> Runtime read-only Capability
  -> Runtime Observation acquisition / Provider read path
  -> trusted fact
  -> planning
```

Runtime Assurance remains independent:

```text
Procedure / precondition / postcondition
  -> Predicate
  -> required Observation
  -> Runtime Observation acquisition
  -> Evidence
  -> PASS / FAIL / UNKNOWN
```

The two consumers may share ObservationSource, binding, normalization, provenance, and a freshness-valid cache. But:

```text
Agent read result
  = planning input

Predicate result
  = assurance verdict authority
```

A model having inspected a fact does not make a postcondition pass. Runtime Assurance also must not depend on the model having inspected first.

Do not introduce `PlanningObservation`, `Agent Observation Projection`, or another parallel Observation fact type. Retain fact-oriented distinctions such as Network Observation and Environment Observation.

## Load detailed references only when needed

Read `references/authoring-syntax.md` when creating or changing:

- `assurance/contract.yaml`;
- `assurance/procedure.yaml`;
- `assurance/predicates.yaml`;
- governed `scripts/*.py`;
- `cases/<case>/case.yaml`.

Do not load it for a simple model-context/routing-policy edit that only changes `SKILL.md` or model references.

## Core authoring invariants

- reuse governed Registry Capability/Predicate/schema contracts before creating local ones;
- Procedure source uses current object-form vNext (`procedures -> start/nodes`);
- use governed outcomes and explicit `on` routing;
- mutation `OUTCOME_UNKNOWN` preserves uncertainty and must reconcile before retry/continuation;
- `applicability.when` is Procedure selection, not Runtime Predicate evaluation;
- if planning needs current state, ensure an appropriate read-only Capability exists within the Skill resource boundary; do not assume Skill prose makes it visible;
- model Tool choice is normally autonomous within the Runtime-resolved set;
- Agent read-only inspection may share Runtime Observation acquisition with Assurance, but not verdict authority;
- Runtime Assurance must not depend on the model having inspected first;
- Observation acquisition happens before Predicate evaluation;
- missing/stale/unavailable required evidence becomes `UNKNOWN`, not business `FAIL`;
- CEL is for small auditable deterministic assertions; governed Script is for complex deterministic local judgment;
- Predicate Scripts must not call Providers, MCP servers, networks, or acquire additional evidence;
- SkillTestCase is not BenchmarkCase;
- Case coverage follows semantic obligations, not a fixed count.

## Workflow

1. Read repository `AGENTS.md`.
2. Classify the request as executable Skill, model-context/routing policy, or Runtime Capability.
3. Inspect one or two adjacent official Skills with similar semantics.
4. Reuse existing governed contracts before introducing new local assets.
5. If model planning depends on current state, confirm an appropriate read-only Capability exists and place it in the correct `allowedResources.capabilities` boundary where applicable.
6. Put epistemic/domain constraints in `SKILL.md`; name a specific Capability only for genuine domain ambiguity.
7. Read `references/authoring-syntax.md` only if assurance, Script, or Case source must change.
8. Write the smallest complete package; do not add speculative files or duplicate language docs.
9. Run focused compile:

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

10. Before delivery, run:

   ```bash
   make verify
   ```

11. Run additional qualification/production admission required by the owning Runtime/Sandbox environment.
12. Report exactly what ran and what did not run.

A focused compile or green source gate is not production qualification.

## Do not create parallel contracts

Do not add:

- standalone `evidence.yaml`;
- package-root `examples/`;
- per-Skill root validators such as `scripts/validate_<skill>.py`;
- another compile helper under this authoring workflow;
- Provider/deployment mappings in model context;
- raw ObservationRef / ObservationBinding as model-facing Tool guidance;
- `PlanningObservation` / `Agent Observation Projection` as new artifact types;
- `visibleTools` / `planningTools` / `observationTools` as local Tool-authority fields;
- graph coordinates/layout metadata in Skill source;
- `ExecutionTarget.v1`, `RunPlanSnapshot.v1`, `RunPlanRevision.v1`, or generic `PlanDelta.v1` as new cross-repository contracts.

If a scenario appears impossible, first determine whether the gap is an appropriate read-only Capability, Skill resource boundary, Runtime Tool eligibility resolution, ProviderBinding, ObservationBinding/ObservationSource, Runtime behavior, qualification, or integration before changing the Skill language.

## Delivery

Report:

- files added/changed/removed;
- semantic decisions and reused contracts;
- exact verification/compile/qualification commands actually run;
- unresolved Toolchain, Runtime, Provider, Sandbox, or deployment dependencies.

For detailed syntax, read `references/authoring-syntax.md`. For Skill-vs-Capability granularity, read `references/skill-granularity.md`. For the human-oriented guide, see `docs/authoring.md`.
