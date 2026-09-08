# `download-object-by-deadline` migration

## PR7 preflight hardening

The deadline path now consumes real Procedure outputs: trusted request
`secondsRemaining` and `sizeBytes`, or `object.metadata.query.output.sizeBytes`,
feed the governed local derivation Script. Its typed output feeds QoS
capacity/admission, then `file.download`; the final completion and deadline
Predicates remain independent post-download proofs. An `OUTCOME_UNKNOWN`
download is reconciled through `file.download.status`, not through PDU-session
reconcile. The current authoring contract has no governed wall-clock binding,
so `secondsRemaining` is an explicit trusted request input and is not computed
from an untrusted fact.

## M0-M2

- M0 Inventory: DONE in `connectionagent/docs/skill-source-migration-s3.md`.
- M1 Target Authoring: DONE in this target package. The target removes
  `assurance/evidence.yaml`, uses `PredicateSet` with typed Observation
  requirements and CEL, and selects procedures from the request's trusted
  `sizeBytes` presence rather than duplicating dynamic observation state in
  planning facts.
- M2 Target Golden: DONE in the current working tree. The source-level closure
  check passes, all 14 cases are preserved, and Platform compilation plus the
  complete 14-case deterministic planning matrix pass.

## Target boundary

Observation acquisition, catalog publication, provider bindings, and evidence
provenance remain Runtime/deployment responsibilities. This package declares
only canonical observation references, scopes, freshness, and deterministic
predicate interpretation. The local transfer-requirement script remains
network-free local computation.

M3 compiler compatibility is CORE PUBLISHED at Platform `fba3010`. M4 Runtime
compatibility is CORE PUBLISHED at Runtime `dbb2195` and has a real
Platform-generated Bundle smoke (`runtimeBundleDigest`
`sha256:dbc775c77ff7832c3834accc2928d0ef329a0d07572519634d1daa33c1257f41`)
and all three target predicates evaluate PASS against a normalized fixture
source. M4 production acquisition/provenance and M5 qualification remain open:
deployment ObservationCatalog content and real adapters are not supplied by
this repository. No consumer cutover or deletion of the Platform source is
claimed by this file.

Target deterministic SQ2 qualification is nevertheless PASS for all 11
executable cases through Platform's real Mock Runtime
(`TestMigratedDownloadObjectTargetMockQualification`). The 3 remaining cases
are planning-blocked and do not start Mock execution under the existing
qualification rule. This does not establish production acquisition or
deployment qualification.
