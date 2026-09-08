#!/usr/bin/env python3
"""Source-level semantic regression checks for the download Skill."""

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1] / "skills" / "download-object-by-deadline"


def fail(message):
    raise AssertionError(message)


def load(path):
    return yaml.safe_load(path.read_text())


def route_check(name, procedure):
    nodes = procedure["nodes"]
    if not nodes:
        fail(f"{name}: procedure has no nodes")
    terminals = {node.get("terminal") for node in nodes.values() if "terminal" in node}
    if not {"SUCCEEDED", "FAILED", "UNRESOLVED", "SAFE_STOPPED"}.issubset(terminals):
        fail(f"{name}: terminal outcomes are not explicit")
    for node_id, node in nodes.items():
        for outcome, target in node.get("on", {}).items():
            if target not in nodes:
                fail(f"{name}: dangling route {node_id}/{outcome} -> {target}")
    reachable = set()
    pending = [procedure["start"]]
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(nodes[node_id].get("on", {}).values())
    if reachable != set(nodes):
        fail(f"{name}: unreachable nodes: {sorted(set(nodes) - reachable)}")


def validate_cases(procedures):
    cases = sorted(path for path in (ROOT / "cases").iterdir() if path.is_dir())
    if len(cases) != 14:
        fail(f"expected 14 cases, found {len(cases)}")
    for case in cases:
        spec = load(case / "case.yaml")["spec"]
        request = spec["context"]["request"]
        if "secondsRemaining" not in request:
            fail(f"{case.name}: trusted secondsRemaining is required")
        facts = spec["context"].get("facts", {})
        for forbidden in ("bytes_remaining", "seconds_remaining", "minimum_payload_bitrate_bps",
                          "file_transfer.completed", "file_transfer.deadline_met"):
            if forbidden in facts:
                fail(f"{case.name}: dynamic/final fact is pre-injected: {forbidden}")
        procedure_name = spec["expect"].get("procedure")
        if procedure_name is None:
            continue
        procedure = procedures[procedure_name]
        nodes = procedure["nodes"]
        trace = spec["expect"].get("trace", {}).get("ordered", [])
        for current, following in zip(trace, trace[1:]):
            node = nodes.get(current["nodeId"])
            if node is None or node.get("on", {}).get(current["outcome"]) != following["nodeId"]:
                fail(f"{case.name}: trace route mismatch at {current['nodeId']}/{current['outcome']}")
        if trace and spec["expect"].get("terminal"):
            last = trace[-1]
            route = nodes[last["nodeId"]].get("on", {}).get(last["outcome"])
            if route and nodes[route].get("terminal") != spec["expect"]["terminal"]:
                # Budget exhaustion terminates at the Runtime safety boundary.
                if spec["expect"].get("errorCode") != "ACTION_BUDGET_EXHAUSTED_WITH_PENDING_WRITE":
                    fail(f"{case.name}: trace does not reach expected terminal")


def main():
    assurance = ROOT / "assurance"
    if (assurance / "evidence.yaml").exists():
        fail("legacy assurance/evidence.yaml must not exist")
    procedure_set = load(assurance / "procedure.yaml")
    procedures = procedure_set["procedures"]
    if set(procedures) != {"download-direct", "observe-then-download"}:
        fail("download Skill must expose exactly two canonical Procedures")
    contract = load(assurance / "contract.yaml")["spec"]
    allowed = set(contract["allowedResources"]["capabilities"])
    allowed.update(contract["allowedResources"].get("localTools", []))
    for name, procedure in procedures.items():
        route_check(name, procedure)
        for node in procedure["nodes"].values():
            ref = node.get("call") or node.get("script")
            if ref and ref not in allowed and not ref.endswith("derive_transfer_requirement.py"):
                fail(f"{name}: undeclared resource {ref}")

    direct = procedures["download-direct"]["nodes"]
    observed = procedures["observe-then-download"]["nodes"]
    if direct["resolve-qos"]["with"]["minimumPayloadBitrateBps"]["from"] != "derive-requirement.output.minimumPayloadBitrateBps":
        fail("direct QoS resolution does not consume script output")
    if observed["derive-requirement"]["with"]["bytesRemaining"]["from"] != "observe-object.output.sizeBytes":
        fail("metadata output is not consumed by requirement derivation")
    for nodes in (direct, observed):
        if nodes["reconcile-download"]["call"] != "file.download.status":
            fail("download UNKNOWN uses an unrelated reconcile capability")
        if nodes["resolve-qos"]["on"].get("SUCCEEDED") != "download-object":
            fail("QoS admission must gate download through its Capability outcome")
    procedure_text = (assurance / "procedure.yaml").read_text()
    if re.search(r"context\.facts\.(bytes_remaining|minimum_payload_bitrate_bps|seconds_remaining)", procedure_text):
        fail("Procedure still depends on fake planning facts")
    script = (ROOT / "scripts" / "derive_transfer_requirement.py").read_text()
    if not script.startswith("# /// connectionagent-tool") or re.search(r"\b(socket|requests|urllib|subprocess)\b", script):
        fail("derive script metadata or network denial is invalid")
    validate_cases(procedures)
    print("download-object-by-deadline semantic closure: PASS")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f"download-object-by-deadline semantic closure: FAIL: {error}", file=sys.stderr)
        sys.exit(1)
