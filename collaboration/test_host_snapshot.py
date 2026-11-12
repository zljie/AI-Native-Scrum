"""Capture provenance and integrity checks, not authenticated host acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from host_contract import capture, inspect_installed, verify_snapshot


class SnapshotTests(unittest.TestCase):
    raw = b'{"properties": {}}'

    def test_capture_binds_exact_bytes_and_unique_observation(self):
        first = capture(self.raw, 'installed_codex', '0.167.0-alpha.4')
        second = capture(self.raw, 'installed_codex', '0.167.0-alpha.4')
        self.assertEqual(first['schema_sha256'], hashlib.sha256(self.raw).hexdigest())
        self.assertNotEqual(first['capture_id'], second['capture_id'])
        self.assertFalse(verify_snapshot(second, first['snapshot_sha256']))
        self.assertTrue(verify_snapshot(first, first['snapshot_sha256']))
        self.assertEqual(first['native_spawn'], 'NOT_VERIFIED')

    def test_every_evidence_field_is_bound(self):
        report = capture(self.raw, 'installed_codex', '0.167.1')
        for field, value in {'source': 'supplied_schema', 'host_version': '0.168.0',
                             'schema_sha256': 'a'*64, 'capture_id': 'other',
                             'captured_at': 'later', 'native_spawn': 'VERIFIED',
                             'restricted_read_declared': True}.items():
            with self.subTest(field=field):
                self.assertFalse(verify_snapshot({**report, field: value}, report['snapshot_sha256']))

    def test_import_never_borrows_local_version(self):
        report = capture(self.raw, 'supplied_schema')
        self.assertEqual(report['host_version'], 'UNKNOWN')
        with self.assertRaisesRegex(ValueError, 'IMPORTED_VERSION_UNVERIFIED'):
            capture(self.raw, 'supplied_schema', '0.167.1')

    def test_invalid_source_version_and_expected_digest(self):
        for source, version in [('arbitrary', 'UNKNOWN'), ('installed_codex', 'SECRET /private/path')]:
            with self.assertRaises(ValueError):
                capture(self.raw, source, version)
        report = capture(self.raw, 'supplied_schema')
        for invalid in (None, [], '', 'a'*63, 'SECRET'):
            self.assertFalse(verify_snapshot(report, invalid))
        self.assertFalse(verify_snapshot([], report['snapshot_sha256']))

    def test_version_probe_is_strict_and_schema_uses_same_binary(self):
        for stdout, expected in [(b'codex-cli 0.167.1\n', '0.167.1'),
                                 (b'codex-cli 0.167.1 SECRET\n', 'UNKNOWN')]:
            calls = []
            def run(argv, **kwargs):
                calls.append(argv)
                if argv[1] == '--version':
                    return subprocess.CompletedProcess(argv, 0, stdout, b'')
                output = Path(argv[-1])/'v2/TurnStartParams.json'
                output.parent.mkdir()
                output.write_bytes(self.raw)
                return subprocess.CompletedProcess(argv, 0, b'', b'')
            with patch('host_contract.shutil.which', return_value='/fixture/codex'), patch('host_contract.subprocess.run', side_effect=run):
                report = inspect_installed()
            self.assertEqual(report['host_version'], expected)
            self.assertEqual([call[0] for call in calls], ['/fixture/codex']*2)
            self.assertNotIn('SECRET', json.dumps(report))
            self.assertNotIn('/fixture', json.dumps(report))

    def test_version_timeout_is_unknown_not_schema_failure(self):
        def run(argv, **kwargs):
            if argv[1] == '--version':
                raise subprocess.TimeoutExpired(argv, 10)
            output = Path(argv[-1])/'v2/TurnStartParams.json'
            output.parent.mkdir()
            output.write_bytes(self.raw)
            return subprocess.CompletedProcess(argv, 0, b'', b'')
        with patch('host_contract.shutil.which', return_value='/fixture/codex'), patch('host_contract.subprocess.run', side_effect=run):
            self.assertEqual(inspect_installed()['host_version'], 'UNKNOWN')

    def test_cli_roundtrip_and_wrong_capture_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = capture(self.raw, 'supplied_schema')
            path = Path(tmp)/'snapshot.json'
            path.write_text(json.dumps(snapshot))
            command = [sys.executable, str(Path(__file__).with_name('host_contract.py')),
                       '--verify-snapshot', str(path), '--expected-snapshot-sha256']
            for digest, code in [(snapshot['snapshot_sha256'], 0), ('a'*64, 2)]:
                result = subprocess.run(command+[digest], capture_output=True, text=True)
                self.assertEqual(result.returncode, code)
                self.assertEqual(json.loads(result.stdout)['native_spawn'], 'NOT_VERIFIED')
                self.assertNotIn(tmp, result.stdout+result.stderr)

    def test_deep_or_cyclic_input_fails_safely(self):
        cyclic = {'provenance_version': 'host-capability-snapshot/v1', 'snapshot_sha256': 'a'*64}
        cyclic['cycle'] = cyclic
        self.assertFalse(verify_snapshot(cyclic, 'a'*64))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'deep.json'
            path.write_text('['*10000 + '0' + ']'*10000)
            for options in (['--schema', str(path)], ['--verify-snapshot', str(path), '--expected-snapshot-sha256', 'a'*64]):
                result = subprocess.run([sys.executable, str(Path(__file__).with_name('host_contract.py'))]+options,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(json.loads(result.stdout)['status'].startswith('BLOCKED_'))
                self.assertEqual(result.stderr, '')
