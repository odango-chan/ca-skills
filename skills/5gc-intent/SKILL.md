---
name: core5g-intent
description: Interpret generic gateway 5GC intents and propose the best governed execution target, preferring certified Skills and Variants over ad-hoc network operations.
---

# 5GC Intent

## Goal

Turn a generic `[TASK: 5GC-INTENT]` request into a structured `ExecutionTargetCandidate` for deterministic Runtime admission.

This is an Agent-side intent-routing Skill. It decides what governed capability package should handle the request; it does not itself advance a network Procedure program counter, call NF Providers, or perform deterministic business execution.

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
4. Produce a structured `ExecutionTargetCandidate` identifying the proposed Skill, optional Variant/entrypoint, and canonical target request.
5. If no governed target can satisfy the intent, return `NEEDS_EXTENSION` rather than fabricating a raw Tool sequence.

A generic intent must not be converted directly into `sbi_request`, NF-specific HTTP paths, database writes, process-management calls, or vendor-private commands.

## Selection principles

### Prefer governed reuse

If a specialized Skill already exists, use it instead of rebuilding its workflow dynamically.

Examples:

```text
large-file transfer
  -> core5g-file-transfer

ensure PDU Session QoS
  -> ensure-session-qos

initial UE registration
  -> ue-registration
```

A reusable CompiledProcedureVariant is also preferred when its selection descriptor and eligibility rules match the current request.

### Keep Skill selection separate from Provider binding

The routing decision proposes semantic execution assets:

```text
Skill / Variant / Entrypoint
```

It does not select a concrete free5GC/Open5GS/vendor endpoint. Provider Binding remains a Runtime/deployment decision after admission.

### Do not use a universal SBI escape hatch

Generic `sbi_request(method, path, target, body)` is intentionally not part of this Skill's authority surface.

If a new intent requires a network operation that is not represented by a governed Skill or stable Capability, that is an extension gap, not permission to bypass the Capability/Assurance boundary.

## Intent normalization

Natural-language interpretation may normalize:

- requested network goal;
- target UE or participant set;
- QoS/deadline/urgency semantics;
- resource or service scope;
- explicit constraints from the gateway request.

Canonical identifiers from the gateway/runtime context are preferred over copied natural-language aliases.

Normalization does not create authoritative network facts. Current network state must come from Runtime-governed facts or Observations when the selected executable Skill runs.

## Output contract

The Agent output is a candidate, not an admitted execution target.

The package defines:

```text
schemas/execution-target-candidate.schema.yaml
```

A resolved candidate contains:

```text
requestId
status = RESOLVED
target.skill
target.variant? 
target.entrypoint?
request
```

If no governed target can satisfy the intent, return:

```text
status = NEEDS_EXTENSION
reasonCode = ...
```

The Agent must not assert that the candidate is admitted, qualified, executable, or safe merely because it selected it.

## Deterministic admission boundary

After this Skill proposes a candidate:

```text
core5g-intent
  -> ExecutionTargetCandidate
  -> deterministic Target Admission
  -> admitted ExecutionTarget
  -> selected assurance-enabled Skill
  -> RunPlan materialization
  -> deterministic Procedure execution
  -> Provider Binding / dispatch
```

Target Admission validates at least:

- the proposed Skill exists and resolves to an available governed artifact;
- an explicitly selected Variant/entrypoint exists and is eligible;
- the candidate request conforms to the target Skill input schema;
- the target authority and required semantic dependencies can be admitted in the current environment;
- the selected artifact/variant satisfies the applicable qualification and policy requirements.

A rejected candidate is returned to the Agent/routing layer or reported as `NEEDS_EXTENSION`; it never crosses directly into side-effect execution.

The key trust boundary is:

```text
LLM may propose the wrong target
but it cannot make that target executable by assertion
```

## No Execution Assurance Extension here

This Skill intentionally has no `assurance/` directory.

Its primary work is semantic interpretation and routing, which is intentionally Agentic rather than forced into a deterministic Procedure. Deterministic safety starts at Target Admission and continues inside the selected executable Skill's optional Execution Assurance Extension.

This also means routing quality and intent-to-Skill correctness belong primarily to Agent/Benchmark evaluation, while admission safety and business execution reliability belong to Runtime/Assurance evaluation.

## Current fallback behavior

The first governed version is routing-first:

```text
matching governed target -> RESOLVED candidate
no matching governed target -> NEEDS_EXTENSION
```

A future version may support bounded run-scoped capability planning through the formal Agent `PlanDelta` / Runtime `RunPlanRevision` path. That capability must be added explicitly; it must not be simulated by broadening this Skill's Tool authority.

## References

The routing and normalization model is preloaded from `references/preload/intent-routing-model.md`.

Representative mappings are documented in `examples/`.

The final source of truth for Skill/Variant availability, eligibility, Capability compatibility, Provider Binding, Target Admission, and Runtime execution remains the corresponding Registry/Artifact/Runtime contract.
