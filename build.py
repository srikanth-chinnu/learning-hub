#!/usr/bin/env python3
"""
build.py — Convert markdown sources to a navigable HTML site.

Re-run this any time you edit the .md files under ./sources/.

Usage:
    pip install markdown pygments
    python build.py

Output: ./*.html (and dsa/, system-design/ subdirs)
Open: index.html in any browser.
"""
import os
import re
import shutil
from pathlib import Path
import markdown

HUB = Path(__file__).resolve().parent
SOURCES = HUB / "sources"
SD_SRC = SOURCES / "system-design"
RESEARCH = SOURCES

MD_EXT = [
    "markdown.extensions.tables",
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.toc",
    "markdown.extensions.sane_lists",
    "markdown.extensions.attr_list",
    "markdown.extensions.def_list",
]

PAGE_TMPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Learning Hub</title>
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="topbar">
  <a href="{root}index.html" class="brand">📚 Learning Hub</a>
  <nav class="topnav">
    <a href="{root}index.html">Home</a>
    <a href="{root}roadmap.html">Roadmap</a>
    <a href="{root}dsa/index.html">DSA</a>
    <a href="{root}system-design/index.html">System Design</a>
  </nav>
</header>
<div class="layout">
  <aside class="sidebar">{sidebar}</aside>
  <main class="content">
    <div class="breadcrumb">{crumbs}</div>
    <article class="md">{body}</article>
    <nav class="prevnext">{prevnext}</nav>
  </main>
</div>
<footer class="foot">
  <span>Generated from local .md files. Edit sources, then run <code>python build.py</code>.</span>
</footer>
</body>
</html>
"""

CSS = r"""
:root{
  --bg:#0d1117; --panel:#161b22; --border:#30363d; --text:#e6edf3; --muted:#8b949e;
  --link:#58a6ff; --accent:#f78166; --code-bg:#1f242c; --shadow:rgba(0,0,0,.4);
  --good:#3fb950; --warn:#d29922; --bad:#f85149;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--text);font:16px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
code,pre,kbd{font-family:Consolas,Menlo,Monaco,'Courier New',monospace}
.topbar{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;background:var(--panel);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:50}
.brand{font-weight:700;font-size:18px;color:var(--text)}
.topnav a{margin-left:18px;color:var(--muted);font-weight:500}
.topnav a:hover{color:var(--text);text-decoration:none}
.layout{display:flex;max-width:1400px;margin:0 auto}
.sidebar{width:300px;flex-shrink:0;border-right:1px solid var(--border);padding:24px 16px;height:calc(100vh - 60px);overflow-y:auto;position:sticky;top:60px;background:var(--bg)}
.sidebar h3{margin:18px 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.sidebar ul{list-style:none;margin:0;padding:0}
.sidebar li{margin:2px 0}
.sidebar a{display:block;padding:5px 10px;border-radius:6px;color:var(--text);font-size:14px}
.sidebar a:hover{background:var(--panel);text-decoration:none}
.sidebar a.active{background:var(--panel);color:var(--accent);font-weight:600}
.sidebar .group{padding-left:14px;border-left:1px solid var(--border);margin-left:4px}
.content{flex:1;padding:30px 50px;max-width:900px;min-width:0}
.breadcrumb{color:var(--muted);font-size:13px;margin-bottom:14px}
.breadcrumb a{color:var(--muted)}
.md h1{font-size:32px;border-bottom:1px solid var(--border);padding-bottom:10px;margin-top:0}
.md h2{font-size:24px;border-bottom:1px solid var(--border);padding-bottom:6px;margin-top:30px}
.md h3{font-size:19px;margin-top:24px}
.md h4{font-size:16px;margin-top:18px}
.md p{margin:12px 0}
.md ul,.md ol{padding-left:28px}
.md li{margin:4px 0}
.md blockquote{border-left:4px solid var(--accent);background:var(--panel);padding:8px 16px;margin:16px 0;color:var(--muted)}
.md table{border-collapse:collapse;margin:14px 0;display:block;overflow-x:auto;max-width:100%}
.md th,.md td{border:1px solid var(--border);padding:8px 12px;text-align:left}
.md th{background:var(--panel)}
.md tr:nth-child(even){background:rgba(255,255,255,.02)}
.md code{background:var(--code-bg);padding:2px 6px;border-radius:4px;font-size:.92em}
.md pre{background:var(--code-bg);border:1px solid var(--border);border-radius:6px;padding:14px 16px;overflow-x:auto;font-size:13.5px;line-height:1.45}
.md pre code{background:transparent;padding:0;font-size:13.5px}
.md hr{border:0;border-top:1px solid var(--border);margin:30px 0}
.md img{max-width:100%}
.codehilite .k,.codehilite .kn,.codehilite .kd,.codehilite .kc{color:#ff7b72}
.codehilite .s,.codehilite .s1,.codehilite .s2{color:#a5d6ff}
.codehilite .nf,.codehilite .nx{color:#d2a8ff}
.codehilite .nb,.codehilite .nc{color:#79c0ff}
.codehilite .c,.codehilite .c1,.codehilite .cm{color:#8b949e;font-style:italic}
.codehilite .mi,.codehilite .mf{color:#79c0ff}
.codehilite .o,.codehilite .p{color:#e6edf3}
.prevnext{display:flex;justify-content:space-between;margin-top:40px;padding-top:20px;border-top:1px solid var(--border);gap:10px}
.prevnext a{flex:1;padding:14px 18px;background:var(--panel);border:1px solid var(--border);border-radius:8px;display:block}
.prevnext a:hover{border-color:var(--accent);text-decoration:none}
.prevnext .label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
.prevnext .title{font-weight:600;color:var(--text);margin-top:4px}
.prevnext a.next{text-align:right}
.foot{padding:16px 20px;text-align:center;color:var(--muted);font-size:13px;border-top:1px solid var(--border);margin-top:40px}
.foot code{background:var(--code-bg);padding:2px 6px;border-radius:4px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin:24px 0}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:22px;transition:.2s}
.card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 6px 20px var(--shadow)}
.card h3{margin:0 0 8px;color:var(--text)}
.card p{color:var(--muted);margin:0 0 14px;font-size:14px}
.card a{display:inline-block;padding:8px 14px;background:var(--bg);border:1px solid var(--border);border-radius:6px;font-size:13px;font-weight:500}
.tag{display:inline-block;padding:2px 9px;background:var(--bg);border:1px solid var(--border);border-radius:99px;font-size:11px;color:var(--muted);margin-right:6px}
.tag.tier1{color:var(--good);border-color:var(--good)}
.tag.tier2{color:var(--link);border-color:var(--link)}
.tag.tier3{color:var(--warn);border-color:var(--warn)}
.tag.tier4{color:var(--bad);border-color:var(--bad)}
.hero{background:linear-gradient(135deg,var(--panel) 0%,var(--bg) 100%);border:1px solid var(--border);border-radius:14px;padding:40px;margin-bottom:30px}
.hero h1{margin:0 0 10px;font-size:36px;border:none}
.hero p{color:var(--muted);font-size:17px;max-width:700px;margin:0}
@media (max-width:980px){
  .layout{flex-direction:column}
  .sidebar{width:100%;height:auto;position:static;border-right:none;border-bottom:1px solid var(--border)}
  .content{padding:20px}
}
"""


def title_from_md(text, fallback):
    m = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    return (m.group(1).strip() if m else fallback).replace("`", "")


def render_md(text):
    md = markdown.Markdown(extensions=MD_EXT, output_format="html5")
    return md.convert(text)


def write_page(out_path: Path, title: str, body_html: str, sidebar_html: str,
               crumbs_html: str, prevnext_html: str, root: str):
    html = PAGE_TMPL.format(title=title, body=body_html, sidebar=sidebar_html,
                            crumbs=crumbs_html, prevnext=prevnext_html, root=root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")


def crumbs(items):
    return " &rsaquo; ".join(
        f'<a href="{href}">{name}</a>' if href else name for name, href in items
    )


def prev_next(prev, nxt):
    out = []
    if prev:
        out.append(f'<a class="prev" href="{prev["href"]}"><div class="label">← Previous</div><div class="title">{prev["title"]}</div></a>')
    else:
        out.append("<span></span>")
    if nxt:
        out.append(f'<a class="next" href="{nxt["href"]}"><div class="label">Next →</div><div class="title">{nxt["title"]}</div></a>')
    else:
        out.append("<span></span>")
    return "".join(out)


def build_section(files, src_dir):
    pages = []
    for rel_md, title in files:
        src = src_dir / rel_md
        if not src.exists():
            print(f"  ! missing: {src}")
            continue
        text = src.read_text(encoding="utf-8")
        body = render_md(text)
        pages.append({
            "title": title or title_from_md(text, src.stem),
            "html_name": src.stem + ".html",
            "body": body,
            "src": src,
        })
    return pages


def write_section(pages, out_dir: Path, root: str, sidebar_html: str, crumbs_prefix):
    for i, p in enumerate(pages):
        prev = {"href": pages[i-1]["html_name"], "title": pages[i-1]["title"]} if i > 0 else None
        nxt = {"href": pages[i+1]["html_name"], "title": pages[i+1]["title"]} if i < len(pages)-1 else None
        cb = crumbs(crumbs_prefix + [(p["title"], None)])
        write_page(out_dir / p["html_name"], p["title"], p["body"],
                   sidebar_html, cb, prev_next(prev, nxt), root)


def build_root_sidebar(active=""):
    return """
    <h3>Learning Hub</h3>
    <ul>
      <li><a href="index.html"{0}>🏠 Home</a></li>
      <li><a href="roadmap.html"{1}>🗺️ Roadmap</a></li>
    </ul>
    <h3>Tracks</h3>
    <ul>
      <li><a href="dsa/index.html">🧠 DSA &amp; Problem Solving</a></li>
      <li><a href="system-design/index.html">🏗️ System Design</a></li>
    </ul>
    <h3>Quick links</h3>
    <ul>
      <li><a href="system-design/5-minute-reads/index.html">⏱️ 5-Minute Reads (System Design)</a></li>
      <li><a href="system-design/tradeoffs-deep-dive.html">⚖️ Trade-offs Deep Dive</a></li>
    </ul>
    """.format(' class="active"' if active=="home" else "",
               ' class="active"' if active=="roadmap" else "")


def build_dsa_sidebar():
    return """
    <h3>DSA Curriculum</h3>
    <ul>
      <li><a href="index.html" class="active">📖 Full Curriculum (77 reads)</a></li>
    </ul>
    <h3>Tiers (anchors)</h3>
    <ul>
      <li><a href="index.html#tier-1-beginner-foundations-you-cannot-skip">Tier 1 — Beginner</a></li>
      <li><a href="index.html#tier-2-intermediate-interview-ready">Tier 2 — Intermediate</a></li>
      <li><a href="index.html#tier-3-advanced-dp-shortest-paths-segment-trees">Tier 3 — Advanced</a></li>
      <li><a href="index.html#tier-4-expert-rarely-interviewed-often-contest-decisive">Tier 4 — Expert</a></li>
      <li><a href="index.html#meta-cross-cutting-problem-solving-skills">Meta</a></li>
    </ul>
    <h3>Other tracks</h3>
    <ul>
      <li><a href="../roadmap.html">🗺️ Roadmap</a></li>
      <li><a href="../system-design/index.html">🏗️ System Design</a></li>
    </ul>
    """


def build_sd_sidebar(sd_pages, in_5min=False, five_pages=None):
    items = []
    for p in sd_pages:
        href = p["html_name"] if not in_5min else f"../{p['html_name']}"
        items.append(f'<li><a href="{href}">{p["title"]}</a></li>')
    sb = '<h3>System Design</h3><ul>' + "".join(items) + '</ul>'
    if in_5min and five_pages:
        five_items = "".join(
            f'<li><a href="{p["html_name"]}">{p["title"]}</a></li>' for p in five_pages
        )
        sb += '<h3>5-Minute Reads</h3><ul class="group">' + five_items + '</ul>'
    else:
        href = "5-minute-reads/index.html"
        sb += f'<h3>5-Minute Reads</h3><ul><li><a href="{href}">All 20 reads →</a></li></ul>'
    up = "../" if not in_5min else "../../"
    sb += f'<h3>Other tracks</h3><ul><li><a href="{up}roadmap.html">🗺️ Roadmap</a></li><li><a href="{up}dsa/index.html">🧠 DSA</a></li></ul>'
    return sb


def write_landing():
    body = """
    <div class="hero">
      <h1>📚 Learning Hub</h1>
      <p>Two tracks. One discipline. Everything you need to go from beginner to expert in <strong>data structures &amp; problem solving</strong> and <strong>system design</strong>.</p>
    </div>

    <h2>Start here</h2>
    <div class="cards">
      <div class="card">
        <h3>🗺️ The Roadmap</h3>
        <p>4-phase plan with milestones, kill-switches, and what to <em>stop</em> doing. Read this first.</p>
        <a href="roadmap.html">Open roadmap →</a>
      </div>
      <div class="card">
        <h3>🧠 DSA &amp; Problem Solving</h3>
        <p>77 five-minute reads across Beginner → Intermediate → Advanced → Expert + Meta skills. Code in Python &amp; C++.</p>
        <a href="dsa/index.html">Start DSA →</a>
      </div>
      <div class="card">
        <h3>🏗️ System Design</h3>
        <p>Foundations, scaling, distributed systems, expert patterns. Plus 20 focused 5-minute reads.</p>
        <a href="system-design/index.html">Start system design →</a>
      </div>
    </div>

    <h2>Quick reference</h2>
    <div class="cards">
      <div class="card">
        <h3>⏱️ 5-Minute Reads (System Design)</h3>
        <p>20 bite-sized topics — caching, consistent hashing, CAP, consensus, observability, and more.</p>
        <a href="system-design/5-minute-reads/index.html">Open →</a>
      </div>
      <div class="card">
        <h3>⚖️ Trade-offs Deep Dive</h3>
        <p>The tax sheet for every architecture decision. CAP, latency vs. throughput, sync vs. async, monolith vs. microservices.</p>
        <a href="system-design/tradeoffs-deep-dive.html">Open →</a>
      </div>
      <div class="card">
        <h3>📚 Books, Courses &amp; Papers</h3>
        <p>Curated reading list — DDIA, Kleppmann's papers, Raft, Dynamo, MapReduce, etc.</p>
        <a href="system-design/books-and-courses.html">Open →</a>
      </div>
    </div>

    <h2>Track levels at a glance</h2>
    <table>
      <thead><tr><th>Tier</th><th>DSA</th><th>System Design</th></tr></thead>
      <tbody>
        <tr><td><span class="tag tier1">Beginner</span></td><td>Big-O, arrays, hashing, two pointers, sliding window, recursion</td><td>What is system design, scalability basics, latency, APIs</td></tr>
        <tr><td><span class="tag tier2">Intermediate</span></td><td>Trees, graphs, heaps, DSU, tries, intervals, monotonic stacks</td><td>Caching, sharding, replication, consistent hashing, microservices</td></tr>
        <tr><td><span class="tag tier3">Advanced</span></td><td>DP families, Dijkstra, segment trees, KMP, MST</td><td>CAP, consistency models, message queues, rate limiting</td></tr>
        <tr><td><span class="tag tier4">Expert</span></td><td>HLD, suffix structures, FFT, MCMF, persistent segtree, 2-SAT</td><td>Consensus (Raft/Paxos), event-driven + saga, resilience, observability</td></tr>
      </tbody>
    </table>

    <h2>How to use this hub</h2>
    <ol>
      <li><strong>Read the roadmap.</strong> Don't skip it. It tells you what NOT to do, which is more valuable than what to do.</li>
      <li><strong>Pick one tier per track.</strong> Mixing levels is how people stay stuck.</li>
      <li><strong>One topic = one solved problem (DSA) or one design walkthrough (system design).</strong> Reading without doing is entertainment.</li>
      <li><strong>Track in a spreadsheet.</strong> The roadmap explains why this is non-optional.</li>
    </ol>

    <h2>Edit &amp; rebuild</h2>
    <p>All sources are markdown files. Edit the <code>.md</code> in either:</p>
    <ul>
      <li><code>C:\\Users\\smudili\\Documents\\system-design-learning</code></li>
      <li><code>C:\\Users\\smudili\\.copilot\\session-state\\7a4bac2b-6e57-404c-b633-f638cacb3ddf\\research</code></li>
    </ul>
    <p>Then run: <code>python C:\\Users\\smudili\\Documents\\learning-hub\\build.py</code></p>
    """
    cb = crumbs([("Home", None)])
    write_page(HUB / "index.html", "Learning Hub", body,
               build_root_sidebar(active="home"), cb,
               prev_next(None, {"href":"roadmap.html","title":"Roadmap"}),
               root="")


def main():
    print(f"Building hub at {HUB}")
    HUB.mkdir(exist_ok=True)
    (HUB / "assets").mkdir(exist_ok=True)
    (HUB / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    # Roadmap
    rm_src = RESEARCH / "roadmap.md"
    if rm_src.exists():
        text = rm_src.read_text(encoding="utf-8")
        title = title_from_md(text, "Roadmap")
        body = render_md(text)
        cb = crumbs([("Home", "index.html"), ("Roadmap", None)])
        write_page(HUB / "roadmap.html", title, body,
                   build_root_sidebar(active="roadmap"), cb,
                   prev_next(None, {"href":"dsa/index.html","title":"DSA Curriculum"}),
                   root="")
        print("  + roadmap.html")

    # DSA
    dsa_src = RESEARCH / "dsa.md"
    if dsa_src.exists():
        (HUB / "dsa").mkdir(exist_ok=True)
        text = dsa_src.read_text(encoding="utf-8")
        title = title_from_md(text, "DSA Curriculum")
        body = render_md(text)
        cb = crumbs([("Home", "../index.html"), ("DSA", None)])
        write_page(HUB / "dsa" / "index.html", title, body,
                   build_dsa_sidebar(), cb,
                   prev_next({"href":"../roadmap.html","title":"Roadmap"},
                             {"href":"../system-design/index.html","title":"System Design"}),
                   root="../")
        print("  + dsa/index.html")

    # System Design
    if SD_SRC.exists():
        sd_out = HUB / "system-design"
        sd_out.mkdir(exist_ok=True)
        top_pages = [
            ("README.md", "Overview"),
            ("01-beginner.md", "Beginner"),
            ("02-intermediate.md", "Intermediate"),
            ("03-advanced.md", "Advanced"),
            ("04-expert.md", "Expert"),
            ("tradeoffs-deep-dive.md", "Trade-offs Deep Dive"),
            ("books-and-courses.md", "Books & Courses"),
            ("github-repos.md", "GitHub Repos"),
            ("seminal-papers.md", "Seminal Papers"),
        ]
        sd_pages = build_section(top_pages, SD_SRC)
        for p in sd_pages:
            if p["html_name"] == "README.html":
                p["html_name"] = "index.html"
                p["title"] = "System Design — Overview"
        sd_sidebar = build_sd_sidebar(sd_pages)
        write_section(sd_pages, sd_out, root="../", sidebar_html=sd_sidebar,
                      crumbs_prefix=[("Home","../index.html"),("System Design","index.html")])
        print(f"  + system-design/ ({len(sd_pages)} pages)")

        five_dir = SD_SRC / "5-minute-reads"
        if five_dir.exists():
            five_out = sd_out / "5-minute-reads"
            five_out.mkdir(exist_ok=True)
            five_files = sorted(p.name for p in five_dir.glob("*.md") if p.name != "README.md")
            inputs = [("README.md", "5-Minute Reads — Index")] + [(f, None) for f in five_files]
            five_pages = build_section(inputs, five_dir)
            for p in five_pages:
                if p["html_name"] == "README.html":
                    p["html_name"] = "index.html"
            five_sidebar = build_sd_sidebar(sd_pages, in_5min=True, five_pages=five_pages)
            write_section(five_pages, five_out, root="../../",
                          sidebar_html=five_sidebar,
                          crumbs_prefix=[("Home","../../index.html"),
                                         ("System Design","../index.html"),
                                         ("5-Minute Reads","index.html")])
            print(f"  + system-design/5-minute-reads/ ({len(five_pages)} pages)")

    write_landing()
    print(f"\nDone. Open: {HUB / 'index.html'}")


if __name__ == "__main__":
    main()
