# 🟡 #10 — Database Sharding (5-min read)

## 🎯 TL;DR
**Sharding splits one big database into many smaller ones, each holding a subset of data. It's the only way to scale writes beyond a single server. It's also the most operationally painful thing you can do — avoid until forced.**

---

## 📖 Plain English

[Replication](./09-database-replication.md) gave us many copies of the same data — great for reads, useless for writes. All writes still go to one primary.

When that one primary can't handle the write volume? **Sharding.**

```
Before sharding:           After sharding:

   [DB]                     [DB-A: users 1-1M]
     ↑                      [DB-B: users 1M-2M]
     │                      [DB-C: users 2M-3M]
[All writes]                [DB-D: users 3M-4M]
```

Each shard is a **complete, independent database** holding part of the data. Each handles its own writes. No single bottleneck.

---

## 🔑 Sharding Strategies

### 1️⃣ Range-Based Sharding
- Split by ranges: shard A = users `aaron-james`, shard B = `jane-rachel`, etc.
- ✅ Range queries are efficient
- ❌ Hot spots (e.g., everyone whose name starts with "A")
- Used by: HBase, BigQuery (partitioning)

### 2️⃣ Hash-Based Sharding
- `shard = hash(user_id) % N`
- ✅ Even distribution
- ❌ Range queries require hitting all shards
- ❌ Re-sharding = nightmare (every key moves when N changes)

### 3️⃣ Consistent Hashing ★
- Hash both keys *and* shards onto a ring; key → next clockwise shard
- ✅ Adding/removing shards moves only ~1/N of the keys
- Used by: Cassandra, DynamoDB, memcached clients
- 📖 See [5-min read #11](./11-consistent-hashing.md)

### 4️⃣ Directory-Based Sharding (Lookup Service)
- A **router** service maps key → shard (e.g., `user_42 → shard_3`)
- ✅ Most flexible (rebalance anytime)
- ❌ Router is a new single point of failure; extra hop adds latency
- Used by: Vitess (YouTube/Square), Discord's message store

### 5️⃣ Geographic Sharding
- Shard by user's region: US users → us-shard, EU users → eu-shard
- ✅ Lower latency, GDPR/data residency
- ❌ Cross-region queries are expensive
- Used by: Netflix, Uber (geo-partitioning by city)

---

## 🏗️ Real-World Example: Discord

Discord stores **trillions** of messages.[^1] How?

- **Sharded by `(channel_id, bucket)`** — bucket = time-window
- Each shard is a Cassandra (now ScyllaDB) partition
- Hot channels distributed across many partitions naturally
- Look up messages by channel; recent first (uses range scan within shard)

---

## ⚠️ Sharding's Painful Realities

### 1. Cross-Shard Queries Are Brutal
- "Top 10 users by total spending" — must hit ALL shards, merge results in app
- Joins across shards = essentially impossible
- **Mitigation:** Denormalize. Pre-compute aggregates in a separate analytics DB (often Spark/Snowflake).

### 2. Re-sharding = Operational Hell
- Adding a new shard means migrating data while live traffic flows
- **Mitigation:** Start with virtual shards (e.g., 1024 logical shards from day 1, even if you only have 4 physical servers).

### 3. Transactions Across Shards
- ACID is hard when data spans shards
- **Mitigation:** Choose shard key so most transactions stay within one shard. Use Saga pattern for cross-shard.

### 4. Hot Shards
- One celebrity user gets 1M views/sec → that user's shard melts
- **Mitigation:** Add a salt to the key, or split hot keys into sub-shards

---

## 🔑 Choosing a Shard Key — The #1 Decision

The shard key determines everything:
- ✅ **Good shard keys**: `user_id` (uniform), `tenant_id` (multi-tenant SaaS), `(channel_id, time)` (Discord)
- ❌ **Bad shard keys**: `country` (skew toward US/EU), `date` (today's shard is hot)

**Rule:** Choose a key with high cardinality and uniform access. Most queries should be answerable with just the shard key.

---

## 📊 When NOT to Shard

| Situation | Why not |
|---|---|
| < 1 TB data, < 10K writes/sec | Single beefy Postgres server handles it |
| Heavy joins / analytics | Use a separate OLAP DB (Snowflake, BigQuery) |
| You haven't tried read replicas yet | Try replication first |
| You haven't tried partitioning yet | PostgreSQL native partitioning is simpler |
| You're "doing it for the resume" | Stop. |

**Most companies put off sharding until it's painful.** Stripe, Instagram, GitHub all ran on a single Postgres for years.

---

## 🚦 Modern Alternatives

Before sharding manually, consider:
- **PostgreSQL partitioning** — automatic in modern Postgres
- **Vitess** (YouTube) — sharding layer on MySQL
- **Citus** (Microsoft) — sharded Postgres
- **CockroachDB / Spanner / Aurora** — globally distributed; auto-shard
- **DynamoDB / Cassandra** — sharding built in from day 1

These hide much of the sharding pain behind a managed layer.

---

## 🔗 Dig Deeper

- 📘 *Designing Data-Intensive Applications* — Chapter 6: Partitioning
- 📘 [Discord engineering: how they store messages](https://discord.com/blog/how-discord-stores-trillions-of-messages)
- 📺 [ByteByteGo: Database Sharding Explained](https://www.youtube.com/@ByteByteGo)

---

## 📖 Citations

[^1]: [How Discord Stores Trillions of Messages](https://discord.com/blog/how-discord-stores-trillions-of-messages) — explains their `(channel_id, bucket)` sharding model.

---

← [Back to 5-min reads index](./README.md)
