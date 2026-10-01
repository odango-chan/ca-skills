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
import atexit
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


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
# Facts that a run produces (a virtual group id created/reconciled by a node)
# must reach consumers through the producing node's output. Freezing such a
# value as a Procedure input sourced from `context.facts.*` is unsatisfiable at
# Runtime binding time because no deployment trusted-context resolver owns it.
# See odango-chan/ca-skills#13. `wifi-file-transfer`'s `wifi_transfer.id` is the
# same class of defect but is tracked as a separate follow-up owner issue, so it
# is deliberately not listed here yet.
RUN_PRODUCED_FACT_IDS = ("virtual_group.id",)


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

                procedure_source = assurance / "procedure.yaml"
                if procedure_source.is_file():
                    source = procedure_source.read_text(encoding="utf-8")
                    for fact_id in RUN_PRODUCED_FACT_IDS:
                        if re.search(
                            r"from:\s*context\.facts\." + re.escape(fact_id) + r"\b", source
                        ):
                            errors.append(
                                f"{skill.name}: Procedure input binds run-produced fact "
                                f"'{fact_id}' from context.facts; bind it from the producing "
                                "node's output instead (odango-chan/ca-skills#13)"
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
    platform_value = (
        os.environ.get("CA_SKILL_TOOLCHAIN_ROOT", "").strip()
        or os.environ.get("CONNECTIONAGENT_SKILL_PLATFORM_ROOT", "").strip()
    )
    if platform_value:
        platform = Path(platform_value).resolve()
    else:
        candidates = (
            ROOT.parent / "ca-skill-toolchain",
            ROOT.parent / "connectionagent-skill-platform",
        )
        platform = next((candidate.resolve() for candidate in candidates if candidate.exists()), candidates[0].resolve())

    # A normal checkout has a .git directory while a linked Git worktree has
    # a .git file. Accept both, and also require the Platform paths this script
    # actually invokes so a similarly named directory fails closed.
    required_paths = (
        platform / ".git",
        platform / "backend" / "cmd" / "caskill",
        platform / "registry",
    )
    if not all(path.exists() for path in required_paths):
        raise SystemExit(
            "CA_SKILL_TOOLCHAIN_ROOT (or compatibility alias CONNECTIONAGENT_SKILL_PLATFORM_ROOT) "
            "must point to a Skill Toolchain Git checkout "
            "with backend/cmd/caskill and registry when ../ca-skill-toolchain is unavailable"
        )
    return platform


def platform_env(platform):
    env = os.environ.copy()
    env["CONNECTIONAGENT_SKILLS_ROOT"] = str(ROOT)
    env["CA_SKILLS_ROOT"] = str(ROOT)
    env["GOWORK"] = "off"

    # The canonical module paths are intentionally published independently of
    # this repository. Until those sibling commits are published, make the
    # standard ca-* workspace usable without asking authors to maintain a
    # local replacement configuration or changing the checked-in go.mod.
    mod_dir = Path(tempfile.mkdtemp(prefix="ca-skills-verify-"))
    atexit.register(shutil.rmtree, mod_dir, ignore_errors=True)
    modfile = mod_dir / "workspace.mod"
    shutil.copy2(platform / "go.mod", modfile)
    go_sum = platform / "go.sum"
    if go_sum.exists():
        shutil.copy2(go_sum, mod_dir / "workspace.sum")
    dependency_root = platform.parent
    required_repositories = ("ca-runtime", "ca-sandbox", "nodus")
    while not all((dependency_root / name).exists() for name in required_repositories):
        parent = dependency_root.parent
        if parent == dependency_root:
            raise SystemExit("could not locate sibling ca-runtime, ca-sandbox, and nodus repositories")
        dependency_root = parent
    env["CA_BENCHMARKS_QUALIFICATION_DIR"] = str(dependency_root / "ca-benchmarks" / "qualification")
    with modfile.open("a", encoding="utf-8") as handle:
        handle.write(
            "\nreplace github.com/odango-chan/ca-runtime => "
            f"{(dependency_root / 'ca-runtime').resolve()}\n"
            "replace github.com/odango-chan/ca-sandbox => "
            f"{(dependency_root / 'ca-sandbox').resolve()}\n"
            "replace github.com/odango-chan/nodus => "
            f"{(dependency_root / 'nodus').resolve()}\n"
        )
    existing_flags = env.get("GOFLAGS", "").strip()
    env["GOFLAGS"] = f"{existing_flags} -mod=mod -modfile={modfile}".strip()
    return env


def compile_package(package, platform, env):
    run(
        [
            "go",
            "run",
            "./backend/cmd/caskill",
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
    env = platform_env(platform)
    print(f"=== focused Platform compile: {package.name} ===", flush=True)
    compile_package(package, platform, env)
    print(f"Focused compile: PASS ({package.name})")
    print("Note: compile PASS is not SQ/Q4 or production qualification.")


def full_verify():
    # 1. Repository-local source hygiene only. Machine grammar belongs to Platform.
    print("=== 1/8 package layout ===", flush=True)
    validate_skill_packages(all_skill_packages())

    platform = resolve_platform_root()
    env = platform_env(platform)

    # 2. official source compile through the current Platform compiler gate.
    print(
        "=== 2/8 official source compile "
        "(ue-registration, ensure-session-qos, download-object-by-deadline, query-weather-for-ue) ===",
        flush=True,
    )
    run(
        [
            "go",
            "test",
            "./backend/internal/compiler",
            "-run",
            "^TestCommittedSkillsCompileValid$",
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

    # 5. committed official Skill Cases through the current deterministic Mock Runtime gate.
    print("=== 5/8 committed Skill Cases through Mock Runtime ===", flush=True)
    run(
        [
            "go",
            "test",
            "./backend/internal/mockruntime",
            "-run",
            "^TestReferenceMockCases$",
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

    # 8. official file-transfer Artifact invariant retained by the Platform.
    print("=== 8/8 official file-transfer Artifact contract ===", flush=True)
    run(
        [
            "go",
            "test",
            "./backend/internal/skillbuildartifact",
            "-run",
            "^TestOfficialFileTransferArtifactsExcludeAuthorizationOutcome$",
            "-count=1",
        ],
        platform,
        env,
    )

    print("Skills verification: PASS")
    print("COMPILE PASS | CASE PASS | PLANNING PASS | MOCK-RUNTIME PASS | ARTIFACT CONTRACT PASS")
    print("Note: these local gates are not live owner execution or production qualification.")


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
