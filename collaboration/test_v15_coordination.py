"""V1.5 integration: project facts -> capability activation -> journal -> trace.

Fixture receipts DO NOT imply authenticated host subagents or business acceptance.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/"collaboration"), str(ROOT/"observability")]
from test_collaboration import setup, FixtureAdapter
from project_context import snapshot, write_once as save_pack
from agent_collaboration import Engine, Fault, drive
from v15_activation import activation
from v15_controller import start_plan, capabilities, release_assessment
from v15_graph import graph, metrics, record_drift


class V15CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base, self.auth = setup(self.root, ["database_schema"])
        for name, content in {
            "db/schema.sql": "create table equipment(id integer primary key);",
            "interfaces/openapi.json": '{"paths":{}}',
            "docs/architecture.md": "equipment module existing",
            "docs/requirements.md": "add optional maintenance grade",
        }.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
        pack_req = {
            "schema": "project-context-request/v1",
            "goal_ref": self.base["goal_ref"], "task_ref": self.base["task_ref"],
            "sources": {
                "architecture": ["docs/architecture.md"],
                "database": ["db/schema.sql"],
                "interfaces": ["interfaces/openapi.json"],
                "implementation": ["src/app.py"],
                "tests": ["tests/test_sample.py"],
                "requirements": ["docs/requirements.md"],
            }
        }
        (self.root/"intake/pack-request.json").write_text(json.dumps(pack_req))
        save_pack(self.root, "intake/project-pack.json", snapshot(self.root, "intake/pack-request.json"))
        self.request = {
            "schema": "activation-request/v1", "run_id": "RUN-001",
            "goal_ref": self.base["goal_ref"], "story_ref": self.base["story_ref"],
            "task_ref": self.base["task_ref"],
            "authorization_ref": self.base["authorization_ref"],
            "sample_kind": "fixture",
            "context_pack_ref": "intake/project-pack.json",
            "signals": ["database_schema"],
            "signal_evidence": {"database_schema": ["db/schema.sql"]},
            "scopes": self.base["scopes"],
        }
        self.save()

    def save(self):
        (self.root/"intake/v15-request.json").write_text(json.dumps(self.request))

    def plan(self):
        self.save()
        return start_plan(self.root, "intake/v15-request.json", "intake/v15-context.json")

    def engine(self):
        return Engine(self.root, "RUN-001")

    def test_database_expert_is_selected_from_grounded_signal(self):
        data = self.plan()
        self.assertEqual(data["execution"], "not_started")
        self.assertTrue(data["project_context_bound_in_inputs"])
        plan = self.engine().load()
        self.assertIn("database_agent", {d["role"] for d in plan["assignments"].values()})
        self.assertEqual(self.engine().history()[0]["event"]["event_type"], "TASK_CLASSIFIED")
        self.assertEqual(metrics(self.engine())["verified_runtime_session_starts"], 0)

    def test_database_source_alone_never_triggers_database_expert(self):
        self.request["signals"] = ["api_contract"]
        self.request["signal_evidence"] = {"api_contract": ["interfaces/openapi.json"]}
        self.save()
        context, preview = activation(self.root, "intake/v15-request.json")
        self.assertFalse(preview["database_change_signalled"])
        self.assertNotIn("database_agent", {a["role"] for a in preview["assignments"]})
        self.assertEqual(context["sample_kind"], "fixture")

    def test_signal_cannot_be_backed_by_unrelated_file(self):
        self.request["signal_evidence"] = {"database_schema": ["interfaces/openapi.json"]}
        self.save()
        with self.assertRaisesRegex(Fault, "SIGNAL_NOT_GROUNDED"):
            activation(self.root, "intake/v15-request.json")


    def write_impact_review(self, decision="required", reviewer="product_agent",
                            rationale="The requirement changes the equipment schema and existing data contract.",
                            refs=None):
        (self.root / "intake/impact-confirmation.md").write_text(
            "Independent review noted by the project operator; this file does not authenticate identity.\n"
        )
        doc = {
            "schema": "activation-impact-review/v1",
            "run_id": self.request["run_id"],
            "context_pack_ref": self.request["context_pack_ref"],
            "proposer": "architect_agent",
            "reviewer": reviewer,
            "confirmation_ref": "intake/impact-confirmation.md",
            "decisions": {
                "database_schema": {
                    "decision": decision,
                    "rationale": rationale,
                    "evidence_refs": ["db/schema.sql"] if refs is None else refs,
                },
            },
        }
        (self.root / "intake/impact-review.json").write_text(json.dumps(doc))
        self.request["impact_review_ref"] = "intake/impact-review.json"
        return doc

    def test_real_activation_requires_independent_impact_review_record(self):
        self.request["sample_kind"] = "real"
        self.save()
        with self.assertRaisesRegex(Fault, "IMPACT_REVIEW_REQUIRED"):
            activation(self.root, "intake/v15-request.json")
        self.write_impact_review()
        self.save()
        context, preview = activation(self.root, "intake/v15-request.json")
        self.assertIn("intake/impact-review.json", context["inputs"])
        self.assertIn("intake/impact-confirmation.md", context["inputs"])
        self.assertEqual(preview["impact_review"], "recorded_identity_unverified")
        self.assertEqual(preview["execution"], "not_started")

    def test_impact_review_rejects_self_review_or_unsupported_signal(self):
        self.request["sample_kind"] = "real"
        self.write_impact_review(reviewer="architect_agent")
        self.save()
        with self.assertRaisesRegex(Fault, "IMPACT_REVIEW_SELF_REVIEW"):
            activation(self.root, "intake/v15-request.json")
        self.write_impact_review(refs=["interfaces/openapi.json"])
        self.save()
        with self.assertRaisesRegex(Fault, "IMPACT_REVIEW_EVIDENCE"):
            activation(self.root, "intake/v15-request.json")

    def test_impact_review_rejects_unconfirmed_or_empty_rationale(self):
        self.request["sample_kind"] = "real"
        self.write_impact_review(decision="uncertain")
        self.save()
        with self.assertRaisesRegex(Fault, "IMPACT_REVIEW_NOT_CONFIRMED"):
            activation(self.root, "intake/v15-request.json")
        self.write_impact_review(rationale="yes")
        self.save()
        with self.assertRaisesRegex(Fault, "IMPACT_REVIEW_RATIONALE"):
            activation(self.root, "intake/v15-request.json")

    def test_pack_drift_blocks_activation(self):
        (self.root/"db/schema.sql").write_text("alter table equipment add column grade text;")
        self.save()
        with self.assertRaisesRegex(Fault, "PACK_STALE"):
            activation(self.root, "intake/v15-request.json")

    def test_task_ref_mismatch_blocks_activation(self):
        self.request["task_ref"] = "intake/consent.md"
        self.save()
        with self.assertRaisesRegex(Fault, "PACK_TASK_MISMATCH"):
            activation(self.root, "intake/v15-request.json")

    def test_plan_is_not_a_runtime_receipt(self):
        self.plan()
        s = metrics(self.engine())
        self.assertEqual(s["planned_steps"], len(self.engine().load()["assignments"]))
        self.assertEqual(s["fixture_starts"], 0)
        self.assertIsNone(s["native_subagent_starts"])
        self.assertIsNone(s["end_to_end_token_total"])
        self.assertEqual(s["real_agent_acceptance"], "NOT_RUN")

    def test_fixture_drive_produces_trace_without_false_native_claim(self):
        self.plan()
        engine = self.engine()
        result = drive(engine, FixtureAdapter())
        self.assertTrue(result["findings"] or not result["checks_passed"])  # independent validation still required
        summary = metrics(engine)
        self.assertGreater(summary["fixture_starts"], 0)
        self.assertEqual(summary["verified_runtime_session_starts"], 0)
        self.assertEqual(summary["accepted_handoffs"], summary["submitted_handoffs"])
        self.assertIsNone(summary["native_subagent_starts"])
        self.assertEqual(summary["real_agent_acceptance"], "NOT_RUN")
        self.assertFalse(engine.check(release=True)["checks_passed"])
        self.assertIn("V15_NATIVE_SUBAGENT_BACKEND_NOT_IMPLEMENTED",
                      release_assessment(engine)["findings"])

    def test_input_change_invalidates_whole_plan_and_resume_needs_replan(self):
        self.plan()
        engine = self.engine()
        (self.root/"db/schema.sql").write_text("alter table equipment add grade text;")
        g = graph(engine)
        self.assertTrue(g["new_plan_required"])
        self.assertIn("db/schema.sql", g["changed_sources"])
        self.assertEqual(len(g["affected_steps"]), len(engine.load()["assignments"]))
        record_drift(engine)
        self.assertEqual(engine.load()["mode"], "blocked")
        self.assertEqual(engine.load()["reason"], "PROJECT_INPUT_DRIFT_REPLAN_REQUIRED")
        n = len(engine.history())
        record_drift(engine)
        self.assertEqual(len(engine.history()), n)
        self.assertEqual(engine.ready(), [])


    def prepare_replan(self):
        self.plan()
        previous = self.engine()
        (self.root / "db/schema.sql").write_text(
            "alter table equipment add column maintenance_grade text;")
        record_drift(previous)
        self.assertEqual(previous.load()["mode"], "blocked")
        self.request["run_id"] = "RUN-002"
        self.request["context_pack_ref"] = "intake/project-pack-v2.json"
        save_pack(self.root, "intake/project-pack-v2.json",
                  snapshot(self.root, "intake/pack-request.json"))
        return previous

    def add_replan_authorization(self):
        old = json.loads((self.root / self.base["authorization_ref"]).read_text())
        (self.root / "intake/replan-confirmation.md").write_text(
            "Human confirmation for a new run after source drift (fixture only).")
        old["confirmation_ref"] = "intake/replan-confirmation.md"
        (self.root / "intake/replan-authorization.json").write_text(json.dumps(old))
        self.request["authorization_ref"] = "intake/replan-authorization.json"

    def test_drift_replan_requires_new_authorization_and_links_history(self):
        previous = self.prepare_replan()
        previous_rows = len(previous.history())
        self.save()
        with self.assertRaisesRegex(Fault, "REPLAN_NEW_AUTHORIZATION_REQUIRED"):
            start_plan(self.root, "intake/v15-request.json",
                       "intake/v15-context-v2.json", previous_run_id="RUN-001")
        self.add_replan_authorization()
        self.save()
        result = start_plan(self.root, "intake/v15-request.json",
                            "intake/v15-context-v2.json", previous_run_id="RUN-001")
        self.assertEqual(result["supersedes_run"], "RUN-001")
        new_engine = Engine(self.root, "RUN-002")
        self.assertEqual(graph(new_engine)["supersedes_run"], "RUN-001")
        self.assertEqual(metrics(new_engine)["supersedes_run"], "RUN-001")
        self.assertEqual(new_engine.history()[-1]["event"]["event_type"], "RUN_REPLANNED_FROM")
        self.assertEqual(len(previous.history()), previous_rows)
        self.assertTrue(new_engine.ready())

    def test_replan_rejects_changed_task_identity(self):
        self.prepare_replan()
        self.add_replan_authorization()
        self.request["task_ref"] = "intake/another-task.md"
        (self.root / "intake/another-task.md").write_text("New unrelated task.")
        self.save()
        with self.assertRaisesRegex(Fault, "PACK_TASK_MISMATCH"):
            start_plan(self.root, "intake/v15-request.json",
                       "intake/v15-context-v2.json", previous_run_id="RUN-001")

    def test_dependency_without_accepted_handoff_is_not_ready(self):
        self.plan()
        g = graph(self.engine())
        d = {n["step"]: n for n in g["nodes"]}
        self.assertTrue(d["architecture_pre"]["ready"])  # product step is skipped for database-only impact
        self.assertTrue(d["database_design"]["blockers"])
        self.assertFalse(d["database_design"]["ready"])

    def test_recovery_marks_orphaned_task_without_reexecution(self):
        self.plan()
        engine = self.engine()
        with engine.lock():
            s = engine.load()
            node = s["assignments"]["architecture_pre"]
            node["status"] = "requested"
            node["attempt"] = 1
            node["attempts"].append({"status": "requested", "instance_ref": None})
            engine.append(s, "AGENT_INVOCATION_REQUESTED", "architecture_pre", after="requested")
        self.assertEqual(engine.recover(), ["architecture_pre"])
        self.assertEqual(engine.load()["assignments"]["architecture_pre"]["status"], "blocked")
        self.assertEqual(metrics(engine)["verified_runtime_session_starts"], 0)
        # No replay without confirming unknown side effects from the interrupted
        # request. This remains blocked even if no runtime start receipt exists.
        with self.assertRaisesRegex(Fault, "INTERRUPTED_RECONCILIATION_REQUIRED"):
            engine.retry("architecture_pre")
        self.assertEqual(len(engine.history()[-1]["state"]["assignments"]["architecture_pre"]["attempts"]), 1)


    def interrupted_engine(self):
        self.plan()
        engine = self.engine()
        with engine.lock():
            s = engine.load()
            node = s["assignments"]["architecture_pre"]
            node["status"] = "requested"
            node["attempt"] = 1
            node["attempts"].append({"status": "requested", "instance_ref": None})
            engine.append(s, "AGENT_INVOCATION_REQUESTED",
                          "architecture_pre", after="requested")
        self.assertEqual(engine.recover(), ["architecture_pre"])
        return engine

    def reconciliation_record(self, engine, effects="none_observed", disposition="retry"):
        (self.root / "intake/reconcile-confirmation.md").write_text(
            "Explicit second confirmation to retry only after checking side effects.\n"
        )
        event = [row["event"] for row in engine.history()
                 if row["event"]["event_type"] == "AGENT_BLOCKED"
                 and row["event"]["delegation_id"] == "architecture_pre"][-1]
        record = {
            "schema": "collaboration-reconciliation/v1",
            "run_id": "RUN-001",
            "step": "architecture_pre",
            "attempt": 1,
            "blocked_event_id": event["event_id"],
            "proposer": "architect_agent",
            "reviewer": "test_agent",
            "observed_effects": effects,
            "disposition": disposition,
            "reason": "Checked current test artifacts and verified the interrupted task produced no effects.",
            "confirmation_ref": "intake/reconcile-confirmation.md",
            "evidence_refs": ["db/schema.sql"],
        }
        (self.root / "intake/reconcile.json").write_text(json.dumps(record))
        return record

    def test_reconciliation_requires_independent_record_and_explicit_retry(self):
        engine = self.interrupted_engine()
        record = self.reconciliation_record(engine)
        before = len(engine.history())
        self.assertFalse(graph(engine)["nodes"][0]["ready"])
        result = engine.reconcile("architecture_pre", "intake/reconcile.json")
        self.assertTrue(result["retry_eligible"])
        self.assertEqual(result["identity_authentication"], "not_verified_by_local_contract")
        self.assertEqual(engine.load()["assignments"]["architecture_pre"]["status"], "blocked")
        self.assertEqual(len(engine.history()), before + 1)
        self.assertEqual(metrics(engine)["reconciliation_records"], 1)
        self.assertEqual(engine.reconcile.__name__, "reconcile")
        self.assertIn("architecture_pre", engine.retry("architecture_pre"))
        self.assertEqual(engine.load()["assignments"]["architecture_pre"]["status"], "proposed")
        self.assertEqual(len(engine.load()["assignments"]["architecture_pre"]["attempts"]), 1)

    def test_reconciliation_rejects_mismatch_and_unsafe_effects(self):
        engine = self.interrupted_engine()
        record = self.reconciliation_record(engine)
        record["reviewer"] = "architect_agent"
        (self.root / "intake/reconcile.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(Fault, "RECONCILIATION_SELF_REVIEW"):
            engine.reconcile("architecture_pre", "intake/reconcile.json")
        record["reviewer"] = "test_agent"
        record["blocked_event_id"] = "EVT-000001"
        (self.root / "intake/reconcile.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(Fault, "RECONCILIATION_EVENT_MISMATCH"):
            engine.reconcile("architecture_pre", "intake/reconcile.json")
        record["blocked_event_id"] = [row["event"]["event_id"]
                                      for row in engine.history()
                                      if row["event"]["event_type"] == "AGENT_BLOCKED"][-1]
        record["observed_effects"] = "unknown"
        (self.root / "intake/reconcile.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(Fault, "RECONCILIATION_UNSAFE_RETRY"):
            engine.reconcile("architecture_pre", "intake/reconcile.json")
        record["disposition"] = "new_run_or_manual_resolution"
        (self.root / "intake/reconcile.json").write_text(json.dumps(record))
        self.assertFalse(engine.reconcile("architecture_pre", "intake/reconcile.json")["retry_eligible"])
        with self.assertRaisesRegex(Fault, "INTERRUPTED_RECONCILIATION_REQUIRED"):
            engine.retry("architecture_pre")

    def test_reconciliation_ref_cannot_drift_before_retry(self):
        engine = self.interrupted_engine()
        self.reconciliation_record(engine)
        engine.reconcile("architecture_pre", "intake/reconcile.json")
        (self.root / "intake/reconcile-confirmation.md").write_text("confirmation changed")
        with self.assertRaisesRegex(Fault, "RECONCILIATION_STALE_OR_UNSAFE"):
            engine.retry("architecture_pre")

    def test_full_database_fixture_flow_with_post_architecture_review(self):
        self.plan()
        engine = self.engine()
        drive(engine, FixtureAdapter())
        state = engine.load()
        self.assertEqual(state["assignments"]["architecture_post"]["status"], "completed")
        self.assertEqual(state["assignments"]["database"]["role"], "database_agent")
        check = engine.validate(self.auth["validation_commands"][0])
        self.assertEqual(check["exit_code"], 0)
        self.assertTrue(engine.finish()["checks_passed"])
        summary = metrics(engine)
        self.assertEqual(summary["completed_steps"], summary["planned_steps"])
        self.assertEqual(summary["real_agent_acceptance"], "NOT_RUN")
        self.assertIsNone(summary["end_to_end_token_total"])
        self.assertFalse(engine.check(release=True)["checks_passed"])

    def test_graph_respects_active_resource_limit(self):
        self.plan()
        engine = self.engine()
        with engine.lock():
            state = engine.load()
            state["authorization"]["max_parallel"] = 1
            # Synthetic scheduler boundary: make analysis independently ready,
            # then prove the active slot still blocks dispatch.
            state["assignments"]["analysis"]["depends_on"] = []
            node = state["assignments"]["architecture_pre"]
            node["status"] = "running"
            node["attempt"] = 1
            node["attempts"].append({"status": "running", "instance_ref": "FIX-reserved"})
            engine.append(state, "AGENT_STARTED", "architecture_pre", after="running",
                          source="fixture_transport", verification="unverified")
        g = graph(engine)
        remaining = [x for x in g["nodes"] if x["status"] in ("proposed", "queued")]
        self.assertTrue(remaining)
        self.assertTrue(all(not x["ready"] for x in remaining))
        analysis = next(x for x in remaining if x["step"] == "analysis")
        self.assertIn("RESOURCE_OR_WRITE_CONFLICT", analysis["blockers"])

    def test_controller_advertises_runtime_session_not_spawn_agent(self):
        status = capabilities()
        self.assertEqual(status["execution_mode"], "runtime_session")
        self.assertFalse(status["native_spawn_agent_supported"])
        self.assertFalse(status["authorization_granted"])
        self.plan()
        released = release_assessment(self.engine())
        self.assertFalse(released["checks_passed"])
        self.assertIn("V15_NATIVE_SUBAGENT_EVIDENCE_UNAVAILABLE", released["findings"])
        self.assertEqual(released["authenticated_host_acceptance"], "NOT_RUN")
        self.assertEqual(released["native_spawn_agent_acceptance"], "NOT_RUN")
        self.assertEqual(released["business_project_acceptance"], "NOT_RUN")
        self.assertEqual(metrics(self.engine())["native_spawn_agent_acceptance"], "NOT_RUN")

    def test_review_usage_known_and_missing_are_separate(self):
        self.plan()
        engine = self.engine()
        engine.dispatch("architecture_pre", FixtureAdapter())
        handoff = engine.submit("architecture_pre", "analysis")

        class MeteredReview(FixtureAdapter):
            def review(self, packet, started):
                answer = super().review(packet, started)
                return {**answer, "usage": {"input_tokens": 13, "output_tokens": 7}}

        engine.review(handoff["handoff_id"], MeteredReview())
        totals = metrics(engine)
        self.assertEqual(totals["review_attempt_count"], 1)
        self.assertEqual(totals["review_usage_known_count"], 1)
        self.assertEqual(totals["review_usage_unknown_count"], 0)
        self.assertEqual(totals["review_token_known_subtotal"], 20)
        self.assertEqual(totals["review_token_coverage"], "complete")
        self.assertEqual(totals["known_runtime_token_subtotal"], 20)
        self.assertIsNone(totals["end_to_end_token_total"])

    def test_review_usage_rejects_boolean_and_does_not_claim_coverage(self):
        self.plan()
        engine = self.engine()
        engine.dispatch("architecture_pre", FixtureAdapter())
        handoff = engine.submit("architecture_pre", "analysis")

        class InvalidReview(FixtureAdapter):
            def review(self, packet, started):
                answer = super().review(packet, started)
                return {**answer, "usage": {"input_tokens": True, "output_tokens": 7}}

        with self.assertRaisesRegex(Fault, "REVIEW_USAGE_INVALID"):
            engine.review(handoff["handoff_id"], InvalidReview())
        totals = metrics(engine)
        self.assertEqual(totals["review_attempt_count"], 1)
        self.assertEqual(totals["review_usage_known_count"], 0)
        self.assertEqual(totals["review_usage_unknown_count"], 1)
        self.assertEqual(totals["review_token_coverage"], "unknown")
        self.assertIsNone(totals["end_to_end_token_total"])


    def test_fixture_native_like_labels_never_count_as_live_native(self):
        self.plan()
        engine = self.engine()
        with engine.lock():
            state = engine.load()
            node = state["assignments"]["architecture_pre"]
            node["status"] = "running"
            node["attempt"] = 1
            node["attempts"].append({
                "status": "completed", "execution_mode": "native_subagent",
                "instance_ref": "RT-fake", "start_evidence": {
                    "source": "fixture_transport", "sample_kind": "fixture"}})
            engine.append(state, "AGENT_STARTED", "architecture_pre",
                          source="fixture_transport", verification="unverified")
        report = metrics(engine)
        self.assertIsNone(report["native_subagent_starts"])
        self.assertEqual(report["native_spawn_agent_acceptance"], "NOT_RUN")

    def test_source_version_drift_from_unrelated_category_still_blocks(self):
        self.plan()
        engine = self.engine()
        (self.root/"docs/architecture.md").write_text("updated architecture")
        g = graph(engine)
        self.assertTrue(g["new_plan_required"])
        self.assertIn("docs/architecture.md", g["changed_sources"])


if __name__ == "__main__":
    unittest.main()
