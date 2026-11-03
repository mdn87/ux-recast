"""Differential harness (plan slice S1.6): run the frozen corpus against one or two implementations and diff.

An implementation is the pair of command-line entry points, named on the command line:

    --impl NAME=CONTROL.py,PACKET.py[,ENV=value;ENV2=value]

Each corpus scenario (``corpus/*.json``) is a list of steps run in a fresh project
directory. For every step the harness keeps the exit code and the normalized
stdout; at the end it keeps the normalized ``.ux-review/`` tree. Normalization
replaces the project path, run ids and timestamps with placeholders so two runs
of the same implementation are byte-identical. Paths under the project are
written with ``/``, and the tree's files are read with the platform's newline
translated, as Python's text mode reads them, so a baseline recorded on one
operating system compares on the other. Everything else must match.

    python tests/differential/run.py --impl a=... --impl b=...        # diff a against b
    python tests/differential/run.py --impl a=... --record out.json   # freeze a as a baseline
    python tests/differential/run.py --impl b=... --compare out.json  # diff b against a baseline

Exit code 0 means no differences, 1 means differences (printed), 2 means a harness error.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CORPUS = HERE / "corpus"
FIXTURE = HERE.parents[1] / "fixtures" / "contact-request"
SESSION = "differential"
EXPECTED_ALIASES = {"control", "packet"}


def parse_impl(spec):
    name, _, rest = spec.partition("=")
    parts = rest.split(",")
    if len(parts) < 2:
        raise SystemExit(f"--impl needs NAME=CONTROL,PACKET[,ENV=v;ENV=v]: {spec}")
    env = {}
    if len(parts) > 2 and parts[2]:
        for item in parts[2].split(";"):
            key, _, value = item.partition("=")
            env[key] = value
    return {"name": name, "control": str(_native(parts[0]).resolve()), "packet": str(_native(parts[1]).resolve()), "env": env}


def _native(path):
    """Accept Git Bash style /c/Users/... on Windows; the shell converts only the first such path in an argument."""
    match = re.fullmatch(r"/([A-Za-z])/(.*)", path)
    if match and os.name == "nt":
        return Path(f"{match.group(1).upper()}:/{match.group(2)}")
    return Path(path)


class Normalizer:
    def __init__(self, project):
        root = str(project)
        self.forms = sorted({root, root.replace("\\", "\\\\"), root.replace("\\", "/"), str(Path(root).resolve()),
                             str(Path(root).resolve()).replace("\\", "\\\\"), str(Path(root).resolve()).replace("\\", "/")},
                            key=len, reverse=True)
        self.run_ids = {}
        self.digests = {}
        # The same path printed through repr() inside JSON carries 2, 4 or 8 backslashes per separator,
        # so match the path's parts joined by any run of separators.
        resolved = Path(root).resolve()
        drive = resolved.drive.rstrip(":")
        sep = r"[\\/]+"
        head = (re.escape(drive) + ":" + sep) if drive else sep
        self.project_pattern = re.compile(head + sep.join(re.escape(part) for part in resolved.parts[1:]))

    def text(self, value):
        for form in self.forms:
            value = value.replace(form, "<project>")
        value = self.project_pattern.sub("<project>", value)
        # The separators inside a project path are the platform's (repr() doubles a backslash, JSON doubles it again).
        value = re.sub(r"<project>((?:(?:\\+|/)[\w.-]+)+)",
                       lambda m: "<project>" + re.sub(r"\\+", "/", m.group(1)), value)
        value = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", "<time>", value)
        value = re.sub(r"local-\d{8}-\d{6}", "local-<stamp>", value)

        def digest(match):
            # Digests cover text that embeds the random run id, so they can never match across runs;
            # alias them in order of appearance, which still checks that equal digests stay equal.
            self.digests.setdefault(match.group(0), f"<sha{len(self.digests) + 1}>")
            return self.digests[match.group(0)]
        value = re.sub(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", digest, value)

        def run_id(match):
            self.run_ids.setdefault(match.group(0), f"<run{len(self.run_ids) + 1}>")
            return self.run_ids[match.group(0)]
        return re.sub(r"(?<![0-9a-f])[0-9a-f]{12}(?![0-9a-f])", run_id, value)


def write_inputs(project):
    shutil.copy2(FIXTURE / "task.json", project / "task.json")
    (project / "page.html").write_text("<form><input id='email'></form>\n", encoding="utf-8")
    (project / "evidence.json").write_text(json.dumps({
        "observations": [{"step": "rejected", "visible_text": "Please check your details", "name": "", "email": "alex@"}],
        "screenshots": [], "coverage": "one submit"}, indent=2), encoding="utf-8")


def run_scenario(impl, scenario, python):
    project = Path(tempfile.mkdtemp(prefix="ux-diff-")).resolve()
    norm = Normalizer(project)
    steps_out = []
    try:
        write_inputs(project)
        run_id = None
        for step in scenario["steps"]:
            if "write" in step:
                target = project / step["write"]
                target.parent.mkdir(parents=True, exist_ok=True)
                content = step["text"] if "text" in step else json.dumps(step["json"], indent=2)
                target.write_text(content, encoding="utf-8")
                steps_out.append({"step": "write", "path": step["write"]})
                continue
            if "append" in step:
                target = project / step["append"]
                target.write_text(target.read_text(encoding="utf-8") + step["text"], encoding="utf-8")
                steps_out.append({"step": "append", "path": step["append"]})
                continue
            if "result_from_packet" in step:
                spec = step["result_from_packet"]
                key = hashlib.sha256(SESSION.encode()).hexdigest()[:24]
                packet_path = project / ".ux-review" / "packets" / f"{key}-{run_id}" / "packet.json"
                if not packet_path.exists():
                    steps_out.append({"step": "result_from_packet", "path": spec["path"], "error": "no packet to read"})
                    continue
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
                result = {"status": spec.get("status", "completed"), "run_id": "20260101-000000-abcdefabcdef",
                          "selected_route": "fixture:route", "model": "fixture", "artifact_dir": "/autowork-runs/fixture",
                          "changed_paths": spec.get("changed_paths", []), "worktree": None,
                          "answer": spec.get("answer", "F1"), "task_sha256": spec.get("task_sha256", packet["task_sha256"])}
                result.update(spec.get("extra", {}))
                target = project / spec["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(result, indent=2), encoding="utf-8")
                steps_out.append({"step": "result_from_packet", "path": spec["path"]})
                continue
            tool = step["tool"]
            if tool not in EXPECTED_ALIASES:
                raise SystemExit(f"unknown tool {tool!r} in {scenario['name']}")
            args = [a.replace("{run}", run_id or "none") for a in step["args"]]
            script = impl["control"] if tool == "control" else impl["packet"]
            argv = [python, script, "--project", str(project), "--session", SESSION, *args]
            env = {**os.environ, **impl["env"], "PYTHONIOENCODING": "utf-8"}
            proc = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", env=env, cwd=str(project))
            stdout = proc.stdout
            if tool == "control" and step["args"][:1] == ["checkpoint"] and proc.returncode == 0:
                try:
                    payload = json.loads(stdout)
                    run_id = payload.get("run_id", run_id)
                except json.JSONDecodeError:
                    pass
            steps_out.append({"step": f"{tool} {' '.join(step['args'])}", "returncode": proc.returncode,
                              "stdout": norm.text(stdout), "stderr_tail": norm.text(proc.stderr[-600:])})
        tree = {}
        state_dir = project / ".ux-review"
        if state_dir.exists():
            for path in sorted(p for p in state_dir.rglob("*") if p.is_file()):
                rel = norm.text(str(path.relative_to(project)).replace("\\", "/"))
                raw = path.read_bytes()
                try:
                    # Both implementations write state in text mode, so the newline on disk is the platform's.
                    tree[rel] = norm.text(raw.decode("utf-8").replace(os.linesep, "\n"))
                except UnicodeDecodeError:
                    tree[rel] = f"<binary {len(raw)} bytes>"
        return {"steps": steps_out, "tree": tree}
    finally:
        shutil.rmtree(project, ignore_errors=True)


def run_all(impl, python):
    results = {}
    for path in sorted(CORPUS.glob("*.json")):
        scenario = json.loads(path.read_text(encoding="utf-8"))
        results[scenario["name"]] = run_scenario(impl, scenario, python)
    return results


def diff(a, b, name_a, name_b):
    problems = []
    for scenario in sorted(set(a) | set(b)):
        if scenario not in a or scenario not in b:
            problems.append(f"{scenario}: only in {'a' if scenario in a else 'b'}")
            continue
        sa, sb = a[scenario]["steps"], b[scenario]["steps"]
        for index, (x, y) in enumerate(zip(sa, sb)):
            for key in ("step", "returncode", "stdout"):
                if x.get(key) != y.get(key):
                    problems.append(f"{scenario} step {index} ({x.get('step')}): {key} differs\n  {name_a}: {str(x.get(key))[:300]!r}\n  {name_b}: {str(y.get(key))[:300]!r}")
        if len(sa) != len(sb):
            problems.append(f"{scenario}: {len(sa)} steps vs {len(sb)}")
        ta, tb = a[scenario]["tree"], b[scenario]["tree"]
        for rel in sorted(set(ta) | set(tb)):
            if ta.get(rel) != tb.get(rel):
                problems.append(f"{scenario} tree {rel}: differs ({name_a}: {len(ta.get(rel) or '')} chars, {name_b}: {len(tb.get(rel) or '')} chars)")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--impl", action="append", required=True)
    ap.add_argument("--record", type=Path)
    ap.add_argument("--compare", type=Path)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--json", type=Path, help="also write the full results of every implementation here")
    a = ap.parse_args(argv)
    impls = [parse_impl(spec) for spec in a.impl]
    results = {impl["name"]: run_all(impl, a.python) for impl in impls}
    if a.json:
        a.json.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    if a.record:
        a.record.write_text(json.dumps({"implementation": impls[0], "results": results[impls[0]["name"]]},
                                       indent=2, sort_keys=True), encoding="utf-8")
        print(f"recorded {impls[0]['name']}: {len(results[impls[0]['name']])} scenarios -> {a.record}")
    problems = []
    if a.compare:
        baseline = json.loads(a.compare.read_text(encoding="utf-8"))
        problems += diff(baseline["results"], results[impls[0]["name"]], "baseline", impls[0]["name"])
    if len(impls) == 2:
        problems += diff(results[impls[0]["name"]], results[impls[1]["name"]], impls[0]["name"], impls[1]["name"])
    scenarios = {name: [(s.get("step"), s.get("returncode")) for s in r["steps"] if "returncode" in s]
                 for name, r in results[impls[0]["name"]].items()}
    for name, steps in scenarios.items():
        print(f"{name}: " + ", ".join(f"{step.split()[0]}:{code}" for step, code in steps))
    if problems:
        print(f"\n{len(problems)} difference(s):")
        for problem in problems:
            print("-", problem)
        return 1
    print("\nno differences" if (a.compare or len(impls) == 2) else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
