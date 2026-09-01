# Predicate Evaluation

This Skill uses the target three-file machine model:

```text
contract.yaml
procedure.yaml
predicates.yaml
```

`predicates.yaml` contains both the canonical Observation requirements and the evaluator that consumes them. There is no standalone `evidence.yaml` and no legacy scalar `valueType + rules` authoring shape.

## CEL is sufficient here

Both Wi-Fi predicates are simple enough to remain CEL expressions.

`transfer.intent.urgent` depends only on the normalized request:

```text
request.urgency == "urgent"
```

It needs no environment Observation declaration.

`wifi_transfer.request.satisfied` declares the typed inputs beside its CEL evaluator:

```yaml
observations:
  transfer:
    ref: wifi.transfer.snapshot
    freshness: 5s
  qosBoost:
    ref: wifi.qos.boost_state
    freshness: 5s
    when: request.urgency == "urgent"
```

and evaluates:

```text
observations.transfer.state == "CREATED" &&
(request.urgency == "normal" ||
 observations.qosBoost.state == "COMMITTED")
```

The `qosBoost` Observation is required only for urgent requests.

## Evidence Gate and ObservationBinding

The Skill declares **what canonical Observation is required**, not which Tool should be called to obtain it.

Runtime/deployment `ObservationBinding` may satisfy `wifi.transfer.snapshot` or `wifi.qos.boost_state` from an earlier governed action result, runtime state, signaling, replay data, or a read-only deployment-specific query.

The Runtime Evidence Gate determines active Observation requirements, materializes them through those bindings, checks schema/freshness, preserves provenance, and returns `UNKNOWN` when required evidence cannot be established.

CEL therefore evaluates a prepared typed context and normally returns:

```text
true  -> PASS
false -> FAIL
```

## Why there is no Python evaluator

Iteration, simple branching, enum comparison, and urgency-dependent boolean conditions are not sufficient reasons to introduce a script. Python is reserved for predicates whose semantic branching, cross-object correlation, conflict handling, or diagnostic output would make CEL difficult to audit.

This Skill demonstrates the lightweight end of the target authoring model: one `PredicateSet`, typed Observations, CEL, and no custom evaluator script.
