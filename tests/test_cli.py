import argparse
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from codex_workflow import cli


class CodexWorkflowCliTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)

    def test_init_creates_workflow_structure(self) -> None:
        args = argparse.Namespace(path=str(self.root), mode="overnight", force=False)

        result = cli.cmd_init(args)

        self.assertEqual(result, 0)
        self.assertTrue((self.root / "AGENTS.codex.md").exists())
        self.assertTrue((self.root / "docs" / "workflow" / "current_feature.md").exists())
        self.assertTrue((self.root / "docs" / "architecture").exists())
        self.assertTrue((self.root / "docs" / "backlog").exists())
        self.assertTrue((self.root / "docs" / "decisions").exists())

    def test_start_feature_creates_current_feature_and_docs(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))

        result = cli.cmd_start_feature(
            argparse.Namespace(
                path=str(self.root),
                name="HTML Email Support",
                slug="html-email-support",
                goal="Support HTML email bodies.",
                stage="architecture",
                branch="main",
                non_interactive=True,
            )
        )

        self.assertEqual(result, 0)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["name"], "HTML Email Support")
        self.assertEqual(current["slug"], "html-email-support")
        self.assertEqual(current["stage"], "architecture")
        self.assertTrue((self.root / "docs" / "architecture" / "html-email-support.md").exists())
        self.assertTrue((self.root / "docs" / "backlog" / "html-email-support.md").exists())

    def test_create_from_idea_initializes_discovery_packet(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))

        result = cli.cmd_create_from_idea(
            argparse.Namespace(
                path=str(self.root),
                idea="Let admins export monthly billing summaries.",
                name="Billing Export",
                goal="Export monthly billing summaries.",
                constraints="No UI changes in the first version.",
                non_interactive=True,
            )
        )

        self.assertEqual(result, 0)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["name"], "Billing Export")
        self.assertEqual(current["slug"], "billing-export")
        self.assertEqual(current["stage"], "discovery")
        self.assertIn("Raw idea:", current["notes_for_codex"])
        architecture = (
            self.root / "docs" / "architecture" / "billing-export.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Constraints\nNo UI changes in the first version.\n", architecture)

    def test_add_task_updates_backlog_and_active_item(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.cmd_start_feature(
            argparse.Namespace(
                path=str(self.root),
                name="HTML Email Support",
                slug="html-email-support",
                goal="Support HTML email bodies.",
                stage="approved",
                branch="feat/html-email",
                non_interactive=True,
            )
        )

        result = cli.cmd_add_task(
            argparse.Namespace(
                path=str(self.root),
                task_id="B2",
                title="HTML body handling",
                goal="Support html input.",
                scope="send path only",
                non_goals="templates",
                acceptance="html works",
                tests="unit tests",
                non_interactive=True,
            )
        )

        self.assertEqual(result, 0)
        backlog = (self.root / "docs" / "backlog" / "html-email-support.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## B2 - HTML body handling", backlog)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["active_backlog_item"], "B2")

    def test_set_active_task_updates_current_feature(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.cmd_start_feature(
            argparse.Namespace(
                path=str(self.root),
                name="HTML Email Support",
                slug="html-email-support",
                goal="Support HTML email bodies.",
                stage="approved",
                branch="feat/html-email",
                non_interactive=True,
            )
        )
        cli.cmd_add_task(
            argparse.Namespace(
                path=str(self.root),
                task_id="B1",
                title="HTML body handling",
                goal="Support html input.",
                scope="send path only",
                non_goals="templates",
                acceptance="html works",
                tests="unit tests",
                non_interactive=True,
            )
        )
        cli.cmd_add_task(
            argparse.Namespace(
                path=str(self.root),
                task_id="B2",
                title="HTML tests",
                goal="Add tests.",
                scope="tests only",
                non_goals="new UX",
                acceptance="tests cover html path",
                tests="unit tests",
                non_interactive=True,
            )
        )

        result = cli.cmd_set_active_task(
            argparse.Namespace(path=str(self.root), task_id="B1")
        )

        self.assertEqual(result, 0)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["active_backlog_item"], "B1")

    def test_update_architecture_replaces_selected_section(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.cmd_start_feature(
            argparse.Namespace(
                path=str(self.root),
                name="HTML Email Support",
                slug="html-email-support",
                goal="Support HTML email bodies.",
                stage="architecture",
                branch="main",
                non_interactive=True,
            )
        )

        result = cli.cmd_update_architecture(
            argparse.Namespace(
                path=str(self.root),
                section="Recommended approach",
                content="Use multipart emails with text fallback.",
                non_interactive=True,
            )
        )

        self.assertEqual(result, 0)
        architecture = (
            self.root / "docs" / "architecture" / "html-email-support.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Recommended approach\nUse multipart emails with text fallback.\n", architecture)

    def test_refine_architecture_updates_multiple_sections_and_stage(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.cmd_start_feature(
            argparse.Namespace(
                path=str(self.root),
                name="Billing Export",
                slug="billing-export",
                goal="Export monthly billing summaries.",
                stage="discovery",
                branch="main",
                non_interactive=True,
            )
        )

        result = cli.cmd_refine_architecture(
            argparse.Namespace(
                path=str(self.root),
                current_state="Data exists but no export path.",
                constraints="No schema changes.",
                options_considered="CSV export\nBackground job",
                recommended_approach="Start with synchronous CSV export.",
                test_strategy="Serializer unit tests and command tests.",
                open_questions="Should exports be persisted?",
                non_interactive=True,
            )
        )

        self.assertEqual(result, 0)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["stage"], "architecture")
        architecture = (
            self.root / "docs" / "architecture" / "billing-export.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Current state\nData exists but no export path.\n", architecture)
        self.assertIn("## Recommended approach\nStart with synchronous CSV export.\n", architecture)

    def test_next_prompt_uses_execution_stage_and_active_task(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.save_current_feature(
            self.root,
            {
                "name": "Feature",
                "slug": "feature",
                "stage": "execution",
                "goal": "Goal",
                "constraints": "",
                "approved_assumptions": "",
                "current_branch": "feat/feature",
                "active_backlog_item": "B2",
                "notes_for_codex": "",
            },
        )
        (self.root / "docs" / "architecture" / "feature.md").write_text(
            "# Architecture: Feature\n", encoding="utf-8"
        )
        (self.root / "docs" / "backlog" / "feature.md").write_text(
            "# Backlog: Feature\n", encoding="utf-8"
        )

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = cli.cmd_next_prompt(argparse.Namespace(path=str(self.root)))

        self.assertEqual(result, 0)
        output = buffer.getvalue()
        self.assertIn("active approved backlog item `B2` only", output)
        self.assertIn(str(self.root / "docs" / "workflow" / "current_feature.md"), output)

    def test_prepare_overnight_creates_packet_and_updates_feature(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.cmd_start_feature(
            argparse.Namespace(
                path=str(self.root),
                name="Billing Export",
                slug="billing-export",
                goal="Export monthly billing summaries.",
                stage="approved",
                branch="main",
                non_interactive=True,
            )
        )
        cli.cmd_add_task(
            argparse.Namespace(
                path=str(self.root),
                task_id="B2",
                title="Implement export generator",
                goal="Generate CSV export.",
                scope="service and command",
                non_goals="email delivery",
                acceptance="CSV export produced from sample data",
                tests="unit tests",
                non_interactive=True,
            )
        )

        result = cli.cmd_prepare_overnight(
            argparse.Namespace(
                path=str(self.root),
                task_id="B2",
                branch_prefix="overnight",
            )
        )

        self.assertEqual(result, 0)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["stage"], "execution")
        self.assertTrue(current["current_branch"].startswith("overnight/billing-export-"))
        packet = (self.root / "docs" / "workflow" / "overnight_task.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("## Active task\nB2 - Implement export generator", packet)
        self.assertIn("Recommended prompt", packet)

    def test_set_stage_updates_current_feature(self) -> None:
        cli.cmd_init(argparse.Namespace(path=str(self.root), mode="overnight", force=False))
        cli.save_current_feature(
            self.root,
            {
                "name": "Feature",
                "slug": "feature",
                "stage": "discovery",
                "goal": "Goal",
                "constraints": "",
                "approved_assumptions": "",
                "current_branch": "main",
                "active_backlog_item": "none",
                "notes_for_codex": "",
            },
        )

        result = cli.cmd_set_stage(argparse.Namespace(path=str(self.root), stage="execution"))

        self.assertEqual(result, 0)
        current = cli.load_current_feature(self.root)
        self.assertEqual(current["stage"], "execution")

    def test_slugify_normalizes_feature_names(self) -> None:
        self.assertEqual(cli.slugify("HTML Email Support"), "html-email-support")
        self.assertEqual(cli.slugify("  !!! "), "feature")

    def test_parse_args_defaults_to_guide_when_no_command_is_given(self) -> None:
        original_argv = cli.sys.argv
        self.addCleanup(setattr, cli.sys, "argv", original_argv)
        cli.sys.argv = ["cli.py"]

        args = cli.parse_args()

        self.assertEqual(args.command, "guide")
        self.assertEqual(args.path, ".")
        self.assertIs(args.func, cli.cmd_guide)

    def test_main_returns_clean_exit_on_eof(self) -> None:
        args = argparse.Namespace(func=lambda _args: (_ for _ in ()).throw(EOFError()))
        original_parse_args = cli.parse_args
        self.addCleanup(setattr, cli, "parse_args", original_parse_args)
        cli.parse_args = lambda: args

        result = cli.main()

        self.assertEqual(result, 130)


if __name__ == "__main__":
    unittest.main()
