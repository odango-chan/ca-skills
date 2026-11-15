"""Validate Owner-provided UDM subscription and choose the explicit IPv4/SSC1 profile.

This pure CA-SL v1alpha4 Script cannot establish provenance by itself.
The UDM Result/Schema/Evidence must be linked and verified independently by Owner.
"""
from __future__ import annotations
from typing import Annotated, Literal, NotRequired, TypedDict


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


class Arp(TypedDict):
    priorityLevel: int
    preemptCap: Literal["MAY_PREEMPT", "NOT_PREEMPT"]
    preemptVuln: Literal["PREEMPTABLE", "NOT_PREEMPTABLE"]


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


class SubscriptionSource(TypedDict):
    transactionRef: Annotated[str, {"minLength": 1}]
    requestRef: Annotated[str, {"minLength": 1}]
    fabricRecordRef: Annotated[str, {"minLength": 1}]
    fabricRecordDigest: Annotated[str, {"minLength": 1}]


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


class SelectionInput(TypedDict):
    dnn: str
    sNssai: SNssai
    requestedPduSessionType: str
    requestedSscMode: int
    udmResult: UdmReadResult


class SelectionOutput(TypedDict):
    dnn: str
    sNssai: SNssai
    pduSessionType: Literal["IPV4"]
    sscMode: Literal[1]
    subscriptionData: SubscriptionData
    subscriptionSource: SubscriptionSource


def main(input: SelectionInput) -> SelectionOutput:
    result = input["udmResult"]
    if (result["selection"] != "MATCHED" or result["httpStatus"] != 200
            or result["networkOutcome"] != "HTTP_RESPONSE"
            or result["responseOrigin"] != "TARGET_SERVICE_VIA_SCP"
            or result["captureComplete"] is not True):
        raise ValueError("UDM response was not completely captured from the selected target")
    if input["requestedPduSessionType"] != "IPV4" or input["requestedSscMode"] != 1:
        raise ValueError("unsupported decoded UE request")
    subscription = result["subscription"]
    if subscription["dnn"] != input["dnn"] or subscription["sNssai"] != input["sNssai"]:
        raise ValueError("subscription is not for the admitted DNN and slice")
    session_types = subscription["pduSessionTypes"]
    ssc_modes = subscription["sscModes"]
    allowed_types = session_types.get("allowedSessionTypes", [session_types["defaultSessionType"]])
    allowed_modes = ssc_modes.get("allowedSscModes", [ssc_modes["defaultSscMode"]])
    # The subscribed default SSC1 is sufficient even when the optional
    # allowedSscModes list is present and does not repeat the default.
    if "IPV4" not in allowed_types or (ssc_modes["defaultSscMode"] != 1 and 1 not in allowed_modes):
        raise ValueError("subscription does not authorize IPv4/SSC1")
    return {
        "dnn": input["dnn"],
        "sNssai": input["sNssai"],
        "pduSessionType": "IPV4",
        "sscMode": 1,
        "subscriptionData": subscription,
        "subscriptionSource": {
            "transactionRef": result["transactionRef"],
            "requestRef": result["requestRef"],
            "fabricRecordRef": result["fabricRecordRef"],
            "fabricRecordDigest": result["fabricRecordDigest"],
        },
    }
