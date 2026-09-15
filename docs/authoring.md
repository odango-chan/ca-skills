# Authoring ConnectionAgent Skills

This guide explains how to add or change official Skill source in this repository.

For detailed YAML and Script examples, use `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md`. Machine validity is defined by the current schemas and compiler in `ca-skill-toolchain`.

Chinese version: [`authoring.zh-CN.md`](authoring.zh-CN.md)

## 1. Choose the right asset type

Before creating files, decide whether the change belongs to a Skill, a routing-policy package, or a Runtime Capability.

### Executable Skill

Use an executable Skill for a product or domain goal that needs deterministic execution assurance. It normally contains `SKILL.md` and the complete `assurance/` extension.

Typical examples:

- `ue-registration`
- `ensure-session-qos`
- `download-object-by-deadline`
- `query-weather-for-ue`

### Routing-policy or model-context package

Use this form when the Agent needs business semantics or routing policy, but there is no Runtime Procedure to execute.

`5gc-intent` is the reference package. Routing remains Agent-owned behavior; do not model routing as one executable Skill selecting another executable Skill.

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
- model-facing Markdown under `skills/` is written in English;
- do not create empty directories.

> A new Rule / Case-lineage design baseline was frozen on 2026-09-15, but `rules.yaml`, `SkillRuleSet`, and `ruleRefs` are not yet part of the Toolchain schemas. Do not add those assets or fields to production Skill source until the machine contract lands.

## 3. Write `SKILL.md` for the model

`SKILL.md` is the package-root model-facing entry point. Keep it focused on information that changes model behavior:

- when the Skill applies;
- the business or domain goal;
- input normalization and disambiguation;
- model-facing input and output expectations;
- constraints the model must not guess or bypass.

Do not place implementation or deployment mechanics in `SKILL.md`. Provider mappings, endpoints, ObservationBinding details, Runtime state machines, qualification status, Benchmark scoring, migration notes, and architecture tutorials belong elsewhere.

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

When Rule support is implemented, it should reuse the same authoring primitives rather than introduce a separate DSL. Candidate shared primitives include:

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
5gc-file-transfer.urgency.explicit-only
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

Current Skills therefore continue to use the existing syntax in the following sections. `5gc-file-transfer` will be used as the reference migration before the machine contract is implemented.

## 5. Authoring contracts

For executable Skills, the three files under `assurance/` have distinct roles:

| File | Purpose |
| --- | --- |
| `contract.yaml` | Skill goal, admissible resources, preconditions, requirements, postconditions, and planning limits |
| `procedure.yaml` | deterministic workflow structure and data/control bindings |
| `predicates.yaml` | required observations and deterministic judgment over materialized evidence |

Use these Platform schemas as the authoring authority:

| Source asset | Platform schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| governed Script metadata | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

For `procedure.yaml`, author against `procedure-source.schema.yaml`. Current official source uses the object-form vNext model (`procedures -> start/nodes`). Do not use the older array/type/action source shape.

The detailed syntax reference is intentionally kept in one place:

```text
.agents/skills/create-connectionagent-skill/references/authoring-syntax.md
```

## 6. Evidence and Predicate rules

Observation acquisition and Predicate evaluation are separate.

Runtime materializes the required observations first. The Evidence Gate checks whether required evidence is present, fresh, and usable. Missing or unusable required evidence produces `UNKNOWN` before the evaluator runs.

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
- independent postcondition failure.

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

| Need | Reference package |
| --- | --- |
| compact end-to-end executable Skill | `query-weather-for-ue` |
| mutation and reconcile handling | `ue-registration` |
| requirements and postconditions | `ensure-session-qos` |
| deadline and local computation | `download-object-by-deadline` |
| non-executable routing policy | `5gc-intent` |

This keeps examples aligned with the compiler and avoids maintaining a second set of sample packages.

Before Rule/Case migration is implemented, `5gc-file-transfer` is the planned reference migration target, not a replacement for the current package contract.

## 9. Authoring workflow

For a new Skill or a structural change:

1. Read `AGENTS.md`.
2. Decide whether the asset is an executable Skill, routing-policy/model-context package, or Runtime Capability.
3. Inspect one or two current packages with similar semantics.
4. Reuse existing Registry capability, predicate, and schema contracts where possible.
5. Read the relevant section of `.agents/skills/create-connectionagent-skill/references/authoring-syntax.md` before editing assurance source, Scripts, or Cases.
6. For one executable package, run:

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

   Set `CA_SKILL_TOOLCHAIN_ROOT=/path/to/ca-skill-toolchain` when the Toolchain repository is not available as sibling `../ca-skill-toolchain`. The historical `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` remains a compatibility alias.

7. Before delivery, run:

   ```bash
   make verify
   ```

8. Report the checks that actually ran and any remaining Platform, Runtime, Provider, Sandbox, or deployment dependency.

A successful compile or repository preflight check does not make a Skill production-qualified.

## 10. Ownership

Keep the repository boundary simple:

```text
ca-skills
  authoring guidance + official Skill / Rule source authority
  # Rule machine source becomes active only after the schema lands

ca-skill-toolchain
  machine schemas + compiler + qualification

ca-runtime
  admission + binding + deterministic execution

ca-benchmarks / ca-benchmark-engine
  BenchmarkCase + held-out evaluation + assessment
```

If a concrete scenario cannot be expressed, first check whether the missing piece is a ProviderBinding, ObservationBinding, Runtime behavior, qualification rule, Benchmark/Judge requirement, or integration issue before changing the Skill language.
