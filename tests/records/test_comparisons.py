"""S2.6: v2 comparison records, append-only, with frozen criteria, evidence, limitations, effort and a six-value decision."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from ux_recast import contracts
from ux_recast.records import comparisons

ROOT = Path(__file__).parents[2]
CYCLE_002 = ROOT / "docs" / "evidence" / "fixture-cycle-002"


def record(**changes):
    base = {
        "schema": "ux-recast/comparison@2", "kind": "product", "task": "contact-request",
        "baseline": "index.before.html", "candidate": "index.repaired.html",
        "criteria": {"frozen_at": "checkpoint, task sha256 70fb42a2", "items": ["A rejected email preserves the entered name and request"]},
        "conditions": {"content": "fixture data", "viewports": ["1280x720", "375x812"], "revision_before": "a", "revision_after": "b"},
        "before": {"flow": "submit with a bad email", "evidence": ["before.png"]},
        "after": {"flow": "submit with a bad email", "evidence": ["after.png"]},
        "structural_changes": [], "improvements": [{"claim": "entries kept", "evidence_before": "before.png",
                                                    "evidence_after": "after.png", "kind": "observed"}],
        "findings_disposition": [{"id": "F1", "disposition": "addressed"}],
        "verification": {"checks": [], "failure_paths": []}, "assumptions": [],
        "evidence": ["after-tests.txt"], "limitations": ["same agent reviewed and repaired"],
        "effort": {"review_passes": 1, "retries": 0, "false_findings": 0, "user_interventions": 0, "wall_time_seconds": 80.5},
        "decision": "accept", "decided_by": "fixture driver", "decided_at": "2026-11-04T00:00:00Z",
    }
    base.update(changes)
    return base


class Comparisons(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def assertRefused(self, comparison, field):
        with self.assertRaisesRegex(ValueError, f"^comparison\\.{field}"):
            comparisons.append(self.project, comparison)

    def test_a_valid_record_is_appended_and_read_back(self):
        stored = comparisons.append(self.project, record())
        self.assertEqual(comparisons.read(self.project), [stored])
        self.assertTrue((self.project / ".ux-recast" / "comparisons.jsonl").is_file())
        self.assertFalse((self.project / ".ux-recast" / "decisions.jsonl").exists())

    def test_the_decision_is_one_of_six_or_pending(self):
        self.assertEqual(contracts.COMPARISON_DECISIONS_V2,
                         {"accept", "revise", "keep_local", "reject", "insufficient_evidence", "keep_baseline"})
        for decision in sorted(contracts.COMPARISON_DECISIONS_V2):
            comparisons.append(self.project, record(decision=decision))
        comparisons.append(self.project, record(decision="pending", decided_by="", decided_at=""))
        for decision in ("accepted", "rejected", "maybe"):
            self.assertRefused(record(decision=decision), "decision")

    def test_keeping_the_baseline_may_claim_no_improvement(self):
        comparisons.append(self.project, record(decision="keep_baseline", improvements=[]))
        self.assertRefused(record(decision="accept", improvements=[]), "improvements")

    def test_missing_v2_fields_are_refused(self):
        for field in ("kind", "baseline", "candidate", "criteria", "evidence", "limitations", "effort"):
            broken = record()
            del broken[field]
            self.assertRefused(broken, field)
        self.assertRefused(record(kind="vibes"), "kind")
        self.assertRefused(record(criteria={"frozen_at": "", "items": ["x"]}), "criteria.frozen_at")
        self.assertRefused(record(criteria={"frozen_at": "start", "items": []}), "criteria.items")
        self.assertRefused(record(evidence=[]), "evidence")
        for key, value in (("retries", -1), ("review_passes", 1.5), ("user_interventions", True), ("wall_time_seconds", -2)):
            effort = dict(record()["effort"], **{key: value})
            self.assertRefused(record(effort=effort), f"effort.{key}")
        self.assertRefused(record(score=9), "score")

    def test_only_v2_records_enter_the_log(self):
        with self.assertRaisesRegex(ValueError, "^schema:"):
            comparisons.append(self.project, record(schema="ux-recast/comparison@1"))
        with self.assertRaisesRegex(ValueError, "^id:"):
            comparisons.append(self.project, record(id="mine"))

    def test_v1_records_still_validate(self):
        example = json.loads((ROOT / "templates" / "comparison.example.json").read_text(encoding="utf-8"))
        contracts.validate("comparison", example)
        v1 = copy.deepcopy(example)
        v1["decision"] = "accept"
        with self.assertRaises(contracts.ContractError):
            contracts.validate("comparison", v1)

    def test_effort_comes_from_the_cycle_log(self):
        log = {"phases": ["baseline", "record", "repair", "finish", "lesson"],
               "before": {"seconds": 30.0}, "after": {"seconds": 25.5}, "oracle": {"seconds": 20.0}}
        effort = comparisons.effort_from_cycle(log, [{"id": "F1", "disposition": "addressed"},
                                                     {"id": "F2", "disposition": "rejected"}])
        self.assertEqual({k: effort[k] for k in contracts.EFFORT_FIELDS},
                         {"review_passes": 1, "retries": 0, "false_findings": 1, "user_interventions": 0,
                          "wall_time_seconds": 75.5})
        self.assertIn("not counted", effort["basis"])
        log["phases"] += ["record"]
        self.assertEqual(comparisons.effort_from_cycle(log)["retries"], 1)

    def test_the_fixture_cycle_002_comparison_is_a_valid_product_record(self):
        comparison = json.loads((CYCLE_002 / "comparison.json").read_text(encoding="utf-8"))
        contracts.validate("comparison", comparison)
        self.assertEqual((comparison["schema"], comparison["kind"]), ("ux-recast/comparison@2", "product"))
        self.assertIn(comparison["decision"], contracts.COMPARISON_DECISIONS_V2)
        self.assertTrue(comparison["criteria"]["items"] and comparison["limitations"])
        cycle = json.loads((CYCLE_002 / "cycle.json").read_text(encoding="utf-8"))
        expected = comparisons.effort_from_cycle(cycle, comparison["findings_disposition"])
        self.assertEqual(comparison["effort"], expected)
        self.assertEqual(comparison["criteria"]["items"], cycle["final_state"]["runs"][-1]["task"]["acceptance"])
        for ref in comparison["evidence"]:
            self.assertTrue((CYCLE_002 / ref.split("#", 1)[0]).is_file(), ref)


if __name__ == "__main__":
    unittest.main()
