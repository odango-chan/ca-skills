# Authoring ConnectionAgent Skills

This guide explains how to add or change official Skill source in this repository.

For the canonical source-language and semantic-token contract, see [Skill Language Specification](skill-language-spec.md). Use `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md` for practical examples, [Authoring Model](authoring-model.md) for current 5GC node semantics, [Current 5GC Skill baseline](current-5gc-skill-baseline.md) for provenance/compatibility, and [Project Layout](project-layout.md) for workspace structure. The legacy `ca-skill-toolchain` validates only constructs represented by its current schemas. The conventional 5GC Procedure uses node-level `preconditions/postconditions` that the legacy schema does not support; the accepted stateless Compiler v0 is not implemented yet.

Chinese version: [`authoring.zh-CN.md`](authoring.zh-CN.md)

## 1. Choose the right asset type

Before creating files, decide whether the change belongs to a Skill, a routing-policy package, or a Runtime Capability.

### Executable Skill

Use an executable Skill for a product or domain goal that needs deterministic execution assurance. It normally contains `SKILL.md` and the complete `assurance/` extension.

Current 5GC executable examples:

- `establish-pdu-session` — conventional initial establishment profile;
- `establish-pdu-session-mas` — SMF MAS policy-first initial establishment profile.

They are separate business profiles, not fallbacks for one another. Other historical packages remain outside the current 5GC baseline.

### Routing-policy or model-context package

Use this form when the Agent needs business semantics or routing policy, but there is no Runtime Procedure to execute.

Routing remains Agent-owned behavior; do not model routing as one executable Skill selecting another executable Skill. No historical routing package is treated as part of the current 5GC baseline.

### Runtime Capability

Low-level Provider actions belong to Runtime capability contracts. Do not create a Skill merely to wrap a single query, create, update, or delete operation.

For boundary examples, see `.agents/skills/create-connectionagent-skill/references/skill-granularity.md`.

## 2. Package layout

A model-context package may be as small as:

```text
skills/<name>/
├── SKILL.md
├── references/    # optional
└── schemas/       # optional
```

The **current** governed executable Skill layout is:

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
└── scripts/       # optional
```

Repository rules:

- `assurance/` is all-or-nothing;
- there is no standalone `evidence.yaml`;
- each qualification case is one `cases/<case>/case.yaml` file;
- package-root `README.md`, `MIGRATION.md`, and `examples/` are not part of the canonical package shape;
- explanatory samples belong under `references/samples/`;
- `references/` is Skill-owned supplemental material, but its contents are **not automatically model-visible**. `SKILL.md` lists exact paths and when each may help; the model decides whether to read a relevant reference. Do not create `preload/` or `on-demand/` directory conventions;
- `scripts/` remains a first-class optional governed local-compute asset; create it only when the Skill actually needs deterministic local computation, never as an empty placeholder;
- cross-cutting Planner/Linker/Admission fixtures belong in their owning test area, not under a business Skill's `references/`;
- model-facing Markdown under `skills/` is written in English;
- do not create empty directories.

> A new Rule / Case-lineage design baseline was frozen on 2026-09-15, but `rules.yaml`, `SkillRuleSet`, and `ruleRefs` are not yet part of the Toolchain schemas. Do not add those assets or fields to production Skill source until the machine contract lands.

## 3. Write `SKILL.md` for the model

`SKILL.md` is the package-root model-facing entry point. Keep it focused on information that changes model behavior:

- when the Skill applies;
- the business or domain goal;
- input normalization and disambiguation;
- model-facing input and output expectations **when the Skill actually owns such a payload**;
- constraints the model must not guess or bypass;
- when the next decision depends on current state, **which facts must first be established and which substitute inferences are invalid**.

For an executable Skill, do **not** invent a Skill-specific model response payload merely to report execution success. Runtime success is established by governed Procedure execution and SkillContract postconditions / Predicate verdicts. If a model stage such as routing or semantic choice has a structured response, that response contract belongs to the owning Host/model adapter unless the Skill itself genuinely owns a semantic payload.

If the Skill itself does own a real model-facing payload, describe its semantics in `SKILL.md` and put the exact reusable payload shape in `schemas/` when a schema is useful. Do not create `output.schema.yaml` by default for executable Skills.

Do not make `SKILL.md` a default Tool workflow script. A general-purpose Agent should normally choose among its current model-visible read-only Capabilities from their names, descriptions, and schemas.

Prefer guidance such as:

```text
Before choosing a recovery action, establish current user-plane reachability.
Do not infer user-plane reachability from PDU Session existence.
```

rather than a default recipe such as:

```text
Step 1: call user_plane.inspect_connectivity
Step 2: ...
```

Explicitly recommend a model-visible business Capability only when there is real domain ambiguity, for example:

```text
multiple visible Tools have very similar names or semantics
the model can easily choose the wrong fact source
choosing the right class of fact is itself domain knowledge
```

Even then, `SKILL.md` names only the business-semantic Capability, never raw ObservationRefs, ObservationBinding, environment endpoints, or source-specific transport details.

Do not place implementation or deployment mechanics in `SKILL.md`. Provider mappings, endpoints, raw ObservationRefs, ObservationBinding details, ObservationSource transport, Runtime state machines, Runtime Tool-eligibility policy, qualification status, Benchmark scoring, migration notes, and architecture tutorials belong elsewhere.

### 3.1 Skill semantics are not Tool authority

`SKILL.md` provides epistemic/domain guidance:

```text
what must be known
what must not be guessed
which inference is invalid
```

The authoritative ConnectionAgent Tool visibility upper bound is resolved by Runtime/Harness:

```text
Runtime Capability Catalog
  + selected Skill/Artifact
  + SkillContract allowedResources
  + Context / Template / AgentProfile / Environment / policy
  -> Runtime Resolved CA Toolset
```

Host and `ca-mcp` mechanically map and may further narrow that set. They must not widen Tool authority based on Skill prose or Goal text.

If a semantically appropriate read-only Capability is not visible to the current AgentInstance, the model must treat it as unavailable. It must not bypass Runtime/`ca-mcp` and call Sandbox, Service Fabric, or a raw Observation API directly.

## 4. Long-term Rule / Procedure / Predicate model

The Rule design is now a **design baseline** in `ca-skill-toolchain/docs/rule-authoring-and-case-lineage.md`.

The intended responsibilities are:

```text
Rule
  = what must hold / what is forbidden

Procedure
  = how governed execution proceeds

Predicate
  = how PASS / FAIL / UNKNOWN is determined from Observation / Evidence

Qualification Case
  = how an immutable Skill Artifact is qualified

Benchmark Case
  = how Model / Agent / Harness / System behavior is independently evaluated
```

They remain separate artifact types.

Example:

```text
Rule:
  no blind retry after OUTCOME_UNKNOWN

Procedure:
  mutation OUTCOME_UNKNOWN -> reconcile

Predicate / Evidence:
  determine goal state or reconciliation result
```

A Procedure may enforce a Rule, but a Procedure node is not the Rule identity. A Predicate may provide truth required by a Rule, but a Predicate is not the normative source.

### 4.1 One CA Authoring Language Core

The source-derived v0 language contract and semantic-token taxonomy are specified in [Skill Language Specification](skill-language-spec.md). The shared primitives below remain the long-term design direction; they are not all current reserved syntax. In particular, Rule syntax is not part of the current Skill source baseline. When Rule support is implemented, it should reuse the same authoring primitives rather than introduce a separate DSL. Candidate shared primitives include:

```text
ref
from / value
when
expression
verify
path / op / value
for   # only where the artifact type permits iteration
```

Each artifact remains a constrained sub-language:

```text
Procedure
  may call / tool / reconcile / on / terminal

Rule
  expresses when / verify / appliesTo / violation / severity
  never performs mutation or owns workflow routing

Predicate
  owns observations / freshness / evaluator

Case
  owns challenge / fixture / evidence / expectation
```

The principle is:

> **Share authoring primitives, not execution authority.**

### 4.2 Rule ID and Violation Code are different

Future Rule identities may look like:

```text
5gc.pdu-session.initial-establishment.profile-bound
execution.outcome-unknown.no-blind-retry
```

Cross-Skill evaluation categories may look like:

```text
PARAMETER_FABRICATION
BLIND_RETRY_AFTER_UNKNOWN
INVENTED_RUNTIME_STATE
```

Specific normative Rule identity and aggregate violation taxonomy must not share one ID space.

### 4.3 Do not migrate source early

The Toolchain does not currently implement:

```text
SkillRuleSet schema
rules.yaml package support
SkillTestCase.ruleRefs
Rule compile/artifact
```

Current Skills continue to use the source constructs recorded in [Skill Language Specification](skill-language-spec.md) until the new Compiler and Rule machine contract are implemented. Historical packages are not used as current 5GC authoring examples.

## 5. Authoring contracts

For executable Skills, the three files under `assurance/` have distinct roles:

| File | Purpose |
| --- | --- |
| `contract.yaml` | Skill goal, admissible resources, preconditions, requirements, postconditions, and planning limits |
| `procedure.yaml` | deterministic workflow structure and data/control bindings |
| `predicates.yaml` | required observations and deterministic judgment over materialized evidence |

`contract.yaml` has an additional important role: `allowedResources.capabilities` is one upper-bound input to Runtime/Harness ConnectionAgent Tool-eligibility resolution for this Skill.

Keep the distinction explicit:

```text
allowedResources.capabilities
  = Capability universe / upper-bound input allowed by the Skill

Runtime Resolved CA Toolset
  = the subset currently allowed to be model-visible for the resolved Agent/Skill/Context/Environment
```

Therefore `allowedResources.capabilities`:

- may include read-only or inspect Capabilities useful to model planning;
- may also include deterministic Procedure-only Capabilities that do not need to be model-visible;
- is not an MCP Tool catalog;
- is not the final model-visible Toolset;
- cannot bypass Environment, policy, or Runtime admission constraints.

A resource entry may be a registered Capability ID (resolved by the deployment CapabilityContracts registry to its exact Operations) or a direct exact Operation ID. Procedure `call` always names an exact Operation ID. The current conventional 5GC Skill uses direct Operation grants. The ToolCatalog defines Operation contracts; it is not the deployment Capability registry.

Use these Platform schemas as the authoring authority:

| Source asset | Platform schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| governed Script metadata | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

For `procedure.yaml`, the current source uses the object-form vNext model (`procedures -> start/nodes`), not the older array/type/action shape. Compatibility warning: the current legacy `procedure-source.schema.yaml` does not model node-level `preconditions/postconditions` used by the conventional PDU Session Skill. Do not delete or flatten those fields to make the legacy compiler accept the source. The new stateless Compiler is the target, but implementation has not started.

The detailed syntax reference is intentionally kept in one place:

```text
.agents/skills/create-connectionagent-skill/references/authoring-syntax.md
```

## 6. Observation, Evidence, Agent reads, and Predicate

These roles must remain distinct.

### 6.1 Agent read-only inspection

When model planning depends on current state, the model should autonomously select an appropriate read-only Capability from the Runtime Resolved CA Toolset.

```text
Skill/domain constraints
  -> what must be known / what must not be inferred

Runtime/Harness
  -> resolves allowed read-only Capabilities

Agent
  -> chooses one visible read-only Tool
  -> ca-mcp
  -> Runtime read-only Capability
  -> Runtime Observation acquisition / Provider read path
  -> trusted fact
  -> Agent planning
```

The model does not need raw ObservationRefs, ObservationBinding, Sandbox Observation APIs, or Service Fabric internal streams.

A Skill does not need to name a specific Tool by default; explicit Tool guidance is only for real domain ambiguity.

### 6.2 Runtime Assurance

Runtime materializes the observations required by a Predicate. The Evidence Gate checks whether required evidence is present, fresh, and usable.

```text
Procedure / precondition / postcondition
  -> Predicate
  -> required Observation
  -> Runtime Observation acquisition
  -> Evidence
  -> PASS / FAIL / UNKNOWN
```

Missing or unusable required evidence produces `UNKNOWN` before the evaluator runs.

### 6.3 Shared facts, separate verdict authority

Agent read-only Capabilities and Runtime Assurance may share the same ObservationSource, binding, normalization, provenance, and observation cache when freshness and binding requirements are satisfied.

But:

```text
Agent read result
  = planning input

Predicate result
  = assurance verdict authority
```

A model having just inspected state does not make a postcondition pass. Runtime Assurance also does not depend on the model having inspected first.

Observation classes remain fact-oriented, such as Network Observation and Environment Observation. Do not introduce `Planning Observation`, `Agent Observation Projection`, or similar parallel fact types.

### 6.4 Predicate evaluator

Use CEL for short, auditable deterministic checks. Use a governed Predicate Script only when the judgment is too complex for a clear CEL expression.

Predicate Scripts may only evaluate supplied data. They must not call Providers, MCP servers, external services, or acquire additional evidence.

Future Rule expressions should reuse the same deterministic expression direction instead of inventing a separate Rule expression language.

## 7. Qualification cases

Skill cases validate the source package and its expected planning/execution behavior. They are not Benchmark cases.

Use one `case.yaml` per case directory. Coverage should follow the Skill's semantic obligations rather than a fixed case count. Depending on the Skill, useful classes include:

- normal success;
- denied or failed operations;
- evidence `UNKNOWN`;
- mutation `OUTCOME_UNKNOWN` followed by reconcile;
- budget or planning limits;
- independent postcondition failure;
- when planning depends on current state, whether the model can discover and use an appropriate allowed read-only Capability instead of guessing;
- where domain ambiguity exists, whether Skill semantics prevent the model from substituting the wrong class of fact.

Do not treat fixture output as proof of the business result. Final success must still be supported by the required postconditions.

In the future, Qualification Cases and Benchmark Cases may reference the same stable Rule through `ruleRefs`, while preserving separate identities and verdicts:

```text
SkillTestCase
  = package/artifact qualification
  = fixture-driven

BenchmarkCase
  = independent evaluation question
  = held-out variants + independent evidence
```

Do not copy Qualification examples directly into formal Benchmark tasks when that would expose the answer rather than test generalization.

## 8. Use existing Skills as examples

Prefer current official packages over copied tutorial examples:

| Need | Current reference package |
| --- | --- |
| conventional UE-requested initial PDU Session Establishment | `establish-pdu-session` |
| SMF MAS policy-first initial establishment | `establish-pdu-session-mas` |

These are the only current 5GC Skill source examples for this repository baseline. They are not yet fully compiler/link validated; see [Current 5GC Skill baseline](current-5gc-skill-baseline.md). Other historical packages remain unchanged and are outside this authoring scope.

Rule/Case machine migration remains deferred until its schema and compiler support are available. Do not use a historical package as a substitute for the current 5GC source contract.

## 9. Authoring workflow

For a new Skill or a structural change:

1. Read `AGENTS.md`.
2. Decide whether the asset is an executable Skill, routing-policy/model-context package, or Runtime Capability.
3. Inspect one or two current packages with similar semantics.
4. Reuse existing Registry capability, predicate, and schema contracts where possible.
5. If model planning may depend on current state, confirm that an appropriate read-only Capability exists and place it within the correct `allowedResources.capabilities` resource boundary; do not put low-level Observation wiring into `SKILL.md` just to prompt inspection.
6. Add explicit Tool guidance in `SKILL.md` only when domain semantics make the correct fact source genuinely ambiguous.
7. Read the relevant section of `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md` before editing assurance source, Scripts, or Cases.
8. For one legacy-compatible executable package, run:

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

   Set `CA_SKILL_TOOLCHAIN_ROOT=/path/to/ca-skill-toolchain` when the Toolchain repository is not available as sibling `../ca-skill-toolchain`. The historical `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` remains a compatibility alias.

9. Before delivery, run:

   ```bash
   make verify
   ```

10. Report the checks that actually ran and any remaining Platform, Runtime, Provider, Sandbox, or deployment dependency.

A successful legacy compile or repository preflight check does not make a Skill production-qualified. Do not treat a legacy compile attempt as validation of the current 5GC baseline while its node-level Procedure fields remain unsupported.

## 10. Ownership

Keep the repository boundary simple:

```text
ca-skills
  authoring guidance + official Skill / Rule source authority
  Skill resource boundary + epistemic/domain guidance
  # Rule machine source becomes active only after the schema lands

ca-skill-toolchain
  machine schemas + compiler + qualification

ca-runtime / Harness
  admission + ConnectionAgent Tool eligibility + binding + deterministic execution + Observation/Evidence/Predicate authority

ca-mcp
  mechanical mapping from Runtime-authorized Capability to Agent MCP Tool

Agent Host
  registers model-visible Tools; for CA Tools it may only apply Runtime Resolved CA Toolset or narrow it further

ca-benchmarks / ca-benchmark-engine
  BenchmarkCase + held-out evaluation + assessment
```

If a concrete scenario cannot be expressed, first check whether the missing piece is an appropriate read-only Capability, the Skill `allowedResources.capabilities` boundary, Runtime Tool-eligibility resolution, ProviderBinding, ObservationBinding/ObservationSource, Runtime behavior, qualification, Benchmark/Judge requirements, or integration before changing the Skill language.
