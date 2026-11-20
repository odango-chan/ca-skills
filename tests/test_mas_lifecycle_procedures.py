from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODIFY = ROOT / "examples/skills/modify-pdu-session-mas"
RELEASE = ROOT / "examples/skills/release-pdu-session-mas"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def node_block(source: str, node_id: str) -> str:
    pattern = re.compile(
        rf"(?ms)^  {re.escape(node_id)}:\n(.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)"
    )
    match = pattern.search(source)
    if not match:
        raise AssertionError(f"Procedure node not found: {node_id}")
    return match.group(1)


class MasLifecycleProcedureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modify_procedure = read(MODIFY / "assurance/procedure.yaml")
        cls.release_procedure = read(RELEASE / "assurance/procedure.yaml")
        cls.modify_contract = read(MODIFY / "assurance/contract.yaml")
        cls.release_contract = read(RELEASE / "assurance/contract.yaml")
        cls.modify_predicates = read(MODIFY / "assurance/predicates.yaml")
        cls.release_predicates = read(RELEASE / "assurance/predicates.yaml")
        cls.modify_request = read(MODIFY / "schemas/modify-request.schema.yaml")
        cls.release_request = read(RELEASE / "schemas/release-request.schema.yaml")
        cls.source_mapping = read(ROOT / "docs/mas-lifecycle-source-mapping.md")
        cls.owner_contract = read(ROOT / "docs/mas-lifecycle-owner-contract.md")
        cls.acceptance = read(ROOT / "docs/mas-lifecycle-acceptance-matrix.md")

    def test_mandatory_modify_and_release_operation_order(self) -> None:
        modify = re.findall(r"(?m)^      tool: mas::([A-Z0-9_]+\.[A-Z0-9_]+)$", self.modify_procedure)
        release = re.findall(r"(?m)^      tool: mas::([A-Z0-9_]+\.[A-Z0-9_]+)$", self.release_procedure)
        self.assertEqual(
            modify,
            [
                "SC.UPDATE_SM_CONTEXT",
                "UPN.MODIFY_UP_SESSION_INTENT",
                "SSM.SIGNAL_UE_AN_MODIFY",
                "UPN.MODIFY_UP_SESSION",
            ],
        )
        self.assertEqual(
            release,
            [
                "UPN.DELETE_UP_SESSION",
                "SSM.SIGNAL_UE_AN_RELEASE",
                "PA.DELETE_SM_POLICY",
                "SC.RELEASE_SM_CONTEXT",
                "SE.EMIT_RELEASE_EVENT",
            ],
        )

    def test_optional_charging_and_skipped_compensation_are_not_nodes(self) -> None:
        for source in (self.modify_procedure, self.release_procedure):
            self.assertNotIn("tool: mas::CA.UPDATE_CHARGING", source)
            self.assertNotIn("tool: mas::CA.DELETE_CHARGING", source)
            self.assertNotIn("COMPENSATE_RELEASE", source)
            self.assertNotRegex(source, r"(?m)^  r7:")
        self.assertIn("optional", self.source_mapping)
        self.assertIn("execute: skip", self.source_mapping)

    def test_m3_m5_and_ssm_profiles_are_not_widened(self) -> None:
        self.assertIn("UPN.MODIFY_UP_SESSION_INTENT", self.modify_procedure)
        self.assertIn("UPN.MODIFY_UP_SESSION", self.modify_procedure)
        self.assertIn("SSM.SIGNAL_UE_AN_MODIFY", self.modify_procedure)
        self.assertIn("SSM.SIGNAL_UE_AN_RELEASE", self.release_procedure)
        self.assertIn("upn-modify-intent-result", self.modify_predicates)
        self.assertIn("v0.2.0:upn-modify-up-session-result", self.modify_predicates)
        self.assertIn("v0.2.0:ssm-signal-ue-an-result", self.modify_predicates)
        self.assertIn("distinct typed callable profile", self.source_mapping)

    def test_release_trigger_is_numeric_and_entry_kind_is_explicit(self) -> None:
        self.assertIn("enum: [1, 2, 3, 4, 5, 6, 7]", self.release_request)
        for entry in ("UE_INITIATED", "AMF_INITIATED", "NETWORK_TRIGGERED"):
            self.assertIn(entry, self.release_request)
            self.assertIn(entry, self.release_predicates)
        for trigger in ("trigger == 1", "trigger == 2", "trigger == 3", "trigger == 4",
                        "trigger == 5", "trigger == 6", "trigger == 7"):
            self.assertIn(trigger, self.release_predicates)
        self.assertIn("RAN_INITIATED", self.source_mapping)

    def test_request_schemas_are_closed_and_only_carry_public_fields(self) -> None:
        for source in (self.modify_request, self.release_request):
            self.assertIn("additionalProperties: false", source)
            self.assertIn("pduSessionId", source)
            for private in ("sessionRef", "smContextRef", "generation", "stepId",
                            "invocationId", "idempotencyKey", "streamId"):
                self.assertNotIn(private, source)

    def test_preconditions_have_explicit_success_failure_and_unknown_routes(self) -> None:
        modify = node_block(self.modify_procedure, "validate-modify-request")
        release = node_block(self.release_procedure, "validate-release-request")
        for block, target in ((modify, "m0"), (release, "r2")):
            self.assertIn(f"PASS: {target}", block)
            self.assertIn("FAIL: FAILED", block)
            self.assertIn("UNKNOWN: UNRESOLVED", block)

    def test_every_mutation_has_fail_closed_unknown_route(self) -> None:
        expected = {
            self.modify_procedure: ("m0", "m3", "m4", "m5"),
            self.release_procedure: ("r2", "r3", "r4", "r5", "r6"),
        }
        for source, node_ids in expected.items():
            for node_id in node_ids:
                block = node_block(source, node_id)
                self.assertIn("OUTCOME_UNKNOWN: SAFE_STOPPED", block, node_id)
                self.assertIn("FAILED:", block, node_id)
                self.assertIn("DENIED:", block, node_id)

        self.assertIn("FAILED: FAILED", node_block(self.modify_procedure, "m0"))
        self.assertIn("DENIED: FAILED", node_block(self.modify_procedure, "m0"))
        self.assertIn("FAILED: FAILED", node_block(self.release_procedure, "r2"))
        self.assertIn("DENIED: FAILED", node_block(self.release_procedure, "r2"))
        for node_id in ("m3", "m4", "m5"):
            self.assertIn("FAILED: SAFE_STOPPED", node_block(self.modify_procedure, node_id))
            self.assertIn("DENIED: SAFE_STOPPED", node_block(self.modify_procedure, node_id))
        for node_id in ("r3", "r4", "r5", "r6"):
            self.assertIn("FAILED: SAFE_STOPPED", node_block(self.release_procedure, node_id))
            self.assertIn("DENIED: SAFE_STOPPED", node_block(self.release_procedure, node_id))

    def test_only_final_postcondition_can_publish_succeeded(self) -> None:
        for source in (self.modify_procedure, self.release_procedure):
            self.assertEqual(source.count("PASS: SUCCEEDED"), 1)
            self.assertNotIn("NOT_COMMITTED:", source)
            self.assertNotIn("COMMITTED:", source)
        self.assertIn("PASS: SUCCEEDED", node_block(self.modify_procedure, "verify-modify-completion"))
        self.assertIn("PASS: SUCCEEDED", node_block(self.release_procedure, "verify-release-completion"))

    def test_no_wait_retry_compensation_or_replan_is_authored(self) -> None:
        for source in (self.modify_procedure, self.release_procedure):
            self.assertNotRegex(source, r"(?m)^\s*wait\s*:")
            self.assertNotIn("NOT_COMMITTED:", source)
            self.assertNotIn("COMMITTED:", source)
        self.assertNotIn("retry", self.modify_procedure.lower())
        self.assertNotIn("retry", self.release_procedure.lower())

    def test_no_undeclared_release_output_fields_are_used(self) -> None:
        for source in (self.release_procedure, self.release_predicates):
            self.assertNotIn("terminated", source)
            self.assertNotIn("last_event", source)
        self.assertIn("r3.operation.output", self.release_procedure)
        self.assertIn("r4.operation.output", self.release_procedure)
        self.assertIn("r6.operation.output", self.release_procedure)
        self.assertIn("result != null", self.release_predicates)

    def test_release_plan_trigger_defect_is_recorded_as_blocking(self) -> None:
        self.assertIn("start_inputs: {}", self.source_mapping)
        self.assertIn("from_start: trigger", self.source_mapping)
        self.assertIn("must declare the typed trigger input", self.owner_contract)

    def test_source_pins_and_qualification_matrices_are_present(self) -> None:
        self.assertIn("594dec78b95bff4fdc34deac8a3a9681fb41228f", self.source_mapping)
        self.assertIn("8a2caf343c29bb64cbb09b29994c79ac8ad5da05", self.source_mapping)
        self.assertIn("849c3206569d452a663d1b8d42a63ffdc367be31", self.source_mapping)
        for skill in (MODIFY, RELEASE):
            mapping = read(skill / "references/openamsm-operation-mapping.md")
            self.assertIn("Qualification scenario matrix", mapping)

    def test_owner_and_runtime_qualification_are_not_claimed(self) -> None:
        self.assertIn("NOT PUBLISHED", self.owner_contract)
        self.assertIn("NOT_LINKABLE / NOT_QUALIFIED", self.owner_contract)
        self.assertIn("OUTCOME_UNKNOWN", self.owner_contract)
        self.assertIn("Runtime NOT_RUN", self.acceptance)
        self.assertIn("live 5GC E2E", self.acceptance)
        self.assertIn("in-memory", self.owner_contract)


if __name__ == "__main__":
    unittest.main()
