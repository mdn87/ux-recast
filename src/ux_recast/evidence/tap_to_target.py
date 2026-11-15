"""Tap-to-target capture (S4.5; decision D-12, roundtable P-3).

A person points at a thing on a page, and the finding should carry a reference to that thing.
``target_at`` opens one page in one engine at one viewport, takes the deepest element under a
point, and returns a selector for it, its ``data-*`` attributes, its box, and the conditions the
capture was taken under. ``element_reference`` turns a capture into the string a finding's
``element`` field carries.

The point is in CSS pixels from the top left of the viewport, after any ``scroll_y``. A point read
off a screenshot is in screenshot pixels: divide it by the device pixel ratio first.

Deepest means the innermost element the browser would deliver the tap to: ``elementFromPoint``,
followed into open shadow roots. Inside a shadow root the selector is the host's selector, then
``>>``, then the selector within that root (the form Playwright locators take). A frame's content
is not entered; a tap on a frame yields the frame element.

Every selector is checked before it is returned: it must resolve back to the one element that was
tapped, so a capture never names a neighbour.

Needs the ``playwright`` extra and a browser (``python -m playwright install chromium``).
"""
from datetime import datetime, timezone
import re

SCHEMA = "ux-recast/tap-target@1"

SCRIPT = """
([x, y]) => {
  let el = document.elementFromPoint(x, y);
  if (!el) return null;
  while (el.shadowRoot) {
    const inner = el.shadowRoot.elementFromPoint(x, y);
    if (!inner || inner === el || !el.shadowRoot.contains(inner)) break;
    el = inner;
  }
  const within = node => {
    const root = node.getRootNode(), parts = [];
    for (let n = node; n; n = n.parentElement) {
      if (n.id && root.querySelectorAll('#' + CSS.escape(n.id)).length === 1) { parts.unshift('#' + CSS.escape(n.id)); break; }
      if (n === document.body) { parts.unshift('body'); break; }
      const same = Array.from(n.parentNode.children).filter(c => c.localName === n.localName);
      parts.unshift(same.length === 1 ? n.localName : n.localName + ':nth-of-type(' + (same.indexOf(n) + 1) + ')');
    }
    return parts.join(' > ');
  };
  const steps = [];
  for (let n = el; n;) {
    steps.unshift(within(n));
    const root = n.getRootNode();
    n = root instanceof ShadowRoot ? root.host : null;
  }
  const selector = steps.join(' >> ');
  const resolved = steps.reduce((scope, step) => {
    const base = scope === document ? document : scope && scope.shadowRoot;
    const found = base ? base.querySelectorAll(step) : [];
    return found.length === 1 ? found[0] : null;
  }, document);
  if (resolved !== el) throw new Error('selector does not resolve back to the tapped element: ' + selector);
  const data = {};
  for (const attribute of Array.from(el.attributes)) {
    if (attribute.name.startsWith('data-')) data[attribute.name] = attribute.value;
  }
  const box = el.getBoundingClientRect(), round = value => Math.round(value * 1000) / 1000;
  return {selector, tag: el.localName, data,
          box: {x: round(box.x), y: round(box.y), width: round(box.width), height: round(box.height)},
          scroll_y: round(window.scrollY)};
}
"""


def target_at(url, x, y, *, revision, viewport=(390, 844), device_pixel_ratio=3, engine="chromium",
              scroll_y=0, ready=None, timeout_ms=15000):
    """The deepest element at CSS-pixel point ``(x, y)`` of ``url``: selector, ``data-*`` state, box, conditions."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        try:
            # The same context a measurement uses, so a point read from one applies to the other.
            context = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]},
                                          device_scale_factor=device_pixel_ratio, is_mobile=engine == "chromium",
                                          has_touch=True, reduced_motion="reduce")
            page = context.new_page()
            page.goto(url, wait_until="load", timeout=timeout_ms)
            if ready:
                page.wait_for_selector(ready, state="attached", timeout=timeout_ms)
            if scroll_y:
                page.evaluate("y => window.scrollTo(0, y)", scroll_y)
            found = page.evaluate(SCRIPT, [x, y])
            version = browser.version
        finally:
            browser.close()
    if found is None:
        raise ValueError(f"No element at ({x}, {y}) in a {viewport[0]}x{viewport[1]} viewport")
    conditions = {"engine": f"{engine} {version}", "viewport": f"{viewport[0]}x{viewport[1]}",
                  "device_pixel_ratio": device_pixel_ratio, "scroll_y": found.pop("scroll_y"),
                  "revision": revision, "url": url,
                  "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}
    return {"schema": SCHEMA, "point": {"x": x, "y": y}, **found, "conditions": conditions}


def element_reference(capture):
    """The string for a finding's ``element`` field: the selector, then the ``data-*`` state as attribute selectors.

    The state is what the element carried when it was tapped, in attribute-name order, so the
    reference names the element and records the state the finding was observed in.
    """
    state = "".join(f'[{_css_name(name)}="{_css_string(value)}"]' for name, value in sorted(capture["data"].items()))
    return capture["selector"] + state


def _css_name(name):
    return re.sub(r"([^a-zA-Z0-9_-])", r"\\\1", name)


def _css_string(value):
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\a ")
