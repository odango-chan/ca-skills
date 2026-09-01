---
name: wifi-file-transfer
description: Normalize receiver identities and urgency for a gateway-driven Wi-Fi transfer, then hand the canonical request to governed execution.
---

# WiFi File Transfer

## Purpose

Prepare the canonical request for the `wifiboost` gateway's Wi-Fi transfer workflow. The gateway owns consent, file bytes, timers, user interaction, and the broader transfer lifecycle.

## Use when

Use this Skill only for a request corresponding to:

```text
[TASK: WIFI-TRANSFER]
```

Do not use it for `5GC-*` tasks or ordinary human messages.

## Receiver normalization

Resolve receiver references against the live roster supplied with the task:

- a name or alias must resolve to exactly one roster member;
- a canonical 15-digit ID may be used directly when it exists in the roster;
- `everyone` means every roster member except the sender;
- never include the sender in `receiverIds`;
- if a receiver is unknown or ambiguous, do not guess.

The normalized execution request contains canonical `senderId` and `receiverIds`, not raw names or aliases.

## Urgency normalization

Normalize urgency to:

- `urgent` only when the source intent explicitly asks for accelerated completion, such as urgent, ASAP, hurry, or an equivalent expression;
- `normal` otherwise.

If urgency is uncertain, use `normal`.

Once receiver IDs and urgency are canonical, hand execution to the governed assurance entrypoint. Do not assemble Wi-Fi Tool calls from prose.

## References

- `references/preload/orchestration-model.md` -> normalization and orchestration model.
- `references/on-demand/wifiboost-provider-mapping.md` -> current provider migration mapping.
- `references/on-demand/predicate-evaluation.md` -> target Predicate/Observation evaluation details.
