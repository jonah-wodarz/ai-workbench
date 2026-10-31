# doc-kit

Config-driven lint (`doclint`) and templates for multi-file Markdown documentation. Also a Claude skill: see [`SKILL.md`](SKILL.md).

- **Use it:** copy `kit/tools/` and a preset from `kit/presets/` into a project as `tools/` and `tools/doclint.json`, then run `python tools/doclint.py`.
- **Configure it:** [`CONFIG.md`](CONFIG.md).
- **Test it:** `python -m unittest discover -s tests` (Python 3.8+ for the tests; the lint itself runs on 3.7+).
- **Regression against Wayfarer:** `python tests/regression_wayfarer.py <wayfarer-copy> .`
- **Changes:** [`CHANGELOG.md`](CHANGELOG.md).
