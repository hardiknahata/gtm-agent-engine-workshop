import os
import pathlib
import sys
import types
import unittest


os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ["LANGSMITH_TRACING"] = "false"
package_path = pathlib.Path(__file__).resolve().parent
package = types.ModuleType("gtm_agent")
package.__path__ = [str(package_path)]
sys.modules["gtm_agent"] = package

from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTests(unittest.TestCase):
    def test_blocks_disqualified_prospect(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-50001",
                "name": "Priya Nair",
                "email": "priya.nair@brightwaveapps.com",
            },
            "Demo invitation",
            "Please book a demo.",
            runtime=None,
            from_rep={"name": "Marco Rossi", "email": "marco.rossi@northpoint.com"},
        )

        self.assertEqual(
            result,
            {
                "status": "blocked",
                "reason": "prospect is disqualified",
                "prospect_id": "LEAD-50001",
            },
        )

    def test_sends_non_disqualified_prospect(self):
        result = send_prospect_email.func(
            {
                "prospect_id": "LEAD-12853",
                "name": "Omar Okafor",
                "email": "omar.okafor@northstarhealth.com",
            },
            "Discovery call",
            "Please share your availability.",
            runtime=None,
            from_rep={"name": "Tara Kim", "email": "tara.kim@northpoint.com"},
        )

        self.assertEqual(result["status"], "sent")
        self.assertTrue(result["message_id"].startswith("msg-"))


if __name__ == "__main__":
    unittest.main()
