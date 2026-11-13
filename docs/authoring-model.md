# Authoring Model — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The complete and authoritative business/Procedure authoring rules are maintained in the CA-SL specification. This file is retained as an implementation-oriented index only. If any wording here conflicts with the specification, the specification takes precedence.

Key boundaries:
- Procedure is the deterministic business execution graph.
- Tool Operations and Observation Queries are explicit callable contracts.
- Observation is a specialized read-only Tool query, not a parallel registry.
- Predicates are pure and consume explicitly bound inputs.
- Evidence is Host / Runtime governed and separate from business payload.
- Skill-level Wait / Await / polling is not part of vNext.
- Asynchronous completion belongs to the owning Tool / Provider / SMF Operation.
- Mutation outcomes that are unknown require Reconcile of the original mutation.
