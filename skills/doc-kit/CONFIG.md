# doclint configuration reference

`tools/doclint.json`. Keys starting with `_` are comments. Paths are relative to `root` unless noted; "docs-relative" means relative to `docs_dir`. Start from `kit/presets/basic.json` or `kit/presets/design.json`.

## Discovery

| Key | Meaning | Default |
|---|---|---|
| `root` | Repository root, relative to the config file | `".."` |
| `docs_dir` | Docs folder | `"docs"` |
| `skip_dirs` | First-level folders under `docs_dir` that are not scanned | `["archive", "templates"]` |
| `expect_front_matter.include` | Docs-relative prefixes whose files should have front matter; others are reported as "not yet migrated" | `[]` |
| `expect_front_matter.exclude_regex` | Regex of docs-relative paths exempt from that | `null` |

Every `.md` under `root` is scanned (hidden folders excluded). Files without front matter get only link and stale-term checks.

## Codes and IDs

| Key | Meaning |
|---|---|
| `codes.file` | Docs-relative file holding the code table (e.g. `CONVENTIONS.md`); `null` for none |
| `codes.pattern` | Regex with two groups (code, path) applied per line of that file |
| `codes.inline` | `{code: docs-relative path}` merged with the table |
| `code_path_prefixes` | Prefixes tried when resolving a code's path (e.g. `["", "design/"]`) |
| `id_scheme` | `code` regex, `rule`/`question`/`interface` letters, `decision_prefix`, `decision_digits`. Default: `ARC-R7`, `ARC-Q2`, `ARC-I1`, `D-ARC-006`. The interface letter is read only when `coupling` is configured |

## Front matter and types

| Key | Meaning |
|---|---|
| `types.<type>.required` | Keys that must be present and non-empty |
| `types.<type>.enums_always` | Enum keys checked even when missing (reports `unknown <key> 'None'`) |
| `types.<type>.id_matches_path` | The file's `id` must map to this file in the code table |
| `types.<type>.enums` | Per-type enum values, overriding `enums` for that type (e.g. playbook statuses in a design project) |
| `enums` | `{key: [allowed values]}`, checked whenever the key is present |
| `date_fields` | Keys that must be `YYYY-MM-DD` |
| `depends_field` | Key listing codes this doc depends on (unknown codes warn) |
| `unique_id_exempt_types` | Types whose `id` may repeat (e.g. decision logs share their spec's code) |
| `decision_log_types` | Types checked as decision logs (heading IDs unique and matching the file code) instead of body checks |
| `mirror` | `{types, from, to}`: each file under `from` needs a twin under `to` (warning) |

## Body

| Key | Meaning |
|---|---|
| `sections.<name>` | `{heading, allowed_status, exempt, message}`. `heading` is the lower-cased `## ` line. `allowed_status` errors if the section appears with another status; `exempt` skips prose/ID checks inside it |
| `tags.rule` / `tags.question` | `{types, values}`: each rule/question line must end with exactly one tag. `rule.section_only` maps a section heading to the only tag allowed there (and only there) |
| `prose.types` | Types the prose checks apply to |
| `prose.checks` | Any of `heading_emoji`, `heading_date`, `changelog_heading`, `star`, `strikethrough`, `first_person` (inline code is ignored) |
| `prose.patterns` | `[{regex, level: warn|error, message}]` custom line checks |
| `early_quantity` | `{types, below_layer, pattern, exempt_tag}`: a rule line (one carrying a rule ID) that contains a quantity gets a warning when the document's front-matter `layer` is below `below_layer` (ordered as `enums.layer`) and the line does not end with `exempt_tag`. Off when the key is absent. See below |
| `coupling` | `{types, max_fan_out, parameter_section}`: foreign rule references, interface items, fan-out and cycles (warnings). Off when the key is absent. See below |
| `word_budget` | `{type: words}` warning threshold (exempt sections excluded) |

**`early_quantity`** keeps numbers out of rules above L3 (state an ordering or a tier, or tag the rule `placeholder`). Inline code, link targets and section references are ignored.

| Key | Meaning | Default |
|---|---|---|
| `types` | Doc types checked | `["spec"]` |
| `below_layer` | Layer value (from `enums.layer`) from which quantities are allowed; documents on an earlier layer are checked. Required | none |
| `pattern` | Regex for a quantity | A decimal number, or a number followed by `%` or a unit (`s`, `min`, `h`, `m`, `km`, `kg`, `hp`, `x` and similar). Rule IDs, dates, version numbers and bare integers do not match |
| `exempt_tag` | Closing rule tag that exempts the line | `placeholder` |

**`coupling`** keeps systems loosely coupled: a spec depends on another system's interface, not on its rules. Also `--coupling` (report mode). Warnings unless noted; existing dependencies are made visible, not blocked.

| Key | Meaning | Default |
|---|---|---|
| `types` | Doc types checked; also the nodes of the dependency graph | `["spec"]` |
| `max_fan_out` | Warn when a document lists more than this many distinct codes in `depends_field`; `null` turns the check off | `5` |
| `parameter_section` | Lower-cased heading of the parameters section | `"## parameters"` |

| Check | Fires on |
|---|---|
| Foreign rule reference | A rule line, or a non-blank line in `parameter_section`, citing a rule ID whose code differs from the document's `id`. Open-question lines, exempt sections (working notes), history lines, fences, inline code and link targets are skipped. Question and interface citations are fine |
| Interface item IDs | `<CODE>-I<n>` list lines (`- **ARC-I1** ...`). A duplicate ID within a document or a code that differs from the file's `id` is an **error**, as for rule IDs. A cited interface item that the target spec does not define is a warning (cited rule and question IDs that do not exist stay errors) |
| Fan-out | Dependency count above `max_fan_out`, on line 1 of the file |
| Cycle | One warning per cycle, on the file of its smallest code, with the path (`ARC -> CHA -> ARC`). Edges to codes without a document of a configured type are ignored. In a dense graph every edge on a cycle is covered by the shortest cycle through it, so not every elementary cycle is listed |

`python tools/doclint.py --coupling` prints, per system in code order, the fan-out, fan-in, foreign rule references made and interface items defined, then the cycles. Plain text; exit code 2 when `coupling` is not configured.

## Cross-file

| Key | Meaning |
|---|---|
| `stale_terms.file` | One regex per line, optional `=> hint` |
| `stale_terms.retired_names` | `{file, heading, use_column, pattern_column}`: a glossary table whose pattern cells (in backticks) become checked terms |
| `stale_terms.exempt` / `refs.exempt` | `{exclude: [...], include: [...]}` docs-relative paths; entries ending in `/` are prefixes. `include` re-admits |
| `history_line` | Regex for dated changelog lines that stale/ref checks skip |
| `index` | `{file, question_tags}`: questions with these tags must appear in the index file |

## Map (`--map`)

| Key | Meaning |
|---|---|
| `map.source` | `codes` (one row per code, shows missing/unmigrated owners) or `files` (one row per file with front matter) |
| `map.columns` | `[[header, field], ...]`; fields: `code`, `link` or any front-matter key |
| `map.sort` | Fields to sort by |
| `map.types` | Only these doc types appear (`source: files` only); default all |

## Plugins

`plugins: ["style", ...]` loads `tools/doclint_plugins/<name>.py`; `plugin_config.<name>` becomes its `CONFIG`. Hooks, all optional:

| Hook | Called |
|---|---|
| `check_any(project, doc, report)` | Every file |
| `check_migrated(project, doc, report)` | Every file with front matter and a known, non-decision-log type |
| `check_project(project, report)` | Once at the end |
| `summary(project) -> str` | Appended to the summary line |
| `verbose(project) -> str` | Printed with `--verbose` |

`doc.walk()` yields `(line_no, line, in_fence, section)`; `project.rx_rule_line`, `rx_question_line`, `fmt_rule`, `fmt_question`, `codes`, `cfg` and `extra` (a dict for plugin state) are available. See `examples/wayfarer/doclint_plugins/wayfarer.py`.

**Prefer config over plugins.** A plugin is for a check that config can't express; most project rules fit `prose.patterns`.
