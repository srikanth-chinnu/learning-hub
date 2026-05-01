# Trade-offs in System Design: A Comprehensive Guide (HLD + LLD in Python & C++)

> **Companion to:** `system-design/` folder (00-intro through 04-expert)
> **Audience:** Engineers who want to *reason* about trade-offs, not memorize them.
> **How to use:** Read Part 1 (mental models) once. Then dip into Parts 2–4 by topic. Use Part 5 (decision matrices) as a cheat sheet when you're actually designing.

---

## Executive Summary

There is exactly one correct answer to almost every system-design interview question, and it is **"it depends — on what?"** The job of a senior engineer is not to know which technology is "best." It is to identify the **two or three axes** on which a real decision turns, articulate the **trade-off curve** along each axis, and then pick the point on the curve that matches the **business and operational reality** in front of them.

This guide catalogues the trade-offs that recur in real systems:

- **Part 1 — Mental models.** Six lenses (two-way doors, "choose boring technology," hierarchy of needs, "it depends *on what*?", monolith-first, the constant-work pattern) for thinking about *any* trade-off.
- **Part 2 — HLD trade-offs.** ~40 cataloged decisions across foundational theorems (CAP/PACELC/FLP), data tier (replication, sharding, caching, queues), architecture patterns (monolith vs microservices, REST/gRPC/GraphQL, CQRS, Lambda/Kappa), resilience (circuit breakers, retries, timeouts, bulkheads, load shedding) and operations (multi-region, observability).
- **Part 3 — LLD in Python.** ~20 trade-offs with runnable snippets (SOLID, Singleton/Borg/module, Factory, Strategy, Observer, State, Adapter, Builder, Repository, DI, Decorator, duck-typing, dataclasses, `__slots__`).
- **Part 4 — LLD in C++.** ~26 trade-offs with snippets (parameter passing, move semantics & RVO, Rule of 0/3/5, smart pointers, `optional`/`variant`/`any`, Sean-Parent value semantics, virtual vs CRTP vs `std::function` vs concepts, EBO, RAII, container choice, SBO/SSO, PMR, false sharing, `constexpr`, threads vs async, `mutex` vs atomics, PIMPL).
- **Part 5 — Decision matrices** you can paste into a design doc.
- **Part 6 — Case studies.** Discord's MongoDB → Cassandra → ScyllaDB migration; Stripe's online migrations methodology.

A meta-point that runs through everything: **most trade-offs are not symmetric.** One side is usually a **two-way door** (cheap to undo) and the other a **one-way door** (expensive). When in doubt, take the two-way door first.

---

# PART 1 — How to Think About Trade-offs

## 1.1 The Six Mental Models

### Model 1: Two-way doors vs one-way doors (Bezos, 2015 shareholder letter)

> "Some decisions are consequential and irreversible or nearly irreversible — one-way doors — and these decisions must be made methodically, carefully, slowly, with great deliberation and consultation. ... But most decisions aren't like that — they are changeable, reversible — they're two-way doors." — Jeff Bezos, 2015

**Apply it:**
- Choosing a feature flag system → two-way door (rip and replace in a sprint).
- Choosing your primary datastore → one-way door (migrations take *quarters*; see Discord's MongoDB → Cassandra → ScyllaDB story below).
- Choosing your event schema (Kafka topic format) → one-way door for downstream consumers; deserves design review.
- Choosing a Python web framework → two-way door (FastAPI/Flask are largely interchangeable for CRUD).

**The asymmetry rule:** When the door is two-way, **bias toward action**. When it is one-way, **bias toward deliberation** and write it down.

### Model 2: Choose Boring Technology (Dan McKinley, 2015)

> "Let's say every company gets about three innovation tokens. You can spend these however you want, but the supply is fixed for a long time. ... If you choose to write your website in NodeJS, you just spent one of your innovation tokens. If you choose to use MongoDB, you just spent one of your innovation tokens. If you choose to use service discovery tech that's existed for a year or less, you just spent one of your innovation tokens." — Dan McKinley, *Choose Boring Technology*

**Apply it:** Postgres, Redis, nginx, RabbitMQ are boring. They have known failure modes, large hiring pools, mature client libraries, and a decade of Stack Overflow answers. Spend innovation tokens on the **one or two things that are actually your business differentiator**, not on the database.

**The corollary:** "Boring" ≠ "outdated." Postgres in 2025 is far more capable than most NoSQL stores were in 2015. The boring tools have been *secretly accumulating features*.

### Model 3: "It depends — on what?"

When you say "it depends," **always answer the follow-up before it's asked.** The variables that almost every architecture decision turns on:

| Variable | Why it matters |
|---|---|
| **Read:write ratio** | 99:1 reads → caching, read replicas, denormalization. 1:99 writes → log-structured storage, async pipelines. |
| **Consistency requirement** | Money/inventory → strong. Likes/views → eventual is fine. |
| **Latency budget (p50, p99, p99.9)** | <10ms p99 → in-memory + same-region. <1s → cross-region OK. |
| **Throughput (RPS, peak vs avg)** | 10× spikes → autoscaling + queues. Steady → simpler provisioning. |
| **Data size & growth rate** | TB/day → partition early. GB/year → don't bother. |
| **Team size & expertise** | 3 devs → monolith. 300 devs → service per team. |
| **Cost sensitivity** | Startup → cloud-managed everything. Hyperscale → buy the hardware. |
| **Regulatory** | GDPR/HIPAA/PCI → data residency, audit logs, encryption at rest. |
| **Failure cost** | Plane control system vs ad-click counter — *very* different bars. |

**Interview tip:** Before sketching boxes and arrows, **ask three of these questions**. The interviewer will notice; it is the single most senior-engineering signal you can give.

### Model 4: The Hierarchy of Needs

Like Maslow, optimize from the bottom up. Don't tune cache sizes if your data is wrong.

```
        ┌──────────────────────┐
        │       Cost           │  ← optimize last
        ├──────────────────────┤
        │     Performance      │
        ├──────────────────────┤
        │     Reliability      │
        ├──────────────────────┤
        │     Correctness      │  ← optimize first
        └──────────────────────┘
```

A 50-ms response that's wrong is worse than a 500-ms response that's right. A 99.99%-reliable system that occasionally double-charges customers is a **lawsuit**, not a system.

### Model 5: MonolithFirst (Martin Fowler, 2015)

> "Almost all the successful microservice stories have started with a monolith that got too big and was broken up. Almost all the cases where I've heard of a system that was built as a microservice system from scratch, it has ended up in serious trouble." — Martin Fowler, *MonolithFirst*

**Why:** You don't know the right service boundaries until you've lived with the domain. Premature decomposition fossilizes the *wrong* boundaries — and undoing them across a network boundary is a one-way door.

**Exception:** When you already have a deeply understood domain (e.g., the team is rebuilding a known system) or when the workload of one component is so different (e.g., ML inference on GPUs) that bundling it makes no sense.

### Model 6: The Constant Work Pattern (AWS Builders' Library)

A system whose load *doesn't change* under failure is more reliable than one that scales up exotic recovery code paths exactly when things are worst. AWS's Route 53 health checker pushes a **full configuration** to every edge every few seconds whether anything changed or not. Cost: bandwidth. Benefit: the failure path *is* the steady-state path; there are no "untested under load" code paths.

**Apply it:** Prefer a daily full snapshot over a clever incremental sync that breaks during outages.

## 1.2 The Three Questions to Ask Before Any Decision

1. **What does success look like (in numbers)?** — Without an SLO/budget you have no way to know if a trade-off is acceptable.
2. **What's the blast radius if I'm wrong?** — Is this a two-way or one-way door?
3. **What's the simplest thing that could possibly work?** — If the simplest thing meets (1), don't pay for more.

---

# PART 2 — HLD Trade-offs

## 2A. Foundational Theorems

### CAP (Brewer, 2000; proven by Gilbert & Lynch 2002)

In the presence of a **network Partition**, you must choose between **Consistency** (all nodes see the same data) and **Availability** (every request gets a response).

**The 2012 revision (Brewer, IEEE Computer / InfoQ):**

> "The 2 of 3 formulation was always misleading because it tended to oversimplify the tensions among properties. ... The modern CAP goal should be to maximize combinations of consistency and availability that make sense for the specific application."

**Practical reading:**
- Partitions are **rare** (within a datacenter) but **inevitable** (cross-region).
- "Choose CP or AP" is the wrong frame. Real systems choose **per-operation** — strong-consistency for writes to the order ledger, eventual for the recommendation feed.
- During non-partition operation, the choice is between **latency and consistency** (PACELC).

### PACELC (Daniel Abadi, 2010)

> "If there is a Partition (P), how does the system trade off Availability and Consistency (A and C); else (E), when the system is running normally in the absence of partitions, how does the system trade off Latency (L) and Consistency (C)?"

| System | Partition behavior | Normal behavior |
|---|---|---|
| Dynamo / Cassandra / Riak | PA (sacrifice C for A) | EL (sacrifice C for low L) |
| BigTable / HBase / MongoDB (default) | PC (sacrifice A for C) | EC (sacrifice L for C) |
| MySQL / Postgres (single primary) | PC | EC |
| Spanner | PC (CP) | EC (Paxos round-trip cost) |
| PNUTS (Yahoo) | PA | EC |

**Interview gold:** Quote PACELC, not just CAP. It signals you understand the *latency* axis even when nothing is broken.

### FLP Impossibility (Fischer, Lynch, Paterson, 1985)

In an **asynchronous** system with even **one** crash failure, you cannot have a **deterministic** consensus algorithm that is *both* always-safe AND always-live.

**What this means in practice:** Paxos, Raft, etc., are **safe** (never wrong) but only **live with a synchrony assumption** (e.g., timeouts). They can stall during network instability. This is why your Raft cluster sometimes "elects forever" during a flaky network.

## 2B. Data Tier Trade-offs

### ACID vs BASE

| | ACID (RDBMS) | BASE (NoSQL) |
|---|---|---|
| **A** | Atomic | Basically Available |
| **C** | Consistent | Soft state |
| **I** | Isolated | Eventually consistent |
| **D** | Durable | (also durable, usually) |

Werner Vogels (Amazon CTO): *"In an environment where we accept that consistency may be eventual, we get higher availability, better partition tolerance and lower latency."*

**Rule of thumb:** Money, inventory, identity → ACID. Counts, feeds, recommendations, analytics → BASE.

### Replication Trade-offs

#### Master-slave (single-leader)
- **Pros:** Simple, strong consistency on master, easy to reason about. Postgres streaming replication, MySQL binlog.
- **Cons:** Master is SPOF (until failover); writes don't scale; replica lag = stale reads.

#### Multi-master
- **Pros:** Writes scale; survives leader loss.
- **Cons:** **Conflict resolution** is the swamp. Last-write-wins loses data. CRDTs work for some types (counters, sets) but not arbitrary records.

#### Leaderless (Dynamo-style)
- **Pros:** No leader to fail; tunable consistency via R+W>N.
- **Cons:** Read-repair / anti-entropy adds complexity; can serve stale reads even with quorum.

#### Sync vs Async replication
- **Sync:** Write doesn't ack until N replicas durable. **Latency cost:** at minimum one cross-region RTT (~70ms US east↔west). **Benefit:** zero RPO (no data loss on primary failure).
- **Async:** Fast writes, **non-zero RPO** — if primary dies, you can lose the last few seconds.
- **Semi-sync:** Compromise; ack after one replica gets it. MySQL's default for production HA.

### Sharding (Partitioning) Trade-offs

| Strategy | Pros | Cons | When to use |
|---|---|---|---|
| **Hash partitioning** | Even distribution; simple. | No range scans; resharding is painful (consistent hashing helps). | UUIDs, user IDs. |
| **Range partitioning** | Range scans cheap; ordered iteration. | Hot spots (e.g., `created_at` shard burning). | Time-series, lexicographic keys. |
| **Geo / directory** | Locality; data residency. | Manual shard management; rebalancing. | GDPR / per-region products. |
| **Composite (hash-of-prefix + range)** | Spread + locality. | Complex. | Cassandra's partition+clustering keys. |

**The hot-shard problem:** If 1% of users generate 50% of traffic (Pareto), hash partitioning *still* concentrates them on one shard. Solutions: **sub-shard hot keys** (e.g., `user:42:shard_3`), **add a randomized suffix**, or **route hot keys to dedicated shards**.

### Caching: Five Patterns

| Pattern | Read path | Write path | Consistency | Pros | Cons |
|---|---|---|---|---|---|
| **Cache-aside (lazy load)** | App checks cache → miss → load DB → fill cache. | App writes DB and **invalidates** cache. | Eventual. | Most flexible; cache failure ≠ app failure. | Stale on race conditions; thundering herd on miss. |
| **Read-through** | App calls cache; cache loads on miss. | Same as cache-aside. | Eventual. | App code is simpler. | Cache library coupling. |
| **Write-through** | Same as read-through. | App writes cache → cache writes DB synchronously. | Strong. | No stale reads. | Higher write latency. |
| **Write-back / write-behind** | Cache. | App writes cache; cache asynchronously flushes to DB. | Eventual; data loss if cache crashes. | Massive write throughput. | Durability risk. |
| **Write-around** | Cache-aside. | App writes DB only; cache filled lazily on next read. | Eventual. | Avoids cache pollution from rarely-read writes. | First read after write is a miss. |

### Cache Invalidation: The Real Hard Problem

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

| Strategy | Pros | Cons |
|---|---|---|
| **TTL** | Trivial. | Stale until expiry; thundering herd on expiry. |
| **Explicit invalidation on write** | Fresh. | Easy to miss a write path; no global view. |
| **Versioned keys** (`user:42:v17`) | Atomically swap. | Stale entries linger (need eviction or LRU). |
| **Write-through** | Always fresh. | Coupled write path. |
| **Pub/sub invalidation** (Redis keyspace events) | Multi-region. | Eventual; messages can be lost. |

**Meta TAO:** Achieved cache hit rates of 99.99999999% (10 nines) by combining a write-through layer with a leaderless invalidation broadcast. Quote from the team: *"Going from six nines to ten nines was about eliminating the categories of bug, not optimizing the average case."*

### Cache Stampede / Thundering Herd

When a hot key expires, *every* request misses simultaneously and stampedes the database.

**Mitigations:**
1. **Singleflight** — only one request per key fetches; the rest wait. Go's `singleflight.Group` is the canonical implementation.
2. **Probabilistic early expiration** — refresh with probability that increases as TTL approaches.
3. **Stale-while-revalidate** — serve the stale value while refreshing in the background.
4. **Coalescing at the cache layer** — Discord uses request coalescing inside their cache service so 1M concurrent reads of the same expired key result in 1 DB read.
5. **Pre-warm** — daemon refreshes hot keys before they expire.

### Cache Eviction: LRU / LFU / ARC / TinyLFU

| Algorithm | Recency | Frequency | Use when |
|---|---|---|---|
| **LRU** | ✓ | ✗ | General-purpose; most common. |
| **LFU** | ✗ | ✓ | Workloads with stable popularity (e.g., CDN edge). |
| **ARC** | ✓ | ✓ (adaptive) | Database buffer pools (Postgres considers it; ZFS ships it). |
| **TinyLFU / W-TinyLFU** | ✓ | ✓ (sketched) | Modern caches (Caffeine, Ristretto). Very low metadata overhead via Bloom-style sketches. |

### Message Queues: Kafka vs RabbitMQ vs SQS vs Pulsar vs NATS

| | Kafka | RabbitMQ | SQS | Pulsar | NATS |
|---|---|---|---|---|---|
| **Model** | Distributed log | Broker (smart) | Managed queue | Distributed log + queue | Pub/sub + JetStream |
| **Ordering** | Per partition | Per queue | FIFO mode | Per partition | Per subject (with JS) |
| **Throughput** | 100k–1M msg/s/partition | 20–50k/queue | High but per-shard | Comparable to Kafka | Very high (single-digit μs) |
| **Latency** | 5–30 ms | <1 ms | 10–100 ms | 5–30 ms | <1 ms |
| **Retention** | Long (TB-scale) | Short (queue empties) | 14 days max | Tiered (long) | Configurable |
| **Push vs Pull** | **Pull** | Push | Pull | Both | Push |
| **Use case** | Event sourcing, streaming, log aggregation | Task queues, RPC, work distribution | Cloud-native simple queueing | Multi-tenant, geo-replication | Microservice mesh, IoT |

**Why Kafka uses pull:** Pull is structural backpressure — slow consumers can't be overwhelmed; they just lag. Push systems require careful credit/flow-control protocols (RabbitMQ has them, but they're hard).

### Delivery Semantics

| Semantic | What it means | How |
|---|---|---|
| **At-most-once** | Send and forget. | UDP-style, fire-and-forget. |
| **At-least-once** | Will retry until ack. **Duplicates possible.** | Default for most queues. Requires idempotent consumers. |
| **Exactly-once** | Each message processed exactly once. | **Hard.** Kafka transactions (within Kafka). End-to-end requires idempotent consumers + dedup. |

**The Outbox Pattern (poor man's exactly-once across DB+queue):**
1. App opens DB transaction.
2. Writes business row + a row to `outbox` table — atomically.
3. Separate poller reads `outbox`, publishes to queue, marks row as published.

Avoids 2PC (which is operationally horrible and has well-known FLP-related liveness issues). Used by Stripe, Shopify, many event-sourced systems.

### Lambda vs Kappa Architectures

**Lambda (Marz, 2011):** Two parallel pipelines — batch (correct, slow) and speed (approximate, fast). Query layer merges.
- **Pro:** Reprocess history when logic changes.
- **Con:** Two codebases, two operational stacks, eventual consistency between layers.

**Kappa (Kreps, 2014, *Questioning the Lambda Architecture*):** One stream pipeline. Reprocess by replaying the log from offset 0.

> "If you can replay your log, you don't need a separate batch pipeline." — Jay Kreps

**When Lambda still wins:** Heavy ML training jobs that need full historical scans on a different engine (Spark) than the streaming engine (Flink).

### Coordination Avoidance / I-Confluence (Bailis et al., VLDB 2015)

The cheapest distributed system is the one that doesn't coordinate. **Coordination-free** operations include:
- Counter increments (CRDT).
- Adding to a set (CRDT G-Set).
- Append-only logs.
- Idempotent inserts with UUID PKs.

**Coordination required:**
- Unique constraints (username taken?).
- Bank transfer with negative-balance check.
- Inventory decrement when stock approaches 0.

**Design principle:** Push coordination to the *boundary* of the system (one Postgres row holds the unique constraint) and keep the hot path coordination-free.

### Consensus: Paxos / Raft / ZAB / Multi-Paxos

| | Use |
|---|---|
| **Paxos** (Lamport 1998) | Foundational. Hard to implement correctly. |
| **Multi-Paxos** | Streamlined Paxos for log replication. |
| **Raft** (Ongaro & Ousterhout 2014) | Designed for understandability. etcd, Consul, TiKV. **Default choice today.** |
| **ZAB** | ZooKeeper. |
| **PBFT / HotStuff** | Byzantine — needed only for blockchain or hostile environments. |

**Crash-fail vs Byzantine:**
- Crash-fail: nodes either work correctly or stop. Tolerate `f` failures with `2f+1` nodes.
- Byzantine: nodes can lie. Tolerate `f` with `3f+1` nodes. **3× the cost.** Almost no internal corporate system needs this.

## 2C. Architecture Pattern Trade-offs

### Monolith vs Microservices vs Modular Monolith

| | Monolith | Modular monolith | Microservices |
|---|---|---|---|
| **Deploy unit** | 1 | 1 | N |
| **Boundary enforcement** | Code review | Module/package boundaries | Network |
| **Refactor across boundary** | Easy (rename) | Easy (move file) | Hard (API + data migration) |
| **Independent scaling** | All-or-nothing | All-or-nothing | Per-service |
| **Independent deploy** | No | No | Yes |
| **Operational burden** | Low | Low | **High** (service discovery, mesh, observability per service) |
| **Failure mode** | All-or-nothing | All-or-nothing | Cascading; need circuit breakers everywhere |
| **Hire/onboard** | Easy | Easy | Hard (each service has its own state) |

**Heuristic:** Stay monolithic until either (a) team size > Dunbar's-number-ish (~150 engineers) OR (b) you have a *real* scale-asymmetric component (ML inference on GPUs, low-latency trading core, etc.).

### REST vs gRPC vs GraphQL vs WebSockets

| | REST | gRPC | GraphQL | WebSockets |
|---|---|---|---|---|
| **Transport** | HTTP/1.1 or 2 | HTTP/2 | HTTP | TCP upgrade |
| **Encoding** | JSON | Protobuf (binary) | JSON | Anything |
| **Schema** | OpenAPI (optional) | .proto (required) | SDL (required) | None |
| **Streaming** | SSE workaround | Bidi native | Subscriptions (over WS) | Native |
| **Browser-native** | Yes | No (needs gRPC-Web proxy) | Yes | Yes |
| **Best for** | Public APIs, CRUD | Internal microservices | Aggregation across many backends, mobile | Real-time push |

**Cost of gRPC:** Operational complexity (HTTP/2 ALB quirks, harder debugging — need `grpcurl`), not browser-native.
**Cost of GraphQL:** N+1 queries on the resolver layer (need DataLoader); harder caching (no URL-based HTTP cache); query complexity attacks.

### CQRS (Command Query Responsibility Segregation)

Split write model from read model. Writes go to a normalized OLTP store; reads go to denormalized projections optimized for queries.

**When to use:** When read load >> write load AND read patterns are diverse (multiple denormalizations needed).
**When NOT to use:** Most CRUD apps. The eventual consistency between write and read sides is *real*; users see "I just saved this — why isn't it in my list?" complaints.

### Event Sourcing

Store the *log of state-changing events*, not the current state. Project current state by replay.

**Pros:** Full audit log; time-travel; replay to fix bugs; natural fit for CQRS.
**Cons:** Schema evolution of events is *hard* (events are immutable forever); querying current state requires projections; debugging requires replaying from snapshot.

**Don't apply globally.** Apply to *specific bounded contexts* where the audit log is intrinsic to the business (banking ledger, order lifecycle, IoT telemetry).

## 2D. Resilience Pattern Trade-offs

### Circuit Breakers (Hystrix-style)

States: **Closed** (pass through) → **Open** (fast-fail) → **Half-open** (probe).

**Trade-off:**
- **Threshold too low** → opens on transient blips → unnecessary outages.
- **Threshold too high** → never opens → your callers cascade-fail because you're not failing fast.

**Tune by:** % failures over rolling window (e.g., 50% over 10s with min 20 requests). Always combine with **timeouts** — a circuit breaker without timeouts is decoration.

### Retries

> "Retries are 'selfish.' What I mean is that when a client retries, it takes more of the server's time to get a higher chance of success. ... When the server is healthy, retries fix transient faults. When the server is unhealthy, retries amplify the problem." — AWS Builders' Library, *Timeouts, retries, and backoff with jitter*

**Always combine retries with:**
1. **Exponential backoff** — `wait = base * 2^attempt`.
2. **Jitter** — `wait = random(0, base * 2^attempt)`. **Without jitter, you get retry storms** (every client retries at the same beat).
3. **Cap on total attempts** — typically 3.
4. **Token bucket** at the *caller* — caps the *rate* of retries even when many requests are failing simultaneously.

### Timeouts

The worst timeout is no timeout. The second-worst is the wrong timeout.

**Heuristic:** Timeout = 99.9th-percentile observed latency × 1.5–2. *Not* the average. Use percentiles.

**Cascading timeouts:** Caller timeout MUST be > callee timeout, OR the caller cancels work the callee is still doing → wasted resources. Prefer **deadline propagation** (gRPC native; HTTP via `X-Deadline-Ms` header) — every hop subtracts its expected work and forwards the remaining budget.

### Bulkheads

Isolate resources so one slow dependency doesn't drain *all* threads.

```
Request pool (200 threads) — bad: one slow downstream eats them all
   vs
Bulkheaded:
  Pool A (50 threads) → Service X
  Pool B (50 threads) → Service Y
  Pool C (50 threads) → Service Z
  Pool D (50 threads) → spillover/critical
```

If X dies, A is starved but B/C/D still serve. **Cost:** Each pool is sized for peak — total capacity > undivided pool. **Worth it** for any system with >1 critical dependency.

### Fallback / Default Responses

> "Fallbacks are a deceptive safety net. They look like resilience, but they often just delay the failure or move it somewhere harder to see." — AWS Builders' Library

**Use fallbacks ONLY when:**
- The fallback is **truly equivalent** in business terms (e.g., empty recommendation list is fine; missing payment auth is *not*).
- You can **distinguish primary from fallback in your metrics** so you don't accidentally serve degraded experiences for weeks.

### Load Shedding

When overloaded, **drop requests with intent**. Two key techniques:

1. **Prioritization queues** — health checks, control plane > user reads > user writes > batch.
2. **LIFO (Last-In-First-Out) shedding** — when the queue is too long, serve the *newest* requests, drop the *oldest*. Counter-intuitive but **the oldest request's user has already given up** (closed the browser tab); serving them is wasted work.

**Brownout vs blackout:** Prefer brownout (degrade non-critical features) to blackout (whole-service down).

## 2E. Operations Trade-offs

### Multi-Region: Active-Passive vs Active-Active

| | Active-Passive | Active-Active |
|---|---|---|
| **Cost** | 2× | 2× |
| **Failover** | Manual or DNS, ~minutes | Automatic, ~seconds |
| **Data sync** | Async replication | Multi-master or per-region with reconciliation |
| **Complexity** | Low | High (conflict resolution; user routing) |
| **RTO** | minutes-hours | seconds-minutes |
| **RPO** | seconds-minutes (async lag) | depends — can be near-zero with sync |
| **Conflict possibility** | None (writes only in one region) | Real (need CRDT, LWW, or business-level merge) |

**The honest answer:** Most companies *think* they're active-active, but their data layer is single-region. They can serve reads globally, but writes go to one region.

### Routing: Geo-DNS vs Anycast

| | Geo-DNS | Anycast |
|---|---|---|
| **Mechanism** | DNS returns nearest region's IP. | Many regions advertise the *same* IP via BGP; routers pick. |
| **Failover speed** | Bounded by TTL (often minutes). | Sub-second (BGP convergence). |
| **Stickiness** | Per-DNS-cache (ISP, browser). Up to TTL. | Per-flow; can flap mid-session. |
| **Use** | App tier (HTTP/HTTPS via CDN). | Authoritative DNS (Route 53), edge gateways (Cloudflare). |

### Observability: Sampling

| | Head-based | Tail-based |
|---|---|---|
| **Decision time** | Start of trace. | End of trace. |
| **Throws away** | A fraction of *all* traces. | Sampled non-interesting traces; **always keeps errors and slow traces**. |
| **Cost** | Cheap. | Memory: must buffer trace until end. |
| **Use** | High-volume normal-case observation. | Debugging — keeps the rare interesting traces. |

### Cardinality (Charity Majors / Honeycomb)

> "Cardinality is the number of unique values per dimension. High-cardinality dimensions like user-id, request-id, build-id are exactly the dimensions you most want to debug with — and they are exactly the ones legacy metrics tools cannot handle." — Charity Majors

**Trade-off:**
- Metrics (Prometheus, etc.) are *cheap* but cap cardinality (each label combination is a new time series).
- Wide events / structured logs (Honeycomb, Lightstep, ClickHouse) handle high cardinality but cost more.

**Rule:** Don't put `user_id` as a Prometheus label. Do put it in the wide event for tracing.

---

# PART 3 — LLD Trade-offs (Python)

> Code targets Python 3.11+. All snippets are runnable. Source patterns: Brandon Rhodes (`python-patterns.guide`), the `dataclasses` and `abc` stdlib docs, and battle-tested industry usage.

## 3.1 SOLID in Python (with ABCs)

### Single Responsibility (SRP)
A class should have one reason to change. In Python, this is often enforced by **module boundaries**, not class hierarchy.

```python
# Bad: a User that does too much
class User:
    def __init__(self, name): self.name = name
    def save(self): ...      # persistence
    def send_email(self): ... # comms
    def render_html(self): ...# presentation

# Better: separate by responsibility
@dataclass
class User: name: str

class UserRepository:    # persistence
    def save(self, user: User): ...

class UserMailer:        # comms
    def send_welcome(self, user: User): ...

class UserView:          # presentation
    def render(self, user: User) -> str: ...
```

**Trade-off:** More files, more glue. **Worth it** when each responsibility changes for *different* reasons.

### Liskov Substitution — the Square/Rectangle trap

```python
class Rectangle:
    def __init__(self, w: int, h: int): self.w, self.h = w, h
    def set_width(self, w):  self.w = w
    def set_height(self, h): self.h = h
    def area(self) -> int:   return self.w * self.h

# LSP violation: Square IS-A Rectangle? No — Square breaks Rectangle's invariants.
class Square(Rectangle):
    def set_width(self, w):  self.w = self.h = w     # surprise!
    def set_height(self, h): self.w = self.h = h     # surprise!

def stretch(r: Rectangle):
    r.set_width(10); r.set_height(5)
    assert r.area() == 50    # FAILS for Square — area becomes 25
```
**Fix:** Don't model "is-a" by inheritance when invariants differ. Use **composition** or separate types.

### Interface Segregation via ABCs / Protocols

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> bytes: ...

class Writable(Protocol):
    def write(self, data: bytes) -> int: ...

# A function that only reads: depend only on Readable
def hash_file(f: Readable) -> str: ...
```
**Trade-off:** ABCs (`abc.ABC`) enforce inheritance; `Protocol` enables structural typing (duck typing for type checkers). **`Protocol` is preferred** in modern Python — looser coupling, easier testing.

## 3.2 `@property` vs Direct Attribute Access

```python
class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def celsius(self) -> float: return self._celsius

    @celsius.setter
    def celsius(self, v: float):
        if v < -273.15: raise ValueError("below absolute zero")
        self._celsius = v

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9/5 + 32
```
**Pythonic principle ("uniform access"):** Start with public attributes. Promote to `@property` *only when* you need validation or computation, with **no caller change** required. This is one of Python's superpowers — Java needs getters/setters everywhere defensively.

## 3.3 Singleton vs Borg vs Module

Brandon Rhodes' verdict (`python-patterns.guide`): *"In Python, the Singleton pattern is unnecessary — modules ARE singletons."*

```python
# Approach 1: Module-level (idiomatic — preferred)
# config.py
_settings = {"db_url": "..."}
def get(k): return _settings[k]
def set(k, v): _settings[k] = v

# Approach 2: Singleton via __new__
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Approach 3: Borg (shared state, multiple instances)
class Borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = Borg._shared_state
```
| | Pros | Cons |
|---|---|---|
| Module | Simple; tests can `monkeypatch`. | Hard to have configurable instance. |
| Singleton | Familiar from Java. | Hard to test (can't reset between tests). |
| Borg | Shared state, multiple instances. | Confusing to readers. |

**Recommendation:** Use modules. If you need a class for configurability, accept that **you have a class with two instances during tests** and inject it.

## 3.4 Factory: Function vs Abstract Factory

```python
# Function-style (Pythonic)
def make_logger(kind: str):
    if kind == "json": return JsonLogger()
    if kind == "text": return TextLogger()
    raise ValueError(kind)

# Abstract Factory (when you need *families* of related objects)
class UIFactory(Protocol):
    def make_button(self) -> Button: ...
    def make_window(self) -> Window: ...

class MacFactory:
    def make_button(self): return MacButton()
    def make_window(self): return MacWindow()
```
**Trade-off:** Functions for one product type; Abstract Factory when product families must stay consistent.

## 3.5 Strategy: Function-based vs Class-based

```python
# Class-based (when state)
class CompressionStrategy(Protocol):
    def compress(self, data: bytes) -> bytes: ...

class GzipStrategy:
    def __init__(self, level=6): self.level = level
    def compress(self, d): import gzip; return gzip.compress(d, self.level)

# Function-based (when stateless — preferred when possible)
import gzip, lzma
strategies = {"gzip": gzip.compress, "lzma": lzma.compress}
result = strategies["gzip"](data)
```
**In Python, functions are first-class.** Don't make a class for a single method without state. (`__call__` exists when you need both.)

## 3.6 Observer vs Pub-Sub

| | Observer (in-process) | Pub-Sub (decoupled / distributed) |
|---|---|---|
| **Coupling** | Subject knows observers (or via list). | Through a broker (Redis, Kafka, AsyncIO event loop). |
| **Sync/async** | Usually sync. | Usually async. |
| **Process boundary** | Same process. | Same or distributed. |

```python
# Observer (sync, in-process)
class Subject:
    def __init__(self): self._obs = []
    def subscribe(self, fn): self._obs.append(fn)
    def notify(self, ev):
        for fn in self._obs: fn(ev)

# Pub-Sub via asyncio
import asyncio
class AsyncBus:
    def __init__(self): self._subs = {}
    def subscribe(self, topic, q): self._subs.setdefault(topic, []).append(q)
    async def publish(self, topic, msg):
        for q in self._subs.get(topic, []): await q.put(msg)
```

## 3.7 State Pattern vs if/elif

```python
# if/elif: fine for 2-3 states
class VendingMachine:
    def __init__(self): self.state = "idle"
    def insert(self):
        if self.state == "idle": self.state = "has_money"; return
        if self.state == "has_money": print("already inserted"); return
        if self.state == "dispensing": raise RuntimeError("wait")
    # ... 7 more methods × 4 states = 28 if/elif branches

# State pattern (when many states × many transitions)
class State(Protocol):
    def insert(self, m: "VendingMachine"): ...
    def select(self, m): ...
    def dispense(self, m): ...

class IdleState:
    def insert(self, m): m.state = HasMoneyState()
    def select(self, m): print("insert money first")
    def dispense(self, m): pass

class HasMoneyState:
    def insert(self, m): print("already inserted")
    def select(self, m): m.state = DispensingState()
    def dispense(self, m): pass

class VendingMachine:
    def __init__(self): self.state = IdleState()
    def insert(self): self.state.insert(self)
```
**Heuristic:** ≤3 states or ≤3 transitions → if/elif. ≥4 states with many transitions → State pattern.

## 3.8 `dataclass` vs Named Tuple vs `attrs` vs Pydantic

| | Mutability | Validation | Speed | Use |
|---|---|---|---|---|
| **NamedTuple** | Immutable | None | Fast (tuple). | Lightweight records. |
| **`@dataclass`** | Mutable (or `frozen=True`) | None (use `__post_init__`). | Standard. | **Default for internal classes.** |
| **`attrs`** | Both | Validators built-in. | Faster than dataclass. | Heavy domain models pre-Pydantic. |
| **Pydantic** | Mutable | Strong (parses & coerces). | Slower (validation). | **API boundaries** — DTOs, request/response. |

**Rule of thumb:** `dataclass` inside, **Pydantic** at the edges (API/serialization).

## 3.9 `__slots__`: When the Memory Saving Matters

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
```
- ~40-50% memory reduction per instance.
- Forbids adding attributes at runtime.
- Cannot multiply-inherit from non-`__slots__` classes.

**Use when:** Millions of instances. Otherwise, the readability cost > benefit.

## 3.10 Repository Pattern: Worth It in Python?

```python
class UserRepository(Protocol):
    def get(self, id: int) -> User | None: ...
    def save(self, user: User) -> None: ...

class SqlUserRepository:
    def __init__(self, conn): self.conn = conn
    def get(self, id): ...
    def save(self, user): ...

class InMemoryUserRepository:
    def __init__(self): self._d = {}
    def get(self, id): return self._d.get(id)
    def save(self, user): self._d[user.id] = user
```
**Pros:** Test with in-memory; swap DB. **Cons:** Layers of indirection. **In Python**, monkeypatching often does the same job — you can directly patch `db.execute` in tests. **Use Repository when:** business logic is genuinely DB-agnostic (DDD-style domain layer).

## 3.11 Dependency Injection: Constructor vs Setter vs Parameter

```python
# Constructor (preferred — required deps)
class OrderService:
    def __init__(self, repo: OrderRepository, mailer: Mailer):
        self.repo, self.mailer = repo, mailer

# Setter (optional deps that may change post-construction — rare in Python)
class OrderService:
    def __init__(self): self.metrics = NoOpMetrics()
    def set_metrics(self, m): self.metrics = m

# Parameter (per-call)
def process_order(order, repo: OrderRepository): ...
```
Python rarely needs DI frameworks. Constructor injection + manual wiring in `main()` is enough for most apps. Use `dependency-injector` or `wired` only at scale.

## 3.12 Decorator Chaining

```python
@app.route("/items")        # outermost (last-applied)
@auth_required
@rate_limit(per_min=100)
@cached(ttl=60)             # innermost (first-applied)
def list_items(): ...
```
**Trade-off:** Order matters. `cached` inside `rate_limit` means cached responses *don't* count against rate limit; reverse the order if they should. Always document order in big comment when it matters.

## 3.13 `__eq__` and `__hash__` Together

If you override `__eq__`, you MUST address `__hash__` (Python defaults `__hash__` to None when `__eq__` is overridden, making the class unhashable). For dataclasses: `@dataclass(frozen=True, eq=True)` makes them hashable.

## 3.14 Async vs Threads vs Multiprocessing

| | When |
|---|---|
| **`asyncio`** | I/O-bound, many connections (10k+ concurrent). |
| **`threading`** | I/O-bound, fewer connections, blocking libraries (no async support). GIL means CPU work is *not* parallel. |
| **`multiprocessing`** | CPU-bound. Bypasses GIL. Cost: pickling overhead, no shared memory unless explicit. |
| **`concurrent.futures`** | Highest-level API; `ThreadPoolExecutor` and `ProcessPoolExecutor`. |

In Python 3.13+ free-threaded build, threads can run CPU-bound truly in parallel — watch this space.

---

# PART 4 — LLD Trade-offs (C++)

> Code targets C++17/20. References: ISO C++ Core Guidelines (`isocpp/CppCoreGuidelines`, SHA `ceebda5`), Sean Parent's talks ("Better Code: Runtime Polymorphism"), Stroustrup, and Herb Sutter (GotW).

## 4.1 Parameter Passing (CG F.16, F.17, F.18, F.19, F.20)

| Category | Signature | When |
|---|---|---|
| **Cheap to copy (≤16 bytes)** | `void f(int x)` | Always pass by value. |
| **In, may copy** | `void f(string s)` | Pass by value if you'll *store* it (move from parameter). |
| **In, no copy** | `void f(const string& s)` | Read-only access; cheaper than copy. |
| **In-out** | `void f(string& s)` | Mutates. |
| **Forward** | `template<class T> void f(T&& x)` | Forwarding reference; `std::forward<T>(x)` inside. |
| **Move-only sink** | `void f(string&& s)` | Caller must `std::move`. |

**The "store it?" rule (Herb Sutter):**
```cpp
// "Sink" — going to be stored:
void Customer::set_name(std::string n) { name_ = std::move(n); }  // pass by value

// "Observer" — only reads:
void log(const std::string& s) { std::cout << s; }                 // const ref
```

## 4.2 Move Semantics & RVO/NRVO

```cpp
// RVO: compiler elides the copy of the return value.
std::string make_greeting() { return "hello"; }   // no copy, no move

// NRVO: named return value optimization.
std::string build() {
    std::string s = "hello";
    return s;   // compiler elides; do NOT std::move(s)!
}

// F.48: ANTI-PATTERN — disables NRVO!
std::string build_bad() {
    std::string s = "hello";
    return std::move(s);   // BAD: forces a move; prevents elision
}
```
> "Don't `std::move` a local variable in `return`. NRVO will elide entirely; move only forces a less-efficient copy." — C++ Core Guidelines F.48

## 4.3 Rule of 0/3/5 (CG C.20, C.21)

**Rule of 0:** Don't define ANY of the special members. Let the compiler generate them; rely on RAII members (`unique_ptr`, `vector`, etc.) to handle resources.

```cpp
// Rule of 0 — preferred
struct Document {
    std::string title;
    std::vector<Page> pages;
    std::unique_ptr<Index> index;   // owns; non-copyable
    // Compiler generates correct copy/move. No work for me.
};
```

**Rule of 5:** If you must define one of the five (destructor, copy ctor/op, move ctor/op), define them all (or `=delete` / `=default` deliberately).

```cpp
class FileHandle {
    FILE* fp_;
public:
    explicit FileHandle(const char* path) : fp_(fopen(path, "r")) {}
    ~FileHandle() { if (fp_) fclose(fp_); }
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& o) noexcept : fp_(o.fp_) { o.fp_ = nullptr; }
    FileHandle& operator=(FileHandle&& o) noexcept {
        if (this != &o) { if (fp_) fclose(fp_); fp_ = o.fp_; o.fp_ = nullptr; }
        return *this;
    }
};
```
**Better still:** wrap the resource in `std::unique_ptr<FILE, decltype(&fclose)>` and apply Rule of 0.

## 4.4 Smart Pointers (CG R.20-R.30)

| Smart pointer | Ownership | Cost | Use |
|---|---|---|---|
| `std::unique_ptr<T>` | Single owner. | Zero overhead vs raw pointer. | **Default.** Most owners are unique. |
| `std::shared_ptr<T>` | Shared (refcount). | Atomic refcount; control block (~16-24 bytes). | When ownership is genuinely shared (e.g., DAG of objects). |
| `std::weak_ptr<T>` | Non-owning observer of `shared_ptr`. | One atomic check on `lock()`. | Break cycles; cache references. |
| Raw pointer `T*` | Non-owning. | Free. | Function parameters that never own. |
| Raw reference `T&` | Non-owning, non-null. | Free. | Function parameters that never own and can't be null. |

**Decision tree:**
```
Need ownership?
├─ Yes
│  ├─ Single owner? → unique_ptr
│  └─ Shared? → shared_ptr (and weak_ptr to break cycles)
└─ No (just observe)
   ├─ Can be null? → T*
   └─ Always valid? → T& (or std::reference_wrapper for storage)
```

**`std::make_shared` vs `std::shared_ptr<T>(new T())`:** Prefer `make_shared` — single allocation for control block + object (cache-friendlier, exception-safer).

## 4.5 `std::optional<T>` vs Sentinel Values vs Exceptions

```cpp
std::optional<User> find_user(int id);  // explicit "may be missing"

if (auto u = find_user(42)) {
    use(*u);
} else {
    // not found
}
```
| | When |
|---|---|
| `optional<T>` | "May not exist" is normal. Look-ups, parses. |
| Sentinel (`-1`, `nullptr`, `""`) | C-era; ambiguous. Avoid in new code. |
| Exception | **Truly exceptional**, not control flow. File-not-found-when-expected; OOM. |
| `expected<T, E>` (C++23) | "May fail with reason X" — replaces optional + error code. |

## 4.6 `std::variant` vs Inheritance

```cpp
// Closed set of types — variant
using Shape = std::variant<Circle, Square, Triangle>;
double area(const Shape& s) {
    return std::visit([](const auto& x) { return x.area(); }, s);
}

// Open set — virtual
struct Shape { virtual double area() const = 0; virtual ~Shape() = default; };
struct Circle : Shape { ... };
```
| | Variant | Inheritance |
|---|---|---|
| **Add new type** | Recompile all `visit`s. | Just inherit. |
| **Layout** | Stack; size = max(types) + tag. | Heap (usually); pointer indirection. |
| **Performance** | Compiler can devirtualize visits. | Virtual call cost (~few ns + cache miss). |
| **Best for** | Closed AST nodes, state machines. | Plugin systems, framework hooks. |

## 4.7 Sean Parent: Value Semantics & Type Erasure

> "Polymorphism is not a property of the object. It is a property of the *use*. Inheritance is the base class of evil." — Sean Parent

Value-semantic type erasure (lets you do polymorphism *without* a base class in user code):

```cpp
class Drawable {
    struct Concept {
        virtual ~Concept() = default;
        virtual std::unique_ptr<Concept> clone() const = 0;
        virtual void draw() const = 0;
    };
    template<class T> struct Model : Concept {
        T x;
        Model(T t) : x(std::move(t)) {}
        std::unique_ptr<Concept> clone() const override {
            return std::make_unique<Model>(*this);
        }
        void draw() const override { x.draw(); }
    };
    std::unique_ptr<Concept> p_;
public:
    template<class T> Drawable(T x)
        : p_(std::make_unique<Model<T>>(std::move(x))) {}
    Drawable(const Drawable& o) : p_(o.p_->clone()) {}
    Drawable(Drawable&&) noexcept = default;
    void draw() const { p_->draw(); }
};
// Now: Circle and Square don't share a base. They just need draw().
```

**Trade-off:** Heap allocation per instance, but **value semantics** (you can put `Drawable` directly in a `vector<Drawable>` and copy it). This is what `std::function` does internally.

## 4.8 Polymorphism: virtual vs CRTP vs `std::function` vs Concepts

| Mechanism | Dispatch | Cost | When |
|---|---|---|---|
| `virtual` | Runtime via vtable. | ~1-2 ns + cache miss. | Open-set polymorphism, plugins. |
| **CRTP** (Curiously Recurring Template Pattern) | Compile-time. | Zero overhead. | Mixin behavior; static polymorphism. |
| `std::function` | Runtime + small-buffer optimization or heap. | ~5-15 ns. | Callbacks, type-erased lambdas. |
| **C++20 Concepts** | Compile-time. | Zero. | Templates with readable error messages. |

```cpp
// CRTP — static polymorphism
template<class Derived>
struct Counted {
    static inline int count = 0;
    Counted() { ++count; }
};
struct Widget : Counted<Widget> {};
struct Gadget : Counted<Gadget> {};
// Widget::count and Gadget::count are independent — no virtual call.
```

## 4.9 Inheritance vs Composition (CG C.120, C.121)

> "Prefer composition over inheritance." — Effective C++

Inheritance is for **substitutability** (LSP). If you wouldn't use a `Derived*` where a `Base*` is expected, you don't want inheritance — you want composition.

```cpp
// Bad: inheriting for code reuse
class Stack : public std::vector<int> { ... };  // Stack IS-A vector? No.

// Good: composition
class Stack {
    std::vector<int> v_;
public:
    void push(int x) { v_.push_back(x); }
    int pop() { int x = v_.back(); v_.pop_back(); return x; }
};
```

## 4.10 EBO and `[[no_unique_address]]` (C++20)

```cpp
// Pre-C++20 EBO: empty bases occupy 0 bytes
struct Allocator {};   // empty
template<class A>
struct Container : private A {   // EBO: A contributes 0 bytes
    int* data_;
};

// C++20: [[no_unique_address]] for members
template<class A>
struct Container2 {
    [[no_unique_address]] A alloc;   // 0 bytes if A is empty
    int* data_;
};
```

## 4.11 Stack vs Heap; RAII

```cpp
// Stack — automatic, fast, scope-bound
void f() {
    std::array<int, 1024> a;       // 4 KB on stack — instant
    process(a);
}

// Heap — flexible size, slower allocation
void g(int n) {
    std::vector<int> v(n);         // n*4 bytes on heap
    process(v);
}                                  // RAII cleans up
```

**Rule of thumb:**
- < 1 KB AND known at compile-time → stack.
- > 1 KB OR variable size → heap (via vector/unique_ptr).
- Stack overflow on Windows: ~1 MB default. Linux: ~8 MB.

## 4.12 Container Choice (Stroustrup GotW #4)

> "If in doubt, use `std::vector`." — Bjarne Stroustrup

| Container | Random access | Insert/erase mid | Insert end | Memory | Use |
|---|---|---|---|---|---|
| `std::vector` | O(1) | O(n) | Amortized O(1) | Contiguous; cache-friendly | **Default.** |
| `std::deque` | O(1) | O(n) | O(1) front+back | Chunked | Front+back insert. |
| `std::list` | O(n) | O(1) (with iter) | O(1) | Node-per-element; cache-unfriendly | Almost never. |
| `std::array<T,N>` | O(1) | n/a | n/a | Stack | Compile-time-fixed size. |
| `std::unordered_map` | n/a | O(1) avg | O(1) avg | Hash table | Lookup-by-key. |
| `std::map` | n/a | O(log n) | O(log n) | Red-black tree | Sorted iteration. |
| `std::flat_map` (C++23) | n/a | O(n) | O(n) | Sorted vector | Read-heavy with few inserts. |

**Why `vector` beats `list`:** Cache. Even O(n) linear scans on `vector` beat O(1) `list` traversal because of cache prefetching. The only time `list` wins is when you have stable iterators across mutations.

## 4.13 `unordered_map` vs `map`: Cache Behavior

| | `map` (RB-tree) | `unordered_map` (hashtable) |
|---|---|---|
| Lookup | O(log n) | O(1) avg, O(n) worst |
| Order | Sorted | Unspecified |
| Memory | ~3 pointers/node | Buckets + linked lists/probing |
| Cache | Bad (pointer chasing) | OK on hot keys |

**For hot small maps (≤ 100 entries), a sorted `vector<pair<K,V>>` with `std::lower_bound` often beats both** — fully contiguous, no allocations.

## 4.14 SBO / SSO

`std::string` typically reserves 15-23 bytes inline (Small String Optimization). For `<` that size, no heap allocation. Same idea in `std::function` (typically 16-32 bytes inline). Implication: don't worry about strings up to ~22 chars; they're free.

## 4.15 `std::array<T,N>` vs `std::vector<T>`

```cpp
std::array<int, 3> point{1, 2, 3};   // size baked at compile time
std::vector<int> dynamic{1, 2, 3};    // heap; size at runtime
```
**Use array when:** Size is known at compile time and small. **Use vector when:** Size unknown or large. Both work in `constexpr` (vector since C++20).

## 4.16 Memory Pools / PMR (C++17)

```cpp
#include <memory_resource>

std::pmr::monotonic_buffer_resource pool(4096);   // bump allocator
std::pmr::vector<int> v{&pool};
v.reserve(100);   // allocates from pool
v.push_back(42);
// pool destroyed at end of scope — bulk free; no per-element delete
```
**Trade-off:** Massive allocation throughput; lifetime constraints (everything in pool freed at once). Used for parsers, request-scoped allocations, game frame allocators.

Also: `std::pmr::pool_options` for sized pools, `std::pmr::synchronized_pool_resource` for thread-safe.

## 4.17 False Sharing and `alignas(64)`

```cpp
struct BadStats {
    std::atomic<int> reads;
    std::atomic<int> writes;
    // Both on same 64-byte cache line.
    // Two cores hammering reads & writes on different cores ping-pong the line.
};

struct GoodStats {
    alignas(64) std::atomic<int> reads;
    alignas(64) std::atomic<int> writes;
    // Each on its own cache line — independent.
};
```
**Cost:** Memory (64 bytes per atomic instead of 4). **Benefit:** Often 10-100× throughput improvement on contended counters.

## 4.18 `constexpr` vs Runtime

```cpp
constexpr int factorial(int n) { return n <= 1 ? 1 : n * factorial(n-1); }
constexpr int x = factorial(5);   // 120 — computed at compile time

// With consteval (C++20): MUST be compile-time.
consteval int square(int x) { return x * x; }
constexpr int y = square(7);   // OK, compile time
// int z = square(runtime_var);  // ERROR — must be constant
```
**Trade-off:** Compile time goes up; runtime goes down. Pre-compute lookup tables, hashes, dispatch tables.

## 4.19 Concurrency: `std::thread` vs `std::async` vs Thread Pool vs `std::jthread`

```cpp
// std::thread — manual lifecycle
std::thread t([] { work(); });
t.join();   // forget this and you abort()

// std::jthread (C++20) — RAII; auto-joins; supports cooperative cancellation
std::jthread jt([](std::stop_token st) {
    while (!st.stop_requested()) work();
});
// no join needed; destructor handles it

// std::async — high-level; can run sync or async (impl-defined)
auto f = std::async(std::launch::async, []{ return compute(); });
int r = f.get();

// Thread pool — best for many short tasks (stdlib doesn't ship one until C++26 executors)
```
**Heuristic:** Use `jthread` for new code (C++20+). Use a thread-pool library (`folly`, `taskflow`) for parallel-task workloads. Avoid raw `std::thread` outside of trivial cases.

## 4.20 Locks vs Atomics — Memory Order

```cpp
std::atomic<int> counter{0};
counter.fetch_add(1, std::memory_order_relaxed);   // counter, no ordering
counter.fetch_add(1, std::memory_order_acquire);   // for synchronized loads

// Mutex — heavier but easier to reason about
std::mutex m;
std::lock_guard lock(m);   // RAII; unlocks on scope exit
```

| `memory_order` | Guarantee | Cost | Use |
|---|---|---|---|
| `relaxed` | Atomicity only. | Cheapest. | Counters where ordering doesn't matter. |
| `consume` | (largely deprecated; treat as acquire) | | |
| `acquire` | This load + later ops can't move before. | One barrier. | Reading a flag set by another thread. |
| `release` | This store + earlier ops can't move after. | One barrier. | Setting a flag readers will check. |
| `acq_rel` | Both. | Two barriers. | RMW operations. |
| `seq_cst` | Total order across all threads. | Most expensive. | **Default.** Most readable. Use unless profiled otherwise. |

**Rule:** Start with `seq_cst`. Profile. Relax only on hot paths and prove correctness.

## 4.21 `std::shared_mutex`: Reader-Writer

```cpp
std::shared_mutex m;
{ std::shared_lock r(m); /* many readers OK */ }
{ std::unique_lock w(m); /* exclusive writer */ }
```
**Trade-off:** Heavier than `mutex`; pays off only when reader work is **substantial** AND **frequent** — otherwise contended exclusive-mode RW locks lose to plain `mutex`. Rule of thumb: don't use unless reader hold time ≫ writer hold time AND readers ≫ writers.

## 4.22 PIMPL Idiom

```cpp
// widget.h — public header; no implementation details
class Widget {
public:
    Widget();
    ~Widget();
    Widget(Widget&&) noexcept;
    Widget& operator=(Widget&&) noexcept;
    void render();
private:
    struct Impl;
    std::unique_ptr<Impl> p_;
};

// widget.cpp
struct Widget::Impl {
    int width, height;
    std::vector<Pixel> pixels;
    void do_render();
};
Widget::Widget() : p_(std::make_unique<Impl>()) {}
Widget::~Widget() = default;   // MUST be in .cpp where Impl is complete
Widget::Widget(Widget&&) noexcept = default;
Widget& Widget::operator=(Widget&&) noexcept = default;
void Widget::render() { p_->do_render(); }
```
**Pros:** Stable ABI; faster compilation (no #includes leak); hide implementation.
**Cons:** Heap allocation per object; one indirection per call. Used heavily by Qt, libraries with stable ABI requirements.

---

# PART 5 — Decision Matrices

## 5.1 Datastore Choice

| Workload | Choice | Notes |
|---|---|---|
| Money / orders / inventory | **Postgres** | ACID, mature. Default. |
| Time-series telemetry | **TimescaleDB** or **InfluxDB** | Hypertable + downsampling. |
| Graph traversal | **Neo4j** or **Postgres + recursive CTE** | Try Postgres first; switch only if you do real graph algos. |
| Search | **Elasticsearch** / **OpenSearch** / **Postgres FTS** | Postgres FTS for ≤10M docs; ES for full-text at scale. |
| Massive denormalized writes | **Cassandra/ScyllaDB** | If you actually need 100k+ writes/s/server. |
| Caches | **Redis** | Boring; correct. |
| Document store | **Postgres `jsonb`** | Mongo only if document-first is genuinely your model. |
| Wide-column / mixed | **Cassandra** | Last resort; operational tax is real. |

## 5.2 CAP Decision Tree

```
Is partition tolerance optional? (single-DC, no network)
├─ Yes: choose CA — i.e., a single-node RDBMS.
└─ No (real distributed system): choose between
   ├─ AP — eventual consistency
   │  └─ Cassandra, Dynamo, Riak, Couchbase
   │     Use when: availability matters more than freshness
   │     (carts, sessions, reviews, timelines)
   └─ CP — strong consistency
      └─ Spanner, etcd, ZooKeeper, MongoDB (default)
         Use when: correctness matters more than uptime
         (ledgers, identity, locks, leader election)
```

## 5.3 Smart Pointer Choice (C++)

```
Is anyone going to own this?
├─ No (just observe) → T* or T&
└─ Yes
   ├─ One owner → std::unique_ptr<T>
   └─ Shared
      ├─ Acyclic → std::shared_ptr<T>
      └─ Cyclic risk → shared_ptr + weak_ptr to break cycle
```

## 5.4 Sync vs Async (Both Languages)

```
Is the work I/O-bound?
├─ Yes
│  ├─ Many concurrent ops (>1000)? → async (asyncio in Py; coroutines/io_uring in C++)
│  └─ Few concurrent ops? → threads (or sync if blocking is OK)
└─ No (CPU-bound)
   ├─ Python → multiprocessing (GIL) or 3.13+ free-threaded
   └─ C++ → std::jthread / thread pool / parallel STL / SIMD
```

## 5.5 Replication Strategy

| Need | Strategy |
|---|---|
| Strong consistency, single region | Single primary + sync replica for HA |
| Read scale-out within region | Single primary + N async read replicas |
| Cross-region reads | Per-region read replica with async stream from primary |
| Cross-region writes | Either active-passive failover OR multi-master with conflict design (CRDT/LWW) |
| Zero-RPO | Sync replication (Paxos/Raft) — 2 of 3 nodes in different AZs |

---

# PART 6 — Real-World Case Studies

## 6.1 Discord: MongoDB → Cassandra → ScyllaDB

**Timeline (per Discord engineering blog):**

- **Pre-2016:** Single Mongo replica set holding messages.
- **2015 outage:** Working set exceeded RAM; queries that scanned non-RAM data became unpredictably slow. The "tipping point" trade-off: Mongo's lack of explicit per-query memory budget meant a single bad query could degrade the cluster.
- **2016: Migrated to Cassandra** (177-node cluster). Trade-offs:
  - **Pro:** Horizontal scale; tunable consistency; predictable.
  - **Con:** GC pauses (JVM); maintenance overhead; tombstones from deletes blew up read latency.
  - p99 latency: 40-125 ms. Trillions of messages.
- **2022: Migrated to ScyllaDB** (Cassandra-compatible C++ rewrite, no GC). Result:
  - **177 → 72 nodes** (~60% reduction).
  - **p99: 40-125 ms → ~15 ms** (~7× improvement).
  - Eliminated GC-induced tail latency.

**Trade-off lesson:** *The right datastore today may be the wrong datastore in 5 years.* Discord's 2016 choice was correct for 2016. Their 2022 move was correct for 2022. The cost of staying on Cassandra (operational tax + p99) eventually exceeded the cost of migrating.

**The migration itself** used a dual-write pattern: write to both Cassandra and Scylla; read from one; reconcile diffs; cut over.

## 6.2 Stripe: Online Migrations as a Repeatable Process

Stripe's blog (Jacqueline Xu, 2017) on *Online Migrations at Scale* describes a four-step methodology applied to nearly every schema or store change:

1. **Dual-write to old + new stores.** Both serve writes; only old serves reads.
2. **Backfill** old data into new. Run in parallel with dual-write.
3. **Read from new store** (still dual-writing). Compare results to old store via the **Scientist library** (open-sourced by GitHub) — calls both stores, returns old result, *logs* discrepancies. Find bugs without breaking prod.
4. **Stop writing to old store; remove code.**

**Trade-offs of this pattern:**
- **Cost:** 2× write load during migration; lots of monitoring code.
- **Benefit:** Zero-downtime migrations. Reversible at any step (two-way door).

**Trade-off lesson:** Migration *as a process*, not a *project*, lets the team make many one-way doors look like two-way doors. Stripe runs dozens of migrations like this concurrently.

---

# Confidence Assessment

| Section | Confidence | Notes |
|---|---|---|
| Mental models (Part 1) | **High** | Direct quotes from primary sources (Bezos shareholder letter, Dan McKinley, Fowler, AWS Builders' Library). |
| HLD theorems (CAP/PACELC/FLP) | **High** | Brewer 2012 InfoQ, Abadi 2010, FLP 1985 are foundational. |
| HLD patterns (replication, caching, queues) | **High** | Reflects 2024-2025 industry consensus; specific numbers (Discord, Stripe) cited from blogs. |
| LLD Python | **High** | Snippets follow `python-patterns.guide` (Brandon Rhodes) and PEP 8. |
| LLD C++ | **High** | Aligned with C++ Core Guidelines (SHA `ceebda5`); Sean Parent / Sutter / Stroustrup quotes verified. |
| Case studies | **Medium-High** | Numbers from public Discord/Stripe blogs; *interpretation* of why is mine. |
| Decision matrices | **Medium** | Heuristics — *will* be wrong for some workloads. Use as starting points, not absolutes. |

**Where I'd be cautious:** Specific "X is faster than Y by N×" claims in real systems are workload-dependent. The trade-offs themselves are durable; the *quantities* are not.

---

# Citations & References

**Books:**
- *Designing Data-Intensive Applications* — Martin Kleppmann (O'Reilly).
- *Effective C++* / *Effective Modern C++* — Scott Meyers.
- *C++ Core Guidelines* — Stroustrup & Sutter — `github.com/isocpp/CppCoreGuidelines` SHA `ceebda537b941d435f8822a335c4e87fc46ecc79`.
- *Site Reliability Engineering* — Beyer et al. (Google) — sre.google/books.
- *Release It!* — Michael Nygard.

**Repos:**
- `donnemartin/system-design-primer` — SHA `9e2cdb8`.
- `isocpp/CppCoreGuidelines` — SHA `ceebda5`.

**Papers:**
- Brewer (2000), *Towards Robust Distributed Systems* — origin of CAP.
- Brewer (2012), *CAP twelve years later* — IEEE Computer / InfoQ revision.
- Gilbert & Lynch (2002), *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*.
- Fischer, Lynch, Paterson (1985), *Impossibility of Distributed Consensus with One Faulty Process*.
- Abadi (2010), *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC)*.
- Bailis et al. (VLDB 2015), *Coordination Avoidance in Database Systems*.
- Ongaro & Ousterhout (2014), *In Search of an Understandable Consensus Algorithm (Raft)*.

**Blogs / talks:**
- Jeff Bezos (2015), Amazon shareholder letter — "two-way doors."
- Dan McKinley (2015), *Choose Boring Technology*.
- Martin Fowler, *MonolithFirst*, *Microservices*.
- Jay Kreps (2014), *Questioning the Lambda Architecture*.
- Werner Vogels, *Eventually Consistent* — All Things Distributed.
- Charity Majors (Honeycomb), high-cardinality observability series.
- Brandon Rhodes, `python-patterns.guide`.
- Sean Parent, *Better Code: Runtime Polymorphism* (talks).
- Herb Sutter, *Guru of the Week (GotW)* series.
- AWS Builders' Library — *Timeouts, retries, and backoff with jitter*; *Avoiding insurmountable queue backlogs*; *Caching challenges and strategies*.
- Discord engineering blog — *How Discord Stores Trillions of Messages* (2022).
- Stripe engineering blog — *Online Migrations at Scale* (2017).
- Meta engineering — TAO posts on cache consistency.

**Companion files in this repository:**
- `system-design/00-introduction.md` — orientation.
- `system-design/01-beginner.md` through `system-design/04-expert.md` — leveled curriculum.
- `system-design/05-min-reads/` — 20 quick-read deep dives (CAP, caching, queues, etc.).
- `system-design/seminal-papers.md` — annotated paper list.
- `system-design/books-and-courses.md`, `system-design/github-repos.md`.

---

*End of guide. The real test is whether you can sketch the trade-off curve for a problem you've never seen before and articulate which axis matters most. Practice on your own systems first — they have the trade-offs you actually care about.*
