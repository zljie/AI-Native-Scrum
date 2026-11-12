import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from host_contract import assess

class HostContractTests(unittest.TestCase):
    def schema(self):
        return {'properties': {'sandboxPolicy': {'oneOf': [{'properties': {
            'type': {'enum': ['readOnly']}, 'access': {'properties': {
                'type': {'enum': ['restricted']}, 'readableRoots': {'type': 'array'},
                'includePlatformDefaults': {'type': 'boolean'}}}}}]}}}

    def test_declared_is_not_verified(self):
        result = assess(self.schema())
        self.assertTrue(result['restricted_read_declared'])
        for field in ('native_spawn', 'sandbox_enforcement'):
            self.assertEqual(result[field], 'NOT_VERIFIED')
        self.assertEqual(result['authentication'], 'NOT_CHECKED')

    def test_legacy_readonly_without_access_is_blocked(self):
        schema = self.schema()
        del schema['properties']['sandboxPolicy']['oneOf'][0]['properties']['access']
        self.assertFalse(assess(schema)['restricted_read_declared'])

    def test_local_reference_and_full_access_negative(self):
        schema = self.schema()
        branch = schema['properties']['sandboxPolicy']
        schema['definitions'] = {'Policy': branch}
        schema['properties']['sandboxPolicy'] = {'$ref': '#/definitions/Policy'}
        self.assertTrue(assess(schema)['restricted_read_declared'])
        branch['oneOf'][0]['properties']['access']['properties']['type']['enum'] = ['fullAccess']
        self.assertFalse(assess(schema)['restricted_read_declared'])

    def test_recursive_and_external_refs_do_not_fetch_or_loop(self):
        for ref in ('#/properties/sandboxPolicy', 'https://example.invalid/schema'):
            self.assertFalse(assess({'properties': {'sandboxPolicy': {'$ref': ref}}})['restricted_read_declared'])

    def test_cli_failure_is_safe_and_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'schema.json'
            path.write_text('SECRET INVALID JSON')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('host_contract.py')), '--schema', str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)['status'], 'BLOCKED_SCHEMA_UNAVAILABLE')
            self.assertNotIn('SECRET', result.stdout + result.stderr)
            self.assertNotIn(tmp, result.stdout + result.stderr)
