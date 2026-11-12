"""Opt-in journal binding negatives; fixture results never clear live-host gates."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from codex_adapter import CodexAdapter
from agent_collaboration import Engine, Fault
from host_contract import capture
from test_collaboration import setup, FixtureAdapter


class BoundFixture(FixtureAdapter):
    def run(self, packet, started):
        def bound(receipt):
            started({**receipt, 'host_snapshot_sha256': packet['host_snapshot']['snapshot_sha256']})
        return super().run(packet, bound)
    def review(self, packet, started):
        def bound(receipt):
            started({**receipt, 'host_snapshot_sha256': packet['host_snapshot']['snapshot_sha256']})
        return super().review(packet, bound)


class HostBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        setup(self.root); self.engine = Engine(self.root, 'RUN-001')
        self.engine.create('intake/context.json')
        schema = {'properties': {'sandboxPolicy': {'properties': {'type': {'const': 'readOnly'},
                  'access': {'properties': {'type': {'const': 'restricted'}, 'readableRoots': {'type': 'array'},
                                          'includePlatformDefaults': {'type': 'boolean'}}}}}}}
        self.snapshot = capture(json.dumps(schema).encode(), 'supplied_schema')
        self.path = self.root/'intake/host.json'; self.path.write_text(json.dumps(self.snapshot))
    def tearDown(self): self.tmp.cleanup()
    def bind(self):
        return self.engine.bind_host_snapshot('intake/host.json', self.snapshot['snapshot_sha256'])

    def test_binding_is_journaled_and_receipt_correlated(self):
        self.bind(); name = self.engine.ready()[0]
        self.engine.dispatch(name, BoundFixture())
        row = self.engine.load()['assignments'][name]['attempts'][-1]
        self.assertEqual(row['host_snapshot_sha256'], self.snapshot['snapshot_sha256'])
        self.assertEqual(row['start_evidence']['host_snapshot_sha256'], self.snapshot['snapshot_sha256'])
        self.assertIn('HOST_SNAPSHOT_BOUND', [r['event']['event_type'] for r in self.engine.history()])

    def test_drift_blocks_before_dispatch(self):
        self.bind(); name = self.engine.ready()[0]
        self.path.write_text(json.dumps({**self.snapshot, 'host_version': '0.167.1'}))
        with self.assertRaisesRegex(Fault, 'HOST_SNAPSHOT_DRIFT'):
            self.engine.dispatch(name, BoundFixture())
        self.assertFalse(self.engine.load()['assignments'][name]['attempts'])

    def test_wrong_or_missing_receipt_binding_never_starts(self):
        self.bind(); name = self.engine.ready()[0]
        with self.assertRaisesRegex(Fault, 'RECEIPT_FIELDS'):
            self.engine.dispatch(name, FixtureAdapter())
        self.assertFalse([r for r in self.engine.history() if r['event']['event_type']=='AGENT_STARTED'])

    def test_binding_cannot_replace_existing_capture(self):
        self.bind(); history = len(self.engine.history())
        with self.assertRaisesRegex(Fault, 'HOST_SNAPSHOT_ALREADY_BOUND'):
            self.bind()
        self.assertEqual(len(self.engine.history()), history)

    def test_bind_after_execution_is_denied(self):
        self.engine.dispatch(self.engine.ready()[0], FixtureAdapter())
        with self.assertRaisesRegex(Fault, 'HOST_BINDING_TOO_LATE'):
            self.bind()

    def test_bad_expected_digest_and_blocked_declaration(self):
        with self.assertRaisesRegex(Fault, 'HOST_SNAPSHOT_INVALID'):
            self.engine.bind_host_snapshot('intake/host.json', 'a'*64)
        blocked = capture(b'{"properties": {}}', 'supplied_schema')
        self.path.write_text(json.dumps(blocked))
        self.engine.bind_host_snapshot('intake/host.json', blocked['snapshot_sha256'])
        with self.assertRaisesRegex(Fault, 'HOST_CAPABILITY_BLOCKED'):
            self.engine.ready()

    def test_wrong_capture_receipt_never_starts(self):
        self.bind(); name = self.engine.ready()[0]
        class Wrong(FixtureAdapter):
            def run(self, packet, started):
                return super().run(packet, lambda r: started({**r, 'host_snapshot_sha256': 'a'*64}))
        with self.assertRaisesRegex(Fault, 'HOST_RECEIPT_MISMATCH'):
            self.engine.dispatch(name, Wrong())
        self.assertFalse([r for r in self.engine.history() if r['event']['event_type']=='AGENT_STARTED'])

    def test_invalidation_during_run_blocks_artifact_apply(self):
        self.bind(); name = self.engine.ready()[0]
        engine = self.engine
        class Revoke(BoundFixture):
            def run(self, packet, started):
                result = super().run(packet, started)
                engine.invalidate_host_snapshot()
                return result
        with self.assertRaisesRegex(Fault, 'HOST_SNAPSHOT_INVALIDATED'):
            self.engine.dispatch(name, Revoke())
        self.assertFalse((self.root/'outputs').exists())
        self.assertIn('HOST_SNAPSHOT_INVALIDATED', [r['event']['event_type'] for r in self.engine.history()])
        self.assertTrue(self.engine.load()['host_binding']['invalidated'])

    def test_review_receipt_retains_bound_capture(self):
        self.bind(); first = self.engine.ready()[0]
        self.engine.dispatch(first, BoundFixture())
        target = next(k for k,v in self.engine.load()['assignments'].items() if first in v['depends_on'])
        handoff = self.engine.submit(first, target)
        reviewed = self.engine.review(handoff['handoff_id'], BoundFixture())
        self.assertEqual(reviewed['review']['receipt']['host_snapshot_sha256'], self.snapshot['snapshot_sha256'])

    def test_runtime_schema_mismatch_blocks_before_session(self):
        binding = {'source':'installed_codex', 'host_version':'0.167.1',
                   'schema_sha256':'a'*64, 'snapshot_sha256':'b'*64}
        observed = {**binding, 'schema_sha256':'c'*64, 'restricted_read_declared':True}
        adapter = CodexAdapter(self.root)
        with patch('host_contract.inspect_installed', return_value=observed), patch.object(adapter, '_session') as launch:
            with self.assertRaisesRegex(Fault, 'HOST_RUNTIME_MISMATCH'):
                adapter.run({'host_snapshot':binding, 'documents':[]}, lambda _:None)
            launch.assert_not_called()

    def test_import_cannot_back_real_runtime_binding(self):
        self.bind()
        state = self.engine.load(); state['sample_kind'] = 'real'
        with self.assertRaisesRegex(Fault, 'HOST_SOURCE_UNVERIFIED'):
            self.engine.host_snapshot(state)

    def test_snapshot_path_alias_cannot_bypass_write_protection(self):
        first = self.engine.ready()[0]
        path = self.root/'outputs'/f'{first}.md'
        path.parent.mkdir(); path.write_text(json.dumps(self.snapshot))
        alias = f'outputs/./{first}.md'
        bound = self.engine.bind_host_snapshot(alias, self.snapshot['snapshot_sha256'])
        self.assertEqual(bound['ref'], f'outputs/{first}.md')
        with self.assertRaisesRegex(Fault, 'HOST_SNAPSHOT_WRITE_DENIED'):
            self.engine.dispatch(first, BoundFixture())
        self.assertEqual(json.loads(path.read_text()), self.snapshot)

    def test_bound_probe_and_launch_share_absolute_executable(self):
        binding = {'source':'installed_codex', 'host_version':'0.167.1',
                   'schema_sha256':'a'*64, 'snapshot_sha256':'b'*64}
        observed = {**binding, 'restricted_read_declared':True}
        adapter = CodexAdapter(self.root)
        with patch('codex_adapter.shutil.which', return_value='relative/codex'), \
             patch('host_contract.inspect_installed', return_value=observed) as probe, \
             patch('codex_adapter.subprocess.Popen', side_effect=RuntimeError('intercepted')) as launch:
            with self.assertRaisesRegex(RuntimeError, 'intercepted'):
                adapter.run({'host_snapshot':binding, 'documents':[]}, lambda _:None)
            expected = str(Path('relative/codex').resolve())
            probe.assert_called_once_with(expected)
            self.assertEqual(launch.call_args.args[0], [expected, 'app-server'])
