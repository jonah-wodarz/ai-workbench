"""The example project must stay clean under the design preset and its committed map must be current."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE = os.path.join(ROOT, "examples", "bike-shop")


class Example(unittest.TestCase):
    def setUp(self):
        self.root = os.path.join(tempfile.mkdtemp(), "bike-shop")
        self.addCleanup(shutil.rmtree, os.path.dirname(self.root))
        shutil.copytree(EXAMPLE, self.root)
        shutil.copytree(os.path.join(ROOT, "kit", "tools"), os.path.join(self.root, "tools"), dirs_exist_ok=True)

    def lint(self, *args):
        p = subprocess.run([sys.executable, "tools/doclint.py"] + list(args), cwd=self.root, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True, encoding="utf-8")
        self.assertNotIn("Traceback", p.stderr, p.stderr)
        return p.returncode, p.stdout

    def test_example_uses_the_design_preset_unchanged(self):
        with open(os.path.join(EXAMPLE, "tools", "doclint.json"), encoding="utf-8") as a, \
                open(os.path.join(ROOT, "kit", "presets", "design.json"), encoding="utf-8") as b:
            self.assertEqual(a.read(), b.read())

    def test_example_is_clean(self):
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertIn("0 errors, 0 warnings", out)

    def test_committed_map_is_current(self):
        rc, out = self.lint("--map")
        with open(os.path.join(EXAMPLE, "docs", "SYSTEM_MAP.md"), encoding="utf-8") as f:
            self.assertIn(out.strip(), f.read())

    def test_system_map_page_builds(self):
        rc, out = self.lint("--system-map")
        self.assertEqual(rc, 0, out)
        self.assertIn("(3 systems, 2 dependencies)", out)


if __name__ == "__main__":
    unittest.main()
