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

ARCHITECTURE_SECTIONS = [
    "Goal",
    "Current state",
    "Constraints",
    "Options considered",
    "Recommended approach",
    "Migration / rollout",
    "Test strategy",
    "Open questions",
]

REFINEMENT_SECTIONS = [
    ("Current state", "Current state"),
    ("Constraints", "Constraints"),
    ("Options considered", "Options considered"),
    ("Recommended approach", "Recommended approach"),
    ("Test strategy", "Test strategy"),
    ("Open questions", "Open questions"),
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

    idea_parser = subparsers.add_parser(
        "create-from-idea",
        aliases=["cfi", "idea"],
        help="Create a new feature packet from a raw idea.",
    )
    idea_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    idea_parser.add_argument("--idea", help="Raw feature idea.")
    idea_parser.add_argument("--name", help="Feature display name.")
    idea_parser.add_argument("--goal", help="Feature goal or desired outcome.")
    idea_parser.add_argument("--constraints", help="Known constraints.")
    idea_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing values.",
    )
    idea_parser.set_defaults(func=cmd_create_from_idea)

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

    architecture_parser = subparsers.add_parser(
        "update-architecture",
        aliases=["ua"],
        help="Update one section of the active feature architecture doc.",
    )
    architecture_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    architecture_parser.add_argument(
        "--section",
        choices=ARCHITECTURE_SECTIONS,
        help="Architecture section to replace.",
    )
    architecture_parser.add_argument(
        "--content",
        help="Replacement text for the selected section.",
    )
    architecture_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing values.",
    )
    architecture_parser.set_defaults(func=cmd_update_architecture)

    refine_parser = subparsers.add_parser(
        "refine-architecture",
        aliases=["ra"],
        help="Run a guided architecture-refinement pass for the active feature.",
    )
    refine_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    refine_parser.add_argument("--current-state", dest="current_state")
    refine_parser.add_argument("--constraints")
    refine_parser.add_argument("--options", dest="options_considered")
    refine_parser.add_argument("--recommended", dest="recommended_approach")
    refine_parser.add_argument("--test-strategy", dest="test_strategy")
    refine_parser.add_argument("--open-questions", dest="open_questions")
    refine_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting for missing values.",
    )
    refine_parser.set_defaults(func=cmd_refine_architecture)

    active_task_parser = subparsers.add_parser(
        "set-active-task",
        aliases=["sat"],
        help="Set the active backlog item in the current feature file.",
    )
    active_task_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    active_task_parser.add_argument(
        "--id",
        dest="task_id",
        help="Backlog task ID to activate. Prompts if omitted.",
    )
    active_task_parser.set_defaults(func=cmd_set_active_task)

    status_parser = subparsers.add_parser(
        "status",
        help="Show a concise summary of the current feature state.",
    )
    status_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    status_parser.set_defaults(func=cmd_status)

    next_prompt_parser = subparsers.add_parser(
        "next-prompt",
        aliases=["np"],
        help="Print the recommended next Codex prompt for the current stage.",
    )
    next_prompt_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    next_prompt_parser.set_defaults(func=cmd_next_prompt)

    overnight_parser = subparsers.add_parser(
        "prepare-overnight",
        aliases=["po"],
        help="Prepare an overnight execution packet and branch suggestion.",
    )
    overnight_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target repo path. Defaults to the current directory.",
    )
    overnight_parser.add_argument(
        "--task-id",
        help="Backlog task ID to prepare. Defaults to the active backlog item.",
    )
    overnight_parser.add_argument(
        "--branch-prefix",
        default="overnight",
        help="Branch prefix to use for the suggested branch name.",
    )
    overnight_parser.set_defaults(func=cmd_prepare_overnight)

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


def architecture_path(root: Path, slug: str) -> Path:
    return root / "docs" / "architecture" / f"{slug}.md"


def backlog_path(root: Path, slug: str) -> Path:
    return root / "docs" / "backlog" / f"{slug}.md"


def overnight_packet_path(root: Path) -> Path:
    return root / "docs" / "workflow" / "overnight_task.md"


def parse_backlog_tasks(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    tasks: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()
        if " - " not in heading:
            continue
        task_id, title = heading.split(" - ", 1)
        tasks.append({"id": task_id.strip(), "title": title.strip()})
    return tasks


def task_title_for_id(path: Path, task_id: str) -> str | None:
    for task in parse_backlog_tasks(path):
        if task["id"] == task_id:
            return task["title"]
    return None


def replace_markdown_section(path: Path, section_name: str, content: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing architecture file: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    end = None
    needle = f"## {section_name}"
    for index, line in enumerate(lines):
        if line.strip() == needle:
            start = index
            continue
        if start is not None and line.startswith("## "):
            end = index
            break
    if start is None:
        raise SystemExit(f"Section not found in {path}: {section_name}")
    if end is None:
        end = len(lines)
    replacement = [needle, content.strip(), ""]
    updated = lines[:start] + replacement + lines[end:]
    path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")


def choose_task_id(tasks: list[dict[str, str]]) -> str:
    labels = [f"{task['id']} - {task['title']}" for task in tasks]
    choice = prompt_choice("Select active task:", labels)
    return tasks[labels.index(choice)]["id"]


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

    write_if_allowed(architecture_path(root, slug), architecture_template(name, goal), force=False)
    write_if_allowed(backlog_path(root, slug), backlog_template(name), force=False)
    print(f"Started feature '{name}' ({slug}) in {root}")
    return 0


def cmd_create_from_idea(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    if args.non_interactive:
        if not (args.idea and args.goal):
            raise SystemExit("--idea and --goal are required in --non-interactive mode.")
        idea = args.idea
        name = args.name or idea
        goal = args.goal
        constraints = args.constraints or ""
    else:
        idea = args.idea or prompt_multiline("Raw feature idea")
        name = args.name or prompt_nonempty("Feature name")
        goal = args.goal or prompt_multiline("Desired outcome / goal")
        constraints = args.constraints if args.constraints is not None else prompt_multiline("Known constraints")

    slug = slugify(name)
    cmd_start_feature(
        argparse.Namespace(
            path=str(root),
            name=name,
            slug=slug,
            goal=goal,
            stage="discovery",
            branch="main",
            non_interactive=True,
        )
    )
    replace_markdown_section(
        architecture_path(root, slug),
        "Current state",
        "Current implementation to be analyzed.",
    )
    replace_markdown_section(
        architecture_path(root, slug),
        "Constraints",
        constraints or "No constraints captured yet.",
    )
    replace_markdown_section(
        architecture_path(root, slug),
        "Options considered",
        "\n".join(
            [
                "Option 1:",
                "",
                "Option 2:",
                "",
                "Option 3:",
                "",
            ]
        ).strip(),
    )
    feature = load_current_feature(root)
    feature["notes_for_codex"] = (
        "Use the raw idea and architecture doc as the source of truth. "
        "Planning mode only. Analyze options before implementation.\n\n"
        f"Raw idea:\n{idea}"
    )
    save_current_feature(root, feature)
    print(f"Created feature from idea '{name}' ({slug}) in {root}")
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

    backlog_file = backlog_path(root, slug)
    if not backlog_file.exists():
        raise SystemExit(f"Missing backlog file: {backlog_file}")
    existing = backlog_file.read_text(encoding="utf-8").rstrip()
    updated = existing + "\n\n" + render_task(
        task_id, title, goal, scope, non_goals, acceptance, tests_required
    )
    backlog_file.write_text(updated + "\n", encoding="utf-8")
    feature["active_backlog_item"] = task_id
    save_current_feature(root, feature)
    print(f"Added task {task_id} to {backlog_file.name}")
    return 0


def cmd_update_architecture(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug")
    if not slug:
        raise SystemExit("Current feature slug is empty. Run 'start-feature' first.")
    if args.non_interactive:
        if not (args.section and args.content is not None):
            raise SystemExit("--section and --content are required in --non-interactive mode.")
        section = args.section
        content = args.content
    else:
        section = args.section or prompt_choice(
            "Select architecture section:",
            ARCHITECTURE_SECTIONS,
            default="Recommended approach",
        )
        content = args.content if args.content is not None else prompt_multiline(f"{section} content")
    replace_markdown_section(architecture_path(root, slug), section, content)
    print(f"Updated architecture section '{section}'.")
    return 0


def cmd_refine_architecture(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug")
    if not slug:
        raise SystemExit("Current feature slug is empty. Run 'start-feature' first.")
    if args.non_interactive:
        values = {
            "Current state": args.current_state,
            "Constraints": args.constraints,
            "Options considered": args.options_considered,
            "Recommended approach": args.recommended_approach,
            "Test strategy": args.test_strategy,
            "Open questions": args.open_questions,
        }
        missing = [name for name, value in values.items() if value is None]
        if missing:
            raise SystemExit(
                "Missing required non-interactive fields: " + ", ".join(missing)
            )
    else:
        values = {}
        for field, label in REFINEMENT_SECTIONS:
            values[field] = prompt_multiline(label)

    for field, value in values.items():
        replace_markdown_section(architecture_path(root, slug), field, value)
    feature["stage"] = "architecture"
    save_current_feature(root, feature)
    print(f"Refined architecture for '{feature.get('name', slug)}'.")
    return 0


def cmd_set_active_task(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug")
    if not slug:
        raise SystemExit("Current feature slug is empty. Run 'start-feature' first.")
    tasks = parse_backlog_tasks(backlog_path(root, slug))
    if not tasks:
        raise SystemExit("No backlog tasks found. Add a task first.")
    task_ids = {task["id"] for task in tasks}
    task_id = args.task_id or choose_task_id(tasks)
    if task_id not in task_ids:
        raise SystemExit(f"Task not found in backlog: {task_id}")
    feature["active_backlog_item"] = task_id
    save_current_feature(root, feature)
    print(f"Active task set to {task_id}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug", "")
    print(f"Feature: {feature.get('name') or '(unset)'}")
    print(f"Slug: {slug or '(unset)'}")
    print(f"Stage: {feature.get('stage') or '(unset)'}")
    print(f"Branch: {feature.get('current_branch') or '(unset)'}")
    print(f"Active task: {feature.get('active_backlog_item') or 'none'}")
    if slug:
        print(f"Architecture: {architecture_path(root, slug)}")
        print(f"Backlog: {backlog_path(root, slug)}")
        tasks = parse_backlog_tasks(backlog_path(root, slug))
        if tasks:
            print("Tasks:")
            for task in tasks:
                marker = "*" if task["id"] == feature.get("active_backlog_item") else "-"
                print(f"  {marker} {task['id']}: {task['title']}")
    overnight_file = overnight_packet_path(root)
    if overnight_file.exists():
        print(f"Overnight packet: {overnight_file}")
    return 0


def cmd_next_prompt(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug", "")
    stage = feature.get("stage", "")
    active_task = feature.get("active_backlog_item", "none")
    architecture_file = architecture_path(root, slug) if slug else root / "docs" / "architecture"
    backlog_file = backlog_path(root, slug) if slug else root / "docs" / "backlog"

    if stage in {"discovery", "architecture"}:
        prompt = (
            f"Use {current_feature_path(root)} and {architecture_file} as the source of truth. "
            f"This feature is in {stage} stage. Planning mode only. "
            "Do not change files. Analyze the current implementation, refine architecture options, "
            "and update the architecture plan if needed."
        )
    elif stage == "approved":
        prompt = (
            f"Use {current_feature_path(root)} and {backlog_file} as the source of truth. "
            "Break the approved architecture into implementation-ready backlog items or refine the existing backlog. "
            "Do not implement code yet unless explicitly requested."
        )
    elif stage in {"execution", "verification"}:
        prompt = (
            f"Use {current_feature_path(root)}, {architecture_file}, and {backlog_file} as the source of truth. "
            f"Implement or verify the active approved backlog item `{active_task}` only. "
            "Stay within scope, run relevant verification, and summarize assumptions and remaining risks."
        )
    elif stage == "done":
        prompt = (
            f"Use {current_feature_path(root)} and {backlog_file}. "
            "Review the completed feature for residual risks, documentation gaps, and follow-up tasks."
        )
    else:
        prompt = (
            f"Use {current_feature_path(root)} and the feature docs to identify the blocker, "
            "clarify what is missing, and propose the smallest next step to unblock work."
        )
    print(prompt)
    return 0


def cmd_prepare_overnight(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug", "")
    if not slug:
        raise SystemExit("Current feature slug is empty. Run 'start-feature' first.")
    backlog_file = backlog_path(root, slug)
    tasks = parse_backlog_tasks(backlog_file)
    if not tasks:
        raise SystemExit("No backlog tasks found. Add a task first.")
    task_id = args.task_id or feature.get("active_backlog_item") or "none"
    task_title = task_title_for_id(backlog_file, task_id)
    if task_title is None:
        raise SystemExit(f"Task not found in backlog: {task_id}")
    safe_task = slugify(f"{task_id}-{task_title}")
    branch_name = f"{args.branch_prefix}/{slug}-{safe_task}"
    feature["active_backlog_item"] = task_id
    feature["current_branch"] = branch_name
    feature["stage"] = "execution"
    save_current_feature(root, feature)
    prompt = (
        f"Create or use branch `{branch_name}` and implement backlog item `{task_id} - {task_title}` autonomously there. "
        f"Use {current_feature_path(root)}, {architecture_path(root, slug)}, and {backlog_file} as the source of truth. "
        "Do not stop for minor ambiguity; make reasonable decisions and document them at the end. "
        "Complete the task end-to-end, run relevant tests, and leave the branch ready for review. "
        "Only stop if blocked by missing credentials, required approvals, destructive actions, or a fundamental architectural contradiction."
    )
    packet = "\n".join(
        [
            "# Overnight Task Packet",
            "",
            "## Feature",
            feature.get("name", slug),
            "",
            "## Stage",
            "execution",
            "",
            "## Branch",
            branch_name,
            "",
            "## Active task",
            f"{task_id} - {task_title}",
            "",
            "## Source of truth files",
            str(current_feature_path(root)),
            str(architecture_path(root, slug)),
            str(backlog_file),
            "",
            "## Recommended prompt",
            prompt,
            "",
        ]
    )
    overnight_packet_path(root).write_text(packet + "\n", encoding="utf-8")
    print(f"Prepared overnight packet for {task_id} on branch {branch_name}")
    print(f"Packet: {overnight_packet_path(root)}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    feature = load_current_feature(root)
    slug = feature.get("slug", "")
    print(current_feature_path(root).read_text(encoding="utf-8").rstrip())
    if slug:
        architecture = architecture_path(root, slug)
        backlog = backlog_path(root, slug)
        print("")
        print(f"Architecture: {architecture}")
        print(f"Backlog: {backlog}")
    return 0


def cmd_guide(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve()
    options = [
        "init repo workflow",
        "create feature from idea",
        "start feature",
        "continue current feature",
        "refine architecture",
        "update architecture",
        "set stage",
        "set active task",
        "add task",
        "prepare overnight task",
        "show status",
        "print next prompt",
        "show current feature",
    ]
    choice = prompt_choice("Select action:", options)
    if choice == "init repo workflow":
        return cmd_init(argparse.Namespace(path=str(root), mode="overnight", force=False))
    if choice == "create feature from idea":
        return cmd_create_from_idea(
            argparse.Namespace(
                path=str(root),
                idea=None,
                name=None,
                goal=None,
                constraints=None,
                non_interactive=False,
            )
        )
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
            [
                "show status",
                "refine architecture",
                "update architecture",
                "set stage",
                "set active task",
                "add task",
                "prepare overnight task",
                "print next prompt",
                "show current feature",
            ],
            default="show status",
        )
        if follow_up == "show status":
            return cmd_status(argparse.Namespace(path=str(root)))
        if follow_up == "refine architecture":
            return cmd_refine_architecture(
                argparse.Namespace(
                    path=str(root),
                    current_state=None,
                    constraints=None,
                    options_considered=None,
                    recommended_approach=None,
                    test_strategy=None,
                    open_questions=None,
                    non_interactive=False,
                )
            )
        if follow_up == "update architecture":
            return cmd_update_architecture(
                argparse.Namespace(
                    path=str(root),
                    section=None,
                    content=None,
                    non_interactive=False,
                )
            )
        if follow_up == "set stage":
            stage = prompt_choice("Select stage:", VALID_STAGES, default=feature.get("stage"))
            return cmd_set_stage(argparse.Namespace(path=str(root), stage=stage))
        if follow_up == "set active task":
            return cmd_set_active_task(argparse.Namespace(path=str(root), task_id=None))
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
        if follow_up == "prepare overnight task":
            return cmd_prepare_overnight(
                argparse.Namespace(
                    path=str(root),
                    task_id=None,
                    branch_prefix="overnight",
                )
            )
        if follow_up == "print next prompt":
            return cmd_next_prompt(argparse.Namespace(path=str(root)))
        return cmd_show(argparse.Namespace(path=str(root)))
    if choice == "refine architecture":
        return cmd_refine_architecture(
            argparse.Namespace(
                path=str(root),
                current_state=None,
                constraints=None,
                options_considered=None,
                recommended_approach=None,
                test_strategy=None,
                open_questions=None,
                non_interactive=False,
            )
        )
    if choice == "update architecture":
        return cmd_update_architecture(
            argparse.Namespace(
                path=str(root),
                section=None,
                content=None,
                non_interactive=False,
            )
        )
    if choice == "set stage":
        stage = prompt_choice("Select stage:", VALID_STAGES)
        return cmd_set_stage(argparse.Namespace(path=str(root), stage=stage))
    if choice == "set active task":
        return cmd_set_active_task(argparse.Namespace(path=str(root), task_id=None))
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
    if choice == "prepare overnight task":
        return cmd_prepare_overnight(
            argparse.Namespace(
                path=str(root),
                task_id=None,
                branch_prefix="overnight",
            )
        )
    if choice == "show status":
        return cmd_status(argparse.Namespace(path=str(root)))
    if choice == "print next prompt":
        return cmd_next_prompt(argparse.Namespace(path=str(root)))
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
