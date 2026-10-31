"""Local regression tests without a network or upstream AI dependency."""
from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "slopmonster_advisory.py"
spec = importlib.util.spec_from_file_location("slopmonster_advisory", MODULE)
assert spec and spec.loader
advisory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(advisory)


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, text=True,
                          capture_output=True).stdout.strip()


class EditorialAdvisoryTests(unittest.TestCase):
    def test_file_selection_and_exclusions(self):
        for good in ["README.md", "docs/guide.md", "notes/CHANGELOG.md", "index.html", "docs/landing.html"]:
            self.assertTrue(advisory.eligible(good), good)
        for bad in ["../../key.md", "/etc/secrets.md", "build/readme.md", "vendor/lib.md",
                    "node_modules/foo.md", ".github/PR_TEMPLATE.md", "src/main.js",
                    "src/index.html", ""]:
            self.assertFalse(advisory.eligible(bad), bad)

    def test_report_escapes_filename_and_checker_output(self):
        result = advisory.format_summary(
            [("docs/a|b<script>.md", "Review suggested", "<script>alert('x')</script>")],
            0, True,
        )
        self.assertIn("&#124;", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertNotIn("<script>", result)
        self.assertIn("This is advisory", result)

    def test_missing_checker_nonzero_without_mutating_docs(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "README.md").write_text("Preserve this.", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = advisory.main(["--repo", str(repo), "--checker", str(repo / "absent.py")])
            self.assertEqual(code, 2)
            self.assertEqual((repo / "README.md").read_text(), "Preserve this.")

    def test_scan_uses_fake_checker_and_never_fails_on_writing_flags(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "README.md").write_text("This is sloppy.", encoding="utf-8")
            git(repo, "init", "-b", "main")
            git(repo, "add", "README.md")
            checker = repo / "fake_checker.py"
            checker.write_text(
                "import sys\nprint('score 4/5  needs a cleanse' if 'sloppy' in open(sys.argv[1]).read() "
                "else 'score 5/5  CLEAN')\nsys.exit(1 if 'sloppy' in open(sys.argv[1]).read() else 0)\n",
                encoding="utf-8",
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = advisory.main(["--repo", str(repo), "--checker", str(checker)])
            self.assertEqual(code, 0)
            self.assertIn("Review suggested", output.getvalue())
            self.assertEqual((repo / "README.md").read_text(), "This is sloppy.")

    def test_readme_plus_changed_markdown_only_and_full_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.email", "test@example.invalid")
            git(repo, "config", "user.name", "Test")
            (repo / "README.md").write_text("Readme", encoding="utf-8")
            (repo / "docs").mkdir()
            (repo / "docs" / "guide.md").write_text("Guide", encoding="utf-8")
            (repo / "src").mkdir()
            (repo / "src" / "code.py").write_text("x=1", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "initial")
            initial = git(repo, "rev-parse", "HEAD")
            (repo / "docs" / "guide.md").write_text("Changed", encoding="utf-8")
            (repo / "src" / "code.py").write_text("x=2", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "change")
            selected, dropped, bad = advisory.candidates(repo, initial, False)
            self.assertFalse(bad)
            self.assertEqual(selected, ["README.md", "docs/guide.md"])
            self.assertEqual(dropped, 0)
            selected_all, _, bad = advisory.candidates(repo, "", True)
            self.assertFalse(bad)
            self.assertEqual(selected_all, ["README.md", "docs/guide.md"])

    def test_symlink_and_large_docs_skipped(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            outside = repo / "target.txt"
            outside.write_text("Private data", encoding="utf-8")
            (repo / "linked.md").symlink_to(outside)
            (repo / "large.md").write_text("x" * (advisory.MAX_FILE_BYTES + 1), encoding="utf-8")
            rows, skipped = advisory.scan(repo, repo / "missing.py", ["linked.md", "large.md"])
            self.assertEqual(rows, [])
            self.assertEqual(skipped, 2)

    def test_unavailable_git_base_falls_back_to_tracked_prose(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.email", "test@example.invalid")
            git(repo, "config", "user.name", "Test")
            (repo / "README.md").write_text("README", encoding="utf-8")
            (repo / "docs").mkdir()
            (repo / "docs" / "intro.md").write_text("Intro", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "initial")
            selected, skipped, bad = advisory.candidates(repo, "f" * 40, False)
            self.assertFalse(bad)
            self.assertEqual(selected, ["README.md", "docs/intro.md"])
            self.assertEqual(skipped, 0)

    def test_missing_base_falls_back_to_full_bounded_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            git(repo, "init", "-b", "main")
            git(repo, "config", "user.email", "test@example.invalid")
            git(repo, "config", "user.name", "Test")
            (repo / "README.md").write_text("README", encoding="utf-8")
            (repo / "GUIDE.md").write_text("GUIDE", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "initial")
            selected, _, bad = advisory.candidates(repo, "", False)
            self.assertFalse(bad)
            self.assertEqual(selected, ["README.md", "GUIDE.md"])

    def test_symlinked_directory_outside_repo_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as target:
            repo = Path(temp)
            elsewhere = Path(target)
            (elsewhere / "external.md").write_text("secret", encoding="utf-8")
            (repo / "docs").symlink_to(elsewhere, target_is_directory=True)
            rows, skipped = advisory.scan(repo, repo / "missing.py", ["docs/external.md"])
            self.assertEqual(rows, [])
            self.assertEqual(skipped, 1)

    def test_hard_failure_distinguished_from_editorial_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "README.md").write_text("README", encoding="utf-8")
            checker = repo / "error_checker.py"
            checker.write_text("import sys;sys.exit(3)", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = advisory.main(["--repo", str(repo), "--checker", str(checker)])
            self.assertEqual(code, 2)

    def test_exit_one_without_score_is_not_editorial_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("Test", encoding="utf-8")
            script = root / "bad.py"
            script.write_text("import sys\nprint('invalid argument')\nsys.exit(1)\n", encoding="utf-8")
            rows, skipped = advisory.scan(root, script, ["README.md"])
            self.assertEqual(skipped, 0)
            self.assertEqual(rows[0][1], "Scorer error")

    def test_exit_zero_without_score_is_not_clear(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("Test", encoding="utf-8")
            script = root / "bad.py"
            script.write_text("pass\n", encoding="utf-8")
            rows, _ = advisory.scan(root, script, ["README.md"])
            self.assertEqual(rows[0][1], "Scorer error")

    def test_empty_visible_prose_is_not_a_writing_finding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text("```python\nx = 2\n```\n", encoding="utf-8")
            script = root / "checker.py"
            script.write_text("import sys\nprint('deslop: no visible copy to score')\nsys.exit(1)\n", encoding="utf-8")
            rows, _ = advisory.scan(root, script, ["README.md"])
            self.assertEqual(rows[0][1], "No visible prose")
            report = advisory.format_summary(rows, 0, True)
            self.assertIn('no visible prose: 1', report)

    def test_partial_coverage_warning(self):
        report = advisory.format_summary([("README.md", "Clear", "score 5/5 CLEAN")], 2, True)
        self.assertIn("Partial coverage", report)

    def test_missing_git_cannot_appear_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / "README.md").write_text("Plain text.", encoding="utf-8")
            checker = repo / "checker.py"
            checker.write_text("import sys;sys.exit(0)", encoding="utf-8")
            result = io.StringIO()
            with contextlib.redirect_stdout(result):
                code = advisory.main(["--repo", str(repo), "--checker", str(checker)])
            self.assertEqual(code, 2)
            self.assertIn("Incomplete scan", result.getvalue())

    def test_no_eligible_prose_cannot_complete_pilot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            git(root, "init", "-b", "main")
            (root / "other.py").write_text("print('Hello')\n", encoding="utf-8")
            git(root, "add", "other.py")
            checker = root / "checker.py"
            checker.write_text("print('score 5/5  CLEAN')\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = advisory.main(["--repo", str(root), "--checker", str(checker)])
            self.assertEqual(code, 2)
            self.assertIn("No verified prose scan", output.getvalue())

    def test_all_empty_prose_cannot_complete_pilot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            git(root, "init", "-b", "main")
            (root / "README.md").write_text("```python\nx = 1\n```\n", encoding="utf-8")
            git(root, "add", "README.md")
            checker = root / "checker.py"
            checker.write_text("import sys\nprint('deslop: no visible copy to score')\nsys.exit(1)\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = advisory.main(["--repo", str(root), "--checker", str(checker)])
            self.assertEqual(code, 2)
            self.assertIn("No verified prose scan", output.getvalue())
            self.assertIn("No visible prose", output.getvalue())

    def test_all_skipped_prose_cannot_complete_pilot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            git(root, "init", "-b", "main")
            (root / "README.md").write_text("x" * (advisory.MAX_FILE_BYTES + 1), encoding="utf-8")
            git(root, "add", "README.md")
            checker = root / "checker.py"
            checker.write_text("print('score 5/5  CLEAN')\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = advisory.main(["--repo", str(root), "--checker", str(checker)])
            self.assertEqual(code, 2)
            self.assertIn("No verified prose scan", output.getvalue())
            self.assertIn("skipped: 1", output.getvalue())

    def test_workflow_contracts_are_advisory(self):
        base = Path(__file__).resolve().parents[1]
        shared = (base / ".github/workflows/slopmonster-advisory.yml").read_text()
        self.assertIn("continue-on-error: true", shared)
        self.assertIn("timeout-minutes: 10", shared)
        self.assertIn("permissions:\n  contents: read", shared)
        self.assertIn("if: ${{ always() && steps.score.outcome == 'skipped' }}", shared)
        self.assertIn("workflow_call:", shared)
        self.assertIn("advisory_sha:", shared)
        self.assertIn("ref: ${{ inputs.advisory_sha || 'main' }}", shared)
        self.assertNotIn("pull_request_target:", shared)

    def test_report_filename_cannot_break_markdown_rows(self):
        report = advisory.format_summary([("docs/multi\nline|name.md", "Clear", "")], 0, True)
        self.assertIn("docs/multi line&#124;name.md", report)
        self.assertEqual(report.count("| Clear |"), 1)


if __name__ == "__main__":
    unittest.main()
