#!/usr/bin/env python3
"""Validate the documented IngressCatalog example against its structural schema."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/design/integration-ingress-operation-contract-vnext.zh-CN.md"
SCHEMA = ROOT / "docs/design/schemas/ingresscatalog.v1alpha1.schema.json"
DURATION = re.compile(
    r"P(?:(?P<days>[1-9][0-9]*)D)?"
    r"(?:T(?:(?P<hours>[1-9][0-9]*)H)?"
    r"(?:(?P<minutes>[1-9][0-9]*)M)?"
    r"(?:(?P<seconds>[1-9][0-9]*)S)?)?"
)


def load_example() -> dict:
    text = DOC.read_text(encoding="utf-8")
    blocks = re.findall(r"~~~yaml\s*\n(.*?)\n~~~", text, flags=re.DOTALL)
    candidates = [block for block in blocks if "id: nsmf-pdusession.update-sm-context" in block]
    if len(candidates) != 1:
        raise SystemExit(f"expected exactly one IngressCatalog YAML example, found {len(candidates)}")
    value = yaml.safe_load(candidates[0])
    if not isinstance(value, dict):
        raise SystemExit("IngressCatalog example must be a YAML mapping")
    return value


def fixed_duration_seconds(value: str, label: str) -> int:
    match = DURATION.fullmatch(value)
    if not match:
        raise SystemExit(f"{label}: invalid positive fixed duration: {value!r}")
    parts = {key: int(part) if part else 0 for key, part in match.groupdict().items()}
    if not any(parts.values()):
        raise SystemExit(f"{label}: duration must be greater than zero")
    if "T" in value and not any(parts[key] for key in ("hours", "minutes", "seconds")):
        raise SystemExit(f"{label}: T must be followed by a time component")
    return parts["days"] * 86400 + parts["hours"] * 3600 + parts["minutes"] * 60 + parts["seconds"]


def unique(values: list, label: str) -> None:
    encoded = [json.dumps(value, sort_keys=True, separators=(",", ":")) for value in values]
    if len(encoded) != len(set(encoded)):
        raise SystemExit(f"{label}: duplicate values are not allowed")


def validate_semantics(catalog: dict) -> None:
    operations = catalog["spec"]["operations"]
    for operation in operations:
        op_id = operation["id"]
        if operation["security"]["authenticatedPeerType"] != operation["event"]["source"]:
            raise SystemExit(f"{op_id}: authenticatedPeerType must equal event.source")

        request = operation["request"]
        request_max = request["maxBytes"]
        binary_max = request.get("binaryContent", {}).get("maxBytes")
        if binary_max is not None and binary_max > request_max:
            raise SystemExit(f"{op_id}: binaryContent.maxBytes exceeds request.maxBytes")
        accepted = request["acceptedMediaTypes"]
        source_types = [item["mediaType"] for item in request["sourceSchemas"]]
        representations = request["normalization"]["representations"]
        representation_types = [item["mediaType"] for item in representations]
        for label, values in (
            ("sourceSchemas", source_types),
            ("normalization.representations", representation_types),
        ):
            if len(values) != len(set(values)) or set(values) != set(accepted):
                raise SystemExit(
                    f"{op_id}: {label} media types must match acceptedMediaTypes exactly once"
                )

        for representation in representations:
            parts = {part["name"]: part for part in representation.get("parts", [])}
            if len(parts) != len(representation.get("parts", [])):
                raise SystemExit(f"{op_id}: duplicate multipart part name")
            for part in parts.values():
                if part["maxBytes"] > request_max:
                    raise SystemExit(f"{op_id}: multipart part maxBytes exceeds request.maxBytes")
                if part["kind"] == "binary" and binary_max is not None and part["maxBytes"] > binary_max:
                    raise SystemExit(f"{op_id}: binary part maxBytes exceeds binaryContent.maxBytes")
            targets = [mapping["target"] for mapping in representation["mappings"]]
            unique(targets, f"{op_id}: duplicate normalization target")
            for mapping in representation["mappings"]:
                source = mapping["source"]
                kind = source["kind"]
                if kind in ("multipart-json", "multipart-binary"):
                    part = parts.get(source["part"])
                    if part is None:
                        raise SystemExit(f"{op_id}: mapping references an undeclared multipart part")
                    expected_kind = "json" if kind == "multipart-json" else "binary"
                    if part["kind"] != expected_kind:
                        raise SystemExit(f"{op_id}: multipart mapping kind does not match declared part")
                if mapping["transform"] == "binary-content-ref" and kind != "multipart-binary":
                    raise SystemExit(f"{op_id}: binary-content-ref requires a multipart-binary source")

        correlation = operation["correlation"]
        key_fields = correlation["keyFields"]
        key_paths = [field["requestPath"] for field in key_fields]
        unique(key_paths, f"{op_id}: duplicate correlation requestPath")
        stale = correlation["staleDelivery"]
        if stale["strategy"] == "wire-discriminator":
            if stale["discriminatorPath"] not in key_paths:
                raise SystemExit(f"{op_id}: wire discriminator must be included in correlation keyFields")
        else:
            if stale["resourceKey"] not in key_paths:
                raise SystemExit(f"{op_id}: single-flight resourceKey must be included in correlation keyFields")
            durations = [
                stale["maximumLateArrival"],
                stale["clockSkewAllowance"],
                stale["tombstoneRetention"],
            ]
            # The prose example deliberately uses explicit placeholders until a trusted
            # protocol/deployment guarantee supplies real values.
            placeholders = [value.startswith("<") and value.endswith(">") for value in durations]
            if any(placeholders) and not all(placeholders):
                raise SystemExit(f"{op_id}: tombstone durations must be all concrete or all explicit placeholders")
            if not any(placeholders):
                maximum_late = fixed_duration_seconds(durations[0], "maximumLateArrival")
                skew = fixed_duration_seconds(durations[1], "clockSkewAllowance")
                retention = fixed_duration_seconds(durations[2], "tombstoneRetention")
                if retention < maximum_late + skew:
                    raise SystemExit(f"{op_id}: tombstoneRetention is shorter than maximumLateArrival + clockSkewAllowance")

        arming = operation["arming"]
        expected_keys = set(key_paths)
        if arming["start"]["allowed"]:
            bindings = arming["start"]["bindings"]
            actual = [binding["requestKey"] for binding in bindings]
            unique(actual, f"{op_id}: duplicate start binding requestKey")
            if set(actual) != expected_keys:
                raise SystemExit(f"{op_id}: start bindings must cover every correlation key exactly once")
        trigger_ids = []
        for trigger in arming["triggers"]:
            identity = trigger["operation"]
            trigger_ids.append((identity["packageId"], identity["owner"], identity["kind"], identity["id"]))
            actual = [binding["requestKey"] for binding in trigger["bindings"]]
            unique(actual, f"{op_id}: duplicate trigger binding requestKey")
            if set(actual) != expected_keys:
                raise SystemExit(f"{op_id}: each trigger must bind every correlation key exactly once")
        unique(trigger_ids, f"{op_id}: duplicate triggering Operation identity")

        response = operation["response"]
        if response["mode"] == "paired":
            dispositions = response["dispositions"]
            ids = [item["id"] for item in dispositions]
            statuses = [item["status"] for item in dispositions]
            unique(ids, f"{op_id}: duplicate response disposition id")
            unique(statuses, f"{op_id}: duplicate response HTTP status")
            result = response.get("result")
            if result:
                declared = set(ids)
                body_by_id = {item["id"]: item["body"] for item in dispositions}
                mappings = result.get("mappings", [])
                mapped = {item["dispositionId"] for item in mappings}
                cases = result.get("dispositionSelector", {}).get("cases", [])
                selected = {item["dispositionId"] for item in cases}
                unique([item["value"] for item in cases], f"{op_id}: duplicate disposition selector value")
                if not mapped <= declared or not selected <= declared:
                    raise SystemExit(f"{op_id}: response mapping/selector references unknown disposition")
                if len(dispositions) > 1 and selected != declared:
                    raise SystemExit(f"{op_id}: disposition selector must cover every disposition exactly once")
                if any(body_by_id[item] != "required" for item in mapped):
                    raise SystemExit(f"{op_id}: bodyless disposition must not declare a response-body mapping")
                if any(item["body"] == "required" and item["id"] not in mapped for item in dispositions):
                    raise SystemExit(f"{op_id}: body-bearing disposition has no response mapping")
                for disposition_id in declared:
                    targets = [item["to"] for item in mappings if item["dispositionId"] == disposition_id]
                    unique(targets, f"{op_id}: duplicate response mapping target for {disposition_id}")
            elif any(item["body"] == "required" for item in dispositions) or len(dispositions) > 1:
                raise SystemExit(f"{op_id}: body-bearing or multiple dispositions require a typed response result")


def validate_3gpp_reference_example(catalog: dict) -> None:
    operation = catalog["spec"]["operations"][0]
    if operation["id"] != "nsmf-pdusession.update-sm-context":
        raise SystemExit("expected the documented UpdateSMContext reference operation")
    if operation["event"] != {
        "source": "AMF",
        "service": "Nsmf_PDUSession",
        "operation": "UpdateSMContext",
    }:
        raise SystemExit("UpdateSMContext event identity does not match the 3GPP reference")
    openapi = operation["protocol"]["openapi"]
    if (openapi["method"], openapi["path"], openapi["operationId"]) != (
        "POST",
        "/sm-contexts/{smContextRef}/modify",
        "UpdateSmContext",
    ):
        raise SystemExit("UpdateSMContext OpenAPI method/path/operationId mismatch")

    multipart = next(
        item for item in operation["request"]["normalization"]["representations"]
        if item["mediaType"] == "multipart/related"
    )
    part_names = {part["name"] for part in multipart["parts"]}
    required_parts = {"jsonData", "binaryDataN1SmMessage", "binaryDataN2SmInformation"}
    if not required_parts <= part_names:
        raise SystemExit("UpdateSMContext multipart part names do not match the 3GPP OpenAPI reference")

    normalized_targets = {item["target"] for item in multipart["mappings"]}
    if not {"/n1SmMessage", "/n2SmInformation"} <= normalized_targets:
        raise SystemExit("UpdateSMContext binary parts are not mapped to normalized business fields")

    response = operation["response"]
    status_by_id = {item["id"]: item["status"] for item in response["dispositions"]}
    if status_by_id != {
        "update-with-json-cause": 200,
        "update-completed-no-content": 204,
    }:
        raise SystemExit("UpdateSMContext success response dispositions must be 200 and 204")
    mappings = response["result"]["mappings"]
    if not any(item["from"] == "/cause" and item["to"] == "/cause" for item in mappings):
        raise SystemExit("UpdateSMContext response mapping must use SmContextUpdatedData.cause")


def expect_schema_failure(validator: Draft202012Validator, value: dict, label: str) -> None:
    if validator.is_valid(value):
        raise SystemExit(f"negative fixture was unexpectedly accepted by schema: {label}")


def expect_semantic_failure(value: dict, label: str) -> None:
    try:
        validate_semantics(value)
    except SystemExit:
        return
    raise SystemExit(f"negative fixture was unexpectedly accepted by semantic checks: {label}")


def validate_negative_cases(schema: dict, example: dict) -> None:
    validator = Draft202012Validator(schema)

    missing_adapter = copy.deepcopy(example)
    del missing_adapter["spec"]["operations"][0]["adapter"]
    expect_schema_failure(validator, missing_adapter, "missing adapter identity")

    invalid_api_version = copy.deepcopy(example)
    invalid_api_version["spec"]["operations"][0]["protocol"]["apiUriVersion"] = 1
    expect_schema_failure(validator, invalid_api_version, "non-string apiUriVersion")

    missing_binary_policy = copy.deepcopy(example)
    del missing_binary_policy["spec"]["operations"][0]["request"]["binaryContent"]
    expect_schema_failure(validator, missing_binary_policy, "missing binary-content policy")

    missing_request_limit = copy.deepcopy(example)
    del missing_request_limit["spec"]["operations"][0]["request"]["maxBytes"]
    expect_schema_failure(validator, missing_request_limit, "missing total request byte limit")

    missing_part_limit = copy.deepcopy(example)
    del missing_part_limit["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["parts"][0]["maxBytes"]
    expect_schema_failure(validator, missing_part_limit, "missing multipart part byte limit")

    media_type_with_parameters = copy.deepcopy(example)
    media_type_with_parameters["spec"]["operations"][0]["request"]["acceptedMediaTypes"][0] = "application/json; charset=utf-8"
    expect_schema_failure(validator, media_type_with_parameters, "media type essence must not contain parameters")

    multipart_response = copy.deepcopy(example)
    multipart_response["spec"]["operations"][0]["response"]["dispositions"][0]["mediaType"] = "multipart/related"
    expect_schema_failure(validator, multipart_response, "v1alpha1 response body representation is JSON-only")

    duplicate_status = copy.deepcopy(example)
    dispositions = duplicate_status["spec"]["operations"][0]["response"]["dispositions"]
    dispositions[1]["status"] = dispositions[0]["status"]
    expect_semantic_failure(duplicate_status, "duplicate response HTTP status")

    incomplete_selector = copy.deepcopy(example)
    cases = incomplete_selector["spec"]["operations"][0]["response"]["result"]["dispositionSelector"]["cases"]
    cases.pop()
    expect_semantic_failure(incomplete_selector, "incomplete response disposition selector")

    duplicate_selector_value = copy.deepcopy(example)
    cases = duplicate_selector_value["spec"]["operations"][0]["response"]["result"]["dispositionSelector"]["cases"]
    cases[1]["value"] = cases[0]["value"]
    expect_semantic_failure(duplicate_selector_value, "duplicate response disposition selector value")

    bodyless_mapping = copy.deepcopy(example)
    mappings = bodyless_mapping["spec"]["operations"][0]["response"]["result"]["mappings"]
    invalid_mapping = copy.deepcopy(mappings[0])
    invalid_mapping["dispositionId"] = "update-completed-no-content"
    mappings.append(invalid_mapping)
    expect_semantic_failure(bodyless_mapping, "response mapping for bodyless disposition")

    missing_trigger_key = copy.deepcopy(example)
    missing_trigger_key["spec"]["operations"][0]["arming"]["triggers"][0]["bindings"].pop()
    expect_semantic_failure(missing_trigger_key, "trigger missing a correlation key binding")

    wrong_3gpp_part_name = copy.deepcopy(example)
    wrong_3gpp_part_name["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["parts"][1]["name"] = "n1SmMsg"
    expect_semantic_failure(wrong_3gpp_part_name, "incorrect 3GPP multipart part name")

    wrong_3gpp_response_path = copy.deepcopy(example)
    wrong_3gpp_response_path["spec"]["operations"][0]["response"]["result"]["mappings"][0]["from"] = "/smContextRef"
    expect_semantic_failure(wrong_3gpp_response_path, "incorrect SmContextUpdatedData response field")

    short_tombstone = copy.deepcopy(example)
    stale = short_tombstone["spec"]["operations"][0]["correlation"]["staleDelivery"]
    stale["maximumLateArrival"] = "PT30S"
    stale["clockSkewAllowance"] = "PT5S"
    stale["tombstoneRetention"] = "PT30S"
    expect_semantic_failure(short_tombstone, "tombstone shorter than late-arrival plus skew")

    zero_duration = copy.deepcopy(example)
    stale = zero_duration["spec"]["operations"][0]["correlation"]["staleDelivery"]
    stale["maximumLateArrival"] = "PT0S"
    stale["clockSkewAllowance"] = "PT5S"
    stale["tombstoneRetention"] = "PT35S"
    expect_semantic_failure(zero_duration, "zero maximumLateArrival duration")

    invalid_duration = copy.deepcopy(example)
    stale = invalid_duration["spec"]["operations"][0]["correlation"]["staleDelivery"]
    stale["maximumLateArrival"] = "P1DT"
    stale["clockSkewAllowance"] = "PT5S"
    stale["tombstoneRetention"] = "P1DT5S"
    expect_semantic_failure(invalid_duration, "duration with empty time component")


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    example = load_example()
    errors = sorted(
        Draft202012Validator(schema).iter_errors(example),
        key=lambda error: list(map(str, error.absolute_path)),
    )
    if errors:
        for error in errors:
            path = "/" + "/".join(map(str, error.absolute_path))
            print(f"{path}: {error.message}")
        raise SystemExit(f"IngressCatalog example failed with {len(errors)} schema error(s)")
    validate_semantics(example)
    validate_3gpp_reference_example(example)
    validate_negative_cases(schema, example)
    print("IngressCatalog Draft 2020-12 schema, cross-field checks and negative fixtures: PASS")


if __name__ == "__main__":
    main()
