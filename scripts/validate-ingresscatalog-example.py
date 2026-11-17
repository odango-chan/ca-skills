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
    unique([operation["id"] for operation in operations], "duplicate ingress export id")
    unique([operation["event"] for operation in operations], "duplicate ingress event selector")
    for operation in operations:
        op_id = operation["id"]
        if operation["security"]["authenticatedPeerType"] != operation["event"]["source"]:
            raise SystemExit(f"{op_id}: authenticatedPeerType must equal event.source")

        request = operation["request"]
        request_max = request["maxBytes"]
        binary_content = request.get("binaryContent")
        binary_max = binary_content.get("maxBytes") if binary_content else None
        if binary_max is not None and binary_max > request_max:
            raise SystemExit(f"{op_id}: binaryContent.maxBytes exceeds request.maxBytes")
        if binary_content:
            retention = binary_content["retention"]
            is_placeholder = retention.startswith("<") and retention.endswith(">")
            if not is_placeholder:
                fixed_duration_seconds(retention, f"{op_id}: binaryContent.retention")
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
                if kind == "multipart-binary":
                    content_id_reference = source.get("contentIdReference")
                    if content_id_reference:
                        reference_part = parts.get(content_id_reference["part"])
                        if reference_part is None or reference_part["kind"] != "json":
                            raise SystemExit(f"{op_id}: contentIdReference must point to a declared JSON part")
                    if operation["protocol"]["specification"] == "3GPP TS 29.502" and mapping["transform"] == "binary-content-ref" and not content_id_reference:
                        raise SystemExit(f"{op_id}: TS 29.502 binary-content-ref requires contentIdReference")
                if mapping["transform"] == "binary-content-ref" and kind != "multipart-binary":
                    raise SystemExit(f"{op_id}: binary-content-ref requires a multipart-binary source")

        correlation = operation["correlation"]
        key_fields = correlation["keyFields"]
        key_paths = [field["requestPath"] for field in key_fields]
        unique(key_paths, f"{op_id}: duplicate correlation requestPath")
        stale = correlation["staleDelivery"]
        duplicate_source = correlation["duplicate"]["identitySource"]
        duplicate_scope = correlation["duplicate"]["scope"]
        expected_scope = {
            "protocol-request-id": "protocol-defined",
            "trusted-gateway-request-id": "protocol-defined",
            "canonical-request-digest": "expected-ingress",
            "3gpp-sbi-idempotency-key": "target-nf",
        }[duplicate_source]
        if duplicate_scope != expected_scope:
            raise SystemExit(
                f"{op_id}: duplicate identity scope must be {expected_scope} for {duplicate_source}"
            )
        if stale["strategy"] == "wire-discriminator":
            discriminator = stale["discriminator"]
            if discriminator["kind"] == "authenticated-header-parameter":
                if duplicate_source != "3gpp-sbi-idempotency-key":
                    raise SystemExit(f"{op_id}: SBI idempotency-key discriminator must also be the duplicate identity source")
                if operation["protocol"]["specification"] == "3GPP TS 29.502" and (
                    discriminator["header"] != "3gpp-Sbi-Request-Info"
                    or discriminator["parameter"] != "idempotency-key"
                ):
                    raise SystemExit(f"{op_id}: TS 29.502 wire discriminator must be 3gpp-Sbi-Request-Info.idempotency-key")
            elif duplicate_source == "3gpp-sbi-idempotency-key":
                raise SystemExit(f"{op_id}: 3GPP SBI idempotency-key identity requires its authenticated header discriminator")
            elif operation["protocol"]["specification"] == "3GPP TS 29.502" and discriminator["kind"] == "normalized-request-path":
                raise SystemExit(f"{op_id}: UpdateSmContext defines no per-request normalized field suitable as a wire discriminator")
            durations = [
                stale["maximumLateArrival"],
                stale["clockSkewAllowance"],
                stale["discriminatorRetention"],
            ]
            placeholders = [value.startswith("<") and value.endswith(">") for value in durations]
            if any(placeholders) and not all(placeholders):
                raise SystemExit(f"{op_id}: wire discriminator retention durations must be all concrete or all explicit placeholders")
            if not any(placeholders):
                maximum_late = fixed_duration_seconds(durations[0], "maximumLateArrival")
                skew = fixed_duration_seconds(durations[1], "clockSkewAllowance")
                retention = fixed_duration_seconds(durations[2], "discriminatorRetention")
                if retention <= maximum_late + skew:
                    raise SystemExit(f"{op_id}: discriminatorRetention must be strictly greater than maximumLateArrival + clockSkewAllowance")
        else:
            if duplicate_source == "3gpp-sbi-idempotency-key":
                raise SystemExit(f"{op_id}: 3GPP SBI idempotency-key identity requires wire-discriminator strategy")
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
                if retention <= maximum_late + skew:
                    raise SystemExit(f"{op_id}: tombstoneRetention must be strictly greater than maximumLateArrival + clockSkewAllowance")

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
            representations_by_key = {}
            required_combinations = set()
            for disposition in dispositions:
                disposition_id = disposition["id"]
                representations = disposition.get("representations", [])
                if disposition["body"] == "none":
                    if representations:
                        raise SystemExit(f"{op_id}: bodyless disposition must not declare representations")
                    required_combinations.add((disposition_id, None))
                    continue
                representation_ids = [item["id"] for item in representations]
                unique(representation_ids, f"{op_id}: duplicate representation id for {disposition_id}")
                if not representations:
                    raise SystemExit(f"{op_id}: body-bearing disposition must declare representations")
                for representation in representations:
                    key = (disposition_id, representation["id"])
                    representations_by_key[key] = representation
                    required_combinations.add(key)
                    parts = representation.get("parts", [])
                    part_names = [part["name"] for part in parts]
                    unique(part_names, f"{op_id}: duplicate response part name")
                    if representation["mediaType"] == "multipart/related":
                        if not parts or parts[0]["name"] != representation["rootPart"] or parts[0]["kind"] != "json":
                            raise SystemExit(f"{op_id}: multipart response rootPart must be the first JSON part")
                        if not any(part["kind"] == "binary" for part in parts):
                            raise SystemExit(f"{op_id}: multipart response must declare at least one binary part")
                        if sum(part["maxBytes"] for part in parts) > representation["maxBytes"]:
                            raise SystemExit(f"{op_id}: multipart part byte limits exceed representation.maxBytes")
                    elif parts or "rootPart" in representation:
                        raise SystemExit(f"{op_id}: application/json response representation cannot declare multipart parts")
            result = response.get("result")
            multipart_representations = [
                representation
                for representation in representations_by_key.values()
                if representation["mediaType"] == "multipart/related"
            ]
            binary_policy = response.get("binaryContent")
            if multipart_representations and not binary_policy:
                raise SystemExit(f"{op_id}: multipart response requires response.binaryContent")
            if binary_policy:
                retention = binary_policy["retention"]
                if not (retention.startswith("<") and retention.endswith(">")):
                    fixed_duration_seconds(retention, f"{op_id}: response.binaryContent.retention")
                for representation in multipart_representations:
                    for part in representation["parts"]:
                        if part["kind"] == "binary" and part["maxBytes"] > binary_policy["maxBytes"]:
                            raise SystemExit(f"{op_id}: response binary part exceeds response.binaryContent.maxBytes")
            if result:
                mappings = result.get("mappings", [])
                mapping_pairs = [(item["dispositionId"], item["representationId"]) for item in mappings]
                if any(pair not in representations_by_key for pair in mapping_pairs):
                    raise SystemExit(f"{op_id}: response mapping references unknown disposition/representation")
                cases = result.get("dispositionSelector", {}).get("cases", [])
                unique([item["value"] for item in cases], f"{op_id}: duplicate disposition selector value")
                selected = set()
                for case in cases:
                    disposition_id = case["dispositionId"]
                    disposition = next((item for item in dispositions if item["id"] == disposition_id), None)
                    if disposition is None:
                        raise SystemExit(f"{op_id}: response selector references unknown disposition")
                    representation_id = case.get("representationId")
                    if disposition["body"] == "none":
                        if representation_id is not None:
                            raise SystemExit(f"{op_id}: bodyless disposition must not select a representation")
                        selected.add((disposition_id, None))
                    else:
                        if representation_id is None or (disposition_id, representation_id) not in representations_by_key:
                            raise SystemExit(f"{op_id}: body-bearing disposition must select an exact representation")
                        selected.add((disposition_id, representation_id))
                needs_selector = len(dispositions) > 1 or any(
                    len(item.get("representations", [])) > 1 for item in dispositions
                )
                if needs_selector and selected != required_combinations:
                    raise SystemExit(f"{op_id}: disposition selector must cover every disposition/representation combination exactly once")
                mapped_pairs = set(mapping_pairs)
                if any(pair not in mapped_pairs for pair in representations_by_key):
                    raise SystemExit(f"{op_id}: body-bearing response representation has no mapping")
                target_keys = []
                for mapping in mappings:
                    target = mapping["target"]
                    target_key = (
                        mapping["dispositionId"],
                        mapping["representationId"],
                        target["kind"],
                        target.get("part"),
                        target.get("pointer"),
                        json.dumps(target.get("contentIdField"), sort_keys=True),
                    )
                    target_keys.append(target_key)
                    if target["kind"] == "multipart-json":
                        representation = representations_by_key[(mapping["dispositionId"], mapping["representationId"])]
                        if representation["mediaType"] != "multipart/related" or target["part"] not in {
                            part["name"] for part in representation["parts"] if part["kind"] == "json"
                        }:
                            raise SystemExit(f"{op_id}: multipart-json target must reference a declared JSON part")
                    elif target["kind"] == "multipart-binary":
                        representation = representations_by_key[(mapping["dispositionId"], mapping["representationId"])]
                        part = next((part for part in representation.get("parts", []) if part["name"] == target["part"]), None)
                        content_id_field = target["contentIdField"]
                        if representation["mediaType"] != "multipart/related" or part is None or part["kind"] != "binary":
                            raise SystemExit(f"{op_id}: multipart-binary target must reference a declared binary part")
                        if content_id_field["part"] != representation["rootPart"] or not content_id_field["pointer"].endswith("/contentId"):
                            raise SystemExit(f"{op_id}: response Content-ID field must point to root RefToBinaryData.contentId")
                    elif target["kind"] == "json-body":
                        representation = representations_by_key[(mapping["dispositionId"], mapping["representationId"])]
                        if representation["mediaType"] != "application/json":
                            raise SystemExit(f"{op_id}: json-body target requires application/json representation")
                unique(target_keys, f"{op_id}: duplicate response mapping target")
                for pair, representation in representations_by_key.items():
                    if representation["mediaType"] == "multipart/related":
                        for part in representation["parts"]:
                            if part["kind"] == "binary":
                                matches = [
                                    item for item in mappings
                                    if (item["dispositionId"], item["representationId"]) == pair
                                    and item["target"]["kind"] == "multipart-binary"
                                    and item["target"]["part"] == part["name"]
                                ]
                                if len(matches) != 1:
                                    raise SystemExit(f"{op_id}: each multipart binary part must have exactly one mapping")
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
    if operation["protocol"]["specification"] != "3GPP TS 29.502" or operation["protocol"]["release"] != "19.5.0":
        raise SystemExit("UpdateSMContext reference must pin TS 29.502 V19.5.0")
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
    required_parts = {
        "jsonData",
        "binaryDataN1SmMessage",
        "binaryDataN2SmInformation",
        "binaryDataN2SmInformationExt1",
    }
    if not required_parts <= part_names:
        raise SystemExit("UpdateSMContext multipart part names do not match TS 29.502 V19.5.0")

    expected_binary_mappings = {
        "binaryDataN1SmMessage": ("/n1SmMsg/contentId", "/n1SmMessage"),
        "binaryDataN2SmInformation": ("/n2SmInfo/contentId", "/n2SmInformation"),
        "binaryDataN2SmInformationExt1": ("/n2SmInfoExt1/contentId", "/n2SmInformationExt1"),
    }
    mappings_by_part = {
        item["source"]["part"]: item
        for item in multipart["mappings"]
        if item["source"]["kind"] == "multipart-binary"
    }
    if set(mappings_by_part) != set(expected_binary_mappings):
        raise SystemExit("Every declared UpdateSMContext binary part must have exactly one normalized mapping")
    for part_name, (reference_pointer, target) in expected_binary_mappings.items():
        mapping = mappings_by_part[part_name]
        if mapping["source"].get("contentIdReference") != {"part": "jsonData", "pointer": reference_pointer}:
            raise SystemExit(f"{part_name} must be linked to jsonData {reference_pointer} by Content-ID")
        if mapping["target"] != target or mapping["transform"] != "binary-content-ref":
            raise SystemExit(f"{part_name} is not mapped to its typed immutable binary content reference")

    normalized_targets = {item["target"] for item in multipart["mappings"]}
    if not {"/n1SmMessage", "/n2SmInformation", "/n2SmInformationExt1"} <= normalized_targets:
        raise SystemExit("UpdateSMContext binary parts are not mapped to normalized business fields")

    if operation["protocol"]["apiUriVersion"] != "v1":
        raise SystemExit("UpdateSMContext API URI version must be v1")

    response = operation["response"]
    dispositions = {item["id"]: item for item in response["dispositions"]}
    status_by_id = {key: item["status"] for key, item in dispositions.items()}
    if status_by_id != {
        "update-completed": 200,
        "update-completed-no-content": 204,
    }:
        raise SystemExit("UpdateSMContext success response dispositions must be 200 and 204")
    json_response = next(item for item in dispositions["update-completed"]["representations"] if item["id"] == "json")
    multipart_response = next(item for item in dispositions["update-completed"]["representations"] if item["id"] == "multipart")
    bodyless_response = dispositions["update-completed-no-content"]
    if json_response["mediaType"] != "application/json":
        raise SystemExit("UpdateSMContext JSON representation must use application/json")
    if multipart_response["mediaType"] != "multipart/related" or multipart_response["rootPart"] != "jsonData":
        raise SystemExit("UpdateSMContext multipart response must use jsonData as its root part")
    response_part_list = multipart_response["parts"]
    response_parts = {part["name"]: part for part in response_part_list}
    expected_response_part_names = ["jsonData", "binaryDataN1SmMessage", "binaryDataN2SmInformation"]
    if [part["name"] for part in response_part_list] != expected_response_part_names:
        raise SystemExit("UpdateSMContext V19.5.0 multipart response parts must be unique and start with jsonData")
    if multipart_response["rootPart"] != "jsonData":
        raise SystemExit("UpdateSMContext multipart response rootPart must be jsonData")
    root_part = response_parts["jsonData"]
    if (
        root_part["kind"] != "json"
        or root_part["required"] is not True
        or root_part["mediaType"] != "application/json"
        or root_part["schemaRef"] != multipart_response["responseSchemaRef"]
        or root_part["schemaDigest"] != multipart_response["responseSchemaDigest"]
    ):
        raise SystemExit("UpdateSMContext multipart root JSON part must be first and use the exact response Schema and digest")
    if (
        json_response["responseSchemaRef"] != multipart_response["responseSchemaRef"]
        or json_response["responseSchemaDigest"] != multipart_response["responseSchemaDigest"]
    ):
        raise SystemExit("UpdateSMContext JSON and multipart representations must share the same response Schema and digest")
    if response_parts["binaryDataN1SmMessage"]["kind"] != "binary" or response_parts["binaryDataN1SmMessage"]["required"] is not False:
        raise SystemExit("UpdateSMContext N1 SM response part must be optional binary")
    if response_parts["binaryDataN1SmMessage"]["mediaType"] != "application/vnd.3gpp.5gnas":
        raise SystemExit("UpdateSMContext N1 SM response part media type mismatch")
    if response_parts["binaryDataN2SmInformation"]["kind"] != "binary" or response_parts["binaryDataN2SmInformation"]["required"] is not False:
        raise SystemExit("UpdateSMContext N2 SM response part must be optional binary")
    if response_parts["binaryDataN2SmInformation"]["mediaType"] != "application/vnd.3gpp.ngap":
        raise SystemExit("UpdateSMContext N2 SM response part media type mismatch")
    if bodyless_response["body"] != "none" or bodyless_response.get("representations"):
        raise SystemExit("UpdateSMContext 204 success response must be bodyless")
    binary_policy = response.get("binaryContent", {})
    if (
        binary_policy.get("access") != "integration-response-only"
        or binary_policy.get("immutable") is not True
        or binary_policy.get("maxBytes", 0) < max(response_parts[name]["maxBytes"] for name in expected_response_part_names[1:])
    ):
        raise SystemExit("UpdateSMContext multipart response requires bounded immutable Integration-only binary references")
    total_part_limit = sum(part["maxBytes"] for part in response_part_list)
    if multipart_response["maxBytes"] <= total_part_limit:
        raise SystemExit("UpdateSMContext multipart response maxBytes must leave room for MIME framing overhead")

    mappings = response["result"]["mappings"]
    expected_mappings = {
        ("json", "json-body", None, "/cause"): ("/cause", "identity"),
        ("multipart", "multipart-json", "jsonData", "/cause"): ("/cause", "identity"),
        ("multipart", "multipart-binary", "binaryDataN1SmMessage", None): ("/n1SmMessage", "binary-content-ref"),
        ("multipart", "multipart-binary", "binaryDataN2SmInformation", None): ("/n2SmInformation", "binary-content-ref"),
    }
    actual_mapping_keys = []
    for mapping in mappings:
        target = mapping["target"]
        key = (mapping["representationId"], target["kind"], target.get("part"), target.get("pointer"))
        actual_mapping_keys.append(key)
        if key not in expected_mappings:
            raise SystemExit(f"Unexpected UpdateSMContext response mapping target: {key}")
        expected_from, expected_transform = expected_mappings[key]
        if mapping["from"] != expected_from or mapping["transform"] != expected_transform:
            raise SystemExit(f"UpdateSMContext response mapping {key} must read {expected_from} using {expected_transform}")
        if target["kind"] == "multipart-binary":
            expected_pointer = {
                "binaryDataN1SmMessage": "/n1SmMsg/contentId",
                "binaryDataN2SmInformation": "/n2SmInfo/contentId",
            }[target["part"]]
            if target["contentIdField"] != {"part": "jsonData", "pointer": expected_pointer}:
                raise SystemExit(f"{target['part']} response part must be linked through {expected_pointer}")
    if len(actual_mapping_keys) != len(expected_mappings) or len(set(actual_mapping_keys)) != len(actual_mapping_keys):
        raise SystemExit("UpdateSMContext response mappings must cover every declared response field and binary part exactly once")

    selector = response["result"]["dispositionSelector"]
    if selector["sourcePath"] != "/responseRepresentation":
        raise SystemExit("UpdateSMContext response selector must read the typed responseRepresentation field")
    selected = {
        (item["value"], item["dispositionId"], item.get("representationId"))
        for item in selector["cases"]
    }
    if selected != {
        ("json", "update-completed", "json"),
        ("multipart", "update-completed", "multipart"),
        ("no-content", "update-completed-no-content", None),
    }:
        raise SystemExit("UpdateSMContext response selector must cover JSON, multipart and 204 bodyless outcomes")


def expect_schema_failure(validator: Draft202012Validator, value: dict, label: str) -> None:
    if validator.is_valid(value):
        raise SystemExit(f"negative fixture was unexpectedly accepted by schema: {label}")


def expect_semantic_failure(value: dict, label: str) -> None:
    try:
        validate_semantics(value)
    except SystemExit:
        return
    raise SystemExit(f"negative fixture was unexpectedly accepted by semantic checks: {label}")


def expect_protocol_failure(value: dict, label: str) -> None:
    try:
        validate_3gpp_reference_example(value)
    except SystemExit:
        return
    raise SystemExit(f"negative fixture was unexpectedly accepted by 3GPP protocol checks: {label}")


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

    non_multipart_parts = copy.deepcopy(example)
    non_multipart_parts["spec"]["operations"][0]["request"]["normalization"]["representations"][0]["parts"] = copy.deepcopy(
        non_multipart_parts["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["parts"]
    )
    expect_schema_failure(validator, non_multipart_parts, "multipart parts on application/json representation")

    missing_request_limit = copy.deepcopy(example)
    del missing_request_limit["spec"]["operations"][0]["request"]["maxBytes"]
    expect_schema_failure(validator, missing_request_limit, "missing total request byte limit")

    missing_part_limit = copy.deepcopy(example)
    del missing_part_limit["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["parts"][0]["maxBytes"]
    expect_schema_failure(validator, missing_part_limit, "missing multipart part byte limit")

    media_type_with_parameters = copy.deepcopy(example)
    media_type_with_parameters["spec"]["operations"][0]["request"]["acceptedMediaTypes"][0] = "application/json; charset=utf-8"
    expect_schema_failure(validator, media_type_with_parameters, "media type essence must not contain parameters")

    multipart_response_missing_parts = copy.deepcopy(example)
    multipart_response_missing_parts["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1].pop("parts")
    expect_schema_failure(validator, multipart_response_missing_parts, "multipart response missing root/parts declaration")

    missing_response_limit = copy.deepcopy(example)
    del missing_response_limit["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][0]["maxBytes"]
    expect_schema_failure(validator, missing_response_limit, "missing response representation byte limit")

    missing_response_binary_policy = copy.deepcopy(example)
    del missing_response_binary_policy["spec"]["operations"][0]["response"]["binaryContent"]
    expect_schema_failure(validator, missing_response_binary_policy, "multipart response missing binary-content policy")

    invalid_sbi_discriminator = copy.deepcopy(example)
    invalid_sbi_discriminator["spec"]["operations"][0]["correlation"]["duplicate"]["identitySource"] = "3gpp-sbi-idempotency-key"
    invalid_sbi_discriminator["spec"]["operations"][0]["correlation"]["duplicate"]["scope"] = "target-nf"
    stale = invalid_sbi_discriminator["spec"]["operations"][0]["correlation"]["staleDelivery"]
    stale.clear()
    stale.update({
        "strategy": "wire-discriminator",
        "discriminator": {
            "kind": "authenticated-header-parameter",
            "header": "3gpp-Sbi-Correlation-Info",
            "parameter": "supi",
        },
        "maximumLateArrival": "PT30S",
        "clockSkewAllowance": "PT5S",
        "discriminatorRetention": "PT36S",
        "basisRef": "urn:example:retry-window-guarantee",
    })
    expect_semantic_failure(invalid_sbi_discriminator, "UE correlation header is not a request idempotency discriminator")

    valid_sbi_discriminator = copy.deepcopy(example)
    operation = valid_sbi_discriminator["spec"]["operations"][0]
    operation["correlation"]["duplicate"]["identitySource"] = "3gpp-sbi-idempotency-key"
    operation["correlation"]["duplicate"]["scope"] = "target-nf"
    operation["correlation"]["staleDelivery"] = {
        "strategy": "wire-discriminator",
        "discriminator": {
            "kind": "authenticated-header-parameter",
            "header": "3gpp-Sbi-Request-Info",
            "parameter": "idempotency-key",
        },
        "maximumLateArrival": "PT30S",
        "clockSkewAllowance": "PT5S",
        "discriminatorRetention": "PT36S",
        "basisRef": "urn:example:retry-window-guarantee",
    }
    validate_semantics(valid_sbi_discriminator)
    if not validator.is_valid(valid_sbi_discriminator):
        raise SystemExit("valid target-NF-scoped SBI idempotency fixture failed IngressCatalog schema")
    validate_3gpp_reference_example(valid_sbi_discriminator)

    mismatched_sbi_scope = copy.deepcopy(valid_sbi_discriminator)
    mismatched_sbi_scope["spec"]["operations"][0]["correlation"]["duplicate"]["scope"] = "expected-ingress"
    expect_schema_failure(validator, mismatched_sbi_scope, "SBI idempotency scope narrowed to one ingress")
    expect_semantic_failure(mismatched_sbi_scope, "SBI idempotency scope narrowed to one ingress")

    invalid_timestamp_discriminator = copy.deepcopy(valid_sbi_discriminator)
    invalid_timestamp_discriminator["spec"]["operations"][0]["correlation"]["staleDelivery"]["discriminator"] = {
        "kind": "authenticated-header-parameter",
        "header": "3gpp-Sbi-Origination-Timestamp",
        "parameter": "value",
    }
    expect_semantic_failure(invalid_timestamp_discriminator, "retry-updated timestamp is not a request discriminator")

    invalid_max_rsp_time_discriminator = copy.deepcopy(valid_sbi_discriminator)
    invalid_max_rsp_time_discriminator["spec"]["operations"][0]["correlation"]["staleDelivery"]["discriminator"] = {
        "kind": "authenticated-header-parameter",
        "header": "3gpp-Sbi-Max-Rsp-Time",
        "parameter": "value",
    }
    expect_semantic_failure(invalid_max_rsp_time_discriminator, "response deadline header is not a request discriminator")

    invalid_resource_discriminator = copy.deepcopy(valid_sbi_discriminator)
    invalid_resource_discriminator["spec"]["operations"][0]["correlation"]["staleDelivery"]["discriminator"] = {
        "kind": "normalized-request-path",
        "path": "/smContextRef",
    }
    expect_semantic_failure(invalid_resource_discriminator, "smContextRef is a resource key, not a per-request discriminator")

    short_discriminator_retention = copy.deepcopy(valid_sbi_discriminator)
    short_discriminator_retention["spec"]["operations"][0]["correlation"]["staleDelivery"]["discriminatorRetention"] = "PT30S"
    expect_semantic_failure(short_discriminator_retention, "wire discriminator retention not strictly greater than late-arrival plus skew")

    equal_discriminator_retention = copy.deepcopy(valid_sbi_discriminator)
    equal_discriminator_retention["spec"]["operations"][0]["correlation"]["staleDelivery"]["discriminatorRetention"] = "PT35S"
    expect_semantic_failure(equal_discriminator_retention, "wire discriminator retention equal to late-arrival plus skew")

    mismatched_sbi_header = copy.deepcopy(valid_sbi_discriminator)
    mismatched_sbi_header["spec"]["operations"][0]["correlation"]["duplicate"]["identitySource"] = "canonical-request-digest"
    mismatched_sbi_header["spec"]["operations"][0]["correlation"]["duplicate"]["scope"] = "expected-ingress"
    expect_semantic_failure(mismatched_sbi_header, "SBI wire discriminator without matching duplicate identity source")

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

    missing_content_id_binding = copy.deepcopy(example)
    missing_content_id_binding["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["mappings"][2]["source"].pop("contentIdReference")
    expect_protocol_failure(missing_content_id_binding, "missing RefToBinaryData-to-Content-ID binding")

    wrong_content_id_binding = copy.deepcopy(example)
    wrong_content_id_binding["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["mappings"][2]["source"]["contentIdReference"]["pointer"] = "/smContextRef"
    expect_protocol_failure(wrong_content_id_binding, "Content-ID bound to the resource path instead of RefToBinaryData")

    wrong_content_id_member = copy.deepcopy(example)
    wrong_content_id_member["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["mappings"][2]["source"]["contentIdReference"]["pointer"] = "/n1SmMsg"
    expect_protocol_failure(wrong_content_id_member, "Content-ID binding points to RefToBinaryData object instead of its contentId member")

    json_only_binary_reference = copy.deepcopy(example)
    json_mappings = json_only_binary_reference["spec"]["operations"][0]["request"]["normalization"]["representations"][0]["mappings"]
    json_mappings.append({
        "source": {"kind": "json-body", "pointer": "/n1SmMsg/contentId"},
        "target": "/n1SmMessage",
        "transform": "binary-content-ref",
    })
    expect_semantic_failure(json_only_binary_reference, "JSON-only representation cannot synthesize a binary content reference")

    missing_n2_ext1 = copy.deepcopy(example)
    multipart_parts = missing_n2_ext1["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["parts"]
    multipart_parts[:] = [part for part in multipart_parts if part["name"] != "binaryDataN2SmInformationExt1"]
    multipart_mappings = missing_n2_ext1["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["mappings"]
    multipart_mappings[:] = [mapping for mapping in multipart_mappings if mapping["source"].get("part") != "binaryDataN2SmInformationExt1"]
    expect_protocol_failure(missing_n2_ext1, "missing TS 29.502 V19.5 N2 SM Information extension part")

    wrong_3gpp_response_path = copy.deepcopy(example)
    wrong_3gpp_response_path["spec"]["operations"][0]["response"]["result"]["mappings"][0]["from"] = "/smContextRef"
    expect_protocol_failure(wrong_3gpp_response_path, "incorrect SmContextUpdatedData response field")

    wrong_response_content_id = copy.deepcopy(example)
    response_mappings = wrong_response_content_id["spec"]["operations"][0]["response"]["result"]["mappings"]
    binary_mapping = next(item for item in response_mappings if item["target"]["kind"] == "multipart-binary")
    binary_mapping["target"]["contentIdField"]["pointer"] = "/smContextRef"
    expect_protocol_failure(wrong_response_content_id, "response Content-ID must bind RefToBinaryData.contentId")

    missing_response_binary_mapping = copy.deepcopy(example)
    response_mappings = missing_response_binary_mapping["spec"]["operations"][0]["response"]["result"]["mappings"]
    response_mappings[:] = [
        item for item in response_mappings
        if not (item["target"]["kind"] == "multipart-binary" and item["target"]["part"] == "binaryDataN1SmMessage")
    ]
    expect_semantic_failure(missing_response_binary_mapping, "multipart response binary part without mapping")

    mismatched_sbi_identity = copy.deepcopy(example)
    mismatched_sbi_identity["spec"]["operations"][0]["correlation"]["duplicate"]["identitySource"] = "3gpp-sbi-idempotency-key"
    mismatched_sbi_identity["spec"]["operations"][0]["correlation"]["duplicate"]["scope"] = "target-nf"
    expect_semantic_failure(mismatched_sbi_identity, "SBI idempotency identity without wire discriminator")

    invalid_binary_retention = copy.deepcopy(example)
    invalid_binary_retention["spec"]["operations"][0]["request"]["binaryContent"]["retention"] = "P1M"
    expect_semantic_failure(invalid_binary_retention, "calendar-month binary retention")

    duplicate_export_id = copy.deepcopy(example)
    duplicate_export = copy.deepcopy(duplicate_export_id["spec"]["operations"][0])
    duplicate_export["event"]["operation"] = "AnotherOperation"
    duplicate_export_id["spec"]["operations"].append(duplicate_export)
    expect_semantic_failure(duplicate_export_id, "duplicate ingress export id")

    duplicate_event_selector = copy.deepcopy(example)
    duplicate_selector = copy.deepcopy(duplicate_event_selector["spec"]["operations"][0])
    duplicate_selector["id"] = "another-export-id"
    duplicate_event_selector["spec"]["operations"].append(duplicate_selector)
    expect_semantic_failure(duplicate_event_selector, "duplicate event selector")

    short_tombstone = copy.deepcopy(example)
    stale = short_tombstone["spec"]["operations"][0]["correlation"]["staleDelivery"]
    stale["maximumLateArrival"] = "PT30S"
    stale["clockSkewAllowance"] = "PT5S"
    stale["tombstoneRetention"] = "PT30S"
    expect_semantic_failure(short_tombstone, "tombstone not strictly greater than late-arrival plus skew")

    equal_tombstone = copy.deepcopy(example)
    stale = equal_tombstone["spec"]["operations"][0]["correlation"]["staleDelivery"]
    stale["maximumLateArrival"] = "PT30S"
    stale["clockSkewAllowance"] = "PT5S"
    stale["tombstoneRetention"] = "PT35S"
    expect_semantic_failure(equal_tombstone, "tombstone equal to late-arrival plus skew")

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
