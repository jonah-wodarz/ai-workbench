"""Unit tests for the skills-in-use and skill-router hooks (stdlib only).

Run: python -m unittest discover -s setup/claude-code/tests -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOKS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks")
IN_USE = os.path.join(HOOKS, "skills-in-use.py")
ROUTER = os.path.join(HOOKS, "skill-router.py")

CONVENTIONS = """# Conventions

## Skills in use

| When | Skill |
|---|---|
| Recording decisions | `design-capture` |

## 1. Principles

Other text.
"""


def run(script, payload, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    env.update(env_extra or {})
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    proc = subprocess.run(
        [sys.executable, script], input=stdin.encode("utf-8"),
        capture_output=True, env=env, timeout=20,
    )
    return proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")


class SkillsInUseTest(unittest.TestCase):
    def project(self, rel, text):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = os.path.join(tmp.name, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        return tmp.name

    def test_docs_conventions_section_printed(self):
        root = self.project("docs/CONVENTIONS.md", CONVENTIONS)
        code, out, _ = run(IN_USE, {"cwd": root, "hook_event_name": "SessionStart"})
        self.assertEqual(code, 0)
        self.assertIn("`design-capture`", out)
        self.assertNotIn("Other text", out)
        self.assertTrue(out.rstrip().endswith(
            "Load the named skill with the Skill tool before the matching work."))

    def test_root_conventions_fallback(self):
        root = self.project("CONVENTIONS.md", CONVENTIONS)
        code, out, _ = run(IN_USE, {"cwd": root})
        self.assertEqual(code, 0)
        self.assertIn("design-capture", out)

    def test_docs_preferred_over_root(self):
        root = self.project("CONVENTIONS.md", CONVENTIONS.replace("design-capture", "root-skill"))
        os.makedirs(os.path.join(root, "docs"))
        with open(os.path.join(root, "docs", "CONVENTIONS.md"), "w", encoding="utf-8") as fh:
            fh.write(CONVENTIONS)
        _, out, _ = run(IN_USE, {"cwd": root})
        self.assertIn("design-capture", out)
        self.assertNotIn("root-skill", out)

    def test_env_project_dir_wins_over_cwd(self):
        root = self.project("docs/CONVENTIONS.md", CONVENTIONS)
        _, out, _ = run(IN_USE, {"cwd": tempfile.gettempdir()}, {"CLAUDE_PROJECT_DIR": root})
        self.assertIn("design-capture", out)

    def test_silent_without_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run(IN_USE, {"cwd": tmp}), (0, "", ""))

    def test_silent_without_section(self):
        root = self.project("docs/CONVENTIONS.md", "# Conventions\n\n## 1. Principles\n\nText\n")
        self.assertEqual(run(IN_USE, {"cwd": root}), (0, "", ""))

    def test_heading_inside_code_fence_ignored(self):
        root = self.project("docs/CONVENTIONS.md", "# C\n\n```\n## Skills in use\n```\n")
        self.assertEqual(run(IN_USE, {"cwd": root}), (0, "", ""))

    def test_section_at_end_of_file(self):
        root = self.project("docs/CONVENTIONS.md", "# C\n\n## Skills in use\n\n- `playbook`\n")
        _, out, _ = run(IN_USE, {"cwd": root})
        self.assertIn("`playbook`", out)

    def test_invalid_stdin_does_not_fail(self):
        code, out, _ = run(IN_USE, "not json")
        self.assertEqual(code, 0)

    def test_non_ascii_content(self):
        root = self.project("docs/CONVENTIONS.md", "## Skills in use\n\nÜbungsaufgaben → `fair-practice-questions`\n")
        _, out, _ = run(IN_USE, {"cwd": root})
        self.assertIn("Übungsaufgaben", out)


class SkillRouterTest(unittest.TestCase):
    def cfg(self, data):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(data, tmp)
        tmp.close()
        self.addCleanup(os.remove, tmp.name)
        return {"SKILL_ROUTER_CONFIG": tmp.name}

    def prompt(self, text, env=None):
        return run(ROUTER, {"hook_event_name": "UserPromptSubmit", "prompt": text}, env)

    def test_starter_config_is_valid_json_with_all_skills(self):
        with open(os.path.join(HOOKS, "skill-router.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        expected = {"design-capture", "layered-design-facilitation", "structured-project-docs",
                    "doc-kit", "playbook", "report-style", "interrogate", "setup-retro",
                    "fair-practice-questions", "handoff"}
        self.assertEqual(set(cfg["skills"]), expected)

    def test_starter_english_match(self):
        self.assertEqual(self.prompt("Please grill me on this plan"),
                         (0, "Load the `interrogate` skill before answering.\n", ""))

    def test_starter_german_matches(self):
        for text, skill in [("Frag mich aus zum Thema", "interrogate"),
                            ("Mach Übungsaufgaben zu Routing", "fair-practice-questions"),
                            ("Erstelle eine Probeklausur", "fair-practice-questions")]:
            with self.subTest(text=text):
                self.assertIn("`%s`" % skill, self.prompt(text)[1])

    def test_handoff_patterns(self):
        for text in ["write a handoff page", "a visual summary please", "checkpoint report", "decision brief"]:
            with self.subTest(text=text):
                self.assertIn("`handoff`", self.prompt(text)[1])

    def test_case_insensitive(self):
        self.assertIn("`doc-kit`", self.prompt("RUN DOCLINT now")[1])

    def test_no_match_no_output(self):
        self.assertEqual(self.prompt("fix the off-by-one in parser.py"), (0, "", ""))

    def test_empty_and_missing_prompt(self):
        self.assertEqual(run(ROUTER, {}), (0, "", ""))
        self.assertEqual(run(ROUTER, ""), (0, "", ""))

    def test_max_two_skills_ranked_by_hits(self):
        env = self.cfg({"max_skills": 2, "skills": {
            "a": ["foo"], "b": ["foo", "bar"], "c": ["foo", "bar", "baz"]}})
        _, out, _ = self.prompt("foo bar baz", env)
        self.assertEqual(out.splitlines(), [
            "Load the `c` skill before answering.", "Load the `b` skill before answering."])

    def test_config_order_breaks_ties(self):
        env = self.cfg({"skills": {"a": ["foo"], "b": ["foo"], "c": ["foo"]}})
        _, out, _ = self.prompt("foo", env)
        self.assertEqual(len(out.splitlines()), 2)
        self.assertIn("`a`", out)
        self.assertIn("`b`", out)

    def test_bad_regex_skipped(self):
        env = self.cfg({"skills": {"a": ["("], "b": ["ok"]}})
        self.assertEqual(self.prompt("ok", env)[1], "Load the `b` skill before answering.\n")

    def test_missing_config_is_silent(self):
        self.assertEqual(self.prompt("grill me", {"SKILL_ROUTER_CONFIG": "/nonexistent.json"}), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
