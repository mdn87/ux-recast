"""Evidence archive: keep what a Decision cites after ``.ux-review/`` is gone.

``.ux-review/`` is gitignored, so a Decision that cites a packet there would
point at nothing on a clean checkout. Recording a Decision or Outcome for a run
first copies that run's ``packet.json``, ``receipt.json`` and every source file
the packet hashed (the evidence JSON and its screenshots) into
``.ux-recast/evidence/<run>/``, which the project commits. Each source is checked
against the digest the packet recorded before it is copied. An archive is
write-once: a file already archived with different bytes is refused, never
overwritten. ``manifest.json`` maps every archived file to its digest and origin.
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


def _place(source, target):
    if target.exists():
        if target.read_bytes() != source.read_bytes():
            raise ValueError(f"{target.name}: already archived with different content; the archive is write-once")
        return
    shutil.copyfile(source, target)


def archive(project, session, run_id):
    """Copy a run's packet, receipt and hashed sources into the archive; return their project-relative links."""
    if not RUN_ID.match(run_id):
        raise ValueError(f"run: not a run id: {run_id!r}")
    root = Path(project).resolve()
    folder = packet_folder(root, session, run_id)
    packet_path = folder / "packet.json"
    if not packet_path.is_file():
        raise ValueError(f"run {run_id}: no packet to archive")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    sources = []
    for name, expected in packet.get("sources", {}).items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"source {name}: not a file inside the project")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"source {name}: changed since the packet was prepared")
        sources.append((path, expected))

    target = root / ".ux-recast" / "evidence" / run_id
    (target / "sources").mkdir(parents=True, exist_ok=True)
    files = {"packet.json": packet_path}
    if (folder / "receipt.json").is_file():
        files["receipt.json"] = folder / "receipt.json"
    taken = set()
    origins = {}
    for path, _ in sources:
        name, n = path.name, 1
        while name in taken:
            n += 1
            name = f"{path.stem}-{n}{path.suffix}"
        taken.add(name)
        files[f"sources/{name}"] = path
        origins[f"sources/{name}"] = path.relative_to(root).as_posix()
    for relative, source in files.items():
        _place(source, target / relative)

    manifest = {"schema": "ux-recast/evidence-archive@1", "run": run_id, "files": {
        relative: {"sha256": hashlib.sha256((target / relative).read_bytes()).hexdigest(),
                   **({"origin": origins[relative]} if relative in origins else {})}
        for relative in sorted(files)}}
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    manifest_path = target / "manifest.json"
    if manifest_path.exists() and manifest_path.read_bytes() != manifest_bytes:
        raise ValueError("manifest.json: already archived with different content; the archive is write-once")
    manifest_path.write_bytes(manifest_bytes)
    prefix = target.relative_to(root).as_posix()
    return [f"{prefix}/manifest.json"] + [f"{prefix}/{relative}" for relative in sorted(files)]


def record(project, session, run_id, record):
    """Archive the run's evidence, then append the Decision or Outcome citing it."""
    decisions._check(record)
    for key in ("run", "evidence"):
        if key in record:
            raise ValueError(f"{key}: assigned from the archived run")
    links = archive(project, session, run_id)
    return decisions.append(project, {**record, "run": run_id, "evidence": links})
