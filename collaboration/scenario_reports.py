#!/usr/bin/env python3
"""Cross-scenario trace fixtures, visibly distinct from authenticated Agent runs."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'collaboration'),str(ROOT/'observability')]
from test_collaboration import setup,FixtureAdapter
from agent_collaboration import Engine,Fault,drive

class Unavailable(FixtureAdapter):
    def run(self,packet,started): raise Fault('RUNTIME_UNAVAILABLE')

def generate(output):
    target=Path(output).resolve()
    if target.exists(): raise ValueError('OUTPUT_EXISTS')
    target.mkdir(parents=True)
    summaries=[]
    cases=[('ui',['ui_flow']),('api',['api_contract']),('bug',['bugfix']),('operations',['runtime_change']),
           ('rework',['api_contract']),('unavailable',['api_contract']),('no-receipt',['api_contract']),
           ('scope-denied',['copy_only']),('production-blocked',['production'])]
    for label,signals in cases:
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);context,auth=setup(root,signals)
            engine=Engine(root,'RUN-001');engine.create('intake/context.json')
            diagnostic=None
            try:
                if label=='rework':
                    engine.dispatch('architecture_pre',FixtureAdapter())
                    handoff=engine.submit('architecture_pre','analysis')
                    engine.review(handoff['handoff_id'],FixtureAdapter(decision='changes_requested'))
                    engine.retry('architecture_pre');drive(engine,FixtureAdapter())
                elif label=='unavailable':engine.dispatch('architecture_pre',Unavailable())
                elif label=='no-receipt':engine.dispatch('architecture_pre',FixtureAdapter(no_start=True))
                elif label=='scope-denied':
                    engine.dispatch('implementation',FixtureAdapter(extra={'path':'schema/agent-roles.yaml','base_sha256':None,'content':'unauthorized'}))
                elif label=='production-blocked': engine.dispatch('architecture_pre',FixtureAdapter())
                else:drive(engine,FixtureAdapter())
                engine.validate(auth['validation_commands'][0]);engine.finish()
            except Fault as exc:diagnostic=str(exc)
            rows=engine.history();state=engine.load()
            item={'scenario':label,'sample_kind':'fixture','diagnostic':diagnostic,'event_count':len(rows),
                  'roles':sorted({v['role'] for v in state['assignments'].values()}),
                  'simulated_start_receipts':len([r for r in rows if r['event']['event_type']=='AGENT_STARTED']),
                  'native_agent_count':0,'live_acceptance':'NOT_RUN','structural_result':engine.check(),
                  'release_result':engine.check(release=True)}
            if label in ('ui','api','bug','operations','rework') and not item['structural_result']['checks_passed']:
                raise RuntimeError('FIXTURE_PROTOCOL_FAILED')
            if label in ('unavailable','no-receipt','production-blocked') and item['simulated_start_receipts']!=0:
                raise RuntimeError('FALSE_START')
            if item['release_result']['checks_passed']: raise RuntimeError('FALSE_RELEASE')
            (target/(label+'.md')).write_text(engine.report())
            (target/(label+'.json')).write_text(json.dumps(item,indent=2)+'\n')
            summaries.append(item)
    (target/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    return summaries
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);args=p.parse_args()
    print(json.dumps(generate(args.output),indent=2))
