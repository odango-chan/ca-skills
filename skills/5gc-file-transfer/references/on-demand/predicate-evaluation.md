# Predicate Evaluation

This Skill uses the target **Execution Assurance Extension**:

```text
assurance/
├── contract.yaml   -> authority and goal envelope
├── procedure.yaml  -> governed execution flow
└── predicates.yaml -> Observation requirements + evaluator
```

The extension is intentionally generic to dual-engine Agent runtimes. It is not a ConnectionAgent-specific namespace and does not replace the standard `SKILL.md` surface.

There is no standalone `evidence.yaml` and no legacy scalar `valueType + rules` authoring shape.

## Procedure applicability is not a Predicate

Procedure selection uses CEL directly in `assurance/procedure.yaml`:

```yaml
spec:
  selectionPolicy: exactlyOne
  procedures:
  - name: prepare-file-transfer-normal
    applicability:
      when: >
        request.operation == "prepare_transfer" &&
        request.urgency == "normal"
```

`applicability.when` is a deterministic selector over already-admitted context. It does not create a named Predicate, does not run the Evidence Gate, and does not acquire Observations.

The selector environment is intentionally narrow:

```text
request
subject
initial/admitted facts
```

It must not depend on action-produced facts, `observations`, Evidence records, Provider results that have not happened yet, or Tool calls.

`selectionPolicy: exactlyOne` means all Procedure applicability expressions are evaluated before execution and exactly one Procedure must match. Zero or multiple matches fail closed.

This keeps values such as `request.operation` and `request.urgency` where they belong: Procedure selection rather than proof semantics.

## PredicateSet owns proof requirements

Named Predicates are reserved for conditions that the assurance engine must prove, reuse, or expose as verification results. They are referenced by `verify`, `decision`, or contract conditions such as pre/postconditions.

Each Predicate declares the canonical typed Observations it needs beside the evaluator that consumes them.

Example:

```yaml
file_transfer.request.satisfied:
  observations:
    virtualGroup:
      ref: virtual_group.snapshot
      scope: >
        {
          "transferId": request.transferId,
          "groupId": request.operation == "release_group"
            ? request.groupId
            : facts["virtual_group.id"]
        }
      freshness: 5s
    qosBoost:
      ref: transfer.qos.boost_state
      scope: >
        {"transferId": request.transferId}
      freshness: 5s
      when: request.operation == "prepare_transfer" && request.urgency == "urgent"
  evaluator:
    type: script
    ref: skill.evaluate-transfer-request-satisfied
```

The alias (`virtualGroup`, `qosBoost`) becomes a typed field under `PredicateEvaluationContext.observations`.

The requirement expresses:

- `ref`: what semantic Observation is needed;
- `scope`: which canonical object or collection must be observed;
- `freshness`: how recent the proof must be;
- `when`: when this requirement applies.

`scope` belongs to **what to observe**. It is not a Provider binding and must not contain Tool names or endpoints.

## Observation acquisition

Runtime/deployment `ObservationBinding` maps `Observation ID + scope` to concrete sources such as:

- existing governed action results;
- runtime state;
- signaling observations;
- replay data;
- deployment-specific read/query Providers.

The Runtime Evidence Gate resolves active requirements, evaluates scope, materializes observations, checks schema/freshness, and preserves provenance metadata.

Missing, stale, invalid, unavailable, or budget-exhausted required Observations produce `UNKNOWN` before normal evaluator execution.

This is why participant registration and PDU Session checks are direct `verify` nodes in `assurance/procedure.yaml`: the Procedure does not need separate query actions merely to feed a Predicate.

## Bounded participant observation

Participant Observation scopes are derived from the canonical request:

```text
participantImsis = [senderImsi] + receiverImsis
```

`receiverImsis` is bounded by the request schema, so provider-side fan-out has a known maximum cardinality. Observation acquisition remains independently budgeted and visible in Runtime trajectory events even though it is not a business Procedure action.

## CEL predicates

CEL is used when the proof judgement remains a small, directly auditable boolean expression.

Participant registration uses collection aggregation:

```text
observations.participants.all(p,
  p.registrationState == "REGISTERED"
)
```

PDU Session readiness uses the same pattern over the typed participant-session Observation.

Collection iteration alone is not a reason to introduce Python.

A Predicate may still read `request`, `subject`, or `facts` when those values are part of the proof context. The distinction is semantic: a named Predicate represents something that must be proven, not merely a branch selector.

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

`observations` contains business values. `evidence` contains scope/provenance/audit metadata for those values.

The script performs deterministic local computation only. It cannot acquire Observations, dispatch Tools/Capabilities, retry mutations, or modify Runtime Context.

## Design rule

Use `applicability.when` for deterministic Procedure selection from already-known canonical context.

Use a named Predicate when the condition is part of execution assurance: it must be verified, reused as a proof result, or enforced as a contract condition.

Use CEL while the proof judgement is easy to audit as one expression. Use Python when semantic branching, correlation, conflict handling, or diagnostic output would make CEL materially less clear.

Keep acquisition outside both evaluator forms. Evaluators judge prepared canonical data; `ObservationBinding` decides how a deployment obtains that data.
