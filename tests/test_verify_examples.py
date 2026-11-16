"""Regression coverage for local v1alpha4 Script shape and closed-TypedDict links."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from verify_v1alpha4_examples import validate_example_scripts, validate_3gpp_traceability, validate_host_context_separation, validate_pcf_owner_boundary, validate_n4_owner_boundary, validate_async_update_sm_context_boundary, validate_predicate_scripts

SOURCE_PROCEDURE = """start: produce
nodes:
  produce:
    operation:
      script: scripts/produce.py
      arguments:
        x: context.x
      routes:
        SUCCEEDED: consume
        FAILED: FAILED
  consume:
    operation:
      script: scripts/consume.py
      arguments:
        data: produce.operation.output.data
      routes:
        SUCCEEDED: FAILED
        FAILED: FAILED
"""
PRODUCER = """from __future__ import annotations
from typing import TypedDict
class Source(TypedDict):
    a: int
    b: int
class Input(TypedDict):
    x: int
class Output(TypedDict):
    data: Source
def main(input: Input) -> Output:
    return {"data": {"a": input["x"], "b": input["x"]}}
"""
CONSUMER_CLOSED_MISMATCH = """from __future__ import annotations
from typing import TypedDict
class Target(TypedDict):
    a: int
class Input(TypedDict):
    data: Target
class Output(TypedDict):
    ok: bool
def main(input: Input) -> Output:
    return {"ok": True}
"""
CONSUMER_MATCHED = CONSUMER_CLOSED_MISMATCH.replace(
    "    a: int\nclass Input", "    a: int\n    b: int\nclass Input"
)

class V1Alpha4ScriptTests(unittest.TestCase):
    def lint(self, source: str = SOURCE_PROCEDURE,
             producer: str = PRODUCER,
             consumer: str = CONSUMER_MATCHED,
             unused: bool = False) -> list[str]:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text(source, encoding="utf-8")
            (root / "scripts" / "produce.py").write_text(producer, encoding="utf-8")
            (root / "scripts" / "consume.py").write_text(consumer, encoding="utf-8")
            if unused:
                (root / "scripts" / "unused.py").write_text(PRODUCER, encoding="utf-8")
            errors: list[str] = []
            validate_example_scripts(root, errors)
            return errors

    def test_every_procedure_node_requires_3gpp_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: retrieve
nodes:
  # 3GPP: 3GPP_NATIVE — TS 23.502 step 4
  retrieve:
    operation: {}
""", encoding="utf-8")
            tick = chr(96)
            doc = "\n".join([
                "## 3GPP Traceability", "",
                "TS 23.502 V18.12.0",
                "| Procedure Node | Mapping |", "|---|---|",
                "| " + tick + "retrieve" + tick + " | step 4 |",
            ])
            (root / "SKILL.md").write_text(doc, encoding="utf-8")
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertEqual(errors, [])


    def test_local_3gpp_step_classification_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: select
nodes:
  # 3GPP: 3GPP_LOCAL — TS 23.502 step 8; local SMF selection
  select:
    operation:
      script: scripts/select.py
""", encoding="utf-8")
            tick = chr(96)
            doc = "\n".join([
                "## 3GPP Traceability", "TS 23.502 V18.12.0",
                "| Procedure Node | Mapping |", "|---|---|",
                "| " + tick + "select" + tick + " | local SMF selection |",
            ])
            (root / "SKILL.md").write_text(doc, encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "select.py").write_text(
                "from typing import TypedDict\nclass Input(TypedDict):\n    x: int\nclass Output(TypedDict):\n    y: int\ndef main(input: Input) -> Output:\n    return {'y': input['x']}\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertEqual(errors, [])

    def test_author_wait_node_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: wait-for-n2-response
nodes:
  # 3GPP: CA_ADAPTER — TS 23.502 step 15
  wait-for-n2-response:
    operation:
      tool: ssm::SSM.SIGNAL_UE_AN
""", encoding="utf-8")
            tick = chr(96)
            doc = "\n".join([
                "## 3GPP Traceability", "TS 23.502 V18.12.0",
                "| Procedure Node | Mapping |", "|---|---|",
                "| " + tick + "wait-for-n2-response" + tick + " | step 15 |",
            ])
            (root / "SKILL.md").write_text(doc, encoding="utf-8")
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertTrue(any("author-level Wait/Await/Poll" in error for error in errors), errors)

    def test_legacy_waiter_ref_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: retrieve
nodes:
  # 3GPP: 3GPP_NATIVE — TS 23.502 step 4
  retrieve:
    operation:
      tool: udm::Nudm_SDM_Subscribe
      arguments:
        waiterRef: context.holdRef
""", encoding="utf-8")
            tick = chr(96)
            doc = "\n".join([
                "## 3GPP Traceability", "TS 23.502 V18.12.0",
                "| Procedure Node | Mapping |", "|---|---|",
                "| " + tick + "retrieve" + tick + " | step 4 |",
            ])
            (root / "SKILL.md").write_text(doc, encoding="utf-8")
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertTrue(any("legacy waiterRef" in error for error in errors), errors)

    def test_missing_node_mapping_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "assurance").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: retrieve
nodes:
  retrieve:
    operation: {}
""", encoding="utf-8")
            doc = "\n".join([
                "## 3GPP Traceability", "TS 23.502 V18.12.0",
                "| Procedure Node | Mapping |", "|---|---|",
            ])
            (root / "SKILL.md").write_text(doc, encoding="utf-8")
            errors: list[str] = []
            validate_3gpp_traceability(root, errors)
            self.assertTrue(any("missing adjacent" in error for error in errors), errors)
            self.assertTrue(any("missing SKILL.md" in error for error in errors), errors)

    def test_closed_nested_typed_dict_matches(self) -> None:
        self.assertEqual(self.lint(), [])

    def test_extra_source_key_is_input_type_mismatch(self) -> None:
        errors = self.lint(consumer=CONSUMER_CLOSED_MISMATCH)
        self.assertTrue(any("INPUT_TYPE_MISMATCH" in e for e in errors), errors)

    def test_unsafe_script_path_and_dead_code(self) -> None:
        errors = self.lint(source=SOURCE_PROCEDURE.replace(
            "scripts/consume.py", "scripts/../escape.py"
        ))
        self.assertTrue(any("unsafe Script ref" in e for e in errors), errors)
        errors = self.lint(unused=True)
        self.assertTrue(any("unreferenced Script" in e for e in errors), errors)

    def test_missing_script_and_wrong_signature(self) -> None:
        errors = self.lint(source=SOURCE_PROCEDURE.replace(
            "scripts/consume.py", "scripts/missing.py"
        ))
        self.assertTrue(any("Script not found" in e for e in errors), errors)
        errors = self.lint(producer=PRODUCER.replace(
            "def main(input: Input)", "def main(input: dict)"
        ))
        self.assertTrue(any("strict TypedDict" in e or "unresolved/recursive" in e for e in errors), errors)

    def test_ambient_import_is_rejected(self) -> None:
        errors = self.lint(producer="import os\n" + PRODUCER)
        self.assertTrue(any("forbidden external/ambient import" in e for e in errors), errors)

    def test_host_business_precondition_is_on_first_node(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "assurance" / "procedure.yaml").write_text("""start: get-sm-subscription-data
nodes:
  get-sm-subscription-data:
    precondition:
      predicates:
        - predicate: establishment.request.supported
          arguments: [context.request.requestType]
      routes:
        FAIL: FAILED
        UNKNOWN: UNRESOLVED
    operation:
      tool: ca::sbi.udm.sm_data.get
""", encoding="utf-8")
            (root / "assurance" / "contract.yaml").write_text(
                "precondition: get-sm-subscription-data.precondition\n"
                "contextSchema: ca-context::urn:connectionagent:ca:context:subject:v1\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_host_context_separation(root, errors)
            self.assertEqual(errors, [])

    def test_host_lifecycle_and_ingress_are_rejected_as_skill_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "assurance" / "procedure.yaml").write_text("""start: admit-create-sm-context-request
nodes:
  admit-create-sm-context-request:
    precondition:
      predicates:
        - predicate: host.lifecycle.ready
          arguments:
            - context.lifecycle
        - predicate: host.ingress.eligible
          arguments:
            - context.ingress
    operation:
      tool: ca::sbi.udm.sm_data.get
      arguments:
        lifecycleRef: context.lifecycleRef
""", encoding="utf-8")
            (root / "assurance" / "contract.yaml").write_text(
                "precondition: admit-create-sm-context-request.precondition\n"
                "contextSchema: ca-context::urn:connectionagent:ca:context:subject:v1\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_host_context_separation(root, errors)
            self.assertTrue(any("Host ingress/lifecycle/correlation context" in e for e in errors), errors)
            self.assertTrue(any("Host dispatch metadata" in e for e in errors), errors)
            self.assertTrue(any("must not be an authored Procedure Node" in e for e in errors), errors)

    def test_pcf_request_preparation_is_inside_single_owner_node(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: get-sm-subscription-data
nodes:
  establish-sm-policy-association:
    operation:
      tool: ca::sbi.pcf.sm_policy.create
      arguments:
        ueRef: context.ueRef
        request: context.request
        udmReadResult: get-sm-subscription-data.operation.output.result
        sdmSubscriptionRef: subscribe-sm-data.operation.output.subscriptionRef
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("""predicates:
  establishment.pcf.association_owned:
    parameters:
      - association: ca::urn:example:5gc:pcf-association-resource:v1
    evidence:
      requires:
        association: [ca::pcf.association-owned]
    evaluator:
      type: cel
      expression: association.creationState == "CREATED"
""", encoding="utf-8")
            errors: list[str] = []
            validate_pcf_owner_boundary(root, errors)
            self.assertEqual(errors, [])

    def test_pcf_script_split_and_skill_facing_input_evidence_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: build-sm-policy-association-inputs
nodes:
  build-sm-policy-association-inputs:
    operation:
      script: scripts/build-pcf-policy-inputs.py
  establish-sm-policy-association:
    operation:
      tool: ca::sbi.pcf.sm_policy.create
      arguments:
        policyInputs: build-sm-policy-association-inputs.operation.output
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("""predicates:
  establishment.pcf.association_owned:
    parameters:
      - association: ca::urn:example:5gc:pcf-association-resource:v1
      - inputs: ca::urn:example:5gc:pcf-create-inputs:v1
    evidence:
      requires:
        inputs: [ca::pcf.create-inputs-current]
""", encoding="utf-8")
            (root / "scripts" / "build-pcf-policy-inputs.py").write_text("# obsolete\n", encoding="utf-8")
            errors: list[str] = []
            validate_pcf_owner_boundary(root, errors)
            self.assertTrue(any("must not be a separate Skill Node" in e for e in errors), errors)
            self.assertTrue(any("must be removed" in e for e in errors), errors)
            self.assertTrue(any("must not pass a separately constructed" in e for e in errors), errors)
            self.assertTrue(any("must remain internal" in e for e in errors), errors)

    def test_step8_native_selection_is_folded_into_n4_owner(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""nodes:
  establish-n4-session:
    operation:
      tool: upn::UPN.CREATE_UP_SESSION
      arguments:
        ueRef: context.ueRef
        request: context.request
        udmReadResult: get-sm-subscription-data.operation.output.result
        policyAssociationRef: establish-sm-policy-association.operation.output.policyAssociationRef
        policyResultRef: establish-sm-policy-association.operation.output.policyResultRef
  transfer-n1n2-message:
    operation:
      tool: ca::sbi.amf.n1n2.transfer
      arguments:
        initialN4Result: establish-n4-session.operation.output
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("""predicates:
  establishment.subscription.request_valid:
    evaluator:
      type: script
      script: scripts/validate-subscription-request.py
""", encoding="utf-8")
            (root / "SKILL.md").write_text(
                "| \x60establish-n4-session\x60 | step 8 native SMF session/UPF selection, then steps 10a–10b; §4.4.1.2 |\\n",
                encoding="utf-8",
            )
            errors: list[str] = []
            validate_n4_owner_boundary(root, errors)
            self.assertEqual(errors, [])

    def test_step8_script_split_and_separate_selection_payload_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""nodes:
  select-session-configuration:
    operation:
      script: scripts/select-establishment-configuration.py
  establish-n4-session:
    operation:
      tool: upn::UPN.CREATE_UP_SESSION
      arguments:
        selection: select-session-configuration.operation.output
  transfer-n1n2-message:
    operation:
      tool: ca::sbi.amf.n1n2.transfer
      arguments:
        selection: select-session-configuration.operation.output
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("predicates: {}\\n", encoding="utf-8")
            (root / "SKILL.md").write_text("| \x60select-session-configuration\x60 | step 8 |\\n", encoding="utf-8")
            (root / "scripts" / "select-establishment-configuration.py").write_text("# obsolete\\n", encoding="utf-8")
            errors: list[str] = []
            validate_n4_owner_boundary(root, errors)
            self.assertTrue(any("must not be a separate Procedure Node" in e for e in errors), errors)
            self.assertTrue(any("must receive the admitted request" in e for e in errors), errors)
            self.assertTrue(any("separate Skill-generated selection payload" in e for e in errors), errors)
            self.assertTrue(any("separate Step 8 Script payload" in e for e in errors), errors)

    def test_predicate_script_uses_generated_input_and_result_contract(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "predicates.yaml").write_text("""predicates:
  establishment.subscription.request_valid:
    evaluator:
      type: script
      script: scripts/check.py
""", encoding="utf-8")
            (root / "scripts" / "check.py").write_text("""from __future__ import annotations
from typing import Annotated, Literal, TypedDict
class PredicateEvaluationResult(TypedDict):
    result: Literal["PASS", "FAIL", "UNKNOWN"]
    reasonCode: Annotated[str, {"minLength": 1}]
    evidenceUsed: list[str]
def main(input: PredicateInput) -> PredicateEvaluationResult:
    return {"result": "PASS", "reasonCode": "OK", "evidenceUsed": []}
""", encoding="utf-8")
            errors: list[str] = []
            refs = validate_predicate_scripts(root, errors)
            self.assertEqual(errors, [])
            self.assertIn((root / "scripts" / "check.py").resolve(), refs)

    def test_update_sm_context_resumes_same_invocation_and_reads_generic_smf_context(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""start: read-existing-sm-context
nodes:
  read-existing-sm-context:
    precondition:
      predicates:
        - predicate: establishment.request.supported
          arguments:
            - context.request.requestType
    observation:
      tool: ca::context.smf.session.read
      arguments:
        ueRef: context.ueRef
        pduSessionId: context.request.pduSessionId
    postcondition:
      predicates:
        - predicate: establishment.smf.session_context_absent
          arguments:
            - read-existing-sm-context.observation.output
      routes:
        PASS: get-sm-subscription-data
        FAIL: SAFE_STOPPED
        UNKNOWN: SAFE_STOPPED
  get-sm-subscription-data:
    operation:
      tool: ca::sbi.udm.sm_data.get
      routes:
        SUCCEEDED: transfer-n1n2-message
  transfer-n1n2-message:
    operation:
      tool: ca::sbi.amf.n1n2.transfer
    postcondition:
      predicates:
        - predicate: establishment.amf.transfer_initiated
          arguments:
            - transfer-n1n2-message.operation.output
      routes:
        PASS: update-sm-context
  update-sm-context:
    operation:
      tool: ssm::SSM.SIGNAL_UE_AN
      arguments:
        transferOperationRef: transfer-n1n2-message.operation.output.operationRef
    postcondition:
      predicates:
        - predicate: establishment.ran.adopted
          arguments:
            - update-sm-context.operation.output
      routes:
        PASS: read-smf-session-context
  read-smf-session-context:
    observation:
      tool: ca::context.smf.session.read
      arguments:
        ueRef: context.ueRef
        pduSessionId: context.request.pduSessionId
    postcondition:
      predicates:
        - predicate: establishment.smf.session_context_profile_ready
          arguments:
            - read-smf-session-context.observation.output
            - context.request.dnn
            - context.request.sNssai.sst
      routes:
        PASS: modify-n4-session
  modify-n4-session:
    operation:
      tool: upn::UPN.MODIFY_UP_SESSION
      arguments:
        initialN4Result: establish-n4-session.operation.output
        ranResult: update-sm-context.operation.output
    postcondition:
      predicates:
        - predicate: establishment.n4.forwarding_ready
          arguments:
            - modify-n4-session.operation.output
      routes:
        PASS: ca-transfer-resource-responsibility
  verify-pdu-session-establishment:
    postcondition:
      predicates:
        - predicate: establishment.ran.adopted
          arguments:
            - update-sm-context.operation.output
        - predicate: establishment.n4.forwarding_ready
          arguments:
            - modify-n4-session.operation.output
""", encoding="utf-8")
            (root / "assurance" / "contract.yaml").write_text("""dependencies:
  ca: urn:example:connectionagent:5gc-tool-contracts
capabilities:
  - urn:example:connectionagent:capability:ca:smf-session-context-read:v1
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("""predicates:
  establishment.smf.session_context_absent:
    parameters:
      - sessionContext: ca::urn:example:5gc:smf-session-context:v1
    evidence:
      requires:
        sessionContext: [ca::smf.session-context.query-evidence]
    evaluator:
      type: script
      script: scripts/validate-smf-session-context-entry.py
  establishment.smf.session_context_profile_ready:
    parameters:
      - sessionContext: ca::urn:example:5gc:smf-session-context:v1
    evidence:
      requires:
        sessionContext: [ca::smf.session-context.query-evidence]
    evaluator:
      type: script
      script: scripts/validate-smf-session-context.py
""", encoding="utf-8")
            (root / "scripts" / "validate-smf-session-context-entry.py").write_text("""def main(input: PredicateInput) -> PredicateEvaluationResult:
    return {"result": "PASS", "reasonCode": "SMF_SESSION_CONTEXT_CONFIRMED_ABSENT", "evidenceUsed": []}
""", encoding="utf-8")
            (root / "scripts" / "validate-smf-session-context.py").write_text("""def main(input: PredicateInput) -> PredicateEvaluationResult:
    return {"result": "PASS", "reasonCode": "OK", "evidenceUsed": []}
""", encoding="utf-8")
            (root / "SKILL.md").write_text("""| \x60read-existing-sm-context\x60 | exact UE/PSI context existence before initial mutations |
| \x60update-sm-context\x60 | step 15 — \x60Nsmf_PDUSession_UpdateSMContext Request\x60 |
| \x60read-smf-session-context\x60 | current SMF session context after step 15 |
| \x60modify-n4-session\x60 | steps 16a–16b — N4 Session Modification |
Runtime resumes the same Invocation; Host returns the paired step 17 response.
""", encoding="utf-8")
            errors: list[str] = []
            validate_async_update_sm_context_boundary(root, errors)
            self.assertEqual(errors, [])

    def test_entry_context_predicate_distinguishes_absent_present_and_unknown(self) -> None:
        import runpy

        main = runpy.run_path(
            str(ROOT / "examples" / "skills" / "establish-pdu-session" / "scripts" / "validate-smf-session-context-entry.py")
        )["main"]
        def evaluate(presence: str) -> dict:
            return main({
                "evidence": {"sessionContext": {"refs": ["evidence:query"]}},
                "sessionContext": {"sessionPresence": presence},
            })
        self.assertEqual(evaluate("ABSENT")["result"], "PASS")
        self.assertEqual(evaluate("ABSENT")["reasonCode"], "SMF_SESSION_CONTEXT_CONFIRMED_ABSENT")
        self.assertEqual(evaluate("PRESENT")["result"], "FAIL")
        self.assertEqual(evaluate("PRESENT")["reasonCode"], "SMF_SESSION_CONTEXT_ALREADY_PRESENT")
        self.assertEqual(evaluate("UNKNOWN")["result"], "UNKNOWN")
        self.assertEqual(evaluate("UNKNOWN")["reasonCode"], "SMF_SESSION_CONTEXT_PRESENCE_UNKNOWN")

        no_evidence = main({
            "evidence": {"sessionContext": {"refs": []}},
            "sessionContext": {"sessionPresence": "ABSENT"},
        })
        self.assertEqual(no_evidence["result"], "UNKNOWN")

        post_main = runpy.run_path(
            str(ROOT / "examples" / "skills" / "establish-pdu-session" / "scripts" / "validate-smf-session-context.py")
        )["main"]
        def evaluate_post(presence: str, projection: str) -> dict:
            return post_main({
                "evidence": {"sessionContext": {"refs": ["evidence:query"]}},
                "sessionContext": {
                    "sessionPresence": presence,
                    "projectionStatus": projection,
                    "context": {
                        "dnn": "internet",
                        "sst": 1,
                        "subscriptionValidated": True,
                        "secondaryAuthRequired": False,
                    },
                },
                "requestedDnn": "internet",
                "requestedSst": 1,
            })
        self.assertEqual(evaluate_post("ABSENT", "UNAVAILABLE")["result"], "FAIL")
        self.assertEqual(evaluate_post("PRESENT", "UNAVAILABLE")["result"], "UNKNOWN")
        self.assertEqual(evaluate_post("PRESENT", "AVAILABLE")["result"], "PASS")

    def test_conventional_skill_requires_context_observation_and_rejects_mas_names(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""nodes:
  update-sm-context:
    operation:
      tool: ssm::SSM.SIGNAL_UE_AN
      routes:
        PASS: modify-n4-session
  modify-n4-session:
    operation:
      tool: upn::UPN.MODIFY_UP_SESSION
""", encoding="utf-8")
            (root / "assurance" / "contract.yaml").write_text("""dependencies:
  smf-mas-observations: urn:connectionagent:ca:5gc:smf-mas-observations
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("predicates: {}\n", encoding="utf-8")
            (root / "SKILL.md").write_text("This conventional Skill must not mention MAS.\n", encoding="utf-8")
            errors: list[str] = []
            validate_async_update_sm_context_boundary(root, errors)
            self.assertTrue(any("must not declare or mention MAS implementation details" in e for e in errors), errors)
            self.assertTrue(any("missing explicit post-callback SMF session-context Observation" in e for e in errors), errors)

    def test_update_sm_context_must_not_restart_or_leak_host_correlation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "establish-pdu-session"
            (root / "assurance").mkdir(parents=True)
            (root / "scripts").mkdir()
            (root / "assurance" / "procedure.yaml").write_text("""nodes:
  transfer-n1n2-message:
    operation:
      tool: ca::sbi.amf.n1n2.transfer
      routes:
        SUCCEEDED: complete-an-resource-setup
  complete-an-resource-setup:
    operation:
      tool: ssm::SSM.SIGNAL_UE_AN
      arguments:
        lifecycleRef: context.lifecycleRef
""", encoding="utf-8")
            (root / "assurance" / "contract.yaml").write_text("""dependencies:
  smf-mas-observations: urn:connectionagent:ca:5gc:smf-mas-observations
capabilities:
  - urn:example:connectionagent:capability:ca:smf-mas-sc-context-read:v1
""", encoding="utf-8")
            (root / "assurance" / "predicates.yaml").write_text("predicates: {}\n", encoding="utf-8")
            (root / "SKILL.md").write_text("## 3GPP Traceability\n", encoding="utf-8")
            errors: list[str] = []
            validate_async_update_sm_context_boundary(root, errors)
            self.assertTrue(any("canonical update-sm-context" in e for e in errors), errors)
            self.assertTrue(any("missing step-15 update-sm-context" in e for e in errors), errors)
            self.assertTrue(any("Host ingress, lifecycle and transport response metadata" in e for e in errors), errors)

if __name__ == "__main__":
    unittest.main()
