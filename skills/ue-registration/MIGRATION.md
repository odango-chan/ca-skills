# S1 migration status

This package is the target-state source for S1 `ue-registration`.

## M0-M2

- M0 inventory: complete against `connectionagent-skill-platform/skills/ue-registration` at the source checkout reviewed for S1.
- M1 target authoring: complete; the source is not a byte-for-byte snapshot.
- M2 target Golden: complete as a source Golden after schema/contract review. It is not production-qualified.

## Explicit dependencies

The target source intentionally waits for the following build/runtime support:

- external Skill source loading and source-root provenance in Skill Platform;
- `applicability.when` request/context CEL selection;
- `PredicateSet` ObservationBinding loading and canonical typed observation normalization;
- CEL evaluator input `{request, subject, facts, observations}`;
- Runtime observation acquisition and freshness/evidence authority;
- target admission and compile/qualification of this source;
- a governed UE registration reconcile Capability before any mutation UNKNOWN can resume.

Until those dependencies are qualified, the old Platform copy remains the source consumed by current production paths. This target source must not be silently substituted for it.
