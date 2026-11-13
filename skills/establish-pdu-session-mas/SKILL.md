---
name: establish-pdu-session-mas
description: Fulfil an admitted UE-requested initial PDU Session Establishment using governed session-management capabilities backed by SMF MAS.
---

# Establish PDU Session through SMF MAS

## When to use

Use this Skill only for one clearly identified, admitted **initial UE-requested PDU Session Establishment**. It does not execute a generic session modification, release, or Service Request activation.

The first supported profile is a local, non-roaming IPv4 session with SSC mode 1, an explicit DNN and S-NSSAI, one default non-GBR flow, and **no required secondary authentication**. The request, subscription, and active deployment facts must all support this profile.

Do not reinterpret an unsupported request, invent missing identifiers, or silently select another profile. If the exact UE, PDU Session, request occurrence, session identity, or execution ownership cannot be established, stop rather than guess.

## Business progression

The admitted request must first be eligible for this establishment operation, including the correct lifecycle, unique execution ownership, and usable subscription. Subscription validation must establish that the requested DNN, slice, session type, and SSC mode are permitted. A protocol acknowledgement or a summary without the relevant subscription restrictions is not sufficient.

The policy-first profile has this ordered business progression:

1. **Validate subscription** and establish the supported no-secondary-auth profile.
2. **Account for secondary-auth disposition.** This profile rejects a subscription that requires secondary authentication. The certified flow still records the no-auth disposition; absence of a requirement is not itself proof that the disposition was accounted for.
3. **Create the SM context** from the validated subscription. Preserve the exact session identity and the SMF-issued context reference.
4. **Register UECM** for the exact UE and PDU Session.
5. **Create the initial policy association before anchor selection and address allocation.**
6. **Select the authorized user-plane anchor.**
7. **Allocate the UE address.**
8. **Update the same policy association using the actual allocated address.** The updated policy, QoS, and user-plane intent are authoritative; do not reuse the initial policy values.
9. **Create charging** for the same session occurrence.
10. **Establish the initial N4 user-plane session.** This creates the initial N4 resources; it does not mean N3 forwarding is already ready.
11. **Confirm the allocated address only when the admitted deployment profile requires it.** Do not infer the need to skip or execute confirmation from the allocator's name alone.
12. **Signal the UE access network.** The SMF must adopt the RAN setup result and return the resulting access tunnel. A transfer acknowledgement alone is not RAN acceptance.
13. **Modify the same N4 session** using the returned access tunnel to establish N3/downlink forwarding.
14. **Emit the establishment event.** Event emission may be asynchronous and is not an additional gate for declaring the session established.

Each step must consume the actual output of its producer and remain bound to the same UE, PDU Session, SM context, policy association, and N4 session instance. Do not substitute a request value for an observed allocated address, a previous policy result for the updated result, or an unrelated N4 SEID or stale RAN tunnel for the current session.

## Operation and waiting boundary

Each MAS business operation is a separate request/response. An SMF operation may keep its own request open while it completes a southbound interaction. That internal wait belongs to the SMF operation; it is not a separate Skill wait step.

In particular:

- The initial N4 establishment result belongs to the N4 establishment operation.
- The RAN-adopted result and access tunnel belong to the access-signalling operation.
- N3 forwarding readiness belongs to the subsequent N4 modification operation.
- Do not add Agent-side polling, a generic wait node, or a repeated QueryContext loop between these operations.
- Do not treat a successful Namf transfer response as proof that the SMF adopted the RAN result.

The Host must handle the required protocol relay and raw southbound callbacks for the outstanding operation. Those protocol messages are not new business Operations and must not be wrapped in a second, competing execution protocol.

## Context and observations

Use Operation outputs directly when they provide the required, correctly scoped result for the next step or Predicate. Do not add a second read merely to reconstruct information already returned by the exact Operation.

SMF MAS QueryContext is a separate, read-only capability for an explicit context lookup or diagnosis. It can report that a MAS projection is AVAILABLE or UNAVAILABLE. Use it only when the requested decision genuinely needs that context; an unavailable projection is not permission to poll repeatedly, and QueryContext does not replace a business Operation or its result.

## What must be known

Before progressing beyond a stage, establish the relevant facts from trusted inputs and current results:

- The exact UE, request, ingress, lifecycle, SM context, and session generation belong to this invocation.
- The subscription and resulting policy authorize the effective DNN, slice, session type, SSC mode, UE address, QoS, and user-plane intent.
- The initial N4 resources exist for this session, and the RAN setup result has actually been adopted by the SMF.
- The final forwarding update belongs to those same resources and uses the current access tunnel.
- All created resources and possible late callbacks/results have a known, durable owner or a verifiable release record.

A successful action response is not by itself proof of a business postcondition. If authoritative evidence is missing, stale, from the wrong producer, or from a different session generation, the business fact remains **UNKNOWN**.

## Completion

Completion requires all of the following for this exact establishment occurrence:

1. The SMF has adopted the relevant RAN setup result.
2. Downlink forwarding is ready on the same N4 session instance.
3. Resource and late-result responsibility has been durably accounted for by the responsible owner.

These conditions must be independently established. A model response, a transfer acknowledgement, or an HTTP success status alone cannot assert completion.

## Failure and uncertainty

An explicit, proven business rejection follows the admitted failure handling. The SMF's compensation operation is best-effort; its response is not, by itself, proof that every resource was released. Only confirmed cleanup or a durable owner handoff can settle created-resource responsibility.

After an action may have been sent, timeout, disconnect, malformed response, or an ambiguous error must not be treated as proof that the action did not commit. Preserve the **original** operation identity for reconciliation. Do not blindly retry the mutation under a new identity or infer success from a late, unrelated response.

When the state of a mutation or its resources cannot be established, stop safely with responsibility preserved. A later continuation requires fresh admission and authoritative state; it does not reuse a guessed outcome.

## Readiness

This package is a source/design candidate, not a deployable executable Skill yet. Execution remains blocked until the SMF Owner publishes the exact ToolCatalog Operations and typed Input/Output Schemas, the deployment publishes the matching CapabilityContracts, and the Host ingress, reconciliation, and durable resource-responsibility boundaries are approved. Do not treat the proposed MAS ToolCatalog in the Agent demo as an approved Owner contract.
