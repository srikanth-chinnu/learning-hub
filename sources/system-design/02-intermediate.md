# 📗 Phase 2: Intermediate — Designing Scalable Systems

> **Goal:** Move from "I understand the parts" to "I can design a non-trivial system end-to-end." This is where you go from junior to mid-level system thinker.

**Duration:** ~4-6 months (10-15 hours/week)
**Prerequisites:** Completed Phase 1 (or equivalent: Alex Xu Vol 1, system-design-primer, hands-on projects).

---

## 🎯 What You'll Learn

By the end of Phase 2 you'll be able to:
- Design Twitter, WhatsApp, Uber, and YouTube at a credible level
- Choose data models, partitioning strategies, and caching layers deliberately
- Reason about trade-offs in microservices vs monolith for a given problem
- Discuss CAP/PACELC and pick consistency level per use case
- Write a serviceable design doc for a feature

---

## 📚 Topics to Master

### 🔀 Load Balancing (deeper)
- L4 vs L7 in detail
- Consistent hashing — when and why
- Health checks — active vs passive
- Active-active vs active-passive
- Connection draining, sticky sessions

### 🚀 Caching Strategies
- The four write strategies: cache-aside, write-through, write-behind, write-around
- Eviction policies — LRU, LFU, FIFO, ARC
- Cache invalidation strategies
- Thundering herd / cache stampede prevention
- Multi-tier caching (browser → CDN → app cache → DB cache)

📖 *5-minute read: [#7 Caching](./5-minute-reads/07-caching.md)*

### 🗄️ Database Scaling
- **Read replicas** — primary-replica, replica lag, read-after-write consistency
- **Vertical vs horizontal partitioning** (functional vs sharding)
- **Sharding strategies** — range, hash, consistent hash, geo, directory-based
- **Choosing a shard key** — the most important DB decision you'll make
- **Cross-shard queries / transactions** — why they hurt; saga pattern alternative
- **Replication topologies** — single-leader, multi-leader, leaderless
- **NoSQL families** — KV, Document, Column-family, Graph

📖 *5-minute reads: [#9 Replication](./5-minute-reads/09-database-replication.md), [#10 Sharding](./5-minute-reads/10-database-sharding.md), [#11 Consistent Hashing](./5-minute-reads/11-consistent-hashing.md)*

### 📨 Message Queues & Async Patterns
- **Queue vs Pub/Sub** — fundamentally different patterns
- **Kafka, RabbitMQ, SQS** — when to choose what
- **Delivery guarantees** — at-most-once, at-least-once, exactly-once
- **Idempotency** — why your consumers MUST be idempotent
- **Dead-letter queues, priority queues, delay queues**
- **Outbox pattern** — atomic write to DB + queue
- **Backpressure & flow control**

📖 *5-minute read: [#13 Message Queues](./5-minute-reads/13-message-queues.md)*

### 🏛️ Microservices vs Monolith
- The Conway's Law principle
- Service boundaries — Domain-Driven Design (DDD) basics
- Inter-service communication — sync (gRPC) vs async (events)
- API gateway patterns
- Service mesh (Istio, Linkerd) — what problem it solves
- Distributed transactions — 2PC, Saga
- The "modular monolith" middle ground

📖 *5-minute read: [#12 Microservices](./5-minute-reads/12-microservices.md)*

### 🌐 Content Delivery Networks (deeper)
- Pull vs push CDN
- Cache-busting URLs vs purge APIs
- Edge compute (Cloudflare Workers, Lambda@Edge)
- Anycast routing

📖 *5-minute read: [#8 CDN](./5-minute-reads/08-cdn.md)*

### 🛑 Rate Limiting (deeper)
- Token Bucket, Leaky Bucket, Sliding Window
- Distributed rate limiting (Redis-based)
- Per-IP, per-user, per-endpoint, per-API-key
- Returning rate limit headers properly

📖 *5-minute read: [#14 Rate Limiting](./5-minute-reads/14-rate-limiting.md)*

### 🔐 Authentication & Authorization
- Sessions vs JWT — pros and cons
- OAuth 2.0 / OpenID Connect basics
- API keys, mTLS for service-to-service
- RBAC vs ABAC
- Where to put the auth — gateway, sidecar, in-service

### 🔍 Search Systems
- Inverted indexes — how Elasticsearch / Lucene work
- Full-text search vs structured filters
- Indexing pipelines
- Real-time vs batch indexing

### 📡 API Design Patterns
- REST best practices, HATEOAS
- Pagination — offset vs cursor (cursor for large datasets)
- Versioning strategies (URL, header)
- Bulk operations
- Webhooks — designing for failure
- Long polling, SSE, WebSockets — when each is right

📖 *5-minute read: [#4 REST vs GraphQL vs gRPC](./5-minute-reads/04-api-styles.md)*

---

## 🎯 The Classic Interview Problems

These are the canonical "design X" problems. Master them.

### Tier A: Must Know
1. **URL Shortener (Bit.ly)** — hashing, base62, KV store
2. **Twitter/X** — fan-out on write vs read, timeline, push vs pull
3. **WhatsApp / Messenger** — XMPP-style, persistent connections, presence
4. **Instagram / Facebook News Feed** — feed generation, ranking, edge cases
5. **Uber / Lyft** — geohashing, real-time matching, location updates
6. **YouTube / Netflix (streaming)** — video pipeline, CDN, adaptive bitrate
7. **Distributed Cache** — consistent hashing, replication, eviction

### Tier B: Strongly Recommended
8. **Distributed Rate Limiter** — token bucket, sliding window in Redis
9. **News Feed (general pattern)** — push vs pull, hybrid
10. **Notification System** — push, fan-out, deduplication
11. **Web Crawler** — politeness, prioritization, dedup, scaling
12. **Distributed File System (Dropbox)** — chunking, dedup, sync
13. **Search Autocomplete (Typeahead)** — trie, ranking, freshness
14. **Top-K problem** — heavy hitters, count-min sketch
15. **Distributed Logging** — Kafka pipeline, ELK, log aggregation

### Tier C: For Interview Prep
16. Stock Exchange / Trading System (low-latency, FIFO)
17. Online Multiplayer Game Backend (real-time, state sync)
18. Yelp / Google Places (geo queries, reviews, ranking)
19. Ticketmaster / StubHub (concurrency, fairness, queueing)
20. ChatGPT-like LLM Service (queueing, autoscaling GPUs)

For each problem:
1. Clarify requirements (functional + non-functional + scale)
2. Estimate the back-of-envelope numbers (RPS, storage, bandwidth)
3. Define the API
4. Sketch HLD components
5. Drill into the **bottleneck** — usually data + scaling story
6. Discuss trade-offs explicitly

---

## 🛠️ Hands-On Projects (Build at Least 2)

### Project 1: Distributed URL Shortener
- Multiple app servers behind NGINX
- Redis for hot URLs
- Postgres with sharding for writes
- CloudFront/CDN for redirect responses
- Rate limiter per API key

### Project 2: Real-Time Chat at Scale
- WebSockets across multiple servers
- Redis Pub/Sub for cross-server message routing
- Postgres for message history
- Read receipts, typing indicators
- Presence service

### Project 3: Twitter Clone
- Tweet creation + timeline
- Fan-out worker (write to followers' timelines)
- Cassandra-style storage (or Postgres + Redis)
- Trending topics (sliding window count)
- Rate limiting + abuse detection

### Project 4: Distributed Rate Limiter Service
- Standalone microservice
- Token bucket algorithm
- Lua script in Redis (atomic check-and-decrement)
- gRPC API
- Configurable per-tenant limits

---

## 📚 Recommended Resources (in priority order)

1. ⭐ **[karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design)** — Chapters III-V cover most of this material
2. ⭐ **System Design Interview Vol 2** by Alex Xu — Chapters on chat systems, news feed, search autocomplete
3. ⭐ ***Designing Data-Intensive Applications*** by Martin Kleppmann — Ch. 3 (Storage), Ch. 5 (Replication), Ch. 6 (Partitioning), Ch. 7 (Transactions), Ch. 11 (Stream Processing)
4. **[ashishps1/awesome-system-design-resources](https://github.com/ashishps1/awesome-system-design-resources)** — comprehensive concept list with diagrams
5. **[ByteByteGoHq/system-design-101](https://github.com/ByteByteGoHq/system-design-101)** — visual flashcards for every concept
6. **[binhnguyennus/awesome-scalability](https://github.com/binhnguyennus/awesome-scalability)** — real architecture case studies
7. **[Grokking the System Design Interview (educative.io)](https://www.educative.io/courses/grokking-the-system-design-interview)** — paid but worth it
8. **[High Scalability blog](http://highscalability.com/)** — historical case studies
9. **[Hussein Nasser YouTube channel](https://www.youtube.com/@hnasr)** — backend deep dives
10. **[codeKarle YouTube channel](https://www.youtube.com/@codeKarle)** — design problems explained

---

## 📖 Reading Plan: Designing Data-Intensive Applications

DDIA is the central book of this phase. Read it slowly:

| Week | Chapter | What to take away |
|---|---|---|
| 1 | Ch. 1: Reliable, Scalable, Maintainable | Foundational vocabulary |
| 2 | Ch. 2: Data Models | Relational vs document vs graph |
| 3-4 | Ch. 3: Storage and Retrieval | B-tree vs LSM-tree |
| 5 | Ch. 4: Encoding | JSON vs Avro vs Protobuf vs Thrift |
| 6-7 | Ch. 5: Replication ★ | Single/multi-leader/leaderless |
| 8 | Ch. 6: Partitioning ★ | Sharding strategies, secondary indexes |
| 9-10 | Ch. 7: Transactions ★ | ACID, isolation levels |
| 11 | Ch. 8: Trouble in Distributed Systems | (Preview of Phase 3) |
| 12 | Ch. 11: Stream Processing | Kafka model, change data capture |

Skip Ch. 9 (Consistency & Consensus) and Ch. 10 (Batch Processing) for now — those belong in Phase 3.

---

## ✅ How to Know You're Ready for Phase 3

Self-check:

1. Can you whiteboard Twitter end-to-end in 45 minutes? (Tweet creation, fan-out, timeline, search, ranking)
2. Can you explain why Discord migrated from MongoDB → Cassandra → ScyllaDB?
3. When would you choose Kafka over RabbitMQ? Why?
4. What's the difference between an outbox pattern and 2PC, and when do you use each?
5. Explain back-of-envelope estimation for "design YouTube" (storage, bandwidth, RPS)
6. What's the difference between consistent hashing and rendezvous hashing?
7. Why does a service mesh exist? What does it buy you?
8. Why does Kafka guarantee ordering only within a partition, not globally?

If yes → ready for [Phase 3: Advanced](./03-advanced.md).

---

⚡ **Tip:** Read the [5-minute reads](./5-minute-reads/README.md) #6-#14 alongside this phase.

← [Previous: Beginner](./01-beginner.md) · [Home](./README.md) · → [Next: Advanced](./03-advanced.md)
