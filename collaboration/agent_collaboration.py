#!/usr/bin/env python3
"""Candidate collaboration protocol; no version promotion or business acceptance.

The immutable journal is the execution-control source. Goal/Story/Task and
artifacts remain project-owned. Filesystem ownership is not identity auth.
"""
from __future__ import annotations
import argparse
import copy
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

# Reuse V1.3's path and atomic-write boundary in installed projects and source tests.
try:
    import harness_observe as obs
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'observability'))
    import harness_observe as obs

VERSION = 'collaboration-candidate/1'
ACTIVE = {'requested', 'running', 'applying'}
TERMINAL = {'completed', 'failed', 'blocked', 'unavailable', 'cancelled'}
ID = re.compile(r'[A-Za-z][A-Za-z0-9_.:-]{0,95}\Z')
DIGEST = re.compile(r'[0-9a-f]{64}\Z')
SENSITIVE = {'.git', '.env', '.ssh', 'credentials', 'secrets', 'auth.json', 'config.toml'}


class Fault(ValueError):
    """Fixed diagnostic codes are safe for logs; never include raw provider errors."""


def require(ok, code):
    if not ok:
        raise Fault(code)


def identifier(value):
    require(isinstance(value, str) and ID.fullmatch(value), 'INVALID_ID')
    return value


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def ref(root, name, exists=True):
    require(isinstance(name, str) and name and len(name) < 400 and not any(ord(c) < 32 or c in '|`' for c in name), 'INVALID_REF')
    require(not any(p in SENSITIVE or p.startswith('.env.') or p.endswith(('.pem', '.key')) for p in Path(name).parts), 'SENSITIVE_REF')
    try:
        p = obs.safe_path(root, name)
    except ValueError:
        raise Fault('UNSAFE_REF') from None
    require(not exists or (p.is_file() and p.stat().st_size > 0), 'MISSING_REF')
    return p


def file_hash(root, name):
    p = ref(root, name)
    require(p.stat().st_size <= 4_000_000, 'ARTIFACT_TOO_LARGE')
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(root, name):
    path = ref(root, name)
    try:
        return obs.read_json(path)
    except (OSError, ValueError):
        raise Fault('INVALID_JSON_REF') from None


def fingerprint(root, names):
    require(isinstance(names, list) and names and len(names) == len(set(names)), 'INVALID_REFS')
    return {name: file_hash(root, name) for name in names}


def current(root, hashes):
    try:
        return all(file_hash(root, name) == h for name, h in hashes.items())
    except Fault:
        return False


def overlaps(left, right):
    return any(a == b or a.startswith(b.rstrip('/') + '/') or b.startswith(a.rstrip('/') + '/') for a in left for b in right)


def protected_write(path):
    return path.split('/')[0] in ('.ai', 'schema', '.codex', '.claude', '.agents', '.git') or path in ('AGENTS.md', 'CLAUDE.md', 'WORKING_STYLE.md', 'initdir.sh', '00_AI_WARMUP.md') or path.startswith('raw/goals/')


def allowed(path, scopes):
    return any(path == s or path.startswith(s.rstrip('/') + '/') for s in scopes)


def validate_registry(registry, policy):
    require(registry.get('schema') == 'agent-capabilities/v1', 'REGISTRY_SCHEMA')
    require(policy.get('schema') == 'activation-policy/v1', 'POLICY_SCHEMA')
    roles = registry.get('roles', {})
    require(isinstance(roles, dict) and roles, 'REGISTRY_EMPTY')
    for role, entry in roles.items():
        identifier(role)
        require(set(entry) - {'skill_refs'} == {'capabilities', 'contract_ref', 'profile_ref', 'enabled', 'priority'}, 'ROLE_FIELDS')
        require(isinstance(entry.get('skill_refs', []), list), 'ROLE_SKILLS')
        require(type(entry['enabled']) is bool and type(entry['priority']) is int, 'ROLE_VALUES')
        require(isinstance(entry['capabilities'], list) and entry['capabilities'], 'ROLE_CAPABILITIES')
        for cap in entry['capabilities']:
            identifier(cap)
    nodes = policy.get('steps', [])
    names = [n['id'] for n in nodes]
    require(len(names) == len(set(names)), 'DUPLICATE_STEP')
    for node in nodes:
        require(set(node) == {'id', 'capability', 'signals', 'depends_on', 'scope_key', 'deliverable', 'phase'}, 'STEP_FIELDS')
        identifier(node['id']); identifier(node['capability']); identifier(node['deliverable'])
        require(node['phase'] in ('design', 'implementation', 'verification', 'reconcile', 'operations'), 'STEP_PHASE')
        require(all(d in names for d in node['depends_on']), 'UNKNOWN_DEPENDENCY')
    visit, done = set(), set()
    def walk(name):
        require(name not in visit, 'DEPENDENCY_CYCLE')
        if name in done:
            return
        visit.add(name)
        for dep in next(n['depends_on'] for n in nodes if n['id'] == name):
            walk(dep)
        visit.remove(name); done.add(name)
    for name in names:
        walk(name)
    return roles, nodes


def make_plan(root, context_ref, registry_ref, policy_ref):
    c, registry, policy = read(root, context_ref), read(root, registry_ref), read(root, policy_ref)
    roles, steps = validate_registry(registry, policy)
    require(set(c) - {'verification'} == {'schema', 'run_id', 'goal_ref', 'story_ref', 'task_ref', 'signals', 'signal_evidence', 'inputs', 'scopes', 'authorization_ref', 'sample_kind'}, 'CONTEXT_FIELDS')
    require(c['schema'] == 'task-context/v1', 'CONTEXT_SCHEMA')
    identifier(c['run_id'])
    require(c['sample_kind'] in ('real', 'fixture'), 'SAMPLE_KIND')
    require(isinstance(c['signals'], list) and c['signals'] and len(c['signals']) == len(set(c['signals'])), 'SIGNALS_REQUIRED')
    known = set(policy['signals'])
    require(set(c['signals']) <= known, 'UNKNOWN_SIGNAL')
    require(set(c['signal_evidence']) == set(c['signals']), 'SIGNAL_EVIDENCE_REQUIRED')
    baseline = [c[k] for k in ('goal_ref', 'story_ref', 'task_ref')] + [context_ref, registry_ref, policy_ref]
    for paths in c['signal_evidence'].values():
        require(isinstance(paths, list) and paths, 'SIGNAL_EVIDENCE_REQUIRED')
        for name in paths: ref(root, name)
    if c['sample_kind'] == 'real': ref(root, 'AGENTS.md')
    for name in ('AGENTS.md', 'WORKING_STYLE.md'):
        if (root / name).is_file(): baseline.append(name)
    anchor = fingerprint(root, list(dict.fromkeys(baseline)))
    source_hashes = fingerprint(root, list(dict.fromkeys(c['inputs'] + [p for names in c['signal_evidence'].values() for p in names])))
    require(isinstance(c['scopes'], dict), 'SCOPES_REQUIRED')
    for scope in c['scopes'].values():
        require(isinstance(scope, list), 'SCOPES_REQUIRED')
        for path in scope:
            ref(root, path, False)
            require(not protected_write(path), 'PROTECTED_WRITE_SCOPE')
    auth = read(root, c['authorization_ref'])
    require(set(auth) == {'schema', 'actor', 'at', 'confirmation_ref', 'task_refs', 'allow_delegation', 'write_paths', 'validation_commands', 'max_attempts', 'max_parallel', 'sample_kind'}, 'AUTH_FIELDS')
    require(auth['schema'] == 'collaboration-authorization/v1' and auth['allow_delegation'] is True, 'AUTH_REQUIRED')
    require(c['task_ref'] in auth['task_refs'] and auth['sample_kind'] == c['sample_kind'], 'AUTH_SCOPE')
    identifier(auth['actor']); ref(root, auth['confirmation_ref'])
    try:
        require(datetime.fromisoformat(auth['at']).tzinfo is not None, 'AUTH_TIME')
    except (TypeError, ValueError):
        raise Fault('AUTH_TIME') from None
    require(type(auth['max_attempts']) is int and 1 <= auth['max_attempts'] <= 20, 'ATTEMPT_LIMIT')
    require(type(auth['max_parallel']) is int and 1 <= auth['max_parallel'] <= 8, 'PARALLEL_LIMIT')
    require(isinstance(auth['validation_commands'], list), 'VALIDATION_COMMANDS')
    require(isinstance(auth['write_paths'], list) and all(isinstance(x,str) and x for x in auth['write_paths']), 'AUTH_WRITE_PATHS')
    for path in auth['write_paths']:
        ref(root, path, False)
        require(not protected_write(path), 'PROTECTED_WRITE_SCOPE')
    for cmd in auth['validation_commands']:
        require(isinstance(cmd, list) and cmd and all(isinstance(x, str) and x for x in cmd), 'VALIDATION_COMMAND')
    verification = c.get('verification')
    if verification is not None:
        require(isinstance(verification, dict) and set(verification) == {'tests', 'inputs', 'covers', 'command'}, 'VERIFICATION_FIELDS')
        require(verification['command'] in auth['validation_commands'], 'COMMAND_NOT_AUTHORIZED')
        for field in ('tests', 'inputs', 'covers'):
            require(isinstance(verification[field], list) and verification[field] and all(isinstance(x,str) and x for x in verification[field]), 'VERIFICATION_FIELDS')
        for path in verification['tests'] + verification['inputs']: ref(root, path, False)
        require(all(re.fullmatch(r'(?:STORY|TASK|BUG)-[A-Za-z0-9_-]+#[A-Za-z0-9_-]+', x) for x in verification['covers']), 'VERIFICATION_COVERS')
        require((root / '.ai/tools/evidence.py').is_file(), 'EVIDENCE_TOOL_REQUIRED')
        anchor.update(fingerprint(root, ['.ai/tools/evidence.py']))
    anchor.update(fingerprint(root, [c['authorization_ref'], auth['confirmation_ref']]))
    for entry in roles.values():
        if entry['enabled']:
            anchor.update(fingerprint(root, [entry['contract_ref'], entry['profile_ref']] + entry.get('skill_refs', [])))
    selected = [n for n in steps if set(n['signals']) & set(c['signals'])]
    selected_names = {n['id'] for n in selected}
    assignments, used = {}, set()
    for spec in selected:
        candidates = [(e['priority'], r) for r, e in roles.items() if e['enabled'] and spec['capability'] in e['capabilities']]
        require(candidates, 'CAPABILITY_UNAVAILABLE')
        role = sorted(candidates)[0][1]
        entry = roles[role]
        ref(root, entry['contract_ref']); ref(root, entry['profile_ref'])
        anchor.update(fingerprint(root, [entry['contract_ref'], entry['profile_ref']] + entry.get('skill_refs', [])))
        scopes = c['scopes'].get(spec['scope_key'], [])
        require(all(allowed(p, auth['write_paths']) for p in scopes), 'WRITE_NOT_AUTHORIZED')
        d = {**copy.deepcopy(spec), 'role': role, 'write_paths': scopes,
             'depends_on': [dep for dep in spec['depends_on'] if dep in selected_names],
             'status': 'proposed', 'attempt': 0, 'attempts': [], 'result_refs': [], 'reason': None,
             'profile_ref': entry['profile_ref'], 'contract_ref': entry['contract_ref'], 'skill_refs': entry.get('skill_refs', [])}
        assignments[spec['id']] = d; used.add(role)
    require(assignments, 'EMPTY_PLAN')
    protected = bool({'production', 'destructive', 'sensitive_permission'} & set(c['signals']))
    return {'schema': VERSION, 'run_id': c['run_id'], 'context_ref': context_ref, 'task_ref': c['task_ref'],
            'goal_ref': c['goal_ref'], 'story_ref': c['story_ref'], 'sample_kind': c['sample_kind'],
            'context_hash': digest(c), 'anchors': anchor, 'source_hashes': source_hashes, 'verification': verification,
            'authorization': auth, 'registry_ref': registry_ref, 'policy_ref': policy_ref,
            'mode': 'blocked' if protected else 'single_agent' if len(used) == 1 else 'collaborative',
            'matched_rules': [n['id'] for n in selected],
            'skipped_roles': {r: 'no_matching_capability' if e['enabled'] else 'project_disabled' for r, e in roles.items() if r not in used},
            'assignments': assignments, 'handoffs': {}, 'validations': [], 'finished': False,
            'sequence': 0, 'reason': 'HUMAN_APPROVAL_REQUIRED' if protected else None}


class Engine:
    def __init__(self, root, run_id):
        self.root = Path(root).resolve(); self.run_id = identifier(run_id)
        self.folder = obs.safe_path(self.root, f'.ai/collaboration/runs/{run_id}')

    @contextmanager
    def lock(self):
        obs.safe_path(self.root, str(self.folder.relative_to(self.root)))
        self.folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock_path = obs.safe_path(self.root, str((self.folder / '.lock').relative_to(self.root)))
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        with os.fdopen(fd, 'a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def history(self):
        previous, rows = None, []
        for i, path in enumerate(sorted(self.folder.glob('[0-9]*.json')), 1):
            require(not path.is_symlink() and path.name == f'{i:06}.json', 'JOURNAL_SEQUENCE')
            row = obs.read_json(path)
            require(set(row) == {'event', 'state', 'previous', 'hash'}, 'JOURNAL_FIELDS')
            require(row['previous'] == previous and row['hash'] == digest({k: row[k] for k in ('event', 'state', 'previous')}), 'JOURNAL_CORRUPT')
            require(row['event']['sequence'] == i and row['state']['sequence'] == i, 'JOURNAL_SEQUENCE')
            require(row['event']['run_id'] == self.run_id and row['state']['run_id'] == self.run_id, 'JOURNAL_ID')
            rows.append(row); previous = row['hash']
        return rows

    def load(self):
        rows = self.history()
        require(rows, 'RUN_NOT_FOUND')
        return copy.deepcopy(rows[-1]['state'])

    def append(self, state, event_type, delegation=None, handoff=None, before=None, after=None, source='system', verification='not_applicable', reason=None, evidence=None, instance_ref=None):
        rows = self.history(); seq = len(rows) + 1
        require(state['sequence'] == seq - 1, 'CONCURRENT_UPDATE')
        for value in (event_type, source, verification, reason):
            if value is not None:
                identifier(value)
        state['sequence'] = seq
        event = {'schema_version': '1.0', 'event_id': f'EVT-{seq:06}', 'sequence': seq,
                 'event_type': event_type, 'occurred_at': obs.now(), 'run_id': self.run_id,
                 'work_item_ref': state['task_ref'], 'trace_id': self.run_id,
                 'delegation_id': delegation, 'agent_instance_ref': None, 'handoff_id': handoff,
                 'actor_type': 'runtime' if source == 'codex_app_server' else 'system', 'source_kind': source,
                 'causation_id': f'EVT-{seq-1:06}' if seq > 1 else None, 'correlation_id': delegation or self.run_id,
                 'state_before': before, 'state_after': after, 'verification_status': verification,
                 'evidence_refs': evidence or [], 'artifact_refs': [], 'payload': {'reason': reason}, 'sample_kind': state['sample_kind']}
        if handoff and handoff in state['handoffs'] and state['handoffs'][handoff].get('review'):
            event['agent_instance_ref'] = state['handoffs'][handoff]['review']['receipt']['instance_ref']
        elif delegation and delegation in state['assignments']:
            attempts = state['assignments'][delegation]['attempts']
            if attempts:
                event['agent_instance_ref'] = attempts[-1].get('instance_ref')
        if instance_ref is not None:
            event['agent_instance_ref'] = identifier(instance_ref)
        row = {'event': event, 'state': state, 'previous': rows[-1]['hash'] if rows else None}
        row['hash'] = digest(row)
        obs.atomic_json(self.folder / f'{seq:06}.json', row)
        # Optional V1.3 bridge: use a dedicated metadata event, never invent native Hook events.
        try:
            store = obs.Store(self.root)
            if store.enabled and store.config['sample_kind'] == state['sample_kind']:
                store.emit('collaboration_transition', 'collaboration', self.run_id, delegation or self.run_id,
                           dedupe_key=f'{self.run_id}:{seq}', run_id=self.run_id,
                           reason=event_type, result=after, execution_mode='protocol',
                           role=state['assignments'][delegation]['role'] if delegation else None)
        except (ValueError, OSError):
            print('OBSERVABILITY_BRIDGE_GAP', file=sys.stderr)
        return event

    def create(self, context_ref, registry_ref='schema/collaboration/registry.json', policy_ref='schema/collaboration/policy.json'):
        state = make_plan(self.root, context_ref, registry_ref, policy_ref)
        require(state['run_id'] == self.run_id, 'RUN_ID_MISMATCH')
        with self.lock():
            require(not self.history(), 'RUN_EXISTS')
            base = obs.safe_path(self.root, '.ai/collaboration/.gitignore')
            if not base.exists():
                base.write_text('*\n', encoding='utf-8')
            require(base.read_text().strip() == '*', 'PRIVATE_IGNORE_CHANGED')
            self.append(state, 'TASK_CLASSIFIED', after=state['mode'])
            for name, item in state['assignments'].items():
                self.append(state, 'AGENT_ACTIVATION_PROPOSED', name, after='proposed')
            if state['mode'] == 'blocked':
                self.append(state, 'HUMAN_APPROVAL_REQUESTED', after='blocked', reason=state['reason'])
        return state

    def freshness(self, s):
        require(current(self.root, s['anchors']), 'CONTEXT_DRIFT')
        require(current(self.root, s['source_hashes']), 'SOURCE_DRIFT')

    def dependency_handoffs(self, s, name):
        latest = []
        for dep in s['assignments'][name]['depends_on']:
            require(s['assignments'][dep]['status'] == 'completed', 'DEPENDENCY_INCOMPLETE')
            candidates = [h for h in s['handoffs'].values() if h['from_delegation'] == dep and h['to_delegation'] == name]
            require(candidates, 'HANDOFF_REQUIRED')
            h = max(candidates, key=lambda x: x['revision'])
            require(h['status'] == 'accepted', 'HANDOFF_NOT_ACCEPTED')
            require(current(self.root, h['artifacts']), 'ARTIFACT_DRIFT')
            require(h['from_attempt'] == s['assignments'][dep]['attempt'], 'HANDOFF_SUPERSEDED')
            latest.append(h['handoff_id'])
        return latest

    def ready(self):
        s = self.load()
        if s['mode'] == 'blocked' or s['finished']:
            return []
        self.freshness(s)
        ready = []
        for name, d in s['assignments'].items():
            if d['status'] not in ('proposed', 'queued'):
                continue
            try:
                self.dependency_handoffs(s, name)
                active = [x for x in s['assignments'].values() if x['status'] in ACTIVE]
                require(len(active) < s['authorization']['max_parallel'], 'RESOURCE_LIMIT')
                require(not any(overlaps(d['write_paths'], x['write_paths']) for x in active), 'WRITE_CONFLICT')
                ready.append(name)
            except Fault:
                continue
        return ready

    def packet(self, s, name, review=None):
        d = s['assignments'][name]
        refs = [x for x in ('AGENTS.md','WORKING_STYLE.md') if x in s['anchors']] + d.get('skill_refs', []) + [s['goal_ref'], s['story_ref'], s['task_ref'], d['profile_ref'], d['contract_ref']] + list(s['source_hashes'])
        for h in s['handoffs'].values():
            if h['to_delegation'] == name:
                refs.extend(h['artifacts'])
        # Context is sent to the authorized engine, never persisted as chat logs.
        docs = []
        for name_ref in dict.fromkeys(refs):
            p = ref(self.root, name_ref)
            require(p.stat().st_size <= 128000, 'CONTEXT_TOO_LARGE')
            docs.append({'ref': name_ref, 'sha256': file_hash(self.root, name_ref), 'text': p.read_text(errors='replace')})
        require(sum(len(x['text']) for x in docs) <= 500000, 'CONTEXT_TOO_LARGE')
        return {'run_id': self.run_id, 'delegation_id': name, 'attempt': d['attempt'], 'role': d['role'],
                'capability': d['capability'], 'phase': 'handoff_review' if review else d['phase'],
                'deliverable': d['deliverable'], 'write_paths': [] if review else d['write_paths'],
                'context_hash': s['context_hash'], 'documents': docs, 'review': review,
                'limitations': ['No production/database operations', 'No delegation or external side effects',
                                'Return scoped file changes; never claim tests ran without tool evidence']}

    def dispatch(self, name, adapter):
        identifier(name)
        with self.lock():
            s = self.load(); require(name in s['assignments'], 'UNKNOWN_DELEGATION')
            d = s['assignments'][name]
            require(s['mode'] != 'blocked' and not s['finished'], 'RUN_BLOCKED')
            self.freshness(s)
            require(re.search(r'^status:[ \t]*approved[ \t]*$', ref(self.root, s['goal_ref']).read_text(), re.MULTILINE), 'GOAL_NOT_APPROVED')
            require(name in self.ready(), 'NOT_READY')
            if d['phase'] == 'implementation' and s['mode'] != 'single_agent':
                require(s['verification'] is not None or s['sample_kind'] == 'fixture', 'TDD_BINDING_REQUIRED')
                if s['verification'] is not None:
                    require(self.tdd_status(s)['red_current'], 'CURRENT_RED_REQUIRED')
                    require(not overlaps(d['write_paths'], s['verification']['tests']), 'IMPLEMENTER_TEST_WRITE_DENIED')
            if d['phase'] == 'verification' and s['verification'] is not None:
                require(self.tdd_status(s)['green_current'], 'CURRENT_GREEN_REQUIRED')
            require(d['attempt'] < s['authorization']['max_attempts'], 'RETRY_LIMIT')
            require(adapter.sample_kind == s['sample_kind'], 'FIXTURE_REAL_MISMATCH')
            if s['sample_kind'] == 'real':
                from codex_adapter import CodexAdapter
                require(type(adapter) is CodexAdapter and adapter.transport is None, 'UNTRUSTED_ADAPTER')
            packet = self.packet(s, name)
            read_snapshot = {x['ref']: x['sha256'] for x in packet['documents']}
            d['status'] = 'queued'
            self.append(s, 'AGENT_QUEUED', name, before='proposed', after='queued')
            d['attempt'] += 1
            key = digest([self.run_id, name, d['attempt'], s['context_hash']])
            d['attempts'].append({'attempt': d['attempt'], 'idempotency_key': key, 'status': 'requested',
                                  'instance_ref': None, 'execution_mode': adapter.mode, 'start_evidence': None,
                                  'started_at': None, 'ended_at': None, 'duration_ms': None, 'usage': None})
            d['status'] = 'requested'
            self.append(s, 'AGENT_INVOCATION_REQUESTED', name, before='queued', after='requested')
            packet['attempt'] = d['attempt']
        started = time.monotonic()
        def on_start(receipt):
            require(set(receipt) == {'instance_ref', 'request_ref', 'source', 'sample_kind'}, 'RECEIPT_FIELDS')
            require(receipt['source'] == adapter.source and receipt['sample_kind'] == adapter.sample_kind, 'RECEIPT_SOURCE')
            identifier(receipt['instance_ref']); identifier(receipt['request_ref'])
            with self.lock():
                state = self.load(); node = state['assignments'][name]; attempt = node['attempts'][-1]
                require(attempt['idempotency_key'] == key, 'LATE_CALLBACK')
                if node['status'] == 'running':
                    require(attempt['instance_ref'] == receipt['instance_ref'], 'CONFLICTING_RECEIPT')
                    return
                require(node['status'] == 'requested', 'LATE_CALLBACK')
                all_instances = [a['instance_ref'] for n in state['assignments'].values() for a in n['attempts'] if a['instance_ref']]
                require(receipt['instance_ref'] not in all_instances, 'REUSED_INSTANCE')
                attempt.update(instance_ref=receipt['instance_ref'], start_evidence=receipt, started_at=obs.now(), status='running')
                node['status'] = 'running'
                self.append(state, 'AGENT_STARTED', name, before='requested', after='running', source=adapter.source,
                            verification='verified' if adapter.sample_kind == 'real' else 'unverified')
        try:
            result = adapter.run(packet, on_start)
            require(set(result) == {'changes', 'artifacts', 'outcome', 'usage', 'assistance'}, 'RESULT_FIELDS')
            if result['outcome'] == 'needs_assistance':
                request = result['assistance']
                require(not result['changes'] and not result['artifacts'], 'ASSISTANCE_MUST_NOT_WRITE')
                require(isinstance(request, dict) and set(request) == {'capability', 'evidence_refs', 'write_paths'}, 'ASSISTANCE_FIELDS')
                with self.lock():
                    state = self.load(); node = state['assignments'][name]
                    require(node['status'] == 'running', 'START_RECEIPT_MISSING')
                    node['status'] = 'blocked'; node['reason'] = 'PROFESSIONAL_ASSISTANCE_REQUEST'
                    node['attempts'][-1].update(status='blocked', ended_at=obs.now(), duration_ms=round((time.monotonic()-started)*1000))
                    self.append(state, 'ASSISTANCE_PROPOSED', name, before='running', after='blocked', source='agent_report', verification='reported')
                self.assist(name, request['capability'], request['evidence_refs'], request['write_paths'])
                return self.load()['assignments'][name]
            with self.lock():
                s = self.load(); d = s['assignments'][name]
                require(d['status'] == 'running' and d['attempts'][-1]['idempotency_key'] == key, 'START_RECEIPT_MISSING')
                self.freshness(s); self.dependency_handoffs(s, name)
                require(current(self.root, read_snapshot), 'EXECUTION_INPUT_DRIFT')
                require(result['assistance'] is None, 'UNEXPECTED_ASSISTANCE')
                require(result['outcome'] == 'completed', 'EXECUTION_FAILED')
                require(isinstance(result['changes'], list) and isinstance(result['artifacts'], list), 'RESULT_FIELDS')
                require(result['changes'] or result['artifacts'], 'RESULT_ARTIFACTS_REQUIRED')
                staged = []
                for change in result['changes']:
                    require(set(change) == {'path', 'base_sha256', 'content'}, 'CHANGE_FIELDS')
                    p = ref(self.root, change['path'], False)
                    require(allowed(change['path'], d['write_paths']), 'WRITE_NOT_AUTHORIZED')
                    require(not any(change['path'] == old[0] for old in staged), 'DUPLICATE_CHANGE')
                    actual = file_hash(self.root, change['path']) if p.exists() else None
                    require(actual == change['base_sha256'], 'WRITE_BASE_DRIFT')
                    require(isinstance(change['content'], str) and 0 < len(change['content']) <= 128000, 'CHANGE_TOO_LARGE')
                    staged.append((change['path'], change['content']))
                d['status'] = 'applying'
                self.append(s, 'ARTIFACT_APPLY_STARTED', name, before='running', after='applying')
                for path, content in staged:
                    target = ref(self.root, path, False); target.parent.mkdir(parents=True, exist_ok=True)
                    # Atomic individual replacement; recovery blocks an interrupted batch.
                    temp = target.with_name('.ans-' + uuid.uuid4().hex)
                    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    if target.exists(): os.fchmod(fd, target.stat().st_mode & 0o777)
                    try:
                        with os.fdopen(fd, 'w') as out:
                            out.write(content); out.flush(); os.fsync(out.fileno())
                        os.replace(temp, target)
                    finally:
                        if temp.exists(): temp.unlink()
                artifacts = list(dict.fromkeys([p for p, _ in staged] + result['artifacts']))
                hashes = fingerprint(self.root, artifacts)
                for path, h in hashes.items():
                    archive = obs.safe_path(self.root, f'.ai/collaboration/artifacts/{h}')
                    archive.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    try:
                        fd = os.open(archive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                        with os.fdopen(fd, 'wb') as out: out.write(ref(self.root, path).read_bytes())
                    except FileExistsError:
                        require(hashlib.sha256(archive.read_bytes()).hexdigest() == h, 'ARCHIVE_CORRUPT')
                for path, _ in staged:
                    s['source_hashes'][path] = hashes[path]
                d['result_refs'] = hashes; d['status'] = 'completed'; d['reason'] = None
                a = d['attempts'][-1]
                # Accept only numeric standardized usage, never free-form provider values.
                usage = result['usage']
                if not isinstance(usage, dict) or set(usage) != {'input_tokens', 'output_tokens'} or not all(type(v) is int and v >= 0 for v in usage.values()):
                    usage = None
                a.update(status='completed', ended_at=obs.now(), duration_ms=round((time.monotonic()-started)*1000), usage=usage)
                self.append(s, 'AGENT_RESULT_SUBMITTED', name, before='applying', after='completed', evidence=list(hashes))
                return copy.deepcopy(d)
        except (Fault, OSError, TimeoutError, ValueError) as exc:
            code = str(exc) if isinstance(exc, Fault) and ID.fullmatch(str(exc)) else 'ADAPTER_ERROR'
            with self.lock():
                s = self.load(); d = s['assignments'][name]
                if d['attempts'][-1]['idempotency_key'] == key and d['status'] not in ('cancelled',):
                    before = d['status']; d['status'] = 'unavailable' if code == 'RUNTIME_UNAVAILABLE' else 'failed'; d['reason'] = code
                    d['attempts'][-1].update(status=d['status'], ended_at=obs.now(), duration_ms=round((time.monotonic()-started)*1000))
                    self.append(s, 'AGENT_UNAVAILABLE' if code == 'RUNTIME_UNAVAILABLE' else 'AGENT_FAILED', name, before=before, after=d['status'], reason=code)
            raise Fault(code) from None

    def submit(self, sender, receiver):
        try:
            return self._submit(sender, receiver)
        except Fault as exc:
            with self.lock():
                s = self.load()
                self.append(s, 'HANDOFF_INVALID', sender if sender in s['assignments'] else None,
                            after='blocked', reason=str(exc))
            raise

    def _submit(self, sender, receiver):
        with self.lock():
            s = self.load(); self.freshness(s)
            require(sender in s['assignments'] and receiver in s['assignments'], 'UNKNOWN_DELEGATION')
            d = s['assignments'][sender]
            require(sender in s['assignments'][receiver]['depends_on'], 'NOT_AN_EDGE')
            require(d['status'] == 'completed' and current(self.root, d['result_refs']), 'RESULT_NOT_CURRENT')
            old = [h for h in s['handoffs'].values() if h['from_delegation'] == sender and h['to_delegation'] == receiver]
            old.sort(key=lambda h: h['revision'])
            if old and old[-1]['from_attempt'] == d['attempt'] and old[-1]['status'] in ('submitted', 'accepted'):
                return old[-1]  # stable repeated submit
            revision = len(old) + 1; hid = f'HO-{sender}-{receiver}-{revision}'
            h = {'schema': 'collaboration-handoff/v1', 'handoff_id': hid, 'revision': revision,
                 'supersedes': old[-1]['handoff_id'] if old else None, 'run_id': self.run_id,
                 'work_item_ref': s['task_ref'], 'from_delegation': sender, 'to_delegation': receiver,
                 'from_actor': d['attempts'][-1]['instance_ref'], 'to_actor': s['assignments'][receiver]['role'],
                 'base_ref': 'sha256:' + digest(s['source_hashes']), 'from_attempt': d['attempt'], 'context_hash': s['context_hash'], 'artifacts': d['result_refs'],
                 'objective_ref': s['task_ref'], 'acceptance_criteria_refs': [s['story_ref']],
                 'constraints_ref': s['authorization']['confirmation_ref'], 'decisions': [], 'open_issues': [], 'risks': [],
                 'checks': [], 'evidence_refs': list(d['result_refs']), 'required_reviewers': [s['assignments'][receiver]['role']],
                 'next_actions': [receiver], 'status': 'submitted', 'created_at': obs.now(), 'review': None}
            s['handoffs'][hid] = h
            self.append(s, 'HANDOFF_SUBMITTED', sender, hid, after='submitted', evidence=h['evidence_refs'])
            return copy.deepcopy(h)

    def review(self, hid, adapter):
        with self.lock():
            s = self.load(); require(hid in s['handoffs'], 'UNKNOWN_HANDOFF')
            h = s['handoffs'][hid]
            require(h['status'] == 'submitted', 'HANDOFF_NOT_SUBMITTED')
            try:
                self.freshness(s)
            except Fault as exc:
                h['status'] = 'changes_requested'
                self.append(s, 'HANDOFF_CHANGES_REQUESTED', h['to_delegation'], hid, before='submitted', after='changes_requested', reason=str(exc))
                raise
            if not current(self.root, h['artifacts']):
                h['status'] = 'changes_requested'
                self.append(s, 'HANDOFF_CHANGES_REQUESTED', h['to_delegation'], hid, after='changes_requested', reason='ARTIFACT_DRIFT')
                raise Fault('ARTIFACT_DRIFT')
            require(adapter.sample_kind == s['sample_kind'], 'FIXTURE_REAL_MISMATCH')
            if s['sample_kind'] == 'real':
                from codex_adapter import CodexAdapter
                require(type(adapter) is CodexAdapter and adapter.transport is None, 'UNTRUSTED_ADAPTER')
            packet = self.packet(s, h['to_delegation'], review=h)
            before_hash = digest(h)
            self.append(s, 'REVIEW_INVOCATION_REQUESTED', h['to_delegation'], hid, source='system')
        receipts = []
        def start(receipt):
            require(set(receipt) == {'instance_ref', 'request_ref', 'source', 'sample_kind'}, 'RECEIPT_FIELDS')
            require(receipt['source'] == adapter.source and receipt['sample_kind'] == adapter.sample_kind, 'RECEIPT_SOURCE')
            identifier(receipt['instance_ref']); identifier(receipt['request_ref'])
            require(receipt['instance_ref'] != h['from_actor'], 'SELF_REVIEW')
            if receipts:
                require(receipts[0] == receipt, 'CONFLICTING_RECEIPT')
                return
            receipts.append(receipt)
            with self.lock():
                state = self.load()
                self.append(state, 'REVIEW_STARTED', h['to_delegation'], hid, source=adapter.source,
                            verification='verified' if adapter.sample_kind == 'real' else 'unverified', instance_ref=receipt['instance_ref'])
        try:
            answer = adapter.review(packet, start)
            require(receipts, 'START_RECEIPT_MISSING')
            review_fields = {'decision', 'reason_code', 'evidence_refs'}
            require(isinstance(answer, dict) and set(answer) in (review_fields, review_fields | {'usage'}), 'REVIEW_FIELDS')
            # Legacy/fixture adapters may not report usage. Unknown is not zero.
            review_usage = answer.get('usage')
            require(review_usage is None or (
                isinstance(review_usage, dict)
                and set(review_usage) == {'input_tokens', 'output_tokens'}
                and all(type(v) is int and v >= 0 for v in review_usage.values())
            ), 'REVIEW_USAGE_INVALID')
            require(answer['decision'] in ('accepted', 'changes_requested', 'rejected'), 'REVIEW_DECISION')
            identifier(answer['reason_code'])
            refs = answer['evidence_refs']
            require(isinstance(refs, list) and bool(refs)
                    and all(isinstance(ref, str) and bool(ref) for ref in refs)
                    and len(refs) == len(set(refs))
                    and set(refs) >= set(h['artifacts']), 'REVIEW_EVIDENCE_REQUIRED')
            with self.lock():
                s = self.load(); live = s['handoffs'][hid]
                require(digest(live) == before_hash, 'REVIEW_CONCURRENT_CHANGE')
                self.freshness(s); require(current(self.root, h['artifacts']), 'ARTIFACT_DRIFT')
                proof = fingerprint(self.root, answer['evidence_refs'])
                live['status'] = answer['decision']
                live['review'] = {**{k: answer[k] for k in review_fields}, 'usage': review_usage,
                                  'receipt': receipts[0], 'evidence_hashes': proof,
                                  'at': obs.now(), 'independence': 'independent_instance'}
                self.append(s, 'HANDOFF_' + answer['decision'].upper(), h['to_delegation'], hid, before='submitted', after=answer['decision'], source=adapter.source,
                            verification='verified' if adapter.sample_kind == 'real' else 'unverified', reason=answer['reason_code'], evidence=list(proof))
                return live
        except (Fault, ValueError, OSError, TimeoutError):
            with self.lock():
                s = self.load()
                self.append(s, 'REVIEW_FAILED', h['to_delegation'], hid, reason='REVIEW_NOT_VERIFIED')
            raise

    def retry(self, name, reason='RETRY_REQUESTED'):
        identifier(reason)
        with self.lock():
            s = self.load(); require(name in s['assignments'], 'UNKNOWN_DELEGATION')
            d = s['assignments'][name]
            require(d['status'] not in ACTIVE | {'applying', 'cancelled'}, 'RETRY_ACTIVE_OR_CANCELLED')
            # A recovered in-flight attempt may have executed external effects
            # before its acknowledgement was persisted. A blind replay can
            # duplicate those effects, even if the original receipt is missing.
            # Require a separately reviewed reconciliation/new run instead.
            require(d.get('reason') != 'INTERRUPTED_RECONCILE_REQUIRED',
                    'INTERRUPTED_RECONCILIATION_REQUIRED')
            require(s['mode'] != 'blocked', 'RUN_BLOCKED')
            if d.get('reason') == 'INTERRUPTED_RECONCILED_NO_EFFECTS':
                proof = d.get('reconciliation')
                require(proof is not None, 'RECONCILIATION_REQUIRED')
                require(d.get('reason') == 'INTERRUPTED_RECONCILED_NO_EFFECTS'
                        and proof['disposition'] == 'retry'
                        and proof['observed_effects'] == 'none_observed'
                        and proof['attempt'] == d['attempt']
                        and current(self.root, proof['evidence_hashes']),
                        'RECONCILIATION_STALE_OR_UNSAFE')
            require(d['attempt'] < s['authorization']['max_attempts'], 'RETRY_LIMIT')
            affected = {name}
            while True:
                added = {n for n, x in s['assignments'].items() if set(x['depends_on']) & affected}
                if added <= affected: break
                affected |= added
            require(not any(s['assignments'][n]['status'] in ACTIVE | {'applying'} for n in affected), 'ACTIVE_DOWNSTREAM')
            for n in affected:
                s['assignments'][n]['status'] = 'proposed'; s['assignments'][n]['reason'] = reason
            for h in s['handoffs'].values():
                if h['from_delegation'] in affected or h['to_delegation'] in affected:
                    h['status'] = 'superseded'
            s['validations'] = [{**v, 'current': False} for v in s['validations']]
            s['finished'] = False
            self.append(s, 'DEPENDENCIES_INVALIDATED', name, after='proposed', reason=reason)
            return sorted(affected)

    def assist(self, requester, capability, evidence_refs, write_paths):
        identifier(capability)
        with self.lock():
            s = self.load(); self.freshness(s)
            require(requester in s['assignments'], 'UNKNOWN_DELEGATION')
            require(s['assignments'][requester]['status'] not in ACTIVE | {'applying'}, 'ASSIST_REQUIRES_PAUSED_TASK')
            proof = fingerprint(self.root, evidence_refs)
            roles = read(self.root, s['registry_ref'])['roles']
            choices = sorted((e['priority'], r) for r, e in roles.items() if e['enabled'] and capability in e['capabilities'])
            require(choices, 'CAPABILITY_UNAVAILABLE')
            role = choices[0][1]; entry = roles[role]
            key = 'assist-' + digest([requester, capability, proof])[:16]
            if key in s['assignments']:
                return key
            require(all(allowed(p, s['authorization']['write_paths']) for p in write_paths), 'WRITE_NOT_AUTHORIZED')
            for p in write_paths:
                ref(self.root, p, False)
                require(not protected_write(p), 'PROTECTED_WRITE_SCOPE')
            for p in (entry['contract_ref'], entry['profile_ref']):
                require(p in s['anchors'], 'NEW_ROLE_REPLAN_REQUIRED')
            affected = {requester}
            while True:
                extra = {n for n,x in s['assignments'].items() if set(x['depends_on']) & affected}
                if extra <= affected: break
                affected |= extra
            require(not any(s['assignments'][n]['status'] in ACTIVE | {'applying'} for n in affected), 'ACTIVE_DOWNSTREAM')
            for n in affected:
                s['assignments'][n]['status'] = 'proposed'
            for h in s['handoffs'].values():
                if h['from_delegation'] in affected or h['to_delegation'] in affected: h['status'] = 'superseded'
            s['validations'] = [{**v, 'current': False} for v in s['validations']]
            s['assignments'][key] = {'id': key, 'role': role, 'capability': capability, 'signals': [], 'phase': 'design',
                'scope_key': 'assistance', 'deliverable': capability, 'write_paths': write_paths, 'depends_on': [],
                'status': 'proposed', 'attempt': 0, 'attempts': [], 'result_refs': [], 'reason': None,
                'profile_ref': entry['profile_ref'], 'contract_ref': entry['contract_ref'], 'skill_refs': entry.get('skill_refs', [])}
            s['assignments'][requester]['depends_on'].append(key)
            s['assignments'][requester]['status'] = 'proposed'; s['finished'] = False
            self.append(s, 'ASSISTANCE_REQUESTED', key, after='proposed', evidence=list(proof))
            return key

    def recover(self):
        with self.lock():
            s = self.load(); changed = []
            for name, d in s['assignments'].items():
                if d['status'] in ACTIVE | {'applying'}:
                    before = d['status']; d['status'] = 'blocked'; d['reason'] = 'INTERRUPTED_RECONCILE_REQUIRED'
                    d['attempts'][-1]['status'] = 'blocked'
                    self.append(s, 'AGENT_BLOCKED', name, before=before, after='blocked', reason=d['reason']); changed.append(name)
            return changed


    def reconcile(self, name, record_ref):
        """Record independent side-effect inspection; never execute a retry here.

        The contract records a named review; local JSON does not authenticate
        the human's identity or prove that external side effects are absent.
        """
        identifier(name)
        with self.lock():
            s = self.load()
            require(name in s['assignments'], 'UNKNOWN_DELEGATION')
            d = s['assignments'][name]
            require(d['status'] == 'blocked' and d.get('reason') == 'INTERRUPTED_RECONCILE_REQUIRED',
                    'RECONCILIATION_NOT_REQUIRED')
            require(d.get('reconciliation') is None, 'RECONCILIATION_ALREADY_RECORDED')
            require(not s['finished'], 'RUN_FINISHED')
            require(not any(n != name and x['status'] in ACTIVE | {'applying'}
                            for n, x in s['assignments'].items()), 'ACTIVE_DOWNSTREAM')
            record = read(self.root, record_ref)
            require(set(record) == {'schema', 'run_id', 'step', 'attempt',
                                    'blocked_event_id', 'proposer', 'reviewer',
                                    'observed_effects', 'disposition',
                                    'reason', 'confirmation_ref', 'evidence_refs'},
                    'RECONCILIATION_FIELDS')
            require(record['schema'] == 'collaboration-reconciliation/v1', 'RECONCILIATION_SCHEMA')
            require(record['run_id'] == self.run_id and record['step'] == name
                    and type(record['attempt']) is int and record['attempt'] == d['attempt'],
                    'RECONCILIATION_ATTEMPT')
            identifier(record['proposer'])
            identifier(record['reviewer'])
            require(record['reviewer'] != record['proposer'], 'RECONCILIATION_SELF_REVIEW')
            rows = self.history()
            blocked = [row['event'] for row in rows
                       if row['event']['event_type'] == 'AGENT_BLOCKED'
                       and row['event']['delegation_id'] == name
                       and row['event']['payload']['reason'] == 'INTERRUPTED_RECONCILE_REQUIRED']
            require(blocked and record['blocked_event_id'] == blocked[-1]['event_id'],
                    'RECONCILIATION_EVENT_MISMATCH')
            require(record['observed_effects'] in ('none_observed', 'present', 'unknown'),
                    'RECONCILIATION_EFFECTS')
            require(record['disposition'] in ('retry', 'new_run_or_manual_resolution'),
                    'RECONCILIATION_DISPOSITION')
            safe_retry = (record['observed_effects'] == 'none_observed'
                          and record['disposition'] == 'retry')
            require(not (record['disposition'] == 'retry' and not safe_retry),
                    'RECONCILIATION_UNSAFE_RETRY')
            require(isinstance(record['reason'], str)
                    and len(record['reason'].strip()) >= 24, 'RECONCILIATION_REASON')
            require(record['confirmation_ref'] != s['authorization']['confirmation_ref'],
                    'RECONCILIATION_REUSED_AUTHORIZATION')
            proof_refs = record['evidence_refs']
            require(isinstance(proof_refs, list) and proof_refs
                    and len(proof_refs) == len(set(proof_refs))
                    and record['confirmation_ref'] not in proof_refs,
                    'RECONCILIATION_EVIDENCE_REQUIRED')
            proof = fingerprint(self.root, [record_ref, record['confirmation_ref']] + proof_refs)
            if safe_retry:
                require(s['mode'] != 'blocked', 'RUN_BLOCKED')
                self.freshness(s)
                require(d['attempt'] < s['authorization']['max_attempts'],
                        'RETRY_LIMIT')
                d['reason'] = 'INTERRUPTED_RECONCILED_NO_EFFECTS'
            d['reconciliation'] = {
                'attempt': d['attempt'], 'record_ref': record_ref,
                'observed_effects': record['observed_effects'],
                'disposition': record['disposition'],
                'evidence_hashes': proof,
                'blocked_event_id': record['blocked_event_id'],
                'identity_authentication': 'not_verified_by_local_contract'}
            self.append(s, 'SIDE_EFFECT_RECONCILIATION_RECORDED', name,
                        before='blocked', after='blocked', source='human_record',
                        verification='reported', evidence=list(proof),
                        reason='NO_EFFECTS_RETRY_ELIGIBLE' if safe_retry
                               else 'NEW_RUN_OR_MANUAL_RESOLUTION_REQUIRED')
            return {'schema': 'collaboration-reconciliation-result/v1',
                    'run_id': self.run_id, 'step': name,
                    'retry_eligible': safe_retry,
                    'execution': 'not_started',
                    'identity_authentication': 'not_verified_by_local_contract'}

    def cancel(self, confirmation_ref):
        file_hash(self.root, confirmation_ref)
        with self.lock():
            s = self.load()
            require(not any(d['status'] in ACTIVE | {'applying'} for d in s['assignments'].values()), 'INTERRUPT_RUNTIME_FIRST')
            for d in s['assignments'].values():
                if d['status'] != 'completed': d['status'] = 'cancelled'
            s['finished'] = True; s['reason'] = 'HUMAN_CANCELLED'
            self.append(s, 'HUMAN_APPROVAL_RESOLVED', after='cancelled', source='human_record', verification='reported', evidence=[confirmation_ref])

    def evidence_module(self, state):
        require(state['verification'] is not None, 'TDD_BINDING_REQUIRED')
        path = ref(self.root, '.ai/tools/evidence.py')
        require(file_hash(self.root, '.ai/tools/evidence.py') == state['anchors']['.ai/tools/evidence.py'], 'EVIDENCE_TOOL_DRIFT')
        spec = importlib.util.spec_from_file_location('_ans_existing_evidence_' + digest(str(self.root))[:12], path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def tdd_status(self, state=None):
        s = state or self.load(); binding = s['verification']
        if binding is None:
            return {'red_current': False, 'green_current': False, 'status': 'not_configured'}
        module = self.evidence_module(s)
        task = Path(s['task_ref']).stem.split('_')[0]
        require(re.fullmatch(r'TASK-[A-Za-z0-9-]+', task), 'EVIDENCE_TASK_ID')
        try:
            records = module.records(self.root, task)
            hashes = module.digest_inputs(self.root, binding['tests'])
            reds = [r for r in records if r.get('phase') == 'red' and r.get('valid') is True
                    and r.get('command') == binding['command'] and set(binding['covers']) <= set(r.get('covers', []))
                    and {t['path']:t['sha256'] for t in r.get('tests', [])} == hashes
                    and file_hash(self.root, r['log'])]
            green, detail, record = module.green_state(self.root, task)
            green_ok = green == 'CURRENT' and record.get('command') == binding['command'] and set(binding['covers']) <= set(record.get('covers', []))
            if green_ok: file_hash(self.root, record['log'])
            return {'red_current': bool(reds), 'green_current': bool(green_ok), 'status': green,
                    'red_log_ref': reds[-1]['log'] if reds else None,
                    'green_log_ref': record.get('log') if record else None}
        except (KeyError, OSError, ValueError, TypeError):
            raise Fault('EVIDENCE_INVALID') from None

    def record_tdd(self, phase):
        require(phase in ('red', 'green'), 'EVIDENCE_PHASE')
        with self.lock():
            s = self.load(); self.freshness(s)
            require(not any(d['status'] in ACTIVE | {'applying'} for d in s['assignments'].values()), 'VALIDATION_DURING_WRITE')
            binding = s['verification']; require(binding is not None, 'TDD_BINDING_REQUIRED')
            require(binding['command'] in s['authorization']['validation_commands'], 'COMMAND_NOT_AUTHORIZED')
            self.evidence_module(s)
            task = Path(s['task_ref']).stem.split('_')[0]
            # The existing recorder owns RED/GREEN truth and writes the original evidence.
            argv = [sys.executable, '.ai/tools/evidence.py', 'run', '--task', task, '--phase', phase,
                    '--tests', *binding['tests'], '--covers', *binding['covers'], '--inputs', *binding['inputs'], '--', *binding['command']]
            self.append(s, 'VALIDATION_REQUESTED', after='requested', reason='TDD_' + phase.upper())
            try:
                process = subprocess.run(argv, cwd=self.root, capture_output=True, timeout=120)
                code = process.returncode
            except (OSError, subprocess.TimeoutExpired):
                code = None
            status = self.tdd_status(s)
            ok = code == 0 and status[phase + '_current']
            log = status.get(phase + '_log_ref')
            self.append(s, 'VALIDATION_RECORDED', after='passed' if ok else 'failed', source='test_runner',
                        verification='verified', reason='TDD_' + phase.upper(), evidence=[log] if log else [])
            require(ok, 'TDD_' + phase.upper() + '_FAILED')
            return status

    def validate(self, argv):
        with self.lock():
            s = self.load(); self.freshness(s)
            require(argv in s['authorization']['validation_commands'], 'COMMAND_NOT_AUTHORIZED')
            require(not any(d['status'] in ACTIVE | {'applying'} for d in s['assignments'].values()), 'VALIDATION_DURING_WRITE')
            artifacts = {p: h for d in s['assignments'].values() for p, h in dict(d['result_refs']).items()}
            require(artifacts and current(self.root, artifacts), 'VALIDATION_STALE')
            self.append(s, 'VALIDATION_REQUESTED', after='requested')
            start = time.monotonic()
            try:
                p = subprocess.run(argv, cwd=self.root, capture_output=True, timeout=120)
                code, stdout, stderr = p.returncode, p.stdout, p.stderr
            except (subprocess.TimeoutExpired, OSError):
                code, stdout, stderr = None, b'', b''
            require(current(self.root, artifacts), 'VALIDATION_MUTATED_INPUTS')
            v = {'command_sha256': digest(argv), 'exit_code': code, 'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr),
                 'artifact_hashes': artifacts, 'at': obs.now(), 'duration_ms': round((time.monotonic()-start)*1000), 'current': True}
            s['validations'].append(v)
            self.append(s, 'VALIDATION_RECORDED', after='passed' if code == 0 else 'failed', source='test_runner', verification='verified')
            return v

    def check(self, release=False):
        s = self.load(); findings = []
        try: self.freshness(s)
        except Fault as e: findings.append(str(e))
        if s['mode'] == 'blocked': findings.append('HUMAN_APPROVAL_REQUIRED')
        for name, d in s['assignments'].items():
            if d['status'] != 'completed': findings.append(f'{name}:NOT_COMPLETED')
            elif not current(self.root, dict(d['result_refs'])): findings.append(f'{name}:ARTIFACT_DRIFT')
            try: self.dependency_handoffs(s, name)
            except Fault as e: findings.append(f'{name}:{e}')
        active_v = [v for v in s['validations'] if v['current']]
        if not active_v or active_v[-1]['exit_code'] != 0 or not current(self.root, active_v[-1]['artifact_hashes']):
            findings.append('VALIDATION_REQUIRED')
        if s['verification'] is not None:
            try:
                if not self.tdd_status(s)['green_current']: findings.append('CURRENT_GREEN_REQUIRED')
            except Fault as e: findings.append(str(e))
        elif s['sample_kind'] == 'real' and s['mode'] != 'single_agent': findings.append('TDD_BINDING_REQUIRED')
        if release:
            if s['sample_kind'] != 'real': findings.append('AT-001:FIXTURE_NOT_LIVE')
            for role in ('architect_agent', 'developer_agent', 'test_agent'):
                receipts = [a for d in s['assignments'].values() if d['role'] == role for a in d['attempts'] if a['status'] == 'completed' and a['start_evidence']]
                if not receipts or any(a['execution_mode'] not in ('runtime_session', 'native_subagent') or a['start_evidence']['source'] != 'codex_app_server' for a in receipts):
                    findings.append(f'AT-001:{role}:LIVE_RECEIPT_REQUIRED')
        return {'schema': VERSION, 'run_id': self.run_id, 'sample_kind': s['sample_kind'], 'checks_passed': not findings,
                'findings': findings, 'human_acceptance': 'not_evaluated', 'release_authorized': False}

    def finish(self):
        result = self.check()
        with self.lock():
            s = self.load(); s['finished'] = result['checks_passed']
            self.append(s, 'RUN_FINISHED', after='engineering_checked' if s['finished'] else 'blocked', reason=None if s['finished'] else 'OPEN_GAPS')
        return result

    def report(self):
        rows = self.history(); s = self.load(); result = self.check()
        text = [f'# Collaboration trace: {self.run_id}', '', f"Sample: **{s['sample_kind']}**; mode: `{s['mode']}`.",
                f"Work item: `{s['task_ref']}`; context hash: `{s['context_hash']}`.",
                'Business acceptance: NOT_EVALUATED. Runtime sessions are not native spawn_agent children.', '',
                '| Assignment | Role | State | Attempts | Engine receipts |', '|---|---|---|---:|---|']
        for name, d in s['assignments'].items():
            receipts = ', '.join(a['instance_ref'] or 'none' for a in d['attempts'])
            text.append(f"| {name} | {d['role']} | {d['status']} | {d['attempt']} | {receipts} |")
        text += ['', '## Skipped roles'] + [f'- `{r}`: `{why}`' for r, why in s['skipped_roles'].items()]
        text += ['', '## Handoffs', '| ID / revision | From → To | Status | Reviewer |', '|---|---|---|---|']
        for h in s['handoffs'].values():
            reviewer = h['review']['receipt']['instance_ref'] if h['review'] else 'not_reviewed'
            text.append(f"| {h['handoff_id']} / {h['revision']} | {h['from_delegation']} → {h['to_delegation']} | {h['status']} | {reviewer} |")
        text += ['', '## Timeline', '| UTC | Event | Assignment | State | Source / verification |', '|---|---|---|---|---|']
        for row in rows:
            e = row['event']
            text.append(f"| {e['occurred_at']} | {e['event_type']} | {e['delegation_id'] or '-'} | {e['state_after'] or '-'} | {e['source_kind']} / {e['verification_status']} |")
        attempts = [a for d in s['assignments'].values() for a in d['attempts']]
        known = [a['usage'] for a in attempts if a.get('usage') is not None]
        subtotal = sum(u['input_tokens'] + u['output_tokens'] for u in known)
        text += ['', '## Execution cost coverage',
                 f'Assignment Token subtotal: {subtotal if known else "unknown"}; measured attempts: {len(known)}/{len(attempts)}.',
                 'Review-session usage is not aggregated by this candidate; end-to-end total and savings remain unknown.',
                 'No independent user acceptance or performance benefit is inferred.']
        text += ['', '## Findings'] + ([f'- `{x}`' for x in result['findings']] or ['No structural findings; no business acceptance inferred.'])
        text += ['', '## Evidence boundary', 'Fixture receipts verify protocol behavior only. Local files are not an authenticated audit system.', 'No prompts, responses, credentials or raw errors are included. Artifacts are authorized project outputs, not chat logs.']
        return '\n'.join(text) + '\n'


def drive(engine, adapter, max_steps=40):
    """Bounded coordinator. Decisions/rework never become implicit approvals."""
    for _ in range(max_steps):
        s = engine.load()
        if s['mode'] == 'blocked' or s['finished']: break
        progressed = False
        for name, d in list(s['assignments'].items()):
            if d['status'] != 'completed': continue
            for target, t in s['assignments'].items():
                if name not in t['depends_on']: continue
                handoff = engine.submit(name, target)
                if handoff['status'] == 'submitted':
                    engine.review(handoff['handoff_id'], adapter); progressed = True
        ready = engine.ready()
        if ready:
            # Explicit dispatch calls may execute concurrently with disjoint scopes;
            # automatic driving starts sequentially to minimize token/concurrency cost.
            node = s['assignments'][ready[0]]
            if s['verification'] is not None:
                tdd = engine.tdd_status()
                if node['phase'] == 'implementation' and not tdd['red_current']: engine.record_tdd('red')
                if node['phase'] == 'verification' and not tdd['green_current']: engine.record_tdd('green')
            engine.dispatch(ready[0], adapter); progressed = True
        if not progressed: break
    return engine.check()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.cwd()); p.add_argument('--run-id', required=True)
    sub = p.add_subparsers(dest='op', required=True)
    new = sub.add_parser('plan'); new.add_argument('--context', required=True)
    for op in ('status', 'ready', 'report', 'recover', 'finish'): sub.add_parser(op)
    t = sub.add_parser('evidence'); t.add_argument('--phase', choices=('red', 'green'), required=True)
    c = sub.add_parser('check'); c.add_argument('--release', action='store_true')
    r = sub.add_parser('retry'); r.add_argument('--delegation', required=True)
    s = sub.add_parser('submit'); s.add_argument('--sender', required=True); s.add_argument('--receiver', required=True)
    for op in ('dispatch', 'drive', 'review'):
        q = sub.add_parser(op); q.add_argument('--execute', action='store_true'); q.add_argument('--model')
        if op == 'dispatch': q.add_argument('--delegation', required=True)
        if op == 'review': q.add_argument('--handoff', required=True)
    a = sub.add_parser('assist'); a.add_argument('--requester', required=True); a.add_argument('--capability', required=True); a.add_argument('--evidence-ref', action='append', required=True); a.add_argument('--write-path', action='append', default=[])
    cancel = sub.add_parser('cancel'); cancel.add_argument('--confirmation-ref', required=True)
    v = sub.add_parser('validate'); v.add_argument('command', nargs=argparse.REMAINDER)
    args = p.parse_args(argv); engine = Engine(args.root, args.run_id)
    try:
        if args.op == 'plan': result = engine.create(args.context)
        elif args.op == 'status': result = engine.load()
        elif args.op == 'ready': result = engine.ready()
        elif args.op == 'report': print(engine.report()); return 0
        elif args.op == 'evidence': result = engine.record_tdd(args.phase)
        elif args.op == 'check': result = engine.check(args.release)
        elif args.op == 'recover': result = engine.recover()
        elif args.op == 'retry': result = engine.retry(args.delegation)
        elif args.op == 'submit': result = engine.submit(args.sender, args.receiver)
        elif args.op == 'assist': result = engine.assist(args.requester, args.capability, args.evidence_ref, args.write_path)
        elif args.op == 'cancel': result = engine.cancel(args.confirmation_ref)
        elif args.op == 'validate': result = engine.validate(args.command[1:] if args.command[:1] == ['--'] else args.command)
        elif args.op == 'finish': result = engine.finish()
        else:
            require(args.execute, 'EXECUTE_REQUIRED')
            from codex_adapter import CodexAdapter
            adapter = CodexAdapter(args.root, model=args.model)
            if args.op == 'dispatch': result = engine.dispatch(args.delegation, adapter)
            elif args.op == 'review': result = engine.review(args.handoff, adapter)
            else: result = drive(engine, adapter)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        failed = isinstance(result, dict) and (result.get('checks_passed') is False or (args.op == 'validate' and result.get('exit_code') != 0))
        return 1 if failed else 0
    except (Fault, OSError, ValueError) as exc:
        code = str(exc) if isinstance(exc, Fault) else 'COLLABORATION_IO_ERROR'
        print(json.dumps({'error': code}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.modules.setdefault('agent_collaboration', sys.modules[__name__])
    sys.exit(main())
