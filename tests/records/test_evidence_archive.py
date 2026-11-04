"""S2.3: recording a Decision archives the packet, receipt and screenshots it cites."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from ux_recast.records import decisions, evidence_archive

SESSION, RUN = "session-1", "run-0001"
PNG = b"\x89PNG\r\n\x1a\n" + b"pixels"


def _sha(data):
    return hashlib.sha256(data).hexdigest()


class EvidenceArchive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name).resolve() / "project"
        self.project.mkdir()
        work = self.project / ".ux-review" / "work"
        (work / "before").mkdir(parents=True)
        (work / "after").mkdir()
        self.files = {
            work / "evidence.json": b'{"observations": [], "screenshots": []}\n',
            work / "before" / "form.png": PNG + b"before",
            work / "after" / "form.png": PNG + b"after",
        }
        for path, data in self.files.items():
            path.write_bytes(data)
        self.folder = evidence_archive.packet_folder(self.project, SESSION, RUN)
        self.folder.mkdir(parents=True)
        self.packet = {"schema_version": 1, "dispatch_status": "recorded",
                       "sources": {str(path): _sha(data) for path, data in self.files.items()}}
        (self.folder / "packet.json").write_text(json.dumps(self.packet), encoding="utf-8")
        (self.folder / "receipt.json").write_text('{"schema_version": 1, "outcome": "delivered"}', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_recording_a_decision_archives_what_it_cites(self):
        stored = evidence_archive.record(self.project, SESSION, RUN, {"kind": "decision", "summary": "accept"})
        prefix = f".ux-recast/evidence/{RUN}"
        self.assertEqual(stored["run"], RUN)
        self.assertEqual(stored["evidence"], [
            f"{prefix}/manifest.json", f"{prefix}/packet.json", f"{prefix}/receipt.json",
            f"{prefix}/sources/evidence.json", f"{prefix}/sources/form-2.png", f"{prefix}/sources/form.png"])
        self.assertEqual(decisions.read(self.project), [stored])
        manifest = json.loads((self.project / prefix / "manifest.json").read_text(encoding="utf-8"))
        origins = {entry["origin"]: entry["sha256"] for entry in manifest["files"].values() if "origin" in entry}
        self.assertEqual(origins, {path.relative_to(self.project).as_posix(): _sha(data) for path, data in self.files.items()})

    def test_links_resolve_on_a_clean_checkout(self):
        if not shutil.which("git"):
            self.skipTest("needs git")
        (self.project / ".gitignore").write_text(".ux-review/\n", encoding="utf-8")
        stored = evidence_archive.record(self.project, SESSION, RUN, {"kind": "outcome", "summary": "thresholds met"})
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.autocrlf=false"]
        subprocess.run(git + ["init", "-q"], cwd=self.project, check=True)
        subprocess.run(git + ["add", "-A"], cwd=self.project, check=True)
        subprocess.run(git + ["commit", "-q", "-m", "evidence"], cwd=self.project, check=True)
        clone = Path(self.tmp.name) / "clone"
        subprocess.run(git + ["clone", "-q", str(self.project), str(clone)], check=True)
        self.assertFalse((clone / ".ux-review").exists())
        [cloned] = decisions.read(clone)
        manifest = json.loads((clone / stored["evidence"][0]).read_text(encoding="utf-8"))
        for link in cloned["evidence"][1:]:
            relative = link.split(f"{RUN}/", 1)[1]
            self.assertEqual(_sha((clone / link).read_bytes()), manifest["files"][relative]["sha256"], link)

    def test_a_source_changed_since_the_packet_is_refused(self):
        (self.project / ".ux-review" / "work" / "after" / "form.png").write_bytes(PNG + b"edited")
        with self.assertRaisesRegex(ValueError, "changed since the packet was prepared"):
            evidence_archive.record(self.project, SESSION, RUN, {"kind": "decision", "summary": "accept"})
        self.assertEqual(decisions.read(self.project), [])

    def test_a_source_outside_the_project_is_refused(self):
        outside = Path(self.tmp.name) / "outside.png"
        outside.write_bytes(PNG)
        self.packet["sources"][str(outside)] = _sha(PNG)
        (self.folder / "packet.json").write_text(json.dumps(self.packet), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not a file inside the project"):
            evidence_archive.archive(self.project, SESSION, RUN)

    def test_the_archive_is_write_once(self):
        first = evidence_archive.archive(self.project, SESSION, RUN)
        self.assertEqual(evidence_archive.archive(self.project, SESSION, RUN), first)
        (self.folder / "receipt.json").write_text('{"schema_version": 1, "outcome": "unknown"}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "receipt.json: already archived with different content"):
            evidence_archive.archive(self.project, SESSION, RUN)

    def test_cited_after_files_are_archived_at_their_path_and_may_only_be_added(self):
        after = self.project / ".ux-review" / "after-tests.txt"
        after.write_text("Ran 7 tests\nOK\n", encoding="utf-8")
        first = evidence_archive.record(self.project, SESSION, RUN, {"kind": "decision", "summary": "accept"},
                                        cited=[".ux-review/work/after/form.png"])
        self.assertIn(f".ux-recast/evidence/{RUN}/cited/.ux-review/work/after/form.png", first["evidence"])
        second = evidence_archive.record(self.project, SESSION, RUN, {"kind": "outcome", "summary": "held"},
                                         cited=[".ux-review/after-tests.txt"])
        self.assertIn(f".ux-recast/evidence/{RUN}/cited/.ux-review/after-tests.txt", second["evidence"])
        self.assertNotIn(f".ux-recast/evidence/{RUN}/cited/.ux-review/work/after/form.png", second["evidence"])
        manifest = json.loads((self.project / ".ux-recast" / "evidence" / RUN / "manifest.json").read_text(encoding="utf-8"))
        self.assertIn("cited/.ux-review/work/after/form.png", manifest["files"])
        self.assertEqual(manifest["files"]["cited/.ux-review/after-tests.txt"]["sha256"], _sha(after.read_bytes()))
        after.write_text("Ran 7 tests\nFAILED\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "after-tests.txt: already archived with different content"):
            evidence_archive.archive(self.project, SESSION, RUN, [".ux-review/after-tests.txt"])

    def test_cited_files_outside_the_project_or_inside_the_archive_are_refused(self):
        evidence_archive.archive(self.project, SESSION, RUN)
        for name in ("../outside.txt", f".ux-recast/evidence/{RUN}/packet.json"):
            with self.assertRaisesRegex(ValueError, "not a file inside the project and outside the archive"):
                evidence_archive.archive(self.project, SESSION, RUN, [name])

    def test_missing_packet_bad_run_and_assigned_keys_are_refused(self):
        with self.assertRaisesRegex(ValueError, "no packet to archive"):
            evidence_archive.archive(self.project, SESSION, "run-0002")
        with self.assertRaisesRegex(ValueError, "not a run id"):
            evidence_archive.archive(self.project, SESSION, "../escape")
        with self.assertRaisesRegex(ValueError, "^evidence:"):
            evidence_archive.record(self.project, SESSION, RUN, {"kind": "decision", "summary": "x", "evidence": []})
        self.assertFalse((self.project / ".ux-recast" / "evidence").exists())


if __name__ == "__main__":
    unittest.main()
