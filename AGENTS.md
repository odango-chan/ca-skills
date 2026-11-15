# ca-skills repository rules

## Authority

- This repository is the **only authoritative input** for official Skill source and Skill language semantics.
- `ca-agent-demo` is a behavior/consumer reference only. Do not copy its Skill source over ca-skills or make Compiler read it as a second source.
- `ca-skill-compiler` implements the language defined here. Compiler receives caller-supplied files and imported Owner/Tool contracts; it does not manage dependencies, projects, locks, caches, Git, Upload or MCP.
- The old `ca-skill-toolchain` is not a language authority and is not a compatibility target.

## Source scope

- The present 5GC packages `skills/establish-pdu-session/` and `skills/establish-pdu-session-mas/` are legacy v0.2/v1alpha1 behavioral/source examples, NOT v1alpha4 author syntax authority.
- Other historical Skill directories remain outside this refresh and must not be treated as current syntax authority.
- Preserve current business Procedure and Operation identities unless an explicit business-owner decision changes them.
- The MAS Skill's 16 `ca.pdu_session.*` Operation references remain unresolved. Do not invent or approve a ToolCatalog.

## Language contracts

Read before editing:
1. `docs/skill-language-spec.v1alpha4.zh-CN.md` (the current frozen v1alpha4 normative text)
2. `docs/script-contract.md` (legacy v0 source companion; cannot override v1alpha4)
3. `docs/schema-ownership.md`
4. `docs/authoring-model.md`
5. `docs/current-5gc-skill-baseline.md`
6. `language/semantic-tokens.v1.json` (legacy v0.2 selectors, not v1alpha4 syntax)

Key rules:
- Current v1alpha4 Node stages are `precondition`, `operation`, `observation`, `postcondition`; Pre/Post stages have one nonempty ordered `predicates` list each.
- Contract has one `goal` and may declare a **singular** `precondition: <node-id>.precondition`. Do NOT author Contract `preconditions`/`postconditions` or a `postcondition.goal` field.
- Exact external callable references use `operation.tool` / `observation.tool`; author `operation.reconcile` / `resolve` is forbidden. Trusted Owner `mutation.reconcile` belongs to the common Host safety boundary.
- Only a final Postcondition aggregate `PASS` routed directly to `SUCCEEDED` proves the Goal; PASS is not carried across Nodes.
- Source Schemas, Evidence and v1alpha4 ToolCatalog/CapabilityContracts require trusted Owner publications. Missing sources are blockers; a legacy `call`/`with` Script or Owner metadata snapshot cannot be silently relabeled as v1alpha4.
- Cases are source obligations only. Do not add a Qualification engine or claim Case execution.

## Validation

`make verify` performs repository-local source hygiene only. It does not invoke an old Toolchain, Compiler, Runtime or Qualification gate. Compiler conformance is verified in `ca-skill-compiler`; Runtime and live 5GC evidence belong to their owners.

Never claim Compiler/Runtime/Qualification/Live PASS from source hygiene.
