---
name: 5gc-file-transfer
description: Prepare or release governed 5GC resources for gateway-driven file transfers, with optional QoS acceleration for normalized urgent requests.
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

- A `prepare_transfer` request carries canonical sender/receiver IMSIs and a normalized urgency classification. The exact grounding rules for model-produced fields are defined by the frozen model-visible RuleSet for this Skill.
- Current participant endpoint addresses are resolved during governed execution because they are runtime network state; callers provide identity, not a frozen endpoint roster.
- An urgent normalized request may add QoS acceleration before final goal verification. Exact urgency grounding policy, including any policy parameters, belongs to the frozen RuleSet rather than this Markdown file.
- Receiver consent, file upload/download, user-visible messages, and the decision to activate a virtual group remain gateway responsibilities.
- `virtual_group.activate` is therefore outside this Skill.
- Once a request is normalized, execution enters the governed assurance path. Exact model-facing no-bypass constraints are defined by the frozen RuleSet.

Provider implementation, ProviderBinding, ObservationBinding, Predicate execution, UNKNOWN/reconcile behavior, and deployment-specific Tool mappings are governed outside model context by the shared Platform/Runtime contracts.
