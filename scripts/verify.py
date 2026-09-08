#!/usr/bin/env python3
"""Thin source-repository verification coordinator.

The Skill repository owns package/layout and authoring checks. Platform owns
the compiler, Case schema, planning, and qualification semantics; this script
delegates those checks instead of copying them.

make verify should represent "this Skills checkout has passed the canonical
source validation required to enter the next stage". It does not by itself
mean production-qualified.

Gates:
  1. package layout
  2. Skill-specific semantic validators
  3. official source compile (4 official Skills)
  4. canonical Case schema validation
  5. canonical Planning validation
  6. official executable Skill qualification (current SQ/Q4 level)
  7. 5gc-file-transfer compile + cases
  8. wifi-file-transfer compile + cases
  9. local Sandbox/Q4 file-transfer qualification
"""

from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd, env=None):
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, env=env, check=True)


def main():
    # 1. package layout — single execution (Makefile no longer runs it separately)
    print("=== 1/9 package layout ===", flush=True)
    run(["python3", "-B", "scripts/validate_package_layout.py"], ROOT)

    # 2. Skill-specific semantic validators
    print("=== 2/9 Skill-specific semantic validators ===", flush=True)
    run(["python3", "-B", "scripts/validate_ue_registration_target.py"], ROOT)
    run(["python3", "-B", "scripts/validate_query_weather_target.py"], ROOT)
    run(["python3", "-B", "scripts/validate_download_object_target.py"], ROOT)

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

    # 3. official source compile (4 official Skills via Platform canonical gate)
    print("=== 3/9 official source compile (ue-registration, ensure-session-qos, download-object-by-deadline, query-weather-for-ue) ===", flush=True)
    run(["go", "test", "./backend/internal/qualificationruntime",
         "-run", "^TestOfficialTargetSkillsCompileFromExplicitSource$", "-count=1"], platform, env)
    # fail-closed: missing source must fail
    run(["go", "test", "./backend/internal/qualificationruntime",
         "-run", "^TestOfficialSkillSourceFailsClosedWhenMissing$", "-count=1"], platform, env)

    # 4. canonical Case schema validation
    print("=== 4/9 canonical Case schema validation ===", flush=True)
    run(["go", "test", "./backend/internal/compiler",
         "-run", "^TestCanonicalCaseRejectsSplitFilesAndUnknownFields$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/compiler",
         "-run", "^TestProcedureSourcesUseCanonicalAuthoringModel$", "-count=1"], platform, env)

    # 5. canonical Planning validation
    print("=== 5/9 canonical Planning validation ===", flush=True)
    run(["go", "test", "./backend/internal/planning",
         "-run", "^TestReferencePlanningCases$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/planning",
         "-run", "^TestPlanningContextAllowsOpaqueFacts$", "-count=1"], platform, env)

    # 6. official executable Skill qualification (current supported level: m5-q4 via sessionrun + qualificationruntime)
    print("=== 6/9 official executable Skill qualification (current SQ/Q4 level) ===", flush=True)
    run(["go", "test", "./backend/internal/sessionrun",
         "-run", "^TestRunOfficialSkillQualificationUsesCompiledOfficialSourceAndSandbox$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/sessionrun",
         "-run", "^TestRunOfficialSkillQualificationCoversObservationUnknownAndPredicateFail$", "-count=1"], platform, env)

    # 7. 5gc-file-transfer compile + cases (casp compile as canonical CLI)
    print("=== 7/9 5gc-file-transfer compile ===", flush=True)
    run(["go", "run", "./backend/cmd/casp", "compile", "--package",
         str(ROOT / "skills/5gc-file-transfer"), "--registry", str(platform / "registry"), "--format", "json"], platform, env)

    # 8. wifi-file-transfer compile + cases
    print("=== 8/9 wifi-file-transfer compile ===", flush=True)
    run(["go", "run", "./backend/cmd/casp", "compile", "--package",
         str(ROOT / "skills/wifi-file-transfer"), "--registry", str(platform / "registry"), "--format", "json"], platform, env)

    # 9. local Sandbox/Q4 qualification for file-transfer paths
    print("=== 9/9 local Sandbox/Q4 file-transfer qualification ===", flush=True)
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
