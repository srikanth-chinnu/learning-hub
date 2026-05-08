# Content Conventions

These conventions keep the hub consistent across 60+ articles authored over time.

## Frontmatter

Every source file starts with YAML frontmatter. `build.py` reads it.

```yaml
---
title: "Caching: When, What, and Where"
difficulty: intermediate         # beginner | intermediate | advanced | expert | all-levels
read_min: 5                       # estimated read time in minutes
tags: [system-design, caching]
---
```

If you omit fields, `build.py` infers reasonable defaults from filename and content.

## Headings

- `# H1` — used by frontmatter `title`; you can also have one in the body.
- `## H2` — major sections. Each one becomes a right-rail TOC entry.
- `### H3` — subsections. Also TOC.
- Avoid `####` and deeper. If you need `H4`, the section is too deep — split it.

## Multi-language code blocks

Wrap related code samples in a `:::tabs` fence:

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

### Language order (always)

**Python → JavaScript → Java → C++.** Scripting first, systems last. Don't reorder. The code-tab UI remembers the user's pick across articles, so consistent ordering is critical.

### When a concept doesn't translate

If a pattern is genuinely language-specific (e.g., C++ RVO, Python `__slots__`), still include all 4 tabs. The "non-applicable" tab should be a SHORT honest note, not a fake translation:

````markdown
```javascript
// JavaScript engines (V8, SpiderMonkey) auto-elide return-value copies.
// There's no programmer-controlled equivalent of C++ RVO/NRVO.
```
````

This is more educational than "// not applicable" filler.

## Code style per language

| | |
|---|---|
| **Python** | `3.11+`. Type hints. `dataclass` over plain classes. `Path` over string paths. |
| **JavaScript** | ES2022+. `const`/`let`. Arrow functions. Avoid `class` unless modeling state. |
| **Java** | `17+`. `var` for locals. `record` for DTOs. Bare static methods for algorithms (not `class Solution { ... }` wrappers). |
| **C++** | `17/20`. `vector`/`unordered_map` over arrays. Range-based `for`. Structured bindings. `using namespace std` is OK in samples for brevity. |

## Tables

Use them for **trade-off comparisons**. Keep ≤ 5 columns. If a table is wider, restructure as multiple tables or a bulleted list.

## Quotes

Inline quotes get attribution:

```markdown
> "It's not a real distributed system unless it can be partitioned." — Eric Brewer (CAP, 2000)
```

Block quotes for stories. One-liners for punchlines.

## Diagrams

ASCII art is fine and preferred for short diagrams (5–15 lines). For anything larger, drop a static image into `assets/img/` and reference it.

```markdown
![CAP triangle](../assets/img/cap-triangle.svg)
```

## Internal links

Use the SPA hash format:

```markdown
See also [CAP theorem](#/sd/5min/15-cap-theorem) and [the trade-offs deep dive](#/sd/tradeoffs).
```

`build.py` rewrites cross-document Markdown links to hash routes when it can detect them — but explicit hash links are more reliable.

## What NOT to do

- ❌ External "further reading" link dumps. The hub exists so users **don't** bounce. Inline the key idea instead.
- ❌ Copy-pasted code without attribution. If it's from a paper or talk, cite.
- ❌ "TODO" or "WIP" content in `main`. Use a `_drafts/` folder if you need to stage.
- ❌ Long preambles. Get to the trade-off in the first 3 lines.
