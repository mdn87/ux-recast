"""Style guides: Markdown with front matter, sections from the concept's list, every one optional (C-36 to C-38, C-45).

A guide states its ``basis``. Sections appear in the template's order, each behind its marker
comment, so a reader and a check find the same structure. The template carries no palette or
status vocabulary (C-37). When an accompanying sheet draws structural slots, the guide must keep
its content-behavior section: slots stand in for real content, and the guide says how that content
wraps and overflows instead (C-45).
"""
from importlib import resources
import re

from ux_recast.contracts import ContractError

SCHEMA = "ux-recast/guide@1"
SECTIONS = (("audience", "Audience and principles"), ("color", "Color and status semantics"), ("typography", "Typography"),
            ("spacing", "Spacing and layout"), ("anatomy", "Component anatomy"), ("states", "Interaction states"),
            ("input-feedback", "Input and feedback"), ("accessibility", "Accessibility"), ("motion", "Motion"),
            ("content-behavior", "Content behavior"), ("examples", "Examples and counterexamples"),
            ("open-questions", "Open questions"), ("reasons", "Reasons"))
TITLES = dict(SECTIONS)
ORDER = [key for key, _ in SECTIONS]
MARKER = re.compile(r"^<!-- ux-recast:section ([a-z-]+) -->\n## (.+)$", re.M)
PLACEHOLDER = re.compile(r"\{\{.*?\}\}")


def template():
    return resources.files("ux_recast.docs").joinpath("templates/guide.md").read_text("utf-8")


def front_matter(text):
    if not text.startswith("---\n"):
        raise ContractError("guide", "starts with front matter between --- lines")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ContractError("guide", "front matter is not closed")
    meta = {}
    for line in text[4:end].splitlines():
        if line.strip():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, text[end + 5:]


def render(meta, sections):
    """A guide from ``meta`` (subject, basis, basis_reference, sources, sheets) and ``{section_id: body}``."""
    unknown = sorted(set(sections) - set(ORDER))
    if unknown:
        raise ContractError("guide.sections", f"unknown sections {unknown}; known {ORDER}")
    head = ["---", f"schema: {SCHEMA}"] + [f"{key}: {meta[key]}" for key in ("subject", "basis", "basis_reference", "sources", "sheets")
                                           if meta.get(key)] + ["---", ""]
    if meta.get("title"):
        head += [f"# {meta['title']}", ""]
    if meta.get("intro"):
        head += [meta["intro"].strip(), ""]
    body = []
    for key in ORDER:
        if key in sections:
            body += [f"<!-- ux-recast:section {key} -->", f"## {TITLES[key]}", "", sections[key].strip(), ""]
    return "\n".join(head + body).rstrip() + "\n"


def validate(text, *, sheet_uses_slots=False):
    """Check a guide's front matter, section order and placeholders; returns ``{basis, sections}``."""
    meta, body = front_matter(text)
    if meta.get("schema") != SCHEMA:
        raise ContractError("guide.schema", f"must be {SCHEMA}")
    if meta.get("basis") not in {"observed", "accepted", "proposed"}:
        raise ContractError("guide.basis", "a guide states whether it is observed, accepted or proposed (C-38)")
    if meta["basis"] != "observed" and not meta.get("basis_reference"):
        raise ContractError("guide.basis_reference", f"a {meta['basis']} guide names what it rests on")
    for key in ("subject", "sources"):
        if not meta.get(key):
            raise ContractError(f"guide.{key}", "missing")
    if PLACEHOLDER.search(text):
        raise ContractError("guide", f"unfilled placeholder {PLACEHOLDER.search(text).group(0)[:60]}")
    found = MARKER.findall(body)
    headings = re.findall(r"^## (.+)$", body, re.M)
    if len(headings) != len(found):
        raise ContractError("guide.sections", "every ## section sits behind its ux-recast:section marker")
    ids = []
    for key, title in found:
        if key not in TITLES:
            raise ContractError("guide.sections", f"unknown section {key!r}")
        if TITLES[key] != title.strip():
            raise ContractError(f"guide.sections.{key}", f"heading must read {TITLES[key]!r}")
        ids.append(key)
    if ids != sorted(ids, key=ORDER.index) or len(set(ids)) != len(ids):
        raise ContractError("guide.sections", "sections appear once each, in the template's order")
    if not ids:
        raise ContractError("guide.sections", "a guide has at least one section")
    for match, nxt in zip(MARKER.finditer(body), list(MARKER.finditer(body))[1:] + [None]):
        content = body[match.end():nxt.start() if nxt else len(body)].strip()
        if not content:
            raise ContractError(f"guide.sections.{match.group(1)}", "empty; delete a section rather than leave it blank")
    if sheet_uses_slots and "content-behavior" not in ids:
        raise ContractError("guide.sections.content-behavior",
                            "an accompanying sheet uses slots, so the guide says how real content wraps and overflows (C-45)")
    return {"basis": meta["basis"], "sections": ids}
