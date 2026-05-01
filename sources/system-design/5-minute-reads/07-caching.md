# 🟡 #7 — Caching Strategies (5-min read)

## 🎯 TL;DR
**A cache is a fast, in-memory copy of slow-to-fetch data. Caching is the #1 way to make a system faster, but every cache has two hard problems: invalidation and eviction. Know the four write strategies and pick deliberately.**

---

## 📖 Plain English

Your database query takes 50ms. Same query 1 million times = a slow service.

Solution: store the result in **memory** (Redis, Memcached). Next time, fetch in 0.5ms.

```
Without cache:  [App] → [DB] → 50ms
With cache:     [App] → [Cache] → 0.5ms ⚡
```

That's caching. Sounds simple. The hard part is keeping the cache **correct** when data changes.

> *"There are only two hard things in computer science: cache invalidation and naming things."* — Phil Karlton

---

## 🔑 Where Caching Lives (Layers)

| Layer | Example | Latency |
|---|---|---|
| **CPU L1/L2** | Hardware | nanoseconds |
| **Application memory** | In-process map | microseconds |
| **Distributed cache** | Redis, Memcached | <1 ms |
| **CDN edge cache** | Cloudflare, CloudFront | <50 ms (geo) |
| **Browser cache** | HTTP `Cache-Control` | 0 ms |
| **Database cache** | Buffer pool | <1 ms |

**Most systems use multiple layers.** Browser → CDN → Redis → DB.

---

## 📝 The Four Write Strategies

This is **the** intermediate-level concept interviewers love.

### 1️⃣ Cache-Aside (Lazy Loading) — most common
```
Read:   App → cache (miss) → DB → populate cache → return
Write:  App → DB → invalidate cache
```
- ✅ Pros: Only caches what's accessed; resilient (DB is source of truth)
- ❌ Cons: Cache miss penalty; "thundering herd" on popular invalidations

### 2️⃣ Write-Through
```
Write: App → cache → DB (cache writes synchronously to DB)
Read:  App → cache (always populated)
```
- ✅ Pros: Strong consistency; no miss penalty
- ❌ Cons: Higher write latency; caches data that may never be read

### 3️⃣ Write-Behind (Write-Back)
```
Write: App → cache (returns OK)
       cache → DB (asynchronously, batched)
```
- ✅ Pros: Lowest write latency; high throughput
- ❌ Cons: **Data loss risk** if cache dies before flush

### 4️⃣ Write-Around
```
Write: App → DB (skip cache entirely)
Read:  App → cache (miss) → DB → populate cache
```
- ✅ Pros: Good for write-heavy + read-rare
- ❌ Cons: First read is always a miss

**Default choice:** Cache-Aside. Simple, robust, well-understood.

---

## 🚪 Eviction Policies (when cache is full)

| Policy | Strategy | Best for |
|---|---|---|
| **LRU** (Least Recently Used) | Drop the oldest-accessed item | Most general workloads ★ |
| **LFU** (Least Frequently Used) | Drop the least-accessed-overall | Long-lived popular items |
| **FIFO** | Drop the oldest-inserted item | Simple use cases |
| **TTL** (Time-To-Live) | Drop after N seconds | Time-bound data (sessions) |
| **Random** | Drop a random item | Surprisingly OK; very cheap |
| **ARC** (Adaptive Replacement) | LRU + LFU hybrid, self-tuning | When you don't want to choose |

**LRU is the default** in Redis, most systems. Don't overthink.

---

## ❌ When NOT to Cache

1. **Access time of cache ≈ access time of source** — no gain
2. **Low repetition** — every request is unique
3. **Data changes faster than you can invalidate** — cache is always stale
4. **Strong consistency required** — payments, inventory (use cautiously)

---

## 🐝 The "Thundering Herd" Problem

A popular cached value expires. 10,000 requests simultaneously miss the cache. All 10,000 hit the DB. DB melts.

**Solutions:**
- **Request coalescing** — only the first request fetches; others wait
- **Stale-while-revalidate** — serve old value while refetching in background
- **Probabilistic early refresh** — refresh just before expiry
- **Lock-then-fetch** — first miss takes a lock; others retry briefly

Discord's data services layer uses **request coalescing** as a key technique to handle hot keys.[^1]

---

## 🏗️ Real-World Numbers

- **Facebook Memcached:** trillions of requests/day, 99.99% hit rate at the edge[^2]
- **Netflix EVCache:** ~30M ops/sec; up to 30 GB/sec
- **Twitter Redis:** 105 TB RAM, 39M QPS[^3]
- **Stack Overflow:** 90% of pages served entirely from cache

Caching is **the** lever that turns "1000 RPS database" into "1M RPS service."

---

## 🚦 Quick Decision Guide

| Need | Use |
|---|---|
| Session storage | Redis (TTL + LRU) |
| Database query results | Cache-aside with Redis/Memcached |
| Static assets (CSS, JS, images) | CDN with long TTL |
| API responses | HTTP cache headers + CDN |
| Page fragments | Fragment caching in app memory or Redis |

---

## 🔗 Dig Deeper

- 📘 [karanpratapsingh/system-design — Caching chapter](https://github.com/karanpratapsingh/system-design)
- 📘 *Designing Data-Intensive Applications* — discusses caching trade-offs throughout
- 📺 [ByteByteGo: 4 Netflix Caching Strategies](https://www.youtube.com/@ByteByteGo)

---

## 📖 Citations

[^1]: [Discord: Storing Trillions of Messages](https://discord.com/blog/how-discord-stores-trillions-of-messages) — request coalescing in their Rust data services layer.
[^2]: [Scaling Memcache at Facebook (NSDI 2013)](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala)
[^3]: `binhnguyennus/awesome-scalability` repo — How Twitter uses Redis at 105TB / 39M QPS.

---

← [Back to 5-min reads index](./README.md)
