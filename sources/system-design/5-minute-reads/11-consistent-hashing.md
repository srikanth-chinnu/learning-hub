# 🟡 #11 — Consistent Hashing (5-min read)

## 🎯 TL;DR
**Consistent hashing is a clever trick that lets you add or remove servers from a hash-based system while only re-shuffling about 1/N of the data instead of all of it. It's the foundation of every modern distributed cache and database.**

---

## 📖 Plain English

### The Naïve Approach (and why it's broken)

You have 4 cache servers. You assign keys: `server = hash(key) % 4`.

Works great. Until you add a 5th server. Now `hash(key) % 5` gives **completely different** assignments. **Almost every key moves to a different server.** Cache hit rate → 0%. Database melts.

### Consistent Hashing — The Fix

Instead of a modulo, imagine a **circular ring** numbered 0 to 2³². Hash each server onto the ring. Hash each key onto the ring. A key belongs to the **first server clockwise** from its position.

```
       [Server A] (0)
            ●
   k1 ●          ● k2
            
[Server D] ●    ● [Server B]
            
   k4 ●          ● k3
            ●
       [Server C]
```

Now when you add **Server E** somewhere on the ring:
- Only the keys *between Server E and the previous server* move
- All other keys stay on their original server
- ~1/N of keys move (instead of all of them)

---

## 🔑 The Core Properties

| Property | Plain Hashing | Consistent Hashing |
|---|---|---|
| Add 1 server (out of N → N+1) | ~all keys move | ~1/N of keys move |
| Remove 1 server | ~all keys move | ~1/N of keys move |
| Implementation | Trivial | Moderate (sorted ring + binary search) |
| Real-world use | Toy projects | DynamoDB, Cassandra, memcached, Akamai CDN |

---

## 🔁 Virtual Nodes — The Critical Refinement

The basic ring has a problem: if you only have 4 servers, they might cluster on the ring → uneven load distribution.

**Solution: virtual nodes.** Each physical server gets ~100-200 *virtual* positions on the ring.

```
Server A → A1, A2, A3, ..., A150  (150 positions on ring)
Server B → B1, B2, B3, ..., B150
...
```

Now keys are spread evenly. Adding a server is even cleaner: its 150 virtual nodes spread the moved keys across many existing servers (no single server overloaded during rebalance).

**Every real implementation uses virtual nodes.** Cassandra calls them "vnodes."

---

## 🏗️ Where Consistent Hashing Is Used

| System | What's Hashed |
|---|---|
| **DynamoDB** | Items partitioned by hash of partition key |
| **Cassandra** | Rows partitioned across nodes via vnodes |
| **Discord's message store** | Channel messages sharded with consistent hashing |
| **Memcached clients** | Distribute keys across cache servers |
| **Akamai CDN** | Routes requests to edge servers |
| **CDN/load balancers** | Sticky session routing without persistent state |
| **Kubernetes** | Service load balancing |

It's basically the backbone of distributed systems.

---

## 📐 A Tiny Mental Model

Imagine the hash ring as a clock face (0 to 11 instead of 0 to 2³²):

```
              12 ← Server A
       11           1
    10                 2 ← Server B
   9                    3
    8                  4
       7            5
              6 ← Server C
```

- key `apple` hashes to 7 → owned by Server C (next one clockwise)
- key `banana` hashes to 11 → owned by Server A
- Add Server D at position 10 → keys between 8 and 10 move from C to D; everything else unchanged

That's it. The whole concept.

---

## 🎯 Common Use Cases

### Distributed Cache
You have 8 Redis servers. Use consistent hashing to assign keys. When you add a 9th:
- Cache hit rate stays high (only 1/9 of keys move)
- No "stampede" to the database

### Sharded Database
You have 32 database shards. Use consistent hashing on `user_id`. Adding shard #33:
- Only 1/33 of users migrate
- Most users are unaffected

### Load Balancing
You have 50 backend servers. Each user's session sticks to one server based on `hash(user_id)`. When a server dies:
- Users on that server reroute to the *next* one (clockwise)
- All other users' sessions stay put

---

## ⚠️ Pitfalls

1. **Forgetting virtual nodes** — basic ring has uneven distribution; always use vnodes
2. **Hot keys** — one celebrity's data on one shard. Mitigate with key salting or replication.
3. **Choosing a bad hash function** — must be uniform (use MurmurHash3, xxHash; avoid `hashCode()`)
4. **Believing it solves all sharding problems** — it doesn't help with cross-shard queries or transactions

---

## 🔗 Dig Deeper

- 📺 [ByteByteGo: Consistent Hashing Explained](https://www.youtube.com/@ByteByteGo)
- 📘 [Karger et al., 1997 — Original consistent hashing paper](https://www.akamai.com/site/en/documents/research-paper/consistent-hashing-and-random-trees-distributed-caching-protocols-for-relieving-hot-spots-on-the-world-wide-web-technical-publication.pdf)
- 📘 [Amazon Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) — uses consistent hashing in production

---

← [Back to 5-min reads index](./README.md)
