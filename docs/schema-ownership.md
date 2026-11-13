# Schema Ownership — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The complete and authoritative Schema ownership, identity, Evidence, Observation and binding rules are maintained in the CA-SL specification. This file is retained as an implementation-oriented index. If any wording here conflicts with the specification, the specification takes precedence.

Ownership summary:
- Skill owns its public Request Schema and genuinely Skill-owned data.
- Tool Owner owns Operation Input / Output / Reconcile Schemas.
- Observation Owner publishes QueryContext / Input and normalized Output Schemas through ToolCatalog.
- Host / Context Owner owns Subject, Facts, Ingress and Evidence-reference projections.
- Procedure Script inputs derive from explicit call-site bindings.
- Predicate Script inputs derive from the Predicate signature plus Host-attached Evidence refs.
- Script output Schema is generated from the declared TypedDict.
- Consumers must not copy external Owner Schemas into the Skill package.
