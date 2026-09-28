---
name: 5gc-intent
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
     -> admitted read-only Tools when needed
     -> final Skill input
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
2. Skill routing does **not** need to convert a user-visible participant name/alias into IMSI merely to choose a semantic Skill. For example, "send a file to Leo" is already sufficient to route to `5gc-file-transfer`.
3. Preserve user-visible participant references from the Goal. Do not invent canonical identifiers and do not use remembered/static IMSIs.
4. A request-supplied `roster`, when present, is compatibility/demo identity context only. It is not the target architecture's authoritative name->IMSI dependency, and its IMSIs must not be assumed stable across Environments or Trials.
5. After a Skill is selected and its model context is loaded, that Skill's planning phase may use admitted read-only identity capabilities such as `ue.identity.lookup` to resolve a name/alias to the **current** canonical IMSI.
6. Preserve gateway-owned business correlation identifiers, such as `transferId`, when the selected Skill requires them. Do not synthesize them from the routing `requestId`.
7. Prefer the narrowest applicable admitted/certified Variant, then the applicable base Skill, then another governed Skill that explicitly covers the goal.
8. Produce only context known from the user/gateway at routing time. Do not invent Skill policy constants, runtime-derived network state, ProviderBinding values, deployment details, or a current IMSI that has not been supplied or governedly resolved.
9. If the Goal does not identify a required participant at all, return `NEEDS_CONTEXT`. If a later governed identity lookup returns `NOT_FOUND` or `AMBIGUOUS`, the planning phase must request/retain additional context instead of guessing.
10. If no governed target supports the requested behavior, return `NEEDS_EXTENSION` rather than constructing raw SBI, database, shell, MCP, or vendor-private bypass operations.

Semantic normalization may create request facts; it must not invent current network state such as registration, PDU Session, UE IP, QoS, virtual-group status, or mutable identity bindings.

## Routing result

The model-facing routing payload follows `schemas/agent-routing-result.schema.yaml` and uses:

```text
RESOLVED
NEEDS_CONTEXT
NEEDS_EXTENSION
```

A `RESOLVED` result identifies the selected Skill and optional Variant/entrypoint. It may carry normalized planning context that is already known from the Goal/gateway, but that context is **not required to be the selected Skill's final execution request**. Final Skill input is produced only after the selected Skill context is loaded and any required governed read-only lookup has completed.

The routing result does not grant execution authority. Runtime still admits the immutable Artifact/Variant identity, resolves ProviderBinding, and owns deterministic execution.

The canonical benchmark evidence family for routing is `agent.routing_result@1`; this Skill-local schema describes the routing payload semantics, not a new top-level cross-repository contract.

Representative inputs and routing results are under `references/samples/`. The retained roster fixture is compatibility/demo material only.
