# Capability & Authoring Model vNext

Status: **DESIGN-FROZEN (semantic and authoring principles)**  
Version: vNext design baseline  
Scope: ca-skills authoring language and its contracts. This document freezes design principles and migration constraints; it does not claim that the proposed syntax is implemented by the current Compiler or Agent Host.

## 1. Purpose

Unify Capability, Operation, Procedure, Predicate, data binding, Schema ownership, and Evidence semantics into one coherent Skill authoring model.

The design must reduce repetitive YAML without introducing implicit, ambiguous, or runtime-guessed behavior. Existing deterministic 5GC behavior and its evidence guarantees must be preserved during migration.

## 2. Frozen conceptual model

### 2.1 Capability and Operation

- **Capability** is the stable logical identity and authorization boundary for a capability exposed by an implementation.
- **Operation** is the exact callable interface of a Capability.
- Every Operation declares an Effect. The initial supported effects remain `READ` and `MUTATION`.
- A Tool is an implementation/registration unit for one or more Operations; it is not a second authoring-level capability identity.
- Procedure and Predicate both reference exact Operation identities. They must not invent parallel identities for the same callable ability.

### 2.2 Observation

- Observation is not a separate callable identity, registry, or independent Tool category.
- An Observation is a fact acquired by invoking a `READ` Operation and using its output in a Predicate/evaluation context.
- An Operation output is not automatically authoritative evidence merely because its Effect is `READ`.
- Predicate may consume an already-produced Operation output, or declare a required READ Operation to acquire a current/authoritative fact.
- The independent Observation Ref → Observation Source registration model is to be retired through migration, not removed before equivalent behavior is covered.

### 2.3 Evidence

- Evidence is the validated support for a factual claim, not the fact payload itself and not another Capability.
- The Tool/Operation owner defines the evidence guarantees it can provide; Host defines the generic evidence envelope and performs generic validation.
- Evidence requirements may include provenance, observed time, correlation/scope, freshness, and completeness where applicable.
- A mutation response (including a successful HTTP status) is not by itself proof that the external target state now holds.
- Runtime must preserve `PASS / FAIL / UNKNOWN`; missing, stale, uncorrelated, or insufficient evidence must not be promoted to PASS.

### 2.4 Predicate

- Predicate declares what must be established and how to evaluate it.
- Predicate evaluator remains separate from data acquisition.
- Predicate may consume existing producer output, acquire facts through declared READ Operations, or combine both.
- Predicate does not name Provider endpoints, Fabric routes, adapters, or implementation classes.
- Predicate must not directly invoke arbitrary Tools outside the governed Runtime execution path.

## 3. Unified authoring and reference rules

- Procedure `call` and Predicate fact requirements reference the same exact Operation ID namespace.
- No independent Observation Ref namespace is introduced in vNext.
- Procedure and Predicate reuse the same input-binding model and source-reference vocabulary.
- `with/from` remains available for explicit non-default mappings, overrides, and disambiguation; it is not required boilerplate when a binding is deterministically declared by contract.
- No implicit “previous node” binding, field-name guessing, string interpolation, dynamic selector, or runtime parameter guessing is allowed.
- Every resolved binding must have a unique, type-compatible, statically identifiable producer.
- When binding cannot be uniquely resolved, compilation fails with an actionable diagnostic.

## 4. Binding model

Binding is resolved in this order:

1. **Operation contract binding**: the Operation owner may declare a standard semantic source for an input (for example, a subject or request context field).
2. **Procedure context binding**: a Procedure may expose a constrained context projection for its execution.
3. **Explicit call-site binding**: `with/from` (or a literal `value` where allowed) overrides or disambiguates a default.
4. **Produced output binding**: values produced by earlier named steps/nodes must be referenced by an exact producer path; no implicit previous-node behavior is allowed.

This order is a resolution policy, not permission to guess. A binding must be explicit in a contract or source expression and must be type checked. Conflicting declarations are compile errors unless the language explicitly defines a legal override.

The Compiler resolves the binding plan statically and emits it in the build artifact. Runtime executes the resolved plan and validates dynamic value presence/types; Runtime does not infer bindings.

## 5. Requiredness and validation ownership

- Public Skill request requiredness belongs to the Skill-owned Request JSON Schema.
- Operation input requiredness belongs exclusively to the Operation Input Schema owned by the Operation/Tool owner.
- Procedure-specific public inputs, if any remain necessary, must have an explicit Procedure input contract; they must not duplicate Operation requiredness.
- Context availability requirements are declared at the appropriate context contract boundary. Existing `spec.context.requiredFacts` identifies required fact identifiers; it is not a field-level schema and cannot substitute for one.
- Predicate READ requirements inherit required input fields from the referenced Operation Input Schema.
- Compiler checks schema validity, reference resolution, binding completeness, type compatibility, and statically knowable dependency order.
- Runtime checks actual invocation values, dynamic presence, freshness, correlation, and evidence validity.
- Requiredness must not be redundantly restated in every Procedure `with` mapping.

## 6. Schema ownership

| Schema / contract | Owner |
|---|---|
| Public Skill Request Schema | Skill |
| Operation Input Schema | Operation/Tool owner |
| Operation Output Schema | Operation/Tool owner |
| Generic Evidence Envelope Schema | Host |
| Evidence guarantees/capabilities | Operation/Tool owner |
| Normalized projection Schema | Explicit normalization owner |
| Predicate-specific evaluation input contract | Skill, limited to its own projection |
| Script output contract | Skill; Compiler derives/validates according to the Script contract |

An Observation payload uses the referenced READ Operation's Output Schema. Do not create a duplicate Observation payload Schema for the same structure.

If a normalization step changes the structure, the normalized projection has its own explicit owner and Schema. Host must not silently invent domain-specific schemas.

## 7. Procedure and Predicate relationship

- Procedure describes execution order, control flow, explicit calls, and data dependencies.
- Predicate describes a condition and its evaluation logic.
- Procedure may verify a Predicate after an Operation or at another explicit control-flow point.
- Predicate may consume the output of the Operation that just ran; in that case it should not perform a redundant READ if that output has sufficient provenance, correlation, and freshness for the predicate's declared assurance level.
- Predicate may declare a READ Operation requirement when independent/current authoritative state is needed.
- Predicate may combine Procedure-provided inputs and READ Operation outputs.
- A successful Mutation Operation response must not be treated as proof of resulting external state without a suitable evidence contract.

## 8. YAML authoring conventions

### 8.1 File naming

The preferred collection naming is:

```text
assurance/
  contract.yaml
  procedures.yaml
  predicates.yaml
```

- `contract.yaml` contains one SkillContract.
- `procedures.yaml` contains the named Procedure collection.
- `predicates.yaml` contains the named Predicate collection.

Single-resource external definitions may retain descriptive type suffixes such as `*.tool.yaml` and `*.schema.yaml`. Do not rename unrelated files solely for superficial pluralization.

This is the preferred vNext naming convention; migration of existing `procedure.yaml` is a coordinated breaking syntax change and must update all references, examples, Studio behavior, and Compiler fixtures together.

### 8.2 Field naming

- Structural YAML fields use `camelCase` (consistent with existing `apiVersion`, `requestSchema`, `requiredFacts`).
- Operation input property names must match the Operation Input Schema exactly; do not rename them to satisfy stylistic preferences.
- Operation/Capability identities use stable dot-separated names.
- Procedure node names use kebab-case.
- File and directory names use kebab-case.
- Avoid introducing a second naming convention for Predicate requirements or Observation.

### 8.3 YAML shape

- Keep one canonical shape per concept.
- Use maps for named Procedure and Predicate identities where stable lookup by ID is required.
- Use lists for ordered execution steps and ordered requirements.
- Avoid duplicate declarations of the same input, schema, requiredness, or identity.
- Keep the top-level resource envelope consistent with the existing `apiVersion` / `kind` convention where applicable; do not add a second ad hoc envelope.

## 9. File and directory responsibilities

Preferred Skill layout:

```text
<skill>/
  SKILL.md
  assurance/
    contract.yaml
    procedures.yaml
    predicates.yaml
  schemas/              # Skill-owned schemas only
  scripts/              # deterministic Skill-owned logic
  lib/                  # imported/read-only external contracts and assets
  output/               # generated artifacts, not hand-authored source
```

There is no separate `observations/` directory in the vNext authoring model. Observation payload schemas are referenced from the owning READ Operation contract. Existing `lib/observations` material must be audited and migrated according to ownership; do not delete it until all consumers and authoritative schemas are accounted for.

## 10. Compiler and Runtime responsibilities

Compiler:
- links exact Capability and Operation identities;
- validates Operation Input/Output Schema references;
- resolves all bindings and producer paths;
- checks required inputs and type compatibility;
- constructs a deterministic dependency/data-flow plan;
- validates Predicate READ requirements and evidence contract compatibility;
- rejects ambiguous or unresolved bindings.

Runtime:
- executes the compiled plan through governed Tool execution;
- enforces authorization, Effect, budgets, timeout, and invocation scope;
- validates dynamic values and Evidence;
- preserves correlation, provenance, freshness, and tri-state Predicate outcomes;
- does not guess bindings or own domain payload schemas.

## 11. Migration and compatibility constraints

- This is a breaking authoring-language evolution; v0.2 remains the current implemented language until a separately approved migration lands.
- Do not claim that the current Compiler or Agent Host supports the proposed syntax.
- Do not remove current Observation Source registration or schemas until every existing Observation Ref has a mapped READ Operation, owner, input/output contract, evidence guarantee, and passing regression coverage.
- Use both `establish-pdu-session` and `establish-session-mas` as mandatory migration fixtures.
- Preserve all currently passing deterministic 5GC behavior and live E2E guarantees.
- Compiler and Studio must consume the same canonical contract and examples; neither may independently redefine semantics.

## 12. Explicitly deferred design details

The following require concrete examples and schema/compiler feasibility review before syntax is frozen at the byte-level:
- exact YAML key for Predicate READ requirements (`requires`, `reads`, or another name);
- exact representation of contract-level default bindings and Procedure context projection;
- whether Procedure inputs remain as a concise explicit interface or are derived entirely from context contracts;
- exact representation of evidence capabilities and freshness policy;
- exact normalized-output contract and whether it is represented as an Operation or a declared projection.

These are syntax details, not permission to change the frozen semantic principles above.
