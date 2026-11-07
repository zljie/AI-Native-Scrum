#!/usr/bin/env python3
"""V1.5 derived task graph, drift impact, and coverage-aware collaboration metrics.

The existing collaboration journal remains the ONLY execution-control source.
Derived views never mark work accepted or turn runtime_session into native_spawn.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

from agent_collaboration import Engine, Fault, file_hash, require


def drift(root, expected: dict):
    changed = []
    for ref, sha in expected.items():
        try:
            if file_hash(root, ref) != sha:
                changed.append(ref)
        except (OSError, Fault):
            changed.append(ref)
    return sorted(changed)


def graph(engine: Engine):
    state = engine.load()
    anchor_drift = drift(engine.root, state["anchors"])
    source_drift = drift(engine.root, state["source_hashes"])
    changed = sorted(set(anchor_drift + source_drift))
    # All steps in a plan are based on one approved context and policy. If a
    # shared input drifts, force a new plan, not an unproved partial rebase.
    try:
        runnable = set(engine.ready()) if not changed else set()
    except Fault:
        runnable = set()
    nodes = []
    for name, d in state["assignments"].items():
        reasons = []
        for dep in d["depends_on"]:
            if state["assignments"][dep]["status"] != "completed":
                reasons.append("DEPENDENCY_INCOMPLETE:" + dep)
                continue
            candidates = [h for h in state["handoffs"].values()
                          if h["from_delegation"] == dep and h["to_delegation"] == name]
            if not candidates:
                reasons.append("HANDOFF_REQUIRED:" + dep)
                continue
            h = max(candidates, key=lambda x: x["revision"])
            if h["status"] != "accepted":
                reasons.append("HANDOFF_NOT_ACCEPTED:" + dep)
            if h["from_attempt"] != state["assignments"][dep]["attempt"]:
                reasons.append("HANDOFF_SUPERSEDED:" + dep)
            if drift(engine.root, h["artifacts"]):
                reasons.append("HANDOFF_ARTIFACT_DRIFT:" + dep)
        if changed:
            reasons.append("PROJECT_INPUT_DRIFT")
        if state["mode"] == "blocked":
            reasons.append("RUN_BLOCKED")
        if state["finished"]:
            reasons.append("RUN_FINISHED")
        if d["status"] in ("proposed", "queued") and not reasons and name not in runnable:
            reasons.append("RESOURCE_OR_WRITE_CONFLICT")
        nodes.append({"step": name, "role": d["role"], "status": d["status"],
                      "attempt": d["attempt"], "depends_on": list(d["depends_on"]),
                      "blockers": sorted(set(reasons)),
                      "ready": name in runnable})
    return {"schema": "collaboration-task-graph/v1", "run_id": state["run_id"],
            "sample_kind": state["sample_kind"], "sequence": state["sequence"],
            "nodes": nodes, "changed_anchors": anchor_drift,
            "changed_sources": source_drift, "new_plan_required": bool(changed),
            "affected_steps": [n["step"] for n in nodes] if changed else [],
            "execution_state_authority": "collaboration-journal",
            "project_approval": "not_inferred"}


def metrics(engine: Engine):
    state, rows = engine.load(), engine.history()
    assignments = list(state["assignments"].values())
    attempts = [a for d in assignments for a in d["attempts"]]
    events = [r["event"] for r in rows]
    real_starts = [e for e in events if e["event_type"] == "AGENT_STARTED"
                   and e["source_kind"] == "codex_app_server" and e["sample_kind"] == "real"
                   and e["verification_status"] == "verified"]
    fixture_starts = [e for e in events if e["event_type"] == "AGENT_STARTED"
                      and e["sample_kind"] == "fixture"]
    usage = [a.get("usage") for a in attempts]
    known = [u for u in usage if isinstance(u, dict) and
             type(u.get("input_tokens")) is int and u["input_tokens"] >= 0
             and type(u.get("output_tokens")) is int and u["output_tokens"] >= 0]
    # Reviews can consume extra tokens but the current adapter does not return
    # review usage; claiming a complete end-to-end total would be misleading.
    subtotal = sum(u["input_tokens"] + u["output_tokens"] for u in known)
    handoffs = list(state["handoffs"].values())
    return {
        "schema": "collaboration-metrics/v1", "run_id": state["run_id"],
        "sample_kind": state["sample_kind"], "event_count": len(rows),
        "planned_steps": len(assignments),
        "completed_steps": sum(d["status"] == "completed" for d in assignments),
        "blocked_steps": sum(d["status"] == "blocked" for d in assignments),
        "attempt_count": len(attempts),
        "verified_runtime_session_starts": len(real_starts),
        "fixture_starts": len(fixture_starts),
        "native_subagent_starts": None,  # app-server threads are not spawn_agent
        "native_subagent_coverage": "not_instrumented_by_coordinator",
        "submitted_handoffs": len(handoffs),
        "accepted_handoffs": sum(h["status"] == "accepted" for h in handoffs),
        "rework_events": sum(e["event_type"] == "DEPENDENCIES_INVALIDATED" for e in events),
        "known_assignment_usage_count": len(known),
        "unknown_assignment_usage_count": len(usage) - len(known),
        "assignment_token_known_subtotal": subtotal if known else None,
        "end_to_end_token_total": None,
        "review_token_coverage": "unknown",
        "independent_business_acceptance": "NOT_EVALUATED",
        "real_agent_acceptance": "NOT_RUN" if state["sample_kind"] == "fixture" else "NOT_EVALUATED",
        "full_runtime_trace": engine.run_id,
    }


def record_drift(engine: Engine):
    impact = graph(engine)
    require(impact["new_plan_required"], "NO_DRIFT")
    with engine.lock():
        state = engine.load()
        require(not state["finished"], "CANNOT_REWRITE_FINISHED_RUN")
        # Only metadata is stored in the journal; no changed file contents.
        if state.get("reason") == "PROJECT_INPUT_DRIFT_REPLAN_REQUIRED":
            return impact
        state["mode"] = "blocked"
        state["reason"] = "PROJECT_INPUT_DRIFT_REPLAN_REQUIRED"
        engine.append(state, "PROJECT_INPUT_DRIFT", after="blocked",
                      reason="REPLAN_REQUIRED")
    return graph(engine)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--run-id", required=True)
    p.add_argument("command", choices=["graph", "metrics", "record-drift"])
    args = p.parse_args(argv)
    try:
        engine = Engine(Path(args.root), args.run_id)
        value = (graph(engine) if args.command == "graph" else
                 metrics(engine) if args.command == "metrics" else record_drift(engine))
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0 if not value.get("new_plan_required", False) else 1
    except (OSError, ValueError, Fault):
        print("COLLABORATION_GRAPH_ERROR: invalid state or protected operation", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
