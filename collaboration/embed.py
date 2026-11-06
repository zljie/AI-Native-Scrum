#!/usr/bin/env python3
"""Embed candidate assets without promoting FRAMEWORK_VERSION or touching project data."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'collaboration'))
from schemas import contracts
spec = importlib.util.spec_from_file_location('existing_observability_embed', ROOT/'observability/embed.py')
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)

def assets(root):
    result = {'.ai/tools/'+name:(root/'collaboration'/name).read_text() for name in ('agent_collaboration.py','codex_adapter.py')}
    result.update({'schema/collaboration/'+name:(root/'collaboration'/name).read_text() for name in ('registry.json','policy.json')})
    result.update({'schema/collaboration/'+name+'.schema.json':json.dumps(value,indent=2,ensure_ascii=False)+'\n' for name,value in contracts().items()})
    result['schema/roles/database_agent.md']=(root/'collaboration/database_agent.md').read_text()
    result['.codex/agents/database_agent.toml']=(root/'collaboration/database_agent.toml').read_text()
    result['.claude/agents/database_agent.md']='---\nname: database_agent\ndescription: Optional independent database design and migration specialist; use the shared collaboration protocol.\n---\nRead AGENTS.md and schema/roles/database_agent.md. Return only authorized artifacts, current evidence and unresolved risks. Never execute production changes, weaken tests or self-approve.\n'
    for prefix in ('.ai/skills','.agents/skills','.claude/skills'):
        result[prefix+'/agent-collaboration/SKILL.md']=(root/'collaboration/skill.md').read_text()
    result['docs/agent-collaboration.md']=(root/'docs/agent-collaboration.md').read_text()
    result['.ai/collaboration/.gitignore']='*\n'
    return result

def render(root):
    text=(root/'initdir.sh').read_text(); data=assets(root)
    if 'FRAMEWORK_VERSION="1.3"' not in text:
        raise ValueError('candidate requires reviewed version baseline; do not silently promote')
    text=base.add_files(text,'FRAMEWORK_FILES',[x for x in data if not x.endswith('/.gitignore')])
    text=base.add_files(text,'PROJECT_FILES',['.ai/collaboration/.gitignore'])
    blocks=[]
    for index,(name,content) in enumerate(data.items()):
        marker='COLLABORATION_ASSET_'+str(index)
        if marker in content.splitlines(): raise ValueError('delimiter collision')
        blocks.append(f'create_file_if_missing "{name}"\nif [ ! -s "{name}" ]; then\ncat > "{name}" <<\'{marker}\'\n{content.rstrip()}\n{marker}\nfi\n')
    text=base.managed(text,'# === COLLABORATION CANDIDATE BEGIN ===','# === COLLABORATION CANDIDATE END ===', '\n'.join(blocks), before='# ============================================================\n# Framework version\n')
    routes='''# Project-aware professional collaboration (candidate)

For substantive feature/bug/API/UI/data/operations work, first inspect project impacts
and read `.ai/skills/agent-collaboration/SKILL.md`. Use only needed professional roles;
Database Agent is an independent optional expert. Preserve approved scope and existing
RED/GREEN evidence. Coordinator-managed assistance and explicit receiving review replace
role prose. Authorization within scope continues; do not re-ask at every handoff.

| Request | Entry |
|---|---|
| Bounded activation, handoffs, rework, status and trace | `python3 .ai/tools/agent_collaboration.py --help` |
| Runtime session transport (invoked by coordinator) | `.ai/tools/codex_adapter.py` |

Read docs/agent-collaboration.md. Missing native runtime or login is a blocker, not
permission to label role simulation as real collaboration. Codex app-server independent
threads are runtime_session, not parent spawn_agent children. Candidate is NOT a V1.4
release. Never change protected business rules, auto-approve, deploy or access secrets.
'''
    text=base.managed(text,'<!-- COLLABORATION ROUTES BEGIN -->','<!-- COLLABORATION ROUTES END -->',routes,before='# Memory Layers\n')
    readme=base.managed((root/'README.md').read_text(),'<!-- COLLABORATION CANDIDATE BEGIN -->','<!-- COLLABORATION CANDIDATE END -->','''## Collaboration candidate (not V1.4 released)

General capability-based coordination now has candidate source, explicit handoff review,
immutable runtime evidence, scoped application and Codex app-server transport. The database
expert is optional and independent. Existing framework version remains 1.3 until all release
gates including a real authenticated multi-role run pass. Mock tests never qualify as live.
Read [candidate scope and activation](docs/agent-collaboration.md) and the iteration report
under docs/iterations/. No target project is upgraded or telemetry enabled by this commit.
''',before='# What This Repository Contains\n')
    warm=base.managed((root/'00_AI_WARMUP.md').read_text(),'<!-- COLLABORATION WARMUP BEGIN -->','<!-- COLLABORATION WARMUP END -->','''## Collaboration candidate diagnostics (not release acceptance)

Check .ai/tools/agent_collaboration.py and codex_adapter.py, schema/collaboration/registry.json
and policy.json, the optional database_agent profiles and native agent-collaboration Skill
entrypoints. Run `python3 .ai/tools/agent_collaboration.py --help`. Do not create a business
Goal or approval for a smoke test. No runtime/auth means live acceptance is NOT_RUN.
Existing five-role CLI compatibility remains; no migration of business truth is required.
''')
    return {'initdir.sh':text,'README.md':readme,'00_AI_WARMUP.md':warm.rstrip()+'\n'}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--apply',action='store_true'); a=p.parse_args()
    outputs=render(ROOT); changed=[n for n,t in outputs.items() if (ROOT/n).read_text()!=t]
    if a.apply:
        for n in changed: (ROOT/n).write_text(outputs[n])
    print(json.dumps({'changed':changed,'applied':a.apply,'release':'not_promoted'}))
    return 0 if not changed or a.apply else 1
if __name__=='__main__': sys.exit(main())
