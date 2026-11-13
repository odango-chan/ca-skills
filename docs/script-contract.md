# Skill-owned Python Predicate Evaluator Contract

**Status:** Companion implementation contract. The [CA-SL vNext Specification](skill-language-spec.zh-CN.md) is the sole normative language authority. If any wording here conflicts with it, the specification takes precedence.

Python Script is an implementation of a Predicate evaluator, not an independent Procedure node, Tool, Operation, or general-purpose computation step.

Core rules:
- The only entry point is `main(input: dict) -> PredicateOutcome`.
- `PredicateOutcome` is exactly `Literal["PASS", "FAIL", "UNKNOWN"]`.
- Business input types derive from the owning Predicate's ordered `parameters` signature.
- Host / Runtime may attach reserved, read-only Evidence refs; Script cannot create, modify, rebind, or widen them.
- Compiler / LSP provides the derived read-only input type environment; authors do not maintain a duplicate Script Input Schema.
- Script cannot access network, HTTP, MCP, shell, database, filesystem, credentials, environment variables, clock, or randomness.
- Compiler validates annotations and restrictions without executing Python to infer schemas or behavior.
