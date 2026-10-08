# ConnectionAgent Skill Authoring Syntax

This reference contains the practical source syntax used when authoring official ConnectionAgent Skills.

It is a concise authoring view, not a second machine-language authority. The current Skill Platform schemas and compiler remain normative.

## Normative source schemas

| Source asset | Skill Platform schema |
| --- | --- |
| `assurance/contract.yaml` | `schemas/v1alpha1/skill-contract.schema.yaml` |
| `assurance/procedure.yaml` | `schemas/v1alpha1/procedure-source.schema.yaml` |
| `assurance/predicates.yaml` | `schemas/v1alpha1/predicate-set.schema.yaml` |
| `cases/<case>/case.yaml` | `schemas/v1alpha1/skill-test-case.schema.yaml` |
| governed Python Script metadata | `schemas/v1alpha1/script-tool-metadata.schema.yaml` |

For official `assurance/procedure.yaml` source, use `procedure-source.schema.yaml`. Do not infer current authoring syntax from older or internal Procedure representations such as the array/type/action form.

## Canonical package shape

A governed executable Skill normally has:

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
├── schemas/          # optional
└── scripts/          # optional governed local compute
```

Rules:

- `assurance/` is all-or-nothing;
- there is no standalone `evidence.yaml`;
- qualification cases use one `case.yaml` per case directory;
- no package-root `README.md`, `MIGRATION.md`, or `examples/`;
- explanatory samples belong in `references/samples/`;
- `references/` contents are not automatically injected into model context;
- `scripts/` is optional governed deterministic local compute, not a deprecated package feature;
- cross-cutting Planner/Linker/Admission fixtures belong in their test owner, not a business Skill's `references/`;
- do not create empty placeholder directories.

## `SKILL.md`

Keep the package `SKILL.md` thin and model-facing.

Typical shape:

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

Keep only business/domain meaning, normalization and disambiguation, model-facing structured expectations, and boundaries the model must not guess or bypass.

For executable Skills, "output expectation" does **not** mean every Skill needs a model response schema. Governed execution success is established by Runtime postconditions/Predicates. Only define a Skill-owned model-facing payload/schema when the Skill genuinely owns that semantic payload; stage-owned outputs such as routing or planning-choice responses stay with their owning Host/model adapter.


Do not copy Provider bindings, deployment endpoints, Runtime state machines, full Procedure graphs, qualification status, Benchmark scoring, or migration history into model context.

## `contract.yaml`

Typical executable contract:

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

- `goal` is a business/domain goal, not a Tool outcome;
- `allowedResources.capabilities` lists governed Runtime capabilities that Procedures may call;
- `localTools` lists governed Skill-local Tool identities, not script paths;
- a requirement is something the allowed workflow can actively satisfy;
- a postcondition is final proof and may intentionally have no repair action;
- mutation `OUTCOME_UNKNOWN` must preserve uncertainty and reconcile before retry or continuation;
- ProviderBinding, endpoint, credential, and deployment identity never belong here.

## `procedure.yaml` vNext

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

Use one primary intent per node. Current source supports these authoring forms:

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

Use `verify` for evidence-gated Predicate judgment rather than inventing ad-hoc boolean decision syntax.

### Bindings

Each `with` binding contains exactly one source:

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

Common namespaces:

- `input.<name>` — Procedure input;
- `context.subject.*`, `context.request.*`, `context.facts.*`, `context.constraints.*` — admitted context;
- `<node>.output.*` — prior node output;
- `loop.<name>` — `for` binding;
- `value` — literal constant.

Do not invent `fromContext`, `fromOutput`, hidden interpolation, implicit previous-output binding, or another sequencing DSL.

### Control flow

`on` maps governed outcomes to next node IDs:

```yaml
'on':
  SUCCEEDED: next
  FAILED: failed
  DENIED: failed
```

Mutation paths must explicitly handle `OUTCOME_UNKNOWN` when the capability contract permits it. Never route unknown mutation outcome directly to retry.

### Procedure selection

Use `applicability.when` for deterministic Procedure selection in the current selection context:

```yaml
applicability:
  when: context.request.priority == "high"
```

Selection is not Runtime Predicate evaluation and does not acquire Evidence.

## `predicates.yaml`

Predicates declare required observations and deterministic judgment over already-materialized evidence.

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
- Evidence Gate handles missing, stale, unavailable, or invalid required observations and yields `UNKNOWN` before the evaluator;
- CEL is for small auditable deterministic assertions;
- Script evaluators are for complex deterministic judgment over already-materialized data;
- Predicate Scripts must not call Providers, MCP servers, networks, or acquire more evidence;
- evaluator crash or timeout is infrastructure failure, not business `FAIL`.

## Governed Python Script

Skill-local deterministic scripts carry inline metadata and are referenced by Procedure path or governed local Tool identity.

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

Scripts are deterministic local computation only. Do not hide Provider I/O, network access, shell workflows, credentials, or uncontrolled side effects inside them.

Procedure Script and Predicate Script reuse the governed local-compute execution base but have different semantics: Procedure Script computes workflow data; Predicate Script judges supplied evidence.

## `case.yaml`

Each qualification case is exactly one file:

```text
cases/<case-name>/case.yaml
```

Minimal envelope:

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

The exact `PlanningContext`, expected trace/postcondition fields, fixtures, and Simulation schema remain Platform-owned. Prefer copying the smallest adjacent current Case and changing its semantics rather than inventing fields.

Coverage follows semantic obligations, not a fixed Case count. Include the normal path and relevant failure, denial, Evidence `UNKNOWN`, mutation reconcile, budget, and independent postcondition-failure classes when they are meaningful for the Procedure/Profile.

SkillTestCase is not BenchmarkCase. Do not use Skill-internal expected traces as the black-box Benchmark oracle.

## Current official examples

Prefer real official packages over maintaining another full synthetic example set:

- `skills/query-weather-for-ue/` — compact end-to-end example with Procedure Script, CEL Predicates, Cases, and external read-only capability;
- `skills/ue-registration/` — richer mutation and `OUTCOME_UNKNOWN` / reconcile behavior;
- `skills/ensure-session-qos/` — requirement satisfaction plus independent postcondition verification;
- `skills/download-object-by-deadline/` — deadline-aware composition and governed local computation;
- `skills/5gc-intent/` — model-context/routing-policy package with no executable assurance extension.

## Validation

Focused compile for one executable official package:

```bash
python3 -B scripts/verify.py --compile skills/<name>
```

Full source/preflight gate:

```bash
make verify
```

`verify.py` uses `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` when set; otherwise it expects sibling `../connectionagent-skill-platform`.

A focused compile or green source gate is not production qualification.
