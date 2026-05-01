# 🔴 #17 — Consensus: Raft & Paxos (5-min read)

## 🎯 TL;DR
**Consensus algorithms let a group of computers agree on a value despite failures and network drops. Raft is the modern, understandable version. Paxos is the older, more famous, harder one. Without consensus, distributed systems can't safely pick a leader, lock anything, or agree on order.**

---

## 📖 Plain English

You have 5 servers. They need to agree: "what's the next entry in our log?"

- They can't all write the same thing because they don't trust each other to be alive
- Some might be down
- The network is unreliable; messages can be delayed or dropped

**Consensus** is the algorithm that gets them to safely agree, even with failures.

This is the **secret sauce** behind:
- Distributed locks (etcd, ZooKeeper)
- Distributed databases that need correctness (Spanner, CockroachDB)
- Kubernetes' control plane
- Service discovery (Consul)

Without consensus, you can't safely have a "leader" or a single source of truth in a distributed system.

---

## 🎩 Paxos — The Original

Invented by Leslie Lamport (1998).[^1]

**Phases:** Prepare → Promise → Accept → Accepted

The famous quote about Paxos: *"It's the only consensus protocol... and nobody understands it."* Even Google's engineers struggled with it. So in 2014, Stanford's Diego Ongaro and John Ousterhout wrote a new one designed for **understandability**.

---

## 🛡️ Raft — The Modern Choice

[Raft](https://raft.github.io/) (2014) does the same job as Paxos but is *much* easier to learn.[^2]

### The Big Idea

A cluster has 3 or 5 (odd number) servers. **One is the leader; the rest are followers.**

```
[Follower] ←—— heartbeats ——— [LEADER] ——— heartbeats ——→ [Follower]
                                  │
                                  ▼
                              writes go
                              through here
```

- **Leader handles all writes.** Replicates them to followers.
- **A write is "committed"** once a majority (e.g., 3 of 5) confirms.
- **If leader dies**, followers detect missed heartbeats, vote for a new leader.
- **Split-brain prevention:** A server only votes for one leader per term; majority required.

### The Three Sub-Problems Raft Solves
1. **Leader election** — pick one leader at a time
2. **Log replication** — leader pushes log entries to followers
3. **Safety** — never apply two different values for the same log slot

---

## 🗳️ How Leader Election Works

```
1. All servers start as followers.
2. Each follower has a random "election timeout" (150-300ms).
3. If timeout expires without hearing from a leader, follower → candidate.
4. Candidate increments its term, votes for itself, asks all others for votes.
5. Server votes if: hasn't voted yet this term AND candidate's log is up-to-date.
6. If candidate gets majority votes → becomes leader. Sends heartbeats.
7. If split vote → wait random time, retry.
```

The key insight: **majority quorums + odd cluster size + randomized timeouts** = no two leaders simultaneously, and elections converge fast.

---

## 📦 How Log Replication Works

```
1. Client sends "x = 5" to leader.
2. Leader appends to its local log.
3. Leader sends to all followers: "append 'x = 5' at index 47, term 3".
4. Followers append; reply "ok".
5. Once majority replies, leader marks index 47 as "committed".
6. Leader applies x = 5 to its state machine; tells client "done".
7. Followers also apply once they hear the commit index.
```

The committed log is identical across all servers.

---

## 🤝 Where Raft is Used

| System | Use |
|---|---|
| **etcd** (Kubernetes' brain) | Stores cluster state via Raft |
| **Consul** | Service discovery, configuration |
| **CockroachDB** | Each range of data uses Raft |
| **TiKV** (TiDB's storage) | Raft per partition |
| **MongoDB Replica Set** | Heavily inspired by Raft |
| **Kafka KRaft** | Kafka's metadata layer (replacing ZooKeeper) |

If you've used Kubernetes, you've used Raft (via etcd).

---

## 📚 Where Paxos is Used

| System | Variant |
|---|---|
| **Google Spanner** | Multi-Paxos |
| **Google Chubby** | The OG Paxos service (basis for ZooKeeper) |
| **Apache ZooKeeper** | ZAB (Zookeeper Atomic Broadcast — a Paxos variant) |
| **Apache Cassandra** | Paxos for lightweight transactions |

Modern teams writing new systems usually pick Raft. Old systems and high-end databases (Spanner) often use Paxos variants for historical and performance reasons.

---

## ⚖️ Raft vs Paxos

| | **Raft** | **Paxos** |
|---|---|---|
| Year | 2014 | 1998 |
| Designed for | Understandability | Theoretical minimality |
| Leader role | Strong, single leader | Multi-leader (Multi-Paxos) |
| Learning curve | Days | Weeks |
| Production implementations | Many (etcd, CockroachDB) | Many (Spanner, Chubby) |
| Performance | Comparable | Comparable |

**For learning and most new systems: Raft.**

---

## ⚠️ Why You Need Odd Numbers

Cluster sizes: 3, 5, 7. Why not 4?

- 4-node cluster: majority = 3
- 5-node cluster: majority = 3
- Both tolerate 2 failures... wait, no:
  - 4-node: tolerates 1 failure (need 3 of 4 alive)
  - 5-node: tolerates 2 failures (need 3 of 5 alive)
- **5 nodes ⟹ better fault tolerance than 4** with same majority size

Odd numbers maximize fault tolerance per node.

---

## 🚦 When You Need Consensus

✅ Picking a primary database
✅ Distributed locks ("only one person can edit this resource")
✅ Strict ordering of events (financial transactions)
✅ Service discovery / configuration that must be correct
✅ Any system where "two truths" is catastrophic

❌ Most application data — eventual consistency is fine
❌ Logs / metrics — at-least-once delivery suffices
❌ Caches — staleness is fine

**Don't run consensus everywhere.** It's expensive (multiple round trips per write).

---

## 🔗 Dig Deeper

- 📘 [The Raft paper (super readable!)](https://raft.github.io/raft.pdf)
- 🎮 [Raft visualization (raft.github.io)](https://raft.github.io/) — interactive simulation
- 📘 [MIT 6.824 lectures 5-7 — Raft deep dive](https://pdos.csail.mit.edu/6.824/) ★
- 📘 [Lamport — Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
- 📘 [Lamport — The Part-Time Parliament (original 1998 paper)](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)

---

## 📖 Citations

[^1]: Leslie Lamport, "The Part-Time Parliament," 1998. The original Paxos paper.
[^2]: Diego Ongaro and John Ousterhout, "In Search of an Understandable Consensus Algorithm," USENIX ATC 2014.

---

← [Back to 5-min reads index](./README.md)
