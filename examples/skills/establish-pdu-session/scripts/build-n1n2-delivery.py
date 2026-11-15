"""Select the exact already prepared N1/N2 artifact, never send it."""
from __future__ import annotations
from typing import Literal, TypedDict


class PreparedResponse(TypedDict):
    profileRef: Literal["createdsession-n1n2-sm@0.1.0"]
    responseArtifactRef: str
    artifactDigest: str
    nasDigest: str
    n2Digest: str
    validUntil: str


class DeliveryInput(TypedDict):
    preparedResponse: PreparedResponse
    operationContextRef: str
    policyResultRef: str
    pduSessionType: str


class DeliveryOutput(TypedDict):
    profileRef: Literal["createdsession-n1n2-sm@0.1.0"]
    responseArtifactRef: str
    artifactDigest: str
    nasDigest: str
    n2Digest: str
    validUntil: str
    operationContextRef: str
    policyResultRef: str


def main(input: DeliveryInput) -> DeliveryOutput:
    prepared = input["preparedResponse"]
    if input["pduSessionType"] != "IPV4":
        raise ValueError("admitted N1/N2 profile only supports IPv4")
    if (not prepared["responseArtifactRef"] or not prepared["artifactDigest"]
            or not prepared["nasDigest"] or not prepared["n2Digest"]):
        raise ValueError("missing prepared artifact identity or verified digests")
    return {
        "profileRef": prepared["profileRef"],
        "responseArtifactRef": prepared["responseArtifactRef"],
        "artifactDigest": prepared["artifactDigest"],
        "nasDigest": prepared["nasDigest"],
        "n2Digest": prepared["n2Digest"],
        "validUntil": prepared["validUntil"],
        "operationContextRef": input["operationContextRef"],
        "policyResultRef": input["policyResultRef"],
    }
