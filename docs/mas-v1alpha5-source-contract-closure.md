# MAS v1alpha5 source-contract closure register

**Scope:** `ca-skills/examples/skills/establish-pdu-session-mas` only. **Status:** SOURCE_CONTRACT_REVIEW; FORMAL_BUILD_BLOCKED / NOT_LINKABLE / NOT_QUALIFIED. This is a source-to-Owner contract inventory, **not** a ToolCatalog, Evidence publication, or deployment authorization.

## Ownership and initial-ingress boundary

The MAS Procedure **replaces the initial PDU Session establishment flow** for the fixed policy-first profile; it is not a post-creation Skill. The Host receives an already-admitted, authenticated initial `Nsmf_PDUSession_CreateSMContext` ingress and binds its exact 3GPP `supi` and `pduSessionId` to one original business invocation. It must deduplicate a replay of that *same original ingress* and avoid concurrent unrelated writers for the exact business instance. No new `ueRef` or external Tool argument for Host lifecycle, correlation, idempotency, secret, or transport identity is authorized.

Do **not** add an AMF registration lookup or a `cm_state=connected` precondition to this MAS Skill. Such a second query is not needed to admit an already-valid CreateSMContext request. The Skill's first `precondition` validates only the supported request profile. If the upstream ingress is not authentic, not an initial establishment request, or cannot be correlated uniquely, Host admission must reject or remain unresolved **before** starting the graph; the Skill cannot manufacture the missing evidence.

Do **not** require `sessionPresence == ABSENT` as a prerequisite. The OpenAMSM `/invoke` resolver may create an SMF UE/Session shell before `SC.VALIDATE_SUBSCRIPTION`; the shell is not evidence of an already established PDU Session. Existence, ownership, phase and duplicate prevention are separate concepts. A replay attaches to, or is refused against, its original Host invocation; presence of a shell does not by itself trigger a second operation or a false duplicate rejection. Real established-session conflicts still require an authoritative Host/Owner decision, not a guessed predicate.

The s1 `SC.VALIDATE_SUBSCRIPTION` candidate must **not** be published as READ without proof. It has an `OUTCOME_UNKNOWN → UNRESOLVED` route and a conservative stop on reported failure. Its actual Owner Effect, commit/failure proof, and correlation require Owner validation before formal linking. Every other MAS Operation remains effect-unqualified until the Owner publishes actual semantics. No unknown mutation is retried blindly.

## Fixed MAS callable mapping

Source of truth for the table is the v0.2.0 source map in [ca-client-tools PR #16](https://github.com/odango-chan/ca-client-tools/pull/16), pinned to `env-openamsm@594dec78b95bff4fdc34deac8a3a9681fb41228f`. The candidate has 13 input and 12 distinct output Schema files under `wtlab:openamsm:mas:v0.2.0:`. A formal Build still needs trusted Owner and Deployment publications.

| OES step | Candidate Tool callable | Candidate Capability | Candidate Evidence Guarantee | Expected normalized result fields |
| --- | --- | --- | --- | --- |
| `s1` | `SC.VALIDATE_SUBSCRIPTION` | `mas.sc.subscription.validate` | `sc.subscription-validated` | `sub_summary` |
| `s2` | `SAA.SECONDARY_AUTH` | `mas.saa.secondary.auth` | `saa.secondary-auth-disposition` | `phase` |
| `s3` | `SC.CREATE_SM_CONTEXT` | `mas.sc.context.create` | `sc.context-created` | `session_keys, lifecycle, sm_context_ref` |
| `s3r` | `SC.REGISTER_UECM` | `mas.sc.uecm.register` | `sc.uecm-registered` | `uecm_registered` |
| `s3p` | `PA.CREATE_SM_POLICY` | `mas.pa.sm.policy.create` | `pa.policy-association-created` | `up_intent, authorized_qos, policy_assoc_id` |
| `s4` | `UPS.DECIDE_ANCHOR` | `mas.ups.anchor.decide` | `ups.anchor-selected` | `up_anchor` |
| `s5` | `IAM.ALLOCATE_ADDRESS` | `mas.iam.address.allocate` | `iam.address-allocated` | `ue_addr` |
| `s6u` | `PA.UPDATE_SM_POLICY` | `mas.pa.sm.policy.update` | `pa.policy-updated` | `up_intent, authorized_qos, policy_assoc_id` |
| `s7` | `CA.CREATE_CHARGING` | `mas.ca.charging.create` | `ca.charging-step-skipped` | `charging_ref` |
| `s8` | `UPN.CREATE_UP_SESSION` | `mas.upn.up.session.create` | `upn.n4-session-established` | `n4_seid, est_done` |
| `s10` | `SSM.SIGNAL_UE_AN` | `mas.ssm.ue.an.signal` | `ssm.access-network-ready` | `an_tunnel_teid, an_tunnel_ip, an_tunnel` |
| `s11` | `UPN.MODIFY_UP_SESSION` | `mas.upn.up.session.modify` | `upn.n3-synchronized` | `n3_synced` |
| `s13` | `SE.EMIT_EVENTS` | `mas.se.events.emit` | `se.establishment-event-recorded` | `last_event` |

The graph contains precisely these 13 `mas::` callables, and only their 13 requested Capability IDs. The generic `smf.session.context.query` remains a reusable Host capability for *other* Skills but is **not a dependency of this MAS initial establishment Skill**.

`CA.CREATE_CHARGING` is a successful `NOT_IMPL_skip` marker, not a charging reservation; `SE.EMIT_EVENTS` is a local MAS event, not a 3GPP step-18 notification. `UPS.up_anchor` and `IAM.ue_addr` are readiness/allocation markers, not actual resource identifiers. `SSM.SIGNAL_UE_AN` remains a composite pending Owner Operation until the exact later Nsmf UpdateSMContext completion; do not invent a second Wait Node or second Skill Invocation. The MAS ordering of UECM registration remains intentional.

## Independent contract closure and publication gates

| Gate | Contract required | Owner / publication authority | Status |
| --- | --- | --- | --- |
| S0 | Skill request Schema, fixed profile, 13-node operation graph, explicit profile rejection and final Postcondition | `ca-skills` | Source updated; Compiler re-verification required on this head |
| S1 | Host Invocation Context Schema providing immutable `supi`; authenticated initial ingress and original-invocation deduplication | Host / `ca-agent-demo` + `ca-context` | Contract alignment open; no AMF/CM lookup requirement |
| T1 | 13 precise ToolCatalog entries, input/output Schemas, identity path annotations, `ownerOutcomes`, verified Effects | MAS Tool Owner / Host | **Candidate only**; 25 files source-shape checked, Owner export missing |
| T2 | Each mutation's `receiptSchema`, `mutation.commitProof` containing verified `originalInvocationId` and `commitState`; failure/no-side-effect proof | MAS Tool Owner / Host | **Missing**; `MasInvokeResponse status=OK` is insufficient |
| T3 | Exact-original independent READ Reconcile where declared; original Operation identity binding and durable result/recovery journal | MAS Tool Owner / Host | **Missing**; no blind retry or invented compensation |
| E1 | Evidence descriptors for applicable source-backed outputs with fact/producer/scope/correlation/freshness and independent authority | Owner/Observation authority | **Unpublished**; value marker alone cannot prove external effect |
| C1 | Exact membership of 13 callable Capabilities, Effect agreement, authorized scope policies and Owner identities | Deployment / Capability Authority | **Unpublished** |
| D1 | Immutable `ca-context` and `mas` dependency snapshots with stable package IDs, digests, validated Owner and EvidenceTrustBindings | Owner + Deployment | **Unavailable**; never substitute synthetic fixture |
| B1 | Released `skillc v2.0.1` `check → inspect → build`, deterministic artifact/digest verification, negative fail-closed cases | Compiler + `ca-skills` | **Formal build blocked** until D1/E1/C1/T1–T3 closure |
| R1 | Actual Provider, Owner receipt/reconcile, Temporal continuity, live 5GC execution | `ca-client-tools` + `ca-agent-demo` | Separate qualification; not prerequisite for *source definition*, but required before claiming real guarantees |

**Important distinction:** a complete static contract may be drafted before its implementing code exists. But a trusted Owner must not publish a claim of `COMMITTED`, `NOT_COMMITTED`, no side effects, durable Reconcile, or authoritative Evidence unless that producer actually supplies the guarantee. Do not mock these guarantees in a release snapshot. Fixture-only compilation is strictly labeled `FIXTURE_STATIC_BUILD_PASS / NOT_QUALIFIED`.

## Acceptance cases

- Valid admitted initial CreateSMContext request runs s1–s13 once under a single original Invocation; no AMF status lookup or SMF ABSENT side gate.
- Same original ingress replay does not spawn a second MAS execution; another PSI/lifecycle cannot borrow the first run's evidence.
- An early SMF Session shell is not mistaken for an established PDU Session and cannot by itself prevent the original authorized MAS flow.
- Unsupported request profile fails in the first Precondition before any MAS Operation.
- s1 unknown result stops `UNRESOLVED`; no duplicate dispatch or inferred `NOT_COMMITTED`.
- Unknown mutating outputs, stale or wrong-instance Evidence, missing Owner grants, tampered/duplicate snapshots, and missing proof all fail closed.
- Source assertions retain exactly 13 MAS callables/Capabilities and no separate `ca-session-context` alias or `smf.session.context.query`.
- Source Hygiene and actual released Compiler diagnostics are rechecked on the PR HEAD; no claim of formal Build PASS before trusted Owner publication.

## Current source references

- [Canonical MAS Skill](../examples/skills/establish-pdu-session-mas/SKILL.md)
- [Compiler v2.0.1 gate](mas-v1alpha5-compiler-gate.md)
- [MAS source mapping](../examples/skills/establish-pdu-session-mas/references/openamsm-operation-mapping.md)
- [ca-client-tools candidate](https://github.com/odango-chan/ca-client-tools/tree/main/contracts/mas-owner-candidate/v0.1.0)
- [ca-skills #71](https://github.com/odango-chan/ca-skills/issues/71)
- [ca-agent-demo #215](https://github.com/odango-chan/ca-agent-demo/issues/215)
