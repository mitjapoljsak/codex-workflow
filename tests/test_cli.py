import argparse
import tempfile
import unittest
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
