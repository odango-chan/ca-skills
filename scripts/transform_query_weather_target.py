#!/usr/bin/env python3
"""Mechanically transform the S4 legacy graph into the target graph."""

from copy import deepcopy
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1] / "skills" / "query-weather-for-ue"
PROCEDURE = ROOT / "assurance" / "procedure.yaml"
PREDICATES = ROOT / "assurance" / "predicates.yaml"


def dump(path, value):
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True))


def main():
    legacy = yaml.safe_load(PROCEDURE.read_text())
    old = {proc["name"]: proc for proc in legacy["spec"]["procedures"]}
    nodes = {node["id"]: node for proc in old.values() for node in proc["nodes"]}
    selected = [
        "verify-connectivity",
        "probe-connectivity",
        "ensure-connectivity",
        "reconcile-connectivity",
        "query-weather",
        "normalize-weather",
        "verify-weather-result",
        "done",
        "failed",
        "unresolved",
        "safe-stopped",
    ]
    merged = [deepcopy(nodes[node_id]) for node_id in selected]
    by_id = {node["id"]: node for node in merged}
    by_id["verify-connectivity"]["on"]["FAIL"] = {"next": "ensure-connectivity"}
    by_id["verify-connectivity"]["on"]["UNKNOWN"] = {"next": "probe-connectivity"}
    procedure = {
        "apiVersion": "connectionagent.io/v1alpha1",
        "kind": "ProcedureSet",
        "metadata": {"skill": "query-weather-for-ue"},
        "spec": {
            "selectionPolicy": "exactlyOne",
            "procedures": [{
                "name": "query-weather",
                "goal": "weather.query_for_ue",
                "entry": "verify-connectivity",
                "nodes": merged,
            }],
        },
    }
    dump(PROCEDURE, procedure)

    predicates = {
        "apiVersion": "connectionagent.io/v1alpha1",
        "kind": "PredicateSet",
        "metadata": {"skill": "query-weather-for-ue"},
        "predicates": {
            "ue.registered": {
                "observations": {"registration": {
                    "ref": "ue.registration.snapshot",
                    "scope": '{"ueRef": subject.ueRef}',
                    "freshness": "30s",
                }},
                "evaluator": {"type": "cel", "expression": 'observations.registration.registrationState == "REGISTERED"'},
            },
            "user_plane.connectivity.available": {
                "observations": {"connectivity": {
                    "ref": "user.plane.connectivity.snapshot",
                    "scope": '{"ueRef": subject.ueRef, "pduSessionId": subject.pduSessionId}',
                    "freshness": "5s",
                }},
                "evaluator": {"type": "cel", "expression": "observations.connectivity.available == true"},
            },
            "service.weather.query.succeeded": {
                "observations": {"weather": {
                    "ref": "weather.result.snapshot",
                    "scope": '{"ueRef": subject.ueRef}',
                    "freshness": "5s",
                }},
                "evaluator": {"type": "cel", "expression": "observations.weather.succeeded == true"},
            },
        },
    }
    dump(PREDICATES, predicates)

    for case_dir in sorted((ROOT / "cases").iterdir()):
        if not case_dir.is_dir():
            continue
        path = case_dir / "expected.yaml"
        expected_doc = yaml.safe_load(path.read_text())
        expected = expected_doc["expected"]
        old_name = expected.get("procedure")
        if old_name is None:
            continue
        expected["procedure"] = "query-weather"
        trace = expected.get("trace", {}).get("ordered", [])
        if trace and trace[0].get("nodeId") != "verify-connectivity":
            outcome = {"query-weather-direct": "PASS", "connect-then-query-weather": "FAIL", "probe-then-query-weather": "UNKNOWN"}[old_name]
            trace.insert(0, {"nodeId": "verify-connectivity", "outcome": outcome})
        dump(path, expected_doc)


if __name__ == "__main__":
    main()
