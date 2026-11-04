"""Decisions and Outcomes: ``.ux-recast/decisions.jsonl``, append-only.

One JSON object per line. Acceptance is a user Decision or an observed Outcome
(D-09), so every record has ``kind`` (``decision`` or ``outcome``) and a
``summary``; ux-recast adds ``id`` and ``recorded_at``. Other keys pass through.

Writers serialize on the cycle lock (``cycle.control.locked``) over
``.ux-review/decisions.lock``. The OS releases that lock when a holder dies, so
the lock itself never goes stale; what a killed writer can leave is a torn last
line. The holder therefore writes ``.ux-review/decisions.inflight`` before
appending and removes it after. The next writer that finds it logs the stale
holder, moves any torn tail to ``.ux-recast/decisions.torn`` and truncates the
log back to its last complete line before appending.
"""
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import uuid

from ux_recast.cycle.control import locked

KINDS = {"decision", "outcome"}
log = logging.getLogger("ux_recast.records")


def _paths(project):
    project = Path(project)
    records, cycle = project / ".ux-recast", project / ".ux-review"
    return {
        "log": records / "decisions.jsonl",
        "torn": records / "decisions.torn",
        "lock": cycle / "decisions.lock",
        "inflight": cycle / "decisions.inflight",
    }


def _check(record):
    if not isinstance(record, dict):
        raise ValueError("record: must be an object")
    if record.get("kind") not in KINDS:
        raise ValueError(f"kind: must be one of {', '.join(sorted(KINDS))}")
    if not isinstance(record.get("summary"), str) or not record["summary"].strip():
        raise ValueError("summary: required")
    for key in ("id", "recorded_at"):
        if key in record:
            raise ValueError(f"{key}: assigned by ux-recast")


def _recover(paths):
    """Repair what a writer killed while holding the lock left behind."""
    holder = paths["inflight"].read_text(encoding="utf-8", errors="replace").strip() or "unknown"
    log.warning("recovered stale decisions lock left by %s", holder)
    target = paths["log"]
    if target.exists():
        data = target.read_bytes()
        keep = data.rfind(b"\n") + 1
        if keep < len(data):
            with open(paths["torn"], "ab") as torn:
                torn.write(data[keep:] + b"\n")
            with open(target, "r+b") as handle:
                handle.truncate(keep)
            log.warning("moved a %d-byte torn decisions line to %s", len(data) - keep, paths["torn"].name)
    paths["inflight"].unlink()


def _write_all(fd, data):
    view = memoryview(data)
    while view:
        view = view[os.write(fd, view):]


def append(project, record):
    """Append one record and return it with its assigned ``id`` and ``recorded_at``."""
    _check(record)
    stored = {"id": uuid.uuid4().hex[:12], "recorded_at": datetime.now(timezone.utc).isoformat(), **record}
    line = (json.dumps(stored, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    paths = _paths(project)
    paths["log"].parent.mkdir(exist_ok=True)
    paths["lock"].parent.mkdir(exist_ok=True)
    with locked(paths["lock"]):
        if paths["inflight"].exists():
            _recover(paths)
        paths["inflight"].write_text(f"pid {os.getpid()}\n", encoding="utf-8")
        fd = os.open(paths["log"], os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0), 0o644)
        try:
            _write_all(fd, line)
            os.fsync(fd)
        finally:
            os.close(fd)
        paths["inflight"].unlink()
    return stored


def read(project):
    """Return every complete record in order; an empty list when there is no log yet."""
    target = _paths(project)["log"]
    if not target.exists():
        return []
    with open(target, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.endswith("\n")]
