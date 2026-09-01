#!/usr/bin/env python3
"""Small, source-level M2 closure check for ue-registration.

This intentionally validates the target authoring surface only. It is not a
replacement for the Platform Compiler or Runtime qualification gates.
"""

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSURANCE = ROOT / "assurance"
CASES = ROOT / "cases"


def load(path):
    with path.open() as stream:
        return yaml.safe_load(stream)


def fail(message):
    raise AssertionError(message)


def validate_procedure(procedure, predicates, allowed, request_schema):
    spec = procedure["spec"]
    procedures = spec["procedures"]
    if len(procedures) != 1:
        fail("target must contain exactly one deterministic Procedure")
    proc = procedures[0]
    nodes = proc["nodes"]
    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        fail("duplicate Procedure node id")
    node_map = {node["id"]: node for node in nodes}
    if proc["entry"] not in node_map:
        fail(f"missing entry node: {proc['entry']}")

    referenced_predicates = set()
    edges = {node_id: set() for node_id in ids}
    terminal_results = set()
    for node in nodes:
        if node["type"] == "terminal":
            terminal_results.add(node.get("result"))
        for predicate in node.get("predicates", []):
            referenced_predicates.add(predicate)
        for outcome, route in node.get("on", {}).items():
            if not isinstance(route, dict) or "next" not in route:
                fail(f"non-explicit route at {node['id']}/{outcome}")
            target = route["next"]
            if target not in node_map:
                fail(f"dangling node reference: {node['id']} -> {target}")
            edges[node["id"]].add(target)
        if node["type"] == "action" and node["ref"] not in allowed:
            fail(f"action capability is not allowed: {node['ref']}")
    missing = referenced_predicates - set(predicates["predicates"])
    if missing:
        fail(f"undefined predicate reference(s): {sorted(missing)}")
    if not {"SUCCEEDED", "FAILED", "UNRESOLVED", "SAFE_STOPPED"} <= terminal_results:
        fail("required terminal results are not explicit")

    reachable = set()
    pending = [proc["entry"]]
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(edges[node_id] - reachable)
    if reachable != set(ids):
        fail(f"unreachable Procedure node(s): {sorted(set(ids) - reachable)}")

    when = proc.get("applicability", {}).get("when", "")
    if not re.search(r'request\.registrationType\s*==\s*"initial"', when):
        fail("applicability must select initial registration from request")
    schema_type = request_schema["properties"]["registrationType"]
    if schema_type.get("const") != "initial" and "initial" not in schema_type.get("enum", []):
        fail("request schema does not admit applicability value initial")


def validate_cases(nodes):
    node_ids = {node["id"] for node in nodes}
    node_map = {node["id"]: node for node in nodes}
    for case_dir in sorted(CASES.iterdir()):
        if not case_dir.is_dir():
            continue
        expected = load(case_dir / "expected.yaml")["expected"]
        trace = expected.get("trace", {}).get("ordered", [])
        seen = set()
        for event in trace:
            node_id = event["nodeId"]
            if node_id not in node_ids:
                fail(f"{case_dir.name}: trace references missing node {node_id}")
            if node_id in seen:
                fail(f"{case_dir.name}: duplicate trace node {node_id}")
            seen.add(node_id)
        for current, following in zip(trace, trace[1:]):
            route = node_map[current["nodeId"]].get("on", {}).get(current["outcome"])
            if route is None or route["next"] != following["nodeId"]:
                fail(
                    f"{case_dir.name}: trace route mismatch at "
                    f"{current['nodeId']}/{current['outcome']}"
                )
        if trace:
            last = trace[-1]
            route = node_map[last["nodeId"]].get("on", {}).get(last["outcome"])
            terminal = node_map.get(route["next"]) if route else None
            expected_terminal = expected.get("terminal")
            if expected_terminal is not None and (
                terminal is None or terminal.get("result") != expected_terminal
            ):
                fail(f"{case_dir.name}: trace does not reach expected terminal")
        planning = load(case_dir / "planning-context.yaml")
        if planning.get("facts") not in ({}, None):
            fail(f"{case_dir.name}: dynamic state must not select Procedure via facts")
        if expected.get("procedure") is not None and expected["procedure"] != "ensure-registration":
            fail(f"{case_dir.name}: unexpected Procedure name")


def main():
    procedure = load(ASSURANCE / "procedure.yaml")
    predicates = load(ASSURANCE / "predicates.yaml")
    contract = load(ASSURANCE / "contract.yaml")["spec"]
    schema = load(ROOT / "schemas" / "registration-request.schema.yaml")
    validate_procedure(
        procedure,
        predicates,
        set(contract["allowedResources"]["capabilities"]),
        schema,
    )
    validate_cases(procedure["spec"]["procedures"][0]["nodes"])
    print("M2 target closure: PASS (YAML, references, reachability, applicability, cases)")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f"M2 target closure: FAIL: {error}", file=sys.stderr)
        sys.exit(1)
