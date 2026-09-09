---
name: core5g-intent
description: Interpret a generic 5GC intent and guide Agent-owned routing to the narrowest admitted governed Skill or Variant.
---

# 5GC Intent Routing Policy

## Purpose

Provide model-visible routing policy for generic `[TASK: 5GC-INTENT]` requests.

Routing is owned by the Agent Host. This package is **not** a Runtime execution hop and does not execute a Procedure before another Skill. The Agent uses routing policy to choose from Runtime-discovered/admitted Skills, then loads the selected Skill context, plans its entrypoint/input, and hands the admitted artifact identity to `RuntimeHost` for governed execution.

In other words:

```text
Goal / generic 5GC intent
  -> Agent routing
  -> routing result
  -> selected admitted Skill / Variant
  -> load selected Skill context
  -> planning
  -> RuntimeHost
```

Do not model this as:

```text
routing Skill execution
  -> ExecutionTargetCandidate
  -> ExecutionTarget
  -> second Skill execution
```

Those are not current cross-repository machine contracts.

## Use when

Use this routing policy only for generic:

```text
[TASK: 5GC-INTENT]
```

Already-classified tasks such as `5GC-FILE-TRANSFER`, `5GC-VG-RELEASE`, or `WIFI-TRANSFER` should be routed directly to their specialized governed Skills.

## Routing policy

1. Normalize the user's goal, subjects, participants, urgency, QoS, deadlines, and other explicit constraints.
2. Resolve names or aliases only from identity context supplied with the request, such as the live `roster`. Never invent a canonical identifier.
3. Treat the roster as identity context only. Do not infer or copy current UE IP/session state into the selected Skill request; execution-time network values belong to governed Runtime resolution.
4. Preserve gateway-owned business correlation identifiers, such as `transferId`, when the selected Skill requires them. Do not synthesize them from the routing `requestId`.
5. Prefer the narrowest applicable admitted/certified Variant, then the applicable base Skill, then another governed Skill that explicitly covers the goal.
6. Produce canonical business input containing only values known from the user/gateway context. Do not invent Skill policy constants, runtime-derived network state, ProviderBinding values, or deployment details.
7. If required identity or business context is missing or ambiguous, return `NEEDS_CONTEXT` rather than guessing.
8. If no governed target supports the requested behavior, return `NEEDS_EXTENSION` rather than constructing raw SBI, database, shell, MCP, or vendor-private bypass operations.

Semantic normalization may create request facts; it must not invent current network state such as registration, PDU Session, UE IP, QoS, or virtual-group status.

## Routing result

The model-facing routing payload follows `schemas/agent-routing-result.schema.yaml` and uses:

```text
RESOLVED
NEEDS_CONTEXT
NEEDS_EXTENSION
```

A `RESOLVED` result identifies the selected Skill, optional Variant/entrypoint, and canonical business request. It does not grant execution authority. Runtime still admits the immutable Artifact/Variant identity, resolves ProviderBinding, and owns deterministic execution.

The canonical benchmark evidence family for routing is `agent.routing_result@1`; this Skill-local schema describes the routing payload semantics, not a new top-level cross-repository contract.

Representative inputs, routing results, and demo identity context are under `references/samples/`.
