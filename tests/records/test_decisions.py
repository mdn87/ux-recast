"""S2.2: decisions.jsonl is append-only, serialized on the cycle lock, and survives a killed writer."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from ux_recast.records import decisions

SRC = str(Path(decisions.__file__).parents[2])
ITERATIONS = 200
PAD = 5000  # every line is above 4 KiB, past any single-write atomicity a platform might give

WRITER = textwrap.dedent("""
    import sys
    from ux_recast.records import decisions
    project, writer, count, pad = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    sys.stdin.readline()
    for seq in range(count):
        decisions.append(project, {"kind": "outcome", "summary": writer * pad, "writer": writer, "seq": seq})
""")

KILLED = textwrap.dedent("""
    import os, sys, time
    from pathlib import Path
    from ux_recast.cycle.control import locked
    from ux_recast.records import decisions
    paths = decisions._paths(sys.argv[1])
    with locked(paths["lock"]):
        paths["inflight"].write_text(f"pid {os.getpid()}\\n", encoding="utf-8")
        with open(paths["log"], "ab") as handle:
            handle.write(b'{"kind": "decision", "summary": "cut off mid-wri')
        print("holding", flush=True)
        time.sleep(120)
""")


def _env():
    env = dict(os.environ)
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    return env


class Decisions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_append_assigns_id_and_time_and_reads_back_in_order(self):
        self.assertEqual(decisions.read(self.project), [])
        first = decisions.append(self.project, {"kind": "decision", "summary": "accept the repair", "decided_by": "owner"})
        second = decisions.append(self.project, {"kind": "outcome", "summary": "thresholds met"})
        self.assertEqual(decisions.read(self.project), [first, second])
        self.assertNotEqual(first["id"], second["id"])
        self.assertTrue(first["recorded_at"].endswith("+00:00"))
        self.assertEqual((self.project / ".ux-recast" / "decisions.jsonl").read_bytes().count(b"\n"), 2)

    def test_invalid_records_are_refused(self):
        for record, field in (([], "record"), ({"summary": "x"}, "kind"), ({"kind": "verdict", "summary": "x"}, "kind"),
                              ({"kind": "decision"}, "summary"), ({"kind": "decision", "summary": " "}, "summary"),
                              ({"kind": "decision", "summary": "x", "id": "mine"}, "id")):
            with self.assertRaisesRegex(ValueError, f"^{field}:"):
                decisions.append(self.project, record)
        self.assertFalse((self.project / ".ux-recast" / "decisions.jsonl").exists())

    def test_two_concurrent_writers_keep_every_line_intact(self):
        procs = [subprocess.Popen([sys.executable, "-c", WRITER, str(self.project), name, str(ITERATIONS), str(PAD)],
                                  stdin=subprocess.PIPE, env=_env())
                 for name in "ab"]
        for proc in procs:
            proc.stdin.write(b"go\n")
            proc.stdin.close()
        for proc in procs:
            self.assertEqual(proc.wait(timeout=300), 0)
        raw = (self.project / ".ux-recast" / "decisions.jsonl").read_bytes()
        lines = raw.split(b"\n")
        self.assertEqual(lines[-1], b"")
        records = [json.loads(line) for line in lines[:-1]]
        self.assertEqual(len(records), 2 * ITERATIONS)
        self.assertTrue(all(len(line) > 4096 for line in lines[:-1]))
        for name in "ab":
            mine = [r for r in records if r["writer"] == name]
            self.assertEqual([r["seq"] for r in mine], list(range(ITERATIONS)))
            self.assertTrue(all(r["summary"] == name * PAD for r in mine))
        self.assertEqual(len({r["id"] for r in records}), 2 * ITERATIONS)
        self.assertFalse((self.project / ".ux-review" / "decisions.inflight").exists())

    def test_a_writer_killed_holding_the_lock_is_recovered_and_logged(self):
        kept = decisions.append(self.project, {"kind": "decision", "summary": "before the crash"})
        proc = subprocess.Popen([sys.executable, "-c", KILLED, str(self.project)], stdout=subprocess.PIPE, env=_env())
        try:
            self.assertEqual(proc.stdout.readline().strip(), b"holding")
        finally:
            proc.kill()
            proc.wait(timeout=30)
            proc.stdout.close()
        with self.assertLogs("ux_recast.records", "WARNING") as logs:
            after = decisions.append(self.project, {"kind": "outcome", "summary": "after the crash"})
        self.assertIn(f"recovered stale decisions lock left by pid {proc.pid}", logs.output[0])
        self.assertIn("torn decisions line", logs.output[1])
        self.assertEqual(decisions.read(self.project), [kept, after])
        torn = (self.project / ".ux-recast" / "decisions.torn").read_bytes()
        self.assertEqual(torn, b'{"kind": "decision", "summary": "cut off mid-wri\n')
        self.assertFalse((self.project / ".ux-review" / "decisions.inflight").exists())

    def test_an_intact_log_needs_no_recovery(self):
        decisions.append(self.project, {"kind": "decision", "summary": "one"})
        with self.assertNoLogs("ux_recast.records", "WARNING"):
            decisions.append(self.project, {"kind": "decision", "summary": "two"})


if __name__ == "__main__":
    unittest.main()
