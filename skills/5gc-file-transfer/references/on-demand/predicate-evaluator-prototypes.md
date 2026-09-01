# Predicate Evaluator Prototypes

This Skill includes deterministic Python evaluator prototypes under `scripts/` to exercise the planned complex Predicate evaluation model.

They are intentionally **not wired into Procedure `verify` nodes yet**. The current Runtime contract still uses scalar `PredicateDefinitions`; the prototypes will become eligible once the shared Runtime and Skill Platform support script-backed Predicate evaluators.

## `skill.evaluate-participants-ready`

Purpose:

- aggregate registration and PDU Session observations for a dynamic participant set;
- return `FAIL` when a known negative observation exists;
- return `UNKNOWN` when any participant cannot be proven ready;
- return `PASS` only when every participant is registered and has an active PDU Session.

This demonstrates that collection iteration is acceptable inside a Predicate evaluator when the loop performs only deterministic calculation over already-supplied observations. It does not perform network observation or mutation.

## `skill.evaluate-transfer-request-satisfied`

Purpose:

- evaluate both `prepare_transfer` and `release_group` goals;
- combine virtual-group state, member assignment state, request urgency and QoS boost state;
- distinguish `FAIL` from `UNKNOWN` rather than collapsing incomplete evidence into a boolean.

This demonstrates contextual multi-observation judgement that is awkward to express as scalar equality rules.

## Authority boundary

Both scripts declare:

```text
effect: local_compute
sandbox.network: denied
```

They must not:

- call NF/VG/PCF/Wi-Fi tools;
- perform active observation;
- retry or reconcile mutations;
- modify Runtime Context;
- read host time or randomness for decision making.

Evidence acquisition remains a Runtime/Evidence Adapter responsibility. The scripts only judge canonical input values supplied by Runtime.
