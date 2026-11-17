#!/usr/bin/env python3
"""Validate the documented IngressCatalog example against its structural schema."""

from __future__ import annotations

import copy
import json
import re
from email.parser import BytesParser
from email.policy import default as email_policy
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/design/integration-ingress-operation-contract-vnext.zh-CN.md"
SCHEMA = ROOT / "docs/design/schemas/ingresscatalog.v1alpha1.schema.json"
RESPONSE_RESULT_SCHEMA = ROOT / "docs/design/schemas/update-sm-context-response-result.v1.schema.json"
RESPONSE_BINARY_SCHEMA = ROOT / "docs/design/schemas/response-binary-content-reference.v1.schema.json"
STANDARD_ARTIFACT_LOCK = ROOT / "docs/design/artifacts/ts-29.502-v19.5.0-nsmf-pdusession-openapi-source-lock.yaml"
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
            if representation["mediaType"].startswith("multipart/"):
                part_list = representation["parts"]
                json_parts = [part for part in part_list if part["kind"] == "json"]
                if len(json_parts) != 1 or part_list[0]["kind"] != "json":
                    raise SystemExit(f"{op_id}: multipart request must have exactly one first JSON root part")
                declared_binary_count = sum(part["kind"] == "binary" for part in parts.values())
                minimum_binary = representation["minBinaryParts"]
                maximum_binary = representation["maxBinaryParts"]
                if minimum_binary > maximum_binary or maximum_binary > declared_binary_count:
                    raise SystemExit(f"{op_id}: invalid multipart binary part cardinality")
            for ignored in representation.get("ignoredSources", []):
                source = ignored["source"]
                if source["kind"] == "multipart-json":
                    ignored_part = parts.get(source["part"])
                    if ignored_part is None or ignored_part["kind"] != "json":
                        raise SystemExit(f"{op_id}: ignored multipart-json source must reference a declared JSON part")
                elif source["kind"] == "multipart-binary":
                    ignored_part = parts.get(source["part"])
                    if ignored_part is None or ignored_part["kind"] != "binary":
                        raise SystemExit(f"{op_id}: ignored multipart-binary source must reference a declared binary part")
            unique([item["source"] for item in representation.get("ignoredSources", [])], f"{op_id}: duplicate ignored source")
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
                        json_parts = [part for part in parts if part["kind"] == "json"]
                        if len(json_parts) != 1 or not parts or parts[0]["name"] != representation["rootPart"] or parts[0]["kind"] != "json":
                            raise SystemExit(f"{op_id}: multipart response rootPart must be the unique first JSON part")
                        declared_binary_count = sum(part["kind"] == "binary" for part in parts)
                        minimum_binary = representation["minBinaryParts"]
                        maximum_binary = representation["maxBinaryParts"]
                        if minimum_binary > maximum_binary or maximum_binary > declared_binary_count:
                            raise SystemExit(f"{op_id}: invalid multipart response binary part cardinality")
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
    if multipart["minBinaryParts"] != 1 or multipart["maxBinaryParts"] != 2:
        raise SystemExit("TS 29.502 V19.5.0 multipart request must allow one or two actual binary parts")
    request_part_list = multipart["parts"]
    request_part_names = [part["name"] for part in request_part_list]
    required_parts = [
        "jsonData",
        "binaryDataN1SmMessage",
        "binaryDataN2SmInformation",
        "binaryDataN2SmInformationExt1",
    ]
    if request_part_names != required_parts:
        raise SystemExit("UpdateSMContext request multipart parts must be unique, complete and rooted at jsonData")
    request_root = request_part_list[0]
    if request_root["kind"] != "json" or request_root["required"] is not True or request_root["mediaType"] != "application/json":
        raise SystemExit("UpdateSMContext request multipart root must be the first required application/json part")
    expected_request_part_media_types = {
        "binaryDataN1SmMessage": "application/vnd.3gpp.5gnas",
        "binaryDataN2SmInformation": "application/vnd.3gpp.ngap",
        "binaryDataN2SmInformationExt1": "application/vnd.3gpp.ngap",
    }
    for part_name, media_type in expected_request_part_media_types.items():
        part = next(item for item in request_part_list if item["name"] == part_name)
        if part["kind"] != "binary" or part["required"] is not False or part["mediaType"] != media_type:
            raise SystemExit(f"{part_name} must be an optional binary part with media type {media_type}")
    json_mapping = next((item for item in multipart["mappings"] if item["source"]["kind"] == "multipart-json"), None)
    if json_mapping is None or json_mapping["source"] != {"kind": "multipart-json", "part": "jsonData", "pointer": ""} or json_mapping["target"] != "/updateData" or json_mapping["transform"] != "identity":
        raise SystemExit("UpdateSMContext jsonData must map to updateData while ignoredSources mask transport-only RefToBinaryData")

    expected_binary_mappings = {
        "binaryDataN1SmMessage": ("/n1SmMsg/contentId", "/n1SmMessage"),
        "binaryDataN2SmInformation": ("/n2SmInfo/contentId", "/n2SmInformation"),
        "binaryDataN2SmInformationExt1": ("/n2SmInfoExt1/contentId", "/n2SmInformationExt1"),
    }
    request_binary_mappings = [
        item for item in multipart["mappings"]
        if item["source"]["kind"] == "multipart-binary"
    ]
    mappings_by_part = {item["source"]["part"]: item for item in request_binary_mappings}
    if len(request_binary_mappings) != len(expected_binary_mappings) or set(mappings_by_part) != set(expected_binary_mappings):
        raise SystemExit("Every declared UpdateSMContext binary part must have exactly one normalized mapping")
    for part_name, (reference_pointer, target) in expected_binary_mappings.items():
        mapping = mappings_by_part[part_name]
        if mapping["source"].get("contentIdReference") != {"part": "jsonData", "pointer": reference_pointer}:
            raise SystemExit(f"{part_name} must be linked to jsonData {reference_pointer} by Content-ID")
        if mapping["target"] != target or mapping["transform"] != "binary-content-ref":
            raise SystemExit(f"{part_name} is not mapped to its typed immutable binary content reference")

    ignored_refs = {
        (item["source"]["kind"], item["source"].get("part"), item["source"].get("pointer"))
        for item in multipart.get("ignoredSources", [])
    }
    expected_ignored_refs = {
        ("multipart-json", "jsonData", "/n1SmMsg"),
        ("multipart-json", "jsonData", "/n2SmInfo"),
        ("multipart-json", "jsonData", "/n2SmInfoExt1"),
    }
    if ignored_refs != expected_ignored_refs:
        raise SystemExit("UpdateSMContext must mask all raw RefToBinaryData objects from normalized business data")
    normalized_targets = {item["target"] for item in multipart["mappings"]}
    if not {"/n1SmMessage", "/n2SmInformation", "/n2SmInformationExt1"} <= normalized_targets:
        raise SystemExit("UpdateSMContext binary parts are not mapped to normalized business fields")

    if operation["protocol"]["apiUriVersion"] != "v1":
        raise SystemExit("UpdateSMContext API URI version must be v1")

    response = operation["response"]
    if response["result"]["responseResultSchemaRef"] != "urn:example:response-result:update-sm-context:v1":
        raise SystemExit("UpdateSMContext response result must use the pinned Step 17 response-result Schema")
    if response["binaryContent"]["referenceSchemaRef"] != "urn:example:response:binary-content-reference:v1":
        raise SystemExit("UpdateSMContext response binary references must use the immutable payload-reference Schema")
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
    if multipart_response["minBinaryParts"] != 1 or multipart_response["maxBinaryParts"] != 2:
        raise SystemExit("TS 29.502 V19.5.0 multipart response must allow one or two actual binary parts")
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
        ("multipart", "multipart-json", "jsonData", "/n2SmInfoType"): ("/n2SmInfoType", "identity"),
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


def validate_standard_artifact_lock() -> None:
    lock = yaml.safe_load(STANDARD_ARTIFACT_LOCK.read_text(encoding="utf-8"))
    spec = lock["spec"]
    normative = spec["normativeSource"]
    companion = spec["officialCompanionSource"]
    informative = spec["informativeSource"]
    api = spec["api"]
    if spec["standard"] != {
        "name": "3GPP TS 29.502",
        "version": "19.5.0",
        "release": 19,
    }:
        raise SystemExit("standard artifact lock must identify TS 29.502 V19.5.0 Release 19")
    if (
        api["title"] != "Nsmf_PDUSession"
        or api["openapiVersion"] != "3.0.0"
        or api["apiVersion"] != "1.4.0"
        or api["annex"] != "A.2"
        or api["sourceFileName"] != "TS29502_Nsmf_PDUSession.yaml"
    ):
        raise SystemExit("standard artifact lock does not identify the exact Annex A.2 API")
    if (
        normative["uri"] != "https://www.etsi.org/deliver/etsi_ts/129500_129599/129502/19.05.00_60/ts_129502v190500p.pdf"
        or normative["publisher"] != "ETSI"
        or normative["annexA2"]["normative"] is not True
        or normative["byteLength"] != 2066717
        or normative["sha256"] != "5afc2745fb6baf6c1216b6c5f0873e0696c6aa1531eac462a73f32a80672c436"
    ):
        raise SystemExit("normative PDF metadata or SHA-256 does not match the published ETSI deliverable")
    extracted = companion["extractedFile"]
    if (
        companion["uri"] != "https://www.etsi.org/deliver/etsi_ts/129500_129599/129502/19.05.00_60/ts_129502v190500p0.zip"
        or companion["byteLength"] != 18012
        or companion["sha256"] != "dca26e15363c01f37eac639305834d0359ae6b011f2c5adeac3c09f49300a883"
        or extracted["path"] != "TS29502_Nsmf_PDUSession.yaml"
        or extracted["byteLength"] != 209138
        or extracted["sha256"] != "ca5d94e296a334c85635715fc325167459d865f2c83a16c47926c979dab7545b"
    ):
        raise SystemExit("official ETSI companion package or extracted OpenAPI SHA-256 does not match the artifact lock")
    dependencies = spec["externalDependencies"]
    if len(dependencies) != 1:
        raise SystemExit("TS 29.502 artifact lock must pin exactly one external OpenAPI dependency")
    common = dependencies[0]
    if common["standard"] != {
        "name": "3GPP TS 29.571",
        "version": "19.5.0",
        "release": 19,
    }:
        raise SystemExit("external CommonData dependency must be TS 29.571 V19.5.0 Release 19")
    common_api = common["api"]
    if common_api != {
        "title": "Common Data Types",
        "openapiVersion": "3.0.0",
        "apiVersion": "1.6.0",
        "annex": "A.2",
        "sourceFileName": "TS29571_CommonData.yaml",
    }:
        raise SystemExit("external dependency must identify the exact TS 29.571 Annex A.2 CommonData artifact")
    common_pdf = common["normativeSource"]
    if (
        common_pdf["uri"] != "https://www.etsi.org/deliver/etsi_ts/129500_129599/129571/19.05.00_60/ts_129571v190500p.pdf"
        or common_pdf["publisher"] != "ETSI"
        or common_pdf["byteLength"] != 1191071
        or common_pdf["sha256"] != "a608887aa19de1c28fdef8b3ae02d015fe8ccbaa8db52b3fa7defe48d5ff7c84"
        or common_pdf["annexA2"]["normative"] is not True
    ):
        raise SystemExit("TS 29.571 normative PDF metadata or SHA-256 does not match ETSI V19.5.0")
    common_companion = common["officialCompanionSource"]
    common_extracted = common_companion["extractedFile"]
    if (
        common_companion["uri"] != "https://www.etsi.org/deliver/etsi_ts/129500_129599/129571/19.05.00_60/ts_129571v190500p0.zip"
        or common_companion["publisher"] != "ETSI"
        or common_companion["byteLength"] != 38569
        or common_companion["sha256"] != "5bc10332b197f1df131908cc236ca7c6ab97b0d3c908e7825f1d701c9d56e978"
        or common_extracted["path"] != "TS29571_CommonData.yaml"
        or common_extracted["byteLength"] != 255480
        or common_extracted["sha256"] != "8632cbab60c73e9c3ba9be26577057144255f21aef7430a1990bdf113c1e7bd4"
    ):
        raise SystemExit("official TS 29.571 companion package or extracted CommonData SHA-256 does not match the artifact lock")
    closure = common["operationSchemaClosure"]
    if closure != {
        "operationId": "UpdateSmContext",
        "scope": "operation-request-and-responses",
        "externalDocuments": ["TS29571_CommonData.yaml"],
        "status": "VERIFIED_BY_CI",
    }:
        raise SystemExit("UpdateSmContext operation-scoped OpenAPI reference closure is not pinned")
    if (
        informative["normative"] is not False
        or informative["matchesOfficialCompanionSource"] is not False
        or informative["observedCommit"] != "e4979d6e1d0d181b5a97cc4732855128a1772e64"
        or informative["sha256"] != "1c01de5877b3d80178971a2b788473ea84a6ed6bd09f0a60cfa4fc96784bc9bf"
    ):
        raise SystemExit("the GitLab REL-19 informative copy must remain distinct from the ETSI-published source bytes")
    verification = spec["verification"]
    if verification["status"] != "OFFICIAL_SOURCE_BYTES_PINNED" or verification["admissionAllowed"] is not False:
        raise SystemExit("source bytes may be pinned, but Owner admission must remain blocked until implementation qualification")


def build_multipart_wire(root: dict, binary_parts: list[dict], boundary: str = "ca-step17-boundary") -> bytes:
    crlf = bytes((13, 10))
    chunks = [
        f"--{boundary}".encode() + crlf,
        b"Content-Type: application/json" + crlf,
        b"Content-ID: <root@connectionagent>" + crlf + crlf,
        json.dumps(root, separators=(",", ":")).encode("utf-8"),
        crlf,
    ]
    for item in binary_parts:
        chunks.extend([
            f"--{boundary}".encode() + crlf,
            f"Content-Type: {item['mediaType']}".encode() + crlf,
            f"Content-ID: {item['contentId']}".encode() + crlf,
        ])
        if item.get("duplicateContentId"):
            chunks.append(f"Content-ID: {item['duplicateContentId']}".encode() + crlf)
        chunks.extend([crlf, item.get("body", b"binary"), crlf])
    chunks.append(f"--{boundary}--".encode() + crlf)
    headers = (
        f'Content-Type: multipart/related; boundary="{boundary}"; type="application/json"'.encode("ascii")
        + crlf
        + b"MIME-Version: 1.0"
        + crlf
        + crlf
    )
    return headers + b"".join(chunks)
def parse_3gpp_multipart_reference(raw: bytes, role_map: dict[str, tuple[str, str]]) -> tuple[dict, dict]:
    message = BytesParser(policy=email_policy).parsebytes(raw)
    if not message.is_multipart() or message.get_content_type() != "multipart/related":
        raise ValueError("wire body is not multipart/related")
    if message.get_param("type") != "application/json":
        raise ValueError("multipart/related type parameter must be application/json")
    parts = list(message.iter_parts())
    if len(parts) < 2 or parts[0].get_content_type() != "application/json":
        raise ValueError("multipart message must begin with one JSON root part")
    if sum(part.get_content_type() == "application/json" for part in parts) != 1:
        raise ValueError("multipart message must contain exactly one JSON root part")
    binary_parts = parts[1:]
    if not 1 <= len(binary_parts) <= 2:
        raise ValueError("TS 29.502 multipart message must contain one or two binary parts")

    root_payload = parts[0].get_payload(decode=True)
    try:
        root = json.loads(root_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("multipart JSON root is invalid") from error
    if not isinstance(root, dict):
        raise ValueError("multipart JSON root must be an object")

    type_pairs = (
        ("n2SmInfo", "n2SmInfoType"),
        ("n2SmInfoExt1", "n2SmInfoTypeExt1"),
    )
    for binary_field, type_field in type_pairs:
        if (binary_field in root) != (type_field in root):
            raise ValueError(f"{binary_field} and {type_field} must be present together")

    references = {}
    for field, (role, media_type) in role_map.items():
        if field not in root:
            continue
        reference = root[field]
        if not isinstance(reference, dict) or not isinstance(reference.get("contentId"), str) or not reference["contentId"]:
            raise ValueError(f"{field} must contain a non-empty RefToBinaryData.contentId")
        content_id = reference["contentId"]
        if content_id in references:
            raise ValueError("RefToBinaryData contentId values must be unique")
        references[content_id] = (field, role, media_type)

    seen_content_ids = set()
    for part in binary_parts:
        content_id_headers = part.get_all("Content-ID", [])
        if len(content_id_headers) != 1:
            raise ValueError("each binary part must have exactly one Content-ID header")
        content_id = str(content_id_headers[0])
        if content_id in seen_content_ids:
            raise ValueError("binary Content-ID values must be unique")
        seen_content_ids.add(content_id)
        reference = references.get(content_id)
        if reference is None:
            raise ValueError("binary part has no matching RefToBinaryData.contentId")
        if part.get_content_type() != reference[2]:
            raise ValueError("binary part media type does not match its RefToBinaryData role")

    if seen_content_ids != set(references):
        raise ValueError("RefToBinaryData contains a missing or dangling binary part reference")

    normalized = {key: value for key, value in root.items() if key not in role_map}
    binary_roles = {value[1]: content_id for content_id, value in references.items()}
    if any(field in normalized for field in role_map):
        raise ValueError("raw RefToBinaryData must not leak into normalized business data")
    return normalized, binary_roles


def validate_json_only_update(root: dict) -> None:
    for field in ("n1SmMsg", "n2SmInfo", "n2SmInfoExt1"):
        if field in root:
            raise ValueError("application/json cannot contain an unresolved RefToBinaryData")


def validate_multipart_wire_reference_vectors() -> None:
    request_roles = {
        "n1SmMsg": ("binaryDataN1SmMessage", "application/vnd.3gpp.5gnas"),
        "n2SmInfo": ("binaryDataN2SmInformation", "application/vnd.3gpp.ngap"),
        "n2SmInfoExt1": ("binaryDataN2SmInformationExt1", "application/vnd.3gpp.ngap"),
    }
    response_roles = {
        "n1SmMsg": ("binaryDataN1SmMessage", "application/vnd.3gpp.5gnas"),
        "n2SmInfo": ("binaryDataN2SmInformation", "application/vnd.3gpp.ngap"),
    }

    one_n1 = {
        "n1SmMsg": {"contentId": "<n1@ca>"},
        "cause": "REQUEST_REJECTED",
    }
    normalized, roles = parse_3gpp_multipart_reference(
        build_multipart_wire(one_n1, [{
            "contentId": "<n1@ca>",
            "mediaType": "application/vnd.3gpp.5gnas",
        }]),
        request_roles,
    )
    if "n1SmMsg" in normalized or roles.get("binaryDataN1SmMessage") != "<n1@ca>":
        raise SystemExit("single N1 request part did not normalize to a transport-only binary reference")

    two_parts = {
        "n1SmMsg": {"contentId": "<n1@ca>"},
        "n2SmInfo": {"contentId": "<n2@ca>"},
        "n2SmInfoType": "PDU_RES_SETUP_REQ",
        "servingNetwork": {"mcc": "001", "mnc": "01"},
    }
    normalized, roles = parse_3gpp_multipart_reference(
        build_multipart_wire(two_parts, [
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
            {"contentId": "<n2@ca>", "mediaType": "application/vnd.3gpp.ngap"},
        ]),
        request_roles,
    )
    if "n1SmMsg" in normalized or "n2SmInfo" in normalized or normalized.get("n2SmInfoType") != "PDU_RES_SETUP_REQ":
        raise SystemExit("two-part request did not preserve business N2 type while masking RefToBinaryData")
    if set(roles) != {"binaryDataN1SmMessage", "binaryDataN2SmInformation"}:
        raise SystemExit("two-part request binary roles were not resolved exactly")

    ext1 = {
        "n2SmInfoExt1": {"contentId": "<n2ext1@ca>"},
        "n2SmInfoTypeExt1": "PDU_RES_SETUP_REQ",
    }
    parse_3gpp_multipart_reference(
        build_multipart_wire(ext1, [{
            "contentId": "<n2ext1@ca>",
            "mediaType": "application/vnd.3gpp.ngap",
        }]),
        request_roles,
    )

    response_reject = {"n1SmMsg": {"contentId": "<reject@ca>"}}
    parse_3gpp_multipart_reference(
        build_multipart_wire(response_reject, [{
            "contentId": "<reject@ca>",
            "mediaType": "application/vnd.3gpp.5gnas",
        }]),
        response_roles,
    )

    invalid_vectors = [
        ("zero binary parts", {"n1SmMsg": {"contentId": "<n1@ca>"}}, []),
        ("three binary parts", {
            "n1SmMsg": {"contentId": "<n1@ca>"},
            "n2SmInfo": {"contentId": "<n2@ca>"},
            "n2SmInfoType": "PDU_RES_SETUP_REQ",
            "n2SmInfoExt1": {"contentId": "<n2ext1@ca>"},
            "n2SmInfoTypeExt1": "PDU_RES_SETUP_REQ",
        }, [
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
            {"contentId": "<n2@ca>", "mediaType": "application/vnd.3gpp.ngap"},
            {"contentId": "<n2ext1@ca>", "mediaType": "application/vnd.3gpp.ngap"},
        ]),
        ("mismatched Content-ID", {"n1SmMsg": {"contentId": "<expected@ca>"}}, [
            {"contentId": "<actual@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
        ]),
        ("unreferenced binary part", {"n1SmMsg": {"contentId": "<n1@ca>"}}, [
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
            {"contentId": "<orphan@ca>", "mediaType": "application/vnd.3gpp.ngap"},
        ]),
        ("N2 info without N2 type", {"n2SmInfo": {"contentId": "<n2@ca>"}}, [
            {"contentId": "<n2@ca>", "mediaType": "application/vnd.3gpp.ngap"},
        ]),
        ("N2 type without N2 info", {"n2SmInfoType": "PDU_RES_SETUP_REQ"}, [
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
        ]),
        ("wrong N1 media type", {"n1SmMsg": {"contentId": "<n1@ca>"}}, [
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.ngap"},
        ]),
        ("duplicate binary Content-ID", {"n1SmMsg": {"contentId": "<n1@ca>"}}, [
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
            {"contentId": "<n1@ca>", "mediaType": "application/vnd.3gpp.5gnas"},
        ]),
    ]
    for label, root, binary_parts in invalid_vectors:
        try:
            parse_3gpp_multipart_reference(build_multipart_wire(root, binary_parts), request_roles)
        except ValueError:
            continue
        raise SystemExit(f"invalid multipart reference vector was unexpectedly accepted: {label}")

    try:
        validate_json_only_update({"n1SmMsg": {"contentId": "<n1@ca>"}})
    except ValueError:
        pass
    else:
        raise SystemExit("application/json request with RefToBinaryData was unexpectedly accepted")

    duplicate_header_wire = build_multipart_wire(
        {"n1SmMsg": {"contentId": "<n1@ca>"}},
        [{
            "contentId": "<n1@ca>",
            "duplicateContentId": "<duplicate@ca>",
            "mediaType": "application/vnd.3gpp.5gnas",
        }],
    )
    try:
        parse_3gpp_multipart_reference(duplicate_header_wire, request_roles)
    except ValueError:
        pass
    else:
        raise SystemExit("binary part with duplicate Content-ID headers was unexpectedly accepted")


def validate_step15_failure_response_schema() -> None:
    result_schema = json.loads(RESPONSE_RESULT_SCHEMA.read_text(encoding="utf-8"))
    binary_schema = json.loads(RESPONSE_BINARY_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(result_schema)
    Draft202012Validator.check_schema(binary_schema)
    registry = Registry().with_resource(
        binary_schema["$id"],
        Resource.from_contents(binary_schema),
    )
    validator = Draft202012Validator(result_schema, registry=registry)

    n1_reference = {
        "payloadRef": "urn:connectionagent:payload:step17-n1-reject-01",
        "mediaType": "application/vnd.3gpp.5gnas",
        "byteLength": 32,
        "sha256": "a" * 64,
    }
    n2_reference = {
        "payloadRef": "urn:connectionagent:payload:step17-n2-response-01",
        "mediaType": "application/vnd.3gpp.ngap",
        "byteLength": 64,
        "sha256": "b" * 64,
    }

    valid_failure = {
        "procedureOutcome": "n2-user-plane-setup-failed",
        "step16Outcome": {
            "n4Action": "session-released",
            "udmRegistration": "skipped",
        },
        "responseRepresentation": "multipart",
        "n1SmMessage": n1_reference,
    }
    valid_enforcement_failure = {
        "procedureOutcome": "user-plane-enforcement-required-unavailable",
        "step16Outcome": {
            "n4Action": "not-performed",
            "udmRegistration": "skipped",
        },
        "responseRepresentation": "multipart",
        "n1SmMessage": n1_reference,
    }
    valid_success_json = {
        "procedureOutcome": "n2-user-plane-setup-succeeded",
        "step16Outcome": {
            "n4Action": "session-modified",
            "udmRegistration": "completed",
        },
        "responseRepresentation": "json",
        "cause": "REQUEST_ACCEPTED",
    }
    valid_success_multipart = {
        "procedureOutcome": "n2-user-plane-setup-succeeded",
        "step16Outcome": {
            "n4Action": "session-modified",
            "udmRegistration": "not-required",
        },
        "responseRepresentation": "multipart",
        "n2SmInformation": n2_reference,
        "n2SmInfoType": "PDU_RES_SETUP_RSP",
    }
    valid_success_no_content = {
        "procedureOutcome": "n2-user-plane-setup-succeeded",
        "step16Outcome": {
            "n4Action": "session-modified",
            "udmRegistration": "not-required",
        },
        "responseRepresentation": "no-content",
    }
    for label, value in (
        ("N2 setup failure with pre-response N4 release and multipart N1 reject", valid_failure),
        ("required UPE failure with Step 16 skipped and multipart N1 reject", valid_enforcement_failure),
        ("successful N2 setup with JSON response", valid_success_json),
        ("successful N2 setup with multipart N2 response", valid_success_multipart),
        ("successful N2 setup with bodyless 204", valid_success_no_content),
    ):
        errors = list(validator.iter_errors(value))
        if errors:
            raise SystemExit(f"{label}: unexpectedly invalid: {errors[0].message}")

    invalid_cases = []

    invalid = copy.deepcopy(valid_failure)
    invalid["responseRepresentation"] = "json"
    invalid_cases.append(("N2 setup failure cannot use JSON without binary part", invalid))

    invalid = copy.deepcopy(valid_failure)
    del invalid["n1SmMessage"]
    invalid_cases.append(("N2 setup failure requires N1 SM Reject", invalid))

    invalid = copy.deepcopy(valid_failure)
    invalid["step16Outcome"]["n4Action"] = "session-modified"
    invalid_cases.append(("N2 setup failure must release N4 Session", invalid))

    invalid = copy.deepcopy(valid_failure)
    invalid["step16Outcome"]["udmRegistration"] = "completed"
    invalid_cases.append(("Step 16c is skipped on the Step 15 N2 failure branch", invalid))

    invalid = copy.deepcopy(valid_enforcement_failure)
    invalid["responseRepresentation"] = "json"
    invalid_cases.append(("required UPE failure cannot use JSON without the N1 Reject binary part", invalid))

    invalid = copy.deepcopy(valid_enforcement_failure)
    del invalid["n1SmMessage"]
    invalid_cases.append(("required UPE failure requires N1 SM Reject", invalid))

    invalid = copy.deepcopy(valid_enforcement_failure)
    invalid["step16Outcome"]["n4Action"] = "session-released"
    invalid_cases.append(("required UPE failure must not model Step 16 N4 release before Step 17", invalid))

    invalid = copy.deepcopy(valid_enforcement_failure)
    invalid["step16Outcome"]["udmRegistration"] = "completed"
    invalid_cases.append(("Step 16c is skipped on required UPE failure", invalid))

    invalid = copy.deepcopy(valid_success_json)
    invalid["step16Outcome"]["n4Action"] = "session-released"
    invalid_cases.append(("successful N2 setup requires N4 Session Modification", invalid))

    invalid = copy.deepcopy(valid_success_multipart)
    del invalid["n2SmInfoType"]
    invalid_cases.append(("N2 binary response requires n2SmInfoType", invalid))

    invalid = copy.deepcopy(valid_success_multipart)
    del invalid["n2SmInformation"]
    invalid_cases.append(("n2SmInfoType cannot exist without N2 binary content", invalid))

    invalid = copy.deepcopy(valid_success_no_content)
    invalid["cause"] = "REQUEST_ACCEPTED"
    invalid_cases.append(("204 response cannot discard a Cause body field", invalid))

    invalid = copy.deepcopy(valid_failure)
    invalid["n1SmMessage"]["mediaType"] = "application/vnd.3gpp.ngap"
    invalid_cases.append(("N1 SM reject must use the 5G NAS media type", invalid))

    invalid = copy.deepcopy(valid_failure)
    invalid["n1SmMessage"]["payloadRef"] = "https://example.invalid/payload"
    invalid_cases.append(("binary payload reference cannot be an arbitrary URL", invalid))

    invalid = copy.deepcopy(valid_failure)
    invalid["n1SmMessage"]["sha256"] = "not-a-digest"
    invalid_cases.append(("binary payload reference requires SHA-256", invalid))

    invalid = copy.deepcopy(valid_failure)
    invalid["n1SmMessage"]["byteLength"] = 1048577
    invalid_cases.append(("binary payload reference must respect the declared maxBytes", invalid))

    for label, value in invalid_cases:
        if validator.is_valid(value):
            raise SystemExit(f"negative response-result fixture was unexpectedly accepted: {label}")


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

    multipart_response_missing_max_binary_parts = copy.deepcopy(example)
    multipart_response_missing_max_binary_parts["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1].pop("maxBinaryParts")
    expect_schema_failure(validator, multipart_response_missing_max_binary_parts, "multipart response missing binary part upper bound")

    request_multipart_missing_min_binary_parts = copy.deepcopy(example)
    request_multipart_missing_min_binary_parts["spec"]["operations"][0]["request"]["normalization"]["representations"][1].pop("minBinaryParts")
    expect_schema_failure(validator, request_multipart_missing_min_binary_parts, "multipart request missing binary part lower bound")

    multipart_response_without_binary = copy.deepcopy(example)
    response_parts = multipart_response_without_binary["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1]["parts"]
    response_parts[:] = [part for part in response_parts if part["kind"] != "binary"]
    expect_schema_failure(validator, multipart_response_without_binary, "multipart response requires at least one binary part")

    multipart_response_with_two_json_roots = copy.deepcopy(example)
    response_parts = multipart_response_with_two_json_roots["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1]["parts"]
    duplicate_root = copy.deepcopy(response_parts[0])
    duplicate_root["name"] = "secondJsonRoot"
    response_parts.append(duplicate_root)
    expect_schema_failure(validator, multipart_response_with_two_json_roots, "multipart response has exactly one JSON root part")

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

    wrong_request_binary_cardinality = copy.deepcopy(example)
    wrong_request_binary_cardinality["spec"]["operations"][0]["request"]["normalization"]["representations"][1]["maxBinaryParts"] = 3
    expect_protocol_failure(wrong_request_binary_cardinality, "TS 29.502 request cannot carry three actual binary parts")

    wrong_response_binary_cardinality = copy.deepcopy(example)
    wrong_response_binary_cardinality["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1]["maxBinaryParts"] = 3
    expect_semantic_failure(wrong_response_binary_cardinality, "response binary part upper bound exceeds declared binary part count")

    missing_ref_to_binary_mask = copy.deepcopy(example)
    multipart_representation = missing_ref_to_binary_mask["spec"]["operations"][0]["request"]["normalization"]["representations"][1]
    multipart_representation.pop("ignoredSources")
    expect_protocol_failure(missing_ref_to_binary_mask, "raw RefToBinaryData would leak into normalized request")

    masked_business_n2_type = copy.deepcopy(example)
    multipart_representation = masked_business_n2_type["spec"]["operations"][0]["request"]["normalization"]["representations"][1]
    multipart_representation["ignoredSources"].append({
        "source": {"kind": "multipart-json", "part": "jsonData", "pointer": "/n2SmInfoTypeExt1"},
        "reason": "incorrectly masked business N2 information type",
    })
    expect_protocol_failure(masked_business_n2_type, "N2SmInfoTypeExt1 must remain a business field")

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

    wrong_response_binary_source = copy.deepcopy(example)
    response_mappings = wrong_response_binary_source["spec"]["operations"][0]["response"]["result"]["mappings"]
    binary_mapping = next(item for item in response_mappings if item["target"]["kind"] == "multipart-binary")
    binary_mapping["from"] = "/smContextRef"
    expect_protocol_failure(wrong_response_binary_source, "binary response mapping cannot read smContextRef")

    missing_n2_info_type_mapping = copy.deepcopy(example)
    response_mappings = missing_n2_info_type_mapping["spec"]["operations"][0]["response"]["result"]["mappings"]
    response_mappings[:] = [
        item for item in response_mappings
        if item["target"].get("pointer") != "/n2SmInfoType"
    ]
    expect_protocol_failure(missing_n2_info_type_mapping, "N2 binary response must map n2SmInfoType")

    wrong_n2_info_type_source = copy.deepcopy(example)
    response_mappings = wrong_n2_info_type_source["spec"]["operations"][0]["response"]["result"]["mappings"]
    n2_type_mapping = next(
        item for item in response_mappings
        if item["target"].get("pointer") == "/n2SmInfoType"
    )
    n2_type_mapping["from"] = "/smContextRef"
    expect_protocol_failure(wrong_n2_info_type_source, "N2SmInfoType must come from the typed response result")

    duplicate_response_mapping = copy.deepcopy(example)
    response_mappings = duplicate_response_mapping["spec"]["operations"][0]["response"]["result"]["mappings"]
    duplicate_mapping = copy.deepcopy(response_mappings[-1])
    duplicate_mapping["from"] = "/cause"
    response_mappings.append(duplicate_mapping)
    expect_protocol_failure(duplicate_response_mapping, "duplicate response binary target mapping")

    wrong_response_root_order = copy.deepcopy(example)
    response_parts = wrong_response_root_order["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1]["parts"]
    response_parts[0], response_parts[1] = response_parts[1], response_parts[0]
    expect_protocol_failure(wrong_response_root_order, "multipart response JSON root is not first")

    mismatched_response_schema_digest = copy.deepcopy(example)
    multipart_response = mismatched_response_schema_digest["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1]
    multipart_response["responseSchemaDigest"] = "sha256:" + "1" * 64
    expect_protocol_failure(mismatched_response_schema_digest, "multipart root response schema digest mismatch")

    insufficient_response_total_limit = copy.deepcopy(example)
    multipart_response = insufficient_response_total_limit["spec"]["operations"][0]["response"]["dispositions"][0]["representations"][1]
    multipart_response["maxBytes"] = 2000000
    expect_protocol_failure(insufficient_response_total_limit, "response total limit cannot fit declared part limits and MIME framing")

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
    validate_step15_failure_response_schema()
    validate_multipart_wire_reference_vectors()
    validate_standard_artifact_lock()
    print("IngressCatalog, Step 17 response-result schemas, multipart wire reference vectors, artifact source lock and negative fixtures: PASS")


if __name__ == "__main__":
    main()
