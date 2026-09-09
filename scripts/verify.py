#!/usr/bin/env python3
"""Single source-repository verification entrypoint.

The Skills repository owns only repository-local package/layout hygiene.
Platform owns the compiler, Case schema, planning, and qualification semantics;
this script delegates those checks instead of copying them into per-Skill
validators.

make verify should represent "this Skills checkout has passed the canonical
source validation required to enter the next stage". It does not by itself
mean production-qualified.

Gates:
  1. repository-local package layout
  2. official source compile (4 official reference Skills)
  3. canonical Case / authoring-model validation
  4. canonical Planning validation
  5. official executable Skill qualification (current SQ/Q4 level)
  6. 5gc-file-transfer compile + cases
  7. wifi-file-transfer compile + cases
  8. local Sandbox/Q4 file-transfer qualification
"""

from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
ASSURANCE_FILES = ("contract.yaml", "procedure.yaml", "predicates.yaml")
LEGACY_CASE_FILES = (
    "planning-context.yaml",
    "mock-outcomes.yaml",
    "mock-predicates.yaml",
    "expected.yaml",
    "evaluation-scenario.yaml",
)
OBSOLETE_ROOT_FILES = ("README.md", "MIGRATION.md")


def run(args, cwd, env=None):
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def validate_package_layout():
    """Check repository-owned source-package hygiene only."""
    errors = []
    skills_root = ROOT / "skills"

    for skill in sorted(skills_root.iterdir()):
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
                    errors.append(f"{skill.name}: partial assurance package; missing {missing}")
                if not present:
                    errors.append(
                        f"{skill.name}: empty assurance/ is ambiguous; remove it or provide "
                        "the full contract/procedure/predicates trio"
                    )
                if (assurance / "evidence.yaml").exists():
                    errors.append(
                        f"{skill.name}: legacy assurance/evidence.yaml is forbidden; "
                        "observations and predicates belong in predicates.yaml"
                    )

        for legacy in LEGACY_CASE_FILES:
            for path in (skill / "cases").glob("*/" + legacy):
                errors.append(f"{path}: consolidate into case.yaml")

        if (skill / "examples").exists():
            errors.append(
                f"{skill.name}: examples/ is forbidden; executable fixtures belong in "
                "cases/, explanatory samples in references/"
            )

    if errors:
        raise SystemExit("\n".join(errors))
    print("PACKAGE_LAYOUT_OK", flush=True)


def main():
    # 1. Repository-local source hygiene only. Machine grammar belongs to Platform.
    print("=== 1/8 package layout ===", flush=True)
    validate_package_layout()

    platform_value = os.environ.get("CONNECTIONAGENT_SKILL_PLATFORM_ROOT", "").strip()
    if platform_value:
        platform = Path(platform_value).resolve()
    else:
        # Convenient for a developer checkout only. CI must set the locator.
        platform = (ROOT.parent / "connectionagent-skill-platform").resolve()
    if not (platform / ".git").is_dir():
        raise SystemExit("CONNECTIONAGENT_SKILL_PLATFORM_ROOT must point to a Skill Platform Git checkout")

    env = os.environ.copy()
    env["CONNECTIONAGENT_SKILLS_ROOT"] = str(ROOT)
    env["GOWORK"] = "off"

    # 2. official source compile (4 reference Skills via Platform canonical gate)
    print("=== 2/8 official source compile (ue-registration, ensure-session-qos, download-object-by-deadline, query-weather-for-ue) ===", flush=True)
    run(["go", "test", "./backend/internal/qualificationruntime",
         "-run", "^TestOfficialTargetSkillsCompileFromExplicitSource$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/qualificationruntime",
         "-run", "^TestOfficialSkillSourceFailsClosedWhenMissing$", "-count=1"], platform, env)

    # 3. canonical Case and authoring-model validation
    print("=== 3/8 canonical Case / authoring-model validation ===", flush=True)
    run(["go", "test", "./backend/internal/compiler",
         "-run", "^TestCanonicalCaseRejectsSplitFilesAndUnknownFields$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/compiler",
         "-run", "^TestProcedureSourcesUseCanonicalAuthoringModel$", "-count=1"], platform, env)

    # 4. canonical Planning validation
    print("=== 4/8 canonical Planning validation ===", flush=True)
    run(["go", "test", "./backend/internal/planning",
         "-run", "^TestReferencePlanningCases$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/planning",
         "-run", "^TestPlanningContextAllowsOpaqueFacts$", "-count=1"], platform, env)

    # 5. official executable Skill qualification (current supported level: m5-q4)
    print("=== 5/8 official executable Skill qualification (current SQ/Q4 level) ===", flush=True)
    run(["go", "test", "./backend/internal/sessionrun",
         "-run", "^TestRunOfficialSkillQualificationUsesCompiledOfficialSourceAndSandbox$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/sessionrun",
         "-run", "^TestRunOfficialSkillQualificationCoversObservationUnknownAndPredicateFail$", "-count=1"], platform, env)

    # 6. 5gc-file-transfer compile + cases (casp compile as canonical CLI)
    print("=== 6/8 5gc-file-transfer compile ===", flush=True)
    run(["go", "run", "./backend/cmd/casp", "compile", "--package",
         str(ROOT / "skills/5gc-file-transfer"), "--registry", str(platform / "registry"), "--format", "json"], platform, env)

    # 7. wifi-file-transfer compile + cases
    print("=== 7/8 wifi-file-transfer compile ===", flush=True)
    run(["go", "run", "./backend/cmd/casp", "compile", "--package",
         str(ROOT / "skills/wifi-file-transfer"), "--registry", str(platform / "registry"), "--format", "json"], platform, env)

    # 8. local Sandbox/Q4 qualification for file-transfer paths
    print("=== 8/8 local Sandbox/Q4 file-transfer qualification ===", flush=True)
    run(["go", "test", "./backend/internal/sessionrun",
         "-run", "^TestRunOfficialFileTransferRecoveryMatrixThroughQualifiedSandbox$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/sessionrun",
         "-run", "^TestRunOfficialMutationUnknownCasesThroughQualifiedSandbox$", "-count=1"], platform, env)

    print("Skills verification: PASS")
    print("COMPILE PASS | CASE PASS | PLANNING PASS | SQ/Q4 PASS (local Sandbox)")
    print("Note: local Sandbox/Q4 PASS is preflight evidence, not production-qualified.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"Skills verification: FAIL ({error.returncode})", file=sys.stderr)
        raise SystemExit(error.returncode)
