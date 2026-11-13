#!/usr/bin/env python3
"""Repository-local source hygiene for the official ConnectionAgent Skills.

This command deliberately does not invoke Compiler, Runtime, Qualification,
Git, MCP or any external repository. Language conformance belongs to the
target ca-skill-compiler; this script checks package/source hygiene only.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
CURRENT_SKILLS = ("establish-pdu-session", "establish-pdu-session-mas")
ASSURANCE_FILES = ("contract.yaml", "procedure.yaml", "predicates.yaml")
SCRIPT_REF_RE = re.compile(r"(?m)^\s*(?:script|ref):\s*(scripts/[^\s#]+)\s*(?:#.*)?$")
RUN_PRODUCED_FACT_IDS = ("virtual_group.id",)


def fail(errors: list[str]) -> None:
    if errors:
        raise SystemExit("\n".join(errors))


def validate_package_layout(skill: Path, errors: list[str]) -> None:
    if not (skill / "SKILL.md").is_file():
        errors.append(f"{skill.relative_to(ROOT)}: missing SKILL.md")

    assurance = skill / "assurance"
    if assurance.exists():
        if not assurance.is_dir():
            errors.append(f"{skill.name}: assurance must be a directory")
        else:
            present = {name for name in ASSURANCE_FILES if (assurance / name).is_file()}
            if present and present != set(ASSURANCE_FILES):
                missing = ", ".join(sorted(set(ASSURANCE_FILES) - present))
                errors.append(f"{skill.name}: partial assurance package; missing {missing}")
            if not present:
                errors.append(f"{skill.name}: empty assurance/ is ambiguous; remove it or provide the complete contract/procedure/predicates trio")
            if (assurance / "evidence.yaml").exists():
                errors.append(f"{skill.name}: legacy assurance/evidence.yaml is forbidden; observations and predicates belong in predicates.yaml")

            procedure = assurance / "procedure.yaml"
            if procedure.is_file():
                source = procedure.read_text(encoding="utf-8")
                for fact_id in RUN_PRODUCED_FACT_IDS:
                    if re.search(r"from:\s*context\.facts\." + re.escape(fact_id) + r"\b", source):
                        errors.append(f"{skill.name}: run-produced fact '{fact_id}' must bind from its producing node output, not context.facts")

    for obsolete in ("README.md", "MIGRATION.md"):
        if (skill / obsolete).exists():
            errors.append(f"{skill.name}: {obsolete} is not a canonical package-root entrypoint; keep model-facing semantics in SKILL.md")
    if (skill / "examples").exists():
        errors.append(f"{skill.name}: examples/ is forbidden; explanatory material belongs in references/")

    cases = skill / "cases"
    if cases.is_dir():
        legacy_case_files = ("planning-context.yaml", "mock-outcomes.yaml", "mock-predicates.yaml", "expected.yaml", "evaluation-scenario.yaml")
        for name in legacy_case_files:
            for path in cases.glob("*/" + name):
                errors.append(f"{path.relative_to(ROOT)}: consolidate case source into case.yaml")


def typed_dict_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if any(isinstance(base, ast.Name) and base.id == "TypedDict" for base in node.bases):
                names.add(node.name)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Name) and call.func.id == "TypedDict":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
    return names


def validate_script(path: Path, errors: list[str]) -> None:
    source = path.read_text(encoding="utf-8")
    if "connectionagent-tool" in source:
        errors.append(f"{path.relative_to(ROOT)}: legacy connectionagent-tool metadata is forbidden")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        errors.append(f"{path.relative_to(ROOT)}:{error.lineno}:{error.offset}: Python syntax error: {error.msg}")
        return

    mains = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"]
    if len(mains) != 1 or not isinstance(mains[0], ast.FunctionDef):
        errors.append(f"{path.relative_to(ROOT)}: expected exactly one synchronous main(input: dict) -> OutputTypedDict")
        return

    main = mains[0]
    args = main.args
    positional = [*args.posonlyargs, *args.args]
    if (
        len(positional) != 1
        or positional[0].arg != "input"
        or not isinstance(positional[0].annotation, ast.Name)
        or positional[0].annotation.id != "dict"
        or args.vararg is not None
        or args.kwarg is not None
        or args.kwonlyargs
        or args.defaults
        or args.kw_defaults
    ):
        errors.append(f"{path.relative_to(ROOT)}: entry point must be exactly main(input: dict)")
    if not isinstance(main.returns, ast.Name) or main.returns.id not in typed_dict_names(tree):
        errors.append(f"{path.relative_to(ROOT)}: main return annotation must name a TypedDict declared in the same file")


def validate_current_skill(skill_name: str, errors: list[str]) -> None:
    skill = SKILLS_ROOT / skill_name
    if not skill.is_dir():
        errors.append(f"current official Skill package missing: {skill_name}")
        return

    assurance = skill / "assurance"
    for required in ASSURANCE_FILES:
        if not (assurance / required).is_file():
            errors.append(f"{skill_name}: missing assurance/{required}")

    contract = (assurance / "contract.yaml").read_text(encoding="utf-8")
    if "localTools:" in contract or "allowedResources:\n    localTools:" in contract:
        errors.append(f"{skill_name}: allowedResources.localTools is not part of the current language")
    request_match = re.search(r"(?m)^\s*requestSchema:\s*(\S+)\s*$", contract)
    if not request_match or not (skill / request_match.group(1)).is_file():
        errors.append(f"{skill_name}: requestSchema must reference an existing Skill-owned schema")

    procedure_path = assurance / "procedure.yaml"
    procedure = procedure_path.read_text(encoding="utf-8")
    if re.search(r"(?m)^\s*tool\s*:", procedure):
        errors.append(f"{skill_name}: tool is not a supported Procedure action")
    for match in SCRIPT_REF_RE.finditer(procedure):
        relative = match.group(1)
        candidate = (skill / relative).resolve()
        try:
            candidate.relative_to(skill.resolve())
        except ValueError:
            errors.append(f"{skill_name}: Script path escapes Skill package: {relative}")
            continue
        if not candidate.is_file():
            errors.append(f"{skill_name}: referenced Script does not exist: {relative}")

    predicates_path = assurance / "predicates.yaml"
    predicates = predicates_path.read_text(encoding="utf-8")
    for match in SCRIPT_REF_RE.finditer(predicates):
        relative = match.group(1)
        candidate = (skill / relative).resolve()
        try:
            candidate.relative_to(skill.resolve())
        except ValueError:
            errors.append(f"{skill_name}: Predicate Script path escapes Skill package: {relative}")
            continue
        if not candidate.is_file():
            errors.append(f"{skill_name}: referenced Predicate Script does not exist: {relative}")

    scripts = skill / "scripts"
    if scripts.is_dir():
        for path in sorted(scripts.rglob("*.py")):
            validate_script(path, errors)

    schemas = skill / "schemas"
    if schemas.is_dir():
        for path in schemas.rglob("*-input.schema.*"):
            errors.append(f"{path.relative_to(ROOT)}: Script input schemas are derived, not authored")
        for path in schemas.rglob("*-evaluation-input.schema.*"):
            errors.append(f"{path.relative_to(ROOT)}: Predicate Script input schemas are derived, not authored")


def validate_semantic_tokens(errors: list[str]) -> None:
    path = ROOT / "language" / "semantic-tokens.v1.json"
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"semantic-token registry cannot be read: {error}")
        return

    token_types = {item.get("id") for item in registry.get("legend", {}).get("tokenTypes", [])}
    if registry.get("version") != "0.2.0":
        errors.append("semantic-token registry version must be 0.2.0")
    if "skillTool" in token_types:
        errors.append("semantic-token registry must not define the removed local Tool token")
    used = {
        rule.get("type")
        for profile in registry.get("profiles", {}).values()
        for rule in profile.get("rules", [])
    }
    missing = sorted(item for item in used if item not in token_types)
    if missing:
        errors.append("semantic-token rules use undefined token types: " + ", ".join(missing))

    procedure = registry.get("profiles", {}).get("procedure", {})
    main_keywords = procedure.get("keywords", {}).get("procedures/*/nodes/*", [])
    step_keywords = procedure.get("keywords", {}).get("procedures/*/nodes/*/preconditions/steps/*", [])
    if "tool" in main_keywords or "tool" in step_keywords or "procedure" in step_keywords:
        errors.append("semantic-token registry exposes an unsupported Procedure action")
    call_rules = [
        rule for rule in procedure.get("rules", [])
        if rule.get("path", "").endswith("/call") and rule.get("part") == "value"
    ]
    if not call_rules or any(rule.get("type") != "skillOperation" for rule in call_rules):
        errors.append("call scalar values must use the skillOperation semantic token")

    contract = registry.get("profiles", {}).get("contract", {})
    if "schemas" not in contract.get("keywords", {}).get("spec/context", []):
        errors.append("semantic-token registry must classify spec.context.schemas")
    if "localTools" in contract.get("keywords", {}).get("spec/allowedResources", []):
        errors.append("semantic-token registry must not expose allowedResources.localTools")

    predicates = registry.get("profiles", {}).get("predicates", {})
    if not any(rule.get("path") == "predicates/*/evaluator/ref" for rule in predicates.get("rules", [])):
        errors.append("semantic-token registry must classify Predicate evaluator.ref")


def validate_udm_owner_output_schema(errors: list[str]) -> None:
    """Keep the ToolCatalog result projection byte-for-byte aligned with its Owner Schema export."""
    schema_path = ROOT / "lib" / "schemas" / "ca" / "createdsession-udm-runtime-value-v1alpha1.schema.yaml"
    catalog_path = ROOT / "lib" / "tools" / "createdsession.tool.yaml"
    if not schema_path.is_file():
        errors.append("Host-owned normalized UDM READ result Schema is missing from lib/schemas/ca/")
        return
    if not catalog_path.is_file():
        return

    schema_text = schema_path.read_text(encoding="utf-8").rstrip("\\n")
    schema_id = re.search(r"(?m)^\\$id:\\s*(\\S+)\\s*$", schema_text)
    if not schema_id:
        errors.append("Host-owned normalized UDM READ result Schema must declare an exact $id")
        return

    catalog_text = catalog_path.read_text(encoding="utf-8")
    operation = re.search(
        r"(?ms)^  - operation: sbi\\.udm\\.sm_data\\.get\\n(?P<body>.*?)(?=^  - operation:|\\Z)",
        catalog_text,
    )
    if not operation:
        errors.append("ToolCatalog is missing sbi.udm.sm_data.get")
        return
    body = operation.group("body")
    if not re.search(r"(?m)^    effect: READ\\s*$", body):
        errors.append("sbi.udm.sm_data.get must remain a READ Operation")
    result = re.search(r"(?m)^        result:\\s*$", body)
    if not result:
        errors.append("sbi.udm.sm_data.get outputSchema.result must embed the Host-owned UDM Schema")
        return

    embedded_lines = []
    for line in body[result.end():].splitlines():
        if not line.strip():
            embedded_lines.append("")
            continue
        if not line.startswith("          "):
            break
        embedded_lines.append(line[10:])
    embedded = "\\n".join(embedded_lines).rstrip("\\n")
    if embedded != schema_text:
        errors.append(
            "sbi.udm.sm_data.get outputSchema.result must exactly match "
            "lib/schemas/ca/createdsession-udm-runtime-value-v1alpha1.schema.yaml"
        )


def main() -> None:
    errors: list[str] = []
    if not SKILLS_ROOT.is_dir():
        raise SystemExit("skills/ directory is missing")

    packages = sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir())
    for skill in packages:
        validate_package_layout(skill, errors)

    for name in CURRENT_SKILLS:
        validate_current_skill(name, errors)

    catalog = ROOT / "lib" / "tools" / "createdsession.tool.yaml"
    if not catalog.is_file():
        errors.append("approved conventional PDU ToolCatalog snapshot is missing from lib/tools/")
    else:
        count = len(re.findall(r"(?m)^\s*-\s*operation:\s*", catalog.read_text(encoding="utf-8")))
        if count != 12:
            errors.append(f"expected 12 approved conventional PDU Operations in the pinned ToolCatalog, found {count}")

    validate_semantic_tokens(errors)
    validate_udm_owner_output_schema(errors)
    fail(errors)

    print(f"PACKAGE_LAYOUT_OK ({len(packages)} Skill directories)")
    print("CURRENT_5GC_SOURCE_OK (2 official packages)")
    print("SCRIPT_CONTRACT_SHAPE_OK")
    print("IMPORTED_TOOL_CATALOG_OK (12 Operations)")
    print("SEMANTIC_TOKEN_REGISTRY_OK (v0.2.0)")
    print("SOURCE_HYGIENE_PASS")
    print("Note: this gate does not run Compiler, Runtime, Qualification or live 5GC.")


if __name__ == "__main__":
    main()
