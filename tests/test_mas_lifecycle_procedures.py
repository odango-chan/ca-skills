"""Source-level regression guards for the MAS Modify / Release v1alpha5 drafts.

These tests check authored graph and provenance invariants only. They do not
simulate Owner receipts, Host concurrency, Runtime execution or live 5GC E2E.
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "skills"
MODIFY = EXAMPLES / "modify-pdu-session-mas"
RELEASE = EXAMPLES / "release-pdu-session-mas"
SOURCE_MAP = ROOT / "docs" / "mas-lifecycle-source-mapping.md"
OWNER_CONTRACT = ROOT / "docs" / "mas-lifecycle-owner-contract.md"
ACCEPTANCE = ROOT / "docs" / "mas-lifecycle-acceptance-matrix.md"

MODIFY_OPERATIONS = [
    "SC.UPDATE_SM_CONTEXT",
    "CA.UPDATE_CHARGING",
    "UPN.MODIFY_UP_SESSION",
    "SSM.SIGNAL_UE_AN",
    "UPN.MODIFY_UP_SESSION",
]
RELEASE_OPERATIONS = [
    "CA.DELETE_CHARGING",
    "UPN.DELETE_UP_SESSION",
    "SSM.SIGNAL_UE_AN",
    "PA.DELETE_SM_POLICY",
    "SC.RELEASE_SM_CONTEXT",
    "SE.EMIT_EVENTS",
]


def operation_ids(source: str) -> list[str]:
    return re.findall(r"(?m)^[ \t]+tool:[ \t]+mas::([A-Z_]+\.[A-Z_]+)[ \t]*$", source)


def node_block(source: str, node_id: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(node_id)}:\n(.*?)(?=^  [A-Za-z0-9-]+:[ \t]*$|\Z)",
        source,
    )
    if not match:
        raise AssertionError(f"missing Procedure node: {node_id}")
    return match.group(1)


class MASLifecycleProcedureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modify_procedure = (MODIFY / "assurance" / "procedure.yaml").read_text(encoding="utf-8")
        cls.release_procedure = (RELEASE / "assurance" / "procedure.yaml").read_text(encoding="utf-8")
        cls.modify_skill = (MODIFY / "SKILL.md").read_text(encoding="utf-8")
        cls.release_skill = (RELEASE / "SKILL.md").read_text(encoding="utf-8")
        cls.modify_request = (MODIFY / "schemas" / "modify-request.schema.yaml").read_text(encoding="utf-8")
        cls.release_request = (RELEASE / "schemas" / "release-request.schema.yaml").read_text(encoding="utf-8")
        cls.source_map = SOURCE_MAP.read_text(encoding="utf-8")
        cls.owner_contract = OWNER_CONTRACT.read_text(encoding="utf-8")
        cls.acceptance = ACCEPTANCE.read_text(encoding="utf-8")

    def test_exact_modify_source_occurrences(self) -> None:
        self.assertEqual(operation_ids(self.modify_procedure), MODIFY_OPERATIONS)
        for node_id in ("m0", "m2", "m3", "m4", "m5"):
            node_block(self.modify_procedure, node_id)

    def test_exact_release_source_occurrences_and_r7_exclusion(self) -> None:
        self.assertEqual(operation_ids(self.release_procedure), RELEASE_OPERATIONS)
        for node_id in ("r1", "r2", "r3", "r4", "r5", "r6"):
            node_block(self.release_procedure, node_id)
        self.assertNotIn("COMPENSATE_RELEASE", self.release_procedure)
        self.assertNotIn("compensate_then_replan_once", self.release_procedure)

    def test_every_mutation_has_fail_closed_outcome_routes(self) -> None:
        first_step = {"modify": "m0", "release": "r1"}
        for label, source in (("modify", self.modify_procedure), ("release", self.release_procedure)):
            nodes = ("m0", "m2", "m3", "m4", "m5") if label == "modify" else ("r1", "r2", "r3", "r4", "r5", "r6")
            first = first_step[label]
            for node_id in nodes:
                with self.subTest(procedure=label, node=node_id):
                    block = node_block(source, node_id)
                    self.assertIn("OUTCOME_UNKNOWN: SAFE_STOPPED", block)
                    self.assertIn("COMMITTED: SAFE_STOPPED", block)
                    if node_id == first:
                        self.assertIn("FAILED: FAILED", block)
                        self.assertIn("NOT_COMMITTED: FAILED", block)
                        self.assertIn("DENIED: FAILED", block)
                    else:
                        self.assertIn("FAILED: SAFE_STOPPED", block)
                        self.assertIn("NOT_COMMITTED: SAFE_STOPPED", block)
                        self.assertIn("DENIED: SAFE_STOPPED", block)

    def test_only_final_postcondition_can_publish_succeeded(self) -> None:
        for source in (self.modify_procedure, self.release_procedure):
            self.assertEqual(source.count("PASS: SUCCEEDED"), 1)
            self.assertNotIn("UNKNOWN: SUCCEEDED", source)
            self.assertNotIn("FAIL: SUCCEEDED", source)

    def test_request_schemas_model_entry_variants_and_private_boundary(self) -> None:
        for schema in (self.modify_request, self.release_request):
            for variant in ("UE_INITIATED", "AMF_INITIATED", "NETWORK_TRIGGERED"):
                self.assertIn(variant, schema)
            for private_name in ("sessionRef", "smContextRef", "generation", "stepId", "idempotencyKey"):
                self.assertNotIn(private_name, schema)
        for trigger in (
            "UE_REQUESTED",
            "AMF_UPDATE_SM_CONTEXT",
            "AMF_RELEASE_SM_CONTEXT",
            "PCF_INITIATED",
            "SMF_INITIATED",
            "LOCAL_INITIATED",
        ):
            self.assertIn(trigger, self.release_request)

    def test_source_plan_and_candidate_schema_provenance_are_pinned(self) -> None:
        self.assertIn("594dec78b95bff4fdc34deac8a3a9681fb41228f", self.source_map)
        self.assertIn("8a2caf343c29bb64cbb09b29994c79ac8ad5da05", self.source_map)
        self.assertIn("849c3206569d452a663d1b8d42a63ffdc367be31", self.source_map)
        self.assertIn("wtlab:openamsm:mas:v0.3.0:", self.source_map)

    def test_owner_contract_keeps_unknown_duplicate_generation_and_scope_fail_closed(self) -> None:
        for term in ("OUTCOME_UNKNOWN", "Duplicate original invocation", "Wrong generation", "Late callback", "Mixed UE"):
            self.assertIn(term, self.owner_contract)

    def test_acceptance_matrix_contains_required_scenarios(self) -> None:
        for term in ("Successful Modify", "Successful Release", "DENIED", "OUTCOME_UNKNOWN", "Duplicate invocation", "Wrong generation", "Late callback", "Mixed UE", "Establishment s10 callback"):
            self.assertIn(term, self.acceptance)

    def test_establishment_deferred_callback_is_not_a_new_skill_run(self) -> None:
        self.assertIn("s10 OWNER_DEFERRED", self.modify_skill)
        self.assertIn("same Establishment Run", self.modify_skill)
        self.assertIn("newer Run", self.release_skill)
        self.assertNotIn("wait:", self.modify_procedure)
        self.assertNotIn("wait:", self.release_procedure)

    def test_source_nonclaims_are_explicit(self) -> None:
        combined = self.modify_skill + self.release_skill + self.source_map
        self.assertIn("does not create a CHF charging reservation", combined)
        self.assertIn("not a 3GPP SM Context Status Notify", combined)
        self.assertNotIn("last_event:", self.release_procedure)
        self.assertNotIn("user_plane_ready:", self.release_procedure)
        self.assertNotIn("sm_context_ref:", self.release_procedure)

    def test_owner_publication_is_not_claimed(self) -> None:
        for source in (self.modify_skill, self.release_skill):
            self.assertIn("NOT_QUALIFIED / NOT_LINKABLE", source)
        self.assertIn("NOT PUBLISHED", self.owner_contract)


if __name__ == "__main__":
    unittest.main()
