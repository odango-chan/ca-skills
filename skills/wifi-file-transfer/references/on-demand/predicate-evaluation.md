# Predicate Evaluation

This Skill uses the target **Execution Assurance Extension**:

```text
assurance/
├── contract.yaml
├── procedure.yaml
└── predicates.yaml
```

The extension is generic to a dual-engine Agent architecture. It is not a ConnectionAgent-specific namespace and does not replace the standard `SKILL.md` surface.

`assurance/predicates.yaml` contains both canonical Observation requirements and the evaluator that consumes them. There is no standalone `evidence.yaml` and no legacy scalar `valueType + rules` authoring shape.

## CEL is sufficient here

Both Wi-Fi predicates are simple enough to remain CEL expressions.

`transfer.intent.urgent` depends only on the normalized request:

```text
request.urgency == "urgent"
```

It needs no environment Observation declaration.

`wifi_transfer.request.satisfied` declares scoped typed inputs beside its CEL evaluator:

```yaml
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
```

The evaluator then checks the prepared canonical values. `qosBoost` is required only for urgent requests.

## Scope is not acquisition

`scope` answers which transfer must be observed. It does not select `wifi_status` or any concrete Provider query.

Runtime/deployment `ObservationBinding` maps `wifi.transfer.snapshot + scope` and `wifi.qos.boost_state + scope` to an available source such as:

- a fresh action result;
- runtime state;
- signaling;
- replay data;
- a read-only deployment-specific status query.

That acquisition mechanism can change without changing this Skill.

## Evidence Gate

The Runtime Evidence Gate determines active requirements, evaluates scope, materializes typed Observations, checks schema/freshness, preserves provenance, and returns `UNKNOWN` when required proof cannot be established.

Observation acquisition is separately bounded and traced even though it is not a business Procedure action.

CEL therefore evaluates a prepared typed context and normally returns:

```text
true  -> PASS
false -> FAIL
```

## Why there is no Python evaluator

Iteration, simple branching, enum comparison, and urgency-dependent boolean conditions are not sufficient reasons to introduce a script. Python is reserved for predicates whose semantic branching, cross-object correlation, conflict handling, or diagnostic output would make CEL difficult to audit.

This Skill demonstrates the lightweight end of the target assurance authoring model: one `PredicateSet`, scoped typed Observations, CEL, and no custom evaluator script.
