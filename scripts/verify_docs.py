#!/usr/bin/env python3
"""Structural lint for the frozen CA-SL v1alpha4 single-file specification.

Checks Markdown structure and frozen index counts only. This is NOT a
Compiler/Studio/Runtime/Owner/5GC conformance or fixture runner.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "skill-language-spec.v1alpha4.zh-CN.md"
ENTRY = ROOT / "docs" / "skill-language-spec.md"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def slice_between(text: str, left: str, right: str) -> str:
    if text.count(left) != 1 or text.count(right) != 1:
        raise ValueError("expected one section boundary: " + left + " / " + right)
    return text.split(left, 1)[1].split(right, 1)[0]


def check_fences(lines: list[str], errors: list[str]) -> None:
    # Accept both Markdown backtick and tilde fences, including info strings.
    token = re.escape(chr(96))
    fence_pattern = re.compile(r"^ {0,3}((?:" + token + r"){3,}|~{3,})(.*)$")
    opened: tuple[str, int, int] | None = None
    for line_number, line in enumerate(lines, 1):
        match = fence_pattern.match(line)
        if match is None:
            continue
        fence, suffix = match.groups()
        if opened is None:
            opened = (fence[0], len(fence), line_number)
        elif fence[0] == opened[0] and len(fence) >= opened[1] and not suffix.strip():
            opened = None
    require(opened is None, "unclosed Markdown code fence at line " + str(opened[2]) if opened else "", errors)


def check_sections(text: str, errors: list[str]) -> None:
    require(text.rstrip().endswith("**全文结束。**"), "complete-spec end marker is missing", errors)
    for letter in "EFGHIJK":
        require(
            re.search(r"(?m)^# 附录 " + letter + r"[：:]", text) is not None,
            "missing Appendix " + letter,
            errors,
        )
    for number in range(1, 15):
        require(
            re.search(r"(?m)^## E\." + str(number) + r"\s", text) is not None,
            "missing or incorrectly nested E." + str(number) + " heading",
            errors,
        )
    require(
        re.search(r"(?m)^## H\.0\s", text) is not None,
        "H.0 must be a Markdown section heading",
        errors,
    )
    incorrect = re.findall(r"(?m)^## (\d+\.\d+(?:\.\d+)*)\s", text)
    require(not incorrect, "numbered subsection heading level incorrect: " + ", ".join(incorrect), errors)
    headings = set(re.findall(r"(?m)^#{1,6}\s+(\d+(?:\.\d+)*)(?=[.\s]|$)", text))
    references = set(re.findall(r"§(\d+(?:\.\d+)*)", text))
    unknown = sorted(references - headings)
    require(not unknown, "unresolved numbered section references: " + ", ".join(unknown), errors)


def check_table(text: str, head: str, tail: str, first_id: int, last_id: int, columns: int, errors: list[str]) -> None:
    try:
        segment = slice_between(text, head, tail)
    except ValueError as exc:
        errors.append(str(exc))
        return
    all_lines = segment.splitlines()
    rows = [line for line in all_lines if line.startswith("|")]
    expected_ids = ["E" + str(number) for number in range(first_id, last_id + 1)]
    ids = [re.match(r"^\|\s*(E\d+)\s*\|", line) for line in rows[2:]]
    actual_ids = [match.group(1) if match else "" for match in ids]
    require(
        actual_ids == expected_ids,
        head + ": unexpected E row identifiers or missing table rows",
        errors,
    )
    require(len(rows) == len(expected_ids) + 2, head + ": table header/separator or row count wrong", errors)
    for row in rows:
        require(
            row.endswith("|") and len(row.split("|")) - 2 == columns,
            head + ": table has wrong number of columns: " + row[:95],
            errors,
        )
    for index in range(1, len(all_lines) - 1):
        if not all_lines[index].strip() and all_lines[index - 1].startswith("|") and all_lines[index + 1].startswith("|"):
            errors.append(head + ": blank line splits a Markdown table")
            break


def check_counts(text: str, errors: list[str]) -> None:
    check_table(text, "## E.9 补充符合性用例", "## E.10 单数", 67, 91, 3, errors)
    check_table(text, "## E.14 扩展符合性用例", "# 附录 F", 98, 104, 2, errors)

    if "| Code | Phase |" not in text:
        errors.append("missing Appendix H diagnostic table")
    else:
        after = text.split("| Code | Phase |", 1)[1].splitlines()
        rows: list[str] = []
        for line in after[2:]:
            if not line.startswith("|"):
                break
            rows.append(line)
        pairs = [(row.split("|")[1].strip(), row.split("|")[2].strip()) for row in rows]
        require(len(rows) == 99, "Appendix H must have 99 diagnostic rows", errors)
        require(len(set(pairs)) == 99, "Appendix H (Code, Phase) identities must be unique", errors)
        require(len(set(code for code, _ in pairs)) == 98, "Appendix H must have 98 unique Codes", errors)

    try:
        k1 = slice_between(text, "## K.1 E01", "## K.2 诊断 Fixture")
        k2 = slice_between(text, "## K.2 诊断 Fixture", "### K.2.0")
    except ValueError as exc:
        errors.append(str(exc))
        return
    e_ids = re.findall(r"(?m)^\|\s*(E\d{2,3})\s*\|", k1)
    dfx = re.findall(r"(?m)^\|\s*(DFX-\d{3})\s*\|", k2)
    require(e_ids == ["E" + str(n).zfill(2) for n in range(1, 121)], "K.1 must enumerate E01–E120 once, in order", errors)
    require(dfx == ["DFX-" + str(n).zfill(3) for n in range(1, 42)], "K.2 must enumerate DFX-001–041 once, in order", errors)


def main() -> None:
    errors: list[str] = []
    if not SPEC.is_file() or not ENTRY.is_file():
        raise SystemExit("DOC_STRUCTURE_FAIL: normative specification or index is missing")
    text = SPEC.read_text(encoding="utf-8")
    index = ENTRY.read_text(encoding="utf-8")
    require(
        "skill-language-spec.v1alpha4.zh-CN.md" in index and "connectionagent.io/v1alpha4" in index,
        "current language index must reference frozen v1alpha4, not v1alpha3",
        errors,
    )
    check_fences(text.splitlines(), errors)
    check_sections(text, errors)
    check_counts(text, errors)
    if errors:
        raise SystemExit("DOC_STRUCTURE_FAIL\n" + "\n".join(errors))
    print("DOC_STRUCTURE_PASS (fences / headings / § references / E tables / H and K counts)")
    print("Note: document structure checks are not Compiler, Studio, Host or Owner qualification.")


if __name__ == "__main__":
    main()
