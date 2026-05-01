# 🟡 #9 — Database Replication (5-min read)

## 🎯 TL;DR
**Replication = keeping copies of your database on multiple servers. It boosts read scalability, availability, and disaster tolerance. The big trade-off: synchronous replication is slow but consistent; asynchronous is fast but can lose data.**

---

## 📖 Plain English

You have one database. Two problems:

1. **Reads are bottlenecked** — millions of users querying one server.
2. **It's a single point of failure** — server dies, app dies.

**Solution: replicate.** Run two (or more) copies of the DB. One is the **primary** (handles writes). The others are **replicas** (handle reads, can take over if primary dies).

```
[App writes] → [Primary]
                  │  ← writes replicated
                  ▼
            [Replica 1]  ← reads
            [Replica 2]  ← reads
            [Replica 3]  ← reads
```

Same data, three places. Reads scale horizontally. If primary dies, promote a replica.

---

## 🔄 Three Replication Topologies

### 1️⃣ Single-Leader (Primary-Replica) — most common ★
```
   [Primary]   ←—— writes
   /   |   \
[R1] [R2] [R3]   ←—— reads
```
- One write source, many read destinations
- Used by: PostgreSQL, MySQL, MongoDB, Redis (default)
- ✅ Simple, well-understood
- ❌ Primary is bottleneck for writes

### 2️⃣ Multi-Leader (Multi-Primary)
```
[Leader A] ←——→ [Leader B]
   ↑               ↑
writes         writes
```
- Multiple primaries accept writes; sync between each other
- Used by: Multi-region setups, MySQL with circular replication, CRDTs (Riak)
- ✅ Local writes in each region; survives a region failure
- ❌ **Conflict resolution is hard.** Two writes to the same row in different leaders → which wins?

### 3️⃣ Leaderless (Peer-to-Peer)
```
[Node A] ←→ [Node B]
   ↕            ↕
[Node C] ←→ [Node D]
```
- Any node accepts any write; quorum protocols ensure correctness
- Used by: Cassandra, DynamoDB, Riak
- ✅ Maximum availability; no single point of failure
- ❌ Quorum reads/writes; eventual consistency by default

---

## ⚡ Synchronous vs Asynchronous Replication

This is the **fundamental trade-off**.[^1]

### Synchronous
- Primary waits for replica(s) to acknowledge before confirming write to the app
- ✅ **Strong consistency** — replicas always up-to-date
- ❌ **Slow writes** — limited by slowest replica
- ❌ **Reduced availability** — if replica is down, primary stalls
- Used in: financial systems, strict consistency needs

### Asynchronous (the default in most systems)
- Primary commits the write locally and replies immediately to the app
- Replicas catch up "soon" (milliseconds, usually)
- ✅ **Fast writes** — primary doesn't wait
- ❌ **Replica lag** — reads from replicas can be stale
- ❌ **Data loss possible** — if primary dies before replication, last few writes are gone
- Used in: most production systems

### Semi-Synchronous (compromise)
- Wait for at least 1 replica to ack (configurable)
- Best of both: durability + speed
- Used by: MySQL semi-sync, PostgreSQL sync replication

---

## 📈 The Replica Lag Problem

**You wrote a comment. You refresh. Comment is gone.** Why?

- Your write went to primary (fast)
- Your refresh hit a replica that hadn't caught up yet (lag of 50-500ms)

### Solutions
1. **Read your writes consistency:** route the user back to primary for N seconds after a write
2. **Monotonic reads:** stick the user to one replica during a session
3. **Bounded staleness:** only use replicas with lag < 100ms
4. **Synchronous replication** for the affected tables (extreme)

---

## 🚦 Failover

When the primary dies:

1. **Detect failure** (health checks, missed heartbeats)
2. **Choose a new primary** (the most up-to-date replica)
3. **Reconfigure clients** (DNS, service discovery)
4. **Old primary rejoins as replica** when revived

**Automated failover** is dangerous if you misjudge "is the primary really dead?" Two leaders simultaneously = **split-brain** = data corruption. Use proven tools (Patroni, MongoDB ReplicaSet, AWS RDS Multi-AZ).

---

## 🏗️ Real-World Examples

| System | Pattern |
|---|---|
| **PostgreSQL with read replicas** | Single-leader, async by default, can configure semi-sync |
| **MongoDB Replica Set** | Single-leader with automatic failover (3+ nodes for quorum) |
| **MySQL with Galera/Group Replication** | Multi-leader; synchronous |
| **Cassandra / DynamoDB** | Leaderless; tunable consistency (QUORUM, ONE, ALL) |
| **CockroachDB / Spanner** | Synchronous via Raft consensus across regions |

---

## 🔗 Dig Deeper

- 📘 *Designing Data-Intensive Applications* — Chapter 5: Replication ★
- 📘 [karanpratapsingh/system-design — Database Replication](https://github.com/karanpratapsingh/system-design)
- 📺 [Martin Kleppmann's Cambridge course — replication lecture](https://www.cl.cam.ac.uk/teaching/2021/ConcDisSys/)

---

## 📖 Citations

[^1]: Kleppmann, *Designing Data-Intensive Applications*, Ch. 5 — defines synchronous vs asynchronous replication trade-offs in detail.

---

← [Back to 5-min reads index](./README.md)
