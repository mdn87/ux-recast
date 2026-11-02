"""S1.6: the differential corpus runs against the package and matches the recorded ux-recast baseline.

The baseline (`tests/differential/baseline-ux-recast.json`) was recorded on
2026-11-02 and verified byte-identical, after normalization, to the Lugos legacy
scripts at e868aec4 and to the Phase 3 shims. This test keeps the package's own
behaviour from drifting; the cross-implementation comparison is run from Lugos
(slice S3.4) with the same harness.
"""
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
RUN = HERE / "differential" / "run.py"
SRC = HERE.parent / "src" / "ux_recast"
BASELINE = HERE / "differential" / "baseline-ux-recast.json"


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
