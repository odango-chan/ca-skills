# ca-skills repository rules

## Authority

- This repository is the **only authoritative input** for official Skill source and Skill language semantics.
- `ca-agent-demo` is a behavior/consumer reference only. Do not copy its Skill source over ca-skills or make Compiler read it as a second source.
- `ca-skill-compiler` implements the language defined here. Compiler receives caller-supplied files and imported Owner/Tool contracts; it does not manage dependencies, projects, locks, caches, Git, Upload or MCP.
- The old `ca-skill-toolchain` is not a language authority and is not a compatibility target.

## Source scope

- The v1alpha4-shaped PDU Session authoring examples are at `examples/skills/establish-pdu-session/` and `examples/skills/establish-pdu-session-mas/`; the original v0.2/v1alpha1 business sources and Cases are archived under `examples/legacy/`, NOT imported into current v1alpha4 builds.
- Other historical Skill directories remain outside this refresh and must not be treated as current syntax authority.
- Preserve current business Procedure and Operation identities unless an explicit business-owner decision changes them.
- For every 5GC Skill, follow [docs/authoring-5gc-3gpp-profile.md](docs/authoring-5gc-3gpp-profile.md): model from the SMF perspective, map each Node to a 3GPP interaction or explicitly classify it as a CA adapter/extension, use canonical 3GPP names where available, and trace every Capability to its NF/service scope.
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
- Do not present helper functions, internal methods, AMF/RAN/UE-owned actions, or unpublished CA operations as standard 3GPP Operations. Exact callable IDs must come from trusted Owner exports; record the 3GPP mapping separately.

## Validation

`make verify` performs repository-local **example-source shape hygiene, legacy snapshot hygiene, and v1alpha4 documentation structure lint with negative tests**. It does not resolve trusted v1alpha4 Owner exports. It does not invoke an old Toolchain, Compiler, Runtime or Qualification gate. Compiler conformance is verified in `ca-skill-compiler`; Runtime and live 5GC evidence belong to their owners.

Never claim Compiler/Runtime/Qualification/Live PASS from source hygiene.
