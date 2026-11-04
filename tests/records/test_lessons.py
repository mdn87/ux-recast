"""S2.4: lessons in two tiers; promotion needs an Outcome from a second project identity."""
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout

from ux_recast import cli
from ux_recast.records import decisions, lessons

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "init.defaultBranch=main"]


def _repo(path, remote, content):
    path.mkdir(parents=True)
    (path / "README.md").write_text(content, encoding="utf-8")
    subprocess.run(GIT + ["init", "-q"], cwd=path, check=True)
    subprocess.run(GIT + ["add", "-A"], cwd=path, check=True)
    subprocess.run(GIT + ["commit", "-q", "-m", "root"], cwd=path, check=True)
    if remote:
        subprocess.run(GIT + ["remote", "add", "origin", remote], cwd=path, check=True)
    return path


def _events(project):
    path = Path(project) / ".ux-recast" / "lessons" / "log.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


@unittest.skipUnless(shutil.which("git"), "needs git")
class Lessons(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home = _repo(base / "home", "git@github.com:owner/home.git", "home\n")
        self.other = _repo(base / "other", "https://github.com/owner/other", "other\n")
        self.shared = base / "shared"
        self.lesson = lessons.create(self.home, "Keep Send in view", "A focused field scrolls; keep Send above it.")

    def tearDown(self):
        self.tmp.cleanup()

    def _recorded_outcome(self, project):
        return decisions.append(project, {"kind": "outcome", "summary": "the lesson held"})["id"]

    def test_identity_is_remote_plus_root_and_ignores_the_path(self):
        ident = lessons.identity(self.home)
        root = subprocess.run(["git", "-C", str(self.home), "rev-list", "--max-parents=0", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(ident, f"github.com/owner/home#{root}")
        copy = Path(self.tmp.name) / "elsewhere" / "home-copy"
        shutil.copytree(self.home, copy)
        self.assertEqual(lessons.identity(copy), ident)
        self.assertNotEqual(lessons.identity(self.other), ident)

    def test_remote_spellings_normalize_to_one_identity(self):
        for url in ("git@github.com:owner/home.git", "https://github.com/owner/home", "https://user@GitHub.com/owner/home.git/",
                    "ssh://git@github.com:22/owner/home.git"):
            self.assertEqual(lessons.normalize_remote(url), "github.com/owner/home", url)

    def test_a_project_without_git_has_no_identity(self):
        with self.assertRaisesRegex(ValueError, "not a git repository"):
            lessons.identity(Path(self.tmp.name))

    def test_promotion_without_a_second_identity_is_refused_and_logged(self):
        lessons.add_support(self.home, self.lesson, self.home, self._recorded_outcome(self.home))
        with self.assertLogs("ux_recast.records", "WARNING") as logs:
            with self.assertRaisesRegex(ValueError, "no supporting outcome from a second project identity"):
                lessons.promote(self.home, self.lesson, self.shared)
        self.assertIn("promotion refused: no supporting outcome from a second project identity", logs.output[0])
        self.assertEqual([e["event"] for e in _events(self.home)], ["promotion_refused"])
        self.assertFalse(self.shared.exists())
        self.assertEqual(lessons.read(self.home, self.lesson)["status"], "candidate")

    def test_a_copy_of_the_same_project_at_a_new_path_does_not_count(self):
        copy = Path(self.tmp.name) / "elsewhere" / "home-copy"
        shutil.copytree(self.home, copy)
        lessons.add_support(self.home, self.lesson, copy, self._recorded_outcome(copy))
        with self.assertRaisesRegex(ValueError, "no supporting outcome from a second project identity"):
            lessons.promote(self.home, self.lesson, self.shared)
        self.assertFalse(self.shared.exists())

    def test_an_outcome_from_a_second_identity_promotes(self):
        lessons.add_support(self.home, self.lesson, self.home, self._recorded_outcome(self.home))
        supported = lessons.add_support(self.home, self.lesson, self.other, self._recorded_outcome(self.other))
        self.assertEqual(len({s["identity"] for s in supported}), 2)
        result = lessons.promote(self.home, self.lesson, self.shared)
        self.assertEqual(result["supported_by"], [lessons.identity(self.other)])
        self.assertFalse(result["by_instruction"])
        shared = (self.shared / f"{self.lesson}.md").read_text(encoding="utf-8")
        self.assertIn('status: "shared"', shared)
        self.assertIn("keep Send above it.", shared)
        self.assertEqual(lessons.read(self.home, self.lesson)["status"], "shared")
        self.assertEqual([e["event"] for e in _events(self.home)], ["promoted"])
        with self.assertRaisesRegex(ValueError, "a shared lesson cannot be promoted"):
            lessons.promote(self.home, self.lesson, self.shared)

    def test_the_explicit_user_instruction_bypass_is_logged(self):
        with self.assertLogs("ux_recast.records", "WARNING") as logs:
            result = lessons.promote(self.home, self.lesson, self.shared, instruction="Matt: share it now")
        self.assertTrue(result["by_instruction"])
        self.assertIn("by explicit user instruction: Matt: share it now", logs.output[0])
        events = _events(self.home)
        self.assertEqual([e["event"] for e in events], ["promotion_by_instruction", "promoted"])
        self.assertEqual(events[0]["instruction"], "Matt: share it now")
        self.assertIn('promoted_by_instruction: "Matt: share it now"', (self.shared / f"{self.lesson}.md").read_text(encoding="utf-8"))

    def test_support_needs_a_recorded_outcome(self):
        decision = decisions.append(self.other, {"kind": "decision", "summary": "a decision is not an outcome"})["id"]
        for outcome in (decision, "000000000000"):
            with self.assertRaisesRegex(ValueError, "no such Outcome"):
                lessons.add_support(self.home, self.lesson, self.other, outcome)
        self.assertEqual(lessons.read(self.home, self.lesson)["supported_by"], [])

    def test_cli_promote_reports_the_refusal(self):
        out = io.StringIO()
        with redirect_stdout(out), self.assertLogs("ux_recast.records", "WARNING"):
            code = cli.main(["lessons", "promote", "--project", str(self.home), "--lesson", self.lesson,
                             "--shared-dir", str(self.shared)])
        self.assertEqual(code, 2)
        self.assertIn("no supporting outcome from a second project identity", json.loads(out.getvalue())["error"])


if __name__ == "__main__":
    unittest.main()
