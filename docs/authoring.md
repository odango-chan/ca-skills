# ConnectionAgent Skill Authoring Guide

This guide follows the current language authority in [Skill Language Specification](skill-language-spec.md), [Script Contract](script-contract.md), [Schema Ownership](schema-ownership.md) and [Authoring Model](authoring-model.md). **ca-skills is the only authoritative input for official Skill source and Skill-authored language semantics.**

## 1. Current source baseline

The current official 5GC executable packages are:

- `skills/establish-pdu-session/` — conventional initial PDU Session Establishment.
- `skills/establish-pdu-session-mas/` — MAS policy-first candidate.

These packages are still the v0.2 source baseline and have not been migrated to vNext. They remain unchanged until a separately reviewed migration. The vNext layout below is a design target, not a claim that existing packages already conform.

The latest `ca-agent-demo` source is used only to verify and refresh business behavior. Compiler and Studio consume the official Skill source from this repository, not from ca-agent-demo.

## 2. Canonical vNext Skill package

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case>/case.yaml
├── references/       # optional model knowledge
├── schemas/          # Skill-owned schemas only
└── scripts/          # Skill-owned deterministic Python
~~~

vNext does not require an authored `assurance/contract.yaml` or a SkillContract YAML wrapper. The single `procedure.yaml` source declares the Goal, optional public Request Schema, explicit Capability grants, Procedure inputs, start node and complete graph. Skill identity is derived from the Package root. Compiler derives language/API version, kind, metadata and any normalized Runtime contract projection.

- `SKILL.md` is model-facing business guidance.
- `procedure.yaml` is the single Skill execution source.
- `predicates.yaml` contains reusable Predicate definitions and typed parameters.
- `cases/` contains source-level semantic obligations, not executable Compiler tests.
- `references/` is optional knowledge. It is not automatically loaded; list exact paths in `SKILL.md` and let the model decide when useful.
- `schemas/` contains only schemas genuinely owned by the Skill, such as the public Request Schema.
- `scripts/` contains deterministic local computation owned by this Skill.

Do not create `preload/` or `on-demand/` directories. Do not create a second prose workflow that duplicates Procedure edges.

## 3. Procedure graph

The vNext Procedure graph has four business node types:

- `precondition` — invokes one Predicate before a protected action.
- `operation` — invokes one exact imported Tool Operation or a Skill-owned pure Procedure Script.
- `observation` — invokes one exact read-only Observation Query when existing values and Evidence are insufficient.
- `postcondition` — invokes one Predicate to judge an intermediate or final business result.

`terminal` declares SUCCEEDED, FAILED, UNRESOLVED or SAFE_STOPPED; it is not a fifth business action. Predicate is a reusable judgment definition, not a Procedure node. No generic computation node is introduced.

The Invocation-wide Precondition, when needed, is the first node. The final business Postcondition is an explicit final node before SUCCEEDED. Every successful path must pass its PASS route. Local Precondition / Postcondition nodes remain available for intermediate gates. There is no separate SkillContract.postconditions field and no second evaluation through a from reference.

A Procedure Script is expressed as a local target of an Operation node:

~~~yaml
prepare-policy-inputs:
  operation:
    script: scripts/build_pcf_policy_inputs.py
  arguments:
    subscriptionData: select-establishment-configuration.output.subscriptionData
    subscriptionSource: select-establishment-configuration.output.subscriptionSource
  'on':
    SUCCEEDED: create-policy
    FAILED: failed
~~~

A Tool Operation is an external callable and requires exact Capability membership / Effect validation. A Procedure Script is pure local computation; it is not a Tool, Capability or READ / MUTATION Effect.

The first vNext version has one entry Procedure graph per Skill. It does not define nested ProcedureCall or graph cycles. Business paths are expressed with explicit branches and routes.

## 4. Arguments and SourcePath

- Tool Operation and Observation use named `arguments` mappings checked against the Owner Input / Query Schema.
- Procedure Script uses a named `arguments` mapping as its complete local input projection.
- Precondition and Postcondition use ordered `arguments` lists matching the Predicate's `parameters` signature.
- Procedure `inputs` use direct SourcePath mappings.
- No implicit previous-node output, parent Procedure state, blanket Context forwarding, field-name guessing or dynamic selector is permitted.

The supported SourcePath roots are `input`, `context.request`, `context.subject`, `context.facts`, `context.ingress`, and an exact prior Node's `output`. vNext first version supports static dot paths only.

## 5. Scripts

Skill-owned Python has two roles:

1. Procedure Script — deterministic local selection, transformation and structured-data construction, invoked through an Operation node.
2. Predicate Script — the evaluator implementation of a Predicate.

Both use the single entry point `main(input: dict)`. The input dict is an invocation container, not an open Input Schema.

- Procedure Script inputs derive from the exact call-site `arguments` mapping and source contracts.
- Predicate Script inputs derive from the owning Predicate's ordered `parameters` signature plus Host-attached read-only Evidence.
- Procedure Script and Predicate Script return types must be strict `TypedDict` declarations.
- Compiler generates read-only Output Schemas from the return types.
- Predicate Script returns a structured result with `result: PASS | FAIL | UNKNOWN`, `reasonCode` and `evidenceUsed`. The latter may cite only Evidence refs attached by Host / Runtime.
- Do not author separate Script Input / Output Schema files.
- Do not add `# /// connectionagent-tool` metadata, independent local Tool IDs or Capability IDs.
- Scripts perform deterministic local computation only. They do not call HTTP, MCP, Providers, Tools, shell commands, databases, filesystems, clocks, environment variables or random sources.

See [Script Contract](script-contract.md) for the exact supported types and constraints.

## 6. Schema ownership and imported contracts

| Contract | Owner | Source |
|---|---|---|
| Public Skill Request | Skill | `schemas/**`, referenced by procedure.yaml |
| Tool Operation Input/Output | Tool owner | Imported ToolCatalog |
| Subject / Facts / Ingress | Agent Host | Exact Host dependency exports |
| Observation payload | Observation owner | Exact Observation dependency exports |
| Procedure Script input | Derived | Exact call-site Producer bindings |
| Predicate Script input | Derived | Predicate parameters + Host Evidence |
| Script output | Skill Script | Generated from return TypedDict |

`requiredFacts` is a list of fact identifiers, not a field-level Schema. Do not fabricate an external Schema, infer it from Python access patterns, or substitute a Deployment Profile.

The Compiler receives immutable DependencySnapshot bytes from Studio / caller. It resolves exact exported IDs and Schema IDs. Do not copy external Owner Schemas into a Skill's `schemas/` directory or bundle every file from external `lib/` snapshots.

## 7. Cases and validation

A Case is one `cases/<name>/case.yaml` source-level scenario and expected semantic obligation. It is not proof of execution, qualification or live 5GC acceptance.

Run:

~~~sh
make verify
~~~

This checks repository-local source hygiene, Script entry-point shape, source references and the semantic-token registry. It does not invoke Compiler, Runtime, Qualification or a live network.

Compiler acceptance is established only by testing the actual target Compiler. Runtime and live 5GC acceptance belong to their respective owners.

## 8. Compiler and artifact boundary

Studio / caller acquires files, imports Tool / Host / Observation contracts and assembles the logical BuildRequest file set. Compiler receives bytes, parses and links the Skill language, validates bindings, generates output files and diagnostics.

Source YAML remains authoritative. The generated Schema serialization (YAML versus canonical JSON) is a separate Compiler Artifact Contract decision; canonical JSON is the recommended machine-output format but is not frozen by the language specification.

Compiler must not copy every external dependency file into the Skill Package or Build Artifact. If a self-contained deployment bundle is required, include only the transitive dependency closure reachable from the compiled Skill; otherwise retain exact external references. Dependency closure packaging is a separate Compiler / Deployment concern.

Compiler does not manage Git, Upload, MCP, dependency resolution, locks, caches, workspace folders, Python execution, Tool execution or Qualification. Studio decides how to display and export BuildResult files.
