# Skill semantic-token projection contract v0.1

The machine-readable [semantic token contract](semantic-tokens.v1.json) identifies
the **roles of source tokens** that editor consumers may color. This is a
presentation-oriented projection of the current ConnectionAgent Skill authoring
model, **not a new YAML grammar**, a compiler schema, a name resolver, or a
Runtime/admission contract.

## Authority and consumers

- `ca-skills` owns the versioned semantic category names and the mappings
  grounded in current official Skill source.
- `ca-skill-compiler` owns target parsing, source validity, reference
  resolution and diagnostics. The existing legacy Toolchain is authoritative
  only for constructs it actually supports.
- Skill Studio provides an editor-side projection and a theme. The theme's
  colors are not part of the language definition.
- A future LSP may emit these same categories as semantic tokens; it must
  not invent a parallel category vocabulary.

This v0.1 taxonomy describes known YAML source roles found in the two 5GC
Skills, including Contract, Procedure, Predicate, Schema and imported
ToolCatalog shapes. Python and Markdown retain their normal syntax
highlighting. A future category addition needs a deliberate contract version
update, cross-consumer tests and a documented provenance change.

## Rules

- `legend.tokenTypes[].id` and `legend.tokenModifiers[].id` are stable,
  case-sensitive VS Code semantic token identifiers.
- `profiles[*].file` selects a relative path with `*` in at most one
  filename segment. Each `rules[].path` is a slash-separated YAML AST path.
  `*` matches one mapping key or one sequence element, never an arbitrary
  depth. `part: key` selects a mapping key; `part: value` selects a scalar.
- `keywords` classify only recognized fields within named structural
  parents. Unknown fields and the same words inside business data do not
  automatically receive a Skill-specific color.
- A `reference` modifier means “this scalar is in a reference position,”
  **not** that the target resolves or the Runtime permits it.
- An `imported` modifier describes a read-only Library declaration; it is
  not a statement about implementation availability or Tool eligibility.
- Invalid YAML, multi-line literals without an exact single-line scalar
  range, and unrecognized file roles fall back to the editor's ordinary
  TextMate syntax highlighting. Never guess source spans or values.
- The document is a read-only color projection. It must not change source
  bytes, require cross-file navigation, or execute scripts/Tools.

## Known source limitations

- The conventional Skill's node-level `preconditions/postconditions` are
  in the source baseline but are not recognized by the legacy Toolchain
  schema; coloring these positions is not compile approval.
- MAS `ca.pdu_session.*` references remain unresolved against the currently
  imported conventional ToolCatalog. A purple Capability token is still only
  a reference, not a successful link.
- Source maps/rules are intentionally bounded; nested Script data and
  arbitrary CEL/Python expressions are not lexed into a second language here.
- Distinguish success of semantic coloring tests from Compiler build/link,
  LSP navigation, Runtime qualification and live 5GC acceptance.

The official 5GC source refresh is tracked separately in
[ca-skills PR #22](https://github.com/odango-chan/ca-skills/pull/22).
