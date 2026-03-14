# codex-workflow

A reusable playbook for Codex-driven software delivery: planning, architecture, backlog design, branch-based autonomous implementation, verification, and future workflow standards across projects.

## What this repo is for

This repo is meant to hold reusable Codex workflow guidance that can be applied across different software projects.

Current scope:

- architecture-first planning workflow
- backlog breakdown conventions
- branch-based autonomous implementation model
- overnight execution rules
- reusable `AGENTS.md` snippets
- a guided CLI for scaffolding workflow files in other repos

## Key files

- [docs/codex_autonomous_workflow.md](/home/mitja/work/codex-workflow/docs/codex_autonomous_workflow.md)
  Full workflow and rationale.

- [docs/agents_codex_standard.md](/home/mitja/work/codex-workflow/docs/agents_codex_standard.md)
  Conservative copy-paste `AGENTS.md` section for normal repos.

- [docs/agents_codex_overnight_standard.md](/home/mitja/work/codex-workflow/docs/agents_codex_overnight_standard.md)
  Branch-based autonomous/overnight copy-paste `AGENTS.md` section.

- [codex_workflow/cli.py](/home/mitja/work/codex-workflow/codex_workflow/cli.py)
  Guided CLI for creating workflow files and active feature packets.

## Intended usage

Use this repo as the source of truth for how you want Codex to work across projects.

Typical pattern:

1. copy the relevant `AGENTS.md` section into another repo
2. add lightweight `docs/architecture/` and `docs/backlog/` structure there
3. use the same prompt patterns and branch policy across projects

Or use the CLI to scaffold and guide the process:

```bash
bin/workflow
bin/workflow /path/to/repo
bin/codex-workflow
bin/codex-workflow init /path/to/repo
bin/codex-workflow start-feature /path/to/repo --name "Feature name" --goal "Goal"
bin/codex-workflow add-task /path/to/repo --id B1 --title "Task title" --goal "Goal" --scope "Scope" --non-goals "Out of scope" --acceptance "Acceptance" --tests "Tests"
bin/codex-workflow guide /path/to/repo
```

`workflow` is the short guided entrypoint. It opens the menu directly and is intended to feel like the "magic word" for workflow management.

## Suggested next step

If you want this to become the canonical shared repo, initialize git here and push it to its own remote.
