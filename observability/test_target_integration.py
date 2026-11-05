"""Integration with the actual generated framework; CI enables this explicitly."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 'cec13f7557f199324f79e916b33334cf52471244'


@unittest.skipUnless(os.environ.get('AI_NATIVE_REAL_BOOTSTRAP') == '1', 'requires actual repository bootstrap (enabled in CI)')
class TargetIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'project with spaces'
        self.root.mkdir()
        for name in ('initdir.sh', '00_AI_WARMUP.md'):
            shutil.copyfile(ROOT / name, self.root / name)
        self.call(['bash', 'initdir.sh'])

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, cmd, expected=0, env=None):
        result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, timeout=180, env=env)
        self.assertEqual(result.returncode, expected, result.stdout[-3000:] + result.stderr[-3000:])
        return result

    def test_selfcontained_disabled_and_sources_in_sync(self):
        for name in ('harness_observe.py', 'harness_report.py'):
            self.assertEqual((self.root / '.ai/tools' / name).read_bytes(), (ROOT / 'observability' / name).read_bytes())
        status = json.loads(self.call(['python3', '.ai/tools/harness_observe.py', 'status']).stdout)
        self.assertFalse(status['enabled'])
        self.assertEqual(status['host_events_observed'], [])
        health = json.loads(self.call(['python3', '.ai/tools/harness_observe.py', 'report']).stdout)
        self.assertTrue(health['no_data'])
        self.assertIsNone(health['total_tokens'])
        self.assertFalse((self.root / '.ai/observability/config.json').exists())
        self.call(['python3', '.ai/tools/check_framework.py'])

    def test_actual_runner_fixture_and_authorization_preserved(self):
        self.call(['python3', '.ai/tools/harness_observe.py', 'enable', '--sample-kind', 'fixture'])
        self.call(['python3', '.ai/tools/harness_observe.py', 'install-hooks', '--provider', 'codex', '--apply'])
        self.call(['python3', '.ai/tools/check_framework.py'])
        (self.root / 'raw/goals/GOAL-001.md').write_text('---\nid: GOAL-001\nstatus: approved\n---\nSynthetic fixture ONLY, not a user approval.\n')
        (self.root / 'intake/auth-fixture.md').write_text('Synthetic test authorization, isolated temporary project only.')
        (self.root / 'intake/prompt-fixture.md').write_text('SECRET-CANARY-PROMPT')
        bindir = self.root / 'fake-bin'
        bindir.mkdir()
        binary = bindir / 'codex'
        binary.write_text('#!/usr/bin/env python3\nimport json,sys\nassert sys.argv[sys.argv.index("--sandbox")+1] == "read-only"\nprint(json.dumps({"type":"item.completed","item":{"text":"SECRET-CANARY-RESPONSE"}}))\nprint(json.dumps({"type":"turn.completed","usage":{"input_tokens":100,"cached_input_tokens":40,"output_tokens":20}}))\n')
        binary.chmod(0o700)
        env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ['PATH'])
        cmd = ['python3', '.ai/tools/local_agent_runner.py', 'run', '--run-id', 'RUN-001', '--goal', 'GOAL-001',
               '--task', 'TASK-001', '--role', 'test_agent', '--provider', 'codex', '--prompt-file', 'intake/prompt-fixture.md',
               '--authorization-ref', 'intake/auth-fixture.md', '--execute']
        self.call(cmd, env=env)
        health = json.loads(self.call(['python3', '.ai/tools/harness_observe.py', 'report', '--include-fixtures']).stdout)
        self.assertEqual(health['total_tokens'], 120)
        self.assertEqual(health['native_subagent_instances'], 0)
        self.assertEqual(health['run_results'], {'process_succeeded': 1})
        for file in (self.root / '.ai/observability/events').glob('*.json'):
            self.assertNotIn('SECRET-CANARY', file.read_text())
        self.assertTrue((self.root / 'wiki/runs/RUN-001.json').exists())
        self.call(cmd, expected=2, env=env)  # existing RUN ID remains protected
        self.call(cmd + ['--allow-write'], expected=2, env=env)  # independent write approval still required
        noauth = list(cmd)
        noauth[noauth.index('intake/auth-fixture.md')] = 'intake/no-auth.md'
        self.call(noauth, expected=2, env=env)

    def test_hook_from_config_runs_in_nested_non_git_directory(self):
        self.call(['python3', '.ai/tools/harness_observe.py', 'enable', '--sample-kind', 'fixture'])
        self.call(['python3', '.ai/tools/harness_observe.py', 'install-hooks', '--provider', 'codex', '--apply'])
        config = json.loads((self.root / '.codex/hooks.json').read_text())
        command = config['hooks']['SubagentStart'][-1]['hooks'][0]['command']
        nested = self.root / 'nested dir'
        nested.mkdir()
        payload = json.dumps({'hook_event_name': 'SubagentStart', 'session_id': 'fixture-session', 'agent_id': 'fixture-agent', 'agent_type': 'test_agent'})
        result = subprocess.run(['sh', '-c', command], input=payload, text=True, capture_output=True, cwd=nested, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '{}')
        health = json.loads(self.call(['python3', '.ai/tools/harness_observe.py', 'report', '--include-fixtures']).stdout)
        self.assertEqual(health['native_subagent_instances'], 1)
        # This is a shell replay of the exact configured command, not a live native host test.

    def test_v12_upgrade_preserves_business_and_local_rules(self):
        old = Path(self.tmp.name) / 'old'
        old.mkdir()
        for name in ('initdir.sh', '00_AI_WARMUP.md'):
            result = subprocess.run(['git', 'show', BASE + ':' + name], cwd=ROOT, capture_output=True, check=True)
            (old / name).write_bytes(result.stdout)
        subprocess.run(['bash', 'initdir.sh'], cwd=old, capture_output=True, check=True)
        agent = old / 'AGENTS.md'
        agent.write_text(agent.read_text() + '\nLOCAL_CUSTOM_RULE_MUST_SURVIVE\n')
        business = old / 'raw/goals/GOAL-777.md'
        business.write_text('Unapproved synthetic project knowledge; preserve exactly.\n')
        before = {str(p.relative_to(old)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (agent, business)}
        upgrade = subprocess.run(['bash', str(ROOT / 'initdir.sh'), '--upgrade', '--apply'], cwd=old,
                                 capture_output=True, text=True, timeout=180)
        self.assertEqual(upgrade.returncode, 0, upgrade.stdout[-3000:] + upgrade.stderr[-3000:])
        for path, digest in before.items():
            self.assertEqual(hashlib.sha256((old / path).read_bytes()).hexdigest(), digest)
        self.assertTrue((old / '.ai/tools/harness_observe.py').exists())
        self.assertFalse((old / '.ai/observability/config.json').exists())
        self.assertIn('1.3', (old / '.ai/framework-version').read_text())


if __name__ == '__main__':
    unittest.main()
