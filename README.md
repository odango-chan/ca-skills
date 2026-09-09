# ConnectionAgent Skills

`connectionagent-skills` is the source-of-truth repository for official ConnectionAgent **Skill source assets** and model-visible routing policy assets.

## Repository boundary

This repository owns:

- standard `SKILL.md` model-visible semantics;
- optional Skill-local `assurance/` execution contracts;
- Skill Qualification `cases/` when they belong to the source package;
- `references/` and Skill-local schemas;
- optional governed Skill-local `scripts/` and metadata.

This repository does not own:

- Compiler / ProcedurePatch / Artifact / Variant / Qualification orchestration -> `connectionagent-skill-platform`;
- Agent loop / goal interpretation / routing / model adapters -> `connectionagent-agent`;
- admission / ProviderBinding / Procedure execution / Evidence Gate / Predicate evaluation / Reconcile -> `connectionagent-runtime`;
- simulated environment / fault injection / ground truth -> `connectionagent-sandbox`;
- Benchmark Verdict / Certification -> `connectionagent-benchmark`;
- product UI -> `connectionagent-web`.

## Package model

A lightweight model-context package may contain:

```text
skills/
└── <package>/
    ├── SKILL.md
    ├── references/
    └── schemas/
```

An executable governed Skill adds the Execution Assurance Extension:

```text
assurance/
├── contract.yaml
├── procedure.yaml
└── predicates.yaml

scripts/
cases/
```

The assurance files answer different questions:

```text
contract.yaml
  -> What may this Skill do and what must ultimately hold?

procedure.yaml
  -> Which deterministic Procedure applies and how does governed execution flow?

predicates.yaml
  -> What state must be proven, what must be observed, and how is it judged?
```

There is intentionally no standalone `evidence.yaml` in the target model.

## Model-context authoring rule

`SKILL.md` is a **thin model-visible semantic layer**, not a prose copy of machine contracts.

Keep content there only when it materially changes model decisions such as:

```text
when the capability/policy applies
business/domain semantics
normalization/disambiguation rules
structured model output expectations
```

Do not repeat Runtime-owned mechanics such as Procedure graphs, budgets, UNKNOWN/reconcile state machines, Predicate execution, Observation acquisition, ProviderBinding, qualification checks, or Sandbox rules when those semantics already exist in machine contracts.

`references/preload/` should be rare. Architecture explanation, provider mappings, Predicate internals, migration notes, and examples normally belong in `references/on-demand/` or repository documentation.

## Agent routing vs governed execution

Routing is an **Agent-owned behavior**.

The current product flow is:

```text
Goal / intent
  -> Agent routing over Runtime-discovered admitted Skills
  -> agent.routing_result@1
  -> selected Skill / Variant
  -> load selected Skill context
  -> planning
  -> RuntimeHost
  -> Runtime admission + ProviderBinding + deterministic execution
```

The target architecture does **not** use this retired chain:

```text
routing Skill execution
  -> ExecutionTargetCandidate
  -> ExecutionTarget
  -> RunPlan
  -> second Skill execution
```

`ExecutionTarget.v1`, `RunPlanSnapshot.v1`, `RunPlanRevision.v1`, and generic `PlanDelta.v1` are not current cross-repository machine contracts.

`skills/5gc-intent` remains the model-visible reference policy package for generic 5GC intent routing. It intentionally has no `assurance/` directory and must not be treated as a Runtime Procedure hop. Its Skill-local `agent-routing-result.schema.yaml` describes model-facing routing payload semantics; canonical routing evidence remains Agent-owned `agent.routing_result@1`.

Routing outcomes distinguish:

```text
RESOLVED
NEEDS_CONTEXT
NEEDS_EXTENSION
```

`NEEDS_CONTEXT` covers missing or ambiguous identity/business input. Production routing must use live identity context supplied with the request. Identity context is deliberately identity-only: current UE IP, PDU Session state, QoS state, and similar dynamic network values are not routing inputs.

## Input ownership and execution-time dataflow

Keep four input classes separate:

```text
Agent-selected Skill request
  -> external business inputs and canonical identities

read-only Capability + prior Action output
  -> dynamic operational data needed by later business Actions

Procedure / Predicate
  -> deterministic Skill policy and literals

ProviderBinding / deployment
  -> concrete environment values
```

For the 5GC file-transfer example:

```text
transferId / senderImsi / receiverImsis
  -> Agent-selected business request

current participant IP addresses
  -> transfer.participants.resolve_endpoints
  -> output.members

fixed duration=3600 / 5QI=8 / proof scope
  -> Skill policy

concrete provider endpoint / UPF identity
  -> ProviderBinding
```

A read whose output is direct operational input to a later mutation is a legitimate governed read-only Capability. A read that exists only to prove a Predicate belongs behind `ObservationBinding` and should not be modeled as a verify-only query Action.

Prior-output bindings use canonical `with` / `from`, for example:

```yaml
with:
  members:
    from: resolve-member-endpoints.output.members
```

## Procedure selection vs Predicate proof

Known canonical request/context values select a Procedure directly with CEL:

```yaml
procedures:
  create-wifi-transfer-normal:
    applicability:
      when: request.urgency == "normal"
  create-wifi-transfer-urgent:
    applicability:
      when: request.urgency == "urgent"
```

`applicability.when` is a selector, not a Predicate. It does not create PASS/FAIL/UNKNOWN, run the Evidence Gate, or acquire Observations. Exactly one Procedure must match before execution; zero or multiple matches fail closed.

Named Predicates are reserved for conditions that execution assurance must prove, reuse, or enforce.

## Observation model

A Predicate may declare canonical Observation requirements beside its evaluator:

```yaml
wifi_transfer.request.satisfied:
  observations:
    transfer:
      ref: wifi.transfer.snapshot
      scope: >
        {"requestId": request.requestId, "transferId": facts["wifi_transfer.id"]}
      freshness: 5s
  evaluator:
    type: cel
    expression: observations.transfer.state == "READY"
```

The Skill declares **what** must be observed:

- `ref` -> canonical Observation;
- `scope` -> bounded object/collection scope;
- `freshness` -> freshness requirement;
- `when` -> optional activation condition.

The deployment/Runtime owns **how** the Observation is obtained through `ObservationBinding`.

Predicate evaluators receive a stable Runtime-assembled context:

```text
request
subject
facts
observations
evidence metadata
```

## Predicate evaluators and governed Scripts

Target Predicate authoring uses:

```yaml
evaluator:
  type: cel
  expression: ...
```

or:

```yaml
evaluator:
  type: script
  ref: skill.evaluate-transfer-request-satisfied
```

Use CEL for small auditable assertions. Use governed Script for deterministic business logic that requires non-trivial branching, aggregation, correlation, intermediate values, or richer diagnostics.

The Runtime Evidence Gate materializes required typed Observations before evaluator execution. Missing, stale, invalid, unavailable, or budget-exhausted required Observations produce `UNKNOWN` before evaluator execution.

Result semantics remain separated:

```text
PASS / FAIL / UNKNOWN
  <- domain judgement

EVALUATOR_EXECUTION_FAILED / TIMEOUT / POLICY_REJECTED / OUTPUT_INVALID
  <- infrastructure failure
```

Infrastructure failure must never be silently converted to `FAIL`.

Procedure Script and Predicate Script reuse the same governed local-compute execution authority:

```text
Procedure Script
  -> deterministic typed computation

Predicate Script
  -> deterministic judgement over already-materialized evidence
```

Predicate Scripts cannot invoke Providers/MCP/tools, access network, acquire Observations, mutate state, or alter Procedure flow.

## Procedure authoring baseline

The canonical object-form vNext source uses:

```text
start
nodes
call
verify
script
procedure
for
reconcile
terminal
with
on
```

`nodes` is a semantic graph, not visual layout. Authors do not store coordinates, compiler node IDs, or projection-only fields. `for` is the collection construct. Static Procedure source, admitted LLM proposal, and certified fallback lower through the same canonical Procedure admission/IR path.

## Skill Case baseline

The only Qualification Case entry is:

```text
cases/<case>/case.yaml
```

Package-root `examples/` and old split Case files are rejected. Explanatory samples belong in `references/samples/`.

SkillTestCase and BenchmarkCase remain different assets:

```text
SkillTestCase
  -> package qualification, fixture-aware

BenchmarkCase
  -> black-box/system evaluation with independent evidence
```

Benchmark does not copy SkillTestCase YAML or use the expected Procedure path itself as the correctness oracle.

## Current qualification status

Official executable reference Skills are production-qualified through Platform/Runtime/Sandbox:

```text
ue-registration
ensure-session-qos
download-object-by-deadline
query-weather-for-ue
```

Current product-target Skills:

```text
5gc-file-transfer
wifi-file-transfer
```

For both file-transfer packages, current preflight status is:

```text
source              PASS
compile             PASS
cases               PASS
registry closure    PASS
local Sandbox/Q4    PASS
production-qualified NO
```

The remaining production-admission closure is deployment/lifecycle work, not a reason to reopen the Skill authoring model:

```text
immutable Artifact/Variant admission
production deployment ProviderBinding closure
ObservationCatalog / ObservationBinding closure
```

`make verify` is the source/preflight gate and does not auto-promote a Skill to production-qualified.

## Current package roles

```text
5gc-intent
  -> Agent routing policy/model-context asset; no assurance; not a Runtime execution hop

5gc-file-transfer
  -> executable product target; preflight-qualified, production deployment closure pending

wifi-file-transfer
  -> executable product target; preflight-qualified, production deployment closure pending

ue-registration
ensure-session-qos
download-object-by-deadline
query-weather-for-ue
  -> official executable production-qualified reference Skills
```

Gateway task markers are external protocol identifiers and do not need to equal internal package names.

Verification entry is `make verify` (`scripts/verify.py` delegating canonical Platform/Runtime/Sandbox gates). See `docs/skill-preflight-hardening.md` for the detailed qualification matrix.
