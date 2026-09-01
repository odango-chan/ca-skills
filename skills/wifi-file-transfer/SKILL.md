---
name: wifi-file-transfer
description: Coordinate gateway-driven Wi-Fi file-transfer setup by canonicalizing receiver identities and urgency, creating the transfer once, and requesting QoS boost only on the governed urgent path.
---

# WiFi File Transfer

## Goal

Create the Wi-Fi transfer context required by the `wifiboost` gateway and optionally request one QoS boost when the sender's original intent is explicitly urgent.

The gateway owns the user-facing transfer lifecycle. This Skill owns only the network-orchestration decision and deterministic execution boundary.

## When to use

Use this Skill only for a normalized request corresponding to:

```text
[TASK: WIFI-TRANSFER]
```

Do not use it for `5GC-*` tasks or ordinary human messages.

## Responsibility boundary

The gateway owns:

- consent dialogs and receiver interaction;
- file upload and file bytes;
- per-receiver boost offers;
- transfer timers;
- all user-visible messages;
- the live phone roster supplied with the task.

This Skill owns:

- resolving receiver references from the user intent;
- excluding the sender from the receiver set;
- expanding `everyone` to every other live roster member;
- canonicalizing receiver identities to stable 15-digit IDs before execution;
- canonicalizing urgency to `normal` or `urgent`;
- creating the Wi-Fi transfer exactly once per governed run;
- requesting at most one QoS boost on the urgent path.

## Receiver canonicalization

Natural-language names and aliases belong to the interpretation stage, not the deterministic Procedure.

Before execution, receiver references must be resolved against the live roster to canonical 15-digit IDs:

```text
"Leo"        -> 001019876543211
"Phone 2"    -> 001019876543211
"everyone"   -> every roster member except the sender
```

The final request contains `receiverIds`, not the raw receiver phrase. The Procedure and Provider must not perform a second independent name-resolution pass.

If a receiver cannot be resolved unambiguously, do not guess and do not start the transfer.

## Urgency canonicalization

Before deterministic execution, urgency is normalized to:

- `urgent`: the original user intent explicitly requests accelerated completion, such as urgent, ASAP, hurry, as fast as possible, or an equivalent expression in another language;
- `normal`: urgency was not positively established.

If interpretation is uncertain, use `normal`.

The Procedure never re-reads the original natural-language intent during execution.

## Execution principles

1. The model performs semantic normalization only. The transfer workflow itself is deterministic.
2. `wifi.transfer.create` is dispatched at most once in a run.
3. `wifi.qos.boost` exists only on the urgent deterministic path and is dispatched at most once.
4. Successful legacy strings such as `created`, `recommended`, `already`, or `ok` are normalized by the Provider; the model does not parse them.
5. A mutation that becomes `OUTCOME_UNKNOWN` is never blindly replayed. With the current legacy Tool surface, the governed behavior is safe stop unless the Provider can independently reconcile the mutation.
6. `wifi.status` is read-only evidence and may support final-state verification or future reconciliation.
7. The Skill never invokes filesystem, shell, process-management, messaging, 5GC NF/VG/PCF, cron, spawn, or web capabilities.
8. Success means the final Wi-Fi transfer request predicate is proven, not merely that a Tool returned a success-looking string.

## References

The normalization and execution model is preloaded from `references/preload/orchestration-model.md`.

The migration mapping from the current `wifiboost` Tools to stable Capability semantics is documented in `references/on-demand/wifiboost-provider-mapping.md`.

Procedure structure, authority, budgets, UNKNOWN handling, and Provider Binding remain machine-contract concerns rather than prompt instructions.

## Short examples

- `Send this to Leo`: canonicalize Leo to one receiver ID -> create transfer -> verify.
- `Send this to everyone as fast as possible`: canonicalize every non-sender roster member -> urgent path -> create transfer -> one QoS boost -> verify.
- Ambiguous receiver alias: do not create the transfer until the receiver identity is resolved.
