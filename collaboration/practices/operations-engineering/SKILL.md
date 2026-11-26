---
name: operations-engineering
description: Evaluate operational readiness, observability and recovery using current environment and delivery evidence; use for ops_agent assignments with evidenced runtime, configuration or release impact.
---
# Operations engineering baseline

Read `.ai/skills/professional-baseline/SKILL.md` first. Activate methods only for
the assigned operational impact. Bind current task/authorization, architecture,
runtime/environment conventions, deployment configuration and runbooks to actual
sources and versions. Report inaccessible environments and absent evidence.
Reuse `.ai/skills/delivery-loop/SKILL.md` and existing operations gates; do not
introduce another release authority, scheduler or mandatory platform.

## Establish current operational facts

Identify the affected service/process, environment, artifact revision, dependency
versions, configuration changes and ownership. Inspect the actual CI run and
required jobs for that revision; pending, skipped or unavailable checks are not
success. Bind any release artifact to its actual build/digest when available.
Keep source verification, environment verification and deployment state separate.

Inspect configuration references without exposing credentials or secret values.
Use project standards for health checks, resource limits, startup/shutdown,
timeouts, retries and compatibility. Flag relevant differences between the
verified environment and the intended target; do not infer production parity.

## Define readiness and recovery

1. Describe the concrete change and its operational failure modes: startup
   failure, incompatible configuration/data, dependency failure, unavailable
   capacity or degraded behavior, as applicable to the inspected system.
2. Define preconditions, ordered rollout steps, responsible owner and bounded
   validation. Use existing delivery mechanisms. Keep the plan reviewable when
   execution is outside current authorization.
3. Specify observation and stop conditions with project-approved thresholds.
   Distinguish an actual alert, a proposed alert and a missing measurement. Use
   observable behavior; do not invent availability/performance commitments.
4. Specify rollback or forward recovery, artifact/configuration compatibility,
   and data reconciliation where relevant. Expose irreversible effects and
   verify prerequisites in an authorized isolated environment when possible.
5. Map failure to the responsible task and exact recovery/recheck condition.
   Preserve failed attempts and evidence; do not erase an incident by replacing
   its report with a later green run.

## Reuse observability without overstating coverage

Use the project's installed V1.3 observation tools and `docs/harness-observability.md`
when present; inspect their actual version, configuration and available events.
Do not enable collectors, change hooks or export data without matching scope.
Reuse existing run/trace references instead of creating a second event ledger.
Configured collection is not proof of observed activity. Keep missing usage,
incomplete traces and unavailable model costs unknown rather than filling zero.

Report app-server `runtime_session`, CLI role execution and native `spawn_agent`
evidence according to their actual source. Hook/profile presence does not prove
native delegation. Fixture records and another host's run never verify this host.
Keep sensitive payloads out of shared reports and follow existing retention rules.

## Verify and return the readiness review

Run only authorized checks. Record command, environment, artifact/source version,
exit status, observation and evidence reference. An unexecuted smoke/recovery
procedure is a plan; mark its result NOT_RUN with the missing access or prerequisite.
Recheck readiness after a relevant artifact, configuration or environment change.

Return applicability, verified facts, CI/artifact references, rollout/recovery
plan, monitoring/owner/stop conditions, executed checks and remaining blockers.
Report readiness, deployment, operational verification and business acceptance
separately. Existing authorization continues within scope; production database
changes, deployment, rollback, permission expansion and main merge require their
own matching authorization. A readiness opinion grants none of those permissions.
