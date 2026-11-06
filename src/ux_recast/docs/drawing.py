"""SVG drawing kit for component sheets.

Line conventions follow the Dimensional Drawing sheet format (MIT, Enes Ozturk, pinned at
5c457437c8c8; see the notice in ``templates/sheet.html``): object outline 1.6, dimension lines
0.7, extension lines 0.55 offset 3 and overshooting 5, filled 7-unit arrows, 11-unit dimension
text knocked out in white, 9-unit capital slot labels, dashed slots, light gray hug fills, long
dashes for regions and dash-dot for centre lines and envelopes. Monochrome by design (C-46).

A view is a list of operations. Geometry may be a number or a formula over variable codes
(``"S1 + H3"``), multiplied by the view's ``scale``, so the drawing is computed from the same
table the sheet prints and cannot drift from it. Every dimension shows a code, never a number.
"""
from html import escape

from ux_recast.contracts import ContractError
from ux_recast.docs.variables import evaluate

STYLES = {
    "outline": 'fill="none" stroke="#111" stroke-width="1.6"',
    "inset": 'fill="#f2f2f2" stroke="#111" stroke-width="1"',
    "hug": 'fill="#e6e6e6" stroke="#111" stroke-width="1"',
    "slot": 'fill="none" stroke="#555" stroke-width="0.9" stroke-dasharray="4 3"',
    "region": 'fill="none" stroke="#777" stroke-width="0.7" stroke-dasharray="10 4"',
    "envelope": 'fill="none" stroke="#777" stroke-width="0.7" stroke-dasharray="12 3 2 3"',
    "hit": 'fill="url(#hatch)" stroke="#777" stroke-width="0.6" stroke-dasharray="2 2"',
    "edge": 'fill="#333" stroke="none"',
}
OPS = {"rect", "line", "text", "slot", "dim_h", "dim_v", "callout", "note", "title"}


class View:
    def __init__(self, codes, scale, origin, where):
        self.codes, self.scale, self.where = codes, scale, where
        self.ox, self.oy = origin
        self.parts = []

    def num(self, value, key, *, scaled=True):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result = value
        elif isinstance(value, str):
            result = evaluate(value, self.codes, f"{self.where}.{key}")
        else:
            raise ContractError(f"{self.where}.{key}", "a number or a formula over codes")
        return result * self.scale if scaled else result

    def x(self, op, key):
        return self.ox + self.num(op[key], key)

    def y(self, op, key):
        return self.oy + self.num(op[key], key)

    def add(self, svg):
        self.parts.append(svg)


def _f(value):
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _label(text, x, y, *, size=11, anchor="middle", cls="dim", rotate=None):
    turn = f' transform="rotate({rotate} {_f(x)} {_f(y)})"' if rotate else ""
    return (f'<text class="{cls}" x="{_f(x)}" y="{_f(y)}" font-size="{size}" text-anchor="{anchor}"'
            f'{turn}>{escape(text)}</text>')


def _code(op, where):
    code = op.get("code")
    if not isinstance(code, str) or not code:
        raise ContractError(f"{where}.code", "a dimension shows a code from the table")
    return code


def render_view(view, codes, where="view"):
    """Render one view to an SVG ``<g>``; returns ``(svg, codes_referenced)``."""
    scale = view.get("scale", 1)
    v = View(codes, scale, (view.get("x", 0), view.get("y", 0)), where)
    referenced = set()
    for index, op in enumerate(view.get("ops", [])):
        w = f"{where}.ops[{index}]"
        kind = op.get("op")
        if kind not in OPS:
            raise ContractError(f"{w}.op", f"{kind!r} not in {sorted(OPS)}")
        v.where = w
        if kind in {"rect", "slot"}:
            x, y, width, height = v.x(op, "x"), v.y(op, "y"), v.num(op["w"], "w"), v.num(op["h"], "h")
            radius = v.num(op.get("r", 0), "r")
            style = STYLES["slot" if kind == "slot" else op.get("style", "outline")]
            mark = ' data-slot="true"' if kind == "slot" else ""
            v.add(f'<rect{mark} x="{_f(x)}" y="{_f(y)}" width="{_f(width)}" height="{_f(height)}" rx="{_f(radius)}" {style}/>')
            if kind == "slot" and op.get("label"):
                v.add(_label(op["label"].upper(), x + width / 2, y + height / 2 + 3, size=9, cls="slot"))
        elif kind == "line":
            dash = {"center": ' stroke-dasharray="12 3 2 3"', "region": ' stroke-dasharray="10 4"'}.get(op.get("style"), "")
            v.add(f'<line x1="{_f(v.x(op, "x1"))}" y1="{_f(v.y(op, "y1"))}" x2="{_f(v.x(op, "x2"))}" y2="{_f(v.y(op, "y2"))}" '
                  f'stroke="#555" stroke-width="{op.get("width", 0.7)}"{dash}/>')
        elif kind == "text":
            v.add(_label(op["text"], v.x(op, "x"), v.y(op, "y"), size=op.get("size", 9), anchor=op.get("anchor", "start"),
                         cls=op.get("cls", "slot")))
        elif kind == "title":
            v.add(_label(op["text"].upper(), v.x(op, "x"), v.y(op, "y"), size=12, anchor="start", cls="vt"))
            if op.get("sub"):
                v.add(_label(op["sub"].upper(), v.x(op, "x"), v.y(op, "y") + 14, size=9.5, anchor="start", cls="vs"))
        elif kind == "dim_h":
            code = _code(op, w)
            referenced.add(code)
            x1, x2, y = v.x(op, "x1"), v.x(op, "x2"), v.y(op, "y")
            e1, e2 = v.y(op, "from1") if "from1" in op else y, v.y(op, "from2") if "from2" in op else y
            for xe, ye in ((x1, e1), (x2, e2)):
                if abs(ye - y) > 0.01:
                    sign = 1 if y > ye else -1
                    v.add(f'<line class="ext" x1="{_f(xe)}" y1="{_f(ye + 3 * sign)}" x2="{_f(xe)}" y2="{_f(y + 5 * sign)}"/>')
            outside = abs(x2 - x1) < 28
            v.add(f'<line class="dl" x1="{_f(x1)}" y1="{_f(y)}" x2="{_f(x2)}" y2="{_f(y)}" '
                  + ('marker-start="url(#arr-out)" marker-end="url(#arr-out)"/>' if outside else
                     'marker-start="url(#arr)" marker-end="url(#arr)"/>'))
            label = op.get("label", code)
            dy = 13 if op.get("below") else -4
            v.add(_label(label, (x1 + x2) / 2 + op.get("dx", 0), y + dy + op.get("dy", 0)).replace("<text ", f'<text data-code="{escape(code)}" ', 1))
        elif kind == "dim_v":
            code = _code(op, w)
            referenced.add(code)
            y1, y2, x = v.y(op, "y1"), v.y(op, "y2"), v.x(op, "x")
            e1, e2 = v.x(op, "from1") if "from1" in op else x, v.x(op, "from2") if "from2" in op else x
            for ye, xe in ((y1, e1), (y2, e2)):
                if abs(xe - x) > 0.01:
                    sign = 1 if x > xe else -1
                    v.add(f'<line class="ext" x1="{_f(xe + 3 * sign)}" y1="{_f(ye)}" x2="{_f(x + 5 * sign)}" y2="{_f(ye)}"/>')
            outside = abs(y2 - y1) < 28
            v.add(f'<line class="dl" x1="{_f(x)}" y1="{_f(y1)}" x2="{_f(x)}" y2="{_f(y2)}" '
                  + ('marker-start="url(#arr-out)" marker-end="url(#arr-out)"/>' if outside else
                     'marker-start="url(#arr)" marker-end="url(#arr)"/>'))
            label = op.get("label", code)
            side = op.get("side", "r")
            lx = x + (6 if side == "r" else -6) + op.get("dx", 0)
            v.add(_label(label, lx, (y1 + y2) / 2 + 4 + op.get("dy", 0), anchor="start" if side == "r" else "end")
                  .replace("<text ", f'<text data-code="{escape(code)}" ', 1))
        elif kind == "callout":
            px, py, ex, ey = v.x(op, "px"), v.y(op, "py"), v.x(op, "ex"), v.y(op, "ey")
            shoulder = ex + (14 if op.get("dir", "r") == "r" else -14)
            v.add(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="1.8" fill="#111"/>'
                  f'<polyline class="lead" points="{_f(px)},{_f(py)} {_f(ex)},{_f(ey)} {_f(shoulder)},{_f(ey)}"/>')
            text = op["label"]
            for code in op.get("codes", []):
                referenced.add(code)
            v.add(_label(text, shoulder + (3 if op.get("dir", "r") == "r" else -3), ey + 4,
                         anchor="start" if op.get("dir", "r") == "r" else "end", cls="dim"))
        elif kind == "note":
            x, y = v.x(op, "x"), v.y(op, "y")
            v.add(f'<rect class="nb" x="{_f(x - 8)}" y="{_f(y - 8)}" width="16" height="16"/>'
                  + _label(str(op["n"]), x, y + 4, size=10, cls="nbt"))
    return "\n".join(v.parts), referenced


def render_drawing(views, codes, *, width, height, where="drawing"):
    """The sheet's SVG: border, defs (arrows and hatch), then every view in order."""
    body, referenced = [], set()
    for index, view in enumerate(views):
        svg, used = render_view(view, codes, f"{where}.views[{index}]")
        body.append(f'<g class="view" data-view="{escape(view.get("id", str(index)))}">{svg}</g>')
        referenced |= used
    svg = (f'<svg class="sheet" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Component drawing">'
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0,1 L10,5 L0,9 z" fill="#111"/></marker>'
           '<marker id="arr-out" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M10,1 L0,5 L10,9 z" fill="#111"/></marker>'
           '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           '<line x1="0" y1="0" x2="0" y2="6" stroke="#999" stroke-width="0.8"/></pattern></defs>'
           f'<rect x="6" y="6" width="{width - 12}" height="{height - 12}" rx="14" fill="#fff" stroke="#111" stroke-width="1.2"/>'
           + "\n".join(body) + "</svg>")
    return svg, referenced
