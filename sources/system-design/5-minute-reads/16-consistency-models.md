# 🔴 #16 — Consistency Models (5-min read)

## 🎯 TL;DR
**"Consistency" isn't binary — it's a spectrum from "everyone sees the same thing immediately" to "eventually maybe." Pick the weakest model that meets your requirements; weaker = faster, more available.**

---

## 📖 Plain English

When two people read the same data on different servers, what should they see?

- **Same answer, always, immediately?** That's *strong* consistency. Slow, expensive.
- **Same answer eventually?** That's *eventual* consistency. Fast, cheap, but you might briefly see different things.

In between are dozens of useful guarantees with funny names. The trick is to pick the **weakest** one that still meets your business needs.

---

## 📊 The Consistency Spectrum (strongest → weakest)

### 1. Linearizability ★ (the gold standard)
- All operations appear to happen in a single, real-time order
- A read after a write sees the write
- Looks like one perfect single-machine
- **Cost:** Slow, requires coordination (Paxos/Raft)
- **Examples:** etcd, ZooKeeper, Spanner, HBase

### 2. Sequential Consistency
- All operations appear in *some* order, same to all observers
- Real-time isn't required (can reorder slightly)
- **Cost:** Less than linearizability
- **Examples:** Some NoSQL configurations

### 3. Causal Consistency
- "Cause comes before effect" — you'll see operations in causal order
- Two unrelated ops can appear in different orders to different observers
- **Cost:** Affordable; great for messaging
- **Examples:** Comment threads, chat apps (you see your reply after the original)

### 4. Read Your Writes
- After you write, **you** read your own writes (others may not yet)
- "Just-posted comment shows up for me, but maybe not for others for 5s"
- **Cost:** Cheap; common UX expectation
- **Examples:** Social media, content management

### 5. Monotonic Reads
- Once you've seen value V, future reads return V or newer (never go backward)
- "Inbox count won't appear to decrease and then re-increase"
- **Cost:** Cheap (sticky session per user)
- **Examples:** Counters, notifications

### 6. Eventual Consistency (the bottom)
- "Given enough time and no new writes, all replicas converge"
- No guarantee of *when* — could be ms, could be minutes
- **Cost:** Cheapest; maximum availability/throughput
- **Examples:** DNS, Amazon S3, social media likes counter

---

## 🏗️ Real-World Examples

| Need | Model | Why |
|---|---|---|
| Bank transfer | **Linearizable** | Money cannot be wrong, ever |
| Distributed lock | **Linearizable** | Only one holder ever |
| Username availability | **Linearizable** | Two people can't claim same name |
| Comment thread (replies in order) | **Causal** | Cause/effect must be visible |
| User's "just posted" content | **Read Your Writes** | Don't lie to the user |
| Like count on a post | **Eventual** | Off-by-one is fine for UX |
| DNS records | **Eventual** | TTL-based; convergence is the point |
| Inventory counter | **Linearizable or near** | Don't oversell |
| Shopping cart | **Causal + CRDT merging** | Concurrent edits should reconcile |

---

## ⚙️ How Systems Achieve These

| Mechanism | Provides | Used in |
|---|---|---|
| **Single-master replication** | Linearizable on the master | PostgreSQL, MySQL primary |
| **Quorum (R + W > N)** | Tunable, often linearizable | Cassandra, DynamoDB |
| **Consensus protocols** (Raft, Paxos) | Linearizable | etcd, Spanner, CockroachDB |
| **Vector clocks / version vectors** | Causal | Riak, DynamoDB internals |
| **CRDTs (Conflict-Free Replicated Data Types)** | Eventual + auto-merge | Redis, Riak, Yjs (collab editors) |
| **Read repair / anti-entropy** | Eventual convergence | Cassandra, DynamoDB |

---

## 🚦 The Pragmatic Decision Tree

```
"If two ops conflict, can the system pick the wrong one?"
└─ NO → Linearizable (use Spanner/Postgres/etcd)
└─ YES, with limits → 
    "Must users see their own writes?"
    └─ YES → Read Your Writes (most apps need this)
    └─ "Must order be preserved within a chain?"
        └─ YES → Causal
        └─ NO  → Eventual (cheapest, fastest)
```

---

## 🎯 Real Cassandra Tunable Consistency

This is **the** classic example of consistency-as-knobs:

```
Total replicas N = 3

Read consistency:        Write consistency:
ONE     → 1 replica      ONE      → 1 replica  
QUORUM  → 2 replicas     QUORUM   → 2 replicas  
ALL     → 3 replicas     ALL      → 3 replicas
```

Rule: **`R + W > N` ⇒ strong consistency** (overlapping reads/writes).

- Want low latency? `R=1, W=1` → `1+1=2 < 3` → eventual consistency
- Want correctness? `R=2, W=2` → `2+2=4 > 3` → strong consistency (any two replicas overlap)

You choose **per query**.

---

## ⚠️ Common Misconceptions

1. **"NoSQL = eventual consistency"** — Wrong. Most NoSQL DBs offer strong consistency as an option (DynamoDB, Cassandra, MongoDB).
2. **"Strong consistency = no bugs"** — You still need to handle concurrency *correctly*. Strong consistency just removes one class of issues.
3. **"Eventual = a few seconds"** — Could be ms or hours. Without a bound, "eventual" is dangerous.
4. **"Linearizable is the only safe choice"** — Many apps work fine on causal or read-your-writes. Don't over-pay.

---

## 🔗 Dig Deeper

- 📘 *Designing Data-Intensive Applications* — Chapter 9: Consistency and Consensus ★★★
- 📘 [Jepsen Consistency Models](https://jepsen.io/consistency) ★ — clearest visualization on the web
- 📘 [Peter Bailis — Highly Available Transactions](http://www.bailis.org/papers/hat-vldb2014.pdf)
- 📘 Vogels, "Eventually Consistent" — `papers-we-love` repo

---

← [Back to 5-min reads index](./README.md)
