# /// connectionagent-tool
# name: evaluate-wifi-transfer-satisfied
# inputSchema: WifiTransferEvaluationInput
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

from typing import Any, Dict


def main(input: Dict[str, Any]) -> Dict[str, Any]:
    observations_used = input.get("observationIds", [])
    transfer_state = input["transferState"]

    if transfer_state == "UNKNOWN":
        return {
            "result": "UNKNOWN",
            "reasonCode": "WIFI_TRANSFER_STATE_UNKNOWN",
            "summary": "The transfer creation state cannot be proven.",
            "observationsUsed": observations_used,
        }

    if transfer_state != "CREATED":
        return {
            "result": "FAIL",
            "reasonCode": "WIFI_TRANSFER_NOT_CREATED",
            "summary": "The WiFi transfer was not created.",
            "observationsUsed": observations_used,
        }

    urgency = input["urgency"]
    boost_state = input["boostState"]

    if urgency == "urgent":
        if boost_state == "UNKNOWN":
            return {
                "result": "UNKNOWN",
                "reasonCode": "WIFI_QOS_BOOST_STATE_UNKNOWN",
                "summary": "Urgent transfer readiness cannot be proven because boost state is unknown.",
                "observationsUsed": observations_used,
            }
        if boost_state != "COMMITTED":
            return {
                "result": "FAIL",
                "reasonCode": "WIFI_QOS_BOOST_NOT_COMMITTED",
                "summary": "Urgent WiFi transfer readiness requires a committed QoS boost.",
                "observationsUsed": observations_used,
                "details": {"boostState": boost_state},
            }
    elif boost_state not in ("NOT_REQUIRED", "COMMITTED"):
        return {
            "result": "UNKNOWN" if boost_state == "UNKNOWN" else "FAIL",
            "reasonCode": "UNEXPECTED_WIFI_QOS_STATE",
            "summary": "The normal WiFi transfer path has an inconsistent boost state.",
            "observationsUsed": observations_used,
            "details": {"boostState": boost_state},
        }

    return {
        "result": "PASS",
        "reasonCode": "WIFI_TRANSFER_REQUEST_SATISFIED",
        "summary": "The requested WiFi transfer setup is satisfied.",
        "observationsUsed": observations_used,
    }
