# 🟢 #5 — SQL vs NoSQL (5-min read)

## 🎯 TL;DR
**SQL is your default. Choose NoSQL when you have a specific reason: massive scale, flexible schema, specific access patterns. "NoSQL" isn't one thing — it's four very different families of databases.**

---

## 📖 Plain English

### SQL (Relational)
**Data lives in tables with rows and columns.** Strict schema. You join tables. Examples: PostgreSQL, MySQL.

```sql
SELECT u.name, o.total
FROM users u JOIN orders o ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '7 days';
```

### NoSQL — Four Distinct Families
1. **Key-Value** (Redis, DynamoDB) — `key → value`. Like a giant hash map.
2. **Document** (MongoDB, Firestore) — JSON blobs grouped into collections.
3. **Column-Family / Wide-Column** (Cassandra, HBase) — rows with dynamic columns; great for time-series.
4. **Graph** (Neo4j, Neptune) — nodes + edges; great for relationships.

These have **almost nothing in common** with each other except "not SQL."

---

## 🔑 The Key Differences

| | **SQL** | **NoSQL** (typical) |
|---|---|---|
| **Schema** | Strict (defined upfront) | Flexible (per-document) |
| **Joins** | First-class | Avoided / not supported |
| **ACID transactions** | Strong | Limited (often per-document only) |
| **Scaling** | Vertical (mostly) | Horizontal (built-in) |
| **Query language** | SQL (standardized) | Varies per DB |
| **Consistency** | Strong by default | Often eventual |
| **Best for** | Relational data, transactions | Massive scale, simple access patterns |

---

## 🏗️ The "Which DB?" Decision Tree

```
Need ACID transactions across multiple records?
└─ YES → SQL (Postgres, MySQL, Aurora)

Need to scale horizontally to billions of rows?
└─ Time-series / append-heavy?       → Cassandra, HBase, Bigtable
└─ Document-shaped data?              → MongoDB, DynamoDB
└─ Sub-millisecond reads?             → Redis (key-value)
└─ Pattern matching on relationships? → Neo4j (graph)

Don't know yet?
└─ → SQL. Always start here. Migrate later if forced.
```

---

## 📋 Quick Use-Case Map

| Scenario | Best Choice | Why |
|---|---|---|
| User accounts, orders, payments | **PostgreSQL** | ACID + relations + audit |
| Session storage, leaderboards | **Redis** (KV) | Sub-ms latency |
| Product catalog with varied attributes | **MongoDB** (Document) | Flexible schema |
| IoT sensor readings, time-series | **Cassandra** or **InfluxDB** | Write-heavy, ordered |
| Twitter timeline cache | **Redis** sorted sets | Fast push/pop |
| Recommendation graph (Netflix) | **Neo4j** or graph DB | Multi-hop traversal |
| Product reviews, comments | **PostgreSQL** with JSONB | Best of both worlds |
| Analytics on terabytes of clicks | **BigQuery / Snowflake** | Columnar, OLAP |

---

## ❌ Common Mistakes

1. **"NoSQL is faster"** — Wrong. SQL with proper indexes is *blazing* fast. NoSQL trades query flexibility for scale, not raw speed.
2. **"NoSQL means schemaless"** — Wrong. You always have a schema; NoSQL just doesn't enforce it. You enforce it in code instead.
3. **"NoSQL doesn't support transactions"** — Wrong. MongoDB has multi-document transactions; DynamoDB has them too. They're more limited but they exist.
4. **"Use NoSQL because we'll have lots of users"** — Wrong. PostgreSQL handles millions of users fine on a single server. Stripe ran on Postgres for years.
5. **"Joins don't scale"** — Right at extreme scale (>10TB). Wrong at almost everyone else's scale. Don't optimize for problems you don't have.

---

## 🔍 Quick Indexing Note

| | **SQL (B-Tree)** | **NoSQL (LSM-Tree)** |
|---|---|---|
| Best at | Random reads, in-place updates | Sequential writes |
| Used by | PostgreSQL, MySQL | Cassandra, RocksDB |
| Trade-off | Read-optimized | Write-optimized |

If your workload is **write-heavy** (logs, events, IoT) → LSM-tree DB shines.
If it's **read-mostly with random access** → B-tree DB shines.

See: [5-min read on database replication](./09-database-replication.md).

---

## 🚦 The Pragmatic Rule

> **Default to PostgreSQL.** Move to NoSQL only when you have a specific, measured reason — not because someone said it's "more scalable." Most companies that "moved to NoSQL" (then back to SQL) didn't actually need NoSQL.[^1]

Companies that famously stuck with PostgreSQL: Stripe, Instagram (in early days), Robinhood, GitLab.
Companies that migrated to NoSQL for real reasons: Discord (MongoDB → Cassandra → ScyllaDB for trillions of messages),[^2] Netflix (Cassandra for eventual consistency at edge).

---

## 🔗 Dig Deeper

- 📘 [karanpratapsingh/system-design — Chapter II: Databases](https://github.com/karanpratapsingh/system-design)
- 📘 *Designing Data-Intensive Applications* (Kleppmann) — Chapter 2 + 3
- 📺 [ByteByteGo: How to choose a database](https://www.youtube.com/@ByteByteGo)

---

## 📖 Citations

[^1]: Pat Helland's "Life Beyond Distributed Transactions" — many companies that swore off SQL came back. `papers-we-love/papers-we-love` repository.
[^2]: [Discord: How Discord Stores Trillions of Messages](https://discord.com/blog/how-discord-stores-trillions-of-messages) — Cassandra → ScyllaDB migration story.

---

← [Back to 5-min reads index](./README.md)
