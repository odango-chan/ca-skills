# ca-skills repository rules

## Authority

- This repository is the **only authoritative input** for official Skill source and Skill language semantics.
- `ca-agent-demo` is a behavior/consumer reference only. Do not copy its Skill source over ca-skills or make Compiler read it as a second source.
- `ca-skill-compiler` implements the language defined here. Compiler receives caller-supplied files and imported Owner/Tool contracts; it does not manage dependencies, projects, locks, caches, Git, Upload or MCP.
- The old `ca-skill-toolchain` is not a language authority and is not a compatibility target.

## Source scope

- Current syntax examples: `skills/establish-pdu-session/` and `skills/establish-pdu-session-mas/`.
- Other historical Skill directories remain outside this refresh and must not be treated as current syntax authority.
- Preserve current business Procedure and Operation identities unless an explicit business-owner decision changes them.
- The MAS Skill's 16 `ca.pdu_session.*` Operation references remain unresolved. Do not invent or approve a ToolCatalog.

## Language contracts

Read before editing:
1. `docs/skill-language-spec.md`
2. `docs/script-contract.md`
3. `docs/schema-ownership.md`
4. `docs/authoring-model.md`
5. `docs/current-5gc-skill-baseline.md`
6. `language/semantic-tokens.v1.json`

Key rules:
- Procedure `call` is a scalar exact Operation ID. No dependency/operation wrapper.
- Main node intents: `call`, `script`, `procedure`, `verify`, `reconcile`, `terminal`.
- Preconditions/postconditions steps: `call`, `script`, `verify`.
- Script identity is Skill + relative file path. No `connectionagent-tool` metadata and no independent local Tool ID.
- Script signature is `main(input: dict) -> NonEmptyOutputTypedDict`; inputs derive from Procedure `with` or Predicate Evaluation Context; output Schema is generated.
- External Producer Schemas come from real Owner files. `requiredFacts` is not a Schema. Missing Owner files remain explicit blockers.
- Cases are source obligations only. Do not add a Qualification engine or claim Case execution.

## Validation

`make verify` performs repository-local source hygiene only. It does not invoke an old Toolchain, Compiler, Runtime or Qualification gate. Compiler conformance is verified in `ca-skill-compiler`; Runtime and live 5GC evidence belong to their owners.

Never claim Compiler/Runtime/Qualification/Live PASS from source hygiene.
