---
name: ue-registration
description: Converge a target UE to a trusted REGISTERED state, or verify consistent registration context without treating one protocol message or Capability success as completion.
---

# UE Registration

Select this Skill for Initial Registration or when the UE registration state and network-side registration context must be confirmed.

Registration is a business progression: trusted identity, successful authentication, security context, registration context preparation, registration completion, and final state verification. NAS, NGAP, and SBI messages are internal protocol events; do not orchestrate them individually.

Keep intermediate and business success separate. Authentication does not prove a Security Context, a Security Context does not prove Registration Context, and Registration Accept does not prove Registration Complete. Runtime must independently prove `ue.registered` and `ue.registration_context.consistent` with canonical typed observations.

Do not guess unobserved state or infer goal completion from `COMMITTED`. If a side-effecting Action returns `OUTCOME_UNKNOWN`, do not retry blindly. With no trusted Reconcile Capability in the current version, leave recovery to the deterministic execution plane, which must safe-stop.

Submit the business request or select the `ue-registration` execution target. Do not select individual `resolve`, `authenticate`, `establish`, `prepare`, or `finalize` Actions. Governed execution owns identity, protocol, and vendor-specific implementation.
