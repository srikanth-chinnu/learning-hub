# Contributing

Personal repo, but the workflow is the same whether you're editing your own notes or sending a PR.

## Setup

```bash
git clone https://github.com/srikanth-chinnu/learning-hub.git
cd learning-hub
pip install markdown pygments
```

That's the entire toolchain.

## Add or edit an article

1. **Find the right source file.** See [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for the full layout.
   - DSA topics: edit `sources/dsa.md` (one big file; `build.py` splits it into chunks).
   - System Design tier: `sources/system-design/tiers/0X-*.md`.
   - System Design 5-min read: drop a new file under `sources/system-design/5-minute-reads/` named `NN-slug.md`.
   - Trade-offs deep dive: `sources/system-design/deep-dives/tradeoffs.md`.

2. **Use the conventions** in [`docs/CONTENT-CONVENTIONS.md`](CONTENT-CONVENTIONS.md) (frontmatter, `:::tabs`, language order).

3. **Build:**
   ```bash
   python build.py
   ```
   Output: `content/`, `manifest.json`, refreshed `index.html` + `assets/`.

4. **Preview locally** (the SPA needs HTTP, not `file://`):
   ```bash
   python -m http.server 8765
   # open http://localhost:8765/
   ```

5. **Sanity-check before commit:**
   - Search works (press `/`).
   - Your new article shows in the sidebar.
   - Code tabs render with all 4 languages where applicable.
   - The right-rail TOC populates from your `## ` and `### ` headings.

## Commit & push

```bash
git add -A
git commit -m "feat: <one-line summary>" -m "<details>" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push origin main
```

GitHub Pages rebuilds in ~30 seconds. Watch the deploy:

```bash
gh run list --limit 3
```

If the latest run shows `failure`, see [`docs/ARCHITECTURE.md`](ARCHITECTURE.md#deploy) — usually it's a `.nojekyll` issue.

## Style

- Articles are **opinionated**, not exhaustive. Pick a side; explain trade-offs.
- Lead with **what** + **when to use it**, then mechanics, then code.
- Code samples should be **runnable** wherever possible. No pseudo-code passed off as real.
- Quotes are cited with author + year + source.
- Numbers (latency, throughput, $) come with a primary source link.

## What NOT to commit

- `node_modules/` (only ever appears if you ran a Playwright test)
- `__pycache__/`, `*.pyc`
- Editor cruft (`.vscode/`, `.idea/`)
- Anything under `_drafts/` (if you create one for in-progress work)

These are covered by `.gitignore`. Keep it clean.
