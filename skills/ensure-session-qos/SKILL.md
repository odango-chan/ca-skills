---
name: ensure-session-qos
description: Converge a target UE to a PDU Session satisfying the requested DNN, S-NSSAI, and 5QI, with independent user-plane evidence for the final state.
---

# Ensure Session QoS

Use this Skill when the business goal is to ensure that a target UE has a data connection satisfying the requested DNN, S-NSSAI, and 5QI.

The goal is a PDU Session whose QoS is actually satisfied; one successful create or modify Action is not enough. User-plane connectivity is an independent final business condition, but restoring connectivity is not this Skill's active objective.

Follow these boundaries:

1. Do not start a Session mutation until the target UE is trusted as registered.
2. If the current Session and QoS already satisfy the request, verify them instead of writing again.
3. Do not maintain a second Session state model from guesses.
4. Do not blindly retry a side-effecting Action with an unknown outcome.
5. Prove Session state, QoS, and user-plane connectivity independently before declaring success.

Request fields and deterministic execution flow are defined by the `assurance/` machine contracts. Provider, Tool, ObservationBinding, and acquisition details belong to the governed execution plane.
