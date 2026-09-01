# ConnectionAgent Skills

`connectionagent-skills` is the repository for official ConnectionAgent **Skill source assets**.

The repository keeps standard Skill-facing content separate from an optional machine-readable **Execution Assurance Extension**. The assurance model is intentionally not named after ConnectionAgent: the same pattern can be reused by other Agent runtimes that combine an LLM/Agent engine with a deterministic execution/verification engine.

## Repository boundary

This repository owns:

- `SKILL.md`;
- optional Skill-local `assurance/` contracts;
- vendor/qualification `cases/` when they belong to the Skill source package;
- `references/`;
- optional Skill-local `scripts/` and their metadata;
- Skill-local schemas, examples, and documentation.

This repository does not own:

- Skill Compiler / ProcedurePatch apply / SkillProfile resolution -> `connectionagent-skill-platform`;
- LLM / Agent loop / model adapters -> `connectionagent-agent`;
- deterministic Procedure execution / Evidence Gate / Observation resolution / Reconcile -> `connectionagent-runtime`;
- Observation acquisition/binding for a deployment -> Runtime/deployment Registry;
- 5GC simulated world / fault injection -> `connectionagent-sandbox`;
- production UI -> `connectionagent-web`.

## Target package layout

```text
skills/
└── <skill-package>/
    ├── SKILL.md
    ├── assurance/
    │   ├── contract.yaml
    │   ├── procedure.yaml
    │   └── predicates.yaml
    ├── cases/
    ├── references/
    ├── schemas/
    ├── scripts/
    └── examples/
```

`assurance/` is an optional extension layer. A normal Skill can exist without it. A Skill that needs deterministic governed execution can add the extension without changing the meaning of `SKILL.md`.

The three assurance files answer three different questions:

```text
assurance/contract.yaml
  -> What may this Skill do, and what must ultimately hold?

assurance/procedure.yaml
  -> How does governed deterministic execution flow?

assurance/predicates.yaml
  -> What must be observed, and how is correctness judged?
```

The directory name means **execution assurance**, not merely post-execution verification. It covers the authority envelope, deterministic Procedure, proof requirements, and failure semantics needed by the reliable execution engine.

There is intentionally no standalone `evidence.yaml` in the target model. Observation requirements live beside the Predicate evaluator that consumes them:

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
- `when` -> when the requirement is active.

It does not declare how a deployment obtains the Observation. Runtime/deployment `ObservationBinding` resolves a canonical Observation from runtime state, signaling, a read-only Provider query, replay data, or an earlier governed action result.

This keeps Observation acquisition out of business Procedure authoring and prevents Provider-specific read paths from becoming stable Skill semantics.

## Dual-engine model

The package boundary is intentionally compatible with a dual-engine architecture:

```text
Standard Skill surface
  SKILL.md / references / examples
        ↓
Agent / LLM engine
  interpretation / selection / bounded planning

Execution Assurance Extension
  assurance/*.yaml
        ↓
Deterministic engine / Harness Runtime
  admission / execution / verification / reconcile
```

The assurance extension therefore describes a reliability/execution pattern rather than a ConnectionAgent-specific runtime namespace.

## Predicate evaluators

Target Predicate authoring uses two evaluator forms:

- **CEL** for small, auditable deterministic boolean judgement, including collection aggregation;
- **Python** for genuinely complex deterministic branching, correlation, semantic conflict handling, or richer diagnostics.

The Runtime Evidence Gate materializes the required typed Observations before evaluator execution. Missing, stale, invalid, unavailable, or budget-exhausted required Observations produce `UNKNOWN`. CEL normally returns a boolean (`true -> PASS`, `false -> FAIL`); Python may also return semantic `UNKNOWN` when complete evidence is internally contradictory.

Skill-local Python evaluators remain `local_compute` with denied network access. They must not acquire Observations, dispatch Tools/Capabilities, or hide workflow execution.

## Canonical Observation model

Canonical Observation contracts belong to a shared `ObservationCatalog`. Each contract defines both:

```text
scope schema -> canonical value schema
```

Examples include:

```text
transfer.participants.registration
transfer.participants.session
virtual_group.snapshot
transfer.qos.boost_state
wifi.transfer.snapshot
wifi.qos.boost_state
```

A deployment maps semantic Observation IDs to concrete acquisition mechanisms through `ObservationBinding`. This is analogous to Capability -> Provider Binding while remaining a proof/evidence concern rather than a Procedure business action.

Collection scopes must be bounded. Gateway-oriented request schemas therefore cap receiver cardinality so an Observation provider cannot hide unbounded fan-out behind a single `verify` checkpoint.

## Migration rule

Official Skills are migrated from `connectionagent-skill-platform/skills/` into this repository using a target-state process:

1. establish the target Skill source package here;
2. refactor Skill Platform and Runtime contracts to consume the target assurance model;
3. qualify the independent Skill source against the new contracts;
4. remove superseded official/fixture assets from old locations.

The current gateway-oriented branch intentionally targets the refactored `assurance/` extension with a combined `PredicateSet`. It does not preserve the old standalone `EvidenceRules` or scalar Predicate authoring contract.

## Current gateway-oriented Skills

The repository now includes source packages for:

- `core5g-intent` -> generic `[TASK: 5GC-INTENT]` routing;
- `core5g-file-transfer` -> `[TASK: 5GC-FILE-TRANSFER]` and `[TASK: 5GC-VG-RELEASE]`;
- `wifi-file-transfer` -> `[TASK: WIFI-TRANSFER]`.

Gateway task markers are external protocol identifiers. They do not need to equal the internal Skill name.
