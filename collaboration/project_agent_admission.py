#!/usr/bin/env python3
"""Source-only INIT-S2 admission; reuses Engine execution, authorization and journal.

prepare creates pending work/review material. review checks an external record.
plan starts no model: it creates a normal Engine run with immutable profile anchors.
Existing source drive/review/recover commands operate on that same run. Legacy runs
are unchanged; this is not a global enforcement retrofit or an OMP adapter.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import sys

import project_agents as pa
import project_context as pc
from project_agent_review import (candidate, initialization_task, pin, read_pinned,
                                  recheck, render_brief, require, review_template,
                                  validate_review)
from agent_collaboration import Engine, Fault, make_plan, overlaps

ADMISSION_FIELDS = {'schema', 'project_id', 'manifest_ref', 'context_ref',
                    'context_pack_ref', 'policy_ref', 'profiles'}


def output_scope(root, directory):
    path = pa.ref_path(root, directory, False)
    require(path.relative_to(root).as_posix().startswith('generated/project-agents/'), 'INIT_OUTPUT_SCOPE')
    return directory


def text_once(root, ref, text):
    path = pa.ref_path(root, ref, False)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        stream.write(text)


def prepare(root, manifest_ref, project_id, role_id, variant, sample_kind, output_dir):
    root = Path(root).resolve()
    output_scope(root, output_dir)
    task = initialization_task(root, manifest_ref, project_id, role_id, variant)
    brief = render_brief(root, manifest_ref, project_id, role_id, variant)
    template = review_template(root, manifest_ref, project_id, role_id, variant, sample_kind)
    recheck(root, task['source_hashes'])
    names = [output_dir + '/' + n for n in ('initialization-task.json', 'work-instructions.md', 'review-template.json')]
    require(all(not pa.ref_path(root, ref, False).exists() for ref in names), 'INIT_OUTPUT_EXISTS')
    pc.write_once(root, names[0], task)
    text_once(root, names[1], brief)
    pc.write_once(root, names[2], template)
    return {'task_ref': names[0], 'brief_ref': names[1], 'review_template_ref': names[2],
            'review_decision': 'pending', 'runtime_status': 'NOT_RUN', 'authorization': 'not_granted'}


def plan(root, request_ref, output_dir):
    root = Path(root).resolve()
    output_scope(root, output_dir)
    frozen = {}
    request = read_pinned(root, request_ref, frozen)
    pa.fields(request, ADMISSION_FIELDS, 'INIT_ADMISSION_FIELDS')
    require(request['schema'] == 'project-agent-admission/v1', 'INIT_ADMISSION_SCHEMA')
    project_id = pa.identifier(request['project_id'])
    manifest = read_pinned(root, request['manifest_ref'], frozen)
    check = pa.check(root, manifest, project_id)
    require(check['current'] and check['configuration_status'] == 'CANDIDATE', 'INIT_PROFILE_NOT_CURRENT')
    context = read_pinned(root, request['context_ref'], frozen)
    pack = read_pinned(root, request['context_pack_ref'], frozen)
    pack_result = pc.validate(root, pack)
    require(pack_result['current'], 'INIT_TASK_PACK_STALE')
    require(pack['goal_ref'] == context.get('goal_ref') and pack['task_ref'] == context.get('task_ref'),
            'INIT_TASK_PACK_MISMATCH')
    pin(root, request['policy_ref'], frozen)
    registry = read_pinned(root, manifest['registry_ref'], frozen)
    original = make_plan(root, request['context_ref'], manifest['registry_ref'], request['policy_ref'])
    selected = request['profiles']
    require(isinstance(selected, list) and 1 <= len(selected) <= 20, 'INIT_ADMISSION_PROFILES')
    bindings, briefs = {}, {}
    for entry in selected:
        pa.fields(entry, {'role_id', 'variant', 'review_ref'}, 'INIT_ADMISSION_PROFILE_FIELDS')
        role_id, variant = pa.identifier(entry['role_id']), pa.identifier(entry['variant'])
        require(role_id not in bindings, 'INIT_ADMISSION_DUPLICATE_ROLE')
        result = validate_review(root, request['manifest_ref'], project_id, role_id, variant,
                                 entry['review_ref'], context['sample_kind'])
        for ref, expected in result['source_hashes'].items():
            pin(root, ref, frozen)
            require(frozen[ref] == expected, 'INIT_REVIEW_INPUT_CHANGED')
        bindings[role_id] = {k: v for k, v in result.items() if k != 'source_hashes'}
        briefs[role_id] = render_brief(root, request['manifest_ref'], project_id, role_id, variant)
    expected_roles = {name: d['role'] for name, d in original['assignments'].items()}
    require(set(expected_roles.values()) <= set(bindings), 'INIT_PLANNED_ROLE_NOT_REVIEWED')
    # Pin the task pack inventory through existing inputs. Intentional implementation
    # writes still use Engine's normal source hashes; initialization sources below
    # are stricter immutable anchors and may not be task write targets.
    pack_inputs = list(pack['dependencies']) + [e['ref'] for values in pack['sources'].values() for e in values]
    effective = copy.deepcopy(registry)
    generated = {}
    for role_id, role in effective['roles'].items():
        role['enabled'] = role_id in bindings
        if role_id in bindings:
            brief_ref = output_dir + '/brief-' + role_id + '.md'
            generated[brief_ref] = briefs[role_id]
            role['skill_refs'] = list(dict.fromkeys(role.get('skill_refs', []) + [brief_ref]))
    registry_out, context_out = output_dir + '/registry.json', output_dir + '/context.json'
    outputs = list(generated) + [registry_out, context_out]
    require(all(not pa.ref_path(root, ref, False).exists() for ref in outputs), 'INIT_OUTPUT_EXISTS')
    # Broad writable ancestors would let an assisting role replace the accepted
    # policy. Reject the authorization itself, not just currently selected scopes.
    protected = list(frozen) + outputs
    for scope in original['authorization']['write_paths']:
        pa.ref_path(root, scope, False)
        require(not overlaps([scope], protected), 'INIT_AUTH_WRITES_BOUND_INPUT')
    recheck(root, frozen)
    for ref, text in generated.items():
        text_once(root, ref, text)
        pin(root, ref, frozen)
    pc.write_once(root, registry_out, effective)
    pin(root, registry_out, frozen)
    bound_context = copy.deepcopy(context)
    bound_context['inputs'] = list(dict.fromkeys(context['inputs'] + pack_inputs + list(frozen)))
    pc.write_once(root, context_out, bound_context)
    pin(root, context_out, frozen)
    binding = {'schema': 'project-agent-run-binding/v1', 'project_id': project_id,
               'manifest_ref': request['manifest_ref'], 'manifest_version': manifest['version'],
               'context_pack_ref': request['context_pack_ref'], 'admission_ref': request_ref,
               'profiles': bindings, 'runtime_initialization': 'NOT_RUN',
               'identity_verification': 'not_performed'}

    class AdmissionEngine(Engine):
        def append(self, state, event_type, *args, **kwargs):
            if state['sequence'] == 0:
                # Called by the original Engine.create under its original lock,
                # before the first journal snapshot is visible to other commands.
                recheck(root, frozen)
                require({n: d['role'] for n, d in state['assignments'].items()} == expected_roles,
                        'INIT_ASSIGNMENT_CHANGED')
                require(state['context_hash'] == pa.digest(bound_context), 'INIT_CONTEXT_CHANGED')
                state['anchors'].update(frozen)
                state['project_agent_initialization'] = copy.deepcopy(binding)
            return super().append(state, event_type, *args, **kwargs)

    engine = AdmissionEngine(root, context['run_id'])
    state = engine.create(context_out, registry_out, request['policy_ref'])
    return {'run_id': state['run_id'], 'context_ref': context_out, 'registry_ref': registry_out,
            'profile_count': len(bindings), 'execution': 'not_started', 'runtime_status': 'NOT_RUN',
            'authorization': 'existing_task_authorization_only',
            'configuration_record_check': 'PASS', 'business_acceptance': 'not_evaluated'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('prepare', 'review'):
        sub = commands.add_parser(command)
        for flag in ('manifest', 'project-id', 'role', 'variant'):
            sub.add_argument('--' + flag, required=True)
        sub.add_argument('--sample-kind', choices=('real', 'fixture'), required=True)
        sub.add_argument('--output-dir' if command == 'prepare' else '--record', required=True)
    create = commands.add_parser('plan')
    create.add_argument('--request', required=True)
    create.add_argument('--output-dir', required=True)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == 'plan':
            result = plan(root, args.request, args.output_dir)
        elif args.command == 'prepare':
            result = prepare(root, args.manifest, args.project_id, args.role, args.variant,
                             args.sample_kind, args.output_dir)
        else:
            result = validate_review(root, args.manifest, args.project_id, args.role, args.variant,
                                     args.record, args.sample_kind)
            result = {k: v for k, v in result.items() if k != 'source_hashes'}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (pc.ContextError, Fault, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, (pc.ContextError, Fault)) else 'INVALID_INPUT'
        print('PROJECT_AGENT_ADMISSION_ERROR ' + code, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
