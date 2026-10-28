"""Regression tests for the deterministic CreatedSession Skill scripts."""
from pathlib import Path
from runpy import run_path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/establish-pdu-session"
select_configuration = run_path(str(SKILL / "scripts/select_establishment_configuration.py"))["main"]
evaluate_udm_read = run_path(str(SKILL / "scripts/evaluate_udm_read.py"))["main"]
evaluate_transfer_start = run_path(str(SKILL / "scripts/evaluate_transfer_start.py"))["main"]


def selection_input():
    return {
        "dnn": "internet",
        "sNssai": {"sst": 1, "sd": 0},
        "requestedPduSessionType": "IPV4",
        "requestedSscMode": 1,
        "subscription": {
            "dnn": "internet",
            "sNssai": {"sst": 1, "sd": 0},
            "pduSessionTypes": {"allowedSessionTypes": ["IPV4"]},
            "sscModes": {"allowedSscModes": [1]},
        },
    }


class CreatedSessionScriptInputTests(unittest.TestCase):
    def test_allowed_lists_do_not_require_default_values(self):
        selected = select_configuration(selection_input())
        self.assertEqual(selected["pduSessionType"], "IPV4")
        self.assertEqual(selected["sscMode"], 1)

    def test_subscription_defaults_are_used_when_allowed_lists_are_absent(self):
        value = selection_input()
        value["subscription"]["pduSessionTypes"] = {"defaultSessionType": "IPV4"}
        value["subscription"]["sscModes"] = {"defaultSscMode": 1}
        self.assertEqual(select_configuration(value)["pduSessionType"], "IPV4")

    def test_string_session_type_set_is_rejected(self):
        value = selection_input()
        value["subscription"]["pduSessionTypes"]["allowedSessionTypes"] = "IPV4"
        with self.assertRaisesRegex(ValueError, "session type set"):
            select_configuration(value)

    def test_boolean_ssc_mode_is_not_treated_as_integer_one(self):
        value = selection_input()
        value["subscription"]["sscModes"]["allowedSscModes"] = [True]
        with self.assertRaisesRegex(ValueError, "SSC mode set"):
            select_configuration(value)

    def test_matched_udm_result_with_null_subscription_is_unknown(self):
        result = evaluate_udm_read({
            "observations": {"response": {
                "networkOutcome": "HTTP_RESPONSE",
                "responseOrigin": "TARGET_SERVICE_VIA_SCP",
                "captureComplete": True,
                "httpStatus": 200,
                "selection": "MATCHED",
                "subscription": None,
            }}
        })
        self.assertEqual(result["result"], "UNKNOWN")

    def test_null_transfer_http_status_is_unknown_without_exception(self):
        result = evaluate_transfer_start({
            "observations": {"response": {
                "networkOutcome": "HTTP_RESPONSE",
                "responseOrigin": "TARGET_SERVICE_VIA_SCP",
                "captureComplete": True,
                "httpStatus": None,
            }}
        })
        self.assertEqual(result["result"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
