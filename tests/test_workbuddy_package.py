import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / 'tools' / 'package_workbuddy.py'


class WorkBuddyPackageTest(unittest.TestCase):
    def test_builds_a_single_minimal_skill_bundle(self):
        with TemporaryDirectory() as scratch:
            package = Path(scratch) / 'workbuddy.zip'
            built = subprocess.run([sys.executable, str(PACKAGER), str(package)], cwd=scratch,
                                   capture_output=True, text=True, timeout=10)
            self.assertEqual(built.returncode, 0, built.stderr)
            with ZipFile(package) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), {
                    'session-name/SKILL.md', 'session-name/LICENSE',
                    'session-name/references/prefixes.json',
                    'session-name/references/configuration.md',
                    'session-name/references/hosts.md', 'session-name/scripts/title.mjs',
                })
                self.assertIn(b'## Tencent WorkBuddy', archive.read('session-name/references/hosts.md'))
                archive.extractall(scratch)
            formatter = Path(scratch) / 'session-name' / 'scripts' / 'title.mjs'
            formatted = subprocess.run(['node', str(formatter), 'format', '--type', 'feat',
                                        '--topic', 'WorkBuddy'], cwd=scratch,
                                       capture_output=True, text=True, timeout=10)
            self.assertEqual(formatted.returncode, 0, formatted.stderr)
            self.assertEqual(formatted.stdout.strip(), '[feat] WorkBuddy')


if __name__ == '__main__':
    unittest.main()
