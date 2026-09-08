#!/usr/bin/env python3
"""Canonical source sanity check; compiler/qualification remain Platform gates."""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1] / "skills" / "ue-registration"

def main():
    procedure = yaml.safe_load((ROOT / "assurance/procedure.yaml").read_text())
    if set(procedure) != {"procedures"} or not procedure["procedures"]:
        raise AssertionError("canonical vNext procedures are required")
    cases = list((ROOT / "cases").glob("*/case.yaml"))
    if len(cases) != 9:
        raise AssertionError(f"expected 9 cases, found {len(cases)}")
    if (ROOT / "assurance/evidence.yaml").exists():
        raise AssertionError("legacy evidence.yaml is forbidden")
    print("ue-registration source closure: PASS")

if __name__ == "__main__":
    try: main()
    except (AssertionError, KeyError, TypeError, yaml.YAMLError) as e:
        print(f"ue-registration source closure: FAIL: {e}", file=sys.stderr); raise SystemExit(1)
