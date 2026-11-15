"""Select policy inputs from a verified UDM subscription (no Owner authority)."""
from __future__ import annotations
from typing import Literal, NotRequired, TypedDict


class Ambr(TypedDict):
    uplink: str
    downlink: str


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


class SubscriptionData(TypedDict):
    sessionAmbr: Ambr
    defaultQos: InputDefaultQos


class SubscriptionSource(TypedDict):
    transactionRef: str
    requestRef: str
    fabricRecordRef: str
    fabricRecordDigest: str


class PolicyInput(TypedDict):
    subscriptionData: SubscriptionData
    subscriptionSource: SubscriptionSource


class PolicyOutput(TypedDict):
    ambr: Ambr
    defaultQos: OutputDefaultQos
    subscriptionSource: SubscriptionSource


def main(input: PolicyInput) -> PolicyOutput:
    subscription = input["subscriptionData"]
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
        "subscriptionSource": input["subscriptionSource"],
    }
