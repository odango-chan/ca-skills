#!/usr/bin/env python3
"""Verify the current 5GC production-profile ETSI V19.7.0 artifact lock."""
from __future__ import annotations

import hashlib
import pathlib
import sys
import zipfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = ROOT / "docs/design/artifacts/ts-29.502-v19.7.0-nsmf-pdusession-openapi-source-lock.yaml"


class StrictLoader(yaml.SafeLoader):
    pass


def construct_unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise yaml.constructor.ConstructorError(
                "while constructing a lock mapping", node.start_mark,
                "mapping keys must be strings", key_node.start_mark,
            )
        if key in result:
            raise yaml.constructor.ConstructorError(
                "while constructing a lock mapping", node.start_mark,
                f"duplicate mapping key {key!r}", key_node.start_mark,
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping)


def fail(message: str) -> None:
    raise SystemExit(message)


def load_yaml(path: pathlib.Path):
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    except yaml.YAMLError as exc:
        fail(f"strict YAML parse failed for {path}: {exc}")


def verify_bytes(path: pathlib.Path, expected: dict, label: str) -> bytes:
    data = path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if len(data) != expected["byteLength"]:
        fail(f"{label} byteLength mismatch: {len(data)} != {expected['byteLength']}")
    if actual != expected["sha256"]:
        fail(f"{label} SHA-256 mismatch: {actual} != {expected['sha256']}")
    return data


def verify_zip_member(zip_path: pathlib.Path, member: dict, extracted_path: pathlib.Path, label: str) -> bytes:
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if names.count(member["path"]) != 1:
            fail(f"{label} archive must contain exactly one {member['path']}")
        data = archive.read(member["path"])
    if data != extracted_path.read_bytes():
        fail(f"{label} extracted YAML does not byte-match the official companion ZIP member")
    if len(data) != member["byteLength"]:
        fail(f"{label} extracted YAML byteLength mismatch")
    actual = hashlib.sha256(data).hexdigest()
    if actual != member["sha256"]:
        fail(f"{label} extracted YAML SHA-256 mismatch: {actual}")
    return data


def main() -> None:
    if len(sys.argv) != 7:
        fail("usage: validate_etsi_production_artifact_lock.py PDF502 ZIP502 YAML502 PDF571 ZIP571 YAML571")

    pdf502, zip502, yaml502, pdf571, zip571, yaml571 = map(pathlib.Path, sys.argv[1:])
    lock = load_yaml(LOCK)
    spec = lock["spec"]
    if lock.get("apiVersion") != "connectionagent.io/standard-artifact-lock/v1alpha1":
        fail("unexpected standard artifact lock apiVersion")
    if lock.get("kind") != "StandardArtifactLock":
        fail("unexpected standard artifact lock kind")
    if spec["standard"] != {"name": "3GPP TS 29.502", "version": "19.7.0", "release": 19}:
        fail("primary lock must pin TS 29.502 V19.7.0")
    dependency = spec["externalDependencies"][0]
    if dependency["standard"] != {"name": "3GPP TS 29.571", "version": "19.7.0", "release": 19}:
        fail("external dependency must pin TS 29.571 V19.7.0")

    verify_bytes(pdf502, spec["normativeSource"], "TS 29.502 V19.7.0 PDF")
    verify_bytes(zip502, spec["officialCompanionSource"], "TS 29.502 V19.7.0 companion ZIP")
    verify_zip_member(
        zip502, spec["officialCompanionSource"]["extractedFile"], yaml502,
        "TS 29.502 V19.7.0",
    )
    verify_bytes(pdf571, dependency["normativeSource"], "TS 29.571 V19.7.0 PDF")
    verify_bytes(zip571, dependency["officialCompanionSource"], "TS 29.571 V19.7.0 companion ZIP")
    verify_zip_member(
        zip571, dependency["officialCompanionSource"]["extractedFile"], yaml571,
        "TS 29.571 V19.7.0",
    )

    session = load_yaml(yaml502)
    common = load_yaml(yaml571)
    if session["openapi"] != "3.0.0" or session["info"]["title"] != "Nsmf_PDUSession" or session["info"]["version"] != "1.4.1":
        fail("TS 29.502 V19.7.0 Annex A.2 OpenAPI identity mismatch")
    if "3GPP TS 29.502 V19.7.0" not in session["externalDocs"]["description"]:
        fail("TS 29.502 official standard version mismatch")
    if common["openapi"] != "3.0.0" or common["info"]["title"] != "Common Data Types" or common["info"]["version"] != "1.6.2":
        fail("TS 29.571 V19.7.0 Annex A.2 OpenAPI identity mismatch")
    if "19.7.0" not in common["externalDocs"]["description"]:
        fail("TS 29.571 official standard version mismatch")

    operations = [
        (path, method.lower(), operation)
        for path, methods in session["paths"].items()
        for method, operation in methods.items()
        if isinstance(operation, dict) and operation.get("operationId") == "UpdateSmContext"
    ]
    if len(operations) != 1:
        fail("expected exactly one UpdateSmContext operation")
    path, method, operation = operations[0]
    if (method, path) != ("post", "/sm-contexts/{smContextRef}/modify"):
        fail("UpdateSmContext HTTP method/path mismatch")

    request_schema = session["components"]["schemas"]["SmContextUpdateData"]
    response_schema = session["components"]["schemas"]["SmContextUpdatedData"]
    request_fields = ("n1SmMsg", "n2SmInfo", "n2SmInfoType", "n2SmInfoExt1", "n2SmInfoTypeExt1")
    response_fields = ("n1SmMsg", "n2SmInfo", "n2SmInfoType", "cause")
    for schema, fields, label in (
        (request_schema, request_fields, "request"),
        (response_schema, response_fields, "response"),
    ):
        if not set(fields) <= set(schema["properties"]):
            fail(f"UpdateSmContext {label} schema is missing mapped fields")

    common_ref = "TS29571_CommonData.yaml#/components/schemas/RefToBinaryData"
    request_external = ("n1SmMsg", "n2SmInfo", "n2SmInfoExt1")
    response_external = ("n1SmMsg", "n2SmInfo")
    for schema, fields, label in (
        (request_schema, request_external, "request"),
        (response_schema, response_external, "response"),
    ):
        for field in fields:
            if schema["properties"][field].get("$ref") != common_ref:
                fail(f"UpdateSmContext {label}.{field} does not resolve to pinned TS 29.571 RefToBinaryData")
    ref_to_binary = common["components"]["schemas"]["RefToBinaryData"]
    if ref_to_binary.get("type") != "object" or "contentId" not in ref_to_binary.get("required", []):
        fail("RefToBinaryData.contentId must be a required property")
    if ref_to_binary["properties"]["contentId"].get("type") != "string":
        fail("RefToBinaryData.contentId must be string-valued")

    request_content = operation["requestBody"]["content"]
    response_content = operation["responses"]["200"]["content"]
    for content, label in ((request_content, "request"), (response_content, "response 200")):
        if not {"application/json", "multipart/related"} <= set(content):
            fail(f"UpdateSmContext {label} must support JSON and multipart/related")
    request_parts = set(request_content["multipart/related"]["schema"]["properties"])
    response_parts = set(response_content["multipart/related"]["schema"]["properties"])
    if not {"jsonData", "binaryDataN1SmMessage", "binaryDataN2SmInformation", "binaryDataN2SmInformationExt1"} <= request_parts:
        fail("UpdateSmContext request multipart parts do not match TS 29.502 V19.7.0")
    if not {"jsonData", "binaryDataN1SmMessage", "binaryDataN2SmInformation"} <= response_parts:
        fail("UpdateSmContext response multipart parts do not match TS 29.502 V19.7.0")

    closure = dependency["operationSchemaClosure"]
    if closure["operationId"] != "UpdateSmContext" or closure["httpMethod"] != "POST" or closure["path"] != path:
        fail("lock operationSchemaClosure identity mismatch")
    if tuple(closure["requestExternalRefFields"]) != request_external:
        fail("lock request external-reference field set mismatch")
    if tuple(closure["responseExternalRefFields"]) != response_external:
        fail("lock response external-reference field set mismatch")
    if closure["externalDocuments"] != ["TS29571_CommonData.yaml"]:
        fail("lock external Schema artifact list mismatch")
    if closure["refSchema"] != "/components/schemas/RefToBinaryData":
        fail("lock RefToBinaryData pointer mismatch")

    print("Official ETSI TS 29.502 / TS 29.571 V19.7.0 byte locks: PASS")
    print("TS 29.502 OpenAPI: 3.0.0 / 1.4.1; TS 29.571 CommonData: 3.0.0 / 1.6.2")
    print("UpdateSmContext: POST /sm-contexts/{smContextRef}/modify")
    print("Request multipart parts:", sorted(request_parts))
    print("Response 200 multipart parts:", sorted(response_parts))
    print("RefToBinaryData.contentId and mapped external Schema closure: PASS")
    print("Production Admission: BLOCKED pending real Owner Schema Closure and Adapter qualification")


if __name__ == "__main__":
    main()
