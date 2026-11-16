"""Regression coverage for local v1alpha4 Script shape and closed-TypedDict links."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_v1alpha4_examples import validate_example_scripts, validate_3gpp_traceability

SOURCE_PROCEDURE = """start: produce
nodes:
  produce:
    operation:
      script: scripts/produce.py
      arguments:
        x: context.x
      routes:
        SUCCEEDED: consume
        FAILED: FAILED
  consume:
    operation:
      script: scripts/consume.py
      arguments:
        data: produce.operation.output.data
      routes:
        SUCCEEDED: FAILED
        FAILED: FAILED
"""
PRODUCER = """from __future__ import annotations
from typing import TypedDict
class Source(TypedDict):
    a: int
    b: int
class Input(TypedDict):
    x: int
class Output(TypedDict):
    data: Source
def main(input: Input) -> Output:
    return {"data": {"a": input["x"], "b": input["x"]}}
"""
CONSUMER_CLOSED_MISMATCH = """from __future__ import annotations
from typing import TypedDict
class Target(TypedDict):
    a: int
class Input(TypedDict):
    data: Target
class Output(TypedDict):
    ok: bool
def main(input: Input) -> Output:
    return {"ok": True}
"""
CONSUMER_MATCHED = CONSUMER_CLOSED_MISMATCH.replace(
    "    a: int\nclass Input", "    a: int\n    b: int\nclass Input"
)

class V1Alpha4ScriptTests(unittest.TestCase):
    def lint(self, source: str = SOURCE_PROCEDURE,
             producer: str = PRODUCER,
             consumer: str = CONSUMER_MATCHED,
             unused: bool = False) -> list[str]:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text(source, encoding="utf-8")
            (root / "scripts" / "produce.py").write_text(producer, encoding="utf-8")
            (root / "scripts" / "consume.py").write_text(consumer, encoding="utf-8")
            if unused:
                (root / "scripts" / "unused.py").write_text(PRODUCER, encoding="utf-8")
            errors: list[str] = []
            validate_example_scripts(root, errors)
            return errors

    def test_every_procedure_node_requires_3gpp_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text(
                "start: retrieve\\nnodes:\\n  # 3GPP: 3GPP_NATIVE — TS 23.502 step 4\\n  retrieve:\\n    operation: {}\\n",
                encoding="utf-8",
            )
            (root / "SKILL.md").write_text(
                "## 3GPP Traceability\\n\\nTS 23.502 V18.12.0\\n"
                "| Procedure Node | Mapping |\\n|---|---|\\n| \\x60retrieve\\x60 | step 4 |\\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertEqual(errors, [])

    def test_missing_node_mapping_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text(
                "start: retrieve\\nnodes:\\n  retrieve:\\n    operation: {}\\n",
                encoding="utf-8",
            )
            (root / "SKILL.md").write_text(
                "## 3GPP Traceability\\nTS 23.502 V18.12.0\\n"
                "| Procedure Node | Mapping |\\n|---|---|\\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertTrue(any("missing adjacent" in error for error in errors), errors)
            self.assertTrue(any("missing SKILL.md" in error for error in errors), errors)

    def test_closed_nested_typed_dict_matches(self) -> None:
        self.assertEqual(self.lint(), [])

    def test_extra_source_key_is_input_type_mismatch(self) -> None:
        errors = self.lint(consumer=CONSUMER_CLOSED_MISMATCH)
        self.assertTrue(any("INPUT_TYPE_MISMATCH" in e for e in errors), errors)

    def test_unsafe_script_path_and_dead_code(self) -> None:
        errors = self.lint(source=SOURCE_PROCEDURE.replace(
            "scripts/consume.py", "scripts/../escape.py"
        ))
        self.assertTrue(any("unsafe Script ref" in e for e in errors), errors)
        errors = self.lint(unused=True)
        self.assertTrue(any("unreferenced Script" in e for e in errors), errors)

    def test_missing_script_and_wrong_signature(self) -> None:
        errors = self.lint(source=SOURCE_PROCEDURE.replace(
            "scripts/consume.py", "scripts/missing.py"
        ))
        self.assertTrue(any("Script not found" in e for e in errors), errors)
        errors = self.lint(producer=PRODUCER.replace(
            "def main(input: Input)", "def main(input: dict)"
        ))
        self.assertTrue(any("strict TypedDict" in e or "unresolved/recursive" in e for e in errors), errors)

    def test_ambient_import_is_rejected(self) -> None:
        errors = self.lint(producer="import os\n" + PRODUCER)
        self.assertTrue(any("forbidden external/ambient import" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
