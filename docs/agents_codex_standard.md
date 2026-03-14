# Standard AGENTS.md Section For Codex

Use this as a copy-paste baseline in other repos.

```md
## Codex Delivery Workflow

Use two distinct modes:

1. Planning mode
   - Analyze the current implementation first.
   - Propose architecture, tradeoffs, and rollout strategy.
   - Break approved designs into backlog items.
   - Do not change files unless explicitly requested.

2. Execution mode
   - Implement one approved backlog item at a time.
   - Stay within the defined scope.
   - Update tests and docs when relevant.
   - Run verification before concluding.
   - Do not silently broaden scope.

For larger features:

- prefer branch-isolated implementation
- keep one coherent feature per branch
- document architecture in `docs/architecture/`
- document backlog in `docs/backlog/`
- stop if the task requires re-architecting outside the approved plan

When working autonomously:

- stop on ambiguity that changes architecture, scope, or product behavior
- stop when credentials, approvals, or destructive actions are required
- stop when unrelated failing tests block safe progress
- summarize blockers clearly
- always report verification results

Task packet format:

- `id`
- `title`
- `goal`
- `scope`
- `non_goals`
- `dependencies`
- `acceptance_criteria`
- `tests_required`

Recommended prompt patterns:

- Planning:
  `Analyze feature X. Do not change files. Produce architecture, tradeoffs, backlog, risks, and test strategy.`

- Execution:
  `Implement backlog item B2 only. Stay within scope. Run verification and summarize results.`

- Overnight/autonomous:
  `Implement backlog item B2 only. Do not re-architect outside the approved plan. Stop if blocked or if unrelated failures appear. Run verification and summarize blockers.`
```

## Minimal repo structure

Recommended supporting files:

- `AGENTS.md`
- `docs/architecture/`
- `docs/backlog/`
- `docs/decisions/`

Minimum viable version:

- `docs/architecture/current_state.md`
- `docs/backlog/<feature>.md`

## Intent

This keeps Codex useful across repos without letting implementation drift ahead of architecture.
