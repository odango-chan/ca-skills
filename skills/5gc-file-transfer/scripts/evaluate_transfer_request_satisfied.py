# /// connectionagent-tool
# name: evaluate-transfer-request-satisfied
# inputSchema: TransferRequestEvaluationInput
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

from typing import Any, Dict


def main(input: Dict[str, Any]) -> Dict[str, Any]:
    observations_used = input.get("observationIds", [])
    operation = input["operation"]
    group_state = input["groupState"]

    if operation == "release_group":
        if group_state in ("RELEASED", "NOT_FOUND"):
            return {
                "result": "PASS",
                "reasonCode": "VIRTUAL_GROUP_RELEASED",
                "summary": "The virtual group is released or no longer present.",
                "observationsUsed": observations_used,
            }
        if group_state == "UNKNOWN":
            return {
                "result": "UNKNOWN",
                "reasonCode": "VIRTUAL_GROUP_RELEASE_STATE_UNKNOWN",
                "summary": "The release state cannot be proven.",
                "observationsUsed": observations_used,
            }
        return {
            "result": "FAIL",
            "reasonCode": "VIRTUAL_GROUP_STILL_PRESENT",
            "summary": "The virtual group is still present after a release request.",
            "observationsUsed": observations_used,
            "details": {"groupState": group_state},
        }

    if group_state == "UNKNOWN" or input["membersAssigned"] is None:
        return {
            "result": "UNKNOWN",
            "reasonCode": "TRANSFER_PREPARATION_STATE_UNKNOWN",
            "summary": "Transfer preparation cannot be proven from the available observations.",
            "observationsUsed": observations_used,
        }

    if group_state not in ("CREATED", "MEMBERS_ASSIGNED"):
        return {
            "result": "FAIL",
            "reasonCode": "VIRTUAL_GROUP_NOT_PREPARED",
            "summary": "The virtual group is not in a prepared state.",
            "observationsUsed": observations_used,
            "details": {"groupState": group_state},
        }

    if not input["membersAssigned"]:
        return {
            "result": "FAIL",
            "reasonCode": "VIRTUAL_GROUP_MEMBERS_NOT_ASSIGNED",
            "summary": "The virtual group does not contain the required members.",
            "observationsUsed": observations_used,
        }

    urgency = input["urgency"]
    qos_state = input["qosBoostState"]
    if urgency == "urgent":
        if qos_state == "UNKNOWN":
            return {
                "result": "UNKNOWN",
                "reasonCode": "QOS_BOOST_STATE_UNKNOWN",
                "summary": "Urgent transfer preparation cannot be proven because QoS boost state is unknown.",
                "observationsUsed": observations_used,
            }
        if qos_state != "COMMITTED":
            return {
                "result": "FAIL",
                "reasonCode": "QOS_BOOST_NOT_COMMITTED",
                "summary": "Urgent transfer preparation requires a committed QoS boost.",
                "observationsUsed": observations_used,
                "details": {"qosBoostState": qos_state},
            }
    elif qos_state not in ("NOT_REQUIRED", "COMMITTED"):
        return {
            "result": "UNKNOWN" if qos_state == "UNKNOWN" else "FAIL",
            "reasonCode": "UNEXPECTED_QOS_BOOST_STATE",
            "summary": "The normal transfer path has an inconsistent QoS boost state.",
            "observationsUsed": observations_used,
            "details": {"qosBoostState": qos_state},
        }

    return {
        "result": "PASS",
        "reasonCode": "TRANSFER_REQUEST_SATISFIED",
        "summary": "The requested transfer network preparation is satisfied.",
        "observationsUsed": observations_used,
    }
