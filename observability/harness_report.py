#!/usr/bin/env python3
"""Local health/paired-experiment reports. Outcomes require separately supplied evidence."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import re
import statistics
import sys
import tempfile
import os
import hashlib
from harness_observe import load_events, summarize, safe_path, read_json, SKILLS, ident

SHA = re.compile(r"[a-f0-9]{64}\Z")
CASE_FIELDS = {"case_id", "repeat", "variant", "task_sha256", "acceptance_sha256", "model_config_sha256",
               "environment_sha256", "framework_revision", "trace_ids", "observation_complete", "expected_director",
               "director_guidance_passed", "native_agent_applicable", "engineering_passed", "first_pass",
               "rework_count", "human_active_seconds", "evidence_refs", "reviewer_source", "reviewer_id"}


def ratio(values):
    known = [v for v in values if v is not None]
    return {"value": sum(known) / len(known) if known else None, "known": len(known), "missing": len(values) - len(known)}


def validate_manifest(root, doc):
    if not isinstance(doc, dict) or set(doc) != {"schema", "experiment_id", "cases"} or doc["schema"] != "harness-experiment/v1":
        raise ValueError("invalid experiment schema")
    if not ident(doc["experiment_id"]) or not isinstance(doc["cases"], list) or not doc["cases"]:
        raise ValueError("experiment requires cases")
    seen, traces, pairs = set(), set(), {}
    for case in doc["cases"]:
        if not isinstance(case, dict) or set(case) != CASE_FIELDS:
            raise ValueError("invalid case fields")
        if not ident(case["case_id"]) or type(case["repeat"]) is not int or case["repeat"] < 1 or case["variant"] not in ("baseline", "candidate"):
            raise ValueError("invalid case identity")
        key = (case["case_id"], case["repeat"], case["variant"])
        if key in seen:
            raise ValueError("duplicate case observation")
        seen.add(key)
        signature = tuple(case[name] for name in ("task_sha256", "acceptance_sha256", "model_config_sha256", "environment_sha256"))
        if not all(isinstance(v, str) and SHA.fullmatch(v) for v in signature):
            raise ValueError("missing reproducibility fingerprints")
        paired = key[:2]
        if paired in pairs and pairs[paired] != signature:
            raise ValueError("paired conditions are not comparable")
        pairs[paired] = signature
        if not ident(case["framework_revision"]):
            raise ValueError("framework revision missing")
        ids = case["trace_ids"]
        if not isinstance(ids, list) or not ids or not all(ident(t) for t in ids) or len(set(ids)) != len(ids):
            raise ValueError("invalid trace references")
        if traces.intersection(ids):
            raise ValueError("one trace cannot count in two observations")
        traces.update(ids)
        for field in ("observation_complete", "native_agent_applicable"):
            if type(case[field]) is not bool:
                raise ValueError("missing applicability/coverage label")
        for field in ("director_guidance_passed", "engineering_passed", "first_pass"):
            if case[field] is not None and type(case[field]) is not bool:
                raise ValueError("outcome must be boolean or null")
        if case["first_pass"] is True and case["engineering_passed"] is not True:
            raise ValueError("first pass contradicts final outcome")
        if case["expected_director"] is not None and case["expected_director"] not in SKILLS:
            raise ValueError("unknown expected skill")
        for field in ("rework_count", "human_active_seconds"):
            v = case[field]
            if v is not None and (type(v) is not int or v < 0):
                raise ValueError("invalid effort measurement")
        if case["reviewer_source"] not in ("human", "independent_test_runner") or not ident(case["reviewer_id"]):
            raise ValueError("independent assessment provenance required")
        refs = case["evidence_refs"]
        if not isinstance(refs, list) or not refs:
            raise ValueError("assessment evidence required")
        for ref in refs:
            path = safe_path(root, ref)
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError("assessment evidence missing")
    for case_id, repetition in pairs:
        if not all((case_id, repetition, variant) in seen for variant in ("baseline", "candidate")):
            raise ValueError("both variants are required for each paired case")


def compare(root, manifest, include_fixtures=False):
    validate_manifest(root, manifest)
    events, errors = load_events(root, include_fixtures)
    if errors:
        raise ValueError("invalid telemetry must be repaired before comparison")
    rows = []
    for case in manifest["cases"]:
        selected = [e for e in events if e["trace_id"] in case["trace_ids"]]
        if {e["trace_id"] for e in selected} != set(case["trace_ids"]):
            raise ValueError("referenced trace is missing or excluded as fixture")
        health = summarize(selected)
        observed = case["observation_complete"] and health["incomplete_runs"] == 0
        expected = case["expected_director"]
        observed_skill = bool(health["skill_invocations"].get(expected))
        has_claude_hook = any(e["source"] == "claude_hook" for e in selected)
        has_native_hook = any(e["source"] in ("codex_hook", "claude_hook") for e in selected)
        invoked = (True if observed_skill else False if observed and has_claude_hook else None) if expected is not None else None
        native = (True if health["native_subagent_instances"] > 0 else False if observed and has_native_hook else None) if case["native_agent_applicable"] else None
        rows.append({"case_id": case["case_id"], "repeat": case["repeat"], "variant": case["variant"],
                     "tokens": health["total_tokens"] if observed else None,
                     "director_invoked": invoked,
                     "director_effective": case["director_guidance_passed"] if expected is not None else None,
                     "native_participation": native,
                     "engineering_passed": case["engineering_passed"], "first_pass": case["first_pass"],
                     "rework_count": case["rework_count"], "human_active_seconds": case["human_active_seconds"]})
    variants = {}
    for variant in ("baseline", "candidate"):
        selected = [r for r in rows if r["variant"] == variant]
        token_values = [r["tokens"] for r in selected]
        total = sum(token_values) if all(v is not None for v in token_values) else None
        passed = sum(r["engineering_passed"] is True for r in selected)
        all_outcomes_known = all(r["engineering_passed"] is not None for r in selected)
        variants[variant] = {"cases": len(selected), "token_total": total,
            "token_median": statistics.median(token_values) if total is not None else None,
            "token_missing_cases": sum(v is None for v in token_values),
            "tokens_per_passed_case": total / passed if total is not None and passed and all_outcomes_known else None,
            **{name: ratio([r[name] for r in selected]) for name in ("director_invoked", "director_effective", "native_participation", "engineering_passed", "first_pass", "rework_count", "human_active_seconds")}}
    baseline, candidate = (variants[v]["token_total"] for v in ("baseline", "candidate"))
    delta = (candidate - baseline) / baseline * 100 if baseline is not None and baseline > 0 and candidate is not None else None
    return {"schema": "harness-comparison/v1", "experiment_id": manifest["experiment_id"], "variants": variants,
            "token_change_percent": delta, "rows": rows,
            "fixture_data_included": any(e["sample_kind"] == "fixture" for e in events),
            "evidence_hashes": {ref: hashlib.sha256(safe_path(root, ref).read_bytes()).hexdigest() for c in manifest["cases"] for ref in c["evidence_refs"]},
            "limitations": ["Pilot descriptive comparison, not a causal or statistical significance claim.",
                "Human/independent-test labels are externally supplied; collector cannot authenticate authorship.",
                "Skill invocation does not prove correct guidance. Missing usage is not zero.",
                "Failure/retry cost is included only when every attempt trace is registered.",
                "Token counts are not subscription charges or monetary cost."]}


def render_html(report):
    content = html.escape(json.dumps(report, ensure_ascii=False, indent=2))
    return ('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Harness observability report</title><style>body{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:0 1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:1.5rem;border:1px solid #ccc}h1{font-size:1.8rem}</style>'
            '<h1>AI-Native-Scrum 运行与实验报告</h1><p>本地数据；未知值保持 null。运行成功不等于人工业务验收。</p><pre>' + content + '</pre></html>')


def save_report(root, output, report):
    path = safe_path(root, output)
    if not Path(output).parts or Path(output).parts[0] != "generated" or path.suffix not in (".json", ".html"):
        raise ValueError("exports must be new generated/*.json or *.html files")
    if path.exists():
        raise ValueError("report exists; choose a new versioned filename")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_html(report) if path.suffix == ".html" else json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    fd, name = tempfile.mkstemp(prefix=".report-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.link(name, path)
    finally:
        os.unlink(name)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--manifest", help="project-relative evidence-backed paired experiment JSON")
    p.add_argument("--trace", help="show one observed trace as a metadata-only timeline")
    p.add_argument("--include-fixtures", action="store_true", help="explicit diagnostic use only")
    p.add_argument("--output", help="new generated/reports/*.json or *.html; never overwrites")
    args = p.parse_args(argv)
    try:
        root = args.root.resolve()
        if args.manifest and args.trace:
            raise ValueError("choose a comparison or one trace")
        if args.trace:
            if not ident(args.trace):
                raise ValueError("invalid trace identity")
            events, errors = load_events(root, args.include_fixtures)
            selected = [e for e in events if e["trace_id"] == args.trace]
            if not selected:
                raise ValueError("trace not observed")
            result = {**summarize(selected, errors), "trace_id": args.trace, "timeline": selected}
        else:
            result = compare(root, read_json(safe_path(root, args.manifest)), args.include_fixtures) if args.manifest else summarize(*load_events(root, args.include_fixtures))
        if args.output:
            save_report(root, args.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get("invalid_events") else 0
    except (ValueError, OSError, TypeError):
        print("OBSERVABILITY_REPORT_ERROR: invalid/unsafe/missing input or non-comparable pairs", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
