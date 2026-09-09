#!/usr/bin/env python3
"""Validate repository-local Skill package layout without duplicating compiler semantics."""
import argparse
from pathlib import Path


ASSURANCE_FILES = ("contract.yaml", "procedure.yaml", "predicates.yaml")
LEGACY_CASE_FILES = (
    "planning-context.yaml",
    "mock-outcomes.yaml",
    "mock-predicates.yaml",
    "expected.yaml",
    "evaluation-scenario.yaml",
)
OBSOLETE_ROOT_FILES = ("README.md", "MIGRATION.md")


def validate(root):
    errors = []
    for skill in sorted(root.iterdir()):
        if not skill.is_dir():
            continue

        if not (skill / "SKILL.md").is_file():
            errors.append(f"{skill.name}: missing SKILL.md")

        for name in OBSOLETE_ROOT_FILES:
            path = skill / name
            if path.exists():
                errors.append(
                    f"{skill.name}: {name} is not a canonical package-root entrypoint; "
                    "keep current model semantics in SKILL.md and history outside the package"
                )

        assurance = skill / "assurance"
        if assurance.exists():
            if not assurance.is_dir():
                errors.append(f"{skill.name}: assurance must be a directory")
            else:
                present = {name for name in ASSURANCE_FILES if (assurance / name).is_file()}
                if present and present != set(ASSURANCE_FILES):
                    missing = ", ".join(sorted(set(ASSURANCE_FILES) - present))
                    errors.append(
                        f"{skill.name}: partial assurance package; missing {missing}"
                    )
                if not present:
                    errors.append(
                        f"{skill.name}: empty assurance/ is ambiguous; remove it or provide the full contract/procedure/predicates trio"
                    )
                if (assurance / "evidence.yaml").exists():
                    errors.append(
                        f"{skill.name}: legacy assurance/evidence.yaml is forbidden; observations and predicates belong in predicates.yaml"
                    )

        for legacy in LEGACY_CASE_FILES:
            for path in (skill / "cases").glob("*/" + legacy):
                errors.append(f"{path}: consolidate into case.yaml")

        if (skill / "examples").exists():
            errors.append(
                f"{skill.name}: examples/ is forbidden; executable fixtures belong in cases/, explanatory samples in references/"
            )

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "skills",
    )
    args = parser.parse_args()
    errors = validate(args.skills_root)
    if errors:
        raise SystemExit("\n".join(errors))
    print("PACKAGE_LAYOUT_OK")


if __name__ == "__main__":
    main()
