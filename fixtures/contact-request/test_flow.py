"""Browser regression checks for the intended contact-request outcome.

Uses the existing Python Playwright installation and a loopback-only HTTP server.
Set DEMO_EVIDENCE_DIR to retain screenshots, user-visible state, and a trace.
Set DEMO_PAGE=index.before.html to replay the intentionally defective baseline.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import threading
import unittest

from playwright.sync_api import sync_playwright, expect

HERE = Path(__file__).resolve().parent
ARTIFACTS = Path(os.environ.get("DEMO_EVIDENCE_DIR", str(HERE / "evidence" / "latest")))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(HERE)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/" + os.environ.get("DEMO_PAGE", "index.html")
        ARTIFACTS.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1100, "height": 900})
        self.context.tracing.start(screenshots=True, snapshots=True, sources=False)
        self.page = self.context.new_page()
        self.page.goto(self.base)
        self.observations = []

    def tearDown(self):
        name = self._testMethodName
        (ARTIFACTS / (name + ".json")).write_text(json.dumps(self.observations, indent=2), encoding="utf-8")
        self.context.tracing.stop(path=str(ARTIFACTS / (name + ".zip")))
        self.context.close()

    def capture(self, label):
        filename = self._testMethodName + "-" + label + ".png"
        self.page.screenshot(path=str(ARTIFACTS / filename), full_page=True)
        self.observations.append({
            "step": label, "screenshot": filename,
            "visible_text": self.page.locator("body").inner_text(),
            "name": self.page.get_by_label("Your name").input_value(),
            "email": self.page.get_by_label("Email address").input_value(),
            "request": self.page.get_by_label("What do you need help with?").input_value(),
            "focused_element": self.page.locator(":focus").evaluate("e => ({tag:e.tagName,id:e.id,text:e.textContent})")
                if self.page.locator(":focus").count() else None,
        })

    def fill(self, email="alex@example.test"):
        self.page.get_by_label("Your name").fill("Alex Morgan")
        self.page.get_by_label("Email address").fill(email)
        self.page.get_by_label("What do you need help with?").fill("Please help me change my delivery date.")

    def test_invalid_email_preserves_work_and_can_complete(self):
        self.fill("alex@")
        self.capture("entered")
        self.page.get_by_role("button", name="Send request", exact=True).click()
        self.capture("rejected")
        expect(self.page.get_by_label("Your name")).to_have_value("Alex Morgan")
        expect(self.page.get_by_label("What do you need help with?")).to_have_value("Please help me change my delivery date.")
        expect(self.page.get_by_label("Email address")).to_be_focused()
        expect(self.page.get_by_label("Email address")).to_have_attribute("aria-invalid", "true")
        expect(self.page.get_by_text("Enter an email address like name@example.com.", exact=True)).to_be_visible()
        self.page.get_by_label("Email address").fill("alex@example.test")
        self.page.get_by_role("button", name="Send request", exact=True).click()
        expect(self.page.get_by_role("heading", name="Request received")).to_be_visible()
        self.capture("completed")

    def test_empty_form_identifies_required_fields(self):
        self.page.get_by_role("button", name="Send request", exact=True).click()
        self.capture("required")
        expect(self.page.get_by_label("Your name")).to_be_focused()
        expect(self.page.get_by_text("Enter your name.", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Describe what you need help with.", exact=True)).to_be_visible()
        expect(self.page.get_by_label("Email address")).to_have_attribute("aria-describedby", "email-error")

    def test_keyboard_can_finish(self):
        self.page.keyboard.press("Tab")
        expect(self.page.get_by_label("Your name")).to_be_focused()
        self.page.keyboard.type("Alex Morgan")
        self.page.keyboard.press("Tab")
        self.page.keyboard.type("alex@example.test")
        self.page.keyboard.press("Tab")
        self.page.keyboard.type("Please help me change my delivery date.")
        self.page.keyboard.press("Tab")
        expect(self.page.get_by_role("button", name="Send request", exact=True)).to_be_focused()
        self.capture("keyboard-focus")
        self.page.keyboard.press("Enter")
        expect(self.page.get_by_role("heading", name="Request received")).to_be_visible()
        expect(self.page.locator("#confirmation")).to_be_focused()
        self.capture("keyboard-completed")

    def test_slow_send_can_cancel_without_losing_work(self):
        self.page.goto(self.base + "?scenario=slow")
        self.fill()
        self.page.get_by_role("button", name="Send request", exact=True).click()
        expect(self.page.get_by_role("button", name="Sending…", exact=True)).to_be_disabled()
        self.capture("sending")
        self.page.get_by_role("button", name="Cancel sending").click()
        expect(self.page.get_by_text("Sending cancelled. Your entries are still here.")).to_be_visible()
        # Wait beyond the service response to prove cancellation prevents late success.
        self.page.wait_for_timeout(2700)
        expect(self.page.get_by_role("heading", name="Request received")).to_be_hidden()
        expect(self.page.get_by_label("Your name")).to_have_value("Alex Morgan")
        expect(self.page.get_by_label("What do you need help with?")).to_have_value("Please help me change my delivery date.")
        self.capture("cancelled")
        self.page.get_by_role("button", name="Send request", exact=True).click()
        expect(self.page.get_by_role("heading", name="Request received")).to_be_visible()

    def test_keyboard_validation_recovery(self):
        self.page.keyboard.press("Tab")
        self.page.keyboard.type("Alex Morgan")
        self.page.keyboard.press("Tab")
        self.page.keyboard.type("alex@")
        self.page.keyboard.press("Tab")
        self.page.keyboard.type("Please help me change my delivery date.")
        self.page.keyboard.press("Tab")
        self.page.keyboard.press("Enter")
        expect(self.page.get_by_label("Email address")).to_be_focused()
        self.capture("keyboard-error")
        self.page.keyboard.press("ControlOrMeta+A")
        self.page.keyboard.type("alex@example.test")
        self.page.keyboard.press("Tab")
        self.page.keyboard.press("Tab")
        self.page.keyboard.press("Enter")
        expect(self.page.get_by_role("heading", name="Request received")).to_be_visible()
        expect(self.page.get_by_label("Your name")).to_have_value("Alex Morgan")
        expect(self.page.get_by_label("What do you need help with?")).to_have_value("Please help me change my delivery date.")
        self.capture("keyboard-recovered")

    def test_temporary_failure_allows_retry(self):
        self.page.goto(self.base + "?scenario=fail-once")
        self.fill()
        self.page.get_by_role("button", name="Send request", exact=True).click()
        expect(self.page.get_by_text("Could not send your request. Your entries are saved here. Please try again.")).to_be_visible()
        self.capture("service-failure")
        expect(self.page.get_by_label("Your name")).to_have_value("Alex Morgan")
        expect(self.page.get_by_label("What do you need help with?")).to_have_value("Please help me change my delivery date.")
        self.page.get_by_role("button", name="Send request", exact=True).click()
        expect(self.page.get_by_role("heading", name="Request received")).to_be_visible()
        self.capture("retried")

    def test_small_touch_viewport_recovery(self):
        self.context.close()
        self.context = self.browser.new_context(viewport={"width": 375, "height": 812}, is_mobile=True, has_touch=True)
        self.context.tracing.start(screenshots=True, snapshots=True, sources=False)
        self.page = self.context.new_page()
        self.page.goto(self.base)
        self.fill("alex@")
        self.page.get_by_role("button", name="Send request", exact=True).tap()
        self.capture("mobile-error")
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        expect(self.page.get_by_label("Your name")).to_have_value("Alex Morgan")
        self.page.get_by_label("Email address").fill("alex@example.test")
        self.page.get_by_role("button", name="Send request", exact=True).tap()
        expect(self.page.get_by_role("heading", name="Request received")).to_be_visible()
        self.capture("mobile-completed")


if __name__ == "__main__":
    unittest.main()
