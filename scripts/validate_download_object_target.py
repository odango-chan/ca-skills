#!/usr/bin/env python3
"""Source-level M2 closure check for download-object-by-deadline.

This validates the target authoring surface and case graph. Platform compile
and Runtime qualification remain separate gates.
"""

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1] / "skills" / "download-object-by-deadline"


def load(path):
    return yaml.safe_load(path.read_text())


def fail(message):
    raise AssertionError(message)


def validate_procedure(proc, predicate_ids, allowed):
    nodes = proc["nodes"]
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        fail(f"{proc['name']}: duplicate node id")
    node_map = {node["id"]: node for node in nodes}
    if proc["entry"] not in node_map:
        fail(f"{proc['name']}: missing entry node")
    edges = {node_id: set() for node_id in ids}
    terminals = set()
    referenced = set()
    for node in nodes:
        if node["type"] == "terminal":
            terminals.add(node.get("result"))
        referenced.update(node.get("predicates", []))
        for outcome, route in node.get("on", {}).items():
            if not isinstance(route, dict) or "next" not in route:
                fail(f"{proc['name']}: non-explicit route at {node['id']}/{outcome}")
            target = route["next"]
            if target not in node_map:
                fail(f"{proc['name']}: dangling route {node['id']} -> {target}")
            edges[node["id"]].add(target)
        if node["type"] == "action":
            ref = node["ref"]
            if isinstance(ref, dict):
                ref = ref.get("value")
            if ref not in allowed:
                fail(f"{proc['name']}: action resource is not allowed: {ref}")
    if referenced - predicate_ids:
        fail(f"{proc['name']}: undefined predicate(s): {sorted(referenced - predicate_ids)}")
    if not {"SUCCEEDED", "FAILED", "UNRESOLVED", "SAFE_STOPPED"} <= terminals:
        fail(f"{proc['name']}: required terminal results are not explicit")

    reachable = set()
    pending = [proc["entry"]]
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(edges[node_id] - reachable)
    if reachable != set(ids):
        fail(f"{proc['name']}: unreachable nodes: {sorted(set(ids) - reachable)}")


def validate_cases(procedures):
    node_maps = {
        proc["name"]: {node["id"]: node for node in proc["nodes"]}
        for proc in procedures
    }
    cases = sorted(path for path in (ROOT / "cases").iterdir() if path.is_dir())
    if len(cases) != 14:
        fail(f"expected 14 cases, found {len(cases)}")
    for case in cases:
        expected = load(case / "case.yaml")["spec"]["expect"]
        procedure = expected.get("procedure")
        if procedure is None:
            continue
        if procedure not in node_maps:
            fail(f"{case.name}: unknown expected procedure {procedure}")
        nodes = node_maps[procedure]
        trace = expected.get("trace", {}).get("ordered", [])
        for current, following in zip(trace, trace[1:]):
            node = nodes.get(current["nodeId"])
            if node is None:
                fail(f"{case.name}: unknown trace node {current['nodeId']}")
            route = node.get("on", {}).get(current["outcome"])
            if route is None or route["next"] != following["nodeId"]:
                fail(f"{case.name}: trace route mismatch at {current['nodeId']}/{current['outcome']}")
        if trace:
            last = trace[-1]
            node = nodes.get(last["nodeId"])
            route = node.get("on", {}).get(last["outcome"])
            terminal = nodes.get(route["next"]) if route else None
            implicit_budget_stop = (
                expected.get("errorCode") == "ACTION_BUDGET_EXHAUSTED_WITH_PENDING_WRITE"
                and last["outcome"] == "OUTCOME_UNKNOWN"
            )
            if expected.get("terminal") and not implicit_budget_stop and (
                terminal is None or terminal.get("result") != expected["terminal"]
            ):
                fail(f"{case.name}: trace does not reach expected terminal")


def main():
    assurance = ROOT / "assurance"
    if (assurance / "evidence.yaml").exists():
        fail("legacy assurance/evidence.yaml must not exist")
    predicates = load(assurance / "predicates.yaml")
    if predicates.get("kind") != "PredicateSet":
        fail("target predicates must use PredicateSet")
    predicate_ids = set(predicates["predicates"])
    if predicate_ids != {"object.size.known", "file_transfer.completed", "file_transfer.deadline_met"}:
        fail(f"unexpected target predicate ids: {sorted(predicate_ids)}")
    for predicate_id, definition in predicates["predicates"].items():
        if not definition.get("observations") or definition.get("evaluator", {}).get("type") != "cel":
            fail(f"{predicate_id}: typed Observation and CEL evaluator are required")
    procedure_set = load(assurance / "procedure.yaml")
    procedures = procedure_set["spec"]["procedures"]
    if procedure_set["spec"].get("selectionPolicy") != "exactlyOne" or len(procedures) != 2:
        fail("target must use exactlyOne selection with two Procedures")
    whens = [proc.get("applicability", {}).get("when", "") for proc in procedures]
    if not any(re.search(r"request\.sizeBytes", when) for when in whens):
        fail("Procedure selection must be request-driven")
    contract = load(assurance / "contract.yaml")["spec"]
    allowed = set(contract["allowedResources"]["capabilities"])
    allowed.update(contract["allowedResources"].get("localTools", []))
    for proc in procedures:
        validate_procedure(proc, predicate_ids, allowed)
    validate_cases(procedures)
    script = (ROOT / "scripts" / "derive_transfer_requirement.py").read_text()
    if re.search(r"\b(socket|requests|urllib|subprocess)\b", script):
        fail("local transfer-requirement script contains a network/process dependency")
    print("M2 target closure: PASS (YAML, target predicates, graph, cases, local script boundary)")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f"M2 target closure: FAIL: {error}", file=sys.stderr)
        sys.exit(1)
