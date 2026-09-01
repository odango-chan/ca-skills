---
name: core5g-file-transfer
description: Prepare and release governed 5GC network resources for SBI-proxy gateway file transfers; verify participant registration and PDU sessions, prepare the edge cache and virtual group, and request QoS boost only for canonical urgent intents.
---

# 5GC File Transfer

## Goal

Prepare the 5GC network resources required by a gateway-driven large-file transfer, and release the corresponding virtual group when the transfer completes or is cancelled.

This Skill owns only core-network orchestration. It does not own the file-transfer application lifecycle.

## When to use

Use this Skill for normalized gateway requests corresponding to:

- `[TASK: 5GC-FILE-TRANSFER]` -> `prepare_transfer`;
- `[TASK: 5GC-VG-RELEASE]` -> `release_group`.

`[TASK: 5GC-INTENT]` belongs to the separate `core5g-intent` Skill. Keeping generic 5GC intent handling separate prevents broad intent authority from leaking into the file-transfer execution envelope.

## Responsibility boundary

The gateway owns:

- receiver consent and confirmation;
- file upload, binding, and download;
- all user-visible messages;
- the decision to activate or end a transfer;
- parsing the gateway task and building the normalized request surface.

This Skill owns:

- proving that the sender and every receiver are registered;
- proving that the sender and every receiver have an active PDU session;
- preparing the edge cache;
- creating a virtual group;
- assigning canonical IMSI/IP membership;
- requesting a QoS boost only when urgency has been positively established;
- releasing the specified virtual group for a release request.

This Skill does not read or write file bytes, message users, start or stop network processes, modify subscriber databases, or invoke Wi-Fi capabilities.

## Intent normalization

Before deterministic execution starts, a `prepare_transfer` request must contain canonical urgency:

- `urgent`: the original user intent explicitly expresses urgency, such as ASAP, urgent, quickly, hurry, fast, or an equivalent expression in another language;
- `normal`: no explicit urgency was established.

A large file is not automatically urgent.

The normalized value is frozen for the run. The Procedure does not re-interpret natural language during execution.

## Execution principles

1. `prepare_transfer` and `release_group` use governed deterministic Procedures. The model does not assemble an ad-hoc Tool-call sequence at execution time.
2. Dynamic receiver count is not a model loop. `transfer.participants.*` observation capabilities accept the canonical participant set and the Provider performs deterministic per-member observation.
3. Concrete `nf_udm_*`, `edge_cache_*`, `vg_*`, and `pcf_*` Tool names are Provider/Binding details, not stable Procedure semantics.
4. `virtual_group.activate` is outside this Skill. The gateway decides activation after receiver confirmation.
5. QoS boost exists only on the `urgent` deterministic path and may be dispatched at most once.
6. A mutation returning `OUTCOME_UNKNOWN` must never be blindly replayed. The Procedure enters its governed reconciliation path when one exists, otherwise it stops safely.
7. `already released` and `not found` are normalized by the release Capability/Provider as successful release semantics; the model never parses those strings.
8. Gateway-specific text rendering such as `vg-YYYYMMDD-NNN` belongs to the output adapter. Runtime and Skill logic use structured `groupId` values.
9. Gateway-provided IMSI/IP membership is authoritative after request normalization and Schema validation. A static phone roster must not override live gateway data.
10. Success means the final request predicate is proven, not merely that the last Tool returned a success-looking string.

## References

The core orchestration model is preloaded from `references/preload/orchestration-model.md`.

The migration mapping between stable Capabilities and the current SBI-proxy NF/VG/PCF Tools is documented in `references/on-demand/sbi-proxy-provider-mapping.md`. That document is implementation guidance, not the Runtime Binding Truth Source.

Procedure structure, predicates, budgets, UNKNOWN handling, and recovery semantics are defined by `assurance/`, Runtime Capability Contracts, and Provider Bindings.

## Short examples

- Normal transfer: verify all participants -> prepare edge cache -> create virtual group -> assign members -> verify the goal. No QoS boost is dispatched.
- Urgent transfer: the same governed path, followed by at most one QoS boost before final verification.
- Virtual-group release: dispatch one governed release mutation; if its outcome becomes ambiguous, reconcile or stop safely rather than replaying release.
