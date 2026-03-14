# Standard AGENTS.md Section For Overnight / Autonomous Codex Work

Use this version when the goal is maximum autonomous progress on isolated branches with morning review.

```md
## Codex Autonomous Overnight Workflow

Default working model:

- For substantial features, refactors, or experiments, work on a new branch, not on `main`.
- Complete the requested task as autonomously as possible within the requested scope.
- Make reasonable implementation decisions without asking for confirmation unless blocked by a hard dependency or destructive risk.
- Prefer finishing the task end-to-end over stopping for minor ambiguity.
- Run relevant tests, checks, and validation before concluding.
- Summarize assumptions, changes, verification results, and remaining risks at the end.

Planning mode:

- If explicitly asked for planning only, analyze the current implementation and propose architecture, tradeoffs, rollout plan, and backlog.
- Do not change files in planning-only requests.

Execution mode:

- When asked to implement, create or use a dedicated feature branch if the work is substantial or risky.
- Implement one coherent feature or task set end-to-end.
- You may make local architectural decisions needed to complete the task, as long as they remain consistent with the request.
- Do not stop for minor product or implementation ambiguity; choose the most reasonable path and document it afterward.
- Update tests and docs when relevant.
- Prefer complete working output over partial progress reports.

Overnight mode:

- Treat overnight work as branch-isolated autonomous execution.
- Do not wait for human intervention unless blocked by:
  - missing credentials or required approvals
  - destructive actions not explicitly authorized
  - external system failures that prevent progress
  - fundamental ambiguity that makes multiple incompatible outcomes equally likely
- If blocked, leave the branch in a clear state and summarize exactly what remains.
- If not blocked, continue until the task is implemented, verified, and committed.

Branch policy:

- Use one branch per substantial feature, refactor, or experiment.
- Suggested names:
  - `feat/<name>`
  - `refactor/<name>`
  - `spike/<name>`
  - `overnight/<name>`

Verification policy:

- Run the most relevant available tests.
- If full verification is not possible, run the best partial verification available and state what was not verified.
- Do not claim completion without reporting verification status.

Safety limits:

- Do not perform destructive repo operations without explicit approval.
- Do not revert unrelated user changes.
- Do not expose or commit secrets.
- Keep changes scoped to the requested task unless a small adjacent fix is required to make the task work.

End-of-run output:

- branch name
- what was implemented
- assumptions made
- tests/checks run
- remaining risks
- recommended next step

Recommended overnight prompt pattern:

`Create a new branch for this task and implement it autonomously there. Do not stop for minor ambiguity; make reasonable decisions and document them at the end. Complete the feature end-to-end, run relevant tests, and leave the branch ready for review. Only stop if blocked by missing credentials, required approvals, destructive actions, or a fundamental architectural contradiction.`

Optional wizard trigger:

- If the user says `workflow`, switch into guided workflow mode.
- Ask one question at a time.
- Offer concrete next-step alternatives instead of open-ended planning prompts.
- Maintain the workflow files for the active feature and task state.
```

## How to use it

This version is appropriate when:

- you want Codex to keep going while you are away or asleep
- you accept review/revert in the morning as the control mechanism
- the branch is disposable if the result is not good enough

This version is not appropriate when:

- the task can cause production-impacting destructive changes
- the task depends on frequent product decisions
- the environment requires repeated manual approvals

## Recommended companion files

To make overnight work reliable, pair this with:

- `docs/architecture/`
- `docs/backlog/`
- `tests/`
- one-command verification such as `make test` or `bin/test`
