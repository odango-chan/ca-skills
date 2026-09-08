---
name: query-weather-for-ue
description: Query weather for a target UE after trusted user-plane connectivity prerequisites are satisfied; choose connection convergence, probing, or reconciliation from observed state.
---

# Query Weather for UE

Use this Skill when the user requests weather for a specified city and the business path must access the weather service through the target UE's data connection.

The UE must have trusted registration and usable user-plane connectivity before the weather service is called. An existing PDU Session does not prove connectivity, and a successful weather Tool call alone does not prove the business result.

Reject incomplete, empty, or invalid weather results explicitly. Never fabricate a business value. If no compliant weather capability is available, do not generate an unexecutable request.

Read `references/on-demand/weather-service-semantics.md` only when the weather Tool's input, output, or prerequisite semantics are needed. Procedure, Predicate, budget, and recovery behavior are defined by the `assurance/` machine contracts and Runtime contract.
