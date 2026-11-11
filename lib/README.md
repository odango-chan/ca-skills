# Imported Tool Library

This directory contains exact snapshots of externally owned contracts. Treat every file here as **imported and read-only**; refresh from the owning repository rather than editing the snapshot in place. Current imports are ToolCatalogs under `tools/`. A project may optionally import a deployment-owned CapabilityContracts snapshot under `capabilities/` when Capability-ID navigation is required; no such snapshot is present in this project.

## Current import

| Local path | Source | Source commit | Use |
| --- | --- | --- | --- |
| `tools/createdsession.tool.yaml` | `odango-chan/ca-agent-demo/tools/contracts/createdsession.tool.yaml` | `4395982fa6efb97714b97901603b2dfb7018c4d0` | 12 conventional 5GC Operations used by `establish-pdu-session` |

An imported contract proves only that a contract snapshot is present. It does not prove that an implementation is registered, deployed, READY, or authorized.

The MAS Skill references 16 `ca.pdu_session.*` Operation identities that are not present in this snapshot. These comprise 14 MAS business operations and two Host-side resource-finalization/cleanup operations. Its `design/tool-contract.yaml` is a design artifact, not an approved ToolCatalog, and is intentionally not imported.
