# ConnectionAgent Skill Authoring Guide

This guide follows the [CA-SL vNext Specification](skill-language-spec.zh-CN.md), the sole normative language authority.

## 1. Current source baseline

The runnable 5GC Skills remain on the v0.2 business/source baseline and have not yet been migrated to vNext. MAS is a design candidate, not the first live execution acceptance baseline. Do not rewrite the current runnable packages before a separately reviewed migration.

## 2. Canonical vNext Skill package

~~~text
skills/<name>/
├── SKILL.md
├── assurance/
│   ├── contract.yaml
│   ├── procedure.yaml
│   └── predicates.yaml
├── cases/<case>/case.yaml
├── references/
├── schemas/
└── scripts/
~~~

The three assurance files have separate responsibilities:

- `contract.yaml`: public Skill declaration — Goal, global Precondition references, public Request Schema, Host Invocation Context Schema, public dependency identities and Capability Grants.
- `procedure.yaml`: the single execution graph — start, business Nodes with ordered optional phases, and Terminal Nodes. A Node's phases are Precondition, Operation, Observation, and Postcondition.
- `predicates.yaml`: reusable Predicate parameter signatures and CEL / Python evaluators.

The Contract remains author-maintained source. Only redundant wrapper fields and values derivable elsewhere are removed; the public declarations it owns are not deleted. Compiler may derive a normalized Runtime contract from Contract, Procedure, Predicates and dependency snapshots, but that artifact does not replace the source Contract.

## 3. Contract ownership

| Field | Treatment |
|---|---|
| `goal` | Keep: business goal |
| `requestSchema` | Skill-owned public Request Schema |
| `contextSchema` | Exact Host-owned Invocation Context Schema |
| `dependencies` | Alias → stable Package ID string |
| `capabilities` | Requested Capability IDs |
| `apiVersion`, `kind` | Omit from source; selected by Compiler Target / file structure |
| `metadata.name` | Derive from Skill Package root |
| `entryProcedure` | Omit: one Procedure entry per Skill |
| `preconditions` | Optional list of `<node-id>.precondition` references. Every listed gate must PASS before a business Mutation or SUCCEEDED |
| `postconditions` | Procedure nodes mark the Goal they prove with `postcondition.goal`; each success path must carry a valid Goal PASS |
| `planning.allowDynamicProcedure` | Omit: static DAG is a language invariant |
| `planning.maxActions` | Superseded; optional `limits.maxActions` imposes a stricter Skill action bound. Host's positive budget is mandatory |
| `failureSemantics.outcomeUnknown.requireReconcile` | General safety rule for Mutation UNKNOWN, not a per-Skill toggle |

Dependencies and Capability Grants are different: dependencies make Owner contracts available for linking; grants express the Skill's authorization request. A dependency does not grant permission, and a grant does not provide the ToolCatalog / Schema contract needed to compile a reference.

## 4. Skill Studio creation flow

Studio should guide authors through selection rather than requiring manual entry of Owner IDs:

1. Select public dependencies (Host Context, ToolCatalog, Observation and shared Schema packages).
2. Select the Host-owned Invocation Context Schema.
3. Select requested Capabilities from trusted CapabilityContracts.
4. Create or select the Skill-owned Request Schema.
5. Generate / update `contract.yaml`; bind exact callable exports while authoring Procedure.

Selections remain editable later in Dependencies / Capabilities views. Studio fetches exact dependency snapshots and supplies them to Compiler. Compiler parses, links and validates only; it does not download dependencies or manage dependency versions.

The Contract maps each dependency Alias to a stable Package ID. The build caller binds that identity and the allowed Owners to the existing snapshot alias and verified digest. Compiler links exact Owner exports. The Contract does not store download locations, version locks or digests. Preserve immutable version markers in Owner Schema IDs.

## 5. Further reading

Use the comprehensive specification for the concept model, Contract / Dependency / Capability ownership, four Procedure node types, Predicate parameters, ToolCatalog, Observation, Evidence, Schema ownership, Script roles, PDU Session examples, exceptional cases and FAQ.
