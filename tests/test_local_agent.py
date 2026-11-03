"""S1.5: the local-agent provider prepares a real packet, hands the agent a template, and records only valid findings."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from ux_recast.cycle.control import execute
from ux_recast.providers import local_agent, lugos_autowork

FIXTURE = Path(__file__).parents[1] / "fixtures" / "contact-request"
SESSION = "local-agent-test"


def finding(**over):
    base = {"id": "F1", "category": "observed failure", "task_step": "submit", "observed": "fields cleared",
            "evidence": "step rejected", "principle": "preserve work", "likely_consequence": "retyping",
            "severity": "High", "confidence": "high", "confidence_reason": "captured values",
            "proposed_correction": "do not reset", "verification": "resubmit and check values", "kind": "implementation"}
    base.update(over)
    return base


class LocalAgentProvider(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copy2(FIXTURE / "task.json", self.root / "task.json")
        (self.root / "page.html").write_text("<form></form>", encoding="utf-8")
        self.evidence = self.root / "evidence.json"
        self.evidence.write_text(json.dumps({"observations": [{"step": "rejected", "name": "", "email": ""}],
                                             "screenshots": []}), encoding="utf-8")
        execute(self.root, SESSION, ["mode", "once", "--scope", "contact-request"])
        opened = execute(self.root, SESSION, ["checkpoint", "--id", "b1", "--stage", "implementation",
                                              "--affected", "contact-request", "--task", "task.json",
                                              "--input", "page.html", "--origin", "checkpoint"])
        self.assertTrue(opened["invoke"], opened)
        self.run_id = opened["run_id"]

    def folder(self):
        return lugos_autowork.folder_for(self.root, SESSION, self.run_id)

    def test_prepare_writes_packet_and_template_and_claims(self):
        out = local_agent.prepare(self.root, SESSION, self.run_id, self.evidence)
        folder = self.folder()
        packet = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["dispatch_status"], "claimed")
        self.assertEqual(packet["request"]["input_modalities"], ["text"])
        template = json.loads((folder / "findings.template.json").read_text(encoding="utf-8"))
        self.assertEqual(template["schema"], "ux-recast/findings@1")
        self.assertEqual(template["task_sha256"], packet["task_sha256"])
        self.assertEqual(out["packet"]["task_sha256"], packet["task_sha256"])
        self.assertEqual(json.loads((folder / "provider.json").read_text(encoding="utf-8"))["provider"], "local-agent")
        with self.assertRaises(ValueError):  # the claim is single use, as for the Autowork provider
            local_agent.prepare(self.root, SESSION, self.run_id, self.evidence)

    def _findings(self, **over):
        packet = json.loads((self.folder() / "packet.json").read_text(encoding="utf-8"))
        doc = {"schema": "ux-recast/findings@1", "provider": "local-agent", "task_sha256": packet["task_sha256"],
               "reviewer": "test", "findings": [finding()], "remaining_uncertainty": "none"}
        doc.update(over)
        path = self.root / "findings.json"
        path.write_text(json.dumps(doc), encoding="utf-8")
        return path

    def test_record_accepts_a_filled_template(self):
        local_agent.prepare(self.root, SESSION, self.run_id, self.evidence)
        receipt = local_agent.record(self.root, SESSION, self.run_id, self._findings())
        self.assertTrue(receipt["accepted"])
        self.assertEqual(receipt["findings_count"], 1)
        self.assertEqual(receipt["selected_route"], "local-agent")
        folder = self.folder()
        self.assertEqual(json.loads((folder / "packet.json").read_text(encoding="utf-8"))["dispatch_status"], "recorded")
        self.assertTrue((folder / "findings.json").exists())
        result = json.loads((folder / "local-result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["status"], "completed")
        self.assertEqual(json.loads(result["answer"])["findings"][0]["id"], "F1")
        consumed = lugos_autowork.consume(self.root, SESSION, self.run_id)
        self.assertEqual(consumed["findings"], "current")

    def test_record_refuses_malformed_findings_and_leaves_the_claim(self):
        local_agent.prepare(self.root, SESSION, self.run_id, self.evidence)
        bad = self._findings(findings=[finding(severity="Blocker")])
        with self.assertRaises(ValueError) as caught:
            local_agent.record(self.root, SESSION, self.run_id, bad)
        self.assertIn("severity", str(caught.exception))
        self.assertEqual(json.loads((self.folder() / "packet.json").read_text(encoding="utf-8"))["dispatch_status"], "claimed")
        self.assertFalse((self.folder() / "receipt.json").exists())

    def test_record_refuses_a_hash_that_is_not_the_claimed_packet(self):
        local_agent.prepare(self.root, SESSION, self.run_id, self.evidence)
        with self.assertRaises(ValueError) as caught:
            local_agent.record(self.root, SESSION, self.run_id, self._findings(task_sha256="0" * 64))
        self.assertIn("task_sha256", str(caught.exception))

    def test_cli_review_and_findings(self):
        base = [sys.executable, "-m", "ux_recast.cli"]
        common = ["--project", str(self.root), "--session", SESSION, "--run", self.run_id]
        proc = subprocess.run([*base, "review", *common, "--evidence", str(self.evidence), "--provider", "local"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertTrue(Path(out["findings_template"]).exists())
        proc = subprocess.run([*base, "findings", *common, "--file", str(self._findings())],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(json.loads(proc.stdout)["accepted"])
        proc = subprocess.run([*base, "findings", *common, "--file", str(self._findings())],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 2, "a second record against a recorded dispatch must be refused")

    def test_cli_walkthrough_mode_and_prompt_hand_off(self):
        base = [sys.executable, "-m", "ux_recast.cli"]
        common = ["--project", str(self.root), "--session", SESSION, "--run", self.run_id]
        proc = subprocess.run([*base, "review", *common, "--evidence", str(self.evidence), "--mode", "walkthrough"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["review_mode"], "walkthrough")
        self.assertIn("packet prompt", out["hand_off"])
        self.assertEqual(json.loads((self.folder() / "provider.json").read_text(encoding="utf-8"))["mode"], "walkthrough")
        proc = subprocess.run([*base, "packet", *common, "prompt"], capture_output=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        packet = json.loads((self.folder() / "packet.json").read_text(encoding="utf-8"))
        self.assertEqual(proc.stdout.decode("utf-8"), packet["request"]["task"])
        self.assertTrue(proc.stdout.decode("utf-8").startswith("# Fresh-evaluator walkthrough assignment"))
        target = self.root / "handoff.txt"
        proc = subprocess.run([*base, "packet", *common, "prompt", "--out", str(target)],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(target.read_bytes().decode("utf-8"), packet["request"]["task"])
        self.assertEqual(json.loads(proc.stdout)["task_chars"], len(packet["request"]["task"]))
        proc = subprocess.run([*base, "findings", *common, "--file", str(self._findings(reviewer="fresh subagent"))],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(json.loads(proc.stdout)["accepted"])


if __name__ == "__main__":
    unittest.main()
