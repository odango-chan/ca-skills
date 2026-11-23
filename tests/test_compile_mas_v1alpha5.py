"""Input-admission tests for the official MAS / Compiler v2.0.2 bridge.

The real Compiler is invoked by scripts/compile_mas_v1alpha5.py; these
tests intentionally do not impersonate its static semantic validation.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compile_mas_v1alpha5.py"
SPEC = importlib.util.spec_from_file_location("compile_mas_v1alpha5", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CompilerProjectGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.skill = root / "skill"
        assurance = self.skill / "assurance"
        assurance.mkdir(parents=True)
        (assurance / "contract.yaml").write_text(
            "goal: test\n"
            "dependencies:\n"
            "  mas: urn:example:test:mas\n"
            "  ca-context: urn:example:test:context\n"
            "capabilities: []\n",
            encoding="utf-8",
        )
        (assurance / "predicates.yaml").write_text(
            "predicates: {}\n", encoding="utf-8"
        )
        self.trusted = root / "trusted"
        self.trusted.mkdir()
        for alias in ("mas", "ca-context"):
            snapshot = self.trusted / "snapshots" / alias
            snapshot.mkdir(parents=True)
            (snapshot / "contract.yaml").write_text("fixture: true\n", encoding="utf-8")
        (self.trusted / "capability").mkdir()
        (self.trusted / "capability" / "grant.yaml").write_text(
            "fixture: true\n", encoding="utf-8"
        )
        self.config = {
            "dependencyBindings": [
                {"dependencyId": "mas", "stablePackageId": "urn:example:test:mas"},
                {"dependencyId": "ca-context", "stablePackageId": "urn:example:test:context"},
            ],
            "deployment": {
                "capabilityDirectory": "capability",
                "authorizationRef": "urn:example:test:authorization",
            },
        }
        self._write_config()

    def _write_config(self) -> None:
        (self.trusted / "trusted.json").write_text(
            json.dumps(self.config), encoding="utf-8"
        )

    def test_fixture_inventory_uses_exact_alias_and_identity(self) -> None:
        inventory, errors = MODULE.validate_inputs(self.skill, self.trusted, "fixture")
        self.assertEqual(errors, [])
        self.assertEqual(
            inventory["dependencyAliases"],
            {"mas": "urn:example:test:mas", "ca-context": "urn:example:test:context"},
        )
        self.assertEqual(inventory["mode"], "fixture")

    def test_release_mode_rejects_example_dependencies(self) -> None:
        _, errors = MODULE.validate_inputs(self.skill, self.trusted, "release")
        self.assertTrue(any("urn:example" in error for error in errors), errors)

    def test_missing_snapshot_fails_closed(self) -> None:
        (self.trusted / "snapshots" / "mas" / "contract.yaml").unlink()
        _, errors = MODULE.validate_inputs(self.skill, self.trusted, "fixture")
        self.assertTrue(any("missing or empty snapshot" in e for e in errors), errors)

    def test_missing_owner_binding_fails_closed(self) -> None:
        self.config["dependencyBindings"] = self.config["dependencyBindings"][1:]
        self._write_config()
        _, errors = MODULE.validate_inputs(self.skill, self.trusted, "fixture")
        self.assertIn("unresolved dependency: mas", errors)

    def test_wrong_stable_package_id_fails_closed(self) -> None:
        self.config["dependencyBindings"][0]["stablePackageId"] = "urn:wrong:mas"
        self._write_config()
        _, errors = MODULE.validate_inputs(self.skill, self.trusted, "fixture")
        self.assertTrue(any("package identity mismatch" in e for e in errors), errors)

    def test_duplicate_binding_fails_closed(self) -> None:
        self.config["dependencyBindings"].append(
            dict(self.config["dependencyBindings"][0])
        )
        self._write_config()
        _, errors = MODULE.validate_inputs(self.skill, self.trusted, "fixture")
        self.assertIn("duplicate trusted dependencyBinding: mas", errors)

    def test_source_copied_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            MODULE.copy_project(self.skill, self.trusted, dest, self.config)
            self.assertEqual(
                (dest / "skills" / self.skill.name / "assurance" / "contract.yaml").read_bytes(),
                (self.skill / "assurance" / "contract.yaml").read_bytes(),
            )
            self.assertTrue((dest / "snapshots" / "mas" / "contract.yaml").is_file())
            self.assertTrue((dest / "capability" / "grant.yaml").is_file())

    def test_unsafe_bundle_directory_fails_closed(self) -> None:
        self.config["deployment"]["capabilityDirectory"] = "../outside"
        self._write_config()
        _, errors = MODULE.validate_inputs(self.skill, self.trusted, "fixture")
        self.assertTrue(any("unsafe deployment bundle" in e for e in errors), errors)


    def test_official_mas_skills_share_the_published_owner_package_identity(self) -> None:
        expected = "urn:openamsm:mas:tool-contracts"
        for skill_name in MODULE.SKILLS:
            contract = (
                MODULE.REPO / "examples" / "skills" / skill_name
                / "assurance" / "contract.yaml"
            ).read_text(encoding="utf-8")
            aliases = MODULE.dependency_aliases(contract)
            self.assertEqual(aliases["mas"], expected, skill_name)


if __name__ == "__main__":
    unittest.main()
