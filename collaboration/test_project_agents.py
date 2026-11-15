"""Deterministic initialization contracts, not live Agent or human approval evidence."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'collaboration'))
import project_agents as pa
from project_context import ContextError, fingerprint


def put(root, ref, content):
    path = root / ref
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def seed(root, project_id='project-vue', framework='Vue'):
    put(root, 'schema/collaboration/registry.json', (ROOT / 'collaboration/registry.json').read_text())
    put(root, 'schema/agent-roles.yaml', '# Synthetic role contract for deterministic tests\n')
    put(root, 'schema/roles/database_agent.md', '# Synthetic optional database contract\n')
    put(root, 'docs/frontend.md', framework + ' project-specific conventions\n')
    put(root, 'docs/api.md', 'API contract fixture\n')
    put(root, 'docs/sdd.md', 'Specification before implementation\n')
    put(root, 'docs/confirmation.md', 'Synthetic declaration only; not authenticated consent\n')
    put(root, 'package.json', json.dumps({'framework': framework}))
    request = {'schema': pa.REQUEST, 'project_id': project_id,
               'registry_ref': 'schema/collaboration/registry.json', 'roles': [{
                   'role_id': 'developer_agent', 'variant': 'frontend',
                   'required_standards': ['frontend', 'api', 'sdd'],
                   'standards': {name: {'source_ref': 'docs/' + name + '.md',
                                        'confirmation_ref': 'docs/confirmation.md'}
                                 for name in ('frontend', 'api', 'sdd')},
                   'fact_refs': ['package.json'], 'conflict_refs': []}]}
    put(root, 'intake/agent-init.json', json.dumps(request))
    return request


class ProjectAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.request = seed(self.root)

    def build(self):
        put(self.root, 'intake/agent-init.json', json.dumps(self.request))
        return pa.build(self.root, 'intake/agent-init.json')

    def rehash(self, manifest):
        manifest['version'] = pa.digest({k: v for k, v in manifest.items() if k != 'version'})

    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'collaboration/project_agents.py'),
                               '--root', str(self.root), *args], capture_output=True, text=True, timeout=20)

    def test_candidate_is_deterministic_and_never_authorizes(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        manifest = self.build()
        self.assertEqual(manifest, self.build())
        self.assertEqual(manifest['configuration_status'], 'CANDIDATE')
        self.assertEqual(manifest['runtime_status'], 'NOT_RUN')
        result = pa.check(self.root, manifest, 'project-vue')
        self.assertTrue(result['current'])
        self.assertFalse(result['delegation_authorized'])
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertNotIn('project-specific conventions', json.dumps(manifest))

    def test_two_projects_share_role_not_requirements(self):
        vue = self.build()
        with tempfile.TemporaryDirectory() as temp:
            other = Path(temp).resolve()
            seed(other, 'project-react', 'React')
            react = pa.build(other, 'intake/agent-init.json')
            self.assertEqual(vue['profiles'][0]['role_id'], react['profiles'][0]['role_id'])
            self.assertNotEqual(vue['profiles'][0]['version'], react['profiles'][0]['version'])
            self.assertNotEqual(vue['dependencies']['docs/frontend.md'], react['dependencies']['docs/frontend.md'])
            self.assertTrue(pa.check(other, react, 'project-react')['current'])
            self.assertEqual(vue, self.build())

    def test_wrong_project_rejected(self):
        with self.assertRaisesRegex(ContextError, 'INIT_PROJECT_MISMATCH'):
            pa.check(self.root, self.build(), 'other-project')

    def test_all_existing_roles_and_variants_reused(self):
        registry = json.loads((ROOT / 'collaboration/registry.json').read_text())
        template = self.request['roles'][0]
        self.request['roles'] = [dict(copy.deepcopy(template), role_id=role) for role in registry['roles']]
        self.request['roles'].append(dict(copy.deepcopy(template), variant='backend'))
        manifest = self.build()
        self.assertEqual(len(manifest['profiles']), 7)
        self.assertEqual(manifest['profiles'][0]['capabilities'], registry['roles']['product_agent']['capabilities'])

    def test_unknown_or_disabled_role_rejected(self):
        for name in ('unknown_agent', 'developer_agent'):
            with self.subTest(name=name):
                self.request['roles'][0]['role_id'] = name
                if name == 'developer_agent':
                    ref = self.root / self.request['registry_ref']
                    registry = json.loads(ref.read_text())
                    registry['roles'][name]['enabled'] = False
                    ref.write_text(json.dumps(registry))
                with self.assertRaisesRegex(ContextError, 'INIT_ROLE_UNAVAILABLE'):
                    self.build()

    def test_missing_standard_not_satisfied_by_fact(self):
        role = self.request['roles'][0]
        del role['standards']['sdd']
        role['fact_refs'].append('docs/sdd.md')
        manifest = self.build()
        self.assertEqual(manifest['configuration_status'], 'BLOCKED')
        self.assertIn({'code': 'MISSING_STANDARD', 'standard': 'sdd'}, manifest['profiles'][0]['findings'])
        self.assertEqual(pa.check(self.root, manifest, 'project-vue')['configuration_status'], 'BLOCKED')

    def test_conflicts_remain_blocked(self):
        put(self.root, 'docs/conflict.md', 'API return convention unresolved')
        self.request['roles'][0]['conflict_refs'] = ['docs/conflict.md']
        self.assertEqual(self.build()['configuration_status'], 'BLOCKED')

    def test_confirmation_reference_required_but_not_authenticated(self):
        manifest = self.build()
        self.assertEqual(manifest['confirmation_identity'], 'not_verified')
        del self.request['roles'][0]['standards']['sdd']['confirmation_ref']
        with self.assertRaisesRegex(ContextError, 'INIT_STANDARD_FIELDS'):
            self.build()

    def test_project_scope_cannot_add_permissions_or_prompts(self):
        for key in ('permissions', 'tools', 'system_prompt', 'authorization'):
            with self.subTest(key=key):
                self.request['roles'][0][key] = 'allow-all'
                with self.assertRaisesRegex(ContextError, 'INIT_BINDING_FIELDS'):
                    self.build()
                del self.request['roles'][0][key]

    def test_nested_lists_rejected_without_type_error(self):
        for key in ('required_standards', 'fact_refs', 'conflict_refs'):
            original = self.request['roles'][0][key]
            for value in ([[]], [{}], [''], 'not-a-list'):
                with self.subTest(key=key, value=value):
                    self.request['roles'][0][key] = value
                    with self.assertRaisesRegex(ContextError, 'INIT_STRING_LIST'):
                        self.build()
            self.request['roles'][0][key] = original

    def test_duplicate_role_variant_rejected(self):
        self.request['roles'].append(copy.deepcopy(self.request['roles'][0]))
        with self.assertRaisesRegex(ContextError, 'INIT_DUPLICATE_ROLE_VARIANT'):
            self.build()

    def test_request_unknown_fields_rejected(self):
        self.request['approved'] = True
        with self.assertRaisesRegex(ContextError, 'INIT_REQUEST_FIELDS'):
            self.build()

    def test_duplicate_json_keys_rejected(self):
        put(self.root, 'intake/duplicate.json', '{"schema":"one","schema":"two"}')
        with self.assertRaisesRegex(ContextError, 'INIT_DUPLICATE_JSON_KEY'):
            pa.build(self.root, 'intake/duplicate.json')

    def test_drift_reports_affected_role_without_mutation(self):
        other = copy.deepcopy(self.request['roles'][0])
        other.update(role_id='test_agent', variant='verification', required_standards=['sdd'],
                     standards={'sdd': other['standards']['sdd']}, fact_refs=[])
        self.request['roles'].append(other)
        manifest = self.build()
        before = copy.deepcopy(manifest)
        put(self.root, 'docs/frontend.md', 'Changed frontend convention')
        result = pa.check(self.root, manifest, 'project-vue')
        self.assertEqual(result['configuration_status'], 'STALE')
        self.assertEqual(result['changed_refs'], ['docs/frontend.md'])
        self.assertEqual(result['affected_profiles'], ['developer_agent:frontend'])
        self.assertEqual(before, manifest)

    def test_common_contract_or_request_drift_invalidates(self):
        for ref in ('schema/agent-roles.yaml', 'intake/agent-init.json', self.request['registry_ref'], 'docs/confirmation.md'):
            with self.subTest(ref=ref):
                manifest = self.build()
                original = (self.root / ref).read_bytes()
                (self.root / ref).write_bytes(original + b'\n')
                self.assertFalse(pa.check(self.root, manifest, 'project-vue')['current'])
                (self.root / ref).write_bytes(original)

    def test_deleted_dependency_is_stale(self):
        manifest = self.build()
        (self.root / 'docs/api.md').unlink()
        self.assertEqual(pa.check(self.root, manifest, 'project-vue')['configuration_status'], 'STALE')

    def test_manifest_cannot_claim_runtime_or_authorization(self):
        for key in pa.AUTHORITY:
            manifest = self.build()
            manifest[key] = 'PASS'
            self.rehash(manifest)
            with self.assertRaisesRegex(ContextError, 'INIT_AUTHORITY'):
                pa.check(self.root, manifest, 'project-vue')

    def test_rehashed_forgery_rejected_by_rederivation(self):
        manifest = self.build()
        manifest['profiles'][0]['capabilities'].append('production_deploy')
        self.rehash(manifest)
        with self.assertRaisesRegex(ContextError, 'INIT_DERIVATION_MISMATCH'):
            pa.check(self.root, manifest, 'project-vue')

    def test_omitted_dependency_cannot_be_hidden_by_rehash(self):
        manifest = self.build()
        del manifest['dependencies']['docs/api.md']
        manifest['profiles'][0]['input_refs'].remove('docs/api.md')
        self.rehash(manifest)
        with self.assertRaisesRegex(ContextError, 'INIT_DERIVATION_MISMATCH'):
            pa.check(self.root, manifest, 'project-vue')

    def test_sensitive_escape_and_noncanonical_sources_rejected(self):
        for ref in ('../outside', '/tmp/outside', '.env', '.ai/tool.py', 'docs//api.md',
                    'docs/./api.md', 'docs/api.md\n', 'secrets/token', 'docs\\api.md'):
            with self.subTest(ref=ref):
                self.request['roles'][0]['fact_refs'] = [ref]
                with self.assertRaises(ContextError):
                    self.build()

    def test_symlink_source_rejected(self):
        (self.root / 'docs/link.md').symlink_to(self.root / 'docs/api.md')
        self.request['roles'][0]['fact_refs'] = ['docs/link.md']
        with self.assertRaisesRegex(ContextError, 'SYMLINK_REF'):
            self.build()

    def test_cli_write_once_and_source_preservation(self):
        args = ('build', '--spec', 'intake/agent-init.json', '--output', 'generated/project-agents/p1.json')
        before = fingerprint(self.root / 'docs/api.md')
        first = self.cli(*args)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.cli(*args)
        self.assertEqual(second.returncode, 2)
        self.assertIn('OUTPUT_EXISTS', second.stderr)
        result = self.cli('check', '--manifest', 'generated/project-agents/p1.json', '--project-id', 'project-vue')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['delegation_authorized'])
        self.assertEqual(before, fingerprint(self.root / 'docs/api.md'))
        self.assertFalse((self.root / '.ai').exists())

    def test_cli_blocked_and_stale_nonzero(self):
        del self.request['roles'][0]['standards']['sdd']
        self.build()
        result = self.cli('build', '--spec', 'intake/agent-init.json', '--output', 'generated/project-agents/blocked.json')
        self.assertEqual(result.returncode, 1, result.stderr)
        put(self.root, 'docs/api.md', 'Changed')
        result = self.cli('check', '--manifest', 'generated/project-agents/blocked.json', '--project-id', 'project-vue')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['configuration_status'], 'STALE')

    def test_cli_cannot_write_governance_or_follow_output_symlink(self):
        result = self.cli('build', '--spec', 'intake/agent-init.json', '--output', 'schema/other.json')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'schema/other.json').exists())
        (self.root / 'generated').mkdir()
        (self.root / 'generated/project-agents').symlink_to(self.root / 'docs', target_is_directory=True)
        result = self.cli('build', '--spec', 'intake/agent-init.json', '--output', 'generated/project-agents/p.json')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'docs/p.json').exists())

    def test_cli_deep_json_is_sanitized(self):
        put(self.root, 'intake/deep.json', '[' * 2000 + '0' + ']' * 2000)
        result = self.cli('build', '--spec', 'intake/deep.json', '--output', 'generated/project-agents/p.json')
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)
        self.assertNotIn(str(self.root), result.stderr)


@unittest.skipUnless((ROOT / 'initdir.sh').is_file(), 'Full checkout required for generated-project integration')
class GeneratedProjectAgentTests(unittest.TestCase):
    def test_real_bootstrap_contracts_consumed_without_installing_or_launching(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            request = seed(root)
            (root / 'schema/agent-roles.yaml').unlink()
            (root / 'schema/roles/database_agent.md').unlink()
            for name in ('initdir.sh', '00_AI_WARMUP.md'):
                shutil.copyfile(ROOT / name, root / name)
            process = subprocess.run(['bash', 'initdir.sh'], cwd=root, capture_output=True, text=True, timeout=180)
            self.assertEqual(process.returncode, 0, process.stdout[-2000:] + process.stderr[-2000:])
            before = (root / '.codex/agents/developer_agent.toml').read_bytes()
            manifest = pa.build(root, 'intake/agent-init.json')
            self.assertTrue(pa.check(root, manifest, request['project_id'])['current'])
            self.assertEqual(manifest['runtime_status'], 'NOT_RUN')
            self.assertEqual(before, (root / '.codex/agents/developer_agent.toml').read_bytes())
            # S1 explicitly does not claim target-project installation.
            self.assertFalse((root / '.ai/tools/project_agents.py').exists())


if __name__ == '__main__':
    unittest.main()
