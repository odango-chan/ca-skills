# OpenAMSM MAS Modify / Release source mapping

**Status: SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.** This document records the pinned OES plans and the candidate CA-facing contracts required by the two v1alpha5 Procedures. It is not a published Owner ToolCatalog, a trusted DependencySnapshot, or runtime acceptance evidence.

## Pinned source baseline

- Repository: [odango-chan/env-openamsm](https://github.com/odango-chan/env-openamsm)
- Commit: [594dec78b95bff4fdc34deac8a3a9681fb41228f](https://github.com/odango-chan/env-openamsm/commit/594dec78b95bff4fdc34deac8a3a9681fb41228f)
- Modify plan: `upstream/openamsm/tools/nw-agent/plans/modify/pdu-mod-v3.yaml`
  - Blob SHA: `8a2caf343c29bb64cbb09b29994c79ac8ad5da05`
- Release plan: `upstream/openamsm/tools/nw-agent/plans/release/pdu-rel-v4.yaml`
  - Blob SHA: `849c3206569d452a663d1b8d42a63ffdc367be31`

Relevant pinned implementation files include `src/smf/mas/common/mas-facade.c`, `mas/sc/session_context.c`, `mas/ca/charge_adapter.c`, `mas/upn/upnode.c`, `mas/ssm/ssm_ue.c`, `mas/pa/policy_adapter.c` and `mas/se/session_exposure.c`.

## Modify: exact plan-to-Procedure mapping

| CA-SL Node | OES step | MAS / operation | Candidate Capability | OES inputs | OES outputs | Candidate Schema IDs |
| --- | --- | --- | --- | --- | --- | --- |
| `m0` | `m0` | `SC.UPDATE_SM_CONTEXT` | `mas.sc.context.update` | none; `ue_identity` / `psi` are Owner scope bindings only | `lifecycle` | `sc-update-sm-context-input` / `sc-update-sm-context-result` |
| `m2` | `m2` (optional) | `CA.UPDATE_CHARGING` | `mas.ca.charging.update` | none; `ue_identity` / `psi` are Owner scope bindings only | `charging_ref` | `ca-update-charging-input` / `ca-update-charging-result` |
| `m3` | `m3` | `UPN.MODIFY_UP_SESSION` | `mas.upn.up.session.modify` (reuse) | `up_intent="1"` | `n4_seid` | shared v0.3.0 `upn-modify-up-session-input` / `upn-modify-up-session-result` |
| `m4` | `m4` | `SSM.SIGNAL_UE_AN` | `mas.ssm.ue.an.signal` (reuse) | none; `ue_identity` / `psi` are Owner scope bindings only | `an_tunnel_teid`, `an_tunnel_ip`, `an_tunnel` | shared v0.3.0 `ssm-signal-ue-an-input` / `ssm-signal-ue-an-result` |
| `m5` | `m5` | `UPN.MODIFY_UP_SESSION` | `mas.upn.up.session.modify` (same callable, distinct occurrence) | `an_tunnel_teid`, `an_tunnel_ip`, `n4_seid` | `n3_synced` | same shared v0.3.0 UPN Schema pair |

The source step IDs are not public Skill arguments. The Host / Owner private binding must map the exact CA-SL node occurrence to the corresponding OES `stepId`; callable ID alone is insufficient. In particular, m3 and m5 are two distinct Mutations using the same callable identity and different input / output branches.

## Release: exact plan-to-Procedure mapping

| CA-SL Node | OES step | MAS / operation | Candidate Capability | OES inputs | OES outputs | Candidate Schema IDs |
| --- | --- | --- | --- | --- | --- | --- |
| `r1` | `r1` (optional) | `CA.DELETE_CHARGING` | `mas.ca.charging.delete` | none; `ue_identity` / `psi` are Owner scope bindings only | `charging_ref` | `ca-delete-charging-input` / `ca-delete-charging-result` |
| `r2` | `r2` | `UPN.DELETE_UP_SESSION` | `mas.upn.up.session.delete` | `trigger` | `released` | `upn-delete-up-session-input` / `upn-delete-up-session-result` |
| `r3` | `r3` | `SSM.SIGNAL_UE_AN` | `mas.ssm.ue.an.signal` (reuse) | `release="1"`, `trigger` | none | shared v0.3.0 SSM Schema pair |
| `r4` | `r4` | `PA.DELETE_SM_POLICY` | `mas.pa.sm.policy.delete` | `release="1"` | none | `pa-delete-sm-policy-input` / `pa-delete-sm-policy-result` |
| `r5` | `r5` | `SC.RELEASE_SM_CONTEXT` | `mas.sc.context.release` | `release="1"` | `lifecycle` | `sc-release-sm-context-input` / `sc-release-sm-context-result` |
| `r6` | `r6` | `SE.EMIT_EVENTS` | `mas.se.events.emit` (reuse candidate ID; release branch required) | `ev="RELEASED"` | none | v0.3.0 `se-emit-events-input` / `se-emit-events-result` |

OES r7 is `COMPENSATE_RELEASE` with `execute: skip`; it is not a Procedure Node. The plan's `compensate_then_replan_once` policy is not imported.

## Candidate Owner Schema inventory

The IDs below are **expected Owner exports**, not local Skill schemas. They must be published by the MAS Owner (currently ca-client-tools candidate work) and then linked through the exact `mas` DependencySnapshot. The package remains NOT_LINKABLE until those files and the corresponding ToolCatalog / Evidence / Capability contracts exist.

All IDs use the source-candidate namespace `wtlab:openamsm:mas:v0.3.0:`.

| Schema ID suffix | Required typed shape |
| --- | --- |
| `sc-update-sm-context-input` | object; `ue_identity` (SUPI string) and `psi` (integer 1–15), both Owner scope-only |
| `sc-update-sm-context-result` | object; `lifecycle` string |
| `ca-update-charging-input` | object; `ue_identity` and `psi`, Owner scope-only |
| `ca-update-charging-result` | object; `charging_ref` string |
| `upn-modify-up-session-input` | object; `ue_identity`, `psi`, and exactly one of: `upIntent="1"` (m3) OR `anTunnelTeid` + `anTunnelIp` + `n4Seid` (m5) |
| `upn-modify-up-session-result` | object; exactly one source branch: `n4_seid` string (m3) OR `n3_synced` string (m5) |
| `ssm-signal-ue-an-input` | object; `ue_identity`, `psi`, and exactly one branch: no additional OES inputs (m4) OR `release="1"` + normalized `trigger` (r3) |
| `ssm-signal-ue-an-result` | object; exactly one branch: `an_tunnel_teid`, `an_tunnel_ip`, `an_tunnel` strings (m4) OR empty object (r3) |
| `ca-delete-charging-input` | object; `ue_identity` and `psi`, Owner scope-only |
| `ca-delete-charging-result` | object; `charging_ref` string |
| `upn-delete-up-session-input` | object; `ue_identity`, `psi`, and normalized `trigger` enum |
| `upn-delete-up-session-result` | object; `released` string |
| `pa-delete-sm-policy-input` | object; `ue_identity`, `psi`, `release="1"` |
| `pa-delete-sm-policy-result` | empty object; r4 declares no public output |
| `sc-release-sm-context-input` | object; `ue_identity`, `psi`, `release="1"` |
| `sc-release-sm-context-result` | object; `lifecycle` string; r5 plan exposes no other field |
| `se-emit-events-input` | object; `ue_identity`, `psi`, `event="RELEASED"`; r6 does not declare `sessionKeys` |
| `se-emit-events-result` | empty object for r6; r6 declares no public output |

The shared UPN / SSM / SE callable IDs have occurrence-specific shapes. The Owner must publish a versioned union Schema that validates the exact branch selected by the private OES `stepId`. For `SE.EMIT_EVENTS`, the new release branch must not silently remove the existing Establishment `ESTABLISHED` / `sessionKeys` branch or change the existing Skill source. If one callable cannot safely expose both branches, publish a distinct Release callable export rather than weakening the schema. The Establishment v0.2.0 Procedure and 13-operation mapping are not modified by this PR.

### Trigger normalization

Release Request Schema values are symbolic Host-normalized values:

- `UE_REQUESTED`
- `AMF_UPDATE_SM_CONTEXT`
- `AMF_RELEASE_SM_CONTEXT`
- `PCF_INITIATED`
- `SMF_INITIATED`
- `LOCAL_INITIATED`

The Host classifies authenticated Nsmf Update / Release ingress or a trusted internal Owner event. The Owner adapter must map each symbolic value to the exact numeric trigger constant in the pinned OpenAMSM build before filling the OES `trigger` input. The numeric source mapping must be verified from the pinned headers and published in the Owner package. Passing a symbolic value directly to an `atoi`-based field is invalid. Until that mapping is published and tested, Release remains NOT_LINKABLE.

## Source facts and non-claims

- m2 is optional in the OES plan. The pinned CA adapter currently returns `charging_ref="1"` and records `NOT_IMPL_skip`; it does not perform a CHF reservation. The Skill represents this only as a local marker.
- r1 is optional in the OES plan. The pinned CA adapter currently returns `charging_ref="0"` and records `NOT_IMPL_skip`; it does not delete a CHF charging resource.
- m3 and m5 reuse `UPN.MODIFY_UP_SESSION` but have different input and output branches. Both are MUTATIONs with distinct occurrence identities.
- m4 and r3 reuse `SSM.SIGNAL_UE_AN` but have different occurrence semantics. m4 returns AN tunnel fields; r3 declares no output and must settle the exact release signal disposition.
- r2 is not complete merely because the Owner accepted the request. Its `released="1"` result must be tied to the exact PFCP Session Deletion completion.
- r3 may require a later AMF release confirmation. Owner completion must remain attached to the original occurrence and generation.
- r4 declares no public output. Evidence must distinguish a real PCF association deletion from a verified `NOT_PRESENT` association.
- r5 declares only `lifecycle`; the source returns `RELEASING`. Do not invent `RELEASED`, `user_plane_ready` or a Host ResourceMap tombstone output.
- r6 declares no public output. The local event is not a 3GPP SM Context Status Notify. Do not use `last_event` as an r6 output.
- No source-declared output may be inferred from private C fields that the OES plan does not project.

The Owner and Host requirements common to both Procedures are in [mas-lifecycle-owner-contract.md](mas-lifecycle-owner-contract.md). Scenario coverage and the current test boundary are in [mas-lifecycle-acceptance-matrix.md](mas-lifecycle-acceptance-matrix.md).
