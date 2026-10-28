# /// connectionagent-tool
# name: evaluate-udm-read
# inputSchema: UdmResponseEvaluationInput
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

class UdmResponseEvaluationInput(dict):
    pass

class PredicateEvaluationResult(dict):
    pass

def main(input: UdmResponseEvaluationInput) -> PredicateEvaluationResult:
    response = input["observations"]["response"]
    refs = []
    for metadata in input.get("evidence", {}).values():
        for ref in metadata.get("refs", []):
            if ref not in refs:
                refs.append(ref)
    result = "UNKNOWN"
    reason = "UDM_RESULT_UNUSABLE"
    if response.get("networkOutcome") == "HTTP_RESPONSE":
        if response.get("responseOrigin") == "TARGET_SERVICE_VIA_SCP":
            if response.get("captureComplete") is True:
                selection = response.get("selection")
                status = response.get("httpStatus")
                if type(status) is int:
                    if status == 200:
                        if selection == "MATCHED":
                            subscription = response.get("subscription")
                            if type(subscription) is dict and subscription:
                                result = "PASS"
                                reason = "UDM_SUBSCRIPTION_MATCHED"
                        elif selection == "NO_MATCH":
                            result = "FAIL"
                            reason = "UDM_SUBSCRIPTION_NOT_MATCHED"
                    elif selection == "HTTP_ERROR":
                        if status >= 400:
                            if status <= 599:
                                result = "FAIL"
                                reason = "UDM_TARGET_HTTP_ERROR"
    return {"result": result, "reasonCode": reason, "evidenceUsed": refs}
