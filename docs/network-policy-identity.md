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
shape owner = ca-skills
              skills/5gc-file-transfer/schemas/file-transfer-request.schema.yaml
value owner = business materialization / gateway
              (the same initiator that supplies transferId and the participant IMSIs)
```

`ca-skills` owns the *shape*: the field names, types, ranges and the invariant
that every consumer reads the same object. The *values* are business input,
exactly like `transferId` in `docs/business-resource-identity.md`.

The Environment owner (`ca-lab`) has not yet declared the reference 5GC network
profile that a deployment would materialize (open: `odango-chan/ca-lab#15`).
Until it does, this Skill takes the values as an **explicit request field**
supplied by business materialization; it does not invent defaults, and the
request schema fails closed when `networkPolicy` is absent for
`prepare_transfer`.

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
business gateway / materialization
  -> request.networkPolicy {dnn, sst, sd, pduSessionId, fiveQi}
  -> 5gc-file-transfer procedure inputs
       policy-dnn, policy-sst, policy-sd, policy-pdu-session-id, policy-five-qi
  -> composed ensure-session-qos input (dnn, sst, sd, fiveqi) per receiver
  -> virtual_group.create fiveQi
  -> independent final goal verification (file_transfer.request.satisfied)
```

The binding is by reference in the Procedure source, so the value is resolved
once from the request and cannot diverge between these consumers.

## 5. Prohibited

```text
no literal sst/sd/fiveQi in assurance/predicates.yaml or assurance/procedure.yaml
no default invented by the routing Agent, the Benchmark, or the executor
networkPolicy values must not be derived from Trial/Attempt/Run/request ids
the urgent QoS boost must not be silently aliased to the baseline fiveQi
```

A missing or malformed `networkPolicy` fails request admission; it must never
fall back to a remembered fixture or static roster value.
