"""Validate the requested session profile against the exact UDM subscription result.

This is a Step 4 Postcondition evaluator, not a Procedure Operation and not a
replacement for native SMF Step 8 UPF/session-address selection.
"""
from __future__ import annotations

from typing import Annotated, Literal, TypedDict


class PredicateEvaluationResult(TypedDict):
    result: Literal["PASS", "FAIL", "UNKNOWN"]
    reasonCode: Annotated[str, {"minLength": 1}]
    evidenceUsed: list[str]


def main(input: PredicateInput) -> PredicateEvaluationResult:
    evidence_refs = input["evidence"]["receipt"]["refs"]
    if not evidence_refs:
        return {
            "result": "UNKNOWN",
            "reasonCode": "UDM_SUBSCRIPTION_EVIDENCE_MISSING",
            "evidenceUsed": [],
        }

    subscription = input["receipt"]["result"]["subscription"]
    if (subscription["dnn"] != input["requestedDnn"]
            or subscription["sNssai"] != input["requestedSNssai"]):
        return {
            "result": "FAIL",
            "reasonCode": "UDM_SUBSCRIPTION_SCOPE_MISMATCH",
            "evidenceUsed": evidence_refs,
        }

    session_types = subscription["pduSessionTypes"]
    allowed_types = session_types.get(
        "allowedSessionTypes", [session_types["defaultSessionType"]]
    )
    if input["requestedPduSessionType"] not in allowed_types:
        return {
            "result": "FAIL",
            "reasonCode": "PDU_SESSION_TYPE_NOT_ALLOWED",
            "evidenceUsed": evidence_refs,
        }

    ssc_modes = subscription["sscModes"]
    allowed_modes = ssc_modes.get("allowedSscModes", [])
    if (input["requestedSscMode"] != ssc_modes["defaultSscMode"]
            and input["requestedSscMode"] not in allowed_modes):
        return {
            "result": "FAIL",
            "reasonCode": "SSC_MODE_NOT_ALLOWED",
            "evidenceUsed": evidence_refs,
        }

    return {
        "result": "PASS",
        "reasonCode": "UDM_SUBSCRIPTION_PROFILE_MATCHES_REQUEST",
        "evidenceUsed": evidence_refs,
    }
