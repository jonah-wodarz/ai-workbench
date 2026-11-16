# Changelog

Versions follow [SemVer](https://semver.org/). While the version is 0.x, any release may change behaviour.

## 0.1.0 — First public pre-release
The five skills as one bundle, installable as a Claude Code plugin or one skill folder at a time.

- **Added**
  - `skills/layered-design-facilitation` — design in layers L0 to L4, top-down by default, with the moves park, probe and ascend.
  - `skills/design-capture` — design talk becomes specs, a decision history and open questions.
  - `skills/structured-project-docs` — a docs tree of small single-topic files.
  - `skills/doc-kit` — `doclint` 0.5.0 with the `basic` and `design` presets, templates, the generated system map page and an example project.
  - `skills/handoff` — HTML pages built from data: overview, decision brief, explainer.
  - `.claude-plugin/` — plugin manifest and a one-plugin marketplace.
  - `hooks/` — a session-start hook that puts a routing table (which skill for which work) into every Claude Code session.
