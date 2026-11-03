#!/usr/bin/env python3
"""Bind a completed real-browser example report to generated governance files."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

repo=Path(__file__).resolve().parents[1]
example=repo/'examples/codex-list-contract'
report=example/'test-results/contract-result.json'
assert report.is_file(), 'Run real browser tests first; no report means no acceptance'
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    subprocess.run(['bash',str(repo/'initdir.sh')],cwd=root,check=True,stdout=subprocess.DEVNULL)
    shutil.copytree(example,root/'example',ignore=shutil.ignore_patterns('node_modules','test-results'))
    page={'id':'demo-list','route':'file:///example/index.html','sources':['example/index.html','example/package-lock.json'], 'tests':['example/tests/list.spec.cjs','example/contract-reporter.cjs','example/playwright.config.cjs'], 'fieldMapping':{'createdBy':'fixture.author','updatedAt':'fixture.updated'}}
    (root/'schema/ui/pages.json').write_text(json.dumps({'pages':[page]}))
    tool=root/'.ai/tools/check_ui_contracts.py'
    for mode in ('snapshot','verify'):
        subprocess.run(['python3',str(tool),mode,'--report',str(report),'--evidence',str(root/'evidence.json')],cwd=root,check=True)
print('PASS: actual example browser report bound to current example and generated rule contents')
