#!/usr/bin/env python3
"""Validate the IngressCatalog v1alpha1 diagnostic registry contract.

This verifies registry metadata and cross-document identity consistency. It
does not execute a CA-SL Compiler or prove product conformance.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/design/ingress-diagnostic-registry-v1alpha1.json"
REGISTRY_DOC = ROOT / "docs/design/ingress-diagnostic-registry-v1alpha1.md"
CONTRACT = ROOT / "docs/design/integration-ingress-operation-contract-vnext.zh-CN.md"
CATALOG_SCHEMA = ROOT / "docs/design/schemas/ingresscatalog.v1alpha1.schema.json"

EXPECTED = [
    ("INGRESS_CATALOG_INVALID", 10, "ingress.catalog.invalid", ("IN-055",)),
    ("INGRESS_EXPORT_ID_DUPLICATE", 20, "ingress.export.id.duplicate", ("IN-005",)),
    ("INGRESS_EVENT_SELECTOR_DUPLICATE", 21, "ingress.event.selector.duplicate", ("IN-056",)),
    ("INGRESS_PROTOCOL_ARTIFACT_INVALID", 30, "ingress.protocol.artifact.invalid", ("IN-007", "IN-057")),
    ("INGRESS_PEER_PROFILE_REFERENCE_INVALID", 40, "ingress.peer.profile.reference.invalid", ("IN-058",)),
    ("INGRESS_NORMALIZATION_INVALID", 50, "ingress.normalization.invalid", ("IN-014", "IN-015", "IN-039", "IN-059")),
    ("INGRESS_BINARY_CONTENT_LIFECYCLE_INVALID", 55, "ingress.binary.content.lifecycle.invalid", ("IN-016", "IN-042")),
    ("INGRESS_CORRELATION_INVALID", 60, "ingress.correlation.invalid", ("IN-023", "IN-046", "IN-047", "IN-060")),
    ("INGRESS_RESPONSE_CONTRACT_INVALID", 70, "ingress.response.contract.invalid", ("IN-027", "IN-033", "IN-040", "IN-061")),
    ("INGRESS_RESPONSE_MAPPING_INVALID", 80, "ingress.response.mapping.invalid", ("IN-032", "IN-044", "IN-045", "IN-062")),
]


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry.get("schemaVersion") != "connectionagent.io/diagnostic-registry/v1":
        fail("unexpected diagnostic registry schemaVersion")
    if registry.get("registryId") != "connectionagent.io/ingress-diagnostics/v1alpha1":
        fail("unexpected Ingress diagnostic registryId")
    if registry.get("status") != "NORMATIVE_FROZEN":
        fail("registry status must be NORMATIVE_FROZEN")
    applies_to = registry.get("appliesTo", {})
    if applies_to != {
        "apiVersion": "connectionagent.io/ingresscatalog/v1alpha1",
        "kind": "IngressCatalog",
    }:
        fail("registry appliesTo must pin IngressCatalog v1alpha1")
    defaults = registry.get("defaults", {})
    if defaults != {"phase": "C_STATIC", "severity": "ERROR", "blocksBuild": True}:
        fail("all Ingress registry entries must be C_STATIC / ERROR / build-blocking")

    entries = registry.get("entries")
    if not isinstance(entries, list):
        fail("registry entries must be an array")
    actual = [
        (
            entry.get("code"),
            entry.get("precedence"),
            entry.get("messageKey"),
            tuple(entry.get("conformanceCases", [])),
        )
        for entry in entries
    ]
    if actual != EXPECTED:
        fail("registry must contain the exact ten diagnostic identities, order and precedence")
    if len({entry["code"] for entry in entries}) != len(entries):
        fail("duplicate diagnostic Code")
    if len({entry["precedence"] for entry in entries}) != len(entries):
        fail("duplicate diagnostic precedence")

    location = registry.get("sourceLocation", {})
    if location.get("fields") != ["dependencyAlias", "snapshotPath", "jsonPointer"]:
        fail("source location must preserve dependencyAlias, snapshotPath and jsonPointer")
    if location.get("jsonPointerDialect") != "RFC6901" or location.get("fragmentPrefix") != "#":
        fail("source locations must use canonical RFC 6901 fragment pointers")

    envelope = registry.get("envelope", {})
    required = set(envelope.get("requiredFields", []))
    if not {
        "code", "phase", "severity", "registryId", "messageKey", "sourceLocation"
    } <= required:
        fail("Compiler Diagnostic[] logical envelope is missing required provenance fields")
    if envelope.get("forIngressEntries") != {
        "phase": "C_STATIC", "severity": "ERROR", "blocksBuild": True
    }:
        fail("Compiler envelope mapping must preserve static ERROR/build-blocking semantics")

    for entry in entries:
        if entry.get("phase") != "C_STATIC" or entry.get("severity") != "ERROR" or entry.get("blocksBuild") is not True:
            fail(f"{entry['code']} has incorrect phase, severity or blocking behavior")
        if not entry.get("trigger") or not entry.get("messageTemplate"):
            fail(f"{entry['code']} is missing trigger or canonical message template")
        pointers = entry.get("sourceLocation", {})
        primary = pointers.get("primaryPointerTemplate")
        related = pointers.get("relatedPointerTemplate")
        if not isinstance(primary, list) or not primary:
            fail(f"{entry['code']} is missing primaryPointerTemplate")
        if not isinstance(related, list):
            fail(f"{entry['code']} is missing relatedPointerTemplate")
        for pointer in primary:
            if not isinstance(pointer, str) or not pointer.startswith("#"):
                fail(f"{entry['code']} has a non-canonical primary RFC 6901 pointer template")
        for pointer in related:
            if not isinstance(pointer, str) or not (pointer.startswith("#") or "}#" in pointer):
                fail(f"{entry['code']} has a non-canonical related source pointer template")

    catalog_schema = json.loads(CATALOG_SCHEMA.read_text(encoding="utf-8"))
    if catalog_schema.get("properties", {}).get("apiVersion", {}).get("const") != applies_to["apiVersion"]:
        fail("IngressCatalog JSON Schema apiVersion and diagnostic registry target disagree")

    registry_doc = REGISTRY_DOC.read_text(encoding="utf-8")
    contract_doc = CONTRACT.read_text(encoding="utf-8")
    for code, _, message_key, conformance_cases in EXPECTED:
        if code not in registry_doc or code not in contract_doc:
            fail(f"{code} is missing from the registry document or Ingress contract §13")
        if message_key not in registry_doc:
            fail(f"{message_key} is missing from the registry document")
        for case_id in conformance_cases:
            rows = [
                line for line in contract_doc.splitlines()
                if line.startswith("| " + case_id + " |")
            ]
            if len(rows) != 1 or code not in rows[0]:
                fail(f"{code} must be explicitly assigned by exact conformance row {case_id}")
    if registry["registryId"] not in registry_doc or registry["registryId"] not in contract_doc:
        fail("versioned registry ID is not cross-referenced by both normative documents")

    print("Ingress diagnostic registry integrity: PASS (10 identities; product execution NOT_RUN)")


if __name__ == "__main__":
    main()
