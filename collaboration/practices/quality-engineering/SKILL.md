---
name: quality-engineering
description: Design discriminating behavior tests and independently verify the current ANS implementation, contracts and regressions. Use for test_agent's test_design and quality_verify work, including precise defect handoff and re-verification after changes.
---
# Quality engineering baseline

Read `.ai/skills/professional-baseline/SKILL.md`, `.ai/skills/tdd-director/SKILL.md`, `.ai/skills/review-director/SKILL.md`, approved AC, current design and the project's test/evidence rules. Use existing AC/TC identifiers and evidence storage; do not create a parallel test truth or accept business scope on the user's behalf.

## Design tests that reject wrong behavior

Map the changed behavior and risks to concrete checks at the cheapest reliable boundary: unit, contract, integration, actual database or browser as appropriate. Name the wrong implementation each important test must reject. Include relevant boundaries, invalid input, authorization/tenant isolation, state transitions, retries, failure recovery and compatibility. Avoid tests that merely repeat implementation details or use mocks to assume the behavior under test.

Specify setup/data/environment, command, assertions, expected failure and evidence location. Use actual project tools and commands. If the required environment is missing, separate a test design from a test execution. Do not install unrelated infrastructure or exercise production merely to make a check runnable.

Observe a valid RED before passing the prerequisite to Development where the project requires it. Record the actual failure and confirm it concerns the intended behavior. Setup errors, zero collected cases or unrelated failures are not valid RED. Preserve original evidence and approved test expectations.

## Independently verify the candidate

Check the current code, test and dependency revisions and received artifacts. Re-run the agreed command and relevant regression scope; inspect failures, skips and coverage of changed behavior, not only the summary exit code. Reuse CI evidence only when its tested commit/tree and environment match the candidate. A prior head's green checks do not verify a new change.

For UI behavior, use the project's actual browser and UI contracts. For database concurrency or migrations, use the required dialect and approved isolated environment. Mock/SQLite-only checks cannot establish another database's behavior. For host delegation, require that host's actual lifecycle evidence; runtime_session is not native spawn_agent. Leave unavailable checks NOT_RUN.

During independent verification, do not patch production code or weaken assertions to obtain green. Return a reproducible defect to Lead with scenario/AC, environment/revision, command/steps, expected/actual result, evidence, impact and responsible task. If the test itself is wrong, identify the contradiction and seek the existing contract correction process; do not conceal it.

## Return and recheck

Return the AC-to-case/check mapping, actual results and evidence, unresolved failures/skips/NOT_RUN, affected source/test revisions and required rechecks. Distinguish technical verification from the Director's actual scenario verification and human acceptance. Reject a blanket PASS when a required check failed or did not run.

On rework, read the new attempt and changed dependencies, then rerun the affected checks and mandated regression gate. Keep earlier failures and results versioned. Report only verified outcomes; no efficiency, reliability or production-quality claim without a measured comparison.
