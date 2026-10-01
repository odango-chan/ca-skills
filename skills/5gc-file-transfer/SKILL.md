---
name: 5gc-file-transfer
description: Prepare or release governed 5GC resources for gateway-driven file transfers, with optional QoS acceleration for explicitly urgent requests.
---

# 5GC File Transfer

## Purpose

Prepare the 5GC resources needed by a gateway-driven file transfer, or release the transfer's virtual group when it ends.

This Skill owns core-network orchestration only. The gateway owns the file-transfer application lifecycle.

## Use when

Use this Skill for normalized requests corresponding to:

- `[TASK: 5GC-FILE-TRANSFER]` -> `prepare_transfer`;
- `[TASK: 5GC-VG-RELEASE]` -> `release_group`.

Do not use it for generic `[TASK: 5GC-INTENT]` routing or Wi-Fi transfer tasks.

## Business semantics

- The final `prepare_transfer` execution request must contain canonical sender/receiver IMSIs. A user-facing Goal may identify a receiver by name or alias instead of IMSI.
- When a participant is known only by name or alias, use an eligible model-visible read-only `ue.identity.lookup` Tool before constructing the final execution request. The lookup is planning input; it does not change Runtime execution authority.
- Treat identity lookup status explicitly:
  - `RESOLVED`: use the returned canonical IMSI for the returned logical subject;
  - `NOT_FOUND`: do not invent an IMSI; request/retain additional context;
  - `AMBIGUOUS`: do not pick one candidate; request disambiguation.
- Name/alias is a logical user-visible reference. IMSI is a current Provider/Environment binding and may change between Environments or Trials. Do not reuse an IMSI remembered from a previous Goal, Trial, lookup result, demo fixture, or static roster. Use the current admitted lookup result and its mapping provenance.
- Current UE endpoint addresses are dynamic network state and are not routing-model inputs.
- If the Agent must reason about a participant's current endpoint, connectivity, or other dynamic network state before selecting an execution target, establish that fact with an eligible model-visible read-only Tool rather than copying static data or inferring from an earlier mutation.
- For the current ConnectionAgent reference profile, `ue.identity.lookup` is the semantic read-only Capability for resolving a user-visible UE name/alias to a canonical IMSI. `RESOLVED` may be used to construct `receiverImsis`; `NOT_FOUND` or `AMBIGUOUS` requires context clarification rather than a guessed target.
- Agent-visible read results are planning inputs only. Governed execution independently acquires and verifies the evidence required by its Predicate and assurance contracts.
- Governed execution resolves the current participant endpoint set before assigning virtual-group members. Do not copy IP addresses from identity context.
- On `prepare_transfer`, the virtual-group id is produced during governed execution when the group is created or reconciled. It is not a planning input: do not require, supply, or infer it from request context (`release_group` supplies its own `groupId`).
- Registration and PDU-session/QoS readiness are *converged*, not assumed. Governed execution composes the certified `ue-registration` and `ensure-session-qos` Skills instead of re-authoring their action graphs, and a participant that is not registered or has no baseline session is brought to readiness before transfer-specific work. Do not pre-filter requests on those prerequisites, and do not treat their absence as an unconditional failure.
- `prepare_transfer` requires `networkPolicy` (`dnn`, `sst`, `sd`, `pduSessionId`, `fiveQi`). Its shape is owned by this Skill; its values are business input owned by the initiating gateway / materialization, in the same way as `transferId`. Do not invent, default, or copy these values from a fixture, roster, or prior Goal. See `docs/network-policy-identity.md`.
- Baseline `networkPolicy.fiveQi` is the single baseline applied to the converged session and the virtual group. Urgent acceleration is a distinct concern and is never expressed by rewriting the baseline value.
- `urgent` means the source intent explicitly asks for accelerated completion, such as urgent, ASAP, hurry, or an equivalent expression. A large file by itself is not urgent.
- Receiver consent, file upload/download, user-visible messages, and the decision to activate a virtual group remain gateway responsibilities.
- `virtual_group.activate` is therefore outside this Skill.
- Once the request is normalized, hand execution to the governed assurance entrypoint. Do not construct ad-hoc NF/VG/PCF Tool sequences from prose.

Provider implementation, ProviderBinding, identity-directory configuration, ObservationBinding, Predicate execution, UNKNOWN/reconcile behavior, Tool eligibility, and deployment-specific Tool mappings are governed outside model context by their owning Platform/Runtime/Environment contracts.
