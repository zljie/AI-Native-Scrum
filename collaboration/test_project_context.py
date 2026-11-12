#!/usr/bin/env python3
"""V1.5 project-context regression tests; no live Agent or database required."""
import json
from pathlib import Path
import tempfile
import unittest

from project_context import snapshot, validate, write_once, ContextError, safe_path, CATEGORIES, main


class ContextPackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, content in {
            "goal.md": "goal accepted? test only",
            "task.md": "task fixture",
            "db/schema.sql": "create table equipment(id integer primary key);",
            "src/service.py": "def load(): return 1",
            "tests/test_service.py": "assert True",
            "architecture.md": "existing structure",
        }.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        self.spec = {
            "schema": "project-context-request/v1",
            "goal_ref": "goal.md", "task_ref": "task.md",
            "sources": {k: [] for k in CATEGORIES}
        }
        self.spec["sources"]["database"] = ["db/schema.sql"]
        self.spec["sources"]["architecture"] = ["architecture.md"]
        self.spec["sources"]["implementation"] = ["src/service.py"]
        self.spec["sources"]["tests"] = ["tests/test_service.py"]
        self.save_spec()

    def save_spec(self):
        (self.root / "request.json").write_text(json.dumps(self.spec))

    def test_build_check_and_no_authority(self):
        data = snapshot(self.root, "request.json")
        self.assertEqual(data["agent_dispatch"], "not_performed")
        self.assertEqual(data["authorization"], "not_granted")
        self.assertTrue(validate(self.root, data)["current"])
        self.assertEqual(validate(self.root, data)["checked_files"], 7)
        write_once(self.root, "out/pack.json", data)
        self.assertEqual(main(["--root", str(self.root), "check", "--pack", "out/pack.json"]), 0)

    def test_source_change_invalidates_pack(self):
        data = snapshot(self.root, "request.json")
        (self.root / "db/schema.sql").write_text("alter table equipment add column grade text;")
        result = validate(self.root, data)
        self.assertFalse(result["current"])
        self.assertEqual(result["changed_refs"], ["db/schema.sql"])

    def test_task_and_spec_change_invalidate(self):
        data = snapshot(self.root, "request.json")
        (self.root / "task.md").write_text("updated task")
        self.assertIn("task.md", validate(self.root, data)["changed_refs"])
        (self.root / "task.md").write_text("task fixture")
        self.spec["sources"]["interfaces"].append("src/service.py")
        self.save_spec()
        self.assertIn("request.json", validate(self.root, data)["changed_refs"])

    def test_no_sources_and_duplicate_rejected(self):
        self.spec["sources"] = {k: [] for k in CATEGORIES}
        self.save_spec()
        with self.assertRaises(ContextError):
            snapshot(self.root, "request.json")
        self.spec["sources"]["database"] = ["db/schema.sql", "db/schema.sql"]
        self.save_spec()
        with self.assertRaises(ContextError):
            snapshot(self.root, "request.json")

    def test_secrets_and_traversal_rejected(self):
        for name in ["../outside", "/tmp/outside", ".env", ".git/config", ".ai/config.json", "secrets/token.txt"]:
            with self.subTest(name=name):
                with self.assertRaises(ContextError):
                    safe_path(self.root, name, False)

    def test_symlink_escape_rejected(self):
        external = self.root.parent / (self.root.name + "-external")
        external.write_text("outside")
        self.addCleanup(lambda: external.unlink(missing_ok=True))
        (self.root / "db/escape.sql").symlink_to(external)
        self.spec["sources"]["database"] = ["db/escape.sql"]
        self.save_spec()
        with self.assertRaises(ContextError):
            snapshot(self.root, "request.json")

    def test_no_overwrite(self):
        data = snapshot(self.root, "request.json")
        write_once(self.root, "out/pack.json", data)
        with self.assertRaises(ContextError):
            write_once(self.root, "out/pack.json", data)

    def test_forged_authority_rejected(self):
        data = snapshot(self.root, "request.json")
        data["authorization"] = "approved"
        with self.assertRaises(ContextError):
            validate(self.root, data)

    def test_manifest_omission_and_recategorization_rejected(self):
        data = snapshot(self.root, "request.json")
        data["sources"]["database"] = []
        with self.assertRaisesRegex(ContextError, "PACK_SOURCE_MISMATCH"):
            validate(self.root, data)

        data = snapshot(self.root, "request.json")
        moved = data["sources"]["database"].pop()
        data["sources"]["interfaces"].append(moved)
        with self.assertRaisesRegex(ContextError, "PACK_SOURCE_MISMATCH"):
            validate(self.root, data)

    def test_dependency_omission_and_size_forgery_rejected(self):
        data = snapshot(self.root, "request.json")
        del data["dependencies"]["task.md"]
        with self.assertRaisesRegex(ContextError, "PACK_DEPENDENCIES"):
            validate(self.root, data)

        data = snapshot(self.root, "request.json")
        data["sources"]["database"][0]["size_bytes"] += 1
        with self.assertRaisesRegex(ContextError, "PACK_SIZE_MISMATCH"):
            validate(self.root, data)

    def test_pack_identity_cannot_be_redirected(self):
        data = snapshot(self.root, "request.json")
        data["goal_ref"] = "src/service.py"
        with self.assertRaisesRegex(ContextError, "PACK_DEPENDENCIES"):
            validate(self.root, data)

    def test_malformed_source_ref_rejected_as_context_error(self):
        data = snapshot(self.root, "request.json")
        data["sources"]["database"][0]["ref"] = ["db/schema.sql"]
        with self.assertRaisesRegex(ContextError, "PACK_REF"):
            validate(self.root, data)

    def test_no_classification_from_schema_name(self):
        data = snapshot(self.root, "request.json")
        self.assertEqual(data["classification"], "not_performed")
        self.assertEqual(data["sources"]["database"][0]["ref"], "db/schema.sql")


if __name__ == "__main__":
    unittest.main()
