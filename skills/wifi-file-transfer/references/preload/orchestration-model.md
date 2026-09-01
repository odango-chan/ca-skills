# WiFi File Transfer Orchestration Model

## 1. Interpretation ends before deterministic execution

The raw gateway task contains a live roster and the sender's natural-language intent. The Agent/Gateway Adapter normalizes that input before Runtime execution:

```text
raw WIFI-TRANSFER task
  -> identify sender from task envelope
  -> resolve receiver references against live roster
  -> canonical receiver IDs
  -> canonical urgency
  -> validated request
  -> deterministic Procedure selection
```

The deterministic Procedure never performs name resolution or natural-language urgency interpretation.

## 2. Receiver resolution

Receiver resolution is semantic, but the execution surface is canonical.

Rules:

- a named receiver resolves to exactly one live roster member;
- a 15-digit ID resolves directly if it exists in the live roster;
- `everyone` means every live roster member except the sender;
- the sender is never included in `receiverIds`;
- ambiguous or unknown aliases fail normalization instead of guessing.

The gateway's live roster is the authority for the current task. No static roster embedded in the Skill is a Runtime Truth Source.

## 3. Urgency

Urgency is normalized to:

```text
urgent
normal
```

Only explicit urgency produces `urgent`. Uncertainty falls back to `normal`.

The normalized value selects one of two governed Procedures:

```text
normal -> create transfer -> verify
urgent -> create transfer -> one QoS boost -> verify
```

## 4. Transfer identifier

`wifi.transfer.create` must return a structured canonical transfer identifier and contribute:

```text
facts.wifi_transfer.id
```

Downstream actions consume that fact. The model and Procedure never parse a transfer ID from a human-readable Tool string.

The gateway may render `tr-*` text from the structured identifier when producing its own response.

## 5. At-most-once mutations and UNKNOWN

The legacy workflow requires create and boost to be called at most once.

Therefore the current governed procedures use:

```text
mutation OUTCOME_UNKNOWN
  -> SAFE_STOPPED
```

rather than replaying either mutation.

A future Provider may replace this with explicit reconciliation only after it has an independently trustworthy correlation/observation mechanism. `wifi.status` alone is not automatically sufficient if the create response was lost before a transfer ID became known.

## 6. Gateway ownership

The Skill does not own consent, file bytes, upload/download flow, timers, receiver boost offers, or user messaging. Those remain gateway concerns.
