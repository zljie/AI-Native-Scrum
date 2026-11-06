"""Real pipe/process tests against a protocol fixture, NOT a live Codex model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from codex_adapter import CodexAdapter
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
  send({'method':'item/completed','params':{'threadId':thread,'turnId':turn,'item':{'type':'agentMessage','text':json.dumps(answer)}}})
  if mode!='no_usage':
   send({'method':'thread/tokenUsage/updated','params':{'threadId':'thread-fixture','tokenUsage':{'total':{'inputTokens':100,'outputTokens':20}}}})
  status='failed' if mode=='failed' else 'completed'
  send({'method':'turn/completed','params':{'threadId':'thread-fixture','turn':{'id':'turn-fixture','status':status}}})
 elif m=='turn/interrupt': send({'id':q['id'],'result':{}})
'''


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.server=self.root/'server.py'; self.server.write_text(SERVER)
        self.packet={'documents':[{'ref':'src/app.py','text':'X=1','sha256':'a'*64}], 'role':'architect_agent'}
    def tearDown(self): self.tmp.cleanup()
    def adapter(self,mode):
        def transport():
            return subprocess.Popen([sys.executable,str(self.server),mode],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True,bufsize=1)
        return CodexAdapter(self.root,timeout=2,transport=transport)
    def test_actual_protocol_io_and_usage(self):
        receipts=[]; a=self.adapter('ok'); r=a.run(self.packet,receipts.append)
        self.assertEqual(a.sample_kind,'fixture'); self.assertEqual(len(receipts),1)
        self.assertEqual(r['usage'],{'input_tokens':100,'output_tokens':20})
        self.assertNotIn('thread-fixture',json.dumps(receipts))
    def test_readonly_review_separate_receipt(self):
        receipts=[]; r=self.adapter('ok').review(self.packet,receipts.append)
        self.assertEqual(r['decision'],'accepted'); self.assertTrue(receipts)
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
