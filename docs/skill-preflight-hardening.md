# Skill Preflight Hardening

Status: PR7 descendant work. PR6 remains a frozen historical baseline.

The official executable Skills retain the frozen package model:

```text
SKILL.md                 model-visible semantics
assurance/contract.yaml  allowed capabilities and final contract
assurance/procedure.yaml deterministic flow
assurance/predicates.yaml proof requirements and judgement
scripts/                 governed deterministic local computation
cases/<case>/case.yaml   qualification assets
```

## Download deadline dataflow

`download-object-by-deadline` now requires trusted `secondsRemaining` in the
request. The request `deadline` remains the business deadline used by the
download oracle; the remaining-time value is supplied by the trusted caller
because the current Procedure authoring contract has no governed wall-clock
binding.

The known-size path is:

```text
request.sizeBytes
  -> derive_transfer_requirement.py
  -> qos.requirement.resolve
  -> file.download
  -> file_transfer.completed + file_transfer.deadline_met
```

When size is absent, `object.metadata.query.output.sizeBytes` feeds the same
derivation. QoS admission is represented by the resolver Capability outcome;
the resolver owns the capacity/admission decision because the current
Capability catalog has no separately qualified capacity-estimate Action.
the final file-transfer Predicates are never used before download. A download
`OUTCOME_UNKNOWN` enters `file.download.status`, whose reconciliation outcomes
are `COMMITTED`, `NOT_COMMITTED`, or `UNRESOLVED`.

The source-level regression validator rejects reintroduction of planning facts
for derived values, ignored metadata output, the old PDU-session reconcile, or
pre-download file-transfer proof.

## Qualification boundary

`ue-registration`, `ensure-session-qos`, `download-object-by-deadline`, and
`query-weather-for-ue` are the canonical official executable Skill sources.
`5gc-file-transfer` and `wifi-file-transfer` compile as valid source packages
and their deterministic cases pass the current local Sandbox/Q4 qualification
path. This is SQ2/preflight evidence, not production qualification: immutable
artifact/profile admission and deployment-owned ProviderBinding and
ObservationCatalog closure are still required before PR7-C Native Agent
admission.

## Verification

The local Runtime/Sandbox overlay passes the official download and
file-transfer Q4 paths, and Runtime itself passes its full standalone test
suite. The consumer `GOWORK=off` path is pinned to published Runtime
`0eafdef`, while the Script-output binding correction is still an unpublished
working-tree change. Platform standalone download qualification therefore
remains blocked until that Runtime change is published and the immutable
consumer pin is regenerated.

Run `make verify` with `CONNECTIONAGENT_SKILL_PLATFORM_ROOT` explicitly set in
CI. The entry point delegates compiler, Case schema, and Planning validation to
Skill Platform; it does not copy Platform compiler logic. The Agent may propose
an `ExecutionTargetCandidate`, but Target Admission still requires a qualified
executable Skill and immutable artifact provenance.
