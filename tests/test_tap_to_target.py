"""S4.5: a tap coordinate becomes the element under it, in a form a finding can carry."""
import os
from pathlib import Path
import tempfile
import unittest

from ux_recast.contracts import validate
from ux_recast.evidence import measure, tap_to_target

FIXTURE = Path(__file__).parents[1] / "fixtures" / "contact-request" / "index.html"

# The copied fixture page carries no data-* attributes and is pinned by hash, so the
# data-* state, sibling order, shadow root and scrolling cases use this page instead.
PAGE = """<!doctype html><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{margin:0;padding-bottom:2000px} .row{height:60px} button{width:200px;height:40px;display:block}
#far{margin-top:1500px}</style>
<div class="row"><button data-state="idle" data-kind="primary">Send</button></div>
<div class="row"><button>First</button><button data-state='say "hi"'>Second</button></div>
<x-card id="card"></x-card>
<button id="far" data-state="below">Far</button>
<script>
  const root = document.getElementById('card').attachShadow({mode: 'open'});
  root.innerHTML = '<style>span{display:block;width:200px;height:40px}</style><span data-part="title">Inside</span>';
</script>
"""


def finding_with(element):
    return {"schema": "ux-recast/findings@1", "provider": "local-agent", "task_sha256": "0" * 64, "reviewer": "test",
            "remaining_uncertainty": "none",
            "findings": [{"id": "F1", "category": "observed failure", "task_step": "submit", "observed": "fields cleared",
                          "evidence": "step rejected", "principle": "preserve work", "likely_consequence": "retyping",
                          "severity": "High", "confidence": "high", "confidence_reason": "captured values",
                          "proposed_correction": "do not reset", "verification": "resubmit and check values",
                          "kind": "implementation", "element": element}]}


class ElementReference(unittest.TestCase):
    def test_a_selector_without_data_state_is_the_reference(self):
        self.assertEqual(tap_to_target.element_reference({"selector": "#send", "data": {}}), "#send")

    def test_data_state_is_appended_in_name_order_and_escaped(self):
        capture = {"selector": "body > div > button",
                   "data": {"data-state": 'say "hi"', "data-kind": "a\\b", "data-x:y": "1"}}
        self.assertEqual(tap_to_target.element_reference(capture),
                         'body > div > button[data-kind="a\\\\b"][data-state="say \\"hi\\""][data-x\\:y="1"]')

    def test_inside_a_shadow_root_the_state_belongs_to_the_last_step(self):
        capture = {"selector": "#card >> span", "data": {"data-part": "title"}}
        self.assertEqual(tap_to_target.element_reference(capture), '#card >> span[data-part="title"]')

    def test_a_finding_accepts_the_reference(self):
        reference = tap_to_target.element_reference({"selector": "#send", "data": {"data-state": "idle"}})
        validate("findings", finding_with(reference))


def _browser():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch().close()
        return True
    except Exception:
        return False


@unittest.skipUnless(os.environ.get("UX_RECAST_BROWSER_TESTS") == "1" or _browser(), "needs Playwright Chromium")
class TapToTarget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        page = Path(cls.temp.name) / "page.html"
        page.write_text(PAGE, encoding="utf-8")
        cls.page, cls.fixture = page.as_uri(), FIXTURE.as_uri()

    def centre(self, url, selector):
        """The middle of an element's box, measured under the conditions a capture uses."""
        values = measure.measure(url, {"part": selector}, [("part", name) for name in ("x", "y", "width", "height")],
                                 revision="test")["values"]
        return values["part.x"] + values["part.width"] / 2, values["part.y"] + values["part.height"] / 2

    def resolves_to(self, url, reference):
        """The text of the one element a reference resolves to in a fresh page, or None."""
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url)
                found = page.locator(reference)
                return found.inner_text().strip() if found.count() == 1 else None
            finally:
                browser.close()

    def test_a_tap_on_the_fixture_page_yields_the_element_and_a_finding_accepts_it(self):
        x, y = self.centre(self.fixture, "#send")
        capture = tap_to_target.target_at(self.fixture, x, y, revision="fixture")
        self.assertEqual(capture["schema"], "ux-recast/tap-target@1")
        self.assertEqual((capture["selector"], capture["tag"], capture["data"]), ("#send", "button", {}))
        self.assertEqual(capture["point"], {"x": x, "y": y})
        self.assertTrue(capture["box"]["x"] <= x <= capture["box"]["x"] + capture["box"]["width"])
        conditions = capture["conditions"]
        self.assertTrue(conditions["engine"].startswith("chromium "))
        self.assertEqual((conditions["viewport"], conditions["device_pixel_ratio"], conditions["revision"]),
                         ("390x844", 3, "fixture"))
        self.assertEqual(conditions["url"], self.fixture)
        validate("findings", finding_with(tap_to_target.element_reference(capture)))

    def test_the_deepest_element_wins_over_its_container(self):
        x, y = self.centre(self.fixture, "label[for=email]")
        capture = tap_to_target.target_at(self.fixture, x, y, revision="fixture")
        self.assertEqual(capture["tag"], "label")
        self.assertNotIn(capture["selector"], ("body", "main", "form"))

    def test_data_state_comes_back_with_the_selector(self):
        capture = tap_to_target.target_at(self.page, 100, 20, revision="test")
        self.assertEqual(capture["selector"], "body > div:nth-of-type(1) > button")
        self.assertEqual(capture["data"], {"data-kind": "primary", "data-state": "idle"})
        self.assertEqual(tap_to_target.element_reference(capture),
                         'body > div:nth-of-type(1) > button[data-kind="primary"][data-state="idle"]')

    def test_same_tag_siblings_are_told_apart_and_the_reference_resolves(self):
        capture = tap_to_target.target_at(self.page, 100, 60 + 40 + 20, revision="test")
        self.assertEqual(capture["selector"], "body > div:nth-of-type(2) > button:nth-of-type(2)")
        self.assertEqual(self.resolves_to(self.page, tap_to_target.element_reference(capture)), "Second")

    def test_a_tap_inside_an_open_shadow_root_reaches_the_inner_element(self):
        capture = tap_to_target.target_at(self.page, 100, 120 + 20, revision="test")
        self.assertEqual((capture["selector"], capture["tag"]), ("#card >> span", "span"))
        self.assertEqual(capture["data"], {"data-part": "title"})
        self.assertEqual(self.resolves_to(self.page, tap_to_target.element_reference(capture)), "Inside")

    def test_a_tap_after_scrolling_finds_what_is_below_the_fold(self):
        _, page_y = self.centre(self.page, "#far")
        scroll = int(page_y) - 100
        capture = tap_to_target.target_at(self.page, 100, page_y - scroll, revision="test", scroll_y=scroll)
        self.assertEqual((capture["selector"], capture["data"]), ("#far", {"data-state": "below"}))
        self.assertEqual(capture["conditions"]["scroll_y"], scroll)

    def test_a_point_outside_the_viewport_has_no_element(self):
        with self.assertRaises(ValueError) as caught:
            tap_to_target.target_at(self.page, 5000, 20, revision="test")
        self.assertIn("No element at", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
