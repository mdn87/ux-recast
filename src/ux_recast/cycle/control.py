"""Session-scoped UX workflow gate. Emits work requests; never launches an agent.

No packages required. State belongs to the selected project, not the user profile.
The agent must honor invoke/allowed; this is workflow control, not a sandbox.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    mode = sub.add_parser("mode")
    mode.add_argument("mode", choices=["off", "once", "session"])
    mode.add_argument("--scope", nargs="+", default=[])
    mode.add_argument("--shared", action="append", default=[], metavar="COMPONENT=FLOW,FLOW")
    cp = sub.add_parser("checkpoint")
    cp.add_argument("--id", required=True, help="Stable coherent batch identifier")
    cp.add_argument("--stage", choices=["plan", "implementation"], required=True)
    cp.add_argument("--affected", nargs="+", required=True, help="Flow or shared-component IDs")
    cp.add_argument("--task", required=True, type=Path)
    # Opt-in snapshot trigger: the manifest, not --id, identifies the reviewed state.
    cp.add_argument("--input", nargs="+", default=[], metavar="PATH", help="Relevant project files to bind")
    cp.add_argument("--config", action="append", default=[], metavar="NAME=IDENTITY")
    cp.add_argument("--origin", choices=["checkpoint", "event", "repair", "reviewer-output"],
                    help="Only a completed coherent checkpoint can request review")
    phase = sub.add_parser("phase")
    phase.add_argument("run_id")
    phase.add_argument("phase", choices=["repair", "verify"])
    phase.add_argument("--config", action="append", default=None, metavar="NAME=IDENTITY")
    finish = sub.add_parser("finish")
    finish.add_argument("run_id")
    finish.add_argument("--result", choices=["verified", "remaining", "unavailable"], required=True)
    finish.add_argument("--report", default="", help="Evidence/report path; no credentials")
    return p


@contextmanager
def locked(path):
    # A persistent lock file avoids deletion races; OS locks release on process exit.
    with path.open("a+b") as f:
        f.seek(0, 2)
        if f.tell() == 0:
            f.write(b"0")
            f.flush()
        f.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            f.seek(0)
            if os.name == "nt":
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f, fcntl.LOCK_UN)


def execute(project, session, args):
    if not session.strip():
        raise ValueError("A session identifier is required; do not reuse one across sessions")
    project = Path(project).resolve(strict=True)
    a = parser().parse_args(args)
    folder = project / ".ux-review"
    folder.mkdir(exist_ok=True)
    key = hashlib.sha256(session.encode()).hexdigest()[:24]
    path = folder / (key + ".json")
    with locked(folder / (key + ".lock")):
        state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "version": 1, "mode": "off", "scope": [], "shared": {}, "runs": [],
        }
        if state.get("version") != 1 or state.get("mode") not in {"off", "once", "session"}:
            raise ValueError("Unknown state version or mode; no review authorized")
        output = dispatch(state, a, project)
        if a.command != "status":
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            temporary.replace(path)
        return {"mode": state["mode"], "scope": state["scope"], **output}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def load_task(path):
    task = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(task, dict):
        raise ValueError("Task must be a JSON object")
    return task


def check_task(task, selected):
    for field in ("flow", "goal", "starting_conditions", "expected_outcome", "device_input", "source"):
        if not isinstance(task.get(field), str) or not task[field].strip():
            raise ValueError("Task requires nonempty " + field)
    if not isinstance(task.get("assumptions"), list):
        raise ValueError("Task requires an assumptions list (may be empty)")
    if not isinstance(task.get("acceptance"), list) or not task["acceptance"] or not all(
            isinstance(item, str) and item.strip() for item in task["acceptance"]):
        raise ValueError("Task requires explicit outcome acceptance criteria")
    if task["flow"] not in selected:
        raise ValueError("Task flow is not in the affected enabled scope")


def input_hashes(project, paths, *, allow_missing=False):
    hashes = {}
    for value in paths:
        path = (project / value).resolve(strict=not allow_missing)
        if not path.is_relative_to(project) or (path.exists() and not path.is_file()):
            raise ValueError("Inputs must be files inside the selected project")
        name = path.relative_to(project).as_posix()
        if name.split("/")[0] == ".ux-review":
            raise ValueError("Review state and reviewer output cannot be trigger inputs")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return hashes


def bound_changes(root, run, config=None):
    manifest = run.get("manifest")
    if not manifest:
        return []
    if config is None and manifest["config"]:
        raise ValueError("Current config identities are required; repeat --config when using findings")
    changed = []
    for name, expected in manifest["inputs"].items():
        try:
            current = input_hashes(root, [name], allow_missing=True)
        except (OSError, ValueError):
            current = {}
        if current != {name: expected}:
            changed.append(name)
    if config is not None and config != manifest["config"]:
        changed.append("config")
    try:
        task_path = next(iter(input_hashes(root, [manifest["task_path"]])))
        current_task = load_task(root / task_path)
    except (OSError, ValueError):
        current_task = None
    if (fingerprint(current_task) != manifest["task_sha256"]
            or fingerprint(run["task"]) != manifest["task_sha256"]):
        changed.append("task")
    return changed


def config_values(items):
    config = {}
    for item in items:
        name, sep, identity = item.partition("=")
        if not sep or not name.strip() or not identity.strip() or name in config:
            raise ValueError("Use distinct --config NAME=IDENTITY values")
        config[name] = identity
    return config


def new_run(state, checkpoint, task, **binding):
    # One task per claim; shared changes may need several flow claims.
    run = {"run_id": uuid.uuid4().hex[:12], "checkpoint": checkpoint,
           "task": task, "status": "active", "phase": "review",
           "budget": {"review_passes": 1, "repair_batches": 1, "verification_passes": 1,
                      "max_actionable_findings": 5}, **binding}
    state["runs"].append(run)
    return {"invoke": True, **run,
            "instruction": "Read ux-review/SKILL.md; use the saved task as the acceptance contract"}


def snapshot_checkpoint(state, a, project, selected, skip):
    if not a.origin or not a.input:
        raise ValueError("Snapshot checkpoints require --origin and at least one --input")
    if a.origin == "reviewer-output":
        return skip("reviewer output is not a trigger origin")
    task_path = next(iter(input_hashes(project, [a.task])))
    task = load_task(project / task_path)
    check_task(task, selected)
    config = config_values(a.config)
    manifest = {"flow": task["flow"], "stage": a.stage, "task_sha256": fingerprint(task),
                "task_path": task_path, "inputs": input_hashes(project, a.input, allow_missing=True), "config": config}
    key = fingerprint(manifest)
    current = next((r for r in state["runs"] if r["status"] == "active"), None)
    if current:
        if a.origin == "repair" and current.get("manifest", {}).get("flow") == task["flow"]:
            if current["phase"] != "repair":
                return skip("claim the repair phase before recording repaired inputs")
            original = current["manifest"]
            if any(manifest[field] != original[field] for field in ("stage", "task_sha256", "task_path", "config")):
                raise ValueError("Repair must preserve the original task contract and stage")
            # Repaired state belongs to this cycle's verification, not to a new review.
            if key not in current["repair_manifests"]:
                current["repair_manifests"].append(key)
            current["repair_inputs"] = sorted(set(current.get("repair_inputs", original["inputs"]))
                                              | set(manifest["inputs"]))
            return skip("repair stays within the active cycle budget")
        return skip("finish the active bounded cycle first")
    if a.origin != "checkpoint":
        return skip("only completed coherent checkpoints request review")
    previous = next((r for r in state["runs"] if r.get("manifest_sha256") == key
                     or key in r.get("repair_manifests", [])), None)
    if previous:
        return skip("snapshot previously %s in run %s; renamed checkpoints do not restart a cycle"
                    % (previous["status"], previous["run_id"]))
    return new_run(state, [a.id, a.stage, task["flow"]], task,
                   manifest=manifest, manifest_sha256=key, repair_manifests=[])


def dispatch(state, a, project):
    if a.command == "status":
        return dict(state)
    if a.command == "mode":
        if a.mode != "off" and not a.scope:
            raise ValueError("Enabled review requires explicit flow scope")
        shared = {}
        for mapping in a.shared:
            component, sep, flows = mapping.partition("=")
            if not sep or not component or not flows or any(not f for f in flows.split(",")):
                raise ValueError("Use --shared COMPONENT=FLOW,FLOW")
            shared[component] = flows.split(",")
        for run in state["runs"]:
            if run["status"] == "active":
                run["status"] = "cancelled"
        state.update(mode=a.mode, scope=a.scope, shared=shared)
        return {"message": "UX review " + a.mode + "; ordinary tests are unchanged"}
    if a.command == "checkpoint":
        def skip(reason):
            return {"invoke": False, "reason": reason}
        if state["mode"] == "off":
            return skip("off")
        affected = set(a.affected)
        for item in a.affected:
            affected.update(state["shared"].get(item, []))
        selected = affected.intersection(state["scope"])
        if not selected:
            return skip("outside scope")
        if a.origin or a.input or a.config:
            return snapshot_checkpoint(state, a, project, selected, skip)
        if any(r["status"] == "active" for r in state["runs"]):
            return skip("finish the active bounded cycle first")
        task = load_task(a.task)
        checkpoint = [a.id, a.stage, task.get("flow")]
        if any(r["checkpoint"] == checkpoint for r in state["runs"]):
            return skip("checkpoint already reviewed; do not restart an exhausted cycle")
        check_task(task, selected)
        return new_run(state, checkpoint, task)
    run = next((r for r in state["runs"] if r["run_id"] == a.run_id), None)
    if run is None:
        raise ValueError("Unknown review run")
    if state["mode"] == "off" or run["status"] != "active":
        return {"allowed": False, "reason": "review stopped or completed"}
    if a.command == "phase":
        allowed = (run["phase"], a.phase) in {("review", "repair"), ("review", "verify"), ("repair", "verify")}
        if allowed:
            if run.get("manifest") and a.phase == "repair":
                config = config_values(a.config) if a.config is not None else None
                if bound_changes(project, run, config):
                    raise ValueError("Bound checkpoint inputs changed; stale findings cannot authorize repair")
            if run.get("manifest") and run["phase"] == "repair" and a.phase == "verify":
                # The normal phase transition seals repaired inputs without another caller event.
                repaired = dict(run["manifest"])
                if fingerprint(load_task(project / repaired["task_path"])) != repaired["task_sha256"]:
                    raise ValueError("Repair must preserve the original task contract")
                repaired["inputs"] = input_hashes(project, run.get("repair_inputs", repaired["inputs"]),
                                                  allow_missing=True)
                key = fingerprint(repaired)
                if key not in run["repair_manifests"]:
                    run["repair_manifests"].append(key)
            run["phase"] = a.phase
        return {"allowed": allowed, "run_id": a.run_id, "phase": run["phase"],
                "reason": "one repair batch and one verification pass per cycle"}
    if a.result == "verified" and run["phase"] != "verify":
        raise ValueError("Cannot record verified before the verification phase")
    run.update(status=a.result, report=a.report)
    if state["mode"] == "once":
        state["mode"] = "off"
    return {"allowed": True, "run_id": a.run_id, "result": a.result,
            "message": "Recorded agent report; not independent proof of verification"}


def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--session", required=True)
    known, args = p.parse_known_args()
    try:
        print(json.dumps(execute(known.project, known.session, args), indent=2))
    except (ValueError, OSError) as exc:
        print(json.dumps({"invoke": False, "allowed": False, "error": str(exc)}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
