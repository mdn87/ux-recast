"""One findings-driven review -> repair -> verify cycle on the contact-request fixture (plan slice S1.8).

The cycle runs the Lugos-ported controller and packet helper from the installed
``ux_recast`` package only. Every file open in this process and in the test
subprocesses is logged through ``sys.addaudithook``; the run fails if anything
under a Lugos checkout was read. The reviewer is the agent driving the script
(``local_agent`` provider): the script never writes findings or a repair itself.

Phases, in order:

    baseline  copy the fixture into .work/<cycle>/ with the defective page as
              index.html, run the seven flow tests against it, bundle the
              observations and up to five screenshots as evidence, open the
              controller cycle, prepare and claim the packet, write the
              findings template.
    record    validate and record the agent's findings; move to the repair phase.
    repair    install the agent-authored page as index.html, seal the repaired
              input, move to the verification phase, rerun the flow tests.
    finish    record the controller result, consume the receipt, copy the
              sanitized evidence into docs/evidence/<cycle>/.
    lesson    (S2.5) give the scratch project its own git identity, record the
              Outcome with the after screenshots, diff, findings and passing
              test output archived, write the agent-authored project lesson
              linking them, commit, and check every link from a clean clone.
    compare   (S2.6) record the product comparison: criteria, conditions,
              verification, evidence and effort from the log; claims,
              dispositions, limitations and the decision from --comparison.

Usage: python scripts/fixture_cycle.py <phase> [--cycle fixture-cycle-001] [--findings F] [--page P] [--lesson L.json] [--comparison C.json]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "fixtures" / "contact-request"
LUGOS = Path(os.environ.get("UX_RECAST_LUGOS_CHECKOUT", REPO.parent / "lugos")).resolve()
SESSION = "fixture-cycle"
HOOK_DIR = REPO / "scripts" / "_audit_hook"

# ---------------------------------------------------------------- access log

def install_audit_hook(log_path):
    """Log every open() this process makes; the same hook runs in subprocesses via sitecustomize."""
    HOOK_DIR.mkdir(exist_ok=True)
    (HOOK_DIR / "sitecustomize.py").write_text(HOOK_SOURCE, encoding="utf-8")
    os.environ["UX_RECAST_ACCESS_LOG"] = str(log_path)
    os.environ["PYTHONPATH"] = os.pathsep.join(p for p in (str(HOOK_DIR), os.environ.get("PYTHONPATH", "")) if p)
    namespace = {}
    exec(HOOK_SOURCE, namespace)  # the same hook in this process


HOOK_SOURCE = '''
import os, sys
LOG = os.environ.get("UX_RECAST_ACCESS_LOG")
if LOG:
    _fd = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    _busy = [False]
    def _hook(event, args):
        if event != "open" or _busy[0] or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        _busy[0] = True
        try:
            path = os.fsdecode(args[0])
            if path != LOG:
                os.write(_fd, (path + "\\n").encode("utf-8", "replace"))
        except Exception:
            pass
        finally:
            _busy[0] = False
    sys.addaudithook(_hook)
'''


def lugos_reads(log_path):
    seen = sorted({line.strip() for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()})
    inside = [p for p in seen if _under(Path(p), LUGOS)]
    return seen, inside


def _under(path, root):
    try:
        Path(path).resolve().relative_to(root)
        return True
    except (ValueError, OSError):
        return False

# ---------------------------------------------------------------- helpers

def paths(cycle):
    work = REPO / ".work" / cycle
    return {"work": work, "evidence": work / "evidence", "log": work / "cycle.json",
            "access": work / "access-log.txt", "out": REPO / "docs" / "evidence" / cycle}


def control(work, argv):
    from ux_recast.cycle.control import execute
    return execute(work, SESSION, argv)


def run_flow_tests(work, page, evidence_dir):
    env = dict(os.environ, DEMO_PAGE=page, DEMO_EVIDENCE_DIR=str(evidence_dir), PYTHONIOENCODING="utf-8")
    started = time.time()
    proc = subprocess.run([sys.executable, str(work / "test_flow.py"), "-v"], cwd=str(work),
                          capture_output=True, text=True, encoding="utf-8", env=env)
    text = proc.stdout + proc.stderr
    outcomes = dict(re.findall(r"^(test_\w+) \(.*?\) \.\.\. (ok|FAIL|ERROR)$", text, re.M))
    return {"page": page, "returncode": proc.returncode, "seconds": round(time.time() - started, 1),
            "outcomes": outcomes, "output": text}


def bundle_evidence(work, run_dir, outcomes):
    """Observations from every test, screenshots from failing tests first, within the packet caps."""
    observations = []
    for name in sorted(outcomes):
        obs_file = run_dir / f"{name}.json"
        steps = json.loads(obs_file.read_text(encoding="utf-8")) if obs_file.exists() else []
        for step in steps:
            step = dict(step)
            step["visible_text"] = step.get("visible_text", "")[:600]
            observations.append({"test": name, "outcome": outcomes[name], **step})
    failing = [n for n, o in outcomes.items() if o != "ok"]
    shots = []
    for name in failing + [n for n in outcomes if n not in failing]:
        for step in observations:
            if step["test"] == name and (run_dir / step["screenshot"]).exists() and step["screenshot"] not in shots:
                shots.append(step["screenshot"])
    shots = shots[:5]
    evidence = {"observations": observations,
                "screenshots": [str(Path(run_dir / s).relative_to(work)).replace("\\", "/") for s in shots],
                "coverage": {"tests": outcomes, "failing": failing,
                             "note": "Observations are Playwright captures from the fixture's own flow tests "
                                     "run against the defective page; visible_text is truncated to 600 chars."}}
    raw = json.dumps(evidence, ensure_ascii=False).encode("utf-8")
    while len(raw) > 60000 and evidence["observations"]:
        for step in evidence["observations"]:
            step["visible_text"] = step["visible_text"][:200]
        evidence["observations"] = evidence["observations"][: max(1, len(evidence["observations"]) * 3 // 4)]
        raw = json.dumps(evidence, ensure_ascii=False).encode("utf-8")
    path = work / "evidence.json"
    path.write_bytes(raw)
    return path, evidence

# ---------------------------------------------------------------- phases

def baseline(a):
    p = paths(a.cycle)
    if p["work"].exists():
        rmtree(p["work"])
    p["evidence"].mkdir(parents=True)
    install_audit_hook(p["access"])
    for name in ("task.json", "plan.txt", "test_flow.py", "index.before.html"):
        shutil.copy2(FIXTURE / name, p["work"] / name)
    shutil.copy2(FIXTURE / "index.before.html", p["work"] / "index.html")
    before = run_flow_tests(p["work"], "index.html", p["evidence"] / "before")
    (p["evidence"] / "before-tests.txt").write_text(before["output"], encoding="utf-8")
    evidence_path, evidence = bundle_evidence(p["work"], p["evidence"] / "before", before["outcomes"])

    control(p["work"], ["mode", "once", "--scope", "contact-request"])
    opened = control(p["work"], ["checkpoint", "--id", a.cycle, "--stage", "implementation",
                                 "--affected", "contact-request", "--task", "task.json",
                                 "--input", "index.html", "--origin", "checkpoint"])
    if not opened.get("invoke"):
        raise SystemExit(f"controller did not open a cycle: {opened}")
    from ux_recast.providers import local_agent
    prepared = local_agent.prepare(p["work"], SESSION, opened["run_id"], evidence_path)
    log = {"cycle": a.cycle, "session": SESSION, "run_id": opened["run_id"],
           "before": {k: v for k, v in before.items() if k != "output"},
           "evidence": {"observations": len(evidence["observations"]), "screenshots": evidence["screenshots"],
                        "bytes": evidence_path.stat().st_size},
           "packet": {"task_sha256": prepared["packet"]["task_sha256"], "rubric_sha256": prepared["packet"]["rubric_sha256"],
                      "request_chars": prepared["request_chars"], "modalities": prepared["packet"]["request"]["input_modalities"]},
           "findings_template": prepared["findings_template"], "phases": ["baseline"]}
    p["log"].write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps({k: log[k] for k in ("run_id", "before", "evidence", "packet", "findings_template")}, indent=2))


def record(a):
    p = paths(a.cycle)
    log = json.loads(p["log"].read_text(encoding="utf-8"))
    install_audit_hook(p["access"])
    from ux_recast.providers import local_agent, lugos_autowork
    receipt = local_agent.record(p["work"], SESSION, log["run_id"], a.findings)
    applicable = lugos_autowork.consume(p["work"], SESSION, log["run_id"])
    phase = control(p["work"], ["phase", log["run_id"], "repair"])
    shutil.copy2(a.findings, p["evidence"] / "findings.json")
    log.update(receipt=receipt, consume_before_repair=applicable, repair_phase=phase)
    log["phases"].append("record")
    p["log"].write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps({"receipt": receipt, "consume": applicable, "phase": phase}, indent=2))


def repair(a):
    p = paths(a.cycle)
    log = json.loads(p["log"].read_text(encoding="utf-8"))
    install_audit_hook(p["access"])
    if not log["repair_phase"].get("allowed"):
        raise SystemExit("repair phase was not granted")
    page = Path(a.page).read_text(encoding="utf-8")
    (p["work"] / "index.html").write_text(page, encoding="utf-8")
    shutil.copy2(a.page, p["evidence"] / "index.repaired.html")
    diff = subprocess.run(["git", "diff", "--no-index", "--", str(p["work"] / "index.before.html"), str(p["work"] / "index.html")],
                          capture_output=True, text=True, encoding="utf-8")
    (p["evidence"] / "repair.diff").write_text(diff.stdout, encoding="utf-8")
    sealed = control(p["work"], ["checkpoint", "--id", a.cycle, "--stage", "implementation",
                                 "--affected", "contact-request", "--task", "task.json",
                                 "--input", "index.html", "--origin", "repair"])
    verify = control(p["work"], ["phase", log["run_id"], "verify"])
    if not verify.get("allowed"):
        raise SystemExit(f"verification phase refused: {verify}")
    after = run_flow_tests(p["work"], "index.html", p["evidence"] / "after")
    (p["evidence"] / "after-tests.txt").write_text(after["output"], encoding="utf-8")
    oracle = run_flow_tests(FIXTURE, "index.html", p["evidence"] / "oracle")
    (p["evidence"] / "oracle-tests.txt").write_text(oracle["output"], encoding="utf-8")
    log.update(repair_seal=sealed, verify_phase=verify,
               after={k: v for k, v in after.items() if k != "output"},
               oracle={k: v for k, v in oracle.items() if k != "output"})
    log["phases"].append("repair")
    p["log"].write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps({"sealed": sealed, "verify": verify, "after": log["after"], "oracle": log["oracle"]}, indent=2))


def finish(a):
    p = paths(a.cycle)
    log = json.loads(p["log"].read_text(encoding="utf-8"))
    install_audit_hook(p["access"])
    from ux_recast.providers import lugos_autowork
    if "finish" not in log:  # the controller accepts one finish per run; a rerun only re-exports
        result = "verified" if log["after"]["returncode"] == 0 else "remaining"
        report = f"docs/evidence/{a.cycle}/cycle.json"
        finished = control(p["work"], ["finish", log["run_id"], "--result", result, "--report", report])
        stale = lugos_autowork.consume(p["work"], SESSION, log["run_id"])
        log.update(finish=finished, consume_after_repair=stale, final_state=control(p["work"], ["status"]))
        log["phases"].append("finish")
    seen, inside = lugos_reads(p["access"])
    log["access"] = {"files_opened": len(seen), "lugos_checkout": str(LUGOS), "lugos_reads": inside}
    finished, stale = log["finish"], log["consume_after_repair"]
    p["log"].write_text(json.dumps(log, indent=2), encoding="utf-8")
    export(p, log)
    if inside:
        raise SystemExit(f"{len(inside)} reads under the Lugos checkout; the cycle is not independent")
    print(json.dumps({"finish": finished, "consume_after_repair": stale, "files_opened": len(seen), "lugos_reads": inside}, indent=2))


def rmtree(path):
    """Remove a tree, including git's read-only object files on Windows."""
    def retry(func, target, _):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, **({"onexc": retry} if sys.version_info >= (3, 12) else {"onerror": retry}))


GIT = ["git", "-c", "user.name=fixture-cycle", "-c", "user.email=fixture-cycle@example.invalid",
       "-c", "core.autocrlf=false", "-c", "init.defaultBranch=main"]


def lesson(a):
    """Record the Outcome, archive what it rests on, write the linked lesson, and prove it on a clean clone."""
    p = paths(a.cycle)
    log = json.loads(p["log"].read_text(encoding="utf-8"))
    if "finish" not in log or log["after"]["returncode"] != 0:
        raise SystemExit("lesson needs a finished cycle whose after-run passed")
    if "lesson" in log:
        raise SystemExit("this cycle already has its lesson; rerun from baseline for a new one")
    install_audit_hook(p["access"])
    spec = json.loads(Path(a.lesson).read_text(encoding="utf-8"))
    work, run = p["work"], log["run_id"]
    from ux_recast.records import decisions, evidence_archive, lessons
    if not (work / ".git").exists():
        (work / ".gitignore").write_text(".ux-review/\n", encoding="utf-8", newline="\n")
        subprocess.run(GIT + ["init", "-q"], cwd=work, check=True)
        subprocess.run(GIT + ["add", "-A"], cwd=work, check=True)
        subprocess.run(GIT + ["commit", "-q", "-m", "fixture project before the lesson"], cwd=work, check=True)

    test = spec["test"]
    if log["after"]["outcomes"].get(test) != "ok" or log["before"]["outcomes"].get(test) == "ok":
        raise SystemExit(f"{test}: the lesson's test must fail before and pass after")
    findings = json.loads((p["evidence"] / "findings.json").read_text(encoding="utf-8"))
    if spec["finding"] not in {f["id"] for f in findings["findings"]}:
        raise SystemExit(f"{spec['finding']}: not a recorded finding")
    before_shots = [s for s in log["evidence"]["screenshots"] if Path(s).name.startswith(test)]
    after_shots = sorted(f"evidence/after/{f.name}" for f in (p["evidence"] / "after").glob(f"{test}-*.png"))
    if not before_shots or not after_shots:
        raise SystemExit(f"{test}: needs before and after screenshots")
    cited = ["evidence/findings.json", "evidence/repair.diff", "evidence/after-tests.txt", *after_shots]
    outcome = evidence_archive.record(work, SESSION, run, {
        "kind": "outcome", "summary": f"After the repair the seven flow tests pass; {test} failed before it.",
        "result": log["finish"].get("result", "verified"), "tests": log["after"]["outcomes"]}, cited=cited)
    archived = f".ux-recast/evidence/{run}"
    links = {
        "finding": [f"{archived}/cited/evidence/findings.json#{spec['finding']}"],
        "diff": [f"{archived}/cited/evidence/repair.diff"],
        "before": [f"{archived}/sources/{Path(s).name}" for s in before_shots],
        "after": [f"{archived}/cited/{s}" for s in after_shots],
        "test": [f"{archived}/cited/evidence/after-tests.txt#{test}"],
        "outcome": [f".ux-recast/decisions.jsonl#{outcome['id']}"],
    }
    lesson_id = lessons.create(work, spec["title"], spec["body"], links)
    subprocess.run(GIT + ["add", "-A"], cwd=work, check=True)
    subprocess.run(GIT + ["commit", "-q", "-m", f"record outcome {outcome['id']} and lesson {lesson_id}"], cwd=work, check=True)

    clone = work.parent / f"{a.cycle}-clone"
    if clone.exists():
        rmtree(clone)
    subprocess.run(GIT + ["clone", "-q", str(work), str(clone)], check=True)
    cloned = lessons.read(clone, lesson_id)
    manifest = json.loads((clone / archived / "manifest.json").read_text(encoding="utf-8"))["files"]
    checks = {}
    for rel, targets in cloned["links"].items():
        for target in targets:
            name = target.split("#", 1)[0]
            path = clone / name
            ok = path.is_file()
            if ok and name.startswith(archived + "/"):
                ok = hashlib.sha256(path.read_bytes()).hexdigest() == manifest[name[len(archived) + 1:]]["sha256"]
            checks[target] = ok
    [cloned_outcome] = [r for r in decisions.read(clone) if r["id"] == outcome["id"]]
    for link in cloned_outcome["evidence"]:
        checks.setdefault(link, (clone / link).is_file())
    log["lesson"] = {"id": lesson_id, "outcome": outcome["id"], "identity": cloned["identity"], "links": cloned["links"],
                     "clean_clone": {"ux_review_present": (clone / ".ux-review").exists(), "checks": checks}}
    log["phases"].append("lesson")
    rmtree(clone)
    export(p, log)
    out = p["out"] / "ux-recast"
    if out.exists():
        rmtree(out)
    for src in (work / ".ux-recast").rglob("*"):
        if src.is_file():
            dst = out / src.relative_to(work / ".ux-recast")
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix in {".json", ".jsonl", ".md", ".txt", ".diff", ".html"}:
                dst.write_text(scrub(src.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
            else:
                shutil.copy2(src, dst)
    leftovers = [str(n) for n in out.rglob("*") if n.is_file() and n.suffix != ".png" and re.search(r"Users|Matt", n.read_text(encoding="utf-8"))]
    failed = [k for k, ok in checks.items() if not ok]
    if leftovers or failed or log["lesson"]["clean_clone"]["ux_review_present"]:
        raise SystemExit(f"lesson evidence incomplete: leftovers={leftovers} failed_links={failed}")
    p["log"].write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(json.dumps(log["lesson"], indent=2))


def compare(a):
    """Record the product comparison for this cycle (S2.6): the agent supplies the judgement, the log the rest."""
    p = paths(a.cycle)
    log = json.loads(p["log"].read_text(encoding="utf-8"))
    if "lesson" not in log:
        raise SystemExit("compare runs after the lesson phase")
    if "comparison" in log:
        raise SystemExit("this cycle already has its comparison; rerun from baseline for a new one")
    install_audit_hook(p["access"])
    spec = json.loads(Path(a.comparison).read_text(encoding="utf-8"))
    from ux_recast.records import comparisons
    run = log["final_state"]["runs"][-1]
    before, after = log["before"]["outcomes"], log["after"]["outcomes"]
    failure_paths = ["test_invalid_email_preserves_work_and_can_complete", "test_keyboard_validation_recovery",
                     "test_slow_send_can_cancel_without_losing_work", "test_temporary_failure_allows_retry",
                     "test_small_touch_viewport_recovery"]
    record = {
        "schema": "ux-recast/comparison@2", "kind": "product", "task": run["task"]["flow"],
        "baseline": "index.before.html, the fixture's defective page",
        "candidate": "index.repaired.html, the agent-authored repair applied in this cycle",
        "criteria": {"frozen_at": f"checkpoint of run {log['run_id']}: task.json sha256 {run['manifest']['task_sha256']}, "
                                  "bound by the controller before the review",
                     "items": run["task"]["acceptance"]},
        "conditions": {"content": run["task"]["starting_conditions"], "viewports": ["1100x900", "375x812 mobile with touch"],
                       "revision_before": f"index.html sha256 {run['manifest']['inputs']['index.html']}",
                       "revision_after": f"repair manifest {run['repair_manifests'][-1]}",
                       "notes": "Both sides ran the fixture's seven Playwright flow tests in one session, Chromium."},
        "before": {"flow": "the seven flow tests on the defective page", "evidence": ["before-tests.txt", "evidence.json"]},
        "after": {"flow": "the same seven flow tests on the repaired page", "evidence": ["after-tests.txt", "oracle-tests.txt"]},
        "structural_changes": spec["structural_changes"], "improvements": spec["improvements"],
        "findings_disposition": spec["findings_disposition"],
        "verification": {"checks": [{"name": name, "before": before.get(name, "absent"), "after": after[name]} for name in sorted(after)],
                         "failure_paths": [name for name in failure_paths if after.get(name) == "ok"]},
        "assumptions": run["task"].get("assumptions", []),
        "evidence": ["before-tests.txt", "after-tests.txt", "oracle-tests.txt", "findings.json", "repair.diff",
                     "screenshots/test_invalid_email_preserves_work_and_can_complete-rejected.png",
                     f"ux-recast/evidence/{log['run_id']}/manifest.json", f"ux-recast/lessons/project/{log['lesson']['id']}.md"],
        "limitations": spec["limitations"],
        "effort": comparisons.effort_from_cycle(log, spec["findings_disposition"]),
        "decision": spec["decision"], "decided_by": spec["decided_by"], "decided_at": spec["decided_at"],
        "decision_note": spec["decision_note"],
    }
    stored = comparisons.append(p["work"], record)
    log["comparison"] = {"id": stored["id"], "decision": stored["decision"], "effort": stored["effort"]}
    log["phases"].append("compare")
    export(p, log)
    out = p["out"]
    (out / "comparison.json").write_text(scrub(json.dumps(stored, indent=2, ensure_ascii=False)) + "\n", encoding="utf-8", newline="\n")
    target = out / "ux-recast" / "comparisons.jsonl"
    target.write_text(scrub((p["work"] / ".ux-recast" / "comparisons.jsonl").read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    p["log"].write_text(json.dumps(log, indent=2), encoding="utf-8")
    (out / "cycle.json").write_text(scrub(json.dumps(log, indent=2)), encoding="utf-8", newline="\n")
    print(json.dumps(log["comparison"], indent=2))


def export(p, log):
    """Copy the committed evidence set with local paths removed."""
    out = p["out"]
    out.mkdir(parents=True, exist_ok=True)
    keep = ["before-tests.txt", "after-tests.txt", "oracle-tests.txt", "findings.json", "repair.diff", "index.repaired.html"]
    for name in keep:
        src = p["evidence"] / name
        if src.exists():
            (out / name).write_text(scrub(src.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    (out / "cycle.json").write_text(scrub(json.dumps(log, indent=2)), encoding="utf-8", newline="\n")
    packet_dir = next((p["work"] / ".ux-review" / "packets").glob("*"))
    for name in ("packet.json", "receipt.json"):
        (out / name).write_text(scrub((packet_dir / name).read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    (out / "evidence.json").write_text(scrub((p["work"] / "evidence.json").read_text(encoding="utf-8")), encoding="utf-8", newline="\n")
    shots = out / "screenshots"
    shots.mkdir(exist_ok=True)
    for rel in log["evidence"]["screenshots"]:
        shutil.copy2(p["work"] / rel, shots / Path(rel).name)
    seen, _ = lugos_reads(p["access"])
    (out / "access-log.txt").write_text(scrub("\n".join(seen)) + "\n", encoding="utf-8", newline="\n")
    leftovers = [n.name for n in out.rglob("*") if n.suffix in {".json", ".txt", ".diff", ".html"}
                 and re.search(r"Users|Matt", n.read_text(encoding="utf-8"))]
    if leftovers:
        raise SystemExit(f"local paths survived scrubbing: {leftovers}")


def scrub(text):
    # A file passed in from the temp directory (an agent's scratchpad) keeps only its name: the
    # folder names there can embed the user's profile path.
    temp = tempfile.gettempdir()
    for form in (temp, temp.replace("\\", "\\\\"), temp.replace("\\", "/")):
        text = re.sub(re.escape(form) + r"[^\"\s]*", lambda m: "<tmp>/" + re.split(r"[\\/]+", m.group(0))[-1], text)
    home = str(Path.home())
    for root, token in ((str(REPO), "<repo>"), (str(LUGOS), "<lugos>"), (home, "~")):
        for form in (root, root.replace("\\", "\\\\"), root.replace("\\", "/")):
            text = text.replace(form, token)
    text = re.sub(r"(<repo>|<lugos>|~)((?:\\\\|\\)[^\"\s]*)", lambda m: m.group(1) + m.group(2).replace("\\\\", "/").replace("\\", "/"), text)
    return re.sub(r"[A-Za-z]:[\\/](?:[^\\/\"\s]+[\\/])*(?:Users|AppData)[^\"\s]*", "<local-path>", text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("phase", choices=["baseline", "record", "repair", "finish", "lesson", "compare"])
    ap.add_argument("--cycle", default="fixture-cycle-001")
    ap.add_argument("--findings", type=Path)
    ap.add_argument("--page", type=Path)
    ap.add_argument("--lesson", type=Path, help="agent-authored {title, body, finding, test}")
    ap.add_argument("--comparison", type=Path, help="agent-authored {structural_changes, improvements, findings_disposition, "
                                                     "limitations, decision, decided_by, decided_at, decision_note}")
    a = ap.parse_args()
    if a.phase == "record" and not a.findings:
        ap.error("record needs --findings")
    if a.phase == "repair" and not a.page:
        ap.error("repair needs --page")
    if a.phase == "lesson" and not a.lesson:
        ap.error("lesson needs --lesson")
    if a.phase == "compare" and not a.comparison:
        ap.error("compare needs --comparison")
    {"baseline": baseline, "record": record, "repair": repair, "finish": finish, "lesson": lesson,
     "compare": compare}[a.phase](a)


if __name__ == "__main__":
    main()
