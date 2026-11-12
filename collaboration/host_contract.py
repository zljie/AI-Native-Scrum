"""Offline declared-schema check, not login, enforcement or native-agent proof."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def variants(value, document):
    """Resolve bounded local references and union branches; never fetch a URL."""
    pending = [(value, 0)]
    seen = set()
    while pending:
        node, depth = pending.pop()
        if not isinstance(node, dict) or depth > 20 or id(node) in seen:
            continue
        seen.add(id(node))
        ref = node.get('$ref')
        if ref is not None:
            if not isinstance(ref, str) or not ref.startswith('#/'):
                continue
            target = document
            try:
                for part in ref[2:].split('/'):
                    target = target[part.replace('~1', '/').replace('~0', '~')]
            except (KeyError, TypeError):
                continue
            pending.append((target, depth + 1))
        elif any(key in node for key in ('oneOf', 'anyOf', 'allOf')):
            for key in ('oneOf', 'anyOf', 'allOf'):
                for branch in node.get(key, []):
                    pending.append((branch, depth + 1))
        else:
            yield node


def declares(value, expected):
    return isinstance(value, dict) and (value.get('const') == expected or expected in value.get('enum', []))


def assess(document):
    if not isinstance(document, dict):
        raise ValueError('SCHEMA_INVALID')
    supported = False
    policy = document.get('properties', {}).get('sandboxPolicy', {})
    for branch in variants(policy, document):
        props = branch.get('properties', {})
        if not declares(props.get('type'), 'readOnly'):
            continue
        for access in variants(props.get('access', {}), document):
            fields = access.get('properties', {})
            roots = fields.get('readableRoots', {})
            if (declares(fields.get('type'), 'restricted')
                    and roots.get('type') == 'array'
                    and fields.get('includePlatformDefaults', {}).get('type') == 'boolean'):
                supported = True
    return {'schema_version': 'host-contract-check/v1',
            'evidence_kind': 'declared_schema_only',
            'restricted_read_declared': supported,
            'status': 'DECLARED_REQUIRES_LIVE_VERIFICATION' if supported else 'BLOCKED_RESTRICTED_READ_NOT_DECLARED',
            'authentication': 'NOT_CHECKED', 'sandbox_enforcement': 'NOT_VERIFIED',
            'native_spawn': 'NOT_VERIFIED', 'business_acceptance': 'NOT_RUN'}


def inspect_installed():
    # This only generates protocol files. It starts no model turn and reads no credentials.
    with tempfile.TemporaryDirectory(prefix='ans-host-schema-') as directory:
        result = subprocess.run(['codex', 'app-server', 'generate-json-schema', '--out', directory],
                                capture_output=True, timeout=30, check=False)
        if result.returncode:
            raise ValueError('SCHEMA_GENERATION_FAILED')
        return assess(json.loads((Path(directory)/'v2/TurnStartParams.json').read_text()))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema', type=Path, help='Explicit TurnStartParams JSON schema; otherwise inspect installed Codex')
    args = parser.parse_args(argv)
    try:
        report = assess(json.loads(args.schema.read_text())) if args.schema else inspect_installed()
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError):
        report = {'schema_version': 'host-contract-check/v1', 'status': 'BLOCKED_SCHEMA_UNAVAILABLE',
                  'evidence_kind': 'declared_schema_only', 'native_spawn': 'NOT_VERIFIED'}
    print(json.dumps(report, sort_keys=True))
    return 0 if report.get('restricted_read_declared') else 2

if __name__ == '__main__':
    raise SystemExit(main())
