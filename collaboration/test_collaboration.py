"""PRD AT-002..014 protocol checks. Fixture successes never satisfy live AT-001."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'collaboration'), str(ROOT/'observability')]
from agent_collaboration import Engine, Fault, digest, file_hash, make_plan, drive
from codex_adapter import CodexAdapter
import harness_observe as obs


class FixtureAdapter:
    sample_kind = 'fixture'; source = 'fixture_transport'; mode = 'fixture'
    def __init__(self, no_start=False, decision='accepted', fail=False, duplicate=False, extra=None, instance=None):
        self.no_start=no_start; self.decision=decision; self.fail=fail; self.duplicate=duplicate
        self.extra=extra; self.instance=instance
    def receipt(self, started):
        r={'instance_ref':self.instance or 'FIX-'+uuid.uuid4().hex, 'request_ref':'REQ-'+uuid.uuid4().hex,
           'source':self.source,'sample_kind':self.sample_kind}
        if not self.no_start:
            started(r)
            if self.duplicate: started(r)
    def run(self, packet, started):
        self.receipt(started)
        if self.fail: raise TimeoutError('SECRET-RAW-ERROR')
        changes=[]
        if packet['write_paths']:
            scope=packet['write_paths'][0]
            path=scope if '.' in Path(scope).name else scope+'/result.md'
            base=next((x['sha256'] for x in packet['documents'] if x['ref']==path), None)
            changes=[{'path':path,'base_sha256':base,'content':'Fixture '+packet['delegation_id']+'\n'}]
        if self.extra: changes.append(self.extra)
        return {'outcome':'completed','changes':changes,'artifacts':[],'usage':None,'assistance':None}
    def review(self, packet, started):
        self.receipt(started)
        return {'decision':self.decision,'reason_code':'FIXTURE_REVIEW', 'evidence_refs':list(packet['review']['artifacts'])}


def setup(root, signals=None, kind='fixture'):
    signals=signals or ['api_contract']
    paths={'raw/goals/GOAL-001.md':'---\nid: GOAL-001\nstatus: approved\n---\nFixture only.\n',
           'wiki/workitems/STORY-001.md':'Fixture AC: preserve old behavior.\n',
           'wiki/workitems/TASK-001.md':'Fixture implementation task.\n',
           'intake/consent.md':'Synthetic isolated-test authorization, NOT a user approval.\n',
           'src/app.py':'VALUE = 1\n', 'schema/agent-roles.yaml':'roles: five existing core roles\n',
           'schema/roles/database_agent.md':'Optional database expert contract\n',
           'tests/test_sample.py':'import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertEqual(1,1)\n'}
    paths['AGENTS.md'] = 'Synthetic fixture rules: no production or secret access.\n'
    for entry in json.loads((ROOT/'collaboration/registry.json').read_text())['roles'].values():
        for sk in entry.get('skill_refs', []): paths[sk] = 'Fixture skill method.\n'
    for role in json.loads((ROOT/'collaboration/registry.json').read_text())['roles']:
        paths['.codex/agents/'+role+'.toml']='name = "'+role+'"\ndescription = "fixture"\ndeveloper_instructions = "bounded task"\n'
    paths['schema/collaboration/registry.json']=(ROOT/'collaboration/registry.json').read_text()
    paths['schema/collaboration/policy.json']=(ROOT/'collaboration/policy.json').read_text()
    for name,text in paths.items():
        p=root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
    policy=json.loads(paths['schema/collaboration/policy.json'])
    scopes={n['scope_key']:['outputs/'+n['id']+'.md'] for n in policy['steps']}
    auth={'schema':'collaboration-authorization/v1','actor':'fixture_owner','at':'2026-11-06T00:00:00+00:00',
          'confirmation_ref':'intake/consent.md','task_refs':['wiki/workitems/TASK-001.md'],
          'allow_delegation':True,'write_paths':['outputs','src'],
          'validation_commands':[[sys.executable,'-m','unittest','discover','-s','tests','-v']],
          'max_attempts':3,'max_parallel':2,'sample_kind':kind}
    c={'schema':'task-context/v1','run_id':'RUN-001','goal_ref':'raw/goals/GOAL-001.md',
       'story_ref':'wiki/workitems/STORY-001.md','task_ref':'wiki/workitems/TASK-001.md',
       'signals':signals,'signal_evidence':{s:['src/app.py'] for s in signals},'inputs':['src/app.py'],
       'scopes':scopes,'authorization_ref':'intake/authorization.json','sample_kind':kind}
    (root/'intake/authorization.json').write_text(json.dumps(auth)); (root/'intake/context.json').write_text(json.dumps(c))
    return c,auth


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.context,self.auth=setup(self.root)
        self.engine=Engine(self.root,'RUN-001')
    def tearDown(self): self.tmp.cleanup()
    def plan(self,signals=None):
        if signals:
            self.context['signals']=signals; self.context['signal_evidence']={s:['src/app.py'] for s in signals}
            (self.root/'intake/context.json').write_text(json.dumps(self.context))
        return self.engine.create('intake/context.json')
    def starts(self): return [r for r in self.engine.history() if r['event']['event_type']=='AGENT_STARTED']
    def complete(self):
        drive(self.engine,FixtureAdapter())
        self.engine.validate(self.auth['validation_commands'][0])
        return self.engine.finish()
    def test_AT002_simple_no_unneeded_roles(self):
        p=self.plan(['copy_only'])
        self.assertEqual(p['mode'],'single_agent'); self.assertEqual(list(p['assignments']),['implementation'])
        self.assertEqual(len(p['skipped_roles']),5); self.assertEqual(self.starts(),[])
        self.assertTrue(self.complete()['checks_passed'])
    def test_cross_scenario_policy_not_db_specific(self):
        expected={'ui_flow':{'product_agent','developer_agent','test_agent'},'api_contract':{'architect_agent','developer_agent','test_agent'},
                  'bugfix':{'developer_agent','test_agent'},'runtime_change':{'architect_agent','developer_agent','test_agent','ops_agent'},
                  'database_schema':{'architect_agent','developer_agent','test_agent','database_agent'}}
        for signal,roles in expected.items():
            with tempfile.TemporaryDirectory() as t:
                root=Path(t); setup(root,[signal]); e=Engine(root,'RUN-001'); s=e.create('intake/context.json')
                self.assertEqual({d['role'] for d in s['assignments'].values()},roles)
                drive(e,FixtureAdapter()); e.validate([sys.executable,'-m','unittest','discover','-s','tests','-v'])
                self.assertTrue(e.finish()['checks_passed'],e.check())
    def test_AT003_no_result_no_dependency_unlock(self):
        self.plan(); self.assertNotIn('analysis',self.engine.ready())
        with self.assertRaises(Fault): self.engine.submit('architecture_pre','analysis')
        self.engine.dispatch('architecture_pre',FixtureAdapter())
        self.assertNotIn('analysis',self.engine.ready())
        h=self.engine.submit('architecture_pre','analysis')
        self.assertNotIn('analysis',self.engine.ready())
        self.engine.review(h['handoff_id'],FixtureAdapter())
        self.assertIn('analysis',self.engine.ready())
    def test_AT004_AT009_rework_retains_revision_and_events(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter())
        h=self.engine.submit('architecture_pre','analysis')
        self.engine.review(h['handoff_id'],FixtureAdapter(decision='changes_requested'))
        self.engine.retry('architecture_pre')
        self.engine.dispatch('architecture_pre',FixtureAdapter())
        h2=self.engine.submit('architecture_pre','analysis')
        self.assertEqual(h2['revision'],2); self.assertEqual(h2['supersedes'],h['handoff_id'])
        self.engine.review(h2['handoff_id'],FixtureAdapter())
        self.assertIn('analysis',self.engine.ready())
        self.assertTrue(any(r['event']['event_type']=='HANDOFF_CHANGES_REQUESTED' for r in self.engine.history()))
        self.assertEqual(len(self.engine.load()['assignments']['architecture_pre']['attempts']),2)
    def test_AT005_unavailable_is_not_started(self):
        self.plan()
        class Missing(FixtureAdapter):
            def run(self,p,s): raise Fault('RUNTIME_UNAVAILABLE')
        with self.assertRaisesRegex(Fault,'RUNTIME_UNAVAILABLE'): self.engine.dispatch('architecture_pre',Missing())
        self.assertEqual(self.starts(),[])
        self.assertEqual(self.engine.load()['assignments']['architecture_pre']['status'],'unavailable')
    def test_AT006_no_receipt_cannot_complete(self):
        self.plan()
        with self.assertRaisesRegex(Fault,'START_RECEIPT_MISSING'): self.engine.dispatch('architecture_pre',FixtureAdapter(no_start=True))
        self.assertFalse(self.starts()); self.assertFalse((self.root/'outputs/architecture_pre.md').exists())
    def test_AT007_scope_denied_before_any_write(self):
        self.plan()
        bad={'path':'src/forbidden.py','base_sha256':None,'content':'SECRET-CANARY'}
        with self.assertRaisesRegex(Fault,'WRITE_NOT_AUTHORIZED'): self.engine.dispatch('architecture_pre',FixtureAdapter(extra=bad))
        self.assertFalse((self.root/'src/forbidden.py').exists()); self.assertFalse((self.root/'outputs/architecture_pre.md').exists())
    def test_AT007_production_blocks_before_call(self):
        p=self.plan(['production']); self.assertEqual(p['mode'],'blocked')
        with self.assertRaisesRegex(Fault,'RUN_BLOCKED'): self.engine.dispatch('architecture_pre',FixtureAdapter())
        self.assertFalse(self.starts())
    def test_AT008_drift_at_review_rejected(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter())
        h=self.engine.submit('architecture_pre','analysis')
        (self.root/'outputs/architecture_pre.md').write_text('changed\n')
        with self.assertRaises(Fault): self.engine.review(h['handoff_id'],FixtureAdapter())
        with self.assertRaisesRegex(Fault,'SOURCE_DRIFT'): self.engine.ready()
    def test_AT008_task_context_change_blocks(self):
        self.plan(); (self.root/'wiki/workitems/STORY-001.md').write_text('new requirement\n')
        with self.assertRaisesRegex(Fault,'CONTEXT_DRIFT'): self.engine.dispatch('architecture_pre',FixtureAdapter())
    def test_AT010_fake_role_words_not_a_receipt(self):
        self.plan()
        class Pretend(FixtureAdapter):
            def run(self,p,s): return {'outcome':'completed','artifacts':['src/app.py'],'changes':[],'usage':None,'assistance':None}
        with self.assertRaisesRegex(Fault,'START_RECEIPT_MISSING'): self.engine.dispatch('architecture_pre',Pretend())
        self.assertFalse(self.starts())
    def test_AT010_fixture_cannot_enter_real_run(self):
        self.context,self.auth=setup(self.root,kind='real'); self.plan()
        with self.assertRaisesRegex(Fault,'FIXTURE_REAL_MISMATCH'): self.engine.dispatch('architecture_pre',FixtureAdapter())
    def test_AT011_duplicate_receipt_and_submit_idempotent(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter(duplicate=True))
        self.assertEqual(len(self.starts()),1)
        h=self.engine.submit('architecture_pre','analysis'); n=len(self.engine.history())
        self.assertEqual(self.engine.submit('architecture_pre','analysis'),h); self.assertEqual(n,len(self.engine.history()))
    def test_AT011_timeout_retry_preserves_failure(self):
        self.plan()
        with self.assertRaises(Fault): self.engine.dispatch('architecture_pre',FixtureAdapter(fail=True))
        self.engine.retry('architecture_pre'); self.engine.dispatch('architecture_pre',FixtureAdapter())
        d=self.engine.load()['assignments']['architecture_pre']
        self.assertEqual([a['status'] for a in d['attempts']],['failed','completed'])
        self.assertNotIn('SECRET-RAW-ERROR',self.engine.report())
    def test_AT012_parallel_join_requires_all_edges(self):
        self.plan(['database_schema'])
        # Execute until both database and implementation become ready.
        while 'database' not in self.engine.ready():
            s=self.engine.load()
            for n,d in s['assignments'].items():
                if d['status']=='completed':
                    for to,target in s['assignments'].items():
                        if n in target['depends_on']:
                            h=self.engine.submit(n,to)
                            if h['status']=='submitted': self.engine.review(h['handoff_id'],FixtureAdapter())
            r=self.engine.ready()
            if 'database' not in r: self.engine.dispatch(r[0],FixtureAdapter())
        self.engine.dispatch('database',FixtureAdapter()); self.engine.dispatch('implementation',FixtureAdapter())
        hd=self.engine.submit('database','verification'); hi=self.engine.submit('implementation','verification')
        self.engine.review(hd['handoff_id'],FixtureAdapter()); self.assertNotIn('verification',self.engine.ready())
        self.engine.review(hi['handoff_id'],FixtureAdapter()); self.assertIn('verification',self.engine.ready())
    def test_AT013_reopen_same_run_replays_history(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter())
        e=Engine(self.root,'RUN-001'); self.assertEqual(e.load(),self.engine.load()); self.assertEqual(e.report(),self.engine.report())
    def test_AT013_orphan_request_recovers_as_blocked(self):
        self.plan()
        with self.engine.lock():
            s=self.engine.load(); d=s['assignments']['architecture_pre']; d['status']='requested'
            d['attempts'].append({'status':'requested','instance_ref':None})
            self.engine.append(s,'AGENT_INVOCATION_REQUESTED','architecture_pre',after='requested')
        self.assertEqual(self.engine.recover(),['architecture_pre']); self.assertEqual(self.engine.recover(),[])
        self.assertFalse(self.starts())
    def test_AT014_no_content_in_metadata_report(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter())
        self.assertNotIn('Synthetic isolated-test authorization',self.engine.report())
        for row in self.engine.history(): self.assertNotIn('SECRET',json.dumps(row))
    def test_AT014_hash_chain_corruption_detected(self):
        self.plan(); p=self.engine.folder/'000001.json'; x=json.loads(p.read_text()); x['state']['mode']='done'; p.write_text(json.dumps(x))
        with self.assertRaisesRegex(Fault,'JOURNAL_CORRUPT'): self.engine.load()
    def test_live_AT001_gate_never_passes_fixture(self):
        self.plan(); self.complete()
        self.assertFalse(self.engine.check(release=True)['checks_passed'])
        self.assertIn('AT-001:FIXTURE_NOT_LIVE',self.engine.check(release=True)['findings'])
    def test_unknown_signal_not_silently_dropped(self):
        with self.assertRaisesRegex(Fault,'UNKNOWN_SIGNAL'): self.plan(['unknown'])
    def test_auth_no_delegation_denied(self):
        self.auth['allow_delegation']=False; (self.root/'intake/authorization.json').write_text(json.dumps(self.auth))
        with self.assertRaisesRegex(Fault,'AUTH_REQUIRED'): self.plan()
    def test_no_goal_approval_no_execution(self):
        (self.root/'raw/goals/GOAL-001.md').write_text('status: draft\n')
        self.plan()
        with self.assertRaisesRegex(Fault,'GOAL_NOT_APPROVED'): self.engine.dispatch('architecture_pre',FixtureAdapter())
    def test_required_contract_missing(self):
        (self.root/'schema/agent-roles.yaml').unlink()
        with self.assertRaises(Fault): self.plan()
    def test_symlink_and_traversal_denied(self):
        from agent_collaboration import ref
        for p in ('../escape','/etc/passwd','.env','.ai/../escape'):
            with self.assertRaises(Fault): ref(self.root,p,False)
        (self.root/'link').symlink_to('/tmp')
        with self.assertRaises(Fault): ref(self.root,'link/escape',False)
    def test_self_review_rejected(self):
        self.plan(); d=self.engine.dispatch('architecture_pre',FixtureAdapter()); h=self.engine.submit('architecture_pre','analysis')
        with self.assertRaisesRegex(Fault,'SELF_REVIEW'): self.engine.review(h['handoff_id'],FixtureAdapter(instance=d['attempts'][-1]['instance_ref']))
    def test_malformed_review_evidence_fails_closed_and_is_journaled(self):
        self.plan()
        self.engine.dispatch('architecture_pre', FixtureAdapter())
        handoff = self.engine.submit('architecture_pre', 'analysis')
        valid_ref = next(iter(handoff['artifacts']))
        malformed = (
            [[valid_ref]],               # nested list used to raise TypeError
            [{'ref': valid_ref}],         # nested mapping used to raise TypeError
            [valid_ref, valid_ref],       # duplicate reference
            [42],                         # non-string reference
            valid_ref,                    # scalar instead of array
            [],                           # no review evidence
        )
        for refs in malformed:
            with self.subTest(evidence=repr(refs)):
                class MalformedReview(FixtureAdapter):
                    def review(self, packet, started):
                        answer = super().review(packet, started)
                        answer['evidence_refs'] = refs
                        return answer
                with self.assertRaisesRegex(Fault, 'REVIEW_EVIDENCE_REQUIRED'):
                    self.engine.review(handoff['handoff_id'], MalformedReview())
                self.assertEqual(
                    self.engine.history()[-1]['event']['event_type'], 'REVIEW_FAILED')
                self.assertEqual(
                    self.engine.load()['handoffs'][handoff['handoff_id']]['status'],
                    'submitted')
        self.engine.review(handoff['handoff_id'], FixtureAdapter())
        self.assertEqual(
            self.engine.load()['handoffs'][handoff['handoff_id']]['status'],
            'accepted')

    def test_claimed_review_without_start_refused(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter()); h=self.engine.submit('architecture_pre','analysis')
        with self.assertRaisesRegex(Fault,'START_RECEIPT_MISSING'): self.engine.review(h['handoff_id'],FixtureAdapter(no_start=True))
    def test_new_role_selected_without_core_code_change(self):
        path=self.root/'schema/collaboration/registry.json'; r=json.loads(path.read_text())
        r['roles']['interface_expert']={**r['roles']['architect_agent'],'priority':1}; path.write_text(json.dumps(r))
        self.assertEqual(self.plan()['assignments']['architecture_pre']['role'],'interface_expert')
    def test_assistance_generically_links_return_dependency(self):
        self.plan()
        k=self.engine.assist('architecture_pre','product_contract',['src/app.py'],['outputs/assist.md'])
        self.assertEqual(k,self.engine.assist('architecture_pre','product_contract',['src/app.py'],['outputs/assist.md']))
        self.assertIn(k,self.engine.ready()); self.assertNotIn('architecture_pre',self.engine.ready())
        self.engine.dispatch(k,FixtureAdapter()); h=self.engine.submit(k,'architecture_pre'); self.engine.review(h['handoff_id'],FixtureAdapter())
        self.assertIn('architecture_pre',self.engine.ready())
    def test_cycle_rejected(self):
        path=self.root/'schema/collaboration/policy.json'; p=json.loads(path.read_text()); p['steps'][0]['depends_on']=['operations']; path.write_text(json.dumps(p))
        with self.assertRaisesRegex(Fault,'DEPENDENCY_CYCLE'): self.plan()
    def test_protected_write_scope_rejected(self):
        self.context['scopes']['implementation']=['schema/rules']; (self.root/'intake/context.json').write_text(json.dumps(self.context))
        with self.assertRaisesRegex(Fault,'PROTECTED_WRITE_SCOPE'): self.plan()
    def test_real_receipt_cannot_be_injected_by_custom_adapter(self):
        setup(self.root,kind='real'); self.plan()
        fake=FixtureAdapter(); fake.sample_kind='real'; fake.source='codex_app_server'; fake.mode='runtime_session'
        with self.assertRaisesRegex(Fault,'UNTRUSTED_ADAPTER'): self.engine.dispatch('architecture_pre',fake)
    def test_unapproved_test_command_refused(self):
        self.plan()
        with self.assertRaisesRegex(Fault,'COMMAND_NOT_AUTHORIZED'): self.engine.validate(['true'])
    def test_artifact_archive_and_metadata_private(self):
        self.plan(); d=self.engine.dispatch('architecture_pre',FixtureAdapter())
        h=next(iter(d['result_refs'].values())); p=self.root/'.ai/collaboration/artifacts'/h
        self.assertEqual(p.stat().st_mode & 0o777,0o600)
        self.assertEqual((self.root/'.ai/collaboration/.gitignore').read_text(),'*\n')
    def test_retry_limit_and_single_writer(self):
        self.plan()
        for _ in range(3):
            with self.assertRaises(Fault): self.engine.dispatch('architecture_pre',FixtureAdapter(fail=True))
            if _<2: self.engine.retry('architecture_pre')
        with self.assertRaisesRegex(Fault,'RETRY_LIMIT'): self.engine.retry('architecture_pre')
    def test_legitimate_owned_source_change_updates_expected_hash(self):
        self.context['scopes']['implementation']=['src/app.py']; (self.root/'intake/context.json').write_text(json.dumps(self.context))
        self.plan(['copy_only']); self.engine.dispatch('implementation',FixtureAdapter())
        self.engine.freshness(self.engine.load())
    def test_out_of_band_source_change_rejected(self):
        self.plan(); (self.root/'src/app.py').write_text('VALUE=2\n')
        with self.assertRaisesRegex(Fault,'SOURCE_DRIFT'): self.engine.ready()


if __name__=='__main__': unittest.main()
