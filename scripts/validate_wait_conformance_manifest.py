#!/usr/bin/env python3
"""Validate the machine-readable CA-SL v1alpha5 Wait conformance obligation register.

This checks register integrity only. SPECIFICATION_ONLY cases are not executable
Compiler/Host/Runtime/Integration fixtures and must never be reported as PASS.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "design" / "wait-conformance-v1alpha5.json"
SPEC = ROOT / "docs" / "skill-language-spec.v1alpha5.zh-CN.md"
EXPECTED_IDS = [f"EW-{index:03d}" for index in range(1, 37)]
WAIT_DIAGNOSTICS = {
    "WAIT_DECLARATION_INVALID",
    "WAIT_TIMEOUT_INVALID",
    "WAIT_INGRESS_EXPORT_NOT_FOUND",
    "WAIT_INGRESS_EXPORT_AMBIGUOUS",
    "WAIT_CORRELATION_BINDING_INVALID",
    "WAIT_TIMEOUT_ROUTE_INVALID",
    "WAIT_NODE_STAGE_REQUIRED",
    "WAIT_RESPONSE_BOUNDARY_INVALID",
    "WAIT_RESPONSE_MAPPING_INVALID",
}
INGRESS_DIAGNOSTICS = {
    "INGRESS_CATALOG_INVALID",
    "INGRESS_EXPORT_ID_DUPLICATE",
    "INGRESS_EVENT_SELECTOR_DUPLICATE",
    "INGRESS_PROTOCOL_ARTIFACT_INVALID",
    "INGRESS_PEER_PROFILE_REFERENCE_INVALID",
    "INGRESS_NORMALIZATION_INVALID",
    "INGRESS_CORRELATION_INVALID",
    "INGRESS_RESPONSE_CONTRACT_INVALID",
    "INGRESS_RESPONSE_MAPPING_INVALID",
}
INGRESS_REGISTRY_ID = "connectionagent.io/ingress-diagnostics/v1alpha1"

EXISTING_DIAGNOSTICS = {
    "SOURCE_NOT_AVAILABLE",
    "ENTRY_PRECONDITION_BYPASSED",
}
HOST_ADMISSION_DIAGNOSTICS = {"WAIT_DURATION_LIMIT_EXCEEDED"}
EXPECTED_MESSAGE_KEYS = {
    "wait.declaration.invalid",
    "wait.timeout.invalid",
    "wait.ingress.export.not_found",
    "wait.ingress.export.ambiguous",
    "wait.correlation.binding.invalid",
    "wait.timeout.route.invalid",
    "wait.node.stage_required",
    "wait.response.boundary.invalid",
    "wait.response.mapping.invalid",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != "connectionagent.io/wait-conformance-manifest/v1":
        fail("unexpected Wait conformance manifest schemaVersion")
    if manifest.get("languageTarget") != "connectionagent.io/v1alpha5":
        fail("manifest languageTarget must be connectionagent.io/v1alpha5")
    if manifest.get("status") != "NORMATIVE_TEST_OBLIGATIONS_NOT_EXECUTED":
        fail("manifest must not claim execution or PASS")
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        fail("manifest cases must be an array")
    ids = [case.get("id") for case in cases]
    if ids != EXPECTED_IDS:
        fail("manifest must contain EW-001 through EW-036 exactly once and in order")
    for case in cases:
        if case.get("fixtureStatus") != "SPECIFICATION_ONLY":
            fail(f"{case['id']} must remain SPECIFICATION_ONLY until executable evidence exists")
        if not case.get("layer") or not case.get("kind") or not case.get("scenario"):
            fail(f"{case['id']} is missing layer, kind or scenario")
        expected = case.get("expected")
        if not isinstance(expected, dict):
            fail(f"{case['id']} must declare an expected result object")
        diagnostics = expected.get("diagnostics")
        if diagnostics is not None:
            if set(expected) != {"diagnostics"} or not isinstance(diagnostics, list) or not diagnostics:
                fail(f"{case['id']} diagnostics must be the sole non-empty expected result")
            for code in diagnostics:
                if code not in WAIT_DIAGNOSTICS | EXISTING_DIAGNOSTICS:
                    fail(f"{case['id']} references an unregistered diagnostic: {code}")
        elif "variants" in expected:
            if set(expected) != {"variants"} or not isinstance(expected["variants"], list) or not expected["variants"]:
                fail(f"{case['id']} variants must be a non-empty expected result list")
            variant_ids = [variant.get("id") for variant in expected["variants"]]
            if len(variant_ids) != len(set(variant_ids)):
                fail(f"{case['id']} has duplicate expected variant IDs")
            for variant in expected["variants"]:
                codes = variant.get("diagnostics")
                if not isinstance(codes, list) or not codes:
                    fail(f"{case['id']} variant {variant.get('id')} requires exact diagnostics")
                for code in codes:
                    if code not in WAIT_DIAGNOSTICS | EXISTING_DIAGNOSTICS:
                        fail(f"{case['id']} variant references an unregistered diagnostic: {code}")
        elif "hostDiagnostic" in expected:
            if set(expected) != {"disposition", "hostDiagnostic"}:
                fail(f"{case['id']} host admission expectation has unexpected fields")
            if expected.get("hostDiagnostic") not in HOST_ADMISSION_DIAGNOSTICS or not isinstance(expected.get("disposition"), str):
                fail(f"{case['id']} references an unregistered Host admission diagnostic")
        elif set(expected) == {"disposition"} and isinstance(expected.get("disposition"), str):
            pass
        else:
            fail(f"{case['id']} has an unsupported expected result shape")

    spec = SPEC.read_text(encoding="utf-8")
    for case_id in EXPECTED_IDS:
        if spec.count(case_id) < 1:
            fail(f"{case_id} is missing from the single-file normative specification")
    for message_key in EXPECTED_MESSAGE_KEYS:
        if message_key not in spec:
            fail(f"normative diagnostic message key is missing: {message_key}")
    for code in INGRESS_DIAGNOSTICS:
        rows = [line for line in spec.splitlines() if line.startswith("| " + code + " |")]
        if len(rows) != 1:
            fail(f"{code} must have exactly one Appendix H.1 identity row")
        if "| C_STATIC | Compiler ERROR | 是 |" not in rows[0]:
            fail(f"{code} must be C_STATIC / ERROR / build-blocking in Appendix H.1")
        if "ingress-diagnostics/v1alpha1" not in rows[0]:
            fail(f"{code} must identify its versioned registry in Appendix H.1")
    if INGRESS_REGISTRY_ID not in spec:
        fail("versioned Ingress diagnostic registry ID is missing from Appendix H")
    if "116 个唯一 Code、117 条唯一" not in spec:
        fail("Appendix H combined diagnostic inventory count is inconsistent")
    print("Wait conformance manifest integrity: PASS (36 Wait obligations; 9 Ingress identities indexed; execution NOT_RUN)")


if __name__ == "__main__":
    main()
