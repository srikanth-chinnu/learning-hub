# 📚 Learning Hub

A personal, **interactive** learning track that goes from **beginner → expert** in two disciplines:

- **DSA & Problem Solving** — 77 topics across 4 tiers + Meta interview prep
- **System Design** — 4 tiers, 20 five-minute reads, 160KB tradeoffs deep-dive, books/papers/repos

**Live site:** https://srikanth-chinnu.github.io/learning-hub/

The site is a single-page app — no page reloads, instant content swap, persistent progress, search, keyboard shortcuts, light/dark theme.

---

## Features

- 🧭 **Hash-based router** — `#/dsa/full`, `#/sd/5min/caching` etc. Bookmarkable, shareable.
- 📂 **Collapsible sidebar tree** — all 32 topics grouped by track, with per-track progress badges.
- 🔍 **Live search** — type to filter the sidebar (press `/` to focus).
- ✅ **Mark-as-complete** — per-topic; progress persisted in `localStorage` per browser.
- 📊 **Auto right-rail TOC** — h2/h3 of the current page, with scroll-spy highlight.
- ⌨️ **Keyboard shortcuts** — `j`/`k` next/prev, `m` mark complete, `t` theme, `g h` home, `/` search, `Esc` blur.
- 🎨 **Theme toggle** — dark/light, persisted.
- 📱 **Responsive** — sidebar collapses on mobile.

---

## Open it

```bash
# Locally — needs a static server (the SPA fetches manifest.json + content fragments)
python -m http.server 8765
# then open http://localhost:8765/
```

GitHub Pages serves over HTTPS so it just works there.

---

## Edit and rebuild

Edit markdown under `sources/` and run:

```bash
pip install markdown pygments
python build.py
```

That regenerates `content/`, `manifest.json`, `index.html`, and `assets/`. Commit and push — Pages auto-rebuilds in ~30 sec.

---

## Repo structure

```
learning-hub/
├── index.html          # SPA shell — the only HTML page
├── manifest.json       # Navigation tree + ordered list + heading anchors
├── build.py            # Markdown → fragments + manifest builder
├── README.md
├── assets/
│   ├── style.css       # Theme (dark/light)
│   └── app.js          # Router, sidebar, progress, search, TOC, keyboard
├── content/            # Pre-rendered HTML fragments (no shell)
│   ├── roadmap/main.html
│   ├── dsa/full.html
│   └── sd/
│       ├── overview.html, tier-*.html, tradeoffs.html, books.html, repos.html, papers.html
│       └── 5min/index.html + 20 topic pages
└── sources/            # The markdown you edit
    ├── roadmap.md
    ├── dsa.md
    └── system-design/
        ├── 01-beginner.md ... 04-expert.md
        ├── tradeoffs-deep-dive.md
        ├── README.md
        ├── books-and-courses.md, github-repos.md, seminal-papers.md
        └── 5-minute-reads/ (20 files)
```

---

## How to use it

1. **Read the roadmap first.** `#/roadmap/main` — read it fully before touching the curriculum.
2. **Pick your daily cadence.** Default: 45 min DSA daily, 2 hr system design weekly.
3. **Mark topics complete as you finish them.** The sidebar shows your progress. The dashboard shows recently viewed.
4. **Track your work in a spreadsheet too.** localStorage is per-browser; spreadsheet is the source of truth.
5. **Hit the kill switches.** If a phase isn't producing evidence, pivot.

Reading is not learning. Solving and explaining is. The hub exists so you don't waste time *finding* what to learn — it doesn't exist to make you feel productive while *not* learning.

---

## License

Personal learning notes. Use freely; no warranty.

