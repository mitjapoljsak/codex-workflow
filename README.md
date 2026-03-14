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

## Key files

- [docs/codex_autonomous_workflow.md](/home/mitja/work/gdpr/codex-workflow/docs/codex_autonomous_workflow.md)
  Full workflow and rationale.

- [docs/agents_codex_standard.md](/home/mitja/work/gdpr/codex-workflow/docs/agents_codex_standard.md)
  Conservative copy-paste `AGENTS.md` section for normal repos.

- [docs/agents_codex_overnight_standard.md](/home/mitja/work/gdpr/codex-workflow/docs/agents_codex_overnight_standard.md)
  Branch-based autonomous/overnight copy-paste `AGENTS.md` section.

## Intended usage

Use this repo as the source of truth for how you want Codex to work across projects.

Typical pattern:

1. copy the relevant `AGENTS.md` section into another repo
2. add lightweight `docs/architecture/` and `docs/backlog/` structure there
3. use the same prompt patterns and branch policy across projects

## Suggested next step

If you want this to become the canonical shared repo, initialize git here and push it to its own remote.
