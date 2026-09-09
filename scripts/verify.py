#!/usr/bin/env python3
"""Single source-repository verification entrypoint.

The Skills repository owns only repository-local package/layout hygiene.
Platform owns the compiler, Case schema, planning, and qualification semantics;
this script delegates those checks instead of copying them into per-Skill
validators.

Usage:
  python3 -B scripts/verify.py
      Run the full repository verification gate used by ``make verify``.

  python3 -B scripts/verify.py --compile skills/<name>
      Run repository-owned hygiene for one official executable package and then
      invoke the Skill Platform compiler for that package only.

A successful focused compile is source/build evidence only. It is not SQ2/Q4 or
production qualification.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = (ROOT / "skills").resolve()
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
    print("+", " ".join(str(arg) for arg in args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def validate_skill_packages(packages):
    """Check repository-owned source-package hygiene only."""
    errors = []

    for skill in sorted(packages):
        if not skill.is_dir():
            errors.append(f"{skill}: package directory does not exist")
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

        cases = skill / "cases"
        if cases.exists():
            for legacy in LEGACY_CASE_FILES:
                for path in cases.glob("*/" + legacy):
                    errors.append(f"{path}: consolidate into case.yaml")

        if (skill / "examples").exists():
            errors.append(
                f"{skill.name}: examples/ is forbidden; executable fixtures belong in "
                "cases/, explanatory samples in references/"
            )

    if errors:
        raise SystemExit("\n".join(errors))
    print("PACKAGE_LAYOUT_OK", flush=True)


def all_skill_packages():
    return [path for path in SKILLS_ROOT.iterdir() if path.is_dir()]


def resolve_official_package(value):
    candidate = Path(value)
    if not candidate.is_absolute():
        if candidate.parts and candidate.parts[0] == "skills":
            candidate = ROOT / candidate
        else:
            candidate = SKILLS_ROOT / candidate
    candidate = candidate.resolve()

    try:
        candidate.relative_to(SKILLS_ROOT)
    except ValueError as error:
        raise SystemExit(
            f"focused compile only accepts official packages under {SKILLS_ROOT}: {candidate}"
        ) from error

    if not candidate.is_dir():
        raise SystemExit(f"Skill package directory does not exist: {candidate}")
    return candidate


def resolve_platform_root():
    platform_value = os.environ.get("CONNECTIONAGENT_SKILL_PLATFORM_ROOT", "").strip()
    if platform_value:
        platform = Path(platform_value).resolve()
    else:
        platform = (ROOT.parent / "connectionagent-skill-platform").resolve()

    # A normal checkout has a .git directory while a linked Git worktree has
    # a .git file. Accept both, and also require the Platform paths this script
    # actually invokes so a similarly named directory fails closed.
    required_paths = (
        platform / ".git",
        platform / "backend" / "cmd" / "casp",
        platform / "registry",
    )
    if not all(path.exists() for path in required_paths):
        raise SystemExit(
            "CONNECTIONAGENT_SKILL_PLATFORM_ROOT must point to a Skill Platform Git checkout "
            "with backend/cmd/casp and registry when ../connectionagent-skill-platform is unavailable"
        )
    return platform


def platform_env():
    env = os.environ.copy()
    env["CONNECTIONAGENT_SKILLS_ROOT"] = str(ROOT)
    env["GOWORK"] = "off"
    return env


def compile_package(package, platform, env):
    run(
        [
            "go",
            "run",
            "./backend/cmd/casp",
            "compile",
            "--package",
            str(package),
            "--registry",
            str(platform / "registry"),
            "--format",
            "json",
        ],
        platform,
        env,
    )


def focused_compile(value):
    package = resolve_official_package(value)
    print(f"=== focused package hygiene: {package.name} ===", flush=True)
    validate_skill_packages([package])

    if not (package / "assurance").is_dir():
        raise SystemExit(
            f"{package.name}: focused compiler mode is for executable packages with assurance/; "
            "model-context/routing-policy packages use repository hygiene only"
        )

    platform = resolve_platform_root()
    env = platform_env()
    print(f"=== focused Platform compile: {package.name} ===", flush=True)
    compile_package(package, platform, env)
    print(f"Focused compile: PASS ({package.name})")
    print("Note: compile PASS is not SQ/Q4 or production qualification.")


def full_verify():
    # 1. Repository-local source hygiene only. Machine grammar belongs to Platform.
    print("=== 1/8 package layout ===", flush=True)
    validate_skill_packages(all_skill_packages())

    platform = resolve_platform_root()
    env = platform_env()

    # 2. official source compile (4 reference Skills via Platform canonical gate)
    print(
        "=== 2/8 official source compile "
        "(ue-registration, ensure-session-qos, download-object-by-deadline, query-weather-for-ue) ===",
        flush=True,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/qualificationruntime",
            "-run",
            "^TestOfficialTargetSkillsCompileFromExplicitSource$",
            "-count=1",
        ],
        platform,
        env,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/qualificationruntime",
            "-run",
            "^TestOfficialSkillSourceFailsClosedWhenMissing$",
            "-count=1",
        ],
        platform,
        env,
    )

    # 3. canonical Case and authoring-model validation
    print("=== 3/8 canonical Case / authoring-model validation ===", flush=True)
    run(
        [
            "go",
            "test",
            "./backend/internal/compiler",
            "-run",
            "^TestCanonicalCaseRejectsSplitFilesAndUnknownFields$",
            "-count=1",
        ],
        platform,
        env,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/compiler",
            "-run",
            "^TestProcedureSourcesUseCanonicalAuthoringModel$",
            "-count=1",
        ],
        platform,
        env,
    )

    # 4. canonical Planning validation
    print("=== 4/8 canonical Planning validation ===", flush=True)
    run(
        [
            "go",
            "test",
            "./backend/internal/planning",
            "-run",
            "^TestReferencePlanningCases$",
            "-count=1",
        ],
        platform,
        env,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/planning",
            "-run",
            "^TestPlanningContextAllowsOpaqueFacts$",
            "-count=1",
        ],
        platform,
        env,
    )

    # 5. official executable Skill qualification (current supported level: m5-q4)
    print("=== 5/8 official executable Skill qualification (current SQ/Q4 level) ===", flush=True)
    run(
        [
            "go",
            "test",
            "./backend/internal/sessionrun",
            "-run",
            "^TestRunOfficialSkillQualificationUsesCompiledOfficialSourceAndSandbox$",
            "-count=1",
        ],
        platform,
        env,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/sessionrun",
            "-run",
            "^TestRunOfficialSkillQualificationCoversObservationUnknownAndPredicateFail$",
            "-count=1",
        ],
        platform,
        env,
    )

    # 6. 5gc-file-transfer compile + cases
    print("=== 6/8 5gc-file-transfer compile ===", flush=True)
    compile_package(ROOT / "skills/5gc-file-transfer", platform, env)

    # 7. wifi-file-transfer compile + cases
    print("=== 7/8 wifi-file-transfer compile ===", flush=True)
    compile_package(ROOT / "skills/wifi-file-transfer", platform, env)

    # 8. local Sandbox/Q4 qualification for file-transfer paths
    print("=== 8/8 local Sandbox/Q4 file-transfer qualification ===", flush=True)
    run(
        [
            "go",
            "test",
            "./backend/internal/sessionrun",
            "-run",
            "^TestRunOfficialFileTransferRecoveryMatrixThroughQualifiedSandbox$",
            "-count=1",
        ],
        platform,
        env,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/sessionrun",
            "-run",
            "^TestRunOfficialMutationUnknownCasesThroughQualifiedSandbox$",
            "-count=1",
        ],
        platform,
        env,
    )

    print("Skills verification: PASS")
    print("COMPILE PASS | CASE PASS | PLANNING PASS | SQ/Q4 PASS (local Sandbox)")
    print("Note: local Sandbox/Q4 PASS is preflight evidence, not production-qualified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compile",
        metavar="SKILL_PACKAGE",
        help="run package hygiene and a focused Platform compile for one official executable Skill",
    )
    args = parser.parse_args()

    if args.compile:
        focused_compile(args.compile)
    else:
        full_verify()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"Skills verification: FAIL ({error.returncode})", file=sys.stderr)
        raise SystemExit(error.returncode)
