"""S4.1: the five-finding cap ranks by severity then input order and defers the overflow."""
import copy
import unittest

from ux_recast.cycle import budget


def finding(fid, severity, **over):
    return {"id": fid, "severity": severity, **over}


SEVEN = [finding("F1", "Low"), finding("F2", "High"), finding("F3", "Critical"), finding("F4", "Medium"),
         finding("F5", "High"), finding("F6", "Low"), finding("F7", "Critical")]


class FindingCap(unittest.TestCase):
    def test_seven_findings_record_five_actionable_and_two_deferred(self):
        recorded = budget.apply_finding_cap(SEVEN, 5)
        self.assertEqual([f["id"] for f in recorded], ["F3", "F7", "F2", "F5", "F4", "F1", "F6"])
        self.assertEqual([f["status"] for f in recorded], ["actionable"] * 5 + ["deferred"] * 2)

    def test_equal_severity_keeps_input_order(self):
        same = [finding(f"F{n}", "High") for n in range(1, 8)]
        recorded = budget.apply_finding_cap(same, 5)
        self.assertEqual([f["id"] for f in recorded], [f"F{n}" for n in range(1, 8)])
        self.assertEqual([f["id"] for f in recorded if f["status"] == "deferred"], ["F6", "F7"])

    def test_the_result_is_deterministic_and_the_input_is_left_alone(self):
        before = copy.deepcopy(SEVEN)
        first = budget.apply_finding_cap(SEVEN, 5)
        second = budget.apply_finding_cap(SEVEN, 5)
        self.assertEqual(first, second)
        self.assertEqual(SEVEN, before)
        self.assertNotIn("status", SEVEN[0])

    def test_at_or_under_the_cap_everything_is_actionable(self):
        recorded = budget.apply_finding_cap(SEVEN[:5], 5)
        self.assertEqual({f["status"] for f in recorded}, {"actionable"})
        self.assertEqual([f["id"] for f in recorded], ["F3", "F2", "F5", "F4", "F1"])
        self.assertEqual(budget.apply_finding_cap([], 5), [])

    def test_a_finding_the_reviewer_deferred_stays_deferred_and_takes_no_slot(self):
        items = [finding("F1", "Critical", status="deferred"), *[finding(f"F{n}", "Low") for n in range(2, 8)]]
        recorded = budget.apply_finding_cap(items, 5)
        by_id = {f["id"]: f["status"] for f in recorded}
        self.assertEqual(by_id["F1"], "deferred")
        self.assertEqual([fid for fid, status in by_id.items() if status == "actionable"],
                         ["F2", "F3", "F4", "F5", "F6"])
        self.assertEqual(by_id["F7"], "deferred")
        self.assertEqual(recorded[0]["id"], "F1", "the list stays in severity order whatever the status")

    def test_a_reviewer_cannot_claim_a_slot_over_the_cap(self):
        items = [finding(f"F{n}", "High") for n in range(1, 7)] + [finding("F7", "High", status="actionable")]
        recorded = budget.apply_finding_cap(items, 5)
        self.assertEqual(recorded[-1]["id"], "F7")
        self.assertEqual(recorded[-1]["status"], "deferred")

    def test_counts(self):
        self.assertEqual(budget.finding_counts(budget.apply_finding_cap(SEVEN, 5)),
                         {"findings_count": 7, "actionable_count": 5, "deferred_count": 2})


if __name__ == "__main__":
    unittest.main()
