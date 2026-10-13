# Canonical Network Policy Identity

**Status: Accepted**
**Version: 1**
**Date: 2026-10-01**
**Tracking: odango-chan/ca-skills#7, odango-chan/ca-skill-toolchain#102, odango-chan/ca-lab#15**
**Companion: `docs/business-resource-identity.md` (the same owner pattern for `transferId`)**

## 1. Purpose

This contract freezes the single canonical source of the baseline 5GC network
policy values used by `5gc-file-transfer`. Before this change the same business
fact was scattered across three unrelated hard-codes:

```text
assurance/predicates.yaml   transfer.participants.pdu_sessions_active  sst: 1, sd: "000000"
assurance/procedure.yaml    virtual_group.create                       fiveQi: 8
(session convergence)       ensure-session-qos request needs           dnn, sst, sd, fiveQi
```

There was no single authority, so prerequisite convergence, virtual-group
creation and final verification could silently disagree. This contract removes
that possibility: one request field set feeds all consumers.

It is a business/domain contract owned by `ca-skills`. It does not introduce a
new cross-repository runtime service or a second policy authority.

## 2. Ownership

```text
shape owner       = ca-skills
                    skills/5gc-file-transfer/schemas/file-transfer-request.schema.yaml
reference value   = Environment owner (ca-lab)
owner               ca-lab/reference-5gc-network-policy@v1, per Environment generation
materialization   = business materialization consumes the selected Environment policy
                    and materializes it into the executable Skill input
```

`ca-skills` owns the *shape*: the field names, types, ranges and the invariant
that every consumer reads the same object.

The *values* are **Environment-owned**, not business-gateway-owned. `ca-lab`
declares the reference 5GC network/session policy as a read-only Environment
parameter (`odango-chan/ca-lab#15`, landed) and exposes it, generation-fenced,
through `calab.environment-inventory/v1` (`networkPolicy {authority, policyRef,
revision, generation, dnn, sst, sd, pduSessionId, fiveQi, digest}`).

Business materialization therefore does **not** author these values and they are
**not** a Goal field: the same logical Goal must not change identity when it is
evaluated in a different Environment. Instead:

```text
Goal { operation, receiverImsis, urgency, transferId }
  -> Resolve / Prepare Environment
  -> EnvironmentInventory networkPolicy (authority/policyRef/revision/generation/digest)
  -> Business Materialization
       ResolvedStimulus + BusinessMaterializationReceipt.businessResources.networkPolicy
  -> executable Skill input { transferId, senderImsi, receiverImsis, urgency, networkPolicy }
```

The Skill request schema still requires `networkPolicy` for `prepare_transfer`
and fails closed when it is absent, but the value comes from the prepared
Environment (via materialization), never from a Benchmark fixture, the routing
Agent or an executor default. If a future product surface must let the gateway
request a different policy, define an explicit `requested policy` vs `effective
Environment policy` distinction instead of merging the two.

### 2.1 5GC transfer resource owner boundary

The policy is consumed by 5GC-domain resources. In the reference simulated
deployment those resources are owned by `env-5gc-sim`, not Sandbox:

```text
ca-lab
  owns effective Environment networkPolicy

env-5gc-sim
  materializes UE/session/QoS state
  owns transfer.participants.* for the 5GC world
  owns edge.cache.* on the 5GC-file-transfer path
  owns virtual_group.* lifecycle/membership
  owns transfer.qos.* urgent acceleration
  owns virtual_group.snapshot / transfer.qos.boost_state readback

ca-sandbox
  owns WiFi simulation plus scheduler/fault/lifecycle surfaces
  is not a 5GC transfer/VG/QoS authority
```

The gateway still owns `transferId` allocation and the application/file-transfer
lifecycle. Passing that business identity into env-5gc-sim does not transfer its
ownership and must never alias it to Trial, Attempt, Runtime, request, or world
identities.

## 3. Canonical value set

`request.networkPolicy` is one object, required for `prepare_transfer`:

```text
dnn           string   baseline Data Network Name
sst           integer  S-NSSAI Slice/Service Type (0..255)
sd            string   S-NSSAI Slice Differentiator, 6 hex digits
pduSessionId  integer  canonical PDU Session identity (1..15)
fiveQi        integer  baseline 5QI applied to the session and the virtual group
```

`pduSessionId` is part of the set because the converged PDU session needs a
stable identity across the Skill's create/reconcile/observation path; it is a
policy value, not a Runtime or Benchmark identity.

### Single baseline 5QI

There is exactly one baseline `fiveQi` in the set. It is used by:

1. the composed `ensure-session-qos` input (`fiveqi`),
2. `virtual_group.create` (`fiveQi`),
3. the baseline QoS the converged PDU session is verified against.

Urgent acceleration is **not** part of this set. It remains the distinct
`transfer.qos.boost` / `transfer.qos.reconcile` path, applied only when the
normalized request is `urgency: urgent`, with its own reconcile semantics. A
deployment that later needs a virtual-group QoS different from the baseline
session QoS must add an explicit, separately owned policy field; it must not
reintroduce a second implicit hard-code.

## 4. Flow

```text
Goal { operation, receiverImsis, urgency, transferId }   # no networkPolicy
  -> Resolve / Prepare Environment
  -> EnvironmentInventory networkPolicy (ca-lab authority/policyRef/revision/generation/digest)
  -> Business Materialization
  -> executable Skill input networkPolicy {dnn, sst, sd, pduSessionId, fiveQi}
  -> 5gc-file-transfer procedure inputs
       policy-dnn, policy-sst, policy-sd, policy-pdu-session-id, policy-five-qi
  -> composed ensure-session-qos input (dnn, sst, sd, fiveqi) per receiver
  -> virtual_group.create fiveQi
  -> independent final goal verification (file_transfer.request.satisfied)
```

The binding is by reference in the Procedure source, so the value is resolved
once from the materialized request and cannot diverge between these consumers.

## 5. Prohibited

```text
no literal sst/sd/fiveQi in assurance/predicates.yaml or assurance/procedure.yaml
no default invented by the routing Agent, the Benchmark, or the executor
no networkPolicy field in the Goal / Intent source contract
networkPolicy values must not be derived from Trial/Attempt/Run/request ids
the urgent QoS boost must not be silently aliased to the baseline fiveQi
```

A missing or malformed `networkPolicy` fails request admission; it must never
fall back to a remembered fixture or static roster value.
