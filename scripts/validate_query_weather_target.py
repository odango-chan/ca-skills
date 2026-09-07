#!/usr/bin/env python3
"""Source-level M2 closure check for query-weather-for-ue."""

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1] / "skills" / "query-weather-for-ue"


def load(path):
    return yaml.safe_load(path.read_text())


def fail(message):
    raise AssertionError(message)


def main():
    assurance = ROOT / "assurance"
    if (assurance / "evidence.yaml").exists():
        fail("legacy assurance/evidence.yaml must not exist")
    predicates = load(assurance / "predicates.yaml")
    if predicates.get("kind") != "PredicateSet":
        fail("target predicates must use PredicateSet")
    predicate_ids = set(predicates["predicates"])
    expected_predicates = {
        "ue.registered",
        "user_plane.connectivity.available",
        "service.weather.query.succeeded",
    }
    if predicate_ids != expected_predicates:
        fail(f"unexpected target predicates: {sorted(predicate_ids)}")
    for predicate_id, definition in predicates["predicates"].items():
        if not definition.get("observations") or definition.get("evaluator", {}).get("type") != "cel":
            fail(f"{predicate_id}: typed Observation and CEL evaluator are required")

    procedure_set = load(assurance / "procedure.yaml")
    spec = procedure_set["spec"]
    if spec.get("selectionPolicy") != "exactlyOne" or len(spec["procedures"]) != 1:
        fail("target must have one exactlyOne Procedure")
    proc = spec["procedures"][0]
    nodes = proc["nodes"]
    node_map = {node["id"]: node for node in nodes}
    if len(node_map) != len(nodes) or proc["entry"] not in node_map:
        fail("Procedure node ids or entry are invalid")
    edges = {node_id: set() for node_id in node_map}
    terminals = set()
    referenced = set()
    for node in nodes:
        if node["type"] == "terminal":
            terminals.add(node.get("result"))
        referenced.update(node.get("predicates", []))
        for outcome, route in node.get("on", {}).items():
            if not isinstance(route, dict) or "next" not in route or route["next"] not in node_map:
                fail(f"invalid route at {node['id']}/{outcome}")
            edges[node["id"]].add(route["next"])
    if referenced - predicate_ids:
        fail(f"undefined predicate references: {sorted(referenced - predicate_ids)}")
    if not {"SUCCEEDED", "FAILED", "UNRESOLVED", "SAFE_STOPPED"} <= terminals:
        fail("required terminal results are not explicit")
    reachable = set()
    pending = [proc["entry"]]
    while pending:
        node_id = pending.pop()
        if node_id in reachable:
            continue
        reachable.add(node_id)
        pending.extend(edges[node_id] - reachable)
    if reachable != set(node_map):
        fail(f"unreachable nodes: {sorted(set(node_map) - reachable)}")

    normalize = node_map["normalize-weather"]
    if normalize.get("inputFrom", {}).get("node") != "query-weather" or normalize.get("inputFrom", {}).get("path") != "output":
        fail("normalization must consume the prior weather Action output")
    cases = sorted(path for path in (ROOT / "cases").iterdir() if path.is_dir())
    if len(cases) != 16:
        fail(f"expected 16 cases, found {len(cases)}")
    for case in cases:
        expected = load(case / "case.yaml")["spec"]["expect"]
        if expected.get("procedure") not in (None, proc["name"]):
            fail(f"{case.name}: expected procedure does not match target")
        trace = expected.get("trace", {}).get("ordered", [])
        exact = expected.get("trace", {}).get("match") == "exact"
        for current, following in zip(trace, trace[1:]):
            node = node_map.get(current["nodeId"])
            if node is None:
                fail(f"{case.name}: trace route mismatch")
            next_node = node.get("on", {}).get(current["outcome"], {}).get("next")
            if exact:
                valid = next_node == following["nodeId"]
            else:
                visited = set()
                queue = [next_node] if next_node else []
                while queue:
                    candidate = queue.pop()
                    if candidate in visited:
                        continue
                    visited.add(candidate)
                    if candidate == following["nodeId"]:
                        break
                    queue.extend(edges[candidate] - visited)
                valid = following["nodeId"] in visited
            if not valid:
                fail(f"{case.name}: trace route mismatch")
    script = (ROOT / "scripts" / "normalize_weather_result.py").read_text()
    if re.search(r"\b(socket|requests|urllib|subprocess)\b", script):
        fail("normalization script contains a network/process dependency")
    print("M2 target closure: PASS (YAML, target predicates, merged graph, fromOutput, cases, local script boundary)")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f"M2 target closure: FAIL: {error}", file=sys.stderr)
        sys.exit(1)
