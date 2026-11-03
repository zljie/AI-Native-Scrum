#!/usr/bin/env python3
"""Exercise generated Codex entry, evidence freshness and fail-closed behavior."""
import json
from pathlib import Path
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    subprocess.run(['bash', str(REPO / 'initdir.sh')], cwd=root, check=True, stdout=subprocess.DEVNULL)
    skill = root / '.agents/skills/frontend-list-contract/SKILL.md'
    assert skill.is_file() and 'name: frontend-list-contract' in skill.read_text()
    assert 'schema/ui/list-page.json' in (root / 'AGENTS.md').read_text()
    (root / 'page.html').write_text('demo source')
    (root / 'test.js').write_text('demo tests')
    report = root / 'report.json'
    data = {'pageIds':['demo'],'exitCode':0,'testsPassed':1,'testsSkipped':0,'browser':'chromium','viewport':[1280,720], 'command':'fixture (not browser execution)', 'checks':['layout','tail-columns','search-behavior','pagination-behavior']}
    report.write_text(json.dumps(data))
    tool = root / '.ai/tools/check_ui_contracts.py'
    def run(mode, success):
        result = subprocess.run(['python3',str(tool),mode,'--report',str(report),'--evidence',str(root/'evidence.json')],cwd=root,capture_output=True,text=True)
        assert (result.returncode == 0) == success, result.stdout+result.stderr
    run('snapshot',False) # empty registry cannot establish acceptance
    registry={'pages':[{'id':'demo','route':'/demo','sources':['page.html'],'tests':['test.js'],'fieldMapping':{'createdBy':'fixture.creator','updatedAt':'fixture.changed'}}]}
    (root/'schema/ui/pages.json').write_text(json.dumps(registry))
    run('snapshot',True)
    run('verify',True)
    (root/'page.html').write_text('changed source')
    run('verify',False)
    run('snapshot',True)
    (root/'test.js').unlink()
    run('verify',False)
    (root/'test.js').write_text('demo tests')
    data['testsSkipped']=1
    report.write_text(json.dumps(data))
    run('snapshot',False)
    # Normal bootstrap reruns preserve registered project-specific mappings.
    before=(root/'schema/ui/pages.json').read_bytes()
    subprocess.run(['bash',str(REPO/'initdir.sh')],cwd=root,check=True,stdout=subprocess.DEVNULL)
    assert (root/'schema/ui/pages.json').read_bytes()==before
print('PASS: generated Codex entry, empty registry, fresh/stale evidence, missing tests, skipped tests, preservation')
