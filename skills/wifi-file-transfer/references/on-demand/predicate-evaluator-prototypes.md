# Predicate Evaluator Prototype

This Skill includes `scripts/evaluate_wifi_transfer_satisfied.py` as a deterministic prototype for the planned script-backed Predicate evaluator model.

It is intentionally **not wired into Procedure `verify` nodes yet**. The current Runtime contract continues to use scalar `PredicateDefinitions` until script-backed Predicate evaluators are formally supported.

## What it demonstrates

The evaluator combines:

- transfer creation state;
- canonical urgency;
- QoS boost state.

For an urgent request, the transfer is satisfied only when transfer creation is proven and QoS boost is committed. Missing/ambiguous state returns `UNKNOWN`; a proven negative state returns `FAIL`.

The evaluator performs no tool calls. It receives canonical input values, calculates a tri-state result and returns stable reason codes for audit and UI use.

## Authority boundary

The script declares `effect: local_compute` and denied network access. Evidence acquisition, tool dispatch, timeout handling, reconciliation and Runtime Context mutation remain outside the script.
