#!/usr/bin/env python3
"""V1.5 project context snapshot: evidence-bound inventory, not a semantic classifier.

This tool reads only explicitly supplied repository-relative files. It does not
invoke a model, authorize delegation, inspect secrets, or infer database needs.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid

SCHEMA = "project-context-pack/v1"
CATEGORIES = ("architecture", "database", "interfaces", "implementation", "tests", "requirements")
BLOCKED = {".git", ".env", ".ssh", ".ai", ".claude", ".codex", "node_modules", "secrets", "credentials"}
MAX_BYTES = 2_000_000
MAX_FILES = 80
SHA = re.compile(r"[0-9a-f]{64}\Z")


class ContextError(ValueError):
    pass


def fail(code):
    raise ContextError(code)


def safe_path(root: Path, name: str, must_exist=True) -> Path:
    if not isinstance(name, str) or not name or len(name) > 300 or "\\" in name or "\x00" in name:
        fail("INVALID_PATH")
    relative = Path(name)
    if relative.is_absolute() or any(x in ("", ".", "..") for x in relative.parts):
        fail("UNSAFE_PATH")
    if any(x in BLOCKED or x.startswith(".env.") or x.endswith((".pem", ".key", ".p12")) for x in relative.parts):
        fail("SENSITIVE_PATH")
    original = root / relative
    if any(p.is_symlink() for p in [original, *list(original.parents)[:-1]] if p != root):
        fail("SYMLINK_REF")
    resolved = original.resolve()
    if not resolved.is_relative_to(root):
        fail("PATH_ESCAPE")
    if must_exist:
        if not resolved.is_file() or resolved.is_symlink():
            fail("MISSING_FILE")
        if resolved.stat().st_size > MAX_BYTES:
            fail("FILE_TOO_LARGE")
    return resolved


def load_spec(root: Path, name: str) -> dict:
    path = safe_path(root, name)
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError):
        fail("INVALID_SPEC")
    if not isinstance(spec, dict) or set(spec) != {"schema", "goal_ref", "task_ref", "sources"}:
        fail("SPEC_FIELDS")
    if spec["schema"] != "project-context-request/v1":
        fail("SPEC_SCHEMA")
    for field in ("goal_ref", "task_ref"):
        safe_path(root, spec[field])
    sources = spec["sources"]
    if not isinstance(sources, dict) or set(sources) != set(CATEGORIES):
        fail("SOURCE_CATEGORIES")
    paths = []
    for category in CATEGORIES:
        entries = sources[category]
        if not isinstance(entries, list) or any(not isinstance(x, str) for x in entries):
            fail("SOURCE_LIST")
        paths.extend(entries)
    if len(paths) > MAX_FILES or len(paths) != len(set(paths)):
        fail("SOURCE_LIMIT_OR_DUPLICATE")
    if not paths:
        fail("NO_SOURCES")
    return spec


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path, spec_ref: str) -> dict:
    spec = load_spec(root, spec_ref)
    sources = {}
    for category in CATEGORIES:
        sources[category] = [
            {"ref": name, "sha256": fingerprint(safe_path(root, name)),
             "size_bytes": safe_path(root, name).stat().st_size}
            for name in spec["sources"][category]
        ]
    dependencies = {name: fingerprint(safe_path(root, name))
                    for name in (spec_ref, spec["goal_ref"], spec["task_ref"])}
    return {
        "schema": SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request_ref": spec_ref,
        "goal_ref": spec["goal_ref"],
        "task_ref": spec["task_ref"],
        "dependencies": dependencies,
        "sources": sources,
        "classification": "not_performed",
        "agent_dispatch": "not_performed",
        "authorization": "not_granted"
    }


def validate(root: Path, pack: dict) -> dict:
    if not isinstance(pack, dict) or pack.get("schema") != SCHEMA:
        fail("PACK_SCHEMA")
    if pack.get("classification") != "not_performed" or pack.get("authorization") != "not_granted" or pack.get("agent_dispatch") != "not_performed":
        fail("PACK_AUTHORITY")
    expected = pack.get("dependencies")
    if not isinstance(expected, dict) or not expected:
        fail("PACK_DEPENDENCIES")
    refs = dict(expected)
    sources = pack.get("sources")
    if not isinstance(sources, dict) or set(sources) != set(CATEGORIES):
        fail("PACK_SOURCES")
    for category in CATEGORIES:
        if not isinstance(sources[category], list):
            fail("PACK_SOURCES")
        for entry in sources[category]:
            if not isinstance(entry, dict) or set(entry) != {"ref", "sha256", "size_bytes"}:
                fail("PACK_ENTRY")
            if entry["ref"] in refs:
                fail("PACK_DUPLICATE")
            if type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0 or entry["size_bytes"] > MAX_BYTES:
                fail("PACK_SIZE")
            refs[entry["ref"]] = entry["sha256"]
    changed = []
    for name, expected_hash in refs.items():
        if not isinstance(expected_hash, str) or not SHA.fullmatch(expected_hash):
            fail("PACK_DIGEST")
        try:
            actual = fingerprint(safe_path(root, name))
        except (ContextError, OSError):
            changed.append(name)
            continue
        if actual != expected_hash:
            changed.append(name)
    return {"schema": "project-context-check/v1", "current": not changed,
            "changed_refs": changed, "checked_files": len(refs),
            "delegation_authorized": False}


def write_once(root: Path, output: str, data: dict):
    path = safe_path(root, output, False)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        fail("OUTPUT_EXISTS")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    sub = p.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--spec", required=True)
    build.add_argument("--output", required=True)
    check = sub.add_parser("check")
    check.add_argument("--pack", required=True)
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "build":
            data = snapshot(root, args.spec)
            write_once(root, args.output, data)
            print(json.dumps({"pack_ref": args.output, "source_count": sum(map(len, data["sources"].values())),
                              "dispatch": "not_performed"}))
            return 0
        pack = json.loads(safe_path(root, args.pack).read_text(encoding="utf-8"))
        result = validate(root, pack)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["current"] else 1
    except (ContextError, OSError, UnicodeError, ValueError) as exc:
        print("CONTEXT_ERROR " + (str(exc) if isinstance(exc, ContextError) else "INVALID_INPUT"), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
