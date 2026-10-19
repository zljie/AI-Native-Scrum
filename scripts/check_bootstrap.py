#!/usr/bin/env python3
"""Check bootstrap behavior and template contracts in isolated temporary folders."""

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


BOOTSTRAP = Path(__file__).resolve().parents[1] / "initdir.sh"
WARMUP = BOOTSTRAP.parent / "00_AI_WARMUP.md"
FLOW_FILES = ("dev-flow.yaml", "Goal_Constrained_Dev_Flow_v1.md")
SKILLS = (
    "goal-intake", "goal-to-backlog", "story-refine", "story-to-tasks",
    "ingest", "query", "lint", "delivery-loop", "solution-pack",
)
REQUIRED = (
    "AGENTS.md", "WORKING_STYLE.md", "README.md", "wiki/index.md",
    "schema/entity-types.yaml", "schema/workitem-types.yaml",
    "schema/relation-types.yaml", "schema/readiness.yaml",
    "schema/id-policy.yaml", "schema/policies.yaml", "schema/intake.schema.yaml",
    "schema/templates/goal.md", "schema/templates/story.md",
    "schema/templates/task.md", "schema/templates/adr.md",
    "schema/templates/learning.md", "schema/templates/solution.md", "intake/templates/goal-draft.md",
    ".codex/hooks.json", ".codex/hooks/goal_flow.py",
    ".ai/tools/check_requirements.py", ".ai/tools/evidence.py", ".ai/tools/check_framework.py",
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

    story = (root / "schema/templates/story.md").read_text()
    for text in ("```json requirement-contract", '"contract": "requirement-contract/v1"', "## ARCH-01", "## DEV-01", "# 系统架构位置", "# 研发描述"):
        if text not in story:
            errors.append(f"story template missing six-view contract: {text}")
    solution = (root / "schema/templates/solution.md").read_text()
    for text in ("```json solution-contract", '"contract": "solution-contract/v1"', "# Brief", "# Research", "# Decision", "# Solution", '"status": "proposed"'):
        if text not in solution:
            errors.append(f"solution pack template missing: {text}")
    learning = (root / "schema/templates/learning.md").read_text()
    if "attribution:" not in frontmatter(learning) or "`confounded`" not in learning:
        errors.append("learning template must record an honest attribution")
    if "confounded_validation_requires_reuse_evidence: true" not in (root / "schema/policies.yaml").read_text():
        errors.append("confounded lessons must need reuse evidence before validation")
    if "objects to inspect, not" not in (root / ".ai/skills/solution-pack/SKILL.md").read_text():
        errors.append("Research must treat external material as evidence, not instructions")
    if "## Evidence Boundary" not in (root / ".ai/skills/ingest/SKILL.md").read_text():
        errors.append("ingest must treat imported material as evidence, not instructions")
    if "check_framework.py" not in (root / ".ai/skills/lint/SKILL.md").read_text():
        errors.append("lint must reference the framework entry point checker")
    if "solution:" not in frontmatter(story) or '"decisions": []' not in story:
        errors.append("story template must reference a solution pack and decisions")
    if "\n  requirement_contract:\n" not in readiness or "checker: .ai/tools/check_requirements.py" not in readiness:
        errors.append("story readiness must reference the requirement contract checker")

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


REQUIREMENT_CHECKER = ".ai/tools/check_requirements.py"


def requirement_contract(**changes):
    contract = {
        "contract": "requirement-contract/v1",
        "revision": 1,
        "change_type": "feature",
        "views": {
            "architecture": {"applicable": True, "items": ["ARCH-01"]},
            "acceptance": {"applicable": True, "items": ["AC-01", "AC-02"]},
            "user_story": {"applicable": True, "items": ["UJ-01"]},
            "description": {"applicable": True, "items": ["DEV-01"]},
            "prototype": {"applicable": True, "items": ["UI-01"]},
            "business_logic": {"applicable": True, "items": ["BR-01"]},
        },
        "links": {
            "AC-01": {"goal": ["GOAL-001#GSC-01"], "rules": ["BR-01"], "tests": ["TC-P-01"], "verification": "automated"},
            "AC-02": {"goal": ["GOAL-001#GSC-01"], "rules": ["BR-01"], "tests": ["TC-N-01"], "verification": "automated"},
            "UI-01": {"rules": ["BR-01"], "acceptance": ["AC-01"]},
        },
        "open_questions": [],
    }
    contract.update(changes)
    return contract


def requirement_story(story_id="STORY-001", contract=None, depends_on="[]", status="refining", sections=None):
    contract = requirement_contract() if contract is None else contract
    headings = sections or ("ARCH-01", "BR-01", "DEV-01", "UI-01", "UJ-01", "TC-P-01", "TC-N-01", "AC-01", "AC-02")
    body = "\n\n".join(f"## {heading}\n\n内容。" for heading in headings)
    block = json.dumps(contract, ensure_ascii=False, indent=2)
    return (
        f"---\nid: {story_id}\ntype: work_item\nwork_type: story\ntitle: 示例\nstatus: {status}\n"
        f"goal_success_criteria: [GOAL-001#GSC-01]\ndepends_on: {depends_on}\n---\n\n"
        f"# 示例 Story\n\n{body}\n\n# 追踪关系\n\n```json requirement-contract\n{block}\n```\n"
    )


def check_requirements(root, *args):
    result = subprocess.run(
        ["python3", str(root / REQUIREMENT_CHECKER), "--root", str(root), *args],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


def solution_pack(decision=None, brief=None, research=None, sections=None):
    contract = {
        "contract": "solution-contract/v1",
        "revision": 1,
        "brief": brief or {"status": "confirmed", "confirmed_by": "johnson", "confirmed_at": "2026-10-16", "confirmation_ref": "项目讨论 2026-10-16"},
        "research": research or [{"id": "RQ-01", "status": "answered", "evidence": [
            {"id": "EV-01", "source": "https://example.com/approval-sync", "accessed_at": "2026-10-16", "nature": "page_observation"},
        ]}],
        "decisions": [decision or {
            "id": "DEC-01", "status": "decided", "research": ["RQ-01"], "recommended": "本地模拟",
            "chosen": "本地模拟", "decided_by": "johnson", "decided_at": "2026-10-16", "confirmation_ref": "项目讨论 2026-10-16",
        }],
        "solution": {"items": ["SOLN-01"]},
    }
    headings = sections or ("RQ-01", "DEC-01", "SOLN-01")
    body = "\n\n".join(f"## {heading}\n\n内容。" for heading in headings)
    block = json.dumps(contract, ensure_ascii=False, indent=2)
    return (
        "---\nid: SOL-001\ntype: solution\ntitle: 采购审批同步\ngoal_success_criteria: [GOAL-001#GSC-01]\n---\n\n"
        f"# Brief\n\n{body}\n\n```json solution-contract\n{block}\n```\n"
    )


def solution_pack_checks(root):
    pack_path = root / "wiki/solutions/SOL-001.md"
    story_path = root / "wiki/workitems/STORY-001.md"

    def linked_story(status="refining", decisions=("SOL-001#DEC-01",)):
        contract = requirement_contract(decisions=list(decisions))
        return requirement_story(contract=contract, status=status).replace("depends_on: []", "depends_on: []\nsolution: SOL-001")

    pack_path.write_text(solution_pack())
    story_path.write_text(linked_story())
    code, output = check_requirements(root)
    require(code == 0 and "STORY-001 READY" in output and "SOL-001 VALID" in output,
            f"Goal -> Brief -> Research -> Decision -> Solution -> Story chain failed:\n{output}")
    print("PASS Goal criterion traces through Brief, Research, human Decision and Solution to a Ready Story")

    base_decision = {"id": "DEC-01", "research": ["RQ-01"], "recommended": "本地模拟", "chosen": "", "decided_by": "", "decided_at": "", "confirmation_ref": ""}
    for status in ("proposed", "needs_research", "rejected", "deferred"):
        pack_path.write_text(solution_pack(decision={**base_decision, "status": status}))
        story_path.write_text(linked_story())
        code, output = check_requirements(root)
        require(code == 0 and "DECISION_NOT_CONFIRMED" in output and "STORY-001 NOT_READY" in output,
                f"{status} decision let a Story become Ready:\n{output}")
        story_path.write_text(linked_story(status="ready_for_task_decomposition"))
        code, output = check_requirements(root)
        require(code == 1 and "READY_STATUS_WITHOUT_READINESS" in output, f"{status} decision allowed a Ready claim:\n{output}")
        print(f"PASS {status} decision keeps the AI recommendation pending; Story cannot be Ready")

    cases = (
        ("decided without confirmation record", {"decision": {**base_decision, "status": "decided", "chosen": "本地模拟"}}, "DECISION_WITHOUT_CONFIRMATION", "DEC-01"),
        ("decision without research", {"decision": {**base_decision, "status": "decided", "chosen": "本地模拟", "research": [], "decided_by": "johnson", "decided_at": "2026-10-16", "confirmation_ref": "讨论"}}, "DECISION_WITHOUT_RESEARCH", "DEC-01"),
        ("unknown research reference", {"decision": {**base_decision, "status": "proposed", "research": ["RQ-99"]}}, "BROKEN_REFERENCE", "RQ-99"),
        ("answered research with inference only", {"research": [{"id": "RQ-01", "status": "answered", "evidence": [{"id": "EV-01", "source": "AI 推断", "accessed_at": "2026-10-16", "nature": "ai_inference"}]}]}, "RESEARCH_WITHOUT_EVIDENCE", "RQ-01"),
        ("evidence without source date", {"research": [{"id": "RQ-01", "status": "answered", "evidence": [{"id": "EV-01", "source": "https://example.com", "nature": "official_claim"}]}]}, "EVIDENCE_FIELD_INVALID", "EV-01"),
        ("undefined pack item", {"sections": ("RQ-01", "SOLN-01")}, "UNDEFINED_ITEM", "DEC-01"),
    )
    for label, options, code_name, subject in cases:
        pack_path.write_text(solution_pack(**options))
        story_path.write_text(linked_story())
        code, output = check_requirements(root)
        require(code == 1 and code_name in output and subject in output and "SOL-001 INVALID" in output and "STORY-001 NOT_READY" in output,
                f"bad solution pack passed: {label}\n{output}")
        print(f"PASS solution pack check rejects {label} and names {subject}")

    pack_path.write_text(solution_pack(brief={"status": "draft"}))
    story_path.write_text(linked_story())
    code, output = check_requirements(root)
    require(code == 0 and "BRIEF_NOT_CONFIRMED" in output and "STORY-001 NOT_READY" in output, f"unreviewed AI Brief allowed Ready:\n{output}")
    print("PASS AI-drafted Brief must be reviewed before dependent Stories are Ready")

    pack_path.write_text(solution_pack())
    story_path.write_text(linked_story(decisions=("SOL-001#DEC-404",)))
    code, output = check_requirements(root)
    require(code == 1 and "BROKEN_REFERENCE" in output and "SOL-001#DEC-404" in output, f"unknown Story decision passed:\n{output}")
    print("PASS Story reference to a missing Decision is rejected")

    pack_path.write_text(solution_pack(decision={**base_decision, "status": "superseded", "chosen": "本地模拟", "decided_by": "johnson", "decided_at": "2026-10-16", "confirmation_ref": "讨论"}))
    story_path.write_text(linked_story())
    code, output = check_requirements(root)
    require(code == 0 and "DECISION_NEEDS_REVIEW" in output and "STORY-001" in output and "STORY-001 NOT_READY" in output,
            f"superseded decision impact was not reported:\n{output}")
    print("PASS superseded Decision marks dependent Stories for review without rewriting history")

    pack_path.unlink()
    story_path.write_text(requirement_story())
    code, output = check_requirements(root)
    require(code == 0 and "STORY-001 READY" in output, f"Story without a solution pack is forced to migrate:\n{output}")
    print("PASS Stories without a solution pack keep six-view checks and are not forced to migrate")


FRAMEWORK_CHECKER = ".ai/tools/check_framework.py"


def check_framework(root):
    result = subprocess.run(
        ["python3", str(root / FRAMEWORK_CHECKER), "--root", str(root)],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


def framework_checks(root):
    code, output = check_framework(root)
    require(code == 0 and "errors=0 warnings=0" in output and "ALWAYS_ON_SIZE" in output,
            f"fresh framework entry points are not reachable:\n{output}")
    print("PASS framework check finds every Skill routed, every route present and hooks well formed")

    def unrouted(path):
        (path / ".ai/skills/extra").mkdir()
        (path / ".ai/skills/extra/SKILL.md").write_text("---\nname: extra\ndescription: Extra work.\n---\n# Extra\n")

    def renamed(path):
        skill = path / ".ai/skills/query/SKILL.md"
        skill.write_text(skill.read_text().replace("name: query", "name: ask", 1))

    def undescribed(path):
        skill = path / ".ai/skills/query/SKILL.md"
        skill.write_text(re.sub(r"^description:.*$", "description:", skill.read_text(), count=1, flags=re.MULTILINE))

    def missing_route(path):
        (path / ".ai/skills/query/SKILL.md").unlink()

    def missing_tool(path):
        (path / ".ai/tools/check_requirements.py").unlink()

    def bad_event(path):
        hooks = json.loads((path / ".codex/hooks.json").read_text())
        hooks["hooks"]["OnStop"] = hooks["hooks"].pop("Stop")
        (path / ".codex/hooks.json").write_text(json.dumps(hooks))

    def bad_json(path):
        (path / ".codex/hooks.json").write_text("{\"hooks\": ")

    def missing_hook_script(path):
        (path / ".codex/hooks/goal_flow.py").rename(path / ".codex/hooks/other.py")

    cases = (
        ("unrouted Skill", unrouted, 0, ("WARN SKILL_NOT_ROUTED .ai/skills/extra/SKILL.md",)),
        ("Skill name not matching its folder", renamed, 1, ("ERROR SKILL_FRONTMATTER .ai/skills/query/SKILL.md",)),
        ("Skill without description", undescribed, 1, ("ERROR SKILL_FRONTMATTER .ai/skills/query/SKILL.md",)),
        ("routed Skill missing", missing_route, 1, ("ERROR ROUTE_TARGET_MISSING AGENTS.md .ai/skills/query/SKILL.md",)),
        ("tool named by AGENTS.md and Skills missing", missing_tool, 1,
         ("ERROR ROUTE_TARGET_MISSING AGENTS.md .ai/tools/check_requirements.py",
          "ERROR SKILL_TOOL_MISSING .ai/skills/lint/SKILL.md .ai/tools/check_requirements.py")),
        ("unknown hook event", bad_event, 1, ("ERROR HOOKS_SCHEMA .codex/hooks.json OnStop",)),
        ("invalid hooks JSON", bad_json, 1, ("ERROR HOOKS_SCHEMA .codex/hooks.json",)),
        ("hook command script missing", missing_hook_script, 1, ("ERROR HOOK_SCRIPT_MISSING .codex/hooks.json",)),
    )
    for label, mutate, expected, names in cases:
        with tempfile.TemporaryDirectory(prefix="framework-check-") as temporary:
            copy = Path(temporary) / "project"
            shutil.copytree(root, copy)
            before = snapshot(copy)
            mutate(copy)
            changed = snapshot(copy)
            code, output = check_framework(copy)
            require(code == expected and all(name in output for name in names),
                    f"framework check missed {label} (exit {code}):\n{output}")
            require(snapshot(copy) == changed, f"framework check edited files for {label}")
            require(before != changed, f"framework fixture did not change for {label}")
        print(f"PASS framework check reports {label}")


def evidence(root, *args):
    result = subprocess.run(
        ["python3", str(root / ".ai/tools/evidence.py"), "--root", str(root), *args],
        capture_output=True, text=True, timeout=60, cwd=root,
    )
    return result.returncode, result.stdout + result.stderr


def evidence_checks(root):
    (root / "app").mkdir()
    (root / "app/feature.py").write_text("def value():\n    return 0\n")
    (root / "app/test_feature.py").write_text(
        "import unittest\nfrom feature import value\n\n"
        "class T(unittest.TestCase):\n    def test_value(self):\n        self.assertEqual(value(), 1)\n\n"
        "if __name__ == '__main__':\n    unittest.main()\n"
    )
    task = root / "wiki/workitems/TASK-001.md"
    task.write_text("---\nid: TASK-001\nstatus: in_progress\n---\n# Task\n")
    run = ("run", "--task", "TASK-001", "--inputs", "app", "wiki/workitems/STORY-001.md", "--")
    test = ("python3", "app/test_feature.py")

    code, output = evidence(root, *run[:-1], "--phase", "red", "--", *test)
    require(code == 0 and "RED recorded" in output, f"behavior RED was not recorded:\n{output}")
    (root / "app/feature.py").write_text("def value():\n    return 1\n")
    code, output = evidence(root, *run[:-1], "--phase", "green", "--", *test)
    require(code == 0 and "GREEN recorded" in output, f"GREEN was not recorded:\n{output}")
    code, output = evidence(root, "verify")
    require(code == 0 and "TASK-001 CURRENT" in output and "ACCEPTED" not in output.replace("not ACCEPTED", ""),
            f"current GREEN evidence was not verified:\n{output}")
    records = list((root / "generated/evidence/TASK-001").glob("*.json"))
    require(len(records) == 2 and all("sha256" in record.read_text() for record in records), "evidence records lack input hashes")
    print("PASS evidence records behavior RED, GREEN, command output and input hashes")

    for label, path, change in (
        ("implementation change", "app/feature.py", "def value():\n    return 1  # changed\n"),
        ("requirement change", "wiki/workitems/STORY-001.md", None),
    ):
        target = root / path
        original = target.read_text()
        target.write_text(change if change is not None else original + "\n变更。\n")
        code, output = evidence(root, "verify")
        require(code == 0 and "TASK-001 STALE" in output and path in output, f"{label} left old evidence current:\n{output}")
        task.write_text(task.read_text().replace("status: in_progress", "status: done"))
        code, output = evidence(root, "verify")
        require(code == 1 and "DONE_WITHOUT_CURRENT_GREEN" in output, f"done Task passed with stale evidence after {label}:\n{output}")
        task.write_text(task.read_text().replace("status: done", "status: in_progress"))
        target.write_text(original)
        print(f"PASS {label} makes old GREEN evidence stale; a done Task needs current evidence")

    code, output = evidence(root, *run[:-1], "--phase", "green", "--", "python3", "-c", "import sys; sys.exit(1)")
    require(code == 1 and "GREEN failed" in output, f"failing GREEN was recorded as passing:\n{output}")
    code, output = evidence(root, "verify")
    require("TASK-001 FAIL" in output, f"latest failing GREEN was hidden by an older pass:\n{output}")
    (root / "app/broken_test.py").write_text("import missing_module_for_red\n")
    code, output = evidence(root, "run", "--task", "TASK-002", "--phase", "red", "--inputs", "app", "--", "python3", "app/broken_test.py")
    require(code == 1 and "INVALID_RED" in output, f"import error accepted as behavior RED:\n{output}")
    code, output = evidence(root, "run", "--task", "TASK-003", "--phase", "green", "--inputs", "app", "--", "python3", "-c", "pass")
    require(code == 1 and "GREEN_WITHOUT_RED" in output, f"GREEN without a prior behavior RED passed:\n{output}")
    require(len(list((root / "generated/evidence/TASK-001").glob("*.json"))) == 3, "failed attempt was not preserved")
    code, output = evidence(root, "run", "--task", "TASK-001", "--phase", "green", "--inputs", "app missing-folder", "--", "python3", "-c", "pass")
    require(code == 2 and "INPUT_NOT_FOUND" in output, f"evidence bound to a missing input was recorded:\n{output}")
    require(len(list((root / "generated/evidence/TASK-001").glob("*.json"))) == 3, "missing-input attempt was recorded")
    print("PASS failed GREEN is preserved and reported; import-error RED and GREEN without RED are rejected")


def requirement_contract_checks(root):
    goal = (
        "---\nid: GOAL-001\ntype: goal\ntitle: 采购审批\nstatus: approved\nrevision: 1\n---\n\n"
        "# Goal\n\n## 成功标准\n\n### GSC-01\n\n可观察结果。\n\n### GSC-02\n\n可观察结果。\n"
    )
    goal_path = root / "raw/goals/GOAL-001.md"
    story_path = root / "wiki/workitems/STORY-001.md"
    goal_path.write_text(goal)
    template = (root / "schema/templates/story.md").read_text()
    story_path.write_text(template.replace("STORY-XXX", "STORY-001").replace("GOAL-XXX", "GOAL-001").replace(
        "goal_success_criteria: []", "goal_success_criteria: [GOAL-001#GSC-01]"))
    code, output = check_requirements(root)
    require(code == 0 and "STORY-001 READY" in output, f"filled Story template fails its own contract:\n{output}")
    story_path.write_text(requirement_story())
    (root / "wiki/workitems/STORY-LEGACY.md").write_text("---\nid: STORY-LEGACY\nstatus: refining\n---\n# Legacy\n")
    code, output = check_requirements(root)
    require(code == 0 and "STORY-001 READY" in output, f"valid requirement contract failed:\n{output}")
    require("LEGACY_STORY_NOT_CHECKED" in output and "STORY-LEGACY" in output, f"legacy Story was not reported as unchecked:\n{output}")
    require("GAP GOAL-001#GSC-02" in output, f"uncovered Goal criterion was not shown:\n{output}")
    code, output = check_requirements(root, "--require-goal-coverage")
    require(code == 1 and "GOAL_COVERAGE_GAP" in output, f"required Goal coverage gap passed:\n{output}")
    print("PASS requirement contract accepts a valid six-view Story, reports legacy Stories and Goal coverage gaps")

    no_ui = requirement_contract()
    no_ui["views"]["prototype"] = {"applicable": False, "reason": "后台同步，无界面"}
    del no_ui["links"]["UI-01"]
    story_path.write_text(requirement_story(contract=no_ui, sections=("ARCH-01", "BR-01", "DEV-01", "UJ-01", "TC-P-01", "TC-N-01", "AC-01", "AC-02")))
    code, output = check_requirements(root)
    require(code == 0 and "STORY-001 READY" in output, f"explicit no-UI applicability failed:\n{output}")
    print("PASS explicit not-applicable prototype with a reason does not require invented pages")

    def contract_with(mutate):
        contract = requirement_contract()
        mutate(contract)
        return contract

    def drop_view(contract):
        del contract["views"]["business_logic"]

    def unexplained(contract):
        contract["views"]["prototype"] = {"applicable": False}

    def bad_rule(contract):
        contract["links"]["UI-01"]["rules"] = ["BR-99"]

    def untested(contract):
        contract["links"]["AC-02"]["tests"] = []

    def foreign_goal(contract):
        contract["links"]["AC-01"]["goal"] = ["GOAL-001#GSC-02"]
        contract["links"]["AC-02"]["goal"] = ["GOAL-001#GSC-02"]

    def blocking(contract):
        contract["open_questions"] = [{"id": "Q-01", "blocking": True, "text": "审批阈值待确认"}]

    cases = (
        ("missing view", {"contract": contract_with(drop_view)}, "MISSING_VIEW", "business_logic"),
        ("unexplained applicability", {"contract": contract_with(unexplained)}, "NOT_APPLICABLE_WITHOUT_REASON", "prototype"),
        ("undefined item", {"sections": ("BR-01", "DEV-01", "UI-01", "UJ-01", "TC-P-01", "TC-N-01", "AC-01", "AC-02")}, "UNDEFINED_ITEM", "ARCH-01"),
        ("prototype rule reference", {"contract": contract_with(bad_rule)}, "BROKEN_REFERENCE", "BR-99"),
        ("acceptance without test", {"contract": contract_with(untested)}, "AC_WITHOUT_TEST", "AC-02"),
        ("Story Goal criterion coverage", {"contract": contract_with(foreign_goal)}, "GSC_NOT_COVERED", "GOAL-001#GSC-01"),
        ("unknown dependency", {"depends_on": "[STORY-404]"}, "BROKEN_REFERENCE", "STORY-001.md:8 STORY-404"),
        ("invalid JSON", {"contract": "{"}, "CONTRACT_INVALID_JSON", "STORY-001.md:"),
    )
    for label, options, code_name, subject in cases:
        contract = options.pop("contract", None)
        text = requirement_story(**options, contract=None if isinstance(contract, str) else contract)
        if isinstance(contract, str):
            text = re.sub(r"(```json requirement-contract\n).*?(\n```)", lambda m: m.group(1) + contract + m.group(2), text, flags=re.S)
        story_path.write_text(text)
        code, output = check_requirements(root)
        require(code == 1 and code_name in output and subject in output and "STORY-001 NOT_READY" in output,
                f"bad requirement contract passed: {label}\n{output}")
        print(f"PASS requirement check rejects {label} and names {subject}")

    story_path.write_text(requirement_story(depends_on="[STORY-002]"))
    (root / "wiki/workitems/STORY-002.md").write_text(requirement_story("STORY-002", depends_on="[STORY-001]"))
    code, output = check_requirements(root)
    require(code == 1 and "DEPENDENCY_CYCLE" in output and "STORY-001 -> STORY-002 -> STORY-001" in output,
            f"dependency cycle passed:\n{output}")
    (root / "wiki/workitems/STORY-002.md").unlink()
    print("PASS requirement check rejects Story dependency cycles")

    for label, change, code_name in (
        ("unapproved Goal", lambda: goal_path.write_text(goal.replace("status: approved", "status: draft")), "GOAL_NOT_APPROVED"),
        ("blocking question", lambda: story_path.write_text(requirement_story(contract=contract_with(blocking))), "BLOCKING_QUESTION"),
    ):
        goal_path.write_text(goal)
        story_path.write_text(requirement_story())
        change()
        code, output = check_requirements(root)
        require(code == 0 and code_name in output and "STORY-001 NOT_READY" in output,
                f"{label} did not block readiness of a refining Story:\n{output}")
        text = story_path.read_text().replace("status: refining", "status: ready_for_task_decomposition")
        story_path.write_text(text)
        code, output = check_requirements(root)
        require(code == 1 and "READY_STATUS_WITHOUT_READINESS" in output,
                f"{label} allowed a Story to claim readiness:\n{output}")
        print(f"PASS complete fields cannot be Ready with {label}; claiming readiness fails")
    goal_path.write_text(goal)
    story_path.write_text(requirement_story())


def manifest(root):
    lines = (root / ".ai/framework-version").read_text().splitlines()
    files = lines[lines.index("files:") + 1:]
    return dict(reversed(line.split("  ", 1)) for line in files)


def set_manifest(root, entries):
    path = root / ".ai/framework-version"
    head = path.read_text().partition("files:\n")[0]
    path.write_text(head + "files:\n" + "".join(f"{entries[name]}  {name}\n" for name in sorted(entries)))


def upgrade(root, source, *args):
    result = subprocess.run(
        ["bash", str(source / "initdir.sh"), "--upgrade", *args], cwd=root,
        capture_output=True, text=True, timeout=120,
    )
    require(result.returncode == 0, f"upgrade {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout


def listed(output, status):
    section = output.partition(f"\n{status}: ")[2].partition("\n\n")[0]
    return {line.strip() for line in section.splitlines()[1:] if line.startswith("  ")}


def upgrade_checks(base):
    text = BOOTSTRAP.read_text()
    framework = set(text.partition('FRAMEWORK_FILES="')[2].partition('"')[0].split())
    owned = set(text.partition('PROJECT_FILES="')[2].partition('"')[0].split())
    written = set(re.findall(r'^(?:cat|sed [^\n]*) > "?([^" \n]+)"?', text, re.MULTILINE)) - {"$1"}
    require(written <= framework | owned, f"files missing from upgrade lists: {sorted(written - framework - owned)}")

    source = base / "new bootstrap"
    source.mkdir()
    (source / "initdir.sh").write_text(text)
    (source / "00_AI_WARMUP.md").write_text(WARMUP.read_text())
    project = base / "upgrade project"
    project.mkdir()
    (project / "initdir.sh").write_text(text)
    (project / "00_AI_WARMUP.md").write_text(WARMUP.read_text())
    subprocess.run(["bash", "initdir.sh"], cwd=project, capture_output=True, check=True, timeout=60)
    entries = manifest(project)
    require(framework | {"initdir.sh", "00_AI_WARMUP.md"} <= set(entries), "version file misses framework files")
    require(all(entries[name] == hashlib.sha256((project / name).read_bytes()).hexdigest() for name in entries),
            "version file hashes differ from generated files")
    print("PASS initialization records the sha256 of every framework file it writes")

    fresh = {name: (project / name).read_bytes() for name in framework}
    stale, local, merge, review, new = (
        ".ai/skills/lint/SKILL.md", "schema/policies.yaml", "schema/templates/story.md",
        "AGENTS.md", ".ai/tools/evidence.py",
    )
    (project / stale).write_text("# old lint Skill\n")
    entries[stale] = hashlib.sha256(b"# old lint Skill\n").hexdigest()
    (project / local).write_text((project / local).read_text() + "# local rule\n")
    (project / merge).write_text("# old story template\n# local tweak\n")
    entries[merge] = hashlib.sha256(b"# old story template\n").hexdigest()
    (project / review).write_text("# AGENTS without a baseline\n")
    del entries[review]
    (project / new).unlink()
    set_manifest(project, entries)

    before = snapshot(project)
    output = upgrade(project, source)
    require(snapshot(project) == before, "upgrade analysis changed project files")
    for status, name in (("NEW", new), ("UPDATE", stale), ("LOCAL", local), ("MERGE", merge), ("REVIEW", review)):
        require(name in listed(output, status), f"{name} not reported as {status}:\n{output}")
    require("UPGRADE_ANALYSIS new=1 update=1 merge=1 review=1 local=1" in output, f"unexpected counts:\n{output}")
    print("PASS upgrade analysis classifies new, stale, local, merge and unknown-baseline files without writing")

    upgrade(project, source, "--apply")
    require((project / stale).read_bytes() == fresh[stale], "unedited stale file was not replaced")
    require((project / new).read_bytes() == fresh[new] and os.access(project / new, os.X_OK), "new tool not created executable")
    for name, content in ((local, None), (merge, "# old story template\n# local tweak\n"), (review, "# AGENTS without a baseline\n")):
        require(content is None or (project / name).read_text() == content, f"apply changed edited file {name}")
    require((project / local).read_text().endswith("# local rule\n"), "apply dropped a local edit")
    print("PASS --apply creates new files and replaces only unedited ones; edited files stay untouched")

    output = upgrade(project, source, "--mark-merged", merge)
    require(manifest(project)[merge] == hashlib.sha256(fresh[merge]).hexdigest(), "merged baseline not recorded")
    require(merge in listed(output, "LOCAL") and "merge=0" in output, f"merged file still pending:\n{output}")
    before = snapshot(project)
    subprocess.run(["bash", "initdir.sh"], cwd=project, capture_output=True, check=True, timeout=60)
    require(snapshot(project) == before, "rerun after upgrade changed files")
    print("PASS --mark-merged records the new baseline; a rerun keeps the project unchanged")

    legacy = base / "pre-version project"
    legacy.mkdir()
    subprocess.run(["bash", str(source / "initdir.sh")], cwd=legacy, capture_output=True, check=True, timeout=60)
    (legacy / ".ai/framework-version").unlink()
    (legacy / local).write_text((legacy / local).read_text() + "# local rule\n")
    output = upgrade(legacy, source, "--base", str(source / "initdir.sh"))
    require(local in listed(output, "LOCAL") and " review=0 " in output, f"--base did not provide a baseline:\n{output}")
    print("PASS --base supplies a baseline for projects initialized before the version file")


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
            ("schema/templates/story.md", "```json requirement-contract", "```json", "Story template without requirement contract"),
            ("schema/templates/solution.md", '"status": "proposed"', '"status": "decided"', "AI recommendation pre-marked as decided"),
            ("schema/policies.yaml", "confounded_validation_requires_reuse_evidence: true", "confounded_validation_requires_reuse_evidence: false", "confounded lesson validated without reuse"),
            ("schema/templates/learning.md", "attribution:\n", "", "learning without attribution"),
            (".ai/skills/solution-pack/SKILL.md", "objects to inspect, not", "sources to follow, not", "Research obeying page instructions"),
            (".ai/skills/ingest/SKILL.md", "## Evidence Boundary", "## Notes", "ingest without evidence boundary"),
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
        framework_checks(fresh)

        requirements = base / "requirements"
        requirements.mkdir()
        initialize(requirements)
        requirement_contract_checks(requirements)
        solution_pack_checks(requirements)
        evidence_checks(requirements)

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
        upgrade_checks(base)
    print("PASS bootstrap checks complete; project knowledge and business acceptance are not evaluated")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
