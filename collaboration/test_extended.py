"""Additional concurrency, privacy, dynamic-expert and truth-boundary tests."""
import json
import threading
import unittest
from pathlib import Path
import test_collaboration as fixtures
FixtureAdapter=fixtures.FixtureAdapter
setup=fixtures.setup
from agent_collaboration import Engine, Fault, drive, file_hash

# Do not inherit ProtocolTests, which would silently duplicate its test count.
class ExtraTests(unittest.TestCase):
    setUp=fixtures.ProtocolTests.setUp; tearDown=fixtures.ProtocolTests.tearDown; plan=fixtures.ProtocolTests.plan
    def test_optional_database_falls_back_when_disabled(self):
        p=self.root/'schema/collaboration/registry.json'; r=json.loads(p.read_text())
        r['roles']['database_agent']['enabled']=False; p.write_text(json.dumps(r))
        s=self.plan(['database_schema'])
        self.assertEqual(s['assignments']['database_design']['role'],'architect_agent')
        self.assertEqual(s['assignments']['database']['role'],'developer_agent')
        self.assertEqual(s['skipped_roles']['database_agent'],'project_disabled')
    def test_project_rules_and_skill_content_bound(self):
        self.plan(); packet=self.engine.packet(self.engine.load(),'architecture_pre')
        names={d['ref'] for d in packet['documents']}
        self.assertIn('AGENTS.md',names)
        self.assertIn('.ai/skills/story-to-tasks/SKILL.md',names)
        (self.root/'AGENTS.md').write_text('changed policy')
        with self.assertRaisesRegex(Fault,'CONTEXT_DRIFT'): self.engine.dispatch('architecture_pre',FixtureAdapter())
    def test_parallel_same_write_scope_is_blocked(self):
        policy=self.root/'schema/collaboration/policy.json'; data=json.loads(policy.read_text())
        data['steps']=[{'id':'left','capability':'implementation_analysis','signals':['api_contract'], 'scope_key':'left','depends_on':[], 'deliverable':'design','phase':'design'},
                       {'id':'right','capability':'implementation_analysis','signals':['api_contract'], 'scope_key':'right','depends_on':[], 'deliverable':'design','phase':'design'}]
        policy.write_text(json.dumps(data)); self.context['scopes']={'left':['outputs/shared.md'],'right':['outputs/shared.md']}
        (self.root/'intake/context.json').write_text(json.dumps(self.context)); self.plan()
        entered=threading.Event(); finish=threading.Event(); errors=[]
        class Slow(FixtureAdapter):
            def run(me,packet,started):
                result=super().run(packet,started); entered.set(); finish.wait(10); return result
        def work():
            try:self.engine.dispatch('left',Slow())
            except Exception as e: errors.append(e)
        thread=threading.Thread(target=work); thread.start(); self.assertTrue(entered.wait(5))
        try:
            with self.assertRaisesRegex(Fault,'NOT_READY'): self.engine.dispatch('right',FixtureAdapter())
        finally: finish.set(); thread.join(10)
        self.assertFalse(errors); self.assertEqual(self.engine.load()['assignments']['left']['status'],'completed')
        self.assertEqual(self.engine.load()['assignments']['right']['attempt'],0)
    def test_interrupted_apply_reserves_writer_until_recovery(self):
        self.plan(['copy_only'])
        with self.engine.lock():
            state=self.engine.load(); d=state['assignments']['implementation']
            d['status']='applying'; d['attempt']=1; d['attempts']=[{'status':'applying','instance_ref':None}]
            self.engine.append(state,'ARTIFACT_APPLY_STARTED','implementation',after='applying')
        self.assertEqual(self.engine.ready(),[])
        self.assertEqual(self.engine.recover(),['implementation'])
        self.assertEqual(self.engine.load()['assignments']['implementation']['status'],'blocked')
    def test_assistance_from_actual_result_is_bounded_and_resumable(self):
        self.plan(['copy_only'])
        class NeedsHelp(FixtureAdapter):
            def run(me,packet,started):
                me.receipt(started)
                return {'outcome':'needs_assistance','changes':[],'artifacts':[],'usage':None,
                        'assistance':{'capability':'architecture_review','evidence_refs':['src/app.py'],'write_paths':['outputs/help.md']}}
        self.engine.dispatch('implementation',NeedsHelp())
        s=self.engine.load(); helpers=[n for n in s['assignments'] if n.startswith('assist-')]
        self.assertEqual(len(helpers),1)
        self.assertEqual(s['assignments']['implementation']['status'],'proposed')
        self.assertEqual(self.engine.ready(),helpers)
        drive(self.engine,FixtureAdapter()); s=self.engine.load()
        self.assertEqual(s['assignments']['implementation']['status'],'completed')
        self.assertEqual(s['assignments']['implementation']['attempt'],2)
        self.assertIn('ASSISTANCE_PROPOSED',[r['event']['event_type'] for r in self.engine.history()])
    def test_assistance_rejects_protected_governance(self):
        self.plan(['copy_only'])
        with self.assertRaises(Fault):
            self.engine.assist('implementation','architecture_review',['src/app.py'],['schema/agent-roles.yaml'])
    def test_receiver_start_receipt_is_preserved(self):
        self.plan(); self.engine.dispatch('architecture_pre',FixtureAdapter())
        h=self.engine.submit('architecture_pre','analysis'); self.engine.review(h['handoff_id'],FixtureAdapter())
        starts=[r['event'] for r in self.engine.history() if r['event']['event_type']=='REVIEW_STARTED']
        self.assertEqual(len(starts),1); self.assertTrue(starts[0]['agent_instance_ref'].startswith('FIX-'))
    def test_real_behavior_change_cannot_bypass_existing_tdd(self):
        self.context['sample_kind']='real'; self.auth['sample_kind']='real'
        (self.root/'intake/context.json').write_text(json.dumps(self.context)); (self.root/'intake/authorization.json').write_text(json.dumps(self.auth))
        self.plan(); self.assertIn('TDD_BINDING_REQUIRED',self.engine.check()['findings'])
    def test_secret_is_not_in_trace_when_source_contains_it(self):
        (self.root/'src/app.py').write_text('VALUE="SECRET-CANARY-never-log"\n')
        self.plan(['copy_only']); drive(self.engine,FixtureAdapter())
        self.assertNotIn('SECRET-CANARY',self.engine.report())
        for path in (self.root/'.ai/collaboration/runs').rglob('*.json'):
            self.assertNotIn('SECRET-CANARY',path.read_text())
    def test_ref_rejects_markdown_injection_and_control_characters(self):
        from agent_collaboration import ref
        for name in ('src/a\nSECRET','src/a|b','src/a`b'):
            with self.assertRaisesRegex(Fault,'INVALID_REF'): ref(self.root,name,False)
    def test_event_bridge_remains_opt_in(self):
        import harness_observe as obs
        self.plan(['copy_only']); self.assertFalse((self.root/'.ai/observability/events').exists())
        obs.configure(self.root,True,sample_kind='fixture')
        drive(self.engine,FixtureAdapter())
        events=list((self.root/'.ai/observability/events').glob('*.json'))
        self.assertTrue(events)
        for p in events:
            e=json.loads(p.read_text()); self.assertEqual(e['type'],'collaboration_transition')
            self.assertEqual(e['sample_kind'],'fixture'); self.assertEqual(e['source'],'collaboration')

if __name__=='__main__': unittest.main()
