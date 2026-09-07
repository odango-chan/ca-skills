# /// connectionagent-tool
# name: evaluate-transfer-request-satisfied
# inputSchema: TransferRequestPredicateEvaluationContext
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

class TransferRequestPredicateEvaluationContext(dict):
    pass

class PredicateEvaluationResult(dict):
    pass

def _evidence_refs(input):
    refs = []
    seen = set()
    for metadata in input.get("evidence", {}).values():
        for ref in metadata.get("refs", []):
            if ref not in seen:
                seen.add(ref)
                refs.append(ref)
    return refs


def main(input: TransferRequestPredicateEvaluationContext) -> PredicateEvaluationResult:
    request = input["request"]
    observations = input["observations"]
    virtual_group = observations["virtualGroup"]
    evidence_used = _evidence_refs(input)

    operation = request["operation"]
    group_state = virtual_group["state"]

    if operation == "release_group":
        if group_state == "RELEASED" or group_state == "NOT_FOUND":
            return {
                "result": "PASS",
                "reasonCode": "VIRTUAL_GROUP_RELEASED",
                "summary": "The virtual group is released or no longer present.",
                "evidenceUsed": evidence_used,
            }
        return {
            "result": "FAIL",
            "reasonCode": "VIRTUAL_GROUP_STILL_PRESENT",
            "summary": "The virtual group is still present after a release request.",
            "evidenceUsed": evidence_used,
            "details": {"groupState": group_state},
        }

    members_assigned = virtual_group["membersAssigned"]
    if group_state != "CREATED" and group_state != "MEMBERS_ASSIGNED":
        return {
            "result": "FAIL",
            "reasonCode": "VIRTUAL_GROUP_NOT_PREPARED",
            "summary": "The virtual group is not in a prepared state.",
            "evidenceUsed": evidence_used,
            "details": {"groupState": group_state},
        }

    if members_assigned is not True:
        return {
            "result": "FAIL",
            "reasonCode": "VIRTUAL_GROUP_MEMBERS_NOT_ASSIGNED",
            "summary": "The virtual group does not contain the required members.",
            "evidenceUsed": evidence_used,
        }

    if request["urgency"] == "urgent":
        qos_boost = observations.get("qosBoost")
        if qos_boost is None:
            # The Evidence Gate should normally prevent this invocation. Keep a
            # fail-closed defensive result in case the evaluator is called directly.
            return {
                "result": "UNKNOWN",
                "reasonCode": "QOS_BOOST_EVIDENCE_MISSING",
                "summary": "Urgent transfer readiness cannot be judged without QoS boost evidence.",
                "evidenceUsed": evidence_used,
            }
        if qos_boost["state"] != "COMMITTED":
            return {
                "result": "FAIL",
                "reasonCode": "QOS_BOOST_NOT_COMMITTED",
                "summary": "Urgent transfer preparation requires a committed QoS boost.",
                "evidenceUsed": evidence_used,
                "details": {"qosBoostState": qos_boost["state"]},
            }

    return {
        "result": "PASS",
        "reasonCode": "TRANSFER_REQUEST_SATISFIED",
        "summary": "The requested transfer network preparation is satisfied.",
        "evidenceUsed": evidence_used,
    }
