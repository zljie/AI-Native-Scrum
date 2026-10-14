#!/usr/bin/env python3
"""Check bootstrap behavior and template contracts in isolated temporary folders."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


BOOTSTRAP = Path(__file__).resolve().parents[1] / "initdir.sh"
FLOW_FILES = ("dev-flow.yaml", "Goal_Constrained_Dev_Flow_v1.md")
SKILLS = (
    "goal-intake", "goal-to-backlog", "story-refine", "story-to-tasks",
    "ingest", "query", "lint", "delivery-loop",
)
REQUIRED = (
    "AGENTS.md", "WORKING_STYLE.md", "README.md", "wiki/index.md",
    "schema/entity-types.yaml", "schema/workitem-types.yaml",
    "schema/relation-types.yaml", "schema/readiness.yaml",
    "schema/id-policy.yaml", "schema/policies.yaml", "schema/intake.schema.yaml",
    "schema/templates/goal.md", "schema/templates/story.md",
    "schema/templates/task.md", "schema/templates/adr.md",
    "schema/templates/learning.md", "intake/templates/goal-draft.md",
    ".codex/hooks.json", ".codex/hooks/goal_flow.py",
    *FLOW_FILES,
) + tuple(f".ai/skills/{name}/SKILL.md" for name in SKILLS)


def field(text, key):
    # shortcut: checks fixed bootstrap scalar fields, use a YAML schema validator for full project lint.
    match = re.search(rf"^{re.escape(key)}:[ \t]*([^\n]*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def frontmatter(text):
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    return match.group(1) if match else ""


def contract_errors(root):
    errors = []
    for name in REQUIRED:
        path = root / name
        if not path.is_file() or not path.read_text().strip():
            errors.append(f"missing or empty: {name}")
    if errors:
        return errors

    draft = frontmatter((root / "intake/templates/goal-draft.md").read_text())
    if field(draft, "status") != "draft":
        errors.append("goal draft must remain unapproved")

    schema = (root / "schema/workitem-types.yaml").read_text()
    lifecycle = schema.partition("\nlifecycle:\n")[2]
    statuses = set(re.findall(r"^[ \t]+- ([a-z_]+)[ \t]*$", lifecycle, re.MULTILINE))
    for name in ("story-refine", "story-to-tasks"):
        skill = (root / f".ai/skills/{name}/SKILL.md").read_text()
        for status in re.findall(r"\bstatus: ([a-z_]+)\b", skill):
            if status not in statuses:
                errors.append(f"unknown work item status: {name}: {status}")
    if not {"ready_for_task_decomposition", "ready", "review", "done"} <= statuses:
        errors.append("missing delivery lifecycle states")

    for name in SKILLS:
        header = frontmatter((root / f".ai/skills/{name}/SKILL.md").read_text())
        if field(header, "name") != name or not field(header, "description"):
            errors.append(f"invalid skill metadata: {name}")

    readiness = (root / "schema/readiness.yaml").read_text()
    goal_ready = readiness.partition("\ngoal_ready:\n")[2].partition("\nstory_ready:")[0]
    for required in ("success_criteria_ids", "protected_constraints", "change_control"):
        if not re.search(rf"\n  {required}:\n[ \t]+required: true\b", goal_ready):
            errors.append(f"goal readiness must require {required}")
    task_ready = readiness.partition("\ntask_ready:\n")[2].partition("\nready_pool:")[0]
    if not re.search(r"\n  verification:\n[ \t]+required: true\b", task_ready):
        errors.append("task verification must be required")
    learning = frontmatter((root / "schema/templates/learning.md").read_text())
    if field(learning, "status") != "candidate":
        errors.append("new learning must be a candidate")
    if field(learning, "reuse_benefit_status") != "unmeasured":
        errors.append("new learning must not claim measured reuse benefits")

    goal = (root / "schema/templates/goal.md").read_text()
    goal_header = frontmatter(goal)
    if field(goal_header, "revision") != "1" or field(goal_header, "change_approval_required") != "true":
        errors.append("goal contract must start at revision 1 with change approval required")
    for text in ("goal_owner:", "protected_constraints: []", "### GSC-01", "## Protected Constraints", "## Change Control"):
        if text not in goal:
            errors.append(f"goal contract missing: {text}")

    for template in ("story.md", "task.md"):
        if "goal_success_criteria: []" not in (root / f"schema/templates/{template}").read_text():
            errors.append(f"{template} must trace Goal success criteria")

    policies = (root / "schema/policies.yaml").read_text()
    if "automatic_enforcement: false" not in policies or "hooks_advisory_only: true" not in policies:
        errors.append("Goal hooks must remain advisory and non-enforcing")

    for name in FLOW_FILES:
        if (root / name).read_bytes() != (BOOTSTRAP.parent / name).read_bytes():
            errors.append(f"Dev Flow differs from bootstrap source: {name}")
    flow = (root / "dev-flow.yaml").read_text()
    for expected in (
        "goalContract: raw/goals/GOAL-*.md", "workItems: wiki/workitems/",
        "workItemLifecycle: schema/workitem-types.yaml", "automaticEnforcement: false",
        "gateExecution: agent_review_with_recorded_evidence",
        "exemptionRequiresApproval: true", "dependsOn: [TEST_RED_GATE]",
        "humanApprovalRequired: true", "statuses: [ON_TRACK, AT_RISK, BLOCKED]",
        "storyLevelParallelism: requires_explicit_authorization",
    ):
        if expected not in flow:
            errors.append(f"Dev Flow contract missing: {expected}")
    for name in ("goal-intake", "goal-to-backlog", "story-refine", "story-to-tasks", "delivery-loop", "lint"):
        skill = (root / f".ai/skills/{name}/SKILL.md").read_text()
        if not all(path in skill for path in FLOW_FILES):
            errors.append(f"missing Dev Flow Skill entry: {name}")

    try:
        hooks = json.loads((root / ".codex/hooks.json").read_text())
        events = set(hooks.get("hooks", {}))
        if events != {"SessionStart", "Stop"}:
            errors.append("Goal hooks must contain only advisory SessionStart and Stop events")
        if "git rev-parse" in json.dumps(hooks):
            errors.append("Goal hook launcher must not depend on Git")
    except json.JSONDecodeError:
        errors.append("invalid .codex/hooks.json")

    try:
        compile((root / ".codex/hooks/goal_flow.py").read_text(), "goal_flow.py", "exec")
    except SyntaxError:
        errors.append("invalid Goal hook Python")
    return errors


def run_goal_hook(root, payload, cwd=None):
    hooks = json.loads((root / ".codex/hooks.json").read_text())
    command = hooks["hooks"][payload["hook_event_name"]][0]["hooks"][0]["command"]
    result = subprocess.run(
        ["sh", "-c", command], cwd=cwd or root,
        input=json.dumps(payload), capture_output=True, text=True, timeout=10,
    )
    require(result.returncode == 0, f"Goal hook failed: {result.stderr}")
    require(not result.stderr, f"Goal hook emitted errors: {result.stderr}")
    return json.loads(result.stdout)


def initialize(root):
    result = subprocess.run(
        ["bash", str(BOOTSTRAP)], cwd=root, capture_output=True, text=True,
        timeout=60,
    )
    if result.returncode:
        raise RuntimeError(f"initializer failed ({result.returncode})\n{result.stdout}\n{result.stderr}")


def snapshot(root):
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    subprocess.run(["bash", "-n", str(BOOTSTRAP)], check=True, timeout=60)
    print("PASS shell syntax")
    with tempfile.TemporaryDirectory(prefix="ai-native-scrum-check-") as temporary:
        base = Path(temporary)
        fresh = base / "fresh"
        fresh.mkdir()
        initialize(fresh)
        require(not contract_errors(fresh), f"fresh contracts: {contract_errors(fresh)}")
        require(not (fresh / ".git").exists(), "fresh initialization created Git metadata")
        start = run_goal_hook(fresh, {"hook_event_name": "SessionStart", "cwd": str(fresh)})
        require(start["hookSpecificOutput"]["hookEventName"] == "SessionStart", "missing Goal start context")
        (fresh / "raw/goals/GOAL-001.md").write_text(
            "---\nid: GOAL-001\ntitle: Example Goal\nstatus: approved\n---\n"
        )
        start_with_goal = run_goal_hook(fresh, {"hook_event_name": "SessionStart", "cwd": str(fresh)})
        require("GOAL-001 Example Goal" in start_with_goal["hookSpecificOutput"]["additionalContext"], "approved Goal missing from start context")
        reminder = run_goal_hook(fresh, {"hook_event_name": "Stop", "last_assistant_message": "已完成实现"})
        require(reminder.get("continue") is True and "systemMessage" in reminder, "missing advisory evidence reminder")
        require("decision" not in reminder, "Goal reminder must not block or continue work")
        verified = run_goal_hook(fresh, {"hook_event_name": "Stop", "last_assistant_message": "已完成实现并通过测试验证"})
        require(verified == {"continue": True}, "verified completion should not warn")
        print("PASS advisory Goal Hooks add context and reminders without blocking")
        before = snapshot(fresh)
        require(all(path.stat().st_size for path in fresh.rglob("*") if path.is_file()), "empty generated file")
        print(f"PASS fresh initialization ({len(before)} nonempty files)")
        initialize(fresh)
        require(snapshot(fresh) == before, "repeat initialization changed existing files")
        print("PASS repeat initialization preserves all file hashes")

        for topology in ("non-git", "git", "multi-repo"):
            project = base / f"{topology} project"
            project.mkdir()
            (project / "README.md").write_text("# Existing project\n")
            (project / "AGENTS.md").write_text("# Existing local rules\n")
            (project / "existing.txt").write_text("Keep my work.\n")
            if topology == "git":
                subprocess.run(["git", "init", "-q", str(project)], check=True)
            nested = project / "nested folder"
            nested.mkdir()
            if topology == "multi-repo":
                for name in ("service a", "service-b"):
                    child = project / name
                    child.mkdir()
                    subprocess.run(["git", "init", "-q", str(child)], check=True)
                    (child / "AGENTS.md").write_text("# Child rules\n")
                    (child / "README.md").write_text(f"# {name}\n")
                nested = project / "service a" / "deep folder"
                nested.mkdir()
                # A child knowledge folder must not redirect the root's hook.
                (nested.parent / "raw/goals").mkdir(parents=True)
            original = snapshot(project)
            initialize(project)
            current = snapshot(project)
            require(all(current.get(path) == digest for path, digest in original.items()),
                    f"{topology} initialization changed existing files or Git metadata")
            require(not contract_errors(project), f"{topology} contracts: {contract_errors(project)}")
            require((project / ".git").exists() == (topology == "git"), "root Git topology changed")
            if topology == "multi-repo":
                for name in ("service a", "service-b"):
                    child_files = {path: digest for path, digest in current.items() if path.startswith(name + "/")}
                    require(child_files == {path: digest for path, digest in original.items() if path.startswith(name + "/")},
                            "initializer wrote inside a child repository")
            (project / "raw/goals/GOAL-ROOT.md").write_text(
                "---\nid: GOAL-ROOT\ntitle: Root Goal\nstatus: approved\n---\n"
            )
            for location in (project, nested):
                start = run_goal_hook(project, {"hook_event_name": "SessionStart", "cwd": str(location)}, location)
                require("GOAL-ROOT Root Goal" in start["hookSpecificOutput"]["additionalContext"],
                        f"{topology} hook resolved the wrong workflow root")
                stop = run_goal_hook(project, {"hook_event_name": "Stop", "last_assistant_message": "已完成实现"}, location)
                require(stop.get("continue") is True and "decision" not in stop and "systemMessage" in stop,
                        f"{topology} stop hook lost its advisory behavior")
            before = snapshot(project)
            initialize(project)
            require(snapshot(project) == before, f"{topology} rerun changed existing files")
            print(f"PASS {topology} root and nested configured Hooks; existing files, Git topology and rerun hashes preserved")

        print("PASS standalone bootstrap embeds synchronized Dev Flow contracts and Skill handoffs")

        mutations = (
            ("intake/templates/goal-draft.md", "status: draft", "status: approved", "unapproved draft"),
            (".ai/skills/story-refine/SKILL.md", "status: ready_for_task_decomposition", "status: unknown", "unknown status"),
            (".ai/skills/delivery-loop/SKILL.md", "name: delivery-loop", "name:", "skill metadata"),
            ("schema/readiness.yaml", "  verification:\n    required: true", "  verification:\n    required: false", "verification gate"),
            ("schema/templates/learning.md", "status: candidate", "status: validated", "unverified learning"),
            ("schema/templates/learning.md", "reuse_benefit_status: unmeasured", "reuse_benefit_status: measured", "unmeasured benefit claim"),
            ("schema/templates/goal.md", "change_approval_required: true", "change_approval_required: false", "unapproved Goal change"),
            ("schema/policies.yaml", "hooks_advisory_only: true", "hooks_advisory_only: false", "enforcing Goal hooks"),
            ("dev-flow.yaml", "goalContract: raw/goals/GOAL-*.md", "goalContract: .goal/contract.yaml", "duplicate Goal source"),
            ("dev-flow.yaml", "automaticEnforcement: false", "automaticEnforcement: true", "unimplemented gate enforcement"),
            ("dev-flow.yaml", "dependsOn: [TEST_RED_GATE]", "dependsOn: [TECH_GATE]", "Dev bypassing RED"),
            (".ai/skills/delivery-loop/SKILL.md", "Goal_Constrained_Dev_Flow_v1.md", "missing-flow-guide.md", "disconnected stage Skill"),
        )
        for relative, original, invalid, label in mutations:
            path = fresh / relative
            content = path.read_text()
            require(original in content, f"negative case has no mutation target: {relative}")
            try:
                path.write_text(content.replace(original, invalid, 1))
                require(bool(contract_errors(fresh)), f"bad fixture incorrectly passed: {label}")
            finally:
                path.write_text(content)
            require(not contract_errors(fresh), f"restored fixture failed: {label}")
            print(f"PASS negative case rejects {label}; restored case passes")

        hooks_path = fresh / ".codex/hooks.json"
        original_hooks = hooks_path.read_text()
        broken_hooks = json.loads(original_hooks)
        broken_hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"] = (
            'python3 "$(git rev-parse --show-toplevel)/.codex/hooks/goal_flow.py"'
        )
        try:
            hooks_path.write_text(json.dumps(broken_hooks))
            require("Goal hook launcher must not depend on Git" in contract_errors(fresh),
                    "Git-dependent launcher incorrectly passed contract checks")
            try:
                run_goal_hook(fresh, {"hook_event_name": "SessionStart", "cwd": str(fresh)})
            except RuntimeError:
                pass
            else:
                raise RuntimeError("broken Git-dependent launcher incorrectly passed runtime checks")
        finally:
            hooks_path.write_text(original_hooks)
        require(not contract_errors(fresh), "restored launcher contracts failed")
        print("PASS regression rejects old Git-dependent Hook command at contract and runtime boundaries")

        legacy = base / "legacy"
        (legacy / "schema").mkdir(parents=True)
        old_schema = (fresh / "schema/workitem-types.yaml").read_text().replace(
            'version: "0.4"', 'version: "0.3"'
        ).replace("  - ready_for_task_decomposition\n", "")
        (legacy / "schema/workitem-types.yaml").write_text(old_schema)
        preference = "# Working Style\n\nKeep my existing preferences.\n"
        (legacy / "WORKING_STYLE.md").write_text(preference)
        custom_flow = "# Existing project-specific Dev Flow\n"
        (legacy / "dev-flow.yaml").write_text(custom_flow)
        initialize(legacy)
        require((legacy / "schema/workitem-types.yaml").read_text() == old_schema, "legacy schema overwritten")
        require((legacy / "WORKING_STYLE.md").read_text() == preference, "user preferences overwritten")
        require((legacy / "dev-flow.yaml").read_text() == custom_flow, "existing Dev Flow overwritten")
        require(bool(contract_errors(legacy)), "mixed legacy contracts were not detected")
        print("PASS legacy schema, personal preferences and existing Dev Flow preserved; incompatible contracts detected")
    print("PASS bootstrap checks complete; project knowledge and business acceptance are not evaluated")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
