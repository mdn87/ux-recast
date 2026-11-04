"""Lessons in two tiers: project lessons and shared lessons.

A project lesson lives at ``.ux-recast/lessons/project/<id>.md`` in the project
that learned it. Promotion copies it into the shared tier (by default the
package's ``lessons/shared/``) so every project's reviews can use it. Promotion
needs support from a second project: at least one ``supported_by`` Outcome from a
project identity other than the lesson's own. Without it, promotion is refused
and logged, unless the user explicitly instructs it, which is logged too.

A project identity is the normalized ``origin`` remote plus the root commit
hash, so a copy of the same repository at another path is the same project.
Support is added through ``add_support``, which computes the supporting
project's identity itself and checks the cited Outcome exists in its
``decisions.jsonl``; ``supported_by`` is never taken on trust.

A lesson moves candidate to project, then shared through promotion; a lesson
that stops holding becomes rejected or superseded with a recorded reason and is
kept, never deleted (C-59). ``set_status`` enforces those moves.

A lesson file is Markdown with a front matter block of ``key: <JSON value>``
lines (valid YAML), then the lesson text. Events (refusals, bypasses and
promotions) are appended to ``.ux-recast/lessons/log.jsonl`` and logged.
"""
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import uuid

from ux_recast.contracts import LESSON_STATUSES as STATUSES, ContractError, validate
from ux_recast.records import decisions

# Moves set_status allows; candidate or project to shared happens only through promote().
TRANSITIONS = {"candidate": {"project", "rejected"}, "project": {"rejected", "superseded"},
               "shared": {"superseded"}, "rejected": set(), "superseded": set()}
LESSON_ID = re.compile(r"^L-[0-9a-f]{8}$")
REFUSAL = "no supporting outcome from a second project identity"
SHARED_DIR = Path(__file__).parents[1] / "lessons" / "shared"
log = logging.getLogger("ux_recast.records")


def _git(project, *args):
    proc = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, encoding="utf-8")
    return proc.stdout.strip() if proc.returncode == 0 else None


def normalize_remote(url):
    url = (url or "").strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    match = re.match(r"^[a-z][a-z0-9+.-]*://(?:[^@/]*@)?([^/:]+)(?::\d+)?/(.*)$", url, re.I) \
        or re.match(r"^(?:[^@/]+@)?([^/:]+):(?!//)(.*)$", url)
    return f"{match.group(1).lower()}/{match.group(2)}" if match else url


def identity(project):
    """Return ``<remote>#<root commit>`` for a git project; refuse anything else."""
    roots = _git(project, "rev-list", "--max-parents=0", "HEAD")
    if not roots:
        raise ValueError(f"{project}: not a git repository with a commit; a project identity needs both")
    remote = normalize_remote(_git(project, "config", "--get", "remote.origin.url"))
    return f"{remote}#{sorted(roots.split())[0]}"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _dump(meta, body):
    try:
        validate("lesson", meta)
    except ContractError as error:
        raise ValueError(str(error)) from error
    head ="".join(f"{key}: {json.dumps(meta[key], ensure_ascii=False, sort_keys=True)}\n" for key in meta)
    return f"---\n{head}---\n\n{body.strip()}\n"


def _load(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[3:]:
        raise ValueError(f"{path.name}: no front matter")
    head, body = text[4:].split("\n---\n", 1)
    meta = {}
    for line in head.splitlines():
        key, _, value = line.partition(": ")
        meta[key] = json.loads(value)
    return meta, body.strip()


def _path(project, lesson_id):
    if not LESSON_ID.match(lesson_id):
        raise ValueError(f"lesson: not a lesson id: {lesson_id!r}")
    path = Path(project) / ".ux-recast" / "lessons" / "project" / f"{lesson_id}.md"
    if not path.is_file():
        raise ValueError(f"lesson {lesson_id}: not found in {project}")
    return path


def _event(project, event, lesson_id, **fields):
    target = Path(project) / ".ux-recast" / "lessons" / "log.jsonl"
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"at": _now(), "event": event, "lesson": lesson_id, **fields}, ensure_ascii=False, sort_keys=True)
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0), 0o644)
    try:
        os.write(fd, (line + "\n").encode("utf-8"))
    finally:
        os.close(fd)


def _write_new(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(text.encode("utf-8"))


def _check_links(project, links):
    """Links name what the lesson rests on: ``{rel: [project-relative path, optionally with #fragment]}``."""
    root = Path(project).resolve()
    checked = {}
    for rel, targets in (links or {}).items():
        targets = [targets] if isinstance(targets, str) else list(targets)
        if not re.match(r"^[a-z][a-z_]*$", rel) or not targets:
            raise ValueError(f"links.{rel}: needs a lowercase name and at least one path")
        for target in targets:
            path = (root / target.split("#", 1)[0]).resolve()
            if "\\" in target or not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f"links.{rel}: {target} is not a file inside the project")
        checked[rel] = targets
    return checked


def create(project, title, body, links=None):
    """Write a new candidate lesson for this project; return its id."""
    if not title.strip() or not body.strip():
        raise ValueError("title and body: required")
    lesson_id = "L-" + uuid.uuid4().hex[:8]
    meta = {"id": lesson_id, "title": title.strip(), "status": "candidate", "identity": identity(project),
            "created_at": _now(), "links": _check_links(project, links), "supported_by": []}
    _write_new(Path(project) / ".ux-recast" / "lessons" / "project" / f"{lesson_id}.md", _dump(meta, body))
    return lesson_id


def read(project, lesson_id):
    meta, body = _load(_path(project, lesson_id))
    return {**meta, "body": body}


def add_support(project, lesson_id, supporter, outcome_id):
    """Cite an Outcome recorded in ``supporter``'s decisions.jsonl as support for the lesson."""
    path = _path(project, lesson_id)
    meta, body = _load(path)
    if not any(r.get("id") == outcome_id and r.get("kind") == "outcome" for r in decisions.read(supporter)):
        raise ValueError(f"outcome {outcome_id}: no such Outcome in {supporter}")
    entry = {"identity": identity(supporter), "outcome": outcome_id}
    if entry not in meta["supported_by"]:
        meta["supported_by"].append(entry)
        path.write_text(_dump(meta, body), encoding="utf-8", newline="\n")
    return meta["supported_by"]


def promote(project, lesson_id, shared_dir=SHARED_DIR, *, instruction=None):
    """Copy a project lesson into the shared tier; refuse without a second project's support."""
    path = _path(project, lesson_id)
    meta, body = _load(path)
    if meta["status"] not in {"candidate", "project"}:
        raise ValueError(f"lesson {lesson_id}: a {meta['status']} lesson cannot be promoted")
    others = sorted({s["identity"] for s in meta["supported_by"]} - {meta["identity"]})
    if not others:
        if not (instruction or "").strip():
            _event(project, "promotion_refused", lesson_id, reason=REFUSAL)
            log.warning("lesson %s: promotion refused: %s", lesson_id, REFUSAL)
            raise ValueError(f"lesson {lesson_id}: promotion refused: {REFUSAL}")
        _event(project, "promotion_by_instruction", lesson_id, instruction=instruction.strip(), reason=REFUSAL)
        log.warning("lesson %s: promoted without a second project identity, by explicit user instruction: %s",
                    lesson_id, instruction.strip())
        meta["promoted_by_instruction"] = instruction.strip()
    meta.update(status="shared", promoted_at=_now())
    target = Path(shared_dir) / f"{lesson_id}.md"
    _write_new(target, _dump(meta, body))
    path.write_text(_dump(meta, body), encoding="utf-8", newline="\n")
    _event(project, "promoted", lesson_id, shared=str(target), supported_by=others)
    return {"lesson": lesson_id, "shared": str(target), "supported_by": others,
            "by_instruction": "promoted_by_instruction" in meta}


def set_status(project, lesson_id, status, *, reason=None, superseded_by=None, shared_dir=SHARED_DIR):
    """Move a lesson along its lifecycle. Rejected and superseded need a reason; the lesson is kept either way."""
    path = _path(project, lesson_id)
    meta, body = _load(path)
    if status not in STATUSES:
        raise ValueError(f"status: {status!r} not in {', '.join(STATUSES)}")
    if status not in TRANSITIONS[meta["status"]]:
        raise ValueError(f"lesson {lesson_id}: cannot move from {meta['status']} to {status}")
    if status in {"rejected", "superseded"}:
        if not (reason or "").strip():
            raise ValueError(f"reason: a {status} lesson records why")
        meta["reason"] = reason.strip()
    if superseded_by is not None:
        if status != "superseded":
            raise ValueError("superseded_by: only a superseded lesson names its replacement")
        meta["superseded_by"] = superseded_by
    previous = meta["status"]
    meta.update(status=status, status_at=_now())
    text = _dump(meta, body)
    path.write_text(text, encoding="utf-8", newline="\n")
    shared = Path(shared_dir) / f"{lesson_id}.md"
    if previous == "shared" and shared.is_file():
        shared.write_text(text, encoding="utf-8", newline="\n")
    _event(project, "status", lesson_id, previous=previous, status=status, **({"reason": meta["reason"]} if "reason" in meta else {}))
    return {"lesson": lesson_id, "previous": previous, "status": status}
