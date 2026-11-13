# CA Owner Schema snapshot

`invocation-context.schema.yaml` is imported as dependency `ca-context`.
The snapshot is copied from
[`ca-agent-demo` at `a8ff6a5d`](https://github.com/odango-chan/ca-agent-demo/blob/a8ff6a5de25fc6b169ac02f3d1dcf1179e738da1/src/ca_agent_host/integrations/fivegc/contracts/invocation-context.schema.yaml).
Refresh from the Owner when updating the dependency.


The Host-owned CreatedSession UDM normalized result is imported from
`ca-agent-demo` main after PR #205:
`createdsession-udm-runtime-value-v1alpha1.schema.yaml`.

Its exact Schema `$id` is
`https://connectionagent.io/ca-agent-host/createdsession/udm-runtime-value/v1alpha1/schema.yaml`.
The vNext Skill dependency snapshot imports this Host Schema under
`lib/schemas/ca/` and embeds the same schema document at
`lib/tools/createdsession.tool.yaml` →
`sbi.udm.sm_data.get.outputSchema.properties.result`. The source-hygiene
validator compares the embedded schema byte-for-byte with the imported Owner
Schema, so these are one contract snapshot rather than independent definitions.
The legacy ToolCatalog in `ca-agent-demo/main` remains unchanged. The upstream
Provider wire result Schema remains a separate Owner contract.
