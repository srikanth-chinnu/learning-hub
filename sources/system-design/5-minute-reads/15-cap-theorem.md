# 🔴 #15 — The CAP Theorem (5-min read)

## 🎯 TL;DR
**In a distributed system that must keep working when the network fails, you can have either Consistency or Availability — not both. CAP is real but its meaning is widely misunderstood. PACELC is the more useful version.**

---

## 📖 Plain English

CAP says: a distributed system can guarantee at most **two** of:

- **C — Consistency** (every read sees the latest write)
- **A — Availability** (every request gets a response, even if not the latest data)
- **P — Partition tolerance** (system keeps working when network drops messages between nodes)

**The catch:** in any real network, partitions WILL happen.[^1] So **P is non-negotiable.** The real choice is between **CP** and **AP**.

```
       Partition happens
              │
   ┌──────────┴──────────┐
   ▼                     ▼
[CP system]          [AP system]
"Refuse requests    "Answer requests
 to keep data        even if data is
 consistent"         possibly stale"
```

---

## 🎯 CP vs AP — A Concrete Example

A bank with 3 datacenters. The link to one is severed.

### CP Choice (favor consistency)
- "I refuse to process withdrawals on the disconnected node — they might double-spend"
- ✅ No inconsistent state
- ❌ Disconnected nodes return errors (unavailable)

### AP Choice (favor availability)
- "I'll process withdrawals everywhere; we'll reconcile later"
- ✅ Always answers
- ❌ Two ATMs may both grant the last $100 in the account → reconciliation pain

**Banks usually pick CP for money** (correctness), AP for things like account balance display (eventual consistency is fine).

---

## 📊 CP vs AP — Real Systems

| System | Choice | Why |
|---|---|---|
| **PostgreSQL with single primary** | CP | Strong consistency over partition tolerance |
| **MongoDB (default)** | CP | Replica set leader stops accepting writes during partition |
| **HBase, ZooKeeper, etcd, Consul** | CP | Coordination needs strict consistency |
| **Cassandra, DynamoDB** | AP | Tunable but defaults toward availability |
| **Riak, CouchDB** | AP | Designed for "always answers" |
| **Spanner, CockroachDB** | CP | Strong consistency via Paxos/Raft + global clock |
| **Redis (cluster)** | CP/AP-ish | Tunable; nuanced |

---

## ⚠️ The Common CAP Misunderstandings

### 1. "Pick 2 out of 3" is misleading
You don't *choose* P. P is reality. You're really choosing between C and A *during a partition*. When there's no partition, you can have both.

### 2. CAP is not about all consistency
"Consistency" in CAP means **linearizability** — the strongest guarantee. Most systems use weaker forms (read-your-writes, monotonic reads, etc.). [See consistency models →](./16-consistency-models.md)

### 3. CAP doesn't apply to single-node systems
Your local SQLite isn't an "AP" or "CP" system; it's just a database.

### 4. CAP doesn't tell you the *latency* cost
Even when there's no partition, strong consistency requires coordination = slower. That's where PACELC comes in.

---

## 🌐 PACELC — The Better Version

Daniel Abadi's PACELC theorem extends CAP:[^2]

> **If there's a Partition (P), choose between Availability (A) and Consistency (C).
> Else (E), choose between Latency (L) and Consistency (C).**

```
                  Partition?
                ┌─────┴─────┐
              YES           NO
                │             │
            A vs C        L vs C
```

This captures something CAP misses: **even on a healthy network, strong consistency costs latency** (you must wait for replicas to confirm).

| System | PACELC | Meaning |
|---|---|---|
| Dynamo, Cassandra | PA / EL | Always available; in normal ops, low latency over consistency |
| MongoDB (default) | PA / EC | Available during partition; consistent in normal ops |
| Spanner | PC / EC | Strong consistency always; eats latency cost |
| MySQL primary-replica | PA / EL | Replicas serve stale reads quickly |
| HBase | PC / EC | Consistent always |

**PACELC is what you want to discuss in distributed systems interviews.**

---

## 🏗️ How Real Systems Cheat

Modern databases give you **tunable consistency** so you can pick per-query:

```sql
-- Cassandra
CONSISTENCY ONE       → AP (fast, possibly stale)
CONSISTENCY QUORUM    → middle ground
CONSISTENCY ALL       → CP (slow, consistent)
```

DynamoDB has **strongly consistent reads** flag — request CP semantics for individual operations.

This means in practice you choose **per operation**, not per system.

---

## 🚦 Practical Rule of Thumb

| Use case | Pick |
|---|---|
| Money, inventory, bookings | **CP** — correctness > availability |
| Social feed, recommendations, analytics | **AP** — staleness is fine |
| Configuration, leader election, locks | **CP** — must be consistent |
| Caching, search results | **AP** — slightly stale is fine |
| Shopping cart | Often AP with merging (CRDTs) |

---

## 🔗 Dig Deeper

- 📘 *Designing Data-Intensive Applications* — Chapter 9: Consistency and Consensus ★
- 📘 [Brewer's CAP keynote (2000) PODC](https://www.cs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf)
- 📘 [Daniel Abadi: Consistency Tradeoffs in Modern Distributed Systems (PACELC)](http://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- 📘 [Martin Kleppmann: A Critique of the CAP Theorem](https://arxiv.org/abs/1509.05393)

---

## 📖 Citations

[^1]: [Things You Believe About Distributed Computing — list of fallacies](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing) — "the network is reliable" is fallacy #1.
[^2]: [Daniel Abadi — Consistency Tradeoffs in Modern Distributed Systems (PACELC)](http://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf), 2010.

---

← [Back to 5-min reads index](./README.md)
