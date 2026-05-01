# ⚡ 5-Minute Reads — System Design Quick Primers

> 20 focused topic primers. Each is designed to be read in **5 minutes or less** while giving you a complete working understanding of one concept.

---

## 🎯 How to Use These

- ☕ **One per day**: Read one with your morning coffee
- 🚇 **Commute reading**: Each fits a short subway ride
- 🔄 **Spaced repetition**: Re-read after 3 days, 1 week, 1 month
- 🎤 **Pre-interview**: Skim the relevant ones before a system design round
- 🧠 **Lookup**: When you need to refresh "what is X, again?"

Each read includes:
- 🎯 **TL;DR** — the one-line takeaway
- 📖 **Plain English explanation**
- 🔑 **Key trade-offs**
- 🏗️ **Real-world example**
- 🚦 **When to use / when NOT to use**
- 🔗 **Where to dig deeper**

---

## 📚 Index by Difficulty

### 🟢 Foundational (start here)
1. [What is System Design?](./01-what-is-system-design.md)
2. [Scalability: Vertical vs Horizontal](./02-scalability-basics.md)
3. [Latency vs Throughput](./03-latency-vs-throughput.md)
4. [REST vs GraphQL vs gRPC](./04-api-styles.md)
5. [SQL vs NoSQL](./05-sql-vs-nosql.md)

### 🟡 Core Concepts (intermediate)
6. [Load Balancing](./06-load-balancing.md)
7. [Caching Strategies](./07-caching.md)
8. [CDN — Content Delivery Networks](./08-cdn.md)
9. [Database Replication](./09-database-replication.md)
10. [Database Sharding](./10-database-sharding.md)
11. [Consistent Hashing](./11-consistent-hashing.md)
12. [Microservices vs Monolith](./12-microservices.md)
13. [Message Queues & Pub/Sub](./13-message-queues.md)
14. [Rate Limiting](./14-rate-limiting.md)

### 🔴 Distributed Systems (advanced)
15. [The CAP Theorem](./15-cap-theorem.md)
16. [Consistency Models](./16-consistency-models.md)
17. [Consensus: Raft & Paxos](./17-consensus-raft-paxos.md)
18. [Event-Driven Architecture & Saga Pattern](./18-event-driven-and-saga.md)
19. [Circuit Breaker, Bulkhead & Resilience Patterns](./19-resilience-patterns.md)
20. [Observability: Logs, Metrics, Traces](./20-observability.md)

---

## 🗺️ Suggested Reading Sequence

### Week 1: Foundations
Mon: #1 → Tue: #2 → Wed: #3 → Thu: #4 → Fri: #5

### Week 2: Core Concepts (Part 1)
Mon: #6 → Tue: #7 → Wed: #8 → Thu: #9 → Fri: #10

### Week 3: Core Concepts (Part 2)
Mon: #11 → Tue: #12 → Wed: #13 → Thu: #14 → Fri: Re-read favorites

### Week 4: Distributed Systems
Mon: #15 → Tue: #16 → Wed: #17 → Thu: #18 → Fri: #19 + #20

After 4 weeks, you'll have working knowledge of every essential system design concept.

---

## 🎯 Quick Lookup by Topic

| Looking for... | Read |
|---|---|
| "What's the difference between X and Y?" | [SQL vs NoSQL](./05-sql-vs-nosql.md), [REST vs GraphQL vs gRPC](./04-api-styles.md), [Microservices vs Monolith](./12-microservices.md) |
| "How do I scale...?" | [Scalability Basics](./02-scalability-basics.md), [Load Balancing](./06-load-balancing.md), [Sharding](./10-database-sharding.md), [Replication](./09-database-replication.md) |
| "How do I make it faster?" | [Caching](./07-caching.md), [CDN](./08-cdn.md), [Latency vs Throughput](./03-latency-vs-throughput.md) |
| "How do I make it reliable?" | [CAP Theorem](./15-cap-theorem.md), [Resilience Patterns](./19-resilience-patterns.md), [Observability](./20-observability.md) |
| "How do distributed systems agree?" | [Consensus](./17-consensus-raft-paxos.md), [Consistency Models](./16-consistency-models.md), [Event-Driven & Saga](./18-event-driven-and-saga.md) |
| "How does data flow async?" | [Message Queues](./13-message-queues.md), [Event-Driven & Saga](./18-event-driven-and-saga.md) |

---

← [Back to System Design home](../README.md)
