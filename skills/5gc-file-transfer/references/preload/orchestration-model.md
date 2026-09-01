# 5GC File Transfer Orchestration Model

## 1. The request is normalized before execution

This Skill does not execute the raw gateway `[TASK: ...]` message directly.

Before Runtime admission, the Gateway/Agent Adapter normalizes the message into `file-transfer-request.schema.yaml`:

```text
raw gateway task
  -> task parsing
  -> intent normalization
  -> canonical request
  -> deterministic Procedure selection
```

`urgency` is restricted to `normal` or `urgent`. Natural language is not re-interpreted during Procedure execution.

## 2. Supported operations

### `prepare_transfer`

The goal is to prepare the network resources required by the transfer:

```text
verify participants registered
  -> verify active PDU sessions
  -> edge cache ready
  -> virtual group created
  -> member addresses assigned
  -> optional QoS boost for urgent requests
  -> goal verification
```

The participant verification checkpoints do not contain explicit query actions. Their `PredicateSet` entries declare scoped canonical Observations and Runtime materializes them through `ObservationBinding`.

Virtual-group activation is intentionally outside this Skill. The gateway decides activation after the receiver-confirmation phase.

### `release_group`

The goal is to make the target virtual group semantically released or absent.

`already released` and `not found` are normalized by the Capability/Provider to successful release semantics. The model does not match human-readable result strings.

## 3. Dynamic participants are bounded proof input, not a model loop

`receiverImsis` is dynamic, but the model does not maintain a `for each receiver` Procedure loop.

The Predicate requirements use scoped collection Observations:

```text
transfer.participants.registration
transfer.participants.session
```

with scope derived from:

```text
participantImsis = [senderImsi] + receiverImsis
```

The request schema bounds `receiverImsis`, so provider-side fan-out has a known maximum cardinality.

An ObservationBinding may deterministically query each participant and return one typed collection Observation. The concrete query mechanism is deployment-specific and is not a business Capability in this Skill.

Collection evaluation remains deterministic:

```text
CEL all(...) -> PASS or FAIL
missing/invalid/stale collection -> Evidence Gate UNKNOWN
```

Observation acquisition order and fan-out must be stable and traced. Runtime also applies a separate observation acquisition budget so moving proof queries out of the Procedure graph does not create hidden unbounded work.

If the Procedure DSL later gains governed bounded collection expansion for **business actions**, that is a separate feature. Verification-side collection observation does not require a new Procedure node type.

## 4. Data flow from virtual-group creation

`virtual_group.create` must return a structured canonical `groupId` and contribute it through Context/Fact normalization as:

```text
facts.virtual_group.id
```

`virtual_group.assign_members` consumes that fact. It must never recover the group identifier by parsing a human-readable Tool result.

Committed create/member-assignment results may also contribute a fresh `virtual_group.snapshot` Observation that final verification can reuse when it satisfies the Predicate freshness/proof policy.

If the gateway requires a `vg-YYYYMMDD-NNN` representation, the output adapter renders it from structured `groupId`.

## 5. UNKNOWN handling

Every mutation follows the Runtime UNKNOWN model:

```text
mutation OUTCOME_UNKNOWN
  -> reconcile
  -> COMMITTED / NOT_COMMITTED / UNRESOLVED
```

A non-idempotent mutation never jumps directly from UNKNOWN back to the original mutation node unless the relevant contract explicitly proves safe repetition.

QoS boost and virtual-group release preserve the old at-most-once business-dispatch rule. Even if reconciliation proves `NOT_COMMITTED`, the current governed Procedure does not dispatch the original boost or release mutation again; it fails or stops safely according to the frozen graph.

Verification UNKNOWN is different: missing/stale/invalid Observation or exhausted observation budget is handled by the Evidence Gate and then follows the Procedure's normal `UNKNOWN` transition.

## 6. Generic 5GC intent is a separate Skill

`[TASK: 5GC-INTENT]` has a much broader semantic scope than file transfer and must not share this Skill's execution envelope.

Generic 5GC intent handling belongs to the separate `core5g-intent` Skill, which owns intent interpretation and governed execution-target selection without inheriting raw SBI authority.
