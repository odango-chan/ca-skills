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

- requiring proof that the sender and every receiver are registered;
- requiring proof that the sender and every receiver have an active PDU session;
- preparing the edge cache;
- creating a virtual group;
- assigning canonical IMSI/IP membership;
- requesting a QoS boost only when urgency has been positively established;
- releasing the specified virtual group for a release request.

This Skill does not choose how registration/session/state observations are acquired. Runtime `ObservationBinding` resolves those canonical Observation requirements for the active deployment.

This Skill does not read or write file bytes, message users, start or stop network processes, modify subscriber databases, or invoke Wi-Fi capabilities.

## Intent normalization

Before deterministic execution starts, a `prepare_transfer` request must contain canonical urgency:

- `urgent`: the original user intent explicitly expresses urgency, such as ASAP, urgent, quickly, hurry, fast, or an equivalent expression in another language;
- `normal`: no explicit urgency was established.

A large file is not automatically urgent.

The normalized value is frozen for the run. The Procedure does not re-interpret natural language during execution.

## Execution principles

1. `prepare_transfer` and `release_group` use governed deterministic Procedures. The model does not assemble an ad-hoc Tool-call sequence at execution time.
2. Participant registration and PDU Session checks are `verify` checkpoints. Runtime materializes the required typed participant Observations through `ObservationBinding`; the Procedure does not contain separate query actions merely to feed verification.
3. Dynamic participant count is not a model loop. The Observation provider may deterministically fan out over the canonical participant set while Runtime still receives one typed collection Observation.
4. Concrete `nf_udm_*`, `edge_cache_*`, `vg_*`, and `pcf_*` Tool names are Provider/Binding details, not stable Procedure semantics.
5. `virtual_group.activate` is outside this Skill. The gateway decides activation after receiver confirmation.
6. QoS boost exists only on the `urgent` deterministic path and may be dispatched at most once.
7. A mutation returning `OUTCOME_UNKNOWN` must never be blindly replayed. The Procedure enters its governed reconciliation path when one exists, otherwise it stops safely.
8. `already released` and `not found` are normalized by the release Capability/Provider as successful release semantics; the model never parses those strings.
9. Gateway-specific text rendering such as `vg-YYYYMMDD-NNN` belongs to the output adapter. Runtime and Skill logic use structured `groupId` values.
10. Gateway-provided IMSI/IP membership is authoritative after request normalization and Schema validation. A static phone roster must not override live gateway data.
11. Success means the final request predicate is proven, not merely that the last Tool returned a success-looking string.

## Execution assurance extension

This Skill adds an optional machine-readable assurance layer alongside the standard Skill surface:

```text
assurance/
├── contract.yaml    -> authority and goal envelope
├── procedure.yaml   -> governed deterministic execution flow
└── predicates.yaml  -> Observation requirements and Predicate evaluators
```

The `assurance/` directory describes execution assurance for a dual-engine Agent architecture. It is not a ConnectionAgent-specific namespace and does not replace `SKILL.md`.

There is no standalone `evidence.yaml` in the target model. Concrete Evidence is assembled at runtime from the Observation requirements declared beside each Predicate.

## References

The core orchestration model is preloaded from `references/preload/orchestration-model.md`.

The migration mapping between stable Capabilities/Observations and the current SBI-proxy NF/VG/PCF Tools is documented in `references/on-demand/sbi-proxy-provider-mapping.md`. That document is implementation guidance, not the Runtime Binding Truth Source.

The target typed-Observation / CEL / Python Predicate split used by this Skill is documented in `references/on-demand/predicate-evaluation.md`.

Procedure structure, predicates, budgets, UNKNOWN handling, recovery semantics, Capability Binding, and Observation Binding remain machine-contract concerns rather than prompt instructions.

## Short examples

- Normal transfer: verify all participants -> prepare edge cache -> create virtual group -> assign members -> verify the goal. No QoS boost is dispatched.
- Urgent transfer: the same governed path, followed by at most one QoS boost before final verification.
- Virtual-group release: dispatch one governed release mutation; if its outcome becomes ambiguous, reconcile or stop safely rather than replaying release.
