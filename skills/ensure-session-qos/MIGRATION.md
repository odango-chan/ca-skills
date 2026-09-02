# S2 migration status

This directory is the target authoring source for `ensure-session-qos`.

## Current status

- M0 Inventory: DONE in `connectionagent/docs/skill-source-migration-s2.md`.
- M1 Target Authoring: DONE. Target `SKILL.md`, `contract.yaml`,
  `procedure.yaml`, request schema, and CEL `PredicateSet` are present.
- M2 Target Golden: DONE as a working-tree source Golden. All 18 qualification
  cases are present, the procedure graph is closed, and Platform compile
  coverage is complete. This is not production qualification.
- M3 Compiler Compatibility: CORE PUBLISHED at Platform `fba3010`; target
  admission and compile support are immutable, while deployment qualification
  remains open.
- M4 Runtime Compatibility: CORE PUBLISHED at Runtime `dbb2195`. A real
  Platform-generated Runtime Bundle preview was loaded and its four target
  predicates were evaluated through Runtime's catalog-admitted evaluator with
  a deterministic fixture source. Production deployment bindings and
  acquisition remain unqualified.
- Target deterministic SQ2 qualification: PASS for all 15 executable cases
  through Platform's real Mock Runtime
  (`TestMigratedEnsureSessionQOSTargetMockQualification`). The 3 remaining
  cases are planning-blocked and do not start Mock execution under the existing
  qualification rule. This is not production acquisition or deployment
  qualification.

The target source intentionally has no `assurance/evidence.yaml`. Predicate
acquisition, freshness, ProviderBinding, and UNKNOWN/reconcile authority remain
Runtime/deployment responsibilities.

The canonical Observation refs currently required are:

```text
ue.registration.snapshot
pdu.session.snapshot
user.plane.connectivity.snapshot
```

Their scope/value schemas must be admitted by the shared Runtime ObservationCatalog
before qualification. This file does not claim those deployment bindings exist.
