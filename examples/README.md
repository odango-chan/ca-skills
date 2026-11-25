# CA-SL v1alpha5 PDU Session examples

- **Language target**: connectionagent.io/v1alpha5
- **Normative source**: [CA-SL v1alpha5 release record](../docs/releases/ca-sl-v1alpha5.md)
- **Status**: Illustrative authoring examples. Product and Owner qualification remains NOT_QUALIFIED.

- [establish-pdu-session](skills/establish-pdu-session/SKILL.md) models the conventional 5GC success path. The Step 11 transfer Operation triggers the Step 15 Node-entry Wait. The accepted request is available as wait.output, the authored timeout goes to SAFE_STOPPED, and Step 17 has its own typed response boundary after Step 16.
- [establish-pdu-session-mas](skills/establish-pdu-session-mas/SKILL.md) follows the OpenAMSM MAS source plan. The composite MAS Operation handles its own event correlation.
- [modify-pdu-session-mas](skills/modify-pdu-session-mas/SKILL.md) follows OpenAMSM pdu-mod-v3.yaml, with explicit UE / AMF / network-triggered Host classification and separate m3 / m5 Mutation occurrences. Optional m2 is excluded because the source plan defines no applicability predicate.
- [release-pdu-session-mas](skills/release-pdu-session-mas/SKILL.md) follows OpenAMSM pdu-rel-v4.yaml, with explicit numeric trigger mapping and mandatory r2–r6 source steps. Optional r1 is excluded, and r7 compensation / replan is not imported.

The conventional Skill's integration dependency stands in for the deployment's trusted IngressCatalog package. Building the examples requires the exact Owner exports and trusted bindings. The Ingress Operation, its Schemas and response mappings, and the MAS ToolCatalog remain unpublished for these examples. All urn:example values are illustrative.

## Skill applicability design example

This proposed excerpt shows the optional top-level field in the existing
[`establish-pdu-session-mas` Contract](skills/establish-pdu-session-mas/assurance/contract.yaml).
The normalized event names and input binding illustrate the selection context.
The existing Contract fields follow the excerpt.

```yaml
when: 'event.type == "nsmf.create-sm-context" && input.requestType == 1'
```

For that event, a normalized integer `requestType` of `1` matches. Another
request type does not match. The [authoring guide](../docs/authoring.md#skill-applicability-proposed-extension)
describes the proposal. The checked-in YAML examples target the frozen
v1alpha5 compiler.
