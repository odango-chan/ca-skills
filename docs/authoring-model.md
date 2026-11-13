# Authoring Model — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The comprehensive specification is the sole normative language authority. If this file conflicts with it, the specification takes precedence.

Procedure business nodes:
- `precondition`: invokes a Predicate before a business action.
- `operation`: invokes an Owner-published Tool Operation.
- `observation`: optionally invokes an Owner-published read-only query when existing results are insufficient or independent observation is required.
- `postcondition`: invokes a Predicate to judge the business outcome.

`terminal` declares an explicit terminal state. Predicate is the deterministic computation / judgment definition, implemented in CEL or a constrained Python evaluator; it is not a separate Procedure node. Python Script is not a free-standing computation node.

Call arguments:
- Operation and Observation use a named `arguments` mapping whose keys are Owner Schema fields.
- Precondition and Postcondition use an ordered `arguments` list matching the Predicate signature.
- Procedure inputs use direct Source Path mappings.
- The old `call`, `verify`, `with`, `from`, and `value` node-binding forms are not vNext syntax.

Observation follows the Result Sufficiency Principle: reuse an adequate Operation Result and its Evidence; query independently only when required. Reconcile is a constrained Operation mode targeting the original Mutation, not a separate business node.

Other details and normative examples are in the main specification.
