"""Pure, deterministic local normalization of an admitted initial PDU request.

CA-SL v1alpha4 Procedure Script: no I/O, ambient Context, randomness or time.
Owner authorization and input identity checks remain outside this Script.
"""
from __future__ import annotations
from typing import TypedDict


class SelectionInput(TypedDict):
    dnn: str
    sst: int
    pduType: str
    sscMode: int


class SelectionOutput(TypedDict):
    dnn: str
    sst: int
    pduType: str
    sscMode: int


def main(input: SelectionInput) -> SelectionOutput:
    if not input["dnn"] or not 0 <= input["sst"] <= 255:
        raise ValueError("unsupported request attributes")
    if input["pduType"] != "IPV4" or input["sscMode"] != 1:
        raise ValueError("example only supports IPv4 and SSC mode 1")
    return {
        "dnn": input["dnn"],
        "sst": input["sst"],
        "pduType": input["pduType"],
        "sscMode": input["sscMode"],
    }
