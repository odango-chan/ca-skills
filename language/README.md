# Skill semantic-token projection contract v0.2

The machine-readable [semantic token registry](semantic-tokens.v1.json) classifies source positions for Skill Studio and future LSP consumers. It is a presentation projection, **not** a YAML grammar, Compiler schema, resolver or Runtime/admission contract.

## Authority

- `ca-skills` owns the versioned token categories and source-position mappings.
- `docs/skill-language-spec.md` and `docs/script-contract.md` own the source-language semantics.
- `ca-skill-compiler` owns parsing, source validity, reference resolution, type/binding checks and diagnostics.
- Skill Studio maps token roles to its theme. Theme colors are not language semantics.
- A future LSP reuses the same categories; it must not create a second vocabulary.

## Current v0.2 rules

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

The current two 5GC Skills are the source examples. MAS Operation references remain unresolved until an approved ToolCatalog is supplied.
