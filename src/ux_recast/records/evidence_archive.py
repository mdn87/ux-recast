"""Evidence archive: keep what a Decision cites after ``.ux-review/`` is gone.

``.ux-review/`` is gitignored, so a Decision that cites a packet there would
point at nothing on a clean checkout. Recording a Decision or Outcome for a run
first copies that run's ``packet.json``, ``receipt.json`` and every source file
the packet hashed (the evidence JSON and its before screenshots) into
``.ux-recast/evidence/<run>/``, which the project commits. Each source is checked
against the digest the packet recorded before it is copied. Files the record
cites beyond the packet (after screenshots, a diff, test output) are named in
``cited`` and kept under ``cited/`` at their project-relative path. An archive
is write-once per file: a file already archived with different bytes is refused,
never overwritten, and a later record may only add files. ``manifest.json`` maps
every archived file to its digest and origin.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil

from ux_recast.providers.lugos_autowork import digest
from ux_recast.records import decisions

RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def packet_folder(project, session, run_id):
    return Path(project).resolve() / ".ux-review" / "packets" / (digest(session.encode())[:24] + "-" + run_id)


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(project, session, run_id, cited=()):
    """Copy a run's packet, receipt, hashed sources and cited files into the archive; return the links this call archived."""
    if not RUN_ID.match(run_id):
        raise ValueError(f"run: not a run id: {run_id!r}")
    root = Path(project).resolve()
    folder = packet_folder(root, session, run_id)
    packet_path = folder / "packet.json"
    if not packet_path.is_file():
        raise ValueError(f"run {run_id}: no packet to archive")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    files = {"packet.json": (packet_path, None)}
    if (folder / "receipt.json").is_file():
        files["receipt.json"] = (folder / "receipt.json", None)
    taken = set()
    for name, expected in packet.get("sources", {}).items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"source {name}: not a file inside the project")
        if _sha(path) != expected:
            raise ValueError(f"source {name}: changed since the packet was prepared")
        stem, n = path.name, 1
        while stem in taken:
            n += 1
            stem = f"{path.stem}-{n}{path.suffix}"
        taken.add(stem)
        files[f"sources/{stem}"] = (path, path.relative_to(root).as_posix())
    archive_root = root / ".ux-recast" / "evidence"
    for name in cited:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or path.is_relative_to(archive_root):
            raise ValueError(f"cited {name}: not a file inside the project and outside the archive")
        origin = path.relative_to(root).as_posix()
        files["cited/" + origin] = (path, origin)

    target = archive_root / run_id
    entries = {relative: {"sha256": _sha(source), **({"origin": origin} if origin else {})}
               for relative, (source, origin) in files.items()}
    manifest_path = target / "manifest.json"
    known = json.loads(manifest_path.read_text(encoding="utf-8"))["files"] if manifest_path.exists() else {}
    for relative, entry in entries.items():
        on_disk = target / relative
        if (relative in known and known[relative] != entry) or (on_disk.exists() and _sha(on_disk) != entry["sha256"]):
            raise ValueError(f"{relative}: already archived with different content; the archive is write-once")
    for relative, (source, _) in files.items():
        on_disk = target / relative
        if not on_disk.exists():
            on_disk.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, on_disk)
    manifest = {"schema": "ux-recast/evidence-archive@1", "run": run_id, "files": {**known, **entries}}
    manifest_path.write_bytes((json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    prefix = target.relative_to(root).as_posix()
    return [f"{prefix}/manifest.json"] + [f"{prefix}/{relative}" for relative in sorted(files)]


def record(project, session, run_id, record, cited=()):
    """Archive the run's evidence and the files it cites, then append the Decision or Outcome citing them."""
    decisions._check(record)
    for key in ("run", "evidence"):
        if key in record:
            raise ValueError(f"{key}: assigned from the archived run")
    links = archive(project, session, run_id, cited)
    return decisions.append(project, {**record, "run": run_id, "evidence": links})
