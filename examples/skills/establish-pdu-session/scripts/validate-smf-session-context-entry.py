"""Classify whether the exact UE/PSI SM Context is absent at Skill entry.

The generic SMF context Observation normalizes the compatibility query:
- 404 SESSION_NOT_FOUND -> sessionPresence=ABSENT
- 200 AVAILABLE or 200 UNAVAILABLE -> sessionPresence=PRESENT
- transport/auth/indeterminate failures -> sessionPresence=UNKNOWN

This Predicate passes only for the explicit business assertion that the context
is absent, selecting the initial-creation path. It does not prove establishment.
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
            "reasonCode": "SMF_SESSION_CONTEXT_ENTRY_EVIDENCE_MISSING",
            "evidenceUsed": [],
        }

    observation = input["sessionContext"]
    presence = observation["sessionPresence"]

    if presence == "ABSENT":
        return {
            "result": "PASS",
            "reasonCode": "SMF_SESSION_CONTEXT_CONFIRMED_ABSENT",
            "evidenceUsed": evidence_refs,
        }

    if presence == "PRESENT":
        return {
            "result": "FAIL",
            "reasonCode": "SMF_SESSION_CONTEXT_ALREADY_PRESENT",
            "evidenceUsed": evidence_refs,
        }

    return {
        "result": "UNKNOWN",
        "reasonCode": "SMF_SESSION_CONTEXT_PRESENCE_UNKNOWN",
        "evidenceUsed": evidence_refs,
    }
