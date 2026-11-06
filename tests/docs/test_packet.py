"""S6.1: a documentation packet is prepared for a provider and what returns is validated before it is written."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from ux_recast.contracts import ContractError
from ux_recast.docs import guide, packet
from tests.docs import helpers

SRC = Path(__file__).parents[2] / "src"


class Packet(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="uxr-packet-"))
        self.revision = helpers.make_project(self.root)
        self.request = {"schema": "ux-recast/documentation-request@1", "request_kind": "documentation", "project": "demo",
                        "subject": "Card", "basis": "accepted", "basis_reference": "D-1",
                        "outputs": {"guide": True, "sheets": True, "motion": True}, "components": ["card"],
                        "inputs": [{"path": "DESIGN.md", "role": "design"}, {"path": "theme.css", "role": "source"}],
                        "out_dir": "docs/design"}
        (self.root / "request.json").write_text(json.dumps(self.request), encoding="utf-8")
        (self.root / "card.json").write_text(json.dumps(helpers.spec(self.revision)), encoding="utf-8")
        meta = {"subject": "Card", "basis": "accepted", "basis_reference": "D-1", "sources": "DESIGN.md", "sheets": "card"}
        (self.root / "guide.md").write_text(guide.render(meta, {"spacing": "S.", "content-behavior": "Wraps."}), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_prepare_hashes_inputs_and_defers_motion(self):
        result = packet.prepare(self.root, self.root / "request.json")
        data = json.loads((Path(result["folder"]) / "packet.json").read_text(encoding="utf-8"))
        self.assertEqual(data["dispatch_status"], "prepared")
        self.assertEqual([i["revision"] for i in data["inputs"]], [self.revision] * 2)
        self.assertIn("Hit area", data["inputs"][0]["text"])
        self.assertNotIn("text", data["inputs"][1])
        self.assertTrue(data["motion"].startswith("deferred"))
        prompt = (Path(result["folder"]) / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("No motion presentation", prompt)
        self.assertIn("<component>.json", prompt)
        self.assertIn("## Content behavior", prompt)

    def test_record_validates_then_writes(self):
        packet_id = packet.prepare(self.root, self.root / "request.json")["id"]
        result = packet.record(self.root, packet_id, guide_path=self.root / "guide.md", sheet_paths=[self.root / "card.json"])
        self.assertEqual(result["written"], ["docs/design/guide.md", "docs/design/sheets/card.html", "docs/design/sheets/card.json"])
        self.assertEqual(result["guide"]["sections"], ["spacing", "content-behavior"])
        data = json.loads((packet.folder_for(self.root, packet_id) / "packet.json").read_text(encoding="utf-8"))
        self.assertEqual(data["dispatch_status"], "recorded")

    def test_nothing_is_written_when_validation_fails(self):
        packet_id = packet.prepare(self.root, self.root / "request.json")["id"]
        meta = {"subject": "Card", "basis": "accepted", "basis_reference": "D-1", "sources": "DESIGN.md"}
        no_content = self.root / "thin.md"
        no_content.write_text(guide.render(meta, {"spacing": "S."}), encoding="utf-8")
        observed = self.root / "observed.json"
        observed.write_text(json.dumps(helpers.spec(self.revision, basis="observed")), encoding="utf-8")
        for kwargs in ({"guide_path": no_content, "sheet_paths": [self.root / "card.json"]},
                       {"guide_path": self.root / "guide.md", "sheet_paths": [observed]},
                       {"guide_path": self.root / "guide.md", "sheet_paths": []},
                       {"guide_path": None, "sheet_paths": [self.root / "card.json"]}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ContractError):
                packet.record(self.root, packet_id, **kwargs)
        self.assertFalse((self.root / "docs").exists())

    def test_missing_input_is_refused(self):
        self.request["inputs"].append({"path": "absent.md", "role": "decision"})
        (self.root / "request.json").write_text(json.dumps(self.request), encoding="utf-8")
        with self.assertRaises(ValueError):
            packet.prepare(self.root, self.root / "request.json")

    def test_cli_round_trip(self):
        env_python = [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); from ux_recast.cli import main; "
                                            "sys.exit(main(sys.argv[2:]))", str(SRC)]
        prepared = subprocess.run(env_python + ["document", "prepare", "--project", str(self.root), "--request",
                                                str(self.root / "request.json")], capture_output=True, text=True)
        self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
        packet_id = json.loads(prepared.stdout)["id"]
        recorded = subprocess.run(env_python + ["document", "record", "--project", str(self.root), "--id", packet_id,
                                                "--guide", str(self.root / "guide.md"), "--sheet", str(self.root / "card.json")],
                                  capture_output=True, text=True)
        self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)
        checked = subprocess.run(env_python + ["document", "check", "--guide", str(self.root / "docs/design/guide.md"),
                                               "--sheet", str(self.root / "docs/design/sheets/card.html")], capture_output=True, text=True)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        traced = subprocess.run(env_python + ["document", "trace", "--sheet", str(self.root / "docs/design/sheets/card.json"),
                                              "--repo", str(self.root)], capture_output=True, text=True)
        # No page to re-measure on: rendered values stay unmeasured, so the trace does not pass.
        self.assertEqual(traced.returncode, 1, traced.stdout + traced.stderr)
        self.assertEqual(sorted(json.loads(traced.stdout)["unmeasured"]), ["H2", "W", "Y1"])


if __name__ == "__main__":
    unittest.main()
