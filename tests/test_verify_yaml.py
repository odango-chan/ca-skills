"""Strict YAML parsing and CA-SL v1alpha4 G.4 Schema regression checks."""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_SKILLS_ROOT = ROOT / "examples" / "skills"
V1ALPHA4_DIALECT = "https://json-schema.org/draft/2020-12/schema"
FORBIDDEN_G4_SCHEMA_KEYS = {"pattern", "format", "allOf", "anyOf", "oneOf", "$defs"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys instead of overwriting them."""


def _construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    loader.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _load_yaml(path: Path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def _mapping_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _mapping_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _mapping_keys(child)


class V1Alpha4YamlTests(unittest.TestCase):
    def test_all_example_skill_yaml_parses_without_duplicate_keys(self) -> None:
        paths = sorted(EXAMPLE_SKILLS_ROOT.rglob("*.yaml"))
        self.assertTrue(paths, "no example Skill YAML files found")
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIsNotNone(_load_yaml(path))

    def test_request_schemas_use_frozen_dialect_and_g4_keywords(self) -> None:
        paths = sorted(EXAMPLE_SKILLS_ROOT.glob("*/schemas/*.schema.yaml"))
        self.assertEqual(len(paths), 2, [str(path.relative_to(ROOT)) for path in paths])
        schema_ids = set()
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                document = _load_yaml(path)
                self.assertEqual(document.get("$schema"), V1ALPHA4_DIALECT)
                self.assertEqual(document.get("type"), "object")
                self.assertIs(document.get("additionalProperties"), False)
                schema_id = document.get("$id")
                self.assertTrue(schema_id)
                self.assertNotIn(schema_id, schema_ids)
                schema_ids.add(schema_id)
                forbidden = sorted(set(_mapping_keys(document)) & FORBIDDEN_G4_SCHEMA_KEYS)
                self.assertEqual(forbidden, [], f"unsupported G.4 keywords: {forbidden}")


if __name__ == "__main__":
    unittest.main()
