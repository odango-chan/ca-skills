#!/usr/bin/env python3
"""Compile the official MAS v1alpha5 example against an explicit trusted snapshot.

This is a project adapter for released skillc v2.0.0, not a compiler,
dependency resolver, Owner publisher or qualification bypass.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = "establish-pdu-session-mas"
SOURCE = REPO / "examples" / "skills" / SKILL
VERSION = "skillc v2.0.2"
TARGET = "connectionagent.io/v1alpha5"


def dependency_aliases(contract: str) -> dict[str, str]:
    """Read the simple top-level dependency map; let skillc parse full YAML."""
    result: dict[str, str] = {}
    in_dependencies = False
    for line in contract.splitlines():
        if line.strip() == "dependencies:" and not line.startswith((" ", "\t")):
            in_dependencies = True
            continue
        if in_dependencies and line.strip() and not line.startswith((" ", "\t", "#")):
            break
        if in_dependencies:
            match = re.fullmatch(r"  ([a-zA-Z][a-zA-Z0-9_-]*):\s*(\S+)\s*(?:#.*)?", line)
            if match:
                if match.group(1) in result:
                    raise ValueError(f"duplicate dependency alias: {match.group(1)}")
                result[match.group(1)] = match.group(2)
    if not result:
        raise ValueError("no dependencies found in the MAS Contract")
    return result


def validate_inputs(source: Path, trusted_root: Path, mode: str) -> tuple[dict, list[str]]:
    errors: list[str] = []
    contract_path = source / "assurance" / "contract.yaml"
    if not contract_path.is_file():
        raise ValueError(f"missing official MAS Contract: {contract_path}")
    aliases = dependency_aliases(contract_path.read_text(encoding="utf-8"))
    trusted_path = trusted_root / "trusted.json"
    if not trusted_path.is_file():
        raise ValueError("missing trusted.json in --trusted-root")
    trusted = json.loads(trusted_path.read_text(encoding="utf-8"))
    if not isinstance(trusted, dict):
        raise ValueError("trusted.json must be a JSON object")

    bindings = trusted.get("dependencyBindings", [])
    if not isinstance(bindings, list):
        raise ValueError("trusted.json dependencyBindings must be an array")
    seen: set[str] = set()
    for item in bindings:
        if not isinstance(item, dict):
            raise ValueError("each dependencyBinding must be an object")
        alias = item.get("dependencyId")
        if not isinstance(alias, str) or not alias:
            errors.append("dependencyBinding without dependencyId")
            continue
        if alias in seen:
            errors.append(f"duplicate trusted dependencyBinding: {alias}")
        seen.add(alias)
        if alias not in aliases:
            errors.append(f"undeclared trusted dependency alias: {alias}")
        elif item.get("stablePackageId") != aliases[alias]:
            errors.append(
                f"package identity mismatch for {alias}: "
                "Contract dependency != trusted stablePackageId"
            )
        snapshot = trusted_root / "snapshots" / alias
        if not snapshot.is_dir() or not any(p.is_file() for p in snapshot.rglob("*")):
            errors.append(f"missing or empty snapshot: snapshots/{alias}")
    for alias in sorted(set(aliases) - seen):
        errors.append(f"unresolved dependency: {alias}")

    deployment = trusted.get("deployment", {})
    if not isinstance(deployment, dict):
        raise ValueError("trusted.json deployment must be an object")
    for field in ("capabilityDirectory", "evidenceDirectory"):
        directory = deployment.get(field)
        if directory:
            path = Path(directory)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"unsafe deployment bundle path: {field}")
            elif not (trusted_root / path).is_dir():
                errors.append(f"missing deployment bundle: {directory}")
    if not deployment.get("capabilityDirectory"):
        errors.append("no deployment CapabilityContracts directory configured")
    if not deployment.get("authorizationRef"):
        errors.append("no deployment authorizationRef configured")

    if mode == "release":
        for path in sorted(source.rglob("*.yaml")):
            if "urn:example:" in path.read_text(encoding="utf-8"):
                errors.append(
                    f"test-only urn:example reference remains: {path.relative_to(source)}"
                )
        if "urn:example:" in trusted_path.read_text(encoding="utf-8"):
            errors.append("test-only urn:example reference remains in trusted.json")

    return {"dependencyAliases": aliases, "mode": mode, "skill": SKILL}, errors


def reject_symlinks(root: Path) -> None:
    if root.is_symlink() or any(p.is_symlink() for p in root.rglob("*")):
        raise ValueError(f"symlink in compiler input tree: {root}")


def copy_project(source: Path, trusted_root: Path, destination: Path, trusted: dict) -> None:
    reject_symlinks(source)
    reject_symlinks(trusted_root)
    shutil.copytree(source, destination / "skills" / SKILL)
    shutil.copy2(trusted_root / "trusted.json", destination / "trusted.json")
    shutil.copytree(trusted_root / "snapshots", destination / "snapshots")
    deployment = trusted.get("deployment", {})
    for field in ("capabilityDirectory", "evidenceDirectory"):
        relative = deployment.get(field)
        if relative:
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe bundle path: {relative}")
            (destination / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(trusted_root / path, destination / path)


def invoke(binary: str, args: list[str]) -> dict:
    try:
        result = subprocess.run(
            [binary, *args], text=True, capture_output=True, check=False
        )
    except OSError as exc:
        raise ValueError(f"cannot start Compiler: {exc}") from exc
    stdout = result.stdout.strip()
    try:
        payload = json.loads(stdout) if stdout else None
    except json.JSONDecodeError:
        payload = stdout
    return {
        "command": args[0],
        "exitCode": result.returncode,
        "result": payload,
        "stderr": result.stderr.strip(),
    }


def execute(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trusted-root", required=True, type=Path,
        help="project with trusted.json, snapshots/ and deployment bundle directories",
    )
    parser.add_argument("--compiler", default="skillc", help="skillc v2.0.0 executable")
    parser.add_argument(
        "--mode", choices=("release", "fixture"), default="release",
        help="fixture permits test-only urn:example references; never qualifies an Owner",
    )
    parser.add_argument("--out", type=Path, help="artifact output directory; omit for Check/Inspect only")
    args = parser.parse_args(argv)
    report: dict = {
        "compilerTarget": TARGET,
        "source": "ca-skills/examples/skills/" + SKILL,
        "qualification": "NOT_QUALIFIED",
        "stages": [],
    }
    try:
        manifest, errors = validate_inputs(SOURCE, args.trusted_root, args.mode)
        report.update(manifest)
        if errors:
            report["status"] = "INPUT_BLOCKED"
            report["blockers"] = errors
            return finish(report, 1)
        reject_symlinks(args.trusted_root)
        version = invoke(args.compiler, ["version"])
        report["compilerVersion"] = version["result"]
        if (version["exitCode"] != 0 or VERSION not in str(version["result"])
                or TARGET not in str(version["result"])):
            report["status"] = "WRONG_COMPILER"
            return finish(report, 2)
        trusted = json.loads((args.trusted_root / "trusted.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory(prefix="ca-mas-skillc-") as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            copy_project(SOURCE, args.trusted_root, project, trusted)
            for command in ("check", "inspect"):
                stage = invoke(args.compiler, [
                    command, str(project), "--skill", SKILL, "--json"
                ])
                report["stages"].append(stage)
                if stage["exitCode"] != 0:
                    report["status"] = "COMPILER_DIAGNOSTICS"
                    return finish(report, 1)
            if args.out:
                stage = invoke(args.compiler, [
                    "build", str(project), "--skill", SKILL,
                    "--out", str(args.out.resolve()), "--json"
                ])
                report["stages"].append(stage)
                if stage["exitCode"] != 0:
                    report["status"] = "BUILD_FAILED"
                    return finish(report, 1)
        report["status"] = (
            "FIXTURE_STATIC_BUILD_PASS" if args.mode == "fixture"
            else "STATIC_BUILD_PASS_OWNER_QUALIFICATION_NOT_ASSERTED"
        ) if args.out else "STATIC_CHECK_PASS_BUILD_NOT_RUN"
        return finish(report, 0)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report["status"] = "INPUT_ERROR"
        report["error"] = str(exc)
        return finish(report, 2)


def finish(report: dict, exit_code: int) -> int:
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(execute())
