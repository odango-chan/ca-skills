# ConnectionAgent Skill Authoring Syntax

This is a practical reference, not a separate language authority. Follow [Skill Language Specification](../../../../docs/skill-language-spec.md), [Script Contract](../../../../docs/script-contract.md), [Schema Ownership](../../../../docs/schema-ownership.md) and [Authoring Model](../../../../docs/authoring-model.md).

## Package

~~~text
skills/<name>/
├── SKILL.md
├── assurance/{contract,procedure,predicates}.yaml
├── cases/<case>/case.yaml
├── references/       # optional model knowledge
├── schemas/          # Skill-owned schemas only
└── scripts/          # pure local computation
~~~

## Procedure

A main-node `call` is a scalar exact Operation ID:

~~~yaml
nodes:
  read-subscription:
    call: sbi.udm.sm_data.get
    with:
      ueRef:
        from: input.ue-ref
~~~

Do not use a `{dependency, operation}` object. Dependency acquisition and source identity are outside the Skill language; the caller supplies ToolCatalog files and Compiler links the exact Operation ID.

Supported main-node actions: `call`, `script`, `procedure`, `verify`, `reconcile` and `terminal`. Preconditions/postconditions contain ordered `steps` using only `call`, `script` or `verify`. `tool` and nested `procedure` steps are not supported.

## Scripts

~~~python
from typing import Literal, TypedDict

class Result(TypedDict):
    accepted: Literal[True]
    value: str

def main(input: dict) -> Result:
    return {"accepted": True, "value": input["source"]}
~~~

`input: dict` is a container only. Procedure inputs come from exact `with:` bindings; Predicate evaluator inputs come from the Host Predicate Evaluation Context and declared observations. The Script output `TypedDict` is the sole Script-owned Schema declaration. Compiler generates the read-only Output JSON Schema.

Do not add `# /// connectionagent-tool` metadata or per-Script `name`, `inputSchema`, `outputSchema`, `effect`, `sandbox` or `timeout` fields. A Script is not a separate Tool/Capability and cannot perform network, MCP, Provider or Tool I/O.

See the Script Contract for supported output types and constraints.

## Schema ownership

- Request Schema: Skill-owned under `schemas/`.
- Tool Schema: imported ToolCatalog under logical `lib/tools/`.
- Subject/Facts/Evidence Schema: real Host Owner files under logical `lib/host/`.
- Observation payload Schema: real Observation Owner files under logical `lib/observations/`.
- Procedure Script input: derived per call site.
- Predicate Script input: derived from Host context and declared observations.
- Script output: generated from Output `TypedDict`.

Do not infer external fields from `requiredFacts`, and do not duplicate external Tool Schema in Script input files.

## Cases and References

Cases are semantic source obligations, not execution evidence. Optional model knowledge belongs in `references/`; it is not evidence or executable syntax and is not automatically loaded.
