"""Component specification sheets: a JSON spec rendered to one self-contained HTML file (C-42 to C-46).

The spec (``ux-recast/sheet@1``) carries the title block, notes, the variable table, how the table
is grouped and the drawing's views. ``render`` turns it into HTML from ``templates/sheet.html``;
the spec is embedded in the page, so ``validate`` can re-render it and require the page to match
byte for byte. That makes the drawing, the printed tables and the data one artifact: a value
edited in the HTML alone, or a drawing code missing from the table, fails validation.
"""
from html import escape
from importlib import resources
import json
import re

from ux_recast.contracts import ContractError
from ux_recast.docs import drawing, variables

SCHEMA = "ux-recast/sheet@1"
UPSTREAM_COMMIT = "5c457437c8c83524308aad3b7443e81adcc13153"
NOTICE = ("MIT License", "Copyright (c) 2026 Enes Ozturk", UPSTREAM_COMMIT)
SPEC_BLOCK = re.compile(r'<script type="application/json" id="ux-recast-sheet">(.*?)</script>', re.S)
HEX_COLOR = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
EXTERNAL = re.compile(r"""(?:src|href)\s*=\s*["']?(?:https?:)?//|@import|url\(\s*["']?(?:https?:)?//""", re.I)


def template():
    return resources.files("ux_recast.docs").joinpath("templates/sheet.html").read_text("utf-8")


def _gray(hex_value):
    value = hex_value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return value[0:2].lower() == value[2:4].lower() == value[4:6].lower()


def _source_text(entry):
    source = entry["source"]
    if entry["value"] == variables.TBD:
        text = "unresolved"
    elif source in {"token", "css-literal", "accepted"}:
        text = f'{source} {entry["file"].rsplit("/", 1)[-1]}:{entry["line"]} @{entry["revision"][:8]}'
        if source == "token":
            text += f' ({entry["token"]})'
        if source == "accepted":
            text += f' ({entry["decision"]})'
    elif source == "rendered":
        text = (f'rendered {entry["part"]} {entry["property"]} · {entry["engine"]} · {entry["viewport"]} '
                f'@{variables.format_number(entry["device_pixel_ratio"])}x ±{variables.format_number(entry["tolerance"])} '
                f'@{entry["revision"][:8]}')
    else:
        text = f'proposed: {entry["proposal"]}'
    if entry.get("formula"):
        text = f'{entry["code"]} = {entry["formula"]} · ' + text
    return text


def _check_spec(spec):
    if not isinstance(spec, dict) or spec.get("schema") != SCHEMA:
        raise ContractError("sheet.schema", f"must be {SCHEMA}")
    for key in ("component", "title", "scope", "dwg_no", "rev", "date", "units", "scale", "basis", "source"):
        if not (isinstance(spec.get(key), str) and spec[key].strip()):
            raise ContractError(f"sheet.{key}", "missing or empty")
    if spec["basis"] not in {"observed", "accepted", "proposed"}:
        raise ContractError("sheet.basis", "observed, accepted or proposed (C-38)")
    summary = variables.validate_table(spec.get("variables"), "sheet.variables")
    codes = {entry["code"]: entry for entry in spec["variables"]}
    grouped = []
    for index, table in enumerate(spec.get("tables") or []):
        if not (isinstance(table, dict) and isinstance(table.get("title"), str) and isinstance(table.get("codes"), list)):
            raise ContractError(f"sheet.tables[{index}]", "expected {title, codes}")
        grouped += table["codes"]
    if sorted(grouped) != sorted(codes):
        missing, unknown = sorted(set(codes) - set(grouped)), sorted(set(grouped) - set(codes))
        raise ContractError("sheet.tables", f"every code in exactly one table; missing {missing}, unknown {unknown}, "
                                            f"repeated {sorted({c for c in grouped if grouped.count(c) > 1})}")
    for code in spec.get("key_variables", []):
        if code not in codes:
            raise ContractError("sheet.key_variables", f"{code} is not in the table")
    for index, note in enumerate(spec.get("notes", [])):
        if not (isinstance(note, dict) and isinstance(note.get("n"), int) and isinstance(note.get("text"), str)):
            raise ContractError(f"sheet.notes[{index}]", "expected {n, text}")
    draw = spec.get("drawing")
    if not (isinstance(draw, dict) and isinstance(draw.get("views"), list) and draw["views"]):
        raise ContractError("sheet.drawing", "expected {width, height, views}")
    return summary, codes


def render(spec):
    """Render ``spec`` to HTML; raises ContractError when the spec, its table or its drawing is inconsistent."""
    summary, codes = _check_spec(spec)
    svg, referenced = drawing.render_drawing(spec["drawing"]["views"], codes, width=spec["drawing"].get("width", 1700),
                                             height=spec["drawing"].get("height", 1060), where="sheet.drawing")
    unknown = sorted(referenced - set(codes))
    if unknown:
        raise ContractError("sheet.drawing", f"codes on the drawing that are not in the table: {unknown}")
    tables = []
    for table in spec["tables"]:
        rows = []
        for code in table["codes"]:
            entry = codes[code]
            value = variables.display(entry)
            cls = "val tbd" if value == variables.TBD else "val"
            rows.append(f'<tr data-code="{escape(code)}"><td class="code">{escape(code)}</td><td>{escape(entry["name"])}</td>'
                        f'<td class="{cls}">{escape(value)}</td><td>{escape(entry["state"])} · {escape(entry["viewport"])}</td>'
                        f'<td class="src">{escape(_source_text(entry))}</td></tr>')
        tables.append(f'<table><caption>{escape(table["title"])}</caption><thead><tr><th>Code</th><th>Variable</th>'
                      f'<th>Value</th><th>State · viewport</th><th>Source</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')
    general = "".join(f"<div>{escape(text)}</div>" for text in spec.get("general_notes", []))
    keys = "".join(f'<span><b>{escape(code)}</b> · {escape(codes[code]["name"])} '
                   f'{escape(codes[code].get("formula", "").lower() or variables.display(codes[code]))}</span>'
                   for code in spec.get("key_variables", []))
    notes = "".join(f'<li><span class="n">{note["n"]}</span><span>{escape(note["text"])}</span></li>' if note["n"] else
                    f'<li><span>{escape(note["text"])}</span></li>' for note in spec.get("notes", []))
    spec_json = json.dumps(spec, indent=1, ensure_ascii=False, sort_keys=True).replace("<", "\\u003c")
    fields = {"TITLE": spec["title"], "SCOPE": spec["scope"], "DWG_NO": spec["dwg_no"], "REV": spec["rev"],
              "UNITS": spec["units"], "SCALE": spec["scale"], "BASIS": spec["basis"], "SOURCE": spec["source"],
              "FOOTER_LEFT": spec.get("footer", {}).get("left", spec["date"]),
              "FOOTER_RIGHT": spec.get("footer", {}).get("right", spec["component"]),
              "TBD_RATIO": str(summary["tbd_ratio"]), "TBD_COUNT": str(summary["tbd"]),
              "VAR_COUNT": str(summary["count"]), "TBD_PERCENT": f'{summary["tbd_ratio"] * 100:.1f}%'}
    html = template()
    for key, value in fields.items():
        html = html.replace("{{" + key + "}}", escape(value))
    for key, value in {"GENERAL_NOTES": general, "KEY_VARIABLES": keys, "DRAWING": svg, "NOTES": notes,
                       "TABLES": "".join(tables), "SPEC_JSON": spec_json}.items():
        html = html.replace("{{" + key + "}}", value)
    return html


def spec_of(html):
    match = SPEC_BLOCK.search(html)
    if not match:
        raise ContractError("sheet", "no embedded ux-recast-sheet spec")
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError as error:
        raise ContractError("sheet", f"embedded spec is not JSON: {error.msg}") from None


def uses_slots(spec):
    return any(op.get("op") == "slot" for view in spec["drawing"]["views"] for op in view.get("ops", []))


def validate(html):
    """Check a rendered sheet: notice, self-contained, monochrome, and identical to its own spec's rendering."""
    head = html[:html.find("<html")]
    for needle in NOTICE:
        if needle not in head:
            raise ContractError("sheet.notice", f"the license header must carry {needle!r}")
    body = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    if EXTERNAL.search(body):
        raise ContractError("sheet", "a sheet is self-contained; it loads nothing from elsewhere")
    style_and_svg = "".join(re.findall(r"<style>.*?</style>|<svg.*?</svg>", body, re.S))
    colored = sorted({c for c in HEX_COLOR.findall(style_and_svg) if not _gray("#" + c)})
    if colored:
        raise ContractError("sheet.color", f"line work and page styles are grays only (C-46); found {colored}")
    spec = spec_of(html)
    expected = render(spec)
    if expected != html:
        raise ContractError("sheet", "the page differs from its embedded spec; render it again instead of editing the HTML")
    summary = variables.validate_table(spec["variables"])
    return {"component": spec["component"], "basis": spec["basis"], "uses_slots": uses_slots(spec), **summary}
