"""P0 behavioral and regression checks for the exemplar Goal."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from examples.report_subscription.service import ReportService


SAMPLE = Path(__file__).resolve().parents[1]


class ReportServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="report-subscription-")
        self.db = Path(self.temp.name) / "demo.sqlite"
        self.service = ReportService(self.db)

    def tearDown(self):
        self.service.close()
        self.temp.cleanup()

    def test_feature_subscription_persists_and_is_visible(self):
        first = self.service.subscribe("operator-1", "monthly-operations")
        self.assertTrue(first["created"])
        self.assertEqual(self.service.subscriptions("operator-1"), ["monthly-operations"])
        self.service.close()
        self.service = ReportService(self.db)
        self.assertEqual(self.service.subscriptions("operator-1"), ["monthly-operations"])

    def test_bugfix_duplicate_or_mixed_case_does_not_create_another_subscription(self):
        original = self.service.subscribe("operator-1", "monthly-operations")
        repeat = self.service.subscribe(" operator-1 ", " MONTHLY-OPERATIONS ")
        self.assertFalse(repeat["created"])
        self.assertEqual(repeat["id"], original["id"])
        self.assertEqual(len(self.service.subscriptions("operator-1")), 1)

    def test_feature_report_request_is_submitted_not_approved(self):
        requested = self.service.request_report("operator-1", "Add a compressor health report")
        self.assertEqual(requested["id"], "REQ-0001")
        self.assertEqual(requested["status"], "submitted")
        row = self.service.connection.execute("SELECT status FROM report_requests").fetchone()
        self.assertEqual(row[0], "submitted")

    def test_invalid_user_and_unpublished_report_are_rejected(self):
        with self.assertRaises(ValueError):
            self.service.subscribe("../guest", "monthly-operations")
        with self.assertRaises(ValueError):
            self.service.subscribe("operator-1", "secret-report")

    def test_request_requires_meaningful_description(self):
        with self.assertRaises(ValueError):
            self.service.request_report("operator-1", "new")
        with self.assertRaises(ValueError):
            self.service.request_report("operator-1", "x" * 501)

    def test_cli_provides_executable_business_workflow(self):
        command = [sys.executable, "-m", "examples.report_subscription.cli", "--db", str(self.db)]
        subscribed = subprocess.run(command + ["subscribe", "--user", "u01", "--report", "daily-operations"],
                                    check=True, text=True, capture_output=True)
        self.assertTrue(json.loads(subscribed.stdout)["created"])
        listed = subprocess.run(command + ["list", "--user", "u01"],
                                check=True, text=True, capture_output=True)
        self.assertEqual(json.loads(listed.stdout)["reports"], ["daily-operations"])

    def test_p0_scenarios_have_explicit_human_boundaries(self):
        for path in sorted((SAMPLE / "scenarios").glob("*.json")):
            scene = json.loads(path.read_text())
            self.assertTrue(scene["approval_required"])
            self.assertFalse(scene["human_acceptance_recorded"])
            self.assertTrue(scene["role_route"])
            self.assertTrue(set(scene["role_route"]).issubset({
                "product_agent", "architect_agent", "test_agent", "developer_agent", "ops_agent"}))
            self.assertIn(scene["kind"], {"feature", "bugfix", "change_request"})
            if scene["kind"] == "change_request":
                self.assertFalse(scene["change_approved"])
                self.assertTrue(scene["blocked_until_human_change_approval"])
        self.assertEqual(len(list((SAMPLE / "scenarios").glob("*.json"))), 3)


if __name__ == "__main__":
    unittest.main()
