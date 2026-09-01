# ConnectionAgent Skills

`connectionagent-skills` is the repository for official ConnectionAgent **Skill source assets**.

This repository owns Skill packages that can be consumed by the Agent and, when they carry the optional Execution Assurance Extension, compiled and qualified for deterministic governed execution.

## Repository boundary

This repository owns:

- standard `SKILL.md` content;
- optional Skill-local `assurance/` execution contracts;
- vendor/qualification `cases/` when they belong to the Skill source package;
- `references/`;
- optional Skill-local `scripts/` and their metadata;
- Skill-local schemas, examples, and documentation.

This repository does not own:

- Skill Compiler / ProcedurePatch apply / SkillProfile resolution -> `connectionagent-skill-platform`;
- LLM / Agent loop / model adapters -> `connectionagent-agent`;
- Target Admission / Procedure execution / Evidence Gate / Observation resolution / Reconcile -> `connectionagent-runtime`;
- Observation acquisition/binding for a deployment -> Runtime/deployment Registry;
- 5GC simulated world / fault injection -> `connectionagent-sandbox`;
- production UI -> `connectionagent-web`.

## Package model

A standard Agentic Skill may be lightweight:

```text
skills/
└── <skill-package>/
    ├── SKILL.md
    ├── references/
    ├── schemas/
    ├── scripts/
    ├── examples/
    └── cases/
```

A Skill that crosses into governed side-effect execution may add:

```text
assurance/
├── contract.yaml
├── procedure.yaml
└── predicates.yaml
```

`assurance/` is an optional **Execution Assurance Extension** for dual-engine Agent architectures. A standard Skill can exist without it; an assurance-enabled Skill adds deterministic authority, execution, recovery, and proof contracts.

The three assurance files answer different questions:

```text
contract.yaml
  -> What may this Skill do and what must ultimately hold?

procedure.yaml
  -> Which deterministic Procedure applies, and how does governed execution flow?

predicates.yaml
  -> What state must be proven, what must be observed, and how is it judged?
```

There is intentionally no standalone `evidence.yaml` in the target model.

## Model-context authoring rule

`SKILL.md` is a **thin model-visible semantic layer**, not a prose copy of the machine contracts.

Keep content in `SKILL.md` only when it materially changes one of these model decisions:

```text
when to select the Skill
what business/domain semantics mean
what must be normalized or disambiguated
what structured result the Agent must produce
```

Do not repeat Runtime-owned mechanics such as Procedure graphs, budgets, UNKNOWN/reconcile handling, Predicate evaluation, Observation acquisition, Provider Binding, qualification checks, or sandbox rules when those semantics already exist in machine contracts or Runtime documentation.

`references/preload/` is also model context and should be rare. Put a reference there only when its content must influence essentially every invocation. Architecture explanations, provider mappings, Predicate internals, and migration notes belong in `references/on-demand/` or repository documentation instead.

The target is:

```text
SKILL.md
  -> concise semantic guidance

assurance/
  -> deterministic machine truth

references/on-demand/
  -> detail when the Agent actually needs it
```

## Agentic routing vs. governed execution

The target architecture does not force every Skill into deterministic Procedure execution.

A routing/interpretation Skill may remain Agentic:

```text
natural-language intent
  -> Agentic routing Skill
  -> ExecutionTargetCandidate
```

The candidate then crosses a deterministic trust boundary:

```text
ExecutionTargetCandidate
  -> Target Admission
  -> admitted ExecutionTarget
  -> assurance-enabled executable Skill
  -> deterministic RunPlan / Procedure execution
```

Target Admission validates the proposed Skill/Variant/entrypoint, target business request schema, eligibility, authority and environment requirements. An LLM may propose the wrong target, but it cannot make that target executable merely by asserting that it is valid.

Routing quality belongs primarily to Agent/Benchmark evaluation. Admission safety and business execution reliability belong to Runtime/Assurance evaluation.

`core5g-intent` is the reference routing Skill and intentionally has **no `assurance/` directory**. It outputs `schemas/execution-target-candidate.schema.yaml`. `core5g-file-transfer` and `wifi-file-transfer` are assurance-enabled executable Skills.

Routing candidates distinguish:

```text
RESOLVED
NEEDS_CONTEXT
NEEDS_EXTENSION
```

`NEEDS_CONTEXT` covers missing or ambiguous external business/canonicalization input such as an unresolved person/device alias. Demo identity data belongs in examples/fixtures; production routing should use the live identity context supplied with the request.

Identity context is deliberately identity-only. Current UE IP, PDU Session state, QoS state, and similar dynamic network values are not routing-model inputs.

## Input ownership and execution-time dataflow

Do not expand a Candidate request merely because a later concrete Tool needs more arguments.

Keep four input classes separate:

```text
Candidate request
  -> external business inputs and canonical identities

read-only Capability + prior Action output
  -> dynamic operational data required by later business Actions

Procedure / Predicate
  -> deterministic Skill policy and literals

ProviderBinding / deployment
  -> concrete environment values
```

For the 5GC file-transfer example:

```text
transferId / senderImsi / receiverImsis
  -> Candidate request

current participant IP addresses
  -> transfer.participants.resolve_endpoints
  -> output.members

fixed duration=3600 / 5QI=8 / slice proof scope
  -> Skill policy

concrete upf-1
  -> ProviderBinding
```

A read whose output is direct operational input to a later mutation is a legitimate governed read-only Capability in the Procedure. A read that exists only to prove a Predicate belongs behind `ObservationBinding` and should not be a verify-only query Action.

```text
Capability
  -> ProviderBinding
  -> governed business read or mutation

Observation + scope
  -> ObservationBinding
  -> proof input
```

Field-level prior-output authoring is expressed with `fromOutput`, for example:

```yaml
members:
  fromOutput:
    node: resolve-member-endpoints
    path: output.members
```

The target Compiler must validate producer/consumer control-flow ordering, output path existence, schema compatibility, bounds, and immutable reuse across reconcile paths. The current shared Runtime does not yet fully implement this field-level prior-output binding, so target Skills using it are authoring/golden fixtures until the coordinated Runtime refactor lands; they must not pass production execution qualification prematurely.

## Procedure selection vs. Predicate proof

Known canonical request/context values select a Procedure directly with CEL:

```yaml
spec:
  selectionPolicy: exactlyOne
  procedures:
  - name: create-wifi-transfer-normal
    applicability:
      when: request.urgency == "normal"

  - name: create-wifi-transfer-urgent
    applicability:
      when: request.urgency == "urgent"
```

`applicability.when` is a selector, not a Predicate. It does not create PASS/FAIL/UNKNOWN, run the Evidence Gate, or acquire Observations. Exactly one Procedure must match before execution; zero or multiple matches fail closed.

Named Predicates are reserved for conditions that execution assurance must prove, reuse, or enforce as pre/postconditions or runtime verification checkpoints.

## Observation model

A proof Predicate can declare canonical Observation requirements beside its evaluator:

```yaml
wifi_transfer.request.satisfied:
  observations:
    transfer:
      ref: wifi.transfer.snapshot
      scope: >
        {
          "requestId": request.requestId,
          "transferId": facts["wifi_transfer.id"]
        }
      freshness: 5s
    qosBoost:
      ref: wifi.qos.boost_state
      scope: >
        {"transferId": facts["wifi_transfer.id"]}
      freshness: 5s
      when: request.urgency == "urgent"
  evaluator:
    type: cel
    expression: ...
```

The Skill declares **what Observation semantics it requires**:

- `ref` -> what canonical Observation;
- `scope` -> which object or bounded collection to observe;
- `freshness` -> how fresh the proof must be;
- `when` -> when that Observation requirement is active.

It does not declare how a deployment obtains the Observation. Runtime/deployment `ObservationBinding` resolves a canonical Observation from runtime state, signaling, a read-only Provider query, replay data, or an earlier governed action result.

Canonical Observation contracts belong to a shared `ObservationCatalog` and define both scope and value schemas.

## Predicate inputs

Predicate evaluators receive one stable context assembled by Runtime:

```text
request
  <- canonicalized Agent/Gateway input

subject
  <- admitted run subject

facts
  <- Runtime context + canonical governed-action contributions

observations
  <- Evidence Gate + ObservationBinding

evidence
  <- scope/provenance/freshness/audit metadata
```

A Predicate may compare request/fact values with Observations. The design only removes request-only Predicate IDs whose sole purpose was Procedure selection.

## Predicate evaluators

Target Predicate authoring uses two evaluator forms:

- **CEL** for small, auditable deterministic boolean judgement, including collection aggregation;
- **Python** for genuinely complex deterministic branching, correlation, semantic conflict handling, or richer diagnostics.

The Runtime Evidence Gate materializes required typed Observations before evaluator execution. Missing, stale, invalid, unavailable, or budget-exhausted required Observations produce `UNKNOWN`. CEL normally returns a boolean (`true -> PASS`, `false -> FAIL`); Python may also return semantic `UNKNOWN` when complete evidence is internally contradictory.

Skill-local Python evaluators remain `local_compute` with denied network access. They must not acquire Observations, dispatch Tools/Capabilities, or hide workflow execution.

Collection scopes must be bounded. Gateway-oriented request schemas cap receiver cardinality so an Observation provider cannot hide unbounded fan-out behind one `verify` checkpoint.

## Migration rule

Official Skills are migrated from `connectionagent-skill-platform/skills/` into this repository using a target-state process:

1. establish the target Skill source package here;
2. refactor Skill Platform and Runtime contracts to consume the target package model;
3. qualify assurance-enabled Skill sources against the new execution contracts;
4. evaluate Agentic routing Skills with routing/selection benchmarks and validate their candidate schemas;
5. remove superseded official/fixture assets from old locations.

The current gateway-oriented branch intentionally targets the refactored model rather than preserving legacy standalone EvidenceRules or scalar Predicate authoring.

## Current gateway-oriented Skills

- `core5g-intent` -> `[TASK: 5GC-INTENT]`; Agentic routing Skill, no `assurance/`, outputs an `ExecutionTargetCandidate`;
- `core5g-file-transfer` -> `[TASK: 5GC-FILE-TRANSFER]` and `[TASK: 5GC-VG-RELEASE]`; assurance-enabled executable Skill target fixture;
- `wifi-file-transfer` -> `[TASK: WIFI-TRANSFER]`; assurance-enabled executable Skill.

Gateway task markers are external protocol identifiers. They do not need to equal the internal Skill name.
