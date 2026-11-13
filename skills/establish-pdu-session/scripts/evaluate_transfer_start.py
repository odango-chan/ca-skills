from typing import Annotated, Literal, TypedDict


class PredicateEvaluationResult(TypedDict):
    result: Literal["PASS", "FAIL", "UNKNOWN"]
    reasonCode: Annotated[str, {"pattern": r"^[A-Z][A-Z0-9_]*$"}]
    evidenceUsed: Annotated[list[Annotated[str, {"minLength": 1}]], {"uniqueItems": True}]


def main(input: dict) -> PredicateEvaluationResult:
    transfer = input["transferResult"]
    refs = list(dict.fromkeys(
        input.get("evidence", {}).get("transferResult", {}).get("refs", [])
    ))
    expected_operation_ref = input["expectedOperationRef"]
    network_result = transfer.get("result")
    if (not isinstance(expected_operation_ref, str) or not expected_operation_ref
            or transfer.get("operationRef") != expected_operation_ref
            or not isinstance(network_result, dict)
            or network_result.get("operationRef") != expected_operation_ref
            or not refs):
        return {
            "result": "UNKNOWN",
            "reasonCode": "AMF_PRODUCER_EVIDENCE_MISMATCH",
            "evidenceUsed": refs,
        }

    result = "UNKNOWN"
    reason = "TRANSFER_NOT_PROVEN"
    status = network_result.get("httpStatus")
    if (network_result.get("networkOutcome") == "HTTP_RESPONSE"
            and network_result.get("responseOrigin") == "TARGET_SERVICE_VIA_SCP"
            and network_result.get("captureComplete") is True and type(status) is int):
        if status == 200 and network_result.get("cause") == "N1_N2_TRANSFER_INITIATED":
            result = "PASS"
            reason = "TRANSFER_INITIATED_ONLY"
        elif 400 <= status <= 599:
            result = "FAIL"
            reason = "AMF_TARGET_HTTP_ERROR"
    return {"result": result, "reasonCode": reason, "evidenceUsed": refs}
