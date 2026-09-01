# Wifiboost Provider Mapping

This document records the migration mapping from the legacy prompt-driven Wi-Fi Skill to stable ConnectionAgent Capability semantics.

It is not the Runtime Binding Truth Source. Production binding belongs to Runtime/deployment configuration.

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

### Reliability gap

If the Tool dispatch succeeds but its response is lost, the caller may not know the new transfer ID. Without a correlation-aware lookup, `wifi_status` cannot necessarily prove which transfer was created.

For that reason the current governed Procedure safe-stops on `OUTCOME_UNKNOWN` instead of replaying `wifi_transfer_create`.

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

## 3. Transfer status

Capability:

```text
wifi.transfer.status
```

Current Tool mapping:

```text
wifi_status(...)
```

This is read-only evidence. The Provider uses the strongest identifier available and maps the result to `wifi_transfer.request.satisfied`.

The exact status arguments are a Provider detail and must not be guessed by the Skill if the current Tool schema differs across deployments.

## 4. Tools intentionally excluded

The following capabilities are outside this Skill's execution envelope:

```text
filesystem / shell / exec
message / spawn / cron / web
nf_*
vg_*
pcf_*
open5gs_*
```

If the workflow later needs another network operation, add a stable Capability and governed Procedure change instead of widening the prompt Tool whitelist.
