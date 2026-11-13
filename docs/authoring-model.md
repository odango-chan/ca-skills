# Authoring Model — Companion Notes

**Status:** Non-normative companion to the [CA-SL vNext Specification](skill-language-spec.zh-CN.md).

The comprehensive specification is the sole normative language authority. If this file conflicts with it, the specification takes precedence.

## Author-maintained source

vNext retains three assurance source files with distinct responsibilities:

- `assurance/contract.yaml`: Skill's public contract — Goal, public Request Schema, required Context facts / Schemas, shared dependency identities and Capability Grants.
- `assurance/procedure.yaml`: the single deterministic execution graph — input projections, start, nodes, routes, reconciliation and final Postcondition.
- `assurance/predicates.yaml`: reusable Predicate definitions and ordered parameter signatures.

Contract is author-maintained source, not a compiler-generated file. The source omits redundant `apiVersion`, `kind` and `metadata.name`; language version comes from BuildRequest / Compiler Target and Skill identity comes from the Package root.

## Contract and dependency semantics

- Goal and public Request belong to Contract, not the Procedure graph.
- Required Host facts and Context Schema identities are explicit Contract requirements.
- Public dependencies declare the stable Owner / Package identities needed for linking. They do not contain source URLs, versions, digests, locks or downloaded bytes.
- Capability Grants are separate from dependencies. Dependencies make contracts available; grants request authorization.
- Studio guides creation by selecting dependencies and Capabilities from available public catalogs, writes stable identities into Contract and obtains exact dependency snapshots for the BuildRequest.
- Compiler receives exact bytes and trusted CapabilityContracts as inputs. It never downloads dependencies, manages versions or infers authorization from the set of imported Tools.
- The exact dependency snapshot / revision selected by Studio belongs to project/build configuration. Owner Schema IDs that intrinsically encode immutable revisions must be preserved exactly.

## Procedure graph

There are four business node types:

- precondition: invokes a Predicate before a protected action;
- operation: invokes either an Owner-published Tool Operation or a Skill-owned pure Procedure Script;
- observation: optionally invokes an Owner-published read-only query when existing values are insufficient or independent observation is required;
- postcondition: invokes a Predicate to judge an intermediate or final business result.

terminal declares an explicit terminal state; it is not a business action. Predicate is the reusable deterministic judgment definition, not a separate Procedure node. There is no generic computation node.

Invocation-wide preconditions belong to the entry gate. If their facts are not already available in trusted Context, explicit Observation nodes may acquire them before the Precondition. No protected Mutation may bypass the required Precondition PASS. The final business Postcondition belongs at the end, before every successful terminal. All SUCCEEDED paths must pass its PASS route. There is no Contract-level duplicate postconditions declaration and no second evaluation through a from reference. Local Precondition / Postcondition nodes remain available where needed.

The first vNext version has one entry Procedure graph per Skill and does not define nested ProcedureCall or graph cycles. Branches and recovery are explicit nodes and routes.

## Arguments and dataflow

- Tool Operation and Observation use a named arguments mapping defined by the Owner Input / Query Schema.
- Procedure Script uses a named arguments mapping as its exact local input projection; its output Schema is derived from strict return TypedDict.
- Precondition and Postcondition use an ordered arguments list matching the Predicate.parameters signature.
- Procedure inputs use direct SourcePath mappings.
- No implicit previous-node binding, parent Procedure state, ambient Context forwarding, or field-name guessing.
- Reconcile is a constrained Operation mode targeting the original Mutation, not a separate business node.

## Script roles

A Procedure Script is a pure local data transformation / selection invoked through an Operation node. It is not a Tool, Capability, or external READ / MUTATION effect.

A Predicate Script implements a Predicate evaluator and returns the structured PredicateEvaluationResult. Its business inputs derive from Predicate.parameters; Evidence remains Host-attached and read-only.

## Generated artifacts and policies

Compiler derives normalized contracts, execution graph, type bindings and generated Schema artifacts from the author sources and exact dependency snapshots.

- No Contract-level `entryProcedure` is needed because the Skill has one Procedure graph.
- Final Postcondition is an executable Procedure node, not a duplicate Contract list.
- Dynamic Procedure generation is forbidden by the static DAG language rule.
- Runtime action budgets belong to Host / Deployment Policy unless proven to be Skill-specific business semantics.
- Mutation UNKNOWN reconciliation is a general Runtime safety invariant; it is not a per-Skill on/off switch.

Generated Schema serialization and whether a deployment bundle embeds the reachable external dependency closure or keeps exact external references belong to the separate Compiler / Deployment Artifact Contract—not the CA-SL node grammar.
