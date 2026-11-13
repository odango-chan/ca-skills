# vNext Skill Authoring Model

**Status:** Normative business and Procedure authoring model for Skill Language vNext.

## 1. One deterministic source graph

- `assurance/procedure.yaml` is the deterministic workflow source.
- `SKILL.md` is model-facing business guidance; it is not a second execution graph.
- Cases record semantic obligations and scenarios; they are not executable workflow or runtime evidence.

## 2. Procedure inputs and minimal bindings

Procedure inputs are the Procedure's actual interface, not a mirror of the entire invocation Context. Declare only values the Procedure consumes or intentionally shares with descendants.

- `context.projections` grants access to approved Context projections; it does not inject them into Procedure or Operation inputs.
- Every consumer receives only its declared input projection. Extra caller fields are never forwarded.
- Operation requiredness comes from the Owner Input Schema. Required inputs must be bound; optional inputs are omitted unless deliberately supplied.
- `with.from: input` is a proposed opt-in same-name shorthand for named-object binding contracts (Operation and Procedure). It binds same-named required inputs only. Optional inputs require explicit bindings; explicit bindings override the shorthand.
- The shorthand never reads Context, parent state or prior-node outputs. Missing required same-name input is an error, not a fallback.
- Predicate uses an ordered `parameters` signature and positional `verify.arguments`; Script calls remain explicitly bound because Script has no separate parameter signature.
- A binding resolves against an authoritative Producer Schema. The Producer must be available on every path reaching the consumer.
- A missing or ambiguous Producer is a build error, not an invitation to guess.
- Omitted and explicit `null` are distinct. Schema `default` annotations do not authorize synthesized values.

## 3. Business-significant nodes

A main Procedure node represents a business-significant Operation, side-effect boundary, independent asynchronous procedure, recovery boundary or recognizable protocol/service step.

Do not create main-flow nodes merely for a local projection or deterministic calculation when it belongs inside the consuming node's `with` binding or a local Script.

## 4. Tool Operations and Observation Tools

- A Tool exposes exact callable Operations with Owner-defined Input/Output Schemas and declared Effect.
- An Observation Tool is a specialized read-only Tool contract. It uses the same ToolCatalog, dependency, Schema, Capability and Runtime admission model; it declares QueryContext/Input, normalized Output, authority, scope, freshness and Evidence guarantees.
- An Observation Tool query is invoked explicitly only when additional authoritative context is needed. It is not required for every Operation and is not one-to-one with Mutation Operations.
- A Predicate consumes explicit Operation outputs, Context projections or Observation query results; it never triggers acquisition itself.
- A MUTATION Operation is governed by Runtime Effect admission and commitment semantics.
- Mutation success does not by itself prove the desired business fact.
- Unknown mutation outcomes must reconcile the exact original operation; never blindly retry.

Each Operation belongs to exactly one Capability in the deployment CapabilityContracts. The Skill grants Capability IDs; Procedure calls exact Operation IDs.

## 5. Fact, Observation and Evidence

- A Fact is a domain, environment or execution-state statement.
- An Observation is an independently addressable read-only query capability over an Owner's facts/state, exposed as a specialized Tool contract. Its result carries source and temporal context.
- Observation Tools use the same ToolCatalog, dependency snapshots, Owner Schemas, CapabilityContracts and Runtime admission as other Tools; no parallel public ObservationSource registry exists in vNext.
- Evidence is validated support for the claim and remains separate from the business payload.
- Operation Result and Observation result are distinct. Reuse an adequate Operation output or trusted Context projection; query an Observation Tool only when additional authoritative context is needed.
- Preserve source ownership, scope, correlation, freshness, temporal semantics and Evidence guarantees in the Observation Tool contract and Host/Runtime validation.

## 6. Pure Predicate

A Predicate declares an ordered, typed `parameters` signature and a CEL or Script evaluator. Procedure invokes it with positional `verify.arguments`, in exactly the declared order. The Predicate signature establishes expected types at authoring time; Producer/Context Schemas establish actual source types, which Compiler checks for assignability at every call site. Predicate has no legacy Observation Ref declaration, acquisition, scope polling, freshness polling or hidden globals.

- CEL refers to the declared parameter names directly; Predicate Script receives the same named projection as `input.<name>`. Its input type environment is derived from the Predicate signature, not separately authored by the Script.
- Predicate arguments lower into the common canonical Binding Plan.
- Host/Runtime attaches Evidence separately and validates it before allowing a definite verdict.
- Predicate Script may return only Evidence refs attached to its own inputs.

## 7. Asynchronous Operation completion

There is no Skill-level Wait/Await/polling construct in vNext. Asynchronous protocol/service work belongs inside the owning Tool/Provider/SMF Operation. The Operation returns its final normalized result and correlated Evidence before Procedure advances. Host retains invocation deadline, cancellation, correlation and UNKNOWN handling as Runtime controls; they are not Skill-authored wait loops.

## 8. Node preconditions and postconditions

`preconditions` are ordered node-entry steps. They complete immediately before the main Operation and stop on the first non-success result.

`postconditions` establish facts after the main Operation and before the business flow advances. Steps are ordered; only PASS advances. FAIL and UNKNOWN follow explicit routes.

Node postconditions differ from `SkillContract.spec.postconditions`, which are final Skill acceptance conditions.

## 9. Script and Schema ownership

- A Script identity is Skill package plus relative Python path.
- Procedure Script input comes from its call-site `with`.
- Predicate Script input is derived from the owning Predicate's typed `parameters` signature plus Host Evidence refs; it does not define another Input Schema.
- Procedure Script input is derived from the call site's explicit `with` projection; it does not define another Input Schema.
- Script output comes from a strict return `TypedDict` and is generated by Compiler.
- Scripts are deterministic local computation only; they do not invoke Tools or external systems.

## 9. 5GC migration baseline

The 5GC Skill's 36 Cases and three References preserve the business scenarios and expected semantics. They are not a requirement to preserve the old Observation architecture or old source field layout.

The vNext migration is judged by the same verified 5GC business behavior and real network capabilities, using the new Tool/Observation/Capability/Operation/Predicate contracts. A source-backed migration rehearsal is required to prove behavior, provenance, scope, freshness, correlation and Evidence equivalence before removing legacy ObservationSource implementations.
