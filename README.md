# 📚 Learning Hub

A free, **interactive** learning hub for **DSA** and **System Design** that goes from **beginner → expert** without the bounce-rate problem of long external links.

**Live site:** https://srikanth-chinnu.github.io/learning-hub/

> Everything is on one page. No accounts, no logins, no tracking. Your progress lives in `localStorage`.

---

## What's inside

- **DSA & Problem Solving** — 4 tiers (Beginner → Expert), 19 chunked articles + an index, with **49 multi-language code samples** in `Python | JavaScript | Java | C++`.
- **System Design — Tiered curriculum** — 4 levels: Beginner, Intermediate, Advanced, Expert.
- **System Design — 20 Five-Minute Reads** — bite-sized articles on caching, sharding, CAP, queues, microservices, observability, etc.
- **System Design — Trade-offs Deep Dive** — a 65 KB long-form on HLD/LLD trade-offs, chunked for browsing.
- **Roadmap** — a brutally honest learning plan.

---

## Features

| | |
|---|---|
| 🧭 **Hash router** | `#/dsa/full`, `#/sd/5min/caching`. Bookmarkable. |
| 📂 **Sidebar tree** | All articles grouped by track + per-track progress. |
| 🔍 **Smart search** | Full-text. `/` to focus, arrows to navigate, `Enter` to open. |
| 🤖 **AI assistant (BYOK)** | Bottom-right chat button. Bring your OpenAI key — stored locally. |
| ✅ **Progress tracking** | Mark complete; persisted in `localStorage` per browser. |
| 💻 **Multi-language code tabs** | Toggle Python / JavaScript / Java / C++. Choice persists. |
| 📋 **One-click copy** | Every code block has a copy button. |
| 📊 **Auto right-rail TOC** | Scroll-spy highlights the current section. |
| ⌨️ **Keyboard shortcuts** | `j`/`k` next/prev, `m` mark complete, `t` theme, `g h` home, `/` search. |
| 🎨 **Dark / light theme** | Toggle in the header; remembered. |
| 📱 **Responsive** | Sidebar collapses on mobile; code tabs scroll horizontally. |

---

## Run it locally

```bash
# 1. Build (regenerates content/, manifest.json, index.html, assets/)
pip install markdown pygments
python build.py

# 2. Serve (the SPA fetches manifest.json, so file:// won't work)
python -m http.server 8765
# open http://localhost:8765/
```

GitHub Pages handles the same flow over HTTPS. The `.nojekyll` file disables Jekyll so curly-brace patterns inside C++/Java code are served as-is.

---

## Repo structure

```
learning-hub/
├── README.md
├── .nojekyll                    # disables Jekyll on GitHub Pages
├── index.html                   # SPA shell (the only HTML page)
├── manifest.json                # nav tree + heading anchors (generated)
├── build.py                     # markdown → fragments + manifest builder
├── assets/
│   ├── app.js                   # router, sidebar, search, TOC, code tabs, AI chat
│   └── style.css                # theme + layout
├── content/                     # pre-rendered HTML fragments (generated)
│   ├── dsa/full/                # 19 chunked DSA HTMLs + index
│   ├── sd/5min/                 # 21 five-minute-read HTMLs
│   ├── sd/tradeoffs/            # 11 trade-off chunks + index
│   └── roadmap/main.html
├── docs/                        # contributor docs
│   ├── ARCHITECTURE.md          # how the SPA + build pipeline works
│   ├── CONTRIBUTING.md          # how to add an article, build, deploy
│   └── CONTENT-CONVENTIONS.md   # :::tabs syntax, frontmatter, language order
└── sources/                     # the markdown you edit
    ├── roadmap.md
    ├── dsa.md                   # 117 KB single-file DSA curriculum
    └── system-design/
        ├── README.md            # System Design overview
        ├── tiers/
        │   ├── 01-beginner.md
        │   ├── 02-intermediate.md
        │   ├── 03-advanced.md
        │   └── 04-expert.md
        ├── 5-minute-reads/      # 20 numbered articles + README index
        ├── deep-dives/
        │   └── tradeoffs.md     # HLD/LLD trade-offs long-form
        └── _archive/            # not built; kept for reference
            ├── books-and-courses.md
            ├── github-repos.md
            └── seminal-papers.md
```

---

## How to use it

1. **Read the roadmap first.** `#/roadmap/main` — sets expectations and cadence.
2. **Pick a daily cadence.** Default: 45 min DSA daily, 2 hr System Design weekly.
3. **Mark topics complete as you finish them.** Sidebar shows your progress.
4. **Try the multi-language code tabs.** Pick the language you'll use in interviews; your choice persists.
5. **Search aggressively.** Press `/` and type anything — the index covers all 60+ articles.
6. **Use the AI assistant** for follow-up questions on the article you're reading.

Reading isn't learning. Solving and explaining is. The hub exists so you don't waste time *finding* what to learn.

---

## Contributing

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for the authoring workflow and content conventions.

## License

Personal learning notes. Use freely; no warranty.
