"""Offline declared-schema check, not login, enforcement or native-agent proof."""
from __future__ import annotations
import argparse
import json
import hashlib
import re
import shutil
import uuid
from datetime import datetime, timezone
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
    properties = document.get('properties', {})
    # Codex 0.167.1 may expose an experimental named-profile selector, but
    # a profile ID does not declare which filesystem roots are readable.
    named_selector = any(
        node.get('type') == 'string'
        for node in variants(properties.get('permissions', {}), document)
    )
    policy = properties.get('sandboxPolicy', {})
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
    status = ('DECLARED_REQUIRES_LIVE_VERIFICATION' if supported else
              'BLOCKED_NAMED_PROFILE_ROOTS_UNVERIFIED' if named_selector else
              'BLOCKED_RESTRICTED_READ_NOT_DECLARED')
    return {'schema_version': 'host-contract-check/v1',
            'evidence_kind': 'declared_schema_only',
            'restricted_read_declared': supported,
            'named_profile_selector_declared': named_selector,
            'named_profile_root_equivalence': 'NOT_VERIFIED',
            'status': status,
            'authentication': 'NOT_CHECKED', 'sandbox_enforcement': 'NOT_VERIFIED',
            'native_spawn': 'NOT_VERIFIED', 'business_acceptance': 'NOT_RUN'}


def snapshot_digest(report):
    payload = {key: value for key, value in report.items() if key != 'snapshot_sha256'}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def capture(raw_schema, source, host_version='UNKNOWN'):
    """Bind one observation, not a trusted host identity or signed attestation."""
    if source not in ('installed_codex', 'supplied_schema'):
        raise ValueError('SOURCE_INVALID')
    if host_version != 'UNKNOWN' and not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?', host_version):
        raise ValueError('VERSION_INVALID')
    if source == 'supplied_schema' and host_version != 'UNKNOWN':
        raise ValueError('IMPORTED_VERSION_UNVERIFIED')
    report = assess(json.loads(raw_schema))
    report.update({'provenance_version': 'host-capability-snapshot/v1',
                   'source': source, 'host_version': host_version,
                   'schema_sha256': hashlib.sha256(raw_schema).hexdigest(),
                   'capture_id': str(uuid.uuid4()),
                   'captured_at': datetime.now(timezone.utc).isoformat(),
                   'binding_assurance': 'capture_integrity_not_host_identity'})
    report['snapshot_sha256'] = snapshot_digest(report)
    return report


def verify_snapshot(report, expected_digest):
    """Require a separately retained digest. A hash is not a signature or proof."""
    if (not isinstance(report, dict) or not isinstance(expected_digest, str)
            or not re.fullmatch(r'[a-f0-9]{64}', expected_digest)
            or report.get('provenance_version') != 'host-capability-snapshot/v1'):
        return False
    try:
        return report.get('snapshot_sha256') == expected_digest == snapshot_digest(report)
    except (TypeError, ValueError, RecursionError):
        return False


def inspect_installed(binary=None):
    # Resolve once so both probes address the same selected executable. This is
    # not a claim that the binary or machine has been cryptographically attested.
    binary = binary or shutil.which('codex')
    if not binary:
        raise ValueError('BINARY_UNAVAILABLE')
    binary = str(Path(binary).resolve())
    host_version = 'UNKNOWN'
    try:
        version = subprocess.run([binary, '--version'], capture_output=True, timeout=10, check=False)
        match = re.fullmatch(rb'codex-cli ([0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?)\s*', version.stdout)
        if version.returncode == 0 and match:
            host_version = match.group(1).decode('ascii')
    except (OSError, subprocess.SubprocessError):
        pass
    with tempfile.TemporaryDirectory(prefix='ans-host-schema-') as directory:
        result = subprocess.run([binary, 'app-server', 'generate-json-schema', '--out', directory],
                                capture_output=True, timeout=30, check=False)
        if result.returncode:
            raise ValueError('SCHEMA_GENERATION_FAILED')
        return capture((Path(directory)/'v2/TurnStartParams.json').read_bytes(),
                       'installed_codex', host_version)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument('--schema', type=Path, help='Imported schema; host version remains UNKNOWN')
    inputs.add_argument('--verify-snapshot', type=Path, help='Verify a saved capture, without probing any host')
    parser.add_argument('--expected-snapshot-sha256', help='Separately retained capture digest; not a host signature')
    args = parser.parse_args(argv)
    if bool(args.verify_snapshot) != bool(args.expected_snapshot_sha256):
        parser.error('--verify-snapshot requires --expected-snapshot-sha256, and vice versa')
    try:
        if args.verify_snapshot:
            valid = verify_snapshot(json.loads(args.verify_snapshot.read_bytes()), args.expected_snapshot_sha256)
            print(json.dumps({'status': 'CAPTURE_INTEGRITY_MATCH' if valid else 'BLOCKED_SNAPSHOT_MISMATCH',
                              'native_spawn': 'NOT_VERIFIED', 'host_identity': 'NOT_VERIFIED'}))
            return 0 if valid else 2
        report = capture(args.schema.read_bytes(), 'supplied_schema') if args.schema else inspect_installed()
    except (OSError, ValueError, TypeError, AttributeError, RecursionError, subprocess.SubprocessError):
        report = {'schema_version': 'host-contract-check/v1', 'status': 'BLOCKED_SCHEMA_UNAVAILABLE',
                  'evidence_kind': 'declared_schema_only', 'native_spawn': 'NOT_VERIFIED'}
    print(json.dumps(report, sort_keys=True))
    return 0 if report.get('restricted_read_declared') else 2

if __name__ == '__main__':
    raise SystemExit(main())
