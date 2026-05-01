# 🟢 #1 — What is System Design? (5-min read)

## 🎯 TL;DR
**System design is the art of making engineering trade-offs to build large-scale systems that are reliable, scalable, and maintainable.** It's how you go from "a website that runs on my laptop" to "a service that survives 100 million users on a Tuesday afternoon."

---

## 📖 Plain English

When you write a small program, you're solving a problem. When you do **system design**, you're solving a problem *and* answering questions like:

- What if 1,000 users use this at once? What about 1 million? 100 million?
- What happens when a server dies at 3 AM?
- What if the user is in Tokyo and the server is in Virginia?
- How do we deploy a fix without downtime?
- How do we make sure money isn't double-charged when the network blips?

System design is the **blueprint** that answers these. Just like an architect draws up plans before bricks get laid, software architects design the major components — databases, caches, queues, load balancers — and how they fit together **before** anyone writes code.

---

## 🔑 The Core Insight

**Everything is a trade-off.**[^1] There is no "best" architecture. Only "best for these constraints":

- Want strong consistency? You'll likely sacrifice availability or latency.
- Want infinite scale? You'll add operational complexity.
- Want millisecond latency? You'll need caching, which means staleness.

Senior engineers are valuable not because they know the "right answer" — they're valuable because they can **articulate the trade-offs** clearly and pick the one that matches the business need.

---

## 🏗️ A Tiny Example

Imagine you build a URL shortener (`bit.ly`).

**Day 1:** A single server with a SQL database. It works. ✅
**Day 100:** 1M users. The database is slow. Add a **cache**. ✅
**Day 365:** 100M users. One database can't hold it all. Add **sharding**. ✅
**Day 1000:** Worldwide users. Add a **CDN** to serve static content from edge servers. ✅

Each step introduces new trade-offs (cache invalidation, data partitioning, eventual consistency). System design is the process of making those choices deliberately.

---

## 📐 The Two Levels

| Level | Focus | Example |
|---|---|---|
| **High-Level Design (HLD)** | Components, data flow, APIs, infrastructure | "Use Redis cache between API and DB; shard users by user_id" |
| **Low-Level Design (LLD)** | Classes, methods, data structures, design patterns | "RateLimiter class with TokenBucket strategy implementing Iterable<T>" |

System design interviews usually focus on **HLD**. LLD comes up in coding/object-oriented design rounds.

---

## 🚦 When System Design Matters

| Use system design thinking when... | Don't bother when... |
|---|---|
| Building anything serving 1000+ concurrent users | Personal scripts |
| Multiple services need to talk to each other | A one-shot data analysis |
| You need to handle failures gracefully | Throwaway prototypes |
| Money / safety / compliance is involved | Hello-world tutorials |

---

## 🔗 Dig Deeper

- 📘 **First, watch:** [CS75 Harvard Scalability Lecture (David Malan)](https://www.youtube.com/watch?v=-W9F__D3oY4)[^2] — the explicit Step 1 in `donnemartin/system-design-primer`
- 📘 **Then read:** [donnemartin/system-design-primer README](https://github.com/donnemartin/system-design-primer) — sections "Performance vs Scalability" and "Latency vs Throughput"
- 📘 **Book:** *System Design Interview Vol 1* by Alex Xu — Chapter 1 "Scale from Zero to Millions of Users"

---

## 📖 Citations

[^1]: `donnemartin/system-design-primer:README.md` — Trade-offs section explicitly defines Performance vs. Scalability, Latency vs. Throughput, Availability vs. Consistency.
[^2]: [CS75 Lecture 9: Scalability — David Malan, Harvard](https://www.youtube.com/watch?v=-W9F__D3oY4)

---

← [Back to 5-min reads index](./README.md)
