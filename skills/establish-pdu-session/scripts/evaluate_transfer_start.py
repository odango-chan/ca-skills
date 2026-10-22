# /// connectionagent-tool
# name: evaluate-transfer-start
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
    result, reason = "UNKNOWN", "TRANSFER_NOT_PROVEN"
    if (response.get("networkOutcome") == "HTTP_RESPONSE"
            and response.get("responseOrigin") == "TARGET_SERVICE_VIA_SCP"
            and response.get("captureComplete") is True):
        if response.get("httpStatus") == 200 and response.get("cause") == "N1_N2_TRANSFER_INITIATED":
            result, reason = "PASS", "TRANSFER_INITIATED_ONLY"
        elif 400 <= response.get("httpStatus", 0) <= 599:
            result, reason = "FAIL", "AMF_TARGET_HTTP_ERROR"
    return {"result": result, "reasonCode": reason, "evidenceUsed": refs}
