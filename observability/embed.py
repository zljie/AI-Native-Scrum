#!/usr/bin/env python3
"""Deterministically embed reviewed observability sources into the two-file bootstrap.

Default is drift checking. --apply modifies only explicitly named source files.
The installed project never imports from this source repository.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'observability'))
from harness_observe import event_schema

BEGIN = '# === OBSERVABILITY GENERATED BEGIN ==='
END = '# === OBSERVABILITY GENERATED END ==='
AGENT_BEGIN = '<!-- OBSERVABILITY ROUTES BEGIN -->'
AGENT_END = '<!-- OBSERVABILITY ROUTES END -->'
README_BEGIN = '<!-- OBSERVABILITY QUICKSTART BEGIN -->'
README_END = '<!-- OBSERVABILITY QUICKSTART END -->'
WARMUP_BEGIN = '<!-- OBSERVABILITY WARMUP BEGIN -->'
WARMUP_END = '<!-- OBSERVABILITY WARMUP END -->'


def replace_once(text, before, after):
    if before not in text:
        if after in text:
            return text
        raise ValueError('expected integration anchor is missing')
    if text.count(before) != 1:
        raise ValueError('ambiguous integration anchor')
    return text.replace(before, after, 1)


def managed(text, begin, end, content, before=None):
    if begin in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError('ambiguous generated markers')
        start = text.index(begin)
        finish = text.index(end) + len(end)
        return text[:start] + begin + '\n' + content.rstrip() + '\n' + end + text[finish:]
    block = begin + '\n' + content.rstrip() + '\n' + end + '\n\n'
    if before:
        return replace_once(text, before, block + before)
    return text.rstrip() + '\n\n' + block


def add_files(text, variable, paths):
    pattern = rf'(?m)^{variable}="([^\"]*)"'
    match = re.search(pattern, text)
    if not match:
        raise ValueError('file ownership list missing')
    names = match.group(1).splitlines()
    names += [p for p in paths if p not in names]
    return text[:match.start()] + variable + '="' + '\n'.join(names) + '"' + text[match.end():]


def runner_integration(text):
    start = text.index("<<'LOCAL_AGENT_RUNNER_PY'\n") + len("<<'LOCAL_AGENT_RUNNER_PY'\n")
    finish = text.index('\nLOCAL_AGENT_RUNNER_PY\n', start)
    code = text[start:finish]
    if 'import harness_observe\n' not in code:
        code = replace_once(code, 'from agent_handoff import project_path', 'from agent_handoff import project_path\nimport harness_observe')
    code = replace_once(code, 'def run(root, args):', 'def run(root, args, observer=None):')
    code = replace_once(code, 'result = subprocess.run(command, cwd=root, capture_output=True, text=True,',
                        'result = (observer or subprocess.run)(command, cwd=root, capture_output=True, text=True,')
    code = replace_once(code, 'return run(Path(args.root).resolve(), args)',
                        'return harness_observe.observe_run(Path(args.root).resolve(), args, run)')
    anchor = '    if args.command == "route":\n'
    if 'harness_observe.record_route(' not in code:
        code = replace_once(code, anchor, anchor + '        harness_observe.record_route(Path(args.root).resolve(), args.kind)\n')
    return text[:start] + code + text[finish:]


def gate_integration(text):
    start = text.index("<<'CHECK_GATES_PY'\n") + len("<<'CHECK_GATES_PY'\n")
    finish = text.index('\nCHECK_GATES_PY\n', start)
    code = text[start:finish]
    if 'import harness_observe\n' not in code:
        code = replace_once(code, 'import argparse\n', 'import argparse\nimport harness_observe\n')
    if 'harness_observe.record_gate(root, result)' not in code:
        code = replace_once(code, '    if args.json:\n', '    harness_observe.record_gate(root, result)\n    if args.json:\n')
    return text[:start] + code + text[finish:]


def render(root):
    assets = {
        '.ai/tools/harness_observe.py': (root / 'observability/harness_observe.py').read_text(),
        '.ai/tools/harness_report.py': (root / 'observability/harness_report.py').read_text(),
        'schema/observability/harness-event.schema.json': json.dumps(event_schema(), indent=2, ensure_ascii=False) + '\n',
        'schema/templates/experiment.md': (root / 'observability/experiment-template.md').read_text(),
        'docs/harness-observability.md': (root / 'docs/harness-observability.md').read_text(),
        '.ai/observability/.gitignore': '*\n',
    }
    path = root / 'initdir.sh'
    text = path.read_text()
    text = replace_once(text, 'FRAMEWORK_VERSION="1.2"', 'FRAMEWORK_VERSION="1.3"')
    text = text.replace('# initdir.sh v1.2', '# initdir.sh v1.3')
    text = add_files(text, 'FRAMEWORK_FILES', [p for p in assets if p != '.ai/observability/.gitignore'])
    text = add_files(text, 'PROJECT_FILES', ['.ai/observability/.gitignore'])
    block = []
    for index, (name, content) in enumerate(assets.items()):
        delimiter = 'OBSERVABILITY_ASSET_' + str(index)
        if delimiter in content.splitlines():
            raise ValueError('heredoc delimiter collision')
        block.append(f'create_file_if_missing "{name}"\nif [ ! -s "{name}" ]; then\ncat > "{name}" <<\'{delimiter}\'\n{content.rstrip()}\n{delimiter}\nfi\n')
    text = managed(text, BEGIN, END, '\n'.join(block), before='# ============================================================\n# Framework version\n')
    routes = '''# Local observability (v1.3)

Default off; enable only with project-owner consent. Logs never grant authority.
Do not equate cli_role with a native subagent or Skill invocation with guidance quality.
Do not log prompts, responses, tool arguments, credentials or raw session IDs.
For actual metadata/coverage and safe activation, read `docs/harness-observability.md`.

| Request | Tool |
|---|---|
| Inspect/enable local runtime telemetry; merge Hooks only after approval | `python3 .ai/tools/harness_observe.py status` |
| Report observed runtime health or evidence-backed paired experiments | `python3 .ai/tools/harness_report.py` |

Unknown usage stays null. Native Hook trust is reviewed in the host, never bypassed.
Architecture choices stay in wiki/decisions/ADR-*.md; experiment design/results stay
in wiki/experiments/EXP-*.md using schema/templates/experiment.md. Neither is business acceptance.
'''
    text = managed(text, AGENT_BEGIN, AGENT_END, routes, before='# Memory Layers\n')
    text = runner_integration(text)
    text = gate_integration(text)
    text = text.replace('"Stop", "SubagentStop", "PreCompact", "Notification",',
                        '"Stop", "SubagentStop", "SubagentStart", "PostModelRequest", "PostToolUseFailure", "PreCompact", "Notification",')
    # No changes to existing permissions, role profiles, Skill logic or native trust state.
    readme = (root / 'README.md').read_text()
    intro = '''## V1.3: opt-in local observability

Fresh initialization and safe upgrades now include runtime telemetry, Token normalization,
health reports, paired experiment comparison and an experiment template. Nothing is collected
until `python3 .ai/tools/harness_observe.py enable` is explicitly run in the target project.
Use `status` before and after enabling. Native Hook collection additionally requires an
approved `install-hooks --provider codex --apply` (or claude), followed by host trust review.
Existing nonempty/customized files remain protected by the normal upgrade mechanism.

Read [the activation, privacy and experiment guide](docs/harness-observability.md).
Collector tests/CI are fixture evidence, not real model benchmarks or measured savings.
The generated Runner preserves its authorization checks and distinguishes cli_role from
runtime-observed native subagents. Actual production/real-model acceptance remains separate.
'''
    readme = managed(readme, README_BEGIN, README_END, intro, before='# What This Repository Contains\n')
    readme = readme.replace('应为 1.2', '应为 1.3')
    warmup = (root / '00_AI_WARMUP.md').read_text()
    warmup = managed(warmup, WARMUP_BEGIN, WARMUP_END, '''## V1.3 observability readiness

Confirm `.ai/tools/harness_observe.py`, `.ai/tools/harness_report.py`,
`schema/observability/harness-event.schema.json`, `schema/templates/experiment.md`
and `docs/harness-observability.md` exist. Run `harness_observe.py status` and
`harness_observe.py report`: a fresh project must say disabled/no_data, not claim
zero cost or completed acceptance. Initialization never enables collection or
installs/trusts new Hooks. Existing enabled project settings are project-owned.

Optional owner-authorized activation is documented in the guide. Configuration
existence does not prove host execution; fixture tests do not prove live native
Hook or authenticated model compatibility. Preserve null/unknown and NOT_RUN.
''')
    return {'initdir.sh': text, 'README.md': readme, '00_AI_WARMUP.md': warmup.rstrip() + '\n'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    try:
        outputs = render(ROOT)
        changed = [name for name, value in outputs.items() if (ROOT / name).read_text() != value]
        if args.apply:
            for name in changed:
                (ROOT / name).write_text(outputs[name], encoding='utf-8')
        print(json.dumps({'changed': changed, 'applied': args.apply}, indent=2))
        return 0 if args.apply or not changed else 1
    except (OSError, ValueError):
        print('EMBED_ERROR: source integration anchors changed; review required', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
