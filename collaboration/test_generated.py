"""Two-file bootstrap, safe upgrade, schema and actual SQLite evidence integration."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'collaboration')]
import demo
import embed
from schemas import contracts

BASE='9e369347c6b1543deb1b8f3f22e4552fb0c7b560'
BLOBS={'initdir.sh':'3ffbe2991e2ac1c9e3b29f52ec36ca956fcfd55c','00_AI_WARMUP.md':'94bea742b512a46038db70b8d1e95a00d9f13ce3'}

def run(argv,cwd):
    p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True,timeout=180)
    if p.returncode: raise AssertionError(p.stdout[-3000:]+p.stderr[-3000:])
    return p.stdout

def baseline(name):
    p=subprocess.run(['git','show',BASE+':'+name],cwd=ROOT,capture_output=True)
    if p.returncode:
        folder=os.environ.get('ANS_V13_BASELINE_DIR')
        if not folder: raise AssertionError('Need fetched V1.3 commit or exact verified ANS_V13_BASELINE_DIR')
        data=(Path(folder)/name).read_bytes()
    else: data=p.stdout
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual!=BLOBS[name]: raise AssertionError('baseline blob mismatch')
    return data

class GeneratedTests(unittest.TestCase):
    def test_assets_drift_check_and_candidate_version(self):
        self.assertEqual({n for n,t in embed.render(ROOT).items() if (ROOT/n).read_text()!=t},set())
        self.assertIn('FRAMEWORK_VERSION="1.3"',(ROOT/'initdir.sh').read_text())
    def test_fresh_selfcontained_native_entries_and_framework_routes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'project spaces'; root.mkdir()
            for name in ('initdir.sh','00_AI_WARMUP.md'): shutil.copyfile(ROOT/name,root/name)
            run(['bash','initdir.sh'],root)
            for name in ('agent_collaboration.py','codex_adapter.py','project_context.py',
                         'v15_activation.py','v15_graph.py','v15_controller.py'):
                self.assertEqual((root/'.ai/tools'/name).read_bytes(),(ROOT/'collaboration'/name).read_bytes())
            self.assertEqual((root/'docs/v1.5-collaboration.md').read_bytes(),
                             (ROOT/'docs/v1.5-collaboration.md').read_bytes())
            for prefix in ('.ai/skills','.agents/skills','.claude/skills'):
                self.assertTrue((root/prefix/'agent-collaboration/SKILL.md').is_file())
            self.assertTrue((root/'.codex/agents/database_agent.toml').is_file())
            out=run([sys.executable,'.ai/tools/check_framework.py'],root)
            self.assertIn('errors=0',out)
            for name in ('agent_collaboration.py','project_context.py','v15_activation.py',
                         'v15_graph.py','v15_controller.py'):
                run([sys.executable,'.ai/tools/'+name,'--help'],root)
            self.assertFalse((root/'.ai/observability/config.json').exists())
            before={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
            run(['bash','initdir.sh'],root)
            self.assertEqual(before,{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in str(p)})
    def test_v13_upgrade_keeps_local_rules_business_and_version(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'project';root.mkdir(); new=Path(d)/'candidate';new.mkdir()
            for name in ('initdir.sh','00_AI_WARMUP.md'):
                (root/name).write_bytes(baseline(name)); shutil.copyfile(ROOT/name,new/name)
            run(['bash','initdir.sh'],root)
            rules=root/'AGENTS.md'; rules.write_text(rules.read_text()+'\nProject custom constraint: creator uses display name.\n')
            (root/'business.txt').write_text('existing business material')
            old_rules=rules.read_bytes()
            before={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}
            run(['bash',str(new/'initdir.sh'),'--upgrade'],root)
            self.assertEqual(before,{p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()})
            run(['bash',str(new/'initdir.sh'),'--upgrade','--apply'],root)
            self.assertEqual(rules.read_bytes(),old_rules)
            self.assertEqual((root/'business.txt').read_text(),'existing business material')
            self.assertTrue((root/'.ai/tools/agent_collaboration.py').is_file())
            self.assertIn('framework_version: 1.3', (root/'.ai/framework-version').read_text())
            self.assertFalse((root/'.git').exists())
    def test_real_sqlite_red_green_fixture_agents_never_live(self):
        with tempfile.TemporaryDirectory() as d:
            summary=demo.run_demo(Path(d)/'report')
            self.assertTrue(summary['engineering_protocol']['checks_passed'])
            self.assertFalse(summary['release_gate']['checks_passed'])
            self.assertTrue(summary['tdd']['red_current']); self.assertTrue(summary['tdd']['green_current'])
            self.assertEqual(summary['real_agent_acceptance'],'NOT_RUN')
            self.assertIsNone(summary['model_tokens'])
            reds=list((Path(d)/'report/evidence/TASK-001').glob('*-red.json'))
            greens=list((Path(d)/'report/evidence/TASK-001').glob('*-green.json'))
            self.assertEqual(len(reds),1); self.assertEqual(len(greens),1)
            red=json.loads(reds[0].read_text());green=json.loads(greens[0].read_text())
            self.assertTrue(red['valid']); self.assertNotEqual(red['exit_code'],0)
            self.assertTrue(green['valid']); self.assertEqual(green['exit_code'],0)
            self.assertEqual(red['tests'],green['tests']);self.assertEqual(red['command'],green['command'])
    def test_published_schemas_cover_actual_context_handoffs_events(self):
        try: import jsonschema
        except ImportError: self.fail('jsonschema is required for source contract tests (not installed project runtime)')
        from test_collaboration import setup,FixtureAdapter
        from agent_collaboration import Engine,drive
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);context,auth=setup(root)
            schemas=contracts(); jsonschema.validate(context,schemas['task-context']);jsonschema.validate(auth,schemas['authorization'])
            jsonschema.validate(json.loads((root/'schema/collaboration/registry.json').read_text()),schemas['registry'])
            engine=Engine(root,'RUN-001');engine.create('intake/context.json');drive(engine,FixtureAdapter())
            for h in engine.load()['handoffs'].values(): jsonschema.validate(h,schemas['handoff'])
            for row in engine.history(): jsonschema.validate(row['event'],schemas['event'])

if __name__=='__main__': unittest.main()
