# Sprint scenario records and derived assessment (candidate)

These records are project artifacts consumed by a read-only checker. The original
Engine Journal remains the only execution-control authority. A record is not a
runtime receipt, authenticated human acceptance or release permission.

## Authoritative task packet

The Engine sends `run_id`, `goal_ref`, `story_ref`, `task_ref`, `sample_kind`,
`delegation_id` and `attempt` explicitly. Use these supplied values rather than
inferring them from examples, filenames or environment defaults. `assignment_ids`
lists the existing assignment IDs available for a rework recommendation. The
runtime receives the packet and its `documents` in a read-only context snapshot;
it does not receive the Engine object or access to its Journal.

`dependency_manifest` has this shape (an empty list here is only illustrative):

```json
{
  "schema": "collaboration-dependency-manifest/v1",
  "complete": true,
  "ancestors": [],
  "checked_hashes": {}
}
```

`ancestors` is the transitive dependency list in dependency order. Each entry
contains `delegation_id`, `attempt`, `status` and `result_refs` (artifact reference
to SHA256). For a completed ancestor, these are its current completed attempt's
results. Incomplete ancestors have empty `result_refs`; historical results kept
after a retry are not current inputs. `checked_hashes` is the exact union of the
completed ancestors' result hashes. The Engine rejects conflicting hashes and
file drift, and supplies every referenced artifact in `documents`, including
artifact-only results that were not file changes or direct incoming handoffs.

A dispatched execution packet requires a complete manifest. For `director_verify`,
copy its `dependency_manifest.checked_hashes` as the report's `checked_hashes` after
actually checking those inputs. The scenario contract is included because it is
an output of the required `director_pre` ancestor. Other context documents, such
as project rules and declared sources, are not automatically scenario checked
inputs; do not add every `documents` hash to the report. The manifest describes
inputs, not evidence that any scenario has run or passed.

The adapter's execution packet contains the newly requested positive `attempt`.
A packet with `phase: handoff_review` is a separate review invocation: its attempt
is the target assignment's current attempt (possibly zero), and its manifest may
be incomplete while other branches are pending. It must not be returned as a
`director_verify` execution report. Neither kind of packet asks the model to
invent its runtime instance ID; the checker derives that identity from the Journal.

## Scenario contract — returned by `director_pre`

Use exactly these fields:

```json
{
  "schema": "sprint-scenario-contract/v1",
  "run_id": "RUN-001",
  "task_ref": "wiki/workitems/TASK-001.md",
  "sample_kind": "fixture",
  "scenarios": [
    {"id": "SC-01", "acceptance_ref": "STORY-001#AC-01", "required": true}
  ]
}
```

The example is synthetic and grants no authorization. Use the actual run/task and
sample kind. Scenario IDs and acceptance references must be nonempty and unique;
references belong to the current Story (its identifier before the filename's `_`
suffix, then `#` and a nonempty criterion). `required` is a boolean. At least one
scenario is required. Preserve paths/branches/recovery in accompanying artifacts;
this inventory defines which scenario verdicts the checker must receive.

## Scenario report — returned by `director_verify`

Use exactly these fields:

```json
{
  "schema": "sprint-scenario-review/v1",
  "run_id": "RUN-001",
  "task_ref": "wiki/workitems/TASK-001.md",
  "sample_kind": "fixture",
  "attempt": 1,
  "delegation_id": "director_verify",
  "checked_hashes": {},
  "evidence_hashes": {},
  "scenarios": [
    {
      "id": "SC-01",
      "status": "NOT_RUN",
      "evidence_refs": [],
      "reason": "No actual product environment is available",
      "rework_step": null
    }
  ]
}
```

`attempt` is a positive integer (not a boolean), and `delegation_id` must be
`director_verify`, both available in the actual task packet. The checker derives
the reviewer instance from the current completed attempt and its real start receipt;
the author must not guess a runtime ID which is unavailable inside the task packet.
The returned report must be among that attempt's Engine `result_refs`; the scenario
contract must be among completed `director_pre` results. Both hashes must be current.

`checked_hashes` must exactly cover the current scenario contract and all output
artifacts of the transitive ancestors of `director_verify`. This includes applicable
scenario/product/UI/architecture/test design, implementation, data and verification
handoffs. Use the actual file SHA256 values. The Engine's own freshness/check still
checks its anchors, declared sources, current validation and current handoffs.

`scenarios` contains exactly one result for each contracted scenario, with no missing,
extra or duplicate IDs. `status` is PASS, FAIL or NOT_RUN. PASS/FAIL require at least
one actual evidence reference. `evidence_hashes` exactly covers the union of those
references, and each file must currently match its hash. A verdict report cannot
use itself as its own evidence. `reason` is nonempty, including when a scenario
could not run. `rework_step` is null or an existing assignment ID, allowed only on
FAIL; it is a recommendation for Lead to inspect, never permission to execute retry.

A required FAIL makes the scenario gate FAIL; otherwise a required NOT_RUN keeps it
NOT_RUN. All required scenarios must be PASS for a recorded PASS. Optional failures
remain visible and yield recommendations; they cannot silently disappear from Review.

## Read-only source entry points

`sprint_flow.preview(root, context_ref, registry_ref, policy_ref)` uses the existing
`make_plan` with an already prepared task context. It does not create output files,
Journal events, adapters or approval. The normal V1.5 plan entry performs activation
and Engine creation when the operator explicitly requests that action.

`sprint_flow.assess(engine, contract_ref=None, report_ref=None)` reads `Engine.check`,
`graph`, `metrics` and Journal history. It returns engineering findings, the recorded
scenario verdict/currentness, structural joint-check result, unresolved work and
rework recommendations. Missing required scenario records are NOT_RUN; invalid,
stale, wrong-run/task/attempt/instance/role artifacts are INVALID and fail the joint
check. A required director step completed without a valid report is not a PASS.

No selected director steps means scenario review is NOT_APPLICABLE only when the
current bound context has no scenario obligation such as `ui_flow` or
`business_rule`. With either signal, missing required director steps keep scenario
review NOT_RUN and the joint check false. Supplying scenario records to a run with
no director assignments is invalid. The checker validates the current context
against its anchored hash; context drift cannot remove an obligation. It must not
claim missing capability is not applicable, write `finished`, call retry or alter
Task/Goal acceptance.

Take one consistent Journal snapshot; reject a concurrent sequence/hash change.
`human_acceptance` is always NOT_EVALUATED and `release_authorized` is always false.
For fixture runs, live-host and native acceptance remain NOT_RUN even when every
structural check passes. For actual runtime evidence, keep real-host/business
acceptance NOT_EVALUATED until its separate acceptance process is performed.

CLI: `--root <project> preview --context <ref> --registry <ref> --policy <ref>`;
`--root <project> --run-id <id> check [--contract <ref> --report <ref>]`.
Check returns 0 only for structural joint success, 1 for open/failed/invalid gates,
and 2 for malformed invocation/input. It never executes the proposed next action.
