# 📘 Phase 1: Beginner — Foundations of System Design

> **Goal:** Build a complete mental model of how scalable systems work. Move from "an app on my laptop" to "I understand how a web service serves a million users."

**Duration:** ~3-4 months (8-12 hours/week)
**Prerequisites:** Comfortable writing code in any language; basic CS knowledge.

---

## 🎯 What You'll Learn

By the end of Phase 1 you'll be able to:
- Explain DNS, HTTP, TCP, UDP, load balancers, and CDN like a pro
- Reason about vertical vs horizontal scaling and stateless services
- Choose between SQL and NoSQL with sound reasoning
- Sketch a high-level architecture for a small web app
- Discuss latency, throughput, availability, and consistency trade-offs

---

## 📚 Prerequisites — Build These First

You can't design systems without understanding the substrate they run on.

### 🌐 Networking (essential)
- **OSI / TCP-IP model** — what each layer does
- **DNS** — recursive resolution, A records, CNAMEs, TTL
- **HTTP/HTTPS** — methods, status codes, headers, cookies
- **TCP vs UDP** — connection-oriented vs connectionless
- **TLS/SSL** — handshake basics, certificates
- **Public-key cryptography** — at conceptual level

📺 **Watch:** [Computer Networking: A Top-Down Approach (Kurose) — youtube playlists](https://www.youtube.com/results?search_query=kurose+computer+networking)
📘 **Read:** [karanpratapsingh/system-design — Chapters: TCP/IP, DNS, HTTP, TLS](https://github.com/karanpratapsingh/system-design)

### ⚙️ Operating Systems (essential)
- **Processes vs threads** — what they share, what they don't
- **Concurrency vs parallelism** — context switches, race conditions
- **Memory hierarchy** — registers, cache (L1/L2/L3), RAM, disk, network
- **File systems & I/O** — sync vs async, blocking vs non-blocking
- **Scheduling basics** — round-robin, priority

📘 **Read:** [Operating Systems: Three Easy Pieces (free book)](https://pages.cs.wisc.edu/~remzi/OSTEP/) — Chapters 4-7, 25-30
📘 **Read:** [karanpratapsingh/system-design — OS section](https://github.com/karanpratapsingh/system-design)

### 🗄️ Databases (essential)
- **SQL fundamentals** — JOINs, indexes, transactions, ACID
- **What an index actually is** (B-Tree)
- **Primary key, foreign key, normalization basics**
- **Query plans** — how the DB decides what to do

📘 **Read:** *Use the Index, Luke!* (free book) — https://use-the-index-luke.com/

### 📐 CS Fundamentals (helpful)
- **Big-O** — at least intuitive understanding
- **Hash maps, trees, linked lists** — when to use what
- **Basic algorithms** — sort, search, BFS/DFS

📘 **Read:** [donnemartin/system-design-primer Anki flashcards](https://github.com/donnemartin/system-design-primer)

---

## 🧠 Core Concepts to Master

### Scalability
- **Vertical vs horizontal scaling** — strengths, ceilings, trade-offs
- **Stateless vs stateful services** — why stateless is the default
- **The role of load balancers** in horizontal scaling
- **CAP theorem** at a basic level (deep dive comes in Phase 3)

### Performance & Reliability
- **Latency vs throughput** — definitions, trade-offs, percentiles (p50/p95/p99)
- **Availability** — calculating SLA (99.9%, 99.99%) and downtime budgets
- **Caching** — why it works, cache hit ratio, basic eviction (LRU)
- **Replication** at the conceptual level

### System Components
- **Web servers vs application servers** — what each does
- **Reverse proxy** vs load balancer (overlap and difference)
- **CDN** — how it makes static content fast globally
- **Message queues** — why async beats sync for many use cases
- **Databases** — SQL vs NoSQL at a high level

### API & Communication
- **REST principles** — verbs, status codes, idempotency
- **HTTP methods semantics** (GET safe & idempotent; POST not idempotent; PUT idempotent; etc.)
- **JSON & data serialization**
- **Authentication basics** — sessions, JWT, OAuth conceptually

---

## 🗓️ A 16-Week Learning Plan

### Weeks 1-2: Networking & OS Refresher
- Watch CS75 Lecture 9 (David Malan)[^1] — gives you the whole stack overview
- Read karanpratapsingh — first 5 chapters (intro through HTTP)
- Build: a simple HTTP server in your favorite language (no frameworks)

### Weeks 3-4: Databases
- Use-the-Index-Luke guide
- karanpratapsingh — Chapter on databases (relational + NoSQL)
- Build: a tiny CRUD API with PostgreSQL; deliberately add an index, measure the speedup

### Weeks 5-6: System Design Primer
- Read [donnemartin/system-design-primer README](https://github.com/donnemartin/system-design-primer) start to finish
- Watch ByteByteGo's "System Design 101" series (YouTube)
- Use the Anki flashcards from the primer (15 min/day)

### Weeks 7-8: Read Alex Xu's Vol 1
- *System Design Interview Vol 1* — Chapters 1-3
- Sketch architectures by hand on paper
- Watch Gaurav Sen's beginner videos in parallel

### Weeks 9-10: Build Project #1 — URL Shortener
- Hash function for short URL
- DB schema
- Caching layer (Redis)
- Rate limiting per IP
- Add a CDN for redirect responses

### Weeks 11-12: Caching & CDN Deep Dive
- Read karanpratapsingh — caching chapter
- Watch ByteByteGo — caching strategies videos
- Add caching to your URL shortener; measure hit rate

### Weeks 13-14: Load Balancing & Replication
- Set up NGINX as reverse proxy / load balancer locally
- Read DDIA Chapter 5 (Replication) — preview of advanced material

### Weeks 15-16: Capstone — Design a Pastebin
- Practice problem from primer & Alex Xu
- Sketch HLD; write a 1-page design doc
- Critique against the canonical solution

---

## 🛠️ Hands-On Projects (Beginner)

### Project 1: URL Shortener (essential)
- Stack suggestion: Python + Flask/FastAPI, Redis, PostgreSQL, NGINX
- Features: shorten, redirect, click count, custom alias, rate limit
- Deploy on a single VPS

### Project 2: Personal Pastebin
- Storage of text snippets with TTL
- Anonymous + auth modes
- Search by title

### Project 3: Real-time Chat (single-room)
- WebSockets
- In-memory store
- Foreshadows distributed-systems concepts

---

## 📚 Recommended Resources (in priority order)

1. ⭐ **[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)** — your bible
2. ⭐ **[karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design)** — most structured course on GitHub
3. ⭐ **System Design Interview Vol 1** — Alex Xu (book)
4. **[ByteByteGo YouTube channel](https://www.youtube.com/@ByteByteGo)** — visual primers
5. **[Gaurav Sen YouTube channel](https://www.youtube.com/@gkcs)** — interview-style walkthroughs
6. **[CS75 Harvard Lecture 9 — Scalability](https://www.youtube.com/watch?v=-W9F__D3oY4)**
7. **[Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)** (free book)
8. **[Use the Index, Luke!](https://use-the-index-luke.com/)** (free)

---

## ❌ What NOT to Do at This Level

- ❌ Don't read DDIA (Kleppmann) yet — it's amazing but dense; will demoralize you
- ❌ Don't watch MIT 6.824 yet — it's a graduate course; needs distributed-systems background
- ❌ Don't try to memorize architectures — focus on the **why**, not the **what**
- ❌ Don't worry about consensus algorithms — they come in Phase 3
- ❌ Don't pick a flashy stack just to learn it — boring tech (Postgres, Redis, NGINX) is best for learning

---

## ✅ How to Know You're Ready for Phase 2

Self-check — can you answer these without notes?

1. What's the difference between a load balancer and a reverse proxy?
2. Why does horizontal scaling require stateless services?
3. When would you choose Cassandra over PostgreSQL?
4. What does "p99 latency = 200ms" tell you about user experience?
5. What's a cache hit ratio and how would you improve it?
6. Why is TCP slower than UDP, and when does that matter?
7. What's a CDN and why does it speed up websites?
8. What's the difference between read-your-writes and eventual consistency?

If yes → ready for [Phase 2: Intermediate](./02-intermediate.md).

---

## 📖 Citations

[^1]: [CS75 Lecture 9: Scalability — David Malan, Harvard](https://www.youtube.com/watch?v=-W9F__D3oY4) — explicitly cited as Step 1 in `donnemartin/system-design-primer`.

---

⚡ **Tip:** Read the [5-minute reads](./5-minute-reads/README.md) #1-#10 alongside this phase. They reinforce the same concepts in tiny digestible pieces.

← [Back to System Design home](./README.md) · → [Next: Intermediate](./02-intermediate.md)
