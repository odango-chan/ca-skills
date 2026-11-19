"""Regression guards for the MAS v1alpha5 initial-session creation boundary.

These are repository-source invariants, not Owner, Compiler or E2E acceptance.
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "examples" / "skills" / "establish-pdu-session-mas"
EXPECTED_MAS_CALLABLES = {
    "SC.VALIDATE_SUBSCRIPTION",
    "SAA.SECONDARY_AUTH",
    "SC.CREATE_SM_CONTEXT",
    "SC.REGISTER_UECM",
    "PA.CREATE_SM_POLICY",
    "UPS.DECIDE_ANCHOR",
    "IAM.ALLOCATE_ADDRESS",
    "PA.UPDATE_SM_POLICY",
    "CA.CREATE_CHARGING",
    "UPN.CREATE_UP_SESSION",
    "SSM.SIGNAL_UE_AN",
    "UPN.MODIFY_UP_SESSION",
    "SE.EMIT_EVENTS",
}


class MASInitialIngressContractTests(unittest.TestCase):
    def setUp(self):
        self.procedure = (SKILL / "assurance/procedure.yaml").read_text(encoding="utf-8")
        self.contract = (SKILL / "assurance/contract.yaml").read_text(encoding="utf-8")
        self.predicates = (SKILL / "assurance/predicates.yaml").read_text(encoding="utf-8")
        self.skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_exactly_13_mas_operations_and_no_shadow_plan(self):
        actual = re.findall(r"(?m)^\s+tool:\s+mas::([A-Z_]+\.[A-Z_]+)\s*$", self.procedure)
        self.assertEqual(len(actual), 13)
        self.assertEqual(set(actual), EXPECTED_MAS_CALLABLES)
        self.assertIn("start: validate-sm-subscription", self.procedure)
        self.assertNotIn("COMPENSATE_RELEASE", self.procedure)

    def test_no_duplicated_smf_absence_or_amf_cm_gate(self):
        initial = self.procedure.split("  skip-secondary-authentication:", 1)[0]
        self.assertNotIn("observation:", initial)
        self.assertNotIn("context.smf.session.read", self.procedure)
        self.assertNotIn("session_context_absent", self.procedure)
        self.assertNotIn("session_context_absent", self.predicates)
        self.assertNotIn("sessionPresence", self.procedure)
        self.assertNotIn("ca-session-context:", self.contract)
        self.assertNotIn("smf.session.context.query", self.contract)
        self.assertNotIn("cm_state", self.procedure)
        self.assertNotIn("mm_state", self.procedure)
        self.assertNotIn("context.amf", self.procedure)
        self.assertIn("precondition: validate-sm-subscription.precondition", self.contract)

    def test_s1_mutation_unknown_is_never_treated_as_read_unknown(self):
        initial = self.procedure.split("  skip-secondary-authentication:", 1)[0]
        operation = initial.split("    operation:", 1)[1].split("    postcondition:", 1)[0]
        self.assertIn("OUTCOME_UNKNOWN: UNRESOLVED", operation)
        self.assertIn("FAILED: SAFE_STOPPED", operation)
        self.assertNotRegex(operation, r"(?m)^\s+UNKNOWN:\s+")
        self.assertEqual(len(re.findall(r"(?m)^\s+- mas\.[\w.]+\s*$", self.contract)), 13)

    def test_docs_do_not_claim_extra_precreation_gate(self):
        self.assertIn("replaces the initial PDU Session establishment", self.skill)
        self.assertIn("No `cm_state=connected` gate is required", self.skill)
        self.assertNotIn("only when the Observation proves `ABSENT`", self.skill)


if __name__ == "__main__":
    unittest.main()
