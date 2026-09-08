#!/usr/bin/env python3
"""Thin source-repository verification coordinator.

The Skill repository owns package/layout and authoring checks. Platform owns
the compiler, Case schema, planning, and qualification semantics; this script
delegates those checks instead of copying them.
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
    run(["python3", "-B", "scripts/validate_package_layout.py"], ROOT)
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
    run(["go", "test", "./backend/internal/qualificationruntime",
         "-run", "^TestOfficialTargetSkillsCompileFromExplicitSource$", "-count=1"], platform, env)
    run(["go", "test", "./backend/internal/planning",
         "-run", "^TestReferencePlanningCases$$|^TestPlanningContextAllowsOpaqueFacts$$", "-count=1"], platform, env)
    run(["go", "run", "./backend/cmd/casp", "compile", "--package",
         str(ROOT / "skills/5gc-file-transfer"), "--registry", str(platform / "registry"), "--format", "json"], platform, env)
    run(["go", "run", "./backend/cmd/casp", "compile", "--package",
         str(ROOT / "skills/wifi-file-transfer"), "--registry", str(platform / "registry"), "--format", "json"], platform, env)
    print("Skills verification: PASS")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"Skills verification: FAIL ({error.returncode})", file=sys.stderr)
        raise SystemExit(error.returncode)
