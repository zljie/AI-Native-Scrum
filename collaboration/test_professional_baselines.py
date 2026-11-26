"""Professional baseline binding through the actual Engine and source Skills.

Task contexts and authorizations are isolated fixtures. Packet inspection and
failure-before-dispatch checks do not claim model skill use, native subagents,
business acceptance or a logged-in Codexhost run.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'collaboration'), str(ROOT / 'observability')]

from agent_collaboration import Engine, Fault
from test_sprint_flow import POLICY, REGISTRY, project


COMMON = '.ai/skills/professional-baseline/SKILL.md'
ROLE_METHODS = {
    'product_agent': 'product-engineering',
    'architect_agent': 'architecture-engineering',
    'developer_agent': 'software-engineering',
    'test_agent': 'quality-engineering',
    'ops_agent': 'operations-engineering',
    'database_agent': 'dba-engineering',
    'director_agent': 'scenario-directing',
    'uiux_agent': 'ux-engineering',
}
ROLE_REFS = {role: '.ai/skills/' + name + '/SKILL.md'
             for role, name in ROLE_METHODS.items()}
FRONTEND_REFS = {'.ai/skills/frontend-engineering/SKILL.md',
                 '.agents/skills/frontend-list-contract/SKILL.md'}
DEFAULT_REGISTRY = 'schema/collaboration/registry.json'
DEFAULT_POLICY = 'schema/collaboration/policy.json'


def source_text(skill_ref):
    return (ROOT / 'collaboration/practices' /
            Path(skill_ref).relative_to('.ai/skills')).read_text()


class ProfessionalBaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def create(self, signals=None, registry=REGISTRY, policy=POLICY):
        context, _ = project(self.root, signals or ['ui_flow', 'database_schema', 'runtime_change'])
        engine = Engine(self.root, context['run_id'])
        state = engine.create('intake/context.json', registry, policy)
        return engine, state

    def test_all_eight_roles_bind_actual_common_and_own_method_in_review_packets(self):
        engine, state = self.create()
        before = engine.history()
        seen = set()
        for name, assignment in state['assignments'].items():
            with self.subTest(step=name, role=assignment['role']):
                role = assignment['role']
                seen.add(role)
                # Upstream work has not executed. A partial handoff-review
                # packet is inspectable, but cannot be an execution receipt.
                packet = engine.packet(state, name, review={'artifacts': {}})
                self.assertEqual(packet['phase'], 'handoff_review')
                self.assertEqual(packet['sample_kind'], 'fixture')
                self.assertEqual(packet['attempt'], 0)
                self.assertEqual(packet['write_paths'], [])
                docs = {entry['ref']: entry for entry in packet['documents']}
                self.assertEqual(set(docs) & set(ROLE_REFS.values()), {ROLE_REFS[role]})
                self.assertEqual(set(docs) & FRONTEND_REFS,
                                 FRONTEND_REFS if role == 'developer_agent' else set())
                for ref in (COMMON, ROLE_REFS[role]):
                    self.assertEqual(docs[ref]['text'], source_text(ref))
                    expected = hashlib.sha256((self.root / ref).read_bytes()).hexdigest()
                    self.assertEqual(docs[ref]['sha256'], expected)
                    self.assertEqual(state['anchors'][ref], expected)
                if assignment['depends_on']:
                    self.assertFalse(packet['dependency_manifest']['complete'])
                    with self.assertRaisesRegex(Fault, 'DEPENDENCY_INCOMPLETE'):
                        engine.packet(state, name)
        self.assertEqual(seen, set(ROLE_METHODS))
        self.assertEqual(engine.history(), before)
        self.assertFalse(any(row['event']['event_type'] == 'AGENT_STARTED' for row in before))

    def test_default_six_roles_have_the_same_baselines_without_sprint_activation(self):
        engine, state = self.create(registry=DEFAULT_REGISTRY, policy=DEFAULT_POLICY)
        expected_roles = set(ROLE_METHODS) - {'director_agent', 'uiux_agent'}
        self.assertEqual({entry['role'] for entry in state['assignments'].values()}, expected_roles)
        for name, assignment in state['assignments'].items():
            with self.subTest(step=name):
                packet = engine.packet(state, name, review={'artifacts': {}})
                refs = {entry['ref'] for entry in packet['documents']}
                self.assertIn(COMMON, refs)
                self.assertEqual(refs & set(ROLE_REFS.values()), {ROLE_REFS[assignment['role']]})
                self.assertEqual(refs & FRONTEND_REFS,
                                 FRONTEND_REFS if assignment['role'] == 'developer_agent' else set())
        self.assertNotIn('director_pre', state['assignments'])
        self.assertNotIn('uiux_design', state['assignments'])

    def test_copy_only_stays_one_developer_with_existing_frontend_supplements(self):
        for registry, policy in ((DEFAULT_REGISTRY, DEFAULT_POLICY), (REGISTRY, POLICY)):
            with self.subTest(registry=registry), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                context, _ = project(root, ['copy_only'])
                engine = Engine(root, context['run_id'])
                state = engine.create('intake/context.json', registry, policy)
                self.assertEqual(state['mode'], 'single_agent')
                self.assertEqual(list(state['assignments']), ['implementation'])
                packet = engine.packet(state, 'implementation')
                self.assertEqual(packet['role'], 'developer_agent')
                refs = {entry['ref'] for entry in packet['documents']}
                self.assertIn(COMMON, refs)
                self.assertIn(ROLE_REFS['developer_agent'], refs)
                self.assertIn('.ai/skills/frontend-engineering/SKILL.md', refs)
                self.assertIn('.agents/skills/frontend-list-contract/SKILL.md', refs)
                self.assertEqual(refs & set(ROLE_REFS.values()), {ROLE_REFS['developer_agent']})
                self.assertTrue(packet['dependency_manifest']['complete'])
                self.assertFalse(any(row['event']['event_type'] == 'AGENT_STARTED'
                                     for row in engine.history()))

    def test_missing_common_or_professional_source_rejects_plan_without_journal(self):
        for missing in (COMMON, ROLE_REFS['developer_agent'], ROLE_REFS['director_agent']):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                context, _ = project(root)
                (root / missing).unlink()
                engine = Engine(root, context['run_id'])
                with self.assertRaisesRegex(Fault, 'MISSING_REF'):
                    engine.create('intake/context.json', REGISTRY, POLICY)
                self.assertEqual(engine.history(), [])
                self.assertFalse(engine.folder.exists())

    def test_baseline_change_is_blocked_before_adapter_or_journal_mutation(self):
        for changed in (COMMON, ROLE_REFS['developer_agent']):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                context, _ = project(root, ['copy_only'])
                engine = Engine(root, context['run_id'])
                engine.create('intake/context.json', REGISTRY, POLICY)
                before = engine.history()
                path = root / changed
                path.write_text(path.read_text() + '\nChanged source during a fixture run.\n')
                adapter = mock.Mock(sample_kind='fixture')
                with self.assertRaisesRegex(Fault, 'CONTEXT_DRIFT'):
                    engine.dispatch('implementation', adapter)
                adapter.run.assert_not_called()
                adapter.review.assert_not_called()
                self.assertEqual(engine.history(), before)

    def test_two_projects_bind_their_own_standards_and_reject_replacement(self):
        engines = []
        packets = []
        for project_name, standard in (
                ('alpha', 'Project Alpha fixture: REST v2; Vue; reviewed API contract.\n'),
                ('beta', 'Project Beta fixture: GraphQL; React; reviewed API contract.\n')):
            root = self.root / project_name
            context, _ = project(root, ['copy_only'])
            norm = root / 'docs/project-standards.md'
            norm.parent.mkdir(parents=True, exist_ok=True)
            norm.write_text(standard)
            context['inputs'].append('docs/project-standards.md')
            (root / 'intake/context.json').write_text(json.dumps(context))
            engine = Engine(root, context['run_id'])
            state = engine.create('intake/context.json', REGISTRY, POLICY)
            packet = engine.packet(state, 'implementation')
            docs = {entry['ref']: entry for entry in packet['documents']}
            self.assertEqual(docs['docs/project-standards.md']['text'], standard)
            self.assertEqual(docs[COMMON]['text'], source_text(COMMON))
            engines.append(engine)
            packets.append(docs)
        self.assertNotEqual(packets[0]['docs/project-standards.md']['sha256'],
                            packets[1]['docs/project-standards.md']['sha256'])
        alpha, beta = engines
        (alpha.root / 'docs/project-standards.md').write_bytes(
            (beta.root / 'docs/project-standards.md').read_bytes())
        adapter = mock.Mock(sample_kind='fixture')
        with self.assertRaisesRegex(Fault, 'SOURCE_DRIFT'):
            alpha.dispatch('implementation', adapter)
        adapter.run.assert_not_called()
        self.assertEqual(beta.ready(), ['implementation'])


if __name__ == '__main__':
    unittest.main()
