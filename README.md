# 📚 Learning Hub

A personal learning track that goes from **beginner → expert** in two disciplines:

- **DSA & Problem Solving** — 77 topics across 4 tiers + Meta interview prep
- **System Design** — 4 tiers, 20 five-minute reads, 160KB tradeoffs deep-dive, books/papers/repos

The repo ships **rendered HTML** (open `index.html` in any browser) plus the **markdown sources** under `sources/` and a self-contained build script.

---

## Open it

```bash
# Just open the rendered site
start index.html        # Windows
open  index.html        # macOS
xdg-open index.html     # Linux
```

That's it. No server, no build step needed if you just want to read.

---

## Edit and rebuild

The HTML files are generated. **Don't edit them directly** — edit the markdown under `sources/` and rebuild:

```bash
pip install markdown pygments
python build.py
```

`build.py` is idempotent and re-reads everything from `sources/` on each run.

---

## Repo structure

```
learning-hub/
├── index.html              # Landing page — start here
├── roadmap.html            # The 4-phase execution plan with kill switches
├── build.py                # Static site generator (markdown → HTML)
├── README.md               # This file
├── assets/
│   └── style.css           # Dark GitHub-style theme
├── sources/                # All source markdown — edit these
│   ├── roadmap.md
│   ├── dsa.md              # 63KB monolithic DSA curriculum
│   └── system-design/      # 30 markdown files
│       ├── README.md
│       ├── 01-beginner.md ... 04-expert.md
│       ├── tradeoffs-deep-dive.md
│       ├── books-and-courses.md, github-repos.md, seminal-papers.md
│       └── 5-minute-reads/ (20 topics)
├── dsa/index.html          # Generated
└── system-design/          # Generated (mirror of sources/system-design)
    ├── index.html
    ├── 01-beginner.html ... 04-expert.html
    ├── 5-minute-reads/
    └── ...
```

---

## How to use it

1. **Read the roadmap first.** `roadmap.html` — read it fully before touching the curriculum.
2. **Pick your daily cadence.** Default: 45 min DSA daily, 2 hr system design weekly.
3. **Track your work.** Use a simple spreadsheet (date, topic, time, evidence).
4. **Hit the kill switches.** If a phase isn't producing evidence, the roadmap tells you when to pivot.

Reading is not learning. Solving and explaining is. The hub exists so you don't waste time *finding* what to learn — it doesn't exist to make you feel productive while *not* learning.

---

## License

Personal learning notes. Use freely; no warranty.
