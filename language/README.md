# Historical Skill semantic-token projection

The v0.2 registry and the [older draft catalog](../spec/skill-language-tokens.yaml) support legacy source positions. [CA-SL v1alpha5](../docs/skill-language-spec.md) is the current language target.

The machine-readable [semantic token registry](semantic-tokens.v1.json) classifies source positions for Skill Studio and future LSP consumers. It is a presentation projection, **not** a YAML grammar, Compiler schema, resolver or Runtime/admission contract.

## Authority

- `ca-skills` owns the versioned token categories and source-position mappings.
- The [CA-SL specification](../docs/skill-language-spec.md) defines current authoring syntax. This registry and the [legacy Script contract](../docs/script-contract.md) describe the historical source projection and Script interface.
- `ca-skill-compiler` owns parsing, source validity, reference resolution, type/binding checks and diagnostics.
- Skill Studio maps token roles to its theme. Theme colors are not language semantics.
- A future LSP reuses the same categories; it must not create a second vocabulary.

## Legacy v0.2 selector rules

- `legend.tokenTypes[].id` and modifiers are stable, case-sensitive semantic token identifiers.
- YAML AST selectors are structural paths. `*` matches one mapping key or sequence item, not arbitrary depth.
- Procedure main-node intents are `call`, `script`, `procedure`, `verify`, `reconcile` and `terminal`.
- Preconditions/postconditions steps support only `call`, `script` and `verify`.
- `call` is a keyword and its scalar value is an exact **Operation ID**.
- `allowedResources.capabilities[]` is a resource-grant reference; its value may be a Capability ID or a direct Operation ID.
- `script` and Predicate `evaluator.ref` values are Skill-relative Script paths. Python bodies retain ordinary Python syntax highlighting.
- `spec.context.schemas.*` values are references to external Owner Schemas under logical `lib/**`.
- A `reference` modifier means only “this scalar is in a reference position”; it does not mean the target resolves.
- Invalid YAML, unknown source roles and positions without exact ranges fall back to ordinary TextMate highlighting. Never guess spans.
- The projection never changes source bytes, runs scripts/tools or proves Compiler/Runtime acceptance.

## Not covered

The registry does not lex CEL/Python expressions, implement cross-file navigation, resolve Operation IDs, prove Host authorization, run Cases/Qualification or establish live 5GC readiness. These remain Compiler/Host/Runtime owner responsibilities.

See the [legacy 5GC source baseline](../docs/current-5gc-skill-baseline.md) for package versions and unresolved MAS Operation references.
