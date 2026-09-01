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
participants registered
  -> participants have active PDU sessions
  -> edge cache ready
  -> virtual group created
  -> member addresses assigned
  -> optional QoS boost for urgent requests
  -> goal verification
```

Virtual-group activation is intentionally outside this Skill. The gateway decides activation after the receiver-confirmation phase.

### `release_group`

The goal is to make the target virtual group semantically released or absent.

`already released` and `not found` are normalized by the Capability/Provider to successful release semantics. The model does not match human-readable result strings.

## 3. Dynamic participants are not a model loop

`receiverImsis` is dynamic, but the model does not maintain a `for each receiver` execution loop.

P0 uses aggregate observation Capabilities:

- `transfer.participants.registration.query`;
- `transfer.participants.session.query`.

The Provider must deterministically query every member of the normalized participant set and produce aggregate Evidence:

```text
all members PASS    -> aggregate PASS
any member FAIL     -> aggregate FAIL
otherwise           -> aggregate UNKNOWN
```

The observation order must be stable: sender first, then receivers in canonical `receiverImsis` order. This keeps replay and audit deterministic.

If the Procedure DSL later gains governed bounded collection expansion, this behavior can move from Provider-side deterministic expansion to compile-time Procedure expansion. Until then, no non-standard Runtime node type is introduced for receiver iteration.

## 4. Data flow from virtual-group creation

`virtual_group.create` must return a structured canonical `groupId` and contribute it through Context/Fact normalization as:

```text
facts.virtual_group.id
```

`virtual_group.assign_members` consumes that fact. It must never recover the group identifier by parsing a human-readable Tool result.

If the gateway requires a `vg-YYYYMMDD-NNN` representation, the output adapter renders it from structured `groupId`.

## 5. UNKNOWN handling

Every mutation follows the Runtime UNKNOWN model:

```text
mutation OUTCOME_UNKNOWN
  -> reconcile
  -> COMMITTED / NOT_COMMITTED / UNRESOLVED
```

A non-idempotent mutation never jumps directly from UNKNOWN back to the original mutation node.

QoS boost and virtual-group release preserve the old at-most-once business-dispatch rule. Even if reconciliation proves `NOT_COMMITTED`, the current governed Procedure does not dispatch the original boost or release mutation again; it fails or stops safely according to the frozen graph.

## 6. Generic 5GC intent is a separate Skill

`[TASK: 5GC-INTENT]` has a much broader semantic scope than file transfer and must not share this Skill's execution envelope.

Generic 5GC intent handling belongs to the separate `core5g-intent` Skill, which owns intent interpretation and governed execution-target selection without inheriting raw SBI authority.
