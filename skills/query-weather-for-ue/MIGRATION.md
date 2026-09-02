# `query-weather-for-ue` migration

## M0-M2

- M0 inventory: DONE in `connectionagent/docs/skill-source-migration-s4.md`.
- M1 target authoring: DONE in this target package. The target removes
  `assurance/evidence.yaml`, uses typed Observation requirements with CEL, and
  merges direct/connect/probe routing into one Runtime Procedure.
- Dynamic connectivity is verified at the Procedure entry. `PASS` queries
  directly, `FAIL` enters connection convergence, and `UNKNOWN` probes before
  convergence; it is not selected by a duplicated planning fact.
- Weather output is passed to normalization through the frozen prior-action
  output binding. Final business success is independently proven by the
  weather-result Observation.
- M2 target Golden: DONE in the current working tree. The independent graph
  and `fromOutput` closure check passes, all 16 cases are preserved, Platform
  compilation is `VALID`, and the complete 16-case deterministic planning
  matrix passes.
- Target deterministic SQ2 qualification: PASS for all 13 executable cases
  through Platform's real Mock Runtime
  (`TestMigratedQueryWeatherTargetMockQualification`). The remaining 3 cases
  are planning-blocked and therefore do not start Mock execution under the
  existing qualification rule. This is not production acquisition or
  deployment qualification.

## M2 status

M3 compiler compatibility is locally VALID, but the result is not yet an
immutable cross-repository pin. M4 local Runtime compatibility has a real
Platform-generated Bundle smoke (`runtimeBundleDigest`
`sha256:f3774c43da2275a80262a625fd7695fd2b643393ab53cb90bc8b60bc05403cad`)
and all three target predicates evaluate PASS against a normalized fixture
source. M4 production acquisition/provenance and M5 qualification remain open:
deployment ObservationCatalog content and real adapters are not supplied by
this repository.

Observation acquisition, catalog publication, provider bindings, evidence
provenance, production qualification, immutable pins, consumer cutover, and
deletion of the Platform source remain outside this authoring slice.
