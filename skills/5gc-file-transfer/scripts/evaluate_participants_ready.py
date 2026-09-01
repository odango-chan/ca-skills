# /// connectionagent-tool
# name: evaluate-participants-ready
# inputSchema: ParticipantReadinessEvaluationInput
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

from typing import Any, Dict, List


def _collect_observation_ids(members: List[Dict[str, Any]]) -> List[str]:
    seen = set()
    result: List[str] = []
    for member in members:
        for observation_id in member.get("observationIds", []):
            if observation_id not in seen:
                seen.add(observation_id)
                result.append(observation_id)
    return result


def main(input: Dict[str, Any]) -> Dict[str, Any]:
    members = input.get("members", [])
    if not members:
        return {
            "result": "UNKNOWN",
            "reasonCode": "PARTICIPANT_EVIDENCE_MISSING",
            "summary": "No participant observations were supplied.",
            "observationsUsed": [],
        }

    observations_used = _collect_observation_ids(members)

    not_registered = [
        member["imsi"]
        for member in members
        if member["registrationState"] == "NOT_REGISTERED"
    ]
    if not_registered:
        return {
            "result": "FAIL",
            "reasonCode": "PARTICIPANT_NOT_REGISTERED",
            "summary": "At least one participant is not registered.",
            "observationsUsed": observations_used,
            "details": {"members": not_registered},
        }

    inactive_sessions = [
        member["imsi"]
        for member in members
        if member["sessionState"] == "INACTIVE"
    ]
    if inactive_sessions:
        return {
            "result": "FAIL",
            "reasonCode": "PARTICIPANT_SESSION_INACTIVE",
            "summary": "At least one participant has no active PDU session.",
            "observationsUsed": observations_used,
            "details": {"members": inactive_sessions},
        }

    unknown_members = [
        member["imsi"]
        for member in members
        if member["registrationState"] == "UNKNOWN"
        or member["sessionState"] == "UNKNOWN"
    ]
    if unknown_members:
        return {
            "result": "UNKNOWN",
            "reasonCode": "PARTICIPANT_READINESS_UNKNOWN",
            "summary": "Participant readiness cannot be proven from the available observations.",
            "observationsUsed": observations_used,
            "details": {"members": unknown_members},
        }

    return {
        "result": "PASS",
        "reasonCode": "ALL_PARTICIPANTS_READY",
        "summary": "All participants are registered and have active PDU sessions.",
        "observationsUsed": observations_used,
        "details": {"participantCount": len(members)},
    }
