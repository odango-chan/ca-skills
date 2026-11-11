# PDU Session Skill — Maintainer Integration Notes

**Maintainer-only. Not part of the Skill package and not model context.**

Source reference: `odango-chan/ca-agent-demo` main commit `4395982fa6efb97714b97901603b2dfb7018c4d0`, original `skills/establish-pdu-session/SKILL.md` and `skills/establish-pdu-session/design/README.md`.

This note preserves operation-context details that were removed from the model-facing `SKILL.md`. It records the current integration snapshot, not a permanent Skill identity or proof of production readiness.

## Purpose-bound handles

The current integration exposes distinct opaque handles. They are not interchangeable:

- `ca.session.operation_context.read` returns an operation-context `contextRef`. It is for the declared `nas-and-n2-delivery` purpose and downstream waits; it is not a PCF-create readiness handle.
- `ca.session.pcf_create_inputs.read` returns `pcfCreateInputsRef`, a short-lived PCF-create input-readiness handle. It does not represent operation context, association ownership, creation, sender reservation or callback ownership.
- `ca.session.pcf_hold.bind` returns the exact held PCF create reference. The original create hold appears only after the corresponding UDM Subscribe response has been answered; it must not gate the earlier subscription stage. The same reference is used for the matching pre-N4 read and governed create dispatch.
- `ca.session.n1n2_hold.bind` returns the exact held N1/N2 transfer reference for the current session occurrence. Binding is read-only: it does not claim or send. The later governed transfer operation owns commitment, claim and dispatch.

Never substitute a transport/hold operation identity for the Provider N4/artifact session instance. The exact current lifecycle, UE, PDU Session, operation and producer association must be preserved.

## UDM subscription provenance

UDM Subscribe uses the UDM read plus the governed selection. The consumer resolves the exact stored UDM record by subject, invocation and transaction; it must require a matched target-service read and compare the selected DNN, S-NSSAI, PDU Session Type and SSC tuple against that record.

The initial N4 wait is joined through the exact pre-N4 policy-association reference, not through an unrelated operation-context handle or a later Post-N4 SEID pair.

## Integration ownership snapshot

The current integration is transitional:

- the temporary SMF still executes PFCP/N4 and participates in compatibility CreateSMContext/UpdateSMContext transactions;
- AMF owns outer NAS transport/security and NGAP;
- the Agent does not construct PFCP or arbitrary NGAP;
- admitted capabilities prepare or read protocol/session artifacts;
- the network mediation path transports and records SBI traffic but does not choose session configuration.

These are maintainer integration facts, not model-facing Skill instructions. Consume real resulting state; never fabricate an address, tunnel identity, flow, protocol success or completion state to keep a temporary component moving.
