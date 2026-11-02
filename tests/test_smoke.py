"""The package imports, the console entry point answers, and the ported modules run as files."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import ux_recast
from ux_recast import cli
from ux_recast.cycle import control
from ux_recast.providers import lugos_autowork


class Smoke(unittest.TestCase):
    def test_version_matches_pyproject(self):
        text = (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{ux_recast.__version__}"', text)

    def test_cli_usage_without_verb(self):
        self.assertEqual(cli.main([]), 2)
        self.assertEqual(cli.main(["--help"]), 0)

    def test_cli_rubric_version(self):
        proc = subprocess.run([sys.executable, "-m", "ux_recast.cli", "rubric", "--version"],
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["rubric_version"], "1")

    def test_ported_modules_run_as_scripts(self):
        for module in (control, lugos_autowork):
            proc = subprocess.run([sys.executable, module.__file__], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(proc.returncode, 2, (module.__name__, proc.stdout, proc.stderr))
            self.assertIn("usage", (proc.stdout + proc.stderr).lower())

    def test_cli_forwards_to_control(self):
        proc = subprocess.run([sys.executable, "-m", "ux_recast.cli", "control"], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
