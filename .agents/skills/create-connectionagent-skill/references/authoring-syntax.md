# ConnectionAgent Skill Authoring Syntax

This is a practical syntax/example reference, not a separate language authority. The canonical source-language semantics and semantic-token taxonomy are defined in [Skill Language Specification](../../../../docs/skill-language-spec.md). Current examples are the two packages in [the current 5GC baseline](../../../../docs/current-5gc-skill-baseline.md). The target Compiler must validate every construct; unsupported syntax must fail explicitly rather than be silently dropped. Legacy Toolchain support is only a subset and does not redefine this source contract.

## Canonical executable package

```text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/
│   └── <case>/case.yaml
├── references/       # optional flat Markdown
├── schemas/           # optional Skill-owned schemas
└── scripts/           # optional governed local compute
```

There is no standalone `evidence.yaml`. Do not add package-root `README.md`, `MIGRATION.md`, `examples/`, or maintainer-only `design/`.

## Contract

`contract.yaml` declares the Skill identity/type, business goal, entry Procedure, request schema, required facts, allowed Capability/local Tool resources, final preconditions/postconditions and action budget.

An allowed Capability is a semantic resource declaration. It is not proof that a Tool implementation is registered, deployed, READY or authorized.

## Procedure source

The current source model uses one deterministic graph:

```yaml
procedures:
  establish:
    inputs: {}
    start: inspect
    nodes:
      inspect:
        call: example.state.read
        'on':
          SUCCEEDED: verify-state
          FAILED: failed
          DENIED: failed
      verify-state:
        verify: example.state.ready
        'on':
          PASS: done
          FAIL: failed
          UNKNOWN: unresolved
      done:
        terminal: SUCCEEDED
      failed:
        terminal: FAILED
      unresolved:
        terminal: UNRESOLVED
```

Current node intents include:

- `call`: invoke a governed Capability;
- `tool`: invoke a governed Skill-local Tool;
- `script`: run deterministic local computation;
- `verify`: evaluate a Predicate against admitted evidence;
- `procedure`: invoke a child Procedure;
- `for`: express an explicitly bounded iteration where supported;
- `reconcile`: reconcile the exact original mutation;
- `terminal`: end with a declared terminal result.

Bindings use explicit `with/from` or `with/value`. Do not invent implicit previous-node outputs, hidden interpolation, or a second sequencing DSL.

## Node preconditions and postconditions

The current conventional PDU Session source uses ordered node-level preparation and verification blocks:

```yaml
preconditions:
  steps:
    - name: prepare-input
      script: scripts/prepare_input.py
  'on':
    PASS: continue
    FAIL: failed
    UNKNOWN: unresolved

postconditions:
  steps:
    - verify: example.operation_effective
  'on':
    PASS: next-business-node
    FAIL: failed
    UNKNOWN: unresolved
```

Preconditions are side-effect-free preparation immediately before the main operation. Postconditions verify the result after the main operation; successful operation outcome enters the postcondition phase, and only PASS advances. See [Authoring model](../../../docs/authoring-model.md) for ordering, allowed steps and failure semantics.

**Compatibility warning:** the current legacy `ca-skill-toolchain` `procedure-source.schema.yaml` does not include these node-level fields. The new stateless Compiler v0 is the target, but its implementation has not started. Do not remove or flatten these fields to force legacy compilation.

## Outcomes and reconciliation

Keep result domains distinct:

- Predicate: `PASS / FAIL / UNKNOWN`;
- operation: the outcomes declared by the imported Tool contract;
- Procedure terminal: `SUCCEEDED / FAILED / UNRESOLVED / SAFE_STOPPED`.

Use `reconcile: <original-node>` for an original mutation with uncertain outcome. Preserve the exact original operation identity. Never blindly retry an unknown mutation.

## Predicate source

`predicates.yaml` declares the observations required and the deterministic evaluator over already materialized evidence. Missing, stale, unavailable, ambiguous or wrong-producer evidence must remain UNKNOWN; do not reinterpret it as FAIL or PASS.

## Cases

Each qualification case is one file:

```text
cases/<case-name>/case.yaml
```

Cases record semantic obligations and expected outcomes. They are not execution evidence. The current conventional PDU Session package documents 36 cases as obligations that are not yet executable Runtime fixtures.

## Scripts and schemas

- Python Scripts are deterministic local computation only; they do not call network services, Providers, MCP servers, shell commands, clocks, databases or credentials.
- Use explicit Script input/output declarations and author-owned schemas. Do not infer constraints that the source declaration does not express.
- Request/response schemas owned by the Skill live under `schemas/`.

## References and imported Library

- Optional model knowledge lives in flat `references/*.md` and is selected when useful; it is not automatically loaded and is not evidence.
- Imported Tool contracts live in project `lib/` as read-only snapshots. Do not edit imported files or infer runtime readiness from their presence.
- Current import: `lib/tools/createdsession.tool.yaml` (12 conventional Operations). The 16 MAS Capability references remain unresolved; the MAS design draft is not an approved ToolCatalog.
