# Predicate Evaluation

This Skill uses the target Predicate model and intentionally does not preserve the legacy scalar `valueType + rules` authoring shape.

## CEL is sufficient here

Both Wi-Fi predicates are simple enough to remain CEL expressions.

`transfer.intent.urgent` depends only on the normalized request:

```text
request.urgency == "urgent"
```

It therefore needs no environment Evidence.

`wifi_transfer.request.satisfied` evaluates typed observations:

```text
observations.transfer.state == "CREATED" &&
(request.urgency == "normal" ||
 observations.qosBoost.state == "COMMITTED")
```

The `qosBoost` observation is conditionally required only when `request.urgency == "urgent"`.

## Evidence Gate

The Runtime Evidence Gate is responsible for determining which observations are required for this evaluation, acquiring or reusing them, checking schema/freshness, and returning `UNKNOWN` when required evidence cannot be established.

CEL therefore operates only on a complete typed evaluation context and returns a boolean result:

```text
true  -> PASS
false -> FAIL
```

## Why there is no Python evaluator

The previous Python prototype was removed intentionally.

Iteration, simple branching, enum comparison, and urgency-dependent boolean conditions are not sufficient reasons to introduce a script. Python is reserved for predicates whose semantic branching, cross-object correlation, conflict handling, or diagnostic output would make CEL difficult to audit.

This Skill is meant to demonstrate the lightweight end of the target authoring model: typed Evidence plus CEL, with no custom evaluator script.
