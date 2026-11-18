# Historical ToolCatalog snapshot

The [legacy 5GC source](../skills/README.md) uses the read-only snapshot under `tools/`. CA-SL v1alpha5 receives trusted Owner contracts as caller-supplied dependency snapshots. See [Schema ownership](../docs/schema-ownership.md) for the current dependency model.

## Pinned import

| Local path | Source | Source commit | Use |
| --- | --- | --- | --- |
| `tools/createdsession.tool.yaml` | `odango-chan/ca-agent-demo/tools/contracts/createdsession.tool.yaml` | `4395982fa6efb97714b97901603b2dfb7018c4d0` | 12 conventional 5GC Operations used by `establish-pdu-session` |

An imported contract proves only that a contract snapshot is present. It does not prove that an implementation is registered, deployed, READY, or authorized.

The MAS Skill references 16 `ca.pdu_session.*` Operation identities that are not present in this snapshot. These comprise 14 MAS business operations and two Host-side resource-finalization/cleanup operations. Its `design/tool-contract.yaml` is a design artifact, not an approved ToolCatalog, and is intentionally not imported.
