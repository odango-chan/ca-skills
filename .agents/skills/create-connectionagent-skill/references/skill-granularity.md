# Skill Granularity

Use this note when deciding whether a requested behavior deserves a new official Skill package.

## Create a Skill when

Create an executable Skill when the model needs a reusable product/domain-level capability with meaningful semantics above primitive provider actions and with a governed deterministic execution contract.

Typical signals:

- the user goal has a stable domain meaning;
- the model must normalize or disambiguate business input;
- execution composes multiple governed actions or assertions;
- success needs explicit postconditions, `UNKNOWN` handling, or reconcile behavior;
- the capability is useful as a discoverable unit independent of one benchmark or one deployment.

## Keep it a Capability when

Keep a primitive operation in the Runtime Capability/Provider layer when it is mainly a low-level side effect or observation primitive with no independent product semantics.

Examples include a single protocol/provider action, a raw state read, or an environment-specific adapter operation.

Do not create one Skill per tool call merely to expose provider functions to the model.

## Keep routing as routing policy

Routing is Agent-owned selection behavior, not deterministic Runtime execution.

A routing-policy/model-context package may provide domain vocabulary, normalization, eligibility hints, ambiguity handling, or context requirements, but it is not executed first in order to produce authority for another Skill.

Do not reintroduce an `ExecutionTarget` handoff such as:

```text
routing Skill -> ExecutionTarget -> executable Skill
```

The current shape is:

```text
Goal
  -> Agent routing over admitted Skill descriptors
  -> routing result / context decision
  -> load selected Skill context
  -> plan entrypoint + input
  -> RuntimeHost
```

Historical routing packages under `skills/` are outside the current 5GC baseline and are not current authoring examples.

## Prefer composition over duplication

If two product behaviors share the same lower-level operation, keep the operation as a shared Capability and express different product semantics in their respective Skills.

If the difference is a governed reusable procedure structure over the same base Skill, consider ProcedurePatch / ProcedureVariant rather than cloning the entire Skill.

If the difference is deployment binding, endpoint, credential, or provider implementation, it is not a new Skill. Those concerns belong to Runtime/deployment ProviderBinding.

## Avoid benchmark-shaped Skills

A Benchmark scenario is not automatically a Skill. Benchmark assets may intentionally stress one failure mode, inject faults, or demand independent evidence. Those evaluation details should not be copied into the production Skill source merely to make a benchmark easy to score.

Create the smallest reusable product/domain Skill first; keep evaluation-specific setup and verdict logic in the Benchmark/Sandbox layers.
