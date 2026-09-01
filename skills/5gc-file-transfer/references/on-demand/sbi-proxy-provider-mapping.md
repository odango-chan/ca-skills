# SBI-proxy Provider Mapping

This document records the migration mapping from the legacy prompt-driven Skill to stable ConnectionAgent Capability semantics.

It is not the Runtime Binding Truth Source. Production binding belongs to Runtime/deployment configuration.

## 1. Participant registration observation

Capability:

```text
transfer.participants.registration.query
```

Current SBI-proxy implementation mapping:

```text
sender
  -> nf_udm_get_am_data(imsi=<sender>)

receivers, in canonical order
  -> nf_udm_get_am_data(imsi=<receiver>)
```

The Provider must issue one NF query per member and aggregate the individual observations into `transfer.participants.registered`.

No member may be silently skipped because another member already failed.

## 2. Participant PDU Session observation

Capability:

```text
transfer.participants.session.query
```

Current mapping:

```text
sender
  -> nf_udm_get_sm_data(imsi=<sender>, sst=1, sd="000000")

receivers, in canonical order
  -> nf_udm_get_sm_data(imsi=<receiver>, sst=1, sd="000000")
```

Again, one NF query is required per member. The aggregate predicate is `transfer.participants.pdu_sessions_active`.

## 3. Edge cache

Capability:

```text
edge.cache.ensure
```

Current mapping:

```text
edge_cache_create(upf_id="upf-1")
```

One Procedure action produces at most one normal dispatch. If dispatch outcome is unknown, Runtime enters `edge.cache.reconcile`; it does not blindly invoke `edge_cache_create` again.

The legacy tool set does not currently expose an explicit cache reconciliation API. The Provider therefore needs either an idempotent ensure contract with independently observable state or a dedicated reconciliation implementation before this path can be certified for ambiguous transport outcomes.

## 4. Virtual Group create

Capability:

```text
virtual_group.create
```

Current mapping:

```text
vg_create(
  sender_imsi=<sender>,
  receiver_imsis=<receivers csv>,
  duration=3600,
  qos_5qi=8
)
```

The canonical Capability input also contains `transferId` as the correlation/idempotency key even though the legacy Tool does not currently accept it.

The canonical result must expose a structured `groupId` and contribute:

```text
facts.virtual_group.id
```

### Reliability gap

The current Tool cannot reliably distinguish these two states after a lost response:

```text
VG was not created
VG was created but the response was lost
```

Before production certification, the Provider needs a correlation-aware create/query contract, for example create/query-by-transferId, or an equivalent independently provable reconciliation mechanism.

## 5. Assign members

Capability:

```text
virtual_group.assign_members
```

Current mapping:

```text
vg_assign_members(
  group_id=<facts.virtual_group.id>,
  members_info=<canonical members JSON>
)
```

`members` must use the gateway-provided IMSI/IP pairs exactly after request validation. The static phone roster from the old prompt is not a Runtime Truth Source.

Ambiguous mutation results enter `virtual_group.reconcile_members` rather than replaying `vg_assign_members` immediately.

## 6. Virtual Group status

Capability:

```text
virtual_group.status
```

Current mapping:

```text
vg_status(group_id=<groupId>)
```

This is read-only evidence used to verify the final request state and to support reconciliation.

`vg_list()` may be used by a Provider implementation only when necessary to resolve a correlation lookup; it should not be exposed as a separate planning action unless required by a governed Procedure.

## 7. QoS boost

Capability:

```text
transfer.qos.boost
```

Current mapping:

```text
pcf_qos_boost(transfer_id=<transferId>)
```

The Provider normalizes legacy results containing `scheduled`, `boosted`, or `accepted` to committed success.

The Procedure contains this action only in the `urgent` variant and dispatches it at most once. It never performs a restore operation.

An ambiguous result enters `transfer.qos.reconcile`. If the Provider cannot independently determine the state, the execution remains unresolved rather than re-dispatching the boost.

## 8. Virtual Group release

Capability:

```text
virtual_group.release
```

Current mapping:

```text
vg_release(group_id=<groupId>)
```

Provider normalization rules:

```text
released          -> COMMITTED
already released  -> COMMITTED
not found         -> COMMITTED
```

A transport-level ambiguous result is different from `not found`: it enters `virtual_group.reconcile_release` and must not cause another release dispatch in the same Procedure.

## 9. Tools intentionally excluded

The following legacy capabilities do not belong to this Skill's execution envelope:

```text
vg_activate
sbi_request
nf_udm_get_smf_select_data
nf_udm_get_ue_ctx_smf
nf_nssf_select_slice
open5gs_* process/database tools
filesystem/shell tools
message/spawn/cron/web
wifi_*
```

If a future file-transfer flow genuinely needs one of them, expand the Capability Contract and Procedure explicitly rather than adding a broad Tool whitelist to `SKILL.md`.
