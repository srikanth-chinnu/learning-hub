# 🏗️ System Design: From Scratch to Expert

> Your complete, structured learning path to system design — from absolute beginner to expert-level distributed systems engineer.

---

## 📂 What's in this folder

```
system-design/
├── README.md                  ← You are here (master index + roadmap)
├── 5-minute-reads/            ⚡ Quick-hit primers (read in 5 min each)
│   ├── README.md              (Index of all 5-min reads)
│   └── 20 focused topic files
├── 01-beginner.md             📘 Phase 1: Fundamentals (3-4 months)
├── 02-intermediate.md         📗 Phase 2: Scalable systems (4-6 months)
├── 03-advanced.md             📕 Phase 3: Distributed systems (6-12 months)
├── 04-expert.md               📙 Phase 4: Real-world architectures (ongoing)
├── github-repos.md            🌟 Top 20 GitHub learning resources
├── books-and-courses.md       📚 Books, courses, YouTube channels
└── seminal-papers.md          📄 Must-read CS / distributed systems papers
```

---

## 🎯 The Four-Phase Roadmap

| Phase | Level | Duration | What You Learn |
|---|---|---|---|
| **1** | 📘 [Beginner](./01-beginner.md) | 3-4 months | Networking, OS basics, scalability fundamentals, single-server → multi-server thinking, basic DB/cache/load-balancer |
| **2** | 📗 [Intermediate](./02-intermediate.md) | 4-6 months | Microservices, sharding, caching strategies, message queues, real interview problems (Twitter, WhatsApp, Uber) |
| **3** | 📕 [Advanced](./03-advanced.md) | 6-12 months | CAP/PACELC, Raft/Paxos, distributed transactions, LSM-trees, CRDTs, event sourcing, papers |
| **4** | 📙 [Expert](./04-expert.md) | Ongoing | Netflix/Uber/Discord case studies, design docs, mentorship, org-level architecture |

---

## ⚡ Special: 5-Minute Reads

**Stuck in a meeting? Need a quick refresher? Want to absorb concepts in tiny doses?**

The [`5-minute-reads/`](./5-minute-reads/) folder contains **20 short, focused primers** — each designed to be read in **5 minutes or less** while giving you a working understanding of one concept.

Perfect for:
- ☕ Coffee-break learning
- 🚇 Commute reading
- 🔄 Spaced-repetition review
- 🧠 "What is X, again?" moments
- 🎤 Right before an interview

**[👉 Browse all 5-minute reads](./5-minute-reads/README.md)**

---

## 🗺️ Recommended Learning Sequence

### 🔰 Week 1: Get Oriented (do this first)
1. ⚡ Read all twenty [5-minute reads](./5-minute-reads/README.md) in order — gives you working vocabulary
2. 📘 Open [01-beginner.md](./01-beginner.md) for the structured deep-dive plan

### 📘 Months 1-4: Beginner
- Watch the **CS75 Harvard Scalability Lecture** (David Malan)[^1]
- Read **karanpratapsingh/system-design** Chapters I-II (free GitHub course)
- Read **Alex Xu — System Design Interview Vol 1**
- Watch **ByteByteGo** + **Gaurav Sen** YouTube channels
- See: [01-beginner.md](./01-beginner.md)

### 📗 Months 5-10: Intermediate
- Read **Designing Data-Intensive Applications** (Kleppmann) — Ch. 3, 5, 6, 7, 11
- Read **karanpratapsingh** Chapters III-V
- Solve 10-12 medium design problems (Twitter, YouTube, WhatsApp, Uber)
- Build 2-3 hands-on projects (URL shortener, chat app, rate limiter)
- See: [02-intermediate.md](./02-intermediate.md)

### 📕 Months 11+: Advanced
- Take **MIT 6.824** (Robert Morris) — implement Raft from scratch[^2]
- Read seminal papers: Dynamo, Spanner, Raft, MapReduce
- Watch **Martin Kleppmann's Cambridge course**
- Study production code: etcd, Kafka, RocksDB
- See: [03-advanced.md](./03-advanced.md)

### 📙 Ongoing: Expert
- 2-3 engineering blog posts/week (Netflix, Uber, Discord, Stripe)
- Lead architecture reviews; write design docs (RFCs)
- Read Jepsen analyses of production databases
- See: [04-expert.md](./04-expert.md)

---

## 🚀 Top 5 GitHub Repositories To Bookmark Now

| Stars | Repo | Best For |
|---|---|---|
| 346K ⭐ | [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) | The undisputed #1 system design resource on GitHub |
| 92K ⭐ | [papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love) | Seminal CS / distributed systems papers |
| 82K ⭐ | [ByteByteGoHq/system-design-101](https://github.com/ByteByteGoHq/system-design-101) | Visual-first explanations with hundreds of diagrams |
| 71K ⭐ | [binhnguyennus/awesome-scalability](https://github.com/binhnguyennus/awesome-scalability) | Curated real-world architecture case studies |
| 43K ⭐ | [karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design) | Most structured beginner→intermediate course |

**[👉 See all 20 with details](./github-repos.md)**

---

## 📚 The 4 Books That Cover Beginner→Expert

1. 📘 **System Design Interview Vol 1** — Alex Xu (Beginner)
2. 📗 **System Design Interview Vol 2** — Alex Xu (Intermediate)
3. 📕 **Designing Data-Intensive Applications** — Martin Kleppmann (Advanced) ★★★★★
4. 📙 **Database Internals** — Alex Petrov (Advanced)

**[👉 See full books + courses + YouTube list](./books-and-courses.md)**

---

## 🧭 How to Use This Folder

1. **Don't try to read everything.** Pick your phase, follow the sequence in that file, and move on.
2. **Code beats theory.** Every level has hands-on projects — build them.
3. **Trade-offs > memorization.** The goal is to reason about trade-offs, not memorize answers.
4. **Spaced repetition.** Use Anki flashcards from `donnemartin/system-design-primer` for retention.
5. **5-minute reads are your friend.** Use them as a daily warm-up or refresher.

---

## ⚠️ Common Pitfalls

- ❌ **Starting with DDIA too early** — it's brilliant but dense. Read Alex Xu Vol 1 first.
- ❌ **Skipping networking fundamentals** — DNS, TCP/UDP, HTTP are non-negotiable.
- ❌ **Memorizing instead of reasoning** — every interviewer asks "why?", not "what?".
- ❌ **MIT 6.824 as a beginner course** — it's a graduate research course; needs DDIA + CS fundamentals first.
- ❌ **Over-engineering small problems** — a URL shortener doesn't need Kafka.

---

## 📖 Citations

[^1]: [CS75 Harvard Scalability Lecture by David Malan](https://www.youtube.com/watch?v=-W9F__D3oY4) — explicitly cited as Step 1 in `donnemartin/system-design-primer`.
[^2]: [MIT 6.824 Distributed Systems](https://pdos.csail.mit.edu/6.824/) — Robert Morris + Frans Kaashoek; covers GFS, MapReduce, Raft, Spanner, ZooKeeper, Dynamo with 5 progressive Go labs.

---

*Built from research across 20+ top GitHub repos, MIT 6.824 syllabus, papers-we-love, and verified engineering blogs from Netflix, Uber, Discord, Stripe, Google, Amazon, Meta.*
