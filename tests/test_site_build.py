import json
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_data import ROOT


class SiteBuildTests(unittest.TestCase):
    def test_documented_command_works_outside_repository_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_site_data.py")],
                cwd=directory, capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        records = json.loads((ROOT / "site/opportunities.json").read_text(encoding="utf-8"))
        expected = {
            path.stem for path in (ROOT / "opportunities").glob("*.yml")
            if not path.name.startswith("_")
        }
        self.assertEqual({record["id"] for record in records}, expected)
        self.assertEqual(len(records), len(expected))
