---
name: download-object-by-deadline
description: Complete a downlink download of a specified object before a trusted deadline; the LLM does not guess object size or low-level QoS, and an independent business oracle proves success.
---

# Download Object by Deadline

Use this Skill when the business request identifies `ueRef`, `objectRef`, a trusted `deadline`, `secondsRemaining`, and `direction=downlink`, and the download must be planned from object size and governed QoS/capacity policy.

Do not guess `sizeBytes`, DNN, S-NSSAI, 5QI, or safety margin. Use a trusted request size when present; otherwise obtain size through the read-only Metadata Capability. If size cannot be observed, block planning or request trusted information.

The governed flow derives the minimum payload bitrate from the real size and trusted remaining time, then uses the QoS resolver for capacity/QoS admission before downloading. Capacity, Session/QoS convergence, and a download `COMMITTED` result are not proof that the business goal succeeded.

The final business result requires both `file_transfer.completed=PASS` and `file_transfer.deadline_met=PASS`. If a download mutation returns `OUTCOME_UNKNOWN`, do not retry it directly; use the matching download status path and let deterministic Runtime recovery decide whether a retry is safe.

Submit the structured business request or select this executable Skill target. Do not invent missing operational values or individual low-level Actions.
