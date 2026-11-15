#!/usr/bin/env python3
"""Repository-local source hygiene for the official ConnectionAgent Skills.

This command deliberately does not invoke Compiler, Runtime, Qualification,
Git, MCP or any external repository. Language conformance belongs to the
target ca-skill-compiler; this script checks package/source hygiene only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from verify_v1alpha4_examples import validate_example_scripts

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
EXAMPLE_SKILLS = ("establish-pdu-session", "establish-pdu-session-mas")
EXAMPLE_SKILLS_ROOT = ROOT / "examples" / "skills"
ASSURANCE_FILES = ("contract.yaml", "procedure.yaml", "predicates.yaml")
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


def validate_v1alpha4_example(skill_name: str, errors: list[str]) -> None:
    """Author-source *shape* gate only; no external Owner/Schema linking."""
    skill = EXAMPLE_SKILLS_ROOT / skill_name
    if not skill.is_dir():
        errors.append(f"v1alpha4 example missing: {skill.relative_to(ROOT)}")
        return

    if not (skill / "SKILL.md").is_file():
        errors.append(f"{skill_name}: missing example SKILL.md")

    for name in ASSURANCE_FILES:
        if not (skill / "assurance" / name).is_file():
            errors.append(f"{skill_name}: missing assurance/{name}")
            return

    contract = (skill / "assurance" / "contract.yaml").read_text(encoding="utf-8")
    procedure = (skill / "assurance" / "procedure.yaml").read_text(encoding="utf-8")
    predicates = (skill / "assurance" / "predicates.yaml").read_text(encoding="utf-8")

    for field in ("goal", "precondition", "requestSchema", "contextSchema", "dependencies", "capabilities"):
        if not re.search(r"(?m)^" + field + r":\s*", contract):
            errors.append(f"{skill_name}: v1alpha4 Contract missing {field}")
    if not re.search(r"(?m)^start: [a-z][a-z0-9-]+$", procedure) or not re.search(r"(?m)^nodes:\s*$", procedure):
        errors.append(f"{skill_name}: v1alpha4 Procedure must have start and nodes")
    if not re.search(r"(?m)^predicates:\s*$", predicates):
        errors.append(f"{skill_name}: v1alpha4 PredicateSet must have predicates root")

    for path, body in (("contract", contract), ("procedure", procedure), ("predicates", predicates)):
        for field in ("apiVersion", "kind", "metadata", "entryProcedure", "preconditions", "postconditions"):
            if re.search(r"(?m)^\s*" + field + r":", body):
                errors.append(f"{skill_name}/{path}: legacy v0.x field {field}")
    for field in ("call", "with", "reconcile", "resolve", "verify", "on"):
        if re.search(r"(?m)^\s*" + field + r":", procedure):
            errors.append(f"{skill_name}: v1alpha4 Procedure cannot contain legacy {field}")
    # Example-level design decision: asynchronous completion belongs to
    # the Owner/Provider/SMF Operation, not an author-facing wait or poll Node.
    if re.search(r"(?m)^  (?:wait|await|poll)[-_a-z0-9]*:", procedure) or re.search(
        r"(?m)^\s*tool:\s*\S*(?:evidence\.await|\.wait|\.poll)(?:\b|$)", procedure
    ):
        errors.append(f"{skill_name}: Skill author must not declare wait/await/poll Nodes or Tool calls")
    if not re.search(r"(?m)^\s+PASS: SUCCEEDED\s*$", procedure):
        errors.append(f"{skill_name}: no final PASS: SUCCEEDED candidate")
    if not re.search(r"(?m)^\s+OUTCOME_UNKNOWN: (UNRESOLVED|SAFE_STOPPED)\s*$", procedure):
        errors.append(f"{skill_name}: no conservative Mutation uncertainty branch")

    request_path = skill / "schemas" / "establishment-request.schema.yaml"
    if not request_path.is_file():
        errors.append(f"{skill_name}: missing Skill-owned request Schema")
    else:
        request = request_path.read_text(encoding="utf-8")
        if re.search(r"(?m)^\s*(pattern|format|allOf|anyOf|oneOf|\$defs):", request):
            errors.append(f"{skill_name}: unsupported G.4 Schema keyword in request Schema")
        if "https://json-schema.org/draft/2020-12/schema" not in request:
            errors.append(f"{skill_name}: request Schema missing frozen Draft 2020-12 dialect")

    # v1alpha4 Script checks are local AST/closed-TypedDict/source hygiene only.
    validate_example_scripts(skill, errors)

    # This gate intentionally does not validate Owner exports/capabilities.
    # Their illustration-only urn:example identities MUST NOT be treated as
    # a real compiler link pass or an approved 5GC implementation.


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


def main() -> None:
    errors: list[str] = []
    if not SKILLS_ROOT.is_dir():
        raise SystemExit("skills/ directory is missing")

    packages = sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir())
    for skill in packages:
        validate_package_layout(skill, errors)

    for name in EXAMPLE_SKILLS:
        validate_v1alpha4_example(name, errors)

    catalog = ROOT / "lib" / "tools" / "createdsession.tool.yaml"
    if not catalog.is_file():
        errors.append("approved conventional PDU ToolCatalog snapshot is missing from lib/tools/")
    else:
        count = len(re.findall(r"(?m)^\s*-\s*operation:\s*", catalog.read_text(encoding="utf-8")))
        if count != 12:
            errors.append(f"expected 12 approved conventional PDU Operations in the pinned ToolCatalog, found {count}")

    validate_semantic_tokens(errors)
    fail(errors)

    print(f"PACKAGE_LAYOUT_OK ({len(packages)} historical Skill directories)")
    print("V1ALPHA4_EXAMPLE_SHAPE_OK (2 source examples; Owner links NOT_QUALIFIED)")
    print("V1ALPHA4_LOCAL_SCRIPT_SHAPE_PASS (typed signatures, path refs, closed Script bindings)")
    print("NOTE: external Owner/Context SourcePaths and historical Cases are not typechecked or executed")
    print("LEGACY_TOOL_CATALOG_SNAPSHOT_OK (12 Operations; not a v1alpha4 Owner publication)")
    print("SEMANTIC_TOKEN_REGISTRY_OK (v0.2.0)")
    print("SOURCE_HYGIENE_PASS")
    print("Note: source shape is NOT YAML/Owner linking, Compiler, Runtime, Qualification or live 5GC.")


if __name__ == "__main__":
    main()
