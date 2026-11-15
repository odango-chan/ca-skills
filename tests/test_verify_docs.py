"""Regression tests for the v1alpha4 documentation structure gate."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_docs  # noqa: E402


class SpecMarkdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = verify_docs.SPEC.read_text(encoding="utf-8")

    def lint(self, text: str) -> list[str]:
        errors: list[str] = []
        verify_docs.check_all_markdown_tables(text, errors)
        verify_docs.check_counts(text, errors)
        return errors

    def test_checked_in_spec_is_valid(self) -> None:
        self.assertEqual(self.lint(self.spec), [])

    def test_one_two_three_blank_lines_split_e9(self) -> None:
        pattern = r"(?m)(^\| E89 \|[^\n]*\n)(\| E90 \|)"
        self.assertEqual(len(re.findall(pattern, self.spec)), 1)
        for n in (1, 2, 3):
            with self.subTest(blank_lines=n):
                altered = re.sub(pattern, lambda m: m.group(1) + "\n" * n + m.group(2), self.spec)
                errors = self.lint(altered)
                self.assertTrue(errors, f"E.9 split by {n} blank lines escaped lint")
                self.assertTrue(any("separator" in x for x in errors), errors)

    def test_e5_table_split_is_detected(self) -> None:
        a = self.spec.index("## E.5 ")
        b = self.spec.index("## E.6 ", a)
        subsection = self.spec[a:b]
        pattern = r"(?m)(^\| E\d{2}\b[^\n]*\n)(\| E\d{2}\b)"
        self.assertIsNotNone(re.search(pattern, subsection), "Expected adjacent E.5 cases")
        broken = re.sub(pattern, lambda m: m.group(1) + "\n\n" + m.group(2), subsection, count=1)
        errors = self.lint(self.spec[:a] + broken + self.spec[b:])
        self.assertTrue(any("separator" in x for x in errors), errors)

    def test_column_mismatch_is_detected(self) -> None:
        pattern = r"(?m)^(\| E90 \|[^\n]*)(\|)$"
        self.assertEqual(len(re.findall(pattern, self.spec)), 1)
        broken = re.sub(pattern, r"\1 |", self.spec, count=1)
        errors = self.lint(broken)
        self.assertTrue(any("column count" in x for x in errors), errors)

    def test_h_text_claim_must_match_98_codes_and_99_pairs(self) -> None:
        pattern = r"(下表包含\s*)98( 个唯一 Code、)99( 条唯一)"
        self.assertEqual(len(re.findall(pattern, self.spec)), 1)
        broken = re.sub(pattern, r"\g<1>97\g<2>99\g<3>", self.spec, count=1)
        errors = self.lint(broken)
        self.assertTrue(any("textual" in x for x in errors), errors)

    def test_pipe_text_inside_fence_is_not_a_table(self) -> None:
        errors: list[str] = []
        verify_docs.check_all_markdown_tables("~~~yaml\n| not a Markdown table |\n~~~\n", errors)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
