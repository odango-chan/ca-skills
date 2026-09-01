# SBI-proxy Provider and Observation Mapping

This document records the migration mapping from the legacy prompt-driven Skill to stable ConnectionAgent Capability and Observation semantics.

It is not a Runtime Binding Truth Source. Production `ProviderBinding` and `ObservationBinding` belong to Runtime/deployment configuration.

## 1. Participant registration Observation

Canonical Observation:

```text
transfer.participants.registration
```

Current SBI-proxy acquisition mapping:

```text
sender
  -> nf_udm_get_am_data(imsi=<sender>)

receivers, in canonical order
  -> nf_udm_get_am_data(imsi=<receiver>)
```

The Observation provider deterministically queries each canonical participant and normalizes the result into one typed participant-registration collection.

This is not a Procedure action in the target Skill. A `verify` checkpoint requires the Observation and Runtime obtains it through `ObservationBinding`.

No member may be silently skipped because another member already failed.

## 2. Participant PDU Session Observation

Canonical Observation:

```text
transfer.participants.session
```

Current acquisition mapping:

```text
sender
  -> nf_udm_get_sm_data(imsi=<sender>, sst=1, sd="000000")

receivers, in canonical order
  -> nf_udm_get_sm_data(imsi=<receiver>, sst=1, sd="000000")
```

`sst=1` and `sd="000000"` are current Skill proof-policy constants, not Agent request fields. They are part of the scoped Observation requirement.

The provider returns one typed collection Observation. Procedure control flow only sees the Predicate result; provider-specific proof fan-out stays behind `ObservationBinding`.

## 3. Participant endpoint resolution

Current UE endpoint addresses are runtime network state, not identity-routing context. They must not be copied from a static roster or produced by the LLM.

The Procedure therefore contains an explicit governed read-only Capability:

```text
transfer.participants.resolve_endpoints
```

Canonical input:

```text
senderImsi
receiverImsis
```

Canonical output:

```text
members:
  - imsi: <sender>
    ip: <current UE IPv4>
  - imsi: <receiver-1>
    ip: <current UE IPv4>
  ...
```

The member set is bounded by the request schema, ordered canonically as sender followed by receivers, and must contain exactly one endpoint for every requested participant. A missing, duplicate, malformed, or ambiguous endpoint does not produce a partial member list.

The concrete provider may resolve this from authoritative SMF/session state, Service Fabric state, or another certified read source. If a fresh previously materialized session Observation already contains the required endpoint data, the provider may reuse it internally, but the semantic read step remains explicit in the RunPlan and trajectory.

This Capability is intentionally different from the verify-only query operations removed from the Procedure. Its output is an operational input to a later mutation:

```text
transfer.participants.resolve_endpoints
  -> output.members
  -> virtual_group.assign_members
```

A read `UNKNOWN` or failure stops the preparation path before member assignment. It does not authorize the Agent or Provider to guess an address.

## 4. Edge cache

Capability:

```text
edge.cache.ensure
```

Current deployment mapping:

```text
edge_cache_create(upf_id="upf-1")
```

`upf-1` is a deployment/ProviderBinding choice. The canonical file-transfer request and Procedure do not ask the Agent to select an UPF merely to satisfy the concrete legacy Tool signature.

One Procedure action produces at most one normal dispatch. If dispatch outcome is unknown, Runtime enters `edge.cache.reconcile`; it does not blindly invoke `edge_cache_create` again.

The legacy tool set does not currently expose an explicit cache reconciliation API. The Provider therefore needs either an idempotent ensure contract with independently observable state or a dedicated reconciliation implementation before this path can be certified for ambiguous transport outcomes.

## 5. Virtual Group create

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

`duration=3600` and `qos_5qi=8` are current deterministic Skill policy and are materialized as Procedure literals. They are not semantic values the routing Agent must invent or copy into the target request.

The canonical Capability input also contains `transferId` as the correlation/idempotency key even though the legacy Tool does not currently accept it.

The canonical result must expose a structured `groupId` and contribute:

```text
facts.virtual_group.id
```

It may also contribute a fresh `virtual_group.snapshot` Observation when the returned state is sufficient and trustworthy; final verification may still require a later observation according to Runtime policy.

### Reliability gap

The current Tool cannot reliably distinguish these two states after a lost response:

```text
VG was not created
VG was created but the response was lost
```

Before production certification, the Provider needs a correlation-aware create/query contract, for example create/query-by-transferId, or an equivalent independently provable reconciliation mechanism.

## 6. Assign members

Capability:

```text
virtual_group.assign_members
```

Current mapping:

```text
vg_assign_members(
  group_id=<facts.virtual_group.id>,
  members_info=<resolved endpoint set JSON>
)
```

The Procedure binds `members` from the successful output of `transfer.participants.resolve_endpoints`, not from the Agent request:

```text
resolve-member-endpoints.output.members
```

This keeps current UE addresses tied to governed execution-time state. The static identity roster is never a Runtime Truth Source for endpoint addresses.

Ambiguous mutation results enter `virtual_group.reconcile_members` rather than replaying `vg_assign_members` immediately. Reconciliation reuses the already-resolved canonical member set from the same run; it does not silently re-resolve a potentially different address set after the mutation outcome became ambiguous.

A committed canonical result may update the reusable `virtual_group.snapshot` Observation.

## 7. Virtual Group Observation

Canonical Observation:

```text
virtual_group.snapshot
```

One current acquisition mechanism is:

```text
vg_status(group_id=<groupId>)
```

This mapping belongs to `ObservationBinding`; `virtual_group.status` is not a stable business Procedure action merely because status must be checked.

`vg_list()` may be used internally by an Observation/Reconciliation provider when necessary to resolve correlation. It should not be exposed as a planning action unless a governed business Procedure genuinely requires that operation.

## 8. QoS boost

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

The canonical action result may contribute:

```text
transfer.qos.boost_state
```

as a typed Observation. Runtime may reuse that Observation during final verification if it satisfies freshness/provenance policy. If stronger or newer proof is required, ObservationBinding may resolve another source.

An ambiguous result enters `transfer.qos.reconcile`. If the Provider cannot independently determine the state, the execution remains unresolved rather than re-dispatching the boost.

## 9. Virtual Group release

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

A committed release result may contribute an updated `virtual_group.snapshot` indicating `RELEASED` or `NOT_FOUND`.

A transport-level ambiguous result is different from `not found`: it enters `virtual_group.reconcile_release` and must not cause another release dispatch in the same Procedure.

## 10. Input ownership rule

Keep four input classes separate:

```text
Gateway / routing request
  -> operation, transferId, urgency, canonical participant identities

Governed execution-time read
  -> current dynamic operational data needed by later actions, such as UE endpoint addresses

Skill policy
  -> fixed slice proof scope, duration and QoS defaults

Runtime / deployment binding
  -> concrete Provider/UPF/endpoints and credentials
```

A dynamic network value should not be pushed upward into the Agent request merely because a later Tool needs it. If it is genuine operational dataflow, represent a stable read-only Capability and pass its typed output to the later action.

Then keep business action and proof acquisition separate:

```text
Capability
  -> ProviderBinding
  -> governed business read or mutation

Observation
  -> ObservationBinding
  -> proof acquisition / reuse / normalization
```

A concrete legacy Tool may participate in either family, but that does not make its Tool name or deployment arguments part of stable Skill request semantics.

## 11. Tools intentionally excluded from business authority

The following legacy operations do not belong to this Skill's governed business-action envelope merely because they exist:

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

Read-only operations may appear behind an authorized ObservationBinding when they exist only to prove a Predicate, or behind a narrowly defined read-only Capability when their output is genuine governed business dataflow such as endpoint resolution.

If a future file-transfer flow genuinely needs a new operation, expand the Capability Contract and Procedure explicitly rather than adding a broad Tool whitelist to `SKILL.md`.
