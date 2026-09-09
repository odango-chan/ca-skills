---
name: create-connectionagent-skill
description: Use when the user asks to design, create, or structurally complete an official ConnectionAgent Skill source package in this repository. Apply the current vNext authoring syntax below, validate against Skill Platform machine schemas/compiler, and run focused compile or repository verification without claiming production qualification.
---

# Create ConnectionAgent Skill

Create or structurally complete official ConnectionAgent Skill source in `connectionagent-skills`.

Official source lives only under `skills/<name>/`. This developer workflow is an authoring assistant, not an official business Skill and not a second machine-language authority.

## 1. Authority and current source schemas

Read repository `AGENTS.md` first. Use this file as the working authoring guide, then validate against the current Skill Platform compiler.

For official source packages, use these machine schemas as the normative authoring surfaces:

| Source asset | Normative Platform schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| governed Python Script metadata | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

For `assurance/procedure.yaml`, **author from `procedure-source.schema.yaml`**. Do not infer current source syntax from `procedure-set.schema.yaml`; the official vNext source packages use the object-form `procedures -> start/nodes` model shown below.

If this cheatsheet conflicts with the current compiler or the schemas above, fix this workflow and follow the machine contract.

## 2. Decide what you are creating

Classify the requested asset before creating files.

- **Executable Skill**: product/domain goal plus deterministic assurance composition. It normally has the complete `assurance/` trio.
- **Model-context / routing-policy package**: model-visible business or routing semantics only. It has no preliminary Runtime Procedure. `5gc-intent` is the reference pattern.
- **Runtime Capability**: a low-level Provider action such as create/query/modify/release. Do not create a Skill merely to wrap one primitive call.

Routing is Agent-owned. Never model routing as “execute Skill A to mint `ExecutionTarget`, then execute Skill B”.

See `references/skill-granularity.md` when the boundary is unclear.

## 3. Canonical package shape

Model-context package:

```text
skills/<name>/
├── SKILL.md
├── references/       # optional
└── schemas/          # optional private model-facing types
```

Governed executable Skill:

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/       # optional
├── schemas/          # optional Skill-local types
└── scripts/          # optional governed local compute
```

Rules:

- `assurance/` is all-or-nothing;
- there is no standalone `evidence.yaml`;
- no package-root `README.md`, `MIGRATION.md`, or `examples/`;
- explanatory samples belong in `references/samples/`;
- model-facing Markdown under `skills/` is written in English;
- do not create empty placeholder directories.

## 4. `SKILL.md`

Keep `SKILL.md` thin. It is the single package-root model-facing entry point.

Minimal shape:

```markdown
---
name: example-skill
description: Achieve <business goal> when <selection condition>.
---

# Example Skill

## Goal
...

## Use when
...

## Inputs and normalization
...

## Decision rules
...

## Success semantics
...
```

Keep business/domain meaning, normalization/disambiguation, model-facing input/output expectations, and boundaries the model must not guess or bypass.

Do not copy Provider bindings, deployment endpoints, Runtime state machines, full Procedure graphs, qualification status, Benchmark scoring, or migration history into model context.

## 5. `contract.yaml` quick reference

A typical executable contract starts like this:

```yaml
apiVersion: connectionagent.io/v1alpha1
kind: SkillContract
metadata:
  name: example-skill
spec:
  skillType: executable
  goal: example.goal_satisfied

  inputs:
    requestSchema: schemas/request.schema.yaml

  context:
    requiredFacts:
    - example.context_fact

  allowedResources:
    capabilities:
    - example.query
    - example.mutate
    - example.reconcile
    localTools: []

  preconditions:
  - predicate: example.precondition
    expect: PASS

  requirements:
  - predicate: example.requirement
    expect: PASS
    satisfiable: true

  postconditions:
  - predicate: example.goal_satisfied
    expect: PASS

  planning:
    maxActions: 8
    allowDynamicProcedure: true

  failureSemantics:
    outcomeUnknown:
      requireReconcile: true
```

Authoring rules:

- `goal` names the business goal, not a Tool outcome;
- `allowedResources.capabilities` lists governed Runtime capabilities the Procedure may call;
- `localTools` lists governed Skill-local Tool identities, not scripts by path;
- a **requirement** is something the allowed workflow can actively satisfy;
- a **postcondition** is final proof and may intentionally have no repair action;
- mutation `OUTCOME_UNKNOWN` must preserve uncertainty and reconcile before retry/continuation;
- ProviderBinding, endpoint, credential, and deployment identity never belong here.

## 6. `procedure.yaml` vNext syntax

Current source shape:

```yaml
procedures:
  default:
    inputs:
      subject-id:
        type: string
        from: context.subject.id
      requested-value:
        type: string
        from: context.request.value

    applicability:
      when: context.request.mode == "managed"

    start: inspect
    nodes:
      inspect:
        call: example.query
        with:
          id:
            from: input.subject-id
        'on':
          SUCCEEDED: verify-goal
          FAILED: failed
          DENIED: failed

      verify-goal:
        verify: example.goal_satisfied
        'on':
          PASS: done
          FAIL: apply-change
          UNKNOWN: unresolved

      apply-change:
        call: example.mutate
        with:
          id:
            from: input.subject-id
          value:
            from: input.requested-value
        'on':
          COMMITTED: verify-goal
          NOT_COMMITTED: failed
          OUTCOME_UNKNOWN: reconcile-change
          FAILED: failed
          DENIED: failed

      reconcile-change:
        call: example.reconcile
        'on':
          COMMITTED: verify-goal
          NOT_COMMITTED: apply-change
          UNRESOLVED: unresolved
          FAILED: safe-stopped
          DENIED: safe-stopped

      done:
        terminal: SUCCEEDED
      failed:
        terminal: FAILED
      unresolved:
        terminal: UNRESOLVED
      safe-stopped:
        terminal: SAFE_STOPPED
```

### Node forms

Use one primary intent per node. New official source should normally use:

```yaml
call: capability.name

tool: skill.local-tool

script: scripts/local_compute.py

verify: predicate.semantic_id

procedure: another-procedure

for:
  each: item
  in:
    from: input.items
do:
  process-item:
    call: example.process
    with:
      item:
        from: loop.item

reconcile: capability.or-reconcile-ref

terminal: SUCCEEDED
```

Use `verify` for evidence-gated Predicate judgment in new official Skills rather than inventing ad-hoc boolean decision syntax.

### Bindings

`with` bindings contain exactly one source:

```yaml
with:
  a:
    from: input.a
  b:
    from: context.request.b
  c:
    from: previous-node.output.value
  item:
    from: loop.item
  fixed:
    value: literal-value
```

Common binding namespaces:

- `input.<name>` — typed Procedure input;
- `context.subject.*`, `context.request.*`, `context.facts.*`, `context.constraints.*` — admitted context;
- `<node>.output.*` — prior node output;
- `loop.<name>` — `for` item/index binding;
- `value` — literal constant.

Do not invent `fromContext`, `fromOutput`, hidden interpolation, implicit previous-output binding, or another sequencing DSL.

### Control flow

`on` maps a governed outcome to the next node ID:

```yaml
'on':
  SUCCEEDED: next
  FAILED: failed
  DENIED: failed
```

Mutation paths must explicitly handle `OUTCOME_UNKNOWN` where the capability contract permits it. Do not route unknown mutation outcome directly to retry.

### Procedure selection

Use `applicability.when` for deterministic Procedure selection predicates expressed in the current CEL-compatible selection context. Selection is not Runtime Predicate evaluation and does not acquire Evidence.

```yaml
applicability:
  when: context.request.priority == "high"
```

## 7. `predicates.yaml` quick reference

Predicates declare **what observations are needed** and **how already-materialized evidence is judged**.

CEL example:

```yaml
apiVersion: connectionagent.io/v1alpha1
kind: PredicateSet
metadata:
  skill: example-skill
predicates:
  example.goal_satisfied:
    observations:
      state:
        ref: example.state.snapshot
        scope: '{"id": subject.id}'
        freshness: 5s
    evaluator:
      type: cel
      expression: observations.state.status == "READY"
```

Script evaluator example:

```yaml
predicates:
  example.complex_consistency:
    observations:
      left:
        ref: example.left.snapshot
        scope: '{"id": subject.id}'
        freshness: 5s
      right:
        ref: example.right.snapshot
        scope: '{"id": subject.id}'
        freshness: 5s
    evaluator:
      type: script
      ref: skill.evaluate-complex-consistency
```

Rules:

- Observation acquisition happens before evaluator execution;
- Evidence Gate handles missing/stale/unavailable/invalid required observations and yields `UNKNOWN` before the evaluator;
- CEL is for small auditable deterministic assertions;
- Script evaluators are for complex deterministic domain judgment over already-materialized data;
- Predicate Scripts must not call Providers, MCP servers, network services, or acquire additional evidence;
- evaluator crash/timeout is an infrastructure failure, not a business `FAIL`.

## 8. Governed Python Script quick reference

A Skill-local deterministic script carries inline metadata and is referenced by Procedure path or governed local Tool identity.

```python
# /// connectionagent-tool
# name: normalize-example
# inputSchema: registry://schemas/example-input@v1
# outputSchema: ExampleOutput
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 2s
# ///


def main(input):
    return {"value": input["value"]}
```

Scripts are local deterministic computation only. Do not hide Provider I/O, network access, shell workflows, credentials, or uncontrolled side effects inside them.

Procedure Script and Predicate Script reuse the governed local-compute execution base but have different semantics: Procedure Script computes workflow data; Predicate Script judges supplied evidence.

## 9. `case.yaml` quick reference

Each qualification case is exactly one file:

```text
cases/<case-name>/case.yaml
```

Envelope:

```yaml
apiVersion: connectionagent.io/v1alpha1
kind: SkillTestCase
metadata:
  skill: example-skill
  name: 01-happy-path
spec:
  classes:
  - happy_path
  purpose: Prove the normal path reaches the independently verified goal.

  context:
    apiVersion: connectionagent.io/v1alpha1
    kind: PlanningContext
    metadata:
      operationId: op-01
      version: 1
    subject:
      id: subject-1
    request: {}
    facts: {}
    availableResources: []
    constraints:
      maxActions: 8

  expect:
    procedure: default
    planningStatus: READY
    terminal: SUCCEEDED
    postconditions:
    - predicate: example.goal_satisfied
      expect: PASS
      actual: PASS

  fixtures: {}
```

The exact `PlanningContext`, expected trace/postcondition fields, fixtures, and Simulation schema are governed by the Platform schemas. Prefer copying the smallest adjacent current case and changing semantics rather than inventing fields.

Coverage should follow semantic obligations, not a fixed Case count. Include normal success, relevant failure/denial, Evidence `UNKNOWN`, mutation reconcile branches, budget behavior, and independent postcondition failure where the Procedure/Profile makes those meaningful.

SkillTestCase is not BenchmarkCase. Do not use Skill-internal expected traces as the black-box Benchmark oracle.

## 10. Authoring workflow

For a new Skill or structural change:

1. Read repository `AGENTS.md` and classify Skill vs routing policy vs Capability.
2. Inspect one or two adjacent official Skills with similar semantics.
3. Reuse Registry Capability/Predicate/schema contracts before creating local ones.
4. Write the smallest complete package using the syntax above.
5. For an executable Skill, run focused compile:

   ```bash
   python3 -B scripts/verify.py --compile skills/<name>
   ```

   `verify.py` uses `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` when set; otherwise it expects sibling `../connectionagent-skill-platform`.

6. Run the full source/preflight gate before delivery:

   ```bash
   make verify
   ```

7. Run any additional SQ1/SQ2/production admission work required by the target profile in the owning Platform/Runtime/Sandbox environment.
8. Report exactly what ran and what did not run.

A focused compile or green source gate is not production qualification.

## 11. Do not create parallel contracts

Do not add:

- standalone `evidence.yaml`;
- package-root `examples/`;
- per-Skill repository validators such as `scripts/validate_<skill>.py`;
- a second compile helper under this authoring workflow;
- Provider/deployment mappings in model context;
- `ExecutionTarget.v1`, `RunPlanSnapshot.v1`, `RunPlanRevision.v1`, or generic `PlanDelta.v1` as new cross-repository contracts;
- graph coordinates/layout metadata in Skill source.

When a concrete scenario appears impossible, first determine whether the gap is actually in ProviderBinding, ObservationBinding, Runtime, qualification, or integration before changing the frozen Skill language.

## 12. Delivery

Report:

- files added/changed/removed;
- semantic decisions and reused contracts;
- exact verification/compile/qualification commands actually run;
- any unresolved Platform, Runtime, Provider, Sandbox, or deployment dependency.

For deeper human-oriented explanation see `docs/authoring.md`; for package granularity see `references/skill-granularity.md`. The Platform compiler remains the final authority on machine validity.
