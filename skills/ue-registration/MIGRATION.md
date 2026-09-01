# S1 migration status

This package is the target-state source for S1 `ue-registration`.

## M0-M2

- M0 Inventory: DONE against `connectionagent-skill-platform/skills/ue-registration` at the source checkout reviewed for S1.
- M1 Target Authoring: DONE against the PR #2 target Skill model.
- M2 Target Golden: DONE as a source Golden after contract, procedure, case, and graph-closure review. It is not production-qualified.

## Explicit dependencies

The target source intentionally waits for the following build/runtime support:

- external Skill source loading and source-root provenance in Skill Platform;
- `applicability.when` request/context CEL selection;
- `PredicateSet` canonical typed Observation loading and deployment-owned ObservationBinding;
- CEL evaluator input `{request, subject, facts, observations}`;
- Runtime observation acquisition and freshness/evidence authority;
- target admission and compile/qualification of this source;
- a governed UE registration reconcile Capability before any mutation UNKNOWN can resume.

## Canonical typed Observation dependency

`assurance/predicates.yaml` declares the typed Observation requirements consumed by
the six UE predicates. The `ue.*.snapshot` identifiers and their fields are not
Skill-local conventions or a production contract by themselves. They depend on a
companion canonical `ObservationCatalog` and schema definitions owned by the
Runtime/shared Registry path (reuse the ObservationCatalog design tracked by
companion Platform PR #80; do not create a second registry here).

The companion contract must define, for each Observation ID, both its scope
schema and value schema. At minimum this includes:

```text
ue.identity.snapshot              -> scope {ueRef}, value {resolutionState}
ue.authentication.snapshot       -> scope {ueRef}, value {authenticationState}
ue.security_context.snapshot     -> scope {ueRef}, value {securityContextState}
ue.registration_context.snapshot -> scope {ueRef}, value {contextState, consistency}
ue.registration.snapshot         -> scope {ueRef}, value {registrationState}
```

This is an M3/M4 dependency. M2 records the requirements and evaluator
expressions, but does not claim that Observation acquisition, binding, schema
publication, or runtime freshness authority already exists.

## Identity resolution semantics

`ue.identity.resolve` remains a Procedure Action. The source Capability Registry,
AMF `resolve_ue_identity` ToolRegistration, and reference fixture all define an
active identity-resolution interaction that establishes the UE identity
association needed by later registration stages. It is a read-only operation in
the side-effect taxonomy, but it is not a proof-only query and is not duplicated
by the `ue.identity.snapshot` Observation. This is an on-demand Registration
operation, including deployments where identity resolution requires network
interaction (for example SUCI/SUPI resolution).

## M0-M7 status

- M0 Inventory: DONE
- M1 Target Authoring: DONE
- M2 Target Golden: DONE after the source graph and case closure in this branch
- M3 Compiler: NOT IMPLEMENTED
- M4 Runtime Observation/Execution support: NOT IMPLEMENTED in this repository
- M5 Production Qualification: NOT STARTED
- M6 Consumer Cutover: NOT STARTED
- M7 Source removal: NOT STARTED

M2 DONE means this package is a consumable target source Golden, not a claim of
production qualification or runtime support.

Until those dependencies are qualified, the old Platform copy remains the source consumed by current production paths. This target source must not be silently substituted for it.
