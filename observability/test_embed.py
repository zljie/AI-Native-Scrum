import tempfile
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import embed


class EmbedTests(unittest.TestCase):
    def test_managed_section_idempotent(self):
        a = embed.managed('HEAD\nANCHOR\nTAIL\n', 'BEGIN', 'END', 'NEW', 'ANCHOR\n')
        self.assertEqual(a, embed.managed(a, 'BEGIN', 'END', 'NEW', 'ANCHOR\n'))
        self.assertIn('TAIL', a)

    def test_managed_section_preserves_user_content(self):
        a = 'HEAD\nBEGIN\nOLD\nEND\nTAIL\n'
        self.assertEqual(embed.managed(a, 'BEGIN', 'END', 'NEW'), 'HEAD\nBEGIN\nNEW\nEND\nTAIL\n')

    def test_replacement_refuses_unknown_source(self):
        with self.assertRaises(ValueError):
            embed.replace_once('unexpected', 'old', 'new')

    def test_ownership_registration_idempotent(self):
        source = 'FRAMEWORK_FILES="one\ntwo"\n'
        once = embed.add_files(source, 'FRAMEWORK_FILES', ['three'])
        self.assertEqual(once, embed.add_files(once, 'FRAMEWORK_FILES', ['three']))

    def test_runner_adapter_is_narrow_and_idempotent(self):
        source = "<<'LOCAL_AGENT_RUNNER_PY'\nfrom agent_handoff import project_path\ndef run(root, args):\n    result = subprocess.run(command, cwd=root, capture_output=True, text=True,\n                            timeout=5)\n    return run(Path(args.root).resolve(), args)\n    if args.command == \"route\":\n        pass\nLOCAL_AGENT_RUNNER_PY\n"
        out = embed.runner_integration(source)
        self.assertEqual(out, embed.runner_integration(out))
        self.assertIn('observer or subprocess.run', out)
        self.assertIn('harness_observe.observe_run', out)


if __name__ == '__main__':
    unittest.main()
