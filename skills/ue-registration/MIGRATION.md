# S1 migration status

This package is the target-state source for S1 `ue-registration`.

## M0-M2

- M0 Inventory: DONE against `connectionagent-skill-platform/skills/ue-registration` at the source checkout reviewed for S1.
- M1 Target Authoring: DONE against the PR #2 target Skill model.
- M2 Target Golden: DONE as a source Golden after contract, procedure, case, and graph-closure review. It is not production-qualified.

## Explicit dependencies

The target source intentionally waits for the following build/runtime support:

- external Skill source loading and source-root provenance in Skill Platform;
- published Runtime/Platform pins carrying the local `applicability.when` and
  `PredicateSet` compiler support;
- `PredicateSet` canonical typed Observation loading and deployment-owned ObservationBinding;
- Runtime PredicateSet CEL evaluator input `{request, subject, facts, observations}`;
- Runtime observation acquisition and evidence/provenance authority;
- target admission and compile/qualification of this source;
- a governed UE registration reconcile Capability before any mutation UNKNOWN can resume.

## Canonical typed Observation dependency

`assurance/predicates.yaml` declares the typed Observation requirements consumed by
the six UE predicates. The `ue.*.snapshot` identifiers and their fields are not
Skill-local conventions or a production contract by themselves. They depend on a
companion canonical `ObservationCatalog` and schema definitions owned by the
Runtime/shared Registry path (reuse the ObservationCatalog design tracked by
companion Platform PR #80; do not create a second registry here).

The Runtime now owns the generic `ObservationCatalog` contract and strict
schema-envelope loader. The companion catalog publication must still define,
for each Observation ID, both its scope schema and value schema. At minimum
this includes:

```text
ue.identity.snapshot              -> scope {ueRef}, value {resolutionState}
ue.authentication.snapshot       -> scope {ueRef}, value {authenticationState}
ue.security_context.snapshot     -> scope {ueRef}, value {securityContextState}
ue.registration_context.snapshot -> scope {ueRef}, value {contextState, consistency}
ue.registration.snapshot         -> scope {ueRef}, value {registrationState}
```

This is an M3/M4 dependency. M2 records the requirements and evaluator
expressions; the current Runtime working tree has the contract/schema loader,
but does not yet claim UE catalog publication, Observation acquisition, binding
deployment, or production provenance authority. Runtime freshness comparison
against the frozen binding requirement is implemented in the current working tree.

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
- M3 Compiler: PARTIAL in the current Platform working tree (`selectionPolicy`,
  `applicability.when`, legacy `evidence.yaml` omission, and `PredicateSet`
  admission); not yet published as an immutable cross-repository pin
- M4 Runtime Observation/Execution support: PARTIAL in the current Runtime working
  tree (PredicateSet loading, ObservationCatalog contract/schema, deployment-owned
  ObservationSource, Runtime freshness comparison, and CEL evaluation); UE catalog
  publication, production acquisition/provenance, qualification, and immutable
  pinning remain open
- Target deterministic SQ2 qualification: PASS for all 8 executable cases through
  Platform's real Mock Runtime (`TestMigratedUERegistrationTargetMockQualification`).
  The resource-unavailable case is planning-blocked and does not start Mock
  execution under the existing qualification rule. This is not production
  acquisition or deployment qualification.
- M5 Production Qualification: NOT STARTED
- M6 Consumer Cutover: NOT STARTED
- M7 Source removal: NOT STARTED

M2 DONE means this package is a consumable target source Golden, not a claim of
production qualification or runtime support.

Until those dependencies are qualified, the old Platform copy remains the source consumed by current production paths. This target source must not be silently substituted for it.
