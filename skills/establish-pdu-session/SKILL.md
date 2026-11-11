---
name: establish-pdu-session
description: Handle one admitted UE-requested initial PDU Session Establishment procedure and converge it to a verified network state.
---

# Establish PDU Session

## Purpose

Fulfil one admitted **UE-requested initial PDU Session Establishment** occurrence.

This Skill owns the session-management business progression for that occurrence. A
successful SBI call, HTTP response, protocol acknowledgement, PFCP request, or observed
mutation is never enough by itself to prove that the PDU Session Establishment procedure
is complete.

Use this Skill only for the exact admitted occurrence presented by the Host. Do not
switch to another UE, PDU Session, attempt, lifecycle, producer, or "latest" state.

For deterministic execution, `assurance/procedure.yaml` remains the exact machine
workflow. For LLM-driven execution, this file is the business guide; do not reconstruct
the deterministic graph as a second workflow.

When a model-driven execution route is enabled, use this file as business guidance. The Host owns execution admission and tool authority; do not reconstruct the deterministic Procedure graph as a second workflow.

## Supported profile

The current profile is intentionally narrow:

- local, non-roaming UE-requested establishment;
- Request Type = initial request;
- IPv4 PDU Session;
- SSC mode 1;
- one default non-GBR flow;
- no secondary PDU Session authentication/authorization with a DN-AAA server;
- no conditional SM Policy Association Modification branch unless a later profile adds it.

If the admitted request requires behavior outside this profile, do not silently skip the
missing branch and continue as though it had succeeded.

The occurrence carries the requested DNN, S-NSSAI, PDU Session Type and SSC mode together
with the exact PDU Session ID and PTI. Missing, stale, ambiguous or cross-occurrence
information is not a usable default.

Preserve the exact SSC mode list returned in `allowedSscModes`; do not truncate or deduplicate it during evaluation or selection. Open5GS may include the default in a three-mode list, while a standards-shaped subscription may list only additional modes. The default mode remains permitted even when it is absent from `allowedSscModes`. The supported request profile still requires SSC mode 1 and must prove that mode 1 is permitted by either the default or the additional-mode list. Read `references/session-selection.md` only if more detail is needed.

## Business progression

Keep the procedure recognizable as UE-requested PDU Session Establishment:

1. `Nudm_SDM_Get`;
2. subscription-constrained selection;
3. `Nudm_SDM_Subscribe`;
4. `Npcf_SMPolicyControl_Create`;
5. initial N4 Session Establishment convergence;
6. `Namf_Communication_N1N2MessageTransfer`;
7. PDU Session Resource Setup convergence;
8. N4 Session Modification / forwarding convergence;
9. resource-responsibility finalization.

This is business guidance, not a replacement execution graph. The model chooses the next
business decision from the current Decision Context and Available Actions.

## Optional business references

You may decide whether more domain knowledge would help the current business
decision. Read only a relevant file through an available read-only reference reader, if one is provided. No reference is required at Skill activation:

- `references/3gpp-procedure.md` — 3GPP actors, message responsibilities and
  the distinction between initiating a transfer and network convergence.
- `references/session-selection.md` — DNN, S-NSSAI, PDU Session Type, SSC mode,
  subscription defaults and effective configuration decisions.
- `references/failure-handling.md` — business rejection, missing evidence,
  asynchronous waits, mutation uncertainty and resource responsibility.

These references supplement this guide, but are not live evidence, business
actions, a second execution graph or an alternative authority. Reference reads
are knowledge-tool interactions **within** a decision, not an `ACT` or
`OBSERVE` business response. Proceed without reading anything when the
current guidance and Decision Context suffice. Do not browse the Skill tree or
guess other paths; if a read is unavailable, never invent its contents or
bypass safety constraints.

## Configuration layers

Keep these three layers distinct:

- **Requested Session Parameters** — what this admitted UE occurrence requested.
- **Subscription-Constrained Selection** — what subscription data permits and supplies as
  policy input.
- **Effective Session Configuration** — what is actually authorized, allocated and ready
  to deliver to UE/RAN.

No earlier layer proves a later one.

Subscription defaults must not silently override the admitted UE request. A successful
policy or allocation operation must not be treated as proof that downstream delivery or
network convergence has already happened.

## Harness-enforced prerequisites

Some Skill-defined facts protect admission or a specific mutation and are enforced by the
Harness at the point where they matter. They are not ordinary model tasks and the model
does not need to spend a turn asking to verify them before every action.

| Prerequisite | Meaning |
| --- | --- |
| `createdsession.ingress.eligible` | this exact occurrence remains admitted for the supported profile |
| `createdsession.lifecycle.ready` | the current lifecycle remains valid for progression |
| `createdsession.pcf.create_inputs.ready` | the PCF create inputs (current session instance, allocated address, matched selection) are readable for this attempt; this is not create authorization |
| `createdsession.pcf.create_governed` | resource creation is authorized: the lifecycle is clean and the original SMF's competing create is governed |
| `createdsession.delivery_context.ready` | the delivery input facts required before N1/N2 transfer are ready; sender uniqueness belongs to the governed transfer mutation, not to this read |
| `createdsession.n1n2.hold_bound` | the exact Fabric-held original SMF N1/N2 transfer for this attempt is bound (a read: it does not claim, send, or prove RAN setup) |

The Host may expose the current result or a blocking reason in Decision Context or
Available Actions. If one of these prerequisites is not satisfied, do not try to bypass
it with another business action. The Harness rechecks mandatory guards when required,
including immediately before mutation dispatch.

## Model decision facts

These business facts are the main state the model consumes when deciding progression.
They may already be present in Decision Context; use `OBSERVE` only when a current fact
is actually needed and is not already established.

| Business fact | Meaning |
| --- | --- |
| `createdsession.udm.subscription_usable` | the current UDM subscription data is usable for this occurrence |
| `createdsession.udm.subscription_owned` | the required SDM subscription is durably owned |
| `createdsession.pcf.association_owned` | the required SM Policy Association is durably owned |
| `createdsession.n4.initial_resources_ready` | authoritative initial N4 resources are ready |
| `createdsession.amf.transfer_initiated` | the exact AMF N1/N2 transfer for this occurrence was initiated |
| `createdsession.ran.setup_accepted` | the RAN accepted PDU Session Resource Setup for this occurrence |
| `createdsession.n4.forwarding_ready` | required forwarding state is ready |
| `createdsession.resources.managed` | created resources and late-result responsibility are durably managed |

A request for one of these facts resolves the current Skill-defined truth through the
admitted verification path. The model does not decide how to query the underlying
Observation source, bind lifecycle/producer identity, or evaluate the Predicate.

## Decision rules

Use admitted business actions and current Skill-defined facts to decide progression.
Treat Harness-enforced prerequisites as execution constraints: consume their presented
status or blocking reason, but do not turn them into a routine OBSERVE checklist.

The Skill may:

- retrieve UDM SM subscription data;
- select configuration within the admitted request and subscription constraints;
- create the UDM SDM subscription;
- create the PCF SM Policy Association;
- obtain the current operation/allocation context;
- prepare the deterministic NAS/N2 SM artifacts required for delivery;
- initiate AMF N1/N2 Message Transfer;
- wait for or request authoritative core-network N4/RAN business facts;
- propose completion when the business goal appears satisfied;
- stop when safe progression cannot be established.

Do not drive the Skill from what a temporary SMF happens to request, from what a waiter
expects to receive, or from a side effect merely being attempted.

## Opaque operation context

Operation-context, PCF-create readiness and held-operation references are distinct,
occurrence-bound handles. Never substitute one for another or infer ownership,
creation, sender reservation, delivery or network convergence from a handle alone.
Binding a hold is a read-only association; it does not claim or send the operation.
Use each handle only for its declared purpose and rely on the admitted Tool contract
and Host to enforce the exact operation identity and side-effect boundary.

## Unsafe inferences

Never make these substitutions:

- `Nudm_SDM_Get` success **does not mean** subscription evidence is usable.
- `Nudm_SDM_Subscribe` commit **does not mean** ownership verification can be skipped.
- `Npcf_SMPolicyControl_Create` success **does not mean** an unsupported conditional
  Policy Association Modification branch has succeeded.
- a temporary SMF/PFCP request **does not mean** initial N4 resources are ready.
- a bound N1/N2 Fabric hold **does not mean** the hold was claimed, that N1/N2 was
  sent, that the AMF answered, or that RAN setup was accepted.
- a Fabric sender grant or a Provider transfer result **does not mean** the original
  SMF waiter received, or consumed, the AMF response.
- AMF N1/N2 transfer success **does not mean** RAN setup is accepted.
- RAN setup acceptance **does not mean** N4 forwarding is ready.
- earlier N4 establishment **does not mean** later forwarding convergence is complete.
- a successful RAN/N4 exchange **does not mean** the UE accepted anything locally;
  UE-internal state is not an Agent-observable business fact and is never a
  completion gate for this Skill.
- successful business operations **do not mean** resource responsibility is finalized.
- reaching the expected last business stage **does not mean** the Skill Contract passes.
- missing, stale, ambiguous, wrong-lifecycle or wrong-producer evidence **does not mean**
  PASS or FAIL; it remains unresolved according to the Skill-defined verification rules.

## Verification and evidence

Business facts are established by the Skill's assurance definitions, not by model
interpretation.

Verification may be simple or procedural:

- a trusted current Observation may be evaluated directly as a Predicate;
- an asynchronous business fact may require governed waiting/read behavior before the
  Predicate can be evaluated.

The same verification machinery is shared by deterministic and LLM-driven execution.

Evidence is always bound to the current occurrence and, where required, to the exact
producer. In particular:

- UDM read usability belongs to the exact UDM invocation/transaction result;
- AMF transfer acknowledgement belongs to the exact N1N2 transfer operation;
- RAN adoption and N4 forwarding convergence belong to the current lifecycle, the
  causal transfer context and the exact Post-N4 session instance;
- resource responsibility belongs to the current lifecycle.

Never use latest-per-UE or latest-per-session evidence as a substitute for exact
occurrence/provenance binding.

## Ownership boundary

This Skill owns business progression and the facts required to prove completion.
Protocol transport, network side effects, operation identity, resource responsibility
and late-result handling belong to the admitted tool owners and Host. An action
response or transport acknowledgement does not prove delivery, RAN adoption,
forwarding convergence or final completion.

## Completion

Operation success and Skill completion are different things.

The Skill succeeds only when the Contract independently establishes all required final
facts, including:

- the SMF adopted the RAN PDU Session Resource Setup of the current occurrence;
- the SMF/UPF downlink forwarding resources of the same N4 session instance are ready;
- created resources and late-result responsibility durably managed.

UE-internal state (NAS PS-ACTIVE, TUN, ping) is deliberately **not** a completion
fact: it is not Agent-observable, and the Agent must not claim it.

A model may propose completion, but the Contract is the final authority.

## Failure and recovery

Keep these outcome domains distinct:

- Predicate: `PASS / FAIL / UNKNOWN`;
- mutation certainty: `COMMITTED / NOT_COMMITTED / OUTCOME_UNKNOWN`;
- Procedure terminal: `SUCCEEDED / FAILED / UNRESOLVED / SAFE_STOPPED`.

Before resource creation begins, an explicit request/subscription/business rejection may
fail; unavailable or ambiguous required evidence remains unresolved.

Once resource creation begins, responsibility for created resources and late results is
retained through every exit.

If a mutation outcome is `OUTCOME_UNKNOWN`:

1. stop business progression;
2. reconcile the exact original mutation;
3. never blindly retry it;
4. never consume an output that may not exist;
5. safe-stop the current invocation according to the governed recovery policy.

Any later continuation is a new admitted recovery decision with a new authoritative
lifecycle identity.
