# Modify OES operation mapping

**Status: SOURCE-ALIGNED DESIGN / NOT_QUALIFIED / NOT_LINKABLE.**

## Pinned source

- Repository: odango-chan/env-openamsm
- Commit: 594dec78b95bff4fdc34deac8a3a9681fb41228f
- Plan: upstream/openamsm/tools/nw-agent/plans/modify/pdu-mod-v3.yaml
- Plan blob SHA: 8a2caf343c29bb64cbb09b29994c79ac8ad5da05
- Implementation: src/smf/mas/sc/session_context.c, src/smf/mas/upn/upnode.c, src/smf/mas/ssm/ssm_ue.c

## Procedure mapping

| CA-SL Node | OES operation | Candidate callable | Effect | Input Schema | Output Schema | OES inputs / outputs |
| --- | --- | --- | --- | --- | --- | --- |
| m0 | SC.UPDATE_SM_CONTEXT | SC.UPDATE_SM_CONTEXT | MUTATION | wtlab:openamsm:mas:v0.3.0:sc-update-sm-context-input | wtlab:openamsm:mas:v0.3.0:sc-update-sm-context-result | no OES inputs; lifecycle |
| m3 | UPN.MODIFY_UP_SESSION | UPN.MODIFY_UP_SESSION_INTENT | MUTATION | wtlab:openamsm:mas:v0.3.0:upn-modify-intent-input | wtlab:openamsm:mas:v0.3.0:upn-modify-intent-result | up_intent='1'; n4_seid |
| m4 | SSM.SIGNAL_UE_AN | SSM.SIGNAL_UE_AN_MODIFY | MUTATION | wtlab:openamsm:mas:v0.3.0:ssm-signal-ue-an-modify-input | wtlab:openamsm:mas:v0.2.0:ssm-signal-ue-an-result | no OES inputs; an_tunnel_teid, an_tunnel_ip, an_tunnel |
| m5 | UPN.MODIFY_UP_SESSION | UPN.MODIFY_UP_SESSION | MUTATION | wtlab:openamsm:mas:v0.2.0:upn-modify-up-session-input | wtlab:openamsm:mas:v0.2.0:upn-modify-up-session-result | an_tunnel_teid, an_tunnel_ip, n4_seid; n3_synced |

The CA-facing ue_identity and psi values bind the exact SUPI / PSI Scope. For m0 and m4 they are Owner-only Scope inputs and are not forwarded as OES step inputs.

m3 and m5 are distinct Mutation occurrences. m3 invokes the no-tunnel UPN branch: the source applies the intent state and returns n4_seid. m5 invokes the tunnel branch, parks the PFCP modification and returns n3_synced only after the PFCP completion path. The existing v0.2.0 UPN Schema matches m5 only; it must not be widened to accept m3.

m4 is not Establishment s10. Its input shape is different even though its declared AN tunnel output shape matches the existing s10 output Schema. It therefore has its own callable and input Schema.

## Optional source step

OES m2 CA.UPDATE_CHARGING is optional and has no applicability predicate in the pinned plan. It is omitted from this Procedure and from its Capability grants. The current adapter writes only a local charging marker and records NOT_IMPL_skip; it does not reserve CHF charging.

## Host binding

The current OpenAMSM agent_step path rejects standard Nsmf Update business admission. The Host / Owner must publish a private binding for a new Modify invocation. A callback completing an existing Establishment s10 or Modify m4 occurrence must resume that exact original invocation, never create a new Modify Run.

## Qualification scenario matrix

| Scenario | Expected contract | Evidence status |
| --- | --- | --- |
| UE_INITIATED | Host-authenticated new UE modification; exact SUPI / PSI / generation | Source design only |
| AMF_INITIATED | Host-authenticated new AMF business modification | Source design only |
| NETWORK_TRIGGERED | Trusted internal Owner event; caller cannot choose the entryKind | Source design only |
| m3 / m5 profile split | Separate input/output Schemas and Mutation receipts; m5 reuses the existing v0.2.0 profile | Static regression only |
| m4 pending result | Complete only on the matching AN result for the original occurrence | Host / Owner test NOT_RUN |
| Unknown result | SAFE_STOPPED; no retry, compensation or new Run | Route design only |
| Establishment s10 callback | Resume the original Establishment Run; do not start Modify | Host test NOT_RUN |

This matrix is not Runtime, live 5GC or product qualification evidence.
