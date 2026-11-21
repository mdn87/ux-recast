"""Replay the eight public CLI scenarios against the current rubric's recording.

The separate baseline-ux-recast.json remains the Phase 3 migration reference.
Rubric 2 changes the review task and its packet metadata in six scenarios.
"""
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
RUN = HERE / "differential" / "run.py"
SRC = HERE.parent / "src" / "ux_recast"
BASELINE = HERE / "differential" / "baseline-rubric-v2.json"


class DifferentialBaseline(unittest.TestCase):
    def test_package_matches_recorded_baseline(self):
        impl = f"recast={SRC / 'cycle' / 'control.py'},{SRC / 'providers' / 'lugos_autowork.py'}"
        proc = subprocess.run([sys.executable, str(RUN), "--impl", impl, "--compare", str(BASELINE)],
                              capture_output=True, text=True, encoding="utf-8", timeout=900)
        self.assertEqual(proc.returncode, 0, proc.stdout[-3000:] + proc.stderr[-1000:])
        self.assertIn("no differences", proc.stdout)

    def test_corpus_covers_the_required_cases(self):
        names = sorted(p.stem for p in (HERE / "differential" / "corpus").glob("*.json"))
        for needle in ("valid", "malformed", "out-of-scope", "double-claim", "stale", "over-cap"):
            self.assertTrue(any(needle in n for n in names), (needle, names))


if __name__ == "__main__":
    unittest.main()
