"""Validate current SMF session facts before N4 forwarding modification.

The Observation is a fresh, read-only business query after the Step 15
continuation. Session presence and projection availability are separate:
ABSENT is a known business failure at this point; PRESENT+UNAVAILABLE is
known presence but insufficient data; UNKNOWN means presence is indeterminate.
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
    presence = observation["sessionPresence"]

    if presence == "ABSENT":
        return {
            "result": "FAIL",
            "reasonCode": "SMF_SESSION_CONTEXT_ABSENT_AFTER_UPDATE",
            "evidenceUsed": evidence_refs,
        }

    if presence != "PRESENT":
        return {
            "result": "UNKNOWN",
            "reasonCode": "SMF_SESSION_CONTEXT_PRESENCE_UNKNOWN",
            "evidenceUsed": evidence_refs,
        }

    if observation["projectionStatus"] != "AVAILABLE":
        return {
            "result": "UNKNOWN",
            "reasonCode": "SMF_SESSION_CONTEXT_PROJECTION_UNAVAILABLE",
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
