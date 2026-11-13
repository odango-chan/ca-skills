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
The `createdsession-tools::sbi.udm.sm_data.get` ToolCatalog snapshot repeats
this schema inline at `outputSchema.properties.result` because the current
Runtime Tool boundary validates self-contained schemas and does not resolve
external Schema references. Keep the two parsed schemas structurally equal.
The upstream Provider wire result Schema remains a separate Owner contract.
