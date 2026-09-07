---
name: core5g-intent
description: Interpret a generic 5GC intent and propose the narrowest governed Skill or Variant that can handle it.
---

# 5GC Intent

## Purpose

Route a generic `[TASK: 5GC-INTENT]` request to a governed execution target. This Skill performs semantic interpretation and produces an `ExecutionTargetCandidate`; it does not execute network Procedures itself.

## Use when

Use this Skill only for:

```text
[TASK: 5GC-INTENT]
```

Already-classified tasks such as `5GC-FILE-TRANSFER`, `5GC-VG-RELEASE`, or `WIFI-TRANSFER` should go directly to their specialized Skills.

## Routing policy

1. Normalize the user's goal, subjects, participants, urgency, QoS, deadlines, and other explicit constraints.
2. Resolve names or aliases only from identity context supplied with the request, such as the live `roster`. Never invent a canonical identifier.
3. Treat the roster as identity context only. Do not infer or copy current UE IP/session state into the target request; execution-time network values belong to governed Runtime resolution.
4. Preserve gateway-owned business correlation identifiers, such as `transferId`, when the selected target requires them. Do not synthesize them from the routing `requestId`.
5. Prefer the narrowest applicable certified Variant, then the applicable base Skill, then another governed Skill that explicitly covers the goal.
6. Produce a canonical target request containing only business inputs that are known from the user/gateway context. Do not invent Skill policy constants, runtime-derived network state, or deployment binding values.
7. If required identity or business context is missing or ambiguous, return `NEEDS_CONTEXT` rather than guessing.
8. If no governed target supports the requested behavior, return `NEEDS_EXTENSION` rather than constructing raw SBI, database, shell, or vendor-private operations.

Semantic normalization may create request facts; it must not invent current network state such as registration, PDU Session, UE IP, QoS, or virtual-group status.

## Output

Return an `ExecutionTargetCandidate` matching `schemas/execution-target-candidate.schema.yaml`.

A `RESOLVED` candidate proposes a Skill, optional Variant/entrypoint, and canonical target request. It is still only a proposal: Runtime admission decides whether it may execute.

Representative inputs and demo identity context are under `references/samples/`.
