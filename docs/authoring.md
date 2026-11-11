# ConnectionAgent Skill Authoring Guide

This guide follows the current language authority in [Skill Language Specification](skill-language-spec.md), [Script Contract](script-contract.md), [Schema Ownership](schema-ownership.md) and [Authoring Model](authoring-model.md). **ca-skills is the only authoritative input for official Skill source and Skill-authored language semantics.**

## 1. Current source baseline

The current official 5GC executable packages are:

- `skills/establish-pdu-session/` — conventional initial PDU Session Establishment.
- `skills/establish-pdu-session-mas/` — MAS policy-first candidate.

These two packages are the current source examples. Other historical packages remain in the repository but are not authorities for the current 5GC language contract.

The latest `ca-agent-demo` source is used only to verify and refresh business behavior. Compiler and Studio consume the official Skill source from this repository, not from ca-agent-demo.

## 2. Canonical Skill package

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case>/case.yaml
├── references/       # optional model knowledge
├── schemas/          # Skill-owned schemas only
└── scripts/          # optional pure local computation
~~~

- `SKILL.md` is model-facing business guidance.
- `assurance/` is the deterministic source contract.
- `cases/` contains source-level semantic obligations, not executable Compiler tests.
- `references/` is optional knowledge. It is not automatically loaded; list exact paths in `SKILL.md` and let the model decide when useful.
- `schemas/` contains only schemas genuinely owned by the Skill, such as the public Request Schema.
- `scripts/` contains deterministic local computation owned by this Skill.

Do not create `preload/` or `on-demand/` directories. Do not create a second prose workflow that duplicates Procedure edges.

## 3. Procedure

The current language uses named Procedures and named nodes. The supported main-node intents are:

- `call` — one exact imported Tool Operation.
- `script` — one Skill-owned Script path.
- `procedure` — local or explicitly identified cross-Skill Procedure.
- `verify` — one Predicate.
- `reconcile` — reconciliation of the exact original mutation node.
- `terminal` — declared Procedure terminal result.

A `call` is always a scalar Operation ID:

~~~yaml
call: sbi.udm.sm_data.get
~~~

Do not use a Capability group, dependency name, MCP tool name, or `{dependency, operation}` object in `call`. The caller supplies ToolCatalog bytes under the logical `lib/tools/**` namespace; Compiler links the exact Operation ID.

Preconditions and postconditions are ordered phases. Their steps support only `call`, `script` and `verify`. They do not support nested Procedure or Tool declarations.

Use explicit `with:` bindings. Each binding has exactly one `from:` or `value:`. Never rely on implicit previous-node output or inferred data flow.

## 4. Scripts

Use the single supported entry point:

~~~python
from typing import Literal, TypedDict

class SelectionOutput(TypedDict):
    accepted: Literal[True]
    dnn: str

def main(input: dict) -> SelectionOutput:
    return {"accepted": True, "dnn": input["dnn"]}
~~~

- The parameter `input: dict` is only the invocation container, not an open Input Schema.
- Procedure Script inputs are derived per call site from that step's `with:` Producer bindings.
- Predicate Script inputs are the Host-created Predicate Evaluation Context plus declared observations.
- The return type must be a non-empty, statically declared `TypedDict`.
- Compiler generates the read-only Script Output JSON Schema.
- Use functional `TypedDict("Name", {...})` when a wire key is not a valid Python identifier, such as `5qi`.
- Do not add `# /// connectionagent-tool` metadata, independent local Tool IDs, or per-Script input/output Schema files.
- Scripts perform deterministic local computation only. They do not call HTTP, MCP, Providers, Tools, shell commands, databases, clocks or random sources.

See [Script Contract](script-contract.md) for the exact supported types and constraints.

## 5. Schema ownership and imported contracts

| Contract | Owner | Source |
|---|---|---|
| Public Skill Request | Skill | `schemas/**` |
| Tool Operation Input/Output | Tool owner | Imported ToolCatalog under logical `lib/tools/**` |
| Subject / Facts / Evidence | Agent Host | Explicit Owner Schema references under `lib/host/**` |
| Observation payload | Observation owner | Explicit Owner Schema references under `lib/observations/**` |
| Procedure Script input | Derived | Exact call-site Producer bindings |
| Predicate Script input | Host + Observation owners | Predicate Evaluation Context |
| Script output | Skill Script | Generated from Output `TypedDict` |

`requiredFacts` is a list of fact identifiers, not a field-level Schema. Do not fabricate an external Schema, infer it from Python access patterns, or substitute a Deployment Profile.

The current official `lib/` snapshot contains the approved 12-Operation conventional PDU ToolCatalog only. The actual Host Subject/Facts/Evidence and Observation Owner Schemas are not currently bundled. Their absence is an explicit external dependency; Compiler must report it when those schemas are required.

The MAS Skill's 16 Operation references remain unresolved until the Tool owner supplies an approved ToolCatalog. Its design file is not an approved import.

## 6. Cases and validation

A Case is one `cases/<name>/case.yaml` source-level scenario and expected semantic obligation. It is not proof of execution, qualification or live 5GC acceptance.

Run:

~~~sh
make verify
~~~

This checks repository-local source hygiene, Script entry-point shape, source references and the semantic-token registry. It does not invoke Compiler, Runtime, Qualification or a live network.

Compiler acceptance is established only by testing the actual target Compiler. Runtime and live 5GC acceptance belong to their respective owners.

## 7. Compiler and Studio boundary

Studio/caller acquires files, imports Tool/Host/Observation contracts and assembles the logical BuildRequest file set. Compiler receives bytes, parses and links the Skill language, validates bindings, generates output files and diagnostics.

Compiler does not manage Git, Upload, MCP, dependencies, locks, caches, workspace folders, Python execution, Tool execution or Qualification. Studio decides how to display and export BuildResult files.
