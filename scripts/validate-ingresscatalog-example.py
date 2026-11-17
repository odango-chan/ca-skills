#!/usr/bin/env python3
"""Validate the documented IngressCatalog example against its structural schema."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/design/integration-ingress-operation-contract-vnext.zh-CN.md"
SCHEMA = ROOT / "docs/design/schemas/ingresscatalog.v1alpha1.schema.json"


def load_example() -> dict:
    text = DOC.read_text(encoding="utf-8")
    blocks = re.findall(r"~~~yaml\s*\n(.*?)\n~~~", text, flags=re.DOTALL)
    candidates = [block for block in blocks if "kind: IngressCatalog" in block]
    if len(candidates) != 1:
        raise SystemExit(f"expected exactly one IngressCatalog YAML example, found {len(candidates)}")
    value = yaml.safe_load(candidates[0])
    if not isinstance(value, dict):
        raise SystemExit("IngressCatalog example must be a YAML mapping")
    return value


def validate_semantics(catalog: dict) -> None:
    operations = catalog["spec"]["operations"]
    for operation in operations:
        request = operation["request"]
        accepted = request["acceptedMediaTypes"]
        source_types = [item["mediaType"] for item in request["sourceSchemas"]]
        representation_types = [item["mediaType"] for item in request["normalization"]["representations"]]
        for label, values in (
            ("sourceSchemas", source_types),
            ("normalization.representations", representation_types),
        ):
            if len(values) != len(set(values)) or set(values) != set(accepted):
                raise SystemExit(
                    f"{operation['id']}: {label} media types must match acceptedMediaTypes exactly once"
                )

        response = operation["response"]
        if response["mode"] == "paired":
            dispositions = response["dispositions"]
            ids = [item["id"] for item in dispositions]
            statuses = [item["status"] for item in dispositions]
            if len(ids) != len(set(ids)):
                raise SystemExit(f"{operation['id']}: duplicate response disposition id")
            if len(statuses) != len(set(statuses)):
                raise SystemExit(f"{operation['id']}: duplicate response HTTP status")
            result = response.get("result")
            if result:
                declared = set(ids)
                mapped = {item["dispositionId"] for item in result.get("mappings", [])}
                selected = {
                    item["dispositionId"]
                    for item in result.get("dispositionSelector", {}).get("cases", [])
                }
                if not mapped <= declared or not selected <= declared:
                    raise SystemExit(f"{operation['id']}: response mapping/selector references unknown disposition")
                if len(selected) != len(result.get("dispositionSelector", {}).get("cases", [])):
                    raise SystemExit(f"{operation['id']}: duplicate disposition selector value")
                if any(item["body"] == "required" and item["id"] not in mapped for item in dispositions):
                    raise SystemExit(f"{operation['id']}: body-bearing disposition has no response mapping")


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
    print("IngressCatalog schema and cross-field example checks: PASS")


if __name__ == "__main__":
    main()
