---
name: 5gc-intent
description: Interpret generic gateway 5GC intents and resolve them to the best governed ConnectionAgent execution target, preferring certified Skills and Variants over ad-hoc network operations.
---

# 5GC Intent

## Goal

Turn a generic `[TASK: 5GC-INTENT]` request into a governed ConnectionAgent `ExecutionTarget` without giving the model direct SBI or Provider authority.

This is an Agent-side intent-routing Skill. It decides what governed capability package should handle the request; it does not itself advance a network Procedure program counter or call NF Providers.

## When to use

Use this Skill only when the gateway task is:

```text
[TASK: 5GC-INTENT]
```

Do not use it for already-classified transfer tasks such as `5GC-FILE-TRANSFER`, `5GC-VG-RELEASE`, or `WIFI-TRANSFER`. Those should route directly to their specialized Skills.

## Resolution policy

Resolve the intent in this order:

1. Normalize the user's goal and relevant entities from the gateway context.
2. Search the available Skill/Variant catalog for a governed target that already satisfies the goal.
3. Prefer the narrowest certified Skill/Variant whose applicability and authority envelope match the request.
4. Produce a structured `ExecutionTarget` identifying the selected Skill/Artifact/Variant entrypoint.
5. If no governed target can satisfy the intent, return `NEEDS_EXTENSION` rather than fabricating a raw Tool sequence.

A generic intent must not be converted directly into `sbi_request`, NF-specific HTTP paths, database writes, process-management calls, or vendor-private commands.

## Selection principles

### Prefer governed reuse

If a specialized Skill already exists, use it instead of rebuilding its workflow dynamically.

Examples:

```text
large-file transfer
  -> 5gc-file-transfer

ensure PDU Session QoS
  -> ensure-session-qos

initial UE registration
  -> ue-registration
```

A reusable CompiledProcedureVariant is also preferred when its selection descriptor and eligibility rules match the current request.

### Keep Skill selection separate from Provider binding

The routing decision selects semantic execution assets:

```text
Skill / Artifact / Entrypoint / Base-or-Variant
```

It does not select a concrete free5GC/Open5GS/vendor endpoint. Provider Binding remains a Runtime/deployment decision.

### Do not use a universal SBI escape hatch

Generic `sbi_request(method, path, target, body)` is intentionally not part of this Skill's authority envelope.

If a new intent requires a network operation that is not represented by a governed Skill or stable Capability, that is an extension gap, not permission to bypass the Capability/Assurance boundary.

## Intent normalization

Natural-language interpretation may normalize:

- requested network goal;
- target UE or participant set;
- QoS/deadline/urgency semantics;
- resource or service scope;
- explicit constraints from the gateway request.

Canonical identifiers from the gateway/runtime context are preferred over copied natural-language aliases.

Normalization does not create authoritative network facts. Current network state must come from Context/Evidence Providers.

## Execution boundary

After this Skill resolves a target:

```text
5gc-intent
  -> ExecutionTarget
  -> Runtime admission
  -> RunPlan compile
  -> deterministic Procedure execution
  -> Provider Binding / dispatch
```

The Agent never advances the selected Procedure PC and never supplies authoritative operation outcomes.

## Current fallback behavior

The first governed version is routing-first:

```text
matching governed target -> resolve it
no matching governed target -> NEEDS_EXTENSION
```

A future version may support bounded run-scoped capability planning through the formal Agent `PlanDelta` / Runtime `RunPlanRevision` path. That capability must be added explicitly; it must not be simulated by broadening this Skill's Tool whitelist.

## References

The routing and normalization model is preloaded from `references/preload/intent-routing-model.md`.

Representative mappings are documented in `examples/`.

The final source of truth for Skill/Variant availability, eligibility, Capability compatibility, Provider Binding, and Runtime admission remains the corresponding Registry/Artifact/Runtime contract.
