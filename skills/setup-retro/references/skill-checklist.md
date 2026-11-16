# Skill checklist

Run `python scripts/check_skills.py <skills-dir> [name ...]` first. It covers the mechanical rules: name equals folder, description under 1,024 characters without angle brackets, word count, resolving links, no README.md. The rest is judgment:

**Description**
- Says what the skill does and when, key use case first, with phrases the user would say.
- Covers the cases where it must fire, including repeat-shaped tasks and inputs embedded in other artifacts.
- Names a boundary where another skill overlaps ("for X use skill Y").
- Check `disable-model-invocation`: the skill then never auto-triggers and runs only as `/name`.

**Body**
- First screen holds what matters on every use.
- Steps are numbered, specific and checkable; rules are positive; one term per concept.
- Necessity test per line: would a capable agent do this without the line? If yes, cut it.
- A rule that must always hold moves to a script or the lint.
- Detail needed only sometimes moves to `references/`, linked from the step that needs it.
- Known failures get a short troubleshooting entry.

**Set**
- Each rule has one owning skill; the others point to it.
- Merge, split and rename are proposals with a reason.
