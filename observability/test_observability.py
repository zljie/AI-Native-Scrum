#!/usr/bin/env python3
"""Deterministic fixtures only. These tests are not real model productivity measurements."""
import contextlib
import copy
from datetime import datetime, timedelta, timezone
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_observe as obs
import harness_report as report

CODEX = json.dumps({"type": "turn.completed", "usage": {"input_tokens": 100, "cached_input_tokens": 40, "output_tokens": 20}})
CLAUDE = json.dumps({"type": "result", "subtype": "success", "is_error": False, "usage": {"input_tokens": 10, "cache_read_input_tokens": 60, "cache_creation_input_tokens": 30, "output_tokens": 20}})


class UsageTests(unittest.TestCase):
    def test_codex_cache_not_added_twice(self):
        usage, result = obs.provider_usage("codex", CODEX)
        self.assertEqual((usage["total_tokens"], result), (120, "completed"))

    def test_claude_cache_normalization(self):
        usage, _ = obs.provider_usage("claude", CLAUDE)
        self.assertEqual(usage["input_tokens"], 100)
        self.assertEqual(usage["total_tokens"], 120)

    def test_no_terminal_is_unknown(self):
        self.assertIsNone(obs.provider_usage("codex", '{"type":"item.completed"}')[0]["total_tokens"])

    def test_malformed_stream_is_not_complete(self):
        usage, result = obs.provider_usage("codex", CODEX + '\nnot-json')
        self.assertFalse(usage["complete"])
        self.assertEqual(result, "unknown")

    def test_error_preserves_unknown_total(self):
        usage, result = obs.provider_usage("codex", CODEX + '\n{"type":"turn.failed"}')
        self.assertFalse(usage["complete"])
        self.assertIsNone(usage["total_tokens"])
        self.assertEqual(result, "failed")

    def test_multiple_codex_turns_sum(self):
        self.assertEqual(obs.provider_usage("codex", CODEX + '\n' + CODEX)[0]["total_tokens"], 240)

    def test_claude_does_not_add_assistant_usage(self):
        stream = json.dumps({"type": "assistant", "usage": {"input_tokens": 999}}) + '\n' + CLAUDE
        self.assertEqual(obs.provider_usage("claude", stream)[0]["total_tokens"], 120)

    def test_ambiguous_claude_terminal(self):
        self.assertFalse(obs.provider_usage("claude", CLAUDE + '\n' + CLAUDE)[0]["complete"])

    def test_negative_and_boolean_usage_rejected(self):
        for bad in (-1, True, "100", 1.5):
            usage = obs.normalize_usage("codex", {"input_tokens": 100, "cached_input_tokens": bad, "output_tokens": 10})
            self.assertFalse(usage["complete"])

    def test_cache_exceeding_input_rejected(self):
        self.assertFalse(obs.normalize_usage("codex", {"input_tokens": 10, "cached_input_tokens": 20, "output_tokens": 1})["complete"])

    def test_claude_missing_cache_is_unknown(self):
        usage = obs.normalize_usage("claude", {"input_tokens": 10, "output_tokens": 20})
        self.assertIsNone(usage["total_tokens"])

    def test_zero_is_a_valid_measurement(self):
        usage = obs.normalize_usage("codex", {"input_tokens": 0, "output_tokens": 0})
        self.assertTrue(usage["complete"])
        self.assertEqual(usage["total_tokens"], 0)


class LocalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / '.ai').mkdir()
        (self.root / '.ai/framework-version').write_text('{"framework_version":"1.3"}')
        self.env = patch.dict(os.environ, {}, clear=False)
        self.env.start()
        for key in ('AI_NATIVE_TRACE_ID', 'AI_NATIVE_RUN_ID'):
            os.environ.pop(key, None)

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def enable(self, kind='fixture'):
        obs.configure(self.root, True, kind)
        return obs.Store(self.root)

    def emit(self, store, typ='run_finished', trace='TRACE-1', span='SPAN-1', **kw):
        return store.emit(typ, 'runner', trace, span, **kw)

    def events(self):
        return obs.load_events(self.root, True)[0]

    def test_disabled_is_noop(self):
        store = obs.Store(self.root)
        self.assertIsNone(self.emit(store))
        self.assertFalse((self.root / '.ai/observability').exists())

    def test_optin_private_and_disable_preserves(self):
        store = self.enable()
        self.emit(store)
        obs.configure(self.root, False, 'fixture')
        self.assertIsNone(self.emit(obs.Store(self.root)))
        self.assertEqual(len(self.events()), 1)
        self.assertEqual((self.root / '.ai/observability/.gitignore').read_text(), '*\n')
        self.assertEqual((self.root / '.ai/observability/config.json').stat().st_mode & 0o777, 0o600)

    def test_fixture_excluded_by_default(self):
        self.emit(self.enable())
        self.assertEqual(obs.load_events(self.root)[0], [])

    def test_unknown_not_zero_without_data(self):
        summary = obs.summarize([])
        self.assertIsNone(summary['total_tokens'])
        self.assertIsNone(summary['known_token_subtotal'])
        self.assertTrue(summary['no_data'])

    def test_event_schema_and_fingerprints(self):
        event = self.emit(self.enable())
        obs.validate_event(event)
        self.assertEqual(event['framework_version'], '1.3')
        self.assertEqual(len(event['framework_fingerprint']), 64)
        self.assertEqual(len(event['collector_fingerprint']), 64)

    def test_unknown_fields_rejected(self):
        event = self.emit(self.enable())
        event['prompt'] = 'DO NOT STORE'
        with self.assertRaises(ValueError):
            obs.validate_event(event)

    def test_fake_native_source_rejected(self):
        with self.assertRaises(ValueError):
            self.enable().emit('native_subagent_started', 'self_reported', 'TRACE-1', 'SPAN-1', execution_mode='native_subagent')

    def test_concurrent_atomic_events(self):
        store = self.enable()
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda i: self.emit(store, span='SPAN-' + str(i)), range(24)))
        self.assertEqual(len(self.events()), 24)
        self.assertEqual(obs.load_events(self.root, True)[1], [])

    def test_symlink_escape_rejected(self):
        external = self.root / 'external'
        external.mkdir()
        (self.root / '.ai/observability').symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.enable()

    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            obs.safe_path(self.root, '../outside.json')

    def test_corrupt_event_visible_not_silent(self):
        self.emit(self.enable())
        (self.root / '.ai/observability/events/corrupt.json').write_text('broken')
        events, errors = obs.load_events(self.root, True)
        self.assertTrue(errors)
        self.assertFalse(obs.summarize(events, errors)['usage_complete'])

    def test_filename_identity_mismatch_rejected(self):
        event = self.emit(self.enable())
        folder = self.root / '.ai/observability/events'
        (folder / (event['event_id'] + '.json')).rename(folder / 'wrong.json')
        self.assertTrue(obs.load_events(self.root, True)[1])

    def test_native_hook_ids_hashed_no_content(self):
        self.enable()
        payload = {'hook_event_name': 'SubagentStart', 'session_id': 'SECRET-SESSION', 'agent_id': 'SECRET-AGENT',
                   'agent_type': 'test_agent', 'prompt': 'SECRET-PROMPT', 'transcript_path': '/secret/session',
                   'tool_input': {'command': 'SECRET-COMMAND'}, 'last_assistant_message': 'SECRET-RESPONSE'}
        obs.hook_record(self.root, 'codex', payload)
        serialized = json.dumps(self.events())
        self.assertNotIn('SECRET', serialized)
        self.assertNotIn('/secret', serialized)
        self.assertEqual(obs.summarize(self.events())['native_subagent_instances'], 1)

    def test_claude_skill_call_not_guidance_success(self):
        self.enable()
        obs.hook_record(self.root, 'claude', {'session_id': 's1', 'hook_event_name': 'PostToolUse',
            'tool_name': 'Skill', 'tool_input': {'skill': 'product-director', 'args': 'SECRET'}})
        result = obs.summarize(self.events())
        self.assertEqual(result['skill_invocations']['product-director'], 1)
        self.assertEqual(result['director_effectiveness'], 'requires_independent_assessment')

    def test_duplicate_tool_hook_does_not_inflate_skill_invocations(self):
        self.enable()
        payload = {'session_id': 's1', 'hook_event_name': 'PostToolUse', 'tool_name': 'Skill',
                   'tool_use_id': 'call-001', 'tool_input': {'skill': 'product-director'}}
        obs.hook_record(self.root, 'claude', payload)
        obs.hook_record(self.root, 'claude', payload)
        self.assertEqual(obs.summarize(self.events())['skill_invocations']['product-director'], 1)

    def test_codex_file_read_does_not_prove_skill_execution(self):
        self.enable()
        obs.hook_record(self.root, 'codex', {'session_id': 's', 'hook_event_name': 'PostToolUse',
            'tool_name': 'Bash', 'tool_input': {'command': 'cat .ai/skills/product-director/SKILL.md'}})
        self.assertEqual(obs.summarize(self.events())['skill_invocations'], {})

    def test_hooks_merge_idempotent_preserves_existing(self):
        self.enable()
        folder = self.root / '.codex'
        folder.mkdir()
        old = {'description': 'preserve', 'hooks': {'Stop': [{'hooks': [{'type': 'command', 'command': 'old-command'}]}]}}
        (folder / 'hooks.json').write_text(json.dumps(old))
        self.assertFalse(obs.install_hooks(self.root, 'codex')['applied'])
        self.assertEqual(json.loads((folder / 'hooks.json').read_text()), old)
        self.assertTrue(obs.install_hooks(self.root, 'codex', True)['applied'])
        self.assertFalse(obs.install_hooks(self.root, 'codex', True)['changed'])
        new = json.loads((folder / 'hooks.json').read_text())
        self.assertEqual(new['hooks']['Stop'][0], old['hooks']['Stop'][0])
        self.assertEqual(new['description'], 'preserve')
        self.assertEqual(obs.doctor(self.root)['host_events_observed'], [])

    def test_hook_handler_failure_is_nonblocking(self):
        with patch('sys.stdin', io.StringIO('not-json')), contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(obs.main(['--root', str(self.root), 'hook', '--provider', 'codex']), 0)
        self.assertEqual(output.getvalue().strip(), '{}')

    def test_usage_run_total_and_hook_not_double_counted(self):
        store = self.enable()
        usage, _ = obs.provider_usage('codex', CODEX)
        self.emit(store, 'usage_observed', run_id='RUN-001', usage=usage, usage_scope='run_total')
        store.emit('usage_observed', 'codex_hook', 'TRACE-1', 'SPAN-2', run_id='RUN-001', usage=usage, usage_scope='request')
        self.assertEqual(obs.summarize(self.events())['total_tokens'], 120)

    def test_killed_run_not_a_complete_total(self):
        store = self.enable()
        usage, _ = obs.provider_usage('codex', CODEX)
        self.emit(store, 'process_started')
        self.emit(store, 'usage_observed', usage=usage, usage_scope='run_total')
        self.assertFalse(obs.summarize(self.events())['usage_complete'])

    def test_missing_one_run_usage_invalidates_global_total(self):
        store = self.enable()
        usage, _ = obs.provider_usage('codex', CODEX)
        self.emit(store, 'process_started', span='SPAN-missing')
        self.emit(store, 'run_finished', span='SPAN-missing')
        self.emit(store, 'usage_observed', usage=usage, usage_scope='run_total')
        self.assertIsNone(obs.summarize(self.events())['total_tokens'])

    def runner_args(self, execute=True):
        return SimpleNamespace(run_id='RUN-001', goal='GOAL-001', task='TASK-001', role='test_agent', provider='codex', execute=execute)

    def test_runner_dry_run_stays_dry(self):
        self.enable()
        def runner(root, args, observer=None):
            self.assertIsNotNone(observer)
            return 0
        self.assertEqual(obs.observe_run(self.root, self.runner_args(False), runner), 0)
        self.assertNotIn('process_started', obs.summarize(self.events())['type_counts'])
        self.assertEqual(obs.summarize(self.events())['run_results'], {'dry_run': 1})

    def test_runner_validation_still_denies(self):
        self.enable()
        def runner(root, args, observer=None):
            raise ValueError('unauthorized')
        with self.assertRaises(ValueError):
            obs.observe_run(self.root, self.runner_args(), runner)
        self.assertEqual(obs.summarize(self.events())['run_results'], {'not_started': 1})

    def test_runner_real_process_boundary_fixture(self):
        self.enable()
        def runner(root, args, observer=None):
            result = observer([sys.executable, '-c', 'print(' + repr(CODEX) + ')'], cwd=root, capture_output=True, text=True, timeout=5)
            return result.returncode
        self.assertEqual(obs.observe_run(self.root, self.runner_args(), runner), 0)
        summary = obs.summarize(self.events())
        self.assertEqual(summary['total_tokens'], 120)
        self.assertEqual(summary['native_subagent_instances'], 0)
        self.assertEqual(summary['run_results'], {'process_succeeded': 1})

    def test_runner_timeout_usage_unknown(self):
        self.enable()
        def runner(root, args, observer=None):
            try:
                observer([sys.executable, '-c', 'import time;time.sleep(2)'], cwd=root, capture_output=True, text=True, timeout=0.01)
            except subprocess.TimeoutExpired:
                return 1
        self.assertEqual(obs.observe_run(self.root, self.runner_args(), runner), 1)
        self.assertIsNone(obs.summarize(self.events())['total_tokens'])

    def test_failed_run_is_included_in_cost(self):
        self.enable()
        def runner(root, args, observer=None):
            observer([sys.executable, '-c', 'print(' + repr(CODEX) + ')'], cwd=root, capture_output=True, text=True, timeout=5)
            return 1  # simulate artifact/verification failure after provider success
        self.assertEqual(obs.observe_run(self.root, self.runner_args(), runner), 1)
        self.assertEqual(obs.summarize(self.events())['total_tokens'], 120)
        self.assertEqual(obs.summarize(self.events())['run_results'], {'failed_or_unverified': 1})

    def test_export_no_overwrite_no_escape_and_safe_html(self):
        report.save_report(self.root, 'generated/reports/test.html', {'text': '<script>alert(1)</script>'})
        text = (self.root / 'generated/reports/test.html').read_text()
        self.assertNotIn('<script>', text)
        with self.assertRaises(ValueError):
            report.save_report(self.root, 'generated/reports/test.html', {})
        with self.assertRaises(ValueError):
            report.save_report(self.root, '../test.json', {})
        with self.assertRaises(ValueError):
            report.save_report(self.root, 'raw/evidence/test.json', {})

    def test_prune_default_no_delete(self):
        store = self.enable()
        event = self.emit(store)
        event['at'] = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
        path = self.root / '.ai/observability/events' / (event['event_id'] + '.json')
        path.write_text(json.dumps(event))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(obs.main(['--root', str(self.root), 'prune']), 0)
        self.assertTrue(path.exists())
        with contextlib.redirect_stdout(io.StringIO()):
            obs.main(['--root', str(self.root), 'prune', '--apply'])
        self.assertFalse(path.exists())

    def make_experiment(self):
        store = self.enable()
        (self.root / 'evidence.txt').write_text('Synthetic test-runner assessment only; not human acceptance.')
        rows = []
        for i, variant in enumerate(('baseline', 'candidate')):
            trace = 'TRACE-' + variant
            self.emit(store, 'usage_observed', trace=trace, usage=obs.normalize_usage('codex', {'input_tokens': 100 + i*20, 'output_tokens': 20}), usage_scope='run_total')
            rows.append({'case_id': 'CASE-001', 'repeat': 1, 'variant': variant,
                'task_sha256': 'a'*64, 'acceptance_sha256': 'b'*64, 'model_config_sha256': 'c'*64, 'environment_sha256': 'd'*64,
                'framework_revision': 'fixture-' + variant, 'trace_ids': [trace], 'observation_complete': True,
                'expected_director': 'product-director', 'director_guidance_passed': None, 'native_agent_applicable': True,
                'engineering_passed': True, 'first_pass': i == 1, 'rework_count': 1-i, 'human_active_seconds': None,
                'evidence_refs': ['evidence.txt'], 'reviewer_source': 'independent_test_runner', 'reviewer_id': 'fixture-runner'})
        return {'schema': 'harness-experiment/v1', 'experiment_id': 'EXP-001', 'cases': rows}

    def test_paired_compare_descriptive_metrics(self):
        result = report.compare(self.root, self.make_experiment(), True)
        self.assertAlmostEqual(result['token_change_percent'], 100/6)
        self.assertEqual(result['variants']['baseline']['first_pass']['value'], 0)
        self.assertIsNone(result['variants']['baseline']['director_effective']['value'])
        self.assertIsNone(result['variants']['candidate']['human_active_seconds']['value'])

    def test_comparison_rejects_mixed_models(self):
        manifest = self.make_experiment()
        manifest['cases'][1]['model_config_sha256'] = 'e'*64
        with self.assertRaises(ValueError):
            report.compare(self.root, manifest, True)

    def test_comparison_rejects_missing_variant(self):
        manifest = self.make_experiment()
        manifest['cases'].pop()
        with self.assertRaises(ValueError):
            report.compare(self.root, manifest, True)

    def test_comparison_rejects_missing_evidence(self):
        manifest = self.make_experiment()
        manifest['cases'][0]['evidence_refs'] = ['missing.txt']
        with self.assertRaises(ValueError):
            report.compare(self.root, manifest, True)

    def test_comparison_rejects_reused_trace(self):
        manifest = self.make_experiment()
        manifest['cases'][1]['trace_ids'] = manifest['cases'][0]['trace_ids']
        with self.assertRaises(ValueError):
            report.compare(self.root, manifest, True)

    def test_fixture_is_never_real_benchmark_by_default(self):
        manifest = self.make_experiment()
        with self.assertRaises(ValueError):
            report.compare(self.root, manifest)

    def test_cli_role_without_hooks_has_unknown_participation(self):
        manifest = self.make_experiment()
        result = report.compare(self.root, manifest, True)
        self.assertIsNone(result['variants']['baseline']['native_participation']['value'])
        self.assertIsNone(result['variants']['candidate']['director_invoked']['value'])



class AddedBoundaryTests(unittest.TestCase):
    def test_duration_excludes_dry_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obs.configure(root, True, "fixture")
            store = obs.Store(root)
            store.emit("run_finished", "runner", "TRACE-one", "SPAN-one", result="process_succeeded", duration_ms=20)
            store.emit("run_finished", "runner", "TRACE-two", "SPAN-two", result="dry_run", duration_ms=1000)
            health = obs.summarize(*obs.load_events(root, True))
            self.assertEqual(health["run_duration_median_ms"], 20)
            self.assertEqual(health["duration_samples"], 1)

    def test_route_and_gate_record_checks_not_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obs.configure(root, True, "fixture")
            obs.record_route(root, "feature")
            obs.record_gate(root, {"gate_id": "TEST_VERIFY_GATE", "checks_passed": True})
            events, errors = obs.load_events(root, True)
            self.assertFalse(errors)
            self.assertEqual({e["result"] for e in events}, {"plan_only", "checks_passed"})
            self.assertEqual(obs.summarize(events)["business_acceptance"], "not_evaluated")

    def test_trace_filter_is_explicit_and_fixture_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            obs.configure(root, True, "fixture")
            obs.Store(root).emit("route_reported", "runner", "TRACE-demo", "SPAN-demo", route_kind="feature")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(report.main(["--root", str(root), "--trace", "TRACE-demo"]), 2)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(report.main(["--root", str(root), "--trace", "TRACE-demo", "--include-fixtures"]), 0)
            self.assertEqual(len(json.loads(out.getvalue())["timeline"]), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
