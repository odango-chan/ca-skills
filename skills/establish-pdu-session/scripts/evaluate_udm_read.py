from typing import Annotated, Literal, TypedDict


class PredicateEvaluationResult(TypedDict):
    result: Literal["PASS", "FAIL", "UNKNOWN"]
    reasonCode: Annotated[str, {"pattern": r"^[A-Z][A-Z0-9_]*$"}]
    evidenceUsed: Annotated[list[Annotated[str, {"minLength": 1}]], {"uniqueItems": True}]


def main(input: dict) -> PredicateEvaluationResult:
    response = input["udmReadResult"]
    refs = list(dict.fromkeys(input.get("evidence", {}).get("udmReadResult", {}).get("refs", [])))
    result = "UNKNOWN"
    reason = "UDM_RESULT_UNUSABLE"
    status = response.get("httpStatus")
    if (response.get("networkOutcome") == "HTTP_RESPONSE"
            and response.get("responseOrigin") == "TARGET_SERVICE_VIA_SCP"
            and response.get("sourceBindingState") == "MATCHED"
            and response.get("captureComplete") is True and type(status) is int):
        selection = response.get("selection")
        subscription = response.get("subscription")
        if status == 200 and selection == "MATCHED" and isinstance(subscription, dict):
            result = "PASS"
            reason = "UDM_SUBSCRIPTION_MATCHED"
        elif status == 200 and selection == "NO_MATCH":
            result = "FAIL"
            reason = "UDM_SUBSCRIPTION_NOT_MATCHED"
        elif selection == "HTTP_ERROR" and 400 <= status <= 599:
            result = "FAIL"
            reason = "UDM_TARGET_HTTP_ERROR"
        elif selection == "AMBIGUOUS":
            reason = "UDM_SUBSCRIPTION_AMBIGUOUS"
        elif selection == "INVALID_PAYLOAD":
            reason = "UDM_RESPONSE_INVALID_PAYLOAD"
        elif selection == "INVALID_PROFILE_DATA":
            reason = "UDM_SUBSCRIPTION_INVALID_PROFILE"
        elif selection == "UNSUPPORTED_ENUM":
            reason = "UDM_SUBSCRIPTION_UNSUPPORTED_ENUM"
        elif selection == "UNSUPPORTED_VARIANT":
            reason = "UDM_SUBSCRIPTION_UNSUPPORTED_VARIANT"
    elif response.get("networkOutcome") == "TIMEOUT":
        reason = "UDM_READ_TIMEOUT"
    elif response.get("networkOutcome") == "TRANSPORT_FAILURE":
        reason = "UDM_READ_TRANSPORT_FAILURE"
    elif response.get("sourceBindingState") in {"MISMATCH", "UNVERIFIED"}:
        reason = "UDM_SOURCE_BINDING_UNVERIFIED"
    return {"result": result, "reasonCode": reason, "evidenceUsed": refs}
