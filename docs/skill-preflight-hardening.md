# Skill Preflight Hardening

Status: COMPLETE — PR7 Skill Preflight is closed. Skill source is READY FOR PR7-C.

PR6 remains a frozen historical baseline. All PR7 descendant work leaves `connectionagent/bom/connectionagent-pr6-final.lock.yaml` unchanged.

The official package model remains frozen:

```text
SKILL.md                 model-visible semantics
assurance/contract.yaml  allowed capabilities and final contract
assurance/procedure.yaml deterministic flow
assurance/predicates.yaml proof requirements and judgement
scripts/                 governed deterministic local computation
cases/<case>/case.yaml   qualification assets
```

## Historical vs Current

Historical:
  Skill hardening initially discovered a Runtime binding gap: Script-output
  values were not flowing into later Action inputs, and `file.download`
  UNKNOWN reconciliation lacked a governed `file.download.status` observation.

Current:
  Runtime fix published — `connectionagent-runtime` `c9d08889` (includes
  `7417465 fix(runtime): bind Action inputs from prior Script output` and
  the P1 mcp digest hardening).
  Sandbox fix published — `connectionagent-sandbox` `54225f6 fix(sandbox): validate download status and QoS bindings`
  (also `8892061` QoS observation state).
  Platform pin updated — `connectionagent-skill-platform` `9c6e609`
  now pins Runtime `c9d08889` and Sandbox `54225f67`, and
  `9c6e609 feat: consume runtime-owned procedure execution evidence`
  routes `ProcedureExecutionRecord` / budget / pending-write semantics
  from Runtime instead of reconstructing them from Case expected values.
  Platform standalone download qualification is no longer blocked by an
  unpublished Runtime binding.

Do not carry forward the old blocker lines:

```text
Platform pinned Runtime = 0eafdef
Script-output binding still unpublished
Platform standalone qualification blocked
```

as current blockers. They belong to the historical record above.

## Download deadline dataflow

`download-object-by-deadline` requires trusted `secondsRemaining` in the
request. The request `deadline` remains the business deadline used by the
download oracle; the remaining-time value is supplied by the trusted caller
because the current Procedure authoring contract has no governed wall-clock
binding.

```text
secondsRemaining
must come from trusted caller/context
not LLM guessing
```

Long-term Runtime-owned deterministic wall-clock derivation may be added as a
future optimization; it is not a preflight blocker. The canonical dataflow is:

```text
request.sizeBytes
or
object.metadata.query.output.sizeBytes
        ↓
derive_transfer_requirement.py
        ↓
derive-requirement.output.minimumPayloadBitrateBps
        ↓
qos.requirement.resolve
        ↓
file.download
        ↓
file_transfer.completed
        ↓
file_transfer.deadline_met
```

When size is absent, `object.metadata.query.output.sizeBytes` feeds the same
derivation. QoS admission is represented by the resolver Capability outcome;
the resolver owns the capacity/admission decision because the current
Capability catalog has no separately qualified capacity-estimate Action.

Final predicates:

```text
file_transfer.completed
file_transfer.deadline_met
```

are never used before download.

Unknown outcome:

```text
file.download
  OUTCOME_UNKNOWN
        ↓
file.download.status
        ├─ COMMITTED
        │    ↓
        │  verify
        │
        ├─ NOT_COMMITTED
        │    ↓
        │  controlled retry → download-object
        │
        └─ UNRESOLVED
             ↓
          UNRESOLVED
```

Forbidden regressions (blocked by `scripts/validate_download_object_target.py`):

```text
context.facts.bytes_remaining
context.facts.minimum_payload_bitrate_bps

pdu_session.reconcile
used for download reconciliation

file_transfer.completed
verified before download
```

## Trusted time input boundary

The Procedure contract does not own a governed wall-clock binding in this
preflight. `deadline` plus `secondsRemaining` is accepted as the request.
`secondsRemaining` must be trusted; the Skill and Procedure never derive it
from LLM guessing. A future Runtime clock / deadline arithmetic / time sync
subsystem may own this deterministically; until then the boundary is explicit
and documented.

## Qualification boundary

Official executable sources (compile + cases + planning + SQ/Q4 passing in the
canonical Platform gates):

```text
ue-registration               — production-qualified via Platform/Runtime/Sandbox
ensure-session-qos            — production-qualified via Platform/Runtime/Sandbox
download-object-by-deadline   — production-qualified via Platform/Runtime/Sandbox
query-weather-for-ue          — production-qualified via Platform/Runtime/Sandbox
```

PR7-C target sources:

```text
5gc-file-transfer             — see below
wifi-file-transfer            — see below
```

File-transfer status (current):

```text
source                PASS   (package layout + source-specific semantic checks)
compile               PASS   (official source compile via Platform)
cases                 PASS   (canonical Case schema validation)
registry closure      PASS   (capabilities/predicates/scripts in registry)
local Sandbox/Q4      PASS   (Platform sessionrun + Sandbox download/QoS paths)
```

Production-qualified: NO for both `5gc-file-transfer` and `wifi-file-transfer`.

Remaining true blockers before production admission:

```text
immutable artifact/profile admission
deployment-owned ProviderBinding closure
ObservationCatalog closure
```

`make verify` green does not auto-promote these targets to
production-qualified.

## Verification ownership and entry

Ownership:

```text
connectionagent-skills
  owns:
    source layout
    source-specific semantic regression (download / ue-registration / query-weather validators)

connectionagent-skill-platform
  owns:
    compile
    Case schema
    Planning
    Qualification interpretation (SQ/Q4, artifact qualification)

connectionagent-runtime
  owns:
    deterministic execution semantics (budget, pending write, OUTCOME_UNKNOWN,
    execution record projection — consumed, not reconstructed, by Platform)

connectionagent-sandbox
  owns:
    environment/provider observation execution (download status, QoS bindings)
```

`make verify` delegates to the canonical gates; it does not duplicate the
Platform compiler or Runtime state machine.

`make verify` covers (via `scripts/verify.py`):

```text
1. package layout                — scripts/validate_package_layout.py (once)
2. Skill-specific validators      — validate_ue_registration / validate_query_weather / validate_download_object_target
3. official source compile        — qualificationruntime.TestOfficialTargetSkillsCompileFromExplicitSource (4 official Skills)
4. canonical Case schema          — compiler.TestCanonicalCaseRejectsSplitFilesAndUnknownFields (+ compiler gates)
5. canonical Planning             — planning.TestReferencePlanningCases + TestPlanningContextAllowsOpaqueFacts
6. official qualification         — sessionrun m5-q4 / qualificationruntime path at current SQ/Q4 level
7. 5gc-file-transfer compile      — casp compile --package 5gc-file-transfer
8. wifi-file-transfer compile     — casp compile --package wifi-file-transfer
9. local Sandbox/Q4 file-transfer — sessionrun file-transfer recovery matrix / Sandbox-bound qualification
```

COMPILE / CASE / PLANNING / SQ1 / SQ2 / Q4 / PRODUCTION are distinct levels
and are reported separately; a compile-only pass is not qualification.

## Locator and coupling rules

CI must set:

```text
CONNECTIONAGENT_SKILL_PLATFORM_ROOT
```

explicitly to the Skill Platform checkout. Local sibling fallback to
`../connectionagent-skill-platform` is developer convenience only; CI must not
infer it from the working directory.

Platform calls receive:

```text
CONNECTIONAGENT_SKILLS_ROOT
```

so the current Skills source is used, not a historical Platform fixture copy.
There is a fail-closed test:

```text
official source missing → fail
  (qualificationruntime.TestOfficialSkillSourceFailsClosedWhenMissing)
```

Skills `make verify` may invoke the Platform checkout. Platform and Runtime
qualification must consume the published/pinned `connectionagent-runtime`
module (or an explicit `CONNECTIONAGENT_RUNTIME_ROOT` workspace override for
development), not `../connectionagent-runtime` source files directly.

## Admission rule (PR7-C)

```text
Skill visible  ≠  Skill executable
Skill source exists  ≠  production-qualified
```

PR7-C flow:

```text
Goal
 ↓
Skill selection
 ↓
ExecutionTargetCandidate
 ↓
Target Admission
 ↓
qualified target only
 ↓
Runtime
```

`make verify` does not change this boundary.

## Case and predicate notes

`download-object-by-deadline` carries 14 Cases (known size, unknown size
metadata path, metadata unavailable, derive failure, QoS denied, download
success, deadline fail, UNKNOWN→committed, UNKNOWN→not committed→retry,
UNKNOWN→unresolved, budget exhaustion, pending write budget, precondition FAIL,
precondition UNKNOWN). They are not trimmed for speed.

Shared Predicate fixture reuse:

```text
verify-transfer:
  file_transfer.completed: PASS
  file_transfer.deadline_met: PASS
```

is the current contract; multiple Verify nodes reuse one authoring Predicate
observation via the Platform fixture runner. Fixture reuse does not fabricate
values — Platform tests assert this, and Runtime owns the actual execution
values/projection.

Skill Platform does not reconstruct Runtime execution semantics (budget,
pending write, OUTCOME_UNKNOWN, execution record).

## Final status

```text
PR7 Skill Preflight:
  COMPLETE

Official Skill source readiness:
  READY

5gc-file-transfer:
  preflight qualified
  production admission pending deployment closure

wifi-file-transfer:
  preflight qualified
  production admission pending deployment closure

PR7-C execution admission
  waits for deployment qualification closure
```

All file-transfer Skills are intentionally not marked production-qualified
until the remaining blockers above are closed. That does not keep the overall
Skill Preflight incomplete.
