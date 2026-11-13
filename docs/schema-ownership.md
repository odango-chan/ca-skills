# Schema Ownership — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The comprehensive specification is the sole normative source for Schema ownership, identity, Evidence, Observation and argument binding. If this note conflicts with the specification, the specification takes precedence.

Ownership summary:
- Skill owns its public Request Schema and genuinely Skill-owned data.
- Tool Owner owns Operation Input / Output / Reconcile Schemas.
- Observation Owner publishes Query Input and normalized Output Schemas through ToolCatalog.
- Host / Context Owner owns Subject, Facts, Ingress and Evidence-reference projections.
- Procedure inputs are explicit Source Path mappings.
- Operation / Observation arguments are named mappings checked against Owner Schemas.
- Predicate arguments are ordered positional values checked against Predicate.parameters.
- Predicate Script inputs derive from the Predicate signature plus Host-attached Evidence refs.
- Predicate Script returns PASS / FAIL / UNKNOWN; it is not an independent Procedure node.
- Consumers must not copy external Owner Schemas into the Skill package.
