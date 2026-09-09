---
name: core5g-file-transfer
description: Prepare or release governed 5GC resources for gateway-driven file transfers, with optional QoS acceleration for explicitly urgent requests.
---

# 5GC File Transfer

## Purpose

Prepare the 5GC resources needed by a gateway-driven file transfer, or release the transfer's virtual group when it ends.

This Skill owns core-network orchestration only. The gateway owns the file-transfer application lifecycle.

## Use when

Use this Skill for normalized requests corresponding to:

- `[TASK: 5GC-FILE-TRANSFER]` -> `prepare_transfer`;
- `[TASK: 5GC-VG-RELEASE]` -> `release_group`.

Do not use it for generic `[TASK: 5GC-INTENT]` routing or Wi-Fi transfer tasks.

## Business semantics

- A `prepare_transfer` request must already contain canonical sender/receiver IMSIs. Current UE endpoint addresses are runtime network state and are not routing-model inputs.
- Governed execution resolves the current participant endpoint set before assigning virtual-group members. Do not copy IP addresses from a static identity roster.
- `urgent` means the source intent explicitly asks for accelerated completion, such as urgent, ASAP, hurry, or an equivalent expression. A large file by itself is not urgent.
- Receiver consent, file upload/download, user-visible messages, and the decision to activate a virtual group remain gateway responsibilities.
- `virtual_group.activate` is therefore outside this Skill.
- Once the request is normalized, hand execution to the governed assurance entrypoint. Do not construct ad-hoc NF/VG/PCF Tool sequences from prose.

Provider implementation, ProviderBinding, ObservationBinding, Predicate execution, UNKNOWN/reconcile behavior, and deployment-specific Tool mappings are governed outside model context by the shared Platform/Runtime contracts.
