#!/usr/bin/env python3
"""Compile project-bound role configuration candidates; never dispatch or authorize.

S1 source-only API. Facts, declared standards and confirmation references remain
separate. Structural checks do not authenticate people or assess rule semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

from project_context import ContextError, MAX_FILES, SHA, fingerprint, safe_path, write_once

REQUEST = "project-agent-init-request/v1"
MANIFEST = "project-agent-profile-set/v1"
IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
AUTHORITY = {"runtime_status": "NOT_RUN", "authorization": "not_granted",
             "semantic_review": "not_performed", "confirmation_identity": "not_verified"}
REQUEST_FIELDS = {"schema", "project_id", "registry_ref", "roles"}
BINDING_FIELDS = {"role_id", "variant", "required_standards", "standards", "fact_refs", "conflict_refs"}
MANIFEST_FIELDS = {"schema", "project_id", "request_ref", "registry_ref", "dependencies", "profiles",
                   "configuration_status", "version", *AUTHORITY}


def fail(code: str):
    raise ContextError(code)


def fields(value, expected: set, code: str):
    if not isinstance(value, dict) or set(value) != expected:
        fail(code)


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        fail("INIT_IDENTIFIER")
    return value


def strings(value, nonempty=False):
    if (not isinstance(value, list) or len(value) > MAX_FILES or
            any(not isinstance(item, str) or not item for item in value)):
        fail("INIT_STRING_LIST")
    if len(value) != len(set(value)) or (nonempty and not value):
        fail("INIT_STRING_LIST")
    return value


def ref_path(root: Path, ref: str, must_exist=True):
    if (not isinstance(ref, str) or not ref or ref != ref.strip() or
            any(ord(c) < 32 or ord(c) == 127 for c in ref) or
            any(part in ("", ".", "..") for part in ref.split("/"))):
        fail("INIT_NONCANONICAL_REF")
    return safe_path(root, ref, must_exist)


def digest(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail("INIT_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def read_json(root: Path, ref: str):
    try:
        return json.loads(ref_path(root, ref).read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object,
                          parse_constant=lambda _: fail("INIT_INVALID_JSON"))
    except (UnicodeError, ValueError, RecursionError) as exc:
        if isinstance(exc, ContextError):
            raise
        fail("INIT_INVALID_JSON")


def build(root: Path, request_ref: str) -> dict:
    """Read explicit local sources; return a deterministic, non-authorizing candidate."""
    root = Path(root).resolve()
    dependencies = {}

    def track(ref):
        current = fingerprint(ref_path(root, ref))
        if ref in dependencies and dependencies[ref] != current:
            fail("INIT_INPUT_CHANGED")
        dependencies[ref] = current
        if len(dependencies) > MAX_FILES:
            fail("INIT_SOURCE_LIMIT")
        return ref

    def tracked_json(ref):
        track(ref)
        value = read_json(root, ref)
        track(ref)
        return value

    request = tracked_json(request_ref)
    fields(request, REQUEST_FIELDS, "INIT_REQUEST_FIELDS")
    if request["schema"] != REQUEST:
        fail("INIT_REQUEST_SCHEMA")
    project_id = identifier(request["project_id"])
    registry_ref = request["registry_ref"]
    registry = tracked_json(registry_ref)
    fields(registry, {"schema", "roles"}, "INIT_REGISTRY_FIELDS")
    if registry["schema"] != "agent-capabilities/v1" or not isinstance(registry["roles"], dict):
        fail("INIT_REGISTRY_SCHEMA")
    bindings = request["roles"]
    if not isinstance(bindings, list) or not 1 <= len(bindings) <= 20:
        fail("INIT_ROLES")
    profiles, identities = [], set()
    for binding in bindings:
        fields(binding, BINDING_FIELDS, "INIT_BINDING_FIELDS")
        role_id, variant = identifier(binding["role_id"]), identifier(binding["variant"])
        identity = (role_id, variant)
        if identity in identities:
            fail("INIT_DUPLICATE_ROLE_VARIANT")
        identities.add(identity)
        role = registry["roles"].get(role_id)
        if not isinstance(role, dict) or role.get("enabled") is not True:
            fail("INIT_ROLE_UNAVAILABLE")
        capabilities = strings(role.get("capabilities"), nonempty=True)
        for capability in capabilities:
            identifier(capability)
        contract_ref = track(role.get("contract_ref"))
        required = strings(binding["required_standards"], nonempty=True)
        for name in required:
            identifier(name)
        facts, conflicts = strings(binding["fact_refs"]), strings(binding["conflict_refs"])
        standards = binding["standards"]
        if not isinstance(standards, dict) or len(standards) > MAX_FILES:
            fail("INIT_STANDARDS")
        inputs = {request_ref, registry_ref, contract_ref}
        for ref in facts + conflicts:
            inputs.add(track(ref))
        for name, standard in standards.items():
            identifier(name)
            fields(standard, {"source_ref", "confirmation_ref"}, "INIT_STANDARD_FIELDS")
            for ref in standard.values():
                inputs.add(track(ref))
        findings = [{"code": "MISSING_STANDARD", "standard": name}
                    for name in required if name not in standards]
        findings += [{"code": "UNRESOLVED_CONFLICT", "ref": ref} for ref in conflicts]
        profile = {"role_id": role_id, "variant": variant, "contract_ref": contract_ref,
                   "capabilities": capabilities, "required_standards": required,
                   "standards": standards, "fact_refs": facts, "conflict_refs": conflicts,
                   "input_refs": sorted(inputs), "findings": findings,
                   "status": "BLOCKED" if findings else "CANDIDATE"}
        profile["version"] = digest({"project_id": project_id, "profile": profile,
                                      "inputs": {ref: dependencies[ref] for ref in sorted(inputs)}})
        profiles.append(profile)
    # Detect ordinary concurrent edits. This is not a hostile-filesystem sandbox.
    if any(fingerprint(ref_path(root, ref)) != value for ref, value in dependencies.items()):
        fail("INIT_INPUT_CHANGED")
    manifest = {"schema": MANIFEST, "project_id": project_id, "request_ref": request_ref,
                "registry_ref": registry_ref, "dependencies": dependencies, "profiles": profiles,
                "configuration_status": "BLOCKED" if any(p["findings"] for p in profiles) else "CANDIDATE",
                **AUTHORITY}
    manifest["version"] = digest(manifest)
    return manifest


def check(root: Path, manifest: dict, project_id: str) -> dict:
    """Recompute from authoritative request; a hash alone never proves acceptance."""
    root = Path(root).resolve()
    fields(manifest, MANIFEST_FIELDS, "INIT_MANIFEST_FIELDS")
    if manifest["schema"] != MANIFEST:
        fail("INIT_MANIFEST_SCHEMA")
    if any(manifest[key] != value for key, value in AUTHORITY.items()):
        fail("INIT_AUTHORITY")
    if manifest["project_id"] != identifier(project_id):
        fail("INIT_PROJECT_MISMATCH")
    if manifest["version"] != digest({k: v for k, v in manifest.items() if k != "version"}):
        fail("INIT_INTEGRITY")
    dependencies = manifest["dependencies"]
    if not isinstance(dependencies, dict) or not 1 <= len(dependencies) <= MAX_FILES:
        fail("INIT_DEPENDENCIES")
    for key in ("request_ref", "registry_ref"):
        ref_path(root, manifest[key], False)
        if manifest[key] not in dependencies:
            fail("INIT_DEPENDENCIES")
    profiles = manifest["profiles"]
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= 20:
        fail("INIT_PROFILES")
    for profile in profiles:
        if not isinstance(profile, dict):
            fail("INIT_PROFILE")
        identifier(profile.get("role_id"))
        identifier(profile.get("variant"))
        inputs = strings(profile.get("input_refs"), nonempty=True)
        if any(ref not in dependencies for ref in inputs):
            fail("INIT_DEPENDENCIES")
    changed = []
    for ref, expected in dependencies.items():
        ref_path(root, ref, False)
        if not isinstance(expected, str) or not SHA.fullmatch(expected):
            fail("INIT_DIGEST")
        try:
            if fingerprint(ref_path(root, ref)) != expected:
                changed.append(ref)
        except (ContextError, OSError):
            changed.append(ref)
    if changed:
        status = "STALE"
    else:
        if build(root, manifest["request_ref"]) != manifest:
            fail("INIT_DERIVATION_MISMATCH")
        status = manifest["configuration_status"]
    affected = [p["role_id"] + ":" + p["variant"] for p in profiles
                if set(p["input_refs"]).intersection(changed)]
    return {"schema": "project-agent-profile-check/v1", "current": not changed,
            "configuration_status": status, "changed_refs": sorted(changed),
            "affected_profiles": affected, "delegation_authorized": False, **AUTHORITY}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("--spec", required=True)
    create.add_argument("--output", required=True)
    verify = commands.add_parser("check")
    verify.add_argument("--manifest", required=True)
    verify.add_argument("--project-id", required=True)
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "build":
            output = ref_path(root, args.output, False)
            if not output.relative_to(root).as_posix().startswith("generated/project-agents/"):
                fail("INIT_OUTPUT_SCOPE")
            manifest = build(root, args.spec)
            write_once(root, args.output, manifest)
            result = {"manifest_ref": args.output, "version": manifest["version"],
                      "configuration_status": manifest["configuration_status"], **AUTHORITY}
        else:
            result = check(root, read_json(root, args.manifest), args.project_id)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["configuration_status"] == "CANDIDATE" else 1
    except (ContextError, OSError, ValueError, TypeError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, ContextError) else "INVALID_INPUT"
        print("PROJECT_AGENT_INIT_ERROR " + code, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
