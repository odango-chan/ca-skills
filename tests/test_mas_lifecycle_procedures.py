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


def predicate_block(source: str, name: str) -> str:
    pattern = re.compile(
        rf"(?ms)^  {re.escape(name)}:\n(.*?)(?=^  [A-Za-z0-9_.-]+:\n|\Z)"
    )
    match = pattern.search(source)
    if not match:
        raise AssertionError(f"Predicate not found: {name}")
    return match.group(1)


def procedure_node_ids(source: str) -> list[str]:
    return re.findall(r"(?m)^  ([a-z0-9][a-z0-9-]*):$", source)


def tool_sequence(source: str) -> list[str]:
    return re.findall(r"(?m)^      tool: mas::([A-Z0-9_]+\.[A-Z0-9_]+)$", source)


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
        cls.modify_skill = read(MODIFY / "SKILL.md")
        cls.release_skill = read(RELEASE / "SKILL.md")
        cls.modify_mapping = read(MODIFY / "references/openamsm-operation-mapping.md")
        cls.release_mapping = read(RELEASE / "references/openamsm-operation-mapping.md")
        cls.source_mapping = read(ROOT / "docs/mas-lifecycle-source-mapping.md")
        cls.owner_contract = read(ROOT / "docs/mas-lifecycle-owner-contract.md")
        cls.acceptance = read(ROOT / "docs/mas-lifecycle-acceptance-matrix.md")

    # -- Scheme C graph -----------------------------------------------------

    def test_mandatory_modify_and_release_operation_order(self) -> None:
        self.assertEqual(
            tool_sequence(self.modify_procedure),
            [
                "SSM.PARSE_N1_MODIFY",
                "UPN.MODIFY_QOS_DELTA",
            ],
        )
        self.assertEqual(
            tool_sequence(self.release_procedure),
            [
                "SSM.PARSE_N1_RELEASE",
                "SSM.BUILD_RELEASE_COMMAND",
                "SSM.RELEASE_CONFIRM_N1",
                "SSM.RELEASE_CONFIRM_N2",
                "PA.DELETE_SM_POLICY_C",
                "UPN.DELETE_UP_SESSION",
                "SE.EMIT_RELEASE_EVENT_C",
                "SC.RELEASE_SM_CONTEXT_C",
            ],
        )

    def test_old_oes_operations_are_not_used(self) -> None:
        # The superseded OES-shaped callables must not survive in the
        # Procedure sources; the merged Owner Scheme C callables replace them.
        for old_tool in (
            "SC.UPDATE_SM_CONTEXT",
            "UPN.MODIFY_UP_SESSION_INTENT",
            "SSM.SIGNAL_UE_AN_MODIFY",
            "UPN.MODIFY_QOS_FLOWS",
            "SSM.SIGNAL_UE_AN_RELEASE",
            "PA.DELETE_SM_POLICY",
            "SC.RELEASE_SM_CONTEXT",
            "SE.EMIT_RELEASE_EVENT",
        ):
            self.assertNotIn(
                f"tool: mas::{old_tool}\n",
                self.modify_procedure + self.release_procedure,
            )

    def test_procedure_node_ids_match_scheme_c(self) -> None:
        self.assertEqual(
            procedure_node_ids(self.modify_procedure),
            [
                "validate-modify-request",
                "parse-n1",
                "apply-qos-delta",
                "verify-modify-completion",
            ],
        )
        self.assertEqual(
            procedure_node_ids(self.release_procedure),
            [
                "validate-release-request",
                "parse-n1",
                "build-command",
                "confirm-n1",
                "confirm-n2",
                "delete-policy",
                "delete-user-plane",
                "emit-release-event",
                "release-sm-context",
                "verify-release-completion",
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

    # -- parse read-only / mutation fail-closed routes ----------------------

    def test_parse_is_read_only_and_has_no_mutation_routes(self) -> None:
        for source, tool, next_node in (
            (self.modify_procedure, "SSM.PARSE_N1_MODIFY", "apply-qos-delta"),
            (self.release_procedure, "SSM.PARSE_N1_RELEASE", "build-command"),
        ):
            block = node_block(source, "parse-n1")
            self.assertIn(f"tool: mas::{tool}", block)
            self.assertIn('parse_n1: "1"', block)
            # A READ occurrence has no commit ambiguity: no OUTCOME_UNKNOWN.
            self.assertNotIn("OUTCOME_UNKNOWN", block)
            self.assertIn("FAILED: FAILED", block)
            self.assertIn("DENIED: FAILED", block)
            self.assertRegex(block, rf"PASS: {re.escape(next_node)}")
        self.assertIn("must not mutate session state", self.source_mapping)
        self.assertIn("read-only", self.source_mapping)

    def test_preconditions_gate_on_public_admission_and_route(self) -> None:
        modify = node_block(self.modify_procedure, "validate-modify-request")
        release = node_block(self.release_procedure, "validate-release-request")
        for block in (modify, release):
            self.assertIn("PASS: parse-n1", block)
            self.assertIn("FAIL: FAILED", block)
            self.assertIn("UNKNOWN: UNRESOLVED", block)

    def test_every_mutation_has_fail_closed_unknown_route(self) -> None:
        modify_mutations = ("apply-qos-delta",)
        release_mutations = (
            "build-command",
            "confirm-n1",
            "confirm-n2",
            "delete-policy",
            "delete-user-plane",
            "emit-release-event",
            "release-sm-context",
        )
        for source, node_ids in (
            (self.modify_procedure, modify_mutations),
            (self.release_procedure, release_mutations),
        ):
            for node_id in node_ids:
                block = node_block(source, node_id)
                self.assertIn("OUTCOME_UNKNOWN: SAFE_STOPPED", block, node_id)
                self.assertIn("FAILED:", block, node_id)
                self.assertIn("DENIED:", block, node_id)

        # The first Modify mutation is still pre-commit, so it may terminate
        # FAILED; release mutations after Build only SAFE_STOP.
        self.assertIn("FAILED: FAILED", node_block(self.modify_procedure, "apply-qos-delta"))
        self.assertIn("DENIED: FAILED", node_block(self.modify_procedure, "apply-qos-delta"))

    def test_only_final_postcondition_can_publish_succeeded(self) -> None:
        for source in (self.modify_procedure, self.release_procedure):
            self.assertEqual(source.count("PASS: SUCCEEDED"), 1)
            self.assertNotIn("NOT_COMMITTED:", source)
            self.assertNotIn("COMMITTED:", source)
        self.assertIn(
            "PASS: SUCCEEDED", node_block(self.modify_procedure, "verify-modify-completion")
        )
        self.assertIn(
            "PASS: SUCCEEDED", node_block(self.release_procedure, "verify-release-completion")
        )

    def test_no_wait_retry_compensation_or_replan_is_authored(self) -> None:
        for source in (self.modify_procedure, self.release_procedure):
            self.assertNotRegex(source, r"(?m)^\s*wait\s*:")
            self.assertNotIn("NOT_COMMITTED:", source)
            self.assertNotIn("COMMITTED:", source)
            lowered = source.lower()
            for forbidden in ("retry", "replan", "compensat"):
                self.assertNotIn(forbidden, lowered)

    # -- closed public request schemas --------------------------------------

    def test_request_schemas_are_closed_and_only_carry_public_fields(self) -> None:
        for source in (self.modify_request, self.release_request):
            self.assertIn("additionalProperties: false", source)
            self.assertIn("pduSessionId", source)
            self.assertIn("entryKind", source)
            for private in (
                "sessionRef",
                "smContextRef",
                "generation",
                "stepId",
                "invocationId",
                "idempotencyKey",
                "streamId",
            ):
                self.assertNotIn(private, source)

        self.assertIn("required: [pduSessionId, entryKind]", self.modify_request)
        self.assertIn("required: [pduSessionId, entryKind, trigger]", self.release_request)

        # The raw N1, the Host-private release transaction and the parsed QoS
        # delta are Host-private / Provider-injected, never request fields.
        for forbidden in ("n1Sm", "releaseTxn", "qosFlowsDelta"):
            self.assertNotIn(forbidden, self.modify_request)
            self.assertNotIn(forbidden, self.release_request)

    def test_release_entry_variant_and_numeric_trigger_are_public(self) -> None:
        self.assertIn("enum: [UE_INITIATED]", self.release_request)
        self.assertIn("enum: [1, 2, 3, 4, 5, 6, 7]", self.release_request)
        admitted = predicate_block(self.release_predicates, "release.request.admitted")
        self.assertIn('entryKind == "UE_INITIATED"', admitted)
        for node_id in ("build-command", "delete-policy", "release-sm-context"):
            self.assertIn(
                "trigger: context.request.trigger",
                node_block(self.release_procedure, node_id),
            )

    def test_request_admitted_predicates_take_only_public_inputs(self) -> None:
        for source, name in (
            (self.modify_predicates, "modify.request.admitted"),
            (self.release_predicates, "release.request.admitted"),
        ):
            block = predicate_block(source, name)
            for field in ("supi: string", "pduSessionId: integer", "entryKind: string"):
                self.assertIn(field, block)
            for private in ("qfi", "five_qi", "gfbr_", "mfbr_", "releaseTxn", "n1Sm"):
                self.assertNotIn(private, block)
            self.assertIn("pduSessionId <= 15", block)
            self.assertIn('supi != ""', block)

    def test_modify_request_does_not_carry_qos_delta_or_pattern(self) -> None:
        # CA-SL v1alpha5 rejects `pattern` in a Skill-owned request Schema.
        self.assertNotIn("pattern:", self.modify_request)
        for field in ("qfi", "fiveQi", "gfbrUl", "gfbrDl", "mfbrUl", "mfbrDl"):
            self.assertNotIn(field + ":", self.modify_request)

        apply_block = node_block(self.modify_procedure, "apply-qos-delta")
        for field in ("qfi", "five_qi", "gfbr_ul", "gfbr_dl", "mfbr_ul", "mfbr_dl"):
            self.assertIn(
                f"{field}: parse-n1.operation.output.{field}",
                apply_block,
            )
        self.assertNotIn("context.request.qosFlowsDelta", self.modify_procedure)

    # -- modify postcondition: applied result vs parsed Owner target --------

    def test_modify_qos_postcondition_compares_the_parsed_target(self) -> None:
        block = predicate_block(self.modify_predicates, "modify.mas.qos_delta_applied")
        positions = [block.index(name) for name in ("- result:", "- parsed:")]
        self.assertEqual(positions, sorted(positions))
        for field in ("qfi", "five_qi", "gfbr_ul", "gfbr_dl", "mfbr_ul", "mfbr_dl"):
            self.assertIn(f"result.{field} == parsed.{field}", block)
        self.assertIn("has(result.five_qi)", block)
        self.assertIn('result.n1n2_dispatched == "1"', block)
        self.assertIn("!has(result.n1n2_dispatched)", block)
        self.assertIn('qos_delta_state == "APPLIED"', block)
        self.assertIn('qos_delta_state == "ALREADY"', block)
        # No numeric coercion or ordering is introduced for decimal strings.
        for forbidden in ("int(", "double(", "float("):
            self.assertNotIn(forbidden, block)

    def test_modify_postcondition_call_sites_bind_result_and_parsed(self) -> None:
        call = re.compile(
            r"(?ms)- predicate: modify\.mas\.qos_delta_applied\n"
            r"          arguments:\n((?:            - [^\n]*\n)+)"
        )
        matches = call.findall(self.modify_procedure)
        self.assertEqual(
            len(matches), 2, "apply-qos-delta and verify-modify-completion must both bind"
        )
        expected = [
            "apply-qos-delta.operation.output",
            "parse-n1.operation.output",
        ]
        for block in matches:
            self.assertEqual([line.strip()[2:] for line in block.splitlines()], expected)

    def test_modify_goal_scope_is_documented_as_pfcp_plus_dispatch(self) -> None:
        for source in (self.modify_skill, self.modify_mapping):
            for marker in (
                "canonical decimal",
                "PFCP_APPLIED",
                "N1N2_DISPATCHED",
                "RAN_MODIFICATION_CONFIRMED",
                "TARGET_STATE_VERIFIED",
            ):
                self.assertIn(marker, source)
        self.assertIn("target state verified", self.modify_mapping)

    # -- release predicates use only declared Owner outputs -----------------

    def test_release_predicates_use_only_declared_owner_output_fields(self) -> None:
        allowed = {
            "ssm-parse-n1-release-result": {"release_intent", "psi", "pti", "cause"},
            "ssm-build-release-command-result": {
                "release_phase",
                "n1_sm_hex",
                "n2_sm_hex",
                "n2_sm_info_type",
                "release_txn",
                "release_generation",
            },
            "ssm-release-confirm-n1-result": {"n1_released"},
            "ssm-release-confirm-n2-result": {"n2_released", "release_ready"},
            "pa-delete-sm-policy-result": {"terminated"},
            "upn-delete-up-session-result": {"released"},
            "se-emit-release-event-result": {"last_event"},
            "sc-release-sm-context-result": {"lifecycle"},
        }
        predicates = re.findall(r"(?m)^  (release\.[a-z0-9_.]+):$", self.release_predicates)
        self.assertGreaterEqual(len(predicates), 8)
        for name in predicates:
            block = predicate_block(self.release_predicates, name)
            type_match = re.search(r"- result:\s+mas::\S+:([\w-]+)", block)
            if type_match is None:
                # release.request.admitted takes only public request values.
                self.assertEqual(name, "release.request.admitted")
                continue
            result_type = type_match.group(1)
            self.assertIn(result_type, allowed, name)
            used = set(re.findall(r"\bresult\.([a-z0-9_]+)", block))
            undeclared = used - allowed[result_type]
            self.assertEqual(undeclared, set(), f"{name} uses undeclared Owner output fields")

        # The Scheme C Owner really exposes these outputs; do not hide them.
        for field in (
            "release_ready",
            "n1_released",
            "n2_released",
            "terminated",
            "released",
            "last_event",
            "lifecycle",
        ):
            self.assertIn(field, self.release_predicates)

    # -- docs / qualification honesty ---------------------------------------

    def test_private_request_fields_and_run_binding_are_documented(self) -> None:
        for phrase in (
            "raw N1",
            "release transaction id",
            "not Skill-authored request fields",
            "A confirmation must be bound to the original Run",
        ):
            self.assertIn(phrase, self.owner_contract)

    def test_docs_describe_scheme_c_not_the_old_oes_shape(self) -> None:
        for source in (self.source_mapping, self.acceptance):
            self.assertNotIn("m0 -> m3 -> m4 -> m5", source)
            self.assertNotIn("r2 -> r3 -> r4 -> r5 -> r6", source)
        self.assertIn("Scheme C", self.source_mapping)
        self.assertIn("SSM.PARSE_N1_MODIFY", self.source_mapping)
        self.assertIn("UPN.MODIFY_QOS_DELTA", self.source_mapping)
        self.assertIn("superseded", self.source_mapping)

    def test_release_parse_and_build_binding_are_documented(self) -> None:
        self.assertIn("only PTI binding", self.release_mapping)
        self.assertIn("read-only", self.release_mapping)
        self.assertIn("must not mutate session state", self.release_mapping)

    def test_source_pins_and_qualification_matrices_are_present(self) -> None:
        self.assertIn("594dec78b95bff4fdc34deac8a3a9681fb41228f", self.source_mapping)
        self.assertIn("8a2caf343c29bb64cbb09b29994c79ac8ad5da05", self.source_mapping)
        self.assertIn("849c3206569d452a663d1b8d42a63ffdc367be31", self.source_mapping)
        for mapping in (self.modify_mapping, self.release_mapping):
            self.assertIn("Qualification scenario matrix", mapping)

    def test_owner_and_runtime_qualification_are_not_claimed(self) -> None:
        self.assertIn("NOT PUBLISHED", self.owner_contract)
        self.assertIn("NOT_LINKABLE / NOT_QUALIFIED", self.owner_contract)
        self.assertIn("OUTCOME_UNKNOWN", self.owner_contract)
        self.assertIn("in-memory", self.owner_contract)
        self.assertIn("Runtime NOT_RUN", self.acceptance)
        self.assertIn("live 5GC E2E", self.acceptance)
        self.assertIn("NOT_QUALIFIED / NOT_LINKABLE", self.source_mapping)
        for mapping in (self.modify_mapping, self.release_mapping):
            self.assertIn("NOT_QUALIFIED / NOT_LINKABLE", mapping)


if __name__ == "__main__":
    unittest.main()
