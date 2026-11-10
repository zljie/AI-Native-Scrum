#!/usr/bin/env python3
"""V1.5 evidence-bound professional activation.

A coordinator supplies explicit change signals, each backed by files in a
current Project Context Pack. This validates evidence and chooses capabilities
using the existing registry/policy; it never infers business intent from names,
grants authorization or invokes a model.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys

from project_context import safe_path, validate as check_pack, ContextError, CATEGORIES
from agent_collaboration import Fault, read, validate_registry, identifier, require, file_hash

SCHEMA = "activation-request/v1"
SOURCE_CATEGORIES = {
    "copy_only": ("implementation", "requirements"),
    "ui_flow": ("interfaces", "implementation", "requirements", "tests"),
    "business_rule": ("requirements", "interfaces", "implementation"),
    "api_contract": ("interfaces",),
    "database_schema": ("database",),
    "bugfix": ("implementation", "tests"),
    "runtime_change": ("architecture", "implementation"),
    "cross_module": ("architecture", "interfaces", "implementation"),
    "production": ("architecture", "requirements"),
    "destructive": ("database", "architecture"),
    "sensitive_permission": ("requirements", "architecture"),
}



def validate_impact_review(root: Path, req: dict, signals: list, evidence: dict):
    """Validate a recorded impact review, not the human's authenticated identity.

    A file containing a reviewer name is NOT a trusted identity attestation.
    Real runs require this reviewed impact record in addition to authorization;
    runtime/business acceptance must still be verified independently.
    """
    review_ref = req.get("impact_review_ref")
    if not review_ref:
        require(req["sample_kind"] != "real", "IMPACT_REVIEW_REQUIRED")
        return None
    review = read(root, review_ref)
    require(isinstance(review, dict) and set(review) == {
        "schema", "run_id", "context_pack_ref", "proposer", "reviewer",
        "confirmation_ref", "decisions"}, "IMPACT_REVIEW_FIELDS")
    require(review["schema"] == "activation-impact-review/v1", "IMPACT_REVIEW_SCHEMA")
    require(review["run_id"] == req["run_id"] and
            review["context_pack_ref"] == req["context_pack_ref"], "IMPACT_REVIEW_CONTEXT")
    identifier(review["proposer"])
    identifier(review["reviewer"])
    require(review["reviewer"] != review["proposer"], "IMPACT_REVIEW_SELF_REVIEW")
    file_hash(root, review["confirmation_ref"])
    require(isinstance(review["decisions"], dict) and
            set(review["decisions"]) == set(signals), "IMPACT_REVIEW_DECISIONS")
    for signal in signals:
        decision = review["decisions"][signal]
        require(isinstance(decision, dict) and set(decision) == {
            "decision", "rationale", "evidence_refs"}, "IMPACT_REVIEW_DECISION_FIELDS")
        require(decision["decision"] == "required", "IMPACT_REVIEW_NOT_CONFIRMED")
        require(isinstance(decision["rationale"], str) and
                len(decision["rationale"].strip()) >= 24, "IMPACT_REVIEW_RATIONALE")
        refs = decision["evidence_refs"]
        require(isinstance(refs, list) and
                len(refs) == len(set(refs)) and
                set(refs) == set(evidence[signal]), "IMPACT_REVIEW_EVIDENCE")
        for path in refs:
            file_hash(root, path)
    return review

def activation(root: Path, request_ref: str,
               registry_ref="schema/collaboration/registry.json",
               policy_ref="schema/collaboration/policy.json"):
    root = Path(root).resolve()
    req = read(root, request_ref)
    mandatory = {"schema", "run_id", "goal_ref", "story_ref", "task_ref",
                 "authorization_ref", "sample_kind", "context_pack_ref",
                 "signals", "signal_evidence", "scopes"}
    require(isinstance(req, dict) and mandatory <= set(req) and
            set(req) <= mandatory | {"verification", "impact_review_ref"}, "ACTIVATION_FIELDS")
    require(req["schema"] == SCHEMA, "ACTIVATION_SCHEMA")
    identifier(req["run_id"])
    require(req["sample_kind"] in ("real", "fixture"), "SAMPLE_KIND")
    pack = read(root, req["context_pack_ref"])
    try:
        result = check_pack(root, pack)
    except (ContextError, ValueError):
        raise Fault("PACK_INVALID") from None
    require(result["current"], "PACK_STALE")
    require(req["goal_ref"] == pack["goal_ref"] and req["task_ref"] == pack["task_ref"], "PACK_TASK_MISMATCH")
    for field in ("goal_ref", "story_ref", "task_ref", "authorization_ref"):
        file_hash(root, req[field])
    registry, policy = read(root, registry_ref), read(root, policy_ref)
    roles, steps = validate_registry(registry, policy)
    valid = set(policy["signals"])
    signals = req["signals"]
    require(isinstance(signals, list) and bool(signals) and len(signals) == len(set(signals)), "SIGNALS_INVALID")
    require(set(signals) <= valid and set(signals) <= set(SOURCE_CATEGORIES), "SIGNALS_UNKNOWN")
    evidence = req["signal_evidence"]
    require(isinstance(evidence, dict) and set(evidence) == set(signals), "SIGNAL_EVIDENCE_REQUIRED")
    sources = {category: {entry["ref"] for entry in pack["sources"][category]}
               for category in CATEGORIES}
    allowed_sources = {signal: set().union(*(sources[category] for category in SOURCE_CATEGORIES[signal]))
                       for signal in signals}
    for signal in signals:
        provided = evidence[signal]
        require(isinstance(provided, list) and bool(provided) and len(provided) == len(set(provided)), "SIGNAL_EVIDENCE_REQUIRED")
        require(set(provided) <= allowed_sources[signal], "SIGNAL_NOT_GROUNDED")
    impact_review = validate_impact_review(root, req, signals, evidence)
    if "database_schema" not in signals:
        # DB source presence never implies a DB migration or specialist activation.
        db_required = False
    else:
        db_required = True
    inputs = list(dict.fromkeys(
        [req["context_pack_ref"], pack["request_ref"]]
        + list(pack["dependencies"])
        + [entry["ref"] for category in CATEGORIES for entry in pack["sources"][category]]
        + ([req["impact_review_ref"], impact_review["confirmation_ref"]]
           if impact_review else [])
    ))
    require(inputs, "PACK_EMPTY")
    for path in inputs:
        file_hash(root, path)
    matched = [step for step in steps if set(step["signals"]) & set(signals)]
    chosen, used = [], set()
    for step in matched:
        candidates = sorted((entry["priority"], role) for role, entry in roles.items()
                            if entry["enabled"] and step["capability"] in entry["capabilities"])
        require(bool(candidates), "CAPABILITY_UNAVAILABLE")
        role = candidates[0][1]
        chosen.append({"step": step["id"], "capability": step["capability"], "role": role,
                       "reason_signals": sorted(set(step["signals"]) & set(signals)),
                       "depends_on": [d for d in step["depends_on"] if d in
                                      {s["id"] for s in matched}]})
        used.add(role)
    require(chosen, "NO_MATCHING_TASKS")
    context = {"schema": "task-context/v1", "run_id": req["run_id"],
               "goal_ref": req["goal_ref"], "story_ref": req["story_ref"],
               "task_ref": req["task_ref"], "signals": signals,
               "signal_evidence": evidence, "inputs": inputs,
               "scopes": req["scopes"], "authorization_ref": req["authorization_ref"],
               "sample_kind": req["sample_kind"]}
    if "verification" in req:
        context["verification"] = req["verification"]
    preview = {"schema": "activation-preview/v1", "run_id": req["run_id"],
               "context_pack_ref": req["context_pack_ref"],
               "context_pack_current": True, "database_change_signalled": db_required,
               "impact_review": "recorded_identity_unverified" if impact_review else "fixture_only_not_recorded",
               "assignments": chosen,
               "skipped_roles": {r: ("disabled" if not e["enabled"] else "no_matching_capability")
                                 for r, e in roles.items() if r not in used},
               "execution": "not_started", "native_subagent": "not_observed",
               "authority": "unchanged"}
    return context, preview


def write_once(root: Path, output_ref: str, data: dict):
    path = safe_path(root, output_ref, False)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise Fault("OUTPUT_EXISTS")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, sort_keys=True, indent=2)
        out.write("\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--request", required=True)
    p.add_argument("--output", help="Create a task-context/v1 file; omit for read-only preview")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        context, preview = activation(root, args.request)
        if args.output:
            write_once(root, args.output, context)
            preview["task_context_ref"] = args.output
        print(json.dumps(preview, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except (Fault, ContextError, OSError, ValueError):
        print("ACTIVATION_ERROR: invalid or stale context, evidence or authorization", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
