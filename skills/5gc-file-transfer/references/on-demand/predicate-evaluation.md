# Predicate Evaluation

This Skill is authored against the target three-file machine model:

```text
contract.yaml   -> authority and goal envelope
procedure.yaml  -> execution flow
predicates.yaml -> Observation requirements + evaluator
```

There is no standalone `evidence.yaml` and no legacy scalar `valueType + rules` authoring shape.

## PredicateSet owns proof requirements

Each Predicate may declare the canonical typed Observations it needs beside the evaluator that consumes them.

Example:

```yaml
file_transfer.request.satisfied:
  observations:
    virtualGroup:
      ref: virtual_group.snapshot
      freshness: 5s
    qosBoost:
      ref: transfer.qos.boost_state
      freshness: 5s
      when: request.operation == "prepare_transfer" && request.urgency == "urgent"
  evaluator:
    type: script
    ref: skill.evaluate-transfer-request-satisfied
```

The alias (`virtualGroup`, `qosBoost`) becomes a typed field under `PredicateEvaluationContext.observations`.

The Skill specifies semantic requirements such as Observation ID, freshness, and a request-dependent `when` condition. It does **not** specify the concrete acquisition path.

## Observation acquisition

Runtime/deployment `ObservationBinding` maps canonical Observation IDs to concrete sources such as:

- existing governed action results;
- runtime state;
- signaling observations;
- replay data;
- deployment-specific read/query Providers.

The Runtime Evidence Gate resolves the active requirements, materializes the observations, checks schema/freshness, and preserves provenance metadata.

Missing, stale, invalid, or unavailable required Observations produce `UNKNOWN` before normal evaluator execution.

This is why participant registration and PDU Session checks are now direct `verify` nodes in `procedure.yaml`: the Procedure does not need separate query actions merely to feed a Predicate.

## CEL predicates

CEL is used when the judgement remains a small, directly auditable boolean expression.

Request-only predicates require no Observation declaration:

```text
transfer.operation.prepare
transfer.operation.release
transfer.intent.urgent
```

Participant registration uses collection aggregation:

```text
observations.participants.all(p,
  p.registrationState == "REGISTERED"
)
```

PDU Session readiness uses the same pattern over the typed participant-session Observation.

Collection iteration alone is not a reason to introduce Python.

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

Here `observations` contains business values and `evidence` contains provenance/audit metadata for those values.

The script performs deterministic local computation only. It cannot acquire Observations, dispatch Tools/Capabilities, retry mutations, or modify Runtime Context.

## Design rule

Use CEL while the judgement is still easy to audit as one expression.

Use Python when semantic branching, correlation, conflict handling, or diagnostic output would make CEL materially less clear.

Keep acquisition outside both evaluator forms. Evaluators judge prepared canonical data; `ObservationBinding` decides how a deployment obtains that data.
