---
name: establish-pdu-session
description: Fulfil an admitted UE initial PDU Session Establishment request using independent SBI orchestration, N1/N2 SM semantics and verified network results.
---

# Establish PDU Session

Use this Skill for an admitted UE-originated initial establishment request, not for a user request to create a session from the core or to ensure an arbitrary desired state.

The first profile accepts a local non-roaming 3GPP IPv4 request with explicitly decoded SSC mode 1 and one default non-GBR flow. Required UE request fields must be established from that request. Missing extraction is not evidence that an information element was absent, and subscription defaults do not replace UE-requested values.

Use the uniquely selected subscription for the exact DNN, slice and serving PLMN. Preserve MNC width and absent versus zero SD. Do not infer a session is absent from an initial request or a missing source row.

Business choices remain independent of temporary SMF waiters. Real allocated UE addresses and current-instance resources are execution prerequisites; a policy response does not create them. Do not infer current-instance identity from SUPI/PSI reuse, equal TEIDs or nearby timestamps.

As the session-management controller, handle both N1 SM and N2 SM semantics: select the required resource setup and use typed RAN tunnel, flow and failure results. A governed deterministic protocol tool computes the required NAS/N2 containers; a separate admitted operation sends them. SMF retains N4 and native N2 result processing; AMF owns outer NGAP and NAS transport/security. Do not manually assemble protocol bytes or arbitrary NGAP information elements, invent tunnel parameters, or assume that NAS alone triggers radio setup.

A transfer acknowledgment, RAN result, UPF resource state and UE acceptance prove different things. Complete only when all required postconditions and ongoing resource responsibility are independently established. Missing, stale or ambiguous evidence remains unknown; a timeout is not permission to retry a mutation.
