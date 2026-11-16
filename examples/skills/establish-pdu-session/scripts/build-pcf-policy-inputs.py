"""Build the SM Policy Association inputs from the Step 4 UDM result.

This is deterministic local business-data projection. It does not call an Owner,
authorize subscription data, or create Evidence.
"""
from __future__ import annotations
from typing import Annotated, Literal, NotRequired, TypedDict


class Ambr(TypedDict):
    uplink: Annotated[str, {"minLength": 1}]
    downlink: Annotated[str, {"minLength": 1}]


class Arp(TypedDict):
    priorityLevel: int
    preemptCap: Literal["MAY_PREEMPT", "NOT_PREEMPT"]
    preemptVuln: Literal["PREEMPTABLE", "NOT_PREEMPTABLE"]


class InputDefaultQos(TypedDict):
    fiveQi: int
    arp: Arp
    priorityLevel: NotRequired[int]


OutputDefaultQos = TypedDict(
    "OutputDefaultQos",
    {"5qi": int, "arp": Arp, "priorityLevel": NotRequired[int]},
)


class SNssai(TypedDict):
    sst: Annotated[int, {"minimum": 0, "maximum": 255}]
    sd: NotRequired[Annotated[int, {"minimum": 0, "maximum": 16777214}]]


class PduSessionTypes(TypedDict):
    defaultSessionType: Literal["IPV4", "IPV6", "IPV4V6"]
    allowedSessionTypes: NotRequired[list[Literal["IPV4", "IPV6", "IPV4V6"]]]


class SscModes(TypedDict):
    defaultSscMode: int
    allowedSscModes: NotRequired[list[int]]


class SessionAmbr(TypedDict):
    uplink: Annotated[str, {"minLength": 1}]
    downlink: Annotated[str, {"minLength": 1}]


class DefaultQos(TypedDict):
    fiveQi: int
    arp: Arp
    priorityLevel: NotRequired[int]


class SubscriptionData(TypedDict):
    sNssai: SNssai
    dnn: Annotated[str, {"minLength": 1}]
    pduSessionTypes: PduSessionTypes
    sscModes: SscModes
    sessionAmbr: SessionAmbr
    defaultQos: DefaultQos


class UdmReadResult(TypedDict):
    selection: str
    httpStatus: int
    networkOutcome: str
    responseOrigin: str
    captureComplete: bool
    transactionRef: str
    requestRef: str
    fabricRecordRef: str
    fabricRecordDigest: str
    subscription: SubscriptionData


class SubscriptionSource(TypedDict):
    transactionRef: Annotated[str, {"minLength": 1}]
    requestRef: Annotated[str, {"minLength": 1}]
    fabricRecordRef: Annotated[str, {"minLength": 1}]
    fabricRecordDigest: Annotated[str, {"minLength": 1}]


class PolicyInput(TypedDict):
    udmResult: UdmReadResult


class PolicyOutput(TypedDict):
    ambr: Ambr
    defaultQos: OutputDefaultQos
    subscriptionSource: SubscriptionSource


def main(input: PolicyInput) -> PolicyOutput:
    result = input["udmResult"]
    subscription = result["subscription"]
    qos = subscription["defaultQos"]
    result_qos: OutputDefaultQos = {
        "5qi": qos["fiveQi"],
        "arp": qos["arp"],
    }
    priority = qos.get("priorityLevel")
    if priority is not None:
        result_qos["priorityLevel"] = priority
    return {
        "ambr": subscription["sessionAmbr"],
        "defaultQos": result_qos,
        "subscriptionSource": {
            "transactionRef": result["transactionRef"],
            "requestRef": result["requestRef"],
            "fabricRecordRef": result["fabricRecordRef"],
            "fabricRecordDigest": result["fabricRecordDigest"],
        },
    }
