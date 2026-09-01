# 5GC Intent Routing Model

## 1. Purpose

`core5g-intent` is a semantic routing layer between a generic gateway intent and a governed ConnectionAgent execution asset.

It is not a universal network Tool wrapper.

```text
[TASK: 5GC-INTENT]
  -> intent normalization
  -> Skill / Variant catalog resolution
  -> ExecutionTarget
  -> Runtime admission
```

## 2. Prefer the narrowest governed target

Selection priority:

```text
applicable certified Variant
  -> applicable certified Base Skill
  -> other governed Skill explicitly covering the goal
  -> NEEDS_EXTENSION
```

A more specialized Skill is preferred over a broad generic target when both can satisfy the same request.

Examples:

```text
"prepare a large file transfer"
  -> core5g-file-transfer

"ensure this UE has 5QI 8"
  -> ensure-session-qos

"register this UE"
  -> ue-registration
```

## 3. Intent facts are not network facts

The model may normalize semantic request facts such as:

```text
goal
subject
participants
urgency
deadline
requested QoS
```

It must not invent authoritative current-state facts such as:

```text
UE is registered
PDU Session exists
QoS is already satisfied
virtual group exists
```

Those facts belong to Context/Evidence Providers.

## 4. Selection is separate from binding

The Agent resolves an execution asset:

```text
Skill
Artifact
Entrypoint
Base or Variant
```

Runtime later resolves Provider Binding.

The intent router must not select a concrete vendor endpoint or embed credentials.

## 5. No generic SBI bypass

A missing governed operation is represented as an extension gap.

Do not translate a novel intent into arbitrary:

```text
sbi_request
HTTP method + NF path
vendor-private command
raw database mutation
```

A new reusable network behavior should enter the system as a stable Capability and/or governed Skill/Variant with explicit authority and qualification.

## 6. Future run-scoped planning

The routing-first version intentionally fails closed when no governed execution target exists.

If ConnectionAgent later enables bounded ad-hoc capability planning for generic 5GC intents, it should use the formal control path:

```text
Agent decision
  -> PlanDelta / governed proposal
  -> Runtime validation
  -> RunPlanRevision
  -> deterministic execution
```

That future mechanism must remain distinct from reusable ProcedurePatch/Variant compilation.
