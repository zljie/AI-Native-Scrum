"""Guard copyable README entry points and their installed command contracts."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class QuickStartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / 'README.md').read_text(encoding='utf-8')
        cls.quick = cls.text.split('# Quick Start\n', 1)[1].split('# Knowledge Architecture\n', 1)[0]
        cls.initial = cls.quick.split('## A. Initialize a project\n', 1)[1].split('```text\n', 1)[1].split('\n```', 1)[0]
        cls.update = cls.quick.split('## B. Incremental update of an initialized project\n', 1)[1].split('```text\n', 1)[1].split('\n```', 1)[0]

    def test_source_is_commit_pinned_and_both_files_downloaded_together(self):
        self.assertIn('$SOURCE_SHA/$FILE', self.quick)
        self.assertIn('for FILE in initdir.sh 00_AI_WARMUP.md', self.quick)
        self.assertNotIn('raw.githubusercontent.com/zljie/AI-Native-Scrum/main/', self.quick)
        self.assertIn('mktemp -d', self.quick)

    def test_initialization_is_non_destructive_and_not_business_execution(self):
        for value in ('不创建/移动.git', '保留已有非空文件', '不创建业务Goal/Story/Task',
                      '不启动付费模型执行', '固定数量', 'runtime_session', 'NOT_RUN'):
            self.assertIn(value, self.initial)

    def test_update_requires_quiescence_and_keeps_audit_history(self):
        for value in ('requested/running/applying', '不杀进程', '不自动recover',
                      'MERGE/REVIEW', '--mark-merged', '不改旧status', '不擅自回填AT-001',
                      '不要自动执行drive --execute', '版本仍为1.3不代表无更新'):
            self.assertIn(value, self.update)

    def test_installation_does_not_claim_v14_or_spawn_child_validation(self):
        for prompt in (self.initial, self.update):
            self.assertIn('1.3', prompt)
            self.assertIn('V1.4', prompt)
            self.assertIn('spawn_agent', prompt)
            self.assertIn('Codex app-server', prompt)
        self.assertIn('框架源码仓库', self.quick)
        self.assertIn('AT-001为NOT_RUN', self.quick)
        self.assertIn('check --release', self.quick)

    def test_documented_python_entry_points_are_bootstrap_assets(self):
        script = (ROOT / 'initdir.sh').read_text()
        tools = set(re.findall(r'python3 (\.ai/tools/[a-z_]+\.py)', self.quick))
        self.assertTrue({'.ai/tools/agent_collaboration.py', '.ai/tools/harness_observe.py', '.ai/tools/evidence.py'}.issubset(tools))
        for tool in tools:
            self.assertIn(tool, script, tool)
        source = (ROOT / 'collaboration/agent_collaboration.py').read_text()
        for option in ('--run-id', '--context', '--execute', '--release'):
            self.assertIn(option, source)
        for operation in ('plan', 'ready', 'drive', 'check', 'report'):
            self.assertIn("'" + operation + "'", source)

    def test_pinned_download_recipe_has_valid_bash_syntax(self):
        section = self.quick.split('## Get the bootstrap files\n', 1)[1].split('## A.', 1)[0]
        recipe = section.split('```bash\n', 1)[1].split('\n```', 1)[0]
        checked = subprocess.run(['bash', '-n'], input=recipe, text=True, capture_output=True)
        self.assertEqual(checked.returncode, 0, checked.stderr)


if __name__ == '__main__':
    unittest.main()
