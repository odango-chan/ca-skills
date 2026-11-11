# Skill Project Layout

This is the project-level contract shared by Skill Studio and the stateless Skill Compiler. It follows the accepted [Skill Compiler v0 design](https://github.com/odango-chan/ca-skill-toolchain/blob/main/docs/design/skill-compiler-v0.md).

## Three fixed roots

```text
project/
├── skills/   # author-owned source
├── lib/      # imported external contracts
└── output/   # generated build projection
```

These are semantic roots, not three interchangeable folders. Their names and roles are fixed by the project format. A user must not rename, move, or delete the three roots through ordinary Explorer actions.

| Root | Ownership | Studio interaction | Compiler role |
| --- | --- | --- | --- |
| `skills/` | Skill author | Editable source; create, rename, move and delete files/packages below this root | Primary source input |
| `lib/` | External contract owner; project holds an imported snapshot | Read-only preview. No inline edit, rename or arbitrary file mutation. Explicit Import / Re-import / Remove Import actions manage snapshots | Read-only dependency input |
| `output/` | Compiler | Read-only generated view; inspect, navigate diagnostics, copy/export ZIP or authorized folder | Build result only; never build input |

## 1. `skills/` — editable source

- Contains one directory per Skill package.
- Normal source editors, YAML validation, Python syntax support, Markdown preview and Procedure Designer apply here.
- Package children may be created, renamed, moved and deleted subject to package validation.
- Do not create another `source/` layer. `skills/` is the unique business source root.
- Other files at the project root are project metadata/docs; they are not additional Skill package roots.

## 2. `lib/` — imported and read-only

Library files are external contracts, not Skill-authored source.

- Display import provenance: source repository/path, source revision or digest, and import time when available.
- Open files in a read-only preview with normal syntax highlighting and navigation.
- Disable text editing, rename, move, paste-overwrite and ordinary Delete actions.
- Provide explicit `Import`, `Re-import` and `Remove Import` operations. Re-import replaces the imported snapshot from its owner; Remove Import removes the project reference/snapshot after confirmation. These are dependency-management actions, not source editing.
- Keep each imported file at its project-relative path. Do not copy a ToolCatalog into each Skill.
- Current import kind: `lib/tools/*.yaml` for ToolCatalog Operations. Optional future import kind: `lib/capabilities/*.yaml` for deployment-owned CapabilityContracts, when the project explicitly needs Capability-ID navigation. Such a snapshot is read-only and does not become a Skill-authored or deployment-approval authority.
- A present contract does not mean its Tool implementation is registered, deployed, READY, authorized or executable.
- A design draft is not an approved external contract and must not be imported as one.

The current 5GC project imports only `lib/tools/createdsession.tool.yaml` from `ca-agent-demo`. The conventional PDU Session Skill's 12 direct Operation grants and Procedure calls resolve against it. The project does not import the deployment-owned CapabilityContracts registry. The MAS Skill's 16 `ca.pdu_session.*` Operation identities remain unresolved; its design-only ToolCatalog is not imported.

## 3. `output/` — generated and read-only

- Represents the latest successful or partially successful compiler build projection.
- Studio may render it as a virtual tree; it need not exist as writable browser storage.
- Every generated item is read-only. Disable editing, rename, move, paste-overwrite and ordinary Delete actions.
- Allow inspection, diagnostics navigation, copying file content, ZIP export and authorized folder save.
- Rebuild replaces the generated projection. Do not patch generated files by hand.
- Never include `output/**` in a subsequent BuildRequest. Build inputs are `skills/**` and `lib/**` only.
- Never copy generated output back into `skills/` automatically. This avoids build → import → build recursion and source/output drift.
- In a local CLI, `output/` is an ordinary generated directory. It is ignored by source control and can be regenerated.

A ZIP is a delivery container, not a deployment, Runtime admission or qualification result.

## Explorer presentation

Use a subtle, consistent distinction rather than inventing a second visual language:

- `skills/`: source-folder icon (for example, folder/code) and normal editable affordances.
- `lib/`: library/import icon with a small lock or read-only marker; tooltip says “Imported · Read-only”.
- `output/`: build/package icon with a generated marker; tooltip says “Generated · Read-only”.

Keep the three roots visible in a stable order: `skills/`, `lib/`, `output/`. Their root context menus should be role-specific, not the ordinary file/folder menu. Do not show disabled editing actions that imply the user might unlock them; show only the supported role-specific actions.

## Compiler boundary

The Studio sends only source and imported files to the stateless Compiler:

```text
BuildRequest.files = skills/** + lib/**
BuildResult.outputFiles = output/**
```

The Compiler returns diagnostics and a file map. Studio owns the Explorer, editor permissions, visualizations, Problems view, ZIP/folder export and user authorization. The Compiler does not own UI state, workspace permissions, Runtime registration or deployment.

For this repository, `output/` is intentionally not committed. The checked-in `skills/` are author source; `lib/` is an explicitly imported read-only snapshot.
