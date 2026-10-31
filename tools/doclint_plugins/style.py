"""doclint plugin 'style': mechanical writing checks for persistent docs. Warnings only.

Config (plugin_config.style):
  types                   doc types to check (default: none)
  max_sentence_words      warn on longer sentences (default 30; 0 disables)
  max_bold_per_100_words  warn when a file's bold density exceeds this (default 4; 0 disables).
                          Bold IDs (e.g. **ARC-R1**) don't count.
  emoji_in_prose          warn on emoji/symbol markers in prose lines (default true)

Skips headings, table rows, code fences and sections marked "exempt" in the core config.
"""
import re

CONFIG = {}

BOLD = re.compile(r"\*\*([^*]+)\*\*")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[*`])")
MARKUP = re.compile(r"`[^`]*`|\[([^\]]*)\]\([^)]*\)|[*_]")
EMOJI = re.compile("[☀-➿⬀-⯿\U0001F000-\U0001FAFF✅❌⭐]")


def _setting(key, default):
    return CONFIG.get(key, default)


def check_migrated(project, doc, report):
    if doc.fm.get("type") not in _setting("types", []):
        return
    max_words = _setting("max_sentence_words", 30)
    max_bold = _setting("max_bold_per_100_words", 4)
    emoji_on = _setting("emoji_in_prose", True)
    exempt = {s["heading"] for s in project.cfg["sections"].values() if s.get("exempt")}
    id_rx = re.compile(r"^[A-Z]+(-[A-Z]+)?-[A-Z]?\d+$")
    words_total, bold_total = 0, 0
    for n, line, fence, section in doc.walk():
        stripped = line.strip()
        if fence or section in exempt or not stripped or stripped.startswith(("#", "|", ">")):
            continue
        bold_total += sum(1 for b in BOLD.findall(line) if not id_rx.match(b.strip()))
        plain = MARKUP.sub(lambda m: m.group(1) or " ", stripped)
        plain = re.sub(r"^([-*+]|\d+[.)])\s+", "", plain)
        words_total += len(re.findall(r"\w+", plain))
        if emoji_on and EMOJI.search(stripped):
            report.warn(doc.path, n, "style: emoji or symbol marker in prose; put status in tags or front matter")
        if max_words:
            for sentence in SENTENCE_END.split(plain):
                count = len(re.findall(r"\w+", sentence))
                if count > max_words:
                    report.warn(doc.path, n, "style: {}-word sentence (limit {}); split it".format(count, max_words))
    if max_bold and words_total >= 100:
        density = bold_total * 100.0 / words_total
        if density > max_bold:
            report.warn(doc.path, 0, "style: {:.1f} bold spans per 100 words (limit {}); bold only defined terms at first use".format(
                density, max_bold))
