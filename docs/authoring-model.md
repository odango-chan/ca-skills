# vNext Skill Authoring Model

**Status:** Normative business and Procedure authoring model for Skill Language vNext.

## 1. One deterministic source graph

- `assurance/procedure.yaml` is the deterministic workflow source.
- `SKILL.md` is model-facing business guidance; it is not a second execution graph.
- Cases record semantic obligations and scenarios; they are not executable workflow or runtime evidence.

## 2. Procedure inputs and explicit bindings

Procedure inputs are named aliases over the frozen invocation context. The Contract declares the Owner Schema for each exposed context namespace once; Procedure paths such as `context.subject.ueRef` use that declared contract. Every Operation, Script and Predicate consumer receives explicit `with/from` bindings. Input types are derived from the producer Schema, not repeated as author-written `type` fields.

- A binding resolves against an authoritative Producer Schema.
- The Producer must be available on every path reaching the consumer.
- No implicit previous-node binding, automatic semantic matching, hidden context injection or string interpolation is allowed in the initial vNext implementation.
- A missing or ambiguous Producer is a build error, not an invitation to guess.

### 2.1 Context projections are schema bindings

`SkillContract.context.projections` maps each runtime context namespace used by the Skill to one exact imported Owner Schema:

- the map key is the root name used in Procedure paths, such as `context.subject`;
- the value is an alias-qualified Schema `$id`, such as `fivegc-context::urn:connectionagent:5gc:skill-context:subject:v1`;
- the dependency alias selects the caller-supplied BuildRequest snapshot; it is not the Schema owner or a runtime data value.

The Host/integration creates the actual context before Procedure execution. The Compiler only resolves the Schema and checks paths/types; it does not construct or fetch context. Runtime receives the actual values and validates their dynamic properties and Evidence.

For the 5GC entry, `subject` identifies the UE through `ueRef`; `facts` carries exact ingress/lifecycle correlation handles; and `ingress` carries a narrow projection of the admitted HELD message. These are different contracts. The `request` namespace is governed separately by the Skill-owned `requestSchema`, so it is not repeated in `context.projections`.

The current `facts` projection contains handles, not assertions such as registration or forwarding readiness. Those business facts must come from their authoritative READ Operations and Evidence. Keep the Host Owner's namespace name; any rename must be coordinated with its schema and materializer.

## 3. Business-significant nodes

A main Procedure node represents a business-significant Operation, side-effect boundary, independent asynchronous procedure, recovery boundary or recognizable protocol/service step.

Do not create main-flow nodes merely for a local projection or deterministic calculation when it belongs inside the consuming node's `with` binding or a local Script.

## 4. READ and MUTATION Operations

- A READ Operation returns one typed normalized value and Evidence from that same invocation.
- A Predicate consumes that exact output; it does not trigger another read.
- A MUTATION Operation is governed by Runtime Effect admission and commitment semantics.
- Mutation success does not by itself prove the desired business fact.
- Unknown mutation outcomes must reconcile the exact original operation; never blindly retry.

Each Operation belongs to exactly one Capability in the deployment CapabilityContracts. The Skill grants Capability IDs; Procedure calls exact Operation IDs.

## 5. Pure Predicate

A Predicate declares named `inputs` and a CEL or Script evaluator. It has no Observation declaration, scope acquisition, freshness polling or hidden globals.

- Procedure `verify.with` supplies all Predicate inputs.
- CEL and Script evaluators read `input.<name>`.
- Host/Runtime attaches Evidence separately and validates it before allowing a definite verdict.
- Predicate Script may return only Evidence refs attached to its own inputs.

## 6. Waiting

Bounded waiting is a Host Runtime Operation, not a Predicate feature. It targets one exact READ Operation and explicit scope. It returns a wait summary only. Procedure then performs a final READ Operation and supplies that final result to the Predicate.

Wait and final read must share the exact attempt selector. The wait target must also be covered by a granted Capability.

## 7. Node preconditions and postconditions

`preconditions` are ordered node-entry steps. They complete immediately before the main Operation and stop on the first non-success result.

`postconditions` establish facts after the main Operation and before the business flow advances. Steps are ordered; only PASS advances. FAIL and UNKNOWN follow explicit routes.

Node postconditions differ from `SkillContract.spec.postconditions`, which are final Skill acceptance conditions.

## 8. Script and Schema ownership

- A Script identity is Skill package plus relative Python path.
- Procedure Script input comes from its call-site `with`.
- Predicate Script input comes from declared Predicate inputs plus Host Evidence refs.
- Script output comes from a strict return `TypedDict` and is generated by Compiler.
- Scripts are deterministic local computation only; they do not invoke Tools or external systems.

## 9. 5GC migration baseline

The 5GC Skill's 36 Cases and three References preserve the business scenarios and expected semantics. They are not a requirement to preserve the old Observation architecture or old source field layout.

The vNext migration is judged by the same verified 5GC business behavior and real network capabilities, using the new Operation/Capability/Predicate contracts. No separate migration rehearsal is required. Paper review finds Owner gaps; implementation and focused tests close them.
