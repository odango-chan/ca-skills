---
name: 5gc-file-transfer
description: Prepare or release governed 5GC resources for gateway-driven file transfers, with optional policy-governed QoS acceleration.
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

- A `prepare_transfer` request contains canonical sender/receiver IMSIs. Runtime endpoint state is resolved by governed execution rather than supplied as static identity data.
- `urgency` is a policy-governed normalized field. Follow the frozen model-visible Rule snapshot for the exact grounding policy; do not invent an urgency value from unsupported context.
- Receiver consent, file upload/download, user-visible messages, and the decision to activate a virtual group remain gateway responsibilities.
- `virtual_group.activate` is outside this Skill.
- After normalization, use the governed assurance entrypoint described by the frozen model-visible Rule snapshot and Tool/Skill context; do not invent ungoverned execution paths.

## Model-visible normative source

When this Skill is assembled for a model call, the Context Assembly result must include the applicable frozen model-visible Skill Rule snapshot and its digest. This Markdown is business guidance; it is not a second machine-authoritative copy of threshold values or violation taxonomy.

Provider implementation, ProviderBinding, ObservationBinding, Predicate execution, UNKNOWN/reconcile behavior, and deployment-specific Tool mappings are governed outside model context by the shared Platform/Runtime contracts.
