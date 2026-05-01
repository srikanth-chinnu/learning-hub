# 📕 Phase 3: Advanced — Distributed Systems Theory & Practice

> **Goal:** Understand WHY distributed systems are hard. Read the seminal papers. Implement consensus algorithms. Reason about correctness, not just performance.

**Duration:** ~6-12 months (depending on prior CS background)
**Prerequisites:** Phase 1 + 2 complete; comfortable with DDIA Ch. 1-7.

This is where you stop being someone who *uses* distributed systems and start being someone who *understands* them.

---

## 🎯 What You'll Learn

By the end of Phase 3 you'll be able to:
- Read distributed systems research papers comfortably
- Implement Raft from scratch
- Reason about linearizability vs serializability vs read-committed
- Critique architectures using vocabulary like "FLP impossibility," "snapshot isolation," "monotonic timestamps"
- Understand why Spanner needs atomic clocks (TrueTime) and why CockroachDB doesn't

---

## 🌐 Distributed Systems Theory

### The Core Hard Problems
- **The 8 Fallacies of Distributed Computing** — internalize these[^1]
- **Failure modes** — crash, omission, timing, Byzantine
- **Network partitions** — they happen; your system must survive them
- **The two generals problem** — perfect coordination is impossible

📖 *5-minute read: [#15 CAP Theorem](./5-minute-reads/15-cap-theorem.md)*

### The Famous Theorems
- **CAP Theorem** — Brewer (2000), proved by Gilbert & Lynch (2002)
- **PACELC Theorem** — Abadi (2010), the more useful version
- **FLP Impossibility** — Fischer, Lynch, Paterson (1985): no deterministic consensus with 1 faulty process in async system
- **End-to-End Argument** — Saltzer, Reed, Clark (1984)

### Consistency Models — The Full Spectrum
From strongest to weakest:
1. **Linearizability** — appears as a single-machine real-time order
2. **Sequential Consistency** — same order to all observers, real-time not required
3. **Causal Consistency** — happened-before relation preserved
4. **Read-Your-Writes** — see your own writes
5. **Monotonic Reads** — never go backward
6. **Eventual Consistency** — converge eventually

📖 *5-minute read: [#16 Consistency Models](./5-minute-reads/16-consistency-models.md)*

📘 **Reference:** [Jepsen Consistency Models](https://jepsen.io/consistency) — the visual canonical reference

---

## 🤝 Consensus Algorithms (implement these!)

### Paxos
- **Original Paxos** (Lamport 1998) — basic Paxos for single-decree
- **Multi-Paxos** — practical optimization (used in Google Chubby, Spanner)
- **Fast Paxos** — eliminates a round trip in common case
- **Egalitarian Paxos** — no leader; better for write-heavy workloads

### Raft (start here ★)
- Designed for **understandability** — Ongaro & Ousterhout (2014)
- Leader election → log replication → safety
- Strong leader simplifies reasoning
- Used in: etcd, Consul, CockroachDB, MongoDB Replica Set, TiKV
- **Implement it:** [MIT 6.824 Lab 2](https://pdos.csail.mit.edu/6.824/) makes you write Raft from scratch

### ZAB (ZooKeeper Atomic Broadcast)
- Used in Apache ZooKeeper
- Total order broadcast variant
- Inspiration for Kafka's Controller (pre-KRaft)

### Byzantine Consensus
- Tolerates malicious nodes (not just crash)
- **PBFT** (Castro & Liskov 1999)
- Used in blockchains; rarely needed in standard distributed systems

📖 *5-minute read: [#17 Consensus](./5-minute-reads/17-consensus-raft-paxos.md)*

---

## 💾 Distributed Transactions

### Two-Phase Commit (2PC)
- Coordinator + participants
- Atomic commit across nodes
- **Blocking on coordinator failure** — major weakness
- Used in: traditional XA transactions, distributed SQL DBs

### Three-Phase Commit (3PC)
- Adds a "pre-commit" to reduce blocking
- Still doesn't handle network partitions
- Mostly theoretical interest

### The Saga Pattern (the practical alternative)
- Sequence of local transactions + compensations
- Choreography vs Orchestration
- Used by every modern microservice architecture

📖 *5-minute read: [#18 Event-Driven & Saga](./5-minute-reads/18-event-driven-and-saga.md)*

### Calvin / Deterministic Concurrency Control
- Pre-determine ordering, then execute
- Used in FaunaDB
- Eliminates need for 2PC in some cases

---

## ⏱️ Time, Order & Causality

In distributed systems, **time is broken**. Clocks drift; ordering is hard.

### Logical Clocks
- **Lamport timestamps** (1978) — total order from partial order
- **Vector clocks** — track causality across N nodes
- **Hybrid Logical Clocks (HLC)** — combine logical + physical
- **TrueTime** (Google Spanner) — atomic clocks + GPS for tight bounds

📘 **Read:** [Lamport — Time, Clocks, and the Ordering of Events in a Distributed System (1978)](https://amturing.acm.org/p558-lamport.pdf) ★ — the foundational paper

### Snowflake IDs
- Distributed unique ID generation
- Time + machine + sequence
- Twitter's design; used everywhere

---

## 📦 Storage Engines (deep dive)

### B-Tree (the classic)
- Self-balancing tree
- Used in: PostgreSQL, MySQL InnoDB, MongoDB
- Optimized for **random reads + in-place updates**

### LSM-Tree (Log-Structured Merge)
- Append-only writes; periodic merge/compaction
- Used in: Cassandra, RocksDB, LevelDB, HBase, Bigtable
- Optimized for **write-heavy workloads**
- **Compaction strategies:** size-tiered, leveled

### B+Tree vs LSM Trade-offs
- B-tree: faster reads, worse writes (write amplification due to in-place updates)
- LSM: faster writes, slower reads (must check multiple SSTables; bloom filters help)

📘 **Read:** *Database Internals* by Alex Petrov — entire book is on this

---

## 🌊 Distributed Databases

### Relational at Scale
- **Google Spanner** — globally distributed, externally consistent (uses TrueTime)
- **CockroachDB** — Spanner-inspired, no atomic clocks (uses HLC + retry)
- **YugabyteDB** — Postgres-compatible distributed SQL
- **TiDB / TiKV** — MySQL-compatible, Raft-based

### NoSQL
- **DynamoDB** — leaderless, consistent hashing, tunable consistency (Amazon Dynamo paper)
- **Cassandra** — open-source DynamoDB cousin
- **MongoDB** — document, replica set + sharding
- **HBase / Bigtable** — column-family, single-leader per region

### Newcomers
- **FoundationDB** — ACID + KV; foundation of Snowflake, iCloud
- **FaunaDB** — Calvin-based deterministic transactions
- **TigerBeetle** — financial-grade transactions

---

## 🌳 CRDTs (Conflict-Free Replicated Data Types)

Data types that **always converge** without coordination — magic for collaborative apps and offline-first.

### State-Based CRDTs (CvRDTs)
- G-Counter (grow-only counter)
- PN-Counter (positive-negative counter)
- G-Set (grow-only set)
- OR-Set (observed-remove set)
- LWW-Register (last-write-wins)

### Operation-Based CRDTs (CmRDTs)
- Logoot, RGA — for sequence/text editing
- Used in: Google Docs, Figma, Yjs, Automerge

📘 **Read:** [Shapiro et al. — Conflict-free Replicated Data Types (2011)](https://hal.inria.fr/inria-00609399v1/document)

---

## 📡 Architecture Patterns (advanced)

### CQRS — Command Query Responsibility Segregation
- Separate read model from write model
- Optimize each independently
- Pairs with event sourcing

### Event Sourcing
- State = log of events
- Replay to reconstruct state
- Foundation of audit-trail systems, Stripe, banking

### Service Mesh
- Sidecar proxy per service (Envoy)
- Centralized policy: retries, circuit breakers, mTLS, tracing
- Istio, Linkerd, Consul Connect

### Lambda Architecture vs Kappa Architecture
- **Lambda**: batch + speed layer (complex, dual-codepath)
- **Kappa**: streaming-only (simpler, modern)

### Cell-Based Architecture
- Partition users into "cells" (independent stacks)
- Blast radius limited to a cell
- Used by AWS, Slack at scale

---

## 📄 Seminal Papers — The Required Reading List

These are the **must-read** papers. The `papers-we-love/papers-we-love` repo (~92K stars) curates them.

### Foundational
- 📄 [Lamport — Time, Clocks, and the Ordering of Events (1978)](https://amturing.acm.org/p558-lamport.pdf) ★
- 📄 [Fischer, Lynch, Paterson — Impossibility of Distributed Consensus (1985)](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf)
- 📄 [Brewer — CAP keynote (2000)](https://www.cs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf)
- 📄 [Saltzer, Reed, Clark — End-to-End Arguments (1984)](https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf)

### Consensus
- 📄 [Lamport — Paxos Made Simple (2001)](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
- 📄 [Ongaro & Ousterhout — In Search of an Understandable Consensus Algorithm (Raft, 2014)](https://raft.github.io/raft.pdf) ★

### Storage / Databases
- 📄 [Google File System (GFS, 2003)](https://research.google/pubs/the-google-file-system/)
- 📄 [MapReduce (2004)](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
- 📄 [Bigtable (2006)](https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data-2/)
- 📄 [Amazon Dynamo (2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- 📄 [Spanner (2012)](https://research.google/pubs/spanner-googles-globally-distributed-database/)

### Coordination
- 📄 [Chubby Lock Service (2006)](https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/)
- 📄 [ZooKeeper (USENIX 2010)](https://www.usenix.org/conference/usenix-atc-10/zookeeper-wait-free-coordination-internet-scale-systems)

### Streaming
- 📄 [Kafka — A Distributed Messaging System for Log Processing (2011)](https://notes.stephenholiday.com/Kafka.pdf)
- 📄 [The Log: Jay Kreps' essay](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying)

### Observability
- 📄 [Dapper — Distributed Tracing (Google, 2010)](https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/)

📘 **Repository to bookmark:** [papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love) — full curation with PDFs

---

## 🎓 Courses to Take

### MIT 6.824 — Distributed Systems ★★★
- Robert Morris, Frans Kaashoek
- 23 video lectures (free on YouTube)
- 5 hands-on labs in Go: MapReduce, Raft, KV server, Sharded KV
- **The gold standard** for distributed systems learning
- 🔗 [Course page](https://pdos.csail.mit.edu/6.824/)
- 🔗 [Lecture videos](https://www.youtube.com/playlist?list=PLrw6a1wE39_tb2fErI4-WkMbsvGQk9_UB)

### Martin Kleppmann's Cambridge Course
- Free YouTube playlist
- Reinforces DDIA with academic rigor
- 🔗 [YouTube playlist](https://www.youtube.com/playlist?list=PLeKd45zvjcDFUEv_ohr_HdUFe97RItdiB)

### CMU 15-445 / 15-721 — Database Systems
- Andy Pavlo (the database genius)
- Free lectures, labs in C++
- 15-445 = intro; 15-721 = advanced
- 🔗 [CMU DB courses](https://15445.courses.cs.cmu.edu/)

---

## 💻 Production Code to Read

Reading good code accelerates learning more than any book.

| Project | Language | What to Study |
|---|---|---|
| **etcd** | Go | Raft implementation, watch API, lease management |
| **CockroachDB** | Go | Distributed SQL, Raft per range, time-series |
| **TiKV** | Rust | Raft, transactions, Multi-Raft |
| **RocksDB** | C++ | LSM-tree, compaction, write batches |
| **Apache Kafka** | Java/Scala | Log-based architecture, partition leadership |
| **Redis** | C | Data structures, Sentinel, Cluster |
| **CRDB / Vitess** | Go | Sharding patterns |

Pick one. Read its design docs (`docs/`). Then read the most central component (e.g., Raft package in etcd).

---

## 🎯 Hands-On Goals (Pick at Least One)

### Goal A: Implement Raft (the rite of passage)
- Use MIT 6.824 Lab 2 framework
- Learn Raft by implementing leader election + log replication
- Validates true distributed-systems understanding

### Goal B: Build a Mini Distributed KV Store
- 3 nodes; replication; failover
- Use existing Raft library (or your own from Goal A)
- Stretch goal: sharding across multiple Raft groups

### Goal C: Contribute to a Distributed System
- Pick a project you've used (etcd, CockroachDB, RocksDB)
- Find "good first issue" labels
- Submit a PR — even a small one

---

## ✅ How to Know You're Ready for Phase 4

Self-check:

1. Can you implement Raft leader election from memory (in pseudocode)?
2. Can you explain *why* Spanner uses TrueTime (and what alternative CockroachDB uses)?
3. What's the difference between snapshot isolation and serializable isolation?
4. Why does Kafka have at-least-once delivery by default? What would exactly-once require?
5. Can you read a Jepsen analysis (e.g., of MongoDB) and understand 80% of it?
6. Can you discuss CRDTs at a level where you'd reach for them appropriately?
7. Could you teach the difference between L7 LB, service mesh, and API gateway?

If yes → you're ready for [Phase 4: Expert](./04-expert.md), which is more about depth and breadth than new concepts.

---

## 📖 Citations

[^1]: [Fallacies of Distributed Computing (Wikipedia)](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing) — Peter Deutsch's list, expanded by James Gosling.

---

⚡ **Tip:** Read the [5-minute reads](./5-minute-reads/README.md) #15-#20 to keep core concepts fresh as you work through papers.

← [Previous: Intermediate](./02-intermediate.md) · [Home](./README.md) · → [Next: Expert](./04-expert.md)
