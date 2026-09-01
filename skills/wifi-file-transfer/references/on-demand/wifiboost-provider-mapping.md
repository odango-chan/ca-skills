# Wifiboost Provider and Observation Mapping

This document records the migration mapping from the legacy prompt-driven Wi-Fi Skill to stable ConnectionAgent Capability and Observation semantics.

It is not a Runtime Binding Truth Source. Production `ProviderBinding` and `ObservationBinding` belong to Runtime/deployment configuration.

## 1. Transfer creation

Capability:

```text
wifi.transfer.create
```

Current Tool mapping:

```text
wifi_transfer_create(
  sender=<canonical senderId>,
  receivers=<canonical receiver IDs>
)
```

The old Tool accepted names and/or IDs as a comma-separated string. The governed Skill no longer relies on that ambiguity: names are resolved before execution and the Provider receives canonical IDs.

The Capability input also includes `requestId` as a stable correlation key. The legacy Tool may not currently accept this field; Provider support is required before ambiguous create outcomes can be reconciled reliably.

The canonical result must expose a structured transfer identifier and contribute:

```text
facts.wifi_transfer.id
```

A committed canonical result may also contribute a fresh:

```text
wifi.transfer.snapshot
```

Observation for later verification.

### Reliability gap

If the Tool dispatch succeeds but its response is lost, the caller may not know the new transfer ID. Without a correlation-aware lookup, `wifi_status` cannot necessarily prove which transfer was created.

For that reason the governed Procedure safe-stops on `OUTCOME_UNKNOWN` instead of replaying `wifi_transfer_create`.

## 2. QoS boost

Capability:

```text
wifi.qos.boost
```

Current Tool mapping:

```text
wifi_qos_boost(transfer_id=<facts.wifi_transfer.id>)
```

This action appears only in the urgent Procedure.

Legacy success strings including `recommended`, `already`, or `ok` are normalized by the Provider to committed success. The Procedure never retries a boost whose outcome is ambiguous.

A committed canonical result may contribute:

```text
wifi.qos.boost_state
```

as a typed Observation for final verification.

## 3. Transfer Observation

Canonical Observation:

```text
wifi.transfer.snapshot
```

One current acquisition mechanism is:

```text
wifi_status(...)
```

This mapping belongs to `ObservationBinding`, not to the Skill's business Capability whitelist. The exact status arguments and correlation mechanism are deployment/Provider concerns.

Runtime may reuse a fresh Observation contributed by `wifi.transfer.create`; otherwise it may use this read-only binding when the Evidence Gate needs a current snapshot.

## 4. QoS Observation

Canonical Observation:

```text
wifi.qos.boost_state
```

For an urgent run, Runtime may satisfy this requirement from the canonical `wifi.qos.boost` action result when it is fresh and valid. A deployment may later provide a stronger independent read path through ObservationBinding without changing the Skill Predicate.

Normal requests do not require this Observation because the Predicate requirement is conditional on `request.urgency == "urgent"`.

## 5. Binding rule

Keep business action and proof acquisition separate:

```text
wifi.transfer.create / wifi.qos.boost
  -> ProviderBinding
  -> governed Procedure actions

wifi.transfer.snapshot / wifi.qos.boost_state
  -> ObservationBinding
  -> typed proof inputs
```

The same underlying legacy service may implement both families, but the Skill depends only on the stable Capability or Observation semantic ID.

## 6. Tools intentionally excluded from business authority

The following operations are outside this Skill's governed business-action envelope:

```text
filesystem / shell / exec
message / spawn / cron / web
nf_*
vg_*
pcf_*
open5gs_*
```

Read-only `wifi_status` may exist behind ObservationBinding without becoming a directly callable Procedure resource.

If the workflow later needs another business operation, add a stable Capability and governed Procedure change instead of widening the prompt Tool whitelist.
