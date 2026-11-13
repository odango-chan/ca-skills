# Authoring Model — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The comprehensive specification is the sole normative language authority. If this file conflicts with it, the specification takes precedence.

## Author-maintained source

vNext does not require a separate authored SkillContract or assurance/contract.yaml. The single assurance/procedure.yaml source contains:
- goal: the Skill's business goal;
- requestSchema: the Skill-owned public Request Schema;
- capabilities: explicit Capability grants;
- inputs: explicit Procedure input projections;
- start and nodes: one deterministic Procedure graph.

Skill identity is derived from the Package root. Language/API version, kind, metadata and any normalized SkillContract projection are Compiler-generated build information, not duplicated author fields.

## Procedure graph

There are four business node types:
- precondition: invokes a Predicate before a protected action;
- operation: invokes either an Owner-published Tool Operation or a Skill-owned pure Procedure Script;
- observation: optionally invokes an Owner-published read-only query when existing results are insufficient or independent observation is required;
- postcondition: invokes a Predicate to judge an intermediate or final business result.

terminal declares an explicit terminal state; it is not a business action. Predicate is the reusable deterministic judgment definition, not a separate Procedure node. There is no computation node.

Invocation-wide preconditions belong at the beginning of the graph. The final business Postcondition belongs at the end, before every successful terminal. All SUCCEEDED paths must pass its PASS route. There is no separate SkillContract.postconditions declaration and no second evaluation through a from reference. Local Precondition / Postcondition nodes remain available where needed.

The first vNext version has one entry Procedure graph per Skill and does not define nested ProcedureCall or graph cycles. Branches and recovery are explicit nodes and routes.

## Arguments and dataflow

- Tool Operation and Observation use a named arguments mapping defined by the Owner Input / Query Schema.
- Procedure Script uses a named arguments mapping as its exact local input projection; its output Schema is derived from strict return TypedDict.
- Precondition and Postcondition use an ordered arguments list matching the Predicate.parameters signature.
- Procedure inputs use direct SourcePath mappings.
- No implicit previous-node binding, parent Procedure state, ambient Context forwarding, or field-name guessing.
- Reconcile is a constrained Operation mode targeting the original Mutation, not a separate business node.

## Script roles

A Procedure Script is a pure local data transformation/selection invoked through an Operation node. It is not a Tool, Capability, or external READ/MUTATION effect.

A Predicate Script implements a Predicate evaluator and returns the structured PredicateEvaluationResult. Its business inputs derive from Predicate.parameters; Evidence remains Host-attached and read-only.

## Build artifacts

Source YAML remains authoritative. Compiler derives normalized contracts, execution graph, type bindings and generated Schema artifacts. Whether generated Schemas serialize as YAML or canonical JSON, and whether a deployment bundle embeds the reachable external dependency closure or keeps exact external references, belong to the separate Compiler / Deployment Artifact Contract—not the CA-SL node grammar.
