"""INIT-S2 deterministic fixtures using the real existing Engine, never live Agents."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'collaboration'))
import agent_collaboration as ac
import project_agents as pa
import project_context as pc
import project_agent_review as review
import project_agent_admission as admission
from test_collaboration import setup, FixtureAdapter


def put(root, ref, value):
    path = root / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value if isinstance(value, str) else json.dumps(value), encoding='utf-8')


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.context, self.auth = setup(self.root)
        put(self.root, 'package.json', {'name': 'synthetic-project'})
        for name in ('api', 'frontend', 'sdd'):
            put(self.root, 'docs/' + name + '.md', 'Synthetic ' + name + ' standard.\n')
        put(self.root, 'docs/standard-confirmation.md', 'Synthetic source confirmation; not actual consent.\n')
        put(self.root, 'docs/review-confirmation.md', 'Synthetic review confirmation; not authenticated.\n')
        put(self.root, 'docs/review-evidence.md', 'Synthetic initialization analysis, not a real Agent output.\n')
        registry = json.loads((self.root / 'schema/collaboration/registry.json').read_text())
        roles = [{'role_id': role, 'variant': 'project', 'required_standards': ['api', 'frontend', 'sdd'],
                  'standards': {name: {'source_ref': 'docs/' + name + '.md',
                                      'confirmation_ref': 'docs/standard-confirmation.md'}
                                for name in ('api', 'frontend', 'sdd')},
                  'fact_refs': ['package.json'], 'conflict_refs': []} for role in registry['roles']]
        put(self.root, 'intake/init.json', {'schema': pa.REQUEST, 'project_id': 'project-a',
                                          'registry_ref': 'schema/collaboration/registry.json', 'roles': roles})
        self.manifest_ref = 'generated/project-agents/profiles.json'
        self.manifest = pa.build(self.root, 'intake/init.json')
        put(self.root, self.manifest_ref, self.manifest)
        source = {category: [] for category in pc.CATEGORIES}
        source['implementation'] = ['src/app.py']
        source['tests'] = ['tests/test_sample.py']
        put(self.root, 'intake/pack-request.json', {'schema': 'project-context-request/v1',
            'goal_ref': self.context['goal_ref'], 'task_ref': self.context['task_ref'], 'sources': source})
        put(self.root, 'intake/pack.json', pc.snapshot(self.root, 'intake/pack-request.json'))
        self.records = {}
        for role in registry['roles']:
            record = review.review_template(self.root, self.manifest_ref, 'project-a', role, 'project', 'fixture')
            record.update(prepared_by='fixture_author', reviewed_by='fixture_reviewer',
                          reviewed_at='2026-11-15T00:00:00+00:00', decision='accepted',
                          confirmation_ref='docs/review-confirmation.md',
                          evidence_hashes={'docs/review-evidence.md': pc.fingerprint(self.root / 'docs/review-evidence.md')})
            self.records[role] = record
            put(self.root, 'intake/review-' + role + '.json', record)
        self.request = {'schema': 'project-agent-admission/v1', 'project_id': 'project-a',
                        'manifest_ref': self.manifest_ref, 'context_ref': 'intake/context.json',
                        'context_pack_ref': 'intake/pack.json', 'policy_ref': 'schema/collaboration/policy.json',
                        'profiles': [{'role_id': role, 'variant': 'project', 'review_ref': 'intake/review-' + role + '.json'}
                                     for role in ('architect_agent', 'developer_agent', 'test_agent')]}
        self.output = 'generated/project-agents/admitted'
        put(self.root, 'intake/admission.json', self.request)

    def plan(self):
        put(self.root, 'intake/admission.json', self.request)
        result = admission.plan(self.root, 'intake/admission.json', self.output)
        return ac.Engine(self.root, result['run_id'])

    def change_record(self, **values):
        record = copy.deepcopy(self.records['developer_agent'])
        record.update(values)
        put(self.root, 'intake/review-developer_agent.json', record)

    def validate_record(self):
        return review.validate_review(self.root, self.manifest_ref, 'project-a', 'developer_agent',
                                      'project', 'intake/review-developer_agent.json', 'fixture')

    def assert_no_journal(self):
        self.assertEqual(ac.Engine(self.root, 'RUN-001').history(), [])

    def test_prepare_is_pending_no_model_no_authorization(self):
        result = admission.prepare(self.root, self.manifest_ref, 'project-a', 'developer_agent',
                                   'project', 'fixture', 'generated/project-agents/prepared')
        task = json.loads((self.root / result['task_ref']).read_text())
        template = json.loads((self.root / result['review_template_ref']).read_text())
        self.assertEqual(task['status'], 'PROPOSED')
        self.assertEqual(task['runtime_status'], 'NOT_RUN')
        self.assertEqual(template['decision'], 'pending')
        self.assertIsNone(template['reviewed_by'])
        self.assertIn('SDD', (self.root / result['brief_ref']).read_text())
        self.assert_no_journal()
        with self.assertRaises(pc.ContextError):
            admission.prepare(self.root, self.manifest_ref, 'project-a', 'developer_agent',
                              'project', 'fixture', 'generated/project-agents/prepared')

    def test_review_record_pass_does_not_authenticate_or_dispatch(self):
        result = self.validate_record()
        self.assertEqual(result['record_status'], 'ACCEPTED_RECORD')
        self.assertEqual(result['identity_verification'], 'not_performed')
        self.assertFalse(result['delegation_authorized'])
        self.assertEqual(result['runtime_status'], 'NOT_RUN')
        self.assert_no_journal()

    def test_pending_rejected_or_changes_requested_cannot_admit(self):
        for decision in ('pending', 'rejected', 'changes_requested', True):
            with self.subTest(decision=decision):
                self.change_record(decision=decision)
                with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_NOT_ACCEPTED'):
                    self.plan()
                self.assert_no_journal()

    def test_same_named_reviewer_case_alias_rejected(self):
        self.change_record(prepared_by='Reviewer', reviewed_by='reviewer')
        with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_SELF_ACCEPTANCE'):
            self.validate_record()

    def test_review_wrong_project_role_variant_or_version_rejected(self):
        for key in ('project_id', 'role_id', 'variant', 'profile_version', 'manifest_version', 'manifest_ref'):
            with self.subTest(key=key):
                self.change_record(**{key: 'wrong'})
                with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_BINDING_MISMATCH'):
                    self.validate_record()

    def test_review_fixture_not_usable_as_real_record(self):
        with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_BINDING_MISMATCH'):
            review.validate_review(self.root, self.manifest_ref, 'project-a', 'developer_agent',
                                   'project', 'intake/review-developer_agent.json', 'real')

    def test_review_unknown_permission_field_rejected(self):
        self.change_record(allow_deployment=True)
        with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_FIELDS'):
            self.validate_record()

    def test_review_timestamp_must_have_timezone(self):
        for timestamp in (None, [], 'bad', '2026-11-15T00:00:00'):
            self.change_record(reviewed_at=timestamp)
            with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_TIME'):
                self.validate_record()

    def test_missing_input_hash_or_extra_capability_cannot_be_reviewed(self):
        self.change_record(input_hashes={})
        with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_INPUT_COVERAGE'):
            self.validate_record()

    def test_evidence_missing_malformed_stale_or_empty_rejected(self):
        for evidence in ({}, [], {'docs/review-evidence.md': []}, {'docs/review-evidence.md': '0' * 64}):
            self.change_record(evidence_hashes=evidence)
            with self.assertRaises(pc.ContextError):
                self.validate_record()
        put(self.root, 'docs/review-evidence.md', '')
        self.change_record(evidence_hashes={'docs/review-evidence.md': pc.fingerprint(self.root / 'docs/review-evidence.md')})
        with self.assertRaisesRegex(pc.ContextError, 'INIT_REVIEW_EVIDENCE_STALE'):
            self.validate_record()

    def test_missing_or_self_referenced_confirmation_rejected(self):
        for ref in ('docs/missing.md', 'intake/review-developer_agent.json', '.env'):
            self.change_record(confirmation_ref=ref)
            with self.assertRaises(pc.ContextError):
                self.validate_record()

    def test_missing_selected_role_blocks_before_journal(self):
        self.request['profiles'] = self.request['profiles'][:1]
        with self.assertRaisesRegex(pc.ContextError, 'INIT_PLANNED_ROLE_NOT_REVIEWED'):
            self.plan()
        self.assert_no_journal()

    def test_duplicate_role_cannot_choose_two_variants(self):
        self.request['profiles'].append(copy.deepcopy(self.request['profiles'][0]))
        with self.assertRaisesRegex(pc.ContextError, 'INIT_ADMISSION_DUPLICATE_ROLE'):
            self.plan()
        self.assert_no_journal()

    def test_stale_profile_denied_before_any_journal(self):
        put(self.root, 'docs/api.md', 'changed standard')
        with self.assertRaisesRegex(pc.ContextError, 'INIT_PROFILE_NOT_CURRENT'):
            self.plan()
        self.assert_no_journal()

    def test_stale_task_context_pack_denied(self):
        put(self.root, 'src/app.py', 'VALUE = 2\n')
        with self.assertRaisesRegex(pc.ContextError, 'INIT_TASK_PACK_STALE'):
            self.plan()
        self.assert_no_journal()

    def test_task_pack_cannot_be_for_another_task(self):
        self.context['task_ref'] = 'wiki/workitems/TASK-other.md'
        put(self.root, self.context['task_ref'], 'Other task')
        put(self.root, 'intake/context.json', self.context)
        with self.assertRaisesRegex(pc.ContextError, 'INIT_TASK_PACK_MISMATCH'):
            self.plan()
        self.assert_no_journal()

    def test_existing_delegation_authorization_still_required(self):
        self.auth['allow_delegation'] = False
        put(self.root, 'intake/authorization.json', self.auth)
        with self.assertRaisesRegex(ac.Fault, 'AUTH_REQUIRED'):
            self.plan()
        self.assert_no_journal()

    def test_broad_authorization_cannot_modify_bound_rules(self):
        for scope in ('docs', 'generated', 'intake', 'package.json'):
            with self.subTest(scope=scope):
                self.auth['write_paths'] = ['outputs', 'src', scope]
                put(self.root, 'intake/authorization.json', self.auth)
                with self.assertRaisesRegex(pc.ContextError, 'INIT_AUTH_WRITES_BOUND_INPUT'):
                    self.plan()
                self.assert_no_journal()

    def test_plan_uses_original_journal_and_freezes_profile_from_first_event(self):
        before = (self.root / '.codex/agents/developer_agent.toml').read_bytes()
        engine = self.plan()
        first = engine.history()[0]['state']
        self.assertIn('project_agent_initialization', first)
        self.assertIn('docs/api.md', first['anchors'])
        self.assertEqual(first['project_agent_initialization']['runtime_initialization'], 'NOT_RUN')
        self.assertEqual(before, (self.root / '.codex/agents/developer_agent.toml').read_bytes())
        self.assertFalse(any(r['event']['event_type'] == 'AGENT_STARTED' for r in engine.history()))
        self.assertIn('architecture_pre', engine.ready())

    def test_actual_engine_packet_contains_role_brief_and_norms(self):
        engine = self.plan()
        packet = engine.packet(engine.load(), 'analysis')
        refs = {d['ref'] for d in packet['documents']}
        self.assertIn(self.output + '/brief-developer_agent.md', refs)
        self.assertIn('docs/api.md', refs)
        self.assertIn('intake/review-developer_agent.json', refs)
        self.assertEqual(packet['role'], 'developer_agent')

    def test_standard_engine_reopen_cannot_ignore_standard_drift(self):
        self.plan()
        reopened = ac.Engine(self.root, 'RUN-001')
        put(self.root, 'docs/api.md', 'changed after plan')
        with self.assertRaisesRegex(ac.Fault, 'CONTEXT_DRIFT'):
            reopened.dispatch('architecture_pre', FixtureAdapter())
        self.assertFalse(any(r['event']['event_type'] == 'AGENT_STARTED' for r in reopened.history()))

    def test_changed_review_record_blocks_reopened_engine(self):
        self.plan()
        self.change_record(decision='rejected')
        with self.assertRaisesRegex(ac.Fault, 'CONTEXT_DRIFT'):
            ac.Engine(self.root, 'RUN-001').ready()

    def test_drift_during_execution_prevents_result_write(self):
        engine = self.plan()
        root = self.root
        class Drifting(FixtureAdapter):
            def run(self, packet, started):
                result = super().run(packet, started)
                put(root, 'docs/sdd.md', 'Changed during execution')
                return result
        with self.assertRaisesRegex(ac.Fault, 'CONTEXT_DRIFT'):
            engine.dispatch('architecture_pre', Drifting())
        self.assertFalse((self.root / 'outputs/architecture_pre.md').exists())
        self.assertEqual(engine.load()['assignments']['architecture_pre']['status'], 'failed')

    def test_drift_before_handoff_review_prevents_acceptance(self):
        engine = self.plan()
        engine.dispatch('architecture_pre', FixtureAdapter())
        handoff = engine.submit('architecture_pre', 'analysis')
        put(self.root, 'docs/frontend.md', 'Changed before review')
        with self.assertRaises(ac.Fault):
            engine.review(handoff['handoff_id'], FixtureAdapter())
        self.assertNotEqual(engine.load()['handoffs'][handoff['handoff_id']]['status'], 'accepted')

    def test_unreviewed_assisting_role_is_not_enabled(self):
        engine = self.plan()
        with self.assertRaisesRegex(ac.Fault, 'CAPABILITY_UNAVAILABLE'):
            engine.assist('implementation', 'operations_review', ['src/app.py'], ['outputs/ops-help.md'])
        self.assertFalse(any(d['role'] == 'ops_agent' for d in engine.load()['assignments'].values()))

    def test_explicitly_reviewed_assisting_role_can_be_used(self):
        self.request['profiles'].append({'role_id': 'ops_agent', 'variant': 'project',
                                         'review_ref': 'intake/review-ops_agent.json'})
        engine = self.plan()
        step = engine.assist('implementation', 'operations_review', ['src/app.py'], ['outputs/ops-help.md'])
        self.assertEqual(engine.load()['assignments'][step]['role'], 'ops_agent')
        self.assertIn(self.output + '/brief-ops_agent.md', engine.load()['assignments'][step]['skill_refs'])

    def test_fixture_full_flow_keeps_existing_review_validation_and_live_gate(self):
        engine = self.plan()
        ac.drive(engine, FixtureAdapter())
        engine.validate(self.auth['validation_commands'][0])
        self.assertTrue(engine.finish()['checks_passed'])
        self.assertFalse(engine.check(release=True)['checks_passed'])
        self.assertEqual(engine.load()['project_agent_initialization']['runtime_initialization'], 'NOT_RUN')

    def test_legacy_engine_run_not_silently_claimed_initialized(self):
        engine = ac.Engine(self.root, 'RUN-legacy')
        self.context['run_id'] = 'RUN-legacy'
        put(self.root, 'intake/context.json', self.context)
        state = engine.create('intake/context.json')
        self.assertNotIn('project_agent_initialization', state)

    def test_norm_race_before_first_journal_is_rejected(self):
        original = ac.make_plan
        def raced(*args, **kwargs):
            state = original(*args, **kwargs)
            put(self.root, 'docs/api.md', 'Concurrent norm edit')
            return state
        with patch.object(ac, 'make_plan', side_effect=raced):
            with self.assertRaises(pc.ContextError):
                self.plan()
        self.assert_no_journal()

    def test_authorization_race_before_first_journal_is_rejected(self):
        original = ac.make_plan
        def raced(*args, **kwargs):
            self.auth['write_paths'].append('docs')
            put(self.root, 'intake/authorization.json', self.auth)
            return original(*args, **kwargs)
        with patch.object(ac, 'make_plan', side_effect=raced):
            with self.assertRaises((pc.ContextError, ac.Fault)):
                self.plan()
        self.assert_no_journal()

    def test_pack_source_race_before_first_journal_is_rejected(self):
        original = ac.make_plan
        def raced(*args, **kwargs):
            put(self.root, 'src/app.py', 'VALUE = 9\n')
            return original(*args, **kwargs)
        with patch.object(ac, 'make_plan', side_effect=raced):
            with self.assertRaises((pc.ContextError, ac.Fault)):
                self.plan()
        self.assert_no_journal()

    def test_duplicate_plan_preserves_history(self):
        engine = self.plan()
        before = copy.deepcopy(engine.history())
        with self.assertRaises(pc.ContextError):
            self.plan()
        self.assertEqual(before, engine.history())

    def test_cli_malformed_request_is_sanitized(self):
        put(self.root, 'intake/admission.json', {'schema': 'bad'})
        result = subprocess.run([sys.executable, str(ROOT / 'collaboration/project_agent_admission.py'),
            '--root', str(self.root), 'plan', '--request', 'intake/admission.json',
            '--output-dir', self.output], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
        self.assertNotIn(str(self.root), result.stderr)
        self.assert_no_journal()


if __name__ == '__main__':
    unittest.main()
