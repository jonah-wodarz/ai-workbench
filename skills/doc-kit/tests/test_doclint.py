"""Unit tests for doclint core, presets and the style plugin.

Run from the kit root:  python -m unittest discover -s tests -v
Each test builds a throwaway project with the kit's tools/ and a preset config.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit")


class ProjectCase(unittest.TestCase):
    preset = "design"
    overrides = {}

    def setUp(self):
        self.root = tempfile.mkdtemp()
        shutil.copytree(os.path.join(KIT, "tools"), os.path.join(self.root, "tools"))
        with open(os.path.join(KIT, "presets", self.preset + ".json"), encoding="utf-8") as f:
            cfg = json.load(f)
        cfg.update(self.overrides)
        self.write("tools/doclint.json", json.dumps(cfg, indent=2))
        self.write("tools/stale-terms.txt", "old fact \\d+ => use the new fact\n")
        os.makedirs(os.path.join(self.root, "docs"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def lint(self, *args):
        p = subprocess.run([sys.executable, "tools/doclint.py"] + list(args), cwd=self.root,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertNotIn("Traceback", p.stderr, p.stderr)
        return p.returncode, p.stdout

    def assertFinding(self, out, level, where, text):
        hits = [l for l in out.splitlines() if l.startswith(level) and where in l and text in l]
        self.assertTrue(hits, "expected {} {} '{}' in:\n{}".format(level, where, text, out))

    def assertNoFindings(self, out):
        self.assertTrue(out.strip().startswith("0 errors, 0 warnings"), out)


DESIGN_CONVENTIONS = """# Conventions
| Code | File |
|---|---|
| `ARC` | design/combat/archery.md |
| `CHA` | design/combat/charged.md |
| `GLO` | GLOSSARY.md |
"""

SPEC = """---
id: ARC
title: Archery
type: spec
layer: L2
status: settled
updated: 2026-10-01
depends_on: [CHA]
---
# Archery
> Purpose.

## Rules
- **ARC-R1** The bow draws. `locked`
- **ARC-R2** The crossbow loads. `placeholder`

## Open questions
- **ARC-Q1** Range? `major`
"""

CHARGED = SPEC.replace("id: ARC", "id: CHA").replace("ARC-", "CHA-").replace("depends_on: [CHA]", "depends_on: []")

HISTORY = """---
id: ARC
title: Archery - decision history
type: decisions
updated: 2026-10-01
---
# Archery - decision history
### D-ARC-001 - Draw stages
2026-10-01 · accepted · rules ARC-R1
"""

GLOSSARY = """---
id: GLO
title: Glossary
type: registry
updated: 2026-10-01
---
# Glossary
| Term | Means | Owner | Not to be confused with |
|---|---|---|---|
| **Precision** | Bow stat: velocity per draw stage | ARC | - |

## Retired names
| Retired | Use instead | Lint pattern |
|---|---|---|
| Wobble | Precision | `\\b[Ww]obble\\b` |
| Power | Precision | |
"""


class DesignPreset(ProjectCase):
    def setUp(self):
        super().setUp()
        self.write("docs/CONVENTIONS.md", DESIGN_CONVENTIONS)
        self.write("docs/GLOSSARY.md", GLOSSARY)
        self.write("docs/design/combat/archery.md", SPEC)
        self.write("docs/design/combat/charged.md", CHARGED)
        self.write("docs/decisions/combat/archery.md", HISTORY)
        self.write("docs/decisions/combat/charged.md", HISTORY.replace("ARC", "CHA"))
        self.write("docs/planning/OPEN_QUESTIONS.md", "# Open questions\n")

    def test_clean_project(self):
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertNoFindings(out)

    def test_broken_link(self):
        self.write("docs/design/combat/archery.md", SPEC + "\nSee [x](missing.md).\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1)
        self.assertFinding(out, "ERROR", "archery.md:20", "broken link: missing.md")

    def test_links_in_code_fences_are_ignored(self):
        self.write("docs/design/combat/archery.md", SPEC + "\n```\n[x](missing.md)\n```\n")
        self.assertNoFindings(self.lint()[1])

    def test_retired_name_and_stale_fact(self):
        self.write("docs/design/combat/archery.md", SPEC + "\nNo wobble, old fact 3.\n")
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "archery.md", "retired name; use: Precision")
        self.assertFinding(out, "ERROR", "archery.md", "use the new fact")

    def test_stale_terms_exempt_in_decisions(self):
        self.write("docs/decisions/combat/archery.md", HISTORY + "\nNo wobble here.\n")
        self.assertNoFindings(self.lint()[1])

    def test_front_matter_errors(self):
        bad = SPEC.replace("status: settled", "status: done").replace("updated: 2026-10-01", "updated: soon") \
                  .replace("layer: L2\n", "").replace("depends_on: [CHA]", "depends_on: [ZZZ]")
        self.write("docs/design/combat/archery.md", bad)
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "archery.md:1", "unknown status 'done'")
        self.assertFinding(out, "ERROR", "archery.md:1", "'updated' must be YYYY-MM-DD")
        self.assertFinding(out, "ERROR", "archery.md:1", "missing 'layer'")
        self.assertFinding(out, "ERROR", "archery.md:1", "unknown layer 'None'")
        self.assertFinding(out, "WARN", "archery.md:1", "depends_on 'ZZZ'")

    def test_unknown_type_does_not_crash(self):
        self.write("docs/design/combat/archery.md", SPEC.replace("type: spec", "type: sdd"))
        self.assertFinding(self.lint()[1], "ERROR", "archery.md:1", "unknown type 'sdd'")

    def test_id_must_match_path_and_be_unique(self):
        self.write("docs/design/combat/charged.md", CHARGED.replace("id: CHA", "id: ARC"))
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "charged.md:1", "id 'ARC' belongs to design/combat/archery.md")
        self.assertFinding(out, "ERROR", "charged.md:1", "already used by")

    def test_rule_tags(self):
        body = SPEC.replace("The bow draws. `locked`", "The bow draws.") \
                   .replace("The crossbow loads. `placeholder`", "The crossbow loads. `leaning`")
        self.write("docs/design/combat/archery.md", body)
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "archery.md:14", "must end with exactly one tag")
        self.assertFinding(out, "ERROR", "archery.md:15", "only allowed under Provisional rules")

    def test_provisional_section_requires_leaning(self):
        self.write("docs/design/combat/archery.md", SPEC + "\n## Provisional rules\n- **ARC-R3** Maybe. (ARC-Q1) `locked`\n")
        self.assertFinding(self.lint()[1], "ERROR", "archery.md", "must be tagged `leaning`")

    def test_duplicate_and_foreign_ids(self):
        self.write("docs/design/combat/archery.md", SPEC + "\n- **ARC-R1** Again. `locked`\n- **CHA-R1** Foreign. `locked`\n")
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "archery.md", "duplicate rule id ARC-R1")
        self.assertFinding(out, "ERROR", "archery.md", "rule CHA-R1 does not match file code ARC")

    def test_question_tags_and_index(self):
        self.write("docs/design/combat/archery.md", SPEC + "- **ARC-Q2** Untagged?\n- **ARC-Q3** Blocks? `blocking`\n")
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "archery.md", "question ARC-Q2 must end with exactly one tag")
        self.assertFinding(out, "ERROR", "archery.md", "blocking question ARC-Q3 is not listed")
        self.write("docs/planning/OPEN_QUESTIONS.md", "# Open questions\n- **ARC-Q3** Blocks? · link\n")
        self.assertNotIn("ARC-Q3 is not listed", self.lint()[1])

    def test_references(self):
        self.write("docs/design/combat/charged.md", CHARGED + "\nSee ARC-R1, ARC-R9, D-ARC-001, D-ARC-007.\n")
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "charged.md", "dangling reference ARC-R9")
        self.assertFinding(out, "ERROR", "charged.md", "dangling reference D-ARC-007")
        self.assertNotIn("ARC-R1:", out)

    def test_prose_checks(self):
        self.write("docs/design/combat/archery.md",
                   SPEC + "\n## Changelog\n## Notes 2026-01-01\n★ key ~~old~~. My view. Ships in v2.\n")
        out = self.lint()[1]
        for text in ("changelog section", "heading contains a date", "is not used in specs",
                     "strikethrough", "first person"):
            self.assertFinding(out, "ERROR", "archery.md", text)
        self.assertFinding(out, "WARN", "archery.md", "release scheduling")

    def test_working_notes_only_while_drafting(self):
        self.write("docs/design/combat/archery.md", SPEC + "\n## Working notes\nMy ★ ideas, v2.\n")
        out = self.lint()[1]
        self.assertFinding(out, "ERROR", "archery.md", "working notes are only allowed")
        self.assertNotIn("first person", out)  # notes are exempt from prose checks
        self.write("docs/design/combat/archery.md",
                   SPEC.replace("status: settled", "status: drafting") + "\n## Working notes\nMy ideas.\n")
        self.assertNoFindings(self.lint()[1])

    def test_mirror_and_decision_log(self):
        os.remove(os.path.join(self.root, "docs/decisions/combat/charged.md"))
        self.write("docs/decisions/combat/archery.md", HISTORY + "### D-ARC-001 - Dup\n### D-CHA-001 - Wrong\n")
        out = self.lint()[1]
        self.assertFinding(out, "WARN", "charged.md", "no decision-history file at docs/decisions/combat/charged.md")
        self.assertFinding(out, "ERROR", "decisions/combat/archery.md", "duplicate decision id D-ARC-001")
        self.assertFinding(out, "ERROR", "decisions/combat/archery.md", "decision D-CHA-001 does not match file code ARC")

    def test_word_budget(self):
        self.write("docs/design/combat/archery.md", SPEC + "\n" + "word " * 1600 + "\n")
        self.assertFinding(self.lint()[1], "WARN", "archery.md", "exceeds the ~1500-word budget")

    def test_missing_front_matter_is_listed(self):
        self.write("docs/design/combat/raw.md", "# Raw\nSee ARC-R1.\n")
        rc, out = self.lint("--verbose")
        self.assertIn("1 not yet migrated", out)
        self.assertIn("design/combat/raw.md", out)

    def test_map_from_codes(self):
        rc, out = self.lint("--map")
        self.assertIn("| `ARC` | Archery | spec | L2 | settled | [`design/combat/archery.md`](design/combat/archery.md) |", out)
        self.assertIn("| `GLO` | Glossary | registry |", out)

    def test_quiet_hides_warnings(self):
        self.write("docs/design/combat/archery.md", SPEC + "\nShips in v2.\n")
        out = self.lint("--quiet")[1]
        self.assertNotIn("WARN", out)

    def test_config_comments_ignored_and_version(self):
        rc, out = self.lint("--version")
        self.assertTrue(out.startswith("doclint "))


class EarlyQuantity(ProjectCase):
    """Rules below L3 state orderings or tiers; quantities need the `placeholder` tag."""
    ANCHOR = "- **ARC-R2** The crossbow loads. `placeholder`\n"

    def setUp(self):
        super().setUp()
        self.write("docs/CONVENTIONS.md", DESIGN_CONVENTIONS)
        self.write("docs/GLOSSARY.md", GLOSSARY)
        self.write("docs/decisions/combat/archery.md", HISTORY)

    def lint_rules(self, rules, layer="L2"):
        text = SPEC.replace(self.ANCHOR, rules).replace("layer: L2", "layer: " + layer)
        self.write("docs/design/combat/archery.md", text)
        return self.lint()[1]

    def test_fires_on_quantity_in_l2_rule(self):
        out = self.lint_rules("- **ARC-R2** Damage rises by 12%. `locked`\n- **ARC-R3** A draw takes 1.5 s. `locked`\n")
        self.assertFinding(out, "WARN", "archery.md:15", "quantity in a rule below L3")
        self.assertFinding(out, "WARN", "archery.md:16", "tag it `placeholder`")
        self.assertEqual(out.count("quantity in a rule"), 2, out)

    def test_fires_on_decimal_and_unit(self):
        out = self.lint_rules("- **ARC-R2** Range is 2.5 tiles. `locked`\n- **ARC-R3** A volley lasts 3 seconds. `locked`\n")
        self.assertEqual(out.count("quantity in a rule"), 2, out)

    def test_is_a_warning_not_an_error(self):
        self.write("docs/design/combat/archery.md", SPEC.replace(self.ANCHOR, "- **ARC-R2** Costs 12%. `locked`\n"))
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)

    def test_silent_when_tagged_placeholder(self):
        self.assertNoFindings(self.lint_rules("- **ARC-R2** Damage rises by 12%. `placeholder`\n"))

    def test_silent_in_l3_doc(self):
        self.assertNoFindings(self.lint_rules("- **ARC-R2** Damage rises by 12%. `locked`\n", layer="L3"))

    def test_silent_on_non_rule_lines(self):
        out = self.lint_rules(self.ANCHOR + "\nThe draw takes 1.5 s and deals 12% more.\n"
                              "- **ARC-Q2** Is 12% too much? `minor`\n")
        self.assertNotIn("quantity in a rule", out)

    def test_silent_on_ids_dates_and_structural_integers(self):
        out = self.lint_rules("- **ARC-R2** Two shield types and 3 phases; extends ARC-R1 and D-ARC-001, "
                              "decided 2026-11-14, see section 3.2 and v0.3.0. `locked`\n")
        self.assertNotIn("quantity in a rule", out)

    def test_silent_inside_inline_code(self):
        out = self.lint_rules("- **ARC-R2** The config key `draw_time: 1.5 s` is named in code. `locked`\n")
        self.assertNotIn("quantity in a rule", out)

    def test_silent_when_not_configured(self):
        path = os.path.join(self.root, "tools", "doclint.json")
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
        del cfg["early_quantity"]
        self.write("tools/doclint.json", json.dumps(cfg))
        self.assertNoFindings(self.lint_rules("- **ARC-R2** Damage rises by 12%. `locked`\n"))

    def test_threshold_and_pattern_are_configurable(self):
        path = os.path.join(self.root, "tools", "doclint.json")
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["early_quantity"] = {"below_layer": "L2", "pattern": r"\bten\b"}
        self.write("tools/doclint.json", json.dumps(cfg))
        rules = "- **ARC-R2** Costs 12%. `locked`\n- **ARC-R3** Deals ten damage. `locked`\n"
        self.assertNoFindings(self.lint_rules(rules, layer="L2"))
        out = self.lint_rules(rules, layer="L1")
        self.assertFinding(out, "WARN", "archery.md:16", "quantity in a rule below L2")
        self.assertEqual(out.count("quantity in a rule"), 1, out)


class Coupling(ProjectCase):
    """Foreign rule references, interface items, fan-out and cycles (all warnings except ID integrity)."""
    CODES = ["ARC", "CHA", "SHD", "DMI"]

    def setUp(self):
        super().setUp()
        table = "# Conventions\n| Code | File |\n|---|---|\n" + "".join(
            "| `{}` | design/combat/{}.md |\n".format(c, c.lower()) for c in self.CODES) + "| `GLO` | GLOSSARY.md |\n"
        self.write("docs/CONVENTIONS.md", table)
        self.write("docs/GLOSSARY.md", GLOSSARY)
        self.write("docs/planning/OPEN_QUESTIONS.md", "# Open questions\n")

    def spec(self, code, deps=(), body=None, status="settled", kind="spec", extra=""):
        body = body if body is not None else "- **{0}-R1** The system works. `locked`\n".format(code)
        text = ("---\nid: {0}\ntitle: {0} system\ntype: {kind}\nlayer: L2\nstatus: {status}\n"
                "updated: 2026-10-01\ndepends_on: [{deps}]\n---\n# {0}\n> Purpose.\n\n"
                "## Interface\n- **{0}-I1** Offers a term.\n\n## Rules\n{body}\n{extra}").format(
                    code, kind=kind, status=status, deps=", ".join(deps), body=body, extra=extra)
        self.write("docs/design/combat/{}.md".format(code.lower()), text)

    def all_specs(self, **deps):
        for code in self.CODES:
            self.spec(code, deps.get(code, ()))

    def hits(self, out, text):
        return [l for l in out.splitlines() if text in l]

    def set_coupling(self, value):
        path = os.path.join(self.root, "tools", "doclint.json")
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
        if value is None:
            cfg.pop("coupling", None)
        else:
            cfg["coupling"] = value
        self.write("tools/doclint.json", json.dumps(cfg))

    # -- foreign rule references
    def test_foreign_rule_reference_warns_with_fix(self):
        self.all_specs()
        self.spec("ARC", body="- **ARC-R1** Draw follows CHA-R1 exactly. `locked`\n")
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertFinding(out, "WARN", "arc.md:17",
                           "rule cites CHA-R1 of another system: cite an interface item (CHA-I\u2026) or the system code")

    def test_foreign_reference_in_parameter_line_warns(self):
        self.all_specs()
        self.spec("ARC", extra="## Parameters\n| Draw time | per CHA-R1 |\n")
        self.assertFinding(self.lint()[1], "WARN", "arc.md", "parameter cites CHA-R1 of another system")

    def test_foreign_reference_exemptions(self):
        self.all_specs()
        body = ("- **ARC-R1** Uses the CHA interface (CHA-I1), the code CHA and own ARC-R2; `CHA-R1` is code. `locked`\n"
                "- **ARC-R2** Reads [the charged spec](cha.md) by link only. `locked`\n"
                "- **ARC-R3** Waits on ARC-Q1 and CHA-Q1 (questions, not rules). `locked`\n")
        self.spec("CHA", extra="## Open questions\n- **CHA-Q1** Range? `minor`\n")
        extra = ("## Open questions\n- **ARC-Q1** Does CHA-R1 still hold? `major`\n\n"
                 "## Working notes\nCHA-R1 and SHD-R1 here.\n")
        self.spec("ARC", body=body, extra=extra, status="drafting")
        out = self.lint()[1]
        self.assertEqual(self.hits(out, "of another system"), [], out)

    def test_foreign_reference_ignored_outside_configured_types(self):
        self.all_specs()
        self.spec("ARC", kind="data", body="- **ARC-R1** Follows CHA-R1. `locked`\n")
        self.assertEqual(self.hits(self.lint()[1], "of another system"), [])

    # -- interface items
    def test_interface_items_are_ids(self):
        self.all_specs()
        self.spec("ARC", deps=["CHA"], body="- **ARC-R1** Needs CHA-I1 from CHA. `locked`\n")
        out = self.lint()[1]
        self.assertEqual(self.hits(out, "dangling"), [], out)
        self.assertEqual(self.hits(out, "of another system"), [], out)

    def test_dangling_interface_citation_is_a_warning(self):
        self.all_specs()
        self.spec("ARC", deps=["CHA"], body="- **ARC-R1** Needs CHA-I9. `locked`\n")
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertFinding(out, "WARN", "arc.md:17", "dangling reference CHA-I9")

    def test_dangling_rule_citation_stays_an_error(self):
        self.all_specs()
        self.spec("ARC", extra="Mentions CHA-R9.\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertFinding(out, "ERROR", "arc.md", "dangling reference CHA-R9")

    def test_duplicate_and_mismatched_interface_ids_are_errors(self):
        self.all_specs()
        self.spec("ARC", extra="- **ARC-I1** Again.\n- **CHA-I2** Wrong file.\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertFinding(out, "ERROR", "arc.md", "duplicate interface item id ARC-I1")
        self.assertFinding(out, "ERROR", "arc.md", "interface item CHA-I2 does not match file code ARC")

    # -- fan-out
    def test_fan_out_over_the_limit_warns(self):
        self.set_coupling({"types": ["spec"], "max_fan_out": 2})
        self.all_specs(ARC=["CHA", "SHD", "DMI"])
        out = self.lint()[1]
        self.assertFinding(out, "WARN", "arc.md", "fan-out 3 exceeds the limit of 2")

    def test_fan_out_at_the_limit_is_silent(self):
        self.set_coupling({"types": ["spec"], "max_fan_out": 3})
        self.all_specs(ARC=["CHA", "SHD", "DMI"])
        self.assertEqual(self.hits(self.lint()[1], "fan-out"), [])

    def test_fan_out_default_limit_and_disable(self):
        self.set_coupling({})
        self.all_specs(ARC=["CHA", "SHD", "DMI", "ARC", "XXX", "YYY"])
        self.assertFinding(self.lint()[1], "WARN", "arc.md", "fan-out 6 exceeds the limit of 5")
        self.set_coupling({"max_fan_out": None})
        self.assertEqual(self.hits(self.lint()[1], "fan-out"), [])

    # -- cycles
    def test_two_cycle_reported_once(self):
        self.all_specs(ARC=["CHA"], CHA=["ARC"])
        out = self.lint()[1]
        self.assertEqual(self.hits(out, "dependency cycle"), ["WARN  docs/design/combat/arc.md:1  dependency cycle: ARC -> CHA -> ARC"])

    def test_three_cycle_reported_once(self):
        self.all_specs(CHA=["SHD"], SHD=["DMI"], DMI=["CHA"])
        out = self.lint()[1]
        self.assertEqual(self.hits(out, "dependency cycle"),
                         ["WARN  docs/design/combat/cha.md:1  dependency cycle: CHA -> SHD -> DMI -> CHA"])

    def test_acyclic_dependencies_and_unknown_codes_are_silent(self):
        self.all_specs(ARC=["CHA", "SHD"], CHA=["SHD", "ZZZ"])
        self.assertEqual(self.hits(self.lint()[1], "dependency cycle"), [])

    def test_find_cycles_covers_self_loop_and_shared_nodes(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("doclint_under_test", os.path.join(KIT, "tools", "doclint.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        graph = {"A": ["A", "B"], "B": ["A", "C"], "C": ["B"], "D": []}
        self.assertEqual(mod.find_cycles(graph), [("A",), ("A", "B"), ("B", "C")])
        dense = {str(i): [str(j) for j in range(14) if j != i] for i in range(14)}
        self.assertTrue(mod.find_cycles(dense))  # polynomial: returns at once on a dense graph

    # -- report mode
    def test_coupling_report(self):
        self.all_specs(ARC=["CHA", "SHD"], CHA=["ARC"])
        self.spec("SHD", body="- **SHD-R1** Follows ARC-R1 and ARC-R1 again, and CHA-R1. `locked`\n")
        rc, out = self.lint("--coupling")
        self.assertEqual(rc, 0, out)
        self.assertEqual(out, (
            "System  Fan-out  Fan-in  Foreign rule refs  Interface items\n"
            "------  -------  ------  -----------------  ---------------\n"
            "ARC           2       1                  0                1\n"
            "CHA           1       1                  0                1\n"
            "DMI           0       0                  0                1\n"
            "SHD           0       1                  2                1\n"
            "\nCycles: 1\n  ARC -> CHA -> ARC\n"))

    # -- off when not configured
    def test_everything_is_off_without_the_key(self):
        self.set_coupling(None)
        self.all_specs(ARC=["CHA", "SHD", "DMI", "ARC", "XXX", "YYY"], CHA=["ARC"])
        self.spec("ARC", deps=["CHA", "SHD", "DMI", "ARC", "XXX", "YYY"],
                  body="- **ARC-R1** Draw follows CHA-R1 and needs CHA-I9. `locked`\n", extra="- **ARC-I1** Again.\n")
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        for text in ("another system", "fan-out", "dependency cycle", "interface item", "CHA-I9"):
            self.assertEqual(self.hits(out, text), [], out)
        rc, out = self.lint("--coupling")
        self.assertEqual(rc, 2, out)

    def test_spec_template_has_an_interface_section_before_rules(self):
        with open(os.path.join(KIT, "templates", "design", "docs", "templates", "spec.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertLess(text.index("## Intent"), text.index("## Interface"))
        self.assertLess(text.index("## Interface"), text.index("## Rules"))
        self.assertIn("**XXX-I1**", text)

    def test_wayfarer_example_config_has_no_coupling_key(self):
        path = os.path.join(os.path.dirname(KIT), "examples", "wayfarer", "doclint.json")
        with open(path, encoding="utf-8") as f:
            self.assertNotIn("coupling", json.load(f))


class VocabularyTags(ProjectCase):
    """`conflicting`, `needs-build` and `validated` are accepted by the design preset."""

    def test_new_tags_and_status_are_valid(self):
        self.write("docs/CONVENTIONS.md", DESIGN_CONVENTIONS)
        self.write("docs/GLOSSARY.md", GLOSSARY)
        self.write("docs/decisions/combat/archery.md", HISTORY)
        text = SPEC.replace("status: settled", "status: validated") \
                   .replace(EarlyQuantity.ANCHOR, "- **ARC-R2** Reload is slower than draw (ARC-R3, ARC-Q2). `conflicting`\n"
                            "- **ARC-R3** Reload is faster than draw (ARC-R2, ARC-Q2). `conflicting`\n") \
                   + "- **ARC-Q2** Which rule holds? `needs-build`\n"
        self.write("docs/design/combat/archery.md", text)
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertNoFindings(out)


class StylePlugin(ProjectCase):
    preset = "design"

    def setUp(self):
        super().setUp()
        self.write("docs/CONVENTIONS.md", DESIGN_CONVENTIONS)
        self.write("docs/decisions/combat/archery.md", HISTORY)

    def test_long_sentence_and_emoji(self):
        long = " ".join(["word"] * 35) + "."
        self.write("docs/design/combat/archery.md", SPEC + "\n" + long + " Short one.\nStatus ✅ done.\n")
        out = self.lint()[1]
        self.assertFinding(out, "WARN", "archery.md", "style: 35-word sentence")
        self.assertFinding(out, "WARN", "archery.md", "style: emoji")

    def test_bold_density_ignores_ids(self):
        text = SPEC + "\n" + " ".join(["**bold**"] * 10 + ["plain"] * 100) + "\n"
        self.write("docs/design/combat/archery.md", text)
        self.assertFinding(self.lint()[1], "WARN", "archery.md", "bold spans per 100 words")
        rules = SPEC + "\n" + "\n".join("- **ARC-R{}** plain words here for the count. `locked`".format(i)
                                        for i in range(3, 40)) + "\n"
        self.write("docs/design/combat/archery.md", rules)
        self.assertNotIn("bold spans", self.lint()[1])


class BasicPreset(ProjectCase):
    preset = "basic"

    def test_basic_project(self):
        self.write("docs/GLOSSARY.md", "---\ntitle: Glossary\ntype: registry\nupdated: 2026-10-01\n---\n# Glossary\n"
                   "## Retired names\n| Retired | Use instead | Lint pattern |\n|---|---|---|\n| Foo | Bar | `\\bFoo\\b` |\n")
        self.write("docs/guide/setup.md", "---\ntitle: Setup\ntype: doc\nstatus: current\nupdated: 2026-10-01\n---\n"
                   "# Setup\nInstall it. See [glossary](../GLOSSARY.md).\n")
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertNoFindings(out)
        self.write("docs/guide/setup.md", "---\ntitle: Setup\ntype: doc\nstatus: live\nupdated: 2026-10-01\n---\n"
                   "# Setup\nUse Foo.\n")
        self.write("docs/notes.md", "# Notes\n")
        out = self.lint("--verbose")[1]
        self.assertFinding(out, "ERROR", "setup.md:1", "unknown status 'live'")
        self.assertFinding(out, "ERROR", "setup.md", "retired name; use: Bar")
        self.assertIn("notes.md", out)

    def test_basic_map_from_files(self):
        self.write("docs/guide/setup.md", "---\ntitle: Setup\ntype: doc\nstatus: current\nupdated: 2026-10-01\n---\n# Setup\n")
        out = self.lint("--map")[1]
        self.assertIn("| Setup | doc | current | 2026-10-01 | [`guide/setup.md`](guide/setup.md) |", out)


class Playbooks(unittest.TestCase):
    """Playbook and run-log templates lint clean as real docs in both presets; statuses are per type."""

    def project(self, preset):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        shutil.copytree(os.path.join(KIT, "tools"), os.path.join(root, "tools"))
        shutil.copy(os.path.join(KIT, "presets", preset + ".json"), os.path.join(root, "tools", "doclint.json"))
        tdir = os.path.join(KIT, "templates", preset, "docs", "templates")
        for src, dst in (("playbook.md", "docs/playbooks/deploy.md"), ("run-log.md", "docs/playbooks/runs/deploy.md")):
            with open(os.path.join(tdir, src), encoding="utf-8") as f:
                text = f.read().replace("YYYY-MM-DD", "2026-10-31").replace("<file>", "deploy")
            path = os.path.join(root, dst)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        if preset == "design":
            shutil.copy(os.path.join(KIT, "templates", "design", "docs", "CONVENTIONS.md"),
                        os.path.join(root, "docs", "CONVENTIONS.md"))
        return root

    def lint(self, root):
        p = subprocess.run([sys.executable, "tools/doclint.py"], cwd=root, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True)
        self.assertNotIn("Traceback", p.stderr, p.stderr)
        return p.returncode, p.stdout

    def edit(self, root, rel, old, new):
        path = os.path.join(root, rel)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new))

    def test_templates_clean_in_both_presets(self):
        for preset in ("basic", "design"):
            rc, out = self.lint(self.project(preset))
            self.assertEqual(rc, 0, preset + "\n" + out)
            self.assertIn("0 errors, 0 warnings", out)

    def test_design_statuses_are_per_type(self):
        root = self.project("design")
        self.edit(root, "docs/playbooks/deploy.md", "status: draft", "status: settled")
        rc, out = self.lint(root)
        self.assertIn("unknown status 'settled'", out)

    def test_playbook_needs_runs_and_valid_last_run(self):
        root = self.project("basic")
        self.edit(root, "docs/playbooks/deploy.md", "runs: 1\n", "")
        self.edit(root, "docs/playbooks/deploy.md", "last_run: 2026-10-31", "last_run: yesterday")
        out = self.lint(root)[1]
        self.assertIn("missing 'runs'", out)
        self.assertIn("'last_run' must be YYYY-MM-DD", out)

    def test_first_person_inside_inline_code_is_ignored(self):
        root = self.project("basic")
        self.edit(root, "docs/playbooks/deploy.md", "## Gotchas", "The pattern `my` and `I think` are examples.\n\n## Gotchas")
        self.assertEqual(self.lint(root)[0], 0)
        self.edit(root, "docs/playbooks/deploy.md", "are examples.", "are examples, my friend.")
        self.assertIn("first person", self.lint(root)[1])

    def test_map_types_filter(self):
        root = self.project("basic")
        cfg_path = os.path.join(root, "tools", "doclint.json")
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        cfg["map"]["types"] = ["playbook"]
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
        out = subprocess.run([sys.executable, "tools/doclint.py", "--map"], cwd=root, stdout=subprocess.PIPE,
                             universal_newlines=True).stdout
        self.assertIn("playbooks/deploy.md", out)
        self.assertNotIn("runs/deploy.md", out)

    def test_run_log_allows_first_person(self):
        root = self.project("basic")
        self.edit(root, "docs/playbooks/runs/deploy.md", "<attempt>", "I tried my first idea")
        self.assertEqual(self.lint(root)[0], 0)


class Scaffold(unittest.TestCase):
    """A fresh project from each template set must lint clean once dates are filled in."""

    def scaffold(self, preset):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        shutil.copytree(os.path.join(KIT, "templates", preset), root, dirs_exist_ok=True)
        shutil.copytree(os.path.join(KIT, "tools"), os.path.join(root, "tools"), dirs_exist_ok=True)
        shutil.copy(os.path.join(KIT, "presets", preset + ".json"), os.path.join(root, "tools", "doclint.json"))
        for base, _, files in os.walk(root):
            for f in files:
                if f.endswith(".md"):
                    p = os.path.join(base, f)
                    with open(p, encoding="utf-8") as fh:
                        t = fh.read()
                    with open(p, "w", encoding="utf-8") as fh:
                        fh.write(t.replace("YYYY-MM-DD", "2026-10-31"))
        p = subprocess.run([sys.executable, "tools/doclint.py"], cwd=root, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, universal_newlines=True)
        return p.returncode, p.stdout + p.stderr

    def test_basic_scaffold_is_clean(self):
        rc, out = self.scaffold("basic")
        self.assertEqual(rc, 0, out)
        self.assertIn("0 errors, 0 warnings", out)

    def test_design_scaffold_is_clean(self):
        rc, out = self.scaffold("design")
        self.assertEqual(rc, 0, out)
        self.assertIn("0 errors, 0 warnings", out)


if __name__ == "__main__":
    unittest.main()
