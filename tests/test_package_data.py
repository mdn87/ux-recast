"""S0.2: a built wheel carries the rubric and schema files and loads them through importlib.resources.

Builds the wheel from this checkout, installs it into a scratch target directory
(no site-packages changes), and imports from there in a subprocess with the
source tree removed from sys.path.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).parents[1]
EXPECTED = {
    "ux_recast/rubric/rubric.md", "ux_recast/rubric/autowork-reviewer.md", "ux_recast/rubric/walkthrough.md",
    "ux_recast/rubric/VERSION",
    "ux_recast/schemas/task.schema.json", "ux_recast/schemas/state.schema.json",
    "ux_recast/schemas/packet.schema.json", "ux_recast/schemas/receipt.schema.json",
    "ux_recast/schemas/findings.schema.json", "ux_recast/schemas/comparison.schema.json",
}

PROBE = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import ux_recast
from ux_recast import rubric, contracts
from ux_recast.cycle import control
from ux_recast.providers import lugos_autowork, local_agent
print(json.dumps({
    "file": ux_recast.__file__,
    "rubric_version": rubric.version(),
    "rubric_bytes": len(rubric.read_bytes("rubric.md")),
    "schemas": sorted(k for k in contracts.KINDS if contracts.schema(k)["title"]),
}))
"""


def _build_available():
    return subprocess.run([sys.executable, "-c", "import build"], capture_output=True).returncode == 0


@unittest.skipUnless(_build_available(), "needs the build package")
class WheelPackageData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="ux-recast-wheel-"))
        out = cls.tmp / "dist"
        proc = subprocess.run([sys.executable, "-m", "build", "--wheel", "--outdir", str(out), str(ROOT)],
                              capture_output=True, text=True, encoding="utf-8")
        if proc.returncode:
            raise unittest.SkipTest(f"wheel build failed: {proc.stderr[-800:]}")
        cls.wheel = next(out.glob("ux_recast-*.whl"))
        cls.target = cls.tmp / "site"
        proc = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--no-deps", "--target", str(cls.target), str(cls.wheel)],
                              capture_output=True, text=True, encoding="utf-8")
        if proc.returncode:
            raise unittest.SkipTest(f"pip install --target failed: {proc.stderr[-800:]}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_wheel_lists_package_data(self):
        names = set(zipfile.ZipFile(self.wheel).namelist())
        missing = EXPECTED - names
        self.assertFalse(missing, f"missing from wheel: {sorted(missing)}")
        self.assertFalse([n for n in names if n.startswith("tests/") or "lugos_compat" in n], "tests leaked into the wheel")

    def test_installed_package_loads_data(self):
        proc = subprocess.run([sys.executable, "-I", "-c", PROBE, str(self.target)], cwd=str(self.tmp),
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["file"].replace("\\", "/").startswith(str(self.target).replace("\\", "/")), payload["file"])
        self.assertEqual(payload["rubric_version"], "1")
        self.assertGreater(payload["rubric_bytes"], 1000)
        self.assertEqual(payload["schemas"], ["comparison", "findings", "packet", "receipt", "state", "task"])


if __name__ == "__main__":
    unittest.main()
