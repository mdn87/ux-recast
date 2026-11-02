"""S1.4: contracts validate the recorded Lugos corpus and refuse the shapes they must refuse."""
import copy
import json
from pathlib import Path
import unittest

from ux_recast.contracts import KINDS, ContractError, schema, validate

CORPUS = Path(__file__).parent / "corpus" / "lugos-2026-10-24"
LIVE = Path(__file__).parent / "corpus" / "lugos-2026-11-02"
FIXTURE_TASK = Path(__file__).parents[1] / "fixtures" / "contact-request" / "task.json"


def load(name):
    return json.loads((CORPUS / name).read_text(encoding="utf-8"))


class Corpus(unittest.TestCase):
    def test_state(self):
        validate("state", load("state.json"))

    def test_packets(self):
        for name in ("packet-plan.json", "packet-implementation.json"):
            with self.subTest(name=name):
                packet = validate("packet", load(name))
                self.assertEqual(packet["dispatch_status"], "recorded")

    def test_receipts(self):
        plan = validate("receipt", load("receipt-plan.json"))
        self.assertTrue(plan["accepted"])
        self.assertEqual(plan["status"], "completed")
        # The implementation-stage submit hit the visual precondition and was refused: a real recorded outcome.
        implementation = validate("receipt", load("receipt-implementation.json"))
        self.assertFalse(implementation["accepted"])
        self.assertEqual(implementation["status"], "failed_precondition")

    def test_packet_and_receipt_agree_on_task_hash(self):
        for stage in ("plan", "implementation"):
            self.assertEqual(load(f"packet-{stage}.json")["task_sha256"], load(f"receipt-{stage}.json")["task_sha256"])

    def test_fixture_task(self):
        validate("task", json.loads(FIXTURE_TASK.read_text(encoding="utf-8")))

    def test_corpus_has_no_local_paths(self):
        for path in CORPUS.glob("*.json"):
            text = path.read_text(encoding="utf-8")
            for needle in ("Users", "C:\\", "C:/", "AppData"):
                self.assertNotIn(needle, text, path.name)


class LiveBaseline(unittest.TestCase):
    """S0.6 live submits on the legacy scripts: one text-only, one with image input, both accepted."""

    def load(self, name):
        return json.loads((LIVE / name).read_text(encoding="utf-8"))

    def test_text_packet_and_receipt(self):
        packet = validate("packet", self.load("packet-text.json"))
        self.assertEqual(packet["request"]["input_modalities"], ["text"])
        self.assertNotIn("visual_inputs", packet["request"])
        receipt = validate("receipt", self.load("receipt-text.json"))
        self.assertTrue(receipt["accepted"])
        self.assertEqual(receipt["task_sha256"], packet["task_sha256"])

    def test_image_packet_and_receipt(self):
        packet = validate("packet", self.load("packet-image.json"))
        self.assertEqual(packet["request"]["input_modalities"], ["text", "image"])
        self.assertEqual(len(packet["request"]["visual_inputs"]), 2)
        receipt = validate("receipt", self.load("receipt-image.json"))
        self.assertTrue(receipt["accepted"])
        self.assertEqual(receipt["task_sha256"], packet["task_sha256"])

    def test_final_state_has_both_runs_finished(self):
        state = validate("state", self.load("state.json"))
        self.assertEqual(state["mode"], "off")
        self.assertEqual([run["status"] for run in state["runs"]], ["remaining", "remaining"])

    def test_no_local_paths(self):
        for path in LIVE.glob("*.json"):
            self.assertNotIn("Users", path.read_text(encoding="utf-8"), path.name)


class Schemas(unittest.TestCase):
    def test_every_kind_ships_a_schema(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                doc = schema(kind)
                self.assertEqual(doc["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertIn("required", doc)

    def test_unknown_kind(self):
        with self.assertRaises(ContractError):
            schema("nope")
        with self.assertRaises(ContractError):
            validate("nope", {})


class Refusals(unittest.TestCase):
    def assertField(self, kind, data, field):
        with self.assertRaises(ContractError) as caught:
            validate(kind, data)
        self.assertEqual(caught.exception.field, field, str(caught.exception))

    def test_packet_request_must_stay_read_only(self):
        packet = load("packet-plan.json")
        packet["request"]["allowed_paths"] = ["src/"]
        self.assertField("packet", packet, "packet.request.allowed_paths")

    def test_packet_images_travel_together(self):
        packet = load("packet-implementation.json")
        self.assertIn("visual_inputs", packet["request"])
        broken = copy.deepcopy(packet)
        broken["request"]["input_modalities"] = ["text"]
        self.assertField("packet", broken, "packet.request")

    def test_packet_schema_version(self):
        packet = load("packet-plan.json")
        packet["schema_version"] = 2
        self.assertField("packet", packet, "packet.schema_version")

    def test_receipt_accepted_requires_completed(self):
        receipt = load("receipt-plan.json")
        receipt["status"] = "failed"
        self.assertField("receipt", receipt, "receipt.accepted")

    def test_receipt_never_carries_findings(self):
        receipt = load("receipt-plan.json")
        receipt["findings"] = [{"id": "F1"}]
        self.assertField("receipt", receipt, "receipt.findings")

    def test_state_mode(self):
        state = load("state.json")
        state["mode"] = "always"
        self.assertField("state", state, "state.mode")

    def test_task_needs_acceptance(self):
        task = json.loads(FIXTURE_TASK.read_text(encoding="utf-8"))
        task["acceptance"] = []
        self.assertField("task", task, "task.acceptance")

    def test_findings_shape(self):
        good = {"schema": "ux-recast/findings@1", "provider": "local-agent", "task_sha256": "0" * 64,
                "reviewer": "test", "findings": [{
                    "id": "F1", "category": "observed failure", "task_step": "submit", "observed": "x",
                    "evidence": "step 3", "principle": "error prevention", "likely_consequence": "y",
                    "severity": "High", "confidence": "high", "confidence_reason": "seen",
                    "proposed_correction": "z", "verification": "rerun", "kind": "implementation"}]}
        validate("findings", good)
        dup = copy.deepcopy(good)
        dup["findings"].append(dict(good["findings"][0]))
        self.assertField("findings", dup, "findings.findings[1].id")
        bad = copy.deepcopy(good)
        bad["findings"][0]["severity"] = "Blocker"
        self.assertField("findings", bad, "findings.findings[0].severity")
        scored = copy.deepcopy(good)
        scored["findings"][0]["score"] = "pass"
        self.assertField("findings", scored, "findings.findings[0].score")


if __name__ == "__main__":
    unittest.main()
