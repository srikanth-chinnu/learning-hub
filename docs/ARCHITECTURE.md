# Architecture

Learning Hub is a hand-rolled static SPA. The pipeline is short and intentionally boring.

## Pipeline

```
sources/*.md              build.py            content/*.html             index.html
   (you edit) ────────►  (Python +  ────────►  + manifest.json  ────────► (SPA shell)
                         markdown +              (generated)                 │
                         pygments)                                           ▼
                                                                       fetched at runtime
                                                                       by assets/app.js
```

- **`sources/`** — the only thing you edit by hand. Markdown, with custom `:::tabs` blocks for multi-language code samples.
- **`build.py`** — walks `sources/`, runs Python `markdown` + Pygments syntax highlighting, splits long files into named "chunks" of ~5 minutes' reading, and writes:
  - `content/<track>/<id>.html` — pre-rendered HTML fragments (no `<html>` / `<body>` wrappers; just the article).
  - `manifest.json` — nav tree, ordered list for prev/next, heading anchors for TOC, search index.
- **`index.html`** — minimal SPA shell. Loads `style.css` and `app.js`.
- **`assets/app.js`** — vanilla JS. Hash router, sidebar tree, scroll-spy TOC, search overlay, code-tab switcher, copy button, AI chat panel. No build step, no framework.

## Source conventions

### Multi-language code samples

Wrap groups of code blocks in a `:::tabs` fence so they render as language tabs:

````markdown
:::tabs

```python
def add(a, b): return a + b
```

```javascript
const add = (a, b) => a + b;
```

```java
static int add(int a, int b) { return a + b; }
```

```cpp
int add(int a, int b) { return a + b; }
```

:::
````

Order convention across the hub: **Python | JavaScript | Java | C++**.

### Chunking long files

Files like `dsa.md` and `deep-dives/tradeoffs.md` are large. `render_split_source()` in `build.py` splits them at H2 boundaries and emits one fragment per chunk. The first chunk becomes the master "Index" page.

## Why custom

Every static site generator (Jekyll, Hugo, 11ty, Astro, MkDocs) was tried and rejected for one of:
- Slow build for our number of pages
- No native support for `:::tabs`
- Couldn't produce a single-page app from markdown
- Required Node + 200 dependencies for a 10-page site

Plain Python + Markdown + Pygments + a 1-file vanilla JS SPA covers everything we need. Total dependencies: `markdown` and `pygments`.

## SPA runtime flow

1. Browser loads `index.html`.
2. `app.js` fetches `manifest.json` → builds the sidebar tree.
3. On hash change (e.g. `#/sd/5min/caching`), `app.js`:
   - Looks up the item in the manifest
   - Fetches `content/sd/5min/caching.html`
   - Injects it into the main pane
   - Builds the right-rail TOC from `<h2>` / `<h3>` anchors
   - Activates code-tab buttons + copy buttons
4. Progress (read/complete) and preferences (theme, code-tab language, AI key) are read/written from `localStorage`.

No server. No backend. No accounts. Everything client-side.

## Deploy

`main` branch → GitHub Pages.

`.nojekyll` at the repo root tells Pages to serve files as-is and **skip** Jekyll. Without this, Jekyll tries to parse `{{ ... }}` patterns inside C++/Java code blocks as Liquid template variables and the deploy fails.
