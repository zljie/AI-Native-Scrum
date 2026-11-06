#!/usr/bin/env python3
"""Isolated fixture-agent demo with real SQLite migrations and bound RED/GREEN tests.
Never uses production data, accounts, native model sessions or simulated token usage.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'collaboration'),str(ROOT/'observability')]
from test_collaboration import setup, FixtureAdapter
from agent_collaboration import Engine, drive, Fault, file_hash
import harness_observe as obs

INITIAL='''import sqlite3
from pathlib import Path

def connect():
    db=sqlite3.connect(':memory:')
    db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE equipment (id INTEGER PRIMARY KEY, name TEXT NOT NULL)')
    db.execute("INSERT INTO equipment VALUES (1, 'legacy pump')")
    return db

def migrate(db):
    names={row[1] for row in db.execute('PRAGMA table_info(equipment)')}
    if 'maintenance_grade' not in names:
        db.executescript((Path(__file__).resolve().parents[1]/'migrations/001_grade.sql').read_text())

def list_equipment(db, grade=None):
    return [{'id':r['id'],'name':r['name'],'maintenance_grade':None} for r in db.execute('SELECT * FROM equipment')]

def set_grade(db, device_id, grade, actor_role='editor'):
    return False
'''
TARGET=INITIAL[:INITIAL.index('def list_equipment')]+'''def list_equipment(db, grade=None):
    if grade is not None and grade not in ('A','B','C'):
        raise ValueError('invalid grade')
    if grade is None:
        rows=db.execute('SELECT id,name,maintenance_grade FROM equipment ORDER BY id')
    else:
        rows=db.execute('SELECT id,name,maintenance_grade FROM equipment WHERE maintenance_grade=? ORDER BY id',(grade,))
    return [dict(r) for r in rows]

def set_grade(db, device_id, grade, actor_role='editor'):
    if actor_role != 'editor': raise PermissionError('editor required')
    if grade is not None and grade not in ('A','B','C'): raise ValueError('invalid grade')
    with db:
        result=db.execute('UPDATE equipment SET maintenance_grade=? WHERE id=?',(grade,device_id))
        if result.rowcount != 1: raise ValueError('device missing')
    return True
'''
SQL="ALTER TABLE equipment ADD COLUMN maintenance_grade TEXT CHECK(maintenance_grade IS NULL OR maintenance_grade IN ('A','B','C'));\n"
TESTS='''import sqlite3
import unittest
from src.equipment import connect,migrate,list_equipment,set_grade

class EquipmentTests(unittest.TestCase):
    def setUp(self):
        self.db=connect(); migrate(self.db)
    def tearDown(self): self.db.close()
    def test_schema_and_legacy_identity(self):
        self.assertIn('maintenance_grade',{r[1] for r in self.db.execute('PRAGMA table_info(equipment)')})
        self.assertEqual(list_equipment(self.db),[{'id':1,'name':'legacy pump','maintenance_grade':None}])
    def test_update_and_filter(self):
        self.assertTrue(set_grade(self.db,1,'A'))
        self.assertEqual(len(list_equipment(self.db,'A')),1)
        self.assertEqual(list_equipment(self.db,'B'),[])
    def test_illegal_value_rejected(self):
        with self.assertRaises(ValueError): set_grade(self.db,1,'INVALID')
        self.assertIsNone(list_equipment(self.db)[0]['maintenance_grade'])
    def test_null_clears(self):
        self.assertTrue(set_grade(self.db,1,'B'))
        self.assertTrue(set_grade(self.db,1,None))
        self.assertIsNone(list_equipment(self.db)[0]['maintenance_grade'])
    def test_repeat_migration(self):
        self.assertIn('maintenance_grade',{r[1] for r in self.db.execute('PRAGMA table_info(equipment)')})
        migrate(self.db); migrate(self.db)
        self.assertEqual(len(list_equipment(self.db)),1)
    def test_missing_device(self):
        with self.assertRaises(ValueError): set_grade(self.db,404,'A')
    def test_viewer_denied(self):
        with self.assertRaises(PermissionError): set_grade(self.db,1,'A',actor_role='viewer')
    def test_database_constraint(self):
        self.assertIn('maintenance_grade',{r[1] for r in self.db.execute('PRAGMA table_info(equipment)')})
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("UPDATE equipment SET maintenance_grade='INVALID'")
if __name__=='__main__': unittest.main()
'''

class DomainFixture(FixtureAdapter):
    def run(self,packet,started):
        result=super().run(packet,started)
        name=packet['delegation_id']
        pair={'test_design':('tests/test_equipment.py',TESTS),
              'database':('migrations/001_grade.sql',SQL),
              'implementation':('src/equipment.py',TARGET)}.get(name)
        if pair:
            path,text=pair
            prior=next((d['sha256'] for d in packet['documents'] if d['ref']==path),None)
            result['changes'].append({'path':path,'base_sha256':prior,'content':text})
        return result

def prepare(root):
    context,auth=setup(root,['database_schema','business_rule','api_contract','ui_flow'])
    # Install real existing evidence tool via the actual self-contained bootstrap.
    result=subprocess.run(['bash',str(ROOT/'initdir.sh')],cwd=root,capture_output=True,text=True,timeout=120)
    if result.returncode: raise RuntimeError('BOOTSTRAP_FAILED')
    (root/'tests/test_sample.py').unlink()
    for name,text in [('src/equipment.py',INITIAL),('migrations/001_grade.sql','SELECT 1;\n')]:
        p=root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
    context['inputs']=['src/equipment.py','migrations/001_grade.sql']
    context['signal_evidence']={s:['src/equipment.py'] for s in context['signals']}
    context['scopes']['test_design'].append('tests/test_equipment.py')
    context['scopes']['database'].append('migrations/001_grade.sql')
    context['scopes']['implementation'].append('src/equipment.py')
    auth['write_paths']+=['tests','migrations']
    cmd=[sys.executable,'-m','unittest','discover','-s','tests','-v']
    auth['validation_commands']=[cmd]
    context['verification']={'tests':['tests/test_equipment.py'], 'inputs':['src','migrations','wiki/workitems/STORY-001.md'],
                             'covers':['STORY-001#TC-P-01','STORY-001#TC-N-01'],'command':cmd}
    (root/'intake/context.json').write_text(json.dumps(context,indent=2))
    (root/'intake/authorization.json').write_text(json.dumps(auth,indent=2))
    obs.configure(root,True,sample_kind='fixture')
    engine=Engine(root,'RUN-001'); engine.create('intake/context.json')
    return engine,auth

def run_demo(output):
    output=Path(output).resolve()
    if output.exists(): raise ValueError('OUTPUT_EXISTS')
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='ans-collaboration-fixture-') as tmp:
        project=Path(tmp)/'project'; project.mkdir()
        engine,auth=prepare(project)
        drive(engine,DomainFixture(),max_steps=80)
        engine.validate(auth['validation_commands'][0]); result=engine.finish()
        release=engine.check(release=True)
        if not result['checks_passed'] or release['checks_passed']:
            raise RuntimeError('DEMO_BOUNDARY_FAILED:'+json.dumps(result))
        state=engine.load()
        (output/'trace.md').write_text(engine.report())
        (output/'summary.json').write_text(json.dumps({'schema':'candidate-demo/v1','sample_kind':'fixture',
             'engineering_protocol':result,'release_gate':release,'domain_tests':8,'real_agent_acceptance':'NOT_RUN',
             'actual_roles':sorted({d['role'] for d in state['assignments'].values()}),
             'events':len(engine.history()),'handoffs':len(state['handoffs']),
             'tdd':engine.tdd_status(),'model_tokens':None},indent=2)+'\n')
        # Synthetic, isolated evidence only; these exports contain no user credentials/data.
        shutil.copytree(project/'raw/evidence',output/'evidence')
        shutil.copytree(project/'.ai/collaboration/runs',output/'fixture-journal')
        shutil.copytree(project/'src',output/'sample-source')
        shutil.copytree(project/'tests',output/'sample-tests')
        shutil.copytree(project/'migrations',output/'sample-migrations')
    return json.loads((output/'summary.json').read_text())

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',required=True); args=p.parse_args()
    print(json.dumps(run_demo(args.output),indent=2)); return 0
if __name__=='__main__': sys.exit(main())
