"""S6.7: the mechanical trace passes on true values and catches every seeded mutation."""
import os
import shutil
import tempfile
from pathlib import Path
import unittest

from ux_recast.docs import trace
from tests.docs import helpers


class Trace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="uxr-trace-"))
        cls.revision = helpers.make_project(cls.root)
        cls.reader = trace.SourceReader(cls.root)
        cls.measurer = helpers.FakeMeasurer(helpers.TRUE_VALUES)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_true_values_pass_with_zero_deltas(self):
        report = trace.trace(helpers.entries(self.revision), reader=self.reader, measurer=self.measurer)
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["deltas"], [])
        self.assertEqual(report["checked"], 10)
        self.assertEqual([item["code"] for item in report["remainder"]], ["V1"])

    def test_every_seeded_mutation_is_caught(self):
        entries = helpers.entries(self.revision)
        result = trace.sensitivity(entries, 40, reader=self.reader, measurer=self.measurer, seed=7)
        self.assertGreaterEqual(result["seeded"], 20)
        self.assertEqual(result["missed"], [], result["missed"])
        self.assertEqual({r["kind"] for r in result["results"]}, {"value", "line", "literal", "formula"})

    def test_many_seeds(self):
        entries = helpers.entries(self.revision)
        for seed in range(5):
            with self.subTest(seed=seed):
                self.assertEqual(trace.sensitivity(entries, 10, reader=self.reader, measurer=self.measurer, seed=seed)["missed"], [])

    def test_other_conditions_are_a_delta_not_a_pass(self):
        other = helpers.FakeMeasurer(helpers.TRUE_VALUES, engine="webkit 26.0")
        report = trace.trace(helpers.entries(self.revision), reader=self.reader, measurer=other)
        self.assertFalse(report["passed"])
        self.assertEqual({d["kind"] for d in report["deltas"]}, {"conditions"})

    def test_no_measurer_leaves_rendered_values_unmeasured(self):
        report = trace.trace(helpers.entries(self.revision), reader=self.reader)
        self.assertFalse(report["passed"])
        self.assertEqual(sorted(report["unmeasured"]), ["H2", "W", "Y1"])

    def test_an_explained_delta_is_reported_and_does_not_fail(self):
        values = dict(helpers.TRUE_VALUES, **{"card.width": 360})
        report = trace.trace(helpers.entries(self.revision), reader=self.reader, measurer=helpers.FakeMeasurer(values),
                             explanations={"W": "fixture viewport differs"})
        self.assertTrue(report["passed"])
        self.assertEqual(report["deltas"][0]["explained"], "fixture viewport differs")

    def test_a_changed_source_line_is_caught_at_a_new_revision(self):
        css = (self.root / "theme.css").read_text(encoding="utf-8").replace("padding:10px 12px", "padding:8px 12px")
        clone = Path(tempfile.mkdtemp(prefix="uxr-trace2-"))
        try:
            revision = helpers.make_project(clone)
            (clone / "theme.css").write_text(css, encoding="utf-8", newline="\n")
            helpers.git(clone, "-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-qam", "change")
            entries = helpers.entries(helpers.git(clone, "rev-parse", "HEAD"))
            report = trace.trace(entries, reader=trace.SourceReader(clone), measurer=self.measurer)
            # S2's literal quotes its neighbour, so a change beside it is flagged for re-checking too.
            self.assertEqual([d["code"] for d in report["deltas"]], ["S1", "S2"])
            self.assertTrue(trace.trace(helpers.entries(revision), reader=trace.SourceReader(clone), measurer=self.measurer)["passed"])
        finally:
            shutil.rmtree(clone, ignore_errors=True)


def _browser():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch().close()
        return True
    except Exception:
        return False


@unittest.skipUnless(os.environ.get("UX_RECAST_BROWSER_TESTS") == "1" or _browser(), "needs Playwright Chromium")
class RealMeasurement(unittest.TestCase):
    """S6.6 against a real page: measured values carry their conditions and re-measure within tolerance."""

    def test_page_measurer_round_trip(self):
        from ux_recast.evidence import measure
        root = Path(tempfile.mkdtemp(prefix="uxr-measure-"))
        try:
            revision = helpers.make_project(root)
            url = (root / "page.html").resolve().as_uri()
            parts = {"card": "#card", "chip": "#chip"}
            done = measure.measure(url, parts, [("card", "width"), ("chip", "height"), ("chip", "top-in:card"),
                                                ("card", "css:padding-top"), ("card", "css:border-top-left-radius")],
                                   revision=revision, device_pixel_ratio=1)
            conditions = done["conditions"]
            self.assertTrue(conditions["engine"].startswith("chromium "))
            self.assertEqual((conditions["viewport"], conditions["device_pixel_ratio"]), ("390x844", 1))
            self.assertIn("fonts", conditions)
            self.assertEqual(done["values"]["card.width"], 362)
            self.assertEqual(done["values"]["card.css:padding-top"], 10)
            self.assertEqual(done["values"]["card.css:border-top-left-radius"], 10)
            entries = helpers.entries(revision, engine=conditions["engine"])
            for entry in entries:
                if entry["source"] == "rendered":
                    entry.update(device_pixel_ratio=1, value=done["values"].get(f'{entry["part"]}.{entry["property"]}', entry["value"]))
                    entry.pop("formula", None)
            report = trace.trace(entries, reader=trace.SourceReader(root), measurer=trace.page_measurer(url, parts))
            self.assertTrue(report["passed"], report)
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
