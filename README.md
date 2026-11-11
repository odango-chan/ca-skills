![ConnectionAgent Skills](assets/repo-banner.svg)

# ConnectionAgent Skills

Official Skill source and authoring guidance for ConnectionAgent.

## Current 5GC baseline

The current 5GC source baseline contains two separate executable Skills:

| Package | Business profile |
| --- | --- |
| `establish-pdu-session` | UE-requested initial PDU Session Establishment through the conventional 5GC procedure |
| `establish-pdu-session-mas` | UE-requested initial PDU Session Establishment through the SMF MAS policy-first profile |

Both packages were synchronized from `odango-chan/ca-agent-demo` main at `4395982fa6efb97714b97901603b2dfb7018c4d0`. See [the source and compatibility record](docs/current-5gc-skill-baseline.md).

The repository also contains a read-only imported ToolCatalog snapshot at `lib/tools/createdsession.tool.yaml`. It contains the 12 Operations used by the conventional Skill. It does not contain the 16 MAS Operations; the MAS design-only Tool contract is not treated as an approved import.

**Validation status:** source synchronization is complete in this change, but compiler/link validation and Runtime qualification are not claimed. The conventional Procedure uses node-level `preconditions/postconditions` that the legacy Toolchain schema does not support. The MAS package has unresolved imported Capability references. The new stateless Compiler v0 design is accepted, but implementation is not yet available.

## Repository layout

```text
ca-skills/
├── skills/                  # official Skill source
├── lib/                     # imported, read-only external contracts
├── output/                  # generated build output (not committed)
├── docs/                    # authoring and maintainer guidance
├── spec/                    # machine-readable Skill language token/reference catalog
├── scripts/verify.py        # existing legacy verification entrypoint
└── .agents/skills/           # repository-local authoring assistant
```

The project follows the `skills/` + `lib/` + `output/` model: editable Skill source, imported read-only contracts, and generated read-only build output. See [Project Layout](docs/project-layout.md) for Explorer behavior and the Compiler boundary.

## Authoring

- [Skill Language Specification](docs/skill-language-spec.md)
- [Semantic token catalog](spec/skill-language-tokens.yaml)
- English: [Authoring guide](docs/authoring.md)
- 中文：[Skill 编写指南](docs/authoring.zh-CN.md)
- [Skill Language Specification](docs/skill-language-spec.md)
- [Authoring model](docs/authoring-model.md)
- [Current 5GC Skill baseline](docs/current-5gc-skill-baseline.md)

`SKILL.md` is the model-facing business guide. `assurance/` contains the deterministic source contract. `references/` contains optional flat Markdown knowledge selected when useful. `scripts/` contains governed local computation only.

## Ownership

| Repository | Responsibility |
| --- | --- |
| `ca-skills` | Official Skill source and authoring semantics |
| `ca-skill-toolchain` | Legacy machine schemas/compiler and existing Toolchain implementation |
| `ca-skill-compiler` | Target stateless multi-Skill compiler; bootstrap only, implementation pending |
| `ca-agent-demo` | Generic Agent Host reference implementation and current source sample |
| `ca-runtime` | Admission, operation authority, evidence and deterministic execution |

Other historical packages remain untouched and are outside the current 5GC baseline. They are not used as current authoring examples.
