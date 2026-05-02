#!/usr/bin/env python3
"""
build.py — Build the interactive Learning Hub (single-page app).

Reads markdown sources from ./sources/ and produces:
  - content/*.html       (rendered article fragments, no shell)
  - manifest.json        (navigation tree + anchors + ordered list)
  - index.html           (the SPA shell)
  - assets/style.css     (theme)
  - assets/app.js        (router + sidebar + progress + search + TOC)

Usage:
    pip install markdown pygments
    python build.py
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

import markdown


HUB = Path(__file__).resolve().parent
SOURCES = HUB / "sources"
CONTENT = HUB / "content"
ASSETS = HUB / "assets"

# Populated by render_source as we walk each markdown file.
# Key: source path relative to SOURCES, POSIX form (e.g. "system-design/README.md")
# Value: SPA item_id (e.g. "sd/overview")
LINK_MAP: dict[str, str] = {}
# (rendered_html_path, source_path) for the post-render link-rewrite pass.
RENDERED_PAGES: list[tuple[Path, Path]] = []

MD_EXT = [
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.toc",
    "markdown.extensions.sane_lists",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
]


# --------------------------------------------------------------------------- #
# Markdown rendering & TOC extraction
# --------------------------------------------------------------------------- #

class HeadingExtractor(HTMLParser):
    """Pull (level, id, text) for h2/h3 headings from rendered HTML."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headings = []
        self._capture = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag in ("h2", "h3"):
            attrs_d = dict(attrs)
            self._capture = (int(tag[1]), attrs_d.get("id", ""))
            self._buf = []

    def handle_endtag(self, tag):
        if tag in ("h2", "h3") and self._capture:
            level, hid = self._capture
            text = "".join(self._buf).strip()
            if hid:
                self.headings.append({"level": level, "id": hid, "text": text})
            self._capture = None
            self._buf = []

    def handle_data(self, data):
        if self._capture is not None:
            self._buf.append(data)


def render_md(text: str):
    md = markdown.Markdown(extensions=MD_EXT, output_format="html5")
    html = md.convert(text)
    extractor = HeadingExtractor()
    extractor.feed(html)
    return html, extractor.headings


def title_from_md(text: str, fallback: str) -> str:
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return (m.group(1).strip() if m else fallback).replace("`", "")


def first_paragraph(text: str, limit: int = 220) -> str:
    """Get a short summary from the first non-heading paragraph."""
    body = re.sub(r"^#.*?$", "", text, count=1, flags=re.MULTILINE).strip()
    parts = re.split(r"\n\s*\n", body)
    for part in parts:
        cleaned = part.strip()
        if not cleaned or cleaned.startswith(("#", ">", "```", "|", "-", "*")):
            continue
        cleaned = re.sub(r"[*_`]", "", cleaned)
        cleaned = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        if len(cleaned) > limit:
            cleaned = cleaned[: limit - 1].rsplit(" ", 1)[0] + "…"
        return cleaned
    return ""


# --------------------------------------------------------------------------- #
# Source -> manifest items
# --------------------------------------------------------------------------- #

def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def render_source(src: Path, item_id: str, default_title: str, tag: str = ""):
    text = src.read_text(encoding="utf-8")
    html, headings = render_md(text)
    title = title_from_md(text, default_title)
    summary = first_paragraph(text)

    # Reading time estimate (technical prose ≈ 220 wpm).
    word_count = len(re.findall(r"\b\w+\b", text))
    read_min = max(1, round(word_count / 220))

    rel_out = Path("content") / (item_id + ".html")
    out = HUB / rel_out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    try:
        src_rel = src.resolve().relative_to(SOURCES).as_posix()
        LINK_MAP[src_rel] = item_id
    except ValueError:
        pass
    RENDERED_PAGES.append((out, src.resolve()))

    return {
        "id": item_id,
        "title": title,
        "src": rel_out.as_posix(),
        "anchors": headings,
        "summary": summary,
        "tag": tag,
        "words": word_count,
        "read_min": read_min,
    }


# --------------------------------------------------------------------------- #
# Rewrite cross-document .md links into SPA hash routes
# --------------------------------------------------------------------------- #

_HREF_RE = re.compile(r'href="([^"]+)"')
_SCHEME_RE = re.compile(r'^(?:[a-z][a-z0-9+.\-]*:|#|//)', re.IGNORECASE)


def resolve_href(href: str, src_dir: Path) -> str | None:
    """Resolve a relative href found in a rendered fragment.

    Returns a new SPA hash href (e.g. '#/sd/5min/caching#anchor') when the
    target is a known source document, or None when the href should be left
    untouched (external URL, in-page anchor, unknown target).
    """
    if not href or _SCHEME_RE.match(href):
        return None

    # Split fragment / query off the path.
    anchor = ""
    if "#" in href:
        href, anchor = href.split("#", 1)
    if "?" in href:
        href = href.split("?", 1)[0]
    href = unquote(href)
    if not href:
        return None

    try:
        target = (src_dir / href).resolve()
        rel = target.relative_to(SOURCES).as_posix()
    except (ValueError, OSError):
        return None

    item_id = LINK_MAP.get(rel)
    if item_id is None:
        # Directory-style link → try its README.md (and a slash-stripped variant).
        for candidate in (rel.rstrip("/") + "/README.md", rel + "/README.md"):
            if candidate in LINK_MAP:
                item_id = LINK_MAP[candidate]
                break
    if item_id is None:
        return None

    return f"#/{item_id}#{anchor}" if anchor else f"#/{item_id}"


def rewrite_links() -> int:
    """Walk every rendered fragment and rewrite known .md hrefs.

    Returns the number of substitutions made (for logging).
    """
    total = 0
    for out_path, src in RENDERED_PAGES:
        src_dir = src.parent
        html = out_path.read_text(encoding="utf-8")
        page_count = 0

        def _sub(match: re.Match) -> str:
            nonlocal page_count
            new_href = resolve_href(match.group(1), src_dir)
            if new_href is None:
                return match.group(0)
            page_count += 1
            return f'href="{new_href}"'

        new_html = _HREF_RE.sub(_sub, html)
        if page_count:
            out_path.write_text(new_html, encoding="utf-8")
            total += page_count
    return total


def build_manifest():
    tracks = []
    flat = []  # ordered list for prev/next

    # -- Roadmap ----------------------------------------------------------- #
    roadmap_src = SOURCES / "roadmap.md"
    roadmap_track = {"id": "roadmap", "title": "Roadmap", "icon": "🗺️", "groups": []}
    if roadmap_src.exists():
        item = render_source(roadmap_src, "roadmap/main", "Roadmap", tag="plan")
        roadmap_track["groups"].append({"title": "Plan", "items": [item]})
        flat.append(item)
    tracks.append(roadmap_track)

    # -- DSA --------------------------------------------------------------- #
    dsa_track = {"id": "dsa", "title": "DSA & Problem Solving", "icon": "🧠", "groups": []}
    dsa_src = SOURCES / "dsa.md"
    if dsa_src.exists():
        item = render_source(dsa_src, "dsa/full", "DSA Curriculum", tag="curriculum")
        dsa_track["groups"].append({"title": "Curriculum", "items": [item]})
        flat.append(item)
    tracks.append(dsa_track)

    # -- System Design ----------------------------------------------------- #
    sd_track = {"id": "sd", "title": "System Design", "icon": "🏗️", "groups": []}
    sd_src = SOURCES / "system-design"

    overview_items = []
    if (sd_src / "README.md").exists():
        overview_items.append(render_source(sd_src / "README.md", "sd/overview",
                                            "System Design — Overview", tag="overview"))

    tier_files = [
        ("01-beginner.md",     "sd/tier-beginner",     "Beginner",     "tier-1"),
        ("02-intermediate.md", "sd/tier-intermediate", "Intermediate", "tier-2"),
        ("03-advanced.md",     "sd/tier-advanced",     "Advanced",     "tier-3"),
        ("04-expert.md",       "sd/tier-expert",       "Expert",       "tier-4"),
    ]
    tier_items = []
    for fname, item_id, deflt, tag in tier_files:
        f = sd_src / fname
        if f.exists():
            tier_items.append(render_source(f, item_id, deflt, tag=tag))

    deepdive_items = []
    if (sd_src / "tradeoffs-deep-dive.md").exists():
        deepdive_items.append(render_source(sd_src / "tradeoffs-deep-dive.md",
                                            "sd/tradeoffs", "Trade-offs Deep Dive",
                                            tag="deep-dive"))

    ref_items = []
    for fname, item_id, deflt in [
        ("books-and-courses.md", "sd/books",  "Books & Courses"),
        ("github-repos.md",      "sd/repos",  "GitHub Repos"),
        ("seminal-papers.md",    "sd/papers", "Seminal Papers"),
    ]:
        f = sd_src / fname
        if f.exists():
            ref_items.append(render_source(f, item_id, deflt, tag="reference"))

    five_dir = sd_src / "5-minute-reads"
    five_items = []
    if five_dir.exists():
        if (five_dir / "README.md").exists():
            five_items.append(render_source(five_dir / "README.md",
                                            "sd/5min/index",
                                            "5-Minute Reads — Index",
                                            tag="index"))
        for f in sorted(five_dir.glob("*.md")):
            if f.name.lower() == "readme.md":
                continue
            stem = f.stem  # 01-what-is-system-design
            short = re.sub(r"^\d+-", "", stem)
            five_items.append(render_source(f, f"sd/5min/{short}",
                                            stem.replace("-", " ").title(),
                                            tag="5-min"))

    if overview_items:
        sd_track["groups"].append({"title": "Overview", "items": overview_items})
        flat.extend(overview_items)
    if tier_items:
        sd_track["groups"].append({"title": "Tiers", "items": tier_items})
        flat.extend(tier_items)
    if deepdive_items:
        sd_track["groups"].append({"title": "Deep Dive", "items": deepdive_items})
        flat.extend(deepdive_items)
    if five_items:
        sd_track["groups"].append({"title": "5-Minute Reads", "items": five_items})
        flat.extend(five_items)
    if ref_items:
        sd_track["groups"].append({"title": "References", "items": ref_items})
        flat.extend(ref_items)
    tracks.append(sd_track)

    # Order index for prev/next
    for i, it in enumerate(flat):
        it["order"] = i
        it["prev"] = flat[i - 1]["id"] if i > 0 else None
        it["next"] = flat[i + 1]["id"] if i < len(flat) - 1 else None

    return {"tracks": tracks, "flat": flat}


# --------------------------------------------------------------------------- #
# Static assets (CSS / JS / Shell)
# --------------------------------------------------------------------------- #

CSS = r"""
:root {
  --bg: #0d1117;
  --bg-elev: #161b22;
  --bg-elev-2: #1c2230;
  --border: #30363d;
  --text: #e6edf3;
  --text-dim: #8b949e;
  --link: #58a6ff;
  --link-hover: #79c0ff;
  --accent: #f78166;
  --good: #3fb950;
  --warn: #d29922;
  --bad: #f85149;
  --code-bg: #1c2230;
  --tag-bg: #21262d;
  --shadow: 0 6px 24px rgba(0,0,0,.35);
  --max-content: 920px;
}
[data-theme="light"] {
  --bg: #ffffff;
  --bg-elev: #f6f8fa;
  --bg-elev-2: #eaeef2;
  --border: #d0d7de;
  --text: #1f2328;
  --text-dim: #59636e;
  --link: #0969da;
  --link-hover: #0550ae;
  --accent: #cf222e;
  --good: #1a7f37;
  --warn: #9a6700;
  --bad: #cf222e;
  --code-bg: #f6f8fa;
  --tag-bg: #eaeef2;
  --shadow: 0 6px 24px rgba(0,0,0,.10);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font: 15px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  min-height: 100vh;
}

/* topbar */
.topbar {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 18px;
  background: var(--bg-elev);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(8px);
}
.brand {
  font-weight: 700;
  font-size: 16px;
  color: var(--text);
  text-decoration: none;
  flex-shrink: 0;
}
.brand:hover { color: var(--link); }
.search {
  flex: 1;
  max-width: 480px;
  position: relative;
}
.search input {
  width: 100%;
  background: var(--bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px 8px 34px;
  font: inherit;
  outline: none;
  transition: border-color .15s, box-shadow .15s;
}
.search input:focus {
  border-color: var(--link);
  box-shadow: 0 0 0 3px rgba(88,166,255,.15);
}
.search::before {
  content: "🔍";
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  opacity: .7;
}
.kbd {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--tag-bg);
  border: 1px solid var(--border);
  font: 12px ui-monospace, monospace;
  color: var(--text-dim);
}
.topbar .progress-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 12px;
  color: var(--text-dim);
}
.progress-pill .bar {
  width: 70px;
  height: 6px;
  background: var(--bg-elev-2);
  border-radius: 3px;
  overflow: hidden;
  position: relative;
}
.progress-pill .bar > span {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: linear-gradient(90deg, var(--good), var(--link));
  transition: width .3s;
}
.icon-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 14px;
  cursor: pointer;
  transition: background .15s;
}
.icon-btn:hover { background: var(--bg-elev-2); }

/* layout */
.layout {
  display: grid;
  grid-template-columns: 280px 1fr 220px;
  gap: 0;
  min-height: calc(100vh - 56px);
}
.sidebar {
  border-right: 1px solid var(--border);
  background: var(--bg);
  height: calc(100vh - 56px);
  position: sticky;
  top: 56px;
  overflow-y: auto;
  padding: 14px 8px;
}
.sidebar::-webkit-scrollbar { width: 8px; }
.sidebar::-webkit-scrollbar-thumb { background: var(--bg-elev-2); border-radius: 4px; }

.sidebar .track {
  margin-bottom: 6px;
}
.sidebar .track-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  user-select: none;
  font-weight: 600;
  font-size: 13px;
  color: var(--text);
}
.sidebar .track-header:hover { background: var(--bg-elev); }
.sidebar .track-header .chev {
  display: inline-block;
  transition: transform .15s;
  color: var(--text-dim);
  font-size: 10px;
}
.sidebar .track[data-open="true"] .chev { transform: rotate(90deg); }
.sidebar .track-progress {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-dim);
  font-variant-numeric: tabular-nums;
}
.sidebar .track-body {
  display: none;
  padding: 4px 0 8px 6px;
}
.sidebar .track[data-open="true"] .track-body { display: block; }
.sidebar .group-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .8px;
  color: var(--text-dim);
  padding: 8px 12px 4px;
}
.sidebar a.item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  color: var(--text);
  text-decoration: none;
  border-radius: 6px;
  font-size: 13.5px;
  line-height: 1.4;
  margin: 1px 0;
}
.sidebar a.item:hover { background: var(--bg-elev); color: var(--link); }
.sidebar a.item.active {
  background: var(--bg-elev-2);
  color: var(--link);
  font-weight: 600;
}
.sidebar a.item .check {
  font-size: 11px;
  color: var(--good);
  width: 14px;
  flex-shrink: 0;
}
.sidebar a.item .check:empty::before { content: "○"; color: var(--text-dim); opacity: .35; }
.sidebar a.item.done .check::before { content: "●"; }
.sidebar .empty-search {
  padding: 12px;
  color: var(--text-dim);
  font-size: 13px;
  font-style: italic;
}

/* main */
.content {
  padding: 26px 32px 80px;
  max-width: var(--max-content);
  width: 100%;
  margin: 0 auto;
}
.breadcrumb {
  font-size: 13px;
  color: var(--text-dim);
  margin-bottom: 14px;
}
.breadcrumb a { color: var(--text-dim); text-decoration: none; }
.breadcrumb a:hover { color: var(--link); }
.breadcrumb .sep { margin: 0 6px; opacity: .5; }

.page-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 18px;
  flex-wrap: wrap;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 7px 14px;
  border-radius: 8px;
  cursor: pointer;
  text-decoration: none;
  font: inherit;
  font-size: 13px;
  transition: background .15s, border-color .15s;
}
.btn:hover { background: var(--bg-elev-2); border-color: var(--text-dim); }
.btn.primary {
  background: var(--link);
  border-color: var(--link);
  color: #0d1117;
  font-weight: 600;
}
.btn.primary:hover { background: var(--link-hover); }
.btn.done {
  background: var(--good);
  border-color: var(--good);
  color: #0d1117;
  font-weight: 600;
}
.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--tag-bg);
  border: 1px solid var(--border);
  color: var(--text-dim);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .5px;
}

/* article */
.md h1 { font-size: 28px; margin-top: 0; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
.md h2 { font-size: 22px; margin-top: 36px; padding-bottom: 6px; border-bottom: 1px solid var(--border); scroll-margin-top: 80px; }
.md h3 { font-size: 17px; margin-top: 26px; scroll-margin-top: 80px; }
.md h4 { font-size: 15px; margin-top: 20px; color: var(--text-dim); }
.md p { margin: 12px 0; }
.md a { color: var(--link); }
.md a:hover { color: var(--link-hover); }
.md hr { border: 0; border-top: 1px solid var(--border); margin: 28px 0; }
.md ul, .md ol { padding-left: 26px; }
.md li { margin: 4px 0; }
.md blockquote {
  border-left: 3px solid var(--accent);
  background: var(--bg-elev);
  padding: 8px 14px;
  margin: 14px 0;
  color: var(--text-dim);
  border-radius: 0 6px 6px 0;
}
.md table {
  border-collapse: collapse;
  margin: 16px 0;
  display: block;
  overflow-x: auto;
  width: 100%;
}
.md th, .md td {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
  vertical-align: top;
}
.md th { background: var(--bg-elev); }
.md tr:nth-child(even) td { background: var(--bg-elev); }
.md code {
  background: var(--code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font: 13px ui-monospace, "SF Mono", Consolas, monospace;
  color: var(--accent);
}
.md pre {
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  overflow-x: auto;
  font: 13px ui-monospace, "SF Mono", Consolas, monospace;
  line-height: 1.5;
}
.md pre code { background: transparent; padding: 0; color: var(--text); }

/* codehilite tokens (Pygments) */
.codehilite .k, .codehilite .kd, .codehilite .kn, .codehilite .kr { color: #ff7b72; }
.codehilite .s, .codehilite .s1, .codehilite .s2, .codehilite .sd { color: #a5d6ff; }
.codehilite .c, .codehilite .c1, .codehilite .cm { color: var(--text-dim); font-style: italic; }
.codehilite .nf, .codehilite .nx, .codehilite .nc { color: #d2a8ff; }
.codehilite .mi, .codehilite .mf, .codehilite .mb { color: #79c0ff; }
.codehilite .o, .codehilite .p { color: var(--text-dim); }
.codehilite .nb, .codehilite .bp { color: #ffa657; }

/* prev / next */
.prevnext {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 40px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}
.prevnext a {
  display: block;
  padding: 12px 16px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 10px;
  text-decoration: none;
  color: var(--text);
  transition: border-color .15s, transform .15s;
}
.prevnext a:hover { border-color: var(--link); transform: translateY(-1px); }
.prevnext .label { font-size: 11px; text-transform: uppercase; letter-spacing: .8px; color: var(--text-dim); }
.prevnext .title { font-weight: 600; margin-top: 4px; }
.prevnext .next { text-align: right; }

/* TOC right rail */
.toc-rail {
  position: sticky;
  top: 56px;
  height: calc(100vh - 56px);
  overflow-y: auto;
  padding: 26px 14px 80px 4px;
  border-left: 1px solid var(--border);
  font-size: 12.5px;
}
.toc-rail h4 {
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: .8px;
  color: var(--text-dim);
  margin: 0 0 8px 8px;
}
.toc-rail a {
  display: block;
  padding: 4px 8px;
  border-radius: 4px;
  color: var(--text-dim);
  text-decoration: none;
  border-left: 2px solid transparent;
  margin-left: 2px;
  line-height: 1.35;
}
.toc-rail a.l3 { padding-left: 18px; font-size: 12px; }
.toc-rail a:hover { color: var(--text); }
.toc-rail a.active {
  color: var(--link);
  border-left-color: var(--link);
  background: var(--bg-elev);
}

/* home dashboard */
.hero {
  background: linear-gradient(135deg, var(--bg-elev), var(--bg-elev-2));
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 28px 30px;
  margin-bottom: 22px;
}
.hero h1 { margin: 0 0 6px; font-size: 30px; }
.hero p { margin: 0; color: var(--text-dim); font-size: 16px; }
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
  margin: 14px 0;
}
.card {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  display: flex;
  flex-direction: column;
}
.card h3 { margin: 0 0 6px; font-size: 16px; }
.card p { margin: 0 0 14px; color: var(--text-dim); font-size: 13.5px; flex: 1; }
.card .progress-line {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: var(--text-dim);
  margin-bottom: 10px;
}
.card .progress-line .bar {
  flex: 1;
  height: 4px;
  background: var(--bg-elev-2);
  border-radius: 2px;
  position: relative;
  overflow: hidden;
}
.card .progress-line .bar > span {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  background: linear-gradient(90deg, var(--good), var(--link));
  transition: width .3s;
}
.card a.go {
  align-self: flex-start;
  font-size: 13px;
  font-weight: 600;
  color: var(--link);
  text-decoration: none;
}
.card a.go:hover { color: var(--link-hover); }
.card.recent { border-color: var(--link); }

.shortcut-table {
  margin-top: 18px;
  font-size: 13px;
  border-collapse: collapse;
}
.shortcut-table td { padding: 4px 10px; }
.shortcut-table td:first-child { color: var(--text-dim); }

/* responsive */
@media (max-width: 1100px) {
  .layout { grid-template-columns: 240px 1fr; }
  .toc-rail { display: none; }
}
@media (max-width: 760px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    position: fixed;
    left: 0; top: 56px;
    width: 280px;
    height: calc(100vh - 56px);
    background: var(--bg);
    transform: translateX(-100%);
    transition: transform .2s;
    z-index: 40;
    box-shadow: var(--shadow);
  }
  body[data-sidebar="open"] .sidebar { transform: translateX(0); }
  .sidebar-toggle { display: inline-flex !important; }
  .topbar .progress-pill { display: none; }
  .content { padding: 18px 16px 60px; }
}
.sidebar-toggle { display: none; }

/* mini animations */
.fade-in { animation: fade .25s ease-out; }
@keyframes fade {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: none; }
}

/* ------- v2 user-friendliness additions ------- */

/* skip link (accessibility) */
.skip-link {
  position: absolute;
  left: -9999px;
  top: 8px;
  background: var(--link);
  color: #fff;
  padding: 8px 14px;
  border-radius: 6px;
  z-index: 200;
  text-decoration: none;
  font-weight: 600;
}
.skip-link:focus { left: 16px; }

/* reading progress bar */
.reading-progress {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: transparent;
  z-index: 60;
  pointer-events: none;
}
.reading-progress > span {
  display: block;
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, var(--good), var(--link));
  transition: width .15s linear;
}

/* meta line under page title */
.page-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 12.5px;
  color: var(--text-dim);
  margin: -6px 0 14px;
}
.page-meta .dot { opacity: .4; }
.page-meta .read-time::before { content: "🕐 "; }
.page-meta .word-count::before { content: "📝 "; }

/* tag color variants by tier / kind */
.tag.tier-1 { background: rgba(63,185,80,.12);  color: var(--good); border-color: rgba(63,185,80,.35); }
.tag.tier-2 { background: rgba(88,166,255,.12); color: var(--link); border-color: rgba(88,166,255,.35); }
.tag.tier-3 { background: rgba(210,153,34,.15); color: var(--warn); border-color: rgba(210,153,34,.35); }
.tag.tier-4 { background: rgba(248,81,73,.12);  color: var(--bad);  border-color: rgba(248,81,73,.35); }
.tag.deep-dive  { background: rgba(247,129,102,.12); color: var(--accent); border-color: rgba(247,129,102,.35); }
.tag.curriculum { background: rgba(88,166,255,.12); color: var(--link);   border-color: rgba(88,166,255,.35); }
.tag.plan       { background: rgba(63,185,80,.12);  color: var(--good);   border-color: rgba(63,185,80,.35); }
.tag.reference  { background: rgba(139,148,158,.15); color: var(--text-dim); }
.tag.\35 -min   { background: rgba(247,129,102,.10); color: var(--accent); border-color: rgba(247,129,102,.30); }
.tag.overview, .tag.index { background: rgba(139,148,158,.18); color: var(--text); }

/* sidebar item meta (small text under title) */
.sidebar a.item .item-meta {
  font-size: 10.5px;
  color: var(--text-dim);
  margin-left: 22px;
  display: block;
  margin-top: 1px;
}
.sidebar a.item.active .item-meta { color: var(--link); opacity: .9; }
.sidebar a.item .title-line {
  display: block;
  white-space: normal;
}

/* group progress bar */
.sidebar .group-bar {
  height: 2px;
  background: var(--bg-elev-2);
  border-radius: 2px;
  margin: 0 12px 6px;
  overflow: hidden;
}
.sidebar .group-bar > span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--good), var(--link));
  transition: width .3s;
}

/* loading spinner overlay */
.loading {
  display: none;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--text-dim);
  font-size: 14px;
  gap: 12px;
}
.loading.active { display: flex; }
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--bg-elev-2);
  border-top-color: var(--link);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* back-to-top floating button */
.back-to-top {
  position: fixed;
  right: 24px;
  bottom: 24px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--bg-elev);
  color: var(--text);
  border: 1px solid var(--border);
  font-size: 20px;
  cursor: pointer;
  z-index: 45;
  opacity: 0;
  pointer-events: none;
  transform: translateY(8px);
  transition: opacity .2s, transform .2s, background .15s;
  box-shadow: var(--shadow);
}
.back-to-top.visible {
  opacity: 1;
  transform: none;
  pointer-events: auto;
}
.back-to-top:hover { background: var(--bg-elev-2); }

/* modal */
.modal {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.modal.open { display: flex; }
.modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,.55);
  backdrop-filter: blur(2px);
  cursor: pointer;
}
.modal-card {
  position: relative;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0 22px 22px;
  max-width: 520px;
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: var(--shadow);
  animation: modalIn .18s ease-out;
}
@keyframes modalIn {
  from { transform: translateY(8px) scale(.97); opacity: 0; }
  to   { transform: none; opacity: 1; }
}
.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  background: var(--bg-elev);
  padding: 16px 0 12px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.modal-head h2 { margin: 0; font-size: 18px; }
.modal-foot {
  font-size: 12px;
  color: var(--text-dim);
  margin: 14px 0 0;
}
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.setting-row:last-child { border-bottom: 0; }
.setting-row strong { font-size: 14px; }
.setting-help { margin: 2px 0 0; font-size: 12px; color: var(--text-dim); }
.btn.danger {
  background: transparent;
  border-color: rgba(248,81,73,.4);
  color: var(--bad);
}
.btn.danger:hover { background: rgba(248,81,73,.10); }

/* toggle switch */
.switch { position: relative; display: inline-block; width: 38px; height: 22px; flex-shrink: 0; }
.switch input { opacity: 0; width: 0; height: 0; }
.switch span {
  position: absolute; cursor: pointer; inset: 0;
  background: var(--bg-elev-2);
  border: 1px solid var(--border);
  border-radius: 22px;
  transition: background .15s;
}
.switch span::before {
  content: "";
  position: absolute;
  height: 16px; width: 16px;
  left: 2px; top: 2px;
  background: var(--text-dim);
  border-radius: 50%;
  transition: transform .15s, background .15s;
}
.switch input:checked + span { background: var(--link); border-color: var(--link); }
.switch input:checked + span::before { transform: translateX(16px); background: #fff; }

/* toast notifications */
.toast-stack {
  position: fixed;
  right: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 110;
  pointer-events: none;
}
.toast {
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-left: 3px solid var(--good);
  color: var(--text);
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  box-shadow: var(--shadow);
  pointer-events: auto;
  animation: toastIn .2s ease-out, toastOut .2s ease-in 2.6s forwards;
  min-width: 200px;
}
.toast.error { border-left-color: var(--bad); }
.toast.info  { border-left-color: var(--link); }
@keyframes toastIn {
  from { transform: translateX(20px); opacity: 0; }
  to   { transform: none; opacity: 1; }
}
@keyframes toastOut {
  to { transform: translateX(20px); opacity: 0; }
}

/* sidebar mobile backdrop */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.4);
  z-index: 39;
  display: none;
}
body[data-sidebar="open"] .sidebar-backdrop { display: block; }

/* improved focus styles for keyboard nav */
:focus-visible {
  outline: 2px solid var(--link);
  outline-offset: 2px;
  border-radius: 4px;
}
.btn:focus-visible, .icon-btn:focus-visible {
  outline-offset: 1px;
}

/* hero CTA refinement (first-time user) */
.hero.welcome {
  background: linear-gradient(135deg, rgba(88,166,255,.18), rgba(63,185,80,.12));
  border-color: rgba(88,166,255,.4);
}
.hero .cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  background: var(--link);
  color: #0d1117;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  font-size: 14px;
}
.hero .cta:hover { background: var(--link-hover); }
.hero .lede {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-dim);
}

/* continue-learning card pinned at top of home */
.continue-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 22px;
  background: var(--bg-elev);
  border: 1px solid var(--border);
  border-left: 4px solid var(--link);
  border-radius: 12px;
  margin-bottom: 22px;
}
.continue-card .ico { font-size: 28px; flex-shrink: 0; }
.continue-card .body { flex: 1; }
.continue-card .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: .8px;
  color: var(--text-dim);
}
.continue-card h3 { margin: 2px 0; font-size: 16px; }
.continue-card .desc { font-size: 13px; color: var(--text-dim); margin: 0; }
.continue-card .btn { flex-shrink: 0; }

/* completion celebration */
.complete-banner {
  background: linear-gradient(135deg, rgba(63,185,80,.18), rgba(88,166,255,.10));
  border: 1px solid rgba(63,185,80,.4);
  border-radius: 10px;
  padding: 12px 16px;
  margin: 18px 0;
  font-size: 14px;
  color: var(--good);
}

/* responsive tweaks */
@media (max-width: 760px) {
  .sidebar-toggle { display: inline-flex !important; }
  .topbar .progress-pill { display: none; }
  #help-btn, #settings-btn { display: none; }
  .content { padding: 18px 14px 60px; }
  .modal-card { max-width: 100%; }
  .back-to-top { right: 14px; bottom: 14px; }
  .continue-card { flex-direction: column; align-items: flex-start; }
}

/* print-friendly */
@media print {
  .topbar, .sidebar, .toc-rail, .back-to-top, .reading-progress,
  .modal, .toast-stack, .page-actions, .prevnext, .sidebar-backdrop { display: none !important; }
  .layout { grid-template-columns: 1fr !important; }
  .content { max-width: 100%; padding: 0; }
  body { background: #fff; color: #000; }
  .md a { color: #000; text-decoration: underline; }
  .md pre, .md code { background: #f4f4f4 !important; color: #000 !important; }
}

/* reduce-motion respect */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .001ms !important;
    transition-duration: .001ms !important;
  }
}
"""

APP_JS = r"""
(() => {
  const LS_DONE = "lh:done";
  const LS_THEME = "lh:theme";
  const LS_RECENT = "lh:recent";
  const LS_OPEN = "lh:open";
  const LS_AUTO_MARK = "lh:auto-mark";

  let manifest = null;
  let byId = new Map();   // id -> item
  let order = [];         // ordered ids
  let currentId = null;
  let scrollSpyObserver = null;
  let autoMarkTimer = null;

  // --- localStorage helpers --- //
  const lsGet = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
  const lsSet = (k, v) => localStorage.setItem(k, JSON.stringify(v));

  function getDone() { return new Set(lsGet(LS_DONE, [])); }
  function setDone(set) { lsSet(LS_DONE, [...set]); }
  function isDone(id) { return getDone().has(id); }
  function toggleDone(id) {
    const s = getDone();
    if (s.has(id)) s.delete(id); else s.add(id);
    setDone(s);
    return s.has(id);
  }

  function getRecent() { return lsGet(LS_RECENT, []); }
  function pushRecent(id) {
    const r = [id, ...getRecent().filter(x => x !== id)].slice(0, 5);
    lsSet(LS_RECENT, r);
  }

  function getOpenTracks() { return new Set(lsGet(LS_OPEN, ["roadmap", "dsa", "sd"])); }
  function setOpenTracks(s) { lsSet(LS_OPEN, [...s]); }

  function getAutoMark() { return !!lsGet(LS_AUTO_MARK, false); }
  function setAutoMark(v) { lsSet(LS_AUTO_MARK, !!v); }

  // --- toast notifications --- //
  function showToast(msg, kind) {
    const stack = document.getElementById("toasts");
    if (!stack) return;
    const el = document.createElement("div");
    el.className = "toast" + (kind ? " " + kind : "");
    el.textContent = msg;
    stack.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }

  // --- modals --- //
  function showModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.add("open");
    m.setAttribute("aria-hidden", "false");
    const focusable = m.querySelector("button, input, [tabindex]");
    if (focusable) focusable.focus();
  }
  function closeModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.remove("open");
    m.setAttribute("aria-hidden", "true");
  }
  function closeAllModals() {
    document.querySelectorAll(".modal.open").forEach(m => closeModal(m.id));
  }
  function isAnyModalOpen() {
    return document.querySelector(".modal.open") !== null;
  }

  // --- theme --- //
  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = t === "light" ? "🌙" : "☀️";
  }
  function toggleTheme() {
    const cur = document.documentElement.dataset.theme || "dark";
    const nxt = cur === "dark" ? "light" : "dark";
    lsSet(LS_THEME, nxt);
    applyTheme(nxt);
  }

  // --- routing --- //
  function parseHash() {
    const h = (location.hash || "").replace(/^#\/?/, "");
    if (!h) return { id: null, anchor: null };
    const [id, anchor] = h.split("#");
    return { id: id || null, anchor: anchor || null };
  }

  function navigate(id, anchor) {
    let h = "#/";
    if (id) h += id;
    if (anchor) h += "#" + anchor;
    if (location.hash !== h) {
      location.hash = h;
    } else {
      route();
    }
  }

  // --- sidebar --- //
  function buildSidebar() {
    const sb = document.getElementById("sidebar");
    sb.innerHTML = "";
    const open = getOpenTracks();
    const done = getDone();

    for (const track of manifest.tracks) {
      const trackEl = document.createElement("div");
      trackEl.className = "track";
      trackEl.dataset.trackId = track.id;
      trackEl.dataset.open = open.has(track.id) ? "true" : "false";

      const header = document.createElement("div");
      header.className = "track-header";

      const trackItems = track.groups.flatMap(g => g.items);
      const doneCount = trackItems.filter(it => done.has(it.id)).length;
      const total = trackItems.length;

      header.innerHTML = `
        <span class="chev">▶</span>
        <span>${track.icon} ${escape(track.title)}</span>
        <span class="track-progress">${doneCount}/${total}</span>
      `;
      header.addEventListener("click", () => {
        const o = getOpenTracks();
        if (trackEl.dataset.open === "true") {
          trackEl.dataset.open = "false";
          o.delete(track.id);
        } else {
          trackEl.dataset.open = "true";
          o.add(track.id);
        }
        setOpenTracks(o);
      });
      trackEl.appendChild(header);

      const body = document.createElement("div");
      body.className = "track-body";

      for (const group of track.groups) {
        if (track.groups.length > 1) {
          const gt = document.createElement("div");
          gt.className = "group-title";
          gt.textContent = group.title;
          body.appendChild(gt);

          // group progress bar
          const gDone = group.items.filter(it => done.has(it.id)).length;
          const gTotal = group.items.length;
          const gPct = gTotal ? Math.round((gDone / gTotal) * 100) : 0;
          const gBar = document.createElement("div");
          gBar.className = "group-bar";
          gBar.dataset.group = `${track.id}::${group.title}`;
          gBar.innerHTML = `<span style="width:${gPct}%"></span>`;
          body.appendChild(gBar);
        }
        for (const it of group.items) {
          const a = document.createElement("a");
          a.className = "item";
          a.href = "#/" + it.id;
          a.dataset.itemId = it.id;
          if (done.has(it.id)) a.classList.add("done");
          if (currentId === it.id) a.classList.add("active");
          const meta = it.read_min ? `<span class="item-meta">${it.read_min} min read</span>` : "";
          a.innerHTML = `<span class="check"></span><span class="title-line">${escape(it.title)}</span>${meta}`;
          body.appendChild(a);
        }
      }

      trackEl.appendChild(body);
      sb.appendChild(trackEl);
    }
  }

  function highlightSidebar() {
    document.querySelectorAll("#sidebar a.item").forEach(a => {
      a.classList.toggle("active", a.dataset.itemId === currentId);
    });
  }

  function refreshSidebarProgress() {
    const done = getDone();
    document.querySelectorAll("#sidebar a.item").forEach(a => {
      a.classList.toggle("done", done.has(a.dataset.itemId));
    });
    document.querySelectorAll("#sidebar .track").forEach(tr => {
      const id = tr.dataset.trackId;
      const track = manifest.tracks.find(t => t.id === id);
      if (!track) return;
      const trackItems = track.groups.flatMap(g => g.items);
      const dn = trackItems.filter(it => done.has(it.id)).length;
      const prog = tr.querySelector(".track-progress");
      if (prog) prog.textContent = `${dn}/${trackItems.length}`;

      // group bars
      for (const g of track.groups) {
        const sel = `[data-group="${id}::${g.title.replace(/"/g, '\\"')}"]`;
        const bar = tr.querySelector(sel + " > span");
        if (bar) {
          const gd = g.items.filter(it => done.has(it.id)).length;
          const gPct = g.items.length ? Math.round((gd / g.items.length) * 100) : 0;
          bar.style.width = gPct + "%";
        }
      }
    });
    refreshTopbarProgress();
  }

  function refreshTopbarProgress() {
    const done = getDone();
    const total = order.length;
    const dn = order.filter(id => done.has(id)).length;
    const pct = total ? Math.round((dn / total) * 100) : 0;
    const pill = document.getElementById("global-progress");
    if (pill) {
      pill.querySelector(".bar > span").style.width = pct + "%";
      pill.querySelector(".pct").textContent = `${dn}/${total} · ${pct}%`;
    }
  }

  // --- search --- //
  function filterSidebar(q) {
    q = q.trim().toLowerCase();
    const sb = document.getElementById("sidebar");
    sb.querySelectorAll(".empty-search").forEach(e => e.remove());
    let anyShown = false;
    sb.querySelectorAll(".track").forEach(tr => {
      let trackHasMatch = false;
      tr.querySelectorAll("a.item").forEach(a => {
        const t = a.textContent.toLowerCase();
        const match = !q || t.includes(q);
        a.style.display = match ? "" : "none";
        if (match) trackHasMatch = true;
      });
      tr.querySelectorAll(".group-title").forEach(g => {
        let next = g.nextElementSibling;
        let any = false;
        while (next && next.classList.contains("item")) {
          if (next.style.display !== "none") { any = true; break; }
          next = next.nextElementSibling;
        }
        g.style.display = any ? "" : "none";
      });
      tr.style.display = trackHasMatch ? "" : "none";
      if (q && trackHasMatch) tr.dataset.open = "true";
      if (trackHasMatch) anyShown = true;
    });
    if (!anyShown) {
      const e = document.createElement("div");
      e.className = "empty-search";
      e.textContent = `No matches for "${q}"`;
      sb.appendChild(e);
    }
  }

  // --- TOC right rail --- //
  function buildTOC(anchors) {
    const rail = document.getElementById("toc-rail");
    if (!anchors || anchors.length === 0) {
      rail.innerHTML = "";
      return;
    }
    const html = ['<h4>On this page</h4>'];
    for (const a of anchors) {
      html.push(`<a href="#/${currentId}#${a.id}" class="l${a.level}" data-anchor="${a.id}">${escape(a.text)}</a>`);
    }
    rail.innerHTML = html.join("");
  }

  function setupScrollSpy(anchors) {
    if (scrollSpyObserver) scrollSpyObserver.disconnect();
    if (!anchors || anchors.length === 0) return;
    const ids = new Set(anchors.map(a => a.id));
    const targets = [];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) targets.push(el);
    });
    if (targets.length === 0) return;
    scrollSpyObserver = new IntersectionObserver(entries => {
      const visible = entries
        .filter(e => e.isIntersecting)
        .sort((a, b) => a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top);
      if (visible.length === 0) return;
      const id = visible[0].target.id;
      document.querySelectorAll("#toc-rail a").forEach(a => {
        a.classList.toggle("active", a.dataset.anchor === id);
      });
    }, { rootMargin: "-80px 0px -65% 0px", threshold: 0.01 });
    targets.forEach(t => scrollSpyObserver.observe(t));
  }

  // --- breadcrumb --- //
  function buildBreadcrumb(item) {
    const bc = document.getElementById("breadcrumb");
    const track = manifest.tracks.find(t => t.groups.some(g => g.items.some(i => i.id === item.id)));
    const group = track ? track.groups.find(g => g.items.some(i => i.id === item.id)) : null;
    const parts = [`<a href="#/">🏠 Home</a>`];
    if (track) parts.push(`<span class="sep">›</span>${track.icon} ${escape(track.title)}`);
    if (group && track && track.groups.length > 1) parts.push(`<span class="sep">›</span>${escape(group.title)}`);
    parts.push(`<span class="sep">›</span>${escape(item.title)}`);
    bc.innerHTML = parts.join("");
  }

  // --- render --- //
  async function fetchFragment(src) {
    const res = await fetch(src + "?_=" + Date.now());
    if (!res.ok) throw new Error("Failed to load: " + src);
    return res.text();
  }

  async function renderItem(id, anchor) {
    const item = byId.get(id);
    const main = document.getElementById("content");
    if (!item) {
      document.title = "Not found · Learning Hub";
      main.innerHTML = `<h1>Not found</h1><p>The page <code>${escape(id)}</code> doesn't exist. <a href="#/">Go home</a>.</p>`;
      currentId = null;
      buildTOC([]);
      updateBackToTop();
      return;
    }

    currentId = id;
    document.title = item.title + " · Learning Hub";
    main.classList.remove("fade-in");
    void main.offsetWidth;
    main.classList.add("fade-in");

    main.innerHTML = `<div class="loading active"><div class="spinner"></div><span>Loading ${escape(item.title)}…</span></div>`;

    try {
      const html = await fetchFragment(item.src);

      const bc = document.createElement("div");
      bc.className = "breadcrumb";
      bc.id = "breadcrumb";

      const actions = makeActions(item);
      const meta = makePageMeta(item);

      const article = document.createElement("article");
      article.className = "md";
      article.innerHTML = html;

      const prevnext = buildPrevNext(item);

      main.innerHTML = "";
      main.appendChild(bc);
      main.appendChild(actions);
      if (meta) main.appendChild(meta);
      main.appendChild(article);
      main.appendChild(prevnext);

      buildBreadcrumb(item);
      buildTOC(item.anchors);
      setupScrollSpy(item.anchors);
      highlightSidebar();
      pushRecent(id);
      armAutoMark(item);

      if (anchor) {
        const el = document.getElementById(anchor);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          window.scrollTo({ top: 0 });
        }
      } else {
        window.scrollTo({ top: 0 });
      }
      updateReadingProgress();
      updateBackToTop();
    } catch (e) {
      main.innerHTML = `<h1>Error loading content</h1><p>${escape(e.message)}</p><p><a href="#/">Go home</a></p>`;
      showToast("Failed to load: " + e.message, "error");
    }
  }

  function makePageMeta(item) {
    const parts = [];
    if (item.read_min) parts.push(`<span class="read-time">${item.read_min} min read</span>`);
    if (item.words)    parts.push(`<span class="word-count">${item.words.toLocaleString()} words</span>`);
    if (parts.length === 0) return null;
    const m = document.createElement("div");
    m.className = "page-meta";
    m.innerHTML = parts.join('<span class="dot">·</span>');
    return m;
  }

  function makeActions(item) {
    const wrap = document.createElement("div");
    wrap.className = "page-actions";

    const done = isDone(item.id);
    const btn = document.createElement("button");
    btn.className = "btn " + (done ? "done" : "primary");
    btn.id = "mark-done-btn";
    btn.innerHTML = done ? "✓ Completed" : "Mark as complete";
    btn.addEventListener("click", () => {
      const now = toggleDone(item.id);
      btn.className = "btn " + (now ? "done" : "primary");
      btn.innerHTML = now ? "✓ Completed" : "Mark as complete";
      refreshSidebarProgress();
      showToast(now ? `Marked complete: ${item.title}` : `Unmarked: ${item.title}`, now ? null : "info");
    });
    wrap.appendChild(btn);

    if (item.tag) {
      const tag = document.createElement("span");
      tag.className = "tag " + escapeClass(item.tag);
      tag.textContent = item.tag;
      wrap.appendChild(tag);
    }

    const top = document.createElement("button");
    top.className = "btn";
    top.textContent = "↑ Top";
    top.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    wrap.appendChild(top);

    return wrap;
  }

  function buildPrevNext(item) {
    const wrap = document.createElement("div");
    wrap.className = "prevnext";
    const prevId = item.prev;
    const nextId = item.next;
    const prev = prevId ? byId.get(prevId) : null;
    const nxt = nextId ? byId.get(nextId) : null;
    if (prev) {
      wrap.innerHTML += `<a href="#/${prev.id}" class="prev"><div class="label">← Previous</div><div class="title">${escape(prev.title)}</div></a>`;
    } else {
      wrap.innerHTML += "<span></span>";
    }
    if (nxt) {
      wrap.innerHTML += `<a href="#/${nxt.id}" class="next"><div class="label">Next →</div><div class="title">${escape(nxt.title)}</div></a>`;
    } else {
      wrap.innerHTML += "<span></span>";
    }
    return wrap;
  }

  // --- home --- //
  function renderHome() {
    const main = document.getElementById("content");
    currentId = null;
    document.title = "Learning Hub — DSA & System Design";
    main.classList.remove("fade-in");
    void main.offsetWidth;
    main.classList.add("fade-in");
    buildTOC([]);
    if (scrollSpyObserver) scrollSpyObserver.disconnect();
    highlightSidebar();

    const done = getDone();
    const recent = getRecent().map(id => byId.get(id)).filter(Boolean);
    const isFirstTime = done.size === 0 && recent.length === 0;

    const trackCards = manifest.tracks.map(t => {
      const items = t.groups.flatMap(g => g.items);
      const dn = items.filter(it => done.has(it.id)).length;
      const total = items.length;
      const pct = total ? Math.round((dn / total) * 100) : 0;
      const first = items.find(it => !done.has(it.id)) || items[0];
      return `
        <div class="card">
          <h3>${t.icon} ${escape(t.title)}</h3>
          <p>${escape(t.id === "roadmap" ? "Read this first. Four-phase plan with kill switches." :
                      t.id === "dsa"     ? "77 topics across Beginner → Intermediate → Advanced → Expert + Meta." :
                                          "Tiers, 20 five-minute reads, trade-offs deep dive, books and papers.")}</p>
          <div class="progress-line"><span>${dn}/${total}</span><div class="bar"><span style="width:${pct}%"></span></div><span>${pct}%</span></div>
          <a class="go" href="#/${first ? first.id : ""}">${dn > 0 ? "Continue →" : "Start →"}</a>
        </div>`;
    }).join("");

    const continueCard = recent.length === 0 ? "" : `
      <div class="continue-card">
        <div class="ico">📖</div>
        <div class="body">
          <div class="label">Continue where you left off</div>
          <h3>${escape(recent[0].title)}</h3>
          <p class="desc">${escape(recent[0].summary || "")}</p>
        </div>
        <a class="btn primary" href="#/${recent[0].id}">Resume →</a>
      </div>
    `;

    const moreRecentHTML = recent.length <= 1 ? "" : `
      <h2>Recently viewed</h2>
      <div class="cards">
        ${recent.slice(1).map(it => `
          <div class="card recent">
            <h3>${escape(it.title)}</h3>
            <p>${escape(it.summary || "")}</p>
            <a class="go" href="#/${it.id}">Open →</a>
          </div>`).join("")}
      </div>
    `;

    const roadmap = manifest.tracks.find(t => t.id === "roadmap");
    const startId = roadmap ? roadmap.groups[0].items[0].id : (manifest.tracks[0].groups[0].items[0].id);

    const heroHTML = isFirstTime ? `
      <div class="hero welcome">
        <h1>👋 Welcome to your Learning Hub</h1>
        <p>Two tracks. One discipline. From beginner to expert in <strong>data structures &amp; problem solving</strong> and <strong>system design</strong>.</p>
        <div class="lede">
          <span>📚 ${order.length} topics</span>
          <span>⏱ 5-minute reads + deep dives</span>
          <span>⌨️ Keyboard-first</span>
          <span>📊 Progress saved locally</span>
        </div>
        <a class="cta" href="#/${startId}">Start with the Roadmap →</a>
      </div>
    ` : `
      <div class="hero">
        <h1>📚 Learning Hub</h1>
        <p>Pick a track. Mark topics complete as you go. Press <span class="kbd">?</span> for keyboard shortcuts.</p>
      </div>
    `;

    main.innerHTML = `
      ${heroHTML}
      ${continueCard}
      <h2>Tracks</h2>
      <div class="cards">${trackCards}</div>
      ${moreRecentHTML}
    `;
    updateReadingProgress();
    updateBackToTop();
  }

  // --- main route --- //
  function route() {
    const { id, anchor } = parseHash();
    if (!id) {
      renderHome();
    } else {
      renderItem(id, anchor);
    }
  }

  // --- keyboard --- //
  function setupKeys() {
    let gHeld = false;
    let gTimer = null;
    document.addEventListener("keydown", e => {
      // close modals on Esc regardless of focus target
      if (e.key === "Escape" && isAnyModalOpen()) {
        e.preventDefault();
        closeAllModals();
        return;
      }
      if (e.target.matches("input, textarea")) {
        if (e.key === "Escape") e.target.blur();
        return;
      }
      if (isAnyModalOpen()) return;
      if (e.key === "/") {
        e.preventDefault();
        document.getElementById("search-input").focus();
      } else if (e.key === "?") {
        e.preventDefault();
        showModal("help-modal");
      } else if (e.key === "j") {
        if (!currentId) return;
        const it = byId.get(currentId);
        if (it && it.next) navigate(it.next);
      } else if (e.key === "k") {
        if (!currentId) return;
        const it = byId.get(currentId);
        if (it && it.prev) navigate(it.prev);
      } else if (e.key === "m") {
        if (currentId) {
          const btn = document.getElementById("mark-done-btn");
          if (btn) btn.click();
        }
      } else if (e.key === "t") {
        toggleTheme();
      } else if (e.key === "g") {
        gHeld = true;
        clearTimeout(gTimer);
        gTimer = setTimeout(() => { gHeld = false; }, 800);
      } else if (e.key === "h" && gHeld) {
        gHeld = false;
        navigate("");
      }
    });
  }

  // --- helpers --- //
  function escape(s) {
    return String(s ?? "").replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }
  function escapeClass(s) {
    // produce a CSS-class-safe token from a tag value
    return String(s ?? "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^-+|-+$/g, "");
  }

  // --- reading progress bar --- //
  function updateReadingProgress() {
    const bar = document.querySelector(".reading-progress > span");
    if (!bar) return;
    const h = document.documentElement;
    const max = (h.scrollHeight - h.clientHeight) || 1;
    const pct = Math.min(100, Math.max(0, (h.scrollTop / max) * 100));
    bar.style.width = pct + "%";
  }

  // --- back to top button --- //
  function updateBackToTop() {
    const btn = document.getElementById("back-to-top");
    if (!btn) return;
    btn.classList.toggle("visible", window.scrollY > 400);
  }

  // --- auto-mark on scroll --- //
  function armAutoMark(item) {
    if (autoMarkTimer) {
      clearTimeout(autoMarkTimer);
      autoMarkTimer = null;
    }
    if (!getAutoMark() || !item || isDone(item.id)) return;
    // checked from main scroll listener instead of separate observer
    armAutoMark.itemId = item.id;
  }
  function checkAutoMark() {
    if (!getAutoMark()) return;
    const id = armAutoMark.itemId;
    if (!id || id !== currentId || isDone(id)) return;
    const h = document.documentElement;
    const max = (h.scrollHeight - h.clientHeight) || 1;
    const pct = (h.scrollTop / max) * 100;
    if (pct >= 90) {
      toggleDone(id);
      const btn = document.getElementById("mark-done-btn");
      if (btn) {
        btn.className = "btn done";
        btn.innerHTML = "✓ Completed";
      }
      refreshSidebarProgress();
      showToast(`Auto-marked: ${byId.get(id).title}`, "info");
      armAutoMark.itemId = null;
    }
  }

  // --- modal & button wiring --- //
  function wireModals() {
    document.querySelectorAll("[data-modal-close]").forEach(el => {
      el.addEventListener("click", () => {
        const m = el.closest(".modal");
        if (m) closeModal(m.id);
      });
    });
    const helpBtn = document.getElementById("help-btn");
    if (helpBtn) helpBtn.addEventListener("click", () => showModal("help-modal"));
    const settingsBtn = document.getElementById("settings-btn");
    if (settingsBtn) settingsBtn.addEventListener("click", openSettings);
  }
  function openSettings() {
    const cb = document.getElementById("setting-auto-mark");
    if (cb) cb.checked = getAutoMark();
    showModal("settings-modal");
  }
  function wireSettings() {
    const cb = document.getElementById("setting-auto-mark");
    if (cb) {
      cb.addEventListener("change", () => {
        setAutoMark(cb.checked);
        showToast(cb.checked ? "Auto-mark enabled" : "Auto-mark disabled", "info");
      });
    }
    const reset = document.getElementById("reset-progress-btn");
    if (reset) {
      reset.addEventListener("click", () => {
        if (!confirm("Reset all progress? This will clear completed topics, recents, and open tracks. Cannot be undone.")) return;
        try { localStorage.removeItem(LS_DONE); } catch {}
        try { localStorage.removeItem(LS_RECENT); } catch {}
        try { localStorage.removeItem(LS_OPEN); } catch {}
        try { localStorage.removeItem(LS_AUTO_MARK); } catch {}
        const cb2 = document.getElementById("setting-auto-mark");
        if (cb2) cb2.checked = false;
        buildSidebar();
        refreshSidebarProgress();
        route();
        closeModal("settings-modal");
        showToast("Progress reset", "info");
      });
    }
    const exp = document.getElementById("export-progress-btn");
    if (exp) {
      exp.addEventListener("click", () => {
        const data = {
          exportedAt: new Date().toISOString(),
          done: [...getDone()],
          recent: getRecent(),
          openTracks: [...getOpenTracks()],
          autoMark: getAutoMark()
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `learning-hub-progress-${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        showToast("Progress exported", "info");
      });
    }
  }

  // --- bootstrap --- //
  async function init() {
    applyTheme(lsGet(LS_THEME, "dark"));
    document.getElementById("theme-toggle").addEventListener("click", toggleTheme);
    document.getElementById("sidebar-toggle").addEventListener("click", () => {
      document.body.dataset.sidebar = document.body.dataset.sidebar === "open" ? "" : "open";
    });

    const res = await fetch("manifest.json?_=" + Date.now());
    manifest = await res.json();
    byId = new Map();
    order = [];
    for (const t of manifest.tracks) {
      for (const g of t.groups) {
        for (const it of g.items) {
          byId.set(it.id, it);
          order.push(it.id);
        }
      }
    }

    buildSidebar();
    refreshSidebarProgress();

    document.getElementById("search-input").addEventListener("input", e => {
      filterSidebar(e.target.value);
    });

    window.addEventListener("hashchange", route);
    document.addEventListener("click", e => {
      const a = e.target.closest("a[href^='#/']");
      if (a && document.body.dataset.sidebar === "open") {
        document.body.dataset.sidebar = "";
      }
    });

    // sidebar backdrop click closes mobile sidebar
    const backdrop = document.getElementById("sidebar-backdrop");
    if (backdrop) backdrop.addEventListener("click", () => {
      document.body.dataset.sidebar = "";
    });

    // reading progress + back-to-top + auto-mark on scroll
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        updateReadingProgress();
        updateBackToTop();
        checkAutoMark();
        ticking = false;
      });
    }, { passive: true });

    // back-to-top button
    const btt = document.getElementById("back-to-top");
    if (btt) btt.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    wireModals();
    wireSettings();

    setupKeys();
    route();
  }

  init().catch(err => {
    document.getElementById("content").innerHTML =
      `<h1>Failed to load</h1><pre>${err.message}</pre>`;
  });
})();
"""


SHELL_HTML = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Learning Hub</title>
  <meta name="description" content="DSA and System Design — a beginner-to-expert learning hub with progress tracking, search, and keyboard shortcuts.">
  <meta name="theme-color" content="#0d1117">
  <meta property="og:title" content="Learning Hub — DSA & System Design">
  <meta property="og:description" content="Beginner-to-expert curriculum with interactive navigation, progress tracking, and keyboard shortcuts.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://srikanth-chinnu.github.io/learning-hub/">
  <link rel="stylesheet" href="assets/style.css">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%93%9A%3C/text%3E%3C/svg%3E">
</head>
<body>
  <a class="skip-link" href="#content">Skip to content</a>
  <div class="reading-progress" aria-hidden="true"><span></span></div>
  <header class="topbar">
    <a href="#/" class="brand" title="Home">📚 Learning Hub</a>
    <button class="icon-btn sidebar-toggle" id="sidebar-toggle" title="Toggle sidebar" aria-label="Toggle sidebar">☰</button>
    <div class="search">
      <input id="search-input" type="text" placeholder="Search topics  (press /)" autocomplete="off" aria-label="Search topics">
    </div>
    <div class="progress-pill" id="global-progress" title="Overall progress">
      <span class="pct">0/0 · 0%</span>
      <div class="bar"><span style="width:0%"></span></div>
    </div>
    <button class="icon-btn" id="help-btn" title="Keyboard shortcuts (press ?)" aria-label="Keyboard shortcuts">?</button>
    <button class="icon-btn" id="settings-btn" title="Settings" aria-label="Settings">⚙</button>
    <button class="icon-btn" id="theme-toggle" title="Toggle theme (t)" aria-label="Toggle theme">☀️</button>
  </header>
  <div class="sidebar-backdrop" id="sidebar-backdrop" aria-hidden="true"></div>
  <div class="layout">
    <aside class="sidebar" id="sidebar" aria-label="Topic navigation"></aside>
    <main class="content" id="content" tabindex="-1"></main>
    <aside class="toc-rail" id="toc-rail" aria-label="On this page"></aside>
  </div>
  <button class="back-to-top" id="back-to-top" title="Back to top" aria-label="Back to top">↑</button>

  <div class="modal" id="help-modal" role="dialog" aria-modal="true" aria-labelledby="help-modal-title" aria-hidden="true">
    <div class="modal-backdrop" data-modal-close></div>
    <div class="modal-card" role="document">
      <header class="modal-head">
        <h2 id="help-modal-title">Keyboard shortcuts</h2>
        <button class="icon-btn" data-modal-close aria-label="Close">✕</button>
      </header>
      <table class="shortcut-table">
        <tr><td><span class="kbd">/</span></td><td>focus search</td></tr>
        <tr><td><span class="kbd">j</span> / <span class="kbd">k</span></td><td>next / previous topic</td></tr>
        <tr><td><span class="kbd">m</span></td><td>mark current topic complete</td></tr>
        <tr><td><span class="kbd">t</span></td><td>toggle dark / light theme</td></tr>
        <tr><td><span class="kbd">g</span> <span class="kbd">h</span></td><td>go home</td></tr>
        <tr><td><span class="kbd">?</span></td><td>show this help</td></tr>
        <tr><td><span class="kbd">Esc</span></td><td>close dialog / blur search</td></tr>
      </table>
      <p class="modal-foot">Tip: hold <span class="kbd">g</span> then press <span class="kbd">h</span> within 0.8s.</p>
    </div>
  </div>

  <div class="modal" id="settings-modal" role="dialog" aria-modal="true" aria-labelledby="settings-modal-title" aria-hidden="true">
    <div class="modal-backdrop" data-modal-close></div>
    <div class="modal-card" role="document">
      <header class="modal-head">
        <h2 id="settings-modal-title">Settings</h2>
        <button class="icon-btn" data-modal-close aria-label="Close">✕</button>
      </header>
      <div class="setting-row">
        <div>
          <strong>Auto-mark complete on scroll</strong>
          <p class="setting-help">Mark topics complete after you scroll through 90%.</p>
        </div>
        <label class="switch"><input type="checkbox" id="setting-auto-mark"><span></span></label>
      </div>
      <div class="setting-row">
        <div>
          <strong>Reset all progress</strong>
          <p class="setting-help">Clears completed topics, recents, and open tracks. Cannot be undone.</p>
        </div>
        <button class="btn danger" id="reset-progress-btn">Reset</button>
      </div>
      <div class="setting-row">
        <div>
          <strong>Export progress</strong>
          <p class="setting-help">Download your progress as a JSON file.</p>
        </div>
        <button class="btn" id="export-progress-btn">Download</button>
      </div>
    </div>
  </div>

  <div class="toast-stack" id="toasts" aria-live="polite" aria-atomic="false"></div>

  <script src="assets/app.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Entry
# --------------------------------------------------------------------------- #

def main():
    print(f"Building hub at {HUB}")
    if CONTENT.exists():
        for f in CONTENT.glob("**/*"):
            if f.is_file():
                f.unlink()
    CONTENT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    (ASSETS / "style.css").write_text(CSS, encoding="utf-8")
    (ASSETS / "app.js").write_text(APP_JS, encoding="utf-8")

    manifest = build_manifest()
    (HUB / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (HUB / "index.html").write_text(SHELL_HTML, encoding="utf-8")

    rewrites = rewrite_links()

    n_items = len(manifest["flat"])
    n_tracks = len(manifest["tracks"])
    print(f"  + {n_tracks} tracks, {n_items} topics")
    print(f"  + content/ ({len(list(CONTENT.glob('**/*.html')))} fragments)")
    print(f"  + manifest.json")
    print(f"  + index.html (SPA shell)")
    print(f"  + assets/style.css, assets/app.js")
    print(f"  + rewrote {rewrites} cross-document links to SPA hash routes")
    print(f"\nDone. Serve from {HUB} (open index.html via file:// or local server)")


if __name__ == "__main__":
    main()
