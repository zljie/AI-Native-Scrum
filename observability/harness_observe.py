#!/usr/bin/env python3
"""Opt-in, local-only harness telemetry. Never stores prompts, responses or tool arguments.

Sources describe the collection boundary, not authenticated identity. An invocation
is not semantic Skill compliance; a process exit is not business acceptance.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import statistics
import sys
import tempfile
import time
import uuid

VERSION = "1.3.0"
ROLES = ("product_agent", "architect_agent", "developer_agent", "test_agent", "ops_agent")
SKILLS = ("goal-intake", "goal-to-backlog", "story-refine", "story-to-tasks", "ingest", "query", "lint", "delivery-loop", "solution-pack", "product-director", "experience-director", "tdd-director", "review-director", "frontend-list-contract")
EVENTS = ("run_requested", "process_started", "run_finished", "hook_fired", "skill_invoked", "native_subagent_started", "native_subagent_stopped", "usage_observed", "route_reported", "gate_checked", "collaboration_transition")
HOOKS = ("SessionStart", "SessionEnd", "UserPromptSubmit", "PreToolUse", "PostToolUse", "PostToolUseFailure", "SubagentStart", "SubagentStop", "Stop", "PostModelRequest")
FIELDS = ("schema", "event_id", "at", "type", "source", "sample_kind", "trace_id", "span_id", "parent_span_id", "session_id", "run_id", "goal_id", "task_id", "role", "provider", "execution_mode", "skill", "hook", "model", "framework_version", "tool_version", "source_revision", "source_dirty", "framework_fingerprint", "collector_fingerprint", "result", "reason", "duration_ms", "exit_code", "usage", "usage_scope", "route_kind", "gate_id")
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
USAGE_KEYS = ("input_tokens", "cached_input_tokens", "cache_creation_input_tokens", "output_tokens", "total_tokens")


def now():
    return datetime.now(timezone.utc).isoformat()


def token_count(value):
    return value if type(value) is int and value >= 0 else None


def ident(value):
    return value if isinstance(value, str) and ID.fullmatch(value) else None


def safe_path(root, relative):
    """Reject escapes and symlinks in every existing component; not an OS sandbox."""
    root = Path(root).resolve()
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("unsafe relative path")
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink is not allowed")
    if not current.resolve().is_relative_to(root):
        raise ValueError("path escapes root")
    return current


def read_json(path, limit=4_000_000):
    if path.stat().st_size > limit:
        raise ValueError("JSON size limit exceeded")
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path, value, replace=False):
    """Atomic immutable event creation; concurrent readers never see partial JSON."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError("symlink output")
    fd, temporary = tempfile.mkstemp(prefix=".obs-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def empty_usage(reason="unavailable"):
    return {**dict.fromkeys(USAGE_KEYS), "complete": False, "source": reason}


def normalize_usage(provider, usage):
    """Codex cache is a subset of input; Claude cache buckets are additional input."""
    if not isinstance(usage, dict):
        return empty_usage()
    names = ("input_tokens", "output_tokens", "cached_input_tokens") if provider == "codex" else ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
    if any(name in usage and token_count(usage[name]) is None for name in names):
        return empty_usage("invalid_usage")
    inp = token_count(usage.get("input_tokens"))
    out = token_count(usage.get("output_tokens"))
    if provider == "codex":
        cache = token_count(usage.get("cached_input_tokens"))
        creation = None  # the CLI contract does not expose this bucket
        if cache is not None and inp is not None and cache > inp:
            return empty_usage("invalid_usage")
    elif provider == "claude":
        cache = token_count(usage.get("cache_read_input_tokens"))
        creation = token_count(usage.get("cache_creation_input_tokens"))
        inp = inp + cache + creation if all(v is not None for v in (inp, cache, creation)) else None
    else:
        return empty_usage("unsupported_provider")
    complete = inp is not None and out is not None
    return {"input_tokens": inp, "cached_input_tokens": cache, "cache_creation_input_tokens": creation,
            "output_tokens": out, "total_tokens": inp + out if complete else None,
            "complete": complete, "source": "provider_reported"}


def provider_usage(provider, output):
    """Read terminal accounting only; never add assistant messages to a final total."""
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    output = output or ""
    try:
        obj = json.loads(output)
        records = obj if isinstance(obj, list) else [obj]
        invalid = False
    except (ValueError, TypeError):
        records, invalid = [], False
        for line in output.splitlines():
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except ValueError:
                invalid = True
    records = [r for r in records if isinstance(r, dict)]
    if provider == "codex":
        terminal = [r for r in records if r.get("type") == "turn.completed"]
        failed = any(r.get("type") in ("turn.failed", "error") for r in records)
    else:
        terminal = [r for r in records if r.get("type") == "result"]
        failed = any(r.get("is_error") is True or r.get("subtype", "success") != "success" for r in terminal)
        if len(terminal) > 1:
            return empty_usage("ambiguous_terminal"), "unknown"
    if not terminal:
        return empty_usage("terminal_missing"), "failed" if failed else "unknown"
    parts = [normalize_usage(provider, r.get("usage")) for r in terminal]
    result = {key: sum(p[key] for p in parts) if all(p[key] is not None for p in parts) else None for key in USAGE_KEYS}
    result.update(complete=all(p["complete"] for p in parts) and not invalid and not failed,
                  source="provider_reported" if not invalid else "invalid_stream")
    if not result["complete"]:
        result["total_tokens"] = None
    return result, "failed" if failed else ("unknown" if invalid else "completed")


def event_schema():
    props = {name: {"type": ["string", "null"]} for name in FIELDS}
    for name in ("duration_ms", "exit_code"):
        props[name] = {"type": ["integer", "null"]}
    props["duration_ms"]["minimum"] = 0
    props["source_dirty"] = {"type": ["boolean", "null"]}
    props["usage"] = {"type": ["object", "null"], "additionalProperties": False,
        "required": list(USAGE_KEYS) + ["complete", "source"],
        "properties": {**{key: {"type": ["integer", "null"], "minimum": 0} for key in USAGE_KEYS},
                       "complete": {"type": "boolean"}, "source": {"type": "string"}}}
    props["schema"] = {"const": "harness-event/v1"}
    props["type"] = {"enum": list(EVENTS)}
    props["source"] = {"enum": ["runner", "codex_hook", "claude_hook", "gate_checker", "self_reported", "collaboration"]}
    props["sample_kind"] = {"enum": ["real", "fixture"]}
    props["provider"] = {"enum": ["codex", "claude", None]}
    props["execution_mode"] = {"enum": ["cli_role", "native_subagent", "unknown", "protocol", None]}
    props["role"] = {"type": ["string", "null"], "pattern": r"^[A-Za-z][A-Za-z0-9_.:-]{0,95}$"}
    props["skill"] = {"enum": list(SKILLS) + [None]}
    props["hook"] = {"enum": list(HOOKS) + [None]}
    props["usage_scope"] = {"enum": ["run_total", "request", None]}
    props["route_kind"] = {"enum": ["feature", "bugfix", "change_request", None]}
    props["gate_id"] = {"enum": ["TEST_VERIFY_GATE", "OPS_READY_GATE", None]}
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
            "additionalProperties": False, "required": list(FIELDS), "properties": props}


def validate_event(event):
    if not isinstance(event, dict) or set(event) != set(FIELDS):
        raise ValueError("event fields do not match schema")
    if event["role"] is not None and not ident(event["role"]):
        raise ValueError("invalid role identity")
    for key, spec in event_schema()["properties"].items():
        v = event[key]
        if "const" in spec and v != spec["const"]:
            raise ValueError("invalid constant")
        if "enum" in spec and v not in spec["enum"]:
            raise ValueError("invalid enum")
        if key == "usage":
            if v is not None:
                if not isinstance(v, dict) or set(v) != set(USAGE_KEYS) | {"complete", "source"}:
                    raise ValueError("invalid usage fields")
                if type(v["complete"]) is not bool or not ident(v["source"]):
                    raise ValueError("invalid usage provenance")
                for count in USAGE_KEYS:
                    if v[count] is not None and token_count(v[count]) is None:
                        raise ValueError("invalid token count")
                if v["complete"] and (v["input_tokens"] is None or v["output_tokens"] is None or v["total_tokens"] != v["input_tokens"] + v["output_tokens"]):
                    raise ValueError("inconsistent complete usage")
                if v["cached_input_tokens"] is not None and v["input_tokens"] is not None and v["cached_input_tokens"] > v["input_tokens"]:
                    raise ValueError("cache exceeds input")
        elif key == "source_dirty":
            if v is not None and type(v) is not bool:
                raise ValueError("invalid dirty flag")
        elif key in ("duration_ms", "exit_code"):
            if v is not None and (type(v) is not int or (key == "duration_ms" and v < 0)):
                raise ValueError("invalid numeric field")
        elif v is not None and (not isinstance(v, str) or len(v) > 128):
            raise ValueError("invalid scalar")
    for key in ("event_id", "trace_id", "span_id"):
        if not ident(event[key]):
            raise ValueError("invalid identity")
    stamp = datetime.fromisoformat(event["at"])
    if stamp.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    if event["type"].startswith("native_subagent_") and (event["source"] not in ("codex_hook", "claude_hook") or event["execution_mode"] != "native_subagent"):
        raise ValueError("native execution needs host-boundary evidence")


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        path = safe_path(self.root, ".ai/observability/config.json")
        self.config = read_json(path) if path.is_file() else {"enabled": False}
        if not isinstance(self.config, dict):
            raise ValueError("invalid configuration")
        if self.enabled and (self.config.get("sample_kind") not in ("real", "fixture") or not isinstance(self.config.get("salt"), str) or not re.fullmatch(r"[0-9a-f]{32}", self.config["salt"])):
            raise ValueError("invalid enabled configuration")

    @property
    def enabled(self):
        return self.config.get("enabled") is True

    def hash_id(self, value):
        return hashlib.sha256((self.config.get("salt", "") + str(value)).encode()).hexdigest()[:32]

    def emit(self, kind, source, trace, span, dedupe_key=None, **data):
        if not self.enabled:
            return None
        event = dict.fromkeys(FIELDS)
        event.update(schema="harness-event/v1", event_id=self.hash_id(dedupe_key) if dedupe_key is not None else uuid.uuid4().hex, at=now(), type=kind, source=source,
                     sample_kind=self.config.get("sample_kind", "real"), trace_id=trace, span_id=span,
                     tool_version=VERSION, **data)
        version = safe_path(self.root, ".ai/framework-version")
        if version.is_file():
            # The baseline file is a JSON object, with a fallback for legacy line format.
            text = version.read_text(encoding="utf-8")
            event["framework_fingerprint"] = hashlib.sha256(text.encode()).hexdigest()
            try:
                event["framework_version"] = ident(str(json.loads(text).get("framework_version", "unknown")))
            except (ValueError, AttributeError):
                match = re.search(r"framework_version[\"\s:=]+([0-9.]+)", text)
                event["framework_version"] = match.group(1) if match else None
        event["collector_fingerprint"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        try:
            git = subprocess.run(["git", "rev-parse", "--show-toplevel", "HEAD"], cwd=self.root,
                                 capture_output=True, text=True, timeout=3)
            lines = git.stdout.strip().splitlines()
            if git.returncode == 0 and len(lines) == 2 and Path(lines[0]).resolve() == self.root and re.fullmatch(r"[0-9a-f]{40,64}", lines[1]):
                event["source_revision"] = lines[1]
                state = subprocess.run(["git", "status", "--porcelain"], cwd=self.root, capture_output=True, text=True, timeout=3)
                event["source_dirty"] = bool(state.stdout) if state.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            pass
        validate_event(event)
        path = safe_path(self.root, f".ai/observability/events/{event['event_id']}.json")
        try:
            atomic_json(path, event)
        except FileExistsError:
            old = read_json(path, 32000)
            keys = ("type", "source", "trace_id", "span_id", "session_id", "role", "skill", "hook")
            if dedupe_key is None or any(old.get(k) != event.get(k) for k in keys):
                raise ValueError("conflicting duplicate event")
            return None
        return event


def configure(root, enabled, sample_kind="real"):
    store = Store(root)
    base = safe_path(store.root, ".ai/observability")
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    ignore = safe_path(store.root, ".ai/observability/.gitignore")
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")
    elif ignore.read_text(encoding="utf-8").strip() != "*":
        raise ValueError("private telemetry ignore policy was modified; review before enabling")
    config = {**store.config, "enabled": enabled, "salt": store.config.get("salt", uuid.uuid4().hex),
              "sample_kind": sample_kind, "version": VERSION}
    atomic_json(safe_path(store.root, ".ai/observability/config.json"), config, replace=True)


def hook_record(root, provider, payload):
    store = Store(root)
    if not store.enabled:
        return
    if not isinstance(payload, dict) or payload.get("hook_event_name") not in HOOKS:
        raise ValueError("unsupported hook")
    hook = payload["hook_event_name"]
    sid = payload.get("session_id")
    if not isinstance(sid, str) or not sid:
        raise ValueError("missing host session")
    session = store.hash_id(provider + sid)
    explicit = ident(os.environ.get("AI_NATIVE_TRACE_ID"))
    trace = explicit or "TRACE-" + store.hash_id(provider + sid + str(payload.get("turn_id") or payload.get("prompt_id") or "session"))
    agent = payload.get("agent_id")
    span = "SPAN-" + store.hash_id(str(agent or sid))
    run_id = ident(os.environ.get("AI_NATIVE_RUN_ID"))
    shared = dict(provider=provider, session_id=session, run_id=run_id, hook=hook,
                  model=ident(payload.get("model")), role=payload.get("agent_type") if payload.get("agent_type") in ROLES else None,
                  execution_mode="native_subagent" if agent else "unknown")
    source = provider + "_hook"
    call_id = payload.get("tool_use_id")
    stable = source + session + hook + call_id if isinstance(call_id, str) and hook in ("PostToolUse", "PostToolUseFailure") else None
    store.emit("hook_fired", source, trace, span, dedupe_key=stable, **shared)
    if hook in ("SubagentStart", "SubagentStop"):
        if not isinstance(agent, str) or not agent:
            raise ValueError("missing native agent identity")
        store.emit("native_subagent_started" if hook == "SubagentStart" else "native_subagent_stopped", source, trace, span,
                   parent_span_id="SPAN-" + store.hash_id(sid), **shared)
    tool = payload.get("tool_input")
    if hook == "PostToolUse" and provider == "claude" and payload.get("tool_name") == "Skill" and isinstance(tool, dict):
        skill = tool.get("skill")
        if skill in SKILLS:
            store.emit("skill_invoked", source, trace, span, dedupe_key=stable + ":skill" if stable else None,
                       skill=skill, result="invoked_not_verified", **shared)
    if hook == "PostModelRequest" and provider == "codex":
        usage = normalize_usage("codex", payload.get("token_usage"))
        store.emit("usage_observed", source, trace, span, usage=usage, usage_scope="request",
                   result=payload.get("status") if payload.get("status") in ("completed", "failed", "cancelled") else "unknown", **shared)


def hooks_plan(root, provider):
    name = ".codex/hooks.json" if provider == "codex" else ".claude/settings.json"
    path = safe_path(root, name)
    old = read_json(path) if path.is_file() else {}
    obj = json.loads(json.dumps(old))
    if not isinstance(obj, dict) or not isinstance(obj.get("hooks", {}), dict):
        raise ValueError("invalid existing hook configuration")
    events = [h for h in HOOKS if h != "PreToolUse" and not (provider == "codex" and h == "PostToolUseFailure") and not (provider == "claude" and h == "PostModelRequest")]
    command = ('root="${CLAUDE_PROJECT_DIR:-$PWD}"; while [ ! -f "$root/.ai/tools/harness_observe.py" ]; do '
               '[ "$root" != / ] || exit 0; root=$(dirname "$root"); done; '
               'python3 "$root/.ai/tools/harness_observe.py" --root "$root" hook --provider ' + provider)
    for event in events:
        groups = obj.setdefault("hooks", {}).setdefault(event, [])
        if not isinstance(groups, list):
            raise ValueError("invalid existing matcher groups")
        found = any(isinstance(g, dict) and isinstance(g.get("hooks"), list) and
                    any(isinstance(h, dict) and h.get("command") == command for h in g["hooks"]) for g in groups)
        if not found:
            groups.append({"hooks": [{"type": "command", "command": command, "timeout": 5}]})
    return path, old, obj


def install_hooks(root, provider, apply=False):
    path, old, new = hooks_plan(root, provider)
    changed = old != new
    if apply and changed:
        # Additive atomic edit; do not copy potentially secret settings into telemetry backups.
        atomic_json(path, new, replace=True)
    return {"changed": changed, "applied": apply and changed, "hook_trust": "not_granted",
            "runtime_validation": "not_performed", "config": str(path.relative_to(Path(root).resolve()))}


def observe_run(root, args, run_fn):
    """Runner calls this adapter after argument parsing; its validation/permissions stay authoritative.

run_fn accepts observer=None and uses it only at the provider subprocess boundary.
Telemetry failure is visible but never changes the underlying result or authorization.
"""
    try:
        store = Store(root)
        if not store.enabled:
            return run_fn(root, args)
    except (OSError, ValueError):
        print("OBSERVABILITY_UNAVAILABLE", file=sys.stderr)
        return run_fn(root, args)
    trace = ident(os.environ.get("AI_NATIVE_TRACE_ID")) or "TRACE-" + uuid.uuid4().hex
    span = "SPAN-" + uuid.uuid4().hex
    common = dict(run_id=ident(args.run_id), goal_id=ident(args.goal), task_id=ident(args.task),
                  provider=args.provider, role=args.role, execution_mode="cli_role")
    def emit(kind, **data):
        try:
            store.emit(kind, "runner", trace, span, **common, **data)
        except (OSError, ValueError, TypeError):
            print("OBSERVABILITY_WRITE_FAILED", file=sys.stderr)
    emit("run_requested", result="execute_requested" if args.execute else "dry_run")
    launched = False
    terminal = "unknown"
    def observer(command, **kwargs):
        nonlocal launched, terminal
        launched = True
        emit("process_started", result="started")
        env = dict(kwargs.get("env") or os.environ)
        env.update(AI_NATIVE_TRACE_ID=trace, AI_NATIVE_RUN_ID=args.run_id)
        kwargs["env"] = env
        started = time.monotonic()
        try:
            result = subprocess.run(command, **kwargs)
            usage, terminal = provider_usage(args.provider, result.stdout)
            emit("usage_observed", usage=usage, usage_scope="run_total",
                 duration_ms=round((time.monotonic() - started) * 1000), exit_code=result.returncode,
                 result=terminal)
            return result
        except subprocess.TimeoutExpired:
            terminal = "timeout"
            emit("usage_observed", usage=empty_usage("timeout"), usage_scope="run_total", result="timeout")
            raise
        except OSError:
            terminal = "process_error"
            emit("usage_observed", usage=empty_usage("process_error"), usage_scope="run_total", result="failed")
            raise
    started = time.monotonic()
    rc = None
    try:
        rc = run_fn(root, args, observer=observer)
        return rc
    finally:
        result = "dry_run" if not args.execute else ("not_started" if not launched else
                 ("process_succeeded" if rc == 0 and terminal == "completed" else "failed_or_unverified"))
        emit("run_finished", result=result, reason=terminal if launched else None,
             exit_code=rc, duration_ms=round((time.monotonic() - started) * 1000))



def record_route(root, kind):
    try:
        store = Store(root)
        store.emit("route_reported", "runner", ident(os.environ.get("AI_NATIVE_TRACE_ID")) or "TRACE-" + uuid.uuid4().hex,
                   "SPAN-" + uuid.uuid4().hex, route_kind=kind, result="plan_only", reason="no_agent_started")
    except (OSError, ValueError, TypeError):
        print("OBSERVABILITY_WRITE_FAILED", file=sys.stderr)


def record_gate(root, result):
    try:
        store = Store(root)
        gate = result.get("gate_id")
        store.emit("gate_checked", "gate_checker", ident(os.environ.get("AI_NATIVE_TRACE_ID")) or "TRACE-" + uuid.uuid4().hex,
                   "SPAN-" + uuid.uuid4().hex, gate_id=gate if gate in ("TEST_VERIFY_GATE", "OPS_READY_GATE") else None,
                   result="checks_passed" if result.get("checks_passed") else "checks_failed",
                   reason="not_business_acceptance")
    except (OSError, ValueError, TypeError):
        print("OBSERVABILITY_WRITE_FAILED", file=sys.stderr)


def load_events(root, include_fixtures=False):
    folder = safe_path(root, ".ai/observability/events")
    events, errors = [], []
    if not folder.exists():
        return events, errors
    files = sorted(folder.glob("*.json"))
    if len(files) > 100000:
        raise ValueError("event count exceeds explicit report limit")
    seen = set()
    for file in files:
        try:
            safe_path(root, file.relative_to(Path(root).resolve()))
            event = read_json(file, 32000)
            validate_event(event)
            if file.stem != event["event_id"]:
                raise ValueError("event filename and identity differ")
            if event["event_id"] in seen:
                raise ValueError("duplicate event")
            seen.add(event["event_id"])
            if include_fixtures or event["sample_kind"] == "real":
                events.append(event)
        except (ValueError, OSError, TypeError):
            errors.append("invalid_event:" + hashlib.sha256(file.name.encode()).hexdigest()[:12])
    return sorted(events, key=lambda e: (e["at"], e["event_id"])), errors


def summarize(events, errors=()):
    usage = [e for e in events if e["type"] == "usage_observed"]
    totals = {(e["trace_id"], e["run_id"]) for e in usage if e["usage_scope"] == "run_total"}
    # Never add per-request hooks to the same invocation's provider total.
    selected = [e for e in usage if e["usage_scope"] == "run_total" or (e["trace_id"], e["run_id"]) not in totals]
    complete = bool(selected) and not errors and all(e["usage"] and e["usage"]["complete"] for e in selected)
    known = [e["usage"]["total_tokens"] for e in selected if e["usage"] and e["usage"]["total_tokens"] is not None]
    starts = {e["span_id"] for e in events if e["type"] == "process_started"}
    finished = {e["span_id"] for e in events if e["type"] == "run_finished"}
    incomplete = starts - finished
    missing_usage = starts - {e["span_id"] for e in usage if e["usage_scope"] == "run_total"}
    complete = complete and not incomplete and not missing_usage
    durations = [e["duration_ms"] for e in events if e["type"] == "run_finished"
                 and e["result"] not in ("dry_run", "not_started") and e["duration_ms"] is not None]
    return {"schema": "harness-health/v1", "events": len(events), "traces": len({e["trace_id"] for e in events}),
            "source_counts": dict(Counter(e["source"] for e in events)),
            "sample_kind_counts": dict(Counter(e["sample_kind"] for e in events)),
            "fixture_data_included": any(e["sample_kind"] == "fixture" for e in events),
            "native_role_counts": dict(Counter(role or "unmapped" for role in
                {(e["session_id"], e["span_id"]): e["role"] for e in events if e["type"] == "native_subagent_started"}.values())),
            "type_counts": dict(Counter(e["type"] for e in events)),
            "native_subagent_instances": len({(e["session_id"], e["span_id"]) for e in events if e["type"] == "native_subagent_started"}),
            "skill_invocations": dict(Counter(e["skill"] for e in events if e["type"] == "skill_invoked")),
            "run_results": dict(Counter(e["result"] for e in events if e["type"] == "run_finished")),
            "usage_records": len(selected), "usage_complete_records": sum(bool(e["usage"] and e["usage"]["complete"]) for e in selected),
            "known_token_subtotal": sum(known) if known else None, "total_tokens": sum(known) if complete else None,
            "duration_samples": len(durations), "run_duration_median_ms": statistics.median(durations) if durations else None,
            "sum_run_duration_ms": sum(durations) if durations else None,
            "duration_scope": "sum_of_recorded_runs_not_wall_clock_or_human_time",
            "framework_versions": sorted({e["framework_version"] for e in events if e["framework_version"]}),
            "usage_complete": complete, "incomplete_runs": len(incomplete), "missing_run_usage": len(missing_usage), "invalid_events": list(errors),
            "business_acceptance": "not_evaluated", "director_effectiveness": "requires_independent_assessment",
            "coverage": "observed_boundaries_only", "no_data": not events}


def doctor(root):
    store = Store(root)
    events, errors = load_events(root)
    configured = {}
    for provider in ("codex", "claude"):
        path, old, new = hooks_plan(root, provider)
        configured[provider] = "configured" if old == new else "not_fully_configured"
    observed = sorted({e["provider"] for e in events if e["source"].endswith("_hook")})
    return {"enabled": store.enabled, "version": VERSION, "hooks": configured,
            "host_events_observed": observed, "hook_trust": "unknown_do_not_infer", "invalid_events": errors,
            "notice": "No events is unknown/not observed, not proof of zero activity."}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="command", required=True)
    enable = sub.add_parser("enable")
    enable.add_argument("--sample-kind", choices=("real", "fixture"), default="real")
    sub.add_parser("disable")
    sub.add_parser("status")
    sub.add_parser("schema")
    hooks = sub.add_parser("install-hooks")
    hooks.add_argument("--provider", choices=("codex", "claude"), required=True)
    hooks.add_argument("--apply", action="store_true")
    hook = sub.add_parser("hook")
    hook.add_argument("--provider", choices=("codex", "claude"), required=True)
    report = sub.add_parser("report")
    report.add_argument("--include-fixtures", action="store_true")
    prune = sub.add_parser("prune")
    prune.add_argument("--older-than-days", type=int, default=30)
    prune.add_argument("--apply", action="store_true")
    args = p.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "hook":
            try:
                data = sys.stdin.read(1_000_001)
                if len(data) > 1_000_000:
                    raise ValueError("hook payload too large")
                hook_record(root, args.provider, json.loads(data))
            except (ValueError, OSError, TypeError):
                print("OBSERVABILITY_HOOK_FAILED", file=sys.stderr)
            print("{}")  # neutral for Stop/SubagentStop; never grants permission or adds context
            return 0
        if args.command == "enable":
            configure(root, True, args.sample_kind)
            result = {"enabled": True, "location": ".ai/observability", "upload": False}
        elif args.command == "disable":
            configure(root, False, Store(root).config.get("sample_kind", "real"))
            result = {"enabled": False, "existing_events": "preserved"}
        elif args.command == "status":
            result = doctor(root)
        elif args.command == "schema":
            result = event_schema()
        elif args.command == "install-hooks":
            if args.apply and not Store(root).enabled:
                raise ValueError("enable local telemetry explicitly before installing hooks")
            result = install_hooks(root, args.provider, args.apply)
        elif args.command == "report":
            result = summarize(*load_events(root, args.include_fixtures))
        else:
            if args.older_than_days < 1:
                raise ValueError("retention days must be positive")
            events, errors = load_events(root, True)
            if errors:
                raise ValueError("repair invalid event files before pruning")
            cutoff = datetime.now(timezone.utc) - timedelta(days=args.older_than_days)
            selected = [e for e in events if datetime.fromisoformat(e["at"]) < cutoff]
            if args.apply:
                for e in selected:
                    safe_path(root, f".ai/observability/events/{e['event_id']}.json").unlink()
            result = {"eligible": len(selected), "deleted": len(selected) if args.apply else 0, "dry_run": not args.apply}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("invalid_events") else 0
    except (ValueError, OSError, TypeError):
        print("OBSERVABILITY_ERROR: invalid input, configuration or filesystem; no raw content logged", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
