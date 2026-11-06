"""Documentation packets: prepare the inputs for a provider, then validate what it returns before writing it (D-07, I-9).

``prepare`` validates the request, hashes every input at its revision, attaches a rendered
measurement when one is given, and writes ``packet.json`` and ``prompt.md`` under
``.ux-review/documentation/<id>/``. Whoever fills the packet (this agent, a fresh-context agent, an
Autowork route) returns a guide in Markdown and one sheet spec in JSON per component. ``record``
renders each spec, validates the guide and the sheets against the request, and only then writes
them to the request's ``out_dir``: ``guide.md``, ``sheets/<component>.html`` and the spec as
``sheets/<component>.json`` (the machine-readable design data, C-49). Review mode is untouched.

A motion presentation is Phase 7, gated on a verified export (C-47, C-48). A request may ask for it
alongside a sheet; the packet records it as deferred and the static sheet is the deliverable.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from ux_recast.contracts import ContractError, validate
from ux_recast.docs import guide, sheet

PACKET_SCHEMA = "ux-recast/documentation-packet@1"
MOTION_DEFERRED = "deferred: Phase 7 opens only after a real export with Chromium and the two renderer defects are fixed (C-47, C-48)"
TEXT_ROLES = {"design", "decision", "product"}


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def _git(project, *args):
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    return done.stdout.strip() if done.returncode == 0 else None


def folder_for(project, packet_id):
    return Path(project) / ".ux-review" / "documentation" / packet_id


def prepare(project, request_path, *, measurement_path=None):
    project = Path(project)
    raw = Path(request_path).read_bytes()
    request = validate("documentation", json.loads(raw))
    packet_id = "doc-" + _sha(json.dumps(request, sort_keys=True).encode())[:12]
    head = _git(project, "rev-parse", "HEAD")
    inputs = []
    for item in request["inputs"]:
        path = project / item["path"]
        if not path.is_file():
            raise ValueError(f"input {item['path']} does not exist under {project}")
        data = path.read_bytes()
        entry = {"path": item["path"], "role": item["role"],
                 "authority": item.get("authority", "reference" if item["role"] == "reference" else "approved"),
                 "sha256": _sha(data), "bytes": len(data),
                 "revision": _git(project, "log", "-1", "--format=%H", "--", item["path"]),
                 "modified": bool(_git(project, "status", "--porcelain", "--", item["path"]))}
        if item["role"] in TEXT_ROLES:
            entry["text"] = data.decode("utf-8")
        inputs.append(entry)
    measurement = None
    if measurement_path:
        measurement = json.loads(Path(measurement_path).read_text(encoding="utf-8"))
        if measurement.get("schema") != "ux-recast/measurement@1":
            raise ValueError("a measurement is the output of 'ux-recast document measure'")
    outputs = dict(request["outputs"])
    packet = {"schema": PACKET_SCHEMA, "request_kind": "documentation", "id": packet_id, "request": request,
              "request_sha256": _sha(raw), "project_revision": head, "inputs": inputs, "measurement": measurement,
              "templates": {"guide": _sha(guide.template().encode()), "sheet": _sha(sheet.template().encode())},
              "outputs": outputs, "dispatch_status": "prepared", "prepared_at": _now()}
    if outputs.get("motion"):
        packet["motion"] = MOTION_DEFERRED
    folder = folder_for(project, packet_id)
    _write(folder / "packet.json", packet)
    _write(folder / "prompt.md", prompt(packet))
    return {"id": packet_id, "folder": str(folder), "outputs": outputs, "inputs": len(inputs),
            "prompt": str(folder / "prompt.md"), "motion": packet.get("motion")}


def prompt(packet):
    """The provider's instructions: what to return and the rules it will be validated against."""
    request = packet["request"]
    wants = [name for name in ("guide", "sheets") if request["outputs"].get(name)]
    lines = [f"# Documentation packet {packet['id']}", "",
             f"Subject: {request['subject']} (project {request['project']}).",
             f"Basis: {request['basis']}" + (f", resting on {request['basis_reference']}." if request.get("basis_reference") else "."), "",
             "Return:"]
    if "guide" in wants:
        lines.append("- `guide.md`, filled from the guide template below. Keep only the sections the product needs, in order, "
                     "each behind its marker. Front matter `basis` must equal the request's basis.")
    if "sheets" in wants:
        lines.append(f"- One sheet spec per component ({', '.join(request['components'])}) as `<component>.json`, "
                     "schema `ux-recast/sheet@1`. ux-recast renders it to HTML; do not write HTML.")
    if packet.get("motion"):
        lines.append(f"- No motion presentation: {packet['motion']}.")
    lines += ["", "Rules the returned files are validated against:",
              "- Never invent a value. Anything the inputs do not establish is `[TBD]` (C-41).",
              "- Every value names its unit and its source: `token`, `css-literal`, `accepted` (file, line, revision, and the "
              "line's text with `{}` where the value sits), `rendered` (part, property, engine, viewport, device pixel ratio, "
              "tolerance, revision; copy these from the measurement below), or `proposed` (the proposal).",
              "- Derived values carry a formula over codes and its result.",
              "- The drawing shows codes, never numbers; its geometry may be formulas over codes. Line work is monochrome.",
              "- Approved inputs are authoritative; a `reference` input is inspiration and never overrides them (C-39).",
              "- When a sheet draws structural slots, the guide keeps its content-behavior section (C-45).",
              "", "Inputs (hashes are checked; read the files at these revisions):"]
    for item in packet["inputs"]:
        lines.append(f"- `{item['path']}` · {item['role']} · {item['authority']} · {item['revision'] or 'untracked'}"
                     + (" · modified in the working tree" if item["modified"] else "") + f" · sha256 {item['sha256'][:12]}")
    if packet.get("measurement"):
        conditions = packet["measurement"]["conditions"]
        lines += ["", f"Measurement: {conditions['engine']} at {conditions['viewport']} @{conditions['device_pixel_ratio']}x, "
                      f"revision {conditions['revision']}, font used {conditions['font_used']}.", "", "```json",
                  json.dumps(packet["measurement"]["values"], indent=1), "```"]
    if "guide" in wants:
        lines += ["", "Guide template:", "", "````markdown", guide.template().rstrip(), "````"]
    return "\n".join(lines) + "\n"


def record(project, packet_id, *, guide_path=None, sheet_paths=()):
    """Validate the returned guide and sheet specs against the packet; write them to ``out_dir``."""
    project = Path(project)
    folder = folder_for(project, packet_id)
    packet = json.loads((folder / "packet.json").read_text(encoding="utf-8"))
    request = packet["request"]
    outputs = request["outputs"]
    if outputs.get("guide") != bool(guide_path):
        raise ContractError("record.guide", "the request " + ("asks for" if outputs.get("guide") else "did not ask for") + " a guide")
    specs = {}
    for path in sheet_paths:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
        specs[spec.get("component")] = spec
    wanted = set(request.get("components", [])) if outputs.get("sheets") else set()
    if set(specs) != wanted:
        raise ContractError("record.sheets", f"expected sheets for {sorted(wanted)}, got {sorted(map(str, specs))}")
    rendered, slots, summaries = {}, False, {}
    for component, spec in specs.items():
        if spec.get("basis") != request["basis"]:
            raise ContractError(f"record.sheets.{component}.basis", f"must equal the request's basis {request['basis']!r}")
        html = sheet.render(spec)
        summaries[component] = sheet.validate(html)
        slots = slots or summaries[component]["uses_slots"]
        rendered[component] = html
    guide_summary = None
    if guide_path:
        text = Path(guide_path).read_text(encoding="utf-8")
        guide_summary = guide.validate(text, sheet_uses_slots=slots)
        if guide_summary["basis"] != request["basis"]:
            raise ContractError("record.guide.basis", f"must equal the request's basis {request['basis']!r}")
    out = project / request["out_dir"]
    written = []
    if guide_path:
        _write(out / "guide.md", text)
        written.append(out / "guide.md")
    for component, html in rendered.items():
        _write(out / "sheets" / f"{component}.html", html)
        _write(out / "sheets" / f"{component}.json", specs[component])
        written += [out / "sheets" / f"{component}.html", out / "sheets" / f"{component}.json"]
    packet.update(dispatch_status="recorded", recorded_at=_now(),
                  written={str(p.relative_to(project)).replace("\\", "/"): _sha(p.read_bytes()) for p in written})
    _write(folder / "packet.json", packet)
    return {"id": packet_id, "guide": guide_summary, "sheets": summaries, "written": sorted(packet["written"])}
