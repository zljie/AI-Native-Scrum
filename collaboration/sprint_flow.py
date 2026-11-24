#!/usr/bin/env python3
"""Read-only Sprint previews and evidence-bound joint assessment.

The existing Engine journal owns execution state. This module never starts an
adapter, writes a journal entry, retries work, finishes a run or grants approval.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import sys

from agent_collaboration import Engine, Fault, file_hash, identifier, make_plan, ref, require
from v15_graph import graph, metrics


CONTRACT_SCHEMA = 'sprint-scenario-contract/v1'
REPORT_SCHEMA = 'sprint-scenario-review/v1'
SHA256 = re.compile(r'[0-9a-f]{64}\Z')
DIRECTOR_STEPS = {'director_pre': 'scenario_design', 'director_verify': 'scenario_verify'}


def _fields(value, fields, code):
    require(isinstance(value, dict) and set(value) == set(fields), code)


def _text(value, code):
    require(isinstance(value, str) and bool(value.strip()), code)
    return value


def _hashes(value, code):
    require(isinstance(value, dict), code)
    for name, digest in value.items():
        _text(name, code)
        require(isinstance(digest, str) and SHA256.fullmatch(digest), code)
    return value


def _unique_object(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, 'SPRINT_DUPLICATE_JSON_KEY')
        result[name] = value
    return result


def _invalid_constant(_):
    raise Fault('SPRINT_INVALID_JSON')


def _record(root, name):
    """Read only an explicitly linked artifact, with the Engine's path boundary."""
    before = file_hash(root, name)
    try:
        value = json.loads(ref(root, name).read_text(encoding='utf-8'),
                           object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (UnicodeError, ValueError) as exc:
        if isinstance(exc, Fault):
            raise
        raise Fault('SPRINT_INVALID_JSON') from None
    require(file_hash(root, name) == before, 'SPRINT_RECORD_CHANGED')
    return value, before


def _bound_record(root, node, supplied, schema):
    # Legacy Engine plans use [] until the first result, then a hash mapping.
    results = node.get('result_refs')
    if results == []:
        results = {}
    results = _hashes(results, 'SPRINT_RESULT_REFS')
    if supplied is not None:
        require(isinstance(supplied, str) and supplied in results, 'SPRINT_RECORD_NOT_OWNED')
        value, actual = _record(root, supplied)
        require(actual == results[supplied], 'SPRINT_RECORD_STALE')
        return supplied, value, actual
    found = []
    for name, expected in results.items():
        require(file_hash(root, name) == expected, 'SPRINT_RECORD_STALE')
        try:
            value, actual = _record(root, name)
        except Fault as exc:
            if str(exc) == 'SPRINT_INVALID_JSON' and Path(name).suffix.lower() != '.json':
                continue  # A director may also return ordinary prose artifacts.
            raise
        if isinstance(value, dict) and value.get('schema') == schema:
            found.append((name, value, actual))
    require(len(found) <= 1, 'SPRINT_RECORD_AMBIGUOUS')
    return found[0] if found else (None, None, None)


def _attempt(state, name, rows):
    node = state['assignments'][name]
    require(node.get('status') == 'completed', 'SPRINT_DIRECTOR_NOT_COMPLETED')
    number = node.get('attempt')
    require(type(number) is int and number > 0, 'SPRINT_ATTEMPT_INVALID')
    attempts = node.get('attempts')
    require(isinstance(attempts, list) and bool(attempts), 'SPRINT_ATTEMPT_MISSING')
    attempt = attempts[-1]
    require(isinstance(attempt, dict) and attempt.get('attempt') == number
            and type(attempt.get('attempt')) is int and attempt.get('status') == 'completed',
            'SPRINT_ATTEMPT_MISMATCH')
    instance = identifier(attempt.get('instance_ref'))
    receipt = attempt.get('start_evidence')
    require(isinstance(receipt, dict) and receipt.get('instance_ref') == instance
            and receipt.get('sample_kind') == state['sample_kind'], 'SPRINT_RECEIPT_MISMATCH')
    identifier(receipt.get('request_ref'))
    if state['sample_kind'] == 'real':
        require(receipt.get('source') == 'codex_app_server'
                and attempt.get('execution_mode') in ('runtime_session', 'native_subagent'),
                'SPRINT_UNVERIFIED_RUNTIME')
    expected_verification = 'verified' if state['sample_kind'] == 'real' else 'unverified'
    started = any(row['event'].get('event_type') == 'AGENT_STARTED'
                  and row['event'].get('delegation_id') == name
                  and row['event'].get('agent_instance_ref') == instance
                  and row['event'].get('source_kind') == receipt.get('source')
                  and row['event'].get('sample_kind') == state['sample_kind']
                  and row['event'].get('verification_status') == expected_verification
                  and row['state']['assignments'].get(name, {}).get('attempt') == number
                  for row in rows)
    submitted = any(row['event'].get('event_type') == 'AGENT_RESULT_SUBMITTED'
                    and row['event'].get('delegation_id') == name
                    and row['event'].get('agent_instance_ref') == instance
                    and row['state']['assignments'].get(name, {}).get('attempt') == number
                    and row['state']['assignments'][name].get('result_refs') == node['result_refs']
                    for row in rows)
    require(started and submitted, 'SPRINT_INSTANCE_NOT_IN_JOURNAL')
    return attempt


def _ancestors(assignments, name):
    result, visiting = set(), set()

    def visit(current):
        require(current in assignments, 'SPRINT_UNKNOWN_DEPENDENCY')
        require(current not in visiting, 'SPRINT_DEPENDENCY_CYCLE')
        if current in result:
            return
        visiting.add(current)
        for dependency in assignments[current]['depends_on']:
            visit(dependency)
        visiting.remove(current)
        result.add(current)

    visit(name)
    result.remove(name)
    return result


def _scenario(state, rows, root, contract_ref, report_ref):
    result = {'status': 'NOT_RUN', 'current': False, 'findings': [],
              'contract_ref': contract_ref, 'report_ref': report_ref,
              'reviewer_instance': None, 'scenarios': []}
    observed, recommendations = {}, []
    assignments = state['assignments']
    selected = any(name in DIRECTOR_STEPS or node.get('capability') in DIRECTOR_STEPS.values()
                   or node.get('role') == 'director_agent' for name, node in assignments.items())
    try:
        # The selected policy cannot erase obligations from the accepted input.
        # In particular, accidentally using the default six-role policy for a
        # user-facing change must not turn its missing scenario review into N/A.
        context_ref = state['context_ref']
        context, context_hash = _record(root, context_ref)
        require(context_hash == state['anchors'].get(context_ref), 'SPRINT_CONTEXT_DRIFT')
        require(isinstance(context, dict) and context.get('schema') == 'task-context/v1'
                and isinstance(context.get('signals'), list), 'SPRINT_CONTEXT_INVALID')
        scenario_required = bool({'ui_flow', 'business_rule'} & set(context['signals']))
        observed[context_ref] = context_hash
        if not selected:
            require(contract_ref is None and report_ref is None, 'SPRINT_UNEXPECTED_SCENARIO_RECORDS')
            if scenario_required:
                result['findings'].append('SPRINT_DIRECTOR_STEP_MISSING')
                return result, observed, recommendations
            result['status'] = 'NOT_APPLICABLE'
            result['current'] = True
            return result, observed, recommendations
        require(all(name in assignments for name in DIRECTOR_STEPS), 'SPRINT_DIRECTOR_STEP_MISSING')
        for name, capability in DIRECTOR_STEPS.items():
            node = assignments[name]
            require(node.get('role') == 'director_agent' and node.get('capability') == capability,
                    'SPRINT_DIRECTOR_ROLE_MISMATCH')
        pre, verify = assignments['director_pre'], assignments['director_verify']
        contract_ref, contract, contract_hash = _bound_record(root, pre, contract_ref, CONTRACT_SCHEMA)
        report_ref, report, report_hash = _bound_record(root, verify, report_ref, REPORT_SCHEMA)
        result.update(contract_ref=contract_ref, report_ref=report_ref)
        if contract is None or report is None:
            result['findings'].append('SPRINT_SCENARIO_RECORDS_REQUIRED')
            return result, observed, recommendations
        _attempt(state, 'director_pre', rows)
        attempt = _attempt(state, 'director_verify', rows)
        result['reviewer_instance'] = attempt['instance_ref']
        observed.update({contract_ref: contract_hash, report_ref: report_hash})
        _fields(contract, {'schema', 'run_id', 'task_ref', 'sample_kind', 'scenarios'},
                'SPRINT_CONTRACT_FIELDS')
        require(contract['schema'] == CONTRACT_SCHEMA, 'SPRINT_CONTRACT_SCHEMA')
        _fields(report, {'schema', 'run_id', 'task_ref', 'sample_kind', 'attempt', 'delegation_id',
                         'checked_hashes', 'evidence_hashes', 'scenarios'}, 'SPRINT_REPORT_FIELDS')
        require(report['schema'] == REPORT_SCHEMA, 'SPRINT_REPORT_SCHEMA')
        for record in (contract, report):
            require(all(record[field] == state[field] for field in ('run_id', 'task_ref', 'sample_kind')),
                    'SPRINT_RECORD_CONTEXT_MISMATCH')
        require(report['delegation_id'] == 'director_verify' and type(report['attempt']) is int
                and report['attempt'] == attempt['attempt'], 'SPRINT_REPORT_ATTEMPT_MISMATCH')

        scenarios = contract['scenarios']
        require(isinstance(scenarios, list) and bool(scenarios), 'SPRINT_SCENARIO_INVENTORY')
        inventory, acceptances = {}, set()
        story_id = Path(state['story_ref']).stem.split('_', 1)[0]
        for item in scenarios:
            _fields(item, {'id', 'acceptance_ref', 'required'}, 'SPRINT_SCENARIO_FIELDS')
            scenario_id = _text(item['id'], 'SPRINT_SCENARIO_ID')
            acceptance = _text(item['acceptance_ref'], 'SPRINT_ACCEPTANCE_REF')
            require(scenario_id not in inventory and acceptance not in acceptances,
                    'SPRINT_DUPLICATE_SCENARIO')
            require(acceptance.startswith(story_id + '#')
                    and bool(acceptance[len(story_id) + 1:].strip()), 'SPRINT_ACCEPTANCE_STORY_MISMATCH')
            require(type(item['required']) is bool, 'SPRINT_SCENARIO_REQUIRED')
            inventory[scenario_id] = item
            acceptances.add(acceptance)
        require(any(item['required'] for item in inventory.values()), 'SPRINT_REQUIRED_SCENARIO_MISSING')

        expected = {contract_ref: contract_hash}
        ancestors = _ancestors(assignments, 'director_verify')
        require('director_pre' in ancestors, 'SPRINT_SCENARIO_DEPENDENCY_REQUIRED')
        for name in sorted(ancestors):
            node = assignments[name]
            require(node.get('status') == 'completed', 'SPRINT_ANCESTOR_NOT_COMPLETED')
            artifacts = _hashes(node.get('result_refs'), 'SPRINT_ANCESTOR_ARTIFACTS')
            require(bool(artifacts), 'SPRINT_ANCESTOR_ARTIFACTS')
            for path, digest in artifacts.items():
                require(path not in expected or expected[path] == digest,
                        'SPRINT_ANCESTOR_ARTIFACT_CONFLICT')
                require(file_hash(root, path) == digest, 'SPRINT_ANCESTOR_ARTIFACT_STALE')
                expected[path] = digest
        checked = _hashes(report['checked_hashes'], 'SPRINT_CHECKED_HASHES')
        require(checked == expected, 'SPRINT_CHECKED_INPUTS_MISMATCH')
        observed.update(expected)

        verdicts = report['scenarios']
        require(isinstance(verdicts, list), 'SPRINT_VERDICTS')
        seen, evidence = set(), set()
        for item in verdicts:
            _fields(item, {'id', 'status', 'evidence_refs', 'reason', 'rework_step'}, 'SPRINT_VERDICT_FIELDS')
            scenario_id = _text(item['id'], 'SPRINT_SCENARIO_ID')
            require(scenario_id in inventory and scenario_id not in seen, 'SPRINT_VERDICT_INVENTORY_MISMATCH')
            seen.add(scenario_id)
            require(item['status'] in ('PASS', 'FAIL', 'NOT_RUN'), 'SPRINT_VERDICT_STATUS')
            _text(item['reason'], 'SPRINT_VERDICT_REASON')
            refs = item['evidence_refs']
            require(isinstance(refs, list) and all(isinstance(path, str) and path.strip() for path in refs),
                    'SPRINT_EVIDENCE_REFS')
            require(len(refs) == len(set(refs)), 'SPRINT_EVIDENCE_REFS')
            require(item['status'] == 'NOT_RUN' or bool(refs), 'SPRINT_EVIDENCE_REQUIRED')
            for path in refs:
                require(ref(root, path) != ref(root, report_ref), 'SPRINT_SELF_EVIDENCE')
            evidence.update(refs)
            step = item['rework_step']
            require(step is None or (item['status'] == 'FAIL' and isinstance(step, str)
                                     and step in assignments), 'SPRINT_REWORK_STEP')
            if step is not None:
                recommendations.append({'scenario_id': scenario_id, 'step': step,
                                        'action': 'inspect_before_retry'})
            # Metadata only: do not echo free-form reasons or source content.
            result['scenarios'].append({'id': scenario_id, 'required': inventory[scenario_id]['required'],
                                        'status': item['status'], 'evidence_refs': refs, 'rework_step': step})
        require(seen == set(inventory), 'SPRINT_VERDICT_INVENTORY_MISMATCH')
        evidence_hashes = _hashes(report['evidence_hashes'], 'SPRINT_EVIDENCE_HASHES')
        require(set(evidence_hashes) == evidence, 'SPRINT_EVIDENCE_INVENTORY_MISMATCH')
        for path, digest in evidence_hashes.items():
            require(path not in observed or observed[path] == digest,
                    'SPRINT_EVIDENCE_INPUT_MISMATCH')
            require(file_hash(root, path) == digest, 'SPRINT_EVIDENCE_STALE')
        observed.update(evidence_hashes)
        required = [item['status'] for item in result['scenarios'] if item['required']]
        result['status'] = 'FAIL' if 'FAIL' in required else 'NOT_RUN' if 'NOT_RUN' in required else 'PASS'
        result['current'] = True
        result['required_count'] = len(required)
        if result['status'] != 'PASS':
            result['findings'].append('SPRINT_REQUIRED_SCENARIO_' + result['status'])
    except (Fault, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, Fault) else 'SPRINT_INVALID_RECORD'
        result.update(status='INVALID', current=False)
        result['findings'].append(code)
        recommendations = []  # Untrusted/partial records cannot nominate a retry.
    return result, observed, recommendations


def preview(root, context_ref, registry_ref, policy_ref):
    root = Path(root).resolve()
    state = make_plan(root, context_ref, registry_ref, policy_ref)
    return {'schema': 'sprint-preview/v1', 'run_id': state['run_id'], 'sample_kind': state['sample_kind'],
            'mode': state['mode'], 'assignments': [
                {'step': name, **{key: node[key] for key in
                                 ('role', 'capability', 'phase', 'depends_on', 'write_paths', 'deliverable')}}
                for name, node in state['assignments'].items()],
            'skipped_roles': state['skipped_roles'], 'execution': 'not_started',
            'journal_created': False, 'authority': 'unchanged', 'live_host_acceptance': 'NOT_RUN',
            'native_spawn_agent_acceptance': 'NOT_RUN', 'human_acceptance': 'NOT_EVALUATED',
            'release_authorized': False}


def assess(engine, contract_ref=None, report_ref=None):
    rows = engine.history()
    require(bool(rows), 'RUN_NOT_FOUND')
    state = copy.deepcopy(rows[-1]['state'])
    snapshot = (state['sequence'], rows[-1]['hash'])
    scenario, observed, recommendations = _scenario(state, rows, engine.root, contract_ref, report_ref)
    view = graph(engine)
    coverage = metrics(engine)
    engineering = engine.check()
    findings = list(engineering['findings'])
    if view['new_plan_required'] and scenario['status'] not in ('NOT_APPLICABLE', 'NOT_RUN'):
        scenario.update(status='INVALID', current=False)
        scenario['findings'].append('SPRINT_CONTEXT_DRIFT')
        recommendations = []
    if scenario['current'] and observed:
        try:
            require(all(file_hash(engine.root, name) == digest for name, digest in observed.items()),
                    'SPRINT_EVIDENCE_CHANGED_DURING_CHECK')
        except (Fault, OSError):
            scenario.update(status='INVALID', current=False)
            scenario['findings'].append('SPRINT_EVIDENCE_CHANGED_DURING_CHECK')
            recommendations = []
    findings.extend(scenario['findings'])
    unresolved = [{'step': name, 'status': node['status'], 'reason': node.get('reason')}
                  for name, node in state['assignments'].items() if node['status'] != 'completed']
    unresolved.extend({'scenario_id': item['id'], 'status': item['status'], 'required': item['required']}
                      for item in scenario['scenarios'] if item['status'] != 'PASS')
    if scenario['status'] not in ('PASS', 'NOT_APPLICABLE'):
        unresolved.append({'gate': 'scenario_review', 'status': scenario['status'],
                           'findings': list(scenario['findings'])})
    joint = engineering['checks_passed'] and scenario['status'] in ('PASS', 'NOT_APPLICABLE')
    result = {'schema': 'sprint-assessment/v1', 'run_id': state['run_id'],
              'sample_kind': state['sample_kind'], 'sequence': snapshot[0], 'journal_hash': snapshot[1],
              'assessment_status': 'ASSESSED', 'engineering': engineering, 'scenario_review': scenario,
              'structural_checks_passed': bool(joint), 'findings': list(dict.fromkeys(findings)),
              'unresolved_work': unresolved, 'rework_recommendations': recommendations,
              'graph': view, 'metrics': coverage, 'execution_state_authority': 'collaboration-journal',
              'live_host_acceptance': ('NOT_EVALUATED' if state['sample_kind'] == 'real'
                                       and coverage['verified_runtime_session_starts'] else 'NOT_RUN'),
              'native_spawn_agent_acceptance': ('NOT_RUN' if state['sample_kind'] == 'fixture'
                                                else coverage['native_spawn_agent_acceptance']),
              'human_acceptance': 'NOT_EVALUATED', 'release_authorized': False}
    after = engine.history()
    if not after or (after[-1]['state']['sequence'], after[-1]['hash']) != snapshot:
        result.update(assessment_status='BLOCKED', structural_checks_passed=False)
        result['findings'].append('SPRINT_JOURNAL_CHANGED')
        result['scenario_review'].update(status='INVALID', current=False)
        result['scenario_review']['findings'].append('SPRINT_JOURNAL_CHANGED')
        result['rework_recommendations'] = []
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--run-id')
    commands = parser.add_subparsers(dest='command', required=True)
    proposed = commands.add_parser('preview')
    for flag in ('context', 'registry', 'policy'):
        proposed.add_argument('--' + flag, required=True)
    check = commands.add_parser('check')
    check.add_argument('--contract')
    check.add_argument('--report')
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve()
        if args.command == 'preview':
            result = preview(root, args.context, args.registry, args.policy)
        else:
            require(bool(args.run_id), 'RUN_ID_REQUIRED')
            result = assess(Engine(root, args.run_id), args.contract, args.report)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if args.command == 'preview' or result['structural_checks_passed'] else 1
    except (Fault, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, Fault) and re.fullmatch(r'[A-Z0-9_]+', str(exc)) else 'INVALID_INPUT'
        print('SPRINT_FLOW_ERROR ' + code, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
