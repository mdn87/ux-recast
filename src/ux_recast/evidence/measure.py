"""Rendered measurements with the conditions they were taken under (S6.6; roundtable T-19).

A measurement opens one page in one engine at one viewport and device pixel ratio, waits for a
ready selector and for fonts, and reads named properties of named parts. Every result carries
the engine and its version, the viewport, the device pixel ratio, which of the page's font
families were actually available, the revision the caller names and the URL. Values are CSS
pixels, not screenshot pixels (C-41).

Properties:

- ``width``, ``height``, ``x``, ``y``: the part's border box (``getBoundingClientRect``);
- ``left-in:<part>`` / ``top-in:<part>``: offset of this part's box from another part's box;
- ``right-in:<part>`` / ``bottom-in:<part>``: the other part's right or bottom edge minus this
  part's, the inset on that side;
- ``gap-after:<part>``: this part's top minus the other part's bottom;
- ``css:<property>``: a computed style in px (``css:padding-top``, ``css:border-top-left-radius``,
  ``css:font-size``), or a unitless number (``css:font-weight``, ``css:line-height`` as a ratio of
  the font size when the computed value is in px).

Needs the ``playwright`` extra and a browser (``python -m playwright install chromium``).
"""
from datetime import datetime, timezone

SCRIPT = """
([parts, props]) => {
  const out = {}, boxes = {};
  const box = name => {
    if (!(name in boxes)) {
      const el = document.querySelector(parts[name]);
      if (!el) throw new Error('no element for part ' + name + ' (' + parts[name] + ')');
      boxes[name] = el.getBoundingClientRect();
    }
    return boxes[name];
  };
  const px = text => { const m = /^(-?[\\d.]+)px$/.exec(String(text).trim()); return m ? Number(m[1]) : null; };
  for (const [part, prop] of props) {
    const key = part + '.' + prop, b = box(part);
    const [kind, other] = prop.split(':');
    let value;
    if (['width', 'height', 'x', 'y'].includes(prop)) value = b[prop];
    else if (kind === 'left-in') value = b.left - box(other).left;
    else if (kind === 'top-in') value = b.top - box(other).top;
    else if (kind === 'right-in') value = box(other).right - b.right;
    else if (kind === 'bottom-in') value = box(other).bottom - b.bottom;
    else if (kind === 'gap-after') value = b.top - box(other).bottom;
    else if (kind === 'css') {
      const style = getComputedStyle(document.querySelector(parts[part])), raw = style.getPropertyValue(other);
      if (other === 'line-height') { const lh = px(raw), fs = px(style.fontSize); value = lh === null ? raw : Math.round(lh / fs * 1000) / 1000; }
      else value = px(raw) !== null ? px(raw) : (/^-?[\\d.]+$/.test(raw.trim()) ? Number(raw) : raw);
    } else throw new Error('unknown property ' + prop);
    out[key] = typeof value === 'number' ? Math.round(value * 1000) / 1000 : value;
  }
  return out;
}
"""

FONTS = """
(selectors) => {
  const families = new Set();
  for (const s of selectors) {
    const el = document.querySelector(s);
    if (el) getComputedStyle(el).fontFamily.split(',').forEach(f => families.add(f.trim().replace(/^["']|["']$/g, '')));
  }
  const generic = new Set(['serif', 'sans-serif', 'monospace', 'system-ui', 'ui-monospace', 'ui-sans-serif', 'cursive', 'fantasy']);
  const result = {};
  for (const f of families) result[f] = generic.has(f) ? 'generic' : document.fonts.check('14px "' + f + '"');
  return result;
}
"""


def conditions_key(conditions):
    """What must match between a recorded measurement and its re-measurement."""
    return (conditions["engine"], conditions["viewport"], conditions["device_pixel_ratio"])


def measure(url, parts, properties, *, revision, viewport=(390, 844), device_pixel_ratio=3, engine="chromium",
            ready=None, timeout_ms=15000):
    """Measure ``properties`` (pairs of part name and property) on ``url``; returns conditions and values."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = getattr(pw, engine).launch()
        try:
            context = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]},
                                          device_scale_factor=device_pixel_ratio, is_mobile=engine == "chromium",
                                          has_touch=True, reduced_motion="reduce")
            page = context.new_page()
            page.goto(url, wait_until="load", timeout=timeout_ms)
            if ready:
                page.wait_for_selector(ready, state="attached", timeout=timeout_ms)
            page.evaluate("document.fonts.ready.then(() => true)")
            values = page.evaluate(SCRIPT, [parts, [list(p) for p in properties]])
            fonts = page.evaluate(FONTS, sorted(set(parts.values())))
            used = next((name for name, available in fonts.items() if available is True), None)
            conditions = {"engine": f"{engine} {browser.version}", "viewport": f"{viewport[0]}x{viewport[1]}",
                          "device_pixel_ratio": device_pixel_ratio, "fonts": fonts,
                          "font_used": used or next((n for n, a in fonts.items() if a == "generic"), None),
                          "user_agent": page.evaluate("navigator.userAgent"), "revision": revision, "url": url,
                          "measured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")}
        finally:
            browser.close()
    return {"schema": "ux-recast/measurement@1", "conditions": conditions, "parts": parts, "values": values}
