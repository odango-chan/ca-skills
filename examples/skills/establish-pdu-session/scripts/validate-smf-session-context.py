"""Validate the current SMF session context before N4 forwarding modification.

This is a Postcondition Predicate Script over an explicit, read-only context
Observation. It does not poll for UpdateSMContext and does not inspect Host
lifecycle metadata. The underlying context-query compatibility mechanism is
not part of this Skill's business contract.
"""
from __future__ import annotations

from typing import Annotated, Literal, TypedDict


class PredicateEvaluationResult(TypedDict):
    result: Literal["PASS", "FAIL", "UNKNOWN"]
    reasonCode: Annotated[str, {"minLength": 1}]
    evidenceUsed: list[str]


def main(input: PredicateInput) -> PredicateEvaluationResult:
    evidence_refs = input["evidence"]["sessionContext"]["refs"]
    if not evidence_refs:
        return {
            "result": "UNKNOWN",
            "reasonCode": "SMF_SESSION_CONTEXT_EVIDENCE_MISSING",
            "evidenceUsed": [],
        }

    observation = input["sessionContext"]
    if observation["status"] != "AVAILABLE":
        return {
            "result": "UNKNOWN",
            "reasonCode": "SMF_SESSION_CONTEXT_UNAVAILABLE",
            "evidenceUsed": evidence_refs,
        }

    facts = observation["context"]
    required = ("dnn", "sst", "subscriptionValidated", "secondaryAuthRequired")
    if any(field not in facts for field in required):
        return {
            "result": "UNKNOWN",
            "reasonCode": "SMF_SESSION_CONTEXT_FIELDS_INCOMPLETE",
            "evidenceUsed": evidence_refs,
        }

    if facts["dnn"] != input["requestedDnn"] or facts["sst"] != input["requestedSst"]:
        return {
            "result": "FAIL",
            "reasonCode": "SMF_SESSION_CONTEXT_REQUEST_MISMATCH",
            "evidenceUsed": evidence_refs,
        }

    if facts["subscriptionValidated"] is not True:
        return {
            "result": "FAIL",
            "reasonCode": "SMF_SUBSCRIPTION_NOT_VALIDATED",
            "evidenceUsed": evidence_refs,
        }

    if facts["secondaryAuthRequired"] is not False:
        return {
            "result": "FAIL",
            "reasonCode": "SECONDARY_AUTHENTICATION_REQUIRED_OUT_OF_PROFILE",
            "evidenceUsed": evidence_refs,
        }

    return {
        "result": "PASS",
        "reasonCode": "SMF_SESSION_CONTEXT_PROFILE_MATCHED",
        "evidenceUsed": evidence_refs,
    }
