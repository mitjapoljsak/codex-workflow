# Codex Autonomous Delivery Workflow

This document describes a practical way to use Codex across software projects for:

- architecture-first planning
- backlog-driven implementation
- branch-isolated execution
- low-supervision delivery
- safer overnight work

The goal is to let Codex work as autonomously as possible without losing control of architecture, quality, or repo hygiene.

## Core idea

Separate product work into two clearly different modes:

1. `Planning mode`
   Codex analyzes, designs, compares options, and writes plans.
   No code changes.

2. `Execution mode`
   Codex implements one approved task at a time against a defined spec.

This matters because most bad autonomous changes come from mixing architecture decisions with implementation in the same step.

## Recommended operating model

### Phase 1: Discovery

Use Codex to understand the current system before proposing changes.

Expected outputs:

- current architecture summary
- impacted modules
- constraints
- unknowns
- risks
- integration points

Typical instruction:

```text
Analyze the current implementation for feature X. Do not change files. Identify the current architecture, touched modules, risks, and likely implementation approaches.
```

### Phase 2: Architecture

Once the current state is clear, have Codex propose 1-3 implementation options.

Expected outputs:

- option comparison
- recommended architecture
- data model changes
- API changes
- migration strategy
- rollout strategy
- test strategy

Typical instruction:

```text
Do not change files yet. Propose a concrete architecture for feature X. Include tradeoffs, migration plan, and testing strategy. Recommend one option.
```

### Phase 3: Backlog breakdown

Turn the architecture into execution-sized tasks.

Each task should be:

- independently testable
- small enough for one implementation session
- clear on input/output
- clear on touched files
- clear on dependencies

Good backlog item fields:

- `id`
- `title`
- `goal`
- `scope`
- `non_goals`
- `dependencies`
- `files_or_modules`
- `acceptance_criteria`
- `tests_required`
- `risk_level`

Typical instruction:

```text
Break the approved architecture into implementation tasks. Keep them small, ordered, and independently verifiable.
```

### Phase 4: Execution

Once the backlog exists, execute task-by-task.

Best practice:

- one task per prompt
- one coherent change per branch
- require verification before moving on

Typical instruction:

```text
Implement backlog item A3 only. Do not touch other backlog items. Run the relevant tests and summarize the result.
```

### Phase 5: Review and merge

After implementation:

- run tests
- review diffs
- check architecture drift
- merge only after acceptance criteria are met

Typical instruction:

```text
Review this branch against backlog item A3. Focus on behavioral regressions, missing tests, and scope creep.
```

## Branch strategy

Use branches when:

- features are independent
- work is risky
- changes affect architecture
- multiple implementation streams are planned

Suggested naming:

- `feat/<short-name>`
- `refactor/<short-name>`
- `fix/<short-name>`
- `spike/<short-name>`

Examples:

- `feat/html-email`
- `feat/timelog-export`
- `refactor/gmail-service-layer`
- `spike/message-threading`

Use a branch per feature if the feature is substantial.
Use one branch for multiple tasks only when they are tightly coupled.

## Task packet format

Codex works best when each execution task is defined as a packet.

Example:

```text
Task: A3 - Add HTML email support
Goal: Support multipart text/html messages in send flow.
Scope: Sending path only. No inbox rendering.
Non-goals: Rich signature editor, templates, tracking pixels.
Files likely affected: gmail_cli/cli.py, tests/test_cli.py, docs/*
Acceptance criteria:
- send command supports HTML body input
- text fallback still exists
- existing plain-text sending still works
- tests cover both paths
Verification:
- unit tests pass
- no regression in existing send command
```

This reduces ambiguity and makes autonomous work much safer.

## Safe overnight workflow

Overnight work is realistic only if the task is constrained well enough.

Use overnight/autonomous execution only for work that is:

- well scoped
- not architecture-ambiguous
- not waiting on product decisions
- not dependent on secret external systems changing live
- testable locally or in CI

Good overnight tasks:

- isolated features
- refactors with strong tests
- documentation generation
- code cleanup with verification
- branch-local implementation from an approved backlog item

Bad overnight tasks:

- open-ended product design
- unclear migrations
- anything requiring frequent approval
- destructive repo operations
- external-system debugging that depends on manual access

### Overnight execution rules

If you want Codex to work with minimal supervision, define these rules in advance:

- stay within the approved task scope
- do not re-architect outside the task
- stop if blocked by ambiguity
- stop if a command requires destructive action
- stop if a secret, token, or credential is missing
- run tests before concluding
- summarize changes, risks, and blockers at the end

### Overnight stop conditions

Codex should stop and report instead of guessing when:

- acceptance criteria conflict with existing architecture
- migrations are unclear
- unrelated failing tests appear
- credentials or approvals are required
- the task expands beyond the original scope

## Suggested repo structure

For each project, keep lightweight planning artifacts inside the repo:

- `docs/architecture/`
- `docs/backlog/`
- `docs/decisions/`
- `AGENTS.md`

Minimal structure:

- `docs/architecture/current_state.md`
- `docs/architecture/feature_<name>.md`
- `docs/backlog/<feature_name>.md`
- `docs/decisions/<date>_<decision>.md`

This gives Codex durable context without needing to rediscover decisions every time.

## Recommended AGENTS.md policy

Each repo should tell Codex exactly how to behave in planning and execution modes.

Recommended principles:

- architecture work first, code changes second
- no file changes unless explicitly requested
- branch-isolated work for risky features
- always verify before concluding
- stop on ambiguity instead of widening scope silently
- preserve unrelated user changes

## Copy-paste AGENTS.md snippet

Use this in other repos as a starting point:

```md
## Codex Delivery Workflow

Use two distinct modes:

1. Planning mode
   - Analyze the current implementation.
   - Propose architecture and tradeoffs.
   - Break approved designs into backlog items.
   - Do not change files unless explicitly requested.

2. Execution mode
   - Implement one approved backlog item at a time.
   - Stay within the defined scope.
   - Run relevant verification before finishing.
   - Do not silently broaden scope.

For larger features:

- prefer branch-isolated implementation
- keep one coherent feature per branch
- document architecture in `docs/architecture/`
- document backlog in `docs/backlog/`

When working autonomously:

- stop on ambiguity that changes architecture or product behavior
- stop when credentials, approvals, or destructive actions are required
- summarize blockers clearly
- always report verification results
```

Short reusable version:

- [agents_codex_standard.md](/home/mitja/work/codex-workflow/docs/agents_codex_standard.md)
- [agents_codex_overnight_standard.md](/home/mitja/work/codex-workflow/docs/agents_codex_overnight_standard.md)

## Recommended prompt patterns

### Planning prompt

```text
Analyze feature X in the current codebase. Do not change files. Produce:
1. current-state summary
2. recommended architecture
3. implementation options
4. backlog breakdown
5. risks and test strategy
```

### Execution prompt

```text
Implement backlog item B2 only. Stay within scope. Update tests and docs if needed. Run verification and summarize results.
```

### Overnight prompt

```text
Implement backlog items B2 and B3 sequentially on this branch only if B2 completes cleanly. Do not re-architect outside the approved plan. Stop if blocked or if tests fail in unrelated areas. Run verification after each item and summarize what remains.
```

## Practical limits

Be explicit about one important limitation:

Codex is not a substitute for a background job system or CI pipeline.

It can work autonomously within a session, but true unattended overnight delivery is safest when combined with:

- a clear backlog
- a branch strategy
- reproducible local commands
- tests
- optional CI checks

If you want repeatable overnight work, the real architecture is:

- human approves architecture
- Codex executes bounded tasks
- tests/CI validate
- human reviews merge

That is the highest-leverage and lowest-chaos setup.
