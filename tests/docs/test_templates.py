"""S6.3 and S6.4: any subset of guide sections renders; the sheet template carries its notice and opens standalone."""
import os
import re
import tempfile
from pathlib import Path
import unittest

from ux_recast.contracts import ContractError
from ux_recast.docs import guide, sheet
from tests.docs import helpers

META = {"subject": "Card", "basis": "accepted", "basis_reference": "D-1", "sources": "DESIGN.md", "sheets": "card"}


class Guide(unittest.TestCase):
    def test_every_single_section_and_every_prefix_renders_and_validates(self):
        for key in guide.ORDER:
            with self.subTest(section=key):
                summary = guide.validate(guide.render(META, {key: "Body."}))
                self.assertEqual(summary["sections"], [key])
        for size in range(1, len(guide.ORDER) + 1):
            chosen = {key: "Body." for key in guide.ORDER[:size]}
            self.assertEqual(guide.validate(guide.render(META, chosen))["sections"], guide.ORDER[:size])

    def test_sections_keep_template_order_whatever_the_input_order(self):
        text = guide.render(META, {"reasons": "R.", "audience": "A."})
        self.assertLess(text.index("## Audience"), text.index("## Reasons"))

    def test_content_behavior_is_required_only_when_a_sheet_uses_slots(self):
        text = guide.render(META, {"spacing": "S."})
        guide.validate(text, sheet_uses_slots=False)
        with self.assertRaises(ContractError) as caught:
            guide.validate(text, sheet_uses_slots=True)
        self.assertIn("content-behavior", caught.exception.field)
        guide.validate(guide.render(META, {"spacing": "S.", "content-behavior": "Wraps."}), sheet_uses_slots=True)

    def test_basis_is_stated(self):
        for meta in ({**META, "basis": ""}, {**META, "basis": "guess"}, {**META, "basis_reference": ""}):
            with self.subTest(meta=meta), self.assertRaises(ContractError):
                guide.validate(guide.render(meta, {"audience": "A."}))
        guide.validate(guide.render({**META, "basis": "observed", "basis_reference": ""}, {"audience": "A."}))

    def test_refusals(self):
        good = guide.render(META, {"audience": "A.", "color": "C."})
        for bad in (good.replace("Color and status semantics", "Colours"), good.replace("C.", ""),
                    good.replace("A.", "{{fill me}}"), good.replace("<!-- ux-recast:section color -->\n", ""),
                    good + "\n<!-- ux-recast:section audience -->\n## Audience and principles\n\nAgain.\n"):
            with self.assertRaises(ContractError):
                guide.validate(bad)

    def test_template_has_every_section_and_no_default_values(self):
        text = guide.template()
        self.assertEqual([key for key, _ in guide.MARKER.findall(text)], guide.ORDER)
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,8}\b|\d+\s*px", text), "the template carries no palette or sizes (C-37)")


class Sheet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = sheet.render(helpers.spec("0123456789abcdef0123"))

    def test_template_carries_the_notice_and_pinned_commit(self):
        head = sheet.template().split("<html", 1)[0]
        for needle in ("MIT License", "Copyright (c) 2026 Enes Ozturk", "5c457437c8c83524308aad3b7443e81adcc13153",
                       "https://github.com/enesozturk/dimensional-drawing"):
            self.assertIn(needle, head)

    def test_rendered_sheet_validates_with_table_and_tbd(self):
        summary = sheet.validate(self.html)
        self.assertEqual((summary["count"], summary["tbd"], summary["uses_slots"]), (11, 1, True))
        self.assertIn('<td class="val tbd">[TBD]</td>', self.html)
        self.assertIn('data-tbd-ratio="0.0909"', self.html)
        self.assertIn('[TBD] values: 1 of 11 (9.1%)', self.html)
        for code in ("W", "S1", "Y1", "C1"):
            self.assertIn(f'<tr data-code="{code}">', self.html)

    def test_drawing_shows_codes_from_the_table_only(self):
        spec = helpers.spec("0123456789abcdef0123")
        spec["drawing"]["views"][0]["ops"].append({"op": "dim_h", "x1": 0, "x2": 10, "y": 0, "code": "Q9"})
        with self.assertRaises(ContractError):
            sheet.render(spec)

    def test_every_code_sits_in_one_table(self):
        spec = helpers.spec("0123456789abcdef0123")
        spec["tables"][0]["codes"].remove("S1")
        with self.assertRaises(ContractError):
            sheet.render(spec)

    def test_hand_edits_and_outside_resources_are_refused(self):
        for bad in (self.html.replace(">10 px<", ">11 px<", 1),
                    self.html.replace("</style>", "</style><link rel=\"stylesheet\" href=\"https://example.test/x.css\">", 1),
                    self.html.replace('stroke="#111" stroke-width="1.6"', 'stroke="#38d6ff" stroke-width="1.6"', 1),
                    self.html.replace("Copyright (c) 2026 Enes Ozturk", "")):
            with self.assertRaises(ContractError):
                sheet.validate(bad)


def _browser():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            pw.chromium.launch().close()
        return True
    except Exception:
        return False


@unittest.skipUnless(os.environ.get("UX_RECAST_BROWSER_TESTS") == "1" or _browser(), "needs Playwright Chromium")
class Standalone(unittest.TestCase):
    def test_sheet_opens_offline_and_renders_its_parts(self):
        from playwright.sync_api import sync_playwright
        path = Path(tempfile.mkdtemp(prefix="uxr-sheet-")) / "card.html"
        path.write_text(sheet.render(helpers.spec("0123456789abcdef0123")), encoding="utf-8")
        requests = []
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1800, "height": 1200})
            page.on("request", lambda r: requests.append(r.url))
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(path.as_uri())
            self.assertEqual(page.locator("table tr[data-code]").count(), 11)
            self.assertEqual(page.locator("svg.sheet text[data-code]").count(), 2)
            self.assertIn("[TBD] values: 1 of 11", page.inner_text("body"))
            browser.close()
        self.assertEqual([u for u in requests if not u.startswith("file:")], [])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
