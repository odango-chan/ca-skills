# /// connectionagent-tool
# name: evaluate-udm-read
# inputSchema: ProtocolResponseEvaluationInput
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

class ProtocolResponseEvaluationInput(dict):
    pass

class PredicateEvaluationResult(dict):
    pass

def main(input: ProtocolResponseEvaluationInput) -> PredicateEvaluationResult:
    response = input["observations"]["response"]
    refs = []
    for metadata in input.get("evidence", {}).values():
        for ref in metadata.get("refs", []):
            if ref not in refs:
                refs.append(ref)
    result, reason = "UNKNOWN", "UDM_RESULT_UNUSABLE"
    if (response.get("networkOutcome") == "HTTP_RESPONSE"
            and response.get("responseOrigin") == "TARGET_SERVICE_VIA_SCP"
            and response.get("captureComplete") is True):
        selection = response.get("selection")
        if response.get("httpStatus") == 200 and selection == "MATCHED" and "subscription" in response:
            result, reason = "PASS", "UDM_SUBSCRIPTION_MATCHED"
        elif response.get("httpStatus") == 200 and selection == "NO_MATCH":
            result, reason = "FAIL", "UDM_SUBSCRIPTION_NOT_MATCHED"
        elif selection == "HTTP_ERROR" and 400 <= response.get("httpStatus", 0) <= 599:
            result, reason = "FAIL", "UDM_TARGET_HTTP_ERROR"
    return {"result": result, "reasonCode": reason, "evidenceUsed": refs}
