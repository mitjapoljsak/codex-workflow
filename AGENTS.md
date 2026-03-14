# AGENTS.md

## Purpose

This repo stores reusable Codex workflow guidance that can be copied into other software projects.

It is documentation-first. The main outputs here are:

- workflow standards
- reusable `AGENTS.md` sections
- planning and execution conventions
- branch-based autonomous delivery guidance
- CLI tooling that helps apply the workflow to other repos

## Scope

Keep this repo focused on reusable cross-project workflow material.

Good additions:

- improved Codex operating models
- better planning/backlog templates
- reusable prompt patterns
- branch and verification policies
- lightweight standards for overnight execution
- CLI-guided repo state management for stages, architecture, and tasks

Avoid mixing in project-specific implementation details from unrelated apps.

## Important files

- [README.md](/home/mitja/work/codex-workflow/README.md)
- [docs/codex_autonomous_workflow.md](/home/mitja/work/codex-workflow/docs/codex_autonomous_workflow.md)
- [docs/agents_codex_standard.md](/home/mitja/work/codex-workflow/docs/agents_codex_standard.md)
- [docs/agents_codex_overnight_standard.md](/home/mitja/work/codex-workflow/docs/agents_codex_overnight_standard.md)
- [codex_workflow/cli.py](/home/mitja/work/codex-workflow/codex_workflow/cli.py)
- [bin/codex-workflow](/home/mitja/work/codex-workflow/bin/codex-workflow)
- [bin/workflow](/home/mitja/work/codex-workflow/bin/workflow)
- [tests/test_cli.py](/home/mitja/work/codex-workflow/tests/test_cli.py)

## Editing rules

- Prefer concise, reusable guidance over project-specific prose.
- Keep examples practical and copy-paste friendly.
- When adding new standards, explain when to use them and when not to use them.
- If a new workflow supersedes an older one, keep the distinction explicit instead of silently mixing them.

## Future structure

As this repo grows, a sensible structure is:

- `docs/workflows/`
- `docs/templates/`
- `docs/prompts/`
- `docs/decisions/`

For now, keep the structure lightweight until there is enough material to justify splitting it further.
