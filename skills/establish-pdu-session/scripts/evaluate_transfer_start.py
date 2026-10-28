# /// connectionagent-tool
# name: evaluate-transfer-start
# inputSchema: TransferResponseEvaluationInput
# outputSchema: PredicateEvaluationResult
# effect: local_compute
# sandbox:
#   network: denied
# timeout: 1s
# ///

class TransferResponseEvaluationInput(dict):
    pass

class PredicateEvaluationResult(dict):
    pass

def main(input: TransferResponseEvaluationInput) -> PredicateEvaluationResult:
    response = input["observations"]["response"]
    refs = []
    for metadata in input.get("evidence", {}).values():
        for ref in metadata.get("refs", []):
            if ref not in refs:
                refs.append(ref)
    result = "UNKNOWN"
    reason = "TRANSFER_NOT_PROVEN"
    if response.get("networkOutcome") == "HTTP_RESPONSE":
        if response.get("responseOrigin") == "TARGET_SERVICE_VIA_SCP":
            if response.get("captureComplete") is True:
                status = response.get("httpStatus")
                if status == 200:
                    if response.get("cause") == "N1_N2_TRANSFER_INITIATED":
                        result = "PASS"
                        reason = "TRANSFER_INITIATED_ONLY"
                elif type(status) is int:
                    if status >= 400:
                        if status <= 599:
                            result = "FAIL"
                            reason = "AMF_TARGET_HTTP_ERROR"
    return {"result": result, "reasonCode": reason, "evidenceUsed": refs}
