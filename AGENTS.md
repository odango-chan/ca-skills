# ca-skills repository rules

## Authority

- Use the [current CA-SL specification](docs/skill-language-spec.md), its [release record](docs/releases/ca-sl-v1alpha5.md) and the [authoring guide](docs/authoring.md) for new source.
- This repository owns official Skill source and language semantics. Use `ca-agent-demo` as a behavior and integration reference. `ca-skill-compiler` consumes caller-supplied files and Owner contracts.
- The [documentation index](docs/README.md) locates companion references, archived designs and verification inputs.

## Source

- Author new v1alpha5 examples under `examples/skills/`. Preserve business Procedure and Operation identities unless the business owner approved a change.
- Keep the packages under `skills/` available as historical behavior baselines. See the [legacy 5GC baseline](docs/current-5gc-skill-baseline.md) before changing them. The 16 legacy MAS Operation references still require an Owner publication.
- The Contract declares one `goal` and may reference one global `precondition: <node-id>.precondition`. Each Precondition or Postcondition stage has its own nonempty ordered `predicates` list. Only the final Postcondition aggregate `PASS` routed directly to `SUCCEEDED` proves the Goal.
- Use exact `operation.tool` or `observation.tool` references. Trusted Owner `mutation.reconcile` belongs to the Host contract. Node-entry `wait` precedes a Node's business stages and uses the exact trusted IngressCatalog export.
- Link trusted Owner Schemas, Evidence guarantees, ToolCatalog and CapabilityContracts. Example placeholders illustrate the source syntax and need trusted exports to compile.
- Keep the frozen release files at their published paths. Record editorial corrections in the release record.

## Validation

Run `make verify` for source hygiene, specification structure and Wait/Ingress registry checks. Cases are source obligations. Record Compiler, Runtime, Owner and live acceptance only when the corresponding tests have run.
