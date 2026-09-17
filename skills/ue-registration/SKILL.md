---
name: ue-registration
description: Converge a target UE to a trusted REGISTERED state, or verify consistent registration context without treating one protocol message or Capability success as completion.
---

# UE Registration

Select this Skill for Initial Registration or when the UE registration state and network-side registration context must be confirmed.

Registration is a business progression: trusted identity, successful authentication, security context, registration context preparation, registration completion, and final state verification. NAS, NGAP, and SBI messages are internal protocol events; do not orchestrate them individually.

Keep intermediate and business success separate. Authentication does not prove a Security Context, a Security Context does not prove Registration Context, and Registration Accept does not prove Registration Complete. Runtime must independently prove `ue.registered` and `ue.registration_context.consistent` with canonical typed observations.

When planning depends on the UE's current registration or registration-context state, obtain that current fact with an eligible model-visible read-only Tool instead of guessing from protocol progress, previous mutation results, or stale context. The Tool may be exposed directly by its governed owner; do not assume observation must be routed through Runtime.

The Agent-visible read result is planning input only. It does not establish a Runtime Predicate verdict or waive the deterministic verification performed by the assurance path.

Do not guess unobserved state or infer goal completion from `COMMITTED`. If a side-effecting Action returns `OUTCOME_UNKNOWN`, do not retry blindly. With no trusted Reconcile Capability in the current version, leave recovery to the deterministic execution plane, which must safe-stop.

Submit the business request or select the `ue-registration` execution target. Do not select individual `resolve`, `authenticate`, `establish`, `prepare`, or `finalize` Actions. Governed execution owns identity, protocol, and vendor-specific implementation.
