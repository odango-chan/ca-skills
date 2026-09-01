# Predicate Evaluation

This Skill uses the target **Execution Assurance Extension**:

```text
assurance/
├── contract.yaml
├── procedure.yaml
└── predicates.yaml
```

The extension is generic to a dual-engine Agent architecture. It is not a ConnectionAgent-specific namespace and does not replace the standard `SKILL.md` surface.

`assurance/predicates.yaml` contains canonical Observation requirements beside the evaluator that consumes them. There is no standalone `evidence.yaml` and no legacy scalar `valueType + rules` authoring shape.

## Procedure selection is direct CEL

Normal vs. urgent is not modeled as a named Predicate. It is already known from the canonical request and belongs directly to Procedure applicability:

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

`applicability.when` does not run the Evidence Gate or acquire Observations. It only selects the deterministic Procedure from already-admitted context.

`selectionPolicy: exactlyOne` requires exactly one Procedure to match before execution. Zero or multiple matches fail closed.

## CEL is sufficient for the proof Predicate

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

A named Predicate is used here because the final transfer state must be proven as an execution postcondition, not because CEL itself requires a Predicate wrapper.

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

This Skill demonstrates the lightweight end of the target assurance authoring model: direct Procedure applicability CEL, one proof Predicate, scoped typed Observations, CEL, and no custom evaluator script.
