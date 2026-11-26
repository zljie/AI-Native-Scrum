"""Independent Sprint gate regressions using real Engine and synthetic Agent receipts.

All projects, authorizations, scenario observations and runtime receipts here are
fixtures. Passing these checks never substitutes for a logged-in local host run.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'collaboration'), str(ROOT / 'observability')]
from agent_collaboration import Engine, Fault, drive, file_hash, make_plan
from project_context import snapshot, write_once
from test_collaboration import FixtureAdapter, setup
from v15_activation import activation
from v15_controller import start_plan
from sprint_flow import assess, preview


REGISTRY = 'schema/collaboration/sprint/registry.json'
POLICY = 'schema/collaboration/sprint/policy.json'
CONTRACT = 'outputs/director_pre.json'
REPORT = 'outputs/director_verify.json'
EVIDENCE = 'outputs/synthetic-scenario-observation.txt'


def inventory(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob('*') if path.is_file()}


def project(root, signals=None):
    context, authorization = setup(root, signals or ['ui_flow'])
    for source in (ROOT / 'collaboration/sprint').iterdir():
        if source.is_file():
            target = root / 'schema/collaboration/sprint' / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
    # Sprint-only roles can require methods absent from the default six-role
    # fixture. Use actual checked-in practices without weakening missing-ref
    # checks or treating fixture role execution as host acceptance.
    registry = json.loads((root / REGISTRY).read_text())
    for entry in registry['roles'].values():
        for skill_ref in entry.get('skill_refs', []):
            if not skill_ref.startswith('.ai/skills/'):
                continue
            source = ROOT / 'collaboration/practices' / Path(skill_ref).relative_to('.ai/skills')
            if source.is_file():
                target = root / skill_ref
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
    policy = json.loads((root / POLICY).read_text())
    context['scopes'] = {step['scope_key']: ['outputs/' + step['id'] +
                         ('.json' if step['id'].startswith('director_') else '.md')]
                         for step in policy['steps']}
    context['inputs'].append(EVIDENCE)
    (root / 'intake/context.json').write_text(json.dumps(context))
    (root / 'outputs').mkdir(exist_ok=True)
    (root / EVIDENCE).write_text('Synthetic isolated scenario observation; not a user host run.\n')
    return context, authorization


class ScenarioFixtureAdapter(FixtureAdapter):
    """Produce actual Engine-owned artifacts with explicitly fixture provenance."""

    def __init__(self, verdict='PASS', contract_edit=None, report_edit=None):
        super().__init__()
        self.verdict = verdict
        self.contract_edit = contract_edit
        self.report_edit = report_edit
        self.packets = []
        self.review_packets = []

    def review(self, packet, started):
        self.review_packets.append(copy.deepcopy(packet))
        return super().review(packet, started)

    def run(self, packet, started):
        self.packets.append(copy.deepcopy(packet))
        step = packet['delegation_id']
        if step not in ('director_pre', 'director_verify'):
            return super().run(packet, started)
        self.receipt(started)
        if step == 'director_pre':
            document = {'schema': 'sprint-scenario-contract/v1', 'run_id': packet['run_id'],
                        'task_ref': packet['task_ref'], 'sample_kind': packet['sample_kind'],
                        'scenarios': [{'id': 'SC-01',
                                       'acceptance_ref': Path(packet['story_ref']).stem.split('_', 1)[0] + '#AC-01',
                                       'required': True}]}
            if self.contract_edit:
                self.contract_edit(document)
        else:
            manifest = packet['dependency_manifest']
            if not manifest['complete']:
                raise ValueError('Cannot issue a scenario verdict from an incomplete task packet')
            checked = copy.deepcopy(manifest['checked_hashes'])
            documents = {entry['ref']: entry for entry in packet['documents']}
            evidence = [] if self.verdict == 'NOT_RUN' else [EVIDENCE]
            if self.verdict == 'FAIL' and 'implementation' not in packet['assignment_ids']:
                raise ValueError('Fixture rework target is unavailable in this task packet')
            document = {'schema': 'sprint-scenario-review/v1', 'run_id': packet['run_id'],
                        'task_ref': packet['task_ref'], 'sample_kind': packet['sample_kind'],
                        'attempt': packet['attempt'], 'delegation_id': step,
                        'checked_hashes': checked,
                        'evidence_hashes': {ref: documents[ref]['sha256'] for ref in evidence},
                        'scenarios': [{'id': 'SC-01', 'status': self.verdict,
                                       'evidence_refs': evidence,
                                       'reason': 'Synthetic scenario verdict in an isolated protocol test.',
                                       'rework_step': 'implementation' if self.verdict == 'FAIL' else None}]}
            if self.report_edit:
                self.report_edit(document)
        path = packet['write_paths'][0]
        previous = next((entry['sha256'] for entry in packet['documents']
                         if entry['ref'] == path), None)
        return {'outcome': 'completed', 'changes': [
                    {'path': path, 'base_sha256': previous, 'content': json.dumps(document)}],
                'artifacts': [], 'usage': None, 'assistance': None}


class SprintFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.context, self.auth = project(self.root)
        self.engine = Engine(self.root, self.context['run_id'])

    def plan(self):
        return self.engine.create('intake/context.json', REGISTRY, POLICY)

    def complete(self, verdict='PASS', contract_edit=None, report_edit=None):
        self.plan()
        drive(self.engine, ScenarioFixtureAdapter(verdict, contract_edit, report_edit))
        self.engine.validate(self.auth['validation_commands'][0])
        self.assertTrue(self.engine.check()['checks_passed'], self.engine.check())
        return assess(self.engine)

    def test_default_policy_stays_six_roles_without_sprint_directors(self):
        registry = json.loads((ROOT / 'collaboration/registry.json').read_text())
        self.assertEqual(set(registry['roles']), {'product_agent', 'architect_agent',
                         'developer_agent', 'test_agent', 'ops_agent', 'database_agent'})
        original = make_plan(self.root, 'intake/context.json',
                             'schema/collaboration/registry.json', 'schema/collaboration/policy.json')
        self.assertNotIn('director_pre', original['assignments'])
        self.assertNotIn('director_verify', original['assignments'])
        self.assertNotIn('uiux_design', original['assignments'])

    def test_opt_in_preview_selects_uiux_with_dag_and_leaves_no_files(self):
        before = inventory(self.root)
        result = preview(self.root, 'intake/context.json', REGISTRY, POLICY)
        self.assertEqual(inventory(self.root), before)
        self.assertFalse((self.root / '.ai/collaboration').exists())
        self.assertEqual(result['execution'], 'not_started')
        self.assertFalse(result['journal_created'])
        steps = {step['step']: step for step in result['assignments']}
        self.assertEqual(steps['director_pre']['role'], 'director_agent')
        self.assertEqual(steps['uiux_design']['role'], 'uiux_agent')
        self.assertIn('director_pre', steps['product']['depends_on'])
        self.assertIn('verification', steps['director_verify']['depends_on'])
        self.assertNotIn('database', steps)
        self.assertEqual(result['live_host_acceptance'], 'NOT_RUN')

    def test_database_file_does_not_activate_database_role_without_signal(self):
        (self.root / 'db').mkdir()
        (self.root / 'db/schema.sql').write_text('create table equipment(id integer);\n')
        spec = {'schema': 'project-context-request/v1', 'goal_ref': self.context['goal_ref'],
                'task_ref': self.context['task_ref'], 'sources': {
                    'architecture': [], 'database': ['db/schema.sql'], 'interfaces': [],
                    'implementation': ['src/app.py'], 'tests': [], 'requirements': []}}
        (self.root / 'intake/pack-request.json').write_text(json.dumps(spec))
        write_once(self.root, 'intake/pack.json', snapshot(self.root, 'intake/pack-request.json'))
        request = {key: self.context[key] for key in ('run_id', 'goal_ref', 'story_ref', 'task_ref',
                  'authorization_ref', 'sample_kind', 'signals', 'signal_evidence', 'scopes')}
        request.update(schema='activation-request/v1', context_pack_ref='intake/pack.json')
        (self.root / 'intake/activation.json').write_text(json.dumps(request))
        _, result = activation(self.root, 'intake/activation.json', REGISTRY, POLICY)
        self.assertIn('uiux_agent', {item['role'] for item in result['assignments']})
        self.assertNotIn('database_agent', {item['role'] for item in result['assignments']})
        start_plan(self.root, 'intake/activation.json', 'intake/compiled-context.json',
                   registry_ref=REGISTRY, policy_ref=POLICY)
        self.assertIn('director_verify', self.engine.load()['assignments'])

    def test_director_completion_without_accepted_handoff_keeps_product_blocked(self):
        self.plan()
        adapter = ScenarioFixtureAdapter()
        self.engine.dispatch('director_pre', adapter)
        self.assertNotIn('product', self.engine.ready())
        handoff = self.engine.submit('director_pre', 'product')
        self.assertNotIn('product', self.engine.ready())
        self.engine.review(handoff['handoff_id'], adapter)
        self.assertIn('product', self.engine.ready())

    def test_packet_supplies_current_identity_and_excludes_unrelated_output_from_manifest(self):
        task_ref, story_ref = 'wiki/workitems/TASK-777.md', 'wiki/workitems/STORY-777_current.md'
        (self.root / task_ref).write_text('Synthetic task with a non-default identity.\n')
        (self.root / story_ref).write_text('Synthetic Story with a non-default identity.\n')
        self.context.update(task_ref=task_ref, story_ref=story_ref)
        self.auth['task_refs'] = [task_ref]
        self.context['scopes']['independent_note'] = ['outputs/independent-note.md']
        (self.root / 'intake/context.json').write_text(json.dumps(self.context))
        (self.root / self.context['authorization_ref']).write_text(json.dumps(self.auth))
        policy = json.loads((self.root / POLICY).read_text())
        policy['steps'].append({'id': 'independent_note', 'capability': 'implementation_analysis',
                                'signals': ['ui_flow'], 'scope_key': 'independent_note',
                                'depends_on': [], 'deliverable': 'implementation_constraints',
                                'phase': 'design'})
        (self.root / POLICY).write_text(json.dumps(policy))
        self.plan()
        adapter = ScenarioFixtureAdapter()
        self.engine.dispatch('independent_note', adapter)
        drive(self.engine, adapter)
        self.engine.validate(self.auth['validation_commands'][0])
        packet = next(p for p in adapter.packets if p['delegation_id'] == 'director_verify')
        self.assertEqual(packet['task_ref'], task_ref)
        self.assertEqual(packet['story_ref'], story_ref)
        self.assertEqual(packet['goal_ref'], self.context['goal_ref'])
        self.assertEqual(packet['sample_kind'], 'fixture')
        self.assertEqual(packet['attempt'], 1)
        manifest = packet['dependency_manifest']
        self.assertTrue(manifest['complete'])
        self.assertEqual(manifest['schema'], 'collaboration-dependency-manifest/v1')
        expected_names = {'director_pre', 'product', 'uiux_design', 'test_design',
                          'implementation', 'verification'}
        self.assertEqual({item['delegation_id'] for item in manifest['ancestors']}, expected_names)
        self.assertNotIn('outputs/independent-note.md', manifest['checked_hashes'])
        expected = {}
        state = self.engine.load()
        for name in expected_names:
            expected.update(state['assignments'][name]['result_refs'])
        self.assertEqual(manifest['checked_hashes'], expected)
        result = assess(self.engine)
        self.assertTrue(result['structural_checks_passed'], result)
        self.assertEqual(json.loads((self.root / REPORT).read_text())['task_ref'], task_ref)
        self.assertEqual(json.loads((self.root / CONTRACT).read_text())['scenarios'][0]['acceptance_ref'],
                         'STORY-777#AC-01')
        self.assertFalse(hasattr(adapter, 'engine'))
        self.assertEqual(result['live_host_acceptance'], 'NOT_RUN')

    def test_transitive_artifact_only_output_is_in_manifest_and_packet_documents(self):
        artifact = 'outputs/test-design-existing.md'
        (self.root / artifact).write_text('Synthetic pre-existing test design artifact.\n')

        class ArtifactOnlyAdapter(ScenarioFixtureAdapter):
            def run(inner, packet, started):
                if packet['delegation_id'] == 'test_design':
                    inner.packets.append(copy.deepcopy(packet))
                    inner.receipt(started)
                    return {'outcome': 'completed', 'changes': [], 'artifacts': [artifact],
                            'usage': None, 'assistance': None}
                return super().run(packet, started)

        self.plan()
        adapter = ArtifactOnlyAdapter()
        drive(self.engine, adapter)
        self.engine.validate(self.auth['validation_commands'][0])
        packet = next(p for p in adapter.packets if p['delegation_id'] == 'director_verify')
        self.assertNotIn(artifact, self.engine.load()['source_hashes'])
        self.assertNotIn('test_design', self.engine.load()['assignments']['director_verify']['depends_on'])
        self.assertEqual(packet['dependency_manifest']['checked_hashes'][artifact],
                         file_hash(self.root, artifact))
        document = next(item for item in packet['documents'] if item['ref'] == artifact)
        self.assertEqual(document['sha256'], file_hash(self.root, artifact))
        self.assertEqual(document['text'], (self.root / artifact).read_text())
        result = assess(self.engine)
        self.assertTrue(result['structural_checks_passed'], result)
        self.assertEqual(result['native_spawn_agent_acceptance'], 'NOT_RUN')

    def test_handoff_review_packet_may_show_incomplete_ancestors_without_execution_claim(self):
        self.plan()
        adapter = ScenarioFixtureAdapter()
        self.engine.dispatch('director_pre', adapter)
        handoff = self.engine.submit('director_pre', 'uiux_design')
        self.engine.review(handoff['handoff_id'], adapter)
        packet = adapter.review_packets[-1]
        self.assertEqual(packet['phase'], 'handoff_review')
        self.assertEqual(packet['attempt'], 0)
        self.assertEqual(packet['task_ref'], self.context['task_ref'])
        self.assertFalse(packet['dependency_manifest']['complete'])
        ancestors = {item['delegation_id']: item for item in packet['dependency_manifest']['ancestors']}
        self.assertEqual(ancestors['product']['status'], 'proposed')
        self.assertEqual(ancestors['product']['result_refs'], {})
        self.assertIn(CONTRACT, packet['dependency_manifest']['checked_hashes'])
        self.assertNotIn('uiux_design', self.engine.ready())

    def test_writable_registry_is_rejected_by_preview_and_start_before_journal(self):
        writable_registry = 'outputs/runtime-registry.json'
        (self.root / writable_registry).write_bytes((self.root / REGISTRY).read_bytes())
        before = inventory(self.root)
        with self.assertRaisesRegex(Fault, 'CONFIG_WRITE_SCOPE_CONFLICT'):
            preview(self.root, 'intake/context.json', writable_registry, POLICY)
        self.assertEqual(inventory(self.root), before)
        spec = {'schema': 'project-context-request/v1', 'goal_ref': self.context['goal_ref'],
                'task_ref': self.context['task_ref'], 'sources': {
                    'architecture': [], 'database': [], 'interfaces': [],
                    'implementation': ['src/app.py'], 'tests': [], 'requirements': []}}
        (self.root / 'intake/pack-request.json').write_text(json.dumps(spec))
        write_once(self.root, 'intake/pack.json', snapshot(self.root, 'intake/pack-request.json'))
        request = {key: self.context[key] for key in ('run_id', 'goal_ref', 'story_ref', 'task_ref',
                  'authorization_ref', 'sample_kind', 'signals', 'signal_evidence', 'scopes')}
        request.update(schema='activation-request/v1', context_pack_ref='intake/pack.json')
        (self.root / 'intake/activation.json').write_text(json.dumps(request))
        with self.assertRaisesRegex(Fault, 'CONFIG_WRITE_SCOPE_CONFLICT'):
            start_plan(self.root, 'intake/activation.json', 'intake/rejected-context.json',
                       registry_ref=writable_registry, policy_ref=POLICY)
        self.assertFalse((self.root / '.ai/collaboration').exists())

    def test_profile_under_writable_ancestor_is_rejected_before_journal(self):
        registry = json.loads((self.root / REGISTRY).read_text())
        profile = self.root / 'outputs/profiles/director.toml'
        profile.parent.mkdir(parents=True)
        profile.write_bytes((self.root / registry['roles']['director_agent']['profile_ref']).read_bytes())
        registry['roles']['director_agent']['profile_ref'] = 'outputs/profiles/director.toml'
        (self.root / REGISTRY).write_text(json.dumps(registry))
        with self.assertRaisesRegex(Fault, 'CONFIG_WRITE_SCOPE_CONFLICT'):
            preview(self.root, 'intake/context.json', REGISTRY, POLICY)
        with self.assertRaisesRegex(Fault, 'CONFIG_WRITE_SCOPE_CONFLICT'):
            self.plan()
        self.assertFalse((self.root / '.ai/collaboration').exists())

    def test_registry_path_alias_cannot_bypass_exact_write_scope_protection(self):
        canonical = 'outputs/runtime-registry.json'
        (self.root / canonical).write_bytes((self.root / REGISTRY).read_bytes())
        self.auth['write_paths'] = [canonical]
        self.context.update(signals=['copy_only'], signal_evidence={'copy_only': ['src/app.py']},
                            scopes={'implementation': [canonical]})
        (self.root / self.context['authorization_ref']).write_text(json.dumps(self.auth))
        (self.root / 'intake/context.json').write_text(json.dumps(self.context))
        for alias in ('outputs//runtime-registry.json', 'outputs/./runtime-registry.json',
                      './outputs/runtime-registry.json'):
            with self.subTest(alias=alias):
                before = inventory(self.root)
                with self.assertRaisesRegex(Fault, 'CONFIG_WRITE_SCOPE_CONFLICT'):
                    preview(self.root, 'intake/context.json', alias, POLICY)
                with self.assertRaisesRegex(Fault, 'CONFIG_WRITE_SCOPE_CONFLICT'):
                    self.engine.create('intake/context.json', alias, POLICY)
                self.assertEqual(inventory(self.root), before)
                self.assertFalse((self.root / '.ai/collaboration').exists())

    def test_fixture_joint_pass_has_no_live_or_business_acceptance(self):
        result = self.complete()
        self.assertTrue(result['structural_checks_passed'], result)
        self.assertEqual(result['scenario_review']['status'], 'PASS')
        self.assertTrue(result['scenario_review']['current'])
        self.assertEqual(result['live_host_acceptance'], 'NOT_RUN')
        self.assertEqual(result['native_spawn_agent_acceptance'], 'NOT_RUN')
        self.assertEqual(result['human_acceptance'], 'NOT_EVALUATED')
        self.assertFalse(result['release_authorized'])

    def test_required_scenario_fail_blocks_even_after_actual_validation_pass(self):
        result = self.complete('FAIL')
        self.assertTrue(result['engineering']['checks_passed'])
        self.assertEqual(result['scenario_review']['status'], 'FAIL')
        self.assertFalse(result['structural_checks_passed'])
        self.assertIn({'scenario_id': 'SC-01', 'step': 'implementation',
                       'action': 'inspect_before_retry'}, result['rework_recommendations'])

    def test_required_scenario_not_run_blocks_even_after_actual_validation_pass(self):
        result = self.complete('NOT_RUN')
        self.assertTrue(result['engineering']['checks_passed'])
        self.assertEqual(result['scenario_review']['status'], 'NOT_RUN')
        self.assertFalse(result['structural_checks_passed'])

    def test_optional_failure_is_visible_without_rejecting_required_pass(self):
        def add_optional(contract):
            contract['scenarios'].append({'id': 'SC-02', 'acceptance_ref': 'STORY-001#AC-02',
                                          'required': False})

        def report_optional(report):
            report['scenarios'].append({'id': 'SC-02', 'status': 'FAIL', 'evidence_refs': [EVIDENCE],
                                        'reason': 'Synthetic optional observation needs follow-up.',
                                        'rework_step': 'implementation'})

        result = self.complete(contract_edit=add_optional, report_edit=report_optional)
        self.assertTrue(result['structural_checks_passed'], result)
        self.assertEqual(result['scenario_review']['status'], 'PASS')
        self.assertTrue(any(item['id'] == 'SC-02' and item['status'] == 'FAIL'
                            for item in result['scenario_review']['scenarios']))
        self.assertTrue(any(item['scenario_id'] == 'SC-02'
                            for item in result['rework_recommendations']))

    def test_assessment_is_read_only_and_does_not_finish_engine(self):
        self.complete()
        before = inventory(self.root)
        result = assess(self.engine, CONTRACT, REPORT)
        self.assertEqual(inventory(self.root), before)
        self.assertTrue(result['structural_checks_passed'])
        self.assertFalse(self.engine.load()['finished'])

    def test_missing_scenario_results_remain_not_run(self):
        self.plan()
        before = inventory(self.root)
        result = assess(self.engine)
        self.assertEqual(result['scenario_review']['status'], 'NOT_RUN')
        self.assertFalse(result['structural_checks_passed'])
        self.assertEqual(inventory(self.root), before)

    def test_record_must_be_output_of_current_director_attempt(self):
        self.complete()
        alternate = 'outputs/unowned-report.json'
        (self.root / alternate).write_bytes((self.root / REPORT).read_bytes())
        result = assess(self.engine, CONTRACT, alternate)
        self.assertEqual(result['scenario_review']['status'], 'INVALID')
        self.assertFalse(result['structural_checks_passed'])

    def test_report_identity_coverage_and_evidence_negative_cases(self):
        edits = {
            'wrong_run': lambda r: r.update(run_id='RUN-OTHER'),
            'wrong_task': lambda r: r.update(task_ref='wiki/workitems/TASK-OTHER.md'),
            'wrong_sample': lambda r: r.update(sample_kind='real'),
            'wrong_attempt': lambda r: r.update(attempt=r['attempt'] + 1),
            'bool_attempt': lambda r: r.update(attempt=True),
            'wrong_delegation': lambda r: r.update(delegation_id='verification'),
            'missing_scenario': lambda r: r.update(scenarios=[]),
            'duplicate_scenario': lambda r: r['scenarios'].append(copy.deepcopy(r['scenarios'][0])),
            'extra_scenario': lambda r: r['scenarios'].append({**r['scenarios'][0], 'id': 'SC-99'}),
            'missing_checked_hash': lambda r: r['checked_hashes'].pop(CONTRACT),
            'wrong_checked_hash': lambda r: r['checked_hashes'].update({CONTRACT: '0' * 64}),
            'extra_checked_hash': lambda r: r['checked_hashes'].update({'src/app.py': '0' * 64}),
            'wrong_evidence_hash': lambda r: r['evidence_hashes'].update({EVIDENCE: '0' * 64}),
            'pass_without_evidence': lambda r: (r['scenarios'][0].update(evidence_refs=[]),
                                               r.update(evidence_hashes={})),
            'self_evidence': lambda r: (r['scenarios'][0].update(evidence_refs=[REPORT]),
                                       r.update(evidence_hashes={REPORT: '0' * 64})),
            'unknown_rework_step': lambda r: r['scenarios'][0].update(status='FAIL', rework_step='absent'),
            'rework_on_pass': lambda r: r['scenarios'][0].update(rework_step='implementation'),
        }
        for label, edit in edits.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _, auth = project(root)
                engine = Engine(root, 'RUN-001')
                engine.create('intake/context.json', REGISTRY, POLICY)
                drive(engine, ScenarioFixtureAdapter(report_edit=edit))
                engine.validate(auth['validation_commands'][0])
                self.assertTrue(engine.check()['checks_passed'])
                result = assess(engine)
                self.assertEqual(result['scenario_review']['status'], 'INVALID', result)
                self.assertFalse(result['structural_checks_passed'])

    def test_contract_rejects_wrong_story_and_no_required_scenario(self):
        edits = {
            'wrong_story': lambda c: c['scenarios'][0].update(acceptance_ref='STORY-OTHER#AC-01'),
            'no_required': lambda c: c['scenarios'][0].update(required=False),
            'non_boolean': lambda c: c['scenarios'][0].update(required='true'),
            'duplicate_ac': lambda c: c['scenarios'].append({**c['scenarios'][0], 'id': 'SC-02'}),
        }
        for label, edit in edits.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _, auth = project(root)
                engine = Engine(root, 'RUN-001')
                engine.create('intake/context.json', REGISTRY, POLICY)
                drive(engine, ScenarioFixtureAdapter(contract_edit=edit))
                engine.validate(auth['validation_commands'][0])
                result = assess(engine)
                self.assertEqual(result['scenario_review']['status'], 'INVALID', result)
                self.assertFalse(result['structural_checks_passed'])

    def test_wrong_runtime_role_cannot_supply_director_verdict(self):
        registry = json.loads((self.root / REGISTRY).read_text())
        registry['roles']['director_agent']['capabilities'].remove('scenario_verify')
        registry['roles']['product_agent']['capabilities'].append('scenario_verify')
        (self.root / REGISTRY).write_text(json.dumps(registry))
        result = self.complete()
        self.assertEqual(self.engine.load()['assignments']['director_verify']['role'], 'product_agent')
        self.assertEqual(result['scenario_review']['status'], 'INVALID')
        self.assertFalse(result['structural_checks_passed'])

    def test_stale_observation_evidence_invalidates_record_without_rewriting_journal(self):
        self.complete()
        rows = self.engine.history()
        (self.root / EVIDENCE).write_text('Changed synthetic observation after review.\n')
        result = assess(self.engine)
        self.assertEqual(result['scenario_review']['status'], 'INVALID')
        self.assertFalse(result['structural_checks_passed'])
        self.assertEqual(self.engine.history(), rows)

    def test_retry_invalidates_scene_verdict_and_keeps_attempt_history(self):
        self.complete()
        before = self.engine.load()
        old_attempt = copy.deepcopy(before['assignments']['director_verify']['attempts'][0])
        old_rows = len(self.engine.history())
        affected = self.engine.retry('implementation', 'FIXTURE_REWORK')
        self.assertIn('director_verify', affected)
        state = self.engine.load()
        self.assertEqual(state['assignments']['director_verify']['status'], 'proposed')
        self.assertEqual(state['assignments']['director_verify']['attempts'][0], old_attempt)
        self.assertGreater(len(self.engine.history()), old_rows)
        self.assertTrue(any(h['status'] == 'superseded' for h in state['handoffs'].values()))
        result = assess(self.engine, CONTRACT, REPORT)
        self.assertFalse(result['structural_checks_passed'])
        self.assertNotEqual(result['scenario_review']['status'], 'PASS')

    def test_no_director_policy_is_not_applicable_but_rejects_supplied_records(self):
        self.context['signals'] = ['copy_only']
        self.context['signal_evidence'] = {'copy_only': ['src/app.py']}
        (self.root / 'intake/context.json').write_text(json.dumps(self.context))
        self.engine.create('intake/context.json')
        drive(self.engine, FixtureAdapter())
        self.engine.validate(self.auth['validation_commands'][0])
        result = assess(self.engine)
        self.assertEqual(result['scenario_review']['status'], 'NOT_APPLICABLE')
        self.assertTrue(result['structural_checks_passed'])
        result = assess(self.engine, EVIDENCE, EVIDENCE)
        self.assertEqual(result['scenario_review']['status'], 'INVALID')
        self.assertFalse(result['structural_checks_passed'])

    def test_user_facing_default_policy_cannot_skip_required_scenario_review(self):
        self.engine.create('intake/context.json')
        drive(self.engine, FixtureAdapter())
        self.engine.validate(self.auth['validation_commands'][0])
        result = assess(self.engine)
        self.assertTrue(result['engineering']['checks_passed'])
        self.assertNotIn('director_pre', self.engine.load()['assignments'])
        self.assertEqual(result['scenario_review']['status'], 'NOT_RUN')
        self.assertFalse(result['structural_checks_passed'])
        self.assertEqual(result['live_host_acceptance'], 'NOT_RUN')

    def test_context_change_cannot_remove_required_scenario_review(self):
        self.engine.create('intake/context.json')
        drive(self.engine, FixtureAdapter())
        self.engine.validate(self.auth['validation_commands'][0])
        self.assertTrue(self.engine.check()['checks_passed'])
        before = self.engine.history()
        self.context.update(signals=['copy_only'], signal_evidence={'copy_only': ['src/app.py']})
        (self.root / 'intake/context.json').write_text(json.dumps(self.context))
        result = assess(self.engine)
        self.assertEqual(result['scenario_review']['status'], 'INVALID')
        self.assertFalse(result['structural_checks_passed'])
        self.assertEqual(self.engine.history(), before)

    def test_concurrent_journal_append_rejects_mixed_assessment(self):
        self.complete()
        original = self.engine.check
        called = False

        def check_with_concurrent_append(*args, **kwargs):
            nonlocal called
            result = original(*args, **kwargs)
            if not called:
                called = True
                with self.engine.lock():
                    state = self.engine.load()
                    self.engine.append(state, 'TASK_CLASSIFIED', after=state['mode'],
                                       reason='FIXTURE_CONCURRENT_CHANGE')
            return result

        with mock.patch.object(self.engine, 'check', side_effect=check_with_concurrent_append):
            result = assess(self.engine)
        self.assertEqual(result['assessment_status'], 'BLOCKED')
        self.assertFalse(result['structural_checks_passed'])
        self.assertIn('SPRINT_JOURNAL_CHANGED', json.dumps(result))

    def test_cli_preview_is_read_only_and_check_fails_for_unrun_scenarios(self):
        command = [sys.executable, str(ROOT / 'collaboration/sprint_flow.py'),
                   '--root', str(self.root)]
        before = inventory(self.root)
        result = subprocess.run(command + ['preview', '--context', 'intake/context.json',
                                '--registry', REGISTRY, '--policy', POLICY], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['execution'], 'not_started')
        self.assertEqual(inventory(self.root), before)
        self.plan()
        result = subprocess.run(command + ['--run-id', 'RUN-001', 'check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)['structural_checks_passed'])


if __name__ == '__main__':
    unittest.main()
