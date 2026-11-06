"""A small project for the documentation tests: a git repo with a stylesheet, a page and a design record."""
import copy
import subprocess
from pathlib import Path

CSS = """:root{--line:#263140;--red:#ff685f}
.card{display:block;padding:10px 12px;border-radius:10px;border:1px solid var(--line);min-height:44px}
.chip{display:inline-block;height:18px;padding:0 9px;border-radius:999px;font:600 11px/1.5 sans-serif}
.title{display:block;margin-top:6px;font:600 14px/1.45 sans-serif}
"""
PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<link rel="stylesheet" href="theme.css"><style>body{margin:0;padding:6px 14px;font-family:sans-serif}</style></head>
<body><a class="card" id="card"><b class="chip" id="chip">Permission</b><span class="title" id="title">Codex on host</span></a></body></html>
"""
DESIGN = """# Design
- Radii: 10 px cards.
- Hit area at least 44 px.
"""


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def make_project(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "theme.css").write_text(CSS, encoding="utf-8", newline="\n")
    (root / "page.html").write_text(PAGE, encoding="utf-8", newline="\n")
    (root / "DESIGN.md").write_text(DESIGN, encoding="utf-8", newline="\n")
    git(root, "init", "-q")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.test", "add", ".")
    git(root, "-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-q", "-m", "fixture")
    return git(root, "rev-parse", "HEAD")


def entries(revision, engine="chromium 1.0"):
    def lit(code, name, value, unit, line, literal, **extra):
        return {"code": code, "name": name, "value": value, "unit": unit, "source": "css-literal", "state": "default",
                "viewport": "any", "file": "theme.css", "line": line, "revision": revision, "literal": literal, **extra}
    rendered = {"source": "rendered", "state": "default", "viewport": "390x844", "device_pixel_ratio": 1,
                "engine": engine, "revision": revision, "tolerance": 0.5}
    return [
        lit("S1", "card-pad-y", 10, "px", 2, "padding:{} 12px"),
        lit("S2", "card-pad-x", 12, "px", 2, "padding:10px {}"),
        lit("R1", "card-radius", 10, "px", 2, "border-radius:{}"),
        lit("H3", "chip-h", 18, "px", 3, "height:{}"),
        lit("S3", "title-gap", 6, "px", 4, "margin-top:{}"),
        {"code": "C1", "name": "approval", "value": "#ff685f", "unit": "color", "source": "token", "state": "default",
         "viewport": "any", "file": "theme.css", "line": 1, "revision": revision, "literal": "--red:{}", "token": "--red"},
        {"code": "T1", "name": "hit-min", "value": 44, "unit": "px", "source": "accepted", "state": "default", "viewport": "any",
         "file": "DESIGN.md", "line": 3, "revision": revision, "literal": "at least {}", "decision": "D-1"},
        {"code": "W", "name": "card-w", "value": 362, "unit": "px", "part": "card", "property": "width", **rendered},
        {"code": "H2", "name": "chip-box-h", "value": 18, "unit": "px", "part": "chip", "property": "height", **rendered},
        {"code": "Y1", "name": "chip-top", "value": 11, "unit": "px", "part": "chip", "property": "top-in:card",
         "formula": "S1 + 1", **rendered},
        {"code": "V1", "name": "viewport-margin", "value": "[TBD]", "unit": "px", "source": "proposed", "state": "default",
         "viewport": "any"},
    ]


def spec(revision, **changes):
    value = {
        "schema": "ux-recast/sheet@1", "component": "card", "title": "Card", "scope": "A waiting row", "dwg_no": "UI-CARD-001",
        "rev": "A", "date": "2026-11-06", "units": "CSS px", "scale": "1:1", "basis": "accepted", "source": "theme.css",
        "general_notes": ["Do not scale the drawing.", "Slots are placeholders."], "key_variables": ["W", "S1"],
        "notes": [{"n": 1, "text": "Chip sits on the first line."}],
        "variables": entries(revision),
        "tables": [{"title": "Spacing", "codes": ["S1", "S2", "S3", "Y1"]}, {"title": "Size", "codes": ["W", "H2", "H3", "T1", "V1"]},
                   {"title": "Radius and colour", "codes": ["R1", "C1"]}],
        "measurement": {"parts": {"card": "#card", "chip": "#chip"}},
        "drawing": {"width": 900, "height": 300, "views": [{"id": "plan", "x": 60, "y": 80, "scale": 2, "ops": [
            {"op": "title", "x": 0, "y": -40, "text": "Plan view", "sub": "scale 2:1"},
            {"op": "rect", "x": 0, "y": 0, "w": "W", "h": 60, "r": "R1"},
            {"op": "slot", "x": "S2", "y": "S1 + H3 + S3", "w": "W - 2*S2", "h": 20, "label": "title slot · fill"},
            {"op": "dim_h", "x1": 0, "x2": "W", "y": -12, "from1": 0, "from2": 0, "code": "W"},
            {"op": "dim_v", "y1": 0, "y2": "S1", "x": "W + 12", "from1": "W", "from2": "W", "code": "S1"}]}]},
    }
    value.update(changes)
    return copy.deepcopy(value)


class FakeMeasurer:
    """Answers re-measurements from a dict, under fixed conditions."""

    def __init__(self, values, engine="chromium 1.0", viewport="390x844", ratio=1):
        self.values, self.conditions = values, {"engine": engine, "viewport": viewport, "device_pixel_ratio": ratio}

    def __call__(self, rendered):
        return {e["code"]: (self.values.get(f'{e["part"]}.{e["property"]}'), self.conditions) for e in rendered}


TRUE_VALUES = {"card.width": 362, "chip.height": 18.2, "chip.top-in:card": 11}
