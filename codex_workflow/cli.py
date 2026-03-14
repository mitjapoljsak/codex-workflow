#!/usr/bin/env python3
"""Small guided CLI for Codex workflow scaffolding."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VALID_STAGES = [
    "discovery",
    "architecture",
    "approved",
    "execution",
    "verification",
    "done",
    "blocked",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold and guide Codex workflow files in a target repo."
    )
    if len(sys.argv) == 1:
        return argparse.Namespace(command="guide", path=".", func=cmd_guide)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="Initialize Codex workflow files in a target repo."
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    init_parser.add_argument(
        "--mode",
        choices=["standard", "overnight"],
        default="overnight",
        help="Which AGENTS snippet to install by default.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing workflow-managed files.",
    )
    init_parser.set_defaults(func=cmd_init)

    feature_parser = subparsers.add_parser(
        "start-feature", aliases=["sf"], help="Create a new guided feature packet."
    )
    feature_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    feature_parser.add_argument("--name", help="Feature display name.")
    feature_parser.add_argument("--slug", help="Feature slug for filenames.")
    feature_parser.add_argument("--goal", help="Feature goal.")
    feature_parser.add_argument(
        "--stage",
        choices=VALID_STAGES,
        default="discovery",
        help="Initial feature stage.",
    )
    feature_parser.add_argument(
        "--branch", default="main", help="Current branch for the feature."
    )
    feature_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing values.",
    )
    feature_parser.set_defaults(func=cmd_start_feature)

    stage_parser = subparsers.add_parser(
        "set-stage", help="Update the current feature stage."
    )
    stage_parser.add_argument(
        "stage", choices=VALID_STAGES, help="New stage for docs/workflow/current_feature.md."
    )
    stage_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    stage_parser.set_defaults(func=cmd_set_stage)

    task_parser = subparsers.add_parser(
        "add-task", aliases=["at"], help="Append a backlog item to the active feature."
    )
    task_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    task_parser.add_argument("--id", dest="task_id", help="Task ID, for example B2.")
    task_parser.add_argument("--title", help="Task title.")
    task_parser.add_argument("--goal", help="Task goal.")
    task_parser.add_argument("--scope", help="Task scope.")
    task_parser.add_argument("--non-goals", help="Task non-goals.")
    task_parser.add_argument("--acceptance", help="Acceptance criteria summary.")
    task_parser.add_argument("--tests", help="Required tests summary.")
    task_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing values.",
    )
    task_parser.set_defaults(func=cmd_add_task)

    show_parser = subparsers.add_parser(
        "show", help="Print the active workflow files for the current feature."
    )
    show_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    show_parser.set_defaults(func=cmd_show)

    guide_parser = subparsers.add_parser(
        "guide", help="Interactive menu for common workflow actions."
    )
    guide_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    guide_parser.set_defaults(func=cmd_guide)

    return parser.parse_args()


def prompt_nonempty(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("Value is required.")


def prompt_optional(label: str) -> str:
    return input(f"{label}: ").strip()


def prompt_choice(label: str, choices: list[str], default: str | None = None) -> str:
    print(label)
    for index, choice in enumerate(choices, start=1):
        suffix = " (default)" if choice == default else ""
        print(f"  {index}. {choice}{suffix}")
    while True:
        raw = input("> ").strip()
        if not raw and default:
            return default
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(choices):
                return choices[idx - 1]
        if raw in choices:
            return raw
        print("Invalid choice.")


def prompt_multiline(label: str) -> str:
    print(f"{label}. Finish with an empty line:")
    lines = []
    while True:
        line = input()
        if not line and lines:
            return "\n".join(lines).strip()
        if not line:
            print("Value is required.")
            continue
        lines.append(line)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "feature"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_if_allowed(path: Path, content: str, force: bool = False) -> None:
    if path.exists() and not force:
        return
    ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def current_feature_path(root: Path) -> Path:
    return root / "docs" / "workflow" / "current_feature.md"


def load_current_feature(root: Path) -> dict[str, str]:
    path = current_feature_path(root)
    if not path.exists():
        raise SystemExit(f"Missing workflow state file: {path}. Run 'init' first.")
    data: dict[str, str] = {}
    current_key = None
    multiline_lines: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            if current_key is not None:
                data[current_key] = "\n".join(multiline_lines).strip()
            current_key = raw_line[3:].strip().lower().replace(" ", "_")
            multiline_lines = []
            continue
        if current_key is not None:
            multiline_lines.append(raw_line)
    if current_key is not None:
        data[current_key] = "\n".join(multiline_lines).strip()
    return data


def save_current_feature(root: Path, feature: dict[str, str]) -> None:
    path = current_feature_path(root)
    content = "\n".join(
        [
            "# Current Feature",
            "",
            "## Name",
            feature.get("name", ""),
            "",
            "## Slug",
            feature.get("slug", ""),
            "",
            "## Stage",
            feature.get("stage", ""),
            "",
            "## Goal",
            feature.get("goal", ""),
            "",
            "## Constraints",
            feature.get("constraints", ""),
            "",
            "## Approved assumptions",
            feature.get("approved_assumptions", ""),
            "",
            "## Current branch",
            feature.get("current_branch", "main"),
            "",
            "## Active backlog item",
            feature.get("active_backlog_item", "none"),
            "",
            "## Notes for Codex",
            feature.get("notes_for_codex", ""),
            "",
        ]
    )
    write_if_allowed(path, content, force=True)


def standard_agents_snippet(mode: str) -> str:
    source_name = (
        "agents_codex_overnight_standard.md"
        if mode == "overnight"
        else "agents_codex_standard.md"
    )
    return "\n".join(
        [
            "# Codex Workflow Snippet",
            "",
            "Copy one of the standards from the shared codex-workflow repo into this file",
            "or replace this file with your repo-specific AGENTS content.",
            "",
            f"Recommended source: codex-workflow/docs/{source_name}",
            "",
        ]
    )


def architecture_template(feature_name: str, goal: str) -> str:
    return "\n".join(
        [
            f"# Architecture: {feature_name}",
            "",
            "## Goal",
            goal,
            "",
            "## Current state",
            "",
            "## Constraints",
            "",
            "## Options considered",
            "",
            "## Recommended approach",
            "",
            "## Migration / rollout",
            "",
            "## Test strategy",
            "",
            "## Open questions",
            "",
        ]
    )


def backlog_template(feature_name: str) -> str:
    return "\n".join(
        [
            f"# Backlog: {feature_name}",
            "",
            "## Overview",
            "",
            "## Tasks",
            "",
        ]
    )


def render_task(task_id: str, title: str, goal: str, scope: str, non_goals: str, acceptance: str, tests_required: str) -> str:
    return "\n".join(
        [
            f"## {task_id} - {title}",
            "",
            "### Stage",
            "approved",
            "",
            "### Goal",
            goal,
            "",
            "### Scope",
            scope,
            "",
            "### Non-goals",
            non_goals,
            "",
            "### Acceptance criteria",
            acceptance,
            "",
            "### Tests required",
            tests_required,
            "",
        ]
    )


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    docs = root / "docs"
    (docs / "workflow").mkdir(parents=True, exist_ok=True)
    (docs / "architecture").mkdir(parents=True, exist_ok=True)
    (docs / "backlog").mkdir(parents=True, exist_ok=True)
    (docs / "decisions").mkdir(parents=True, exist_ok=True)

    write_if_allowed(root / "AGENTS.codex.md", standard_agents_snippet(args.mode), args.force)
    write_if_allowed(
        current_feature_path(root),
        "\n".join(
            [
                "# Current Feature",
                "",
                "## Name",
                "",
                "## Slug",
                "",
                "## Stage",
                "discovery",
                "",
                "## Goal",
                "",
                "## Constraints",
                "",
                "## Approved assumptions",
                "",
                "## Current branch",
                "main",
                "",
                "## Active backlog item",
                "none",
                "",
                "## Notes for Codex",
                "Planning mode only until a feature is approved.",
                "",
            ]
        ),
        args.force,
    )
    print(f"Initialized Codex workflow files in {root}")
    return 0


def cmd_start_feature(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if args.non_interactive:
        if not (args.name and args.goal):
            raise SystemExit("--name and --goal are required in --non-interactive mode.")
        name = args.name
        goal = args.goal
        slug = args.slug or slugify(name)
        constraints = ""
        assumptions = ""
        notes = ""
    else:
        name = args.name or prompt_nonempty("Feature name")
        goal = args.goal or prompt_multiline("Goal")
        slug = args.slug or slugify(prompt_optional("Slug override") or name)
        constraints = prompt_multiline("Constraints")
        assumptions = prompt_multiline("Approved assumptions")
        notes = prompt_multiline("Notes for Codex")

    save_current_feature(
        root,
        {
            "name": name,
            "slug": slug,
            "stage": args.stage,
            "goal": goal,
            "constraints": constraints,
            "approved_assumptions": assumptions,
            "current_branch": args.branch,
            "active_backlog_item": "none",
            "notes_for_codex": notes or "Planning mode only until approved.",
        },
    )

    write_if_allowed(root / "docs" / "architecture" / f"{slug}.md", architecture_template(name, goal), force=False)
    write_if_allowed(root / "docs" / "backlog" / f"{slug}.md", backlog_template(name), force=False)
    print(f"Started feature '{name}' ({slug}) in {root}")
    return 0


def cmd_set_stage(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    feature["stage"] = args.stage
    save_current_feature(root, feature)
    print(f"Stage set to {args.stage}")
    return 0


def cmd_add_task(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug")
    if not slug:
        raise SystemExit("Current feature slug is empty. Run 'start-feature' first.")

    if args.non_interactive:
        required = [args.task_id, args.title, args.goal, args.scope, args.non_goals, args.acceptance, args.tests]
        if any(value is None for value in required):
            raise SystemExit("All task fields are required in --non-interactive mode.")
        task_id = args.task_id
        title = args.title
        goal = args.goal
        scope = args.scope
        non_goals = args.non_goals
        acceptance = args.acceptance
        tests_required = args.tests
    else:
        task_id = args.task_id or prompt_nonempty("Task ID")
        title = args.title or prompt_nonempty("Task title")
        goal = args.goal or prompt_multiline("Task goal")
        scope = args.scope or prompt_multiline("Task scope")
        non_goals = args.non_goals or prompt_multiline("Task non-goals")
        acceptance = args.acceptance or prompt_multiline("Acceptance criteria")
        tests_required = args.tests or prompt_multiline("Tests required")

    backlog_path = root / "docs" / "backlog" / f"{slug}.md"
    if not backlog_path.exists():
        raise SystemExit(f"Missing backlog file: {backlog_path}")
    existing = backlog_path.read_text(encoding="utf-8").rstrip()
    updated = existing + "\n\n" + render_task(
        task_id, title, goal, scope, non_goals, acceptance, tests_required
    )
    backlog_path.write_text(updated + "\n", encoding="utf-8")
    feature["active_backlog_item"] = task_id
    save_current_feature(root, feature)
    print(f"Added task {task_id} to {backlog_path.name}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug", "")
    print(current_feature_path(root).read_text(encoding="utf-8").rstrip())
    if slug:
        architecture = root / "docs" / "architecture" / f"{slug}.md"
        backlog = root / "docs" / "backlog" / f"{slug}.md"
        print("")
        print(f"Architecture: {architecture}")
        print(f"Backlog: {backlog}")
    return 0


def cmd_guide(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    options = [
        "init repo workflow",
        "start feature",
        "continue current feature",
        "set stage",
        "add task",
        "show current feature",
    ]
    choice = prompt_choice("Select action:", options)
    if choice == "init repo workflow":
        return cmd_init(argparse.Namespace(path=str(root), mode="overnight", force=False))
    if choice == "start feature":
        return cmd_start_feature(
            argparse.Namespace(
                path=str(root),
                name=None,
                slug=None,
                goal=None,
                stage="discovery",
                branch="main",
                non_interactive=False,
            )
        )
    if choice == "continue current feature":
        feature = load_current_feature(root)
        print("")
        print(f"Current feature: {feature.get('name', '(unset)')}")
        print(f"Stage: {feature.get('stage', '(unset)')}")
        follow_up = prompt_choice(
            "What do you want to do next?",
            ["show current feature", "set stage", "add task"],
            default="show current feature",
        )
        if follow_up == "set stage":
            stage = prompt_choice("Select stage:", VALID_STAGES, default=feature.get("stage"))
            return cmd_set_stage(argparse.Namespace(path=str(root), stage=stage))
        if follow_up == "add task":
            return cmd_add_task(
                argparse.Namespace(
                    path=str(root),
                    task_id=None,
                    title=None,
                    goal=None,
                    scope=None,
                    non_goals=None,
                    acceptance=None,
                    tests=None,
                    non_interactive=False,
                )
            )
        return cmd_show(argparse.Namespace(path=str(root)))
    if choice == "set stage":
        stage = prompt_choice("Select stage:", VALID_STAGES)
        return cmd_set_stage(argparse.Namespace(path=str(root), stage=stage))
    if choice == "add task":
        return cmd_add_task(
            argparse.Namespace(
                path=str(root),
                task_id=None,
                title=None,
                goal=None,
                scope=None,
                non_goals=None,
                acceptance=None,
                tests=None,
                non_interactive=False,
            )
        )
    return cmd_show(argparse.Namespace(path=str(root)))


def main() -> int:
    args = parse_args()
    try:
        return args.func(args)
    except (KeyboardInterrupt, EOFError):
        print("Canceled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
