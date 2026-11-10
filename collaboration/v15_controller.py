#!/usr/bin/env python3
"""V1.5 bounded coordination entry point.

Reuses the V1.4 journal, handoff reviews, authorization, TDD gates, recovery
and Codex app-server runtime sessions. Does not implement spawn_agent and
never turns fixture runs into live child-agent evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys

from agent_collaboration import Engine, Fault, drive, require
from codex_adapter import CodexAdapter
from v15_activation import activation, write_once
from v15_graph import graph, metrics, record_drift


def capabilities():
    return {
        "schema": "collaboration-dispatch-capabilities/v1",
        "codex_app_server_installed": bool(shutil.which("codex")),
        "adapter": "codex_app_server",
        "execution_mode": "runtime_session",
        "native_spawn_agent_supported": False,
        "native_spawn_agent_claim": "not_observed",
        "authorization_granted": False,
        "business_accepted": False,
    }


def release_assessment(engine: Engine):
    """Strict V1.5 release gate: a runtime_session is not a native spawn_agent."""
    result = dict(engine.check(release=True))
    findings = list(result["findings"])
    coverage = metrics(engine)
    if not capabilities()["native_spawn_agent_supported"]:
        findings.append("V15_NATIVE_SUBAGENT_BACKEND_NOT_IMPLEMENTED")
    if coverage["native_subagent_starts"] is None:
        findings.append("V15_NATIVE_SUBAGENT_EVIDENCE_UNAVAILABLE")
    elif coverage["native_subagent_starts"] <= 0:
        findings.append("V15_NATIVE_SUBAGENT_NOT_OBSERVED")
    result["checks_passed"] = not findings
    result["findings"] = findings
    result["v15_release_authorized"] = False
    result["v15_release_status"] = "BLOCKED" if findings else "ENGINEERING_READY_NOT_BUSINESS_ACCEPTED"
    result["authenticated_host_acceptance"] = ("NOT_RUN" if coverage["verified_runtime_session_starts"] == 0
                                                 else "NOT_EVALUATED")
    result["native_spawn_agent_acceptance"] = "NOT_RUN"
    result["business_project_acceptance"] = coverage["independent_business_acceptance"]
    return result


def start_plan(root, request_ref, context_out):
    context, proposed = activation(root, request_ref)
    write_once(root, context_out, context)
    engine = Engine(root, context["run_id"])
    result = engine.create(context_out)
    return {"schema": "collaboration-start-plan/v1", "activation": proposed,
            "run_id": result["run_id"], "execution": "not_started",
            "live_agent_verification": "NOT_RUN",
            "project_context_bound_in_inputs": True}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--run-id")
    cmds = p.add_subparsers(dest="command", required=True)
    start = cmds.add_parser("plan")
    start.add_argument("--request", required=True)
    start.add_argument("--context-out", required=True)
    cmds.add_parser("capabilities")
    cmds.add_parser("graph")
    cmds.add_parser("metrics")
    cmds.add_parser("recover")
    rec = cmds.add_parser("reconcile")
    rec.add_argument("--step", required=True)
    rec.add_argument("--record", required=True)
    cmds.add_parser("record-drift")
    check = cmds.add_parser("check")
    check.add_argument("--release", action="store_true")
    for cmd in ("dispatch", "drive", "review"):
        c = cmds.add_parser(cmd)
        c.add_argument("--execute", action="store_true")
        c.add_argument("--model")
        if cmd == "dispatch": c.add_argument("--step", required=True)
        if cmd == "review": c.add_argument("--handoff", required=True)
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.command == "capabilities":
            result = capabilities()
        elif args.command == "plan":
            result = start_plan(root, args.request, args.context_out)
        else:
            require(bool(args.run_id), "RUN_ID_REQUIRED")
            engine = Engine(root, args.run_id)
            if args.command == "graph":
                result = graph(engine)
            elif args.command == "metrics":
                result = metrics(engine)
            elif args.command == "record-drift":
                result = record_drift(engine)
            elif args.command == "recover":
                result = engine.recover()
            elif args.command == "reconcile":
                result = engine.reconcile(args.step, args.record)
            elif args.command == "check":
                result = release_assessment(engine) if args.release else engine.check(False)
            else:
                require(args.execute, "EXECUTE_REQUIRED")
                adapter = CodexAdapter(root, model=args.model)
                require(adapter.available(), "RUNTIME_UNAVAILABLE")
                if args.command == "dispatch":
                    result = engine.dispatch(args.step, adapter)
                elif args.command == "review":
                    result = engine.review(args.handoff, adapter)
                else:
                    result = drive(engine, adapter)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == "check":
            return 0 if result["checks_passed"] else 1
        if args.command == "graph":
            return 1 if result["new_plan_required"] else 0
        if args.command == "drive":
            return 0 if result["checks_passed"] else 1
        return 0
    except (OSError, ValueError, Fault):
        print("V15_CONTROLLER_ERROR: authorization, context, runtime or execution boundary", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
