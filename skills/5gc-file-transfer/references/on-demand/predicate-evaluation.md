# Predicate Evaluation

This Skill is authored against the target Predicate model:

```text
EvidenceRules -> typed observations -> Predicate evaluator -> PASS / FAIL / UNKNOWN
```

It intentionally does not preserve the legacy scalar `valueType + rules` authoring shape.

## CEL predicates

CEL is used when the judgement remains a small, directly auditable boolean expression.

### Request routing predicates

These predicates depend only on the normalized request and therefore do not require `EvidenceRules` entries:

```text
transfer.operation.prepare
transfer.operation.release
transfer.intent.urgent
```

### Participant readiness

`transfer.participants.registered` evaluates the typed `participants` observation with CEL collection aggregation:

```text
observations.participants.all(p,
  p.registrationState == "REGISTERED"
)
```

`transfer.participants.pdu_sessions_active` uses the same pattern for PDU Session state.

Missing, stale, invalid, or unavailable required participant observations are handled by the Runtime Evidence Gate and produce `UNKNOWN` before CEL evaluation.

## Python predicate

`file_transfer.request.satisfied` remains a Python evaluator because it combines:

- prepare vs. release operation semantics;
- virtual-group state;
- member-assignment state;
- urgency-dependent QoS requirements;
- stable diagnostic reason codes.

The script is `scripts/evaluate_transfer_request_satisfied.py`.

It consumes the same target `PredicateEvaluationContext` used by CEL:

```text
request
subject
facts
observations
evidence
```

The script performs deterministic local computation only. It cannot acquire evidence or dispatch Tools/Capabilities.

## Required observations

The target `evidence.yaml` uses named typed observations.

For participant predicates, `participants` resolves to canonical participant-set observations.

For the final request predicate:

- `virtualGroup` is always required;
- `qosBoost` is conditionally required only for an urgent `prepare_transfer` request.

The Runtime Evidence Gate resolves these requirements before the evaluator executes.

## Design rule

Do not use Python merely because a predicate iterates over a collection. CEL collection macros are preferred when the result is still a simple boolean judgement.

Use Python when the semantic branching or diagnostic output is materially richer than a readable CEL expression.
