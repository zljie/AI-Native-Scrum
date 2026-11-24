"""Role skill registration and packet binding tests; no live Agent or business acceptance."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from agent_collaboration import Engine, make_plan
from test_collaboration import ROOT, setup

FRONTEND = '.ai/skills/frontend-engineering/SKILL.md'
DBA = '.ai/skills/dba-engineering/SKILL.md'
LIST = '.agents/skills/frontend-list-contract/SKILL.md'

class EngineeringPracticeTests(unittest.TestCase):
    def test_both_registries_bind_same_role_skills_without_new_role(self):
        for path in ('collaboration/registry.json', 'collaboration/sprint/registry.json'):
            roles = json.loads((ROOT/path).read_text())['roles']
            self.assertIn(FRONTEND, roles['developer_agent']['skill_refs'])
            self.assertIn(LIST, roles['developer_agent']['skill_refs'])
            self.assertIn(DBA, roles['database_agent']['skill_refs'])
            self.assertNotIn(DBA, roles['developer_agent']['skill_refs'])
            self.assertNotIn('dba_agent', roles)

    def test_plan_binds_actual_skill_hash_and_developer_packet(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            setup(root, ['copy_only'])
            for path, name in ((FRONTEND,'frontend-engineering'), (DBA,'dba-engineering')):
                (root/path).write_bytes((ROOT/'collaboration/practices'/name/'SKILL.md').read_bytes())
            engine = Engine(root, 'RUN-001')
            engine.create('intake/context.json')
            state = engine.load()
            self.assertEqual(state['anchors'][FRONTEND], hashlib.sha256((root/FRONTEND).read_bytes()).hexdigest())
            packet = engine.packet(state,'implementation')
            docs = {doc['ref']: doc for doc in packet['documents']}
            self.assertIn(FRONTEND, docs)
            self.assertIn(LIST, docs)
            self.assertNotIn(DBA, docs)
            self.assertNotIn('database', state['assignments'])

    def test_schema_impact_selects_existing_dba_and_binds_practice(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            setup(root, ['database_schema'])
            (root/DBA).write_bytes((ROOT/'collaboration/practices/dba-engineering/SKILL.md').read_bytes())
            state = make_plan(root,'intake/context.json','schema/collaboration/registry.json','schema/collaboration/policy.json')
            self.assertEqual(state['assignments']['database_design']['role'], 'database_agent')
            self.assertIn(DBA, state['assignments']['database_design']['skill_refs'])
            self.assertEqual(state['anchors'][DBA], hashlib.sha256((root/DBA).read_bytes()).hexdigest())

if __name__ == '__main__':
    unittest.main()
