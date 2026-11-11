"""Real pipe/process tests against a protocol fixture, NOT a live Codex model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from codex_adapter import CodexAdapter, NativeProof
from agent_collaboration import Fault

SERVER = r'''
import sys,json,time
mode=sys.argv[1]
def send(d): print(json.dumps(d),flush=True)
for line in sys.stdin:
 q=json.loads(line); m=q.get('method')
 if m=='initialize': send({'id':q['id'],'result':{'userAgent':'fixture'}})
 elif m=='thread/start':
  assert q['params']['sandbox']=='read-only'
  send({'id':q['id'],'result':{'thread':{'id':'thread-fixture'}}})
 elif m=='turn/start':
  assert q['params']['sandboxPolicy']['type']=='readOnly'
  assert q['params']['approvalPolicy']=='never'
  if mode=='reject': send({'id':q['id'],'error':{'message':'SECRET-ERROR'}}); continue
  if mode=='no_receipt': time.sleep(10); continue
  send({'id':q['id'],'result':{'turn':{'id':'turn-fixture','status':'inProgress','items':[]}}})
  if mode=='timeout': time.sleep(10); continue
  if mode=='approval': send({'id':50,'method':'item/commandExecution/requestApproval','params':{'command':'SECRET-COMMAND'}}); continue
  thread='wrong-thread' if mode=='wrong_thread' else 'thread-fixture'
  turn='wrong-turn' if mode=='wrong_turn' else 'turn-fixture'
  schema=q['params']['outputSchema']
  if 'decision' in schema['properties']:
   answer={'decision':'accepted','reason_code':'CHECKED','evidence_refs':['src/app.py']}
  else: answer={'outcome':'completed','changes':[],'artifacts':['src/app.py'],'assistance':None}

  if mode in ('native_child', 'native_without_child', 'native_incomplete',
              'native_late_completion', 'native_late_wrong_turn', 'native_late_wrong_path',
              'native_late_unfinished'):
   if mode!='native_without_child':
    send({'method':'item/completed','params':{
     'threadId':'thread-fixture','turnId':'turn-fixture',
     'item':{'type':'subAgentActivity','id':'sub-fixture-1','kind':'started',
             'agentThreadId':'child-fixture','agentPath':'/root/architecture_pre'}}})
    if mode=='native_child':
     send({'method':'item/completed','params':{
      'threadId':'thread-fixture','turnId':'turn-fixture',
      'item':{'type':'subAgentActivity','id':'sub-fixture-2','kind':'completed',
              'agentThreadId':'child-fixture','agentPath':'/root/architecture_pre'}}})
  send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'type':'agentMessage','text':json.dumps(answer)}}})
  if mode!='no_usage':
   send({'method':'thread/tokenUsage/updated','params':{'threadId':'thread-fixture','tokenUsage':{'total':{'inputTokens':100,'outputTokens':20}}}})
  status='failed' if mode=='failed' else 'completed'
  send({'method':'turn/completed','params':{'threadId':'thread-fixture','turn':{'id':'turn-fixture','status':status}}})
  if mode in ('native_late_completion', 'native_late_wrong_turn', 'native_late_wrong_path'):
   send({'method':'item/completed','params':{
    'threadId':'thread-fixture',
    'turnId':'wrong-turn' if mode=='native_late_wrong_turn' else 'turn-fixture',
    'item':{'type':'subAgentActivity','id':'sub-fixture-2','kind':'completed',
            'agentThreadId':'child-fixture',
            'agentPath':'/root/developer' if mode=='native_late_wrong_path' else '/root/architecture_pre'}}})
 elif m=='turn/interrupt': send({'id':q['id'],'result':{}})
'''


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.server=self.root/'server.py'; self.server.write_text(SERVER)
        self.packet={'documents':[{'ref':'src/app.py','text':'X=1','sha256':'a'*64}], 'role':'architect_agent'}
    def tearDown(self): self.tmp.cleanup()
    def adapter(self,mode,native=False):
        def transport():
            return subprocess.Popen([sys.executable,str(self.server),mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
        return CodexAdapter(self.root,timeout=2,transport=transport,
                            native_subagent=native)
    def test_actual_protocol_io_and_usage(self):
        receipts=[]; a=self.adapter('ok'); r=a.run(self.packet,receipts.append)
        self.assertEqual(a.sample_kind,'fixture'); self.assertEqual(len(receipts),1)
        self.assertEqual(r['usage'],{'input_tokens':100,'output_tokens':20})
        self.assertNotIn('thread-fixture',json.dumps(receipts))
    def test_readonly_review_separate_receipt(self):
        receipts=[]; r=self.adapter('ok').review(self.packet,receipts.append)
        self.assertEqual(r['decision'],'accepted'); self.assertTrue(receipts)
        self.assertEqual(r['usage'], {'input_tokens': 100, 'output_tokens': 20})
    def test_review_missing_usage_is_unknown(self):
        result = self.adapter('no_usage').review(self.packet, lambda _: None)
        self.assertIsNone(result['usage'])

    def test_native_activity_must_show_real_child_lifecycle(self):
        receipts = []
        a = self.adapter('native_child', native=True)
        self.assertEqual(a.sample_kind, 'fixture')
        self.assertEqual(a.mode, 'fixture')
        out = a.run(self.packet, receipts.append)
        self.assertEqual(out['outcome'], 'completed')
        self.assertEqual(len(receipts), 1)
        self.assertNotIn('child-fixture', json.dumps(receipts))
        for mode in ('native_without_child', 'native_incomplete'):
            with self.subTest(mode=mode):
                receipts = []
                with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_NOT_VERIFIED'):
                    self.adapter(mode, native=True).run(self.packet, receipts.append)
                self.assertFalse(receipts)


    def test_native_child_completion_after_parent_turn_is_verified(self):
        # App-server may send V2 child completion after turn/completed.
        # The injected transport is still fixture; this is not live native proof.
        receipts = []
        a = self.adapter('native_late_completion', native=True)
        out = a.run(self.packet, receipts.append)
        self.assertEqual(out['outcome'], 'completed')
        self.assertEqual(out['usage'], {'input_tokens': 100, 'output_tokens': 20})
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]['sample_kind'], 'fixture')
        self.assertNotIn('child-fixture', json.dumps(receipts))

    def test_late_native_completion_requires_matching_parent_turn(self):
        receipts = []
        with self.assertRaisesRegex(Fault, 'RUNTIME_TURN_MISMATCH'):
            self.adapter('native_late_wrong_turn', native=True).run(
                self.packet, receipts.append)
        self.assertFalse(receipts)

    def test_native_v2_late_child_path_change_is_rejected(self):
        receipts = []
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_PATH_MISMATCH'):
            self.adapter('native_late_wrong_path', native=True).run(
                self.packet, receipts.append)
        self.assertFalse(receipts)

    def test_native_v2_completion_cannot_precede_start(self):
        proof = NativeProof('parent-thread')
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_LIFECYCLE_INVALID'):
            proof.observe({'type': 'subAgentActivity', 'kind': 'completed',
                           'agentThreadId': 'child-thread', 'agentPath': '/root/architecture_pre'})

    def test_native_v2_interruption_disqualifies_completion(self):
        proof = NativeProof('parent-thread')
        event = {'type': 'subAgentActivity', 'agentThreadId': 'child-thread',
                 'agentPath': '/root/architecture_pre'}
        proof.observe({**event, 'kind': 'started'})
        proof.observe({**event, 'kind': 'interrupted'})
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_LIFECYCLE_INVALID'):
            proof.observe({**event, 'kind': 'completed'})
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_NOT_VERIFIED'):
            proof.evidence()

    def test_late_native_completion_never_invented(self):
        receipts = []
        a = self.adapter('native_late_unfinished', native=True)
        a.timeout = 0.4
        with self.assertRaisesRegex(Fault, 'NATIVE_CHILD_NOT_VERIFIED'):
            a.run(self.packet, receipts.append)
        self.assertFalse(receipts)

    def test_native_wait_finished_without_completed_child_is_not_proof(self):
        proof = NativeProof("parent-thread")
        proof.observe({"type": "collabAgentToolCall", "tool": "spawnAgent",
                       "status": "completed", "senderThreadId": "parent-thread",
                       "receiverThreadIds": ["child-thread"], "id": "call-spawn"})
        proof.observe({"type": "collabAgentToolCall", "tool": "wait",
                       "status": "completed", "senderThreadId": "parent-thread",
                       "receiverThreadIds": ["child-thread"],
                       "agentsStates": {"child-thread": {"status": "running"}}})
        with self.assertRaisesRegex(Fault, "NATIVE_CHILD_NOT_VERIFIED"):
            proof.evidence()
        proof.observe({"type": "collabAgentToolCall", "tool": "wait",
                       "status": "completed", "senderThreadId": "parent-thread",
                       "receiverThreadIds": ["child-thread"],
                       "agentsStates": {"child-thread": {"status": "completed"}}})
        self.assertEqual(proof.evidence(), "child-thread")

    def test_no_receipt_no_start(self):
        receipts=[]
        with self.assertRaisesRegex(Fault,'RUNTIME_TIMEOUT'): self.adapter('no_receipt').run(self.packet,receipts.append)
        self.assertFalse(receipts)
    def test_timeout_after_start_keeps_receipt(self):
        receipts=[]
        with self.assertRaisesRegex(Fault,'RUNTIME_TIMEOUT'): self.adapter('timeout').run(self.packet,receipts.append)
        self.assertEqual(len(receipts),1)
    def test_engine_refusal_is_sanitized(self):
        receipts=[]
        with self.assertRaisesRegex(Fault,'RUNTIME_REJECTED'): self.adapter('reject').run(self.packet,receipts.append)
        self.assertFalse(receipts)
    def test_approval_never_accepted_automatically(self):
        with self.assertRaisesRegex(Fault,'HUMAN_APPROVAL_REQUIRED'): self.adapter('approval').run(self.packet,lambda _:None)
    def test_thread_and_turn_mismatch_rejected(self):
        for mode in ('wrong_thread','wrong_turn'):
            with self.subTest(mode=mode),self.assertRaises(Fault): self.adapter(mode).run(self.packet,lambda _:None)
    def test_provider_failure_cannot_complete(self):
        with self.assertRaisesRegex(Fault,'TURN_FAILED'): self.adapter('failed').run(self.packet,lambda _:None)
    def test_missing_usage_is_unknown(self):
        self.assertIsNone(self.adapter('no_usage').run(self.packet,lambda _:None)['usage'])
    def test_snapshot_ref_cannot_escape(self):
        self.packet['documents'][0]['ref']='../secret'
        with self.assertRaisesRegex(Fault,'CONTEXT_PATH'): self.adapter('ok').run(self.packet,lambda _:None)


if __name__=='__main__': unittest.main()
